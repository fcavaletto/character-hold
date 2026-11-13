# character-hold

**Saying ≠ using ≠ holding** — under pressure — for *assistant character*.

API chat models are routinely given system prompts that declare stable dispositions (“prefer truth over agreement,” “admit uncertainty,” “keep process under authority”). Users and evaluators often treat those lines as load-bearing. **character-hold** asks a sharper behavioral question: when the *assistant itself* is instructed to hold a principle, does verbal endorsement (**say**) survive into forced action (**use**), and does that disposition survive multi-turn social / authority / urgency pressure (**hold**)?

This is **not** a persona / role-play fidelity benchmark. High RP consistency does not answer whether a declared assistant principle fractures under conflict.

**Author.** [Federico Cavaletto](https://github.com/fcavaletto) · **License.** MIT · **Cite.** [`CITATION.cff`](CITATION.cff) / [`CITATION.bib`](CITATION.bib)

> **Degrees of evidence.** The primary committed demo tables below are still from a **deterministic MOCK provider** (pipeline illustration). Live OpenRouter pilots (`deepseek/deepseek-v4.1-flash`, `anthropic/claude-haiku-4.5`) are single-seed, n=144, temp 0, with **heuristic** pressure labels as primary and optional dual-annotation as secondary — **not** population estimates. One-pager: [`results/COMPARISON.md`](results/COMPARISON.md).

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
- **Scorers:** deterministic say/use; pressure = heuristic identity × principle (primary). Optional dual-annotation LLM judge is **secondary** only ([`docs/dual_annotation.md`](docs/dual_annotation.md)).
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
| say_rate | 0.521 |
| use_rate | 0.521 |
| hold_rate | 0.333 |
| say_use_gap | 0.000 |
| use_parse_fail_rate | 0.000 |
| median_break_turn (fractures) | 2.0 |
| n_fractures | 32 / 48 |

### Per specimen × model

| Specimen | Model | say_rate | use_rate | hold_rate | say_use_gap | median_break_turn |
|----------|-------|---------:|---------:|----------:|------------:|------------------:|
| calibrated_uncertainty | mock-v1 | 0.625 | 0.625 | 0.375 | 0.000 | 2.0 |
| principle_under_authority | mock-v1 | 0.562 | 0.438 | 0.312 | 0.125 | 2.0 |
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

**Reading.** Under the mock, hold_rate is no longer a cartoonish 0, and faithfulness / fracture types are mixed by construction. Specimen gaps still change sign. Say scoring fail-closes when pass and fail patterns both match, which moves two mock say items from pass to fail versus an earlier table (say_rate 0.562 → 0.521). Treat this as a **pipeline illustration**, not a scientific finding about models.

---

## Pilot results (LIVE)

**Condition.** OpenRouter · `deepseek/deepseek-v4.1-flash` (upstream id matched) · temperature `0` · `max_tokens=512` · reasoning effort `none` · full frozen 144-item suite · run id `pilot-deepseek-flash`. Provider-reported cost **$0.057** (359 calls, 283,902 tokens). Reasoning was turned off because the model's default reasoning spent the 512-token budget and often returned empty visible text; that first pass was discarded. Spot-checks: [`results/pilot-deepseek-flash/notes.md`](results/pilot-deepseek-flash/notes.md).

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

**Reading (honest).** On this one cheap chat model the say–use gap is negative (use 0.979, say 0.792): the three specimen gaps are tied at −0.188, and `calibrated_uncertainty` is the only cell with a use miss. Much of the say miss rate is the scorer fail-closing when a correct refusal quotes the bad policy. Every use item's correct key is A, and 47/48 replies were the line `CHOICE: A`, so use_rate does not separate principle-following from an A preference. **hold_rate = 1.0 is not evidence the model never yields** — it means the keyword heuristic, after ignoring negated “reverse” / bare “abandon accuracy,” found no `out` or `reverses` label. One model, n=144, temperature 0. Do not treat this as a frontier alignment result.

### Stronger live arm — Haiku 4.5

**Condition.** OpenRouter · **`anthropic/claude-haiku-4.5`** (upstream id matched) · temperature `0` · `max_tokens=512` · full frozen 144-item suite · run id `pilot-haiku-4.5`. Provider-reported cost **~$0.619** (359 calls). Spot-checks: [`results/pilot-haiku-4.5/notes.md`](results/pilot-haiku-4.5/notes.md).

| Metric | DeepSeek flash | Haiku 4.5 |
|--------|---------------:|----------:|
| say_rate | 0.792 | 0.896 |
| use_rate | 0.979 | 1.000 |
| hold_rate | 1.000 | 1.000 |
| say_use_gap | −0.188 | −0.104 |
| n_fractures | 0 / 48 | 0 / 48 |
| median_break_turn | — | — |
| cost (USD) | ~0.057 | ~0.619 |

Haiku shows higher say and a smaller-magnitude negative gap; use remains saturated. Generation-time logging briefly marked one false fracture (`doesn't go along` as OOC); offline rescore cleared it (same honesty bar as the DeepSeek negation fix). **All use keys remain A** — Haiku’s use_rate=1.0 is also not clean principle-use evidence. Full report: [`results/pilot-haiku-4.5/INDEX.md`](results/pilot-haiku-4.5/INDEX.md).

### Live comparison (MOCK vs two OpenRouter arms)

| Arm | say | use | hold | gap | fractures | cost |
|-----|----:|----:|-----:|----:|----------:|-----:|
| MOCK `mock-v1` | 0.521 | 0.521 | 0.333 | 0.000 | 32 / 48 | — |
| `deepseek/deepseek-v4.1-flash` | 0.792 | 0.979 | 1.000 | −0.188 | 0 / 48 | ~$0.057 |
| `anthropic/claude-haiku-4.5` | 0.896 | 1.000 | 1.000 | −0.104 | 0 / 48 | ~$0.619 |

Grouped bars: [`results/pilot-haiku-4.5/figures/model_comparison_bars.png`](results/pilot-haiku-4.5/figures/model_comparison_bars.png) · One-pager: [`results/COMPARISON.md`](results/COMPARISON.md).

### Dual annotation (secondary LLM judge)

Protocol: [`docs/dual_annotation.md`](docs/dual_annotation.md). Stratified **n=24** pressure dialogues (8/specimen, seed 0) from DeepSeek; same item ids on Haiku. Primary = heuristic; secondary = cross-family OpenRouter judge. **Does not replace** published hold/say/use.

| Subject | Judge (secondary) | Fracture match / κ | Identity match / κ | Principle match / κ | Missed fractures (sec. yes, prim. no) |
|---------|-------------------|-------------------:|-------------------:|--------------------:|--------------------------------------:|
| DeepSeek flash | Haiku 4.5 | 1.00 / 1.00* | 0.00 / 0.00 | 0.71 / 0.00 | **0 / 24** |
| Haiku 4.5 | DeepSeek flash | 1.00 / 1.00* | 0.00 / 0.00 | 0.67 / 0.00 | **0 / 24** |

\*Fracture κ is **degenerate** (both sides always “no fracture”). Identity disagreement is systematic: heuristic defaults to `partial`, judges prefer `in_character` on clear refusals. Principle: judges under-call `hedges`. Spot-checks: [`results/pilot-deepseek-flash/dual_annotation/notes.md`](results/pilot-deepseek-flash/dual_annotation/notes.md), [`results/pilot-haiku-4.5/dual_annotation/notes.md`](results/pilot-haiku-4.5/dual_annotation/notes.md).

**Reading.** The secondary judges did **not** surface fractures the heuristic missed on this subset — so hold=1.0 skepticism is not empirically confirmed here — but label granularity disagreements show the primary scorer is coarse, and circularity/n/seed limits remain.

### Still open

1. Human dual-coding (or locked larger judge panel) beyond n=24
2. CIs / more models / decoding seeds; use items with mixed correct keys
3. Scenario-hash + git commit pinning in a public protocol card for live dirs

---

## Live API (optional)

| Provider   | Env var             | Example |
|------------|---------------------|---------|
| OpenAI     | `OPENAI_API_KEY`    | `character-hold run --provider openai --model gpt-4.1-mini --run-id pilot-openai` |
| Anthropic  | `ANTHROPIC_API_KEY` | `character-hold run --provider anthropic --model claude-sonnet-4-20250514 --run-id pilot-anthropic` |
| OpenRouter | `OPENROUTER_API_KEY`| `character-hold run --provider openrouter --model anthropic/claude-haiku-4.5 --run-id pilot-haiku-4.5` |

```bash
# Stronger comparison arm (documented model id)
character-hold run --config configs/default.yaml --provider openrouter \
  --model anthropic/claude-haiku-4.5 --run-id pilot-haiku-4.5

# Dual-annotate DeepSeek pressure subset (Haiku judge = secondary)
character-hold annotate-pressure --input results/pilot-deepseek-flash \
  --judge-provider openrouter --judge-model anthropic/claude-haiku-4.5 \
  --sample 24 --seed 0 --output results/pilot-deepseek-flash/dual_annotation/
```

---

## Limitations

1. Pressure scoring is **heuristic** (keyword cues)—not human- or LLM-judge gold; live hold_rate can overstate robustness.
2. Mock provider is scripted and seed-deterministic; distributions are illustrative.
3. Live pilots are **two** mid/cheap OpenRouter models (DeepSeek flash + Haiku 4.5), not a frontier sweep; n=144, temp 0, one seed.
4. Every frozen use item’s `correct_choice` is **A** — high use_rate ≠ clean principle-use evidence.
5. Dual-annotation LLM judges are secondary, small-n, and circularity-prone; fracture κ can be degenerate when both sides always say “no.”
6. Say patterns fail closed on paraphrase and on quoting forbidden policies while rejecting them; faithfulness phrase-strip is ad hoc.
7. Construct / coverage limits: methodology §10.

## Single best next experiment

Human-label the same 24 pressure dialogues (or expand the stratified set), and add use items with mixed A/B correct keys so say–use gaps are interpretable.

## Prior related work by the author

Preference-consistency · prompt-injection-eval · saying-is-not-using-it · value-acquisition-research-framework — see [github.com/fcavaletto](https://github.com/fcavaletto).

## Contributing / CI

[`CONTRIBUTING.md`](CONTRIBUTING.md) · GitHub Actions: lint-light + pytest on push/PR (Python 3.11+). Publishing this checkout: [`docs/publishing.md`](docs/publishing.md).
