# Reproduire la validation

Chaque chiffre de [VALIDATION_REPORT.md](../VALIDATION_REPORT.md) vient d'une des commandes ci-dessous. Les dépôts sont clonés côte à côte (`python tools/bootstrap.py clone`) ; le contenu est trouvé par `PS_CONTENT_DIR` ou dans le dossier voisin `Project-s-content/`. Méthode d'avant la migration : [rapport du baseline](baseline-validation-report.md).

## Contrôles de chaque dépôt Rust

Ce sont ceux de la CI commune ([`rust.yml`](../.github/workflows/rust.yml)) :

```sh
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
cargo test --workspace --all-features --release --locked
python ../Project-s-docs/tools/check_boundaries.py .
cargo deny check
```

Ou pour tous les dépôts présents : `python Project-s-docs/tools/bootstrap.py test`.

Contrôle des données du serveur :
```sh
cargo run --release --locked -p ps-server -- --data ../Project-s-content --config deploy/server.example.toml --check
```

Diagnostic ignoré par défaut (Project-s-simulation) :
```sh
cargo test --release -p ps-sim --test sim bot_match_report -- --ignored --nocapture
```

## Autotest du client (vraie fenêtre, vrai GPU), dépôt Project-s

```sh
target/release/Project-S --autotest --map ps_citadel --mode deathmatch --bots 5 --seconds 25 --out autotest-dm
target/release/Project-S --autotest --connect 127.0.0.1:27015 --seconds 25 --out autotest-net
```

Le client joue avec des entrées scriptées (déplacement, rotation, tir), prend des captures puis écrit `autotest-report.json` : images (FPS moyen, p50, p99, max), réseau (snapshots, pertes, RTT, gigue, corrections, erreurs de décodage), joueurs distants affichés. La première exécution après un build compile les shaders.

## Serveur dédié et deux clients

```sh
# Project-s-server
cargo run --release --locked -p ps-server -- --data ../Project-s-content --map ps_citadel --mode deathmatch --bots 4
# Project-s, deux terminaux
target/release/Project-S --autotest --connect 127.0.0.1:27015 --seconds 25 --out mp-a
target/release/Project-S --autotest --connect 127.0.0.1:27015 --seconds 25 --out mp-b
curl -s localhost:27016/metrics | grep projet_s_
```

Sans GPU, les tests e2e de `ps-netclient` (dépôt Project-s) font jouer des clients réels contre un vrai serveur sur UDP : `cargo test --release -p ps-netclient`.

## Laboratoire réseau (Project-s-lab, privé)

`cargo run --release --locked -p ps-netlab -- --seconds 30 --seeds 3 --out results/netlab/<date>-<commit>` : 5 profils × 4 variantes × 3 graines, CSV et JSON dans `results/netlab/<date>-<commit>/`.

## Benchmarks (Project-s-simulation)

```sh
cargo bench -p ps-physics -p ps-movement -p ps-hitreg -p ps-sim
```
