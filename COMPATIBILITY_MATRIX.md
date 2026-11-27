# Matrice de compatibilité

Deux composants sont compatibles s'ils ont les mêmes versions de contrat ([VERSIONING.md](VERSIONING.md#versions-de-contrat)), pas s'ils ont les mêmes versions de crates.

## Release 2026.11-alpha.1

| Composant | Version | `TRANSPORT_VERSION` | `GAME_PROTOCOL` | Contenu (`data_fingerprint`) | Dépend de |
|---|---|---|---|---|---|
| Project-s-protocol | v0.1.0 | — | — | — | — |
| Project-s-netcode | v0.1.0 | **1** (définit) | — | — | — |
| Project-s-simulation | v0.1.0 | 1 | **1** (définit) | lit le contenu 0.1.0 en test | protocol v0.1.0, netcode v0.1.0 |
| Project-s-engine | v0.1.1 | — | — | — | — |
| Project-s-content | v0.1.0 | — | — | **`2aa9cbf7b64f57f0`** (définit) | simulation v0.1.0 (outils) |
| Project-s-server | v0.2.0-alpha.1 | 1 | 1 | `2aa9cbf7b64f57f0` | simulation v0.1.0, netcode v0.1.0, contenu v0.1.0 |
| Project-s (client) | en cours (`refactor/repo-split`) | 1 | 1 | `2aa9cbf7b64f57f0` | simulation v0.1.0, netcode v0.1.0, engine v0.1.1, server v0.2.0-alpha.1 (lib), contenu v0.1.0 |

## Avant la migration

| Client | Serveur | Compatibles | Raison |
|---|---|---|---|
| Projet-S 0.1.0-alpha.1 | Projet-S 0.1.0-alpha.1 | oui | même commit |
| Projet-S 0.1.0-alpha.1 | Project-s-server v0.2.0-alpha.1 | oui, si le contenu est le même | aucun changement de format pendant la migration ; `TRANSPORT_VERSION` et `GAME_PROTOCOL` sont restés à 1 |

## Vérifications

- **À la connexion** : `ps-transport` compare `TRANSPORT_VERSION`. `ps-server` compare `GAME_PROTOCOL` et `data_fingerprint`, puis renvoie `Kicked` avec un message explicite en cas de différence.
- **En CI** : le serveur lance `--check` sur le contenu épinglé (`content-ref` du workflow commun), et les tests de bout en bout de `ps-netclient` démarrent un vrai `ps-server`.
- **Replays** : l'en-tête porte `data_fingerprint`. Une relecture avec un autre contenu est refusée.

## Ajouter une ligne

À chaque release globale (`releases/*.toml`) :
1. Ajouter une section.
2. Recopier les constantes depuis le code des tags publiés, pas de mémoire.
3. Si une constante change, marquer en **gras** les composants qui doivent suivre.
