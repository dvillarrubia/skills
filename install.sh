#!/usr/bin/env bash
# Instala una skill de este repo en Claude Code y/o Google Antigravity (macOS / Linux / Git Bash).
#
# Uso:
#   curl -fsSL https://raw.githubusercontent.com/dvillarrubia/skills/main/install.sh | bash -s -- <skill> [claude|antigravity|all]
#
# Ejemplo:
#   curl -fsSL https://raw.githubusercontent.com/dvillarrubia/skills/main/install.sh | bash -s -- content-prioritization-ai-search all
#
# Si la skill ya estaba instalada, se sustituye por la última versión.
set -euo pipefail

REPO="dvillarrubia/skills"
BRANCH="main"
SKILL="${1:-}"
TARGET="${2:-all}"

if [ -z "$SKILL" ]; then
  echo "Uso: install.sh <skill> [claude|antigravity|all]" >&2
  echo "Skills disponibles: https://github.com/$REPO#catálogo" >&2
  exit 1
fi

case "$TARGET" in
  claude)      DESTS=("$HOME/.claude/skills") ;;
  antigravity) DESTS=("$HOME/.gemini/antigravity-cli/skills" "$HOME/.gemini/config/skills") ;;
  all)         DESTS=("$HOME/.claude/skills" "$HOME/.gemini/antigravity-cli/skills" "$HOME/.gemini/config/skills") ;;
  *) echo "Destino no válido: '$TARGET'. Usa claude, antigravity o all." >&2; exit 1 ;;
esac

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if [ -n "${SKILLS_SRC:-}" ]; then
  SRC_ROOT="$SKILLS_SRC"   # para pruebas locales
else
  echo "Descargando $REPO..."
  curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/heads/$BRANCH" | tar -xz -C "$TMP"
  SRC_ROOT="$TMP/skills-$BRANCH"
fi

SRC="$SRC_ROOT/$SKILL"
if [ ! -f "$SRC/SKILL.md" ]; then
  echo "No existe la skill '$SKILL' en el repo." >&2
  echo "Disponibles:" >&2
  for d in "$SRC_ROOT"/*/; do [ -f "$d/SKILL.md" ] && echo "  - $(basename "$d")" >&2; done
  exit 1
fi

for DEST in "${DESTS[@]}"; do
  mkdir -p "$DEST"
  rm -rf "${DEST:?}/$SKILL"
  cp -R "$SRC" "$DEST/$SKILL"
  echo "Instalada en $DEST/$SKILL"
done

if [ -f "$SRC/requirements.txt" ]; then
  echo
  echo "Esta skill usa Python. Instala sus dependencias con:"
  echo "  python3 -m pip install -r \"${DESTS[0]}/$SKILL/requirements.txt\""
fi

echo
echo "Listo. Reinicia Claude Code / Antigravity para que detecte la skill."
