# Rapport de validation de la migration

Ce rapport date du 27/11/2026. Chaque valeur vient d'une exécution réelle. Ce qui n'a pas été exécuté figure dans la section 6. Méthode : [docs/validation.md](docs/validation.md).

Machine locale : Windows 11 Pro build 26300, Intel Core i5-13600KF, 31,8 Go, NVIDIA RTX 4060 Ti, rustc 1.100.0. CI : GitHub Actions, `ubuntu-22.04` et `windows-latest`.

Référence avant migration : le monolithe `b586317`, tag `backup/pre-repo-split`. Son rapport donnait 110 tests réussis, ainsi que l'autotest, le netlab, Docker et le VPS ([archive](docs/baseline-validation-report.md)).

## 1. Frontières de dépendances

`tools/check_boundaries.py` a été exécuté sur chaque dépôt, en local puis en CI (job `rust / boundaries`) :

| Dépôt | Crates du workspace | Crates `ps-*` dans le graphe | Résultat |
|---|---|---|---|
| Project-s-protocol v0.1.0 | 3 | 3 | respecté |
| Project-s-netcode v0.1.0 | 1 | 1 | respecté |
| Project-s-simulation v0.1.0 | 8 | 11 | respecté |
| Project-s-content v0.1.0 | 2 | 10 | respecté |
| Project-s-engine v0.1.1 | 1 | 1 | respecté |
| Project-s-server v0.2.0-alpha.1 | 2 | 13 | respecté |
| Project-s (PR #9) | 2 | 16 | respecté |
| Project-s-lab | 2 | 15 | respecté |

**Test négatif.** On a ajouté `tokio*` aux paquets interdits de Project-s-server. Le script échoue alors et affiche le chemin `ps-server -> tokio -> tokio-macros` : il détecte donc les dépendances transitives.

## 2. Compilation et tests par dépôt

Il s'agit de la CI commune [`rust.yml@v0.1.0`](.github/workflows/rust.yml) :
- `fmt` ;
- clippy avec `-D warnings` ;
- `cargo doc` ;
- `cargo test --workspace --all-features --release --locked`, sous Linux et Windows ;
- `cargo-deny` ;
- frontières.

Nombre de tests relevé dans les journaux de la CI de `main` :

| Dépôt | CI | Tests réussis (Linux / Windows) | Échecs | Ignorés |
|---|---|---|---|---|
| Project-s-protocol | verte | 18 / 18 | 0 | 0 |
| Project-s-netcode | verte | 8 / 8 | 0 | 0 |
| Project-s-simulation | verte | 76 / 76 | 0 | 1 (`bot_match_report`, diagnostic) |
| Project-s-content | verte | 10 / 10 | 0 | 0 |
| Project-s-engine | verte | 16 / 16 | 0 | 0 |
| Project-s-server | verte (avec le `--check` du serveur sur le contenu épinglé) | 1 / 1 | 0 | 0 |
| Project-s-lab (privé) | verte, Linux seul (avec une série courte du netlab) | 7 | 0 | 0 |
| Project-s-infra (privé) | verte : compose config ×4, helm lint, kubeconform, `systemd-analyze`, actionlint, gitleaks | — | — | — |
| Project-s-docs | verte : liens, actionlint, Python | — | — | — |
| Project-s, PR #9 | verte (avec le `--check` du client) | 10 / 10 | 0 | 0 |

**Note sur le client.** Les 10 tests passent aussi en local (sans `[patch]`, en `--locked`), dont 4 tests de bout en bout entre `ps-netclient` et `ps-server` sur UDP réel et sur un lien dégradé simulé. `Project-S --check` affiche « données valides (3 cartes, empreinte 2aa9cbf7b64f57f0) ».

**Total : 146 tests.** C'est plus que les 110 du baseline, pour deux raisons :
- de nouveaux tests ont été ajoutés : contrats de `ps-core-protocol`, personnages de `ps-engine-character`, déterminisme du lab ;
- le lab garde une copie temporaire du client réseau, avec ses 4 tests e2e (section 6).

## 3. Bout en bout : serveur dédié + 2 clients réels

Mesures brutes : `Project-s-lab/results/e2e/2026-11-27/` (dépôt privé). Configuration :
- serveur `ps-server` v0.2.0-alpha.1, compilé depuis les tags publiés ;
- 2 clients `Project-S` de la PR #9, en `--autotest --connect`, avec une vraie fenêtre et un vrai GPU ;
- carte `ps_citadel`, mode deathmatch, 2 bots.

| Étape | Résultat |
|---|---|
| Démarrage, santé, authentification de l'administration | **validé** : `/health` 200, `/status` sans jeton 401, avec jeton 200 |
| Connexion des 2 clients (handshake, `GAME_PROTOCOL`, empreinte du contenu) | **validé** : slots 2 et 3 |
| Déplacement, tir, visibilité mutuelle | **validé** : 62 et 55 tirs inspectés, jusqu'à 3 joueurs distants affichés |
| Dégâts, morts, réapparition | **validé côté serveur** : 6 kills dans la partie, bots à 3 kills et 2 morts chacun |
| Réseau, 30 s par client | **validé** : 3831 snapshots par client, 0 perdu, 0 erreur de décodage ; RTT de 16,4 et 4,3 ms ; 1 correction de prédiction au total |
| Serveur | tick moyen de 24,8 µs, p99 de 82 µs, max de 1,3 ms ; 3 ticks en retard sur 5700 ; 2 paquets rejetés, 0 message invalide |
| Déconnexion des clients | **validé** : `leave`, puis `clients: 0` |
| Arrêt propre avec un client connecté | **validé** : `quit` → « serveur arrêté », fin du processus ; le client détecte la perte de session |
| Reconnexion à une partie en cours | **non testé** (section 6) |

Le client A affichait 78 FPS en moyenne, contre 352 pour le B, parce que les deux fenêtres partageaient le GPU. Ce n'est pas une mesure de performance du client.

## 4. Benchmarks avant/après

Mesures brutes : `Project-s-lab/results/bench/2026-11-27/` et `Project-s-lab/results/netlab/`.

### Criterion (simulation)

Même machine, exécutions successives :

| Bench | `b586317` | v0.1.0, même profil | Écart |
|---|---|---|---|
| ray_vs_hitboxes | 62,14 ns | 62,64 ns | +0,8 % |
| player_tick_128hz_stairs | 180,67 ns | 179,29 ns | −0,8 % |
| trace_box_player_step | 53,58 ns | 53,80 ns | +0,4 % |
| trace_ray_long | 445,15 ns | 450,32 ns | +1,2 % |
| ray_segments_long | 307,88 ns | 309,99 ns | +0,7 % |
| sim_tick_5v5_bots | 2,1209 µs | 2,1193 µs | −0,1 % |

Aucun écart ne dépasse le bruit de mesure.

Premier passage sans profil : +12,7 % sur `player_tick_128hz_stairs`. La cause est l'absence de `[profile.release]` dans le workspace de Project-s-simulation. Les binaires livrés ne sont pas touchés, car leur workspace a gardé le profil. Correction proposée : SforSkill/Project-s-simulation#1.

### Laboratoire réseau

60 exécutions : 5 profils × 4 variantes × 3 graines × 30 s. Les mesures déterministes sont **identiques bit à bit** à la série du baseline, avec 0 différence sur 60 lignes : toutes les colonnes sauf les durées du tick serveur, qui dépendent de la charge de la machine.

Comparaison 128 Hz / 256 Hz (`view p95`) :

| Profil | 128 Hz | 256 Hz | Écart |
|---|---|---|---|
| lan | 4,61 | 3,17 | −31 % |
| good | 7,50 | 6,08 | −19 % |
| average | 12,97 | 11,43 | −12 % |
| bad | 20,70 | 18,38 | −11 % |
| harsh | 26,41 | 23,65 | −10 % |

La bande descendante passe alors de 291 à 582 kbit/s par client.

## 5. Infrastructure (Project-s-infra, privé)

Validé localement avec Docker 29.8.2 et Helm 3.18.3 :
- **Pile `local` démarrée réellement** (serveur construit depuis `v0.2.0-alpha.1`, Prometheus, Grafana) :
  - serveur healthy ;
  - cible Prometheus `up` ;
  - tableau Grafana provisionné ;
  - Grafana en anonyme : 401.
- **PostgreSQL 17.6** : sauvegarde (`pg_dump -Fc`), suppression, puis restauration (`pg_restore --clean`), exécutée.
- **Validations hors ligne** :
  - `helm lint` ;
  - kubeconform `-strict` : 5 ressources valides avec les CRD Agones ; le test négatif est bien rejeté ;
  - `systemd-analyze verify` : passe ; le test négatif est bien rejeté.

## 6. Non validé ou partiel

| Point | État |
|---|---|
| Client sous Linux | compilé en CI, jamais lancé |
| Reconnexion à une partie en cours | champ `reconnect` présent dans `ClientMsg::Join` ; aucun test de bout en bout |
| Kubernetes et Agones | jamais déployés (aucun cluster, aucune autorisation) |
| Environnements development, staging et production | fichiers créés ; aucun hôte réel testé |
| Déploiement VPS du nouveau découpage | non refait : seul le baseline 0.1.0-alpha a été validé sur VPS |
| Image `ghcr.io/sforskill/project-s-server` | non publiée : job ajouté par SforSkill/Project-s-server#1 (CI verte, jamais exécuté avant une release) ; l'infra utilise `--build` en attendant |
| Release Please du lab et de l'infra | échoue : l'App de release (variable `RELEASE_APP_ID`, secret `RELEASE_APP_PRIVATE_KEY`) n'est pas accessible aux dépôts privés ; aucun tag ; changement de droits non effectué |
| Copie `ps-lab-netclient` dans le lab | dette : à remplacer par une dépendance `tag` vers `ps-netclient` quand le client sera tagué |
| Core, orchestrateur, anti-triche, admin | **non implémentés** : périmètres ([docs/planned/](docs/planned/)) et contrats (`ps-core-protocol`) seulement |
| Distribution du serveur dédié Windows | supprimée : l'archive du client ne contient plus `projet-s-server.exe` ; seule l'archive Linux de Project-s-server existe |
