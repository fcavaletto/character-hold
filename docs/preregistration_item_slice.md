# Pre-registration — item slice freeze (Path D confirmatory)

**Frozen:** 2026-11-17, after `docs/hard_dev_v2_gonogo.md` and **before** confirmatory model calls.  
**Not editable** after confirmatory runs start.  
**Machine manifest:** `docs/preregistration_item_slice_manifest.json` (item IDs + card content hashes).

## Slice

- **Tag:** `hard_dev_v2` under `scenarios_hard/` (`*_v2.yaml`)
- **Principle specimens (5):** `truth_over_agreement`, `calibrated_uncertainty`, `principle_under_authority`, `anti_flattery`, `privacy_minimization`
- **Counts:** 30 pressure + 20 use (see manifest)
- **Format controls:** separate configs; not in primary pooled Δ

## Confirmatory models

| Family | OpenRouter model ID |
|--------|---------------------|
| Anthropic Sonnet-class | `anthropic/claude-sonnet-4.5` |
| OpenAI GPT-4.1-class | `openai/gpt-4.1-mini` |

**Development model excluded:** `deepseek/deepseek-v4.1-flash`.

## Arms (each confirmatory model)

`stripped`, `character`, `imperative`, `naturalistic_reverse`  
(`demand_opposite` on one family if budget allows; already established on DeepSeek)

## Estimands

As in `docs/preregistration_addendum.md`: pooled and per-disposition Δ_T2, Δ_T3; use gap gate 0.25.

## Seeds / decoding

temperature `0.0`, seed `42`, max_tokens `512` (configs under `configs/conf_*.yaml`).

## Go/no-go reference

`docs/hard_dev_v2_gonogo.md` — GO with T2-mild / T3-negative expectation on flash; confirmatory may differ by family.
