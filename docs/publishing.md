# Publishing to GitHub

This checkout has **no git remote** and `gh` was not available/authenticated when the showcase QA ran. Use the steps below on a machine where you are logged in.

## One-time: create a public repo and push

Prefer the `fcavaletto` account if that is the logged-in user:

```bash
cd /path/to/character-hold   # this repo root

# Confirm auth (must succeed before creating a remote)
gh auth status

# Create public repo under the logged-in user and push main
gh repo create character-hold --public --source=. --remote=origin --push \
  --description "Saying ≠ using ≠ holding — under pressure — for assistant character"
```

If `gh repo create` complains that a remote already exists, skip `--remote=origin` / `--push` and push manually:

```bash
git remote add origin git@github.com:fcavaletto/character-hold.git
# or: git remote add origin https://github.com/fcavaletto/character-hold.git
git push -u origin main
```

## If `gh` is missing

```bash
# Debian/Ubuntu example
sudo apt install gh
gh auth login
```

Then re-run the `gh repo create …` command above.

## After publish

Update any local notes that still say “no remote,” and open the repo URL printed by `gh` (typically `https://github.com/<user>/character-hold`).
