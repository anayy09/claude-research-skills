---
name: journal-advisor
description: >-
  Recommend academic journals for a manuscript with an explicit publishing-cost
  route: MUJ and JKLU sponsored lists, University of Florida full APC coverage,
  no-APC open access, Subscribe to Open, and subscription publication without an
  APC. Reads the manuscript, verifies current scope and author eligibility, and
  ranks by likelihood of acceptance, then review speed, then indexing and
  quartile, with a low/medium/high desk-reject risk per venue. Use when the user
  asks where to submit a paper, which journal fits a manuscript, how to shortlist
  or compare venues, what the desk-reject risk is, or says "which journal", "APC",
  "read-and-publish", "is the fee covered", "free to publish", or "no APC"; and
  whenever a manuscript or abstract arrives with a question about placement.
  Fee coverage is always reported as conditional until eligibility is verified.
summary: "Match manuscripts to journals with verified fee routes, institutional eligibility, and desk-reject risk."
version: "2.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-09-19"
---

# Journal Advisor

Recommend a defensible place to submit the manuscript, with a usable publishing
route and explicit author costs. Start from the bundled catalog; expand with
current primary-source evidence when a strong candidate is absent from it.

The advice must be usable. Every claim is either read from the catalog, read
from the journal's own current page, or explicitly labeled as absent. Inventing
an acceptance rate, a turnaround time, or a fee waiver is worse than saying the
publisher does not state one, because the user will act on it. The catalog is a
research snapshot, not a closed whitelist and not a funding approval.

## Fee routes and author context

The five bundled workbooks represent **MUJ** (Manipal University Jaipur: IEEE,
Springer Nature, Elsevier, Taylor & Francis) and **JKLU** (JK Lakshmipat
University: ACM) sponsorship, as identified by the user on 2026-09-19. **UF**
means University of Florida. Preserve that mapping; it does not establish an
author's eligibility or renew an old contract. Do not assume the user personally
holds all three affiliations.

Separate four routes in every recommendation:

| Route | What zero APC means | Essential qualification |
|---|---|---|
| `institutional_oa` | An eligible institution or agreement covers the whole APC | Corresponding author, title, article type, dates, cap and approval must all match |
| `no_apc_oa` | The OA journal states no APC, independent of any agreement | Other fees can still exist; distinguish diamond OA from APC-free only |
| `s2o` | Subscribe to Open gives no-APC OA for a funded year or volume | Verify that year opened, and any submission restrictions |
| `subscription_no_apc` | The author chooses non-OA publication and pays no OA APC | The version of record may be paywalled; page, submission and colour fees may apply |

Partial discounts and discretionary waivers are not full coverage. Absence of an
APC is not zero total cost. `other_fees=unknown` is not `other_fees=no`. For a
strict zero-total-budget shortlist, use records that explicitly declare no other
fees and verify the current author guidelines. A subscription route and green
repository deposit are both different from immediate publisher OA; check what
the user's funder requires before offering either.

Establish the corresponding-author affiliation, article type, expected
submission and acceptance dates, OA requirement, indexing requirement, budget,
and deadline. Infer what the manuscript already provides rather than asking for
it again. While the affiliation is unknown, shortlist the universal routes and
show institutional routes as conditional.

## Workflow

**1. Build the manuscript profile.** From the full text, not just the abstract:

- Core contribution in one sentence, and the claim it rests on.
- Field and subfield, plus the adjacent field it could also be pitched to.
- Article type: full research article, short communication, review, tools or
  software paper, dataset or resource paper, case study, position paper.
- Empirical basis: dataset scale, public or restricted, human subjects and
  ethics approval, clinical validation status.
- Novelty class: new method, new application of a known method, new benchmark or
  evaluation, negative or replication result. This drives desk-reject risk more
  than anything else.
- Constraints: budget, deadline, indexing requirement, OA mandate, affiliation.

Recommending from an abstract alone produces plausible venues that mismatch on
article type or empirical standard, which is the expensive kind of wrong. When
only an abstract is available, label the shortlist provisional and say so; do
not imply the full text was read.

**2. Shortlist from the catalog.** Treat lexical results as a candidate pool,
not a ranking. Search related topic terms too, because thin title metadata
misses strong matches.

```bash
python scripts/find_journals.py --query "medical imaging machine learning" --institution UF -n 15
python scripts/find_journals.py --query "materials physics" --institution UF --route institutional_oa
python scripts/find_journals.py --query "artificial intelligence" --institution none --open-access-only --no-other-fees
python scripts/find_journals.py --query "clinical decision" --route subscription_no_apc
python scripts/find_journals.py --query "robotics" --institution MUJ,JKLU --as-of 2026-10-01
python scripts/find_journals.py --check "Computers in Biology and Medicine" --institution UF
python scripts/find_journals.py --check "2632-2153" --json
```

`--institution UF` returns the universal routes plus UF's; add `--route
institutional_oa` to isolate the agreements. `--institution none` drops the
institutional routes. With no institution filter every route is shown, and all
institutional ones are conditional. `--check` lists every known route for a
title or ISSN and whether each passes the current filters. Expired, future,
closed and superseded records stay out of ordinary search; a record with no
agreement dates is **unconfirmed**, not perpetual. Results group by journal, and
a waiver is never carried from one institution or route to another. Use `--json`
for the full conditions and source links.

**3. Verify each finalist live.** Read the official aims and scope, the accepted
article types, whether submissions are currently open, the author guidelines,
the fee policy, and the relevant institution or publisher agreement. Confirm the
exact title and ISSN, the corresponding-author requirement, the covered article
type, the acceptance or submission window, the quota balance where one exists,
and every charge the route does not cover. A title absent from the catalog may
be recommended on the same primary-source evidence with its route recorded; no
invented membership.

**4. Rank the feasible matches.** Apply the hard constraints first (budget, OA
requirement, eligibility, article type, indexing). Then rank:

1. **Likelihood of acceptance.** A published acceptance rate where one exists,
   otherwise the labeled proxies in [evidence-rules.md](references/evidence-rules.md).
   Scope fit dominates: a manuscript squarely inside a selective journal's scope
   often beats a marginal fit at a permissive one. Never invent a probability.
2. **Review speed.** The publisher-stated median or mean, with the metric named.
   Where absent, "not publicly stated". A fast first decision is not a promise of
   fast peer review or fast publication.
3. **Quartile and indexing.** With the database, metric, category and year named,
   because Q1 by JIF, by CiteScore, and by SJR are three different claims.

When the priorities conflict, follow that order, state the tradeoff in one
sentence, and let the user decide. Do not silently optimize for quartile because
it is the easiest field to fill in.

**5. Assess desk-reject risk** for each finalist as low, medium, or high using
[desk-reject-rubric.md](references/desk-reject-rubric.md), naming the one or two
factors driving the rating and a remedy. "Medium" with no reason is not an
assessment. Fee coverage says nothing about fit.

**6. Write the report** in the structure in
[report-format.md](references/report-format.md): one overall recommendation, a
ranked shortlist grouped by fee route, the tradeoffs, the open eligibility
checks, and the data notes. Group by publisher only when asked.

## Hard constraints

- **No invented numbers.** Acceptance rates, review times, APCs, quotas and
  impact metrics are quoted with a source or marked as not stated.
- **No manufactured coverage.** A discount is not a waiver, a title list is not
  an approval, and `unknown` is not `no`. Every institutional and S2O route is
  reported as conditional, with its conditions named.
- **No transferred eligibility.** MUJ funding never applies to a UF or JKLU
  author, and a route's terms never migrate to another route for the same title.
- **No fee claim without its route.** "No APC" alone is not actionable; name
  which of the four routes produces it and what the author still pays.
- **Distinguish the metric.** Q1 by CiteScore, by JIF, and by SJR are different
  statements. Always name which one, the category, and the year.
- **A DOAJ listing proves none of:** Scopus or WoS indexing, a quartile, that
  submissions are open, or that the venue suits this manuscript. Some source
  serials are proceedings, magazines, or invitation-only review journals;
  confirm each finalist is the venue type the user wants.
- **No predatory venues.** If the user proposes one with predatory markers
  (guaranteed acceptance, fake indexing claims, solicited by email, no traceable
  editorial board), say so directly.
- **Do not overstate fit.** The catalog holds thousands of titles, so a long
  shortlist is cheap to produce and expensive to act on. If nothing fits, say so.
- **Absence is not disqualification.** A title missing from the snapshot is a gap
  in the research, not a quality judgment.

## Evidence discipline

- `assets/journals.csv` is **one row per journal, fee route and source**, not one
  row per journal. Read [catalog-schema.md](references/catalog-schema.md) for the
  fields, the identity linking, rebuilding, and the data licenses.
- The snapshot was researched on **2026-09-19**. The DOAJ export is dated
  **2026-08-19** and individual records may be older still; the workbook metrics
  are 2024 and the Elsevier list is 2025. A retrieval date does not make old
  evidence current.
- Never infer a fee, an indexing status, or a metric from a sibling journal, from
  a publisher's reputation, or from memory of an older figure.
- If live verification fails, say so once, give a provisional shortlist, and name
  what remains unverified. Do not certify funding from a snapshot.
- Each source CSV carries its policy URLs, research dates and eligibility limits;
  retain them when updating the catalog.

## Handing off

The recommendation ends this skill's job. Once a venue is chosen,
[`submission-formatter`](../submission-formatter) builds the submission in that
publisher's template and [`submission-reviewer`](../submission-reviewer) scores
the manuscript before it goes up. Name the next step in one line rather than
starting it here.

## Tone

Concise and factual, the way a senior colleague advises. Short paragraphs and
compact tables. No hedging filler, no motivational framing, no restating the
manuscript back to the user at length. Where the evidence is thin, one clause
saying so is enough.

## Reference files

- `references/catalog-schema.md`: the fields, what each source list is, how
  journal identity is linked, rebuilding, and the DOAJ attribution.
- `references/evidence-rules.md`: where each reported field may come from, the
  permitted acceptance and review-speed proxies, the exact phrasing for absent
  data, and the per-institution eligibility exceptions and exclusions.
- `references/desk-reject-rubric.md`: the low/medium/high criteria, the common
  causes by manuscript type, and how to reduce risk before submitting.
- `references/report-format.md`: the required output structure, the per-journal
  field block, and a worked example.

## Loading discipline

Load this skill once per session, before the step it governs, and do not invoke
it again when it is already in context; a second load re-injects the same text
and nothing else. When a repository carries `docs/SKILL-ROUTING.md`
(`project-ledger`), it names the skill for each step and file; follow it, and
record the skill in that step's progress entry. When a brief names several
skills, each is loaded at the step it governs, not all at the start.
