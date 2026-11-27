# ADR 0001 — Rust, Bevy pour le client, simulation sans moteur

- **Statut** : accepté (0.1.0-alpha)

## Contexte

Le jeu doit avoir un serveur dédié Linux sans écran, à 128 Hz, et une prédiction
client qui donne exactement les mêmes résultats que le serveur. Le délai est
court et il n'y a pas d'artiste.

## Décision

- **Langage** : Rust 1.100 pour tout le projet ; `unsafe_code = "deny"`.
- **Simulation** : la logique de jeu (`engine-*`, `ps-sim`) est en Rust pur,
  sans ECS ni moteur. Elle est écrite comme une fonction `step(entrées) → état`.
  Elle est déterministe et testable sans fenêtre, et partagée par le serveur et
  la prédiction.
- **Client** : Bevy 0.20 pour la fenêtre, le rendu PBR, l'audio et les entrées ;
  egui pour l'interface. Le client ne contient aucune règle de jeu.
- **Contenu** : géométrie et sons générés par code (`tools/ps-mapgen` de Project-s-content, synthèse audio
  dans `ps-client/src/audio.rs`). Aucun asset externe ni sous licence restrictive.

## Conséquences

- Le serveur compile sans Bevy : image de 119 Mo, compilation rapide.
- Simulation et replays sont testés en CI sans GPU ; 110 tests.
- Le rendu reste simple : formes géométriques, pas de modèles animés.
