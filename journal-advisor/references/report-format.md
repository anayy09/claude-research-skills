# Report format

Use this structure. It is ordered so the user can stop reading after the first
section if they only want the answer, and so the cost of publishing is never
further down the page than the recommendation that depends on it.

---

## Required structure

```
## Manuscript profile
Three to five lines: contribution, field, article type, novelty class, and the
constraints the user stated or that were inferred (corresponding-author
affiliation, OA requirement, budget, indexing requirement, deadline). No
restatement of the abstract. If only an abstract was supplied, say here that
the shortlist is provisional.

## Overall best recommendation
**<Journal> (<Publisher>)**, <fee route>, author pays <amount or "no APC
under this route">
One paragraph: why this one wins on the priority order, what the route costs
and what has to be true for it to hold, and the single tradeoff it carries.
Then the full field block (below).

## Shortlist
Five to ten defensible matches, either as one comparison table or grouped by
fee route in this order:
  1. Institution-covered open access, naming UF, MUJ or JKLU separately
  2. Open access with no APC regardless of affiliation, with other fees named
  3. Subscribe to Open, naming the funded year or volume
  4. Subscription publication with no APC, where the user accepts non-OA
Group by publisher only when the user asks. A journal reachable by several
routes is one entry with separate cost lines, not several ranked entries.

## Tradeoffs and what would change the ranking
Three to six lines. Name the decision the user actually faces: usually cost
against fit, or speed against quartile.

## Open eligibility checks
The conditions that remain unverified, per recommendation: corresponding-author
status, agreement term, article type, quota balance, ancillary fees. One line
each, phrased as something the user can go and check.

## Data notes
One or two lines: which fields were unavailable, whether live verification was
performed, and the snapshot date of the catalog against today's date.
```

## The field block

Every journal, in the overall recommendation and in every shortlist entry,
carries these items. Keep each to one line where possible.

- **Identity and fit**: title, publisher, ISSN where disambiguation needs it,
  and one or two sentences naming what in the journal's stated scope matches
  what in the manuscript. Specific, not "strong alignment with the journal's
  aims".
- **Fee route and author cost**: the route (`institutional_oa`, `no_apc_oa`,
  `s2o`, `subscription_no_apc`), the author-payable APC, and every other
  mandatory charge that is known or unknown. Say whether the version of record
  is open.
- **Coverage conditions**: for an institutional or S2O route, name which
  institution, which author role, the term, the cap and its balance, the
  covered article types, the evidence level, and what approval is still
  outstanding. A conditional route is never reported as guaranteed.
- **Article type**: the journal's own category this manuscript would be
  submitted under, and any invitation or presubmission gate.
- **Review speed**: the publisher-stated figure with its metric named, or
  "not publicly stated".
- **Indexing and quartile**: with the database, metric, category and year, or
  "not stated in the provided list". Never inferred from a DOAJ listing.
- **Acceptance prospects**: the published rate if there is one; otherwise the
  labeled proxies from `evidence-rules.md` and the fit-strength judgment.
- **Desk-reject risk**: low, medium, or high, with the driving factors and a
  remedy, per `desk-reject-rubric.md`.

A compact table works when the journals are similar; prose blocks work better
when they differ on different axes. Either is acceptable; do not mix them
within one section.

---

## Worked example of a single entry

> **2. Machine Learning: Science and Technology (IOP Publishing)**, open
> access, UF institutional route
>
> **Fit.** The journal publishes machine learning as a scientific method
> across the physical sciences, including method papers evaluated on
> scientific data rather than on general benchmarks; the manuscript's
> uncertainty-calibrated surrogate model sits inside that remit rather than at
> its edge.
>
> **Fee route and cost.** `institutional_oa`, UF. No author-payable APC if the
> corresponding author is UF-affiliated at acceptance and the allocation has
> not been exhausted. Other fees not stated by the source record; confirm on
> the author-charges page.
>
> **Coverage conditions.** UF is eligible for IOP lists A to D at **40
> accepted articles per year from 1 January**; the remaining balance is not
> published and is unknown here. Evidence is a publisher title list combined
> with the UF agreement page, not a per-author approval. If the quota is spent,
> this becomes a full-APC journal.
>
> **Article type.** Full-length paper.
>
> **Review speed.** Not publicly stated for this title as of <date>.
>
> **Indexing and quartile.** Not stated in the provided list; verify from
> SCImago or the journal page if the user needs it recorded. The DOAJ and
> agreement records carry no metric and one must not be inferred from them.
>
> **Acceptance prospects.** No acceptance rate published. Proxies: an
> explicitly interdisciplinary remit, and a stated requirement that the work
> advance the science rather than the architecture. Fit strength is the main
> favorable factor.
>
> **Desk-reject risk: medium.** Scope fit is good, but the journal expects a
> scientific result rather than a methods demonstration, and the manuscript
> currently leads with the architecture. Reframing the abstract around the
> physical finding would move this to low.

Note what the example does: names the route and what it is conditional on,
gives the quota and admits the balance is unknown, refuses to supply a quartile
the sources do not carry, marks review speed as unstated instead of guessing,
labels the acceptance reasoning as proxies, and gives the desk-reject rating a
reason and a remedy.

---

## Style rules

- Journal names in bold on first mention in each block.
- Name the fee route every time a cost is claimed. "No APC" alone is not a
  statement a user can act on.
- Never a bare "Q1"; always the metric and the year.
- Never a review time without its source and metric.
- Never turn a discount, a waiver policy, or an unknown into coverage, and
  never turn an absent APC into zero total cost.
- Do not move a waiver between institutions, or from one route to another,
  because the same journal appears under both.
- No superlatives about journals ("prestigious", "top-tier"). Give the
  quartile and let it speak.
- No padding. Five well-founded entries beat ten with three invented
  rationales, and the catalog holds thousands of titles, so a long list is
  cheap to produce and expensive to act on.
- Keep the whole report readable in a few minutes. A manuscript profile longer
  than five lines is doing the user's reading for them rather than advising.

## When the answer is "none of these"

If nothing is a defensible match, say so first and explain the gap in one
sentence: the topic sits outside what the catalog covers, or every fitting
title carries an APC the budget does not cover, or the only zero-cost routes
are subscription routes the user has ruled out. Then give the closest options
with honest low ratings, and name which constraint would have to move. Do not
manufacture fit.

A title absent from the catalog is not disqualified. Absence is a gap in a
snapshot, not a quality judgment: if a strong candidate is missing, verify its
scope and fee policy from primary sources and recommend it with that evidence
and a clearly recorded route.

## When live verification was unavailable

Say so once at the top, deliver the shortlist from the catalog with every
unverifiable field marked, and do not upgrade any conditional route to a
confirmed one. A provisional shortlist with honest gaps is useful. A shortlist
that reports a snapshot's `apc_payable=0` as certain funding is not.
