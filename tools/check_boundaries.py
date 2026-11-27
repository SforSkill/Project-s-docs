#!/usr/bin/env python3
"""Vérifie les frontières de dépendances d'un dépôt Rust de Project S.

Lit `boundaries.toml` à la racine du dépôt et le graphe résolu par
`cargo metadata --locked`. Échoue (code 1) si :

- une crate du workspace dépend, même transitivement, d'un paquet interdit
  (`forbid`, motifs glob) ; seules les dépendances normales et de build comptent,
  les dépendances de dev (tests) sont libres ;
- une crate dépend directement d'une crate `ps-*` absente de sa liste `internal`
  (quand la règle en définit une) ;
- le graphe des crates `ps-*` contient un cycle.

Format de `boundaries.toml` :

    [rules."*"]                 # s'applique à toutes les crates du workspace
    forbid = ["bevy*", "sqlx*"]
    internal = []               # facultatif : dépendances ps-* directes permises

    [rules."ps-server"]         # complète "*" pour une crate
    internal = ["ps-sim"]       # remplace la liste internal de "*"
    forbid = ["tokio*"]         # s'ajoute à la liste forbid de "*"

Usage : python check_boundaries.py [CHEMIN_DU_DÉPÔT]
"""

from __future__ import annotations

import fnmatch
import json
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    sys.exit("check_boundaries.py exige Python 3.11+ (tomllib)")

INTERNAL_PREFIX = "ps-"
CHECKED_KINDS = {None, "build"}  # None = dépendance normale


def load_rules(root: Path) -> dict:
    path = root / "boundaries.toml"
    if not path.is_file():
        sys.exit(f"{path} introuvable : chaque dépôt Rust déclare ses frontières")
    return tomllib.loads(path.read_text(encoding="utf-8")).get("rules", {})


def metadata(root: Path) -> dict:
    out = subprocess.run(
        ["cargo", "metadata", "--format-version", "1", "--locked", "--all-features"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout
    return json.loads(out)


def rule_for(rules: dict, crate: str) -> tuple[list[str], list[str] | None]:
    base = rules.get("*", {})
    own = rules.get(crate, {})
    forbid = list(base.get("forbid", [])) + list(own.get("forbid", []))
    internal = own.get("internal", base.get("internal"))
    return forbid, internal


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    rules = load_rules(root)
    meta = metadata(root)

    names = {p["id"]: p["name"] for p in meta["packages"]}
    nodes = {n["id"]: n for n in meta["resolve"]["nodes"]}

    def direct(pkg_id: str) -> list[str]:
        return [
            d["pkg"]
            for d in nodes[pkg_id]["deps"]
            if any(k["kind"] in CHECKED_KINDS for k in d["dep_kinds"])
        ]

    def closure(pkg_id: str) -> dict[str, list[str]]:
        """Paquets atteignables -> chemin depuis pkg_id (pour le message d'erreur)."""
        seen: dict[str, list[str]] = {}
        stack = [(d, [names[pkg_id], names[d]]) for d in direct(pkg_id)]
        while stack:
            cur, path = stack.pop()
            if cur in seen:
                continue
            seen[cur] = path
            stack.extend((d, path + [names[d]]) for d in direct(cur) if d not in seen)
        return seen

    errors: list[str] = []
    members = meta["workspace_members"]
    for member in members:
        crate = names[member]
        forbid, internal = rule_for(rules, crate)
        for dep, path in closure(member).items():
            dep_name = names[dep]
            for pattern in forbid:
                if fnmatch.fnmatchcase(dep_name, pattern):
                    errors.append(f"{crate}: dépendance interdite {dep_name!r} ({pattern}) via {' -> '.join(path)}")
                    break
        if internal is not None:
            for dep in direct(member):
                dep_name = names[dep]
                if dep_name.startswith(INTERNAL_PREFIX) and dep_name not in internal:
                    errors.append(f"{crate}: dépend directement de {dep_name!r}, absent de internal = {internal}")

    # Cycles entre crates ps-* (dépendances normales et de build).
    internal_ids = [i for i in nodes if names[i].startswith(INTERNAL_PREFIX)]
    state: dict[str, int] = {}

    def visit(pkg_id: str, stack: list[str]) -> None:
        state[pkg_id] = 1
        for dep in direct(pkg_id):
            if not names[dep].startswith(INTERNAL_PREFIX):
                continue
            if state.get(dep) == 1:
                cycle = stack[stack.index(dep):] + [dep]
                errors.append("cycle : " + " -> ".join(names[c] for c in cycle))
            elif dep not in state:
                visit(dep, stack + [dep])
        state[pkg_id] = 2

    for pkg_id in internal_ids:
        if pkg_id not in state:
            visit(pkg_id, [pkg_id])

    if errors:
        print("Frontières violées :", file=sys.stderr)
        for e in sorted(set(errors)):
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"Frontières respectées ({len(members)} crates, {len(internal_ids)} crates ps-* dans le graphe).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
