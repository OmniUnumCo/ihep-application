#!/usr/bin/env bash
set -euo pipefail
ROOT="$(pwd)"
IHEP_DIR="$ROOT/ihep"
DRY_RUN=true
if [[ "${1:-}" == "--apply" ]]; then
  DRY_RUN=false
fi
if [[ ! -d "$IHEP_DIR" ]]; then
  echo "Error: $IHEP_DIR not found."
  exit 1
fi
EXCLUDES=( --exclude 'ihep' --exclude '.git' --exclude '.env.local' --exclude 'node_modules' --exclude '*.venv' )
RSYNC_COMMON=( -av "${EXCLUDES[@]}" )
if $DRY_RUN; then
  rsync --dry-run "${RSYNC_COMMON[@]}" ./ "$IHEP_DIR"/
  echo
  echo "Dry-run complete. Rerun with --apply to perform the merge and run scans."
  exit 0
fi
rsync "${RSYNC_COMMON[@]}" ./ "$IHEP_DIR"/
cd "$IHEP_DIR"
if [[ -f package.json ]]; then
  if command -v npm >/dev/null 2>&1; then
    npm ci --silent || true
    if npm run -s lint >/dev/null 2>&1; then
      npm run lint || true
    fi
    if npm test --silent >/dev/null 2>&1; then
      npm test || true
    fi
  else
    echo "npm not found; skipping JS/TS checks."
  fi
fi
if [[ -f tsconfig.json ]] && command -v npx >/dev/null 2>&1; then
  npx -y tsc --noEmit || true
fi
if [[ -f requirements.txt ]] || [[ -f pyproject.toml ]]; then
  PY_VENV=".venv_ihep_merge"
  python3 -m venv "$PY_VENV"
  source "$PY_VENV/bin/activate"
  pip install --upgrade pip >/dev/null
  if [[ -f requirements.txt ]]; then
    pip install -r requirements.txt >/dev/null || true
  fi
  pip install flake8 mypy >/dev/null 2>&1 || true
  if command -v flake8 >/dev/null 2>&1; then
    flake8 . || true
  fi
  if command -v mypy >/dev/null 2>&1; then
    mypy . || true
  fi
  deactivate
fi
if [[ -f go.mod ]]; then
  if command -v go >/dev/null 2>&1; then
    go vet ./... || true
  else
    echo "go not found; skipping go vet."
  fi
fi
grep -RIn --exclude-dir={.git,node_modules} -e '<<<<<<<' -e '>>>>>>>' -e '=======' -e 'TODO' -e 'FIXME' . || true

echo
echo "Scan finished."