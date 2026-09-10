# -*- coding: utf-8 -*-
"""ECREMAGE avant analyse : ecarter, sur titre + resume, les articles qui ne
contiennent PAS de solution technique a analyser (revues, etudes parametriques,
modeles economiques, methodologies de mesure, hors discipline). Le pilote a
montre 52 % d'articles non exploitables analyses pour rien (0,003 $ piece).

Deux niveaux :
  - heuristique (0 $) : motifs lexicaux nets (review, survey, taguchi...) ;
  - --llm : tri par minimax-m2.5 (sans raisonnement, ~0,0001 $/article,
    plafond --cap) pour les cas non tranches par l'heuristique.
Sortie : ecremage_{disc}.json {cle_article: {keep: bool, reason: str, by: heuristic|llm}}
consommee par analyse_articles.py --exclude.
"""
import io
import json
import re
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
CAP = float(_arg("--cap", "0.40"))
USE_LLM = "--llm" in sys.argv
PRIX_IN, PRIX_OUT = 0.30e-6, 1.20e-6           # minimax-m2.5

EXCLURE = re.compile(
    r"\b(a review|review of|systematic review|literature review|state[- ]of[- ]the[- ]art|survey|overview|"
    r"taguchi|response surface|parametric study|effect of process parameters|influence of (?:process )?parameters|"
    r"cost model|economic analysis|life cycle assessment|lca\b|market|supply chain|"
    r"characterization of|rheological (?:behaviou?r|properties) of|mechanical properties of|thermal properties of|"
    r"tutorial|editorial|conference report|book chapter)\b", re.I)
HORS_DISC = {
    "plasturgie": re.compile(r"\b(metabolic|bacteria|cell culture|tissue engineering|scaffold|bone|dental|"
                             r"selective laser melting|slm\b|titanium|steel alloy|concrete|asphalt|"
                             r"microfluidic pump|electrokinetic|semiconductor wafer)\b", re.I),
}
SYSTEM = """Tu tries des articles pour une matrice de solutions inventives en {disc}.
Reponds keep=true SEULEMENT si l'article decrit une SOLUTION TECHNIQUE concrete
(geometrie, procede, outillage, materiau) qui transforme une pratique
conventionnelle. Reponds keep=false pour : revue/etat de l'art, etude
parametrique ou plan d'experiences sans invention, caracterisation de materiau,
modele economique/logistique, methode de mesure ou de simulation sans
transformation du produit ou du procede, hors {disc}.
JSON : {{"keep": true|false, "reason": "5 mots"}}"""


def cle(p):
    return (p.get("doi") or p.get("title") or "").lower().strip()


def main():
    corpus = ROOT / "scripts" / f"corpus_{DISC}.json"      # meme source que analyse_articles.py
    papers = json.load(io.open(corpus, encoding="utf-8"))
    outp = ROOT / "scripts" / f"ecremage_{DISC}.json"
    done = json.load(io.open(outp, encoding="utf-8")) if outp.exists() else {}
    heur = 0
    todo = []
    for p in papers:
        k = cle(p)
        if not k:
            continue
        if k in done and not (USE_LLM and str(done[k].get("reason", "")).startswith("non tranche")):
            continue                      # deja tranche (sauf « non tranche » a re-trier par --llm)
        txt = (p.get("title") or "") + " " + (p.get("abstract") or "")
        m = EXCLURE.search(p.get("title") or "")
        h = HORS_DISC.get(DISC)
        if m:
            done[k] = {"keep": False, "reason": f"titre : {m.group(0)}", "by": "heuristic"}; heur += 1
        elif h and h.search(txt):
            done[k] = {"keep": False, "reason": f"hors discipline : {h.search(txt).group(0)}", "by": "heuristic"}; heur += 1
        elif len(p.get("abstract") or "") < 200:
            done[k] = {"keep": False, "reason": "resume absent/trop court", "by": "heuristic"}; heur += 1
        else:
            todo.append(p)
    print(f"{DISC} : {len(papers)} articles | ecartes par heuristique {heur} | a trier {len(todo)}"
          + ("" if USE_LLM else " (heuristique seule : ils sont GARDES ; --llm pour trier)"), flush=True)
    if not USE_LLM:
        for p in todo:
            done[cle(p)] = {"keep": True, "reason": "non tranche (heuristique)", "by": "heuristic"}
    else:
        import llm
        etat = {"cout": 0.0, "n": 0, "stop": False}
        lock = threading.Lock()

        def run(p):
            if etat["stop"]:
                return cle(p), {"keep": True, "reason": "plafond atteint : garde", "by": "cap"}
            user = f"TITRE : {p.get('title')}\nRESUME : {(p.get('abstract') or '')[:1200]}"
            try:
                text, u = llm.zen_chat(SYSTEM.format(disc=DISC), user, model="minimax-m2.5",
                                       temperature=0.0, max_tokens=60, timeout=60)
                d = llm._extract_json(text) or {}
                keep = bool(d.get("keep", True))
                with lock:
                    etat["cout"] += int(u.get("prompt_tokens", 0) or 0) * PRIX_IN + int(u.get("completion_tokens", 0) or 0) * PRIX_OUT
                    etat["n"] += 1
                    if etat["n"] % 100 == 0:
                        print(f"  {etat['n']}/{len(todo)} — cumul {etat['cout']:.3f} $", flush=True)
                    if etat["cout"] >= CAP:
                        etat["stop"] = True; print(f"  PLAFOND {CAP:.2f} $ ATTEINT", flush=True)
                return cle(p), {"keep": keep, "reason": str(d.get("reason", ""))[:60], "by": "llm"}
            except Exception as e:
                return cle(p), {"keep": True, "reason": f"erreur tri : garde ({str(e)[:40]})", "by": "error"}
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=6) as ex:
            for k, v in ex.map(run, todo):
                done[k] = v
        print(f"  tri LLM : {etat['n']} articles, {time.time()-t0:.0f}s, cout reel {etat['cout']:.4f} $")
    json.dump(done, io.open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    keep = sum(1 for v in done.values() if v["keep"]); print(f"RESULTAT : gardes {keep} / ecartes {len(done)-keep} -> {outp.name}")


if __name__ == "__main__":
    main()
