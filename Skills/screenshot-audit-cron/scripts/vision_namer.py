"""
Uses the Anthropic API's vision capability to look at a screenshot and
propose a short, descriptive filename stem for it. Only called for images
that already failed the naming-rules check in naming_rules.py -- this is
deliberately the expensive/slow path, not something run on every image on
every run.
"""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path

from naming_rules import slugify

SYSTEM_PROMPT = (
    "You name screenshot files for a technical documentation site. Given an "
    "image and context about the page it appears on, respond with ONLY a short "
    "filename stem (no extension, no punctuation besides hyphens) that describes "
    "what the image shows -- lowercase, hyphen-separated, 2 to 6 words, e.g. "
    "'create-api-token-dialog' or 'project-settings-integrations-tab'. "
    "Do not include generic words like 'screenshot' or 'image'. Do not include "
    "the word 'the'. Do not explain your answer or add any other text -- "
    "respond with the filename stem and nothing else."
)


def _encode_image(path: Path) -> tuple[str, str]:
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type not in ("image/png", "image/jpeg", "image/gif", "image/webp"):
        mime_type = "image/png"
    data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
    return mime_type, data


def suggest_filename(
    image_path: Path,
    page_context: str,
    alt_text: str,
    api_key: str,
    model: str = "claude-sonnet-4-6",
) -> str | None:
    """Returns a slugified filename stem (no extension), or None if the
    call failed -- callers should fall back gracefully rather than crash
    a whole audit run over one bad image."""
    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "The 'anthropic' package is required for vision-based naming. "
            "Install it with: pip install anthropic"
        )

    if image_path.suffix.lower() == ".svg":
        # Vision models don't reliably parse SVG source as an image; skip
        # and let the caller fall back to alt-text-based naming instead.
        return None

    try:
        mime_type, image_data = _encode_image(image_path)
    except OSError:
        return None

    client = anthropic.Anthropic(api_key=api_key)

    context_lines = [f"Page section: {page_context}"]
    if alt_text:
        context_lines.append(f"Existing alt text: {alt_text}")
    context_text = "\n".join(context_lines)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=50,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": mime_type, "data": image_data}},
                    {"type": "text", "text": context_text},
                ],
            }],
        )
    except Exception:
        return None

    text_blocks = [b.text for b in response.content if getattr(b, "type", None) == "text"]
    if not text_blocks:
        return None

    return slugify(text_blocks[0])
