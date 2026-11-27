# Glossaire

Chemins notés `dépôt:crate/fichier` (dépôts de l'org `SforSkill`, préfixe `Project-s-` omis).

| Terme | Sens dans Project S | Où |
|---|---|---|
| Tick | un pas de simulation ; 128 par seconde par défaut (`TickRate`) | `protocol:ps-types/src/tick.rs` |
| Sub-tick | horodatage d'une entrée à l'intérieur d'un tick (`SimTime` fractionnaire) : un tir part à l'instant exact du clic | `protocol:ps-types/src/cmd.rs`, client `ps-netclient` |
| `UserCmd` | ce qu'un client demande pour un tick (boutons, angles, segments) | `protocol:ps-types/src/cmd.rs` |
| Sans E/S (sans-IO) | code qui reçoit des datagrammes et une horloge et rend des datagrammes, sans socket : testable de façon déterministe | `netcode:ps-transport`, `server:ps-server`, client `ps-netclient` |
| Autoritaire | seul le serveur décide de l'état du jeu ; le client prédit et se corrige | `simulation:ps-sim`, `server:ps-server` |
| Prédiction | le client rejoue localement son propre déplacement avec le même code que le serveur | `simulation:ps-sim-net/src/predict.rs` |
| Interpolation / extrapolation | affichage des autres joueurs entre deux snapshots reçus, ou au-delà du dernier | client `ps-netclient` |
| Snapshot | état du monde envoyé par le serveur, en delta | `simulation:ps-sim-net/src/proto.rs` |
| Lag compensation | le serveur rejoue les hitboxes à l'instant vu par le tireur, dans une limite | `simulation:ps-hitreg` |
| PIM | gestion d'intérêt prédictive : un client ne reçoit que les joueurs qu'il peut voir bientôt (anti-wallhack) | `server:ps-visibility` |
| Brush | volume convexe défini par des plans ; brique de base des cartes et des collisions | `simulation:ps-physics/src/brush.rs` |
| Hull | boîte du joueur balayée contre le monde (`trace_hull`) | `simulation:ps-physics/src/world.rs` |
| Contre-strafe | appuyer sur la direction opposée pour s'arrêter net et tirer précis | `simulation:ps-movement`, `simulation:docs/movement.md` |
| Pénétration (wallbang) | balle qui traverse une surface selon son matériau et son épaisseur | `simulation:ps-weapons`, `content:configs/materials.toml` |
| MR12 / MR15 / MR16 | nombre maximal de manches : 24, 30 ou 32 | `content:configs/rules.toml`, `simulation:ps-rules` |
| Freeze time | début de manche, joueurs immobiles, achat possible | `simulation:ps-rules` |
| `.psrp` | fichier de replay : entrées par tick, rejouées à l'identique | `protocol:docs/replay-format.md` |
| Ticket | autorisation signée Ed25519 par le Core pour un compte, un match et un serveur | `protocol:ps-core-protocol/src/ticket.rs` |
| Netlab | laboratoire réseau : vrai serveur et vrais clients sur des liens simulés | dépôt `Project-s-lab` (privé) |
| Dossier de contenu | dossier qui contient `configs/`, `maps/` et `manifests/` (`--data`, `PS_CONTENT_DIR`) | `content` |
| u | unité de distance Source, 1 u = 2,54 cm | — |
