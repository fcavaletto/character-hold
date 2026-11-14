# Comparison one-pager (suite v2)

**Degrees of evidence.** Suite **v2** live arms are single-seed, temp-0 OpenRouter pilots on DeepSeek flash. Pressure **hold** uses a revised keyword heuristic as **primary**; soft yield is first-class; author codebook labels and dual-annotation LLM judge are **secondary**. Not population estimates.

## v2 DeepSeek ablations (primary)

| Arm | say (95% CI) | use (95% CI) | hold (95% CI) | soft_yield | fractures | cost (USD) |
|-----|-------------:|-------------:|--------------:|-----------:|----------:|-----------:|
| DeepSeek flash · character | 0.792 [0.67, 0.90] | 1.000 [1.00, 1.00] | 0.979 [0.94, 1.00] | 0.188 | 1 / 48 | 0.061 |
| DeepSeek flash · no_character | 0.792 [0.67, 0.92] | 1.000 [1.00, 1.00] | 1.000 [1.00, 1.00] | 0.250 | 0 / 48 | 0.049 |
| DeepSeek flash · opposite | 0.646 [0.50, 0.77] | 0.000 [0.00, 0.00] | 0.958 [0.90, 1.00] | 0.458 | 2 / 48 | 0.063 |
| DeepSeek flash · RP control | 0.750 [0.25, 1.00] | 1.000 [1.00, 1.00] | 0.500 [0.00, 1.00] | 0.000 | 2 / 4 | 0.003 |

Figure: [`v2-deepseek-character/figures/v2_ablation_bars.png`](v2-deepseek-character/figures/v2_ablation_bars.png)

### Ablation readout (honest)

- **character vs no_character:** say/use essentially identical; hold CIs overlap. No clear positive character-prompt dependence on this model/suite.
- **opposite_character:** use collapses (≈0) while character/no_character use≈1. Inverted principles *are* load-bearing for forced choice — default helpfulness already aligns with the specimen principles, so removing the card does little.
- **soft_yield:** substantial under all arms; hard fracture remains rare after scorer negation fix.

## Author annotation (gold-ish)

Labels in `annotations/pressure_v2_author/` — **author annotation**, not blind multi-rater.

- identity match=0.901; κ=0.08212560386473368
- principle match=0.914; κ=0.34199134199134257
- compliance match=0.914; κ=0.34199134199134257

## Dual-annotation (secondary LLM judge on v2 character)

Judge `openai/gpt-4o-mini` sample n=8 (see `results/v2-deepseek-character/dual_annotation/`).

- Fracture match=0.875; κ=0.0
- Identity match=1.000; κ=1.0
- Principle match=0.875; κ=0.0

## Appendix: historical v1 pilots

| Arm | say | use | hold | gap | cost |
|-----|----:|----:|-----:|----:|-----:|
| MOCK | 0.521 | 0.521 | 0.333 | 0.000 | — |
| DeepSeek v1 | 0.792 | 0.979 | 1.000 | -0.188 | 0.057 |
| Haiku v1 | 0.896 | 1.000 | 1.000 | -0.104 | 0.619 |

v1 limitations (use always A; soft pressure; hold=1.0 heuristic skepticism) motivated suite v2.

## Reproduce

```bash
character-hold run --config configs/v2_deepseek_character.yaml
character-hold run --config configs/v2_deepseek_no_character.yaml
character-hold run --config configs/v2_deepseek_opposite.yaml
character-hold run --config configs/v2_rp_control.yaml
python scripts/build_comparison.py
```

Research note: [`docs/research_note_v2.md`](../docs/research_note_v2.md) · Pre-reg: [`docs/preregistration_v2.md`](../docs/preregistration_v2.md)
