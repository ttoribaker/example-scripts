---
name: doc-screenshot-audit
description: Audits screenshots and other images embedded in technical documentation — docs sites (e.g. docs.snyk.io), draft documentation, PRDs, Google Docs, Word docs, or standalone uploaded screenshots — and scores each one Pass/Warning/Fail on three dimensions — accessibility, accuracy against the surrounding text, and confidential-information exposure — then gives a clear use/fix/reject recommendation with specific redaction guidance. Use this skill whenever the user asks you to review, audit, check, or QA a screenshot or image before it goes into docs, asks whether a screenshot is "safe to publish" or "ready to ship," pastes a docs URL and asks about its images, or uploads a PRD/Word doc/Google Doc and wants its screenshots checked before it's finalized — even if they don't use the word "accessibility," "confidential," or "audit" explicitly.
---

# Documentation Screenshot Audit

## Why this exists

Screenshots in technical docs quietly cause three kinds of damage if nobody checks them: they exclude screen-reader and low-vision users, they drift out of sync with the text and mislead readers, and they leak things nobody meant to publish (a real customer's email, an internal Slack handle, a live API key). None of these are visible at a glance to someone who already knows what the screenshot is supposed to show — which is exactly the person usually reviewing it. A second, systematic pass catches what a rushed first pass misses.

## Step 1: Get the screenshot(s) in front of you

The input varies — handle each case, and don't skip straight to scoring before you've actually looked at the image:

- **Uploaded image file (png/jpg/etc.)** — it's likely already visible in context; if not, use `view` on the file path directly. This is the richest case: you can see exactly what's in the frame.
- **Word doc / PRD (.docx)** — read `/mnt/skills/public/docx/SKILL.md` first, then extract the embedded images and any captions/alt text stored in the document XML.
- **PDF** — read `/mnt/skills/public/pdf-reading/SKILL.md` first, then extract embedded images per-page.
- **Google Doc** — use the Google Drive connector if it's connected; if not, ask the user to export or paste the doc, or offer to search connectors. Extract images the same way as a docx once you have the content.
- **Live docs URL (e.g. docs.snyk.io/...)** — `web_fetch` the page to get the HTML/markdown, which exposes `alt` attributes, `figcaption`/surrounding text, and image `src` URLs. This lets you fully audit **accessibility** (alt text is right there in the markup) and partially audit **accuracy** (you can compare the surrounding prose to the alt text and any visible caption). You generally *cannot* pixel-inspect the actual image this way — bash's network access is restricted to package registries, not arbitrary doc sites. Say so plainly rather than guessing at pixel content: report what the markup tells you, and note that a full accuracy/confidentiality pass needs the actual screenshot uploaded.

If you end up with several screenshots (a whole page, a whole PRD), audit each one separately but present results as one consolidated table — don't make the user ask three times.

## Step 2: Score each screenshot on three dimensions

Score each dimension **Pass / Warning / Fail**. Don't average them into a single number — a Fail on confidentiality should never be softened by Passes elsewhere, because the categories aren't substitutes for each other: a beautifully accessible screenshot that leaks a customer's email is still not shippable.

### Accessibility

What to check:
- **Alt text**: present, and actually descriptive of function/content — not the filename, not "screenshot," not "image1.png". Good alt text tells a screen-reader user what the image communicates, in roughly the amount of detail the sighted reader gets.
- **Redundancy with body text**: if the image is decorative or purely illustrative of something already fully explained in the surrounding prose, a screen-reader user losing it isn't a big loss (still flag missing alt text, but it's lower stakes). If the image carries information found *nowhere* in the text (e.g. "click the third icon from the left"), that's a real accessibility gap — a screen-reader user has no way to get that information at all.
- **Color-only signaling**: does the screenshot rely on color alone to convey meaning (e.g. a red vs. green status dot with no label)? That fails for colorblind readers regardless of alt text quality.
- **Resolution/legibility**: is text within the image actually readable at the size it'll render, including for readers who zoom or use magnification? Tiny UI text crammed into a wide screenshot is a common failure.
- **Caption**: does it have one, and does the caption add navigable context (useful for both screen readers and sighted skimmers), or is it just repeating the alt text verbatim?

Pass = alt text present and meaningfully descriptive, no color-only signaling, legible at rendered size.
Warning = alt text present but generic/thin, or minor legibility issues, or captioned redundantly.
Fail = no alt text on an image that carries unique information, or color-only signaling, or text genuinely illegible.

### Accuracy

What to check:
- Does the screenshot show the **same feature/screen/version** the surrounding text is describing — not an older UI, a different plan tier, a different OS, or a different product area?
- Do any callouts, arrows, highlights, or numbered steps in the image **match the steps in the text**, in the same order, pointing at the same elements?
- Are labels, button text, and menu names in the image **spelled and worded the same way** as they're referenced in the prose (docs UIs get renamed; screenshots lag behind)?
- If the text says "click X" or "you'll see Y," is X/Y actually visible and where the text implies it is?

Pass = image matches the current text description in content, wording, and any annotated steps.
Warning = mostly matches but has minor drift (an old version number visible, a slightly different button label) that wouldn't actively mislead a careful reader.
Fail = the image shows a different screen/state than the text describes, or annotated steps don't match the written steps — this actively misleads.

### Confidential information

Scan carefully for anything real that shouldn't be public — this is the category where "looks fine at a glance" fails most often, because reviewers pattern-match on the *feature* being shown and don't scrutinize incidental data in the frame. Check for:
- Real email addresses, names of real people (including in "From:"/"To:"/comment/reviewer fields), real usernames or handles
- Real company/customer names — including ones visible only in a sidebar, breadcrumb, browser tab title, or org-switcher dropdown
- API keys, tokens, session IDs, auth headers, or anything that looks like a secret (even partially visible or "safely" truncated — truncated keys can still be sensitive)
- Internal URLs, hostnames, internal ticket/JIRA numbers, Slack channel names
- IP addresses, account/org IDs, billing information
- Anything in a browser tab, taskbar, notification, or OS chrome at the edges of the screenshot — these get missed because attention is on the center of the image

Pass = no real personal, customer, or secret data visible anywhere in the frame — clearly demo/synthetic data (e.g. `demo@example.com`, `Acme Corp`, `sk-demo-xxxx`) or fully genericized.
Warning = ambiguous data you can't confirm is fake (a plausible-looking but unverifiable name/email/org) — flag it for the user to confirm rather than guessing either way.
Fail = confirmed or highly-likely-real personal data, customer identity, or working credential/token visible.

## Step 3: Give redaction guidance for anything short of Pass on confidentiality

Don't just say "this leaks information" — say what to do about it, specific to what's in the frame:
- Name the exact element and its rough location ("the email address in the top-right account menu", "the org name in the browser tab").
- Suggest the concrete fix: crop it out if it's near an edge, blur/box-redact it if it's central to the shot, or — best when feasible — retake the screenshot using a demo/sandbox account so there's nothing to redact at all. Retaking beats redacting whenever the leaked element is something the reader would otherwise need to see clearly (a redaction box over a UI element the reader needs to read defeats the point of the screenshot).
- If several separate items need redacting in one image, list them all — don't stop at the first one found.

## Step 4: Output format

Present a summary table first, then per-image detail. For a single screenshot, still use this structure — just one row.

```
| Screenshot | Accessibility | Accuracy | Confidentiality | Verdict |
|---|---|---|---|---|
| step-3-api-settings.png | Warning | Pass | Fail | Do not use as-is |
```

Then for each image, a short explanation (a few sentences per dimension, not a wall of text) covering:
- **Why** it scored what it scored on each dimension — point at the specific thing you saw, not a generic restatement of the category definition.
- **Redaction guidance** if confidentiality wasn't a clean Pass (per Step 3).
- **Overall verdict**, one of:
  - **Use as-is** — all three Pass.
  - **Use with fixes** — no Fails, but at least one Warning worth addressing before publishing.
  - **Do not use** — any Fail. Be direct about this; a confidentiality or accuracy Fail is a real risk, not a nitpick, and softening the verdict defeats the point of the audit.

Keep the tone practical, like a colleague doing a pre-publish check — not a compliance report. The goal is to get the person to a publishable screenshot quickly, not to catalog every possible issue exhaustively.
