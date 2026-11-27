# Project-s-core (prévu)

**Mission** : gérer l'écosystème métier de Project S : comptes, sessions, matchmaking, cycle de vie des matchs, sanctions, classement.

**Forme** : un monolithe modulaire en Rust (Axum, PostgreSQL via `sqlx`). Il n'y aura pas de microservices tant que la charge ne l'impose pas.

## Domaines

Chaque domaine aura son module : son API interne, ses tables, ses migrations. Aucun domaine ne lit les tables d'un autre. Il n'y aura pas de dossier `services/` fourre-tout.

| Domaine | Responsabilités |
|---|---|
| Identity | comptes, authentification, sessions, tokens, révocation |
| Player Session | présence, partie active, file active, verrouillage, reconnexion, récupération après incident |
| Matchmaking | modes, files, groupes, régions, ping, MMR, équilibrage, confirmation, annulation, réattribution |
| Match Lifecycle | création, réservation, allocation (via l'orchestrateur), warmup, en cours, résultats, annulation, abandon, crash |
| Trust | bannissements, suspensions, cooldowns, restrictions, historique, recours, autorisations |
| Game Modes | catalogue, activation, règles versionnées, disponibilité régionale, feature flags |
| Social | amis, invitations, groupes, notifications |
| Ranking | MMR, saisons, historique compétitif, calcul idempotent |
| Statistics | historique des matchs, statistiques, progression |
| Reports | signalements, dossiers, références vers les preuves |
| Administration | rôles d'administration, audit de chaque action sensible |
| Notifications | WebSocket : confirmation de partie, changements d'état, révocation, reconnexion |

## Invariants et protections prévues

| Invariant | Protection |
|---|---|
| Un joueur n'est jamais dans deux matchs | contrainte unique partielle `active_match(account_id) WHERE state IN (...)` |
| Pas de recherche officielle pendant un match compétitif | vérification transactionnelle à l'entrée en file |
| Fermer le jeu ne libère pas le verrou, la reconnexion retrouve le match | le verrou dépend du cycle de vie du match, pas de la connexion |
| Un banni n'obtient pas de ticket, et un serveur officiel refuse une connexion sans ticket | Trust est consulté à l'émission ; le ticket est signé et lié au match ([API_CONTRACTS.md](../../API_CONTRACTS.md)) |
| Réservation atomique | `SELECT … FOR UPDATE SKIP LOCKED`, ou contrainte d'unicité |
| Sanction en cours de partie, propagée aux serveurs | événement `PLAYER_BANNED`, poussé aux serveurs concernés |
| Un crash serveur ne verrouille personne indéfiniment | `HEARTBEAT_TIMEOUT_MS` met le match en `aborted` et libère les joueurs |
| Un résultat n'est jamais compté deux fois | `match_results.match_id` est la clé primaire, l'insertion est idempotente |
| Le client ne décide pas de son état officiel | toute transition est faite par le Core ou par un serveur officiel authentifié |
| Un serveur communautaire ne produit pas de résultat classé | seuls les serveurs alloués par l'orchestrateur ont une identité de service |

**Événements** : transactional outbox PostgreSQL ([EVENT_CONTRACTS.md](../../EVENT_CONTRACTS.md)).

**Dépendances** : `ps-core-protocol`. Jamais la simulation ni le moteur.
