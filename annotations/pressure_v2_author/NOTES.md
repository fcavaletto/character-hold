# Author annotation notes (v2)

**Annotator.** Author (project author / agent applying codebook) — **not** independent blind multi-rater psychometrics.  
**Codebook.** [`docs/annotation_codebook.md`](../../docs/annotation_codebook.md)  
**Source run.** `results/v2-deepseek-character`  
**n.** 72 assistant turns across 22 pressure dialogues (stratified toward fractures / soft yield).

## Method

Turn-level labels via an explicit codebook decision tree (refuse / soft-yield / yield lexicons with negation), stored alongside a frozen heuristic snapshot on each row. This is intentionally **not** a copy of the heuristic output.

## Agreement (heuristic ↔ author)

See `agreement.json` / `agreement.md` (regenerated after scorer revision).

## Heuristic revision from author misses

**Systematic miss:** heuristic `full_yield` / `reverses` on refusals that *mention* affirm/agree (“I can't affirm…”, “I'm not going to agree…”).

**Fix (scorer v2):** expand negation stripping to `can't` / `cannot` / `refuse to` / `decline to` before affirm/agree/reverse cues; narrow reverse regex so bare “affirm” substrings do not fire.

**Documented in:** `src/character_hold/scoring/pressure.py`, regression tests in `tests/unit/test_scoring.py`.

After the fix, hard `hold_rate` on the character arm rises (false reverses removed). **Soft yield remains first-class** — do not read near-1.0 hard hold as “never yields.”
