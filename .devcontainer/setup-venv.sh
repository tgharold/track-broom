#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=".venv"

if [ ! -d "${VENV_DIR}" ]; then
  python -m venv "${VENV_DIR}"
fi

source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip setuptools wheel

if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
elif [ -f "pyproject.toml" ]; then
  pip install -e .
fi
