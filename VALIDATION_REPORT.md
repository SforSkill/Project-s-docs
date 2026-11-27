# Rapport de validation de la migration

**État : en cours.** Ce rapport est complété au fil des validations. Chaque valeur vient d'une exécution réelle, avec sa date. Ce qui n'a pas été exécuté est marqué comme tel.

Machine locale : Windows 11 Pro, Intel Core i5-13600KF, NVIDIA RTX 4060 Ti, Rust 1.100.

Référence avant migration : `b586317` ([rapport du baseline](https://github.com/SforSkill/Project-s/blob/backup/pre-repo-split/docs/validation-report.md) : 110 tests réussis, autotest, netlab, Docker, VPS).

## 1. Frontières de dépendances

Le 27/11/2026, `python tools/check_boundaries.py` a été exécuté sur les tags publiés :

| Dépôt | Crates du workspace | Crates `ps-*` dans le graphe | Résultat |
|---|---|---|---|
| Project-s-protocol v0.1.0 | 3 | 3 | respecté |
| Project-s-netcode v0.1.0 | 1 | 1 | respecté |
| Project-s-simulation v0.1.0 | 8 | 11 | respecté |
| Project-s-content v0.1.0 | 2 | 10 | respecté |
| Project-s-engine v0.1.1 | 1 | 1 | respecté |
| Project-s-server v0.2.0-alpha.1 | 2 | 13 | respecté |

**Test négatif.** On a ajouté `tokio*` aux paquets interdits de Project-s-server. Le script échoue alors et affiche le chemin `ps-server -> tokio -> tokio-macros`. Il détecte donc bien les dépendances transitives.

## 2. Compilation et tests par dépôt

*À compléter : résultats de la CI de chaque dépôt une fois `rust.yml@v0.1.0` publié, puis résultats locaux du client.*

## 3. Bout en bout (serveur + 2 clients)

*À compléter.*

## 4. Benchmarks avant/après

*À compléter.*

## 5. Non validé

*À compléter.*
