# Sentence and document structure

Source: [Writing tips (global communications)](https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips), [Top 10 tips](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice), [Microsoft Learn style guide — quick start](https://learn.microsoft.com/en-us/contribute/content/style-quick-start)

Microsoft style optimizes structure for scanning, not linear reading — developers skim docs looking for the one relevant step or parameter, not reading start to finish. Structure should make that possible.

## Rules to check

### 1. Lead with what's most important

Front-load the key word or action so it's visible when scanning. Don't bury the point at the end of a long sentence or paragraph.

- ❌ "Templates provide a starting point for creating new documents. A template can include the styles, formats, and page layouts you use frequently."
- ✅ "Save time by creating a document template that includes the styles, formats, and page layouts you use most often."

### 2. Use short, simple sentences

Standard word order — subject + verb + object — whenever possible. A sentence with more than a few commas or several clauses is a candidate for splitting.

- ❌ "Inspect the database, which should be backed up beforehand in case something goes wrong, to verify that all tables, data, and relationships were correctly migrated after running the script that was provided in the previous section."
- ✅ "Back up the database first. Then run the migration script from the previous section. Inspect the database to verify that all tables, data, and relationships migrated correctly."

### 3. Replace complex sentences and paragraphs with lists and tables

If a sentence is trying to enumerate several items, parameters, or steps, it's a list, not a sentence.

- ❌ "The function accepts a `timeout` parameter that defaults to 30 seconds, a `retries` parameter that defaults to 3, and a `backoff` parameter that defaults to exponential."
- ✅ A parameter table:

  | Parameter | Default | Description |
  |---|---|---|
  | `timeout` | 30s | ... |
  | `retries` | 3 | ... |
  | `backoff` | exponential | ... |

### 4. Chunk long procedures into sections

Procedures with more than roughly 12 steps are too long for one flat list — group them under subheadings.

### 5. Use sentence-style capitalization for headings

Capitalize only the first word and proper nouns — not title case. (Full rules in `punctuation-and-capitalization.md`; flag it here only if the issue is heading *structure*, e.g., a heading that isn't scannable as a phrase.)

### 6. Include articles and relative pronouns for clarity

Don't drop *the*, *a*, *that*, or *who* just to save words — they help readers (and machine translation) parse sentence structure correctly.

- ❌ "Empty container before syncing folder."
- ✅ "Empty the container before you sync the folder."

- ❌ "Inspect the database to verify all tables, data, and relationships were correctly migrated."
- ✅ "Inspect the database to verify **that** all tables, data, and relationships were correctly migrated."

### 7. Limit sentence fragments

Fragments (fine in headings and UI labels) can be genuinely ambiguous in body prose and are hard to translate. If a fragment appears in a full sentence position, check whether it obscures the actor or action.

### 8. Avoid modifier stacks

Long chains of modifying words before a noun are hard to parse, even for native speakers.

- ❌ "an extremely well thought-out Windows migration project plan"
- ✅ "a well thought-out project plan for your Windows migration"

### 9. Keep adjectives and adverbs close to what they modify

Don't let a modifier drift away from its target across a long clause.

## What NOT to flag

- Necessarily long code blocks, tables, or parameter lists — structure rules are about prose, not about shortening legitimate reference material.
- Deliberate sentence fragments in headings, UI labels, and list items three words or fewer (see `punctuation-and-capitalization.md`, rule on end punctuation).
- One long sentence that is a single, precise technical statement without real ambiguity (e.g., a formal API contract description) — only flag if it's actually hard to parse, not just long.

## Severity guide (for compliance scoring)

- **Minor (−1):** an isolated run-on sentence, a missing article in one spot, a heading that could scan better.
- **Moderate (−2 to −3):** a document that consistently uses paragraphs where lists/tables would clarify parameters or steps, procedures that aren't chunked despite being long.
- **Major (−4 to −5):** structure that actively obscures the steps a reader needs to follow (unclear step order, no separation between concept explanation and actionable steps), pervasive run-on sentences that make the doc hard to scan at all.
