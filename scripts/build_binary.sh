#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller
pyinstaller --onefile --name autohack main.py
sha256sum dist/autohack > dist/autohack.sha256

echo "Built dist/autohack and dist/autohack.sha256"
