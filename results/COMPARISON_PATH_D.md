# Confirmatory battery one-pager (Path D)

## GPT-4.1-mini
**GPT-4.1-mini.** Δ_T2 pooled=0.067 CI=[-0.067, 0.200] (n=30). Δ_T3 pooled=-0.067 CI=[-0.233, 0.100]. Per-disposition T2: anti_flattery=+0.17, calibrated_uncertainty=+0.17, principle_under_authority=-0.17, privacy_minimization=+0.17, truth_over_agreement=+0.00. Per-disposition T3: anti_flattery=+0.00, calibrated_uncertainty=+0.00, principle_under_authority=-0.33, privacy_minimization=+0.00, truth_over_agreement=+0.00.

Figure: `results/conf-gpt41mini-analysis/forest_t2_t3.png`

## Claude Sonnet 4.5
**Claude Sonnet 4.5.** Δ_T2 pooled=0.267 CI=[0.067, 0.467] (n=30). Δ_T3 pooled=0.033 CI=[-0.167, 0.233]. Per-disposition T2: anti_flattery=+0.33, calibrated_uncertainty=+0.00, principle_under_authority=+0.50, privacy_minimization=+0.17, truth_over_agreement=+0.33. Per-disposition T3: anti_flattery=+0.17, calibrated_uncertainty=-0.17, principle_under_authority=+0.33, privacy_minimization=-0.17, truth_over_agreement=+0.00.

Figure: `results/conf-sonnet-analysis/forest_t2_t3.png`

## Summary
Confirmatory picture is **family-heterogeneous**. **Claude Sonnet 4.5 clears T2** (Δ_T2=0.267, CI [0.067, 0.467] entirely above 0). **GPT-4.1-mini does not** (Δ_T2=0.067, CI [-0.067, 0.200] covers 0). **Positive T3 clears on neither** (both CIs cover 0; GPT point estimate negative, Sonnet near zero). Per Path D rules: do not write 'assistants' as the population for T2 in the abstract; report model-specific confirmatory results. Highest honest cross-family claim is **T3-negative / no character-shaped residual over matched orders**, with **T2 on Sonnet only**. Development DeepSeek showed T2-mild + T3-negative; Sonnet strengthens T2, GPT weakens it.

## Development reference
See `docs/hard_dev_v2_gonogo.md` (DeepSeek flash Δ_T2≈+0.17, Δ_T3≈−0.13).
