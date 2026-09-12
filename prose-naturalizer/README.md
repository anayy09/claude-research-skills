# prose-naturalizer

> Strip the tells of AI-generated writing from non-academic prose, based on Wikipedia's Signs of AI writing.

<sub>Formerly `humanizer`.</sub>

[![Version](https://img.shields.io/badge/version-3.0.1-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Edits or reviews text to remove the patterns that make writing read as
machine-generated, so the result sounds like the writer. It is built on
Wikipedia's *"Signs of AI writing"* guide and on reviews of AI-generated text
elsewhere, and it explains why the patterns exist: a model makes the choice
that fits the widest range of readers, so its tells are staging, rhythm by
rule, inflation, formatting by rule, and leftovers from the chat. Twenty-five
patterns, ordered strongest first, each with a before and after, and a
rule for when not to act.

## When Claude uses it

- "Make this blog post / README / email sound less like AI wrote it"
- "Humanize this paragraph" / "remove the AI tells"
- Reviewing or editing documentation, essays, or announcements for naturalness

**Not for manuscripts.** [`research-paper-writing`](../research-paper-writing)
carries the manuscript subset of these patterns as its tell sweep, with a
lint script, and the two skills give conflicting instructions on voice and
on what to return. Load one or the other.

## What's inside

```
prose-naturalizer/
└── SKILL.md    a single, self-contained skill (why the tells exist, how to work, 25 patterns, when not to act)
```

The skill declares `compatibility: claude-code opencode`.

## Changelog

- **3.0.1**: Scope boundary. The description names the prose this skill is
  for (blog posts, essays, documentation, email) and says not to load it for
  a manuscript, thesis, or response letter, which `research-paper-writing`
  now covers. No pattern changed.
- **3.0.0**: Rewritten around why the tells exist. Opens with the five
  structural habits of model prose (staging, rhythm by rule, inflation,
  formatting by rule, leftovers) and orders the patterns strongest first, so
  that not-X-but-Y contrasts, one-line closers, sayings that sound deep,
  staged run-ups, and arguing with no one come before vocabulary. Patterns are
  graded: the first five justify an edit on one sighting, and those marked
  *weak alone* need company. Consolidates the old 31 patterns into 25 with
  paragraph-scale forms (a contrast split across sentences, three parallel
  examples, the same closer after every section), adds vague association and
  a check step naming the five tells that most often survive a rewrite.
- **2.0.1**: Rewritten in plainer language; repaired the frontmatter.
- **2.0.0**: Renamed from `humanizer` to `prose-naturalizer`.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
