# Peer-reviewed sources and the version of record

The default citation target is the **version of record**: the peer-reviewed,
publisher-issued version of a work. A preprint is a legitimate object to find
during searching and an illegitimate object to cite when a peer-reviewed version
of the same work exists. This file covers how to tell the difference
mechanically, how to upgrade a preprint to its published version, and where to
search so the peer-reviewed literature is what comes back first.

## Contents

- Why publisher name is not a peer-review signal
- Determining peer-review status
- Upgrading a preprint to the version of record
- When a preprint may be cited
- Publisher-native search surfaces
- Publisher-scoped metadata queries
- Platform quirks that silently break a strategy

## Why publisher name is not a peer-review signal

"Prefer IEEE, Nature, and Elsevier" cannot be implemented by matching a publisher
name or a DOI prefix, because the major publishers also operate preprint and
working-paper servers under their own prefixes:

| DOI prefix | Registrant | What it actually is |
|---|---|---|
| `10.1109` | IEEE | peer-reviewed journals and conference proceedings |
| `10.36227` | IEEE | **TechRxiv**, a preprint server |
| `10.1016` | Elsevier BV | peer-reviewed journals |
| `10.2139` | Elsevier BV | **SSRN**, working papers, not peer reviewed |
| `10.1038` | Springer Nature | Nature portfolio journals |
| `10.1101` | Cold Spring Harbor Laboratory | **bioRxiv / medRxiv**, preprint servers |
| `10.20944` | MDPI | **Preprints.org**, a preprint server |
| `10.26434` | ACS | **ChemRxiv**, a preprint server |
| `10.21203` | Research Square | preprints |
| `10.31234`, `10.31235` | Center for Open Science | PsyArXiv, SocArXiv, preprints |
| `10.48550` | arXiv, registered with **DataCite** rather than Crossref | preprints |

Two consequences follow. A filter on publisher would admit SSRN and TechRxiv
while excluding a peer-reviewed society journal with an unfamiliar prefix. And
any verifier that queries Crossref alone reports every arXiv DOI as nonexistent,
because arXiv registers with DataCite. That is a false fabrication verdict on a
real object, which is the worst error a citation checker can make.

Filter on **record type and venue**, never on publisher.

## Determining peer-review status

All of the following are free, keyless, and machine-checkable.
`scripts/verify_citations.py` queries them in roughly this order.

| Question | Source | Field |
|---|---|---|
| Is this a preprint? | Crossref | `type == "posted-content"`, usually with `subtype == "preprint"` |
| Is this a preprint? | OpenAlex | `type == "preprint"`, or `primary_location.source.type == "repository"` |
| Which version is this? | OpenAlex | `primary_location.version`: `submittedVersion`, `acceptedVersion`, `publishedVersion` |
| Is this a journal article? | Crossref | `type == "journal-article"` |
| Is this a reviewed conference paper? | Crossref | `type == "proceedings-article"`, then check the venue |
| Who registered the DOI? | `https://doi.org/ra/<prefix>` | `RA`: `Crossref` or `DataCite` |
| Is this an arXiv preprint? | DataCite | `attributes.types.resourceTypeGeneral == "Preprint"` |
| Does the journal run peer review? | DOAJ | `bibjson.editorial.review_process`, for example `["Anonymous peer review"]` |
| Is the venue in the curated core? | OpenAlex `/sources/issn:<issn>` | `is_core`, `is_in_doaj`, `type` |
| Is it indexed in a reviewed corpus? | OpenAlex | `indexed_in` contains `pubmed` |
| Preprint or reviewed, life sciences? | Europe PMC | `SRC:PPR` marks preprints; `SRC:MED` and `SRC:PMC` do not |

`proceedings-article` deserves care. In computer science and engineering the
conference is often the primary peer-reviewed venue, and a paper there outranks
a journal article; elsewhere a "conference paper" may be an unreviewed abstract.
Record which venue it is, and whether that venue reviews full papers, rather than
treating the record type as the answer.

## Upgrading a preprint to the version of record

Run this before extraction, not after writing. A preprint and its published
version differ in ways that change a review: numbers move during review, analyses
get added, and conclusions get softened.

1. **Crossref relation.** On the preprint record, `relation["is-preprint-of"]`
   carries the published DOI. Confirmed live: `10.1101/2020.03.22.20040915`
   resolves with `is-preprint-of -> 10.3390/biology9050097`, and the published
   record carries the reciprocal `relation["has-preprint"]`.
2. **bioRxiv and medRxiv API.** `https://api.biorxiv.org/details/biorxiv/<doi>`
   and the `medrxiv` equivalent return a `published` field holding the journal
   DOI once the paper appears, and `type: PUBLISHAHEADOFPRINT` on the record.
3. **OpenAlex locations.** A work's `locations` array lists every version. If one
   has `source.type == "journal"` and `version == "publishedVersion"`, that is the
   version of record. arXiv preprints that were later published usually merge
   into the published work's OpenAlex record.
4. **Europe PMC.** Search the exact title with `NOT SRC:PPR` to see whether a
   reviewed version exists in MED or PMC.
5. **Title search as the last resort.** Query Crossref with
   `query.bibliographic=<title>&filter=type:journal-article`. Compare authors and
   abstract before accepting the match; a same-title paper by different authors is
   a different paper.

If a published version is found, cite it, and re-extract the data from it. Keep
the preprint in the search log so the audit trail shows how the record was
reached, and keep it out of the reference list.

`scripts/verify_citations.py --upgrade-preprints` does steps 1 to 3 for a whole
reference list and prints the replacement DOI per entry.

## When a preprint may be cited

Preprints are eligible when the protocol says so in advance, and the protocol
should say so for fast-moving fields where the peer-reviewed record lags by a
year or more. When they are eligible:

- State the eligibility decision in the protocol, not in the discussion.
- Record the **version** and the access date. Preprints are mutable, and "v2" is
  part of the citation.
- Label them as preprints in the evidence table and in the reference list.
- Rate them down for risk of bias, or handle them in a sensitivity analysis that
  shows whether the conclusion depends on unreviewed evidence.
- Re-check for a published version before submission. A search run eight months
  before submission will have missed publications since.

A preprint that was rejected and never published is not the same as a preprint
still under review, and neither state is visible from the record. Say so in the
limitations rather than implying preprint status is a neutral formatting detail.

## Publisher-native search surfaces

Federated indexes (Scopus, Web of Science, Europe PMC) give reproducible,
exportable results and should carry the primary search. Publisher platforms are
worth running in addition, because they index full text that the abstract-level
indexes do not, and because a subscription often reaches content the index
records only as metadata.

| Publisher or corpus | Surface | Search syntax notes |
|---|---|---|
| IEEE | IEEE Xplore **Command Search** | fielded terms as `("All Metadata":term)`, also `"Document Title"`, `"Abstract"`, `"Author Keywords"`, `"Publication Title"`; wildcards `*` and `?`; nested parentheses supported |
| Springer Nature, including the Nature portfolio | SpringerLink advanced search, nature.com search | **no truncation operator**: every morphological variant must be listed explicitly |
| Elsevier | Scopus for the systematic search, ScienceDirect for full text | Scopus uses `TITLE-ABS-KEY(...)`; ScienceDirect caps Boolean connectors per field and rejects long strategies, so split them or run the strategy in Scopus |
| ACM | ACM Digital Library advanced search | fielded as `Title:(...)`, `Abstract:(...)`, `AllField:(...)` |
| Wiley | Wiley Online Library advanced search | fielded, supports wildcards |
| Biomedical, keyless and free | Europe PMC REST API | `TITLE:`, `ABSTRACT:`, `AUTH:`, `SRC:`; `NOT SRC:PPR` removes preprints |
| Cross-publisher, keyless and free | Crossref REST, OpenAlex | filter by type and member, see below |

`scripts/search_builder.py` renders one concept-block specification into all of
these, so the strategies cannot drift apart. Run it with `--peer-reviewed-only`
to append each platform's document-type restriction.

The paid publisher APIs (IEEE Xplore API, Springer Nature API, Elsevier Scopus
and ScienceDirect APIs) all require a registered key and, for Elsevier,
institutional entitlement. They are worth setting up for a review that will be
updated, and unnecessary for a one-off search a human can run in the web
interface. Do not write a script that assumes a key exists.

## Publisher-scoped metadata queries

Crossref `member` IDs restrict a metadata query to one publisher's output. These
were confirmed against the live API:

| Publisher | Crossref member ID |
|---|---|
| IEEE | 263 |
| Elsevier BV | 78 |
| Springer Science and Business Media (Springer Nature, including Nature) | 297 |
| ACM | 320 |
| Wiley | 311 |

```
https://api.crossref.org/works
  ?query.bibliographic=<terms>
  &filter=type:journal-article,member:263
  &rows=20&mailto=<you@institution.edu>
```

`filter=type:journal-article` is what excludes preprints; `member` is what scopes
to a publisher. Use the pair, never `member` alone, since member 78 also returns
SSRN and member 263 also returns TechRxiv.

This is a **supplement to**, not a replacement for, a database search. Crossref is
a registration agency: its records are what publishers deposited, its subject
indexing is thin, and relevance ranking on `query.bibliographic` is not a
substitute for a controlled-vocabulary search.

## Platform quirks that silently break a strategy

Each of these produces a plausible-looking result set that is wrong, which is
worse than an error message:

- **SpringerLink has no truncation.** A strategy built with `neoplas*` returns
  nothing useful there. Expand to `neoplasm OR neoplasms OR neoplastic` before
  running it, and report the expanded version as the strategy actually run.
- **ScienceDirect limits Boolean connectors per field** and does not accept the
  long OR-chains a systematic search needs. Run the search in Scopus and use
  ScienceDirect only for full-text follow-up, or split the strategy into blocks
  run separately and report the split.
- **Quoted phrases are not truncated on most platforms.** `"deep learn*"` either
  errors or matches nothing. Truncate single tokens only; `search_builder.py`
  enforces this.
- **IEEE Xplore command search has a term ceiling.** Very large OR-chains are
  rejected or silently truncated. Split the block and report the split.
- **Preprint servers are indexed inconsistently.** Scopus and Web of Science
  largely exclude preprints, Europe PMC includes them under `SRC:PPR`, and Google
  Scholar mixes versions of the same paper without labelling them. Deduplicate
  preprint-and-published pairs explicitly, and count the pair once in the PRISMA
  flow.
- **Google Scholar is not reproducible.** Results are personalized and unstable,
  there is no export of a full result set, and the same query run twice returns
  different counts. Use it for citation chasing and for finding a known item,
  never as a database of record in a PRISMA-S table.
