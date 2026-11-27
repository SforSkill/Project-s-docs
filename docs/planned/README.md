# Composants prévus

Ces composants ont un périmètre arrêté, mais **aucun code** : aucun dépôt n'est créé avant d'avoir du code réel à héberger ([ADR 0007](../decisions/0007-multi-repository.md)). Quand ils existent, leurs contrats sont déjà dans `ps-core-protocol` ([API_CONTRACTS.md](../../API_CONTRACTS.md)).

| Composant | Dépôt futur | Visibilité | Priorité | Document |
|---|---|---|---|---|
| Core | Project-s-core | privé | P1 | [core.md](core.md) |
| Orchestrateur et agent de nœud | Project-s-orchestrator | privé | P1 | [orchestrator.md](orchestrator.md) |
| Anti-triche | Project-s-anticheat | privé | P1 | [anticheat.md](anticheat.md) |
| Administration | Project-s-admin | privé | P2 | [admin.md](admin.md) |
| Launcher | Project-s-launcher | à décider | P3 | [launcher.md](launcher.md) |
| Site public | Project-s-web | public | P3 | [web.md](web.md) |

À la création d'un de ces dépôts, déplacer son document dans le `SCOPE.md` du dépôt. Ne laisser ici qu'un lien.
