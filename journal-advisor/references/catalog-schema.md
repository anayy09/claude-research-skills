# Catalog schema and provenance

## What each bundled list actually is

Three of the five are eligibility or agreement lists, not complete publisher
catalogs. This matters when a user asks why a well-known journal is missing.

| File | Sheet used | Titles | What it is |
|---|---|---|---|
| `IEEE.xlsx` | Title List | 224 | IEEE title list with open-access type and 2024 JCR/CiteScore metrics. The workbook states data is accurate as of 1 January 2026. Header sits on the second row; the last eight rows are footnotes. |
| `Springer_Nature.xlsx` | FOA Agreement Journals List | 620 | Journals eligible under a Springer Nature fully-open-access agreement. Discipline and imprint only, no citation metrics. Header sits on row 7. A second sheet holds a pivot count by subject. |
| `Elsevier.xlsx` | MUJ 2025 eligible pub list | 650 | An institutional eligible publication list. All entries are hybrid. Four columns: ISSN, title, OA type, CiteScore 2024 quartile. |
| `ACM.xlsx` | ACM Journals | 70 | ACM journal list. The Notes sheet records that ACM journals are open access as of 1 January 2026 and that blank fields were absent from the source, not omitted. Scope text present for 18 of 70. |
| `T_F.xlsx` | Open Access | 284 | Taylor & Francis open-access titles with WoS/Scopus coverage and 2024 JIF, CiteScore, SNIP and SJR values and quartiles. |

Total: 1,848 permitted titles.

Because the Elsevier and Springer lists are agreement-scoped, a strong Elsevier
journal outside the institutional list is not recommendable here. Say that
explicitly rather than substituting a weaker in-list title without explanation.

## Normalized fields in `assets/journals.csv`

| Column | Meaning | Populated for |
|---|---|---|
| `publisher` | one of the five | all |
| `journal_title` | title as printed in the source, newlines collapsed | all |
| `acronym` | publisher acronym | IEEE, ACM, T&F |
| `issn`, `eissn` | identifiers as given | varies |
| `oa_model` | hybrid, full/fully open access, open access | all |
| `subject_area` | publisher's own discipline label | Springer, T&F |
| `imprint` | Springer/BioMed Central; T&F/FSG | Springer, T&F |
| `scope` | scope paragraph | 18 ACM rows only |
| `journal_url` | official page | ACM only |
| `index_wos` | SCIE / ESCI / SSCI, or Yes/No | IEEE, T&F |
| `scopus_covered` | Yes/No | T&F only |
| `jif_2024`, `jif_quartile` | JCR 2024 | IEEE, T&F |
| `citescore_2024`, `citescore_quartile` | CiteScore 2024 | Elsevier (quartile), IEEE (value), T&F |
| `sjr_2024`, `sjr_quartile` | SJR 2024 | T&F |
| `best_quartile` | best available among JIF, CiteScore, SJR | see below |
| `quartile_basis` | which metric produced `best_quartile` | all |
| `list_context` | one line describing the source list | all |
| `source_file`, `source_sheet`, `source_row` | provenance back to the spreadsheet | all |

## Quartile coverage, and the rule that follows from it

| Publisher | Titles with a quartile |
|---|---|
| Elsevier | 641 / 650 (CiteScore 2024) |
| Taylor & Francis | 226 / 284 (best of JIF, CiteScore, SJR) |
| IEEE | 189 / 224 (JIF 2024) |
| ACM | 0 / 70 |
| Springer Nature | 0 / 620 |

`quartile_basis` always names the metric. Never present a CiteScore quartile as
a JIF quartile, and never compare them as though they were the same scale: a
journal can be Q1 on CiteScore and Q2 on JIF, and both statements are true.

For ACM and Springer titles, `best_quartile` is empty and `quartile_basis` reads
"not stated in source list". Two acceptable responses:

1. Report it as not stated in the provided list.
2. Look it up from SCImago or the journal page at recommendation time and cite
   that source explicitly.

Not acceptable: inferring a quartile from the publisher's other journals, from
the journal's apparent prestige, or from an impact factor recalled from training
data.

## Fields deliberately absent from every list

Acceptance rate, time to first decision, time to publication, APC, page or word
limits, accepted article types, template requirements, and special-issue status.
All of these are user priorities and none are in the data. See
`evidence-rules.md` for how to source them.

## Rebuilding

```bash
python scripts/build_catalog.py                     # regenerate assets/journals.csv
python scripts/build_catalog.py --out /tmp/test.csv  # dry run elsewhere
```

The script prints per-publisher counts and quartile coverage, which is the
quickest check that a replaced spreadsheet parsed correctly. If a publisher's
count changes unexpectedly after a source update, the header row probably moved:
IEEE and Springer both carry banner rows above their headers, and the parsers
hardcode those offsets with a comment explaining why.

Known parsing decisions worth preserving on any update:

- IEEE footnote rows are dropped by testing for a missing title, not by row
  index, so they stay dropped if the footnote count changes.
- Elsevier quartile cells containing `-` become empty, not Q4.
- Springer cells contain hard newlines inside titles and disciplines; these are
  collapsed to single spaces or titles will not match.
- Duplicate publisher+title pairs are retained if the source contains them, with
  a count printed, because silently deduplicating hides a source problem.
