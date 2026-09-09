# -*- coding: utf-8 -*-
"""MESURE : quelle part de la matrice geometrique est BRIDEE par la contrainte
« une seule piece monobloc fixe » ?  (aucun appel LLM, cout = 0)

Trois questions :
  Q1. Part des solutions du catalogue dont la FONCTION exige du mouvement.
      Deux familles, machineries differentes :
        A. MECANISME   : mouvement relatif entre corps -> couche liaisons build123d
        B. DEFORMATION : grand deplacement elastique d'un corps -> FEA non lineaire
  Q2. Part des 1248 cellules actives ou la matrice recommande un principe
      d'Altshuller de nature cinematique (= angle mort structurel).
  Q3. Part des propositions REELLEMENT affichees (top-6) qui sont mobiles.

Classifieur lexical PONDERE PAR CHAMP : un marqueur dans le NOM dit ce que la
solution EST (poids 2) ; dans desc/instruction il peut n'etre qu'une mention
de passage (poids 1). Seuil = 2. Ce reglage corrige les faux positifs mesures
en v1 (« flambement », « absorption d'energie », « membrane » TPMS, « verrouillage »
topologique, « surface de rotation » : tous statiques).
Croise avec un classifieur par principes TRIZ -> intervalle d'incertitude.
"""
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

# --- A. MECANISME : mouvement relatif entre corps distincts ----------------
MECA = [
    r"pivot", r"articulation", r"articul[ée]e?s?\b", r"rotule",
    r"glissi[èe]re", r"coulisse(?:au|ment)?", r"coulissante?s?\b",
    r"engrenage", r"pignon", r"denture", r"cr[ée]maill[èe]re",
    r"came\b", r"levier", r"bielle", r"manivelle", r"excentrique",
    r"t[ée]lescop", r"encliquet", r"snap[- ]?fit", r"cliquet", r"rochet",
    r"quart de tour", r"ba[iï]onnette", r"vis[- ]?[ée]crou",
    r"d[ée]ployab", r"d[ée]pliab", r"pliable", r"rabattab", r"charni[èe]re\b",
    r"axe de rotation", r"pi[èe]ce mobile", r"partie mobile",
    r"roulement\b", r"palier lisse", r"liaison pivot", r"degr[ée] de libert",
]
# --- B. DEFORMATION : un corps, grand deplacement elastique ----------------
DEFO = [
    r"compliant", r"flexure", r"lame flexible", r"lame souple", r"col de cygne",
    r"charni[èe]re vivante", r"living hinge", r"bistab", r"multistab",
    r"aux[ée]ti", r"poisson n[ée]gatif", r"negative poisson",
    r"morphing", r"4d printing", r"impression 4d", r"m[ée]moire de forme",
    r"membrane flexible", r"membrane souple", r"ressort", r"[ée]lasticit[ée]",
    r"r[ée]tractab", r"gonflab", r"pr[ée]contrainte [ée]lastique",
    r"se d[ée]forme", r"d[ée]formation [ée]lastique", r"clipsab",
]
MECA_RE = [re.compile(p, re.I) for p in MECA]
DEFO_RE = [re.compile(p, re.I) for p in DEFO]

# --- Principes d'Altshuller de nature cinematique ---------------------------
CINE_CORE = {7, 15, 18, 19, 28, 29, 30, 34}          # le principe EST un mouvement
CINE_EXT = CINE_CORE | {1, 13, 14, 17, 20, 21, 25}   # conduit souvent au mobile


def charge_catalogue():
    import geo_solutions as geo
    ext = ROOT / "scripts" / "backups" / "2026-08-29_apres_adoption_geo_solutions_ext.json"
    sols = {s["id"]: dict(s) for s in geo.SOLUTIONS}
    for e in json.load(io.open(ext, encoding="utf-8")):
        if not e.get("id"):
            continue
        if e["id"] in sols:
            sols[e["id"]].update({k: v for k, v in e.items() if v})
        elif e.get("instruction"):
            sols[e["id"]] = dict(e)
    return list(sols.values())


def _score(regs, s):
    """Marqueur dans le nom = 2 (la solution EST cela) ; ailleurs = 1 (mention)."""
    nom = str(s.get("name", ""))
    corps = str(s.get("desc", "")) + " " + str(s.get("instruction", ""))
    sc = 0
    if any(r.search(nom) for r in regs):
        sc += 2
    if any(r.search(corps) for r in regs):
        sc += 1
    return sc


def classe(s):
    d, m = _score(DEFO_RE, s), _score(MECA_RE, s)
    if max(d, m) < 2:
        return "statique"
    return "deformation" if d >= m else "mecanisme"


def main():
    import invent
    import geo_solutions as geo
    sols = charge_catalogue()
    n = len(sols)
    cls = {s["id"]: classe(s) for s in sols}
    nb = {k: sum(1 for v in cls.values() if v == k)
          for k in ("mecanisme", "deformation", "statique")}
    mobile = nb["mecanisme"] + nb["deformation"]

    print(f"CATALOGUE : {n} solutions\n")
    print("Q1. NATURE DES SOLUTIONS")
    for k in ("mecanisme", "deformation", "statique"):
        print(f"    {k:12s} {nb[k]:4d}  ({100*nb[k]/n:4.1f} %)")
    print(f"    -> exigent du mouvement : {mobile}/{n} = {100*mobile/n:.1f} %")
    pc = sum(1 for s in sols if set(s.get("principles", [])) & CINE_CORE)
    pe = sum(1 for s in sols if set(s.get("principles", [])) & CINE_EXT)
    print(f"    contre-mesure par principes : noyau {100*pc/n:.1f} % | etendu {100*pe/n:.1f} %\n")

    actives = cine_core = cine_ext = 0
    for i in range(1, 40):
        for j in range(1, 40):
            if i == j:
                continue
            prn = {p["number"] for p in invent.principles_for(i, j)}
            if not prn:
                continue
            actives += 1
            cine_core += bool(prn & CINE_CORE)
            cine_ext += bool(prn & CINE_EXT)
    print("Q2. CELLULES OU LA MATRICE CONSEILLE DE METTRE EN MOUVEMENT")
    print(f"    actives {actives} | noyau {cine_core} ({100*cine_core/actives:.1f} %)"
          f" | etendu {cine_ext} ({100*cine_ext/actives:.1f} %)\n")

    geo.SOLUTIONS[:] = sols
    geo._BY_ID = {s["id"]: s for s in sols}
    vus = vus_mob = cell_avec = 0
    for i in range(1, 40):
        for j in range(1, 40):
            if i == j:
                continue
            prn = [p["number"] for p in invent.principles_for(i, j)]
            if not prn:
                continue
            top = geo.cell_solutions(i, j, prn, limit=6)
            if not top:
                continue
            vus += len(top)
            k = sum(1 for t in top if cls.get(t["id"]) != "statique")
            vus_mob += k
            cell_avec += bool(k)
    print("Q3. DANS LE TOP-6 AFFICHE")
    print(f"    propositions {vus} | mobiles rendues figees {vus_mob} "
          f"({100*vus_mob/vus:.1f} %) | cellules concernees {cell_avec} "
          f"({100*cell_avec/actives:.1f} %)\n")

    print("ECHANTILLON AUDITABLE (10 par famille) :")
    for fam in ("mecanisme", "deformation", "statique"):
        print(f"  [{fam}]")
        for s in [x for x in sols if cls[x["id"]] == fam][:10]:
            print("    - " + s["name"][:70])

    (ROOT / "scripts" / "mesure_cinematique.json").write_text(json.dumps({
        "catalogue": n, "familles": nb,
        "part_mobile_lexical": round(100 * mobile / n, 1),
        "part_principes_noyau": round(100 * pc / n, 1),
        "part_principes_etendu": round(100 * pe / n, 1),
        "cellules_actives": actives, "cellules_cine_noyau": cine_core,
        "cellules_cine_etendu": cine_ext,
        "top6_total": vus, "top6_mobiles": vus_mob, "top6_cellules": cell_avec,
        "classification": cls,
    }, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
