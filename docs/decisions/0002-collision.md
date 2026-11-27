# ADR 0002 — Collisions maison plutôt qu'un moteur physique

- **Statut** : accepté

## Contexte

Le déplacement de type Source repose sur des tracés de boîte alignée sur les
axes, balayés contre des briques convexes (`TraceHull`). Ces tracés renvoient
une fraction exacte, une normale de plan et une marge de surface de 1/32 u.
Avian3D ou Rapier sont des moteurs de corps rigides généralistes, intégrés à
l'ECS.

## Décision

`ps-physics` implémente ses propres collisions, en environ 400 lignes :
- briques convexes : boîtes, rampes, *clips* ;
- `trace_hull` balayé ;
- lancer de rayon avec épaisseur traversée et matériau, pour la pénétration ;
- grille de cellules pour accélérer les requêtes.

Pas de moteur physique dans la simulation autoritaire.

## Conséquences

- Les résultats sont identiques au bit près entre le client et le serveur, car
  c'est le même code. Le serveur reste sans ECS.
- Coût mesuré (criterion, Intel Core i5-13600KF sous Windows 11, `cargo bench -p ps-physics`) :
  - un pas de joueur, `trace_box_player_step` : 99,6 ns ;
  - un long rayon, `trace_ray_long` : 822 ns.
- Pas de physique d'objets (caisses mobiles, ragdolls). Les grenades utilisent
  leur propre intégrateur de rebonds.
