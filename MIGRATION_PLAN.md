# Plan de migration vers l'écosystème multi-dépôts

Départ : `SforSkill/Projet-S` au commit `b586317` (tag `backup/pre-repo-split`). Raisons : [ARCHITECTURE_AUDIT.md](ARCHITECTURE_AUDIT.md) et [ADR 0007](docs/decisions/0007-multi-repository.md). Résultats : [VALIDATION_REPORT.md](VALIDATION_REPORT.md).

| Phase | Contenu | État |
|---|---|---|
| 1. Audit et baseline | audit, compilation, 110 tests, mesures de référence du baseline (autotest, netlab), tag de sauvegarde | **terminé** |
| 2. Frontières internes | séparation `ps-sim` / `ps-sim-net`, contrats de fil dans `ps-types`, renommage `ps-*`, `boundaries.toml` | **terminé** |
| 3. Extraction des bibliothèques | protocol v0.1.0, netcode v0.1.0, simulation v0.1.0, engine v0.1.1, avec historique conservé par crate | **terminé** (publié) |
| 4. Extraction des applications | server v0.2.0-alpha.1, content v0.1.0, client (`refactor/repo-split`), lab (privé) | serveur et contenu publiés ; client fusionné (PR #9), **pas encore tagué** ; lab créé |
| 5. Infrastructure centrale | Core, orchestrateur, anti-triche : périmètres et contrats seulement (`ps-core-protocol`, [docs/planned/](docs/planned/)) | **contrats définis**, aucun service écrit (hors périmètre de la migration) |
| 6. Distribution et infrastructure | CI commune, cargo-deny, frontières, release-please par dépôt, Project-s-infra (Compose, systemd, Helm, Agones), image ghcr | **terminé**, sauf déploiement réel (non autorisé) |
| 7. Validation globale | compilation de chaque dépôt, tests, bout en bout serveur + 2 clients, benchmarks avant/après, rapport | voir [VALIDATION_REPORT.md](VALIDATION_REPORT.md) |

## Correspondance des crates

| Avant (Projet-S) | Après | Dépôt |
|---|---|---|
| `engine-core` (contrats de fil) | `ps-types` | Project-s-protocol |
| `engine-core` (utilitaires de simulation) | `ps-sim-core` | Project-s-simulation |
| `engine-replay` | `ps-replay` | Project-s-protocol |
| — (nouveau) | `ps-core-protocol` | Project-s-protocol |
| `engine-network` | `ps-transport` | Project-s-netcode |
| `engine-physics`, `engine-movement`, `engine-weapons`, `engine-hitreg`, `game-rules` | `ps-physics`, `ps-movement`, `ps-weapons`, `ps-hitreg`, `ps-rules` | Project-s-simulation |
| `game-sim` (simulation) | `ps-sim` | Project-s-simulation |
| `game-sim` (`proto`, `predict`, `record`) | `ps-sim-net` | Project-s-simulation |
| `engine-visibility` | `ps-visibility` | Project-s-server |
| `game-server` | `ps-server` | Project-s-server |
| `game-client/src/character/` | `ps-engine-character` | Project-s-engine |
| `game-client` | `ps-client` | Project-s |
| `game-netclient` | `ps-netclient` | Project-s |
| `configs/`, `maps/`, `tools/mapgen` | contenu, `ps-content-check`, `ps-mapgen` | Project-s-content |
| `tools/netlab` | laboratoire réseau | Project-s-lab |
| `deploy/docker`, `deploy/systemd`, `deploy/server.example.toml` | idem | Project-s-server |
| `deploy/helm`, `deploy/agones` | idem | Project-s-infra |
| `docs/architecture.md`, `docs/decisions/`, `docs/git-workflow.md`, `docs/glossary.md` | ce dépôt | Project-s-docs |

## Après la fusion du client

Dans l'ordre :
1. ~~Fusionner la PR `refactor/repo-split` du dépôt Project-s~~ (fait).
2. Fusionner la PR de release, ce qui crée le tag du client. Release Please n'en ouvre pas encore : un commit `refactor:` n'est pas « user facing ». Elle s'ouvrira au premier commit `feat:` ou `fix:`, ou avec un commit portant `Release-As: x.y.z`.
3. Mettre à jour `releases/2026.11-alpha.1.toml` (tag du client, `status = "released"`), puis la matrice de compatibilité.
4. Retirer les redirections : remplacer les liens restants vers `SforSkill/Projet-S` par `SforSkill/Project-s`. GitHub redirige l'ancien nom, mais pas indéfiniment s'il est réutilisé.
