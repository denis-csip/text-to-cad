# -*- coding: utf-8 -*-
"""ANALYSE TRIZ D'UN ARTICLE — protocole de Denis (2026-09-10).

Rupture avec l'extraction précédente : on n'étiquette plus une solution par
son VOCABULAIRE, on étiquette la TRANSFORMATION (avant → après). Les principes
observés et la contradiction sont analysés INDÉPENDAMMENT ; la matrice n'est
consultée qu'ensuite, PAR NOUS (déterministe), et l'écart entre la solution
réelle et la recommandation d'Altshuller est CONSERVÉ comme information.

Un article -> une analyse structurée -> (si exploitable) une solution du
catalogue placée dans les SEULES cellules de ses contradictions déclarées
(paires ↑/↓), jamais dans le produit cartésien de listes.
"""
import json

PROTOCOLE = """Tu analyses une solution technique issue d'un article scientifique afin de
déterminer quels principes inventifs TRIZ elle met réellement en œuvre.
Ne classe jamais une solution sur la simple présence de mots, objets, phénomènes
ou technologies associés à un principe TRIZ. Un principe inventif décrit la
TRANSFORMATION qui permet de passer d'une solution conventionnelle à la solution
nouvelle.

ÉTAPE 1 — RECONSTRUIRE LA SOLUTION. Écris obligatoirement :
AVANT : comment le problème est-il normalement traité ?
PROBLÈME : quelle limitation de cette approche cherche-t-on à dépasser ?
TRANSFORMATION : qu'est-ce qui a réellement été modifié, ajouté, supprimé,
déplacé, séparé, rendu variable ou réorganisé ?
APRÈS : quelle architecture ou quel fonctionnement nouveau obtient-on ?
Ne poursuis pas l'analyse si la transformation ne peut pas être explicitée
(mets alors "exploitable": false et explique pourquoi dans "raison").

ÉTAPE 2 — PRINCIPES INVENTIFS OBSERVÉS. Cherche le principe TRIZ qui décrit le
mieux la TRANSFORMATION, et non le domaine technologique. Attribue un principe
DOMINANT et éventuellement jusqu'à deux principes SECONDAIRES. Pour chacun :
numéro, nom, justification causale en une phrase, confiance entre 0 et 1.
N'étiquette pas un principe avec une confiance inférieure à 0,60.
Attention aux faux positifs :
P3 Qualité locale : pas parce qu'un phénomène est local ; il faut que différentes
zones ou parties soient volontairement adaptées à des conditions ou fonctions
différentes.
P15 Dynamisation : pas parce qu'un paramètre varie ; le système, un élément ou
son environnement doit devenir adaptable, réglable, mobile ou configurable au
cours du fonctionnement.
P17 Autre dimension : pas pour toute géométrie 3D ou fabrication additive ; il
doit exister une réelle exploitation d'une dimension, orientation ou
organisation spatiale supplémentaire.
P31 Matériaux poreux : pas parce que le matériau contient une mousse ou des
cellules ; la porosité doit constituer le mécanisme de résolution.
P35 Changement de paramètres : ne pas confondre optimisation de paramètres et
principe inventif ; un changement de température, pression, concentration,
densité ou propriété ne constitue P35 que s'il est lui-même le mécanisme
permettant de dépasser la contradiction.
P40 Matériaux composites : pas dès que plusieurs matériaux sont présents ; la
combinaison de matériaux aux propriétés complémentaires doit constituer la
stratégie de résolution.

ÉTAPE 3 — ANALYSER LA CONTRADICTION INDÉPENDAMMENT. Ignore maintenant les
principes trouvés. À partir du problème décrit, cherche une contradiction
technique de la forme « Si nous améliorons X par l'action A, alors Y se
détériore. » X = paramètre d'Altshuller amélioré, Y = paramètre dégradé. Chaque
contradiction = UNE PAIRE (améliore ↑ / dégrade ↓). Ne crée jamais des listes
dont toutes les combinaisons seraient des contradictions. Maximum trois
contradictions. Pour chacune : phrase causale, paramètre amélioré, paramètre
dégradé, preuve provenant de l'article, confiance. Si aucun paramètre ne se
détériore réellement : "contradictions": [] et "aucune_contradiction": true.
N'invente JAMAIS un paramètre dégradé pour positionner la solution.

ÉTAPE 4 — CONTRADICTION PHYSIQUE. Le problème peut-il se formuler « un même
élément doit avoir la propriété A et la propriété opposée non-A » ? Si oui,
quelle séparation la solution utilise-t-elle : espace, temps, tout/parties,
conditions ? Indépendant de la matrice.

NE CONSULTE PAS la matrice toi-même : la comparaison avec les principes
recommandés est faite ensuite, hors de ta réponse. Ne modifie ni les principes
observés ni les paramètres pour améliorer une concordance.

Les 39 paramètres d'Altshuller : {PARAMETRES}
Les 40 principes inventifs : {PRINCIPES}
{DIALECTE}

Réponds UNIQUEMENT en JSON :
{{"exploitable": true|false, "raison": "si non exploitable",
  "resume_inventif": "2 phrases FR",
  "avant": "...", "probleme": "...", "transformation": "...", "apres": "...",
  "dominant": {{"numero": n, "nom": "...", "justification": "...", "confiance": 0.0}},
  "secondaires": [{{"numero": n, "nom": "...", "justification": "...", "confiance": 0.0}}],
  "contradictions": [{{"phrase": "Si nous améliorons X par A, alors Y se détériore.",
                       "ameliore": n, "degrade": n, "preuve": "citation ou paraphrase de l'article",
                       "confiance": 0.0}}],
  "aucune_contradiction": false,
  "contradiction_physique": {{"presente": true|false, "enonce": "A et non-A", "separation": "espace|temps|tout-parties|conditions|aucune"}},
  "nom_solution": "nom FR court de la solution (5-8 mots)",
  "instruction": "consigne IMPÉRATIVE FR pour appliquer la transformation à une pièce ou un procédé (indicatif)",
  "portee": "cao"|"procede"|"matiere"
}}"""


def prompt_pour(discipline_id="plasturgie"):
    import invent
    import disciplines as d
    p40 = "\n".join(f"{n}. {p.get('label','')}" for n, p in sorted(invent.PRINCIPLES.items()))
    p39 = " ; ".join(f"{p['number']} {p['fr']}" for p in invent.PARAMETERS)
    dd = d.get(discipline_id)
    gl = dd.get("gloses") or {}
    dial = ("Dialecte du métier pour les paramètres : "
            + " ; ".join(f"{n} = {g}" for n, g in sorted(gl.items()))) if gl else ""
    return PROTOCOLE.format(PARAMETRES=p39, PRINCIPES=p40, DIALECTE=dial)


def analyser_article(paper, discipline_id="plasturgie", temperature=0.2):
    """Un article -> analyse structurée (Gemini, JSON). Renvoie (dict, usage)."""
    import llm
    from google.genai import types
    corpus = (f"TITRE : {paper.get('title')}\nANNÉE : {paper.get('year')}\n"
              f"RÉSUMÉ :\n{paper.get('abstract','')}")
    cfg = types.GenerateContentConfig(
        system_instruction=prompt_pour(discipline_id), temperature=temperature,
        response_mime_type="application/json",
        **({"thinking_config": types.ThinkingConfig(thinking_level=llm.THINKING)}
           if "gemini-3" in llm.MODEL else {}))
    resp = llm._get_client().models.generate_content(
        model=llm.MODEL, contents=corpus, config=cfg)
    data = llm._extract_json(resp.text)
    um = getattr(resp, "usage_metadata", None)
    usage = {"in": getattr(um, "prompt_token_count", 0) or 0,
             "out": getattr(um, "candidates_token_count", 0) or 0}
    return (data if isinstance(data, dict) else {}), usage


def concordance(analyse):
    """ÉTAPE 5, déterministe : principes observés vs recommandés par la matrice
    pour la contradiction PRINCIPALE. Aucune des deux listes n'est modifiée."""
    import invent
    obs = []
    d = analyse.get("dominant") or {}
    if d.get("numero") and float(d.get("confiance", 0) or 0) >= 0.6:
        obs.append(int(d["numero"]))
    sec = [int(s["numero"]) for s in (analyse.get("secondaires") or [])
           if s.get("numero") and float(s.get("confiance", 0) or 0) >= 0.6][:2]
    cons = [c for c in (analyse.get("contradictions") or [])
            if c.get("ameliore") and c.get("degrade")]
    if not cons:
        return {"conclusion": "contradiction indéterminée", "recommandes": [],
                "observes": obs + sec, "cellule": None}
    c0 = max(cons, key=lambda c: float(c.get("confiance", 0) or 0))
    i, j = int(c0["ameliore"]), int(c0["degrade"])
    rec = [p["number"] for p in invent.principles_for(i, j)]
    if obs and obs[0] in rec:
        concl = "concordance forte"
    elif any(p in rec for p in sec):
        concl = "concordance partielle"
    else:
        concl = "hors recommandations de la matrice"
    return {"conclusion": concl, "recommandes": rec, "observes": obs + sec,
            "cellule": [i, j], "dominant_recommande": bool(obs and obs[0] in rec)}


def vers_solution(analyse, paper, discipline_id, sid):
    """Analyse -> entrée de catalogue. Placement STRICT par paires de
    contradiction (improves/degrades gardés pour compatibilité = les paires)."""
    d = analyse.get("dominant") or {}
    prins, conf = [], {}
    if d.get("numero") and float(d.get("confiance", 0) or 0) >= 0.6:
        prins.append(int(d["numero"])); conf[int(d["numero"])] = float(d["confiance"])
    for s in (analyse.get("secondaires") or [])[:2]:
        if s.get("numero") and float(s.get("confiance", 0) or 0) >= 0.6:
            n = int(s["numero"]); prins.append(n); conf[n] = float(s["confiance"])
    pairs = [{"up": int(c["ameliore"]), "down": int(c["degrade"]),
              "confiance": float(c.get("confiance", 0) or 0), "phrase": c.get("phrase", ""),
              "preuve": c.get("preuve", "")}
             for c in (analyse.get("contradictions") or [])
             if c.get("ameliore") and c.get("degrade")][:3]
    conc = concordance(analyse)
    return {"id": sid, "kind": "llm", "discipline": discipline_id,
            "name": analyse.get("nom_solution") or (paper.get("title") or sid)[:80],
            "desc": analyse.get("resume_inventif", ""),
            "instruction": analyse.get("instruction", ""),
            "portee": analyse.get("portee") if analyse.get("portee") in ("cao", "procede", "matiere") else "procede",
            "principles": prins, "confiance_principes": conf,
            "dominant": int(d["numero"]) if prins else None,
            "contradictions": pairs,
            "improves": sorted({p["up"] for p in pairs}),
            "degrades": sorted({p["down"] for p in pairs}),
            "physique": analyse.get("contradiction_physique") or {},
            "avant": analyse.get("avant", ""), "transformation": analyse.get("transformation", ""),
            "apres": analyse.get("apres", ""),
            "concordance": conc,
            "sources": [{"title": paper.get("title"), "year": paper.get("year"),
                         "url": paper.get("url")}],
            "methode": "protocole-transformation-2026-09-10"}
