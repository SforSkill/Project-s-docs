# Rapport de validation du baseline (archive)

> Rapport du dépôt unique `SforSkill/Projet-S` au commit `b586317` (tag `backup/pre-repo-split`), recopié sans modification des mesures. Noms de crates et chemins d'avant la migration. Rapport de la migration : [VALIDATION_REPORT.md](../VALIDATION_REPORT.md).


Toutes les valeurs ci-dessous viennent d'exécutions réelles faites le
26/11/2026. Aucune n'est estimée. Les commandes pour les reproduire sont dans
[`docs/validation.md`](validation.md).

Machine : Windows 11 Pro, Intel Core i5-13600KF, NVIDIA RTX 4060 Ti, Docker
Desktop (moteur 29.8.2) pour le serveur Linux. Rust 1.100.

## 1. Contrôles du code

| Contrôle | Résultat |
|---|---|
| `cargo fmt --all -- --check` | OK |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` | OK, 0 avertissement |
| `cargo test --workspace --release --locked` | **110 réussis, 0 échec**, 1 ignoré (`bot_match_report`, diagnostic) |
| `projet-s-server --check` sur `deploy/server.example.toml` | OK |
| `helm lint` + `helm template` (chart `deploy/helm/projet-s`) | OK, 2 ressources générées |

Les tests couvrent notamment :
- le déplacement et le contre-strafe ;
- la dispersion, le recul, la pénétration et le premier tir exact ;
- la compensation de latence ;
- la fumée, la bombe et le tagging ;
- les règles MR12/15/16, les prolongations et l'économie ;
- le déterminisme de la simulation et la relecture exacte d'un replay ;
- un match compétitif 5v5 de bots jusqu'à la fin d'une manche ;
- le transport chiffré (poignée de main, anti-rejeu, pertes) ;
- un test client-serveur de bout en bout sur lien simulé.

## 2. Client Windows (autotest, vraie fenêtre, 1600×900, build release)

| Exécution | Images | FPS moyen | p50 / p99 / max (ms) | Snapshots (perdus) | Octets/snapshot | RTT (ms) | Gigue (ms) | Interp. (ticks) | Corrections |
|---|---|---|---|---|---|---|---|---|---|
| Deathmatch, 5 bots, 1re exécution | 4841 | 194 | 3,07 / 17,35 / 126,1 | 3184 (0) | 228 | 22,2 | 12,63 | 6,04 | 2 |
| Deathmatch, 5 bots | 7784 | 311 | 3,14 / 4,60 / 56,3 | 3189 (0) | — | 3,3 | 1,09 | 2,35 | 0 |
| Deathmatch, 5 bots | 8198 | 328 | 2,99 / 4,25 / 57,2 | 3189 (0) | — | 3,8 | 1,10 | 2,35 | 0 |
| Compétitif 5v5, 9 bots | 7606 | 304 | 3,21 / 4,73 / 58,5 | 3189 (0) | 415 | 2,9 | 0,91 | 2,29 | 70 |
| **Build final**, deathmatch, 5 bots | 5786 | 231 | 4,17 / 6,93 / 70,7 | 3187 (0) | 227 | 6,5 | 1,63 | 2,52 | 1 |
| **Build final**, compétitif 5v5, 9 bots | 5742 | 230 | 4,21 / 6,91 / 64,4 | 3188 (0) | 513 | 4,1 | 1,26 | 2,40 | 25 |

- Compétitif : 275 événements urgents, 0 erreur de décodage, jusqu'à 8 joueurs
  distants affichés en même temps, 17 tirs inspectés.
- La première exécution inclut la compilation des shaders et le premier
  chargement, ce qui explique son p99 et sa gigue plus élevés.
- Les deux exécutions « build final » ont été lancées sur le binaire livré,
  juste après une compilation de 5 minutes. Le FPS plus bas (230 contre 300 à
  330) n'a pas été analysé ; la machine n'était pas au repos.
- Build final, compétitif : 330 événements urgents, 9 joueurs distants affichés.
- Training Lab en build debug : 235 FPS.
- Rapports bruts : `docs/results/autotest/` (`rel-*` : 1re exécution deathmatch et compétitif ; `final-*` : build final ; `mp-*` : essai Docker). Les deux exécutions deathmatch intermédiaires n'ont été relevées que dans la console.

## 3. Serveur dédié Linux (Docker) et deux clients réels

L'image `projet-s-server:0.1.0-alpha` fait 119 Mo (Debian bookworm-slim,
utilisateur non root).

| Vérification | Résultat |
|---|---|
| `GET /health` | 200 |
| `GET /status` sans jeton | 401 |
| 2 clients Windows en UDP vers le conteneur (deathmatch, 4 bots, 25 s) | les 2 rapports sont `ok` |
| Client b (fenêtre au premier plan) | 301 FPS, RTT 3,4 ms, 3189 snapshots, 0 perdu, 0 erreur de décodage |
| Client a (fenêtre en arrière-plan, bridée par Windows) | 62 FPS, 3189 snapshots, 0 perdu |
| Tick serveur (`/metrics`) | moyenne 40 µs, p99 176 µs, max 253 µs, budget 7 812 µs à 128 Hz ; **0 tick en retard** |
| Commandes manquantes côté serveur | 30 au total, toutes au moment de la connexion |
| Éliminations pendant l'essai | 13 |

Avant correction, un premier essai à deux clients avait donné 707 commandes
manquantes. Le client abandonnait le retard accumulé après une saccade de rendu ;
il le rattrape maintenant, avec au plus 8 commandes par frame et un abandon
seulement au-delà de 32. Les chiffres ci-dessus sont postérieurs à la
correction.

## 3 bis. VPS réel par Internet

Installation systemd selon `docs/deployment.md` sur un VPS OVH : Debian 12,
2 vCPU, 2 Go de RAM, déjà occupé par 13 conteneurs, qui sont restés `Up`.
Configuration : compétitif, équipes complétées par des bots, replays coupés.

| Vérification | Résultat |
|---|---|
| `--check`, `systemctl is-active` | OK, `active` |
| `/health` ; `/status` sans jeton | 200 ; 401 |
| Mémoire du service | 3,7 Mo au démarrage, 8,7 Mo de RSS avec 10 bots |
| CPU | environ 13 % d'un cœur avec 10 bots ; tick moyen 92 µs |
| Client Windows (autotest, 25 s) par Internet vers le VPS | `ok` : 241 FPS, RTT 26,8 ms, gigue 4,1 ms, 3182 snapshots, **0 perdu**, 0 erreur de décodage, 3 corrections, 156 événements urgents, 591 octets par snapshot |
| Ticks en retard côté serveur | 0 |

Ces chiffres valent pour un seul client humain scripté. Une partie entre
plusieurs humains n'a toujours pas été jouée.

## 4. Laboratoire réseau A/B/C/D

60 exécutions : 5 profils × 4 variantes × 3 graines, 30 s chacune. Vrai serveur
et vrais clients sur des liens simulés. Tableau complet et analyse :
[`docs/network-lab.md`](https://github.com/SforSkill/Project-s/blob/backup/pre-repo-split/docs/network-lab.md) ; données brutes :
`docs/results/netlab/netlab.csv` et `netlab.json`.

| Profil | p95 erreur de vue A / D (u) | p95 erreur de rembobinage | Rembobinage max A / B,C / D |
|---|---|---|---|
| lan | 4,61 / 3,17 | 0,06 | 0,07 / 0,07 / 0,07 |
| good | 7,50 / 6,08 | 0,06 | 0,07 / 0,07 / 0,13 |
| average | 12,97 / 11,43 | 0,06 | 0,10 / 0,10 / 0,10 |
| bad | 20,70 / 18,38 | 0,07 | 0,40 / 0,31 / 0,97 |
| harsh | 26,41 / 23,65 | 0,09 à 0,11 | 2,04 / 0,59 / 1,78 |

Débit descendant : 291 à 292 kbit/s à 128 Hz, 582 à 583 kbit/s à 256 Hz.
Commandes manquantes après l'échauffement : 0 à 5 par exécution.

## 5. Benchmarks (criterion, `cargo bench`)

| Mesure | Temps médian |
|---|---|
| `engine-physics` `trace_box_player_step` | 99,6 ns |
| `engine-physics` `trace_ray_long` | 821,8 ns |
| `engine-physics` `ray_segments_long` | 692,8 ns |
| `engine-movement` `player_tick_128hz_stairs` | 322,7 ns |
| `engine-hitreg` `ray_vs_hitboxes` | 129,7 ns |
| `game-sim` `sim_tick_5v5_bots` | 2,43 µs |

## 6. Ce qui n'a PAS été validé

- **Client Linux** : construit en CI uniquement, jamais lancé sur une machine
  avec écran.
- **Réseau dégradé réel** : il n'a été mesuré qu'en simulation. Le VPS n'a été testé qu'avec un seul client, sur une bonne connexion.
- **Helm et Agones** : aucun cluster ; seuls `helm lint` et `helm template` ont
  été exécutés.
- **Parties avec plusieurs humains** : les essais à deux clients utilisaient
  des entrées scriptées.
- **Match compétitif complet de 30 manches joué à la main** : les règles sont
  testées, mais aucune partie complète n'a été jouée en temps réel.
- **Lecteur de replay** : il n'existe pas.
- **Workflows GitHub Actions** : voir le rapport final de livraison, selon les
  exécutions réelles sur GitHub.
