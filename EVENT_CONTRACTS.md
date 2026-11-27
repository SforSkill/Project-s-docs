# Contrats d'événements

Propriétaire : `ps-core-protocol::events` ([Project-s-protocol](https://github.com/SforSkill/Project-s-protocol)). Ces événements circuleront entre le Core, le serveur, l'orchestrateur et l'anti-triche. Aucun de ces services n'existe encore : le contrat est **défini et testé**, mais il n'est **produit ni consommé** par aucun composant pour l'instant.

## Enveloppe

```rust
EventEnvelope {
    id: EventId,              // UUID, clé de déduplication
    envelope_version: u16,    // ENVELOPE_VERSION = 1 : forme de l'enveloppe
    version: u16,             // schéma du contenu de cet événement
    occurred_at: UnixMillis,  // UTC
    source: String,           // composant émetteur : « core.trust », « server/<id> »…
    correlation_id: CorrelationId, // UUID, relie les événements d'un même parcours (ex. un match)
    event: CoreEvent,         // JSON {"type": "MATCH_COMPLETED", "data": {...}}
}
```

## Catalogue

« Audit » : conservé sans limite de durée, journal d'audit. « Transient » : rétention courte, utile seulement pour l'état courant.

| Événement | Contenu | Persistance |
|---|---|---|
| `PLAYER_AUTHENTICATED` | `account_id`, `session_id` | Transient |
| `PLAYER_SESSION_REVOKED` | `account_id`, `session_id` | Audit |
| `PLAYER_BANNED` | `sanction` | Audit |
| `PLAYER_UNBANNED` | `account_id`, `sanction_id` | Audit |
| `MATCHMAKING_STARTED` | `party_id`, `mode` | Transient |
| `MATCHMAKING_CANCELLED` | `party_id` | Transient |
| `MATCH_FOUND` | `match_id`, `players` | Transient |
| `MATCH_ACCEPTED` | `match_id`, `account_id` | Transient |
| `MATCH_DECLINED` | `match_id`, `account_id` | Transient |
| `MATCH_CREATED` | `match_id`, `mode` | Audit |
| `SERVER_ALLOCATED` | `match_id`, `server_id`, `address` | Audit |
| `SERVER_READY` | `server_id` | Transient |
| `MATCH_STARTED` | `match_id`, `server_id` | Audit |
| `PLAYER_DISCONNECTED` | `match_id`, `account_id` | Transient |
| `PLAYER_RECONNECTED` | `match_id`, `account_id` | Transient |
| `MATCH_COMPLETED` | `result` (`MatchResult`) | Audit |
| `MATCH_ABORTED` | `match_id`, `reason` | Audit |
| `MATCH_RESULT_RECORDED` | `match_id` | Audit |
| `ANTICHEAT_EVIDENCE_CREATED` | `evidence_id`, `account_id`, `match_id`, `detector`, `detector_version`, `confidence`, `object_key` | Audit |
| `SERVER_UNHEALTHY` | `server_id`, `reason` | Transient |
| `SERVER_DRAINING` | `server_id` | Transient |
| `SERVER_RELEASED` | `server_id` | Transient |

La liste fait foi dans le code (`EventKind::ALL`). Le test `contracts.rs` de Project-s-protocol vérifie le nom sur le fil des 22 événements, la persistance (par exemple `PLAYER_BANNED` en Audit) et l'aller-retour JSON de l'enveloppe.

## Règles de traitement

- **Au moins une fois.** Un consommateur reçoit parfois un événement deux fois. Il déduplique sur `id`, et son traitement est idempotent.
- **Clés d'idempotence métier.** Un résultat est enregistré une seule fois par `MatchResult.match_id`, une sanction une seule fois par `sanction.id`.
- **Pas d'ordre global garanti.** Les décisions qui dépendent d'un état (verrouillage d'un joueur, réservation d'un serveur) relisent l'état transactionnel dans PostgreSQL, sans se fier à l'ordre d'arrivée des événements.
- **Publication** (prévue) : *transactional outbox* PostgreSQL dans le Core, c'est-à-dire que l'événement est écrit dans la même transaction que le changement d'état, puis publié. NATS JetStream pourra remplacer le relais si la charge le justifie ; le contrat ne change pas.
- **Synchrone quand une réponse est nécessaire.** Demander un ticket ou une allocation reste un appel synchrone. L'événement ne fait que notifier ce qui s'est passé.
- **Jamais dans le tick.** Le serveur de jeu produit ses événements dans une file en mémoire, vidée par une tâche hors de la boucle 128 Hz. Si le Core est indisponible, la partie continue.

## Évolution

- Nouvel événement : version mineure de `ps-core-protocol`.
- Nouveau champ dans un événement : champ optionnel, et `version` de l'événement incrémentée.
- Champ retiré ou renommé : version majeure. L'ancien nom n'est jamais réutilisé.
