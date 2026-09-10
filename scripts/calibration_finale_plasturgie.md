# Calibration finale des 8 familles — plasturgie (2026-09-10)

Audit conceptuel FAMILY → cellule Altshuller, contre les définitions canoniques des 39 paramètres
(`app/parametres_definitions.json`). Fait sans LLM, à partir des problèmes initiaux (AVANT/PROBLÈME) des articles.
Règle : SEMANTIC_DISTANCE = HIGH sur l'un des deux paramètres → pas de cellule historique.

| FAMILY | A (performance) → param | Action conventionnelle | B (dégradé causalement) → param | CAUSALITY | CELL | CONF | STATUS |
|---|---|---|---|---|---|---|---|
| CONFORMAL_COOLING (fusion STRENGTH+GEOMETRY) | réduire la durée de refroidissement → 25 (LOW) | rapprocher / multiplier les canaux droits de la cavité | paroi canal↔cavité amincie → tenue du moule sous pression → 14 (LOW) | YES | [25,14] | 0,75 | VALID_MATRIX_CELL |
| LIGHTWEIGHTING_SURFACE_QUALITY | réduire la masse → 2 (LOW) | mousser / réduire la matière | retassures, gauchissement, aspect → 12 (MEDIUM) | YES | [2,12] | 0,65 | VALID_MATRIX_CELL (faible) |
| LIGHTWEIGHT_STRUCTURE_STRENGTH | réduire la masse → 2 (LOW) | réduire la section / la densité | tenue mécanique → 14 (LOW) | YES | [2,14] | 0,85 | VALID_MATRIX_CELL (n=1 après exclusion du scaffold) |
| RECYCLED_PLASTICS_STRENGTH | « taux de recyclé » = exigence imposée, pas une performance ; 26 = HIGH | — | résistance/impact → 14 (LOW) | — | NONE | — | VALID_PROBLEM_FAMILY_NO_ALTSHULLER_CELL (physique : vierge/recyclé, séparation espace) |
| IN_MOLD_SENSING | mesurer l'état réel en cavité → 28 (LOW) | placer des capteurs dans la cavité | intégrité de l'outillage / marques sur la pièce → 13 (MEDIUM) | YES | [28,13] | 0,60 | VALID_MATRIX_CELL (faible) |
| SIMULATION_OPTIMIZATION_TIME | précision de PRÉDICTION (≠ mesure) → 28 (HIGH) ; temps de calcul/données → 25 (HIGH, interdit) | — | — | — | NONE | — | VALID_PROBLEM_FAMILY_NO_ALTSHULLER_CELL |
| DFMA_ASSEMBLY_TIME (tondeuse seule) | réduire le temps d'assemblage → 25 (LOW) | pièces simples et nombreuses | (inverse) simplicité de fabrication de chaque pièce → 32 (LOW) | YES | [32,25] | 0,70 | VALID_MATRIX_CELL (n=1) |
| (ex-DFMA) B-rep plan de joint | représentation d'information / automatisation → aucun paramètre (HIGH) | — | — | — | NONE | — | NO_TECHNICAL_CONTRADICTION (hors 39 paramètres) |
| (ex-DFMA) centre de roue fibres courtes | tenue mécanique → 14 (LOW) | fibres continues / usinage | moulabilité → 32 (LOW) | YES | [14,32] | 0,70 | VALID_MATRIX_CELL (singleton) |

Test CC : UNE seule contradiction générique (option A) — [17,12] était un inconvénient induit ; la limitation « perçage droit » est une
limitation de procédé (option C partielle) qui explique le dominant P17 observé, mais le compromis pré-invention proximité/tenue est réel.
Test recyclage : pas de correspondant canonique fidèle pour « fraction recyclée » → hors matrice.
Test IA/logiciel : temps de calcul, volume de données, précision de prédiction → hors 39 paramètres.

Comptes : VALID_MATRIX_FAMILIES = 5 (CC, LIGHTWEIGHTING_SURFACE, LIGHTWEIGHT_STRUCTURE, IN_MOLD_SENSING, DFMA) + 1 singleton [14,32] ;
VALID_PROBLEM_FAMILIES_WITHOUT_MATRIX_CELL = 2 (RECYCLED, SIMULATION) ; PHYSICAL_ONLY = 0 ; REJECTED = 0 (mais 1 article B-rep → NO_TECHNICAL_CONTRADICTION,
1 scaffold exclu comme hors discipline/hors problème).
Historique des cellules retenues : [25,14] → 29, 3, 28, 18 ; [2,12] → 13, 10, 29, 14 ; [2,14] → 28, 2, 10, 27 ; [28,13] → 32, 35, 13 ; [32,25] → 35, 28, 34, 4 ; [14,32] → 11, 3, 10, 32.
