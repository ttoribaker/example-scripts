"""
Finds documentation pages and pulls out three things per page:

- The existing "page description" field, if any -- checked in frontmatter
  first (YAML block at the top of .md/.mdx files, e.g. `description:`), then
  an HTML `<meta name="description" content="...">` tag as a fallback for
  plain HTML pages.
- The page title (frontmatter `title:`, first `# heading`, or `<title>`/`<h1>`).
- A short excerpt of the body content, used as context for the model when
  it writes or rewrites a description -- not the whole page, just enough to
  ground the summary in what the page actually covers.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

DOC_EXTENSIONS = {".md", ".mdx", ".html", ".htm"}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
MD_HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
HTML_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
HTML_H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
HTML_META_DESC_RE = re.compile(
    r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\'](?P<content>[^"\']*)["\'][^>]*/?>',
    re.IGNORECASE,
)
HTML_TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class PageInfo:
    path: Path
    title: str
    description: str | None
    description_source: str | None  # "frontmatter" | "meta" | None
    frontmatter_field: str | None   # which frontmatter key held it, if frontmatter
    body_excerpt: str
    is_html: bool


def find_doc_files(root: Path, exclude_dirs: set[str] | None = None) -> list[Path]:
    exclude_dirs = exclude_dirs or {"node_modules", ".git", "dist", "build", ".next"}
    files = []
    for path in root.rglob("*"):
        if path.suffix.lower() in DOC_EXTENSIONS and not any(part in exclude_dirs for part in path.parts):
            files.append(path)
    return sorted(files)


def _clean_excerpt(text: str, limit: int = 1200) -> str:
    text = HTML_TAG_RE.sub(" ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)          # markdown images
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)        # markdown links -> link text
    text = re.sub(r"[`*_#>]+", " ", text)                        # markdown formatting chars
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def load_page(path: Path, description_fields: list[str]) -> PageInfo:
    text = path.read_text(encoding="utf-8", errors="ignore")
    is_html = path.suffix.lower() in (".html", ".htm")

    description = None
    description_source = None
    frontmatter_field = None
    title = None
    body_for_excerpt = text

    fm_match = FRONTMATTER_RE.match(text)
    frontmatter_data = {}
    if fm_match:
        try:
            frontmatter_data = yaml.safe_load(fm_match.group(1)) or {}
        except yaml.YAMLError:
            frontmatter_data = {}
        body_for_excerpt = text[fm_match.end():]

        for field in description_fields:
            if isinstance(frontmatter_data, dict) and frontmatter_data.get(field):
                description = str(frontmatter_data[field])
                description_source = "frontmatter"
                frontmatter_field = field
                break

        if isinstance(frontmatter_data, dict) and frontmatter_data.get("title"):
            title = str(frontmatter_data["title"])

    if description is None and is_html:
        meta_match = HTML_META_DESC_RE.search(text)
        if meta_match and meta_match.group("content").strip():
            description = meta_match.group("content").strip()
            description_source = "meta"

    if title is None:
        heading_match = MD_HEADING_RE.search(body_for_excerpt)
        if heading_match:
            title = heading_match.group(1).strip()
        elif is_html:
            h1_match = HTML_H1_RE.search(text)
            title_match = HTML_TITLE_RE.search(text)
            if h1_match:
                title = re.sub(r"\s+", " ", h1_match.group(1)).strip()
            elif title_match:
                title = re.sub(r"\s+", " ", title_match.group(1)).strip()
    if title is None:
        title = path.stem.replace("-", " ").replace("_", " ").title()

    return PageInfo(
        path=path,
        title=title,
        description=description,
        description_source=description_source,
        frontmatter_field=frontmatter_field,
        body_excerpt=_clean_excerpt(body_for_excerpt),
        is_html=is_html,
    )


def scan(docs_root: Path, description_fields: list[str], exclude_dirs: set[str] | None = None) -> list[PageInfo]:
    return [load_page(p, description_fields) for p in find_doc_files(docs_root, exclude_dirs)]
