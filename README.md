# Project S — documentation de l'écosystème

FPS compétitif natif en Rust : simulation autoritaire à 128 Hz, netcode UDP chiffré, client Bevy, serveur dédié headless Linux.

Ce dépôt contient la documentation **transversale** de l'écosystème, ainsi que l'outillage commun :
- le workflow CI réutilisable ;
- la vérification des frontières de dépendances ;
- le script de mise en place du développement local.

La documentation propre à chaque composant reste dans son dépôt. Ce dépôt n'y fait que des liens.

## Par où commencer

| Besoin | Document |
|---|---|
| Comprendre l'architecture | [ARCHITECTURE.md](ARCHITECTURE.md), [REPOSITORY_MAP.md](REPOSITORY_MAP.md), [DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md) |
| Installer un poste de développement | [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md) |
| Contrats entre composants | [API_CONTRACTS.md](API_CONTRACTS.md), [EVENT_CONTRACTS.md](EVENT_CONTRACTS.md) |
| Versions et compatibilité | [VERSIONING.md](VERSIONING.md), [COMPATIBILITY_MATRIX.md](COMPATIBILITY_MATRIX.md), [releases/](releases/) |
| Déployer | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Sécurité | [SECURITY_BOUNDARIES.md](SECURITY_BOUNDARIES.md) |
| Historique de la migration | [ARCHITECTURE_AUDIT.md](ARCHITECTURE_AUDIT.md), [MIGRATION_PLAN.md](MIGRATION_PLAN.md), [VALIDATION_REPORT.md](VALIDATION_REPORT.md) |
| Décisions | [docs/decisions/](docs/decisions/) (ADR) |
| Composants prévus, pas encore écrits | [docs/planned/](docs/planned/) |
| Branches, PR et releases | [docs/git-workflow.md](docs/git-workflow.md) |
| Vocabulaire | [docs/glossary.md](docs/glossary.md) |

## Outillage

| Fichier | Rôle |
|---|---|
| [`.github/workflows/rust.yml`](.github/workflows/rust.yml) | CI commune des dépôts Rust : fmt, clippy, doc, tests Linux et Windows, `cargo-deny`, frontières |
| [`tools/check_boundaries.py`](tools/check_boundaries.py) | Fait échouer la CI si une crate dépend d'un paquet interdit par le `boundaries.toml` de son dépôt, ou si un cycle apparaît |
| [`tools/bootstrap.py`](tools/bootstrap.py) | Clone l'écosystème, vérifie les prérequis et génère la configuration `[patch]` locale |
| [`tools/check_links.py`](tools/check_links.py) | Vérifie les liens relatifs de cette documentation (CI de ce dépôt) |

Les autres dépôts épinglent un **tag** de ce dépôt (`rust.yml@v0.1.0`, `tools-ref: v0.1.0`), jamais `main`. Modifier `rust.yml` ou `check_boundaries.py` impose donc un nouveau tag, puis une PR dans chaque dépôt qui veut l'adopter.

Périmètre : [SCOPE.md](SCOPE.md). Licence : propriétaire ([LICENSE](LICENSE)).
