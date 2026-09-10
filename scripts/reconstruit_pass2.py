# -*- coding: utf-8 -*-
"""Second passage GLOBAL, strict : regrouper les articles restes isoles apres
`reconstruit_contradictions.py` et re-juger les paires « gardees distinctes ».
Regle de Denis : deux articles au meme conflit d'ingenierie recoivent la meme
cellule ; sans justification PHYSIQUE claire, on FUSIONNE vers la cellule la
mieux justifiee. Une matrice de 15 cellules solides vaut mieux que 30 cellules
a un article.
"""
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")
DISC = (sys.argv[sys.argv.index("--discipline") + 1] if "--discipline" in sys.argv else "plasturgie")
PRIX_IN, PRIX_OUT = 0.30e-6, 2.5e-6

SYSTEM = """Tu es un expert TRIZ. Passage GLOBAL STRICT de regroupement.
On te donne : (1) des FAMILLES DE CONTRADICTION deja constituees (probleme
generique, contradiction, cellule [improve, worsen]) ; (2) des ARTICLES ISOLES
avec leur probleme generique reconstruit et leur cellule individuelle.
Regle : la famille est definie par le PROBLEME d'ingenierie (le conflit
initial), jamais par la technologie de solution. Deux articles au meme conflit
-> meme famille, meme cellule. Ne garde une cellule distincte que sur une
justification PHYSIQUE explicite ; sinon FUSIONNE vers la cellule la mieux
justifiee de la famille. Tu peux : rattacher un isole a une famille existante,
creer une nouvelle famille regroupant >= 2 isoles, ou laisser un isole seul
(SINGLETON) si son conflit est reellement unique. Tu peux aussi corriger la
cellule d'une famille existante si le regroupement le justifie (dis pourquoi).
Exemples de familles attendues : RECYCLE1 « augmenter la fraction recyclee en
preservant les proprietes » ; FOAM1/LIGHTWEIGHT1 « reduire matiere/masse en
conservant les proprietes mecaniques » ; COMPLEX_SHAPE_PRECISION1 « obtenir des
formes complexes sans perdre la precision dimensionnelle ».
Parametres sur-utilises a n'employer que si le conflit initial porte dessus :
25, 32, 36, 37, 39.
Reponds UNIQUEMENT en JSON :
{"families": [{"family_id": "...", "generic_problem": "...", "generic_contradiction": "...",
   "improve": n, "worsen": n, "article_ids": ["..."], "justification": "..."}],
 "singletons": [{"article_id": "...", "why_unique": "..."}],
 "coherence_warnings": ["..."]}"""


def main():
    import invent, llm
    from google.genai import types
    PN = {p["number"]: p["fr"] for p in invent.PARAMETERS}
    PL = {n: p.get("label", "") for n, p in invent.PRINCIPLES.items()}
    R = json.load(io.open(ROOT / "scripts" / f"reconstruction_{DISC}.json", encoding="utf-8"))
    recs = {}
    for l in io.open(ROOT / "scripts" / f"analyses_{DISC}.jsonl", encoding="utf-8"):
        r = json.loads(l); p = r.get("paper") or {}
        recs[r.get("article_id") or p.get("doi") or p.get("url") or p.get("title")] = r
    fams = R["NORMALIZED_CONTRADICTION_FAMILIES"]
    in_fam = {a for f in fams for a in f["ARTICLE_IDS"]}
    per = R["PER_ARTICLE"]
    isoles = [{"article_id": a, "title": (recs[a].get("paper") or {}).get("title", "")[:90],
               "probleme_generique": v["probleme_generique"], "phrase": v["phrase"], "cell": v["cell"]}
              for a, v in per.items() if v["status"] == "A" and v["cell"] and a not in in_fam]
    user = ("PARAMETRES : " + " ; ".join(f"{n} {PN[n]}" for n in PN)
            + "\n\nFAMILLES EXISTANTES :\n" + json.dumps([{"family_id": f["FAMILY_ID"], "generic_problem": f["GENERIC_PROBLEM"],
                                                          "generic_contradiction": f["GENERIC_CONTRADICTION"],
                                                          "improve": f["IMPROVE_PARAMETER"]["id"], "worsen": f["WORSENING_PARAMETER"]["id"],
                                                          "article_ids": f["ARTICLE_IDS"]} for f in fams], ensure_ascii=False)
            + "\n\nARTICLES ISOLES :\n" + json.dumps(isoles, ensure_ascii=False)
            + "\n\nPAIRES PRECEDEMMENT GARDEES DISTINCTES (a re-juger) :\n" + json.dumps(R.get("KEPT_DISTINCT"), ensure_ascii=False))
    cfg = types.GenerateContentConfig(system_instruction=SYSTEM, temperature=0.1, response_mime_type="application/json",
                                      **({"thinking_config": types.ThinkingConfig(thinking_level=llm.THINKING)} if "gemini-3" in llm.MODEL else {}))
    resp = llm._get_client().models.generate_content(model=llm.MODEL, contents=user, config=cfg)
    u = getattr(resp, "usage_metadata", None)
    cout = int(getattr(u, "prompt_token_count", 0) or 0) * PRIX_IN + int(getattr(u, "candidates_token_count", 0) or 0) * PRIX_OUT
    d = llm._extract_json(resp.text) or {}
    new_fams = d.get("families") or []
    # --- application : nouvelles familles -> cellules, isoles restants -> singletons
    fam_of = {}
    for f in new_fams:
        for a in f.get("article_ids") or []:
            fam_of[a] = f
    for a, v in per.items():
        f = fam_of.get(a)
        if f and v["status"] == "A" and isinstance(f.get("improve"), int) and isinstance(f.get("worsen"), int):
            v["cell"] = (f["improve"], f["worsen"]); v["family"] = f["family_id"]
    a_dom = {a: ((recs[a]["analyse"].get("dominant") or {}).get("numero")) for a in per}
    a_sec = {a: [s.get("numero") for s in (recs[a]["analyse"].get("secondaires") or [])[:2] if s.get("numero")] for a in per}
    cells = defaultdict(list)
    for a, v in per.items():
        if v["status"] == "A" and v["cell"]:
            cells[tuple(v["cell"])].append(a)
    proposed = []
    for (i, j), arts in sorted(cells.items(), key=lambda kv: -len(kv[1])):
        fs = {per[a]["family"] for a in arts if per[a].get("family")}
        dom = Counter(a_dom[a] for a in arts if a_dom[a]); sec = Counter(s for a in arts for s in a_sec[a])
        hist = [p["number"] for p in invent.principles_for(i, j)]
        n, nf = len(arts), max(1, len(fs))
        status = ("STRONG_EMPIRICAL_CELL" if n >= 8 and nf >= 3 else "SUPPORTED" if n >= 4 and nf >= 2 else "EMERGING" if n >= 2 else "ANECDOTAL")
        gen = next((f["generic_contradiction"] for f in new_fams if (f.get("improve"), f.get("worsen")) == (i, j)), None) or per[arts[0]]["phrase"]
        proposed.append({"CELL": [i, j], "improve": PN[i], "worsening": PN[j], "GENERIC_CONTRADICTION": gen,
                         "N_ARTICLES": n, "ARTICLE_IDS": arts, "N_PROBLEM_FAMILIES": len(fs), "families": sorted(fs),
                         "DOMINANT_EMPIRICAL_PRINCIPLES": {f"P{k} {PL.get(k)}": v for k, v in dom.most_common()},
                         "SECONDARY_EMPIRICAL_DISTRIBUTION": {f"P{k} {PL.get(k)}": v for k, v in sec.most_common()},
                         "HISTORICAL_PRINCIPLES": hist, "OVERLAP_DOMINANT": [k for k in dom if k in hist],
                         "OVERLAP_ANY": sorted({k for k in list(dom) + list(sec) if k in hist}),
                         "CONFIDENCE": ("HIGH" if status in ("STRONG_EMPIRICAL_CELL", "SUPPORTED") else "MEDIUM" if status == "EMERGING" else "LOW"),
                         "STATUS": status})
    fam_out = [{"FAMILY_ID": f.get("family_id"), "GENERIC_PROBLEM": f.get("generic_problem"),
                "GENERIC_CONTRADICTION": f.get("generic_contradiction"),
                "IMPROVE_PARAMETER": {"id": f.get("improve"), "name": PN.get(f.get("improve"))},
                "WORSENING_PARAMETER": {"id": f.get("worsen"), "name": PN.get(f.get("worsen"))},
                "ARTICLE_IDS": f.get("article_ids") or [],
                "DOMINANT_PRINCIPLES_OBSERVED": {f"P{k} {PL.get(k)}": v for k, v in Counter(a_dom.get(a) for a in (f.get("article_ids") or []) if a_dom.get(a)).most_common()},
                "justification": f.get("justification")} for f in new_fams]
    s = R["RECLASSIFICATION_SUMMARY"]
    s.update({"nouveaux_articles_affectes": sum(len(v) for v in cells.values()), "nouvelles_cellules": len(cells),
              "familles": len(new_fams), "singletons": len(d.get("singletons") or []),
              "cout_reel": round(s.get("cout_reel", 0) + cout, 4)})
    R.update({"RECLASSIFICATION_SUMMARY": s, "NORMALIZED_CONTRADICTION_FAMILIES": fam_out,
              "SINGLETONS": d.get("singletons") or [],
              "COHERENCE_WARNINGS": (R.get("COHERENCE_WARNINGS") or []) + (d.get("coherence_warnings") or []),
              "PROPOSED_EMPIRICAL_CELLS": proposed, "PER_ARTICLE": per})
    (ROOT / "scripts" / f"reconstruction_{DISC}.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(s, ensure_ascii=False, indent=1))
    print(f"\nFAMILLES ({len(fam_out)}) :")
    for f in fam_out:
        print(f"  {f['FAMILY_ID']} [{f['IMPROVE_PARAMETER']['id']},{f['WORSENING_PARAMETER']['id']}] n={len(f['ARTICLE_IDS'])} — {f['GENERIC_PROBLEM'][:100]}")
    print(f"SINGLETONS : {len(d.get('singletons') or [])}")
    for x in d.get("singletons") or []:
        print("   -", (x.get("why_unique") or "")[:110])
    print("CELLULES :", [(c["CELL"], c["N_ARTICLES"], c["STATUS"]) for c in proposed])
    print("WARNINGS :"); [print("   -", w[:160]) for w in d.get("coherence_warnings") or []]


if __name__ == "__main__":
    main()
