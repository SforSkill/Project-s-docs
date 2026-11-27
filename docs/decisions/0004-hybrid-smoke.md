# ADR 0004 — Fumigène hybride : volume voxel opaque et réactif

- **Statut** : accepté

## Contexte

Il y a deux familles de fumigènes :
- les fumées à particules « réactives » : volume dynamique, percé par les
  explosions ;
- les sphères opaques nettes, très lisibles.

Le premier modèle est plus vivant, mais coûteux et difficile à garder équitable :
le client et le serveur doivent avoir le même volume, sans fumée « à sens
unique ».

## Décision

`ps-sim/src/smoke.rs` :
- un volume de voxels, rempli **par diffusion** depuis le point d'explosion
  jusqu'à un volume cible. La fumée épouse les couloirs et ne passe jamais à
  travers les murs ;
- un volume **opaque et borné**, à la lecture nette ;
- une **réaction aux grenades explosives** : un trou s'ouvre, puis se reforme.
  Les balles ne modifient pas le volume ;
- un calcul **autoritaire** : le serveur calcule les voxels et les envoie sur le
  canal fiable. Les trous sont recalculés de chaque côté à partir des
  événements explosifs répliqués, avec la même formule ;
- une **ligne de vue symétrique** : le même test de voxels depuis les deux
  extrémités. Le PIM en tient compte : un ennemi caché par la fumée n'est pas
  envoyé.

## Conséquences

- Le test `smoke_never_crosses_walls_blocks_sight_and_reforms_after_he` vérifie trois points : la fumée ne passe
  pas à travers un mur, elle bloque la vue dans les deux sens, une explosion la
  perce puis elle se reforme.
- Le rendu client (cubes translucides instanciés) est simple. Il n'y a ni
  éclairage volumétrique ni particules.
