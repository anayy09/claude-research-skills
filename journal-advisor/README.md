# journal-advisor

> Match a manuscript to the right journal, with desk-reject risk, from five publisher catalogs.

[![Version](https://img.shields.io/badge/version-1.0.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Recommends where to submit a manuscript using five bundled publisher catalogs:
**IEEE, Springer Nature, Elsevier, ACM, and Taylor & Francis**. It reads your
title, abstract, keywords, and full text, then returns one overall best pick plus
a ranked shortlist of three to five journals per publisher. Each candidate comes
with topical fit, review-speed evidence, Scopus/SCImago indexing and quartile, the
matching article type, submission constraints (APC, page limits, template, novelty
expectations), and a low/medium/high **desk-reject risk**.

Recommendations are weighted in this order: **likelihood of acceptance**, then
**review speed**, then **quartile and indexing**. It never recommends a journal
outside the bundled lists.

## When Claude uses it

- "Where should I submit this paper?"
- "Which journal fits this manuscript?"
- "Is venue X a good match?" / "what's my desk-reject risk?"
- "Shortlist some venues" / "compare these candidate journals"

## What's inside

```
journal-advisor/
├── SKILL.md
├── assets/
│   ├── journals.csv               the built catalog the recommender reads
│   └── sources/                   source publisher lists (xlsx):
│       ├── IEEE.xlsx  Springer_Nature.xlsx  Elsevier.xlsx
│       └── ACM.xlsx   T_F.xlsx
├── references/
│   ├── catalog-schema.md          the journal catalog schema
│   ├── desk-reject-rubric.md      how desk-reject risk is scored
│   ├── evidence-rules.md          what counts as review-speed evidence
│   └── report-format.md           the recommendation report layout
└── scripts/
    ├── build_catalog.py           rebuild journals.csv from the source xlsx files
    └── find_journals.py           rank journals for a given manuscript
```

## Scripts

```bash
python journal-advisor/scripts/build_catalog.py --help   # rebuild the catalog
python journal-advisor/scripts/find_journals.py --help   # rank venues for a paper
```

## Changelog

- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
