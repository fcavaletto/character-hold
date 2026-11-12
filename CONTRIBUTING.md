# Contributing

Thanks for interest in **character-hold**. Keep changes small, readable, and honest about evidence.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make validate && make test
```

## Workflow

1. Prefer extending existing modules (`schema`, `scoring`, `analyze`) over new layers.
2. Scenario / specimen YAML must validate via `character-hold validate`.
3. Do not commit `.env`, API keys, or live-run secrets.
4. Mock results are illustrative — label them **MOCK** in writeups; never present as frontier-model findings.
5. Pressure scoring is heuristic unless you add a documented judge with agreement stats.

## Checks before PR

```bash
make lint-light
make test
./scripts/demo.sh   # optional; regenerates results/pilot/
```

## Docs to keep aligned

- Faithfulness label sense: harness = methodology §12 = README footnote
- Pilot protocol card: `docs/pilot_protocol.md`
- Related benchmarks: `docs/related_work.md`
