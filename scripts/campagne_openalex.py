# -*- coding: utf-8 -*-
"""CAMPAGNE de moisson massive — Phase A (OpenAlex, gratuit) + Phase B (extraction
Gemini, ~0,5-1 $) pour peupler la matrice geometrique a l'echelle.

~100 requetes savantes couvrant les familles d'astuces geometriques ->
~2000-3000 abstracts dedoublonnes -> extraction TRIZ par lots de 12 (parallele)
-> candidats etiquetes AVEC sources, dedoublonnes entre eux et contre le
catalogue existant. AUCUNE adoption automatique : la sortie alimente la revue
d'expert (Phase C).

Usage : python scripts/campagne_openalex.py [--harvest-only]
Sortie : scripts/campagne_result.json  {stats, candidates}
"""
import json
import sys
import threading
import time
import urllib.parse
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import disciplines as _disc

# --discipline <id> : banque de requetes + prompt d'extraction du REGISTRE
DISCIPLINE = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--discipline=")),
                  None) or (sys.argv[sys.argv.index("--discipline") + 1]
                            if "--discipline" in sys.argv else "geometrie")
QUERIES = _disc.get(DISCIPLINE)["queries"]

MAX_PAPERS = 3000
UA = {"User-Agent": "text-to-cad/1.0"}
_print_lock = threading.Lock()


def openalex(query, rows=30, tries=5):
    """Recherche OpenAlex avec REPRISE sur 503/429 (attente 3, 6, 12, 24 s) :
    la campagne plasturgie du 2026-09-09 a perdu ~80 requetes sur une indispo."""
    url = ("https://api.openalex.org/works?search=" + urllib.parse.quote(query)
           + f"&per-page={rows}&filter=has_abstract:true")
    req = urllib.request.Request(url, headers=UA)
    data = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            break
        except urllib.error.HTTPError as e:
            if e.code in (503, 429, 502, 504) and k < tries - 1:
                time.sleep(3 * (2 ** k))
                continue
            raise
    if data is None:
        return []
    out = []
    for w in data.get("results", []):
        inv = w.get("abstract_inverted_index") or {}
        words = {}
        for tok, positions in inv.items():
            for p in positions:
                words[p] = tok
        abstract = " ".join(words[i] for i in sorted(words))[:1200]
        doi = w.get("doi")
        oa = (w.get("open_access") or {}).get("oa_url")
        out.append({"title": w.get("display_name"),
                    "year": w.get("publication_year"),
                    "doi": doi, "url": doi or oa or w.get("id"),
                    "abstract": abstract})
    return out


def harvest():
    papers, seen = [], set()
    for i, q in enumerate(QUERIES):
        try:
            got = openalex(q)
        except Exception as e:
            print(f"[{i+1}/{len(QUERIES)}] KO {q[:40]}: {e}", flush=True)
            continue
        new = 0
        for p in got:
            key = (p.get("doi") or p.get("title") or "").lower().strip()
            if key and key not in seen:
                seen.add(key)
                papers.append(p)
                new += 1
        print(f"[{i+1}/{len(QUERIES)}] {q[:50]} -> {new} nouveaux "
              f"(total {len(papers)})", flush=True)
        if len(papers) >= MAX_PAPERS:
            break
        time.sleep(0.15)
    return papers


def extract_all(papers, workers=5):
    import veille
    batches = [papers[i:i + 12] for i in range(0, len(papers), 12)]
    results, done = [], [0]

    def run(batch):
        try:
            c = veille.extract_candidates(batch, discipline=DISCIPLINE)
        except Exception as e:
            c = []
            with _print_lock:
                print("batch KO:", str(e)[:100], flush=True)
        with _print_lock:
            done[0] += 1
            if done[0] % 10 == 0:
                print(f"  extraction {done[0]}/{len(batches)} lots", flush=True)
        return c

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for cands in ex.map(run, batches):
            results.extend(cands)
    return results


def dedup(cands):
    import geo_solutions as geo
    out, ids, names = [], set(), set()
    for c in cands:
        cid = str(c.get("id") or "").strip()
        name = str(c.get("name") or "").lower().strip()
        if not cid or not c.get("instruction"):
            continue
        if cid in ids or cid in geo._BY_ID or (name and name in names):
            continue
        ids.add(cid)
        names.add(name)
        out.append(c)
    return out


def annote_impact(cands):
    """Apport de chaque candidat a la matrice : cellules touchees, dont pauvres
    (<3 solutions aujourd'hui). Tri decroissant = ordre de revue."""
    import geo_solutions as geo
    import invent
    cells = []
    for i in range(1, 40):
        for j in range(1, 40):
            if i == j:
                continue
            prn = {p["number"] for p in invent.principles_for(i, j)}
            if not prn:
                continue
            cur = len(geo.cell_solutions(i, j, list(prn), limit=10 ** 6))
            cells.append((i, j, prn, cur))
    for c in cands:
        P, I, D = set(c.get("principles", [])), set(c.get("improves", [])), set(c.get("degrades", []))
        n = thin = 0
        for i, j, prn, cur in cells:
            sc = geo.principle_score(P, prn) + (3 if i in I else 0) - (2 if j in D else 0)
            # Cellule comptee seulement si le candidat y est SPECIFIQUEMENT a sa
            # place (>= 4 : un principe precis, ou P35 fourre-tout + parametre
            # ameliore). Un simple P35 (1) ou un seul parametre (3) ne suffit pas.
            if sc >= 4:
                n += 1
                thin += cur < 3
        c["impact"] = {"cells": n, "thin": thin}
    # ordre de revue : d'abord l'apport specifique, puis les cellules pauvres
    cands.sort(key=lambda c: (-c["impact"]["cells"], -c["impact"]["thin"]))


def main():
    t0 = time.time()
    print(f"DISCIPLINE : {DISCIPLINE} ({len(QUERIES)} requetes)", flush=True)
    if "--from-papers" in sys.argv:      # reprise : corpus deja moissonne (fichier)
        pf = Path(sys.argv[sys.argv.index("--from-papers") + 1])
        papers = json.loads(pf.read_text(encoding="utf-8"))
        print(f"corpus recharge : {len(papers)} articles depuis {pf.name}", flush=True)
    else:
        papers = harvest()
    print(f"\nPhase A terminee : {len(papers)} articles dedoublonnes "
          f"({time.time()-t0:.0f}s)", flush=True)
    if "--harvest-only" in sys.argv:
        Path(__file__).with_name(f"campagne_{DISCIPLINE}_papers.json").write_text(
            json.dumps(papers, ensure_ascii=False), encoding="utf-8")
        return
    t1 = time.time()
    raw = extract_all(papers)
    cands = dedup(raw)
    stats = {"papers": len(papers), "candidats_bruts": len(raw),
             "candidats_dedoublonnes": len(cands),
             "articles_sources_distincts": len({
                 (s.get("url") or s.get("title") or "").lower()
                 for c in cands for s in c.get("sources", []) if s}),
             "duree_harvest_s": round(t1 - t0),
             "duree_extraction_s": round(time.time() - t1)}
    for c in cands:
        c["discipline"] = DISCIPLINE
    annote_impact(cands)
    stats["discipline"] = DISCIPLINE
    out = Path(__file__).with_name(f"campagne_{DISCIPLINE}_result.json")
    out.write_text(json.dumps({"stats": stats, "candidates": cands},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    Path(__file__).with_name(f"campagne_{DISCIPLINE}_candidates.json").write_text(
        json.dumps(cands, ensure_ascii=False), encoding="utf-8")
    print("\n=== CAMPAGNE TERMINEE ===")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
