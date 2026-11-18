# Character-shaped prompts under pressure: disposition cards vs matched instructions

**Status.** Draft manuscript (Path D). Confirmatory numbers filled from frozen `hard_dev_v2` runs; replace camera-ready κ with external second-human labels when available.

**Pre-registration.** `docs/preregistration_addendum.md`, `docs/preregistration_item_slice.md`.

---

## Abstract

System prompts that declare assistant *character*—stable dispositions such as preferring truth over agreement—are widely used. Practitioners often say these “character cards work,” but that folk claim conflates steering, pressure robustness, Q&A usefulness, and agentic reliability. We evaluate **pressure-robust disposition steering in chat** only. Using a five-disposition battery of best-practice HHH character cards, matched plain-order paraphrases, blank system prompts, and demand vs naturalistic reverse controls, we measure graded yielding under multi-turn social pressure. On development (DeepSeek flash), blank prompts yield substantially; cards reduce yielding vs blank on aggregate, but matched imperatives still win (**T3-negative**). Confirmatory: **Sonnet clears T2**; **GPT-4.1-mini does not**; **neither clears positive T3**. Popular character prompting is not shown to beat matched orders; T2 does not generalize across both confirmatory families. We do not claim Q&A usefulness or tool-using agency.

---

## 1. Introduction

API chat models are routinely given system prompts that declare who the assistant “is”: truth-seeking, uncertain when appropriate, process-faithful under authority, and so on. These **character cards** are treated as load-bearing in products and evaluations. A separate literature measures **persona / role-play fidelity** (e.g. PersonaGym, CharacterEval, RPEval)—whether the model stays in a *fictional* role. That is a different construct from whether *assistant* dispositions survive conflict between niceness and principle.

This paper asks: under social, authority, and urgency pressure in chat, do well-crafted disposition cards change conflict behavior beyond (a) a blank system prompt and (b) the same rules written as plain orders?

## 2. What people mean by “character cards work”

| Meaning | Definition | This paper |
|---------|------------|------------|
| **Steering** | Behavior shifts toward the named disposition | In scope |
| **Robustness** | The shift survives pressure | In scope (primary) |
| **Q&A usefulness** | Better answers / preference / task success | Out of scope |
| **Agency** | Tool-using agents keep constraints in the world | Out of scope (sequel) |

A null or negative result on robustness does **not** refute usefulness or agency claims; a positive residual does **not** establish them. We state this boundary explicitly so “character cards work” is not smuggled across meanings.

## 3. Construct and claim ladder

**Character** = declared assistant dispositions in a specimen system prompt (not RP lore).  
**Character-shaped residual** = conflict effect left after matched instructions, channel priority, and format-rule controls.

We use a pre-registered claim ladder (T0–T5). **Co-primary:** T2 (vs stripped) and T3 (vs imperative), including a licensed **T3-negative** write-up if orders win or tie.

Primary dependent variable: **graded compliance** on hard-pressure dialogues (holds=0, partial=1, full yield=2; worst assistant turn). Forced-choice **use** is sensitivity / demand-characteristics only.

## 4. Method

### 4.1 Five-disposition battery

Built to a shared craft rubric (`docs/character_card_rubric.md`): identity line, principles, behaviors, failure modes, under-pressure paragraph, micro-example, length band.

1. Truth over agreement  
2. Calibrated uncertainty  
3. Principle under authority  
4. Anti-flattery  
5. Privacy minimization  

Each has matched `imperative` and `naturalistic_reverse` arms. Format-rule specimens serve as “any extra rule” controls. Ethics: benign workplace/academic pressure only.

### 4.2 Arms and models

Arms: `stripped`, `character`, `imperative`, `naturalistic_reverse`, `demand_opposite` (honesty).  
Development: DeepSeek flash. Confirmatory: `anthropic/claude-sonnet-4.5`, `openai/gpt-4.1-mini`.  
Slice: `hard_dev_v2` (frozen item IDs and card hashes in `docs/preregistration_item_slice_manifest.json`).

### 4.3 Reliability

Dual annotation on n=24 yielding-rich stripped dialogues (codebook). Author double-code κ≈0.39 (exact match ≈0.79); external second human pending for camera-ready.

## 5. Pilots

**Suite v2.** Character ≈ generic helpful assistant on say/use/hold; demand-style opposite collapses use to 0.  
**hard_dev / hard_dev_v2 (DeepSeek).** Blank prompts yield (mean grade ≈0.70 on v2); character reduces yielding vs blank (Δ_T2≈+0.17); **imperative reduces yielding more** (Δ_T3≈−0.13). Demand opposite annihilates use; naturalistic reverse barely moves it. Heterogeneity across dispositions is large (TOA shows a strong T2-shaped effect; others mixed).

## 6. Confirmatory results

*Filled by analysis after confirmatory runs complete. See `results/conf-*/battery_deltas.json` and figures.*

### 6.1 GPT-4.1-mini

**GPT-4.1-mini.** Δ_T2 pooled=0.067 CI=[-0.067, 0.200] (n=30). Δ_T3 pooled=-0.067 CI=[-0.233, 0.100]. Per-disposition T2: anti_flattery=+0.17, calibrated_uncertainty=+0.17, principle_under_authority=-0.17, privacy_minimization=+0.17, truth_over_agreement=+0.00. Per-disposition T3: anti_flattery=+0.00, calibrated_uncertainty=+0.00, principle_under_authority=-0.33, privacy_minimization=+0.00, truth_over_agreement=+0.00.

### 6.2 Claude Sonnet 4.5

**Claude Sonnet 4.5.** Δ_T2 pooled=0.267 CI=[0.067, 0.467] (n=30). Δ_T3 pooled=0.033 CI=[-0.167, 0.233]. Per-disposition T2: anti_flattery=+0.33, calibrated_uncertainty=+0.00, principle_under_authority=+0.50, privacy_minimization=+0.17, truth_over_agreement=+0.33. Per-disposition T3: anti_flattery=+0.17, calibrated_uncertainty=-0.17, principle_under_authority=+0.33, privacy_minimization=-0.17, truth_over_agreement=+0.00.

### 6.3 Cross-family summary

Confirmatory picture is **family-heterogeneous**. **Claude Sonnet 4.5 clears T2** (Δ_T2=0.267, CI [0.067, 0.467] entirely above 0). **GPT-4.1-mini does not** (Δ_T2=0.067, CI [-0.067, 0.200] covers 0). **Positive T3 clears on neither** (both CIs cover 0; GPT point estimate negative, Sonnet near zero). Per Path D rules: do not write 'assistants' as the population for T2 in the abstract; report model-specific confirmatory results. Highest honest cross-family claim is **T3-negative / no character-shaped residual over matched orders**, with **T2 on Sonnet only**. Development DeepSeek showed T2-mild + T3-negative; Sonnet strengthens T2, GPT weakens it.

## 7. Discussion

If confirmatory families replicate T2-mild / T3-negative: the practical lesson is that **system-channel instructions** move pressure behavior, while **disposition costume** is not necessary—and can underperform a checklist of the same rules. That undercuts a strong reading of “character prompting works” for *pressure robustness*, without settling Q&A or agent claims.

Heterogeneity (e.g. stronger TOA card effects) suggests disposition content and prior alignment interact; craft alone does not guarantee a residual.

We do **not** claim models “have character,” nor that cards improve tool-using agents.

## 8. Limitations and sequel

Chat sandbox; temperature 0; English benign items; author double-code κ until external rater. Sequel: agentic tool-hold; outcome usefulness; mechanisms.

## 9. Conclusion

We separate folk meanings of “character cards work” and test pressure-robust steering in chat with a five-card battery and matched orders. Development evidence favors **T2-mild with T3-negative**; confirmatory results support **T2 on Sonnet only**, **not on GPT-4.1-mini**, and **no positive T3 on either family**. Disposition framing is not licensed as superior to matched instructions; cross-family T2 is not established.
