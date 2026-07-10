#!/usr/bin/env python3
"""
Page description audit for a docs repo.

Usage:
    python scripts/audit_descriptions.py --docs-root docs
    python scripts/audit_descriptions.py --docs-root docs --apply
    python scripts/audit_descriptions.py --config config.yml --apply

Dry run (no --apply) writes a report of what it *would* do -- what's
missing, what's non-compliant and why, and what the model would replace it
with -- without touching any files. --apply performs the writes.

Three outcomes per page:
  - MISSING   -- no description field found; one is generated and added.
  - REWRITTEN -- a description existed but didn't meet Microsoft style
                 (per the heuristics in style_rules.py, and/or the model's
                 own judgment); it's replaced.
  - LEFT ALONE -- a description existed and already complies; nothing changes.

See README.md for the GitHub Actions cron setup that runs this on a
schedule and opens a PR with the results.
"""

from __future__ import annotations

import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path

import yaml

import doc_scanner
import field_writer
import llm_writer
import style_rules

DEFAULT_CONFIG = {
    "docs_root": "docs",
    "exclude_dirs": ["node_modules", ".git", "dist", "build", ".next"],
    "description_fields": ["description", "page_description", "summary"],
    "min_len": 50,
    "max_len": 160,
    "verify_all_with_llm": False,
    "model": "claude-sonnet-4-6",
}


def load_config(path: str | None) -> dict:
    config = dict(DEFAULT_CONFIG)
    if path:
        with open(path) as f:
            user_config = yaml.safe_load(f) or {}
        config.update(user_config)
    return config


def is_git_repo(path: Path) -> bool:
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
    ).returncode == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--docs-root")
    parser.add_argument("--config")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", default=None)
    parser.add_argument("--api-key-env", default="ANTHROPIC_API_KEY")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.docs_root:
        config["docs_root"] = args.docs_root

    docs_root = Path(config["docs_root"]).resolve()
    if not docs_root.is_dir():
        sys.exit(f"docs root not found: {docs_root}")

    api_key = os.environ.get(args.api_key_env)
    if not api_key:
        sys.exit(
            f"{args.api_key_env} is not set. This tool needs the Anthropic API to write "
            "and evaluate descriptions -- there's no rules-only mode for that part "
            "(only the cheap pre-filter in style_rules.py runs without it, and that alone "
            "isn't enough to write or fix a description)."
        )

    pages = doc_scanner.scan(docs_root, config["description_fields"], set(config["exclude_dirs"]))

    added, rewritten, left_alone, errors = [], [], [], []

    for page in pages:
        if page.description is None:
            new_text = llm_writer.generate_description(
                page.title, page.body_excerpt, api_key, config["model"],
                config["min_len"], config["max_len"],
            )
            if new_text is None:
                errors.append((page.path, "description generation failed (API error)"))
                continue
            added.append((page, new_text))
            if args.apply:
                _write_description(page, new_text, config)
            continue

        heuristic = style_rules.check_compliance(page.description, config["min_len"], config["max_len"])
        if heuristic.compliant and not config["verify_all_with_llm"]:
            left_alone.append(page)
            continue

        result = llm_writer.check_and_fix(
            page.description, page.title, page.body_excerpt, heuristic.reasons,
            api_key, config["model"], config["min_len"], config["max_len"],
        )
        if result is None:
            errors.append((page.path, "compliance check failed (API error)"))
            continue

        was_compliant, final_text, reason = result
        if was_compliant and final_text.strip() == page.description.strip():
            left_alone.append(page)
        else:
            rewritten.append((page, final_text, heuristic.reasons, reason))
            if args.apply:
                _write_description(page, final_text, config)

    report_path = Path(args.report) if args.report else Path("reports") / f"description-audit-{datetime.date.today()}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    write_report(report_path, docs_root, added, rewritten, left_alone, errors, args.apply)

    print(f"Report written to {report_path}")
    print(f"{len(pages)} pages scanned")
    print(f"{len(added)} description(s) added")
    print(f"{len(rewritten)} description(s) {'rewritten' if args.apply else 'flagged for rewrite'}")
    print(f"{len(left_alone)} already compliant, left alone")
    if errors:
        print(f"{len(errors)} page(s) hit an API error -- see report")


def _write_description(page: doc_scanner.PageInfo, new_text: str, config: dict) -> None:
    text = page.path.read_text(encoding="utf-8")
    if page.description_source == "meta":
        new_content = field_writer.set_meta_description(text, new_text)
    else:
        field_name = page.frontmatter_field or config["description_fields"][0]
        new_content = field_writer.set_frontmatter_description(text, field_name, new_text)
    page.path.write_text(new_content, encoding="utf-8")


def write_report(path, docs_root, added, rewritten, left_alone, errors, applied):
    lines = [f"# Page description audit -- {datetime.date.today()}", ""]
    lines.append(f"Scanned {len(added) + len(rewritten) + len(left_alone) + len(errors)} page(s).")
    lines.append("")

    lines.append(f"## Descriptions added -- {len(added)}")
    lines.append("")
    if not added:
        lines.append("No pages were missing a description.")
    for page, new_text in added:
        rel = page.path.relative_to(docs_root)
        lines.append(f"### `{rel}`")
        lines.append(f"- {'Added' if applied else 'Would add'}: \"{new_text}\" ({len(new_text)} chars)")
        lines.append("")

    lines.append(f"## Descriptions {'rewritten' if applied else 'flagged for rewrite'} -- {len(rewritten)}")
    lines.append("")
    if not rewritten:
        lines.append("No existing descriptions needed changes.")
    for page, new_text, heuristic_reasons, model_reason in rewritten:
        rel = page.path.relative_to(docs_root)
        lines.append(f"### `{rel}`")
        lines.append(f"- Before: \"{page.description}\"")
        lines.append(f"- {'After' if applied else 'Proposed'}: \"{new_text}\" ({len(new_text)} chars)")
        if heuristic_reasons:
            lines.append(f"- Automated checks: {'; '.join(heuristic_reasons)}")
        if model_reason:
            lines.append(f"- Model's note: {model_reason}")
        lines.append("")

    lines.append(f"## Already compliant, left alone -- {len(left_alone)}")
    lines.append("")
    for page in left_alone:
        rel = page.path.relative_to(docs_root)
        lines.append(f"- `{rel}`")
    lines.append("")

    if errors:
        lines.append(f"## Errors -- {len(errors)}")
        lines.append("")
        for path_, msg in errors:
            lines.append(f"- `{path_}`: {msg}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
