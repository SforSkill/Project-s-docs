# Changelog

## 0.1.0 (2026-11-27)

### Features

* documentation transversale de l'écosystème multi-dépôts : architecture, audit du monolithe `b586317`, carte des dépôts, graphe des dépendances, contrats d'API et d'événements, versionnement, compatibilité, migration, développement local, déploiement, frontières de sécurité, ADR 0001 à 0007, composants prévus
* workflow CI réutilisable `rust.yml` (fmt, clippy, doc, tests Linux/Windows, cargo-deny, frontières)
* `tools/check_boundaries.py` (frontières transitives et cycles), `tools/bootstrap.py` (clonage, `[patch]` locaux, tests), `tools/check_links.py`
* manifeste de release globale `releases/2026.11-alpha.1.toml`
