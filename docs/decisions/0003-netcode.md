# ADR 0003 — Netcode : UDP chiffré maison, snapshots delta, flux urgent

- **Statut** : accepté

## Contexte

Un FPS compétitif a besoin de trois choses :
- des entrées envoyées sans attendre ;
- un état du monde compact à 128 Hz ;
- des événements de combat (tir, dégât, mort) qui ne doivent pas attendre le
  prochain snapshot ni l'interpolation.

Les crates existantes ne donnent pas toutes ce contrôle : renet ou lightyear
sont liées à leur propre modèle de réplication, QUIC fonctionne par flux
ordonnés.

## Décision

- **`ps-transport`** : un transport sans E/S.
  - Poignée de main avec cookie : pas d'amplification ni d'usurpation d'adresse.
  - Chiffrement X25519 + HKDF + ChaCha20-Poly1305.
  - Quatre canaux : Input, Snapshot, Urgent, Reliable.
  - Simulateur de lien pour les tests.
- **Snapshots** : format binaire quantifié, en delta par rapport au dernier
  snapshot acquitté, filtré par la visibilité prédictive (PIM).
- **Flux urgent** : les événements de combat partent dès le tick où ils se
  produisent et sont affichés à réception.
- **Client** : prédiction et rejeu avec le code du serveur ; interpolation
  adaptative à la gigue ; extrapolation bornée des adversaires (variantes B et
  C) ; correction lissée (variante C, la variante par défaut).
- **Compensation de latence** bornée à 200 ms.

Le choix entre les variantes A, B, C et D repose sur les mesures de
le laboratoire réseau (dépôt privé `Project-s-lab`), pas sur des estimations.

## Conséquences

- La boucle serveur et le client réseau se testent sans socket (110 tests,
  laboratoire déterministe).
- Le serveur n'est pas authentifié par une clé longue durée ([modèle de menace](https://github.com/SforSkill/Project-s-server/blob/main/docs/security.md)).
- Coût : environ 292 kbit/s descendant par client à 128 Hz en duel. La variante
  D (256 Hz) double ce débit pour un gain de 10 à 30 % sur l'erreur de vue.
