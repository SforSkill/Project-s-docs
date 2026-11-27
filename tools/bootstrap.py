#!/usr/bin/env python3
"""Met en place un poste de développement multi-dépôts Project S.

Sous-commandes (lancées depuis n'importe où ; --root vaut par défaut le dossier
parent de ce dépôt Project-s-docs) :

  check            vérifie les prérequis (git, cargo, python, docker, gh)
  clone            clone les dépôts manquants dans --root
                   (--release releases/<x>.toml : au tag de la release ;
                    --private : inclut les dépôts privés, accès requis)
  patch            écrit <root>/.cargo/config.toml : chaque dépendance Git
                   SforSkill pointe vers le clone local (développement simultané)
  unpatch          retire ce fichier (à faire avant de régénérer un Cargo.lock à commiter)
  test             fmt + clippy + tests de chaque dépôt Rust cloné

Le fichier .cargo/config.toml est HORS des dépôts : il n'est jamais versionné.
Ne commitez jamais un Cargo.lock résolu pendant que les patches sont actifs.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    sys.exit("bootstrap.py exige Python 3.11+ (tomllib)")

ORG = "SforSkill"
PUBLIC = [
    "Project-s-protocol",
    "Project-s-netcode",
    "Project-s-simulation",
    "Project-s-engine",
    "Project-s-content",
    "Project-s-server",
    "Project-s",
    "Project-s-docs",
]
PRIVATE = ["Project-s-lab", "Project-s-infra"]
# Ordre de compilation : producteurs d'abord.
RUST = [r for r in PUBLIC + PRIVATE if r not in ("Project-s-docs", "Project-s-infra")]
PATCH_MARK = "# Généré par Project-s-docs/tools/bootstrap.py patch : NE PAS VERSIONNER."


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> int:
    print("$", " ".join(cmd), f"  (dans {cwd})" if cwd else "", flush=True)
    return subprocess.run(cmd, cwd=cwd, check=check).returncode


def default_root() -> Path:
    return Path(__file__).resolve().parents[2]


def cmd_check(_: argparse.Namespace) -> int:
    ok = True
    for tool, required, why in [
        ("git", True, "cloner les dépôts"),
        ("cargo", True, "compiler (la version vient de rust-toolchain.toml de chaque dépôt)"),
        ("rustup", True, "installer la toolchain épinglée"),
        ("gh", False, "PR, releases, dépôts privés"),
        ("docker", False, "image du serveur, Project-s-infra"),
    ]:
        path = shutil.which(tool)
        state = "ok" if path else ("MANQUANT" if required else "absent (facultatif)")
        print(f"{tool:8} {state:22} {why}")
        ok &= bool(path) or not required
    if sys.version_info < (3, 11):
        print("python   trop ancien : 3.11+ requis")
        ok = False
    if sys.platform.startswith("linux"):
        print("Linux : le client Bevy exige libasound2-dev libudev-dev libwayland-dev libxkbcommon-dev")
    return 0 if ok else 1


def release_tags(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    tags = {}
    for comp in data.get("components", {}).values():
        if comp.get("tag"):
            tags[comp["repo"].split("/", 1)[1]] = comp["tag"]
    return tags


def cmd_clone(args: argparse.Namespace) -> int:
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    tags = release_tags(args.release)
    for repo in PUBLIC + (PRIVATE if args.private else []):
        dest = root / repo
        if dest.exists():
            print(f"{repo}: déjà présent")
            continue
        cmd = ["git", "clone", f"https://github.com/{ORG}/{repo}.git", str(dest)]
        if repo in tags:
            cmd[2:2] = ["--branch", tags[repo]]
        elif args.release:
            print(f"{repo}: pas de tag dans la release, branche par défaut")
        run(cmd)
    return 0


def local_crates(root: Path) -> dict[str, dict[str, Path]]:
    """{url du dépôt: {nom de crate: dossier}} pour chaque clone local."""
    found: dict[str, dict[str, Path]] = {}
    for repo in PUBLIC + PRIVATE:
        base = root / repo
        if not (base / "Cargo.toml").is_file():
            continue
        crates = {}
        for manifest in list(base.glob("crates/*/Cargo.toml")) + list(base.glob("tools/*/Cargo.toml")):
            pkg = tomllib.loads(manifest.read_text(encoding="utf-8")).get("package", {})
            if "name" in pkg:
                crates[pkg["name"]] = manifest.parent
        if crates:
            found[f"https://github.com/{ORG}/{repo}"] = crates
    return found


def cmd_patch(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    lines = [PATCH_MARK, "# Retirer avec : python Project-s-docs/tools/bootstrap.py unpatch", ""]
    for url, crates in sorted(local_crates(root).items()):
        lines.append(f'[patch."{url}"]')
        for name, path in sorted(crates.items()):
            lines.append(f'{name} = {{ path = "{path.as_posix()}" }}')
        lines.append("")
    out = root / ".cargo" / "config.toml"
    if out.exists() and PATCH_MARK not in out.read_text(encoding="utf-8"):
        sys.exit(f"{out} existe et n'a pas été généré par ce script : refus de l'écraser")
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"écrit : {out}")
    print("Rappel : ne commitez pas un Cargo.lock résolu avec ces patches (lancez `unpatch` puis `cargo update -w`).")
    return 0


def cmd_unpatch(args: argparse.Namespace) -> int:
    out = Path(args.root).resolve() / ".cargo" / "config.toml"
    if out.exists():
        if PATCH_MARK not in out.read_text(encoding="utf-8"):
            sys.exit(f"{out} n'a pas été généré par ce script : laissé en place")
        out.unlink()
        print(f"supprimé : {out}")
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    failed = []
    for repo in RUST:
        cwd = root / repo
        if not (cwd / "Cargo.toml").is_file():
            continue
        steps = [
            ["cargo", "fmt", "--all", "--", "--check"],
            ["cargo", "clippy", "--workspace", "--all-targets", "--all-features", "--", "-D", "warnings"],
            ["cargo", "test", "--workspace", "--all-features", "--release"],
            [sys.executable, str(Path(__file__).with_name("check_boundaries.py")), "."],
        ]
        if any(run(step, cwd=cwd, check=False) != 0 for step in steps):
            failed.append(repo)
    print("Échecs :", ", ".join(failed) if failed else "aucun")
    return 1 if failed else 0


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(default_root()), help="dossier qui contient les clones")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    clone = sub.add_parser("clone")
    clone.add_argument("--release", help="manifeste releases/<x>.toml")
    clone.add_argument("--private", action="store_true", help="inclut Project-s-lab et Project-s-infra")
    sub.add_parser("patch")
    sub.add_parser("unpatch")
    sub.add_parser("test")
    args = parser.parse_args()
    return {"check": cmd_check, "clone": cmd_clone, "patch": cmd_patch, "unpatch": cmd_unpatch, "test": cmd_test}[
        args.cmd
    ](args)


if __name__ == "__main__":
    sys.exit(main())
