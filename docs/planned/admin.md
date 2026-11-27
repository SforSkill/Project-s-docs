# Project-s-admin (prévu, privé)

**Mission** : interface d'administration sécurisée : joueurs, sanctions, signalements, preuves, matchs, sessions verrouillées, instances, modes, versions, feature flags, statistiques, audit.

**Stack** : Nuxt et TypeScript.

## Règles

- Le panneau parle **uniquement** à l'API d'administration du Core, jamais directement à PostgreSQL.
- Rôles distincts, moindre privilège.
- Chaque action sensible est journalisée par le Core.
- Les chiffres affichés viennent de données réelles.

**Dépendances** : le contrat HTTP de l'API d'administration du Core (à définir). Jamais les types internes du Core.
