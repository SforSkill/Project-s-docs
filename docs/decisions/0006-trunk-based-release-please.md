# ADR 0006 — Trunk-based et release-please

- **Statut** : accepté

## Contexte

Le dépôt a démarré sans règle : pushs directs, tags et releases faits à la main. Il faut un flux qui protège la branche livrée, impose une revue et produise versions, changelog et archives sans manipulation manuelle.

Deux modèles ont été comparés : Git Flow (`dev` + `main`, promotion puis report après chaque release) et trunk-based (une seule branche `main`).

## Décision

Trunk-based : branches courtes vers `main` par PR relue, CI verte et titre Conventional Commits, fusion en squash. release-please maintient une PR de release qui cumule les changements ; la fusionner crée le tag, la pre-release et déclenche la construction des archives. Une GitHub App de l'org fournit le jeton de release-please. Détail : [`docs/git-workflow.md`](../git-workflow.md).

## Conséquences

- Moins de PR et de bots que Git Flow, pas de branche à resynchroniser ; c'est le modèle pour lequel release-please est conçu et celui des grands projets (Google, Kubernetes, Rust).
- `main` doit rester livrable : une fonctionnalité inachevée reste dans sa branche ou derrière une option.
- Corriger une ancienne version demandera une branche `release/x.y` créée à ce moment-là.
- Versions et changelog ne se modifient plus à la main.
