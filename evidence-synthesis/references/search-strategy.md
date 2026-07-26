# Search strategy: construction and reporting

The search is the sampling frame. Everything the review can conclude is bounded
by it, which is why PRISMA-S asks for it verbatim rather than in summary.

## Concept blocks

Decompose the question into 2 to 4 concepts, usually mapping onto a framework:

- **PICO** for effect questions: Population, Intervention, Comparator, Outcome.
- **PICo** for qualitative: Population, phenomenon of Interest, Context.
- **SPIDER** for mixed methods: Sample, Phenomenon of Interest, Design,
  Evaluation, Research type.
- **PIRD** for diagnostic accuracy: Population, Index test, Reference standard,
  Diagnosis of interest.

Terms within a block are OR'd; blocks are AND'd. Three blocks is usually the
practical maximum. Adding a fourth block for the outcome often drops relevant
records, because outcomes are frequently absent from titles and abstracts even
when measured; the usual advice is to leave outcome out of the search and apply
it at screening.

## Controlled vocabulary and free text

Use both in every block, for every database that has a thesaurus:

- **MeSH** in PubMed and Cochrane, **Emtree** in Embase. Indexing lags
  publication by months, so recent papers are often unindexed. Controlled
  vocabulary alone will miss them.
- **Free text** in title, abstract and keywords catches the recent and the
  poorly indexed, and catches terminology the thesaurus has not adopted. This
  matters in fast-moving areas: a term like "foundation model" has no thesaurus
  entry long after it is in wide use.

Explode terms when the narrower concepts are all relevant; do not explode when
they are not, and say which you did.

## Truncation and phrases

Truncation (`term*`) is not applied inside quoted phrases on most platforms, so
`"deep learn*"` either errors or matches nothing. Truncate single tokens only.
`scripts/search_builder.py` enforces this.

Beware over-truncation: `nurs*` catches nursing, nurses, and nursery. Check the
term list a platform expands to when the interface offers it.

Spelling variants matter: randomised and randomized, tumour and tumor,
oesophageal and esophageal. Truncation sometimes covers these and sometimes does
not.

## Sensitivity against precision

Systematic reviews favour sensitivity: it is better to screen 3,000 records and
find everything than to screen 400 and miss a trial. Scoping and rapid reviews
can trade toward precision, but the trade must be stated.

Published methodological filters (for RCTs, diagnostic accuracy, prediction
models) improve precision at a known cost in sensitivity. If you use one, cite it
by name and version. An unnamed "filter" is unreproducible.

## Testing the strategy before running it

Two checks, both quick, both frequently skipped:

1. **Known-item testing.** Assemble 5 to 10 papers you already know should be
   included. If the strategy does not retrieve all of them, it is broken. When
   one is missed, look at how it is indexed and add the missing term.
2. **Peer review of the strategy (PRESS).** A librarian or a second reviewer
   checks line syntax, Boolean logic, spelling, and vocabulary coverage. Most
   errors found are mechanical, and mechanical errors silently halve a result
   set.

## Sources beyond bibliographic databases

An exhaustive search is not just databases:

- **Trial and review registries**: ClinicalTrials.gov, ICTRP, PROSPERO. Registry
  searching finds unpublished and ongoing work, which is directly relevant to
  publication bias.
- **Preprint servers**: medRxiv, bioRxiv, arXiv. Decide in the protocol whether
  preprints are eligible, and if they are, record the version.
- **Grey literature**: theses, government and agency reports, conference
  abstracts. Standard in scoping and policy-relevant reviews.
- **Citation chasing**: backward (reference lists of included studies) and
  forward (works citing them). Cheap and consistently productive. Record how many
  records this contributed; PRISMA 2020 has a separate arm of the flow diagram
  for records identified by methods other than database searching.
- **Contacting authors** for missing data or unpublished work.

## Restrictions and their cost

Every restriction is a decision with a bias implication, and belongs in the
eligibility criteria with a justification, not silently in the search string:

- **Language.** Restricting to English is common and is not neutral. The
  justification is usually resource constraint; say that rather than implying the
  non-English literature does not exist.
- **Date.** A start date needs a reason: a technology's introduction, a
  guideline's publication, a prior review's search end date. "The last ten years"
  is not a reason.
- **Publication type.** Excluding conference abstracts is defensible; excluding
  them silently is not, particularly in computer science and engineering where
  the primary venue is often a conference.

## Deduplication

Report the software and settings. Automated deduplication misses records with
differing metadata and occasionally removes distinct records with similar
titles. The count before and after deduplication is a PRISMA item and must
match the flow diagram.

## Updating before submission

Reviews take months and searches age. Rerun the search before submission and
report both dates. A search that ended fourteen months before submission invites
the objection that the review is already out of date, and the rerun usually costs
an afternoon.

## Reporting: PRISMA-S

PRISMA-S (Rethlefsen et al., 2021) is a 16-item extension covering search
reporting. The requirement that surprises people: full strategies for **every**
database and source, copied exactly as run, normally in a supplement. A single
strategy for one database with "adapted for other databases" does not meet it.

`scripts/search_builder.py --prisma-s` emits the record skeleton with the items
as explicit blanks, so an unreported item is visible rather than absent.
