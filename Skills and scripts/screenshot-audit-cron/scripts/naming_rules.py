"""
Filename compliance rules for documentation screenshots.

There isn't a single literal "how to name an image file" chapter in the
Microsoft Writing Style Guide -- it's a prose style guide, not an asset
naming spec. What we apply here is the spirit of it (clear, concise,
unambiguous, no jargon-for-jargon's-sake) combined with the naming
conventions nearly every docs style guide converges on (Write the Docs,
common web/DAM practice): lowercase, hyphen-separated, descriptive,
no auto-generated or placeholder names.

Everything here is deliberately conservative: a filename is only flagged
as non-compliant if it clearly fails one of these checks, not because it's
merely "not perfect." The goal is to catch real problems (auto-generated
names, generic names, duplicates-in-waiting) without churning through a
repo renaming files that are already fine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Words that carry no descriptive information on their own. A filename made
# up mostly of these tells a reader nothing about what the image shows.
GENERIC_TERMS = {
    "image", "img", "screenshot", "screen-shot", "screencap", "screen-cap",
    "photo", "pic", "picture", "graphic", "asset", "file", "untitled",
    "new", "final", "copy", "draft", "temp", "test", "sample", "misc",
    "download", "downloaded", "unnamed", "capture",
}

# Patterns that indicate an auto-generated name from an OS/tool rather than
# a human-chosen descriptive one. These are the highest-confidence flags --
# if a name matches one of these, it's essentially never going to be
# descriptive of content.
AUTO_GENERATED_PATTERNS = [
    re.compile(r"^screen[\s_-]?shot[\s_-]", re.IGNORECASE),
    re.compile(r"^img[\s_-]?\d+", re.IGNORECASE),
    re.compile(r"^dsc[\s_-]?\d+", re.IGNORECASE),
    re.compile(r"^image[\s_-]?\d+$", re.IGNORECASE),
    re.compile(r"^\d{4}-\d{2}-\d{2}[\s_-]+at[\s_-]", re.IGNORECASE),  # "2024-01-01 at 10.23.45"
    re.compile(r"^untitled[\s_-]?\d*", re.IGNORECASE),
    re.compile(r"\(\d+\)$"),          # "diagram (1)"
    re.compile(r"^copy[\s_-]of[\s_-]", re.IGNORECASE),
    re.compile(r"^clipboard[\s_-]?image", re.IGNORECASE),
    re.compile(r"^[a-f0-9]{16,}$", re.IGNORECASE),  # bare hash/uuid, no words at all
]

WORD_SPLIT_RE = re.compile(r"[-_ ]+")


@dataclass
class ComplianceResult:
    compliant: bool
    reasons: list[str] = field(default_factory=list)


def _stem(filename: str) -> str:
    return Path(filename).stem


def _words(stem: str) -> list[str]:
    return [w for w in WORD_SPLIT_RE.split(stem) if w]


def check_compliance(filename: str, min_words: int = 2, max_length: int = 60) -> ComplianceResult:
    """Check a filename (basename, extension included) against the naming rules.

    Returns a ComplianceResult with compliant=False and human-readable reasons
    for every rule that failed, so the audit report can explain *why* -- not
    just flag the file.
    """
    reasons: list[str] = []
    stem = _stem(filename)

    for pattern in AUTO_GENERATED_PATTERNS:
        if pattern.search(stem):
            reasons.append("looks auto-generated (matches a default OS/tool naming pattern)")
            break

    if filename != filename.lower():
        reasons.append("contains uppercase characters (should be all lowercase)")

    if " " in filename:
        reasons.append("contains spaces (should use hyphens)")

    if "_" in stem:
        reasons.append("uses underscores instead of hyphens")

    words = _words(stem)
    meaningful_words = [w for w in words if w.lower() not in GENERIC_TERMS and not w.isdigit()]
    if len(meaningful_words) < min_words:
        reasons.append(
            f"not descriptive enough -- only {len(meaningful_words)} meaningful word(s) "
            f"found (want at least {min_words})"
        )

    if words and all(w.lower() in GENERIC_TERMS or w.isdigit() for w in words):
        reasons.append("filename is made up entirely of generic terms and/or numbers")

    if len(stem) > max_length:
        reasons.append(f"filename is unusually long ({len(stem)} chars, keep it under {max_length})")

    if len(stem) <= 2:
        reasons.append("filename is too short to be descriptive")

    # de-duplicate while preserving order
    seen = set()
    deduped = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            deduped.append(r)

    return ComplianceResult(compliant=not deduped, reasons=deduped)


def slugify(text: str, max_words: int = 6) -> str:
    """Turn arbitrary text (e.g. a model's suggested description) into a
    compliant kebab-case filename stem."""
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    words = [w for w in text.split("-") if w]
    words = [w for w in words if w not in GENERIC_TERMS] or words  # don't strip to nothing
    return "-".join(words[:max_words]) or "untitled-screenshot"


def unique_filename(directory: Path, stem: str, extension: str) -> str:
    """Return a filename guaranteed not to collide with an existing file in
    `directory`, appending -2, -3, ... if needed."""
    candidate = f"{stem}{extension}"
    if not (directory / candidate).exists():
        return candidate
    n = 2
    while (directory / f"{stem}-{n}{extension}").exists():
        n += 1
    return f"{stem}-{n}{extension}"
