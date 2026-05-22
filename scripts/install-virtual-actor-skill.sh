#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
SRC="$REPO_ROOT/tools/skills/virtual-actor-iteration-control"
DEST="$CODEX_HOME/skills/virtual-actor-iteration-control"

if [[ ! -f "$SRC/SKILL.md" ]]; then
  echo "ERROR: skill source not found: $SRC/SKILL.md" >&2
  exit 2
fi

mkdir -p "$DEST"
cp "$SRC/SKILL.md" "$DEST/SKILL.md"

echo "Installed virtual-actor-iteration-control skill to $DEST"
echo "Restart Codex to load the new skill."
