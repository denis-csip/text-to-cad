# -*- coding: utf-8 -*-
"""ANALYSE ARTICLE PAR ARTICLE selon le protocole « transformation » de Denis.

Entrée : scripts/corpus_<discipline>.json (articles moissonnés, gratuit).
Sortie : scripts/analyses_<discipline>.jsonl (une analyse complète par article,
         ajout seul, reprise possible) + scripts/campagne_<discipline>_candidates.json
         (format de la revue : solutions exploitables, placées par PAIRES).

Garde-fous de coût : --limit N, --cap $ (arrêt automatique), avancement par
article, sonde --limit 1 avant tout lot. --dry = 0 appel (mesure du prompt).
Usage : python scripts/analyse_articles.py --discipline plasturgie --limit 100 --cap 0.60
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
sys.path.insert(0, str(ROOT / "scripts"))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")


def _arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


DISC = _arg("--discipline", "plasturgie")
LIMIT = int(_arg("--limit", "0") or 0)
CAP = float(_arg("--cap", "0.60"))
DRY = "--dry" in sys.argv
WORKERS = int(_arg("--workers", "4"))
# Gemini 3.6 Flash : tarifs indicatifs ($/M) — le cumul est recalculé sur les
# tokens RÉELS renvoyés par l'API, le devis est ajusté à la sonde.
PIN, POUT = float(_arg("--pin", "0.30")), float(_arg("--pout", "2.50"))
CORPUS = ROOT / "scripts" / f"corpus_{DISC}.json"
OUT = ROOT / "scripts" / f"analyses_{DISC}.jsonl"
CANDS = ROOT / "scripts" / f"campagne_{DISC}_candidates.json"


def _safe(fn, *a):
    try:
        return fn(*a)
    except Exception as e:
        return {"erreur": str(e)[:80]}


def slug(t):
    s = re.sub(r"[^a-z0-9]+", "_", (t or "").lower()).strip("_")
    return s[:48] or "article"


def main():
    import analyse_triz as A
    papers = json.load(io.open(CORPUS, encoding="utf-8"))
    deja = set()
    if OUT.exists():
        for line in open(OUT, encoding="utf-8"):
            try:
                deja.add(json.loads(line)["key"])
            except Exception:
                pass
    todo = [p for p in papers if (p.get("doi") or p.get("title") or "").lower().strip() not in deja]
    # --exclude ecremage_{disc}.json : les articles ecartes par l'ecremage (revues,
    # etudes parametriques, hors discipline) ne passent pas par l'analyse payante
    excl = _arg("--exclude", None)
    if excl:
        ec = json.load(io.open(ROOT / "scripts" / excl, encoding="utf-8"))
        avant = len(todo)
        keyf = lambda p: (ec.get((p.get("doi") or p.get("title") or "").lower().strip()) or {}).get("keep", True)
        if "--recall-check" in sys.argv:
            # CONTROLE DU RAPPEL de l'ecremage : analyser un echantillon ALEATOIRE
            # des articles ECARTES pour mesurer combien etaient en fait exploitables
            import random
            random.seed(int(_arg("--seed", "7")))
            exclus = [p for p in todo if not keyf(p)]
            todo = random.sample(exclus, min(int(_arg("--recall-check", "100")), len(exclus)))
            for p in todo:
                p["_recall_check"] = True
            print(f"controle du rappel : {len(todo)} articles ECARTES tires au sort sur {len(exclus)}", flush=True)
        else:
            todo = [p for p in todo if keyf(p)]
            print(f"ecremage : {avant - len(todo)} articles ecartes avant analyse", flush=True)
    if LIMIT:
        todo = todo[:LIMIT]
    print(f"{DISC} : {len(papers)} articles, {len(deja)} déjà analysés, {len(todo)} à traiter "
          f"| plafond {CAP:.2f} $", flush=True)
    if DRY:
        sysp = A.prompt_pour(DISC)
        print(f"prompt système : {len(sysp)} caractères (~{len(sysp)//4} tokens) ; "
              f"article médian ~{1300//4 + 60} tokens ; sortie attendue ~600-900 tokens")
        return
    lock = threading.Lock()
    etat = {"cout": 0.0, "in": 0, "out": 0, "done": 0, "stop": False, "expl": 0}

    def run(p):
        if etat["stop"]:
            return None
        key = (p.get("doi") or p.get("title") or "").lower().strip()
        try:
            an, usage = A.analyser_article(p, DISC)
        except Exception as e:
            with lock:
                print("  KO:", str(e)[:100], flush=True)
            return None
        # ROBUSTESSE : une réponse non structurée (chaîne, liste) ne doit jamais
        # tuer le lot entier (crash du 2026-09-10 à 170/408 : 'str' has no 'get')
        if not isinstance(an, dict):
            an = {"exploitable": False, "raison": "réponse LLM non structurée"}
        if not isinstance(usage, dict):
            usage = {"in": 0, "out": 0}
        with lock:
            etat["in"] += usage["in"]; etat["out"] += usage["out"]
            etat["cout"] += usage["in"] * PIN / 1e6 + usage["out"] * POUT / 1e6
            etat["done"] += 1
            if an.get("exploitable"):
                etat["expl"] += 1
            rec = {"key": key, "paper": {"title": p.get("title"), "year": p.get("year"),
                                         "url": p.get("url")},
                   "analyse": an, "concordance": (_safe(A.concordance, an) if an.get("exploitable") else None),
                   "usage": usage, "ts": int(time.time()),
                   "recall_check": bool(p.get("_recall_check"))}
            with open(OUT, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if etat["done"] % 5 == 0 or etat["done"] == len(todo):
                print(f"  {etat['done']}/{len(todo)} — exploitables {etat['expl']} — "
                      f"cumul {etat['cout']:.3f} $ ({usage['in']}/{usage['out']} tok)", flush=True)
            if etat["cout"] >= CAP:
                etat["stop"] = True
                print(f"  PLAFOND {CAP:.2f} $ ATTEINT : arrêt", flush=True)
        return rec

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        list(ex.map(run, todo))
    # reconstruction du fichier de revue depuis TOUTES les analyses exploitables
    cands, ids = [], set()
    for line in open(OUT, encoding="utf-8"):
        rec = json.loads(line)
        an = rec.get("analyse") or {}
        if not an.get("exploitable"):
            continue
        sid = slug(an.get("nom_solution") or rec["paper"].get("title"))
        n = 2
        base = sid
        while sid in ids:
            sid = f"{base}_{n}"; n += 1
        ids.add(sid)
        s = A.vers_solution(an, rec["paper"], DISC, sid)
        if not s["principles"]:
            continue
        cands.append(s)
    # apport de revue : nb de cellules déclarées (paires) — plus de propagation cartésienne
    for c in cands:
        c["impact"] = {"cells": len(c["contradictions"]), "thin": 0}
    cands.sort(key=lambda c: (-max([p["confiance"] for p in c["contradictions"]] or [0]),
                              -max(c["confiance_principes"].values() or [0])))
    json.dump(cands, io.open(CANDS, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"\nTERMINÉ : {etat['done']} analysés, {etat['expl']} exploitables, "
          f"{len(cands)} solutions avec principe(s) ≥0,60 -> {CANDS.name} | "
          f"{time.time()-t0:.0f}s | tokens in {etat['in']} out {etat['out']} | "
          f"COÛT RÉEL {etat['cout']:.4f} $")


if __name__ == "__main__":
    main()
