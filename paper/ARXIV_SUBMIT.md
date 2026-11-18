# arXiv submission checklist

**Package ready in-repo.** PDF: `character_hold_arxiv.pdf`. Bundle: `arxiv_submission_bundle.zip`.

## Upload (manual — requires your arXiv account)

1. Go to https://arxiv.org/submit  
2. New submission → **cs.CL** (primary), add **cs.AI** (secondary).  
3. Upload `paper/character_hold_arxiv.pdf` (or LaTeX source later if you convert).  
4. Optional: also attach `arxiv_submission_bundle.zip` as ancillary.  
5. Title / authors / abstract: copy from `manuscript.md`.  
6. Comments: `Code: https://github.com/fcavaletto/character-hold`  
7. License: match MIT / arXiv non-exclusive distribution.  
8. After acceptance, you get `arXiv:YYYY.NNNNN` — then run:

```bash
# backfill ID into CITATION.cff, CITATION.bib, README badge, manuscript header
# then: git tag v0.3.0-arxiv && git push --tags
```

## Endorsement

If arXiv asks for endorsement in cs.CL, request from a colleague with endorsement rights, or submit via an endorsed co-author workflow.

## Why this file exists

Automated upload needs interactive arXiv login; the repo ships a complete submission package so the remaining step is the web form.
