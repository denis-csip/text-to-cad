"""MATRICE GÉOMÉTRIQUE — ré-instanciation de la matrice d'Altshuller.

Chaque cellule (paramètre amélioré × paramètre dégradé) n'est plus remplie de
principes abstraits mais de SOLUTIONS GÉOMÉTRIQUES : des reconsidérations
concrètes d'un modèle CAO, prêtes à exécuter (déterministes — lattices — ou
opérées par le LLM). Le remplissage des 1248 cellules est AUTOMATIQUE :
- chaque solution déclare les principes d'Altshuller qu'elle INCARNE et les
  paramètres qu'elle AMÉLIORE / RISQUE de dégrader ;
- pour une cellule, les solutions incarnant les principes de la cellule
  (matrice vérifiée) passent en tête — la couche géométrique reste fidèle à
  la donnée historique collationnée.
"""

# Groupes de paramètres (numérotation des 39 d'Altshuller)
W = [1, 2]            # poids
LEN = [3, 4]          # longueurs
AREA = [5, 6]         # surfaces
VOL = [7, 8]          # volumes
FORCE = [10]
STRESS = [11]
SHAPE = [12]
STAB = [13]
STRENGTH = [14]
DURAB = [15, 16]
ENERGY = [19, 20]
WASTE = [23, 26]      # pertes de matière / quantité de matière
RELIAB = [27]
MANUF = [32]
EASE = [33]
REPAIR = [34]
ADAPT = [35]
COMPLEX_ = [36]
PROD = [39]

# kind: 'llm' (instruction d'opérateur) | 'lattice' (générateur déterministe)
SOLUTIONS = [
    dict(id="lattice_gyroid", kind="lattice", name="Âme lattice gyroïde",
         principles=[31, 40, 1], improves=W + VOL + WASTE, degrades=STRENGTH,
         desc="Remplacer le volume interne par un gyroïde TPMS (peau conservée) : "
              "-30 à -60 % de masse, rigidité contrôlée par cellule/brin.",
         lattice=dict(kind="gyroid")),
    dict(id="lattice_gradient", kind="lattice", name="Lattice à GRADIENT de densité",
         principles=[3, 31, 35], improves=W + STRENGTH + WASTE, degrades=[],
         desc="Gyroïde plus DENSE près de la zone chargée/encastrée et aéré ailleurs "
              "— la matière uniquement là où elle travaille (Qualité locale).",
         lattice=dict(kind="gyroid", gradient="z")),
    dict(id="lattice_schwarz", kind="lattice", name="Âme Schwarz-P",
         principles=[31, 40], improves=W + VOL + WASTE, degrades=STRENGTH,
         desc="TPMS Schwarz-P : canaux orthogonaux traversants (drainage, "
              "échange thermique) + allègement.",
         lattice=dict(kind="schwarz")),
    dict(id="lattice_diamond", kind="lattice", name="Âme diamant (TPMS)",
         principles=[31, 40], improves=W + STRENGTH, degrades=[],
         desc="TPMS diamant : le plus isotrope des treillis, bon ratio "
              "rigidité/masse.",
         lattice=dict(kind="diamond")),
    dict(id="shell_ribs", kind="llm", name="Coque + nervures croisées",
         principles=[30, 40, 1], improves=W + STRENGTH + WASTE, degrades=COMPLEX_,
         desc="Remplacer les volumes massifs par des parois de 1.6-2.4 mm raidies "
              "par un quadrillage de nervures.",
         instruction="Transforme les volumes massifs en COQUES de 1.6-2.4 mm "
                     "raidies par un QUADRILLAGE de nervures internes (rib) "
                     "perpendiculaires, hauteur ~40-60% de la profondeur locale."),
    dict(id="pockets", kind="llm", name="Poches d'évidement",
         principles=[2, 31], improves=W + WASTE, degrades=STRENGTH,
         desc="Creuser des poches là où la matière ne travaille pas, en gardant "
              "cadres et membrures continus.",
         instruction="Creuse des POCHES d'évidement (profondeur 60-80% de "
                     "l'épaisseur locale) dans les zones éloignées des appuis et "
                     "des efforts, en conservant un cadre périphérique d'au moins "
                     "4 mm et les bossages autour des trous."),
    dict(id="gussets", kind="llm", name="Goussets aux jonctions",
         principles=[40, 3], improves=STRENGTH + STAB + RELIAB, degrades=W,
         desc="Ajouter des goussets triangulaires à chaque jonction orthogonale "
              "(le point faible classique).",
         instruction="Ajoute des GOUSSETS triangulaires (gusset) à CHAQUE jonction "
                     "orthogonale entre deux parois/ailes, épaisseur égale aux "
                     "parois, cathètes ~40-60% de la hauteur de la jonction."),
    dict(id="arches", kind="llm", name="Arcs et voûtes",
         principles=[14], improves=STRENGTH + W, degrades=SHAPE,
         desc="Courber ce qui est droit : un arc transmet en compression ce qu'une "
              "poutre droite subit en flexion.",
         instruction="REMPLACE les éléments droits travaillant en flexion par des "
                     "ARCS/VOÛTES (profils courbes pleins ou évidés) reliant les "
                     "mêmes points fonctionnels ; conserve les interfaces."),
    dict(id="tubular", kind="llm", name="Sections tubulaires",
         principles=[14, 7], improves=STRENGTH + W, degrades=[],
         desc="Remplacer les sections pleines par des sections creuses (tube) : "
              "même inertie, bien moins de matière.",
         instruction="REMPLACE les sections pleines (barres, montants, bras) par "
                     "des SECTIONS TUBULAIRES ou en caisson (paroi 2-3 mm), de "
                     "même encombrement extérieur."),
    dict(id="local_bosses", kind="llm", name="Bossages et surépaisseurs locales",
         principles=[3], improves=STRENGTH + RELIAB, degrades=W,
         desc="Épaissir UNIQUEMENT autour des trous, appuis et zones chargées.",
         instruction="Ajoute des BOSSAGES locaux (surépaisseur 50-100%) autour de "
                     "chaque trou de fixation, appui et zone d'effort ; amincis "
                     "les zones non sollicitées de 20-30%."),
    dict(id="fillets_stress", kind="llm", name="Congés anti-concentration",
         principles=[14], improves=STRENGTH + DURAB + RELIAB, degrades=[],
         desc="Congés généreux à tous les raccordements : supprime les "
              "concentrations de contraintes.",
         instruction="Ajoute des CONGÉS GÉNÉREUX (rayon ~ épaisseur locale/2) à "
                     "TOUS les raccordements et angles rentrants (try/except par "
                     "congé, réduis le rayon en repli)."),
    dict(id="fold_3d", kind="llm", name="Repli en 3D",
         principles=[17, 7], improves=LEN + AREA + VOL, degrades=COMPLEX_,
         desc="Sortir du plan : plier/superposer la géométrie pour réduire "
              "l'encombrement.",
         instruction="RÉORGANISE la géométrie EN 3D : plie/replie les éléments "
                     "plats, superpose des étages reliés par des voiles, exploite "
                     "la hauteur pour réduire l'emprise au sol, à fonctions et "
                     "interfaces conservées."),
    dict(id="nesting", kind="llm", name="Emboîtement télescopique",
         principles=[7], improves=LEN + VOL + ADAPT, degrades=COMPLEX_,
         desc="Loger un volume dans un autre (rangement, course télescopique).",
         instruction="EMBOÎTE les volumes : structure en éléments concentriques "
                     "coulissants ou logés l'un dans l'autre (jeu 0.4 mm), pour "
                     "réduire l'encombrement replié."),
    dict(id="asym", kind="llm", name="Asymétrie fonctionnelle",
         principles=[4], improves=STRENGTH + W + STAB, degrades=[],
         desc="Adapter chaque côté à son rôle réel au lieu d'une symétrie de "
              "confort.",
         instruction="DISSYMÉTRISE : renforce le côté chargé (triangulation, "
                     "surépaisseur), allège le côté libre ; adapte la forme de "
                     "chaque côté à sa fonction réelle."),
    dict(id="living_hinge", kind="llm", name="Charnière vivante",
         principles=[15, 1], improves=ADAPT + [36], degrades=DURAB,
         desc="Zone flexible imprimée (0.8-1.2 mm) : articulation sans "
              "assemblage.",
         instruction="INTRODUIS une CHARNIÈRE VIVANTE (lame flexible 0.8-1.2 mm "
                     "d'épaisseur, longueur >= 5 mm) là où une articulation ou une "
                     "flexion est utile, au lieu d'une liaison rigide."),
    dict(id="snapfit", kind="llm", name="Assemblage snap-fit",
         principles=[1, 15], improves=REPAIR + EASE + PROD, degrades=RELIAB,
         desc="Rendre démontable sans visserie : languettes élastiques.",
         instruction="REND la pièce DÉMONTABLE : sépare-la en 2 sous-ensembles "
                     "assemblés par languettes SNAP-FIT (snap_tab, jeu 0.3 mm) et "
                     "queues d'aronde (dovetail_rail/slot)."),
    dict(id="dovetail_mod", kind="llm", name="Modularité queue d'aronde",
         principles=[1, 6], improves=ADAPT + REPAIR + [37], degrades=STRENGTH,
         desc="Segmenter en modules interchangeables sur rail.",
         instruction="SEGMENTE la pièce en MODULES le long d'un RAIL en queue "
                     "d'aronde (dovetail_rail sur l'un, dovetail_slot dans "
                     "l'autre, jeu +0.6 mm) pour les rendre interchangeables."),
    dict(id="flat_print", kind="llm", name="Mise à plat d'impression",
         principles=[17, 13], improves=MANUF + PROD + RELIAB, degrades=[],
         desc="Réorienter/décomposer pour imprimer sans supports.",
         instruction="RÉORIENTE la géométrie pour imprimer SANS SUPPORTS : grandes "
                     "faces à plat sur Z=0, surplombs <= 45°, remplace les "
                     "porte-à-faux par des chanfreins d'impression."),
    dict(id="draft_chamfers", kind="llm", name="Chanfreins d'impression",
         principles=[16], improves=MANUF + [30], degrades=[],
         desc="Chanfreiner premières couches et bords : anti-warping, "
              "anti-coupure.",
         instruction="CHANFREINE la première couche (chanfrein 0.6-1 mm sur le "
                     "pourtour bas) et casse tous les bords vifs accessibles "
                     "(chanfrein 1 mm, try/except)."),
    dict(id="compliant", kind="llm", name="Mécanisme compliant",
         principles=[15, 32], improves=[36] + PROD + RELIAB, degrades=DURAB,
         desc="Remplacer un assemblage articulé par une pièce monobloc flexible.",
         instruction="REMPLACE les liaisons articulées par un MÉCANISME COMPLIANT "
                     "monobloc : lames élancées (0.8-1.5 mm) jouant le rôle de "
                     "pivots, imprimé en une seule pièce."),
    dict(id="counterweight_geom", kind="llm", name="Report de masse stabilisant",
         principles=[8], improves=STAB, degrades=W,
         desc="Déplacer/étaler la matière pour abaisser et recentrer le centre "
              "de gravité.",
         instruction="STABILISE par la géométrie : élargis et alourdis la BASE "
                     "(semelle étalée), allège le HAUT (évidements), pour abaisser "
                     "le centre de gravité — sans masse ajoutée inutile."),
    dict(id="capillary_pores", kind="llm", name="Canaux capillaires dimensionnés",
         principles=[31, 29, 3], improves=[10, 33, 36], degrades=MANUF,
         desc="Réseau de micro-canaux dont le diamètre est dimensionné pour faire "
              "monter un liquide par capillarité (h = 2γcosθ/ρgr) — transport "
              "passif, sans pompe (mèche, drainage, auto-arrosage).",
         instruction="INTRODUIS un RÉSEAU DE CANAUX CAPILLAIRES verticaux ou "
                     "inclinés dans la zone utile : diamètre 0.8-2 mm (imprimable "
                     "FDM ; plus fin = montée plus haute, loi de Jurin "
                     "h=2γcosθ/(ρgr) — expose le diamètre en paramètre nommé "
                     "`diametre_canal`), espacés de 2-4 mm, ouverts aux deux "
                     "extrémités, reliés à un réservoir ou à la surface à "
                     "alimenter."),
    dict(id="conformal", kind="llm", name="Épouser la forme (contact conforme)",
         principles=[14, 3], improves=FORCE + RELIAB + EASE, degrades=COMPLEX_,
         desc="Faire épouser à la pièce la forme de l'objet qu'elle tient "
              "(berceau conforme).",
         instruction="RENDS le contact CONFORME : la surface d'accueil épouse la "
                     "forme de l'objet porté (berceau circulaire/profilé au lieu "
                     "d'un appui plan), avec jeu de 0.3 mm."),
]

# Extensions issues de la VEILLE, validées par l'expert (persistées sur /data)
import os as _os
import json as _json
EXT_PATH = _os.environ.get("TCAD_GEOEXT",
                           "/data/geo_solutions_ext.json"
                           if _os.path.isdir("/data") else
                           _os.path.join(_os.path.dirname(__file__), "work",
                                         "geo_solutions_ext.json"))
import re as _re


def _norm_source(x):
    """Uniformise une source en {title, year, url} — les premières adoptions de la
    veille avaient stocké des chaînes brutes « Titre (année) »."""
    if isinstance(x, dict):
        return {"title": x.get("title"), "year": x.get("year"), "url": x.get("url")}
    t = str(x).strip()
    m = _re.match(r"^(.*?)\s*\((\d{4}|None|\?)\)\.?$", t)
    if m:
        return {"title": m.group(1).strip(),
                "year": int(m.group(2)) if m.group(2).isdigit() else None,
                "url": None}
    return {"title": t, "year": None, "url": None}


_CURATED = {s["id"] for s in SOLUTIONS}   # fiches en dur : jamais retirables

try:
    for _s in _json.load(open(EXT_PATH, encoding="utf-8")):
        if not _s.get("id"):
            continue
        _cur = next((x for x in SOLUTIONS if x["id"] == _s["id"]), None)
        if _cur is None:                       # solution adoptée par la veille
            _s["sources"] = [_norm_source(x) for x in _s.get("sources", [])]
            SOLUTIONS.append(_s)
        elif _s.get("sources"):                # overlay : sources d'une fiche du catalogue
            _cur["sources"] = [_norm_source(x) for x in _s["sources"]]
except Exception:
    pass

_BY_ID = {s["id"]: s for s in SOLUTIONS}


def save_sources(sol_id, sources):
    """Persiste des sources (DOI résolus, adossements) : catalogue vivant + ext.json.
    Pour une fiche du catalogue en dur, une entrée-overlay {id, sources} est ajoutée."""
    s = _BY_ID.get(sol_id)
    if not s:
        return False
    s["sources"] = sources
    try:
        ext = []
        try:
            ext = _json.load(open(EXT_PATH, encoding="utf-8"))
        except Exception:
            pass
        for e in ext:
            if e.get("id") == sol_id:
                e["sources"] = sources
                break
        else:
            ext.append({"id": sol_id, "sources": sources})
        _json.dump(ext, open(EXT_PATH, "w", encoding="utf-8"), ensure_ascii=False)
    except Exception:
        pass
    return True


def add_solution(s):
    """Adopte un candidat de la veille : catalogue vivant + persistance."""
    if not s.get("id") or s["id"] in _BY_ID:
        return False
    entry = {"id": s["id"], "kind": "llm", "name": s.get("name", s["id"]),
             "desc": s.get("desc", ""), "instruction": s.get("instruction", ""),
             "principles": s.get("principles", []),
             "improves": s.get("improves", []),
             "degrades": s.get("degrades", []),
             "sources": [_norm_source(x) for x in s.get("sources", [])]}
    SOLUTIONS.append(entry)
    _BY_ID[entry["id"]] = entry
    try:
        ext = []
        try:
            ext = _json.load(open(EXT_PATH, encoding="utf-8"))
        except Exception:
            pass
        ext.append(entry)
        _json.dump(ext, open(EXT_PATH, "w", encoding="utf-8"), ensure_ascii=False)
    except Exception:
        pass
    return True


def remove_solution(sol_id):
    """Annule une adoption (revue d'expert). Les fiches du catalogue en dur sont
    intouchables ; seules les entrées adoptées (ext) peuvent être retirées."""
    if sol_id in _CURATED or sol_id not in _BY_ID:
        return False
    SOLUTIONS[:] = [s for s in SOLUTIONS if s["id"] != sol_id]
    del _BY_ID[sol_id]
    try:
        ext = _json.load(open(EXT_PATH, encoding="utf-8"))
        ext = [e for e in ext if e.get("id") != sol_id]
        _json.dump(ext, open(EXT_PATH, "w", encoding="utf-8"), ensure_ascii=False)
    except Exception:
        pass
    return True


def get(sol_id):
    return _BY_ID.get(sol_id)


def cell_solutions(improve, degrade, cell_principles, limit=6):
    """Remplissage géométrique d'une cellule de la matrice : solutions triées —
    d'abord celles qui INCARNENT les principes de la cellule (fidélité à la
    matrice vérifiée), puis par adéquation au paramètre amélioré, en pénalisant
    celles qui risquent de dégrader le paramètre à préserver."""
    ranked = []
    for s in SOLUTIONS:
        score = 0
        score += 4 * len(set(s["principles"]) & set(cell_principles))
        if improve in s["improves"]:
            score += 3
        if degrade in s.get("degrades", []):
            score -= 2
        if score > 0:
            if s.get("sources"):        # à égalité, une solution SOURCÉE passe devant
                score += 1
            ranked.append((score, s))
    ranked.sort(key=lambda x: -x[0])
    return [{"id": s["id"], "name": s["name"], "kind": s["kind"],
             "desc": s["desc"], "principles": s["principles"], "score": sc,
             "lattice": s.get("lattice"), "sources": s.get("sources", [])}
            for sc, s in ranked[:limit]]
