#!/usr/bin/env python3
"""Initialize a virtual-actor iteration dossier from templates."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import sys

REQUIRED_FILES = [
    "scope.md",
    "design-delta.md",
    "implementation-notes.md",
    "traceability.md",
]


def render_template(content: str, version: str) -> str:
    return content.replace("{{VERSION}}", version).replace("{{DATE}}", date.today().isoformat())


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a virtual-actor iteration dossier")
    parser.add_argument("version", help="Version folder name, e.g. v0.4.0")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1], type=Path)
    parser.add_argument("--template-root", type=Path, help="Optional template directory override")
    parser.add_argument("--force", action="store_true", help="Overwrite existing dossier files")
    parser.add_argument("--set-current", action="store_true", help="Point docs/iterations/current.txt to this version")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    template_dir = (
        args.template_root.resolve()
        if args.template_root
        else repo_root / "docs" / "iterations" / "_template"
    )
    target_dir = repo_root / "docs" / "iterations" / args.version

    if not template_dir.exists():
        print(f"ERROR: template dir not found: {template_dir}", file=sys.stderr)
        return 2

    target_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    skipped: list[Path] = []
    for name in REQUIRED_FILES:
        src = template_dir / name
        dst = target_dir / name
        if not src.exists():
            print(f"ERROR: missing template file: {src}", file=sys.stderr)
            return 2
        if dst.exists() and not args.force:
            skipped.append(dst)
            continue
        dst.write_text(render_template(src.read_text(encoding="utf-8"), args.version), encoding="utf-8")
        created.append(dst)

    if args.set_current:
        current_path = repo_root / "docs" / "iterations" / "current.txt"
        current_path.write_text(f"{args.version}\n", encoding="utf-8")
        created.append(current_path)

    print(f"Initialized iteration dossier for {args.version}")
    for path in created:
        print(f"  created: {path.relative_to(repo_root)}")
    for path in skipped:
        print(f"  skipped: {path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
