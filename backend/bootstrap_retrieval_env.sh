#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${1:-$ROOT_DIR/venv-retrieval}"

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
PYTHONNOUSERSITE=1 "$VENV_DIR/bin/python" -m pip install -r "$ROOT_DIR/backend/requirements-retrieval.txt"

printf '\nRetrieval environment ready at %s\n' "$VENV_DIR"
printf 'Activate with: source "%s/bin/activate"\n' "$VENV_DIR"
