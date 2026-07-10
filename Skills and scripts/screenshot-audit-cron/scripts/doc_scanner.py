"""
Walks a docs repo, finds pages, and extracts every image reference in them
along with which "page grouping" (section) each page belongs to.

Deliberately regex-based rather than a full Markdown/HTML/MDX parser --
docs repos use enough different flavors (Markdown, MDX with JSX image
components, plain HTML) that a single strict parser would miss things. The
patterns below cover the common cases; extend IMAGE_PATTERNS if your repo
uses something unusual (e.g. a custom <Screenshot src="..."> component).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

DOC_EXTENSIONS = {".md", ".mdx", ".html", ".htm"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}

# Each pattern must produce two named groups: `src` and (optionally) `alt`.
IMAGE_PATTERNS = [
    re.compile(r'!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:\s+"[^"]*")?\)'),          # ![alt](src "title")
    re.compile(r'<img[^>]*\bsrc=["\'](?P<src>[^"\']+)["\'][^>]*?(?:\balt=["\'](?P<alt>[^"\']*)["\'])?[^>]*>', re.IGNORECASE),
    re.compile(r'<[A-Za-z][\w.]*[^>]*\bsrc=["\'](?P<src>[^"\']+)["\'][^>]*?(?:\balt=["\'](?P<alt>[^"\']*)["\'])?[^>]*/?>'),  # generic JSX <Image src="..">
]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?\n)---\s*\n", re.DOTALL)
FRONTMATTER_FIELD_RE = re.compile(r"^(category|section|group)\s*:\s*[\"']?(.+?)[\"']?\s*$", re.IGNORECASE | re.MULTILINE)


@dataclass
class ImageReference:
    src: str                 # raw path/URL as written in the doc
    alt: str
    doc_file: Path
    page_group: str
    resolved_path: Path | None   # None if external (http/https) or unresolvable


def find_doc_files(root: Path, exclude_dirs: set[str] | None = None) -> list[Path]:
    exclude_dirs = exclude_dirs or {"node_modules", ".git", "dist", "build", ".next"}
    files = []
    for path in root.rglob("*"):
        if path.suffix.lower() in DOC_EXTENSIONS and not any(part in exclude_dirs for part in path.parts):
            files.append(path)
    return sorted(files)


def get_page_group(doc_file: Path, docs_root: Path, group_depth: int = 1) -> str:
    """Prefer explicit frontmatter (category/section/group); fall back to
    directory structure at `group_depth` levels below docs_root."""
    try:
        text = doc_file.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        text = ""

    fm_match = FRONTMATTER_RE.match(text)
    if fm_match:
        field_match = FRONTMATTER_FIELD_RE.search(fm_match.group(1))
        if field_match:
            return field_match.group(2).strip()

    rel = doc_file.relative_to(docs_root)
    parts = rel.parts[:-1]  # drop the filename itself
    if not parts:
        return "(root)"
    return "/".join(parts[:group_depth])


def resolve_image_path(src: str, doc_file: Path, docs_root: Path, images_root: Path | None) -> Path | None:
    parsed = urlparse(src)
    if parsed.scheme in ("http", "https", "data"):
        return None  # external or inline -- nothing on disk to audit/rename

    src_path = Path(parsed.path)
    candidates = []
    if src_path.is_absolute():
        # Path relative to docs_root or images_root, as written from the site root.
        candidates.append(docs_root / src_path.relative_to(src_path.anchor))
        if images_root:
            candidates.append(images_root / src_path.relative_to(src_path.anchor))
    else:
        candidates.append((doc_file.parent / src_path).resolve())
        if images_root:
            candidates.append((images_root / src_path).resolve())
        candidates.append((docs_root / src_path).resolve())

    for c in candidates:
        if c.exists() and c.suffix.lower() in IMAGE_EXTENSIONS:
            return c
    return None


def scan(docs_root: Path, images_root: Path | None = None, group_depth: int = 1,
          exclude_dirs: set[str] | None = None) -> list[ImageReference]:
    refs: list[ImageReference] = []
    for doc_file in find_doc_files(docs_root, exclude_dirs):
        try:
            text = doc_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        group = get_page_group(doc_file, docs_root, group_depth)

        seen_spans = set()
        for pattern in IMAGE_PATTERNS:
            for m in pattern.finditer(text):
                if m.span() in seen_spans:
                    continue
                seen_spans.add(m.span())
                src = m.group("src")
                if not src or Path(urlparse(src).path).suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                alt = (m.groupdict().get("alt") or "").strip()
                resolved = resolve_image_path(src, doc_file, docs_root, images_root)
                refs.append(ImageReference(src=src, alt=alt, doc_file=doc_file,
                                            page_group=group, resolved_path=resolved))
    return refs
