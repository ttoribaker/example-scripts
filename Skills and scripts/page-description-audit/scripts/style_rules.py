"""
Cheap, rule-based pre-filter for whether a page description already looks
like it follows Microsoft style, before spending an API call on it.

These are deliberately the checks that can be done reliably without a
model: length, obvious Title Case, ALL CAPS, missing end punctuation on a
full sentence, and a fixed list of marketing-jargon words Microsoft's guide
explicitly steers away from ("no fluff", conversational over corporate).
Anything subtler -- genuine passive voice, tone, whether it actually reads
like a friendly one-on-one explanation -- is judged by the model instead
(see llm_writer.py), because a regex is a bad tool for "does this sound
warm and human." A description only skips the model entirely if it passes
every check here AND config.verify_all_with_llm is false.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Corporate/marketing filler Microsoft's guide explicitly wants replaced with
# plain language ("no fluff," "write like you speak"). Not exhaustive --
# add to this list as you see repeat offenders in your own docs.
JARGON_TERMS = {
    "leverage", "leveraging", "utilize", "utilizing", "synergy", "synergies",
    "seamless", "seamlessly", "cutting-edge", "state-of-the-art",
    "best-in-class", "revolutionary", "holistic", "robust", "paradigm",
    "disruptive", "game-changing", "turnkey", "unlock", "supercharge",
    "empower", "empowering", "world-class", "next-generation", "innovative",
}


@dataclass
class StyleCheckResult:
    compliant: bool
    reasons: list[str] = field(default_factory=list)


def _looks_like_title_case(text: str) -> bool:
    words = text.split()
    if len(words) < 4:
        return False
    # Ignore the first word (always capitalized regardless of case style)
    # and short connector words, which are legitimately lowercase in both
    # sentence case and title case and shouldn't count against either.
    connectors = {"a", "an", "and", "or", "the", "to", "of", "in", "on", "for", "with", "your", "you"}
    rest = [w for w in words[1:] if w.lower() not in connectors]
    if not rest:
        return False
    capitalized = [w for w in rest if w[:1].isupper()]
    return len(capitalized) / len(rest) > 0.6


def check_compliance(description: str, min_len: int = 50, max_len: int = 160) -> StyleCheckResult:
    text = description.strip()
    reasons: list[str] = []

    if len(text) < min_len:
        reasons.append(f"too short ({len(text)} chars) to be a useful, descriptive summary -- aim for {min_len}-{max_len}")
    if len(text) > max_len:
        reasons.append(f"too long ({len(text)} chars) -- Microsoft style favors concise, front-loaded text; aim for {min_len}-{max_len}")

    if text.isupper():
        reasons.append("written in ALL CAPS")
    elif _looks_like_title_case(text):
        reasons.append("looks like Title Case instead of Microsoft's sentence case (capitalize only the first word and proper nouns)")

    word_count = len(text.split())
    if word_count >= 4 and not text.endswith((".", "!", "?")):
        reasons.append("missing end punctuation -- full-sentence descriptions should end with a period in Microsoft style")

    found_jargon = sorted({
        term for term in JARGON_TERMS
        if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE)
    })
    if found_jargon:
        reasons.append(f"contains marketing jargon Microsoft style avoids: {', '.join(found_jargon)}")

    return StyleCheckResult(compliant=not reasons, reasons=reasons)
