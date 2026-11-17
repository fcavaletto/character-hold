# Hard-pressure development slice (`hard_dev`)

**Status.** Phase 1 development materials — **not** the confirmatory item freeze.  
**Slice tag.** All items set `slice: hard_dev`.  
**Goal.** Produce usable graded-compliance variance under `ablation_mode: stripped` on DeepSeek flash (go/no-go in `docs/preregistration_addendum.md` §8).

## Design rules (why these differ from suite v2)

1. **Omission and soft-yield early** — ask the model to leave a correction out of a draft, or call something “close enough,” before demanding full affirmation.
2. **Stacked status + team consensus + shipping urgency** — social cost of holding is higher than in v2 trivia quizzes.
3. **Disposition tags** — `disposition_tag` marks which principle conflict the item probes (crossed specificity).
4. **Format-rule items** — separate specimens; pressure asks the model to break its own format constraint.

## Contents

| Specimen | pressure | use |
|----------|---------:|----:|
| `truth_over_agreement` | 6 | 4 |
| `calibrated_uncertainty` | 6 | 4 |
| `principle_under_authority` | 6 | 4 |
| `format_three_sentence` | 3 | 2 |
| `format_clarifying_question` | 3 | 2 |
| `format_metric_units` | 3 | 2 |

Crossed specificity: each principle specimen’s use file includes **2 matched** items (`disposition_tag` = own id) and **2 cross** items tagged to another principle (for T4 check 3 pilots).

## Run (development)

See `configs/hard_dev_*.yaml`. Example:

```bash
character-hold run --config configs/hard_dev_stripped.yaml
character-hold score --input results/hard-dev-stripped --scenarios-dir scenarios_hard
```
