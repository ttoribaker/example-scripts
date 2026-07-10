# Punctuation and capitalization

Source: [Top 10 tips](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice), [Punctuation](https://learn.microsoft.com/en-us/style-guide/punctuation), [Capitalization](https://learn.microsoft.com/en-us/style-guide/capitalization)

## Rules to check

### 1. Sentence-style capitalization for headings and titles

Capitalize only the first word of a heading, title, or UI label, plus any proper nouns. Never use title case.

- ❌ "Find a Microsoft Partner" / "Limited-Time Offer" / "Join Us Online"
- ✅ "Find a Microsoft partner" / "Limited-time offer" / "Join us online"

This applies to document headings, section titles, table headers, and button/menu labels referenced in prose.

### 2. Capitalize proper nouns only

Product names, company names, trademarks, and other proper nouns are capitalized; generic descriptions of them are not. Check whether a term is a proper noun before capitalizing it (a dictionary or the product's own branding is the source of truth — don't assume every technical-sounding term is a proper noun).

- ✅ "Machine Learning" *(only if it's part of a specific product/service name)* vs. "machine learning" *(the general concept — lowercase)*

### 3. Oxford (serial) comma

Include a comma before the conjunction in a list of three or more items.

- ❌ "The API supports JSON, XML and YAML."
- ✅ "The API supports JSON, XML, and YAML."

### 4. One space after periods, question marks, and colons

No double spaces after sentence-ending punctuation.

### 5. No spaces around em dashes

- ❌ "Use pipelines — logical groups of activities — to consolidate tasks."
- ✅ "Use pipelines—logical groups of activities—to consolidate tasks."

### 6. Skip end punctuation on short headings and labels

Titles, headings, subheadings, UI element names, and list items of three or fewer words don't take a period. Reserve periods for paragraphs and full-sentence body copy (including full-sentence list items).

- ✅ Heading: "Move a tile" *(no period)*
- ✅ Body sentence: "Press and hold the tile to move it." *(period, it's a full sentence)*

### 7. Serial/list punctuation consistency

If list items are full sentences, punctuate each with a period and capitalize each. If list items are sentence fragments or short phrases, skip end punctuation and don't capitalize mid-list items unless they start with a proper noun. Don't mix styles within the same list.

### 8. Code, commands, and file names are not subject to prose capitalization/punctuation rules

Don't "correct" the capitalization of a CLI flag, environment variable, JSON key, or file name to match sentence-style rules — those follow the syntax of the language/tool they belong to, not prose conventions. This is a pointer to the guardrail in SKILL.md Step 4, restated here because capitalization is the rule category most likely to accidentally reach into code.

## What NOT to flag

- Proper capitalization of actual product names, trademarks, and brand terms, even if they look like they'd normally be lowercase generic terms.
- Capitalization or punctuation inside code blocks, inline code spans, file paths, or CLI examples.
- Full-sentence list items that correctly use periods — don't strip these to match a fragment-style list elsewhere in the doc; instead flag the *inconsistency*, and let the user decide which style to standardize on if it's ambiguous.

## Severity guide (for compliance scoring)

- **Minor (−1):** an isolated missing Oxford comma, a double space, one heading in title case.
- **Moderate (−2 to −3):** inconsistent list punctuation within a document, headings inconsistently capitalized throughout.
- **Major (−4 to −5):** title case used pervasively for all headings (a strong, visible departure from Microsoft style), inconsistent capitalization of the same proper noun across the document (confusing, not just stylistic).
