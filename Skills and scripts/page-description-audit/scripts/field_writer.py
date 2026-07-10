"""
Writes a description back into a page file, in whichever place it belongs:

- Frontmatter (`description: ...` or whatever field name matched): the
  frontmatter block is parsed with PyYAML, the field is set, and the block
  is re-serialized. This preserves field order for anything already there
  (Python dicts, and PyYAML's default loader, keep insertion order) but it
  does NOT preserve comments inside the frontmatter block -- PyYAML has no
  concept of comments. If your frontmatter relies on comments, expect this
  tool to drop them; that's the one thing worth a manual check in the PR
  diff before merging.
- HTML `<meta name="description">`: a plain regex replace/insert, since
  there's no frontmatter block to parse. Inserted right after `<head>` (or
  after an existing `<title>` tag, if there is one) when no meta tag exists
  yet.
"""

from __future__ import annotations

import re

import yaml

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
HTML_META_DESC_RE = re.compile(
    r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\'][^"\']*["\'][^>]*/?>',
    re.IGNORECASE,
)
HTML_HEAD_RE = re.compile(r"(<head[^>]*>)", re.IGNORECASE)
HTML_TITLE_TAG_RE = re.compile(r"(<title[^>]*>.*?</title>)", re.IGNORECASE | re.DOTALL)


def set_frontmatter_description(text: str, field_name: str, new_value: str) -> str:
    """Set (or add) `field_name` in the file's frontmatter block to
    `new_value`. If the file has no frontmatter block yet, one is created."""
    match = FRONTMATTER_RE.match(text)
    if match:
        try:
            data = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            data = {}
        if not isinstance(data, dict):
            data = {}
        data[field_name] = new_value
        new_block = yaml.dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False, width=1000)
        return f"---\n{new_block}---\n" + text[match.end():]
    else:
        new_block = yaml.dump({field_name: new_value}, sort_keys=False, allow_unicode=True, default_flow_style=False, width=1000)
        return f"---\n{new_block}---\n\n" + text


def set_meta_description(text: str, new_value: str) -> str:
    """Set (or add) an HTML `<meta name="description">` tag."""
    escaped = new_value.replace('"', "&quot;")
    new_tag = f'<meta name="description" content="{escaped}">'

    if HTML_META_DESC_RE.search(text):
        return HTML_META_DESC_RE.sub(new_tag, text, count=1)

    title_match = HTML_TITLE_TAG_RE.search(text)
    if title_match:
        return text[:title_match.end()] + "\n    " + new_tag + text[title_match.end():]

    head_match = HTML_HEAD_RE.search(text)
    if head_match:
        return text[:head_match.end()] + "\n    " + new_tag + text[head_match.end():]

    # No <head> at all -- give up gracefully rather than guessing at structure.
    return text
