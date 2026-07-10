# Voice and tone

Source: [Top 10 tips for Microsoft style and voice](https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice), [Brand voice](https://learn.microsoft.com/en-us/style-guide/brand-voice-above-all-simple-human)

Microsoft's brand voice is **warm and relaxed, crisp and clear, and ready to lend a hand.** For developer documentation specifically, "warm and relaxed" means conversational and direct, not casual to the point of vague — precision still matters more than personality.

## Rules to check

### 1. Use contractions

Use contractions like *it's*, *you'll*, *you're*, *we're*, *let's*, *don't*, *can't*. Formal, contraction-free prose reads as stiff and distant, which works against the "lend a hand" tone.

- ❌ "You will need to configure the endpoint before you can proceed."
- ✅ "You'll need to configure the endpoint before you can proceed."

**Exception:** Don't force a contraction where it creates ambiguity or an awkward stress pattern (e.g., "the request that's failing" is fine, but don't contract in a way that obscures which word is negated in a warning — "You must not skip this step" should stay uncontracted for emphasis and clarity, not become "You mustn't").

### 2. Write in second person

Address the reader directly as *you*. Avoid third-person constructions like "the user" or "the developer" in instructional text.

- ❌ "The developer must set the API key before the client can authenticate."
- ✅ "Set your API key before the client can authenticate."

### 3. Prefer active voice

Active voice is more direct and easier to scan. Passive voice is acceptable when the actor is unknown, irrelevant, or when de-emphasizing the actor is intentional (common in security advisories: "the vulnerability was patched in version 2.1").

- ❌ "The configuration file is read by the server on startup."
- ✅ "The server reads the configuration file on startup."

Flag passive constructions but don't auto-flip ones that look intentional — see Step 4 guardrails in SKILL.md.

### 4. Use imperative mood in procedures, indicative mood elsewhere

Steps in a procedure should be direct commands. Explanatory prose uses ordinary indicative sentences.

- ✅ (procedure step) "Select **Save**."
- ✅ (explanation) "The **Save** button writes your changes to disk."

### 5. Cut throat-clearing openers

Edit out *you can*, *there is*, *there are*, *there were*, and similar filler that delays the verb. Most sentences should start close to the subject and verb.

- ❌ "You can access the dashboard by selecting the icon in the top bar."
- ✅ "Select the icon in the top bar to open the dashboard."

- ❌ "There are three parameters that this function accepts."
- ✅ "This function accepts three parameters."

### 6. Avoid jargon and unnecessary complexity — but keep necessary technical precision

Microsoft style asks writers to sound like "a friendly conversation," not a technical lecture. For developer docs, this means:

- Cut jargon that isn't load-bearing (business-speak like *leverage*, *utilize*, *synergy*, *robust solution*).
- **Keep** precise technical terms the reader needs (*idempotent*, *race condition*, *null pointer*, specific API/parameter names). Simplifying these away would reduce accuracy, which the guide doesn't ask for.
- Rewrite needlessly formal phrasing in favor of plain words: *utilize* → *use*; *in order to* → *to*; *prior to* → *before*; *subsequent to* → *after*; *in the event that* → *if*.

### 7. Give customers/readers just enough information

Prune excess words and don't restate context the reader already has (e.g., don't re-explain what a button does every time it's mentioned). This overlaps with `word-choice-and-grammar.md` — flag it here when it's a tone/verbosity issue (padded, over-explained sentences) rather than a specific weak-construction issue.

## What NOT to flag

- Technical precision that happens to sound "formal" (e.g., "authenticate the request" is correct even though it's not the most casual phrasing — don't downgrade it to "check the request" if that loses meaning).
- Passive voice used deliberately to de-emphasize an actor (security disclosures, postmortems: "the incident was resolved at 14:32 UTC").
- Third-person references to roles when addressing a general audience *about* other people, not the reader (e.g., "Administrators can grant this permission to other users" is fine when *you*, the reader, might not be the administrator in that sentence).

## Severity guide (for compliance scoring)

- **Minor (−1):** occasional missed contraction, one instance of a throat-clearing opener in an otherwise good doc.
- **Moderate (−2 to −3):** passive voice used as the default throughout a section, second person rarely used when it should be, jargon used where a plain-word substitute exists.
- **Major (−4 to −5):** consistently formal/distant register throughout the document, third-person address used pervasively instead of "you," verbosity that regularly buries the action the reader needs to take.
