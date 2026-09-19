# journal-advisor

> Match manuscripts to journals with verified fee routes, institutional eligibility, and desk-reject risk.

[![Version](https://img.shields.io/badge/version-2.0.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Recommends where to submit a manuscript, and says what publishing there will
actually cost the author. It reads the title, abstract, keywords and full text,
then returns one overall best pick plus a ranked shortlist, each entry carrying
topical fit, the **fee route** that makes it affordable, review-speed evidence,
indexing and quartile with the metric named, the matching article type, and a
low/medium/high **desk-reject risk**.

Four routes to zero APC are kept strictly apart, because they are four different
promises:

| Route | Zero APC because | Still verify |
| :--- | :--- | :--- |
| `institutional_oa` | an agreement covers it (UF, MUJ, JKLU) | author role, term, article type, quota |
| `no_apc_oa` | the journal charges no APC at all | other fees; diamond OA vs APC-free |
| `s2o` | Subscribe to Open funded that year | the year opened; submission limits |
| `subscription_no_apc` | the author publishes non-OA | paywalled record; page and colour fees |

A discount is not a waiver, a title list is not an approval, and "no APC" is not
"no cost". Every institutional route is reported as conditional with its
conditions named, and eligibility never transfers between institutions or
routes. Ranking is weighted: **likelihood of acceptance**, then **review
speed**, then **quartile and indexing**.

## When Claude uses it

- "Where should I submit this paper?"
- "Which journal fits this manuscript?"
- "Is the fee covered?" / "which journals can I publish in for free?"
- "Is venue X a good match?" / "what's my desk-reject risk?"
- "Shortlist some venues" / "compare these candidate journals"

Once a venue is picked, [`submission-formatter`](../submission-formatter) puts
the manuscript into that publisher's template, and
[`submission-reviewer`](../submission-reviewer) scores it before you upload.

## What's inside

```
journal-advisor/
├── SKILL.md
├── assets/
│   ├── journals.csv               the built catalog the recommender reads
│   ├── list-provenance.yaml       what each bundled workbook is, whose, and what it says about fees
│   └── sources/                   the research record, one file per source:
│       ├── IEEE.xlsx  Springer_Nature.xlsx  Elsevier.xlsx
│       ├── ACM.xlsx   T_F.xlsx            institution-sponsored workbooks (MUJ, JKLU)
│       ├── uf_100_percent_apc.csv         UF agreements stating full APC coverage
│       ├── no_apc_open_access.csv         DOAJ APC=No plus checked publisher policies
│       ├── subscribe_to_open.csv          S2O titles with their funded year
│       └── subscription_no_apc.csv        non-OA publication carrying no OA APC
├── references/
│   ├── catalog-schema.md          fields, identity linking, rebuilding, data licenses
│   ├── desk-reject-rubric.md      how desk-reject risk is scored
│   ├── evidence-rules.md          what counts as evidence; per-institution exceptions
│   └── report-format.md           the required report structure, with a worked example
└── scripts/
    ├── build_catalog.py           rebuild journals.csv from the nine source files
    └── find_journals.py           shortlist by topic, route, and eligibility date
```

`assets/journals.csv` is **one row per journal, fee route and source**: 20,262
route records linked to 19,533 journals in the 2026-09-19 snapshot. Routes for
the same journal share a `journal_id` and keep their own cost terms, evidence
level, and source links.

## Scripts

Searching uses only the Python standard library. Rebuilding needs pandas,
openpyxl and PyYAML.

```bash
# shortlist: universal routes plus one institution's agreements
python journal-advisor/scripts/find_journals.py --query "medical imaging machine learning" --institution UF

# isolate one route, or assume no affiliation at all
python journal-advisor/scripts/find_journals.py --query "robotics" --institution MUJ,JKLU --route institutional_oa
python journal-advisor/scripts/find_journals.py --query "statistics" --institution none --open-access-only --no-other-fees

# eligibility as it will stand at submission time
python journal-advisor/scripts/find_journals.py --query "materials physics" --institution UF --as-of 2026-10-01

# every known route for one title or ISSN
python journal-advisor/scripts/find_journals.py --check "2632-2153" --json

# rebuild the catalog after updating a source file
python journal-advisor/scripts/build_catalog.py
```

Both scripts take `--help`. Expired, future, closed and superseded records stay
out of ordinary search; `--include-inactive` brings them back for an audit.

See [catalog schema and provenance](references/catalog-schema.md) for the source
files, refresh instructions, and DOAJ attribution, and [evidence
rules](references/evidence-rules.md) for eligibility and verification. The skill
code is MIT-licensed; the adapted DOAJ journal metadata is CC BY-SA 4.0, so do
not relabel the combined catalog as MIT when redistributing it.

## Changelog

- **2.0.0**: The catalog grows from 1,848 titles on five publisher lists to 20,262 fee-route records across 19,533 journals, and the skill's question changes from "which of these titles fits" to "which venue fits and what will it cost". Four fee routes are modeled separately (`institutional_oa`, `no_apc_oa`, `s2o`, `subscription_no_apc`), each carrying its own eligibility, term, cap, ancillary-fee flag, evidence level, and source links. Four researched CSVs join the five bundled workbooks: UF full-APC coverage, DOAJ `APC=No`, Subscribe to Open, and no-APC subscription publication. `find_journals.py` gains `--institution`, `--route`, `--open-access-only`, `--no-other-fees`, `--as-of` and `--include-inactive`, groups results by journal so routes are never merged, and no longer breaks its table on the long publisher names the wider catalog carries. The previous "only the bundled lists" constraint is gone: a title absent from the snapshot may be recommended on primary-source evidence. `references/evidence-rules.md` gains the per-institution exceptions, exclusions and quotas; `references/report-format.md` gains the fee-route grouping and the open-eligibility-checks section.
- **1.1.1**: The description is trimmed below the 1024-character cap that skill portals enforce on the `description` field, by compressing the prose and dropping trigger phrases that duplicated others. Behavior is unchanged.
- **1.1.0**: `assets/list-provenance.yaml` records what each bundled list is (publisher catalog or an institution's read-and-publish agreement list), whose, exported when, and the fee statement that follows. `build_catalog.py` writes `list_kind`, `coverage_note`, and `fee_note` onto every row; the report's field block gains a list-and-fee-coverage line and the data notes name the lists.
- **1.0.2**: The description says what the bundled lists are (publisher exports that may be an institution's read-and-publish eligibility lists), that fee coverage depends on the institution, and that the skill is loaded once per session; the loading-discipline section.
- **1.0.1**: Point to `submission-formatter` for the venue template step.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
