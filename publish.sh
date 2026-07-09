#!/usr/bin/env bash
# Publish cargoeffe-mcp to PyPI.
#
# Usage:
#   ./publish.sh              # auto-bump patch (0.2.0 -> 0.2.1), build, upload
#   ./publish.sh 0.3.0        # set explicit version, build, upload
#
# PyPI token: set once via env var, or the script prompts for it.
#   export PYPI_TOKEN=pypi-xxxx   (add to ~/.zshrc to persist)

set -euo pipefail
cd "$(dirname "$0")"

PYPROJECT="pyproject.toml"
INIT="src/cargoeffe_mcp/__init__.py"

# ── 1. Determine new version ──
CURRENT=$(grep -m1 '^version' "$PYPROJECT" | sed -E 's/.*"([^"]+)".*/\1/')

if [ $# -ge 1 ]; then
  NEW="$1"
else
  # auto-bump patch: 0.2.0 -> 0.2.1
  IFS='.' read -r MAJ MIN PAT <<< "$CURRENT"
  NEW="$MAJ.$MIN.$((PAT + 1))"
fi

echo "→ Version: $CURRENT → $NEW"

# ── 2. Update version in both files ──
sed -i '' "s/version = \"$CURRENT\"/version = \"$NEW\"/" "$PYPROJECT"
sed -i '' "s/__version__ = \"$CURRENT\"/__version__ = \"$NEW\"/" "$INIT"

# ── 3. Build ──
echo "→ Building..."
rm -rf dist
python -m build >/dev/null 2>&1
echo "  Built: $(ls dist/)"

# ── 4. Upload ──
TOKEN="${PYPI_TOKEN:-}"
if [ -z "$TOKEN" ]; then
  echo -n "PyPI token (pypi-...): "
  read -rs TOKEN
  echo ""
fi

echo "→ Uploading to PyPI..."
twine upload dist/* -u __token__ -p "$TOKEN"

# ── 5. Commit version bump ──
git add "$PYPROJECT" "$INIT"
git commit -m "Release $NEW" >/dev/null 2>&1 || true
git push >/dev/null 2>&1 || echo "  (git push skipped — push manually if needed)"

echo ""
echo "✅ Published cargoeffe-mcp $NEW"
echo "   Users get it via: uvx cargoeffe-mcp   (or  pip install -U cargoeffe-mcp)"
