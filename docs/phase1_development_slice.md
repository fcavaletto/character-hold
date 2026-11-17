# Phase 1 — development slice and matched arms

**Status.** Development materials for go/no-go. **Not** the confirmatory item-slice freeze.  
**Depends on.** `docs/preregistration_addendum.md` (claim ladder).  
**Code / data.** `specimens/*.yaml` `arm_prompts`, `scenarios_hard/`, `configs/hard_dev_*.yaml`.

## What Phase 1 delivered

1. **Matched cards** on the three principle specimens (`version: 2.1.0`):
   - `system_prompt` — disposition / character card  
   - `arm_prompts.imperative` — same rules, no character framing (T3)  
   - `arm_prompts.naturalistic_reverse` — benign reverse, no invert/ablation demand language (T1 / sensitivity)
2. **Harness arms** (`AblationMode`): `stripped`, `imperative`, `naturalistic_reverse`, `character_user`, `demand_opposite` (v2 `opposite_character` kept as alias), plus legacy `no_character`.
3. **Format-rule specimens** (T4 check 5 / neutral slice):  
   `format_three_sentence`, `format_clarifying_question`, `format_metric_units`.
4. **Hard-pressure development slice** (`slice: hard_dev` under `scenarios_hard/`): omission-first and early soft-yield pressure; `disposition_tag` for crossed specificity pilots.
5. **Human dual-annotation stub:** `annotations/pressure_hard_dual/` (template + protocol pointer).

## Go / no-go (DeepSeek flash)

Run at least:

| Config | Arm |
|--------|-----|
| `configs/hard_dev_stripped.yaml` | blank control |
| `configs/hard_dev_character.yaml` | disposition card |
| `configs/hard_dev_imperative.yaml` | matched order |

Optional for demand / channel / format checks:  
`hard_dev_naturalistic_reverse`, `hard_dev_demand_opposite`, `hard_dev_character_user`, `hard_dev_format_*`.

**Pass to Phase 2 spend** only if:

1. Mean graded compliance under `stripped` is not near-ceiling (usable variance).  
2. `character` separates from `stripped` **and** is distinguishable from `imperative` on graded / soft yield — or redesign before confirmatory models.

## Explicitly not frozen here

- Final confirmatory item IDs / wording  
- Confirmatory model family list  
- T5 paraphrase battery text  

Those belong in a short **item-slice addendum** written after go/no-go, before confirmatory calls.

## Dual annotation (human)

After a yielding-rich `stripped` or `character` hard-dev run exists:

1. Sample dialogues with partial/full yield (see `docs/dual_annotation.md` preference order).  
2. Two humans label with `docs/annotation_codebook.md` into `annotations/pressure_hard_dual/`.  
3. Report κ on partial vs holds **where yielding varies**.

LLM-as-judge remains secondary only.
