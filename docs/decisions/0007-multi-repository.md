# ADR 0007 — Écosystème multi-dépôts aux frontières vérifiées

- **Statut** : accepté (27/11/2026)

## Contexte

Projet-S était un seul workspace de 13 crates (commit `b586317`). Le client, le serveur, la simulation, le transport et les outils y partageaient tout. Rien n'empêchait par exemple :
- le serveur d'importer Bevy ;
- la simulation d'appeler le réseau ;
- un futur service central d'utiliser des types internes du jeu.

Les composants à venir ont aussi besoin de cycles de version distincts : Core, orchestrateur, anti-triche, administration. L'audit complet est dans [ARCHITECTURE_AUDIT.md](../../ARCHITECTURE_AUDIT.md).

## Décision

- **Un dépôt par responsabilité qui a du code réel.** Huit dépôts publics : client, moteur, simulation, netcode, protocole, serveur, contenu, documentation. Deux privés : laboratoire et infrastructure. Les composants sans code (Core, orchestrateur, anti-triche, admin, launcher, web) ont un périmètre écrit dans [docs/planned/](../planned/), mais aucun dépôt vide.
- **Visibilité.** Est public ce que le client distribue de toute façon, ou ce qui n'a aucune valeur confidentielle. Est privé ce qui ne doit pas être distribué : mesures internes, infrastructure de production, services centraux, règles de détection. La licence reste propriétaire partout.
- **Dépendances Git épinglées sur un tag**, pas de registre Cargo privé pour l'instant. Pas de `branch =` : un build est reproductible depuis le `Cargo.lock`.
- **Un `boundaries.toml` par dépôt**, vérifié en CI par `tools/check_boundaries.py` sur le graphe transitif.
- **CI commune** dans `Project-s-docs/.github/workflows/rust.yml`. Chaque dépôt l'épingle sur un tag.
- **Les frontières de dépôt ne deviennent pas des frontières réseau.** La simulation, le transport et le moteur restent des bibliothèques liées dans le processus.
- **Le jeu local passe par la bibliothèque `ps-server`**, sans sa feature `admin`, embarquée dans le client. Aucune seconde implémentation autoritaire.
- **Renommage** : `game-*`/`engine-*` deviennent `ps-*`. Les crates `engine-*` étaient de la simulation : elles sont dans Project-s-simulation, et « engine » désigne désormais le moteur de présentation. `game-sim` est séparé en `ps-sim` (simulation) et `ps-sim-net` (codec réseau, prédiction, enregistrement).
- **L'historique est conservé** : le dépôt client (`Projet-S`, renommé `Project-s`) garde tout son historique, et le tag `backup/pre-repo-split` marque le commit `b586317` d'avant la séparation. Chaque dépôt extrait cite ce commit source dans son premier commit. `Projet-S-old`, le dépôt antérieur au flux trunk-based, est archivé en lecture seule.

## Conséquences

- Un changement de contrat touche plusieurs dépôts. Il se fait dans une même série de PR, en publiant d'abord le producteur, puis en mettant à jour les tags des consommateurs ([VERSIONING.md](../../VERSIONING.md)).
- Le développement simultané de plusieurs dépôts passe par des `[patch]` locaux, jamais versionnés ([DEVELOPMENT_SETUP.md](../../DEVELOPMENT_SETUP.md)).
- Les dépôts privés peuvent dépendre des publics, jamais l'inverse.
- Sans registre, `cargo update` ne voit pas les nouvelles versions : la montée de version d'une dépendance interne se fait à la main, en changeant le tag. À réévaluer si le nombre de dépôts augmente (registre Cargo privé, par exemple Kellnr).
