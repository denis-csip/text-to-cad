"""Voie INVENTIVE : contradiction technique -> principes (matrice vérifiée)
-> opérateurs géométriques -> variantes mesurées (idéalité).

Les 40 principes deviennent des OPÉRATEURS DE TRANSFORMATION appliqués par le
LLM à la pièce courante. La matrice 39x39 (collationnée sur le scan original
d'Altshuller, portée d'Inventioneering) sert de routeur : elle choisit les
principes pertinents pour la contradiction posée.
"""
import json
from pathlib import Path

_DATA = json.loads((Path(__file__).parent / "triz_data.json").read_text(encoding="utf-8"))
PARAMETERS = _DATA["parameters"]          # [{number, fr}]
PRINCIPLES = {p["number"]: p for p in _DATA["principles"]}   # {n: {label, description}}
_MATRIX = {(c["improving"], c["degrading"]): c["principles"] for c in _DATA["cells"]}


def principles_for(improve: int, degrade: int):
    """Principes recommandés par la matrice pour (paramètre amélioré, dégradé)."""
    nums = _MATRIX.get((improve, degrade), [])
    return [{"number": n,
             "label": PRINCIPLES.get(n, {}).get("label", f"principe {n}"),
             "description": PRINCIPLES.get(n, {}).get("description", ""),
             "operator": n in OPERATORS}
            for n in nums]


# --- Opérateurs géométriques : traduction CAO concrète des principes clés ----
# (les autres principes passent par l'opérateur générique : le LLM interprète
#  la description du principe géométriquement)
OPERATORS = {
    1: ("Segmentation",
        "SEGMENTE la pièce : découpe les volumes massifs en éléments plus fins "
        "(fentes, ajours, treillis de nervures croisées, parois multiples) en "
        "PRÉSERVANT les zones fonctionnelles (appuis, trous, interfaces) et la "
        "connexité (UN seul solide, chevauchements >= 1 mm)."),
    2: ("Extraction",
        "EXTRAIS la matière qui ne travaille pas : identifie les zones peu "
        "sollicitées (loin des appuis et efforts) et RETIRE-les (poches, "
        "évidements traversants) en gardant des cadres/membrures continus."),
    3: ("Qualité locale",
        "RENDS la pièce NON-UNIFORME : épaissis UNIQUEMENT les zones sollicitées "
        "(congés de raccordement généreux, bossages locaux autour des trous) et "
        "amincis partout ailleurs."),
    4: ("Asymétrie",
        "DISSYMÉTRISE : si la pièce est symétrique, adapte chaque côté à son rôle "
        "réel (côté chargé renforcé, côté libre allégé, section triangulée du "
        "côté des efforts)."),
    7: ("Poupées russes",
        "EMBOÎTE : loge un volume dans un autre (structure en coquilles "
        "concentriques, réservations internes utiles, canal interne) au lieu "
        "d'un bloc plein."),
    14: ("Sphéricité",
         "COURBE ce qui est droit : remplace parois planes par des voiles "
         "cintrés/arcs (un arc travaille mieux qu'une poutre droite), congés "
         "larges aux raccordements, sections tubulaires plutôt que carrées."),
    15: ("Dynamisation",
         "REND MOBILE/FLEXIBLE : introduis une articulation imprimée (charnière "
         "mince type living hinge >= 0.8 mm), une zone flexible (lame élancée) "
         "ou une liaison snap (snap_tab) là où la rigidité totale n'est pas "
         "nécessaire."),
    17: ("Autre dimension",
         "PASSE EN 3D : sors du plan — plie/replie la géométrie, superpose des "
         "étages, utilise la hauteur disponible (nervures verticales, voiles "
         "hors-plan) au lieu d'épaissir dans le plan."),
    30: ("Membranes flexibles",
         "REMPLACE les volumes massifs par des PAROIS MINCES raidies : coques "
         "de 1.6-2.4 mm + nervures (rib), au lieu de sections pleines."),
    31: ("Matériaux poreux",
         "AJOURE / ÉVIDE : perce des motifs d'allègement (réseaux de trous "
         "hexagonaux ou circulaires via GridLocations/PolarLocations) dans les "
         "zones peu sollicitées ; ou évide l'intérieur (hollow_tray, coques)."),
    35: ("Modification des propriétés",
         "MODULE les épaisseurs : fais varier les sections le long de la pièce "
         "selon la sollicitation (épais à l'encastrement, fin en bout — profil "
         "en dépouille/taper)."),
    40: ("Matériaux composites",
         "STRUCTURE EN SANDWICH : combine peaux minces + âme nervurée "
         "(quadrillage de ribs entre deux plaques) pour rigidifier sans "
         "alourdir."),
}


def operator_instruction(principle: int, contradiction: str) -> str:
    """Instruction de transformation pour le LLM (refine_code) : applique le
    principe à la pièce courante, en visant la contradiction."""
    p = PRINCIPLES.get(principle, {})
    if principle in OPERATORS:
        name, op = OPERATORS[principle]
        core = op
    else:
        name = p.get("label", f"principe {principle}")
        core = ("INTERPRÈTE GÉOMÉTRIQUEMENT ce principe inventif sur la pièce :\n"
                + p.get("description", "") +
                "\nTraduis-le en modification CONCRÈTE de la géométrie.")
    return (
        f"TRANSFORMATION INVENTIVE — principe TRIZ n°{principle} « {name} ».\n"
        f"CONTRADICTION À RÉSOUDRE : {contradiction}\n"
        f"CONSIGNE : {core}\n"
        "CONTRAINTES : conserve la FONCTION et les interfaces de la pièce "
        "(trous de fixation, appuis, logements aux mêmes positions/cotes) ; "
        "la pièce reste UN SEUL solide connexe, imprimable FDM (parois >= 1.2 mm) ; "
        "garde les paramètres nommés en tête de script et AJOUTE en commentaire "
        f"en première ligne : # PRINCIPE {principle}: {name}. "
        "Modifie la géométrie de façon FRANCHE (l'effet doit être mesurable).")


def ideality(sf, masse_g):
    """Idéalité mesurable : fonction assurée (tenue) / coût matière (masse)."""
    try:
        if sf is None or not masse_g:
            return None
        return round(float(sf) / float(masse_g), 3)
    except Exception:
        return None
