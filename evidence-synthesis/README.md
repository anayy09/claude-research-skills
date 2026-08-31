# evidence-synthesis

> Plan, run, appraise, and report systematic and other evidence syntheses (PRISMA, GRADE, RoB).

[![Version](https://img.shields.io/badge/version-1.1.0-6E56CF)](../CHANGELOG.md)
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
  version of record before extraction, and peer-review status is read from the
  record rather than guessed from the publisher's name
- **Screening logs** with a reconciling PRISMA 2020 flow diagram
- **Risk-of-bias tool selection**: RoB 2, ROBINS-I, QUADAS-2, PROBAST+AI, AMSTAR 2, ROBIS
- **Synthesis** with or without meta-analysis, and **GRADE** certainty rating
- **Executable citation verification**, including retraction and preprint checking
- **RAISE-compliant disclosure** of AI use

## When Claude uses it

- "Do a literature review / systematic review / meta-analysis / scoping review"
- "PRISMA anything": flow diagram, PRISMA-S search reporting, protocol
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
│   ├── peer-reviewed-sources.md     version of record, preprint upgrade, publishers
│   ├── appraisal-tools.md           picking RoB 2 / ROBINS-I / QUADAS-2 / …
│   ├── certainty-and-synthesis.md   synthesis (with/without meta-analysis) + GRADE
│   ├── verification-protocol.md     citation, retraction & peer-review checks
│   └── ai-use-reporting.md          RAISE-compliant AI-use disclosure
├── scripts/
│   ├── search_builder.py            one spec -> 13 platform syntaxes
│   ├── screening_log.py             screening log + reconciling PRISMA 2020 flow
│   └── verify_citations.py          verify, flag retractions, upgrade preprints
└── templates/
    ├── protocol.md                  review protocol scaffold
    ├── evidence-table.md            extraction / evidence table
    └── ai-disclosure.md             AI-use disclosure statement
```

## Scripts

```bash
python evidence-synthesis/scripts/search_builder.py --help    # build a PRISMA-S search
python evidence-synthesis/scripts/search_builder.py --self-test
python evidence-synthesis/scripts/screening_log.py --help     # screening log + PRISMA flow
python evidence-synthesis/scripts/verify_citations.py --help  # verify + retraction check
python evidence-synthesis/scripts/verify_citations.py --self-test

# Peer-reviewed-first workflow
python evidence-synthesis/scripts/search_builder.py --spec search.yaml --peer-reviewed-only
python evidence-synthesis/scripts/verify_citations.py --refs refs.md     --mailto you@uni.edu --upgrade-preprints --require-peer-reviewed
```

`verify_citations.py` makes read-only calls to public keyless APIs (Crossref,
DataCite, OpenAlex, bioRxiv) and degrades gracefully offline: network-dependent
checks are marked *unchecked*, never silently passed or failed. It falls back to
DataCite when Crossref 404s, because arXiv registers there, and without that
fallback every arXiv citation reads as a fabrication. Both scripts ship a
`--self-test` that checks their own logic against fixtures.

> **Related skills:** [`investigating-sources`](../investigating-sources) for
> general citation-honest research and fact-checking. **evidence-synthesis**
> supersedes the deprecated `deep-research` skill for systematic reviews. Reach
> for it whenever the deliverable is a formal, reporting-standard-compliant review.

## Changelog

- **1.1.0**: Peer-reviewed sourcing. `search_builder.py` gains SpringerLink and
  the Nature portfolio, Elsevier ScienceDirect, the ACM Digital Library, Wiley,
  Europe PMC, and a Crossref REST supplement (13 platforms total), a
  `--peer-reviewed-only` mode that applies each platform's publication-type
  restriction, platform-quirk warnings for the failures that silently return the
  wrong result set, and a `--self-test`. `verify_citations.py` gains
  peer-review status per reference, a DataCite fallback so arXiv DOIs stop
  reading as fabrications, `--upgrade-preprints` to find the published version
  of record, `--require-peer-reviewed`, retries with backoff, and reconstruction
  of DOIs from bare `arXiv:` identifiers. New reference
  `peer-reviewed-sources.md`.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
