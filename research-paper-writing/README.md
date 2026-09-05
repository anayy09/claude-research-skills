# research-paper-writing

> Scholarly prose that reads like a working researcher wrote it.

[![Version](https://img.shields.io/badge/version-2.1.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Writes, rewrites, edits, and extends academic research prose that reads as if a
working researcher wrote it, not a language model. It handles full paper sections
(introduction, related work, method, results, discussion, conclusion), thesis
chapters, rebuttals and response letters, conference and journal submissions, and
technical reports. It is for scholarly writing specifically, and deliberately not
for casual summaries, blog posts, marketing copy, slide text, or code.

## When Claude uses it

- "Write the related work / introduction / discussion"
- "Tighten this paragraph" / "help me phrase this contribution"
- "Make this sound less like AI wrote it" (for academic prose)
- Drafting a rebuttal or response-to-reviewers letter
- Extending or restructuring a thesis chapter

> **Tip:** pair this with [`manuscript-editor`](../manuscript-editor) for any
> revision round, resubmission, or whole-manuscript check. It decides what
> belongs in the paper versus the response letter and how much to change, then
> calls this skill for the sentences. Also pair with
> [`prose-naturalizer`](../prose-naturalizer) to scrub residual AI-tells, and
> [`investigating-sources`](../investigating-sources) to keep every citation
> honest.

## What's inside

```
research-paper-writing/
└── SKILL.md    a single, self-contained skill (the drafting + editing playbook)
```

## Changelog

- **2.1.0**: Draws the line against `manuscript-editor`. A scope section says
  this skill owns the prose and not placement, scope of change, or
  whole-manuscript coherence; the rebuttal section states that the account of
  what changed lives only in the response letter, never in the revised
  manuscript; and rewriting now starts by checking whether the manuscript
  already makes the point somewhere else, since a point stated twice reads as
  patching and the two copies drift apart in later rounds.
- **2.0.1**: Hand off to `manuscript-figures` for the figure a results paragraph
  cites, and to `ml-eval-statistics` when a claimed gap still needs an interval.
- **2.0.0**: Current release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
