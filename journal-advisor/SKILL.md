---
name: journal-advisor
description: >-
  Recommend academic journals for a manuscript using only the five bundled
  publisher lists (IEEE, Springer Nature, Elsevier, ACM, Taylor & Francis).
  Reads the title, abstract, keywords, and full text, then produces one overall
  best recommendation plus a ranked list of three to five journals per
  publisher, each with topical fit, review-speed evidence, Scopus/SCImago
  indexing and quartile, matching article type, submission constraints (APC,
  page limits, template, novelty expectations), and a low/medium/high
  desk-reject risk assessment. Priorities are weighted in this order: likelihood
  of acceptance, review speed, then quartile and indexing. Use whenever the user
  asks where to submit a paper, which journal fits a manuscript, whether a target
  venue is a good match, how to shortlist venues, what the desk-reject risk is,
  or asks to compare candidate journals. Also use when a manuscript or abstract
  is supplied with a question about placement. Never recommend a journal outside
  the bundled lists.
summary: "Match a manuscript to the right journal, with desk-reject risk, from five publisher catalogs."
version: "1.0.1"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-08-04"
---

# Journal Advisor

Recommend venues for a manuscript from a fixed permitted set: the five publisher
lists bundled in `assets/sources/`, normalized into `assets/journals.csv`
(1,848 titles). A journal not in those lists is not recommendable here, whatever
its reputation. Absence from the lists is a statement about permission, not about
quality, and should be reported that way.

The advice must be usable. That means every claim is either read from the
catalog, read from the journal's own current page, or explicitly labeled as
absent. Inventing an acceptance rate, a turnaround time, or an APC is worse than
saying the publisher does not state one, because the user will act on it.

## What the lists contain, and what they do not

| Field | IEEE | Springer | Elsevier | ACM | T&F |
|---|---|---|---|---|---|
| Title, ISSN | yes | yes | yes | yes | yes |
| OA model | yes | yes | yes | yes | yes |
| Subject/discipline | no | yes | no | no | yes |
| Scope text | no | no | no | 18 of 70 | no |
| Quartile | 189/224 (JIF) | none | 641/650 (CiteScore) | none | 226/284 (JIF/CiteScore/SJR) |
| WoS / Scopus coverage | Index column | no | no | no | yes |
| **Acceptance rate** | **no** | **no** | **no** | **no** | **no** |
| **Review speed** | **no** | **no** | **no** | **no** | **no** |
| **APC, page limits, article types** | **no** | **no** | **no** | **no** | **no** |

The bottom three rows are the user's top priorities and none of them are in the
data. They must come from each journal's own page at recommendation time, and
where the publisher does not state them, the report says so. Springer Nature and
ACM carry no quartile at all: report "not stated in the provided list" and, if
needed, look it up from SCImago rather than inferring it from a sibling journal.

`references/catalog-schema.md` has the full field map and what each list is
(three of the five are agreement or eligibility lists, not complete publisher
catalogs).

## Workflow

**1. Build the manuscript profile.** From the full text, not just the abstract:

- Core contribution in one sentence, and the claim it rests on.
- Field and subfield, plus the adjacent field it could also be pitched to.
- Article type: full research article, short communication, review, tools or
  software paper, dataset or resource paper, case study, position paper.
- Empirical basis: dataset scale, whether it is public or restricted, human
  subjects and ethics approval, clinical validation status.
- Novelty class: new method, new application of a known method, new benchmark or
  evaluation, negative or replication result. This drives desk-reject risk more
  than anything else.
- Constraints the user stated: budget for APC, deadline, indexing requirement,
  institutional agreement.

If the manuscript is long, read it in full before shortlisting. Recommending
from the abstract alone produces plausible venues that mismatch on article type
or empirical standard, which is the expensive kind of wrong.

**2. Shortlist from the catalog.**

```bash
python scripts/find_journals.py --query "<title + keywords + 10-15 abstract terms>" \
  --per-publisher 8
python scripts/find_journals.py --query "..." --max-quartile Q2 --require-quartile
python scripts/find_journals.py --check "Computers in Biology and Medicine"
python scripts/find_journals.py --list-subjects --publisher "Taylor & Francis"
```

The scorer is lexical and the catalog text is thin, so treat its output as a
candidate pool of roughly 8 to 12 per publisher, not a ranking. Read the titles
and discard obvious mismatches yourself. Run `--check` on any journal the user
names, and on any journal about to enter the report, to confirm it is permitted.

**3. Verify each finalist.** For every journal that will appear in the report,
consult its official page and record: aims and scope, accepted article types,
stated acceptance rate, stated review times, APC, length or page limits, required
template, and any submission gate (presubmission enquiry, member sponsorship,
special issue only). Rules for what counts as evidence and how to phrase absent
information are in `references/evidence-rules.md`. Never carry a number over from
a similar journal or from memory of an older figure.

If web access is unavailable, say so once, mark every unverifiable field as "not
verified in this session", and keep the recommendation limited to what the
catalog supports. A shortlist with honest gaps is useful; a shortlist with
invented turnaround times is not.

**4. Rank by the stated priorities.** In order:

1. **Likelihood of acceptance.** Published acceptance rate where stated.
   Otherwise the evidence-based proxies in `references/evidence-rules.md`,
   each labeled as a proxy. Scope fit dominates: a manuscript squarely inside a
   journal's stated scope at a selective venue often beats a marginal fit at a
   permissive one.
2. **Review speed.** Publisher-stated median or mean times to first decision and
   to publication. Where absent, say "not publicly stated" and do not substitute
   an impression.
3. **Quartile and indexing.** From the catalog where present, from SCImago or
   the publisher page otherwise, with the metric named (JIF, CiteScore, or SJR
   quartiles are different claims).

When the priorities conflict, follow the order, state the tradeoff in one
sentence, and let the user decide. Do not silently optimize for quartile because
it is the easiest field to fill in.

**5. Assess desk-reject risk** for each finalist as low, medium, or high, using
the rubric in `references/desk-reject-rubric.md`. Give the one or two specific
factors driving the rating. "Medium" with no reason is not an assessment.

**6. Write the report** in the exact structure in `references/report-format.md`:
one overall best recommendation with justification, then three to five ranked
journals per publisher, then a short tradeoff note.

## Hard constraints

- **Only bundled titles.** If the ideal venue is outside the lists, name that
  fact plainly and recommend the best permitted alternatives.
- **No invented numbers.** Acceptance rates, review times, APCs, and impact
  metrics are quoted with a source or marked as not stated.
- **No predatory venues.** The bundled lists are all established publishers, so
  this mostly means not drifting outside them. If the user proposes an outside
  venue with predatory markers (guaranteed acceptance, fake indexing claims,
  solicited-by-email, no traceable editorial board), say so directly.
- **Distinguish the metric.** Q1 by CiteScore, by JIF, and by SJR are different
  statements. Always name which one, and the year.
- **Do not overstate fit.** If nothing in the permitted lists is a good match,
  say that. Three weak recommendations presented as strong ones waste a
  submission cycle, which costs months.
- **No preference between publishers** beyond what the evidence supports.

## Handing off

The recommendation ends this skill's job. Once a venue is chosen,
`submission-formatter` builds the submission in that publisher's template, and
`submission-reviewer` scores the manuscript before it goes up. Name the next step
in one line rather than starting it here.

## Tone

Concise and factual, the way a senior colleague advises. Short paragraphs and
compact tables. No hedging filler, no motivational framing, no restating the
manuscript back to the user at length. Where the evidence is thin, one clause
saying so is enough.

## Reference files

- `references/catalog-schema.md` — what each list is, per-field coverage,
  provenance, and rebuilding the catalog.
- `references/evidence-rules.md` — where each required field comes from, what
  counts as evidence for acceptance rate and review speed, permitted proxies,
  and the exact phrasing for absent data.
- `references/desk-reject-rubric.md` — low/medium/high criteria, the common
  desk-reject causes by manuscript type, and how to reduce risk before
  submission.
- `references/report-format.md` — the required output structure with a worked
  example.
