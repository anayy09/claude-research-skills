# Catalog schema and provenance

The master `assets/journals.csv` contains one row per journal, fee route, and
source. Multiple routes for the same journal remain distinct and share a
`journal_id`. The 2026-09-19 catalog has 20,262 route records linked to 19,533
journal IDs. It is a research snapshot, not an exhaustive global directory.

## Source files

All inputs live in `assets/sources/`:

| Input | Contents |
|---|---|
| `IEEE.xlsx`, `Springer_Nature.xlsx`, `Elsevier.xlsx`, `ACM.xlsx`, `T_F.xlsx` | 1,848 MUJ/JKLU sponsored entries; the bundled workbooks, unchanged |
| `uf_100_percent_apc.csv` | 686 conditional UF full-APC coverage records |
| `no_apc_open_access.csv` | 14,645 DOAJ no-APC declarations and three publisher-policy records |
| `subscribe_to_open.csv` | 78 routes with year/volume and other-fee conditions |
| `subscription_no_apc.csv` | 3,002 non-OA routes without an OA APC |

CSV records retain source and policy URLs, research dates, eligibility, and
other-fee flags. `source_file` and `source_row` locate the input in this folder;
CSV row numbers include the header. Institution workbook provenance remains in
`assets/list-provenance.yaml`. See `evidence-rules.md` for funding conditions.

## Fields

| Field | Interpretation |
|---|---|
| `journal_id` | Derived ID linking matching print/electronic ISSNs; title-only fallback for missing identifiers |
| `route_id` | Derived ID for this source and funding route |
| `publisher`, `journal_title`, `issn`, `eissn` | Source identifiers; some ASME/S2O entries lack ISSNs |
| `journal_url`, `subject_area`, `scope` | Discovery metadata; keywords are not verified aims-and-scope prose |
| `oa_model` | Journal's source-reported publishing model; may lag a model change |
| `fee_route` | `institutional_oa`, `no_apc_oa`, `s2o`, or `subscription_no_apc` |
| `institution` | `UF`, `MUJ`, `JKLU`, or `any`; no implicit transfer of eligibility |
| `apc_payable` | `0` under the stated route's conditions; not total publication cost |
| `other_fees` | `no`, `yes`, `possible`, or `unknown`; only `no` passes the strict filter |
| `eligibility`, `article_types` | Conditions requiring verification for the manuscript |
| `agreement_start`, `agreement_end` | ISO date when explicitly available; blank means unknown, not perpetual |
| `annual_cap` | Published allocation (IOP UF: 40); blank is not unlimited |
| `evidence_status` | Source level, listed below; not author-level funding approval |
| `record_status` | `listed`, `superseded`, or `excluded`; listed does not independently prove active submissions |
| `source_url`, `policy_url`, `checked_on` | Discovery/policy provenance and retrieval/research date |
| `source_updated` | Source-reported update date; can precede retrieval by years |
| `source_file`, `source_sheet`, `source_row`, `source_record_id` | Exact input locator where available |
| `doaj_url`, `instructions_url`, `apc_information_url`, `other_fees_url` | Original fee/author-policy links |
| `license`, `languages`, `country` | Source journal metadata; journal article license is distinct from dataset license |
| `notes` | Limits, corrections, and unresolved conditions |

`evidence_status` values:

- `user_confirmed_mapping`: original lists mapped to MUJ/JKLU by the user;
  contracts and renewals have not been independently established.
- `institution_title_list`: UF finder or UF S2O title listing; current author
  and journal eligibility still needs verification.
- `publisher_title_list`: IOP current title lists combined with its UF terms.
- `publisher_catalog_plus_institution_policy`: ASME catalog plus UF agreement
  statement; not a title-by-title contract export.
- `source_reported`: DOAJ journal declaration; policies not individually fetched.
- `publisher_policy`: specific publisher fee statement checked in this research.
- `publisher_catalog_plus_policy`: Springer 2026 model plus subscription policy.
- `legacy_title_list_plus_current_policy`: Elsevier 2025 models plus current
  general subscription policy; verify the journal has not flipped to full OA.

Four fields describe the list a row came from rather than the journal:

| Field | Workbook rows | Fee-route CSV rows |
|---|---|---|
| `list_kind` | the workbook's `kind` from `list-provenance.yaml` | the route's `evidence_status` |
| `list_context` | the workbook's `scope` from the same file | blank |
| `coverage_note` | that scope plus the sponsoring institution | the route's `eligibility` |
| `fee_note` | the workbook's `fee_note` | the route's `notes` |

`assets/list-provenance.yaml` is the only place the five workbooks are
described; edit it there when a workbook is replaced.

Metric fields are populated only where a source supplied them: `index_wos`,
`scopus_covered`, `jif_2024`, `jif_quartile`, `citescore_2024`,
`citescore_quartile`, `sjr_2024`, `sjr_quartile`, `best_quartile` and
`quartile_basis` come from the IEEE, Elsevier and T&F workbooks, and are blank
for roughly 95% of records. `acronym` and `imprint` are similarly sparse. Do not
interpret 2024 metrics as current. `best_quartile` is the numerically best
available metric, with ties preferring JIF then CiteScore then SJR; it is not a
common ranking scale across those systems. Missing metrics stay blank. A route
without a metric can be cross-referenced to a matching ISSN's workbook record,
but never inherits its institution or fee terms.

## Rebuilding and refreshing

Searching uses Python's standard library. Rebuilding requires pandas, openpyxl
and PyYAML. From the skill directory, run:

```bash
python scripts/build_catalog.py
```

The builder reads the nine source files and writes only `assets/journals.csv`.
Use `--out PATH` to write elsewhere. It prints route and journal counts.

Update the source CSVs after checking the cited institution and publisher
policies. Record the actual research and source-update dates; confirm title
packages, dates, article types, caps, closures, and other fees. DOAJ's export is
available at <https://doaj.org/csv>: retain only explicit `APC=No`, preserve
other-fee declarations and continuation flags, and record its export date.
UF discovery starts at <https://guides.uflib.ufl.edu/openaccess/ufinvests> and its
linked <https://search.scifree.se/uflib> finder. Verify finder results against
current publisher terms. Do not convert discounts into full coverage or unknown
fees into zero. Keep URLs and limitations in each row, then rebuild the master.

## Identity limits

ISSNs are linked transitively across print/electronic values. An exact normalized
title bridges rows only where at least one lacks ISSNs. The search returns one
candidate with all matching routes. Derived IDs are deterministic for a fixed
input, but may change when identifiers are corrected; they are not external
persistent identifiers. Different title spellings without shared ISSNs can
remain separate. Counts are linked-record counts, not an independent serials
registry audit. Consult exact ISSNs before merging ambiguous titles.

## Data attribution and reuse

The repository's MIT license applies to the original skill instructions and
scripts. It does **not** relicense third-party metadata or source documents.

### DOAJ

The DOAJ rows in `sources/no_apc_open_access.csv` are a filtered and normalized
adaptation of the Directory of Open Access Journals journal CSV, downloaded from
<https://doaj.org/csv> on 2026-09-19. The delivered export filename was
`doaj_journalcsv_20260819_2320_utf8.csv`, a 2026-08-19 snapshot.

Journal metadata is licensed **Creative Commons Attribution-ShareAlike 4.0
International (CC BY-SA 4.0)**. Attribution: Directory of Open Access Journals
(DOAJ), <https://doaj.org/>. License:
<https://creativecommons.org/licenses/by-sa/4.0/>. Source terms:
<https://doaj.org/terms/>. DOAJ article metadata's CC0 license does not apply to
this journal dataset.

Changes: select `APC=No`; retain other-fee declarations, identifiers and policy
links; normalize whitespace; add provenance and route labels; flag continuation
records and known closures; join matching journal identifiers in the master.
The DOAJ-derived CSV and the adapted DOAJ material in `journals.csv` are supplied
under CC BY-SA 4.0. When redistributing the combined catalog, preserve attribution
and comply with ShareAlike for that adapted material. Do not label the entire
combined data export MIT.

### Other sources

UF and publisher lists are cited row by row. Their original text, webpages,
workbooks, journal names, and trademarks remain subject to their respective
owners' terms. No additional license grant over their source documents is
asserted. The five institution workbooks were supplied with the skill and are
preserved without changing their licensing status.

Three additional publisher-policy rows in `sources/no_apc_open_access.csv`
retain their URLs and checked dates. Dagstuhl separately releases its supplied
metadata under CC0 on the cited TGDK page; journal articles carry their own
stated licenses.
