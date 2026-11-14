# Character-hold suite v2 — research note

**Status.** Pilot measurement redesign + live DeepSeek flash arms (character / no_character / opposite) + RP control + author annotation.  
**Pre-registration:** `docs/preregistration_v2.md` (written before interpreting v2 live aggregates).  
**Claims rule.** Only what survives ablations, CIs, and author-label checks.

## 1. Motivation and predicted dissociations

Declared assistant character is often treated as load-bearing. RP/persona benchmarks measure fictional role fidelity, not whether assistant principles survive **say → use → hold** under pressure.

**Pre-registered predictions:**

1. Soft-yield invites produce visible `partial_compliance` without always hard-fracturing.
2. **Character vs no_character:** load-bearing prompts should raise use/hold or lower soft yield.
3. **Opposite character:** should depress use relative to character.
4. RP control can retain persona flavor without implying factual character-hold.

**Falsifiers:** ablation Δ ≈ 0 on use/hold/soft-yield; author↔heuristic agreement near chance; use A/B imbalance.

## 2. What changed in v2

| Critique | v2 response |
|----------|-------------|
| Use all `correct_choice=A` | **Closed:** ~50/50 A/B |
| Hold=1.0 weak keywords | Soft-yield taxonomy; scorer revised vs author labels; hard hold still high on DeepSeek |
| No gold-ish labels | **Closed (author-only):** 152 turns / 24 dialogues |
| Character vs IF | **Closed as design:** ablations run |
| Soft / partial compliance | **Closed:** first-class `soft_yield_rate` |
| No uncertainty | **Closed:** bootstrap 95% CIs (1000) |
| Brittle say regex | **Closed:** ≤2 `\|` per pattern |
| vs RP evals | **Partial:** small RP control contrast |
| LLM-judge circularity | **Partial:** author gold-ish; judge secondary (n=8) |
| Thin theory | Pre-reg dissociations + falsifiers |

## 3. Live metrics (DeepSeek `deepseek-v4.1-flash`, suite v2)

Temperature 0; reasoning effort none. Primary specimens = 144 items. CIs = percentile bootstrap 95%.

| Arm | say | use | hold | soft_yield | cost |
|-----|-----|-----|------|------------|------|
| **character** | 0.792 [0.667, 0.896] | 1.000 [1.000, 1.000] | 0.979 [0.938, 1.000] | 0.188 | $0.061 |
| **no_character** | 0.792 [0.667, 0.917] | 1.000 [1.000, 1.000] | 0.983 [≈1.0] | 0.283 | $0.049 |
| **opposite** | 0.646 [0.500, 0.771] | **0.000 [0.000, 0.000]** | 0.941 [0.896, 1.000] | 0.451 | $0.063 |
| **RP control** (n=12) | 0.750 | 1.000 | 0.500 | 0.500 | $0.003 |

say–use gap (character): **−0.208** [−0.333, −0.104] (use exceeds say; ceiling on use).

### Ablation deltas

| Contrast | Δsay | Δuse | Δhold | Δsoft_yield |
|----------|------|------|-------|-------------|
| character − no_character | ~0 | ~0 | ~0 | **≈ −0.10** (character slightly less soft yield) |
| character − opposite | +0.15 | **+1.00** | +0.04 | −0.26 |

**Interpretation (honest):**

- On DeepSeek flash, the **default character prompt is not necessary** for principled use (ceiling already under generic system) or hard hold.
- The **opposite prompt fully inverts use (0%)** — system text *can* control forced choice when it fights base priors. So character is **sufficient-looking but not uniquely causal** for use on this model; the informative causal arm is opposite, not no_character.
- Soft yield is the pressure signal that moves: opposite > no_character > character.
- Hard `hold_rate` ≈ 1.0 under out/reverses remains a weak differentiator on this model/suite; do **not** read it as robust alignment.

### RP contrast

Small-n RP persona control: use 1.0, hold 0.5 (wide CI). Suggests persona pressure can hard-fracture more than assistant-character factual pressure on DeepSeek — differentiation is plausible but underpowered.

## 4. Annotation agreement

**Author labels:** 152 turns / 24 dialogues from `results/v2-deepseek-character`  
Codebook: `docs/annotation_codebook.md`  
Path: `annotations/pressure_v2_author/`  
**Not** independent blind multi-rater psychometrics.

| Pair | Dimension | Match | Cohen’s κ |
|------|-----------|------:|----------:|
| Heuristic ↔ author | compliance_level | 0.914 | 0.342 |
| Heuristic ↔ author | principle | 0.914 | 0.342 |
| Heuristic ↔ author | identity | 0.901 | 0.082* |
| Judge ↔ author (overlap) | identity / principle | ~0.90 | ~0* |

\*κ depressed by class imbalance (mostly `holds` / `in_character`).

**Scorer revision:** v2 heuristics initially over-called `partial_compliance` when models quoted soft-yield asks but refused. After author dual-coding, soft lexicon no longer overrides clear hold/refusal language. Documented in `scoring/pressure.py` comments + this note.

## 5. What we claim vs do not claim

**Survives:**

1. v2 closed major measurement confounds (A/B balance, soft yield, CIs, ablation wiring, author path).
2. Opposite-character ablation shows **system prompts can drive use** (0% vs 100%).
3. Character vs no_character is a **near-null** on say/use/hold for DeepSeek flash; soft yield only mildly favors character.
4. Author↔heuristic agreement is high on exact match; κ moderate given imbalance.

**Does not survive / open:**

- “Character prompts improve hold vs generic assistants” on DeepSeek flash (falsified / null).
- Independent multi-rater reliability (needs Federico + second human).
- Cross-model generality (Haiku not re-run on v2 in this pass).
- Hard hold as a sensitive outcome on this suite/model.

## 6. What would further falsify remaining claims

- Opposite use recovers to ~character levels under a harder forced-choice format → prompt control was item-format artifact.
- Federico labels disagree with author-agent labels on soft yield systematically → annotation path invalid.
- Haiku/other models show character ≫ no_character on use/hold → DeepSeek result is model-specific (still fine; must qualify).

## 7. Costs

| Item | USD |
|------|-----|
| DeepSeek character | 0.061 |
| DeepSeek no_character | 0.049 |
| DeepSeek opposite | 0.063 |
| RP control | 0.003 |
| Judge sample (8 dialogues, gpt-4o-mini) | ≪0.05 |
| **Total (approx.)** | **~$0.18–0.22** |

Haiku v2 character arm deferred to save budget after DeepSeek ablations landed.

## 8. Artifacts

- Runs: `results/v2-deepseek-{character,no-character,opposite,rp-control}/`
- Annotations: `annotations/pressure_v2_author/`
- Pre-reg: `docs/preregistration_v2.md`
- Comparison: `results/COMPARISON.md`
