# -*- coding: utf-8 -*-
"""AUTO-COHERENCE : compare DEUX reconstructions independantes (memes analyses,
prompts v2, deux tirages) et ne retient que ce qui est STABLE.

  - article STABLE = meme statut ET (si A) meme cellule dans les deux passes ;
  - article INSTABLE = mis de cote (jamais force) ;
  - cellules stables agregees (dominants d'abord, secondaires a part, statuts
    ANECDOTAL / EMERGING / SUPPORTED / STRONG, historique, overlap) ;
  - QUESTIONS_EXPERT : pour les cellules >= EMERGING, les mappings MEDIUM avec
    leurs deux candidats (worsen / worsen_alt) -> une question par famille.
    C'est la SEULE chose que l'expert lit.

Usage : python scripts/stabilite.py --discipline plasturgie --a reconstruction_X_r1.json --b reconstruction_X_r2.json
"""
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
import invent  # noqa


def _arg(n, d):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


DISC = _arg("--discipline", "plasturgie")
A = ROOT / "scripts" / _arg("--a", f"reconstruction_{DISC}_r1.json")
B = ROOT / "scripts" / _arg("--b", f"reconstruction_{DISC}_r2.json")


def main():
    PN = {p["number"]: p["fr"] for p in invent.PARAMETERS}
    PL = {n: p.get("label", "") for n, p in invent.PRINCIPLES.items()}
    ra, rb = json.load(io.open(A, encoding="utf-8")), json.load(io.open(B, encoding="utf-8"))
    recs = {}
    for l in io.open(ROOT / "scripts" / f"analyses_{DISC}.jsonl", encoding="utf-8"):
        r = json.loads(l); p = r.get("paper") or {}
        recs[r.get("article_id") or p.get("doi") or p.get("url") or p.get("title")] = r
    pa, pb = ra["PER_ARTICLE"], rb["PER_ARTICLE"]
    sa, sb = ra.get("STAGE1", {}), rb.get("STAGE1", {})
    stable, unstable = {}, {}
    for aid in sorted(set(pa) | set(pb)):
        x, y = pa.get(aid), pb.get(aid)
        if not x or not y:
            unstable[aid] = {"raison": "absent d'une passe"}; continue
        cx = tuple(x["cell"]) if x.get("cell") else None
        cy = tuple(y["cell"]) if y.get("cell") else None
        if x["status"] == y["status"] and (x["status"] != "A" or cx == cy):
            stable[aid] = dict(x, cell=cx)
        else:
            unstable[aid] = {"passe_1": [x["status"], cx], "passe_2": [y["status"], cy],
                             "titre": (recs.get(aid, {}).get("paper") or {}).get("title", "")[:90]}
    # familles stables = celles de la passe 1 restreintes aux articles stables (meme cellule)
    fam_of = {}
    for f in ra.get("NORMALIZED_CONTRADICTION_FAMILIES") or []:
        for aid in f.get("ARTICLE_IDS") or []:
            if aid in stable:
                fam_of[aid] = f.get("FAMILY_ID")
    cells = defaultdict(list)
    for aid, v in stable.items():
        if v["status"] == "A" and v["cell"]:
            cells[v["cell"]].append(aid)
    a_dom = {a: ((recs[a]["analyse"].get("dominant") or {}).get("numero")) for a in stable if a in recs}
    a_sec = {a: [s.get("numero") for s in (recs[a]["analyse"].get("secondaires") or [])[:2] if s.get("numero")] for a in stable if a in recs}
    out_cells, questions = [], []
    for (i, j), arts in sorted(cells.items(), key=lambda kv: -len(kv[1])):
        fams = {fam_of.get(a) or f"ART:{a}" for a in arts}
        dom = Counter(a_dom.get(a) for a in arts if a_dom.get(a)); sec = Counter(s for a in arts for s in a_sec.get(a, []))
        hist = [p["number"] for p in invent.principles_for(i, j)]
        n, nf = len(arts), len(fams)
        status = ("STRONG_EMPIRICAL_CELL" if n >= 8 and nf >= 3 else "SUPPORTED" if n >= 4 and nf >= 2 else "EMERGING" if n >= 2 else "ANECDOTAL")
        # mappings MEDIUM -> question a l'expert (une par cellule >= EMERGING)
        meds = []
        for a in arts:
            s1 = sa.get(a) or {}
            for side in ("improve", "worsen"):
                m = s1.get(side) or {}
                alt = s1.get(side + "_alt")
                if str(m.get("semantic_distance", "")).upper() == "MEDIUM" and alt and alt.get("id"):
                    meds.append((side, m.get("id"), alt.get("id"), alt.get("reason", "")))
        if status != "ANECDOTAL" and meds:
            c = Counter((s, mid, aid_) for s, mid, aid_, _ in meds).most_common(1)[0][0]
            side, mid, altid = c
            questions.append({"cell": [i, j], "n_articles": n, "cote": side,
                              "retenu": f"{mid} {PN.get(mid)}", "alternative": f"{altid} {PN.get(altid)}",
                              "motif_alternative": next(r for s, m, a2, r in meds if (s, m, a2) == c)})
        out_cells.append({"CELL": [i, j], "improve": PN[i], "worsening": PN[j], "N_ARTICLES": n,
                          "N_PROBLEM_FAMILIES": nf, "families": sorted(fams), "ARTICLE_IDS": arts,
                          "DOMINANT_EMPIRICAL_PRINCIPLES": {f"P{k} {PL.get(k)}": c for k, c in dom.most_common()},
                          "SECONDARY_EMPIRICAL_DISTRIBUTION": {f"P{k} {PL.get(k)}": c for k, c in sec.most_common()},
                          "HISTORICAL_PRINCIPLES": hist, "OVERLAP_DOMINANT": [k for k in dom if k in hist],
                          "OVERLAP_ANY": sorted({k for k in list(dom) + list(sec) if k in hist}), "STATUS": status})
    st = Counter(v["status"] for v in stable.values())
    summary = {"articles_compares": len(set(pa) | set(pb)), "stables": len(stable), "instables": len(unstable),
               "taux_stabilite": round(100 * len(stable) / max(1, len(set(pa) | set(pb)))),
               "statuts_stables": dict(st), "cellules_stables": len(out_cells),
               "cellules_par_statut": dict(Counter(c["STATUS"] for c in out_cells)),
               "questions_expert": len(questions)}
    out = {"SUMMARY": summary, "STABLE_CELLS": out_cells, "QUESTIONS_EXPERT": questions,
           "UNSTABLE_ARTICLES": unstable, "PER_ARTICLE": {a: dict(v, cell=list(v["cell"]) if v.get("cell") else None) for a, v in stable.items()}}
    (ROOT / "scripts" / f"reconstruction_{DISC}_stable.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    md = [f"# Questions à l'expert — {DISC}", "", f"{len(questions)} question(s). Tout le reste est décidé automatiquement.", ""]
    for q in questions:
        md.append(f"- Cellule [{q['cell'][0]},{q['cell'][1]}] ({q['n_articles']} articles), côté **{q['cote']}** : "
                  f"garder **{q['retenu']}** ou préférer **{q['alternative']}** ? — {q['motif_alternative']}")
    (ROOT / "scripts" / f"questions_expert_{DISC}.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    for c in out_cells:
        if c["STATUS"] != "ANECDOTAL":
            print(f"  [{c['CELL'][0]},{c['CELL'][1]}] n={c['N_ARTICLES']} fam={c['N_PROBLEM_FAMILIES']} {c['STATUS']} | dom {c['DOMINANT_EMPIRICAL_PRINCIPLES']} | hist {c['HISTORICAL_PRINCIPLES']}")


if __name__ == "__main__":
    main()
