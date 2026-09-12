# journal-advisor

> Match a manuscript to the right journal, with desk-reject risk, from five publisher catalogs.

[![Version](https://img.shields.io/badge/version-1.0.2-6E56CF)](../CHANGELOG.md)
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

Once a venue is picked, [`submission-formatter`](../submission-formatter) puts the
manuscript into that publisher's template, and
[`submission-reviewer`](../submission-reviewer) scores it before you upload.

## What's inside

```
journal-advisor/
├── SKILL.md
├── assets/
│   ├── journals.csv               the built catalog the recommender reads
│   ├── list-provenance.yaml       what each source list is, whose, and what it says about fees
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

`assets/list-provenance.yaml` names, per publisher, whether the bundled list
is a publisher catalog or an institution's read-and-publish agreement list,
whose, exported when, and what that means for fees. `build_catalog.py`
writes it onto every row as `list_kind`, `coverage_note`, and `fee_note`,
and the report carries a "list and fee coverage" line per recommendation.
A strong journal outside the lists is outside the permitted set, not a poor
fit, and the report says so.

## Changelog

- **1.1.0**: `assets/list-provenance.yaml` records what each bundled list is (publisher catalog or an institution's read-and-publish agreement list), whose, exported when, and the fee statement that follows. `build_catalog.py` writes `list_kind`, `coverage_note`, and `fee_note` onto every row; the report's field block gains a list-and-fee-coverage line and the data notes name the lists.
- **1.0.2**: The description says what the bundled lists are (publisher exports that may be an institution's read-and-publish eligibility lists), that fee coverage depends on the institution, and that the skill is loaded once per session; the loading-discipline section.
- **1.0.1**: Point to `submission-formatter` for the venue template step.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
