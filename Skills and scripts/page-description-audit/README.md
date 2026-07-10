# Page description audit

Scheduled audit that keeps every docs page's "page description" field (frontmatter `description:`, or an HTML `<meta name="description">` tag) present and aligned with the Microsoft Writing Style Guide. On each run:

1. Scans every page under `docs_root`.
2. **Missing description** -> generates one from the page's title and content and adds it.
3. **Existing description** -> runs cheap heuristic checks (length, Title Case, ALL CAPS, missing end punctuation, marketing jargon) and, for anything flagged, asks Claude to judge it against Microsoft style and rewrite it if needed.
4. **Already compliant** -> left completely untouched -- the file isn't even rewritten, so PR diffs only ever show pages that actually changed.
5. Opens a PR with the changes for review, rather than pushing to `main` directly.

No fabricated rules: the Microsoft Writing Style Guide doesn't have a literal "page description" chapter, so the checks here apply its general, well-documented principles -- sentence case, concise and front-loaded, plain conversational language with no jargon/fluff, active voice, ends with a period. See `scripts/style_rules.py` for the exact heuristics and `scripts/llm_writer.py` for the model prompt.

## Setup

1. Copy this into your docs repo.
2. `pip install -r requirements.txt`
3. Copy `config.example.yml` -> `config.yml` and set `docs_root` and `description_fields` (the frontmatter key(s) your docs use -- e.g. just `description`, or also `page_description`/`summary` if your site uses a different name).
4. Add an `ANTHROPIC_API_KEY` secret: **Settings -> Secrets and variables -> Actions -> New repository secret**.
5. Commit `config.yml` and `.github/workflows/page-description-audit.yml`.

Unlike a pure linter, this tool always needs the API -- there's no rules-only mode for *writing* or *fixing* a description, only for the cheap pre-filter that decides whether a description needs a closer look. Running without `ANTHROPIC_API_KEY` set exits immediately with an explanation rather than silently doing nothing useful.

## Running locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

# dry run -- report only, no files touched
python scripts/audit_descriptions.py --config config.yml

# apply: add missing descriptions, rewrite non-compliant ones
python scripts/audit_descriptions.py --config config.yml --apply
```

Check `reports/description-audit-<date>.md` either way -- it lists every page under three headings (added / rewritten / left alone) with before/after text and the reason for each change.

## How it runs on a schedule

Weekly by default (Monday 06:00 UTC -- edit the `cron:` line in the workflow to change it), plus on-demand via **Actions -> Page description audit -> Run workflow**. It runs with `--apply`, then opens a PR with whatever changed using `peter-evans/create-pull-request`, with the report as the PR body and as a downloadable artifact. Nothing lands on your default branch without that PR being reviewed and merged by a person.

## Tuning

- **`description_fields`** -- add every frontmatter key your docs site might use for a page description; the first one found on a given page wins.
- **`min_len` / `max_len`** -- the target character-count window, used both as a heuristic check and as the target given to the model.
- **`verify_all_with_llm`** -- off by default, so descriptions that already pass the cheap heuristics never cost an API call. Turn it on for a one-off thorough pass if you suspect some descriptions are technically "compliant enough" per the heuristics but still don't read like Microsoft style (passive voice, wrong tone, doesn't actually match the page) -- every page gets a model judgment either way, at higher API cost.
- **`scripts/style_rules.py`** -- `JARGON_TERMS` is a plain Python set; add your own team's banned buzzwords.

## Known limitations

- **Frontmatter comments are not preserved.** The frontmatter block is parsed and re-serialized with PyYAML, which has no concept of comments -- if your frontmatter has inline comments, they'll be dropped when a description is added or changed on that page. Worth a glance in the PR diff.
- **HTML meta-description insertion is best-effort.** For plain `.html`/`.htm` pages with no `<head>` tag at all, the tool leaves the page alone rather than guessing at structure -- these will show up as errors/skipped in the report if they were missing a description.
- This tool never deletes a description or a page -- only adds or rewrites the description field.

## Files

```
scripts/
  audit_descriptions.py   # entrypoint -- run this
  doc_scanner.py            # finds pages, extracts existing description + title + body excerpt
  style_rules.py             # cheap heuristic compliance pre-filter
  llm_writer.py               # Anthropic API calls: generate / judge+rewrite
  field_writer.py              # writes the description back into frontmatter or a meta tag
config.example.yml
.github/workflows/page-description-audit.yml
```
