# ...existing code...
#!/usr/bin/env bash
set -euo pipefail

ENVFILE="ihep/.env.local"
if [[ ! -f "$ENVFILE" ]]; then
  echo "Missing $ENVFILE" >&2
  exit 1
fi

LINE=$(grep -m1 '^GITHUB_PAT=' "$ENVFILE" || true)
if [[ -z "$LINE" ]]; then
  echo "GITHUB_PAT not found in $ENVFILE" >&2
  exit 1
fi

VAL=${LINE#GITHUB_PAT=}
# strip surrounding quotes if present
VAL=${VAL#\"}; VAL=${VAL%\"}
VAL=${VAL#\'}; VAL=${VAL%\'} 

REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
SECRET_NAME="${2:-CODEQL_TOKEN}"

echo "Setting secret $SECRET_NAME in $REPO"
gh secret set "$SECRET_NAME" --repo "$REPO" --body "$VAL"
echo "Secret set."
# ...existing code...
