# Carte des dépôts

Org GitHub : [`SforSkill`](https://github.com/SforSkill). L'état indiqué est celui du 27/11/2026.

| Dépôt | Visibilité | Responsabilité exclusive | Contenu actuel | État |
|---|---|---|---|---|
| [Project-s](https://github.com/SforSkill/Project-s) | public | Client du jeu : menus, HUD, entrées, paramètres, connexion, intégration moteur/netcode/contenu, présentation des replays, Shot Inspector | `ps-client` (Bevy), `ps-netclient` (réseau client sans E/S, tests de bout en bout) | migré (branche `refactor/repo-split`, PR ouverte) |
| [Project-s-engine](https://github.com/SforSkill/Project-s-engine) | public | Moteur de présentation FPS générique sur Bevy | `ps-engine-character` (squelette, maillage, animation procédurale, matériau « peinture liquide », effets) | publié v0.1.1 |
| [Project-s-simulation](https://github.com/SforSkill/Project-s-simulation) | public | Simulation et gameplay partagés (unique implémentation, utilisée par le client et le serveur) | `ps-sim-core`, `ps-physics`, `ps-movement`, `ps-weapons`, `ps-hitreg`, `ps-rules`, `ps-sim`, `ps-sim-net` | publié v0.1.0 |
| [Project-s-netcode](https://github.com/SforSkill/Project-s-netcode) | public | Transport réseau temps réel | `ps-transport` (UDP chiffré sans E/S, 4 canaux, simulateur de lien) | publié v0.1.0 |
| [Project-s-protocol](https://github.com/SforSkill/Project-s-protocol) | public | Contrats et types communs | `ps-types`, `ps-replay`, `ps-core-protocol` | publié v0.1.0 |
| [Project-s-server](https://github.com/SforSkill/Project-s-server) | public | Serveur dédié autoritaire headless | `ps-server` (lib sans E/S + boucle UDP + binaire `projet-s-server`), `ps-visibility` (PIM), `deploy/` (Docker, systemd) | publié v0.2.0-alpha.1 |
| [Project-s-content](https://github.com/SforSkill/Project-s-content) | public | Contenu versionné | `configs/`, `maps/`, `manifests/content.toml`, `ps-content-check`, `tools/ps-mapgen` | publié v0.1.0 |
| [Project-s-docs](https://github.com/SforSkill/Project-s-docs) | public | Documentation transversale et outillage commun | ce dépôt | publié v0.1.0 |
| Project-s-lab | **privé** | Mesures, benchmarks, laboratoire réseau | laboratoire réseau (ex `tools/netlab`), résultats | créé ; pas de tag : Release Please n'a pas accès au secret de l'App |
| Project-s-infra | **privé** | Description et déploiement de l'écosystème | Compose, systemd, Helm, Agones, monitoring | créé, CI verte ; pas de tag (même raison) ; rien déployé |
| Project-s-core | privé (futur) | Comptes, sessions, matchmaking, cycle de vie des matchs, Trust, classement | — (contrats dans `ps-core-protocol`) | prévu : [docs/planned/core.md](docs/planned/core.md) |
| Project-s-orchestrator | privé (futur) | Machines et instances de serveurs de jeu | — | prévu : [docs/planned/orchestrator.md](docs/planned/orchestrator.md) |
| Project-s-anticheat | privé (futur) | Détection et preuves | — | prévu : [docs/planned/anticheat.md](docs/planned/anticheat.md) |
| Project-s-admin | privé (futur) | Interface d'administration | — | prévu : [docs/planned/admin.md](docs/planned/admin.md) |
| Project-s-launcher | — | Installation et mises à jour | — | prévu, non prioritaire : [docs/planned/launcher.md](docs/planned/launcher.md) |
| Project-s-web | — | Site public | — | prévu, non prioritaire : [docs/planned/web.md](docs/planned/web.md) |
| Projet-S-old | privé, archivé | Ancien dépôt, conservé en lecture seule | historique | archivé |

Un dépôt n'est créé que lorsqu'il a du code réel à héberger ([ADR 0007](docs/decisions/0007-multi-repository.md)). Les composants prévus ont déjà leur périmètre, et leurs contrats quand ils existent, mais aucun dépôt vide.

## Public ou privé

Les dépôts publics contiennent ce que le client distribue de toute façon, sous forme de binaire, ou ce qui n'a aucune valeur confidentielle : simulation, protocole, transport, moteur, contenu, serveur communautaire, documentation. La licence reste propriétaire : public ne veut pas dire libre.

Les dépôts privés contiennent ce qui ne doit pas être distribué :
- les mesures internes ;
- l'infrastructure de production ;
- les futurs services centraux : Core, orchestrateur, administration ;
- surtout les règles de détection de l'anti-triche.
