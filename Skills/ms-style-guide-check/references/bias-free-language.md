# Bias-free and inclusive language

Source: [Bias-free communication](https://learn.microsoft.com/en-us/style-guide/bias-free-communication)

Microsoft's reach is global, so inclusive language is treated as a core style requirement, not an optional add-on. For developer docs, this mostly shows up in generic-person references (variable names in examples, hypothetical users, error messages addressed to "the developer") rather than in marketing-style content — scope checks accordingly.

## Rules to check

### 1. Gender-neutral language for generic references

Don't use *he*, *him*, *his*, *she*, *her*, or *hers* when referring to a generic, unspecified person (a hypothetical user, an example developer, a generic admin). Fix with one of:

- Rewrite in second person (*you*)
- Make the noun and pronoun plural
- Use *the*/*a* instead of a pronoun
- Refer to the person's role (*the administrator*, *the caller*, *the client*)
- Use singular *they*/*them*/*their* — acceptable in Microsoft style if you can't rewrite around it

Don't use *he/she* or *s/he* constructions.

- ❌ "When a user submits a request, he receives a confirmation."
- ✅ "When a user submits a request, they receive a confirmation." or "You receive a confirmation when you submit a request."

### 2. Use the pronouns a real, named person uses

This rule only applies to generic/hypothetical references. If the documentation names a real person (an author byline, a quoted contributor), use the pronouns that person uses themselves — don't neutralize those.

### 3. Avoid terms with unconscious bias or militaristic/political associations

Watch for legacy technical terms that carry this kind of baggage (e.g., historically common master/slave, whitelist/blacklist terminology in some codebases). If the source text or the user's actual codebase/API uses such terms as established, real identifiers (e.g., an existing config key literally named `master_branch` in a system Claude doesn't control), flag it as a suggestion rather than silently renaming a real identifier that would break if changed — renaming a real API/config key is a breaking change, not a style edit.

- ❌ "the master branch" *(as generic prose, not a literal existing identifier)* → ✅ "the main branch"
- ❌ "whitelist these IPs" → ✅ "allow these IPs" / "add these IPs to the allowlist"

### 4. Focus on people, not disabilities; avoid pity language

If content discusses accessibility or user characteristics, focus on the person and the task, not a disability label — and don't use language implying pity (*stricken with*, *suffering from*, *victim of*). Don't mention a disability unless it's relevant to the content.

- ❌ "for users suffering from color blindness"
- ✅ "for users who are colorblind" or, better, focus on the design accommodation itself: "for sufficient contrast between error and success states"

### 5. Title-style capitalization for specific racial/ethnic identity terms

When racial or ethnic identity is genuinely relevant to the content (rare in developer docs, but possible in localization guides, accessibility content, or hiring-adjacent documentation), Microsoft style capitalizes terms like *Asian*, *Black*, *African American*, *Hispanic*, *Latinx*, *Native American*, *Indigenous Peoples* — and lowercases *multiracial* and *white*.

## What NOT to flag

- Gendered pronouns used correctly for a real, named individual.
- Established, real identifiers in the user's actual system (API field names, config keys, branch names, package names) — flag as a suggestion only, per rule 3, don't silently rename.
- Role-based third-person references that aren't about the reader (e.g., "Administrators can grant this permission" — see the parallel note in `voice-and-tone.md`).
- Technical terms that are not actually biased language just because they sound similar to a flagged term — don't over-apply rule 3 to unrelated words.

## Severity guide (for compliance scoring)

- **Minor (−1):** an isolated generic *he*/*she* in otherwise inclusive text.
- **Moderate (−2 to −3):** a document that defaults to gendered generic pronouns throughout example code/scenarios, or uses a flagged term in prose (not a real identifier) a few times.
- **Major (−4 to −5):** pervasive gendered defaults across all hypothetical users/examples in the document, pity-framed disability language, or consistent use of a biased term in prose throughout.
