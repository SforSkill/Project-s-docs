# Périmètre de Project-s-docs

## 1. Mission
Centraliser la documentation transversale de l'écosystème Project S et l'outillage partagé par tous les dépôts.

## 2. Responsabilités
| Élément | Contenu |
|---|---|
| Documents racine | architecture, audit, carte des dépôts, graphe des dépendances, contrats, versionnement, compatibilité, migration, développement, déploiement, sécurité, validation |
| `docs/decisions/` | ADR transversales (0001 à 0007) |
| `docs/planned/` | périmètres des composants prévus sans code (Core, orchestrateur, anti-triche, admin, launcher, web) |
| `docs/git-workflow.md`, `docs/glossary.md` | règles de branches et de releases, vocabulaire |
| `releases/` | manifestes de release globale |
| `.github/workflows/rust.yml` | CI réutilisable des dépôts Rust |
| `tools/` | `check_boundaries.py`, `bootstrap.py`, `check_links.py` |

## 3. Ne contient jamais
- La documentation propre à un composant : elle reste dans son dépôt, et ce dépôt n'y fait que des liens.
- Du code de jeu ou de service.
- Un secret, une configuration de production, une règle de détection de l'anti-triche.
- Un résultat de mesure non reproduit : les mesures brutes vivent dans Project-s-lab ou dans le dépôt mesuré.

## 4. Dépendances autorisées
Python 3.11+ (bibliothèque standard seulement), Cargo (via `cargo metadata`), actions GitHub officielles ou largement utilisées (`actions/*`, `Swatinem/rust-cache`, `EmbarkStudios/cargo-deny-action`).

## 5. Dépendances interdites
Toute dépendance Python tierce dans `tools/`. Les scripts doivent tourner sur un poste neuf et en CI sans installation.

## 6. Interfaces publiques
- `rust.yml` : entrées `tools-ref`, `content`, `content-ref`, `bevy`, `extra`, `windows`.
- `check_boundaries.py [CHEMIN]` : code de sortie 0 ou 1.
- `bootstrap.py {check, clone, patch, unpatch, test}`.
- Le format de `boundaries.toml`, décrit dans `check_boundaries.py`.
- Le format des manifestes `releases/*.toml`.

## 7. Contrats
Les dépôts consommateurs épinglent un tag (`rust.yml@vX.Y.Z`, `tools-ref: vX.Y.Z`). Modifier une entrée de `rust.yml` ou le format de `boundaries.toml` est un changement de contrat : nouvelle version, et changelog.

## 8. Performance
`check_boundaries.py` ne compile rien : il lit `cargo metadata`. La CI commune sépare lint, tests, frontières et `cargo-deny`, qui s'exécutent en parallèle, et met en cache la compilation (`rust-cache`).

## 9. Sécurité
Le workflow réutilisable ne reçoit aucun secret, et `permissions: contents: read`. L'entrée `extra` est exécutée telle quelle : elle ne doit venir que du fichier de workflow versionné du dépôt appelant, jamais d'une donnée d'un événement (titre de PR, branche).

## 10. Compilation
Rien à compiler.

## 11. Tests
- Workflow `docs.yml` : liens relatifs (`check_links.py`), `actionlint` sur les workflows, compilation Python des scripts.
- `check_boundaries.py` est exercé par la CI de chaque dépôt Rust.

## 12. Versionnement
SemVer, avec un tag `vX.Y.Z` posé à la main (pas de release-please ici) à chaque changement de l'outillage (`rust.yml`, `tools/`), et une entrée dans `CHANGELOG.md`. Les seules modifications de texte ne demandent pas de tag : les liens pointent vers `main`.

## 13. Déploiement
Aucun. Les dépôts adoptent une nouvelle version de l'outillage par une PR qui change le tag.

## 14. Limites connues
- Pas de site généré : la documentation se lit sur GitHub, avec les diagrammes Mermaid rendus.
- `check_links.py` ne vérifie que les liens relatifs. Les liens vers les autres dépôts (et vers les dépôts privés) ne sont pas vérifiés.
- Le pipeline de compatibilité inter-dépôts se limite aujourd'hui aux tests de bout en bout de `ps-netclient` (client et serveur réels au tag épinglé). Il n'existe pas encore de workflow qui recompose une release globale entière.
