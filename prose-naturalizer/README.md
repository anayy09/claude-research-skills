# prose-naturalizer

> Strip the tells of AI-generated writing, based on Wikipedia's Signs of AI writing.

<sub>Formerly `humanizer`.</sub>

[![Version](https://img.shields.io/badge/version-2.0.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Edits or reviews text to remove the patterns that make writing read as
machine-generated, so the result sounds like a person wrote it. It is built on
Wikipedia's comprehensive *"Signs of AI writing"* guide and targets specific,
nameable tells rather than vibes:

- inflated symbolism and promotional language
- superficial "-ing" analyses and vague attributions
- em-dash overuse and the rule of three
- tic AI vocabulary, passive voice, negative parallelisms, and filler phrases

## When Claude uses it

- "Make this sound less like AI wrote it"
- "Humanize this paragraph" / "remove the AI tells"
- Reviewing or editing prose for naturalness

## What's inside

```
prose-naturalizer/
└── SKILL.md    a single, self-contained skill (the pattern catalog + editing rules)
```

The skill declares `compatibility: claude-code opencode` and a minimal
`allowed-tools` set (Read, Write, Edit, Grep, Glob, AskUserQuestion), so it only
needs to read and edit text.

## Changelog

- **2.0.0**: Renamed from `humanizer` to `prose-naturalizer` (breaking: the
  skill's folder and name changed). No behavior change.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
