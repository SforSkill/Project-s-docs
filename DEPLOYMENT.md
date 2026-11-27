# Déploiement

Seul le **serveur de jeu** est déployable aujourd'hui. Le Core, l'orchestrateur, PostgreSQL et l'anti-triche sont prévus ([docs/planned/](docs/planned/)).

| Cible | Où c'est décrit | État |
|---|---|---|
| Archive Linux + systemd (VPS) | [Project-s-server/docs/deployment.md](https://github.com/SforSkill/Project-s-server/blob/main/docs/deployment.md), `deploy/systemd/` | **validé** : VPS Debian 12, client connecté par Internet (baseline 0.1.0-alpha) |
| Image Docker, serveur seul | `Project-s-server/deploy/docker/` (Dockerfile, `compose.yaml`) | **validé** en CI : santé 200, `/status` 401 sans jeton |
| Image publiée `ghcr.io/sforskill/project-s-server` | `Project-s-server/.github/workflows/release.yml` | construite à chaque release du serveur |
| Pile complète par environnement (serveur, Prometheus, Grafana, PostgreSQL pour le futur Core) | Project-s-infra, `compose/` | créée ; validée par `docker compose config` |
| Kubernetes : Helm, Agones `Fleet` | Project-s-infra, `helm/` et `kubernetes/` | **non déployé** : manifestes validés hors ligne, aucun cluster |
| Client | archive Windows/Linux attachée à la release du dépôt Project-s (`release.yml`), avec le contenu épinglé | Windows validé ; le client Linux est construit, jamais lancé |

## Environnements

| Environnement | Usage | Différences |
|---|---|---|
| `local` | poste de développement | Compose, ports sur 127.0.0.1, jeton d'administration généré localement |
| `development` | serveur partagé de l'équipe | Compose, bots, journaux verbeux |
| `staging` | répétition d'une release | mêmes images et configuration que la production, données jetables |
| `production` | serveurs publics | systemd ou Kubernetes, jetons dans un gestionnaire de secrets, sauvegardes |

Les fichiers par environnement sont dans Project-s-infra. Aucun secret n'est versionné : chaque environnement fournit `PROJET_S_ADMIN_TOKEN` et les futurs identifiants PostgreSQL par l'environnement.

## Ports

| Port | Protocole | Exposition |
|---|---|---|
| 27015 | UDP | public : trafic de jeu |
| 27016 | TCP | **boucle locale ou réseau privé uniquement** : API d'administration, `/metrics` |

## Règles

- La boucle de simulation ne dépend d'aucun service externe. Un serveur démarre et joue sans Core, sans base de données et sans stockage objet.
- On ne déploie rien sur une infrastructure partagée sans autorisation. Vérifier d'abord que 27015/UDP et 27016/TCP sont libres : la procédure est dans le `deployment.md` du serveur.
- **Rollback** :
  - systemd : réinstaller l'archive de la version précédente ;
  - Docker et Kubernetes : revenir au tag d'image précédent.

  Le contenu est épinglé avec le binaire. Il n'y a donc aucune migration de données à défaire tant que le Core n'existe pas.
- **Kubernetes est facultatif** pour l'alpha : systemd et Docker restent les cibles principales.
