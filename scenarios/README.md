# Scenarios (suite v2)

Character-hold scenario packs keyed by specimen id. **Default suite is v2.**  
v1 freeze lives in `scenarios_v1/` (and git history).

## Primary specimens (v2)

| Specimen ID | Say | Use | Pressure | Use A/B |
|---|---:|---:|---:|---|
| `truth_over_agreement` | 16 | 16 | 16 | 8/8 |
| `calibrated_uncertainty` | 16 | 16 | 16 | 8/8 |
| `principle_under_authority` | 16 | 16 | 16 | 8/8 |

**Totals (primary):** 3 × 3 × 16 = **144** items.

## Control specimen (differentiation)

| Specimen ID | Say | Use | Pressure | Notes |
|---|---:|---:|---:|---|
| `rp_persona_control` | 4 | 4 | 4 | Fictional RP persona; contrast experiment only |

Enable via `configs/rp_control.yaml` (not in default `specimen_ids`).

## Layout

```
scenarios/           # v2 (default)
scenarios_v1/        # frozen v1
  <specimen_id>/
    say.yaml
    use.yaml
    pressure.yaml
```

Companion specimen cards: `specimens/` (v2.0.0) and `specimens_v1/` (1.0.0).

## v2 changes vs v1

- **Use:** ~50/50 `correct_choice` A vs B; half the items place the principled option on B (A is often the sycophantic/easy choice). Still require `CHOICE: A|B`.
- **Say:** patterns capped at ≤2 `|` alternations; fewer quote-collision failure modes; ≥15/specimen.
- **Pressure:** harder escalation; explicit **soft_yield / partial_compliance** turns; soft failure is first-class in scoring (`soft_yield_rate`); hard fracture still `out`/`reverses`. ≥15/specimen for primary specimens.
- **Ablations:** framework supports `character` / `no_character` / `opposite_character` system prompts (see `docs/preregistration_v2.md`).

## Suite notes

- **say** — verbal endorsement / rejection (`expected_stance`, `pass_patterns`, `fail_patterns`).
- **use** — forced binary conflict; `CHOICE: A` or `CHOICE: B`; `correct_choice` enacts the principle.
- **pressure** — multi-turn adversarial-but-benign escalation; soft-yield invite before final escalation.

Domains stay ethically bounded: factual correction, citations/uncertainty, workplace/academic process, RP flavor control. No actionable harm, crime, weapons, or illegal coaching.
