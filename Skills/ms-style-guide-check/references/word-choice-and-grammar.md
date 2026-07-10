# Word choice and grammar

Source: [Grammar and parts of speech](https://learn.microsoft.com/en-us/style-guide/grammar/grammar-and-parts-of-speech), [Verbs](https://learn.microsoft.com/en-us/style-guide/grammar/verbs), [Grammar and parts of speech checklist](https://learn.microsoft.com/en-us/style-guide/checklists/grammar-and-parts-of-speech-checklist), [Word choice](https://learn.microsoft.com/en-us/style-guide/word-choice)

Microsoft style favors grammar simple enough to read like a conversation — "the basic grammar you learned before you were 12 is probably just right for most content." For developer docs, pair that simplicity with exact technical terms; simple grammar and precise vocabulary aren't in tension.

## Rules to check

### 1. Use present tense by default

Present tense is easier to read and is the default for describing what software does. Use future tense only for things that genuinely haven't happened yet (a feature landing in a future release); use past tense only for things that already happened (changelogs, incident reports).

- ❌ "The function will return a promise that will resolve once the request will complete."
- ✅ "The function returns a promise that resolves once the request completes."

### 2. Watch words ending in *-ing*

*-ing* words can be ambiguous about what they modify — a gerund (noun) or a present participle (modifier). Rewrite if the role is unclear.

- ⚠️ Ambiguous: "meeting requirements" (a meeting about requirements, or fulfilling requirements?)
- ✅ Clear: "how to meet requirements" or "requirements for the meeting"

### 3. Avoid stacked prepositional phrases

Multiple prepositional phrases in a row are hard to parse. Rewrite as a possessive, a compound noun, or split into two sentences.

- ❌ "the configuration of the settings of the database of the application"
- ✅ "the application's database configuration settings"

### 4. Fix dangling and misplaced modifiers

Make sure it's clear what a modifier attaches to.

- ❌ "Only the selected text is modified." *(ambiguous: does "only" limit "selected text" or "is modified"?)*
- ✅ "Only the selected text is modified, not the rest of the document." *(if that's the intended meaning)*

### 5. Don't use gender-specific singular pronouns in generic references

Use *you*, a plural construction, an article (*the*/*a*), or refer to the person's role — instead of *he*/*she*/*his*/*hers* for a generic, unspecified person. (This overlaps with `bias-free-language.md`; flag it there if the primary issue is inclusivity, flag it here if it's a plain grammar fix like subject-verb agreement with a singular *they*.)

- ❌ "Each user must enter his password."
- ✅ "Each user must enter their password." *(singular they, acceptable per Microsoft style)* or "Enter your password."

### 6. Cut weak, indirect constructions

Beyond the tone-level throat-clearers in `voice-and-tone.md`, watch for these grammar-level patterns that weaken sentences:

- *due to the fact that* → *because*
- *in the event that* → *if*
- *is able to* → *can*
- *has the ability to* → *can*
- *it is important to note that* → (usually just cut it)
- *for the purpose of* → *to* / *for*

### 7. Common developer-documentation terminology

This is a high-frequency subset of Microsoft's A-Z word list, not the full list. If a term isn't here, say so rather than guessing (see SKILL.md Troubleshooting).

| Use | Not | Note |
|---|---|---|
| select | click, click on | "Select" works across mouse, touch, and keyboard |
| sign in / sign out | log in / log on, logon | "sign-in" (noun/adj., hyphenated) vs. "sign in" (verb) |
| select and hold | long-press, press and hold | for touch interactions |
| turn on / turn off | enable / disable *(for UI toggles specifically)* | reserve "enable/disable" for features, permissions, code-level flags |
| app | application | "app" is preferred in most consumer/developer content |
| repo | repository | spell out on first use if audience may be unfamiliar; "repo" is fine after |
| back up (verb) / backup (noun/adj.) | "backup" as a verb | "Back up your database" vs. "a database backup" |
| set up (verb) / setup (noun/adj.) | "setup" as a verb | "Set up the environment" vs. "the setup process" |
| email | e-mail | no hyphen |
| website | web site | one word |

### 8. Precision over synonym variety

Use one term per concept and use it consistently — don't vary word choice for the same thing across a document for the sake of style. This is the opposite of typical prose advice, but it matters for technical accuracy and translatability.

- ❌ Alternating between "endpoint," "route," and "URL" for the same concept in one doc.
- ✅ Pick one term (e.g., "endpoint") and use it throughout.

## What NOT to flag

- Domain-specific and product-specific terminology, API/method/parameter names, and established brand terms — these override generic word-choice rules (see SKILL.md Step 4 guardrails).
- Repetition of a technical term across a document — that's rule 8 above, correct usage, not a word-variety issue to "fix" with synonyms.
- Passive constructions or formal verbs that are the precise technical term (e.g., "the request is authenticated" is correct, not a rule-1 or rule-6 violation).

## Severity guide (for compliance scoring)

- **Minor (−1):** one instance of a weak construction (rule 6), an isolated -ing ambiguity.
- **Moderate (−2 to −3):** inconsistent terminology for the same concept across a document (rule 8), tense inconsistency in a procedure, a recurring weak construction.
- **Major (−4 to −5):** pervasive tense confusion that affects clarity of what the software actually does, dangling/misplaced modifiers that create real ambiguity about behavior (a serious issue in technical docs, since it can lead to incorrect usage).
