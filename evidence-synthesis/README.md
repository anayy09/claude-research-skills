# evidence-synthesis

> Plan, run, appraise, and report systematic and other evidence syntheses (PRISMA, GRADE, RoB).

[![Version](https://img.shields.io/badge/version-1.0.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Treats a review as a research design, not a reading exercise — with a protocol, a
sampling frame (the search), an eligibility rule, a measurement instrument (the
appraisal tool), an analysis, and a reporting standard. It runs inside one
conversation with executable checks at the points where reviews usually break, and
supports the full family of review types: **systematic, scoping, rapid, umbrella,
living, diagnostic-accuracy, and prediction-model** reviews.

It covers the whole pipeline:

- **Review-type selection**, protocol, and registration
- **Concept-block search construction** with PRISMA-S reporting
- **Screening logs** with a reconciling PRISMA 2020 flow diagram
- **Risk-of-bias tool selection** — RoB 2, ROBINS-I, QUADAS-2, PROBAST+AI, AMSTAR 2, ROBIS
- **Synthesis** with or without meta-analysis, and **GRADE** certainty rating
- **Executable citation verification**, including retraction checking
- **RAISE-compliant disclosure** of AI use

## When Claude uses it

- "Do a literature review / systematic review / meta-analysis / scoping review"
- "PRISMA anything" — flow diagram, PRISMA-S search reporting, protocol
- "What does the evidence say about …?"
- "Critically appraise this study / this review"
- "Check whether these references are real" / retraction checking
- "How should I report my search?"
- A reviewer has raised a methods objection about a review

## What's inside

```
evidence-synthesis/
├── SKILL.md
├── references/
│   ├── review-types.md              choosing the right review design
│   ├── search-strategy.md           concept-block search + PRISMA-S
│   ├── appraisal-tools.md           picking RoB 2 / ROBINS-I / QUADAS-2 / …
│   ├── certainty-and-synthesis.md   synthesis (with/without meta-analysis) + GRADE
│   ├── verification-protocol.md     executable citation & retraction checks
│   └── ai-use-reporting.md          RAISE-compliant AI-use disclosure
├── scripts/
│   ├── search_builder.py            assemble a concept-block Boolean search
│   ├── screening_log.py             screening log + reconciling PRISMA 2020 flow
│   └── verify_citations.py          verify citations and flag retractions
└── templates/
    ├── protocol.md                  review protocol scaffold
    ├── evidence-table.md            extraction / evidence table
    └── ai-disclosure.md             AI-use disclosure statement
```

## Scripts

```bash
python evidence-synthesis/scripts/search_builder.py --help    # build a PRISMA-S search
python evidence-synthesis/scripts/screening_log.py --help     # screening log + PRISMA flow
python evidence-synthesis/scripts/verify_citations.py --help  # verify + retraction check
```

`verify_citations.py` makes optional, read-only calls to public metadata APIs and
degrades gracefully offline — network-dependent checks are marked *skipped*, never
silently passed. Live lookups need `requests` (`pip install requests`).

> **Related skills:** [`investigating-sources`](../investigating-sources) for
> general citation-honest research, and [`deep-research`](../deep-research) for its
> multi-agent systematic-review mode. Reach for **evidence-synthesis** when the
> deliverable is a formal, reporting-standard-compliant review.

## Changelog

- **1.0.0** — Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
