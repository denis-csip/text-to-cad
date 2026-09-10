# -*- coding: utf-8 -*-
"""NORMALISATION des contradictions (etapes 1, 4 et 9 des consignes de Denis) :
un passage LLM CONSERVATEUR, par article deja analyse, qui :
  1. verifie chaque contradiction contre la DEFINITION CANONIQUE des 39
     parametres (app/parametres_definitions.json) et corrige le numero si un
     parametre a ete choisi sur un intitule vaguement proche — sans jamais
     redefinir un parametre ; recote la CONTRADICTION_CONFIDENCE (0-1) sur le
     lien causal « ameliorer I par l'action -> J se degrade » ;
  4. pour les articles sans contradiction : UNE tentative supplementaire,
     conservatrice ; sinon NO_MATRIX_CELL definitif ;
  9. attribue une SOLUTION_FAMILY (slug MAJUSCULE stable, ex. CONFORMAL_COOLING)
     pour que 10 articles sur les canaux conformes ne comptent pas comme 10
     decouvertes independantes.
Ne relance JAMAIS l'analyse des articles : ne lit que analyses_{disc}.jsonl.
Sortie : normalisation_{disc}.json consommee par matrice_empirique.py.
Cout : plafond --cap ; ~0,0015 $/article (Gemini 3.6 Flash).
"""
import io
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")


def _arg(n, d):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


DISC = _arg("--discipline", "plasturgie")
CAP = float(_arg("--cap", "0.20"))
PRIX_IN, PRIX_OUT = 0.30e-6, 2.5e-6

SYSTEM = """Tu es un expert TRIZ rigoureux. On te donne une analyse DEJA FAITE d'un
article (avant/probleme/transformation/apres, principes, contradictions) et la
liste CANONIQUE des 39 parametres d'Altshuller avec leurs DEFINITIONS.
Tu ne refais pas l'analyse. Tu NORMALISES et tu VALIDES.

TACHE A — pour chaque contradiction fournie :
- verifie que IMPROVE_PARAMETER et WORSENING_PARAMETER correspondent a leur
  DEFINITION canonique (pas a un intitule vaguement proche). INTERDIT de
  redefinir un parametre pour l'adapter a l'article. Si un numero est
  incorrect, remplace-le par le bon (corrected=true, note) ; s'il n'existe
  aucun parametre canonique qui convienne, mets confidence < 0.65.
- IMPROVE_PARAMETER = caracteristique que le concepteur cherche a AMELIORER
  (pas « valeur qui augmente » : reduire la matiere = ameliorer le 26).
- recote CONTRADICTION_CONFIDENCE (0-1) sur le seul lien CAUSAL :
  « ameliorer I par l'action -> J se degrade ». « I et J sont importants » = 0.
TACHE B — si la liste est vide (aucune contradiction) : UNE tentative
conservatrice a partir du probleme et de la transformation. N'invente jamais un
parametre degrade pour remplir la matrice ; si le compromis n'est pas reel,
renvoie une liste vide et no_cell=true.
TACHE C — SOLUTION_FAMILY : un slug MAJUSCULE_STABLE designant la famille
technologique de la solution (ex. CONFORMAL_COOLING, MICROCELLULAR_FOAMING,
VARIOTHERMAL_MOLDING, OVERMOLDING, IN_MOLD_LABELING, GAS_ASSISTED_INJECTION,
RECYCLED_SANDWICH, ULTRASONIC_WELDING…). Reutilise les slugs de la liste
« familles deja attribuees » quand la solution en releve.

Reponds UNIQUEMENT en JSON :
{"contradictions": [{"improve": n, "worsen": n, "confidence": 0-1,
  "sentence": "Lorsque nous cherchons a ameliorer I par ..., J se degrade car ...",
  "evidence": "citation/paraphrase de l'article", "corrected": bool, "note": "..."}],
 "no_cell": bool, "family": "SLUG"}"""


def main():
    import llm
    from google.genai import types
    import invent
    defs = json.load(io.open(ROOT / "app" / "parametres_definitions.json", encoding="utf-8"))
    canon = "\n".join(f"{n}. {defs.get(str(n), defs.get(n, p['fr']))}" for n, p in
                      ((p["number"], p) for p in invent.PARAMETERS))
    src = ROOT / "scripts" / f"analyses_{DISC}.jsonl"
    recs = [json.loads(l) for l in io.open(src, encoding="utf-8")]
    todo = [r for r in recs if (r.get("analyse") or {}).get("exploitable")]
    outp = ROOT / "scripts" / f"normalisation_{DISC}.json"
    done = json.load(io.open(outp, encoding="utf-8")) if outp.exists() else {}
    todo = [r for r in todo if (r.get("article_id") or (r.get("paper") or {}).get("doi")
                                or (r.get("paper") or {}).get("url")) not in done]
    print(f"{DISC} : {len(todo)} analyses a normaliser (deja faites {len(done)}) | plafond {CAP:.2f} $", flush=True)
    lock = threading.Lock()
    etat = {"cout": 0.0, "stop": False, "n": 0, "fam": set(v.get("family") for v in done.values() if v.get("family"))}
    cfg = types.GenerateContentConfig(
        system_instruction=SYSTEM, temperature=0.1, response_mime_type="application/json",
        **({"thinking_config": types.ThinkingConfig(thinking_level=llm.THINKING)} if "gemini-3" in llm.MODEL else {}))

    def run(r):
        if etat["stop"]:
            return None
        a, p = r["analyse"], r.get("paper") or {}
        aid = r.get("article_id") or p.get("doi") or p.get("url") or p.get("title")
        with lock:
            fams = sorted(etat["fam"])[:80]
        user = ("PARAMETRES CANONIQUES :\n" + canon +
                f"\n\nARTICLE : {p.get('title')} ({p.get('year')})\nANALYSE :\n" +
                json.dumps({k: a.get(k) for k in ("nom_solution", "resume_inventif", "avant", "probleme",
                                                  "transformation", "apres", "dominant", "secondaires",
                                                  "contradictions", "aucune_contradiction", "portee")},
                           ensure_ascii=False) +
                "\n\nFamilles deja attribuees : " + (", ".join(fams) or "(aucune)"))
        try:
            resp = llm._get_client().models.generate_content(model=llm.MODEL, contents=user, config=cfg)
            u = getattr(resp, "usage_metadata", None)
            ti, to = int(getattr(u, "prompt_token_count", 0) or 0), int(getattr(u, "candidates_token_count", 0) or 0)
            data = llm._extract_json(resp.text) or {}
        except Exception as e:
            print("  KO", str(e)[:100], flush=True); return None
        with lock:
            etat["cout"] += ti * PRIX_IN + to * PRIX_OUT; etat["n"] += 1
            if data.get("family"):
                etat["fam"].add(str(data["family"]).upper())
            if etat["n"] % 10 == 0:
                print(f"  {etat['n']}/{len(todo)} — cumul {etat['cout']:.3f} $", flush=True)
            if etat["cout"] >= CAP:
                etat["stop"] = True; print(f"  PLAFOND {CAP:.2f} $ ATTEINT", flush=True)
        cs = []
        for c in data.get("contradictions") or []:
            try:
                cs.append({"improve": int(c["improve"]), "worsen": int(c["worsen"]),
                           "confidence": float(c.get("confidence", 0)), "sentence": c.get("sentence"),
                           "evidence": c.get("evidence"), "corrected": bool(c.get("corrected")),
                           "note": c.get("note", "")})
            except Exception:
                pass
        return aid, {"contradictions": cs, "no_cell": bool(data.get("no_cell")),
                     "retry_no_cell": bool(a.get("aucune_contradiction")) and bool(cs),
                     "family": str(data.get("family") or "").upper() or None}

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(run, todo):
            if res:
                done[res[0]] = res[1]
    json.dump(done, io.open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    corr = sum(1 for v in done.values() for c in v["contradictions"] if c.get("corrected"))
    print(f"\nTERMINE : {len(done)} normalisees | contradictions corrigees {corr} | "
          f"familles distinctes {len({v.get('family') for v in done.values() if v.get('family')})} | "
          f"{time.time()-t0:.0f}s | COUT REEL {etat['cout']:.4f} $ (plafond {CAP:.2f}) -> {outp.name}")


if __name__ == "__main__":
    main()
