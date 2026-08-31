# Source Quality

How to grade a confirmed source. Grading is separate from verification: a source
can be real (confirmed) yet weak (low tier) or compromised (flagged). Assign a
tier and note any flags in the source log.

## Contents

- Tiers
- Peer review is a property of the record, not of the publisher
- Checking peer-review status
- The evidence hierarchy (for empirical claims)
- Currency
- Red flags
- How to weight sources in synthesis

## Tiers

A coarse quality grade that applies across disciplines.

| Tier | What qualifies | Examples |
|------|----------------|----------|
| `tier_1` | Peer-reviewed, high-quality venue | Top-quartile journals, Cochrane/Campbell reviews, flagship conference proceedings with real peer review |
| `tier_2` | Peer-reviewed, standard venue | Other peer-reviewed journals and proceedings |
| `tier_3` | Credible but not peer-reviewed | Preprints, institutional and government reports (OECD, WHO, national statistics), working papers, dissertations |
| `tier_4` | Non-scholarly | Quality journalism, encyclopedias, industry white papers, expert blogs |

"Peer-reviewed" means formal external peer review, not editorial acceptance
alone. Conference papers count as peer-reviewed only when the venue actually
reviews them, which in computing usually means yes (IEEE and ACM conferences
are the reviewed venue of record) and in medicine usually means no (a conference
abstract is not a reviewed paper). Preprints are `tier_3` no matter how
prestigious the authors, because they have not been reviewed yet.

**Prefer tier 1 and tier 2 sources, and reach for them first.** A report built
on `tier_3` and `tier_4` sources when peer-reviewed work exists on the same
question is a search failure, not a source-availability problem. Search the
reviewed record first; `search_sources.md` gives the order and the surfaces.

## Peer review is a property of the record, not of the publisher

A rule like "prefer IEEE, Nature, and Elsevier" cannot be applied by matching a
publisher name or a DOI prefix, because the major publishers also run preprint
and working-paper servers under their own registrations:

| DOI prefix | Registrant | What it actually is |
|---|---|---|
| `10.1109` | IEEE | peer-reviewed journals and proceedings |
| `10.36227` | IEEE | TechRxiv, a preprint server |
| `10.1016` | Elsevier | peer-reviewed journals |
| `10.2139` | Elsevier | SSRN, working papers, not peer reviewed |
| `10.1038` | Springer Nature | Nature portfolio journals |
| `10.1101` | Cold Spring Harbor | bioRxiv and medRxiv, preprint servers |
| `10.20944` | MDPI | Preprints.org, a preprint server |
| `10.26434` | ACS | ChemRxiv, a preprint server |
| `10.48550` | arXiv, registered with DataCite | preprints |

Filtering by publisher would admit SSRN and TechRxiv while excluding a
peer-reviewed society journal with an unfamiliar prefix. Grade on the record
type and the venue instead.

## Checking peer-review status

`scripts/check_citations.py` does this automatically and writes the result to
the `peer_reviewed` field of the source log. The signals, all free and keyless:

| Question | Where | Field |
|---|---|---|
| Is it a preprint? | Crossref | `type == "posted-content"`, `subtype == "preprint"` |
| Is it a preprint? | OpenAlex | `type == "preprint"`, or `primary_location.source.type == "repository"` |
| Is it an arXiv preprint? | DataCite | `types.resourceTypeGeneral == "Preprint"` |
| Does the journal run peer review? | DOAJ | `bibjson.editorial.review_process` |
| Is the venue in the curated core? | OpenAlex `/sources/issn:<issn>` | `is_core`, `is_in_doaj` |
| Is there a published version? | Crossref | `relation["is-preprint-of"]` |

Peer-reviewed status is not a quality verdict. Peer review admits weak studies
routinely, and a careful preprint can be better than a reviewed paper in a
marginal journal. The status decides which version you cite and how you label
it; the evidence hierarchy below decides how much weight it carries.

## The evidence hierarchy (for empirical claims)

When a claim is about what causes what or what an intervention does, tier is not
enough; the study design matters. Roughly strongest to weakest:

1. Systematic reviews and meta-analyses of controlled trials
2. Individual randomized controlled trials
3. Non-randomized controlled and quasi-experimental studies
4. Cohort and case-control studies
5. Cross-sectional and descriptive studies
6. Single case reports and qualitative studies
7. Expert opinion and consensus statements

Two honest caveats. A meta-analysis is only as good as the studies inside it
("garbage in, garbage out"). And this hierarchy is built for questions where
experiments are possible; in fields where randomization is impractical or
unethical (much of education, economics, history), the top rungs are often
unreachable and a strong observational or qualitative study is the best evidence
available. Do not dismiss a well-designed observational study for not being an
RCT when an RCT was never an option. Match the standard to what the field can
actually produce.

## Currency

How recent a source must be depends on the field:

- Fast-moving (AI/ML, much of biomedicine): prefer the last ~3 years.
- General social science and policy: ~5 years is a reasonable default.
- Stable or historical fields (history, philosophy, foundational theory):
  older work is fine and often essential.

Seminal works are exempt from currency limits regardless of field. When a source
predates the useful window, either replace it or note the currency caveat in the
log and flag whether newer work has superseded it.

## Red flags

Note any of these in the source's `notes` field; some downgrade a source,
others disqualify it.

- **Predatory venue**: pay-to-publish with no real review, fake or absent
  editorial board, aggressive solicitation, suspicious metrics. Check whether
  the venue is in DOAJ (which records the review process) or carries
  `is_core: true` in OpenAlex. Disqualifying.
- **Retraction**: Crossref exposes the Retraction Watch database through
  `updated-by`, and OpenAlex through `is_retracted`; the checker queries both. A
  retracted paper is not cited as support; it may be cited only to discuss the
  retraction itself. Disqualifying as evidence.
- **Superseded preprint**: the cited preprint has since been peer reviewed and
  published. Cite the published version and re-read the claim against it,
  because numbers move during review. Disqualifying as a citation target, though
  the work itself is fine.
- **Conflict of interest**: author or funder has a stake in the result, for
  example a product's evidence base written by its vendor. Not disqualifying,
  but cite with the COI disclosed.
- **Unmatched metadata**: the DOI resolves but points to a different title or
  authors than logged. A mashup signal; do not cite until reconciled.
- **Overreach**: the source's own conclusions exceed its data. Cite only the
  part its evidence actually supports.

## How to weight sources in synthesis

When sources conflict, do not average them and do not pick the one you like.
Weight by evidence quality: a `tier_1` meta-analysis outweighs a `tier_4` blog,
and a large well-designed study outweighs a small flawed one. State the weighting
explicitly in the synthesis so the reader can see why one side of a conflict is
given more credence. When two high-quality sources genuinely disagree, report
the disagreement as an open question rather than resolving it artificially.
