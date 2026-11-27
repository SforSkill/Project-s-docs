# Développement local

## Prérequis

- **Git**.
- **Python 3.11+**, pour les scripts de `tools/`.
- **Rust via rustup.** Chaque dépôt épingle sa toolchain dans `rust-toolchain.toml` (1.100), installée automatiquement au premier `cargo`.
- **Linux, pour le client** : `libasound2-dev libudev-dev libwayland-dev libxkbcommon-dev`.
- **Facultatif** :
  - Docker, pour l'image du serveur et Project-s-infra ;
  - `gh`, pour les PR et les dépôts privés.

Vérification : `python tools/bootstrap.py check`.

## Récupérer l'écosystème

```bash
git clone https://github.com/SforSkill/Project-s-docs.git ps/Project-s-docs
cd ps
python Project-s-docs/tools/bootstrap.py clone            # dépôts publics, branche par défaut
python Project-s-docs/tools/bootstrap.py clone --private  # + Project-s-lab et Project-s-infra (accès requis)
python Project-s-docs/tools/bootstrap.py --root ../ps-2026.11 clone --release Project-s-docs/releases/2026.11-alpha.1.toml   # environnement d'une release
```

Tous les dépôts sont clonés côte à côte. Le contenu est trouvé sans configuration supplémentaire : le client et le serveur cherchent un dossier voisin `Project-s-content/`, ou à défaut `--data <dossier>` ou `PS_CONTENT_DIR`.

## Travailler sur un seul dépôt

C'est le cas normal. Chaque dépôt compile seul : ses dépendances internes sont des dépendances Git épinglées sur un tag, que Cargo télécharge.

```bash
cd Project-s-simulation
cargo test --workspace --all-features --release
python ../Project-s-docs/tools/check_boundaries.py .
```

Les tests qui lisent le contenu (simulation, serveur, client) trouvent `../Project-s-content`. Ailleurs, définir `PS_CONTENT_DIR`.

## Travailler sur plusieurs dépôts à la fois

Exemple : une modification de `ps-sim` à tester dans le serveur et le client avant de publier.

```bash
python Project-s-docs/tools/bootstrap.py patch    # écrit ps/.cargo/config.toml (hors des dépôts)
cd Project-s-server && cargo test --workspace     # utilise ../Project-s-simulation local
```

`patch` génère un `[patch."https://github.com/SforSkill/<dépôt>"]` pour chaque crate de chaque clone local. Cargo lit ce fichier depuis le dossier parent, pour tous les dépôts du dossier.

**Ne jamais commiter un `Cargo.lock` résolu avec les patches** : il contiendrait des chemins locaux et casserait `--locked` en CI. Avant de commiter un `Cargo.lock` :

```bash
python Project-s-docs/tools/bootstrap.py unpatch
cargo update -w && cargo test --workspace --locked
```

Ordre de publication d'un changement qui traverse plusieurs dépôts : voir [VERSIONING.md](VERSIONING.md#monter-la-version-dune-dépendance-interne).

## Lancer le jeu

| Quoi | Commande | Dépôt |
|---|---|---|
| Jeu local (serveur embarqué, bots) | `cargo run --release -p ps-client` | Project-s |
| Serveur dédié | `cargo run --release -p ps-server -- --config deploy/server.example.toml` (UDP 27015, admin 127.0.0.1:27016) | Project-s-server |
| Client vers un serveur | `cargo run --release -p ps-client -- --connect 127.0.0.1:27015` | Project-s |
| Démo des personnages | `cargo run --release -p ps-client -- --character-demo` | Project-s |
| Vérifier le contenu | `cargo run --release -p ps-content-check -- check .` | Project-s-content |
| Régénérer les cartes | `cargo run --release -p ps-mapgen` | Project-s-content |
| Laboratoire réseau | voir le README de Project-s-lab | Project-s-lab (privé) |
| Pile locale (serveur + Prometheus + Grafana) | voir `compose/` de Project-s-infra | Project-s-infra (privé) |

Les options exactes de chaque binaire s'affichent avec `--help`, dans son dépôt.

## Tout tester

```bash
python Project-s-docs/tools/bootstrap.py test     # fmt, clippy, tests, frontières dans chaque dépôt Rust cloné
```

Le Core, l'orchestrateur et PostgreSQL n'existent pas encore ([docs/planned/](docs/planned/)). Aucun mock ne les remplace dans le code de production : le serveur fonctionne en mode communautaire, sans eux.
