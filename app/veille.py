"""VEILLE GÉOMÉTRIQUE — le plus grand commun multiple des solutions d'avant-garde.

Balaye la littérature via l'API Elicit (clé de Denis), puis fait extraire par
Gemini des SOLUTIONS GÉOMÉTRIQUES candidates au format du catalogue (avec le
mapping TRIZ : principes incarnés, paramètres améliorés/dégradés parmi les 39).
Les candidats validés par l'expert rejoignent geo_solutions et se re-propagent
automatiquement sur les 1248 cellules de la matrice géométrique.
"""
import json
import os
import urllib.request

ELICIT_KEY = os.environ.get("ELICIT_API_KEY", "")
ELICIT_URL = "https://elicit.com/api/v1/search"

# Requêtes d'avant-garde (EN : Elicit indexe la littérature anglophone)
QUERIES = [
    "novel lattice metamaterial structures for additive manufacturing lightweight design",
    "auxetic negative Poisson ratio structures 3D printing applications",
    "compliant mechanisms monolithic 3D printed flexure design",
    "capillary microchannel structures passive liquid transport 3D printed",
    "triply periodic minimal surfaces functional applications heat exchanger",
    "bioinspired structural geometry additive manufacturing toughness",
    "4D printing shape morphing structures design",
    "functional surface textures 3D printing friction wettability",
]


def elicit_search(query: str, max_results: int = 8):
    body = json.dumps({"query": query[:500], "searchMode": "semantic",
                       "maxResults": max(1, min(20, max_results))}).encode()
    req = urllib.request.Request(
        ELICIT_URL, data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {ELICIT_KEY}",
                 "User-Agent": "text-to-cad/1.0"})   # urllib par defaut = bloque (403)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode())
    out = []
    for p in (data.get("papers") or data.get("results") or []):
        doi = p.get("doi")
        out.append({"title": p.get("title"), "year": p.get("year"), "doi": doi,
                    "url": p.get("url") or (f"https://doi.org/{doi}" if doi else None),
                    "abstract": (p.get("abstract") or "")[:1200]})
    return out


EXTRACT_SYSTEM = """Tu es un expert TRIZ et conception pour fabrication additive.
On te donne des résumés d'articles scientifiques récents. Extrais-en des SOLUTIONS
GÉOMÉTRIQUES transférables à des pièces CAO imprimées en FDM : des transformations
de géométrie concrètes (pas des matériaux, pas des procédés hors FDM).

Réponds UNIQUEMENT en JSON : {"candidates": [
 {"id": "slug_court_en_snake_case",
  "name": "nom FR court",
  "desc": "en 1-2 phrases FR : la géométrie et ce qu'elle apporte",
  "instruction": "consigne IMPÉRATIVE FR pour transformer une pièce CAO existante
                  selon cette solution (dimensions indicatives en mm)",
  "principles": [n° parmi les 40 principes TRIZ que la solution incarne],
  "improves": [n° parmi les 39 paramètres d'Altshuller améliorés],
  "degrades": [n° des paramètres risqués],
  "sources": [numéros [n] des papiers du corpus dont la solution est tirée] }]}

Rappels : 39 paramètres (1 poids mobile, 2 poids fixe, 9 vitesse, 10 force,
11 contrainte/pression, 12 forme, 13 stabilité, 14 résistance, 17 température,
23 pertes de matière, 27 fiabilité, 30 facteurs nuisibles externes, 31 effets
nuisibles induits, 32 fabricabilité, 33 facilité d'usage, 34 réparabilité,
35 adaptabilité, 36 complexité, 39 productivité). 40 principes (1 segmentation,
3 qualité locale, 4 asymétrie, 7 poupées russes, 14 sphéricité, 15 dynamisation,
17 autre dimension, 29 pneumatique/hydraulique, 30 membranes flexibles,
31 matériaux poreux, 35 modification de propriétés, 40 composites...).
2 à 6 candidats MAXIMUM, uniquement les plus originaux et actionnables ;
ignore ce qui n'est pas géométrique."""


def extract_candidates(papers):
    """Gemini transforme un lot de résumés en solutions candidates étiquetées TRIZ.
    Les sources sont référencées par NUMÉRO puis résolues (titre + lien DOI)."""
    import llm
    from google.genai import types
    corpus = "\n\n".join(
        f"[{i+1}] {p['title']} ({p.get('year','?')})\n{p.get('abstract','')}"
        for i, p in enumerate(papers) if p.get("title"))
    cfg = types.GenerateContentConfig(
        system_instruction=EXTRACT_SYSTEM, temperature=0.3,
        response_mime_type="application/json",
        **({"thinking_config": types.ThinkingConfig(thinking_level=llm.THINKING)}
           if "gemini-3" in llm.MODEL else {}))
    resp = llm._get_client().models.generate_content(
        model=llm.MODEL, contents=corpus[:60000], config=cfg)
    data = llm._extract_json(resp.text)
    cands = data.get("candidates", []) if isinstance(data, dict) else []
    for c in cands:                        # résolution n° -> {titre, année, lien}
        src = []
        for s in (c.get("sources") or []):
            try:
                p = papers[int(s) - 1]
                src.append({"title": p.get("title"), "year": p.get("year"),
                            "url": p.get("url")})
            except Exception:
                if isinstance(s, str):
                    src.append({"title": s, "year": None, "url": None})
        c["sources"] = src
    return cands


def harvest(queries=None, per_query=10):
    """Balayage complet : requêtes Elicit -> dédoublonnage -> extraction Gemini."""
    if not ELICIT_KEY:
        return {"ok": False, "error": "ELICIT_API_KEY non configurée."}
    papers, seen, errors = [], set(), []
    for q in (queries or QUERIES):
        try:
            for p in elicit_search(q, per_query):
                key = (p.get("doi") or p.get("title") or "").lower()
                if key and key not in seen:
                    seen.add(key)
                    papers.append(p)
        except Exception as e:
            errors.append(f"{q[:40]}: {str(e)[:80]}")
    if not papers:
        return {"ok": False, "error": "Aucun papier récupéré. " + " ; ".join(errors[:3])}
    # extraction par lots de 12 résumés
    candidates = []
    for i in range(0, len(papers), 12):
        try:
            candidates += extract_candidates(papers[i:i + 12])
        except Exception as e:
            errors.append(f"extraction: {str(e)[:80]}")
    # nettoyage minimal
    clean, ids = [], set()
    for c in candidates:
        cid = str(c.get("id") or "").strip()
        if not cid or cid in ids or not c.get("instruction"):
            continue
        ids.add(cid)
        clean.append({"id": cid, "kind": "llm", "name": c.get("name", cid),
                      "desc": c.get("desc", ""), "instruction": c["instruction"],
                      "principles": [int(x) for x in c.get("principles", []) if 1 <= int(x) <= 40],
                      "improves": [int(x) for x in c.get("improves", []) if 1 <= int(x) <= 39],
                      "degrades": [int(x) for x in c.get("degrades", []) if 1 <= int(x) <= 39],
                      "sources": c.get("sources", [])})
    return {"ok": True, "papers": len(papers), "candidates": clean,
            "errors": errors[:5]}
