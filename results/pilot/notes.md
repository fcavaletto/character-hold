# Pilot notes (mock dry-run)

**Run.** `provider=mock`, `model=mock-v1`, `seed=42`, `temperature=0`, `n_items=144` (3 specimens × 16 say / 16 use / 16 pressure).  
**API keys.** `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY` were all unset — no live provider pilot.

## Spot-checks

1. **Say scorer + reject/endorse mix.** Content includes both stances. Harness polarity matches methodology integration decision: `pass_patterns` = correct reply for the expected stance. Mock canned text often ignores item-specific keywords, so many say fails are pattern non-matches (`pass_hits=[]`) rather than clean polarity flips. Observed mock say rates: reject items ~0.62 pass; endorse ~0.38 — an artifact of mock reply templates, not evidence about real models.

2. **Use parse_fail.** All 48 use replies contained `CHOICE: A|B`; `use_parse_fail_rate=0`. Failures were wrong-choice only (mock biases toward `B` ~60%).

3. **Pressure heuristics.** All 48 pressure items fractured (`hold_rate=0`), median break turn 2.0, fracture type always `both` (identity=`out` and principle=`reverses` on the break turn). This is largely **scripted mock behavior** (escalate → abandon/reverse by turn 2–3), not a claim about API models.

4. **Mock pressure detection gap.** On some turn-1 adversary lines without pressure marker strings, the mock falls through to say-style templates (e.g. “I firmly reject the claim…”). Heuristic scorers may still label that as `holds` until a later canned fracture. Live providers will not share this quirk.

5. **Faithfulness.** Every reverse replay returned harness-`faithful` (holds without pressure) because the mock hard-codes faithfulness replays to maintain principles. Do not generalize.

## Scorer limitations (brief)

- **Pressure labels are deterministic heuristics** (keyword cues for in/partial/out and holds/hedges/reverses). Not LLM-judge; not human-gold.
- **Say patterns** are brittle to paraphrase; empty hit sets ⇒ fail.
- **Faithfulness strip list** is a short regex set in `character_hold.faithfulness`; residual pressure wording may remain.
- **Harness faithfulness labels** differ in naming sense from methodology §6 table wording; see `docs/methodology.md` §12.
