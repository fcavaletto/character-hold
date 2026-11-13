# Comparison one-pager

**Degrees of evidence.** MOCK is a pipeline illustration. Live arms are single-seed, temp-0, n=144 OpenRouter pilots. Pressure **hold** uses a keyword heuristic as **primary**; dual-annotation LLM judge is **secondary** only.

## Aggregate metrics

| Arm | say | use | hold | gap | median break | fractures | cost (USD) |
|-----|----:|----:|-----:|----:|-------------:|----------:|-----------:|
| MOCK `mock-v1` | 0.521 | 0.521 | 0.333 | 0.000 | 2.0 | 32 / 48 | — |
| DeepSeek `deepseek/deepseek-v4.1-flash` | 0.792 | 0.979 | 1.000 | -0.188 | — | 0 / 48 | 0.057 |
| Haiku `anthropic/claude-haiku-4.5` | 0.896 | 1.000 | 1.000 | -0.104 | — | 0 / 48 | 0.619 |

Figure: [`pilot-haiku-4.5/figures/model_comparison_bars.png`](pilot-haiku-4.5/figures/model_comparison_bars.png)

## Dual-annotation (secondary LLM judge)

**DeepSeek subject.** Judge `anthropic/claude-haiku-4.5` on n=24 (seed 0).

- Fracture exact match: 1.000; κ=1.000 (often degenerate when both sides always “no”)
- Identity exact match: 0.000; κ=0.000 (heuristic often defaults to `partial`)
- Principle exact match: 0.708; κ=0.000
- **Secondary fractures primary missed:** 0

**Haiku subject (same item ids when available).** Judge `deepseek/deepseek-v4.1-flash` on n=24 (seed 0).

- Fracture exact match: 1.000; κ=1.000 (often degenerate when both sides always “no”)
- Identity exact match: 0.000; κ=0.000 (heuristic often defaults to `partial`)
- Principle exact match: 0.667; κ=0.000
- **Secondary fractures primary missed:** 0

## Honest limitations

1. Every frozen use item has `correct_choice: A`; a high use_rate does **not** cleanly prove principle-following vs A-preference.
2. `hold_rate = 1.0` under the heuristic means no unnegated `out`/`reverses` cue — not gold evidence of never yielding.
3. Dual-annotation n is a stratified subset (one seed); LLM judge has circularity risk.
4. One temperature (0); not a population estimate across prompts or decoding.

## Reproduce

```bash
character-hold run --config configs/default.yaml --provider openrouter \
  --model anthropic/claude-haiku-4.5 --run-id pilot-haiku-4.5
character-hold annotate-pressure --input results/pilot-deepseek-flash \
  --judge-provider openrouter --judge-model anthropic/claude-haiku-4.5 \
  --sample 24 --seed 0 --output results/pilot-deepseek-flash/dual_annotation/
python scripts/build_comparison.py
```
