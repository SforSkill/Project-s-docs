# ADR 0005 — Personnages « peinture liquide » procéduraux et purement visuels

- **Statut** : accepté

## Contexte

Les joueurs étaient des cubes. La direction artistique demande des humanoïdes
low-poly à facettes, en « peinture liquide » : contour discret, effets de gouttes,
fonte à la mort et reconstitution à la réapparition. Les contraintes :
- garder l'intégrité compétitive : mêmes hitboxes, aucun avantage de couleur ou
  de qualité, aucune vision à travers les murs ;
- ne changer ni le moteur, ni le réseau, ni le gameplay ;
- tenir une performance correcte sur un PC modeste.

Blender n'est pas installé sur la machine de développement, et aucune
illustration de référence n'a été fournie.

## Décision

- **Modèle, squelette et animations générés en Rust** (`character/`). La source
  versionnée est le code : proportions, poids de skinning, LOD. Les animations
  sont procédurales (cycles paramétrés et IK à deux os), pas des clips importés.
- **Visuel découplé du gameplay** : `game.rs` remplit un `CharacterFeed` depuis
  l'état réseau existant. Rien dans `character/` n'est lu par la simulation ou
  par `ps-hitreg`.
- **Matériau unique** `LiquidMaterial` (extension de `StandardMaterial`, shader
  WESL). Tous ses paramètres sont centralisés dans `LiquidStyle`. Les matériaux
  sont partagés, et prêtés à un personnage seulement pendant un effet.
- **Équité par construction** : les qualités ne changent que des détails
  secondaires. Le contour, le flash d'impact et la silhouette restent constants.
  Les palettes ont un contraste minimal vérifié par un test, et deux camps n'ont
  jamais la même. La réapparition n'utilise pas de transparence partielle.
- **Effets locaux et en pool** : sans collision, sans ombre, plafonnés par la
  qualité, limités à 40 m de la caméra.
- **Première personne** : avant-bras et mains seulement, avec le même matériau.
  Les armes restent solides et distinctes.

## Conséquences

- Pas de pipeline d'assets externe : le modèle se modifie dans le code, et les
  tests vérifient le budget de triangles, le skinning et l'absence de torse en
  première personne.
- Des skins restent possibles : de nouvelles palettes dans `style.rs`, ou un
  autre `MeshData` pour le même squelette.
- La qualité artistique est limitée par le procédural : pas de visage sculpté,
  et des animations moins riches que du mocap. Un export glTF du squelette, du
  maillage et des clips échantillonnés permettrait plus tard une reprise dans
  Blender ; il n'est pas encore écrit.
- Le shader n'implémente pas le fondu tramé des LOD : les bascules sont nettes.
