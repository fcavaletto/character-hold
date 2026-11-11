# character-hold

Minimal evaluation framework for character-hold AI-safety research.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # add API keys only if using live providers
```

## Run (mock dry-run)

```bash
character-hold validate
character-hold run --config configs/default.yaml --provider mock
character-hold score --input results/<run_dir>
character-hold report --input results/<run_dir>
```

Live providers (keys via env; never hardcode):

```bash
character-hold run --provider openai --model gpt-4.1-mini
character-hold run --provider anthropic --model claude-sonnet-4-20250514
character-hold run --provider openrouter --model openai/gpt-4.1-mini
```

Tests:

```bash
pytest
```

Specimens/scenarios are loaded from `specimens/` and `scenarios/` (or paths in config). Fixture copies live under `tests/fixtures/` for unit/e2e tests.

<!-- PILOT_RESULTS -->
## Pilot results

_Placeholder — a later agent will fill pilot numbers here._
