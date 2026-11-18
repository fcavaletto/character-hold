# Paper outline — Path D (one manuscript)

**Working title.** Character-shaped prompts under pressure: disposition cards vs matched instructions  

**Status.** Outline for the single paper. Results sections filled after confirmatory runs.

---

## 1. Introduction

- System prompts routinely declare assistant dispositions (“prefer truth over agreement,” etc.).
- Practitioners treat these **character cards** as load-bearing.
- Folk claim “character cards work” is ambiguous — §2.
- This paper asks whether disposition framing produces **pressure-robust steering in chat** beyond blank and matched plain-order controls.

## 2. What people mean by “character cards work”

Four meanings (construct boundary; also in pre-registration):

| Meaning | Definition | This paper |
|---------|------------|------------|
| Steering | Behavior shifts toward the named disposition | In scope |
| Robustness | Shift survives social / authority / urgency pressure | In scope (primary) |
| Q&A usefulness | Better answers, preference, task success | Out of scope |
| Agency | Tool-using agents keep constraints in the world | Out of scope (sequel) |

Contribution: identify (or refute) a **character-shaped residual** for (1)–(2) only; refuse overclaim to (3)–(4).

## 3. Construct

- Assistant **disposition** ≠ fictional RP persona (contrast PersonaGym / CharacterEval / RPEval).
- Load-bearing = say / use / graded hold under conflict.
- Character-shaped residual = effect left after matched instructions, channel, and format-rule controls.

## 4. Claim ladder

T0–T5 permitted sentences (see `docs/preregistration_addendum.md`).  
**Co-primary:** T2 (vs stripped) and T3 (vs imperative), including licensed **T3-negative**.

## 5. Method

- Five-disposition battery + card rubric (`docs/character_card_rubric.md`).
- Arms: stripped, character, imperative, naturalistic_reverse, demand_opposite; format controls; character_user.
- DV: worst-turn graded compliance; use as sensitivity only.
- Ethics: benign pressure only (`docs/ethics.md`).
- Dev model vs confirmatory families; dual human annotation.

## 6. Pilots (brief)

- Suite v2: character ≈ generic assistant; demand opposite collapses use.
- hard_dev: stripped yields; character < stripped yielding; imperative ≤ character yielding on DeepSeek flash.
- Motivation for rubric rebuild and Path D battery.

## 7. Confirmatory results

- Pooled Δ_T2, Δ_T3 with CIs.
- Per-disposition forest plots (heterogeneity).
- Demand vs naturalistic use.
- Specificity / format / channel as available.
- Reliability (κ).

## 8. Discussion

- If T3-negative: popular “character prompting” may be **instructions in the system channel**; costume optional or slightly harmful.
- If heterogeneous: which dispositions show residual under matched craft.
- Do **not** generalize to Q&A usefulness or agentic reliability.

## 9. Limitations and sequel

- Chat sandbox only; no tools.
- Single temperature / API chat setting.
- Sequel: agentic tool-hold; outcome usefulness; mechanisms.

## 10. Conclusion

One paragraph: highest licensed tier + explicit scope limit.
