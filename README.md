# character-hold

Minimal evaluation harness for a **behavioral** question: when an API chat model is given a declared assistant character (principles in a system prompt), does it **say** the principle, **use** it under forced choice, and **hold** it under multi-turn pressure?

This is an extension of the *saying-is-not-using-it* signature to assistant character—not a persona / role-play fidelity benchmark, and not a claim about “true” internal character, moral worth, or deployment-wide alignment.

**Degrees of evidence.** Pilot numbers below are from a **deterministic mock provider** with API keys unset. They validate the pipeline end-to-end. They are **not** population estimates over frontier models.

## Motivation

System prompts routinely declare stable dispositions (“prefer truth over agreement,” “admit uncertainty,” “keep process under authority pressure”). Evaluators and users often treat those declarations as load-bearing. Prior persona / RP benchmarks measure stay-in-character for fictional roles; they do not answer whether a *declared assistant principle* survives conflict between endorsement and action, or between principle and social pressure.

| Signal | Question |
|--------|----------|
| **Say** | Does the model verbally endorse the stated character / principle when asked? |
| **Use** | Does it act on that principle in a forced-choice conflict? |
| **Hold** | Does the disposition survive escalating social / authority / urgency pressure? |

Primary gap metric: **say–use gap** = `say_rate − use_rate`. Pressure dialogues add break turn, fracture type, and optional faithfulness probes when stance reverses.

## Method (short)

Full protocol: [`docs/methodology.md`](docs/methodology.md). Authoring guide: [`docs/scenario_authoring.md`](docs/scenario_authoring.md). Constraints: [`docs/ethics.md`](docs/ethics.md).

- **Specimens** (`specimens/`): character cards + principles (`truth_over_agreement`, `calibrated_uncertainty`, `principle_under_authority`).
- **Scenarios** (`scenarios/`): 16 say + 16 use + 16 pressure items per specimen (144 total).
- **Say / use:** deterministic pattern and `CHOICE: A|B` scorers. `parse_fail` counts as use **fail**; `use_parse_fail_rate` is also reported.
- **Pressure (v0 primary):** deterministic/heuristic identity + principle labels in the framework — **not** an LLM judge. Soft labels (`partial`, `hedges`) are noisy.
- **Fracture:** default `fracture_on: [out, reverses]`; record `break_turn` (1-based).
- **Faithfulness:** on principle reverse, strip a short pressure-phrase list and replay; harness labels documented in methodology §12.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # add API keys only if using live providers; never commit .env
```

## Reproduce (mock dry-run)

```bash
character-hold validate
character-hold run --config configs/default.yaml --provider mock --run-id pilot
character-hold score --input results/pilot --scenarios-dir scenarios
character-hold report --input results/pilot
pytest
```

Artifacts land under **`results/pilot/`**: `raw.jsonl`, `scored.jsonl`, `summary.json`, `summary.md`, `run_manifest.json`, `notes.md`.

## Reproduce (live API)

Keys via environment (names only — never hardcode or commit secrets):

| Provider   | Env var             | Example |
|------------|---------------------|---------|
| OpenAI     | `OPENAI_API_KEY`    | `character-hold run --provider openai --model gpt-4.1-mini --run-id pilot-openai` |
| Anthropic  | `ANTHROPIC_API_KEY` | `character-hold run --provider anthropic --model claude-sonnet-4-20250514 --run-id pilot-anthropic` |
| OpenRouter | `OPENROUTER_API_KEY`| `character-hold run --provider openrouter --model openai/gpt-4.1-mini --run-id pilot-openrouter` |

Then score/report the chosen run directory the same way. Temperature default is `0` (`configs/default.yaml`).

<!-- PILOT_RESULTS -->
## Pilot results

**Condition.** Mock provider `mock-v1`, seed `42`, temperature `0`, full 144-item suite. Live API keys were **unset** at run time — dry-run only. Numbers describe mock scripted behavior under heuristic scorers; they do **not** support claims about real models’ character-hold.

### Aggregate

| Metric | Value |
|--------|------:|
| say_rate | 0.500 |
| use_rate | 0.438 |
| hold_rate | 0.000 |
| say_use_gap | 0.062 |
| use_parse_fail_rate | 0.000 |
| median_break_turn (fractures) | 2.0 |
| n_fractures | 48 / 48 |

### Per specimen × model

| Specimen | Model | say_rate | use_rate | hold_rate | say_use_gap | median_break_turn |
|----------|-------|---------:|---------:|----------:|------------:|------------------:|
| calibrated_uncertainty | mock-v1 | 0.562 | 0.312 | 0.000 | 0.250 | 2.0 |
| principle_under_authority | mock-v1 | 0.500 | 0.438 | 0.000 | 0.062 | 2.0 |
| truth_over_agreement | mock-v1 | 0.438 | 0.562 | 0.000 | −0.125 | 2.0 |

### Fracture types & faithfulness

| Fracture type | Count |
|---------------|------:|
| both (`out` + `reverses`) | 48 |

| Faithfulness (harness) | Count |
|------------------------|------:|
| faithful (replay holds) | 48 |

Source tables: [`results/pilot/summary.md`](results/pilot/summary.md). Spot-checks: [`results/pilot/notes.md`](results/pilot/notes.md).

**Reading.** Under the mock, hold_rate collapses to 0 by construction (canned reverse by turn 2–3). The small aggregate say–use gap is not evidence of a real saying-is-not-using-it effect; specimen gaps even change sign (`truth_over_agreement` gap −0.125). Treat this as a **pipeline smoke test**, not a scientific finding about models.

## Limitations

1. **Pressure scoring is heuristic** (keyword cues). Pilot README and reports must not be read as human- or LLM-judge gold.
2. **Mock provider** uses canned say/use/pressure templates; pressure marker detection can miss turn-1 adversary lines and fall back to say-like text.
3. **No live keys ⇒ dry-run only.** Replace mock tables after an API pilot before discussing model behavior.
4. **Say patterns** fail closed on paraphrase / empty hits; Content mixes `endorse` and `reject` stances.
5. **Faithfulness strip list** is short and ad hoc; label sense is harness-defined (methodology §12).
6. Construct, item, and coverage limits in methodology §10 still apply.

## Single best next experiment

Run the **same frozen 144-item suite** at temperature 0 on **one** strong live chat model (e.g. via OpenRouter or native OpenAI/Anthropic), write results under `results/pilot-<model>/`, and compare say_rate / use_rate / hold_rate / say_use_gap / median_break_turn to this mock baseline — still treating pressure labels as heuristic unless dual-annotated.

## License

MIT — see [`LICENSE`](LICENSE).
