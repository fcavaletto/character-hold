#!/usr/bin/env bash
# One-command mock demo: validate → run → score → report → print artifact paths.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PY="$ROOT/.venv/bin/python"
  CH="$ROOT/.venv/bin/character-hold"
elif command -v character-hold >/dev/null 2>&1; then
  PY="$(command -v python3)"
  CH="$(command -v character-hold)"
else
  echo "ERROR: install the package first: python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'" >&2
  exit 1
fi

echo "==> install check"
"$PY" -c "import character_hold, matplotlib; print('character-hold', character_hold.__version__, '| matplotlib OK')"

echo "==> validate"
"$CH" validate --config configs/default.yaml

echo "==> mock run (CPU-only, deterministic)"
"$CH" run --config configs/default.yaml --provider mock --run-id pilot

echo "==> score"
"$CH" score --input results/pilot --scenarios-dir scenarios

echo "==> report"
"$CH" report --input results/pilot

echo
echo "Demo complete (MOCK provider — not live-model evidence)."
echo "  HTML : $ROOT/results/pilot/report.html"
echo "  MD   : $ROOT/results/pilot/report.md"
echo "  INDEX: $ROOT/results/pilot/INDEX.md"
echo "  Figs : $ROOT/results/pilot/figures/"
