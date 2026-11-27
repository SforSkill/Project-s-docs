# Audit d'architecture — Projet-S avant migration

- **Référence** : `SforSkill/Projet-S`, branche `main`, commit `b586317`, version `0.1.0-alpha.1`.
- **Tag de sauvegarde** : `backup/pre-repo-split`.
- **Date** : 27/11/2026.

Les chiffres sont mesurés sur ce commit : `wc -l` sur les fichiers `.rs`, et `Cargo.toml` pour les dépendances. Le graphe complet est dans [DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md#avant-migration-projet-s-commit-b586317).

## 1. Inventaire

| Élément | Contenu | Taille |
|---|---|---|
| `crates/engine-core` | types communs : `UserCmd`, `SimTime`, angles, équipes, chargement TOML/RON | 8 fichiers, 1 041 lignes |
| `crates/engine-physics` | briques convexes, `trace_hull`, matériaux | 6 fichiers, 997 lignes |
| `crates/engine-movement` | déplacement Source, contre-strafe | 7 fichiers, 1 534 lignes |
| `crates/engine-weapons` | armes, recul, dispersion, pénétration | 6 fichiers, 1 350 lignes |
| `crates/engine-hitreg` | capsules, historique, compensation de latence | 2 fichiers, 488 lignes |
| `crates/engine-visibility` | PIM anti-wallhack | 1 fichier, 171 lignes |
| `crates/engine-network` | transport UDP chiffré sans E/S | 6 fichiers, 1 603 lignes |
| `crates/engine-replay` | conteneur de replay | 1 fichier, 181 lignes |
| `crates/game-rules` | manches, économie, MR12/15/16 | 1 fichier, 875 lignes |
| `crates/game-sim` | simulation complète, bots, grenades, fumée, **codec réseau, prédiction, enregistrement** | 15 fichiers, 5 819 lignes |
| `crates/game-server` | serveur sans E/S, boucle UDP, admin HTTP, binaire | 6 fichiers, 2 332 lignes |
| `crates/game-netclient` | réseau client sans E/S, tests de bout en bout | 3 fichiers, 1 303 lignes |
| `crates/game-client` | jeu Bevy : rendu, HUD, UI, audio, personnages, démo | 18 fichiers, 9 130 lignes |
| `tools/mapgen` | génération des cartes RON | 649 lignes |
| `tools/netlab` | laboratoire réseau A/B/C/D | 442 lignes |
| `configs/`, `maps/` | valeurs de gameplay, 3 cartes | données |
| `deploy/` | Dockerfile, Compose, unité systemd, chart Helm (squelette), Fleet Agones (manifeste seul) | — |
| `.github/workflows/` | CI (lint, tests Linux et Windows, image Docker), release-please, release, PR checks | — |
| `docs/` | 26 documents, 6 ADR, résultats bruts (autotest, netlab) | — |

**Points d'entrée** :
- `game-client` : binaire `Project-S`, avec les modes `--autotest` et `--character-demo` ;
- `game-server` : binaire `projet-s-server`, avec la feature `admin` ;
- `tools/mapgen`, `tools/netlab`.

**Features Cargo** :
- `game-server/admin` (par défaut) : axum, tokio, Prometheus, ctrlc. Le client désactive les features par défaut.

État au baseline :
- **compilation** : Windows (local) et Linux (CI) ;
- **tests** : 110 réussis, 1 ignoré (diagnostic) ([rapport du baseline](https://github.com/SforSkill/Project-s/blob/backup/pre-repo-split/docs/validation-report.md)).

## 2. Ce qui fonctionnait réellement

Source : `docs/status.md` du baseline, colonnes Implémenté / Testé / Validé.

Validé en exécution réelle :
- serveur headless à 128 Hz (Docker et VPS systemd), multijoueur UDP chiffré entre 2 clients réels ;
- déplacement Source, armes, hitreg compensée ;
- santé, mort, réapparition ;
- 3 cartes, HUD, jeu local, bots, deathmatch, 5v5 avec bots ;
- flux urgent, PIM, inspecteur de tirs, API d'administration.

Implémenté et testé, jamais validé à la main : grenades, fumée, armure, tagging, pénétration, économie, bombe, MR15 complet.

**Factice ou partiel** :
- le chart Helm (squelette sans cluster) ;
- le manifeste Agones (SDK non intégré) ;
- aucun lecteur de replay ;
- le client Linux, compilé en CI mais jamais lancé.

## 3. Problèmes de périmètre

| # | Constat | Gravité | Traitement |
|---|---|---|---|
| A1 | `game-sim` mêlait la simulation, le codec réseau (`proto.rs`, qui dépend de `engine-network::wire`), la prédiction client (`predict.rs`) et l'enregistrement (`record.rs`, qui dépend de `engine-replay`). Toute la simulation dépendait du transport. | élevée | séparé en `ps-sim` (pur) et `ps-sim-net` (codec, prédiction, enregistrement) |
| A2 | Le préfixe `engine-` désignait des crates de **simulation** : physique, mouvement, armes, hitreg. Le vrai moteur de rendu était un module de `game-client`. Le nom induisait en erreur sur le périmètre. | moyenne | `engine-*` → `ps-*` dans Project-s-simulation ; `character/` du client → `ps-engine-character` (Project-s-engine) |
| A3 | `engine-core` mêlait des contrats de fil (`UserCmd`, `SimTime`, ticks, angles, versions) et des utilitaires de simulation (configs, RNG, maths, sensibilité). | moyenne | contrats → `ps-types` (Project-s-protocol) ; utilitaires → `ps-sim-core` |
| A4 | Aucun contrat pour le back-end : tickets, sanctions, heartbeats, résultats, événements. | élevée (pour la suite) | `ps-core-protocol`, versionné et testé ([API_CONTRACTS.md](API_CONTRACTS.md)) |
| A5 | Aucune règle de dépendance vérifiée : rien n'empêchait `game-server` d'importer Bevy, ni `game-sim` d'importer tokio. | élevée | `boundaries.toml` + `check_boundaries.py` en CI |
| A6 | `engine-visibility` (PIM) est une politique de divulgation propre au serveur, mais elle était rangée parmi les briques « moteur ». | faible | `ps-visibility` dans Project-s-server |
| A7 | Les données de jeu (`configs/`, `maps/`) étaient versionnées avec le code du client ; le serveur les lisait dans le dépôt client. | moyenne | Project-s-content, avec un manifeste d'intégrité (sha256 et `data_fingerprint`) et des cibles client/serveur par fichier |
| A8 | `deploy/` (serveur) et la documentation transversale (architecture, ADR, git-workflow) étaient dans le dépôt client. | faible | `deploy/` → Project-s-server ; Helm/Agones → Project-s-infra ; documentation → Project-s-docs |
| A9 | `tools/netlab` (mesures internes) était publié avec le client. | faible | Project-s-lab (privé) |
| A10 | Le client dépend de `game-server` pour le jeu local. | — (voulu) | conservé : bibliothèque `ps-server` sans `admin`, aucune seconde implémentation autoritaire |

## 4. Points vérifiés sans problème

- **Duplication de simulation** : aucune. La prédiction client appelle le même `step` de mouvement que le serveur, et il n'existe qu'une implémentation du contre-strafe, du recul et de la physique.
- **Dépendances graphiques côté serveur** : aucune. `game-server` ne dépendait pas de Bevy, et l'image Docker faisait 119 Mo.
- **Secrets** :
  - aucun dans le code ni dans les configurations (recherche des motifs `password`/`secret`/`token`/`api_key` affectés à une chaîne littérale) ;
  - le jeton d'administration est lu dans l'environnement (`PROJET_S_ADMIN_TOKEN`) ;
  - le cookie de poignée de main est généré au démarrage.
- **Code mort et TODO** : aucun `todo!`, `unimplemented!`, `TODO` ni `FIXME` dans `crates/` et `tools/`. La lint `dead_code` passe sous `clippy -D warnings`.
- **Dépendances inutilisées** : aucune signalée par la compilation. `cargo-deny` est ajouté dans chaque dépôt.

## 5. Modules volumineux

| Fichier | Lignes | Décision |
|---|---|---|
| `game-sim/src/sim.rs` | 2 348 | conservé tel quel dans `ps-sim` : `Sim::step` est une machine d'état cohérente. Le découper uniquement pour la taille ajouterait des frontières artificielles dans le chemin critique. |
| `game-server/src/server.rs` | 1 481 | conservé : une seule responsabilité (le serveur sans E/S). |
| `game-client/src/ui.rs` | 1 352 | conservé dans le client : menus et paramètres egui. |
| `game-client/src/game.rs` | 1 241 | conservé dans le client : il alimente `CharacterFeed` et le HUD à partir de l'état réseau. |

## 6. Risques de la migration

| Risque | Mesure |
|---|---|
| Changement involontaire du feeling (mouvement, recul, contre-strafe) | Le code est déplacé sans modification de logique. Les tests de déterminisme, de contre-strafe, de recul et de replay restent dans Project-s-simulation et passent sur le tag publié. |
| Incompatibilité de versions entre client et serveur | À la connexion, `ps-transport` refuse un `TRANSPORT_VERSION` différent, puis `ps-server` refuse un `GAME_PROTOCOL` (`ps-sim-net`) ou une empreinte de contenu (`data_fingerprint`) différents ; voir [COMPATIBILITY_MATRIX.md](COMPATIBILITY_MATRIX.md). |
| Build non reproductible à cause des dépendances Git | Dépendances épinglées sur un tag, `Cargo.lock` versionné, CI en `--locked`. |
| Développement multi-dépôts pénible | `tools/bootstrap.py` et `[patch]` locaux ([DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)). |
| Flottants non portables entre plateformes | Les tests de déterminisme tournent sous Linux et Windows en CI. Le déterminisme **inter-plateformes** bit à bit n'est pas prouvé : le serveur reste l'autorité, et la prédiction tolère une correction. |
