.PHONY: demo validate test lint-light install

PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install -U pip
	$(BIN)/pip install -e ".[dev]"

validate:
	$(BIN)/character-hold validate --config configs/default.yaml

test:
	$(BIN)/pytest -q

lint-light:
	$(BIN)/python -m compileall -q src
	$(BIN)/python -c "import yaml, pathlib; [yaml.safe_load(p.read_text()) for p in list(pathlib.Path('specimens').glob('*.yaml'))+list(pathlib.Path('scenarios').rglob('*.yaml'))+list(pathlib.Path('configs').glob('*.yaml'))]"

demo:
	./scripts/demo.sh
