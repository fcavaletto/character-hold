# character-hold

[![CI](https://github.com/fcavaletto/character-hold/actions/workflows/ci.yml/badge.svg)](https://github.com/fcavaletto/character-hold/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![arXiv](https://img.shields.io/badge/arXiv-TBD-b31b1b.svg)](paper/character_hold_arxiv.pdf)

**Do character system prompts do more than matched instructions under pressure?**

Path D tests five HHH disposition cards against blank and plain-order controls using graded yielding in chat. **Sonnet clears T2** (card vs blank); **GPT-4.1-mini does not**; **neither clears positive T3** (character does not beat matched orders). Folk “character cards work” mixes steering, robustness, usefulness, and agency — this project measures **chat steering + robustness** only.

**Author.** [Federico Cavaletto](https://github.com/fcavaletto) · **License.** [MIT](LICENSE) · **Cite.** [`CITATION.cff`](CITATION.cff)

---

## Start here

| Goal | Go to |
|------|--------|
| **Read the preprint** | [`paper/manuscript.md`](paper/manuscript.md) · [`paper/character_hold_arxiv.pdf`](paper/character_hold_arxiv.pdf) |
| **Results one-pager** | [`results/COMPARISON_PATH_D.md`](results/COMPARISON_PATH_D.md) |
| **Forest plots** | [`paper/figures/forest_sonnet.png`](paper/figures/forest_sonnet.png) · [`paper/figures/forest_gpt41mini.png`](paper/figures/forest_gpt41mini.png) |
| **Pre-registration** | [`docs/preregistration_addendum.md`](docs/preregistration_addendum.md) · [`docs/preregistration_item_slice.md`](docs/preregistration_item_slice.md) |
| **Reliability (LLM judge)** | [`docs/reliability_path_d.md`](docs/reliability_path_d.md) |
| **Run locally (no API)** | [Quickstart](#quickstart) → `make demo` |
| **Portfolio blurb** | [`docs/portfolio_blurb.md`](docs/portfolio_blurb.md) |

> **Degrees of evidence.** Confirmatory arms are single-seed, temp-0 OpenRouter runs. Primary pressure labels are heuristic; LLM-judge is secondary. No independent second human rater. Not population estimates over all models.

---

## Key findings (Path D)

| Model | Δ_T2 (stripped − character) | Δ_T3 (imperative − character) |
|-------|----------------------------:|------------------------------:|
| Claude Sonnet 4.5 | **+0.267** CI [0.067, 0.467] — T2 clears | +0.033 CI covers 0 — no positive T3 |
| GPT-4.1-mini | +0.067 CI [−0.067, 0.200] — T2 fails | −0.067 CI covers 0 — no positive T3 |
| DeepSeek flash (dev) | ≈+0.17 (pilot) | ≈−0.13 (T3-negative lean) |

Full write-up: [`docs/hard_dev_v2_gonogo.md`](docs/hard_dev_v2_gonogo.md) · [`results/COMPARISON_PATH_D.md`](results/COMPARISON_PATH_D.md).

---

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # add API keys only for live providers; never commit .env

make demo              # validate → mock run → score → report (CPU-only)
make paper             # rebuild paper/character_hold_arxiv.pdf
```

Requires Python **3.11+**.

**Live Path D configs** (costs money; needs `OPENROUTER_API_KEY`):

```bash
character-hold run --config configs/hard_dev_v2_stripped.yaml
character-hold run --config configs/conf-sonnet_character.yaml
# see configs/hard_dev_v2_*.yaml and configs/conf-*.yaml
```

---

## Method (short)

**Say → use → graded hold** under benign social/authority/urgency pressure.  
Arms: `stripped` / `character` / `imperative` / `naturalistic_reverse` / `demand_opposite`.  
Five dispositions + format-rule controls. Ethics: [`docs/ethics.md`](docs/ethics.md).

Suite **v2** lives as a **pilot appendix** ([`docs/research_note_v2.md`](docs/research_note_v2.md)).

---

## License

MIT. See [`LICENSE`](LICENSE).
