---
name: ms-style-guide-check
description: Analyzes and edits developer/technical documentation (READMEs, API references, SDK docs, CLI help text, developer guides, release notes, reader-facing code comments, error messages) for alignment with the Microsoft Writing Style Guide (learn.microsoft.com/en-us/style-guide). Checks tone/voice, word choice, grammar, sentence structure, punctuation, capitalization, and bias-free language, and produces a compliance score. Use whenever the user asks to review, edit, proofread, or "clean up" developer/technical docs for style, asks to align docs with Microsoft style, or wants a style/tone/grammar pass on technical writing — even without naming the guide explicitly, e.g. "docs style," "API docs style," "sound more professional/consistent." Also use when drafting new developer docs from scratch, to write them in Microsoft style. Not for marketing copy or general business writing — outside this skill's scope.
---

# Microsoft Style Guide Documentation Checker

Analyzes developer and technical documentation against the Microsoft Writing Style Guide and produces an edited version, a compliance score, and a categorized, rule-cited list of the changes made.

**Scope: developer/technical documentation only** — READMEs, API references, SDK/CLI docs, developer guides, release notes, reader-facing code comments, error messages. If the user asks for a style pass on marketing copy, general business writing, or other non-technical content, say this skill is scoped to technical documentation and offer a general style pass instead.

## Instructions

### Step 1: Get the text

If the text isn't already in context, read it from the uploaded file. If the user references a file path, read that file directly rather than asking them to paste it.

### Step 2: Load the relevant reference files

Don't load every reference for a two-sentence UI string. Match the load to the size and nature of the text:

- **Short text** (a sentence, a UI string, an error message, a single paragraph): load `references/voice-and-tone.md` and `references/punctuation-and-capitalization.md`.
- **Full documents** (READMEs, articles, guides, multi-section docs): load all five files in `references/`.
- **Bias/inclusive-language-specific requests**: load `references/bias-free-language.md` regardless of length.

Expected output of this step: you know which reference files apply and have read them before editing anything.

### Step 3: Analyze in order

Work through these passes in sequence — later passes assume earlier ones are already stable, so don't jump to punctuation before voice and grammar are settled:

1. **Voice and tone** — `references/voice-and-tone.md` (contractions, second person, active voice, warmth vs. jargon)
2. **Word choice and grammar** — `references/word-choice-and-grammar.md` (verb tense, weak constructions, prepositions/modifiers, common terminology)
3. **Sentence and document structure** — `references/sentence-and-document-structure.md` (scannability, lists vs. paragraphs, sentence length, heading style)
4. **Punctuation and capitalization** — `references/punctuation-and-capitalization.md` (sentence-style capitalization, Oxford comma, spacing, end punctuation)
5. **Bias-free and inclusive language** — `references/bias-free-language.md` (gender-neutral language, disability language, inclusive terms)

### Step 4: Apply guardrails while editing

- Never edit text inside code blocks, inline code spans, file paths, or literal command/output samples.
- Don't flatten domain terminology — API names, code identifiers, product names, and CLI flags are not style violations even if they break capitalization or word-choice rules.
- Preserve the author's meaning and technical precision. Microsoft style favors brevity, but cutting a word that changes what a step means is a bug, not an edit.
- If a construction is ambiguous rather than clearly wrong (e.g., passive voice that may be intentional, such as in a security disclosure), flag it as a suggestion rather than silently rewriting it.

### Step 5: Score compliance

Score the **original** text (before your edits), not the revised version — the score reflects how compliant the input was, and the revision is what fixes it.

Score each category out of 20 and sum to a total out of 100:

| Category | Points |
|---|---|
| Tone and voice | /20 |
| Word choice and grammar | /20 |
| Sentence and document structure | /20 |
| Punctuation and capitalization | /20 |
| Bias-free language | /20 |

Scoring approach: start each category at 20 and deduct for violations found in that pass — roughly 1–3 points per instance depending on severity (a single missed Oxford comma is minor; pervasive passive voice throughout a doc is major). Use judgment, not a rigid formula — the score should track how much a technical editor would flag, not just a violation count. If a category wasn't loaded (e.g., short text skipped structure/bias checks), mark it "N/A" and score out of the remaining categories instead of 100 — don't award free points for unchecked categories.

### Step 6: Produce the output

Two deliverables, every time:

1. A **revised version** of the text with edits applied.
2. A **change summary**, grouped by category, each entry showing original → revision and a one-line reason that cites the specific rule (not just "improved clarity").

Expected output of this step: see [Output format](#output-format) below.

## Output format

```markdown
## Compliance score: [total]/100 (or [total]/[max] if a category was skipped)

| Category | Score |
|---|---|
| Tone and voice | /20 |
| Word choice and grammar | /20 |
| Sentence and document structure | /20 |
| Punctuation and capitalization | /20 |
| Bias-free language | /20 |

[1-2 sentence summary of the biggest drivers of the score]

## Revised text

[full edited version, or edited section if the doc is long]

## Summary of changes

### Tone and voice
- "..." → "..." — [reason, e.g., "Microsoft style favors contractions and second person"]

### Word choice and grammar
- ...

### Sentence and document structure
- ...

### Punctuation and capitalization
- ...

### Bias-free language
- ...
```

Omit a category heading entirely if it had no issues — don't write "No issues found" for every section.

**Long documents** (multi-page guides): don't reproduce the full revised text inline in chat. Edit the actual file if one was uploaded, or create a new file with the revision, and summarize changes in chat instead.

**Short text** (a paragraph, a UI string, a README section): inline revision + summary is fine.

## Examples

### Example 1: Short text, quick pass

User says: *"Can you check this error message against Microsoft style: 'The file you have selected cannot be uploaded due to the fact that it exceeds the maximum file size.'"*

Actions:
1. Load `voice-and-tone.md` and `punctuation-and-capitalization.md` (short text, no bias-language concern — structure and bias-free categories marked N/A).
2. Rewrite for conciseness and active phrasing: *"This file is too large to upload. Choose a file under [size limit]."*
3. Return the score (e.g., 30/40 across the two checked categories, since three were N/A), revision, and a short change list (cut "due to the fact that," shortened sentence, made actionable).

Result: score, one revised string, 2–3 bullet change summary. No file created.

### Example 2: Full README review

User says: *"Review this README against Microsoft style"* and uploads `README.md`.

Actions:
1. Read the file from disk.
2. Load all five reference files.
3. Run all five analysis passes, skipping code blocks and CLI flags.
4. Since it's a full document, write the revised version to a new file rather than pasting it inline, and present the categorized change summary in chat.

Result: a compliance score out of 100, a revised `README.md` file, plus an in-chat change summary grouped by category.

### Example 3: Drafting new content in style

User says: *"Write a quickstart section for our API in Microsoft style."*

Actions:
1. Load all five reference files up front, since there's no existing draft to diagnose — the references function as writing guidance, not just a checklist.
2. Draft the section directly following the rules (second person, active voice, sentence-style capitalization, scannable steps).
3. No "change summary" or compliance score is needed here since there's no original to diff against or grade — just note which conventions were applied if it's not obvious.

## Troubleshooting

**Issue: The text is mostly code samples with little prose.**
Cause: Style rules mostly don't apply to code. Solution: Only analyze the surrounding prose (comments in natural language, descriptions, headings). Leave code untouched, including code comments that are effectively part of the code's logic rather than reader-facing explanation.

**Issue: A style rule conflicts with the user's established terminology (e.g., their product name uses non-standard capitalization).**
Cause: Microsoft style assumes Microsoft's own terminology; the user's product/brand terms take precedence. Solution: Don't "fix" proper nouns, product names, or established brand terms to match generic word-choice rules. Flag the conflict if it seems like a genuine oversight, but don't silently override it.

**Issue: User asks about a specific terminology choice not covered in the bundled reference files (e.g., "sign in" vs. "log in" for a term not listed).**
Cause: The bundled references are a high-frequency subset, not the full Microsoft A-Z word list. Solution: Say so explicitly, and offer to check the live style guide (learn.microsoft.com/en-us/style-guide/a-z-word-list-term-collections/) rather than guessing.

**Issue: The text has almost no issues — does it still get a score below 100?**
Cause: A perfect or near-perfect score is legitimate if the text genuinely complies. Solution: Don't deduct points just to avoid awarding 100/100 — if a category has no violations, score it the full 20. A clean doc scoring 98–100 is a correct outcome, not a sign the scoring was too lenient.

**Issue: The user only wants a grammar check, not a full style review.**
Cause: Scope mismatch — this skill covers tone, structure, and bias-free language in addition to grammar. Solution: Ask whether they want the full style pass or grammar only, and narrow the reference files loaded (and the output categories shown) accordingly rather than forcing all five categories into the output.
