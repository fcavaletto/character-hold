# arXiv submission checklist

**Package ready on `main` (tag `v0.3.0-preprint`).**  
PDF: [`character_hold_arxiv.pdf`](character_hold_arxiv.pdf) · Bundle: [`arxiv_submission_bundle.zip`](arxiv_submission_bundle.zip)

Automated browser submit hits the arXiv **login wall** — you must complete the web upload once.

## Paste fields

**Title.** Character-shaped prompts under pressure: disposition cards vs matched instructions  

**Authors.** Federico Cavaletto  

**Comments.** Code: https://github.com/fcavaletto/character-hold  

**Primary category.** cs.CL · **Secondary.** cs.AI  

**Abstract.** (from manuscript)

System prompts that declare assistant character—stable dispositions such as preferring truth over agreement—are widely used. Practitioners often say these character cards work, but that folk claim conflates steering, pressure robustness, Q&A usefulness, and agentic reliability. We evaluate pressure-robust disposition steering in chat only. Using a five-disposition battery of best-practice HHH character cards, matched plain-order paraphrases, blank system prompts, and demand vs naturalistic reverse controls, we measure graded yielding under multi-turn social pressure. On development (DeepSeek flash), blank prompts yield substantially; cards reduce yielding vs blank on aggregate, but matched imperatives still win (T3-negative). Confirmatory: Claude Sonnet 4.5 clears T2; GPT-4.1-mini does not; neither clears positive T3. Popular character prompting is not shown to beat matched orders; T2 does not generalize across both confirmatory families. We do not claim Q&A usefulness or tool-using agency.

## Upload steps

1. https://arxiv.org/submit → log in / register  
2. Upload `character_hold_arxiv.pdf` (+ optional `arxiv_submission_bundle.zip`)  
3. Categories / metadata as above  
4. After ID `arXiv:YYYY.NNNNN` is assigned, tell the agent or run:

```bash
# Replace YYYY.NNNNN then commit:
# - README arXiv badge
# - CITATION.cff identifiers
# - CITATION.bib note/eprint
# - paper/manuscript.md header
git tag -a v0.3.0-arxiv -m "arXiv:YYYY.NNNNN"
git push origin v0.3.0-arxiv
```

## Endorsement

If cs.CL asks for endorsement, request from someone with rights in that category.
