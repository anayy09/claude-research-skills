# investigating-sources

> Citation-honest research where every claim traces to a real, verified source.

[![Version](https://img.shields.io/badge/version-1.0.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

A rigorous research assistant that produces evidence-backed deliverables —
briefs, reports, literature reviews, fact-checks, source-verification audits, and
PRISMA-style systematic reviews — under one hard rule: **every claim is traced to
a real, verified source, and unconfirmable citations are caught rather than
emitted.**

## Why it exists

Two failure modes make AI research untrustworthy: fabricated citations and
overconfident synthesis. This skill attacks both. It catches fabricated sources
with independent verification plus executable checks, and disarms overconfidence
by requiring disconfirming search, disclosure of conflicting evidence, and
explicit limitations.

## When Claude uses it

- "Research this topic, with citations"
- "Verify / fact-check these claims"
- "Are these sources (or DOIs) real?"
- "Build a bibliography" / "grade these sources"
- "Run a systematic review or meta-analysis"
- "Help me scope this vague question into an answerable one"

## Modes

`brief` · `report` · `lit-review` · `fact-check` · `verify` · `systematic` ·
`scope`. Pick one per run; see [`references/modes.md`](./references/modes.md).

## What's inside

```
investigating-sources/
├── SKILL.md               the 7-step workflow + 7 modes
├── references/            loaded on demand
│   ├── modes.md           full spec of every output mode
│   ├── scoping.md         framing answerable questions
│   ├── verification.md    source-log schema + verification decisions
│   ├── source_quality.md  evidence hierarchy and quality flags
│   ├── synthesis.md       integrating across sources
│   ├── reasoning_checks.md fallacy and bias catalog
│   ├── systematic_review.md PRISMA protocol
│   ├── writing_quality.md  prose standards, AI-tell patterns
│   └── audit.md           pre-delivery checklist
├── scripts/
│   ├── check_citations.py verify a source log (Crossref; degrades offline)
│   └── audit_report.py    cross-check a draft against its source log
├── assets/                output templates + blank source log
└── examples/
    └── brief_walkthrough.md full pipeline on a real question
```

## Scripts

Both are network-optional and degrade gracefully offline: structural checks still
run, and network-dependent checks are marked *skipped*, never silently passed.

```bash
# Verify every source in a log; non-zero exit if any FAILs
python investigating-sources/scripts/check_citations.py sources.json

# Confirm a finished draft's citations all map to verified sources
python investigating-sources/scripts/audit_report.py draft.md sources.json
```

Live DOI resolution needs `requests` (`pip install requests`).

## Changelog

- **1.0.0** — Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
