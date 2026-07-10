"""
Two jobs, both via the Anthropic API:

1. Write a description from scratch for a page that doesn't have one.
2. Judge whether an existing description already follows Microsoft style
   and, if not, rewrite it -- used both for descriptions that failed the
   cheap heuristic checks in style_rules.py, and (if verify_all_with_llm is
   on) for descriptions that passed those checks but haven't had a model
   look at tone/voice/passive-construction issues a regex can't catch.

Both functions return None on any failure (bad API response, network
error, unparseable output) rather than raising, so one bad page doesn't
take down an entire audit run -- the caller logs it and moves on.
"""

from __future__ import annotations

import json
import re

STYLE_RULES_SUMMARY = """\
Microsoft Writing Style Guide rules for a page description (the short summary
shown in search results / at the top of a docs page):
- Sentence case: capitalize only the first word and proper nouns. Never Title Case.
- Concise and front-loaded: lead with the most important word or concept, aim for
  roughly 50-160 characters, one sentence.
- Plain, conversational language. No marketing jargon or fluff (avoid words like
  "leverage," "seamless," "cutting-edge," "revolutionary," "best-in-class").
  Contractions are fine.
- Active voice, present tense, written as if speaking directly to the reader
  when that fits naturally.
- End with a period, since it's a full sentence.
- Accurately describes what's actually on the page -- don't invent claims not
  supported by the page content given to you."""


def _extract_json(text: str) -> dict | None:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _get_client(api_key: str):
    import anthropic
    return anthropic.Anthropic(api_key=api_key)


def generate_description(
    page_title: str,
    body_excerpt: str,
    api_key: str,
    model: str = "claude-sonnet-4-6",
    min_len: int = 50,
    max_len: int = 160,
) -> str | None:
    """Write a new page description for a page that has none."""
    system = (
        f"{STYLE_RULES_SUMMARY}\n\n"
        "Respond with ONLY the description text -- no quotes, no preamble, no JSON, "
        "just the finished sentence."
    )
    user = (
        f"Page title: {page_title}\n\n"
        f"Page content (excerpt):\n{body_excerpt}\n\n"
        f"Write a {min_len}-{max_len} character page description for this page."
    )
    try:
        client = _get_client(api_key)
        response = client.messages.create(
            model=model, max_tokens=100, system=system,
            messages=[{"role": "user", "content": user}],
        )
    except Exception:
        return None

    text_blocks = [b.text for b in response.content if getattr(b, "type", None) == "text"]
    if not text_blocks:
        return None
    return text_blocks[0].strip().strip('"')


def check_and_fix(
    existing_description: str,
    page_title: str,
    body_excerpt: str,
    heuristic_reasons: list[str],
    api_key: str,
    model: str = "claude-sonnet-4-6",
    min_len: int = 50,
    max_len: int = 160,
) -> tuple[bool, str, str] | None:
    """Judge an existing description against Microsoft style and fix it if needed.

    Returns (was_compliant, final_text, explanation) -- final_text equals
    existing_description unchanged if it was already compliant. Returns
    None if the API call failed.
    """
    system = (
        f"{STYLE_RULES_SUMMARY}\n\n"
        "You'll be given a page's title, content, its current description, and "
        "(if any) issues already flagged by an automated check. Judge whether the "
        "current description fully complies with Microsoft style. If it does, "
        "return it unchanged. If it doesn't -- whether for the flagged reasons or "
        "anything else you notice (passive voice, doesn't actually match the page "
        "content, doesn't read like a friendly one-on-one explanation) -- rewrite "
        "it to comply while preserving its meaning and any exact product/feature "
        "names.\n\n"
        "Respond with ONLY a JSON object, no other text, in exactly this shape:\n"
        '{"compliant": true or false, "description": "the final description text", '
        '"reason": "one short sentence explaining your judgment"}'
    )
    flagged = "\n".join(f"- {r}" for r in heuristic_reasons) if heuristic_reasons else "(none flagged automatically)"
    user = (
        f"Page title: {page_title}\n\n"
        f"Page content (excerpt):\n{body_excerpt}\n\n"
        f"Current description: {existing_description}\n\n"
        f"Automated checks flagged:\n{flagged}\n\n"
        f"Target length if rewriting: {min_len}-{max_len} characters."
    )
    try:
        client = _get_client(api_key)
        response = client.messages.create(
            model=model, max_tokens=200, system=system,
            messages=[{"role": "user", "content": user}],
        )
    except Exception:
        return None

    text_blocks = [b.text for b in response.content if getattr(b, "type", None) == "text"]
    if not text_blocks:
        return None

    parsed = _extract_json(text_blocks[0])
    if not parsed or "description" not in parsed:
        return None

    was_compliant = bool(parsed.get("compliant", False))
    final_text = str(parsed["description"]).strip().strip('"')
    reason = str(parsed.get("reason", "")).strip()
    return was_compliant, final_text, reason
