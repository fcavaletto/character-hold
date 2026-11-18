# Path D reliability (no second human)

**Policy.** Primary paper metrics use the **deterministic / heuristic** pressure scorer.  
**Secondary.** Cross-family **LLM-as-judge** via `character-hold annotate-pressure`.  
**Not used as dual human.** Author files under `annotations/pressure_hard_dual/` are appendix only.

There is **no independent second human rater** for this preprint.

---

## Design

| Subject run | Subject model | Judge | n pressure | Output |
|-------------|---------------|-------|------------|--------|
| `results/conf-sonnet-character` | `anthropic/claude-sonnet-4.5` | `openai/gpt-4.1-mini` | 30 | `…/dual_annotation_llm/` |
| `results/conf-gpt41mini-character` | `openai/gpt-4.1-mini` | `anthropic/claude-haiku-4.5` | 30 | `…/dual_annotation_llm/` |
| `results/hard-dev-v2-stripped` | `deepseek/deepseek-v4.1-flash` | `openai/gpt-4.1-mini` | 30 | `…/dual_annotation_llm/` |

Seed `0`; full pressure set (30 items). Labels: identity, principle, fracture (see `docs/dual_annotation.md`).  
**Note.** Paper primary DV is *worst-turn graded compliance*; the annotate CLI compares *dialogue-level* heuristic labels (last-turn / fracture). Treat LLM agreement as a check on coarse hold vs yield, not a psychometric validation of soft-yield grades.

---

## Results

### Sonnet character ← GPT-4.1-mini judge

| Dimension | Exact match | Cohen’s κ |
|-----------|------------:|----------:|
| fracture | 1.000 | 1.0 |
| identity | 1.000 | 1.0 |
| principle | 1.000 | 1.0 |

Both sides labeled **all 30** as holds / in_character / no fracture. Agreement is perfect but **uninformative for soft-yield discrimination** (no class variance).

### GPT-4.1-mini character ← Haiku judge

| Dimension | Exact match | Cohen’s κ |
|-----------|------------:|----------:|
| fracture | 0.367 | 0.0 |
| identity | 0.067 | ≈0 |
| principle | 0.100 | ≈0 |

Heuristic: mostly `holds` (28/30). Haiku judge: many `reverses`/`out` (19/30 fractures). **Low agreement:** the secondary judge is much harsher than the keyword heuristic on this arm. Primary tables remain heuristic; this gap is a **limitation** (soft/partial yielding is scorer-sensitive).

### DeepSeek stripped ← GPT-4.1-mini judge

| Dimension | Exact match | Cohen’s κ |
|-----------|------------:|----------:|
| fracture | 0.933 | 0.0* |
| identity | 0.967 | 0.0* |
| principle | 0.900 | 0.0* |

\*κ depressed by class imbalance (almost all non-fracture). Judge called **0** fractures; heuristic called **2**. High exact match, weak κ.

---

## Interpretation for the paper

1. When both systems see near-ceiling hold (Sonnet character), they agree.  
2. When the heuristic is lenient and an LLM judge is strict (GPT character), they diverge — do **not** treat soft-yield point estimates as gold.  
3. Confirmatory **T2/T3 deltas still use the same heuristic on all arms**, so arm contrasts remain internally consistent even if absolute soft-yield rates are biased.  
4. Pre-registered human dual annotation was **not** completed; LLM-judge is the published secondary check.

## Reproduce

```bash
character-hold annotate-pressure --input results/conf-sonnet-character \
  --judge-model openai/gpt-4.1-mini --sample 30 --seed 0 \
  --output results/conf-sonnet-character/dual_annotation_llm/

character-hold annotate-pressure --input results/conf-gpt41mini-character \
  --judge-model anthropic/claude-haiku-4.5 --sample 30 --seed 0 \
  --output results/conf-gpt41mini-character/dual_annotation_llm/

character-hold annotate-pressure --input results/hard-dev-v2-stripped \
  --judge-model openai/gpt-4.1-mini --sample 30 --seed 0 \
  --output results/hard-dev-v2-stripped/dual_annotation_llm/
```
