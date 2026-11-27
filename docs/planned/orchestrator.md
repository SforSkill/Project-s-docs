# Project-s-orchestrator (prévu)

**Mission** : gérer les machines et les instances de serveurs de jeu. Le Core demande une instance ; l'orchestrateur décide où et comment la lancer.

## Control plane

- inventaire des machines, capacité, régions ;
- allocation, réservation, placement ;
- surveillance, drain, maintenance ;
- versions déployées, libération des ressources.

## Agent de nœud

Binaire léger installé sur chaque machine de jeu :
- heartbeats, matériel et métriques ;
- démarrage et arrêt des instances, réservation des ports ;
- téléchargement des versions et vérification d'intégrité (sha256 des archives de release) ;
- supervision des processus, mise à jour progressive.

## Fournisseurs d'exécution

Les fournisseurs passent par un trait commun.

| Fournisseur | Base existante | Priorité |
|---|---|---|
| systemd | l'unité durcie de Project-s-server | alpha |
| Docker | l'image `ghcr.io/sforskill/project-s-server` | alpha |
| Kubernetes / Agones | le `Fleet` de Project-s-infra | plus tard, sans réécrire le Core |

**Ne gère jamais** : le classement, les sanctions, les règles de jeu.

**Dépendances** : `ps-core-protocol`, pour les identifiants et les événements `SERVER_*`.
