# Systematic Review

The protocol for `systematic` mode: an explicit, reproducible review following
PRISMA-style structure. The defining discipline of this mode is honesty about
what was actually searched. Do not manufacture a flow diagram of invented
numbers.

## Contents

- What makes a review "systematic"
- Protocol first
- The five stages
- Reporting real PRISMA counts
- Appraisal and certainty
- The honesty boundary

## What makes a review "systematic"

A systematic review differs from a narrative one by being reproducible: another
person following your documented search strategy and eligibility criteria would
arrive at the same set of included studies. Everything is specified in advance
and recorded: the question, the criteria, the databases, the search strings, the
screening decisions.

## Protocol first

Before searching, write the protocol:

- **Question**, in a structured form. For intervention questions, the PICO frame
  is standard: Population, Intervention, Comparison, Outcome. Adapt for other
  question types.
- **Eligibility criteria** — inclusion and exclusion rules for study design,
  population, date range, language, publication type.
- **Search strategy** — which databases/connectors, and the actual search
  strings (keywords, Boolean structure) for each.
- **Screening and extraction plan** — how records move from identified to
  included, and what data is pulled from each included study.

`assets/report_template.md` covers the general structure; the protocol section
above is specific to this mode.

## The five stages

1. **Protocol** — write and record the above.
2. **Search** — execute the documented search across every planned source. Log
   every query and its yield (see the source log in `references/verification.md`).
3. **Screening** — remove duplicates, then screen by title/abstract, then by
   full text, recording how many records are excluded at each step and the main
   reasons.
4. **Extraction and appraisal** — pull the planned data from each included
   study and assess its risk of bias (design quality, blinding, attrition,
   selective reporting, confounding).
5. **Synthesis and reporting** — synthesize (narratively or, where studies are
   comparable enough, quantitatively), and state the overall certainty.

## Reporting real PRISMA counts

The PRISMA flow reports how records moved through the four phases: Identified →
Screened → Eligibility (full-text assessed) → Included. Report only counts that
reflect searches actually run in this session. Structure:

```
Records identified (per source, summed)
  minus duplicates removed
= Records screened (title/abstract)
  minus records excluded (with reasons)
= Full-text articles assessed
  minus full-text excluded (with reasons)
= Studies included in synthesis
```

If the environment cannot support an exhaustive search (limited database access,
no network), do not invent the numbers. State plainly what was searched, that
the search is not exhaustive, and scope the conclusions to what was found. A
smaller honest review beats a large fabricated one.

## Appraisal and certainty

Assess each included study for risk of bias appropriate to its design, and note
it per study. For an overall certainty statement, a GRADE-style summary
communicates well: rate confidence in the body of evidence as high, moderate,
low, or very low, and say what drives the rating (risk of bias, inconsistency,
imprecision, indirectness, publication bias). Certainty is about the evidence
base as a whole, not any single study.

For quantitative synthesis (meta-analysis): only pool effect sizes when the
studies are genuinely comparable in population, intervention, and outcome, and
report heterogeneity honestly. If studies are too heterogeneous to pool, a
structured narrative synthesis is the correct choice — do not force a pooled
number that misrepresents a diverse evidence base. Do not report effect sizes,
confidence intervals, or heterogeneity statistics that were not computed from
real extracted data.

## The honesty boundary

This mode carries the most authority and so the most temptation to overstate.
The line: every number in the output traces to a real source or a search
actually performed. Screening counts, effect sizes, sample sizes, and certainty
ratings are reported, never invented. When the honest version is "I searched
these three databases, found eleven eligible studies, and here is what they
show," that is a complete and legitimate systematic review of what was done.
