#!/usr/bin/env python3
"""Vérifie que chaque lien Markdown relatif de ce dépôt pointe vers un fichier existant.

Les liens absolus (http, https, mailto) et les ancres seules ne sont pas vérifiés.
Usage : python tools/check_links.py [RACINE]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SKIP = ("http://", "https://", "mailto:", "#")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    broken = []
    files = [p for p in root.rglob("*.md") if ".git" not in p.parts]
    for md in files:
        text = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
        for target in LINK.findall(text):
            if target.startswith(SKIP):
                continue
            path = target.split("#", 1)[0]
            if path and not (md.parent / path).exists():
                broken.append(f"{md.relative_to(root)}: {target}")
    for b in broken:
        print("lien cassé :", b, file=sys.stderr)
    print(f"{len(files)} fichiers Markdown, {len(broken)} lien(s) cassé(s)")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
