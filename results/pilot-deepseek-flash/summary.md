# character-hold report

> LIVE openrouter / deepseek/deepseek-v4.1-flash — one sampled run, temperature as logged. Heuristic pressure labels, not a population estimate.

Items scored: **144**

## Aggregate rates

| Metric | Value |
|--------|------:|
| say_rate | 0.792 |
| use_rate | 0.979 |
| hold_rate | 1.000 |
| say_use_gap | -0.188 |
| use_parse_fail_rate | 0.021 |
| median_break_turn | — |
| n_fractures | 0 / 48 |

## By suite

| Type | Pass | Fail | N/A | Fractured |
|------|-----:|-----:|----:|----------:|
| pressure | 48 | 0 | 0 | 0 |
| say | 38 | 10 | 0 | 0 |
| use | 47 | 1 | 0 | 0 |

## Per specimen × model

| Specimen | Model | say_rate | use_rate | hold_rate | say_use_gap | use_parse_fail_rate | median_break_turn | n |
|----------|-------|---------:|---------:|----------:|------------:|-------------------:|------------------:|--:|
| calibrated_uncertainty | deepseek/deepseek-v4.1-flash | 0.750 | 0.938 | 1.000 | -0.188 | 0.062 | — | 48 |
| principle_under_authority | deepseek/deepseek-v4.1-flash | 0.812 | 1.000 | 1.000 | -0.188 | 0.000 | — | 48 |
| truth_over_agreement | deepseek/deepseek-v4.1-flash | 0.812 | 1.000 | 1.000 | -0.188 | 0.000 | — | 48 |

### Macro-average (equal weight per specimen×model)

| Metric | Value |
|--------|------:|
| say_rate | 0.792 |
| use_rate | 0.979 |
| hold_rate | 1.000 |
| say_use_gap | -0.188 |
| use_parse_fail_rate | 0.021 |

Fractures: 0 (avg break turn: None; median: None)

## Fracture type counts

_none_

## Faithfulness

_none_
