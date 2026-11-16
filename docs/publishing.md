# Publishing to GitHub

Remote: **https://github.com/fcavaletto/character-hold** (public, default branch `main`).

## Push from this checkout

```bash
cd /path/to/character-hold   # this repo root

# Secrets check (must be clean before push)
git check-ignore -v .env
git grep -nE 'sk-or-v1-[A-Za-z0-9]|sk-ant-|sk-proj-' || echo "no live key material in tree"

git remote add origin https://github.com/fcavaletto/character-hold.git
# or: git remote add origin git@github.com:fcavaletto/character-hold.git

git branch -M main
git push -u origin main
```

Do **not** force-push unless the remote is empty and a normal push is impossible for a documented reason.

## Repo About (GitHub UI or `gh`)

If authenticated with [`gh`](https://cli.github.com/):

```bash
gh repo edit fcavaletto/character-hold \
  --description "Saying ≠ using ≠ holding — under pressure — for assistant character" \
  --add-topic ai-safety --add-topic llm-evaluation --add-topic alignment \
  --add-topic python --add-topic evaluation-harness --add-topic openrouter
```

Suggested homepage: leave blank, or point at the HTML report once raw GitHub Pages / another host is set up.

## After publish

1. Confirm README renders: https://github.com/fcavaletto/character-hold
2. Confirm Actions CI started: https://github.com/fcavaletto/character-hold/actions
3. Confirm `.env` is **not** in the tree (`git ls-files .env` should be empty)
