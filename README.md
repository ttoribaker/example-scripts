# example-scripts
A collection of scripts and skills built to showcase how I use AI for technical documentation and more.

## Contents
- **ms-style-guide-check**: This skill reviews and edits developer and technical documentation for alignment with the [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide). It covers READMEs, API references, SDK and CLI docs, developer guides, release notes, reader-facing code comments, and error messages. To use this skill with your own technical documentation, prompt Claude to take in your company style guide for technical docs, and ask it to compare and unify any differences, with you as a reviewer.
- **docs-screenshot-audit**: This skill reviews screenshots and other images used in technical documentation to analyse whether they meet accessibility criteria, if they are reflective of the text around them, and if any confidential ifnormation is exposed. It provides a Pass > Fail feedback and recommends fixes. This is useful when refining a documentation draft that contains images.
- **screenshot-audit-cron**: This script runs on a weekly GitHub Action schedule to determine if any images or screenshots in your repository have bad or incorrect file names. It provides new filenames that meet general guidelines from the Microsoft Writing Style Guide.

## Microsoft Style Guide documentation checker

This skill reviews and edits developer and technical documentation for alignment with the [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide). It covers READMEs, API references, SDK and CLI docs, developer guides, release notes, reader-facing code comments, and error messages.

Claude analyzes text in five passes:
- Voice and tone
- Word choice and grammar
- Sentence and document structure
- Punctuation and capitalization
- Bias-free language

It then returns an edited version of the document, a compliance score, and a categorized list of changes with rule citations.

The skill scales its analysis to the text: short strings like error messages get a lighter pass (voice/tone and punctuation only), while full documents get all five reference checks. It also activates when drafting new developer documentation from scratch, applying Microsoft style from the start rather than correcting it after the fact.

**Scope:** developer and technical documentation only. It does not cover marketing copy or general business writing.

**Trigger phrases:** "review this for style," "clean up these docs," "align with Microsoft style," "does this sound consistent/professional," or any request to draft new technical docs in Microsoft style.

## Documentation screenshot reviewer

A Claude skill for reviewing screenshots in technical documentation before they're published.

Audits screenshots and other images embedded in technical documentation — docs sites, draft documentation, PRDs, Google Docs, Word docs, or standalone uploaded screenshots — and scores each one Pass/Warning/Fail across three dimensions:
- Accessibility (alt text quality, color-only signaling, legibility, captions)
- Accuracy (whether the image matches what the surrounding text describes)
- Confidential information exposure (real emails, names, company identifiers, API keys/tokens, internal URLs).

For anything short of a clean Pass on confidentiality, it gives specific redaction guidance: what to crop, blur, or retake with a demo account, rather than just flagging that a problem exists. Each screenshot gets an overall verdict: Use as-is, Use with fixes, or Do not use.

**Scope:** Single uploaded screenshots, images extracted from docx/PDF/PRD/Google Doc files, and images referenced on a live docs URL (accessibility and partial accuracy checks via page markup; full accuracy/confidentiality checks require the actual image file, since arbitrary external sites can't be pixel-inspected). Does not rename files, edit documents, or take any action on the user's behalf — it's a review/scoring tool only.

**Trigger phrases:** "review/audit/check/QA this screenshot," "is this screenshot safe to publish," "is this ready to ship," a pasted docs URL with a question about its images, or an uploaded PRD/Word doc/Google Doc with a request to check its screenshots before finalizing — including cases where the user doesn't explicitly say "accessibility," "confidential," or "audit."

## Documentation screenshot filename script

Runs on a weekly GitHub Actions schedule (refer to `.github/workflows/screenshot-audit.yml`) to keep documentation screenshots in good shape. Each run scans all docs pages, counts images per page grouping, flags non-descriptive or auto-generated filenames (for example, `Screenshot 2024-01-01 at 10.23.45.png`, `IMG_4821.png`), renames them using Claude's vision API to generate descriptive kebab-case names, updates every reference to the renamed files, and flags exact or near-duplicate screenshots for manual review. Results are opened as a PR for review rather than pushed directly to `main`.

### Setup

1. Files already in place in this repo:
   - `scripts/`: the audit tool (`audit_screenshots.py`, `doc_scanner.py`, `naming_rules.py`, `vision_namer.py`, `duplicates.py`)
   - `.github/workflows/screenshot-audit.yml`: the scheduled workflow
   - `requirements.txt`: Python dependencies
   - `config.example.yml`: example config
2. Copy `config.example.yml` → `config.yml` in the repo root, and set `docs_root` (and `images_root` if images live outside your docs folder) for this repo's structure.
3. Add an `ANTHROPIC_API_KEY` secret: **Settings → Secrets and variables → Actions → New repository secret**.
4. Commit `config.yml`. The workflow runs automatically every Monday (or amend to a schedule or your choosing), or on demand through **Actions → Screenshot audit → Run workflow**.

### Running locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

# dry run — writes a report, changes nothing
python scripts/audit_screenshots.py --config config.yml

# apply renames + reference updates
python scripts/audit_screenshots.py --config config.yml --apply
```

Full details, config options, and how to tune the naming rules are in `README.md` in this repo / the tool's own docs.
