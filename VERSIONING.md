# Versionnement

## Règles par dépôt

- **SemVer** dans chaque dépôt : `version.txt`, `[workspace.package] version` et le tag Git `vX.Y.Z`. Avant la 1.0, une rupture incrémente le chiffre mineur (`bump-minor-pre-major`).
- **Le serveur et le client** sont en pré-release alpha (`0.Y.Z-alpha.N`).
- **release-please** ([docs/git-workflow.md](docs/git-workflow.md)) produit le changelog, la PR de release, le tag et la release GitHub à partir des titres de PR au format Conventional Commits. Personne ne tague à la main, sauf pour le premier tag d'un dépôt.
- **`Cargo.lock` versionné** dans tous les dépôts, bibliothèques comprises : la CI compile en `--locked`.
- **Un tag publié ne bouge jamais.** Pour corriger, on publie une nouvelle version.

## Dépendances entre dépôts

```toml
# Bon : tag immuable, résolu dans Cargo.lock au commit exact
ps-sim = { git = "https://github.com/SforSkill/Project-s-simulation", tag = "v0.1.0" }

# Interdit en production : branche mouvante
ps-sim = { git = "https://github.com/SforSkill/Project-s-simulation", branch = "main" }
```

- Seuls les tags (`tag = "vX.Y.Z"`) et les commits exacts (`rev = "<sha>"`) sont autorisés. `rev` est réservé au dépôt privé Project-s-lab, quand il mesure un commit non publié.
- `deny.toml` (`[sources] allow-git`) n'autorise que les dépôts SforSkill.
- Aucune crate n'est publiée sur crates.io : `publish = false` partout.
- Pas de registre Cargo privé pour l'instant ([ADR 0007](docs/decisions/0007-multi-repository.md)).
- Développement local de plusieurs dépôts à la fois : `[patch]` dans un `.cargo/config.toml` **non versionné** ([DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)). Un `Cargo.lock` résolu avec ces patches ne se commite jamais : il pointerait vers des chemins locaux.

## Monter la version d'une dépendance interne

1. Publier le producteur : fusionner sa PR de release, ce qui crée le tag.
2. Dans chaque consommateur, ouvrir une PR qui :
   - change le tag dans `[workspace.dependencies]` ;
   - lance `cargo update -p <crate>` ;
   - adapte le code ;
   - met à jour le manifeste de release et la [matrice de compatibilité](COMPATIBILITY_MATRIX.md) si un contrat a changé.
3. Ordre de publication : protocol, puis netcode, puis simulation, puis engine et content, puis server, puis client.

## Versions de contrat

Elles sont indépendantes des versions de crates : un patch d'une crate ne change pas son format.

| Constante | Propriétaire | Valeur | Règle |
|---|---|---|---|
| `TRANSPORT_VERSION` | `ps-transport` | 1 | égalité stricte, vérifiée à la poignée de main |
| `GAME_PROTOCOL` | `ps-sim-net::proto` | 1 | égalité stricte, vérifiée au `Join` |
| `data_fingerprint` | Project-s-content (`manifests/content.toml`) | `2aa9cbf7b64f57f0` | égalité stricte, vérifiée au `Join` |
| `PROTOCOL_VERSION` | `ps-types` | 1.0 | majeure égale (`is_compatible_with`) ; portée dans les tickets (`game_protocol`) |
| `TICKET_VERSION` | `ps-core-protocol::ticket` | 1 | égalité stricte |
| `ENVELOPE_VERSION` | `ps-core-protocol::events` | 1 | règle pour les futurs consommateurs : refuser une enveloppe de version supérieure |
| `FORMAT_VERSION` (replay) | `ps-replay` | 1 | relecture d'une version connue seulement |
| `format` (manifeste de contenu) | Project-s-content | 1 | lu par `ps-content-check` |

## Release globale

Une release de l'écosystème est un fichier `releases/<AAAA.MM>-<canal>.<N>.toml`. Il associe une version de chaque composant, ainsi que les versions de contrat attendues.

Il sert à :
- reconstruire un environnement compatible (`tools/bootstrap.py --release releases/<fichier>`, qui clone chaque dépôt au tag indiqué) ;
- servir de référence au pipeline de compatibilité.

**Double version du protocole de jeu (limite connue).** `PROTOCOL_VERSION` (`ps-types`, 1.0) et `GAME_PROTOCOL` (`ps-sim-net`, 1) désignent tous deux les messages de jeu. Seul `GAME_PROTOCOL` est vérifié à la connexion. Les unifier changerait le format sur le fil : ce sera fait avec l'ajout du ticket dans `Join`, en dérivant `GAME_PROTOCOL` de `PROTOCOL_VERSION.major`.

Première release : [releases/2026.11-alpha.1.toml](releases/2026.11-alpha.1.toml).
