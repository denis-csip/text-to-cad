# Pilote protocole « transformation » — plasturgie, 100 articles

48 analyses exploitables sur 100 · coût 0,19 $ · concordance : {'hors recommandations de la matrice': 30, 'concordance partielle': 9, 'concordance forte': 3, 'contradiction indéterminée': 6}

## 1. Canaux de refroidissement conformes pour moules d'injection
*Design and fabrication of conformal cooling channels in molds: Review and progress updates* (2021) — https://doi.org/10.1016/j.ijheatmasstransfer.2021.121082

**Résumé inventif** : Cette solution remplace les canaux de refroidissement droits percés traditionnels par des canaux de refroidissement conformes (CC) qui épousent la géométrie tridimensionnelle de la cavité. Cette disposition tridimensionnelle permet un refroidissement uniforme et accéléré, réduisant fortement le temps de cycle et les déformations thermiques.

- **AVANT** : Les moules d'injection utilisent des canaux de refroidissement droits conventionnels obtenus par perçage rectiligne.
- **PROBLÈME** : Le refroidissement des pièces de forme complexe est non uniforme, ce qui entraîne des temps de cycle longs, un risque de gauchissement et une dégradation de la qualité.
- **TRANSFORMATION** : La géométrie des canaux est modifiée pour passer d'un réseau linéaire simple à un réseau tridimensionnel équidistant de la surface de la cavité (canaux conformes).
- **APRÈS** : Un réseau de canaux de refroidissement suit précisément les contours 3D de la cavité du moule, garantissant un flux thermique homogène.

**Dominant** : P17 Nouvelle dimension — 0.95 — La trajectoire des canaux passe d'un perçage rectiligne unidirectionnel à un réseau tridimensionnel épousant la surface complexe de la cavité.
**Secondaire** : P3 Qualité locale — 0.8 — La disposition et le type de canaux sont adaptés aux spécificités géométriques locales de chaque zone de la pièce.

- **↑39 Productivité / ↓14 Résistance** (0.85) — Si nous améliorons la vitesse de refroidissement et la productivité en augmentant la conformité et le réseau des canaux, alors la résistance mécanique de l'outillage se détériore.  
  *preuve* : To achieve a uniform and rapid cooling, some key design parameters [...] have to be calculated [...] taking into account the cooling performance, mechanical strength...
- **↑39 Productivité / ↓36 Complexité du dispositif** (0.8) — Si nous améliorons l'homogénéité du refroidissement (productivité), alors la complexité de fabrication de l'outillage augmente.  
  *preuve* : CC systems show great promise [...] lower cycle time [...] basic type, more complex types, and hybrid straight-drilled-CC molds

**Contradiction physique** : oui — Les canaux doivent être proches de la cavité pour refroidir efficacement, et éloignés de la cavité pour maintenir la résistance mécanique du moule. — séparation : espace
**Matrice** (cellule [39, 14]) recommande [29, 28, 10, 18] · observés [17, 3] → **hors recommandations de la matrice**
Portée : cao

## 2. Structure sandwich co-injectée à cœur recyclé
*Learnings about design from recycling by using post-consumer polypropylene as a core layer in a co-injection molded sandwich structure product* (2021) — https://doi.org/10.1016/j.matdes.2021.109576

**Résumé inventif** : Afin d'incorporer du polypropylène recyclé contaminé sans dégrader l'aspect visuel ni la rigidité de la pièce, la structure est co-injectée sous forme de sandwich. Le matériau recyclé est confiné au cœur de la pièce tandis qu'une peau en matériau vierge garantit l'esthétique et la finition extérieure.

- **AVANT** : Les caisses de transport sont moulées soit entièrement en polypropylène vierge pour garantir l'aspect et la résistance, soit entièrement en recyclé au détriment de l'esthétique et des propriétés mécaniques.
- **PROBLÈME** : L'utilisation de PP recyclé issu de déchets ménagers introduit des contaminants qui dégradent fortement la résistance à l'impact, l'aspect visuel et la résistance mécanique globale.
- **TRANSFORMATION** : Répartition spatiale des matières par co-injection : le PP recyclé (45 wt%) est injecté exclusivement au cœur de la structure, enfermé par une couche externe de PP vierge.
- **APRÈS** : Une caisse de transport à structure sandwich présentant l'aspect de surface parfait du PP vierge et une rigidité préservée, tout en intégrant près de la moitié de matière recyclée.

**Dominant** : P3 Qualité locale — 0.95 — La pièce est structurée en zones aux propriétés distinctes : une peau externe vierge assurant l'aspect et un cœur interne recevant la matière recyclée contaminée.
**Secondaire** : P40 Matériaux composites — 0.85 — Création d'une structure sandwich multicouche co-injectée combinant les caractéristiques de deux qualités de polymères différentes.

- **↑26 Quantité de substance / ↓14 Résistance** (0.9) — Si nous augmentons le taux de matière recyclée incorporée pour favoriser l'économie circulaire, alors la résistance mécanique et la qualité d'impact se détériorent à cause des impuretés.  
  *preuve* : While these contaminants had no deteriorative effect on stiffness-controlled performance, a strong influence on strength-controlled and impact-related properties was observed.

**Contradiction physique** : oui — La surface/structure doit être en matériau vierge pour conserver l'esthétique et l'impact, et doit être en matériau recyclé pour intégrer des déchets plastiques. — séparation : espace
**Matrice** (cellule [26, 14]) recommande [14, 35, 34, 10] · observés [3, 40] → **hors recommandations de la matrice**
Portée : procede

## 3. Injection cellulaire de polypropylène à retrait maîtrisé
*Post-Molding Shrinkage, Structure and Properties of Cellular Injection-Molded Polypropylene* (2022) — https://doi.org/10.3390/ma15207079

**Résumé inventif** : L'injection de polypropylène cellulaire remplace la structure interne massive par une matrice poreuse microcellulaire. Cela élimine les retassures de surface et réduit le poids des pièces tout en maîtrisant le retrait postérieur à la cristallisation.

- **AVANT** : Moulage par injection conventionnel de pièces en polypropylène sous forme solide et dense.
- **PROBLÈME** : Présence de retassures de surface importantes dues au retrait volumique lors de la cristallisation, associées à une consommation excessive de matière et un poids élevé.
- **TRANSFORMATION** : Création d'une structure interne poreuse/cellulaire au sein du matériau polymère au cours de l'injection en contrôlant le moussage et la phase de maintien.
- **APRÈS** : Pièces en polypropylène à cœur microcellulaire et peau dense, présentant un poids réduit et une disparition des retassures de surface.

**Dominant** : P31 Matériaux poreux — 0.95 — La substitution de la structure interne solide par une structure cellulaire poreuse constitue le mécanisme physique direct permettant de compenser le retrait et d'alléger la pièce.
**Secondaire** : P35 Modification des paramètres physiques/chimiques — 0.75 — La densité globale du matériau et sa structure cristalline sont modifiées par l'action de moussage et de nucléation gazeuse.

- **↑26 Quantité de substance / ↓14 Résistance** (0.85) — Si nous générons une structure alvéolaire pour réduire la quantité de matière injectée, alors la résistance mécanique de la pièce se détériore.  
  *preuve* : Cellular injection molding is a common method... reducing their weight. However, mechanical properties after injection molding change as a result of re-crystallization.
- **↑31 Effets secondaires nuisibles / ↓13 Stabilité de l'objet** (0.8) — Si nous réduisons la densité du matériau pour éliminer les retassures, alors la stabilité dimensionnelle au cours du temps s'en trouve dégradée.  
  *preuve* : assess the changes in the value of processing shrinkage and the size of the sink marks of porous PP moldings depending on the degree of porosity and the time

**Contradiction physique** : oui — Le polymère doit être dense pour maintenir les propriétés mécaniques, et doit être poreux/cellulaire pour absorber le retrait et supprimer les retassures. — séparation : tout-parties
**Matrice** (cellule [26, 14]) recommande [14, 35, 34, 10] · observés [31, 35] → **concordance partielle**
Portée : procede

## 4. Injection de matière moussée par agent gonflant
*Injection mold design for a plastic component with blowing agent* (2018) — https://doi.org/10.1016/j.promfg.2018.10.128

**Résumé inventif** : L'incorporation d'un agent gonflant chimique (CBA) lors du moulage par injection crée une structure cellulaire poreuse au cœur de la pièce. Cela supprime les retassures et le gauchissement tout en réduisant la quantité de matière, le temps de cycle et la taille de presse requise.

- **AVANT** : Injection conventionnelle d'une palette en HDPE dense nécessitant une quantité importante de matière, des forces de fermeture élevées et des temps de cycle longs pour éviter le gauchissement et les retassures.
- **PROBLÈME** : Réduire la masse de la pièce et le temps de cycle sans générer de défauts dimensionnels (retassures, gauchissement) ni nécessiter des machines de très forte puissance.
- **TRANSFORMATION** : Ajout d'un agent gonflant chimique dans le polymère pour générer une structure interne expansée/cellulaire (moussage) au sein de la cavité du moule.
- **APRÈS** : Une pièce en plastique moussé possédant une structure interne cellulaire, plus légère, moulée à plus faible pression avec un temps de cycle réduit et sans retassures.

**Dominant** : P31 Matériaux poreux — 0.95 — L'obtention d'une structure interne moussée/cellulaire grâce à l'agent gonflant constitue le mécanisme direct permettant d'éliminer les retassures tout en réduisant la masse.
**Secondaire** : P35 Modification des paramètres physiques/chimiques — 0.75 — L'ajout d'un additif chimique réactif modifie la densité de la matière et la dynamique de phase lors du remplissage de l'outillage.

- **↑26 Quantité de substance / ↓31 Effets secondaires nuisibles** (0.85) — Si nous réduisons la quantité de matière (26) pour alléger la pièce et raccourcir le cycle, alors les retassures et le gauchissement (31) se détériorent dans une injection conventionnelle.  
  *preuve* : The CBA enables obtaining parts with smaller warp in a shorter cycle [...] save in raw material, with a considerable reduction of weight.

**Contradiction physique** : oui — La pièce doit être massive pour occuper tout le volume de la cavité sans retassure, et doit être non-massive (poreuse) pour réduire la quantité de matière et le poids. — séparation : tout-parties
**Matrice** (cellule [26, 31]) recommande [3, 35, 40, 39] · observés [31, 35] → **concordance partielle**
Portée : procede

## 5. Refroidissement conforme 3D par fabrication additive SLM
*Experimental analysis of conformal cooling in SLM produced injection moulds: Effects on process and product quality* (2019) — https://doi.org/10.1063/1.5084861

**Résumé inventif** : Cette solution remplace les canaux de refroidissement droits conventionnels par des canaux conformes tridimensionnels imprimés en 3D par SLM. En épousant la géométrie complexe de la cavité, le réseau de refroidissement réduit le temps de cycle tout en éliminant les défauts de gauchissement.

- **AVANT** : Les canaux de refroidissement de l'outillage d'injection sont réalisés par perçage mécanique direct, formant un réseau rigide de lignes droites.
- **PROBLÈME** : Le refroidissement est inégal sur les formes complexes, ce qui génère un temps de cycle très long et des défauts géométriques (gauchissement, retassures) sur la pièce moulée.
- **TRANSFORMATION** : Les canaux de refroidissement sont redessinés en 3D pour suivre fidèlement les contours complexes de la cavité (canaux conformes) et sont fabriqués par fabrication additive métal (SLM).
- **APRÈS** : Un outillage intégrant des canaux de refroidissement tridimensionnels sur mesure, offrant un transfert thermique homogène et accéléré sur toute la surface de la pièce.

**Dominant** : P17 Nouvelle dimension — 0.9 — Passage d'un réseau de canaux de refroidissement linéaire/planaire à une trajectoire tridimensionnelle conforme qui épouse les contours complexes de la cavité.
**Secondaire** : P3 Qualité locale — 0.8 — Positionnement et conformation des canaux adaptés spécifiquement aux besoins thermiques des différentes zones de la cavité.

- **↑25 Perte de temps / ↓32 Fabricabilité** (0.85) — Si nous conformons la trajectoire des canaux de refroidissement aux contours complexes de la pièce pour réduire le temps de cycle, alors la fabricabilité de l'outillage par usinage traditionnel se détériore.  
  *preuve* : These often curved cooling channels are difficult or even impossible to produce with conventional techniques such as milling, drilling and EDM.

**Contradiction physique** : oui — Les trajectoires de refroidissement doivent être droites pour être exécutées par perçage classique et non-droites (incurvées 3D) pour suivre la forme de la pièce. — séparation : espace
**Matrice** (cellule [25, 32]) recommande [35, 28, 34, 4] · observés [17, 3] → **hors recommandations de la matrice**
Portée : procede

## 6. Modélisation du degré de fusion pour surmoulage composite
*Analysis of the Thermoplastic Composite Overmolding Process: Interface Strength* (2020) — https://doi.org/10.3389/fmats.2020.00027

**Résumé inventif** : Modélisation de l'adhésion à l'interface de surmoulage composite en intégrant le degré de fusion locale des polymères semi-cristallins. Cette approche dépasse les modèles classiques d'amorphes en prédisant la résistance mécanique selon l'historique thermo-mécanique.

- **AVANT** : L'estimation de la tenue de l'interface lors du surmoulage de composites thermoplastiques s'appuyait sur la théorie de la reptation développée pour les polymères amorphes.
- **PROBLÈME** : La théorie de la reptation amorphe ne prédit pas correctement le comportement des polymères semi-cristallins (PA6, PEEK), dont la cohésion dépend fortement de la fusion et recristallisation locale.
- **TRANSFORMATION** : Prise en compte explicite du degré de fusion et de l'historique thermo-mécanique local à l'interface pour régir la création de liaisons macromoléculaires.
- **APRÈS** : Un modèle prédictif adapté aux matrices semi-cristallines permettant de concevoir le procédé de surmoulage et de garantir la résistance de l'interface sous sollicitations de traction et cisaillement.

**Dominant** : P36 Transitions de phase — 0.85 — La prédiction et l'optimisation de la résistance d'interface reposent sur la modélisation explicite du degré de fusion (changement d'état solide/liquide) du polymère semi-cristallin.
**Secondaire** : P35 Modification des paramètres physiques/chimiques — 0.75 — L'adhésion est pilotée en ajustant et modélisant l'état physique et l'historique thermique local à l'interface.

- **↑14 Résistance / ↓37 Complexité du contrôle** (0.75) — Si nous améliorons la résistance mécanique de l'interface (14) en maximisant la fusion et l'interdiffusion à l'interface composite/résine, alors la complexité du réglage et du contrôle du procédé (37) augmente.  
  *preuve* : Un modèle rudimentaire du degré de fusion en fonction de l'historique thermo-mécanique a dû être développé pour prédire la résistance d'interface.

**Contradiction physique** : oui — Le matériau d'interface doit être fondu (pour permettre la reptation et la soudure) et ne pas être excessivement déformé ou dégradé (pour préserver la structure composite). — séparation : temps
**Matrice** (cellule [14, 37]) recommande [27, 3, 15, 40] · observés [36, 35] → **hors recommandations de la matrice**
Portée : procede

## 7. Modélisation thermoélastique à cœur caoutchoutique
*Thermoelasticity of Injection-Molded Parts* (2023) — https://doi.org/10.3390/polym15132841

**Résumé inventif** : Cette méthode améliore la prédiction numérique des retassures en modélisant le cœur fondu comme un état caoutchoutique plutôt que liquide. Cela permet d'empêcher la dissipation artificielle des contraintes thermiques locales dans la simulation.

- **AVANT** : La déformation des pièces injectées est simulée en considérant le cœur encore fondu comme un fluide liquide parfait.
- **PROBLÈME** : L'approximation fluide dissipe les déformations locales dans le modèle numérique, entraînant une sous-estimation ou une mauvaise localisation des retassures.
- **TRANSFORMATION** : Remplacement du modèle d'état fluide du cœur fondu par un modèle d'état caoutchoutique (rubbery state) dans le calcul thermoélastomécanique pas à pas.
- **APRÈS** : Un modèle de simulation capable de conserver et de restituer fidèlement les déplacements Dus au retrait thermique localisé à proximité de leur zone d'apparition.

**Dominant** : P35 Modification des paramètres physiques/chimiques — 0.85 — Le comportement de la matière au cœur de la pièce est représenté sous un état mécanique équivalent différent (état caoutchoutique/élastomère au lieu d'un état liquide) pour capturer les contraintes de retrait.

- **↑28 Précision de la mesure / ↓37 Complexité du contrôle** (0.75) — Si nous améliorons la précision de mesure des retassures locales par la modélisation à l'état caoutchoutique, alors la complexité du calcul numérique augmente.  
  *preuve* : In our methodology, two treatments of the molten core are considered... the rubbery state treatment provides higher accuracy in predicting the deformation results

**Contradiction physique** : oui — Le cœur de la matière doit être considéré comme liquide pour refléter la phase fondue réelle, et non-liquide (caoutchoutique) pour transmettre et localiser le champ de déformation thermique. — séparation : conditions
**Matrice** (cellule [28, 37]) recommande [26, 24, 32, 28] · observés [35] → **hors recommandations de la matrice**
Portée : procede

## 8. Échangeur thermique en polymère composite chargé
*Thermal and Manufacturing Design of Polymer Composite Heat Exchangers* (2014) — http://hdl.handle.net/1903/15172

**Résumé inventif** : L'utilisation de polymères non chargés pour les échangeurs thermiques évite la corrosion mais souffre d'une faible conductivité thermique, tandis que les métaux résistent mal aux milieux agressifs comme l'eau de mer. La solution consiste à élaborer un matériau composite polymère renforcé thermiquement pour combiner résistance à la corrosion et haute conductivité thermique.

- **AVANT** : Utilisation d'échangeurs thermiques en métal (sujets à la corrosion en milieu marin) ou en polymères non chargés (faible conductivité thermique).
- **PROBLÈME** : Les métaux subissent la corrosion dans des fluides agressifs comme l'eau de mer, alors que les polymères standards présentent un transfert thermique insuffisant.
- **TRANSFORMATION** : Remplacement du matériau homogène classique par une matrice polymère chargée d'additifs à haute conductivité thermique (matériau composite).
- **APRÈS** : Un échangeur thermique en composite polymère combinant la résistance à la corrosion des polymères et la conductivité thermique proche des métaux.

**Dominant** : P40 Matériaux composites — 0.95 — Association d'une matrice polymère résistante à la corrosion et de charges thermiquement conductrices pour obtenir des propriétés combinées inédites.
**Secondaire** : P35 Modification des paramètres physiques/chimiques — 0.7 — Modification de la conductivité thermique globale du matériau par modification de sa composition chimique et de ses charges.

- **↑31 Effets secondaires nuisibles / ↓32 Fabricabilité** (0.85) — Si nous améliorons les propriétés thermiques et la résistance à la corrosion en utilisant un composite polymère thermiquement chargé, alors la fabricabilité par moulage des structures minces se détériore.  
  *preuve* : The widespread use of seawater as a coolant can be made possible by [...] thermally-enhanced polymer composites [...] However, thermally enhanced polymer composites behave differently [...] thin walled large structures are expected to pose challenges during the molding process.

**Contradiction physique** : oui — Le matériau de l'échangeur doit être non métallique pour éviter la corrosion et métallique pour conduire efficacement la chaleur. — séparation : tout-parties
**Matrice** (cellule [31, 32]) recommande [] · observés [40, 35] → **hors recommandations de la matrice**
Portée : matiere

## 9. Centre de roue composite carbone moulé par compression
*Design And Analysis Of A Compression Molded Carbon Composite Wheel Center* (2013) — http://hdl.handle.net/10106/11909

**Résumé inventif** : Cette solution remplace la fabrication conventionnelle de pièces métalliques ou composites continus par un procédé de moulage par compression utilisant un composite à fibres courtes de carbone orientées aléatoirement. Cette transformation permet d'obtenir directement la forme quasi-finale (near-net-shape) avec des propriétés mécaniques quasi-isotropes tout en supprimant les opérations d'usinage secondaires.

- **AVANT** : Fabrication de centres de roues métalliques ou composites à fibres continues nécessitant des usinages secondaires et entraînant des coûts et des temps de cycle élevés.
- **PROBLÈME** : Les procédés conventionnels sont lents, coûteux, génèrent de l'anisotropie et nécessitent des retouches ou reprises d'usinage complexes.
- **TRANSFORMATION** : Remplacement de la structure initiale par une matrice thermodurcissable chargée en fibres de carbone courtes segmentées et orientées de manière aléatoire, mise en forme par moulage par compression.
- **APRÈS** : Un centre de roue composite de géométrie complexe obtenu directement aux cotes quasi-finales, doté de propriétés quasi-isotropes et fabriqué à des cadences élevées.

**Dominant** : P40 Matériaux composites — 0.9 — L'association d'une matrice thermodurcissable et de fibres de carbone courtes permet d'obtenir des propriétés isotropes et une mise en forme directe tout en réduisant le poids.
**Secondaire** : P1 Segmentation — 0.85 — La division des fibres continues en fibres courtes permet un écoulement fluide sous compression sans endommager le renfort.

- **↑32 Fabricabilité / ↓14 Résistance** (0.85) — Si nous améliorons la fabricabilité et la productivité en utilisant un moulage par compression de fibres courtes, alors la résistance mécanique risque de se détériorer par rapport aux composites à fibres continues.  
  *preuve* : production of near net shape parts eliminating secondary operations [...] Compression molding process is the most preferred process as this addresses the problems of fiber damage effectively

**Contradiction physique** : oui — Les fibres doivent être courtes pour s'écouler sans casse dans le moule et doivent être longues pour assurer la reprise des efforts mécaniques. — séparation : tout-parties
**Matrice** (cellule [32, 14]) recommande [1, 3, 10, 32] · observés [40, 1] → **concordance partielle**
Portée : procede

## 10. Segmentation B-rep pour intégration du plan de joint
*A Systematic Approach to Support Design for Manufacturability in Injection Molding and Die Casting* (1995) — https://doi.org/10.1115/cie1995-0804

**Résumé inventif** : L'article propose de découper les surfaces géométriques du modèle CAO (B-rep) en structures de segments dédiées aux lignes de plan de joint. Cette intégration directe de la topologie de démoulage dans l'arbre géométrique accélère la conception des moules d'injection et de fonderie.

- **AVANT** : La définition des lignes de plan de joint et des directions de démoulage se fait manuellement et indépendamment de la maquette numérique B-rep, imposant des itérations lentes et laborieuses.
- **PROBLÈME** : L'absence de représentation explicite du plan de joint dans le modèle géométrique empêche l'automatisation de l'analyse de moulabilité et l'association automatique des dépouilles, seuils et évents.
- **TRANSFORMATION** : Division des surfaces B-rep en sous-segments topologiques interconnectés intégrant directement l'information du plan de joint dans la hiérarchie du modèle CAO.
- **APRÈS** : Un modèle géométrique enrichi d'une structure segmentée où chaque face est liée à ses contraintes de démoulage et de moulage.

**Dominant** : P1 Segmentation — 0.85 — La surface continue de la pièce CAO est découpée en segments géométriques distincts au niveau de la structure B-rep pour y associer individuellement les propriétés de plan de joint.
**Secondaire** : P5 Combinaison — 0.7 — Intégration directe des données de fabrication (plan de joint) au sein de la hiérarchie géométrique B-rep existante.

- **↑32 Fabricabilité / ↓36 Complexité du dispositif** (0.75) — Si nous améliorons la fabricabilité et la vitesse de conception par la segmentation du modèle géométrique, alors la complexité du dispositif informatique/modèle augmente.  
  *preuve* : The typical design cycle is iterative, laborious and time-consuming... The resulting specification is stored in a segment structure which provides a flexible parting description and fits within the B-rep hierarchy.

**Contradiction physique** : non
**Matrice** (cellule [32, 36]) recommande [27, 26, 1] · observés [1, 5] → **concordance forte**
Portée : cao

## 11. Combinaison du moulage microcellulaire avec la décoration en moule
*Production of microcellular lightweight components with improved surface finish by technology combination: A review* (2021) — https://doi.org/10.1016/j.ijlmm.2021.11.005

**Résumé inventif** : Le moulage par injection microcellulaire permet d'alléger les pièces mais dégrade fortement leur état de surface. La solution consiste à combiner au sein du même procédé le moussage microcellulaire avec des technologies de finition et de décoration en moule.

- **AVANT** : Le moulage par injection microcellulaire (MIM) classique est utilisé seul pour réduire la masse des pièces plastiques.
- **PROBLÈME** : Le dégazage et la formation d'alvéoles créent des défauts de surface (traces de swirl, rugosité) inacceptables pour des pièces d'aspect.
- **TRANSFORMATION** : Combinaison et intégration directe du procédé MIM avec des technologies de décoration et de traitement de surface au sein de l'outillage.
- **APRÈS** : Une pièce expansée microcellulaire légère possédant un état de surface de haute qualité et des propriétés décoratives intégrées sans reprise.

**Dominant** : P5 Combinaison — 0.9 — Le procédé rassemble et intègre en un cycle unique le moulage microcellulaire et les technologies de décoration ou de finition de surface.
**Secondaire** : P10 Action préliminaire — 0.7 — L'intégration d'un film ou revêtement décoratif dans le moule avant l'injection microcellulaire prépare la qualité de surface finale.

- **↑26 Quantité de substance / ↓29 Précision de la fabrication** (0.85) — Si nous réduisons la masse de la pièce par injection microcellulaire, alors l'état de surface et la précision d'aspect se détériorent.  
  *preuve* : MIM is used to manufacture plastic components with reduced weight, however this technology is characterized for producing components with a poor surface finish.

**Contradiction physique** : oui — La structure du polymère doit être moussée et alvéolaire pour réduire le poids, et totalement dense et lisse en surface pour l'aspect esthétique. — séparation : tout-parties
**Matrice** (cellule [26, 29]) recommande [33, 30] · observés [5, 10] → **hors recommandations de la matrice**
Portée : procede

## 12. Formulation composite de thermoplastiques recyclés pour FDM
*FDM-based additive manufacturing of recycled thermoplastics and associated composites* (2023) — https://doi.org/10.1007/s10163-022-01588-2

**Résumé inventif** : L'utilisation de thermoplastiques recyclés pour l'impression FDM entraîne une chute de viscosité et de résistance mécanique due à la scission des chaînes polymères. L'incorporation d'additifs et de charges de renfort au plastique recyclé forme un matériau composite qui restaure les propriétés mécaniques du produit final.

- **AVANT** : Utilisation de thermoplastiques recyclés purs pour extruder du filament d'impression FDM.
- **PROBLÈME** : La dégradation thermique et mécanique subie lors des cycles de recyclage provoque une scission des chaînes polymères, réduisant fortement la viscosité et la résistance à la rupture des pièces imprimées.
- **TRANSFORMATION** : Ajout d'additifs, de compatibilisants et de charges renforçantes au polymère recyclé détérioré pour constituer un formulation composite.
- **APRÈS** : Un filament composite à matrice recyclée permettant d'imprimer par FDM des composants dotés de caractéristiques mécaniques et de procédés de transformation équivalents ou supérieurs au plastique vierge.

**Dominant** : P40 Matériaux composites — 0.95 — L'association du polymère recyclé dégradé avec des additifs et charges renforçantes forme un matériau composite rééquilibrant les propriétés mécaniques perdues.
**Secondaire** : P22 Transformation du mal en bien — 0.85 — La conversion de déchets plastiques dégradés (facteur nuisible/rebut) en matière première fonctionnelle pour impression 3D grâce à la formulation d'additifs.

- **↑26 Quantité de substance / ↓14 Résistance** (0.9) — Si nous augmentons le taux de matière plastique recyclée dans le filament d'impression FDM, alors la résistance mécanique de la pièce se détériore en raison de la scission des chaînes polymères.  
  *preuve* : The strength of FDM components produced from thermoplastic waste is lower than that of virgin plastic FDM counterparts... due to chain scission, change in viscosity and breaking strength.

**Contradiction physique** : oui — Le polymère du filament doit être recyclé (pour réutiliser les déchets) et ne doit pas être dégradé par le recyclage (pour garantir la résistance mécanique). — séparation : tout-parties
**Matrice** (cellule [26, 14]) recommande [14, 35, 34, 10] · observés [40, 22] → **hors recommandations de la matrice**
Portée : matiere

## 13. Conception inverse hybride IA et physique
*Toward Knowledge‐Guided AI for Inverse Design in Manufacturing: A Perspective on Domain, Physics, and Human–AI Synergy* (2025) — https://doi.org/10.1002/aidi.202500107

**Résumé inventif** : L'article propose une approche de conception inverse intégrant les connaissances du domaine et la physique au sein des modèles d'apprentissage automatique. Cette synergie permet de restreindre l'espace de recherche et de garantir le respect des contraintes physiques même avec des données rares.

- **AVANT** : La conception inverse s'appuie sur des modèles d'IA purement guidés par les données (data-driven) ou sur des optimisations par essais-erreurs.
- **PROBLÈME** : Les modèles purement guidés par les données nécessitent des volumes massifs de données, généralisent mal en présence de données rares et risquent de violer les contraintes physiques réelles.
- **TRANSFORMATION** : Combinaison d'un filtrage préalable de l'espace de recherche par les connaissances métier, de l'incorporation des lois physiques directement dans la fonction de perte de l'IA (Physics-Informed ML) et d'une interface LLM pour l'interaction humaine.
- **APRÈS** : Un système d'IA guidé par la physique capable d'effectuer une conception inverse rapide et physiquement réaliste dans des espaces à forte dimension avec peu de données.

**Dominant** : P5 Combinaison — 0.85 — La solution associe au sein d'un même cadre fonctionnel l'IA guidée par les données, la modélisation physique (PIML) et les connaissances métier d'experts.
**Secondaire** : P10 Action préliminaire — 0.75 — Les connaissances métier et contraintes physiques sont appliquées en amont pour prétraiter et réduire l'espace des variables avant l'optimisation par l'IA.

- **↑35 Adaptabilité / ↓37 Complexité du contrôle** (0.8) — Si nous améliorons la précision et la capacité à explorer de grands espaces de conception par des modèles d'IA complexes, alors le besoin en données et la complexité du contrôle du procédé se détériorent.  
  *preuve* : purely data-driven approaches often struggle in realistic manufacturing settings characterized by sparse data, high-dimensional design spaces, and complex constraints

**Contradiction physique** : oui — L'espace de recherche de conception doit être vaste pour trouver des solutions optimales inédites, et restraint/étroit pour être exploitable rapidement avec peu de données. — séparation : conditions
**Matrice** (cellule [35, 37]) recommande [1] · observés [5, 10] → **hors recommandations de la matrice**
Portée : procede

## 14. Formulation de résine polyester à faible retrait
*Dilatometric study of low profile unsaturated polyester resins* (1995) — https://doi.org/10.1002/pen.760351005

**Résumé inventif** : L'incorporation d'additifs à faible retrait (LPA) dans des résines polyesters insaturées permet de compenser le retrait volumique lors du thermodurcissement. Un suivi dilatométrique et morphologique permet d'ajuster la concentration de l'additif et la température de cuisson pour éliminer la déformation des pièces.

- **AVANT** : Les résines polyesters insaturées subissent un retrait volumique important lors de leur polymérisation thermodurcissable, entraînant des défauts dimensionnels et de surface.
- **PROBLÈME** : Réduire le retrait lors de la réticulation sans altérer la cuisson ni la tenue mécanique de la résine.
- **TRANSFORMATION** : Ajout d'additifs thermoplastiques à faible retrait (LPA) dans la formulation de la résine et contrôle de la température de cuisson pour induire une séparation de phase microscopique compensatrice.
- **APRÈS** : Une résine polyester insaturée à stabilité dimensionnelle élevée (Low Profile) présentant un retrait volumique quasi nul après moulage.

**Dominant** : P35 Modification des paramètres physiques/chimiques — 0.85 — La modification de la formulation chimique par l'ajout d'additifs LPA et l'ajustement de la température de cuisson modifient le comportement de polymérisation pour annuler le retrait.
**Secondaire** : P40 Matériaux composites — 0.75 — L'association d'un réseau thermodurcissable et d'un polymère thermoplastique crée un système multiphasique aux propriétés dimensionnelles compensées.

- **↑14 Résistance / ↓29 Précision de la fabrication** (0.8) — Si nous augmentons la réticulation pour améliorer la durabilité/résistance, alors le retrait volumique dégrade la précision dimensionnelle.  
  *preuve* : L'article étudie l'effet de la concentration d'additif et de la température de cuisson sur le contrôle du retrait volumique lors de la polymérisation.

**Contradiction physique** : non
**Matrice** (cellule [14, 29]) recommande [3, 27] · observés [35, 40] → **hors recommandations de la matrice**
Portée : matiere

## 15. Injection hybride assistée gaz et moussage
*Development of Innovative Gas-assisted Foam Injection Molding Technology* (2014) — http://hdl.handle.net/1807/43608

**Résumé inventif** : Cette étude combine le moulage par injection avec agent de foisonnement (FIM) et l'injection assistée par gaz (GAIM) en un procédé unique (GAFIM). La structure résultante comporte une peau solide, une couche moussée et un cœur creux, offrant une excellente absorption acoustique pour une épaisseur fortement réduite.

- **AVANT** : Les pièces sont fabriquées soit par moussage sous pression (FIM) pour réduire la masse, soit par injection assistée gaz (GAIM) pour créer une cavité interne, ou nécessitent de mousses polyuréthane épaisses (22 mm) pour l'isolation acoustique.
- **PROBLÈME** : Pour obtenir une haute performance d'absorption acoustique avec les méthodes conventionnelles, il faut augmenter considérablement l'épaisseur et le volume de matériau, ce qui augmente le poids et le temps de cycle.
- **TRANSFORMATION** : Combinaison synergique de deux procédés d'injection séparés (FIM et GAIM) pour mouler séquentiellement une structure sandwich hybride intégrant simultanément une peau pleine, une zone intermédiaire moussée et un canal central creux.
- **APRÈS** : Une pièce thermoplastique monolithique à trois zones concentriques (peau solide / couche moussée / cœur creux) de seulement 6,4 mm d'épaisseur surpassant l'isolation acoustique des mousses PU de 22 mm.

**Dominant** : P5 Combinaison — 0.95 — Fusion de deux technologies d'injection distinctes (moulage moussé FIM et injection assistée gaz GAIM) en un procédé unique GAFIM.
**Secondaire** : P1 Segmentation — 0.85 — Division de la section transversale de la pièce en trois zones structurelles distinctes aux fonctions complémentaires (peau pleine, mousse, cavité).
**Secondaire** : P31 Matériaux poreux — 0.8 — Intégration d'une couche intermédiaire à structure cellulaire moussée pour absorber l'énergie acoustique sans alourdir la pièce.

- **↑8 Volume de l'objet stationnaire / ↓31 Effets secondaires nuisibles** (0.9) — Si nous réduisons le volume et l'épaisseur de la pièce (8) pour économiser de la matière, alors l'absorption des nuisances acoustiques (31) se détériore.  
  *preuve* : The foam structure manufactured by GAFIM consists of a solid skin layer, a foam layer, and a hollow core; and its 6.4-mm thick sample outperformed the conventional 22-mm thick polyurethane foam in terms of the acoustic absorption coefficient.

**Contradiction physique** : oui — La section de la pièce doit être dense et pleine pour garantir la rigidité de surface, et poreuse/creuse pour absorber le son et réduire la masse. — séparation : espace
**Matrice** (cellule [8, 31]) recommande [30, 18, 35, 4] · observés [5, 1, 31] → **hors recommandations de la matrice**
Portée : procede

## 16. Modélisation structurée des capacités d'injection pour DFM
*A manufacturing model to capture injection moulding process capabilities to support design for manufacture* (1994) — https://dspace.lboro.ac.uk/2134/10338

**Résumé inventif** : Cette étude structure les capacités du procédé d'injection sous forme d'un modèle de données unifié (EXPRESS/Objet) divisé en caractéristiques de moulabilité, éléments de moule et de presse. Ce modèle alimente en temps réel des outils DFM pour fournir un retour d'information continu aux concepteurs dès la phase de modélisation.

- **AVANT** : Les informations sur les capacités et contraintes du procédé d'injection plastique sont dispersées, implicites ou consultées tardivement lors de la conception.
- **PROBLÈME** : L'absence de formalisation structurée du procédé empêche l'évaluation automatique et précoce de la moulabilité lors de la conception guidée par ordinateur (DFM).
- **TRANSFORMATION** : Unification et catégorisation des connaissances du procédé (moulabilité, outillage, machine) au sein d'une architecture de données standardisée (EXPRESS) interconnectée à des règles d'évaluation objet.
- **APRÈS** : Un modèle de fabrication centralisé qui alimente dynamiquement des applications DFM pour conseiller l'intervenant au fur et à mesure que le modèle pièce évolue.

**Dominant** : P23 Rétroaction — 0.85 — La structure de données renvoie automatiquement un conseil/retour d'information d'injections au concepteur au fur et à mesure que la géométrie de la pièce évolue.
**Secondaire** : P1 Segmentation — 0.75 — Décomposition systématique du domaine de connaissances en sous-entités distinctes : fonctions de moulabilité, éléments de moule et éléments de presse.

- **↑35 Adaptabilité / ↓37 Complexité du contrôle** (0.7) — Si nous améliorons la précision des règles de conception et l'aide à la décision (35) par l'intégration d'un modèle complet, alors la complexité de gestion de l'information et du contrôle de conception (37) augmente.  
  *preuve* : To explore the use of the Manufacturing Model information to support Design for Manufacturing applications, the resulting model must provide a common source of information to a range of interacting DFM applications.

**Contradiction physique** : non
**Matrice** (cellule [35, 37]) recommande [1] · observés [23, 1] → **concordance partielle**
Portée : cao

## 17. Prototypage rapide d'élastomères par moules imprimés 3D
*Rapid and Low-cost Prototyping of Medical Devices Using 3D Printed Molds for Liquid Injection Molding* (2014) — https://doi.org/10.3791/51745

**Résumé inventif** : La solution remplace les moules métalliques usinés et les presses d'injection industrielles coûteuses par des moules imprimés en 3D (FDM) associés à un dessiccateur de laboratoire adapté. Cela permet un prototypage rapide et économique de pièces médicales complexes en silicone.

- **AVANT** : Le moulage par injection de silicone liquide nécessite des moules métalliques usinés et des équipements d'injection industriels très coûteux et longs à fabriquer.
- **PROBLÈME** : L'investissement financier et les délais d'outillage empêchent le prototypage rapide et itératif à bas coût de dispositifs élastomères.
- **TRANSFORMATION** : Remplacement de l'outillage métallique par des moules polymeres imprimés en 3D par dépôt de fil (FDM) et utilisation d'un dessiccateur de laboratoire modifié en guise de système d'injection et de dégazage.
- **APRÈS** : Un procédé de moulage par injection de liquide à bas coût permettant la fabrication itérative rapide de dispositifs médicaux complexes en silicone au sein d'un laboratoire classique.

**Dominant** : P27 Remplacement par une alternative gratuite — 0.9 — Le moule métallique usiné et la presse d'injection industrielle sont substitués par des équipements très peu coûteux et accessibles : un moule imprimé en 3D FDM et un dessiccateur adapté.
**Secondaire** : P28 Substitution du principe mécanique — 0.7 — L'injection conventionnelle sous forte pression mécanique est remplacée par un transfert de fluide assisté par dépression/pression dans un dessiccateur.

- Aucune contradiction technique Altshuller suffisamment démontrée.

**Contradiction physique** : non
**Matrice** (cellule None) recommande [] · observés [27, 28] → **contradiction indéterminée**
Portée : procede

## 18. Fabrication hybride d'inserts par entités géométriques
*A Novel Feature-Based Manufacturability Assessment System for Evaluating Selective Laser Melting and Subtractive Manufacturing Injection Moulding Tool Inserts* (2023) — https://doi.org/10.3390/designs7030068

**Résumé inventif** : L'article présente un système d'évaluation de la fabriquabilité basé sur les entités géométriques (FBMAS) pour la réalisation d'inserts de moules d'injection. Il permet d'associer localement la fabrication additive par fusion laser (SLM) et l'usinage soustractif selon la complexité des zones.

- **AVANT** : L'évaluation du procédé de fabrication des inserts de moule se fait de manière globale ou conventionnelle, soit entièrement en usinage soustractif, soit entièrement en fabrication additive.
- **PROBLÈME** : L'usinage traditionnel peine sur les géométries internes complexes, tandis que la fabrication additive (SLM) seule présente des limitations d'état de surface, de précision dimensionnelle et de coût.
- **TRANSFORMATION** : Décomposition de l'insert en entités géométriques individuelles et affectation différenciée du procédé de fabrication (additive SLM ou usinage soustractif) selon la complexité et les exigences de chaque zone.
- **APRÈS** : Un insert d'outillage hybride optimisé où chaque zone est produite par le procédé le plus adapté à ses contraintes géométriques et de qualité.

**Dominant** : P3 Qualité locale — 0.85 — Chaque entité ou zone géométrique de l'insert est fabriquée en utilisant le procédé (SLM ou soustractif) le mieux adapté à ses exigences locales de forme et de précision.
**Secondaire** : P5 Combinaison — 0.75 — Combinaison des procédés de fabrication additive (SLM) et soustraire au sein de la même pièce d'outillage.
**Secondaire** : P1 Segmentation — 0.65 — Décomposition de la géométrie globale de l'outil en entités géométriques distinctes pour leur analyse et fabrication.

- **↑12 Forme / ↓29 Précision de la fabrication** (0.85) — Si nous augmentons la complexité géométrique de l'insert par la fabrication additive, alors la précision de fabrication et l'état de surface se détériorent.  
  *preuve* : Additive manufacturing is capable of fabricating complex shapes, yet there are limiting aspects to surface integrity, dimensional accuracy.

**Contradiction physique** : oui — L'insert de moule doit être fabriqué par impression 3D (SLM) pour réaliser des formes complexes et ne doit pas être fabriqué par impression 3D pour garantir la précision dimensionnelle et l'état de surface. — séparation : espace
**Matrice** (cellule [12, 29]) recommande [32, 30, 40] · observés [3, 5, 1] → **hors recommandations de la matrice**
Portée : procede

## 19. Redesign DFMA d'une tondeuse à cheveux
*Re-designing of hair clipper using design for manufacturing and assembly* (2023) — https://doi.org/10.4995/jarte.2023.18810

**Résumé inventif** : Redesign d'une tondeuse à cheveux en appliquant les méthodologies DFMA pour simplifier la structure du produit. L'intégration et la réduction du nombre de pièces permettent de diminuer le temps et les coûts d'assemblage.

- **AVANT** : La tondeuse conventionnelle est composée de nombreuses pièces distinctes nécessitant une longue séquence d'assemblage manuelle ou automatisée.
- **PROBLÈME** : Le grand nombre de composants augmente le temps d'assemblage, les coûts de fabrication et risque de diminuer l'efficacité globale de la conception.
- **TRANSFORMATION** : Réduction du nombre de pièces par fusion/intégration de composants adjacents et simplification des liaisons mécaniques selon les principes de Boothroyd Dewhurst.
- **APRÈS** : Une tondeuse optimisée comportant nettement moins de pièces, avec une efficacité de conception doublée et un temps d'assemblage réduit de près de 50 %.

**Dominant** : P1 Segmentation — 0.75 — L'approche consiste à restructurer les sous-ensembles en réduisant/regroupant les éléments pour éliminer les interfaces inutiles.
**Secondaire** : P34 Élimination/régénération de parties — 0.85 — Suppression directe des pièces non essentielles à la fonction principale après analyse DFMA.

- **↑25 Perte de temps / ↓12 Forme** (0.7) — Si nous réduisons le nombre de pièces et la complexité d'assemblage pour diminuer le temps de cycle, alors la complexité de forme de certaines pièces individuelles réinventées peut augmenter.  
  *preuve* : L'application du DFMA a permis de réduire le temps d'assemblage de 322.91s à 163.81s en reconcevant l'architecture globale des composants.

**Contradiction physique** : oui — Les composants doivent être multiples pour assurer des fonctions distinctes et uniques pour être faciles à assembler et fabriquer. — séparation : tout-parties
**Matrice** (cellule [25, 12]) recommande [4, 10, 34, 17] · observés [1, 34] → **concordance partielle**
Portée : cao

## 20. Structure d'équipement intérieur en composite thermoplastique allégé
*Innovative composite materials application in the design of seats and interior parts* (2012) — https://scholar.uwindsor.ca/etd/5355

**Résumé inventif** : Substitution d'une structure métallique de dossier de siège par une structure en composite thermoplastique. Cela permet de réduire significativement la masse tout en conservant la rigidité mécanique nécessaire.

- **AVANT** : Conception conventionnelle de dossiers de sièges arrière utilisant une armature en acier dense et lourde.
- **PROBLÈME** : Le poids élevé de la structure en acier augmente la consommation de carburant et les émissions de CO2 du véhicule.
- **TRANSFORMATION** : Remplacement du matériau homogène métallique par un matériau composite à matrice thermoplastique léger, recyclable et à haute rigidité spécifique.
- **APRÈS** : Une structure de dossier de siège en composite thermoplastique allégée offrant une rigidité équivalente et une meilleure recyclabilité.

**Dominant** : P40 Matériaux composites — 0.95 — Remplacement d'une structure homogène en acier par un matériau composite thermoplastique combinant légèreté et rigidité mécanique.

- **↑2 Poids de l'objet stationnaire / ↓14 Résistance** (0.9) — Si nous réduisons la masse de la structure par l'emploi de composites légers, alors la résistance mécanique et la rigidité risquent de se détériorer.  
  *preuve* : the substitution of a current rear seat back steel structure, meeting stringent weight and stiffness requirements.

**Contradiction physique** : oui — Le matériau doit être dense/rigide pour résister aux efforts mécaniques, et peu dense/léger pour minimiser la consommation de carburant. — séparation : tout-parties
**Matrice** (cellule [2, 14]) recommande [28, 2, 10, 27] · observés [40] → **hors recommandations de la matrice**
Portée : matiere

## 21. Micropompe MHD à courant alternatif périodique
*Development of micropump for microfluidic applications* (2006) — https://doi.org/10.31390/gradschool_dissertations.2083

**Résumé inventif** : Un micropompe magnétohydrodynamique (MHD) utilise un courant alternatif (AC) au lieu d'un courant continu (DC) pour actionner le fluide conducteur par la force de Lorentz. Ce changement de régime électrique élimine l'électrolyse continue et prévient la formation de bulles qui bloquait le fonctionnement du système.

- **AVANT** : Les micropompes MHD utilisent un courant continu (DC) pour générer une force de Lorentz entraînant le fluide conducteur.
- **PROBLÈME** : L'actionnement par courant continu provoque une électrolyse du fluide, générant des bulles de gaz qui perturbent ou bloquent l'écoulement.
- **TRANSFORMATION** : Remplacement de la tension continue constante (DC) par une tension alternative périodique (AC) combinée à une modélisation par spectroscopie d'impédance.
- **APRÈS** : Une micropompe à écoulement continu sans pièces mécaniques mobiles, dans laquelle la formation de bulles est fortement réduite.

**Dominant** : P19 Action périodique — 0.9 — Le passage d'un courant continu (action continue) à un courant alternatif (action périodique/pulsée) permet d'inhiber la réaction d'électrolyse tout en maintenant l'entraînement du fluide.
**Secondaire** : P35 Modification des paramètres physiques/chimiques — 0.75 — Modification du régime électrique d'alimentation (signal DC vers AC) pour modifier le comportement électrochimique à l'interface fluide/électrode.

- **↑9 Vitesse / ↓31 Effets secondaires nuisibles** (0.85) — Si l'on augmente la force d'actionnement électrique du fluide en courant continu, alors la génération de bulles de gaz par électrolyse augmente, dégradant le fonctionnement.  
  *preuve* : The AC-type MHD micropump was designed and analyzed as a solution to the bubble formation problem encountered in DC-type MHD micropump.

**Contradiction physique** : oui — Le champ électrique doit être continu pour maintenir une force unidirectionnelle continue sur le fluide, et ne doit pas être continu pour éviter l'électrolyse et la formation de bulles. — séparation : temps
**Matrice** (cellule [9, 31]) recommande [2, 24, 35, 21] · observés [19, 35] → **concordance partielle**
Portée : procede

## 22. Méthodologie intégrée DFM-IAO pour pièces injectées
*An integrated design and manufacture methodology for injection moulded components* (2002) — https://research.thea.ie/bitstream/20.500.12065/407/1/Keith_Vaugh_20130911151539.pdf

**Résumé inventif** : Cette étude propose de remplacer le cycle de développement séquentiel traditionnel des pièces injectées par une méthodologie intégrée. En combinant la conception pour la manufacturabilité (DFM), la simulation numérique (CAO/IAO) et l'outillage rapide, les défauts sont corrigés virtuellement avant la réalisation des outillages de série.

- **AVANT** : Un cycle de développement séquentiel de type « conception-fabrication-test-rupture » nécessitant des itérations physiques d'outillage répétées.
- **PROBLÈME** : Des délais de mise sur le marché excessifs et des coûts élevés liés aux incertitudes de moulage et aux modifications tardives des moules.
- **TRANSFORMATION** : Anticipation des contraintes de moulage par intégration de la DFM dès l'origine, remplacement des essais physiques par la simulation virtuelle (IAO) et validation rapide par outillage prototype.
- **APRÈS** : Un processus de développement virtuel et rapide où la pièce et son outillage sont validés virtuellement avant toute fabrication d'outillage définitif.

**Dominant** : P10 Action préliminaire — 0.85 — La simulation numérique et l'analyse DFM sont exécutées en amont pour détecter et résoudre les problèmes de moulage avant la fabrication réelle de l'outillage.
**Secondaire** : P26 Copie — 0.8 — Remplacement des prototypes et outillages physiques coûteux par des modèles informatiques virtuels (CAO/IAO) pour réaliser les essais.
**Secondaire** : P5 Combinaison — 0.75 — Intégration au sein d'une même méthodologie unifiée des outils DFM, CAO, IAO et du prototypage rapide.

- Aucune contradiction technique Altshuller suffisamment démontrée.

**Contradiction physique** : non
**Matrice** (cellule None) recommande [] · observés [10, 26, 5] → **contradiction indéterminée**
Portée : procede

## 23. Conception générative de canaux conformes optimisés localement
*Generative design of conformal cooling channels for hybrid-manufactured injection moulding tools* (2023) — https://doi.org/10.21203/rs.3.rs-3081027/v1

**Résumé inventif** : Cette étude présente un algorithme génétique de conception générative ajustant automatiquement la géométrie et le tracé des canaux de refroidissement conformes (CCC) en fonction de la variabilité thermique locale à l'interface moule-pièce. L'adaptation locale des canaux permet d'optimiser l'évacuation de la chaleur et de réduire significativement le temps de cycle.

- **AVANT** : Les canaux de refroidissement d'outillages d'injection plastique sont percés en lignes droites conventionnelles ou conçus manuellement de façon uniforme.
- **PROBLÈME** : La conception manuelle ou conventionnelle des canaux ne prend pas en compte la variabilité spatiale et locale de la température, entraînant un refroidissement inefficace ou hétérogène et des temps de cycle prolongés.
- **TRANSFORMATION** : Modulation automatique du tracé et de la géométrie des canaux de refroidissement (conception générative) guidée par un algorithme génétique prenant en compte le champ thermique local à l'interface outil-pièce.
- **APRÈS** : Un moule doté de canaux de refroidissement conformes à géométrie localement optimisée, réduisant les temps de cycle d'injection plastique.

**Dominant** : P3 Qualité locale — 0.9 — Le réseau de canaux de refroidissement passe d'une structure uniforme à une architecture adaptée localement en réponse à la variabilité spatiale des contraintes thermiques.
**Secondaire** : P23 Rétroaction — 0.8 — L'algorithme génétique réajuste la conception des canaux en boucle fermée à partir des résultats de simulation thermique locale.

- **↑39 Productivité / ↓36 Complexité du dispositif** (0.85) — Si nous optimisons localement le tracé des canaux de refroidissement pour accélérer le refroidissement, alors la complexité de conception et de l'outillage augmente.  
  *preuve* : Effective cooling systems for injection moulding tools are critical to reducing manufacturing costs & cycle time... adjustable CCC design in response to spatial variability... driven by a genetic algorithm.

**Contradiction physique** : non
**Matrice** (cellule [39, 36]) recommande [12, 17, 28, 24] · observés [3, 23] → **hors recommandations de la matrice**
Portée : procede

## 24. Ingénierie métabolique par inactivation de voies concurrentes et surexpression
*Metabolic engineering of the Colombian strain Clostridium sp. IBUN 158B in order to improve the bioconversion of glycerol into 1,3-propanediol* (2013) — https://doi.org/10.18725/oparu-2603

**Résumé inventif** : Modification génétique de la souche Clostridium sp. IBUN 158B pour optimiser la conversion du glycérol en 1,3-propanediol. La stratégie combine l'inactivation de gènes de voies métaboliques secondaires concurrentes et la surexpression des gènes clés de la voie de réduction du glycérol.

- **AVANT** : La souche sauvage convertit le glycérol en 1,3-propanediol, mais une partie des cofacteurs (NADH) et du substrat est détournée par des voies métaboliques secondaires produisant des sous-produits (hydrogène, butyrate, lactate).
- **PROBLÈME** : Le rendement et la productivité en 1,3-propanediol sont insuffisants pour une exploitation industrielle en raison de la compétition métabolique pour le NADH et le glycérol.
- **TRANSFORMATION** : Suppression/inactivation ciblée des gènes codant les enzymes des voies concurrentes (hydA, hbd, ldhA) et surexpression simultanée du groupe de gènes de la voie réductrice du glycérol (dhaB1, dhaB2, dhaT).
- **APRÈS** : Une souche recombinante dont le flux métabolique et les ressources réduites (NADH) sont réorientés quasi exclusivement vers la production optimale de 1,3-propanediol.

**Dominant** : P2 Extraction — 0.85 — L'inactivation ciblée des gènes (hydA, hbd, ldhA) élimine du métabolisme cellulaire les fonctions/voies parasites qui consomment le NADH nécessaire à la synthèse visée.
**Secondaire** : P34 Élimination/régénération de parties — 0.75 — Les éléments génétiques et enzymatiques inutiles ou nuisibles au rendement final ont été éliminés du réseau métabolique fonctionnel.

- **↑39 Productivité / ↓23 Gaspillage de substance** (0.85) — Si l'on cherche à augmenter la productivité en 1,3-propanediol, alors le gaspillage de substrat et de cofacteurs NADH augmente dans les voies métaboliques secondaires.  
  *preuve* : In order to reach an industrially efficient 1,3-PD production level (...) more NADH generated during the oxidative metabolism should be available for 1,3-PD production

**Contradiction physique** : non
**Matrice** (cellule [39, 23]) recommande [28, 10, 35, 23] · observés [2, 34] → **hors recommandations de la matrice**
Portée : procede

## 25. Échafaudage composite PLA-silice expansé par fluide supercritique
*Construction of novel tissue engineering scaffolds using supercritical fluid gas foaming* (2011) — http://etheses.bham.ac.uk/3184/2/collins_11_PhD.pdf

**Résumé inventif** : L'incorporation de particules de silice minérale dans une matrice de polylactide (PLA) traitée par fluide supercritique (SCF) permet de structurer précisément la porosité du biomatériau. Cette combinaison améliore significativement la résistance mécanique à la limite d'élasticité tout en contrôlant la taille et la connectivité des pores.

- **AVANT** : Les échafaudages tissulaires en polymère biodégradable (PLA) sont élaborés par moussage supercritique sans charge minérale.
- **PROBLÈME** : Les structures poreuses obtenues manquent de résistance mécanique et leur architecture de pores (taille, épaisseur des parois, connectivité) est difficile à réguler.
- **TRANSFORMATION** : L'association de la silice minérale au PLA avant le processus de moussage supercritique permet d'agir comme agent de structuration de la porosité et de renfort mécanique.
- **APRÈS** : Un échafaudage composite PLA-silice présentant une résistance mécanique accrue (jusqu'à 60 N supplémentaires à la limite d'élasticité) et une architecture poreuse contrôlée.

**Dominant** : P40 Matériaux composites — 0.88 — L'association du polymère biodégradable PLA à une phase minérale de silice crée un matériau composite aux propriétés mécaniques et structurales supérieures.
**Secondaire** : P31 Matériaux poreux — 0.75 — Le recours au moussage par fluide supercritique génère une structure poreuse interconnectée indispensable à la fonction d'échafaudage cellulaire.

- **↑14 Résistance / ↓26 Quantité de substance** (0.82) — Si nous améliorons la résistance mécanique par l'ajout de silice dans le polymère, alors la porosité globale et la taille des pores diminuent.  
  *preuve* : silica incorporation increased the load tolerated at yield by up to 60N [...] pore diameters in the range of 0.088-0.924 mm (0% silica) to 0.044–0.342 mm (33.3% silica)

**Contradiction physique** : non
**Matrice** (cellule [14, 26]) recommande [29, 10, 27] · observés [40, 31] → **hors recommandations de la matrice**
Portée : matiere

## 26. Variation locale des épaisseurs de paroi anti-gauchissement
*Variation of Part Wall Thicknesses to Reduce Warpage of Injection-Molded Part: Robust Design Against Process Variability* (1997) — https://doi.org/10.1080/03602559708000661

**Résumé inventif** : Afin d'atténuer le gauchissement des pièces injectées causé par les variations du procédé, la règle conventionnelle d'épaisseur de paroi constante est abandonnée. L'épaisseur de paroi est modifiée localement dans les limites de tolérance autorisées pour compenser les déformations thermiques et stabiliser la géométrie finale.

- **AVANT** : Les pièces moulées par injection sont conçues avec une épaisseur de paroi strictement uniforme sur toute la géométrie selon les règles de l'art conventionnelles.
- **PROBLÈME** : Malgré une épaisseur uniforme, les fluctuations inévitables des conditions du procédé d'injection provoquent du gauchissement et des déformations géométriques.
- **TRANSFORMATION** : L'épaisseur de paroi uniforme est remplacée par une distribution d'épaisseurs localement différenciées, optimisée pour contrecarrer les déformations dues aux variations du procédé.
- **APRÈS** : Une pièce possédant des variations d'épaisseurs locales contrôlées, présentant un gauchissement moyen nettement réduit et une meilleure robustesse face aux variations de procédé.

**Dominant** : P3 Qualité locale — 0.95 — Passage d'une épaisseur de paroi uniforme sur toute la pièce à une structure dont l'épaisseur varie localement selon les contraintes de déformation de chaque zone.
**Secondaire** : P4 Asymétrie — 0.7 — Remplacement d'une géométrie symétrique/régulière en épaisseur par une géométrie asymétrique ou modulée pour contrecarrer le gauchissement.

- **↑13 Stabilité de l'objet / ↓12 Forme** (0.85) — Si nous faisons varier localement l'épaisseur de paroi pour compenser le retrait thermique, alors la stabilité dimensionnelle de la pièce se trouve améliorée, mais la complexité de la forme géométrique s'en trouve augmentée.  
  *preuve* : Varying wall thicknesses exhibits better warpage characteristics in terms of warpage mean and variance compared to constant wall thicknesses that comply with uniform wall thickness rules.

**Contradiction physique** : oui — L'épaisseur de la pièce doit être constante pour respecter les règles de conception conventionnelles et non constante (variable) pour compenser le gauchissement local. — séparation : espace
**Matrice** (cellule [13, 12]) recommande [22, 1, 18, 4] · observés [3, 4] → **concordance partielle**
Portée : cao

## 27. Refroidissement conformel tridimensionnel pour moule d'injection
*Cycle Time Reduction in Injection Molding Process by Selection of Robust Cooling Channel Design* (2014) — https://doi.org/10.1155/2014/968484

**Résumé inventif** : Remplacement des canaux de refroidissement droits conventionnels par des canaux de refroidissement conformels qui épousent la géométrie 3D de la cavité du moule. Cette modification permet une dissipation thermique uniforme, réduisant ainsi le temps de cycle et le gauchissement de la pièce.

- **AVANT** : Les moules d'injection utilisent des canaux de refroidissement droits, perçus mécaniquement selon des lignes droites simples.
- **PROBLÈME** : Les canaux droits ne suivent pas la forme complexe de la cavité, entraînant un refroidissement non uniforme, des temps de refroidissement longs et du gauchissement de la pièce.
- **TRANSFORMATION** : Remplacement du tracé rectiligne des canaux par des circuits conformels qui suivent fidèlement la géométrie et les contours 3D de la surface de la cavité.
- **APRÈS** : Un circuit de refroidissement tridimensionnel conformel qui garantit une extraction de chaleur rapide et homogène sur toute la surface moulée.

**Dominant** : P17 Nouvelle dimension — 0.9 — Passage d'un réseau de canaux de refroidissement linéaires et bidimensionnels à un tracé conformel épousant la géométrie tridimensionnelle complexe de la cavité.
**Secondaire** : P14 Courbure — 0.8 — Substitution des perçages droits et rectilignes par des canaux courbes et épousant les formes de la pièce.
**Secondaire** : P3 Qualité locale — 0.7 — Adaptation de la proximité et du tracé des canaux à chaque zone spécifique de la cavité pour uniformiser la température.

- **↑39 Productivité / ↓13 Stabilité de l'objet** (0.85) — Si nous réduisons le temps de refroidissement pour augmenter la productivité, alors le gradient thermique s'accentue et dégrade la stabilité dimensionnelle (gauchissement) de la pièce.  
  *preuve* : whereas the cycle time of a part can be reduced by reducing the cooling time which can only be achieved by the uniform temperature distribution in the molded part [...] minimum time to reach ejection temperature, uniform temperature distribution, and minimum warpage of part

**Contradiction physique** : non
**Matrice** (cellule [39, 13]) recommande [35, 3, 22, 39] · observés [17, 14, 3] → **concordance partielle**
Portée : cao

## 28. Contrôle qualité en ligne par jauges sur colonnes de presse
*Quality Indexes Design for Online Monitoring Polymer Injection Molding* (2019) — https://doi.org/10.1155/2019/3720127

**Résumé inventif** : Un système de contrôle qualité en ligne mesure l'allongement des colonnes de la presse via des jauges de déformation pour évaluer l'évolution de la force de verrouillage. Cette mesure indirecte, combinée aux profils de pression de la buse et de la cavité, permet un suivi prédictif de la qualité de la pièce moulée sans modifier l'outillage.

- **AVANT** : La qualité des pièces injectées est contrôlée a posteriori ou nécessite l'intégration de capteurs de pression intrusifs et coûteux directement à l'intérieur des cavités du moule.
- **PROBLÈME** : L'instrumentation directe de la cavité augmente la complexité du moule, son coût et le risque d'endommagement, tout en compliquant la maintenance.
- **TRANSFORMATION** : Instrumenter les colonnes de guidage existantes de la presse avec des jauges de déformation externes afin d'extraire des indicateurs de qualité à partir de la variation de force de verrouillage et de l'énergie d'injection.
- **APRÈS** : Un contrôle qualité en temps réel, non destructif et non intrusif vis-à-vis du moule, basé sur le comportement structural global de la presse et les paramètres de plastification.

**Dominant** : P23 Rétroaction — 0.85 — Mise en place d'une boucle d'information continue sur l'état du procédé en mesurant la déformation dynamique de la structure pour corriger ou prédire la qualité des pièces.
**Secondaire** : P28 Substitution du principe mécanique — 0.75 — Remplacement de la mesure directe de pression/matière dans le moule par une mesure opto-électronique indirecte du champ de déformation mécanique sur les colonnes.

- **↑28 Précision de la mesure / ↓36 Complexité du dispositif** (0.75) — Si nous améliorons la précision du suivi de qualité en temps réel par l'instrumentation de la presse, alors la complexité du dispositif de mesure augmente.  
  *preuve* : The study proposes a quality index based on the clamping force increment... providing a feasible basis for the realization of an on-line quality monitoring.

**Contradiction physique** : non
**Matrice** (cellule [28, 36]) recommande [27, 35, 10, 34] · observés [23, 28] → **hors recommandations de la matrice**
Portée : procede

## 29. Transfer learning pour modélisation du procédé d'injection
*Induced network-based transfer learning in injection molding for process modelling and optimization with artificial neural networks* (2021) — https://doi.org/10.1007/s00170-020-06511-3

**Résumé inventif** : Afin d'éviter le besoin d'un grand nombre d'essais coûteux pour modéliser le procédé d'injection d'une nouvelle pièce par réseau de neurones, la solution applique le transfert d'apprentissage à partir de modèles préalablement entraînés sur d'autres pièces. Cela permet d'obtenir un modèle prédictif très précis avec seulement quatre points de données d'essai.

- **AVANT** : L'entraînement d'un réseau de neurones pour optimiser les paramètres de moulage par injection d'une nouvelle pièce nécessite l'acquisition d'un grand volume de données d'essais expérimentaux.
- **PROBLÈME** : La collecte massive de données pour chaque nouvelle géométrie de pièce consomme du temps, de la matière et immobilise la presse à injecter.
- **TRANSFORMATION** : Réutilisation de modèles de réseaux de neurones préalablement entraînés sur 59 pièces différentes (domaine source) et réajustement des poids du réseau sur la pièce cible avec un échantillon extrêmement réduit.
- **APRÈS** : Un modèle prédictif haute précision (R² >= 0,9) est obtenu pour la nouvelle pièce avec seulement 4 points d'essai expérimentaux.

**Dominant** : P10 Action préliminaire — 0.85 — Réaliser un pré-entraînement préalable des réseaux de neurones sur des procédés sources avant d'aborder le processus cible afin de minimiser l'effort d'apprentissage final.
**Secondaire** : P6 Universalité — 0.65 — Exploiter un modèle ou une structure de réseau de neurones générique capable d'effectuer la modélisation de plusieurs pièces différentes moyennant un ajustement mineur.

- **↑25 Perte de temps / ↓27 Fiabilité** (0.9) — Si nous réduisons le nombre d'essais expérimentaux pour diminuer le temps de mise au point (25), alors la précision et la fiabilité du modèle prédictif du procédé (27) se détériorent.  
  *preuve* : The necessity of an abundance of training data commonly hinders the broad use of machine learning... For the right source domain, only 4 sample points of the new process need to be generated to train a model... with a degree of determination R2 of 0.9 or higher.

**Contradiction physique** : oui — Le jeu de données d'apprentissage doit être volumineux pour garantir la précision du modèle et très réduit pour minimiser le temps et les coûts d'essais. — séparation : temps
**Matrice** (cellule [25, 27]) recommande [10, 30, 4] · observés [10, 6] → **concordance forte**
Portée : procede

## 30. Prédiction de qualité d'injection par arbre de décision
*Machine Learning in Injection Molding: An Industry 4.0 Method of Quality Prediction* (2022) — https://doi.org/10.3390/s22072704

**Résumé inventif** : Cette étude remplace l'inspection physique directe des pièces injectées par un modèle virtuel prédictif (Arbre de Décision) fondé sur l'extraction d'indices de pression en empreinte. Cette approche permet d'obtenir une précision de prédiction de qualité supérieure à 90 % en seulement quelques secondes d'apprentissage avec très peu de données.

- **AVANT** : La qualité des pièces injectées en moule multi-empreintes est évaluée par contrôle métrologique manuel, essais destructifs ou suivi empirique complexe de multiples paramètres machine.
- **PROBLÈME** : L'interdépendance complexe des paramètres de réglage rend la prédiction de qualité difficile et nécessite habituellement de grands volumes de données d'apprentissage et un temps de calcul élevé.
- **TRANSFORMATION** : Remplacement du contrôle physique/statistique classique par un modèle prédictif virtuel basique (arbre de décision) exploitant uniquement des indicateurs synthétiques extraits des signaux de pression.
- **APRÈS** : Un système de contrôle prédictif en ligne capable de déterminer la conformité des pièces multi-empreintes avec plus de 90 % de précision en 8 à 10 secondes d'apprentissage.

**Dominant** : P26 Copie — 0.85 — La mesure physique et l'inspection directe des pièces sont remplacées par un modèle virtuel prédictif (arbre de décision) basé sur les signaux de pression.
**Secondaire** : P23 Rétroaction — 0.75 — Introduction d'une boucle d'information en temps réel basée sur l'analyse des empreintes de pression pour piloter la qualité.

- **↑27 Fiabilité / ↓37 Complexité du contrôle** (0.8) — Si nous améliorons la fiabilité de la prédiction de qualité par l'intégration d'algorithmes d'apprentissage machine, alors la complexité du traitement des données et le temps d'apprentissage se détériorent.  
  *preuve* : The decision tree algorithm was the most accurate one, with a computational time of only 8-10 s... exceeded 90%, even for very little training data.

**Contradiction physique** : non
**Matrice** (cellule [27, 37]) recommande [27, 40, 28] · observés [26, 23] → **hors recommandations de la matrice**
Portée : procede

## 31. Régulation thermique segmentée prédictive par modèle pvT
*Prediction and validation of the specific volume for inline warpage control in injection molding* (2021) — https://doi.org/10.1016/j.polymertesting.2021.107393

**Résumé inventif** : Un contrôle thermique dynamique et segmenté du moule est développé pour réguler localement la température selon un modèle prédictif pvT. Cette régulation par zones homogénéise le volume spécifique local de la pièce, réduisant ainsi le gauchissement lors de l'injection.

- **AVANT** : La température du moule d'injection est régulée de manière globale et statique sur l'ensemble de la cavité.
- **PROBLÈME** : Les variations locales de pression et de vitesse de refroidissement créent un volume spécifique hétérogène, entraînant un retrait différentiel et le gauchissement de la pièce.
- **TRANSFORMATION** : Diviser la régulation thermique du moule en segments indépendants pilotés dynamiquement par un contrôle prédictif basé sur un modèle pvT modifié.
- **APRÈS** : Un moule à régulation thermique sectorisée capable de maintenir un volume spécifique homogène sur toute la géométrie de la pièce pour éliminer le gauchissement.

**Dominant** : P3 Qualité locale — 0.92 — La régulation thermique globale est divisée en plusieurs zones/segments indépendants afin d'appliquer des températures différentes selon les contraintes thermiques et de pression locales.
**Secondaire** : P23 Rétroaction — 0.82 — Utilisation d'une commande prédictive basée sur le comportement du volume spécifique prédit en temps réel pour ajuster dynamiquement la température du moule.

- Aucune contradiction technique Altshuller suffisamment démontrée.

**Contradiction physique** : oui — La température du moule doit être élevée pour limiter les écarts de volume spécifique et basse pour assurer un refroidissement efficace. — séparation : espace
**Matrice** (cellule None) recommande [] · observés [3, 23] → **contradiction indéterminée**
Portée : procede

## 32. Injection-compression dynamique pour micro-optiques
*Manufacturing Signatures of Injection Molding and Injection Compression Molding for Micro-Structured Polymer Fresnel Lens Production* (2018) — https://doi.org/10.3390/mi9120653

**Résumé inventif** : L'injection-compression (ICM) remplace l'injection conventionnelle à volume fixe en introduisant une phase de compression dynamique pendant le moulage des lentilles de Fresnel. Cette transformation permet d'obtenir une réplication micrométrique ultra-précise tout en réduisant la biréfringence et le gauchissement de la pièce.

- **AVANT** : La fabrication de lentilles optiques micro-structurées s'effectue par injection conventionnelle dans un moule fermé à volume fixe.
- **PROBLÈME** : Une forte pression de maintien est nécessaire pour répliquer fidèlement les micro-structures, mais elle génère des contraintes résiduelles, de la biréfringence et du gauchissement de la pièce.
- **TRANSFORMATION** : Remplacement du volume de cavité fixe par une fermeture dynamique contrôlée de la cavité (compression) pendant l'injection du polymère.
- **APRÈS** : Un procédé d'injection-compression permettant une répartition uniforme de la pression, une haute fidélité de réplication des micro-mots et une diminution des contraintes optiques/géométriques.

**Dominant** : P15 Dynamisme — 0.85 — La cavité de moulage rigide et fixe est rendue mobile et ajustable durant le cycle de moulage par l'ajout d'une phase de compression dynamique.
**Secondaire** : P35 Modification des paramètres physiques/chimiques — 0.65 — Modification du profil de pression et d'application des contraintes mécaniques durant la phase de solidification.

- **↑29 Précision de la fabrication / ↓31 Effets secondaires nuisibles** (0.85) — Si nous augmentons la fidélité de réplication des micro-structures par une augmentation de la pression, alors le gauchissement et la biréfringence augmentent.  
  *preuve* : ICM provides enhanced optical performances (...) in terms of birefringence and transmission (...) while ensuring required high accuracy geometrical replication.

**Contradiction physique** : oui — La cavité de moulage doit être ouverte/large pour permettre l'écoulement sans contrainte du polymère et fermée/étroite pour compacter très fortement les micro-détails. — séparation : temps
**Matrice** (cellule [29, 31]) recommande [4, 17, 34, 26] · observés [15, 35] → **hors recommandations de la matrice**
Portée : procede

## 33. Refroidissement conforme et inserts haute conductivité
*Enhanced Injection Molding Simulation of Advanced Injection Molds* (2017) — https://doi.org/10.3390/polym9020077

**Résumé inventif** : La solution remplace les canaux de refroidissement droits conventionnels par des canaux conformes épousant la géométrie de la pièce, combinés à l'utilisation d'inserts en alliage de cuivre à haute conductivité thermique (Ampcoloy 940). Cela permet d'uniformiser le retrait thermique et de réduire drastiquement le temps de refroidissement du cycle d'injection.

- **AVANT** : Les moules d'injection utilisent des canaux de refroidissement droits réalisés par perçage mécanique dans des blocs d'acier standard (ex. 1.2311 / P20).
- **PROBLÈME** : Le refroidissement est la phase la plus longue du cycle d'injection et l'extraction de chaleur est non uniforme, ce qui limite la productivité et peut déformer la pièce.
- **TRANSFORMATION** : Remplacement des canaux droits par des circuits de refroidissement conformes à la géométrie 3D de la pièce et substitution de l'acier par un alliage de cuivre à très haute conductivité thermique pour les inserts.
- **APRÈS** : Un moule d'injection à régulation thermique optimisée permettant une extraction de chaleur rapide, uniforme et ciblée.

**Dominant** : P14 Courbure — 0.85 — Substitution de lignes de refroidissement droites obtenues par forage par des canaux conformes courbes qui épousent la forme tridimensionnelle complexe de la pièce.
**Secondaire** : P35 Modification des paramètres physiques/chimiques — 0.8 — Remplacement du matériau de l'outillage (acier) par un alliage de cuivre à haute conductivité thermique pour modifier la vitesse d'extraction de la chaleur.
**Secondaire** : P3 Qualité locale — 0.75 — Positionnement des canaux et choix des matériaux d'insert adaptés localement à la géométrie et au besoin thermique spécifique de chaque zone de la cavité.

- **↑25 Perte de temps / ↓36 Complexité du dispositif** (0.8) — Si nous réduisons le temps de cycle en complexifiant le réseau de refroidissement avec des canaux conformes, alors la complexité de conception et d'outillage du moule augmente.  
  *preuve* : The most time-consuming phase of the injection molding cycle is cooling... Designing optimal cooling systems is a complex process; a proper design requires injection molding simulations

**Contradiction physique** : non
**Matrice** (cellule [25, 36]) recommande [6, 29] · observés [14, 35, 3] → **hors recommandations de la matrice**
Portée : cao

## 34. Nanocomposite PP/MWNT anti-retrait et anti-gauchissement
*Taguchi analysis of shrinkage and warpage of injection-moulded polypropylene/multiwall carbon nanotubes nanocomposites* (2009) — https://doi.org/10.3144/expresspolymlett.2009.79

**Résumé inventif** : Incorporation de 2 % en masse de nanotubes de carbone multi-parois (MWNT) dans du polypropylène pour réduire le retrait et le gauchissement des pièces injectées. L'utilisation du nanocomposite améliore la stabilité dimensionnelle et réduit la sensibilité de la pièce aux variations des paramètres de transformation.

- **AVANT** : L'injection plastique du polypropylène pur engendre un retrait thermique/cristallin et un gauchissement importants des pièces lors du refroidissement.
- **PROBLÈME** : Les variations dimensionnelles (retrait, gauchissement) altèrent la géométrie et la conformité des pièces, et l'optimisation des seuls paramètres de réglage machine reste limitée.
- **TRANSFORMATION** : Ajout d'une faible charge de nanotubes de carbone multi-parois (2 wt% MWNT) au polypropylène pour former un nanocomposite haute performance.
- **APRÈS** : Une réduction du retrait allant jusqu'à 48 % et du gauchissement de plus de 55 %, associée à une plus faible sensibilité aux fluctuations du procédé d'injection.

**Dominant** : P40 Matériaux composites — 0.95 — L'incorporation de nanotubes de carbone (MWNT) au sein du polypropylène crée une structure nanocomposite combinant les propriétés de la matrice et des renforts pour bloquer le retrait et le gauchissement.
**Secondaire** : P35 Modification des paramètres physiques/chimiques — 0.75 — La modification de la composition chimique de la matière première (additiver avec des MWNT) transforme le comportement de cristallisation et de retrait du matériau.

- Aucune contradiction technique Altshuller suffisamment démontrée.

**Contradiction physique** : oui — La matière doit être non chargée pour conserver une grande fluidité et simplicité lors du remplissage, tout en devant être chargée (nanocomposite) pour résister au retrait et au gauchissement lors de la phase de refroidissement. — séparation : tout-parties
**Matrice** (cellule None) recommande [] · observés [40, 35] → **contradiction indéterminée**
Portée : matiere

## 35. Inserts de moule à canaux de refroidissement conformes en spirale
*Development of a Smart Plastic Injection Mold with Conformal Cooling Channels* (2017) — https://doi.org/10.1016/j.promfg.2017.07.020

**Résumé inventif** : Un outillage d'injection intègre des empreintes rapportées imprimées par fabrication additive (SLM) avec des canaux de refroidissement hélicoïdaux au plus près de la matière plastique. Cette modification géométrique ciblée réduit le temps de refroidissement tout en évitant le piégeage thermique au niveau des surépaisseurs de la pièce.

- **AVANT** : L'outillage utilise des canaux de refroidissement droits usinés par perçage mécanique conventionnel, éloignés de la surface de la cavité.
- **PROBLÈME** : Le refroidissement des zones à forte épaisseur est lent et hétérogène, ce qui rallonge le temps de cycle global et risque d'entraîner des défauts d'aspect ou de forme.
- **TRANSFORMATION** : Remplacement des canaux droits par des inserts imprimés en 3D intégraux intégrant des canaux de refroidissement de forme complexe (en spirale / conformes) adaptés localement à la géométrie de la pièce.
- **APRÈS** : Un moule dote d'inserts à canaux conformes épousant la forme exacte et les surépaisseurs de la pièce, réduisant le temps de refroidissement de 30 %.

**Dominant** : P3 Qualité locale — 0.85 — L'action de refroidissement est adaptée localement en créant des inserts spécifiques à canaux en spirale uniquement autour des zones présentant des surépaisseurs.
**Secondaire** : P17 Nouvelle dimension — 0.8 — Utilisation de la fabrication additive 3D pour passer de circuits de refroidissement 2D (lignes droites percées) à des trajectoires tridimensionnelles complexes conformes.

- **↑25 Perte de temps / ↓32 Fabricabilité** (0.75) — Si l'on cherche à accélérer la cadence de production (réduire le temps de cycle) en réduisant le temps de refroidissement (25), alors la régularité dimensionnelle et la fabricabilité de l'outillage (32/12) se détériorent avec des moyens de perçage conventionnels.  
  *preuve* : conformal cooling channels reduce the cycle time approximately 30% compared to conventional cooling channels [en contournant la limitation du perçage droit].

**Contradiction physique** : non
**Matrice** (cellule [25, 32]) recommande [35, 28, 34, 4] · observés [3, 17] → **hors recommandations de la matrice**
Portée : cao

## 36. Optimisation bayésienne de cavité par modèle surrogate
*Using Bayesian optimization for warpage compensation in injection molding* (2024) — https://doi.org/10.1002/mawe.202300157

**Résumé inventif** : Cette étude remplace les simulations éléments finis répétitives et coûteuses en temps par un modèle surrogate basé sur la régression par processus gaussien. Associé à l'optimisation bayésienne, ce modèle permet de compenser le gauchissement des pièces injectées en optimisant la forme de la cavité à moindre coût numérique.

- **AVANT** : L'optimisation de la forme de la cavité pour compenser le retrait et le gauchissement repose sur de multiples simulations éléments finis directes, très coûteuses en temps de calcul.
- **PROBLÈME** : Le temps et les ressources de calcul requis pour enchaîner de nombreuses simulations numériques lourdes rendent l'optimisation géométrique longue et inefficace.
- **TRANSFORMATION** : Remplacement de l'évaluation directe par simulation physique lourde à chaque itération par un modèle prédictif équivalent (régression par processus gaussien) piloté par optimisation bayésienne.
- **APRÈS** : Un processus d'optimisation de la géométrie de la cavité extrêmement rapide qui évalue les déformations à partir d'un métamodèle probabiliste entraîné sur un nombre réduit d'échantillons.

**Dominant** : P26 Copie — 0.92 — Utilisation d'un modèle simplifié (surrogate par processus gaussien) à la place de simulations physiques lourdes et coûteuses pour prédire la déformation.
**Secondaire** : P23 Rétroaction — 0.75 — Mise en place d'une boucle d'optimisation bayésienne réinjectant les prédictions et incertitudes du modèle pour guider l'échantillonnage suivant.

- **↑12 Forme / ↓25 Perte de temps** (0.88) — Si nous améliorons la précision de la forme de la cavité par des simulations numériques itératives, alors les pertes de temps de calcul augmentent fortement.  
  *preuve* : Shape optimization usually requires a sequence of forward simulations, which can be computationally expensive. To reduce this computational cost, we use Bayesian optimization...

**Contradiction physique** : oui — Le modèle numérique doit être complexe et complet pour être précis, et doit être simple et léger pour calculer rapidement les itérations d'optimisation. — séparation : conditions
**Matrice** (cellule [12, 25]) recommande [14, 10, 34, 17] · observés [26, 23] → **hors recommandations de la matrice**
Portée : cao

## 37. Canaux de refroidissement conformes optimisés en 3D
*Design and Optimization of Conformal Cooling Channels for Increasing Cooling Efficiency in Injection Molding* (2023) — https://doi.org/10.3390/app13137437

**Résumé inventif** : La conception de canaux de refroidissement conformes réalisés par fabrication additive permet de suivre la géométrie complexe 3D de la pièce. Cela optimise l'évacuation de la chaleur, réduisant considérablement le temps de cycle et le gauchissement.

- **AVANT** : Les canaux de refroidissement traditionnels sont réalisés par perçage rectiligne dans le moule, ce qui empêche de suivre les contours complexes des pièces.
- **PROBLÈME** : Le refroidissement est non uniforme, ce qui rallonge le temps de cycle (étape la plus longue) et provoque du gauchissement ou des contraintes thermiques.
- **TRANSFORMATION** : Remplacement des lignes de perçage droites par des canaux de refroidissement conformes (CCC) épousant la tridimensionnalité et les courbures de la cavité du moule.
- **APRÈS** : Un réseau de canaux de refroidissement 3D complexes qui maintient une distance constante avec l'empreinte, assurant un refroidissement rapide et homogène.

**Dominant** : P17 Nouvelle dimension — 0.9 — Le réseau de refroidissement passe d'un agencement rectiligne en 2D/axes d'usinage à une topologie 3D tridimensionnelle qui contourne la géométrie de la pièce.
**Secondaire** : P14 Courbure — 0.8 — Substitution des canaux de perçage droits par des canaux curviformes adaptés au profil de la cavité.

- **↑25 Perte de temps / ↓36 Complexité du dispositif** (0.85) — Si nous améliorons le temps de cycle (réduction des pertes de temps) par l'intégration de canaux conformes complexes, alors la complexité de l'outillage augmente.  
  *preuve* : Conformal cooling channels substantially reduce cooling time [...] while their design process is more intricate than that of conventional channels due to complex geometry.

**Contradiction physique** : non
**Matrice** (cellule [25, 36]) recommande [6, 29] · observés [17, 14] → **hors recommandations de la matrice**
Portée : procede

## 38. Moule conformant cœur-coquille à canaux autoportants
*Design and additive manufacturing of novel conformal cooling molds* (2020) — https://doi.org/10.1016/j.matdes.2020.109147

**Résumé inventif** : Cette étude conçoit un moule de refroidissement conformant combinant des canaux autoportants de grand diamètre et une structure cœur-coquille à cœur poreux. L'architecture permet d'augmenter l'efficacité thermique tout en réduisant le temps d'impression LPBF et la quantité de matière consommée.

- **AVANT** : Les moules de refroidissement conformant utilisent des canaux cylindriques standards de petit diamètre (≤8 mm) et un bloc de moule entièrement massif.
- **PROBLÈME** : L'augmentation du diamètre des canaux pour améliorer le refroidissement entraîne leur effondrement lors de l'impression LPBF, tandis que les blocs massifs augmentent le temps d'impression et le coût en poudre métallique.
- **TRANSFORMATION** : Intégration de structures de soutien internes autoportantes dans des canaux de grand diamètre (≥13 mm) et remplacement du corps massif du moule par une structure cœur-coquille (cœur en réseau poreux diamant et enveloppe externe dense).
- **APRÈS** : Un moule imprimé en LPBF comportant des canaux de refroidissement autoportants de 13 à 20 mm réduisant le temps de refroidissement de plus de 20 %, associé à une structure allégée conservant sa résistance mécanique.

**Dominant** : P40 Matériaux composites — 0.9 — Création d'une structure cœur-coquille associant un cœur poreux en treillis diamant à une coquille extérieure dense pour combiner légèreté et résistance mécanique.
**Secondaire** : P3 Qualité locale — 0.85 — Différenciation de la densité du moule entre l'enveloppe externe soumise aux contraintes et le cœur interne fortement allégé.
**Secondaire** : P31 Matériaux poreux — 0.8 — Introduction délibérée d'une structure poreuse en diamant dans le volume interne du moule pour économiser la matière et le temps de fabrication.

- **↑25 Perte de temps / ↓32 Fabricabilité** (0.9) — Si nous augmentons le diamètre des canaux de refroidissement pour accélérer le refroidissement des pièces (25 Perte de temps), alors la fabricabilité par LPBF (32 Fabricabilité) se détériore à cause de l'affaissement des plafonds de canaux.  
  *preuve* : The optimized internal supports suppressed the collapse and warpage of large channels, which improves the manufacturability... self-supporting 13 mm channel reduces the cooling time of more than 20%.
- **↑26 Quantité de substance / ↓14 Résistance** (0.85) — Si nous évidons le corps du moule avec des structures poreuses pour réduire la matière utilisée (26 Quantité de substance), alors la résistance mécanique du moule (14 Résistance) se détériore.  
  *preuve* : the porous diamond structure was designated in the assembly part of the mold to save the materials... To tune the strength, a core-shell composite structure with solid shell surrounding inner porous structures is designed.

**Contradiction physique** : oui — Le corps du moule doit être poreux pour réduire la matière et le temps de fabrication, et doit être dense pour garantir la résistance aux efforts de moulage. — séparation : espace
**Matrice** (cellule [25, 32]) recommande [35, 28, 34, 4] · observés [40, 3, 31] → **hors recommandations de la matrice**
Portée : cao

## 39. Réplique transparente de fracture pour visualisation d'écoulement
*Two‐Phase Flow Visualization and Relative Permeability Measurement in Natural Rough‐Walled Rock Fractures* (1995) — https://doi.org/10.1029/95wr00171

**Résumé inventif** : Pour observer les écoulements diphasiques à l'intérieur de fractures de roches opaques, le système utilise des répliques transparentes reproduisant fidèlement la géométrie rugueuse interne. Cela permet la visualisation optique directe des motifs d'occupation des pores tout en mesurant simultanément les variations de pression et de perméabilité.

- **AVANT** : L'étude des écoulements dans des fractures de roches naturelles s'effectue sur des échantillons de roche réels opaques.
- **PROBLÈME** : L'opacité de la roche empêche de visualiser la distribution des fluides et l'occupation des pores, rendant impossible la compréhension directe des instabilités d'écoulement diphasique.
- **TRANSFORMATION** : Remplacement de la paroi de fracture rocheuse opaque par des répliques en matériau transparent reproduisant la rugosité de la fracture naturelle.
- **APRÈS** : Un dispositif expérimental permettant d'observer directement par voie optique la dynamique des fluides et l'occupation des pores au sein d'une géométrie de fracture réelle.

**Dominant** : P26 Copie — 0.9 — Utilisation d'une réplique transparente simplifiée à la place de la fracture de roche naturelle opaque pour observer des phénomènes internes inaccessibles.
**Secondaire** : P32 Changement de couleur — 0.75 — Remplacement des parois opaques du canal d'écoulement par des parois transparentes afin de rendre le phénomène interne contrôlable visuellement.

- **↑28 Précision de la mesure / ↓36 Complexité du dispositif** (0.85) — Si l'on cherche à visualiser la distribution interne des fluides pour améliorer la précision de mesure (28), alors la complexité du dispositif d'essai (36) augmente en raison de la nécessité de concevoir et fabriquer des répliques transparentes à rugosité contrôlée.  
  *preuve* : Experiments at carefully controlled flow rate and pressure conditions have been performed using a natural fracture and three transparent fracture replicas. Visual observations of changes in pore occupancy showed that the instabilities could be explained...

**Contradiction physique** : oui — La paroi de la fracture doit être opaque (pour conserver la composition de la roche naturelle) et doit être transparente (pour permettre la visualisation optique de l'écoulement). — séparation : conditions
**Matrice** (cellule [28, 36]) recommande [27, 35, 10, 34] · observés [26, 32] → **hors recommandations de la matrice**
Portée : procede

## 40. Régulation variotherme dynamique pour micro-injection polymère
*Microinjection molding of thermoplastic polymers: a review* (2007) — https://doi.org/10.1088/0960-1317/17/6/r02

**Résumé inventif** : L'injection de micro-pièces thermoplastiques nécessite d'éviter la solidification prématurée du polymère dans des cavités à très fort rapport surface/volume. L'utilisation d'un système variotherme permet de chauffer rapidement le moule pendant le remplissage puis de le refroidir efficacement avant l'éjection.

- **AVANT** : En injection conventionnelle, la température de la cavité du moule est maintenue constante et sensiblement inférieure à la température de transition vitreuse du polymère.
- **PROBLÈME** : À l'échelle micrométrique, le rapport surface/volume élevé entraîne un refroidissement ultra-rapide du fluide, provoquant un figeage prématuré et un remplissage incomplet des micro-détails.
- **TRANSFORMATION** : Rendre la température des parois du moule variable et régulée dynamiquement au cours du cycle (chauffage rapide au-dessus de Tg pendant l'injection, puis refroidissement rapide sous Tg pour la solidification).
- **APRÈS** : Un procédé de micro-injection utilisant un moule à régulation thermique dynamique (variotherme) garantissant un remplissage intégral des empreintes microstructurées sans dégrader excessivement le temps de cycle.

**Dominant** : P15 Dynamisme — 0.9 — La température du moule, historiquement statique et constante, est rendue dynamique et adaptable à chaque phase du cycle d'injection.
**Secondaire** : P35 Modification des paramètres physiques/chimiques — 0.75 — La température de paroi est modifiée de manière extrême et cyclique pour changer la viscosité locale du polymère lors du remplissage.

- **↑32 Fabricabilité / ↓25 Perte de temps** (0.85) — Si l'on augmente la température du moule pour améliorer la faisabilité du remplissage des micro-cavités, alors le temps de cycle se détériore.  
  *preuve* : Un moule chaud empêche le figeage prématuré du polymère fluide dans les micro-canaux, mais rallonge la durée nécessaire au refroidissement avant l'éjection de la pièce.

**Contradiction physique** : oui — Le moule doit être chaud lors de l'injection pour fluidifier le polymère et froid lors du maintien/refroidissement pour solidifier la pièce. — séparation : temps
**Matrice** (cellule [32, 25]) recommande [35, 28, 34, 4] · observés [15, 35] → **concordance partielle**
Portée : procede

## 41. Canaux de refroidissement conformes optimisés
*A Thermomechanical Analysis of Conformal Cooling Channels in 3D Printed Plastic Injection Molds* (2018) — https://doi.org/10.3390/app8122567

**Résumé inventif** : Remplace les canaux de refroidissement droits usinés par des canaux conformes épousant la géométrie complexe de la empreinte grâce à la fabrication additive. Cette approche optimise l'efficacité thermique et réduit les déformations thermiques et le temps de cycle.

- **AVANT** : Canaux de refroidissement droits obtenus par perçage mécanique conventionnel dans les moules d'injection.
- **PROBLÈME** : Incapacité des canaux droits à suivre les contours complexes de la pièce, entraînant un refroidissement non uniforme, un temps de cycle allongé et des déformations thermiques.
- **TRANSFORMATION** : Modification de la trajectoire et du profil des canaux de refroidissement pour qu'ils suivent la forme 3D exacte de la surface moulée (canal conforme) grâce à l'impression 3D métallique.
- **APRÈS** : Outillage d'injection intégrant des canaux de refroidissement conformes à section et trajectoire optimisées thermomécaniquement.

**Dominant** : P14 Courbure — 0.95 — Passage d'une géométrie de canaux de refroidissement rectiligne (percée) à une géométrie courbe et conforme qui épouse le relief du moule.
**Secondaire** : P17 Nouvelle dimension — 0.85 — Passage d'une disposition axiale 2D des canaux perçés à un réseau tridimensionnel contournant la pièce dans tout l'espace de la cavité.

- **↑39 Productivité / ↓32 Fabricabilité** (0.9) — Si nous réduisons le temps de refroidissement pour améliorer la productivité, alors la complexité de fabrication du moule augmente.  
  *preuve* : The traditional die design is limited to straight (drilled) cooling channels [...] With the advent of additive manufacturing technology, injection molding tools with conformal cooling channels are now possible.

**Contradiction physique** : oui — La trajectoire des canaux de refroidissement doit être droite pour permettre leur usinage par perçage mécanique traditionnel, et doit être non-droite (courbe) pour maintenir une distance constante avec la surface complexe de la pièce. — séparation : espace
**Matrice** (cellule [39, 32]) recommande [35, 28, 2, 24] · observés [14, 17] → **hors recommandations de la matrice**
Portée : cao

## 42. Optimisation dépouille-stratification pour moules SL
*Layer thickness and draft angle selection for stereolithography injection mould tooling* (2002) — https://doi.org/10.1080/00207540110091875

**Résumé inventif** : L'adaptation conjointe de l'angle de dépouille et de l'épaisseur des couches d'impression SLA permet de réduire les forces de frottement lors de l'éjection. Cela prévient la rupture par traction des noyaux de moule en résine lors du démoulage des pièces plastique.

- **AVANT** : Les moules d'injection prototype sont fabriqués par stéréolithographie (SL) avec des paramètres standards de stratification et de dépouille.
- **PROBLÈME** : Les noyaux du moule SL cassent fréquemment sous l'effet de la force d'éjection lorsque le frottement dépasse la résistance à la traction de la résine.
- **TRANSFORMATION** : Ajustement combiné de l'angle de dépouille et de la résolution verticale (épaisseur de couche d'impression) sur les faces de démoulage pour réduire l'effet d'escalier et l'effort d'extraction.
- **APRÈS** : Un moule SL optimisé géométriquement et surfaciquement, capable de résister aux cycles d'injection sans rupture du noyau lors de l'éjection.

**Dominant** : P3 Qualité locale — 0.72 — Adaptation des caractéristiques géométriques (dépouille) et de résolution d'impression (épaisseur de couche) spécifiquement sur les zones d'interface subissant le frottement d'éjection.
**Secondaire** : P15 Dynamisme — 0.65 — Modulation variable de l'épaisseur de couche et de l'inclinaison des parois selon les contraintes locales d'extraction.

- **↑32 Fabricabilité / ↓29 Précision de la fabrication** (0.75) — Si l'on augmente l'angle de dépouille et réduit l'épaisseur des couches pour diminuer l'effort d'éjection, alors la conformité géométrique de la pièce ou le temps de fabrication du moule se détériore.  
  *preuve* : SL tools may break under the force exerted by part ejection when the friction between a moulding and a core is greater than the tensile strength of the core

**Contradiction physique** : oui — L'épaisseur de couche doit être grande pour fabriquer le moule rapidement, et faible pour réduire l'effet d'escalier et les frottements à l'éjection. — séparation : conditions
**Matrice** (cellule [32, 29]) recommande [] · observés [3, 15] → **hors recommandations de la matrice**
Portée : procede

## 43. Inclusion d'agent de démoulage interne dans le PLA
*The Effect of Processing Parameters and Calcium-stearate on the Ejection Process of Injection Molded Poly(Lactic Acid) Products* (2021) — https://doi.org/10.3311/ppme.18246

**Résumé inventif** : L'incorporation de 1% en masse de stéarate de calcium comme agent de démoulage interne dans le PLA permet de réduire les forces d'éjection. Cette modification de la composition du matériau résout le problème de blocage et de casse des pièces lors du démoulage dans des moules à faible dépouille.

- **AVANT** : Le moulage par injection du PLA dans des empreintes complexes à faible dépouille entraîne une forte adhésion aux parois du moule.
- **PROBLÈME** : Les pièces en PLA restent coincées ou se cassent lors de l'éjection, ce qui perturbe la production continue et endommage les pièces.
- **TRANSFORMATION** : Ajout de 1% en masse de stéarate de calcium agissant comme lubrifiant/agent de démoulage interne au sein du matériau PLA.
- **APRÈS** : Les forces d'éjection requises sont fortement réduites, permettant un démoulage fluide et sans dommage des pièces moulées.

**Dominant** : P35 Modification des paramètres physiques/chimiques — 0.85 — L'ajout d'un additif (stéarate de calcium) modifie les propriétés tribologiques et physico-chimiques internes du polymère pour faciliter le glissement.
**Secondaire** : P24 Intermédiaire — 0.65 — Utilisation d'un agent de démoulage incorporé agissant comme fluide/intermédiaire d'interface entre le polymère et la surface du moule.

- Aucune contradiction technique Altshuller suffisamment démontrée.

**Contradiction physique** : non
**Matrice** (cellule None) recommande [] · observés [35, 24] → **contradiction indéterminée**
Portée : matiere

## 44. Optimisation des paramètres de démoulage par polymère
*Analysis of the effect of draft angle and surface roughness on ejection forces in micro injection molding* (2024) — https://doi.org/10.21741/9781644903131-294

**Résumé inventif** : L'étude adapte spécifiquement les paramètres de température du moule et de rugosité de surface en fonction de la nature du polymère (PP ou COC) pour réduire la force d'éjection. Cette optimisation ciblée des paramètres physico-chimiques et de l'état de surface prévient la détérioration des micro-pièces lors du démoulage.

- **AVANT** : Les paramètres de démoulage (température du moule, rugosité, dépouille) sont appliqués de manière générique sans adaptation spécifique aux interactions physiques propres à chaque polymère.
- **PROBLÈME** : Des forces d'éjection élevées en micro-injection risquent d'endommager ou de déformer les composants micrométriques fragiles lors du démoulage.
- **TRANSFORMATION** : Ajustement et optimisation combinée de la rugosité de surface (Sa), de l'angle de dépouille et de la température du moule en fonction des propriétés thermamécaniques spécifiques du polymère injecté.
- **APRÈS** : Un procédé de micro-injection où la force d'éjection maximale est minimisée sur mesure selon le matériau, garantissant le démoulage sans dommage des micro-pièces.

**Dominant** : P35 Modification des paramètres physiques/chimiques — 0.85 — La variation et l'ajustement précis de la température du moule et de l'état de surface (rugosité Sa) permettent de modifier le comportement d'adhésion et de friction selon le polymère utilisé.
**Secondaire** : P3 Qualité locale — 0.65 — La rugosité de surface du moule est adaptée localement aux spécificités mécaniques et d'adhérence propres à chaque type de polymère.

- **↑32 Fabricabilité / ↓10 Force** (0.8) — Si nous augmentons la température du moule pour améliorer la mise en forme du matériau COC, alors la force nécessaire à l'éjection augmente fortement, risquant d'endommager la pièce.  
  *preuve* : Specifically, an increase in mold temperature led to an 88% increase in ejection force for COC, while resulting in a 63% decrease for PP.

**Contradiction physique** : oui — La température du moule doit être élevée pour faciliter le remplissage/fluidité du polymère, et basse pour réduire la force d'éjection dans le cas du COC. — séparation : conditions
**Matrice** (cellule [32, 10]) recommande [35, 12] · observés [35, 3] → **concordance forte**
Portée : procede

## 45. Moule d'injection instrumenté pour mesure dynamique d'éjection
*Shrinkage and ejection forces in injection moulded products* (2002) — http://hdl.handle.net/1822/173

**Résumé inventif** : L'article présente la conception d'un moule d'injection instrumenté spécifique pour mesurer en temps réel l'évolution des forces d'éjection, de la pression et de la température. Cette instrumentation intégrée permet de caractériser précisément le comportement des pièces sur noyaux profonds et d'optimiser le démoulage.

- **AVANT** : La prédiction des dimensions et des forces d'éjection pour des pièces à noyaux profonds repose sur des calculs théoriques ou des approximations sans mesure directe pendant le cycle.
- **PROBLÈME** : L'absence de données réelles en temps réel sur les contraintes thermomécaniques et l'effort d'éjection entraîne des risques d'endommagement des pièces ou des erreurs de tolérance.
- **TRANSFORMATION** : Intégration directe de capteurs de force, de pression et de température au sein même de la structure du moule d'injection.
- **APRÈS** : Un outillage instrumenté capable de fournir un suivi dynamique et corrélé des grandeurs physiques du procédé et de l'effort d'éjection sous conditions réelles de transformation.

**Dominant** : P23 Rétroaction — 0.85 — Mise en place de capteurs au cœur de l'outillage pour surveiller en continu et en temps réel l'état du procédé et l'effort d'éjection.
**Secondaire** : P28 Substitution du principe mécanique — 0.75 — Remplacement des estimations mécaniques théoriques par des mesures physiques directes (capteurs de pression, force et température) intégrées.

- **↑28 Précision de la mesure / ↓36 Complexité du dispositif** (0.8) — Si nous améliorons la précision de mesure (28) par l'intégration de capteurs au cœur du moule, alors la complexité du dispositif (36) augmente.  
  *preuve* : The mould has the means to measure the pressure and temperature histories, and the force evolution during the ejection process.

**Contradiction physique** : non
**Matrice** (cellule [28, 36]) recommande [27, 35, 10, 34] · observés [23, 28] → **hors recommandations de la matrice**
Portée : procede

## 46. Reconnaissance et génération automatique de dépouilles CAO
*Automatic Recognition and Construction of Draft Angle for Injection Mold Design* (2017) — https://doi.org/10.4236/jsea.2017.101005

**Résumé inventif** : Développement d'un algorithme dans un logiciel CAO pour reconnaître automatiquement les surfaces nécessitant un dépouillage et générer la dépouille selon la typologie de la face. Cette automatisation réduit de 80 % le nombre de clics requis pour la conception des moules d'injection.

- **AVANT** : L'identification des faces parallèles à la direction de démoulage et l'application des angles de dépouille s'effectuent manuellement par le concepteur CAO, face par face.
- **PROBLÈME** : La création manuelle des dépouilles est longue, répétitive, source d'erreurs d'oubli et accroît considérablement le temps de mise au point du modèle CAO.
- **TRANSFORMATION** : Mise en place d'un algorithme d'induction pour identifier et classifier automatiquement les ensembles de surfaces (quilts) à dépouiller, couplé à une génération automatique des fonctions de dépouille selon la topologie des surfaces.
- **APRÈS** : Un outil CAO automatisé qui inspecte automatiquement 90 % des surfaces concernées et génère les caractéristiques de dépouille en économisant 80 % des clics utilisateur.

**Dominant** : P10 Action préliminaire — 0.85 — Pré-analyser et classifier automatiquement la géométrie de la pièce en amont pour appliquer instantanément les fonctions de dépouille adéquates sans intervention manuelle répétitive.
**Secondaire** : P1 Segmentation — 0.75 — Découpage et classification des surfaces du modèle CAO en catégories distinctes (quilts) pour appliquer des règles de dépouille spécifiques à chaque type.

- Aucune contradiction technique Altshuller suffisamment démontrée.

**Contradiction physique** : non
**Matrice** (cellule None) recommande [] · observés [10, 1] → **contradiction indéterminée**
Portée : cao

## 47. Refroidissement conformel pour moule d'injection plastique
*Design of conformal cooling for plastic injection moulding by heat transfer simulation* (2015) — https://doi.org/10.1590/0104-1428.2047

**Résumé inventif** : Remplacement des canaux de refroidissement droits forés mécaniquement par des circuits de refroidissement conformels qui épousent la géométrie complexe de la pièce injectée. Cette transformation géométrique permet d'homogénéiser le transfert thermique et d'extirper les contraintes résiduelles de déformation.

- **AVANT** : Les moules d'injection utilisent des canaux de refroidissement rectilignes simples, obtenus par perçage mécanique droit dans le bloc d'acier.
- **PROBLÈME** : Les canaux droits sont éloignés des empreintes complexes, provoquant un refroidissement inégal, un temps de cycle allongé et des déformations (gauchissement) importantes de la pièce en polypropylène.
- **TRANSFORMATION** : Redesign de la géométrie des canaux de refroidissement pour qu'ils suivent exactement les contours 3D de la pièce (refroidissement conformel), rendus réalisables via la fabrication additive (SLM).
- **APRÈS** : Un moule intégrant des circuits conformels (en série ou en parallèle) épousant la forme de la pièce, garantissant une extraction thermique homogène et réduisant fortement le gauchissement.

**Dominant** : P14 Courbure — 0.9 — Passage de lignes de refroidissement droites et linéaires perçées à des lignes de refroidissement courbes et conformes à la géométrie complexe de la pièce.
**Secondaire** : P3 Qualité locale — 0.8 — Adaptation de la proximité du canal de refroidissement en chaque point de la cavité pour adapter l'évacuation thermique selon l'épaisseur locale de la pièce.
**Secondaire** : P17 Nouvelle dimension — 0.75 — Passage d'un réseau de canaux contraint dans un plan/axes linéaires à une disposition tridimensionnelle enveloppant la pièce.

- **↑13 Stabilité de l'objet / ↓32 Fabricabilité** (0.85) — Si nous améliorons la stabilité dimensionnelle de la pièce par un réseau de refroidissement conformel adapté aux contours, alors la complexité de fabrication du moule augmente.  
  *preuve* : The deformation of the product can be reduced significantly [...] However, conventional methods to manufacture cooling channels (drilling) can only produce linear holes. Selective laser melting (SLM) is an additive manufacturing technique capable to manufacture complex cooling channels... because of the high costs of SLM...

**Contradiction physique** : non
**Matrice** (cellule [13, 32]) recommande [35, 19] · observés [14, 3, 17] → **hors recommandations de la matrice**
Portée : cao

## 48. Moule d'injection instrumenté à capteurs piezoélectriques
*Development of Mold for Demolding Resistance Measurement in Polymer Injection Molding* (2019) — https://doi.org/10.18494/sam.2019.2357

**Résumé inventif** : Intégration de capteurs de force à quartz haute sensibilité directement au sein de la structure du moule pour mesurer précisément les efforts de démoulage des lentilles. Cette instrumentation intégrée permet d'isoler et d'analyser l'influence des paramètres de procédé sur les forces d'éjection.

- **AVANT** : La résistance au démoulage des lentilles optiques est évaluée de façon indirecte ou approximative, sans mesure localisée et précise des efforts réels lors de l'éjection.
- **PROBLÈME** : L'impossibilité de mesurer précisément les forces de démoulage empêche d'optimiser le procédé pour éviter les rayures, fissures et déformations sur les lentilles en polymère.
- **TRANSFORMATION** : Intégration de capteurs de force piezoélectriques à quartz directement dans l'architecture interne du moule d'injection au niveau des zones d'éjection.
- **APRÈS** : Un moule d'injection instrumenté capable de mesurer directement et en temps réel la résistance dynamique au démoulage sous l'effet des paramètres de moulage.

**Dominant** : P28 Substitution du principe mécanique — 0.85 — Utilisation d'effets piezoélectriques (capteurs à quartz) intégrés dans l'outillage pour mesurer les forces d'éjection mécaniques au lieu de méthodes d'estimation mécaniques globales.
**Secondaire** : P23 Rétroaction — 0.75 — Introduction de capteurs de force pour mesurer le comportement dynamique lors du démoulage et fournir une information exploitable pour le réglage du procédé.

- **↑28 Précision de la mesure / ↓36 Complexité du dispositif** (0.8) — Si nous améliorons la précision de la mesure des forces d'éjection par l'intégration de capteurs à quartz dans le moule, alors la complexité du dispositif augmente.  
  *preuve* : In this study, we designed and fabricated a mold equipped with high-sensitivity quartz force sensors for demolding resistance measurement...

**Contradiction physique** : non
**Matrice** (cellule [28, 36]) recommande [27, 35, 10, 34] · observés [28, 23] → **hors recommandations de la matrice**
Portée : cao
