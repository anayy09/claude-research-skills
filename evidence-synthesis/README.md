# evidence-synthesis

> Formal evidence syntheses as research designs: protocol, PRISMA-S search, screening log, RoB, GRADE.

[![Version](https://img.shields.io/badge/version-2.0.1-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Treats a review as a research design, not a reading exercise: with a protocol, a
sampling frame (the search), an eligibility rule, a measurement instrument (the
appraisal tool), an analysis, and a reporting standard. It runs inside one
conversation with executable checks at the points where reviews usually break, and
supports the full family of review types: **systematic, scoping, rapid, umbrella,
living, diagnostic-accuracy, and prediction-model** reviews.

It covers the whole pipeline:

- **Review-type selection**, protocol, and registration
- **Concept-block search construction** with PRISMA-S reporting, rendered to 13
  platforms including IEEE Xplore, SpringerLink and the Nature portfolio,
  Elsevier ScienceDirect, and the ACM Digital Library
- **Peer-reviewed-first sourcing**: preprints are upgraded to the published
  version of record before extraction
- **Screening logs** with a reconciling PRISMA 2020 flow diagram
- **Risk-of-bias tool selection**: RoB 2, ROBINS-I, QUADAS-2, PROBAST+AI, AMSTAR 2, ROBIS
- **Synthesis** with or without meta-analysis, and **GRADE** certainty rating
- **RAISE-compliant disclosure** of AI use

It is for the formal review. A related-work section, a literature sweep, a
cited brief or report, a reference audit, and a reference diet belong to
[`investigating-sources`](../investigating-sources), which also owns the
citation checker this skill calls.

## When Claude uses it

- "Do a systematic review / meta-analysis / scoping review"
- "PRISMA anything": flow diagram, PRISMA-S search reporting, protocol
- "Critically appraise this study / this review" / "risk of bias" / "GRADE"
- "How should I report my search?"
- A reviewer has raised a methods objection about a review

## What's inside

```
evidence-synthesis/
├── SKILL.md
├── references/
│   ├── review-types.md              choosing the right review design
│   ├── search-strategy.md           concept-block search + PRISMA-S
│   ├── peer-reviewed-sources.md     version of record, preprint upgrade, publishers
│   ├── appraisal-tools.md           picking RoB 2 / ROBINS-I / QUADAS-2 / …
│   ├── certainty-and-synthesis.md   synthesis (with/without meta-analysis) + GRADE
│   ├── verification-protocol.md     what the citation check proves and does not
│   └── ai-use-reporting.md          RAISE-compliant AI-use disclosure
├── scripts/
│   ├── search_builder.py            one spec -> 13 platform syntaxes
│   ├── screening_log.py             screening log + reconciling PRISMA 2020 flow
│   └── verify_citations.py          parses a reference list or .bib and delegates to check_citations.py
└── templates/
    ├── protocol.md                  review protocol scaffold
    ├── evidence-table.md            extraction / evidence table
    └── ai-disclosure.md             AI-use disclosure statement
```

The release zip also ships a copy of
`investigating-sources/scripts/check_citations.py` inside `scripts/`, so the
skill installs on its own. In a checkout of the whole collection the shim
finds the sibling copy instead.

## Scripts

```bash
python evidence-synthesis/scripts/search_builder.py --help    # build a PRISMA-S search
python evidence-synthesis/scripts/search_builder.py --self-test
python evidence-synthesis/scripts/screening_log.py --help     # screening log + PRISMA flow
python evidence-synthesis/scripts/verify_citations.py --help  # verify + retraction check
python evidence-synthesis/scripts/verify_citations.py --self-test

# Peer-reviewed-first workflow
python evidence-synthesis/scripts/search_builder.py --spec search.yaml --peer-reviewed-only
python evidence-synthesis/scripts/verify_citations.py --refs refs.md --mailto you@uni.edu \
    --upgrade-preprints --require-peer-reviewed --write-log sources.json
```

`verify_citations.py` needs `requests` for live lookups (the checker it
delegates to uses it) and degrades to structural checks offline, marking
network-dependent checks *skipped*, never passed. `--write-log` keeps the
source log so `audit_report.py` can cross-check the finished manuscript.

## Changelog

- **2.0.1**: The loading-discipline section.
- **2.0.0**: Rescoped to the formal review design and put on the collection's
  one citation checker (behavior change). The description now says what this
  skill is not for: a related-work section, a literature sweep, a cited brief
  or report, a reference audit, or a reference diet are
  `investigating-sources`. `verify_citations.py` is now a shim: it parses the
  reference list or `.bib` into the source-log schema and delegates to
  `investigating-sources/scripts/check_citations.py`, which the release zip
  ships alongside it, so the DataCite fallback, preprint upgrade, and
  retraction check are implemented once. Same flags, plus `--write-log` and
  `--checker`. The `deep-research` skill this one replaced is removed from the
  collection.
- **1.1.0**: Peer-reviewed sourcing across `search_builder.py` (13 platforms,
  `--peer-reviewed-only`) and the verifier (peer-review status, DataCite
  fallback, `--upgrade-preprints`, `--require-peer-reviewed`).
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
