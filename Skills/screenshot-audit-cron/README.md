# Screenshot audit

Scheduled audit for screenshots in a docs repo. On each run it:

1. Scans your docs pages and counts how many images appear in each page grouping.
2. Checks every screenshot's filename against a set of naming rules (descriptive, lowercase, hyphenated, no auto-generated names like `Screenshot 2024-01-01 at 10.23.45.png` or `IMG_4821.png`).
3. For anything non-compliant, sends the image to the Anthropic API (vision) and gets back a suggested descriptive filename.
4. In `--apply` mode: renames the file (via `git mv` if you're in a repo, so history is preserved) and rewrites every reference to it across your docs.
5. Flags duplicate and near-duplicate screenshots for human review. **It never deletes or merges anything itself** -- duplicates almost always need a person to decide which copy is current.
6. Writes a markdown report of everything it did and found.

Nothing here fabricates a "Microsoft Style Guide file-naming rule" that doesn't exist -- the Microsoft Writing Style Guide is a prose/tone guide, not an asset-naming spec. The naming rules in `scripts/naming_rules.py` apply its general spirit (clear, concise, unambiguous) plus the conventions most docs style guides converge on for filenames specifically (lowercase, hyphenated, descriptive, no placeholder/auto-generated names). Adjust `scripts/naming_rules.py` freely if your team has stricter or different conventions.

## Setup

1. Copy this into your docs repo (or point it at your docs repo as a subtree/submodule).
2. `pip install -r requirements.txt`
3. Copy `config.example.yml` to `config.yml` and set `docs_root` (and `images_root` if your images live in a separate folder from your pages).
4. Get an Anthropic API key and set it as the `ANTHROPIC_API_KEY` secret in your repo (Settings -> Secrets and variables -> Actions).
5. Commit `.github/workflows/screenshot-audit.yml` -- this is what runs it on a schedule.

## Running locally

Dry run first -- this touches nothing on disk, just previews what it *would* do:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/audit_screenshots.py --config config.yml
```

Check `reports/screenshot-audit-<date>.md`, then apply for real:

```bash
python scripts/audit_screenshots.py --config config.yml --apply
```

If you don't want to spend API calls generating rename suggestions and just want the compliance/duplicate report:

```bash
python scripts/audit_screenshots.py --config config.yml --skip-vision
```

## How it runs on a schedule

`.github/workflows/screenshot-audit.yml` runs weekly (Monday 06:00 UTC by default -- edit the `cron:` line to change it) and on manual trigger from the Actions tab. It does **not** push straight to your default branch: it runs with `--apply`, then opens a pull request with whatever it changed (renamed files + updated references) using `peter-evans/create-pull-request`, and attaches the report both as the PR body and as a downloadable workflow artifact. That way renames and vision-suggested names get a human glance before they land, same as any other change to your docs.

If you'd rather it just report without ever touching files, drop `--apply` from the workflow's `run:` step -- it'll still scan, still flag naming issues and duplicates, still generate suggested names for the report, but leave your repo untouched. In that mode you can also drop the `create-pull-request` step and just keep the `upload-artifact` step, since there won't be any file changes to open a PR for.

## Tuning

Everything in `config.yml` is meant to be adjusted per-repo:

- **`group_depth`** -- how deep into your folder structure a "page grouping" goes. If a page has `category:`, `section:`, or `group:` in its frontmatter, that's used instead of the folder path.
- **`min_words`** / **`max_filename_length`** -- how strict the descriptiveness check is.
- **`near_duplicate_threshold`** -- lower = fewer false-positive duplicate flags, but may miss real near-duplicates. Start at 5 and adjust based on what the first few reports turn up.
- **`scripts/naming_rules.py`** -- `GENERIC_TERMS` and `AUTO_GENERATED_PATTERNS` are plain Python sets/lists; add your own tool's default naming pattern if it's not already covered (e.g. a specific screen-recording app's export format).

## Files

```
scripts/
  audit_screenshots.py   # entrypoint -- run this
  doc_scanner.py          # finds pages, extracts image refs + page groupings
  naming_rules.py          # compliance checks + slugify
  vision_namer.py          # Anthropic API call for rename suggestions
  duplicates.py             # exact + perceptual-hash duplicate detection
config.example.yml
.github/workflows/screenshot-audit.yml
```
