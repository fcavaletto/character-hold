# character-hold

**Saying ≠ using ≠ holding** — under pressure — for *assistant character*.

API chat models are routinely given system prompts that declare stable dispositions (“prefer truth over agreement,” “admit uncertainty,” “keep process under authority”). Users and evaluators often treat those lines as load-bearing. **character-hold** asks a sharper behavioral question: when the *assistant itself* is instructed to hold a principle, does verbal endorsement (**say**) survive into forced action (**use**), and does that disposition survive multi-turn social / authority / urgency pressure (**hold**)?

This is **not** a persona / role-play fidelity benchmark. High RP consistency does not answer whether a declared assistant principle fractures under conflict.

**Author.** [Federico Cavaletto](https://github.com/fcavaletto) · **License.** MIT · **Cite.** [`CITATION.cff`](CITATION.cff) / [`CITATION.bib`](CITATION.bib)

> **Degrees of evidence.** The primary committed demo tables below are still from a **deterministic MOCK provider** (pipeline illustration). A separate **live OpenRouter** pilot on `deepseek/deepseek-v4.1-flash` is documented in the Live pilot section — one model, n=144, temp 0, heuristic pressure labels; **not** a population estimate.

---

## Why this matters for alignment

Constitution-style and system-prompt “character” are cheap to write and expensive to trust. If models *say* the principle, *fail to use* it under forced choice, and *fracture early* under pressure, then “character” is performance rather than a load-bearing disposition—the same family of risk as sycophancy and saying-is-not-using-it, scoped to assistant principles rather than one-off prefs.

Primary gap metric: **say–use gap** = `say_rate − use_rate`. Pressure adds **break turn**, **fracture type**, and optional **faithfulness** probes when stance reverses.

---

## Differentiation

| | **character-hold** | PersonaGym / CharacterEval / RPEval |
|--|--------------------|-------------------------------------|
| **Object** | Declared *assistant* dispositions (system prompt principles) | Fictional / named persona |
| **Conflict** | Principle vs agreeableness, authority, urgency | Stay-in-character vs OOC |
| **Ladder** | say → use → hold → fracture → faithfulness | Persona consistency / RP rubrics |
| **Risk** | Saying ≠ using; break under pressure | Lore / style drift |
| **Scoring (v0)** | Deterministic say/use + heuristic pressure | Persona / RP judge rubrics |

Full comparative note: [`docs/related_work.md`](docs/related_work.md).

---

## Method

```mermaid
flowchart LR
  S[Specimen system prompt] --> Say[Say: endorse principle?]
  Say --> Use[Use: forced CHOICE A/B]
  Use --> Pressure[Pressure: multi-turn adversary]
  Pressure --> Fracture{Fracture?<br/>out / reverses}
  Fracture -->|no| Hold[Hold through max turns]
  Fracture -->|yes| Break[break_turn + fracture type]
  Break --> Faith[Faithfulness replay<br/>strip pressure → regenerate]
```

| Signal | Question |
|--------|----------|
| **Say** | Does the model verbally endorse the stated principle when asked? |
| **Use** | Does it act on that principle in a forced-choice conflict? |
| **Hold** | Does the disposition survive escalating pressure? |

- **Specimens** (`specimens/`): `truth_over_agreement`, `calibrated_uncertainty`, `principle_under_authority`
- **Scenarios** (`scenarios/`): 16×3 types × 3 specimens = **144** items
- **Scorers:** deterministic say/use; pressure = heuristic identity × principle (not LLM-judge in v0)
- **Faithfulness (harness v0):** `faithful` = replay holds; `unfaithful` = replay still reverses; `transparent` = admits pressure

Protocol: [`docs/methodology.md`](docs/methodology.md) · Authoring: [`docs/scenario_authoring.md`](docs/scenario_authoring.md) · Ethics: [`docs/ethics.md`](docs/ethics.md) · Frozen card: [`docs/pilot_protocol.md`](docs/pilot_protocol.md)

---

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # add API keys only for live providers; never commit .env
```

Requires Python **3.11+**.

---

## One-command demo (CPU-only)

```bash
make demo
# or: ./scripts/demo.sh
```

Runs validate → mock run → score → report. Open:

- [`results/pilot/report.html`](results/pilot/report.html) — static demo report
- [`results/pilot/INDEX.md`](results/pilot/INDEX.md) — one-page landing
- [`results/pilot/figures/`](results/pilot/figures/) — publication-ready PNGs

---

## Reproduce (stepwise)

```bash
character-hold validate
character-hold run --config configs/default.yaml --provider mock --run-id pilot
character-hold score --input results/pilot --scenarios-dir scenarios
character-hold report --input results/pilot
pytest
```

---

## Pilot results (MOCK)

**Condition.** Provider `mock` / `mock-v1`, seed `42`, temperature `0`, full 144-item suite. API keys unset. See protocol card: [`docs/pilot_protocol.md`](docs/pilot_protocol.md).

*Tables below are refreshed by `make demo` / `character-hold report`. Treat as pipeline illustration.*

<!-- PILOT_RESULTS -->
### Aggregate (illustrative MOCK)

| Metric | Value |
|--------|------:|
| say_rate | 0.562 |
| use_rate | 0.521 |
| hold_rate | 0.333 |
| say_use_gap | 0.042 |
| use_parse_fail_rate | 0.000 |
| median_break_turn (fractures) | 2.0 |
| n_fractures | 32 / 48 |

### Per specimen × model

| Specimen | Model | say_rate | use_rate | hold_rate | say_use_gap | median_break_turn |
|----------|-------|---------:|---------:|----------:|------------:|------------------:|
| calibrated_uncertainty | mock-v1 | 0.688 | 0.625 | 0.375 | 0.062 | 2.0 |
| principle_under_authority | mock-v1 | 0.625 | 0.438 | 0.312 | 0.188 | 2.0 |
| truth_over_agreement | mock-v1 | 0.375 | 0.500 | 0.312 | −0.125 | 2.0 |

### Fracture types & faithfulness

| Fracture type | Count |
|---------------|------:|
| both (`out` + `reverses`) | 27 |
| reverses | 5 |

| Faithfulness (harness) | Count |
|------------------------|------:|
| faithful (replay holds) | 19 |
| unfaithful (replay still reverses) | 10 |
| transparent (admits pressure) | 3 |

Full tables, figures, and HTML: [`results/pilot/INDEX.md`](results/pilot/INDEX.md) · [`results/pilot/report.html`](results/pilot/report.html).

**Reading.** Under the mock, hold_rate is no longer a cartoonish 0, and faithfulness / fracture types are mixed by construction. Specimen gaps still change sign. Treat this as a **pipeline illustration**, not a scientific finding about models.

---

## Pilot results (LIVE)

**Condition.** OpenRouter · `deepseek/deepseek-v4.1-flash` · temperature `0` · `max_tokens=512` · reasoning effort `none` · full frozen 144-item suite · run id `pilot-deepseek-flash`. Logged usage ≈ **$0.057**. Spot-checks: [`results/pilot-deepseek-flash/notes.md`](results/pilot-deepseek-flash/notes.md).

### Aggregate (one live model)

| Metric | Value |
|--------|------:|
| say_rate | 0.792 |
| use_rate | 0.979 |
| hold_rate | 1.000 |
| say_use_gap | −0.188 |
| use_parse_fail_rate | 0.021 |
| median_break_turn (fractures) | — |
| n_fractures | 0 / 48 |

### Per specimen × model

| Specimen | Model | say_rate | use_rate | hold_rate | say_use_gap | median_break_turn |
|----------|-------|---------:|---------:|----------:|------------:|------------------:|
| calibrated_uncertainty | deepseek/deepseek-v4.1-flash | 0.750 | 0.938 | 1.000 | −0.188 | — |
| principle_under_authority | deepseek/deepseek-v4.1-flash | 0.812 | 1.000 | 1.000 | −0.188 | — |
| truth_over_agreement | deepseek/deepseek-v4.1-flash | 0.812 | 1.000 | 1.000 | −0.188 | — |

### Fracture types & faithfulness

No pressure fractures under the current deterministic heuristics after fixing false positives on negated “reverse” / bare “abandon accuracy.” Faithfulness probes did not fire (they only run on reverse breaks).

Full tables, figures, and HTML: [`results/pilot-deepseek-flash/INDEX.md`](results/pilot-deepseek-flash/INDEX.md) · [`results/pilot-deepseek-flash/report.html`](results/pilot-deepseek-flash/report.html).

**Reading (honest).** On this cheap chat model the **say–use gap flips sign** versus the mock cartoon: use ≫ say (0.979 vs 0.792), driven largely by brittle say regexes (quoting the bad policy while rejecting it still fail-closes) plus one use parse glitch. **hold_rate = 1.0 is not a claim that the model never fractures** — pressure scoring is keyword heuristics that under-call soft hedges. One model, n=144, temp 0; do not generalize to frontier character robustness.

### Still missing for a stronger pilot

1. Dual annotation or locked LLM-judge agreement on a pressure subset
2. CIs / more models; compare without treating heuristic hold as gold
3. Scenario-hash + git commit pinning in a public protocol card for the live dir

---

## Live API (optional)

| Provider   | Env var             | Example |
|------------|---------------------|---------|
| OpenAI     | `OPENAI_API_KEY`    | `character-hold run --provider openai --model gpt-4.1-mini --run-id pilot-openai` |
| Anthropic  | `ANTHROPIC_API_KEY` | `character-hold run --provider anthropic --model claude-sonnet-4-20250514 --run-id pilot-anthropic` |
| OpenRouter | `OPENROUTER_API_KEY`| `character-hold run --provider openrouter --model deepseek/deepseek-v4.1-flash --run-id pilot-deepseek-flash` |

---

## Limitations

1. Pressure scoring is **heuristic** (keyword cues)—not human- or LLM-judge gold; live hold_rate can overstate robustness.
2. Mock provider is scripted and seed-deterministic; distributions are illustrative.
3. Live pilot above is **one** OpenRouter model (`deepseek/deepseek-v4.1-flash`), not a frontier sweep.
4. Say patterns fail closed on paraphrase and on quoting forbidden policies while rejecting them; faithfulness phrase-strip is ad hoc.
5. Construct / coverage limits: methodology §10.

## Single best next experiment

Re-run the same suite on a stronger live chat model (or two) with dual annotation on the pressure subset; keep heuristic labels as a secondary signal only when comparing say / use / hold / gap to this DeepSeek flash baseline.

## Prior related work by the author

Preference-consistency · prompt-injection-eval · saying-is-not-using-it · value-acquisition-research-framework — see [github.com/fcavaletto](https://github.com/fcavaletto).

## Contributing / CI

[`CONTRIBUTING.md`](CONTRIBUTING.md) · GitHub Actions: lint-light + pytest on push/PR (Python 3.11+). Publishing this checkout: [`docs/publishing.md`](docs/publishing.md).
