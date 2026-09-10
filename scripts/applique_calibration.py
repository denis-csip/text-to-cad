# -*- coding: utf-8 -*-
"""Applique les 8 VERDICTS VALIDES par Denis (2026-09-10, « protocole stabilise »)
a la reconstruction plasturgie et produit la matrice empirique CALIBREE du
pilote. Aucune analyse relancee : pure application de decisions d'expert.
"""
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
import invent  # noqa

DISC = "plasturgie"
# family_id (reconstruction) -> verdict
VERDICTS = {
    "FAMILY_CONFORMAL_COOLING_STRENGTH": ("VALID_MATRIX_CELL", (25, 14), 0.75, "FAMILY_CONFORMAL_COOLING"),
    "FAMILY_CONFORMAL_COOLING_GEOMETRY": ("VALID_MATRIX_CELL", (25, 14), 0.75, "FAMILY_CONFORMAL_COOLING"),   # fusion
    "FAMILY_LIGHTWEIGHTING_SURFACE_QUALITY": ("VALID_MATRIX_CELL", (2, 12), 0.65, "FAMILY_LIGHTWEIGHTING_SURFACE_QUALITY"),
    "FAMILY_LIGHTWEIGHT_STRUCTURE_STRENGTH": ("VALID_MATRIX_CELL", (2, 14), 0.85, "FAMILY_LIGHTWEIGHT_STRUCTURE_STRENGTH"),
    "FAMILY_RECYCLED_PLASTICS_STRENGTH": ("VALID_PROBLEM_FAMILY_NO_ALTSHULLER_CELL", None, None, "FAMILY_RECYCLED_PLASTICS_STRENGTH"),
    "FAMILY_IN_MOLD_SENSING": ("VALID_MATRIX_CELL", (28, 13), 0.60, "FAMILY_IN_MOLD_SENSING"),
    "FAMILY_SIMULATION_OPTIMIZATION_TIME": ("VALID_PROBLEM_FAMILY_NO_ALTSHULLER_CELL", None, None, "FAMILY_SIMULATION_OPTIMIZATION_TIME"),
    "FAMILY_DFMA_ASSEMBLY_TIME": ("VALID_MATRIX_CELL", (32, 25), 0.70, "FAMILY_DFMA_ASSEMBLY_TIME"),
}
# exceptions par article (eclatements / exclusions decides a l'audit)
PAR_ARTICLE = {
    # DFMA eclatee
    "wheel_center": ("VALID_MATRIX_CELL", (14, 32), 0.70, "FAMILY_SHORT_FIBRE_MOULDABILITY"),
    "brep": ("NO_TECHNICAL_CONTRADICTION", None, None, None),
    # scaffold tissulaire : hors discipline / hors probleme
    "scaffold": ("EXCLUDED_OUT_OF_DISCIPLINE", None, None, None),
}
MOTS = {"wheel_center": "wheel center", "brep": "manufacturability in injection", "scaffold": "tissue engineering scaffolds"}


def main():
    R = json.load(io.open(ROOT / "scripts" / f"reconstruction_{DISC}.json", encoding="utf-8"))
    recs = {}
    for l in io.open(ROOT / "scripts" / f"analyses_{DISC}.jsonl", encoding="utf-8"):
        r = json.loads(l); p = r.get("paper") or {}
        recs[r.get("article_id") or p.get("doi") or p.get("url") or p.get("title")] = r
    PN = {p["number"]: p["fr"] for p in invent.PARAMETERS}
    PL = {n: p.get("label", "") for n, p in invent.PRINCIPLES.items()}
    final = {}
    for f in R["NORMALIZED_CONTRADICTION_FAMILIES"]:
        v = VERDICTS.get(f["FAMILY_ID"])
        for a in f["ARTICLE_IDS"]:
            title = ((recs.get(a) or {}).get("paper") or {}).get("title", "").lower()
            exc = next((PAR_ARTICLE[k] for k, m in MOTS.items() if m in title), None)
            status, cell, conf, fam = exc or v
            final[a] = {"status": status, "cell": cell, "confidence": conf, "family": fam}
    # singletons et B/C d'origine restent tels quels (hors familles) ; singletons hors discipline signales
    cells = defaultdict(list)
    for a, v in final.items():
        if v["status"] == "VALID_MATRIX_CELL":
            cells[v["cell"]].append(a)
    a_dom = {a: ((recs[a]["analyse"].get("dominant") or {}).get("numero")) for a in final}
    a_sec = {a: [s.get("numero") for s in (recs[a]["analyse"].get("secondaires") or [])[:2] if s.get("numero")] for a in final}
    out_cells = []
    for (i, j), arts in sorted(cells.items(), key=lambda kv: -len(kv[1])):
        fams = {final[a]["family"] for a in arts}
        dom = Counter(a_dom[a] for a in arts if a_dom[a]); sec = Counter(s for a in arts for s in a_sec[a])
        hist = [p["number"] for p in invent.principles_for(i, j)]
        n, nf = len(arts), len(fams)
        status = ("STRONG_EMPIRICAL_CELL" if n >= 8 and nf >= 3 else "SUPPORTED" if n >= 4 and nf >= 2 else "EMERGING" if n >= 2 else "ANECDOTAL")
        out_cells.append({"CELL": [i, j], "improve": PN[i], "worsening": PN[j], "N_ARTICLES": n,
                          "N_PROBLEM_FAMILIES": nf, "families": sorted(fams),
                          "DOMINANT_EMPIRICAL_PRINCIPLES": {f"P{k} {PL.get(k)}": c for k, c in dom.most_common()},
                          "SECONDARY_EMPIRICAL_DISTRIBUTION": {f"P{k} {PL.get(k)}": c for k, c in sec.most_common()},
                          "HISTORICAL_PRINCIPLES": hist, "OVERLAP_DOMINANT": [k for k in dom if k in hist],
                          "OVERLAP_ANY": sorted({k for k in list(dom) + list(sec) if k in hist}),
                          "STATUS": status, "MAPPING_CONFIDENCE": max(final[a]["confidence"] for a in arts)})
    stat = Counter(v["status"] for v in final.values())
    out = {"VALIDATED_BY": "Denis Cavallucci, 2026-09-10 — « je valide les 8 verdicts, protocole stabilisé »",
           "PER_ARTICLE": final, "CALIBRATED_CELLS": out_cells,
           "SUMMARY": {"articles_in_families": len(final), "status": dict(stat), "cells": len(out_cells),
                       "no_altshuller_cell_families": sorted({v["family"] for v in final.values() if v["status"] == "VALID_PROBLEM_FAMILY_NO_ALTSHULLER_CELL"})}}
    (ROOT / "scripts" / f"matrice_empirique_{DISC}_calibree.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out["SUMMARY"], ensure_ascii=False, indent=1))
    for c in out_cells:
        print(f"  [{c['CELL'][0]},{c['CELL'][1]}] n={c['N_ARTICLES']} fam={c['N_PROBLEM_FAMILIES']} {c['STATUS']} | dom {c['DOMINANT_EMPIRICAL_PRINCIPLES']} | hist {c['HISTORICAL_PRINCIPLES']} | overlap {c['OVERLAP_ANY']}")


if __name__ == "__main__":
    main()
