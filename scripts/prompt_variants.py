# -*- coding: utf-8 -*-
"""STRATEGIES REDACTIONNELLES du prompt de generation — variantes a comparer.

Chaque variante = SYSTEM de base + un bloc ajoute (ou un reglage de reflexion).
Le banc (bench_prompt.py) les note sur les memes briefs, meme graine, meme
scoring : on choisit la strategie sur des chiffres, plus a l'intuition.

V0  baseline .......... le prompt actuel, tel quel (reference)
V1  plan-avant-code ... impose l'ORDRE DE PENSEE d'un projeteur (datums ->
                        squelette -> features -> surfaces fonctionnelles ->
                        controles) en commentaires structures avant le code
V2  exemplaire ........ un script COMPLET exemplaire (few-shot) : montre le
                        niveau de finition attendu plutot que de le decrire
V3  contrat fonctionnel  la piece est decrite par ce qu'elle DOIT FAIRE :
                        surfaces fonctionnelles declarees et intouchables,
                        auto-controle avant de rendre le code
V4  V1+V2 ............. cumul du plan et de l'exemplaire
V5  reflexion haute ... baseline mais thinking_level='high' (levier a 1 ligne)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))
from prompt import SYSTEM                                            # noqa: E402

PLAN = r"""

METHODE DE TRAVAIL OBLIGATOIRE (avant d'ecrire la moindre ligne de geometrie).
Tu raisonnes comme un projeteur, dans CET ordre, et tu ecris ce raisonnement en
commentaires `#` en tete de script (apres les cotes), en 5 lignes maximum :
1. REPERE : ou est l'origine, quel plan est la base d'impression (z=0), quelle
   direction est la hauteur utile.
2. SQUELETTE : la piece en 2-4 volumes primitifs seulement (le gros oeuvre),
   avec leurs recouvrements >= 1 mm.
3. FEATURES : ce qui se retire ou s'ajoute ensuite (percages, poches, nervures).
4. SURFACES FONCTIONNELLES : liste les faces qui portent la fonction (appui,
   contact, interface, logement) — elles gardent leurs cotes exactes.
5. CONTROLES : ce qui rendrait la piece invalide ici (parois minces, volumes
   disjoints, congé trop grand) et comment tu l'evites.
Puis SEULEMENT tu ecris le code, dans le meme ordre que ton plan.
"""

EXEMPLAIRE = r"""

EXEMPLE DE REPONSE ATTENDUE (niveau de finition exige — meme rigueur, meme
structure, adapte a la piece demandee).
Brief : « une equerre de fixation 60x40, epaisseur 5, deux trous de 5 mm dans
la semelle, un trou de 6 mm dans le dosseret, arete interieure renforcee ».
```python
from build123d import *

longueur_semelle = 60.0   # longueur de la semelle (mm)
largeur = 40.0            # largeur commune (mm)
hauteur_dosseret = 45.0   # hauteur du dosseret (mm)
epaisseur = 5.0           # epaisseur des deux ailes (mm)
diam_semelle = 5.0        # percages de la semelle (mm)
diam_dosseret = 6.0       # percage du dosseret (mm)
rayon_gousset = 12.0      # renfort de l'arete interieure (mm)

# REPERE   : origine au coin interieur, semelle a plat sur XY (z=0), dosseret +Z
# SQUELETTE: 2 boites en L, recouvrement franc sur l'epaisseur
# FEATURES : 2 percages traversants semelle, 1 percage dosseret, gousset triangulaire
# SURF.FONC: dessous de semelle (appui) et face avant du dosseret (contact) intactes
# CONTROLES: parois >= 1.2 mm, un seul solide (les boites se chevauchent), pas de congé
#            superieur a l'epaisseur

semelle = Pos(longueur_semelle / 2, 0, epaisseur / 2) * Box(
    longueur_semelle, largeur, epaisseur)
dosseret = Pos(epaisseur / 2, 0, hauteur_dosseret / 2) * Box(
    epaisseur, largeur, hauteur_dosseret)
part = semelle + dosseret

# gousset : triangle dans le plan XZ, extrude sur la largeur (renfort d'arete)
profil = Pos(0, -largeur / 2, 0) * extrude(
    Plane.XZ * Polygon((epaisseur, epaisseur), (epaisseur + rayon_gousset, epaisseur),
                       (epaisseur, epaisseur + rayon_gousset), align=None),
    amount=largeur)
part = part + profil

for x in (longueur_semelle * 0.45, longueur_semelle * 0.8):
    part = part - Pos(x, 0, epaisseur / 2) * Cylinder(diam_semelle / 2, epaisseur * 3)
part = part - Pos(epaisseur / 2, 0, hauteur_dosseret * 0.75) * Rot(0, 90, 0) * Cylinder(
    diam_dosseret / 2, epaisseur * 3)

try:                      # cosmetique : ne doit jamais tuer la piece
    part = fillet(part.edges().filter_by(Axis.Y).group_by(Axis.Z)[-1], radius=1.0)
except Exception:
    pass
```
Retiens de cet exemple : cotes nommees une par ligne, plan en commentaires,
composition par volumes qui se chevauchent, operations fragiles en try/except,
et AUCUN texte hors du bloc de code.
"""

CONTRAT_FONCTIONNEL = r"""

RAISONNEMENT FONCTIONNEL (ce que la piece doit FAIRE prime sur ce a quoi elle
ressemble). Avant de coder, identifie :
- la FONCTION principale (que tient / guide / protege / relie la piece ?) ;
- les SURFACES FONCTIONNELLES qui la realisent : appuis, contacts, interfaces,
  logements, passages. Elles sont INTOUCHABLES : cotes exactes, jamais
  deformees par un congé, un evidement ou un allegement ;
- le CHEMIN D'EFFORT : par ou passe la charge, de son point d'application
  jusqu'a l'ancrage. Mets la matiere sur ce chemin, allege ailleurs.
Le reste de la piece (l'ame, les faces non fonctionnelles) est libre.

AUTO-CONTROLE AVANT DE RENDRE (silencieux, pas de texte en sortie) : relis ton
script et verifie que (a) chaque cote donnee par l'utilisateur apparait bien
comme variable et est bien utilisee, (b) tous les volumes se chevauchent d'au
moins 1 mm — aucune piece flottante, (c) aucune paroi < 1.2 mm, (d) les
surfaces fonctionnelles ont leurs cotes exactes, (e) `part` est bien defini.
Si un point cloche, CORRIGE le script avant de repondre.
"""

VARIANTS = {
    "V0_baseline": {"system": SYSTEM, "thinking": None},
    "V1_plan": {"system": SYSTEM + PLAN, "thinking": None},
    "V2_exemplaire": {"system": SYSTEM + EXEMPLAIRE, "thinking": None},
    "V3_fonctionnel": {"system": SYSTEM + CONTRAT_FONCTIONNEL, "thinking": None},
    "V4_plan_exemplaire": {"system": SYSTEM + PLAN + EXEMPLAIRE, "thinking": None},
    "V5_reflexion_haute": {"system": SYSTEM, "thinking": "high"},
}
