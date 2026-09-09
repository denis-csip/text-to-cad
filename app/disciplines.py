# -*- coding: utf-8 -*-
"""REGISTRE DES DISCIPLINES — la matrice géométrique n'est que la première
instance d'un moteur générique de « matrices disciplinaires ».

Idée (Denis, 2026-09) : au lieu d'une matrice transdisciplinaire à la Altshuller,
une matrice PAR DISCIPLINE qui rend l'expert conscient de toute la diversité des
solutions déjà documentées DANS SON PROPRE MÉTIER. Les 39 paramètres restent ceux
d'Altshuller (comparabilité entre disciplines = la transdisciplinarité redevient
une opération CALCULÉE : cellules pleines partout = principes universels mesurés ;
pleines ici / vides là = candidats au transfert ; vides ici = angles morts).

Une discipline = un id, un libellé, une couleur, des GLOSES des 39 paramètres
(le dialecte du métier), un PROMPT D'EXTRACTION et une BANQUE DE REQUÊTES.
Le reste du pipeline (moisson OpenAlex, extraction Gemini, revue d'expert,
propagation sur les 1248 cellules, fiches, sources DOI) est partagé.

PORTÉE d'une solution (assumée sur la fiche) :
  cao      -> transforme la GÉOMÉTRIE d'une pièce : pilotable par le modeleur
  procede  -> choix / réglage de procédé : recommandation à l'expert
  matiere  -> choix de matériau / formulation : recommandation à l'expert
"""

PORTEES = {"cao": "Géométrie de pièce (pilotable par le modeleur)",
           "procede": "Procédé (recommandation)",
           "matiere": "Matière (recommandation)"}

_JSON_SCHEMA = """Réponds UNIQUEMENT en JSON : {"candidates": [
 {"id": "slug_court_en_snake_case",
  "name": "nom FR court",
  "desc": "en 1-2 phrases FR : la solution et ce qu'elle apporte",
  "instruction": "consigne IMPÉRATIVE FR : comment l'appliquer concrètement
                  (dimensions, réglages ou grades indicatifs)",
  "portee": "cao" | "procede" | "matiere",
  "principles": [n° parmi les 40 principes TRIZ que la solution incarne],
  "improves": [n° parmi les 39 paramètres d'Altshuller améliorés],
  "degrades": [n° des paramètres risqués],
  "sources": [numéros [n] des papiers du corpus dont la solution est tirée] }]}

Les 39 paramètres d'Altshuller : {{PARAMETRES}}

LES 40 PRINCIPES INVENTIFS — étiquette TOUS ceux que la solution incarne
EXPLICITEMENT (2 à 5), en t'appuyant sur ce que le texte DIT : « flash /
ultra-rapide / impulsion » = 21 action éclair ; « ultrasons / vibration » = 18 ;
« pulsé / cyclique » = 19 ; « polymérisation in situ / changement d'état » = 36
transition de phase (PAS 35) ; « film / membrane » = 30 ; « poreux / mousse » = 31 ;
« gaz / eau / contre-pression » = 29 ; « préchauffage / prétraitement » = 10 ;
« couche intermédiaire / primaire » = 24 ; « emboîtement / télescopique » = 7.
Réserve le 35 « modification des propriétés » aux changements d'état ou de
propriété de la matière elle-même, jamais comme fourre-tout.
{{PRINCIPES}}

2 à 6 candidats MAXIMUM, uniquement les plus originaux et actionnables."""


# =============================================================================
# GÉOMÉTRIE 3D — la matrice d'origine (solutions exécutables par le modeleur)
# =============================================================================
GEOMETRIE_EXTRACT = """Tu es un expert TRIZ et conception pour fabrication additive.
On te donne des résumés d'articles scientifiques récents. Extrais-en des SOLUTIONS
GÉOMÉTRIQUES transférables à des pièces CAO imprimées en FDM : des transformations
de géométrie concrètes (pas des matériaux, pas des procédés hors FDM).
La portée est toujours "cao".
""" + _JSON_SCHEMA + "\nIgnore ce qui n'est pas géométrique."

GEOMETRIE_QUERIES = [
    "gyroid lattice mechanical properties additive manufacturing",
    "triply periodic minimal surface lattice stiffness strength",
    "octet truss lattice additive manufacturing mechanical",
    "plate lattice stiffness limit additive manufacturing",
    "functionally graded lattice density design",
    "conformal lattice infill freeform design",
    "honeycomb core out-of-plane crush additive manufacturing",
    "Voronoi irregular lattice design 3D printing",
    "hierarchical multiscale lattice mechanical metamaterial",
    "pentamode metamaterial design fabrication",
    "negative stiffness metamaterial energy absorption",
    "auxetic re-entrant honeycomb design 3D printing",
    "chiral auxetic metamaterial mechanical behavior",
    "rotating squares auxetic perforated sheet design",
    "negative Poisson ratio structure impact protection",
    "Kelvin cell open foam lattice additive manufacturing",
    "strut diameter gradient lattice optimization",
    "shell TPMS lattice wall thickness gradient",
    "Miura-ori fold core sandwich stiffness",
    "origami tube stiff reconfigurable structure",
    "kirigami stretchable structure design",
    "origami crash box energy absorption",
    "bistable origami mechanism design",
    "folded corrugated core sandwich panel",
    "deployable structure origami engineering",
    "compliant mechanism flexure hinge design 3D printed",
    "cross-axis flexural pivot design",
    "bistable compliant mechanism switch design",
    "living hinge design fatigue polypropylene",
    "snap-fit joint design guidelines additive manufacturing",
    "print-in-place joint clearance 3D printing",
    "3D printed thread tolerance design",
    "topological interlocking assembly blocks mechanics",
    "dovetail interlocking 3D printed joint strength",
    "lattice hinge kerf bending design",
    "ratchet pawl mechanism compact design",
    "constant force compliant mechanism design",
    "riblet surface drag reduction texture",
    "shark skin inspired surface texture",
    "superhydrophobic micropillar surface 3D printed",
    "surface texture friction control sliding",
    "dimple texture lubrication friction reduction",
    "anti-icing surface microstructure design",
    "gecko adhesion fibrillar microstructure",
    "anti-fouling surface topography design",
    "conformal cooling channel injection mold design",
    "TPMS heat exchanger thermal performance",
    "capillary wick 3D printed heat pipe",
    "microchannel capillary passive liquid transport",
    "vascular network channel self-healing design",
    "self-draining geometry drainage design",
    "static mixer geometry 3D printed",
    "Tesla valve fluidic diode design",
    "flow distribution manifold header optimization",
    "graded porous media 3D printed filtration",
    "rib layout optimization thin wall stiffening",
    "isogrid stiffened panel design",
    "corrugated panel bending stiffness design",
    "sandwich core shear design additive manufacturing",
    "stress concentration fillet shape optimization",
    "variable thickness tailored design structure",
    "arch dome compression structure form finding",
    "tensegrity structure design fabrication",
    "geodesic rib shell reinforcement",
    "buckling resistant thin structure stiffener design",
    "crash box crush initiator geometry",
    "cellular structure energy absorption plateau stress",
    "bistable array reusable energy absorption",
    "helmet liner lattice impact optimization",
    "thin-walled tube crush trigger design",
    "phononic crystal bandgap design",
    "acoustic metamaterial sound absorption structure",
    "acoustic black hole vibration damping",
    "particle damping 3D printed cavity",
    "architected lattice damping viscoelastic",
    "support-free self-supporting overhang design additive manufacturing",
    "part consolidation assembly reduction additive manufacturing",
    "topology optimization design features additive manufacturing",
    "build orientation anisotropy strength design FDM",
    "residual stress distortion compensation geometry additive",
    "teardrop horizontal hole design FDM",
    "infill pattern strength optimization FDM",
    "screw boss design plastic part guidelines",
    "press fit interference design polymer part",
    "Bouligand helicoidal architecture toughness",
    "nacre brick and mortar architecture toughness",
    "trabecular bone inspired lattice implant",
    "bamboo node structure bending inspiration",
    "plant stem inspired structural design",
    "spider web architecture energy absorption",
    "honeycomb bee comb structure optimization",
    "conch shell hierarchical structure impact",
    "4D printing shape morphing structure design",
    "anisotropic swelling hinge actuator geometry",
    "shape memory polymer printed structure design",
    "bistable morphing panel skin design",
    "Geneva mechanism compact intermittent motion design",
    "flexure bearing linear guide design",
    "origami inspired stent geometry",
    "graded stiffness interface joint dissimilar materials",
]


# =============================================================================
# PLASTURGIE — première matrice disciplinaire (design de pièce, procédé, matière)
# =============================================================================
PLASTURGIE_GLOSES = {
    1: "Masse d'une pièce mobile (levier, volet, pièce embarquée) : allègement",
    2: "Masse d'une pièce fixe (carter, boîtier, panneau) : allègement",
    3: "Longueur / portée d'une pièce en mouvement (bras, languette)",
    4: "Longueur d'une pièce fixe (profilé, longeron, paroi)",
    5: "Surface fonctionnelle mobile (face d'appui, surface de glissement)",
    6: "Surface fixe (aspect, surface projetée du moule, surface d'échange)",
    7: "Volume d'une pièce mobile (encombrement en service)",
    8: "Volume d'une pièce fixe (volume moulé, encombrement, empilage)",
    9: "Vitesse : cadence d'injection / de cycle, vitesse de remplissage, vitesse du produit",
    10: "Force : effort de fermeture, effort d'éjection, force d'assemblage (clip, emmanchement), charge en service",
    11: "Pression : pression d'injection / de maintien, contrainte en service, pression de contact",
    12: "Forme : géométrie moulée, complexité de forme, contre-dépouilles, fidélité de forme",
    13: "Stabilité : stabilité dimensionnelle (retrait, gauchissement, post-retrait), tenue au fluage",
    14: "Résistance mécanique : tenue à la rupture, résistance des lignes de soudure, tenue des clips",
    15: "Durabilité pièce mobile : fatigue (charnière intégrale, clip), usure, cycles",
    16: "Durabilité pièce fixe : vieillissement, UV, fluage long terme, tenue chimique",
    17: "Température : température matière / outillage, tenue en température (HDT), gradients thermiques",
    18: "Luminosité : transparence, aspect optique, brillance, couleur, transmission",
    19: "Énergie consommée par une pièce mobile : énergie d'actionnement, frottement",
    20: "Énergie consommée par une pièce fixe : énergie du cycle (chauffe, refroidissement, fermeture)",
    21: "Puissance : puissance machine, débit d'injection, puissance de chauffe",
    22: "Pertes d'énergie : refroidissement inefficace, chaleur perdue, frottement, rebroyage",
    23: "Pertes de matière : carottes, canaux froids, bavures, rebuts, purges, sur-épaisseurs",
    24: "Perte d'information : traçabilité, marquage, identification matière, données procédé",
    25: "Perte de temps : temps de cycle, temps de refroidissement, changement d'outillage, reprises",
    26: "Quantité de matière : masse injectée, part de charges/renforts, taux de recyclé",
    27: "Fiabilité : reproductibilité pièce à pièce, robustesse du procédé, défauts (retassures, incomplets)",
    28: "Précision de mesure : contrôle dimensionnel, métrologie en ligne, capteurs de cavité",
    29: "Précision de fabrication : tolérances moulées, état de surface, répétabilité, jeu fonctionnel",
    30: "Facteurs nuisibles subis : humidité (hygroscopie), UV, chimie, chocs, température ambiante",
    31: "Effets nuisibles générés : émissions/odeurs, bavures coupantes, contraintes résiduelles, gauchissement",
    32: "Fabricabilité : moulabilité, démoulage, dépouilles, remplissage, éventation, faisabilité outillage",
    33: "Facilité d'usage : ergonomie, assemblage sans outil, ouverture/fermeture, toucher",
    34: "Réparabilité / démontabilité : désassemblage, recyclage en fin de vie, remplacement",
    35: "Adaptabilité : famille de pièces, inserts interchangeables, variantes, modularité",
    36: "Complexité du dispositif : nombre de pièces, nombre de tiroirs / noyaux, complexité outillage",
    37: "Complexité du contrôle : réglage du procédé, nombre de paramètres, mise au point",
    38: "Niveau d'automatisation : robotisation, décarottage automatique, assemblage dans le moule",
    39: "Productivité : cadence, nombre d'empreintes, taux de rendement synthétique",
}

PLASTURGIE_EXTRACT = """Tu es un expert TRIZ et ingénieur PLASTURGISTE (conception de
pièces plastiques, outillage d'injection, procédés de transformation, matériaux
polymères). On te donne des résumés d'articles scientifiques récents. Extrais-en
des SOLUTIONS INNOVANTES DE PLASTURGIE, concrètes et réutilisables par un bureau
d'études ou un atelier : conception de pièce pour le moulage (nervures, bossages,
épaisseurs, dépouilles, charnières intégrales, clips, seuils et lignes de
soudure), outillage (refroidissement conforme, éventation, éjection, noyaux),
procédés (injection assistée gaz/eau, micro-cellulaire, bi-matière, surmoulage,
IMD/IML, injection-compression, thermoformage, extrusion, rotomoulage, soudage),
matériaux (biosourcés, recyclés, renforcés, mousses, mélanges, additifs).

Classe chaque solution par PORTÉE :
  "cao"     = elle modifie la GÉOMÉTRIE de la pièce (transposable dans un modeleur)
  "procede" = elle relève du procédé / de l'outillage / des réglages
  "matiere" = elle relève du choix de matériau ou de formulation

Dialecte des 39 paramètres en plasturgie : 9 = cadence et vitesse de remplissage ;
10 = efforts de fermeture, d'éjection, d'assemblage ; 11 = pressions d'injection
et de maintien ; 12 = forme moulée et contre-dépouilles ; 13 = stabilité
dimensionnelle (retrait, gauchissement) ; 14 = tenue mécanique et lignes de
soudure ; 15 = fatigue des charnières et clips ; 17 = températures matière et
outillage, HDT ; 18 = transparence et aspect ; 23 = carottes, bavures, rebuts ;
25 = temps de cycle et de refroidissement ; 26 = masse injectée, taux de charges
ou de recyclé ; 27 = reproductibilité et défauts ; 29 = tolérances moulées et
état de surface ; 30 = hygroscopie, UV, chimie ; 31 = contraintes résiduelles,
émissions ; 32 = moulabilité et démoulage ; 34 = démontabilité et recyclage ;
36 = nombre de pièces, tiroirs et noyaux ; 38 = décarottage et assemblage
automatisés ; 39 = cadence et nombre d'empreintes.
""" + _JSON_SCHEMA + "\nIgnore ce qui n'est pas transposable en plasturgie."

PLASTURGIE_QUERIES = [
    # --- Conception de pièce pour l'injection (DFM) ---
    "rib design injection molded part sink mark stiffness",
    "boss design screw insert injection molded plastic guidelines",
    "uniform wall thickness injection molding warpage design",
    "draft angle ejection force injection molded part",
    "undercut design collapsible core slider elimination injection molding",
    "living hinge integral hinge polypropylene design molding",
    "snap-fit design injection molded thermoplastic joint",
    "gate location optimization weld line injection molding",
    "weld line strength improvement injection molding design",
    "sink mark prediction elimination injection molding",
    "warpage reduction design injection molded part geometry",
    "corner radius stress concentration molded plastic part design",
    "thin wall injection molding design flow length ratio",
    "part consolidation multifunctional injection molded design",
    "metal replacement plastic part design structural injection molding",
    "design for injection molding manufacturability rules",
    "molded-in stress residual stress reduction part design",
    "integrated fastener design molded plastic assembly",
    "press-fit boss plastic part design retention",
    "lattice structure injection molded part lightweight",
    # --- Outillage / moule ---
    "conformal cooling channel injection mold cycle time",
    "additive manufactured mold insert conformal cooling",
    "hot runner system balance injection mold",
    "mold venting design trapped air burn marks",
    "ejection system design ejector pin marks plastic part",
    "collapsible core undercut molding tooling",
    "family mold multi-cavity balance runner design",
    "rapid tooling 3D printed injection mold low volume",
    "mold surface temperature control variotherm heat and cool",
    "in-mold sensor cavity pressure process monitoring",
    "mold texture laser texturing injection molding surface",
    "mold coating wear release injection molding",
    # --- Procédés d'injection avancés ---
    "gas-assisted injection molding hollow part design",
    "water-assisted injection molding tubular part",
    "microcellular injection molding MuCell foaming weight reduction",
    "injection compression molding thin part optical",
    "two-component injection molding multi-material overmolding",
    "insert molding metal insert plastic bonding",
    "in-mold decoration in-mold labeling film injection",
    "in-mold assembly integrated joint molding",
    "micro injection molding microfluidic device polymer",
    "co-injection sandwich molding recycled core",
    "long fiber reinforced thermoplastic injection molding fiber length",
    "structural foam molding low pressure part design",
    "chemical foaming agent injection molding lightweight",
    "injection molding fiber orientation prediction mechanical",
    # --- Autres procédés de transformation ---
    "thermoforming wall thickness distribution plug assist",
    "extrusion blow molding parison thickness optimization",
    "stretch blow molding preform design PET bottle",
    "rotational molding wall thickness design part",
    "profile extrusion die design flow balance",
    "co-extrusion multilayer barrier film packaging",
    "compression molding sheet molding compound design",
    "resin transfer molding composite part design",
    "thermoplastic composite stamping overmolding hybrid",
    "large format additive manufacturing polymer pellet extrusion",
    # --- Assemblage / soudage ---
    "ultrasonic welding energy director design thermoplastic",
    "laser transmission welding plastic joint design",
    "vibration welding thermoplastic joint strength",
    "hot plate welding plastic joint design",
    "adhesive-free joining polymer parts mechanical interlocking",
    "plastic-metal hybrid joining injection molding surface structuring",
    "heat staking design plastic assembly",
    "screw joint self-tapping screw plastic boss",
    # --- Matériaux ---
    "bio-based polymer injection molding properties",
    "recycled polymer mechanical properties injection molding",
    "post-consumer recycled plastic compatibilizer blend",
    "polymer blend compatibilization impact strength",
    "halogen-free flame retardant thermoplastic",
    "thermally conductive polymer composite heat sink",
    "electrically conductive polymer composite EMI shielding",
    "self-reinforced polymer composite",
    "natural fiber reinforced thermoplastic",
    "polymer foam core sandwich lightweight",
    "thermoplastic elastomer overmolding soft touch seal",
    "high temperature thermoplastic PEEK PPS injection molding",
    "transparent polymer optical part molding birefringence",
    "biodegradable polymer processing",
    "polymer nanocomposite mechanical properties injection",
    # --- Défauts, qualité, tolérances ---
    "shrinkage prediction injection molding dimensional accuracy",
    "post-mold shrinkage annealing dimensional stability",
    "flash defect injection molding cause prevention",
    "short shot defect flow analysis injection molding",
    "jetting flow marks surface defect injection molding",
    "hygroscopic polymer drying moisture defects",
    "injection molding process parameter optimization design of experiments",
    "surface gloss control injection molding",
    "scratch resistance molded surface texture",
    # --- Durabilité / fin de vie ---
    "design for recycling plastic product mono-material",
    "design for disassembly plastic product",
    "chemical recycling polymer depolymerization",
    "plastic part lightweighting design sustainability",
    "circular economy plastic packaging design",
    "recycled content injection molding quality",
    # --- Simulation / optimisation ---
    "mold flow simulation gate optimization",
    "cooling channel optimization simulation injection mold",
    "topology optimization injection molded part manufacturability",
    "digital twin injection molding process control",
    # --- Fonctions intégrées ---
    "molded interconnect device laser direct structuring",
    "in-mold electronics functional film",
    "molded hydrophobic surface microstructure injection",
    "integrated seal design molded part",
    "flexible living hinge packaging closure design",
]


# Injection de la liste COMPLÈTE des 40 principes et des 39 paramètres dans les
# prompts d'extraction : une liste partielle biaisait l'étiquetage vers les
# seuls principes cités (P21, 24, 36, 2 quasi jamais attribués).
try:
    import invent as _inv
    _P40 = "\n".join(f"{n}. {p.get('label','')}" for n, p in sorted(_inv.PRINCIPLES.items()))
    _P39 = " ; ".join(f"{p['number']} {p['fr']}" for p in _inv.PARAMETERS)
except Exception:
    _P40, _P39 = "(liste indisponible)", "(liste indisponible)"
GEOMETRIE_EXTRACT = GEOMETRIE_EXTRACT.replace("{{PRINCIPES}}", _P40).replace("{{PARAMETRES}}", _P39)
PLASTURGIE_EXTRACT = PLASTURGIE_EXTRACT.replace("{{PRINCIPES}}", _P40).replace("{{PARAMETRES}}", _P39)

DISCIPLINES = {
    "geometrie": {
        "id": "geometrie", "label": "Géométrie 3D", "short": "GÉO",
        "color": "#7c3aed", "color_soft": "#ede9fe",
        "desc": "Solutions géométriques exécutables par le modeleur (fabrication additive).",
        "extract_system": GEOMETRIE_EXTRACT, "queries": GEOMETRIE_QUERIES,
        "gloses": {}, "portee_defaut": "cao",
    },
    "plasturgie": {
        "id": "plasturgie", "label": "Plasturgie", "short": "PLAST",
        "color": "#ea580c", "color_soft": "#ffedd5",
        "desc": "Conception de pièces plastiques, outillage, procédés et matériaux.",
        "extract_system": PLASTURGIE_EXTRACT, "queries": PLASTURGIE_QUERIES,
        "gloses": PLASTURGIE_GLOSES, "portee_defaut": "procede",
    },
}
DEFAULT = "geometrie"


def get(did):
    return DISCIPLINES.get(did or DEFAULT, DISCIPLINES[DEFAULT])


def public_list():
    """Vue publique (sans les prompts ni les banques de requêtes)."""
    return [{"id": d["id"], "label": d["label"], "short": d["short"],
             "color": d["color"], "color_soft": d["color_soft"], "desc": d["desc"],
             "gloses": d["gloses"], "n_queries": len(d["queries"])}
            for d in DISCIPLINES.values()]
