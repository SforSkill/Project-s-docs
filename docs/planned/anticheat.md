# Project-s-anticheat (prévu, privé)

**Mission** : analyser les événements autoritaires et les replays, puis produire des **signaux** et des **preuves**. Il ne sanctionne pas lui-même : il transmet au domaine Trust du Core, qui décide.

## Analyses prévues

- déplacements et mouvements angulaires ;
- automatismes et entrées anormales ;
- incohérences ;
- replays et scripts ;
- corrélation de signaux.

## Gouvernance des détecteurs

- détecteurs versionnés (`detector`, `detector_version` dans `ANTICHEAT_EVIDENCE_CREATED`) ;
- évaluation des faux positifs ;
- retraitement des anciennes parties.

## Règles

- **Aucune règle de détection dans le client.** Le dépôt reste privé.
- Les violations impossibles sont bloquées immédiatement par le serveur, qui est autoritaire. Les soupçons comportementaux portent un niveau de confiance (`confidence`) et ne déclenchent jamais seuls une sanction automatique.
- Une performance inhabituelle n'est pas une preuve.
- Les traitements lourds sont faits hors du serveur de jeu, à partir des replays en stockage objet.
- Pas d'anti-triche noyau.

**Dépendances** : `ps-core-protocol`, `ps-replay`. Jamais le client.
