# Source Quality

How to grade a confirmed source. Grading is separate from verification: a source
can be real (confirmed) yet weak (low tier) or compromised (flagged). Assign a
tier and note any flags in the source log.

## Contents

- Tiers
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
reviews them. Preprints are `tier_3` no matter how prestigious the authors,
because they have not been reviewed yet.

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

- **Predatory venue** — pay-to-publish with no real review, fake or absent
  editorial board, aggressive solicitation, suspicious metrics. Disqualifying.
- **Retraction** — check Retraction Watch and the publisher. A retracted paper
  is not cited as support; it may be cited only to discuss the retraction
  itself. Disqualifying as evidence.
- **Conflict of interest** — author or funder has a stake in the result (e.g.,
  a product's evidence base written by its vendor). Not disqualifying, but cite
  with the COI disclosed.
- **Predatory or unmatched metadata** — the DOI resolves but points to a
  different title or authors than logged. A mashup signal; do not cite until
  reconciled.
- **Overreach** — the source's own conclusions exceed its data. Cite only the
  part its evidence actually supports.

## How to weight sources in synthesis

When sources conflict, do not average them and do not pick the one you like.
Weight by evidence quality: a `tier_1` meta-analysis outweighs a `tier_4` blog,
and a large well-designed study outweighs a small flawed one. State the weighting
explicitly in the synthesis so the reader can see why one side of a conflict is
given more credence. When two high-quality sources genuinely disagree, report
the disagreement as an open question rather than resolving it artificially.
