# -*- coding: utf-8 -*-
"""MATRICE EMPIRIQUE — normalisation, validation, affectation aux cellules,
agregation (consignes de Denis, 2026-09-10). Part des analyses deja produites
(`analyses_{disc}.jsonl`, protocole « transformation ») ; ne relance JAMAIS
l'analyse des articles.

Deux couches, jamais melangees :
  HISTORICAL = matrice d'Altshuller (invent.principles_for, 1248 cellules verifiees)
  EMPIRICAL  = principes reellement observes dans les articles, par cellule.

Entree optionnelle `normalisation_{disc}.json` (produite par un passage LLM
separe, cf. --help du script normalise_contradictions.py) :
  { article_id: { "contradictions": [ {improve, worsen, confidence, sentence,
                    evidence, corrected: bool, note} ], "family": "SLUG",
                  "retry_no_cell": bool } }
Sans ce fichier : parametres tels qu'analyses, familles PROVISOIRES (1 par
article, drapeau `provisional`).

Sortie : matrice_empirique_{disc}.json {MATRIX_ASSIGNMENTS, EMPIRICAL_MATRIX,
UNASSIGNED_ARTICLES, QUALITY_REPORT} + resume Markdown.
"""
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
import invent  # noqa: E402

DISC = (sys.argv[sys.argv.index("--discipline") + 1] if "--discipline" in sys.argv else "plasturgie")
SEUIL_VALIDE, SEUIL_PLAUSIBLE = 0.80, 0.65
PN = {p["number"]: p["fr"] for p in invent.PARAMETERS}
PL = {n: p.get("label", "") for n, p in invent.PRINCIPLES.items()}
SEP_EN = {"espace": "space", "temps": "time", "conditions": "conditions",
          "tout-parties": "whole-parts", "tout/parties": "whole-parts", None: "none", "": "none"}


def historical(i, j):
    """(principes, statut) — distingue cellule VIDE DANS LA SOURCE et ERREUR DE LOOKUP."""
    if not (isinstance(i, int) and isinstance(j, int)) or not (1 <= i <= 39 and 1 <= j <= 39) or i == j:
        return [], "LOOKUP_ERROR"
    prn = [p["number"] for p in invent.principles_for(i, j)]
    if prn:
        return prn, "OK"
    # la source (Inventioneering, collationnee sur le scan original) ne
    # transcrit que les cellules NON vides : absence = vide chez Altshuller
    return [], "EMPTY_IN_SOURCE_MATRIX"


def main():
    src = ROOT / "scripts" / f"analyses_{DISC}.jsonl"
    recs = [json.loads(l) for l in io.open(src, encoding="utf-8")]
    norm_p = ROOT / "scripts" / f"normalisation_{DISC}.json"
    norm = json.load(io.open(norm_p, encoding="utf-8")) if norm_p.exists() else {}
    assignments, unassigned = [], []
    cells = defaultdict(lambda: {"articles": [], "secondary": []})
    corrected = lookup_errors = 0
    retried_ok = 0
    for r in recs:
        a = r.get("analyse") or {}
        p = r.get("paper") or {}
        aid = r.get("article_id") or p.get("doi") or p.get("url") or p.get("title")
        if not a.get("exploitable"):
            unassigned.append({"article_id": aid, "title": p.get("title"), "year": p.get("year"),
                               "reason": "NOT_EXPLOITABLE", "note": a.get("raison", "")})
            continue
        n = norm.get(aid) or {}
        contras = n.get("contradictions")
        if contras is None:                       # pas de normalisation LLM : tel quel
            contras = [{"improve": c.get("ameliore"), "worsen": c.get("degrade"),
                        "confidence": c.get("confiance"), "sentence": c.get("phrase"),
                        "evidence": c.get("preuve"), "corrected": False}
                       for c in (a.get("contradictions") or [])]
        else:
            corrected += sum(1 for c in contras if c.get("corrected"))
            if n.get("retry_no_cell") and contras:
                retried_ok += 1
        # seuils + au plus 2 cellules (paires distinctes), secondaires a part
        contras = [c for c in contras if isinstance(c.get("confidence"), (int, float))]
        valides = sorted([c for c in contras if c["confidence"] >= SEUIL_VALIDE],
                         key=lambda c: -c["confidence"])
        plaus = [c for c in contras if SEUIL_PLAUSIBLE <= c["confidence"] < SEUIL_VALIDE]
        retenues, paires = [], set()
        for c in valides:
            k = (c["improve"], c["worsen"])
            if k not in paires and len(retenues) < 2:
                retenues.append(c); paires.add(k)
        if not retenues and not plaus:
            unassigned.append({"article_id": aid, "title": p.get("title"), "year": p.get("year"),
                               "reason": "NO_MATRIX_CELL",
                               "note": "aucune contradiction >= 0.65" if contras else
                                       "aucune contradiction technique Altshuller suffisamment démontrée"})
            continue
        dom = a.get("dominant") or {}
        secs = [s for s in (a.get("secondaires") or []) if s.get("numero")]
        phys = a.get("contradiction_physique") or {}
        fam = n.get("family") or f"ART:{aid}"
        observed = [dom.get("numero")] + [s["numero"] for s in secs]
        observed = [x for x in observed if x]

        def make(c, status):
            i, j = c["improve"], c["worsen"]
            hist, hstat = historical(i, j)
            nonlocal lookup_errors
            if hstat == "LOOKUP_ERROR":
                lookup_errors += 1
            if hstat != "OK":
                match = "historical_cell_empty" if hstat == "EMPTY_IN_SOURCE_MATRIX" else "lookup_error"
            elif dom.get("numero") in hist:
                match = "strong"
            elif set(observed) & set(hist):
                match = "partial"
            else:
                match = "none"
            return {
                "article_id": aid, "title": p.get("title"), "year": p.get("year"),
                "doi_or_url": p.get("doi") or p.get("url"),
                "improve_parameter": {"id": i, "canonical_name": PN.get(i)},
                "worsening_parameter": {"id": j, "canonical_name": PN.get(j)},
                "contradiction_sentence": c.get("sentence"),
                "contradiction_evidence": c.get("evidence"),
                "contradiction_confidence": c.get("confidence"),
                "assignment_status": status,            # validated | secondary
                "parameter_corrected": bool(c.get("corrected")),
                "inventive_summary": a.get("resume_inventif"),
                "dominant_principle": {"id": dom.get("numero"), "name": PL.get(dom.get("numero")),
                                       "confidence": dom.get("confiance")},
                "secondary_principles": [{"id": s["numero"], "name": PL.get(s["numero"]),
                                          "confidence": s.get("confiance")} for s in secs],
                "physical_contradiction": {"present": bool(phys.get("presente")),
                                           "statement": phys.get("enonce"),
                                           "separation": SEP_EN.get(phys.get("separation"), phys.get("separation") or "none")},
                "scope": a.get("portee"),
                "solution_family": fam, "family_provisional": not n.get("family"),
                "historical_matrix_principles": hist, "historical_status": hstat,
                "match_status": match,
            }
        for c in retenues:
            e = make(c, "validated"); assignments.append(e)
            cells[(c["improve"], c["worsen"])]["articles"].append(e)
        if not retenues:                         # seulement du plausible : secondaire
            c = max(plaus, key=lambda c: c["confidence"])
            e = make(c, "secondary"); assignments.append(e)
            cells[(c["improve"], c["worsen"])]["secondary"].append(e)

    # --- agregation par cellule ---------------------------------------------
    matrix = {}
    for (i, j), d in cells.items():
        arts = d["articles"]; secs = d["secondary"]
        allobs = arts + secs
        fams = {e["solution_family"] for e in arts}
        dom_art = Counter(e["dominant_principle"]["id"] for e in arts if e["dominant_principle"]["id"])
        all_art = Counter()
        fam_sup = defaultdict(set)
        for e in arts:
            seen = {e["dominant_principle"]["id"]} | {s["id"] for s in e["secondary_principles"]}
            for pnum in seen:
                if pnum:
                    all_art[pnum] += 1; fam_sup[pnum].add(e["solution_family"])
        n = len(arts)
        hist, hstat = historical(i, j)
        emp = sorted(all_art, key=lambda pnum: (-len(fam_sup[pnum]), -all_art[pnum]))
        overlap = [pnum for pnum in emp if pnum in hist]
        nf = len(fams)
        matrix[f"{i},{j}"] = {
            "cell": [i, j], "improve": PN.get(i), "worsening": PN.get(j),
            "N_ARTICLES": n, "N_SECONDARY": len(secs), "N_SOLUTION_FAMILIES": nf,
            "articles": [e["article_id"] for e in arts],
            "families": sorted(fams),
            "DOMINANT_PRINCIPLE_DISTRIBUTION": {f"P{k}": {"articles": v, "pct": round(100 * v / n)} for k, v in dom_art.most_common()},
            "ALL_OBSERVED_PRINCIPLES_DISTRIBUTION": {f"P{k}": {"name": PL.get(k), "ARTICLE_SUPPORT": all_art[k],
                                                               "FAMILY_SUPPORT": len(fam_sup[k]),
                                                               "pct_articles": round(100 * all_art[k] / n)} for k in emp},
            "TOP_EMPIRICAL_PRINCIPLES": [{"id": k, "name": PL.get(k), "FAMILY_SUPPORT": len(fam_sup[k]),
                                          "ARTICLE_SUPPORT": all_art[k]} for k in emp[:4]],
            "HISTORICAL": hist, "historical_status": hstat,
            "EMPIRICAL": emp, "OVERLAP": overlap,
            "overlap_rate_historical": (round(len(overlap) / len(hist), 2) if hist else None),
            "overlap_rate_empirical": (round(len(overlap) / len(emp), 2) if emp else None),
            "confidence_level": ("fort" if nf >= 3 else "moyen" if nf == 2 else "faible"),
        }
    # --- rapport qualite -----------------------------------------------------
    n_tot = len(recs); n_ass = len({e["article_id"] for e in assignments})
    dom_dist = Counter(e["dominant_principle"]["id"] for e in assignments if e["assignment_status"] == "validated")
    cells_ok = [c for c in matrix.values() if c["N_ARTICLES"]]
    hist_cells = [c for c in cells_ok if c["HISTORICAL"]]
    ov = [c["overlap_rate_historical"] for c in hist_cells]
    match_dist = Counter(e["match_status"] for e in assignments if e["assignment_status"] == "validated")
    quality = {
        "discipline": DISC, "total_articles": n_tot, "exploitable_analyses": sum(1 for r in recs if (r.get("analyse") or {}).get("exploitable")),
        "assigned_articles": n_ass, "unassigned_articles": len(unassigned),
        "unassigned_by_reason": dict(Counter(u["reason"] for u in unassigned)),
        "assignments_validated": sum(1 for e in assignments if e["assignment_status"] == "validated"),
        "assignments_secondary": sum(1 for e in assignments if e["assignment_status"] == "secondary"),
        "articles_in_two_cells": sum(1 for _, k in Counter(e["article_id"] for e in assignments if e["assignment_status"] == "validated").items() if k >= 2),
        "distinct_cells_populated": len(cells_ok),
        "mean_articles_per_cell": (round(sum(c["N_ARTICLES"] for c in cells_ok) / len(cells_ok), 2) if cells_ok else 0),
        "mean_families_per_cell": (round(sum(c["N_SOLUTION_FAMILIES"] for c in cells_ok) / len(cells_ok), 2) if cells_ok else 0),
        "families_provisional": all(e["family_provisional"] for e in assignments) if assignments else None,
        "contradictions_corrected_at_normalisation": corrected,
        "no_cell_retries_recovered": retried_ok,
        "historical_lookup_errors": lookup_errors,
        "historical_cells_empty_in_source": sum(1 for c in cells_ok if c["historical_status"] == "EMPTY_IN_SOURCE_MATRIX"),
        "dominant_principle_distribution": {f"P{k} {PL.get(k)}": v for k, v in dom_dist.most_common()},
        "match_status_distribution": dict(match_dist),
        "global_overlap_rate_historical": (round(sum(ov) / len(ov), 2) if ov else None),
        "cells_with_zero_overlap": sum(1 for c in hist_cells if not c["OVERLAP"]),
    }
    out = {"MATRIX_ASSIGNMENTS": assignments, "EMPIRICAL_MATRIX": matrix,
           "UNASSIGNED_ARTICLES": unassigned, "QUALITY_REPORT": quality}
    (ROOT / "scripts" / f"matrice_empirique_{DISC}.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    # --- resume Markdown -----------------------------------------------------
    md = [f"# Matrice empirique — {DISC}", "", "## QUALITY_REPORT", ""]
    md += [f"- **{k}** : {v}" for k, v in quality.items()]
    md += ["", "## Cellules peuplées (triées par familles puis articles)", ""]
    for key, c in sorted(matrix.items(), key=lambda kv: (-kv[1]["N_SOLUTION_FAMILIES"], -kv[1]["N_ARTICLES"])):
        if not c["N_ARTICLES"]:
            continue
        md += [f"### [{c['cell'][0]},{c['cell'][1]}] améliorer « {c['improve']} » / se dégrade « {c['worsening']} » — {c['N_ARTICLES']} article(s), {c['N_SOLUTION_FAMILIES']} famille(s), confiance {c['confidence_level']}",
               f"- HISTORICAL : {c['HISTORICAL'] or c['historical_status']}",
               f"- EMPIRICAL : " + ", ".join(f"P{t['id']} {t['name']} (fam {t['FAMILY_SUPPORT']}, art {t['ARTICLE_SUPPORT']})" for t in c["TOP_EMPIRICAL_PRINCIPLES"]),
               f"- OVERLAP : {c['OVERLAP'] or '—'} (taux {c['overlap_rate_historical']})", ""]
    (ROOT / "scripts" / f"matrice_empirique_{DISC}.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(quality, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
