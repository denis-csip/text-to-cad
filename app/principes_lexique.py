# -*- coding: utf-8 -*-
"""FILET DE RAPPEL LEXICAL des principes inventifs (0 $, déterministe).

Constat (Denis, 2026-09-09) : l'extracteur LLM manque des principes que le
texte nomme EXPLICITEMENT (« action flash » sans P21 : rappel 12 %). Ce module
repère, pour chaque fiche, les principes dont un marqueur lexical net apparaît
dans nom+desc+instruction alors que le principe n'est pas étiqueté, et les
propose à l'expert (badge 💡 + pré-remplissage de l'éditeur). Il ne modifie
JAMAIS l'étiquetage seul : c'est une suggestion, tranchée par l'humain.

Fiabilité : 'forte' = marqueur quasi univoque ; 'faible' = à vérifier.
"""
import re

MARQUEURS = {
    21: ("forte", r"flash|\béclair\b|\beclair\b|ultra-?rapide|instantan|en un temps très court|très vite|par impulsion|\bpulse\b|femtoseconde|nanoseconde"),
    18: ("forte", r"ultrason|vibration|vibrant|oscillat"),
    19: ("forte", r"périodique|periodique|\bpuls[ée]e?\b|cyclique|intermittent|par impulsions|alternanc"),
    31: ("forte", r"poreu|\bmousse|micro-?cellul|alvéol|alveol|moussage"),
    29: ("forte", r"assist[ée]e? (?:au )?(?:gaz|eau)|pneumati|hydrauli|contre-?pression|injection de gaz|injection d'eau"),
    7:  ("forte", r"emboît|emboit|télescop|telescop|gigogne|imbriqu"),
    30: ("faible", r"\bfilm\b|membrane|peau mince|feuille mince|coque souple"),
    36: ("faible", r"transition de phase|changement d'état|changement d'etat|polymérisation in situ|solidification|cristallisation|passage (?:du |de l')?(?:solide|liquide)"),
    24: ("faible", r"intermédiaire|intermediaire|intercal|couche de liaison|primaire d'adhésion"),
    1:  ("faible", r"segment|fractionn|divis[ée]e? en|modulaire|en plusieurs (?:pièces|parties)"),
    2:  ("faible", r"\bextra(?:it|ction)\b|retir[ée]|\bisol[ée]|\bséparer\b|\bôter\b"),
    3:  ("faible", r"\blocalis|\bcibl[ée]|zone spécifique|sélectiv|localement"),
    17: ("faible", r"multicouche|multi-couche|tridimension|empil|\bsandwich\b|en hauteur"),
    10: ("faible", r"préchauff|prechauff|pré-?traitement|préalabl|au préalable|en amont"),
}
_RX = {p: (f, re.compile(rx, re.I)) for p, (f, rx) in MARQUEURS.items()}


def suggere(fiche):
    """[{principe, mot, fiabilite}] pour les principes NOMMÉS par le texte mais absents."""
    txt = " ".join(str(fiche.get(k, "")) for k in ("name", "desc", "instruction"))
    deja = set(fiche.get("principles") or [])
    out = []
    for p, (fiab, rx) in _RX.items():
        if p in deja:
            continue
        m = rx.search(txt)
        if m:
            out.append({"principe": p, "mot": m.group(0), "fiabilite": fiab})
    out.sort(key=lambda s: (s["fiabilite"] != "forte", s["principe"]))
    return out
