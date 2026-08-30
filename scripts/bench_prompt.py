# -*- coding: utf-8 -*-
"""BANC D'ESSAI DES STRATEGIES REDACTIONNELLES.

Chaque variante de prompt est notee sur les MEMES briefs canoniques, avec le
MEME scoring automatique. On choisit la strategie sur des chiffres.

Score par brief (0-100) :
  50  VALIDITE    le worker build123d produit un solide (0 sinon : tout le reste tombe)
  20  COTES       les cotes chiffrees du brief se retrouvent dans la bbox (tol. 15%)
  15  REGLABLE    parametres nommes detectes (>= 3 = plein score) -> pieces editables
  15  FEATURES    marqueurs geometriques attendus presents (trous, congé, creux...)
      penalites : -10 non etanche, -10 volume aberrant (hors 0.5x-3x l'attendu)

Usage :
  python scripts/bench_prompt.py --dry                 # 0 appel LLM, verifie le banc
  python scripts/bench_prompt.py --variants V0,V1      # sous-ensemble
  python scripts/bench_prompt.py                       # tout (voir --cost pour le devis)
  python scripts/bench_prompt.py --cost                # devis seul, aucun appel
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
from dotenv import load_dotenv                                       # noqa: E402
load_dotenv(ROOT / ".env")

import prompt_variants                                               # noqa: E402

# --- BRIEFS CANONIQUES : familles reelles d'usage fablab / prototypage -------
# dims  = cotes attendues dans la bbox (mm) | vol_cm3 = ordre de grandeur
# feats = marqueurs de features cherches dans le CODE genere
BRIEFS = [
    dict(id="plaque_trous", brief="une plaque de 60 x 40 mm, epaisseur 5 mm, avec "
         "4 trous de 5 mm aux quatre coins, a 8 mm des bords",
         dims=[60, 40, 5], vol_cm3=11.5, feats=["Cylinder|Hole"]),
    dict(id="equerre", brief="une equerre de fixation : semelle 60 x 40 mm et "
         "dosseret 45 mm de haut, epaisseur 5 mm, deux trous de 5 mm dans la "
         "semelle et un trou de 6 mm dans le dosseret",
         dims=[60, 40, 45], vol_cm3=20, feats=["Cylinder|Hole"]),
    dict(id="support_tube", brief="un support mural pour un tube de 25 mm de "
         "diametre : platine 50 x 50 mm epaisseur 4 mm avec 2 trous de 4 mm, "
         "et un collier semi-circulaire qui epouse le tube",
         dims=[50, 50, None], vol_cm3=18, feats=["Cylinder"]),
    dict(id="vide_poche", brief="un vide-poche rectangulaire 90 x 60 mm, "
         "hauteur 30 mm, parois de 2 mm, fond plein, coins arrondis",
         dims=[90, 60, 30], vol_cm3=22, feats=["hollow_tray|offset|fillet"]),
    dict(id="patere", brief="une patere murale : platine 40 x 60 mm epaisseur "
         "5 mm avec 2 trous de 4 mm, et un crochet en L qui remonte, "
         "profondeur 35 mm",
         dims=[40, 60, None], vol_cm3=20, feats=["hook|Box"]),
    dict(id="entretoise", brief="une entretoise cylindrique de 20 mm de "
         "diametre, 30 mm de haut, percee d'un trou central de 8 mm traversant",
         dims=[20, 20, 30], vol_cm3=7.9, feats=["Cylinder"]),
    dict(id="boitier", brief="un boitier rectangulaire 80 x 50 x 25 mm, parois "
         "3 mm, ouvert sur le dessus, avec une decoupe de 12 x 6 mm sur un "
         "cote pour un connecteur USB",
         dims=[80, 50, 25], vol_cm3=25, feats=["hollow_tray|offset", "Box"]),
    dict(id="poignee", brief="une poignee de tiroir : deux pieds de 12 mm de "
         "haut espaces de 96 mm entre axes, relies par une barre horizontale "
         "de 16 mm de diametre, percage M4 dans chaque pied",
         dims=[None, None, None], vol_cm3=25, feats=["Cylinder"]),
    dict(id="cale_angle", brief="une cale d'angle a 30 degres : base 70 x 50 mm, "
         "epaisseur mini 6 mm, face inclinee a 30 degres, une rainure de "
         "5 mm de large au milieu de la face inclinee",
         dims=[70, 50, None], vol_cm3=45, feats=["Box|Polygon|extrude"]),
    dict(id="clip_cable", brief="un clip de cable a visser : embase 30 x 15 mm "
         "epaisseur 4 mm avec un trou de 4 mm, et un anneau ouvert de 10 mm "
         "de diametre interieur pour clipser un cable",
         dims=[30, 15, None], vol_cm3=4, feats=["Cylinder"]),
]


def score_one(b, ok, stats, code, err):
    """Note un brief (0-100) + detail lisible."""
    d = {"valide": bool(ok and stats), "score": 0, "detail": {}}
    if not d["valide"]:
        d["detail"]["erreur"] = (err or "")[:120]
        return d
    s = 50.0
    bbox = sorted(stats.get("bbox_mm") or [], reverse=True)
    want = sorted([x for x in (b["dims"] or []) if x], reverse=True)
    if want:
        hits = 0
        for w in want:
            if any(abs(v - w) <= 0.15 * w for v in bbox):
                hits += 1
        cotes = 20.0 * hits / len(want)
    else:
        cotes = 20.0
    s += cotes
    d["detail"]["cotes"] = round(cotes, 1)
    nparams = len(re.findall(r"^\s*[a-zA-Z_]\w*\s*=\s*-?\d+(?:\.\d+)?\s*(?:#|$)",
                             code, re.M))
    regl = 15.0 * min(nparams, 3) / 3.0
    s += regl
    d["detail"]["parametres"] = nparams
    feat_hits = sum(1 for pat in b["feats"] if re.search(pat, code))
    fs = 15.0 * feat_hits / max(len(b["feats"]), 1)
    s += fs
    d["detail"]["features"] = round(fs, 1)
    if stats.get("watertight") is False:
        s -= 10
        d["detail"]["non_etanche"] = True
    vol = stats.get("volume_cm3")
    if vol and b.get("vol_cm3"):
        if not (0.5 * b["vol_cm3"] <= vol <= 3.0 * b["vol_cm3"]):
            s -= 10
            d["detail"]["volume_aberrant"] = vol
    d["score"] = max(0.0, round(s, 1))
    d["volume_cm3"] = vol
    d["bbox"] = stats.get("bbox_mm")
    return d


def run_variant(name, cfg, briefs, workdir):
    import llm
    import worker_runner
    out = []
    for b in briefs:
        t0 = time.time()
        try:
            code = llm.generate_code(b["brief"], temperature=0.2,
                                     system=cfg["system"], thinking=cfg["thinking"])
        except Exception as e:
            out.append({"id": b["id"], "valide": False, "score": 0,
                        "detail": {"erreur": f"LLM {e}"[:120]}})
            continue
        ok, err, stats = worker_runner.run_code(code, workdir / name / b["id"])
        r = score_one(b, ok, stats, code, err)
        r["id"] = b["id"]
        r["secondes"] = round(time.time() - t0, 1)
        out.append(r)
        print(f"  {name:22s} {b['id']:14s} {'OK ' if r['valide'] else 'KO '}"
              f"score {r['score']:5.1f}  {r['secondes']}s", flush=True)
    valides = sum(1 for r in out if r["valide"])
    return {"variant": name, "results": out,
            "score_moyen": round(sum(r["score"] for r in out) / max(len(out), 1), 1),
            "taux_validite": round(100.0 * valides / max(len(out), 1))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", default="")
    ap.add_argument("--briefs", default="")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--cost", action="store_true")
    a = ap.parse_args()

    variants = prompt_variants.VARIANTS
    if a.variants:
        keys = [k.strip() for k in a.variants.split(",")]
        variants = {k: v for k, v in variants.items()
                    if any(k.startswith(x) for x in keys)}
    briefs = BRIEFS
    if a.briefs:
        ids = {x.strip() for x in a.briefs.split(",")}
        briefs = [b for b in BRIEFS if b["id"] in ids]

    n = len(variants) * len(briefs)
    print(f"{len(variants)} variantes x {len(briefs)} briefs = {n} generations")
    print(f"devis : ~{n * 0.004:.2f} $ (gemini-3.6-flash, ~1 appel de 3-6k tokens "
          f"par generation ; V5 reflexion haute ~2x)")
    if a.cost:
        return
    if a.dry:
        for k, v in variants.items():
            print(f"  {k:22s} systeme {len(v['system'])} car., thinking={v['thinking']}")
        print("banc pret (aucun appel LLM effectue).")
        return

    workdir = ROOT / "out" / "bench"
    workdir.mkdir(parents=True, exist_ok=True)
    all_res = []
    for name, cfg in variants.items():
        print(f"\n== {name} ==", flush=True)
        all_res.append(run_variant(name, cfg, briefs, workdir))
    all_res.sort(key=lambda r: -r["score_moyen"])
    out = ROOT / "scripts" / "bench_result.json"
    out.write_text(json.dumps(all_res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n=== CLASSEMENT DES STRATEGIES ===")
    for r in all_res:
        print(f"  {r['variant']:22s} score {r['score_moyen']:5.1f} / 100 "
              f"· validite {r['taux_validite']}%")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
