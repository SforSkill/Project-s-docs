# Project-s-docs (contexte agents)

Documentation transversale et outillage commun de Project S. Lire [`SCOPE.md`](SCOPE.md).

- La documentation d'un composant se modifie dans **son** dépôt. Ici, on ne met que des liens.
- La documentation décrit l'état réel :
  - « implémenté », « testé », « validé » et « prévu » sont distincts ;
  - un chiffre vient d'une exécution réelle, avec sa date et son commit.
- `.github/workflows/rust.yml` et `tools/check_boundaries.py` sont des contrats utilisés par tous les dépôts. Toute modification demande :
  - un nouveau tag ;
  - une entrée au changelog ;
  - une PR dans chaque dépôt qui l'adopte.

  Ne jamais déplacer un tag existant.
- Python : bibliothèque standard seulement, fins de ligne `\n`.
- Contrat entre dépôts modifié : mettre à jour [API_CONTRACTS.md](API_CONTRACTS.md), [COMPATIBILITY_MATRIX.md](COMPATIBILITY_MATRIX.md) et le manifeste `releases/` dans la même série de PR.

Vérification : `python tools/check_links.py && python -m py_compile tools/*.py`.
