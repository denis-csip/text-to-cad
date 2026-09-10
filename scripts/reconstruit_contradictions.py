# -*- coding: utf-8 -*-
"""RECONSTRUCTION des affectations aux cellules (consignes de Denis, 2026-09-10).

Constat : 42 articles -> 29 cellules = contradictions trop locales, dependantes
de chaque article (inconvenient INDUIT par la solution, ex. « plus complexe »).
Regle nouvelle : la contradiction est reconstruite depuis le PROBLEME INITIAL
(AVANT + PROBLEME), sous la forme « Pour ameliorer A, il faudrait faire X, mais
faire X deteriore B », puis les articles sont REGROUPES par famille de PROBLEME
(pas de technologie) et convergent vers la meme cellule.

Passage 1 (par article, LLM)  : contradiction generique + mapping canonique
   argumente + statut A VALID_MATRIX_CELL / B PHYSICAL_CONTRADICTION_ONLY /
   C NO_TECHNICAL_CONTRADICTION / D NOT_ENOUGH_EVIDENCE.
Passage 2 (global, LLM)       : familles de contradiction, fusion des cellules
   dispersees (justification physique ou fusion), avertissements de coherence.
Passage 3 (deterministe)      : cellules proposees, distributions DOMINANT puis
   SECONDAIRES separees, statuts ANECDOTAL/EMERGING/SUPPORTED/STRONG.
Cout : plafond --cap (defaut 0,25 $).
"""
import io
import json
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")


def _arg(n, d):
    return sys.argv[sys.argv.index(n) + 1] if n in sys.argv else d


DISC = _arg("--discipline", "plasturgie")
CAP = float(_arg("--cap", "0.25"))
PRIX_IN, PRIX_OUT = 0.30e-6, 2.5e-6

P1_SYSTEM = """Tu es un expert TRIZ. On te donne l'analyse DEJA FAITE d'un article
(AVANT, PROBLEME, puis TRANSFORMATION, APRES) et la liste canonique des 39
parametres d'Altshuller AVEC leurs definitions.

Ta tache : reconstruire la CONTRADICTION D'INGENIERIE GENERIQUE que la solution
resout, a partir UNIQUEMENT du PROBLEME INITIAL (AVANT + PROBLEME). Ignore
temporairement la solution. Une contradiction Altshuller ne decrit PAS quel
inconvenient nouveau la solution introduit ; elle decrit le compromis qui
empechait la solution conventionnelle de satisfaire les deux exigences AVANT
l'invention.
INTERDIT : « la solution X reduit le temps de cycle mais rend le moule plus
complexe ». ATTENDU : « pour refroidir vite il faudrait placer le canal pres de
la cavite, mais cette proximite compromet la tenue du moule ».

Ecris :
OBJECTIF A (ce que l'ingenieur veut ameliorer) ; ACTION CONVENTIONNELLE X (ce
qu'il faudrait normalement faire) ; CONSEQUENCE INDESIRABLE B.
Phrase obligatoire : « Pour ameliorer A, il faudrait faire X, mais faire X
deteriore B. » Si elle n'est pas causalement defendable -> NO_TECHNICAL_CONTRADICTION.

Mapping STRICT sur les 39 parametres canoniques (definitions fournies), avec
MAPPING_REASON et CONFIDENCE (0-1) pour chacun. Si le phenomene ne correspond
pas assez a un parametre historique -> NO_MATRIX_MAPPING (n'invente rien).
Parametres actuellement SUR-UTILISES, a n'employer que si le conflit INITIAL
porte reellement sur cette grandeur : 25 perte de temps, 32 fabricabilite,
36 complexite du dispositif, 37 complexite du controle, 39 productivite.
INTERDIT : « solution plus complexe » -> 36 ; « difficile a fabriquer » -> 32 ;
« plus de calcul » -> 37 ; « plus rapide » -> 39.
NUANCE (calibree) : 25 est LEGITIME quand le temps EST l'activite requise du
conflit initial (duree de refroidissement, temps d'assemblage, temps de cycle
d'un procede physique) ; il est ILLEGITIME pour du temps de calcul, de
simulation ou de collecte de donnees.
AMBIGUITE : quand la distance semantique d'un parametre est MEDIUM, donne aussi
le MEILLEUR AUTRE CANDIDAT dans "improve_alt" / "worsen_alt" ({id, name,
reason}) — l'expert tranchera ; ne choisis pas au hasard.

Contradiction PHYSIQUE (separee) : « un meme element doit etre A et non-A »
(ex. moule CHAUD au remplissage ET FROID a la solidification = separation dans
le temps). Si la contradiction physique est forte et que le mapping 39x39 est
artificiel -> statut PHYSICAL_CONTRADICTION_ONLY (l'article ne peuple pas de
cellule). Ce n'est pas un echec.

PROTOCOLE STABILISE (calibration validee par l'expert le 2026-09-10) :
- A = une PERFORMANCE (reduire la duree de refroidissement, augmenter la
  resistance, reduire la masse, ameliorer la precision de mesure...), JAMAIS un
  moyen (creer des canaux conformes, utiliser un composite, augmenter la fraction
  recyclee, appliquer un algorithme).
- B est INVALIDE s'il n'est qu'un cout de la solution nouvelle, une complexite
  apparue apres l'invention, une difficulte de fabrication de la solution
  nouvelle, une condition geometrique preexistante, ou un parametre mentionne
  sans etre causalement deteriore.
- CONDITION IMPOSEE ≠ PARAMETRE DEGRADE : geometrie complexe, forme requise,
  recyclabilite, usage de matiere recyclee, reglementation, environnement
  corrosif, peu de donnees = CONTEXTE du probleme, pas un parametre qui « se
  deteriore ». Ne les transforme pas en 12 Forme, 26 Quantite de substance,
  32 Fabricabilite. Ex. valide : « fraction recyclee » n'a PAS de correspondant
  canonique (26 = consommation de materiaux) -> pas de cellule.
- MAPPING : pour chaque parametre donne SEMANTIC_DISTANCE LOW/MEDIUM/HIGH par
  rapport a la DEFINITION canonique. Si HIGH pour l'un des deux -> statut
  E VALID_PROBLEM_FAMILY_NO_ALTSHULLER_CELL (probleme legitime, pas de cellule).
- IA / logiciel / mesure : temps de calcul, volume de donnees, complexite
  algorithmique, automatisation, precision de PREDICTION (≠ 28 precision de
  MESURE) ne se forcent pas dans 25, 28, 36, 37 -> statut E.
- Hors discipline (biologie, microfluidique, fabrication metallique...) ->
  statut F EXCLUDED_OUT_OF_DISCIPLINE.
- Exemple calibre : refroidissement conforme = UNE contradiction « pour reduire
  la duree de refroidissement (25) il faudrait rapprocher/multiplier les canaux,
  mais la paroi canal-cavite amincie deteriore la tenue du moule (14) » ->
  [25,14] ; « les canaux conformes deforment la piece » [17,12] est un
  inconvenient induit = INTERDIT.

STATUT final : A VALID_MATRIX_CELL | B PHYSICAL_CONTRADICTION_ONLY |
C NO_TECHNICAL_CONTRADICTION | D NOT_ENOUGH_EVIDENCE |
E VALID_PROBLEM_FAMILY_NO_ALTSHULLER_CELL | F EXCLUDED_OUT_OF_DISCIPLINE.
Ajoute dans improve/worsen le champ "semantic_distance": "LOW|MEDIUM|HIGH".

Reponds UNIQUEMENT en JSON :
{"objectif_A": "...", "action_X": "...", "consequence_B": "...",
 "phrase": "Pour ameliorer ..., il faudrait ..., mais ... deteriore ...",
 "probleme_generique": "1 phrase decrivant le conflit d'ingenierie, SANS nommer la technologie de solution",
 "improve": {"id": n|null, "name": "...", "reason": "...", "confidence": 0-1, "semantic_distance": "LOW|MEDIUM|HIGH"},
 "worsen":  {"id": n|null, "name": "...", "reason": "...", "confidence": 0-1, "semantic_distance": "LOW|MEDIUM|HIGH"},
 "improve_alt": {"id": n, "name": "...", "reason": "..."} | null,
 "worsen_alt":  {"id": n, "name": "...", "reason": "..."} | null,
 "physical": {"present": bool, "statement": "...", "separation": "time|space|conditions|whole-parts|none"},
 "status": "A|B|C|D", "status_reason": "..."}"""

P2_SYSTEM = """Tu es un expert TRIZ. On te donne, pour N articles, le PROBLEME
GENERIQUE reconstruit, la contradiction « Pour ameliorer A il faudrait X mais X
deteriore B », et la cellule [IMPROVE, WORSEN] proposee.

Passage GLOBAL obligatoire :
1. Regroupe les articles qui traitent ESSENTIELLEMENT du meme conflit
   d'ingenierie en FAMILLES DE CONTRADICTION (definies par le PROBLEME, jamais
   par la technologie de solution). Ex. FAMILY_CONTRADICTION_CC1 « refroidir
   vite/uniformement une geometrie complexe sans compromettre les contraintes
   du moule » ; FOAM1 « reduire la matiere/masse en conservant les proprietes » ;
   RECYCLE1 « augmenter la fraction recyclee en preservant les proprietes ».
2. Pour chaque famille, fixe UNE contradiction generique et UNE cellule
   [improve, worsen] canonique. Deux articles d'une meme famille recoivent la
   meme cellule, sauf preuve explicite d'un compromis different : dans ce cas
   justifie physiquement ; sans justification claire, FUSIONNE vers la cellule
   la mieux justifiee. Signale chaque fusion.
3. COHERENCE_WARNINGS : familles qui restent ambigues (mapping discutable,
   parametre sur-utilise, articles a cheval sur deux familles).
4. AUDIT DE CHAQUE FAMILLE (protocole stabilise) : A = performance (pas un
   moyen) ; action conventionnelle ; B causalement deteriore AVANT l'invention
   (jamais un inconvenient induit par la solution) ; SEMANTIC_DISTANCE des deux
   parametres (HIGH -> famille VALID_PROBLEM_FAMILY_NO_ALTSHULLER_CELL, sans
   cellule) ; condition imposee (recycle, geometrie complexe, reglementation)
   ≠ parametre degrade. Deux familles au meme probleme initial (ex. refroidissement
   conforme « tenue du moule » vs « geometrie ») DOIVENT fusionner si la seconde
   n'est qu'un inconvenient induit.
N'invente jamais de contradiction pour remplir davantage la matrice.
Une matrice de 15 cellules solides vaut mieux que 30 cellules fabriquees.

Reponds UNIQUEMENT en JSON :
{"families": [{"family_id": "FAMILY_CONTRADICTION_XXX1", "generic_problem": "...",
   "generic_contradiction": "Pour ameliorer ... il faudrait ... mais ... deteriore ...",
   "improve": n|null, "worsen": n|null, "article_ids": ["..."],
   "status": "VALID_MATRIX_CELL|VALID_PROBLEM_FAMILY_NO_ALTSHULLER_CELL|PHYSICAL_CONTRADICTION_ONLY",
   "semantic_distance": {"improve": "LOW|MEDIUM|HIGH", "worsen": "LOW|MEDIUM|HIGH"},
   "mapping_confidence": 0-1,
   "merged_from_cells": [[i,j], ...], "merge_justification": "..."}],
 "kept_distinct": [{"article_ids": ["...","..."], "why_cells_differ": "justification physique"}],
 "coherence_warnings": ["..."]}"""


def main():
    import invent
    import llm
    from google.genai import types
    defs = json.load(io.open(ROOT / "app" / "parametres_definitions.json", encoding="utf-8"))
    canon = "\n".join(f"{p['number']}. {defs.get(str(p['number']), p['fr'])}" for p in invent.PARAMETERS)
    PN = {p["number"]: p["fr"] for p in invent.PARAMETERS}
    PL = {n: p.get("label", "") for n, p in invent.PRINCIPLES.items()}
    recs = {}
    for l in io.open(ROOT / "scripts" / f"analyses_{DISC}.jsonl", encoding="utf-8"):
        r = json.loads(l)
        p = r.get("paper") or {}
        recs[r.get("article_id") or p.get("doi") or p.get("url") or p.get("title")] = r
    # --all : TOUTES les analyses exploitables (mode corpus) ; sinon les articles
    # affectes par la matrice deterministe du pilote (mode historique).
    if "--all" in sys.argv:
        ids = sorted(a for a, r in recs.items() if (r.get("analyse") or {}).get("exploitable"))
        old_cells = {}
    else:
        old = json.load(io.open(ROOT / "scripts" / f"matrice_empirique_{DISC}.json", encoding="utf-8"))
        old_ass = old["MATRIX_ASSIGNMENTS"]
        ids = sorted({e["article_id"] for e in old_ass})
        old_cells = {e["article_id"]: (e["improve_parameter"]["id"], e["worsening_parameter"]["id"])
                     for e in old_ass if e["assignment_status"] == "validated"}
    OUT_SUFFIX = (sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "")
    print(f"{DISC} : {len(ids)} articles affectes a reconstruire | plafond {CAP:.2f} $", flush=True)
    etat = {"cout": 0.0, "stop": False, "n": 0}
    lock = threading.Lock()

    def cfg(system):
        return types.GenerateContentConfig(
            system_instruction=system, temperature=0.1, response_mime_type="application/json",
            **({"thinking_config": types.ThinkingConfig(thinking_level=llm.THINKING)} if "gemini-3" in llm.MODEL else {}))

    def call(system, user):
        resp = llm._get_client().models.generate_content(model=llm.MODEL, contents=user, config=cfg(system))
        u = getattr(resp, "usage_metadata", None)
        ti, to = int(getattr(u, "prompt_token_count", 0) or 0), int(getattr(u, "candidates_token_count", 0) or 0)
        with lock:
            etat["cout"] += ti * PRIX_IN + to * PRIX_OUT
            if etat["cout"] >= CAP:
                etat["stop"] = True
        return llm._extract_json(resp.text) or {}

    # ---------------- passage 1 : par article ----------------
    def p1(aid):
        if etat["stop"]:
            return aid, None
        a = recs[aid]["analyse"]; p = recs[aid].get("paper") or {}
        user = ("PARAMETRES CANONIQUES :\n" + canon + f"\n\nARTICLE : {p.get('title')} ({p.get('year')})\n"
                f"AVANT : {a.get('avant')}\nPROBLEME : {a.get('probleme')}\n"
                f"(pour information seulement, apres avoir formule la contradiction) TRANSFORMATION : {a.get('transformation')}\nAPRES : {a.get('apres')}")
        try:
            d = call(P1_SYSTEM, user)
        except Exception as e:
            print("  KO", str(e)[:90], flush=True); return aid, None
        with lock:
            etat["n"] += 1
            if etat["n"] % 10 == 0:
                print(f"  passage 1 : {etat['n']}/{len(ids)} — cumul {etat['cout']:.3f} $", flush=True)
        return aid, d

    t0 = time.time()
    stage1 = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for aid, d in ex.map(p1, ids):
            if d:
                stage1[aid] = d
    # ---------------- passage 2 : global ----------------
    def cell_of(d):
        i = (d.get("improve") or {}).get("id"); j = (d.get("worsen") or {}).get("id")
        return (i, j) if isinstance(i, int) and isinstance(j, int) and 1 <= i <= 39 and 1 <= j <= 39 and i != j else None
    lignes = []
    for aid, d in stage1.items():
        if d.get("status") != "A":
            continue
        c = cell_of(d)
        lignes.append({"id": aid, "title": (recs[aid].get("paper") or {}).get("title", "")[:100],
                       "probleme_generique": d.get("probleme_generique"), "phrase": d.get("phrase"),
                       "cell": list(c) if c else None,
                       "improve_reason": (d.get("improve") or {}).get("reason"),
                       "worsen_reason": (d.get("worsen") or {}).get("reason")})
    stage2 = {}
    if lignes and not etat["stop"]:
        user = "PARAMETRES : " + " ; ".join(f"{n} {PN[n]}" for n in PN) + "\n\nARTICLES (statut A) :\n" + json.dumps(lignes, ensure_ascii=False)
        try:
            stage2 = call(P2_SYSTEM, user)
        except Exception as e:
            print("  passage 2 KO", str(e)[:90], flush=True)
    # ---------------- passage 3 : deterministe ----------------
    fam_of = {}
    families = stage2.get("families") or []
    for f in families:
        for aid in f.get("article_ids") or []:
            fam_of[aid] = f
    final = {}
    for aid, d in stage1.items():
        st = d.get("status", "D")
        f = fam_of.get(aid)
        c = None
        if st == "A":
            if f and isinstance(f.get("improve"), int) and isinstance(f.get("worsen"), int):
                c = (f["improve"], f["worsen"])
            else:
                c = cell_of(d)
            if c is None:
                st = "C"                       # mapping impossible -> pas de cellule
        final[aid] = {"status": st, "cell": c, "family": (f or {}).get("family_id"),
                      "phrase": d.get("phrase"), "probleme_generique": d.get("probleme_generique"),
                      "physical": d.get("physical"), "status_reason": d.get("status_reason"),
                      "improve": d.get("improve"), "worsen": d.get("worsen")}
    a_dom = {aid: ((recs[aid]["analyse"].get("dominant") or {}).get("numero")) for aid in stage1}
    a_sec = {aid: [s.get("numero") for s in (recs[aid]["analyse"].get("secondaires") or [])[:2] if s.get("numero")] for aid in stage1}
    cells = defaultdict(list)
    for aid, v in final.items():
        if v["status"] == "A" and v["cell"]:
            cells[v["cell"]].append(aid)
    proposed = []
    for (i, j), arts in sorted(cells.items(), key=lambda kv: -len(kv[1])):
        fams = {final[a]["family"] for a in arts if final[a]["family"]}
        dom = Counter(a_dom[a] for a in arts if a_dom[a])
        sec = Counter(s for a in arts for s in a_sec[a])
        hist = [p["number"] for p in invent.principles_for(i, j)]
        n, nf = len(arts), max(1, len(fams))
        status = ("STRONG_EMPIRICAL_CELL" if n >= 8 and nf >= 3 else "SUPPORTED" if n >= 4 and nf >= 2
                  else "EMERGING" if n >= 2 else "ANECDOTAL")
        gen = next((f["generic_contradiction"] for f in families if (f.get("improve"), f.get("worsen")) == (i, j)), None)
        proposed.append({"CELL": [i, j], "improve": PN[i], "worsening": PN[j],
                         "GENERIC_CONTRADICTION": gen or final[arts[0]]["phrase"],
                         "N_ARTICLES": n, "ARTICLE_IDS": arts, "N_PROBLEM_FAMILIES": len(fams),
                         "families": sorted(fams),
                         "DOMINANT_EMPIRICAL_PRINCIPLES": {f"P{k} {PL.get(k)}": v for k, v in dom.most_common()},
                         "SECONDARY_EMPIRICAL_DISTRIBUTION": {f"P{k} {PL.get(k)}": v for k, v in sec.most_common()},
                         "HISTORICAL_PRINCIPLES": hist,
                         "OVERLAP_DOMINANT": [k for k in dom if k in hist],
                         "OVERLAP_ANY": sorted({k for k in list(dom) + list(sec) if k in hist}),
                         "CONFIDENCE": ("HIGH" if status in ("STRONG_EMPIRICAL_CELL", "SUPPORTED") else "MEDIUM" if status == "EMERGING" else "LOW"),
                         "STATUS": status})
    # GARDE ANTI-INVERSION : si une meme paire apparait dans les deux sens
    # [i,j] et [j,i], on force l'orientation MAJORITAIRE (et on le journalise).
    inversions = []
    for (i, j) in list(cells.keys()):
        if (j, i) in cells and i < j:
            a, b = cells[(i, j)], cells[(j, i)]
            keep, drop = ((i, j), (j, i)) if len(a) >= len(b) else ((j, i), (i, j))
            for aid in cells[drop]:
                final[aid]["cell"] = keep; final[aid]["inversion_corrigee"] = True
            cells[keep] = cells[keep] + cells[drop]; del cells[drop]
            inversions.append({"garde": list(keep), "ecarte": list(drop), "articles_deplaces": len(cells[keep]) - len(a if keep == (i, j) else b)})
    statuts = Counter(v["status"] for v in final.values())
    summary = {"ancien_articles_affectes": len(old_cells), "anciennes_cellules": len(set(old_cells.values())),
               "nouveaux_articles_affectes": sum(1 for v in final.values() if v["status"] == "A" and v["cell"]),
               "nouvelles_cellules": len(cells),
               "physical_contradiction_only": statuts.get("B", 0), "no_technical_contradiction": statuts.get("C", 0),
               "not_enough_evidence": statuts.get("D", 0),
               "valid_problem_no_altshuller_cell": statuts.get("E", 0), "excluded_out_of_discipline": statuts.get("F", 0),
               "inversions_corrigees": inversions, "articles_sans_reponse_llm": len(ids) - len(stage1),
               "familles": len(families), "fusions": sum(len(f.get("merged_from_cells") or []) for f in families),
               "cout_reel": round(etat["cout"], 4), "duree_s": round(time.time() - t0)}
    fam_out = [{"FAMILY_ID": f.get("family_id"), "GENERIC_PROBLEM": f.get("generic_problem"),
                "GENERIC_CONTRADICTION": f.get("generic_contradiction"),
                "IMPROVE_PARAMETER": {"id": f.get("improve"), "name": PN.get(f.get("improve"))},
                "WORSENING_PARAMETER": {"id": f.get("worsen"), "name": PN.get(f.get("worsen"))},
                "ARTICLE_IDS": f.get("article_ids") or [],
                "DOMINANT_PRINCIPLES_OBSERVED": {f"P{k} {PL.get(k)}": v for k, v in Counter(a_dom.get(a) for a in (f.get("article_ids") or []) if a_dom.get(a)).most_common()},
                "merged_from_cells": f.get("merged_from_cells"), "merge_justification": f.get("merge_justification")}
               for f in families]
    out = {"RECLASSIFICATION_SUMMARY": summary, "NORMALIZED_CONTRADICTION_FAMILIES": fam_out,
           "COHERENCE_WARNINGS": stage2.get("coherence_warnings") or [], "KEPT_DISTINCT": stage2.get("kept_distinct") or [],
           "PROPOSED_EMPIRICAL_CELLS": proposed, "PER_ARTICLE": final, "STAGE1": stage1}
    (ROOT / "scripts" / f"reconstruction_{DISC}{OUT_SUFFIX}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
