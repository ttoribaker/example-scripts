"""
Duplicate detection for screenshots.

Two tiers, both surfaced for human review -- this script never deletes
anything, it only flags:

- Exact duplicates: identical file bytes (sha256). Usually the same image
  saved twice, or copy-pasted into two page folders.
- Near duplicates: perceptually similar but not byte-identical (a
  perceptual hash, via `imagehash`), e.g. the same UI re-screenshotted a
  pixel or two off, recompressed, or cropped slightly differently. These
  need a human eye -- a small hamming distance can mean "literally the same
  screenshot" or "two different states of the same screen," and only a
  person looking at both can tell which.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

try:
    import imagehash
    from PIL import Image
    _HAS_IMAGEHASH = True
except ImportError:
    _HAS_IMAGEHASH = False


@dataclass
class DuplicateGroup:
    kind: str  # "exact" or "near"
    paths: list[Path]
    distance: int | None = None  # max pairwise hamming distance, for "near" groups


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_duplicates(paths: list[Path], near_threshold: int = 5) -> list[DuplicateGroup]:
    groups: list[DuplicateGroup] = []

    # --- exact duplicates ---
    by_hash: dict[str, list[Path]] = {}
    for p in paths:
        try:
            by_hash.setdefault(sha256_of(p), []).append(p)
        except OSError:
            continue
    exact_dupe_paths = set()
    for _, group_paths in by_hash.items():
        if len(group_paths) > 1:
            groups.append(DuplicateGroup(kind="exact", paths=group_paths))
            exact_dupe_paths.update(group_paths)

    # --- near duplicates (skip anything already flagged as an exact dupe) ---
    if _HAS_IMAGEHASH:
        remaining = [p for p in paths if p not in exact_dupe_paths and p.suffix.lower() != ".svg"]
        phashes: dict[Path, "imagehash.ImageHash"] = {}
        for p in remaining:
            try:
                with Image.open(p) as img:
                    phashes[p] = imagehash.phash(img)
            except Exception:
                continue

        visited = set()
        items = list(phashes.items())
        for i, (path_a, hash_a) in enumerate(items):
            if path_a in visited:
                continue
            cluster = [path_a]
            max_dist = 0
            for path_b, hash_b in items[i + 1:]:
                if path_b in visited:
                    continue
                dist = hash_a - hash_b
                if dist <= near_threshold:
                    cluster.append(path_b)
                    max_dist = max(max_dist, dist)
            if len(cluster) > 1:
                visited.update(cluster)
                groups.append(DuplicateGroup(kind="near", paths=cluster, distance=max_dist))

    return groups
