# Test de reproductibilité du protocole v2 (2026-09-10, coût 0,10 $)

Même pilote (42 articles affectés), prompts v2 (règles de calibration gravées), sans intervention humaine, comparé aux 8 verdicts validés.

- Statut identique : 31/42 (74 %) — 31/39 (79 %) sur les articles comparables (3 statuts v1 malformés exclus)
- Cellule identique : 25/42 (60 %) — 25/39 (64 %)
- Sur les 25 articles des 8 familles validées : verdict reproduit 19/25 (76 %)

Reproduit : CONFORMAL_COOLING 10/10 → [25,14] (⚠ exemple présent dans le prompt : pas un test indépendant) ;
RECYCLED 2/2 → E (⚠ règle explicite dans le prompt) ; SIMULATION 3/3 → E (règle IA/logiciel) ;
LIGHTWEIGHT_STRUCTURE [2,14] ✓ ; métabolique → F ✓.
Non reproduit : IN_MOLD_SENSING (1 → E, 1 → [28,14] au lieu de [28,13] : B « intégrité » ambigu 13/14) ;
microcellulaire surface → [2,31] au lieu de [2,12] (aspect de surface ambigu 12/31) ; scaffold → [14,12] au lieu de F ;
centre de roue → [29,25] au lieu de [14,32] ; tondeuse DFMA → E au lieu de [32,25] (règle « 25 interdit » sur-appliquée) ;
inversions de sens improve/worsen sur des singletons ([30,12] ↔ [12,30]).

Diagnostic : la STRUCTURE du protocole est stable (statuts E/F émergent spontanément, familles de problème cohérentes) ;
l'INSTABILITÉ est concentrée dans le mapping de B quand la distance sémantique est MEDIUM — c'est une ambiguïté du
vocabulaire des 39 paramètres, pas un caprice du modèle. Recommandations : (1) sortir les 2 candidats de B avec distances
quand MEDIUM et trancher par règle humaine ; (2) garde déterministe contre l'inversion improve/worsen dans une famille ;
(3) sur le corpus, deux passes indépendantes et ne retenir que les cellules stables (auto-cohérence), ou revue humaine
des mappings MEDIUM seulement.
