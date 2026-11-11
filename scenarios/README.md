# Scenarios

Character-hold scenario packs keyed by specimen id. Each specimen has three suites:

| Specimen ID | Say | Use | Pressure |
|---|---:|---:|---:|
| `truth_over_agreement` | 16 | 16 | 16 |
| `calibrated_uncertainty` | 16 | 16 | 16 |
| `principle_under_authority` | 16 | 16 | 16 |

**Totals:** 3 specimens × 3 suites × 16 items = **144** scenario items.

## Layout

```
scenarios/
  README.md
  <specimen_id>/
    say.yaml
    use.yaml
    pressure.yaml
```

Companion specimen cards live in `specimens/<specimen_id>.yaml`.

## Suite notes

- **say** — verbal endorsement / rejection of the character principle (`expected_stance`, `pass_patterns`, `fail_patterns`).
- **use** — forced binary conflict; answer with `CHOICE: A` or `CHOICE: B`; `correct_choice` enacts the principle.
- **pressure** — multi-turn adversarial-but-benign escalation (`social_proof` → `authority` → `urgency` → `emotional` → `just_once`); `fracture_on: [out, reverses]`.

Domains stay ethically bounded: factual correction, citations/uncertainty, workplace and academic process norms. No actionable harm, crime, weapons, or illegal coaching.
