#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"
VENV_PY="${VENV_DIR}/bin/python"

# If the venv directory exists but is incomplete/corrupt, recreate it.
if [ -d "${VENV_DIR}" ] && [ ! -x "${VENV_PY}" ]; then
  echo "Found ${VENV_DIR} but ${VENV_PY} is missing. Recreating venv..."
  rm -rf "${VENV_DIR}"
fi

# Create venv if missing
if [ ! -x "${VENV_PY}" ]; then
  python -m venv "${VENV_DIR}"
fi

# Always use the venv interpreter explicitly
"${VENV_PY}" -m pip install --upgrade pip setuptools wheel

if [ -f "requirements.txt" ]; then
  "${VENV_PY}" -m pip install -r requirements.txt
elif [ -f "pyproject.toml" ]; then
  "${VENV_PY}" -m pip install -e ".[dev]"
fi
