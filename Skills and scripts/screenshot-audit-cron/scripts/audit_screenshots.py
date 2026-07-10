#!/usr/bin/env python3
"""
Screenshot naming & duplicate audit for a docs repo.

Usage:
    python scripts/audit_screenshots.py --docs-root docs
    python scripts/audit_screenshots.py --docs-root docs --apply
    python scripts/audit_screenshots.py --config config.yml --apply

Run without --apply first. It's a dry run: it scans everything, calls the
Anthropic API to preview what each non-compliant file *would* be renamed to,
and writes a report -- but touches nothing on disk. Only --apply performs
the actual renames, reference rewrites, and (if run inside a git repo)
stages the changes with `git mv` so history is preserved.

See README.md for the GitHub Actions cron setup that runs this on a
schedule and opens a PR with the results, rather than pushing straight to
main -- renames and vision-model suggestions should get a human glance
before merging, even though nothing here is destructive.
"""

from __future__ import annotations

import argparse
import datetime
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

import yaml

import doc_scanner
import duplicates
import naming_rules
import vision_namer

DEFAULT_CONFIG = {
    "docs_root": "docs",
    "images_root": None,
    "group_depth": 1,
    "exclude_dirs": ["node_modules", ".git", "dist", "build", ".next"],
    "min_words": 2,
    "max_filename_length": 60,
    "near_duplicate_threshold": 5,
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
    return (path / ".git").exists() or subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
    ).returncode == 0


def git_mv(repo_root: Path, old: Path, new: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "mv", str(old), str(new)],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def update_references(doc_files: set[Path], old_src: str, new_src: str) -> list[Path]:
    """Replace every occurrence of `old_src` with `new_src` across the given
    doc files. Returns the list of files actually modified."""
    changed = []
    for doc_file in doc_files:
        try:
            text = doc_file.read_text(encoding="utf-8")
        except OSError:
            continue
        if old_src not in text:
            continue
        doc_file.write_text(text.replace(old_src, new_src), encoding="utf-8")
        changed.append(doc_file)
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--docs-root", help="Root directory containing documentation pages")
    parser.add_argument("--images-root", help="Root directory containing image assets, if different from docs-root")
    parser.add_argument("--config", help="Path to a YAML config file (see config.example.yml)")
    parser.add_argument("--apply", action="store_true", help="Actually rename files and update references (default: dry run / report only)")
    parser.add_argument("--report", default=None, help="Path to write the markdown report to")
    parser.add_argument("--api-key-env", default="ANTHROPIC_API_KEY", help="Env var holding the Anthropic API key")
    parser.add_argument("--skip-vision", action="store_true", help="Flag non-compliant names without generating suggested replacements (no API calls)")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.docs_root:
        config["docs_root"] = args.docs_root
    if args.images_root:
        config["images_root"] = args.images_root

    docs_root = Path(config["docs_root"]).resolve()
    images_root = Path(config["images_root"]).resolve() if config.get("images_root") else None
    exclude_dirs = set(config["exclude_dirs"])

    if not docs_root.is_dir():
        sys.exit(f"docs root not found: {docs_root}")

    repo_root = docs_root
    while repo_root != repo_root.parent and not (repo_root / ".git").exists():
        repo_root = repo_root.parent
    in_git_repo = (repo_root / ".git").exists()

    api_key = os.environ.get(args.api_key_env)
    use_vision = not args.skip_vision and bool(api_key)
    if not args.skip_vision and not api_key:
        print(f"warning: {args.api_key_env} not set -- non-compliant files will be flagged but no rename will be suggested", file=sys.stderr)

    # --- 1. Scan docs, extract image references and page groupings ---
    refs = doc_scanner.scan(docs_root, images_root, config["group_depth"], exclude_dirs)

    page_group_counts: dict[str, int] = defaultdict(int)
    image_to_refs: dict[Path, list[doc_scanner.ImageReference]] = defaultdict(list)
    unresolved: list[str] = []

    for ref in refs:
        page_group_counts[ref.page_group] += 1
        if ref.resolved_path is not None:
            image_to_refs[ref.resolved_path].append(ref)
        elif not ref.src.startswith(("http://", "https://", "data:")):
            unresolved.append(f"{ref.doc_file}: could not resolve '{ref.src}'")

    unique_images = sorted(image_to_refs.keys())

    # --- 2. Naming compliance + (optionally) vision-based rename suggestions ---
    compliance_report = []  # list of dicts for the report
    renames: list[tuple[Path, Path]] = []  # (old_path, new_path)

    for image_path in unique_images:
        result = naming_rules.check_compliance(
            image_path.name, min_words=config["min_words"], max_length=config["max_filename_length"]
        )
        if result.compliant:
            continue

        refs_for_image = image_to_refs[image_path]
        page_context = ", ".join(sorted({r.page_group for r in refs_for_image}))
        alt_text = next((r.alt for r in refs_for_image if r.alt), "")

        suggested_name = None
        if use_vision:
            stem = vision_namer.suggest_filename(image_path, page_context, alt_text, api_key, config["model"])
            if stem:
                suggested_name = naming_rules.unique_filename(image_path.parent, stem, image_path.suffix)

        entry = {
            "path": image_path,
            "pages": sorted({str(r.doc_file.relative_to(docs_root)) for r in refs_for_image}),
            "reasons": result.reasons,
            "suggested_name": suggested_name,
        }
        compliance_report.append(entry)

        if args.apply and suggested_name:
            renames.append((image_path, image_path.parent / suggested_name))

    # --- 3. Apply renames + update references, if requested ---
    applied_renames = []
    if args.apply and renames:
        all_doc_files = {r.doc_file for r in refs}
        for old_path, new_path in renames:
            moved = False
            if in_git_repo:
                moved = git_mv(repo_root, old_path, new_path)
            if not moved:
                old_path.rename(new_path)

            old_refs = image_to_refs[old_path]
            for old_src in {r.src for r in old_refs}:
                new_src = old_src.replace(old_path.name, new_path.name)
                update_references(all_doc_files, old_src, new_src)

            applied_renames.append((old_path, new_path))

    # --- 4. Duplicate detection (run on the post-rename set of paths) ---
    final_image_paths = [new if any(new == n for _, n in applied_renames) else old
                          for old in unique_images
                          for new in [next((n for o, n in applied_renames if o == old), old)]]
    dup_groups = duplicates.find_duplicates(final_image_paths, config["near_duplicate_threshold"])

    # --- 5. Write report ---
    report_path = Path(args.report) if args.report else Path("reports") / f"screenshot-audit-{datetime.date.today()}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    write_report(report_path, page_group_counts, compliance_report, applied_renames, dup_groups, unresolved, docs_root, args.apply)

    print(f"Report written to {report_path}")
    print(f"{len(unique_images)} unique images across {len(page_group_counts)} page groupings")
    print(f"{len(compliance_report)} non-compliant filenames found")
    if args.apply:
        print(f"{len(applied_renames)} files renamed")
    print(f"{len(dup_groups)} duplicate group(s) flagged for review")


def write_report(path, page_group_counts, compliance_report, applied_renames, dup_groups, unresolved, docs_root, applied):
    lines = [f"# Screenshot audit -- {datetime.date.today()}", ""]

    lines.append("## Images per page grouping")
    lines.append("")
    lines.append("| Page grouping | Image count |")
    lines.append("|---|---|")
    for group, count in sorted(page_group_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"| {group} | {count} |")
    lines.append("")

    lines.append(f"## Naming compliance -- {len(compliance_report)} issue(s)")
    lines.append("")
    if not compliance_report:
        lines.append("All screenshot filenames meet the naming rules. Nothing to do here.")
    for entry in compliance_report:
        rel = entry["path"].relative_to(docs_root)
        lines.append(f"### `{rel}`")
        lines.append(f"- Referenced on: {', '.join(entry['pages'])}")
        lines.append(f"- Issues: {'; '.join(entry['reasons'])}")
        if entry["suggested_name"]:
            verb = "Renamed to" if applied else "Suggested rename"
            lines.append(f"- {verb}: `{entry['suggested_name']}`")
        else:
            lines.append("- No rename suggestion available (vision API skipped or failed -- needs a manual look)")
        lines.append("")

    if applied_renames:
        lines.append("## Renames applied")
        lines.append("")
        for old, new in applied_renames:
            lines.append(f"- `{old.name}` -> `{new.name}`")
        lines.append("")

    lines.append(f"## Duplicates flagged for review -- {len(dup_groups)} group(s)")
    lines.append("")
    if not dup_groups:
        lines.append("No exact or near-duplicate screenshots found.")
    for group in dup_groups:
        kind_label = "Exact duplicate" if group.kind == "exact" else f"Possible duplicate (hash distance <= {group.distance})"
        lines.append(f"- **{kind_label}:**")
        for p in group.paths:
            try:
                rel = p.relative_to(docs_root)
            except ValueError:
                rel = p
            lines.append(f"  - `{rel}`")
    lines.append("")

    if unresolved:
        lines.append("## Unresolved image references")
        lines.append("")
        lines.append("These were referenced in a doc but the file couldn't be found on disk -- likely a broken link, worth checking separately:")
        for u in unresolved:
            lines.append(f"- {u}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
