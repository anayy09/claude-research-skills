---
name: evidence-synthesis
description: >-
  Plan, run, appraise, and report literature reviews and evidence syntheses:
  systematic, scoping, rapid, umbrella, living, diagnostic accuracy, and
  prediction-model reviews. Covers review-type selection, protocol and
  registration, concept-block search construction with PRISMA-S reporting,
  screening logs with a reconciling PRISMA 2020 flow diagram, risk-of-bias tool
  selection (RoB 2, ROBINS-I, QUADAS-2, PROBAST+AI, AMSTAR 2, ROBIS), synthesis
  with or without meta-analysis, GRADE certainty rating, executable citation
  verification including retraction checking, and RAISE-compliant disclosure of
  AI use. Use when the user asks for a literature review, systematic review,
  meta-analysis, scoping review, evidence summary, PRISMA anything, "what does
  the evidence say", critical appraisal of a study or review, help checking
  whether references are real, or how to report a search. Also use when a
  reviewer has raised a methods objection about a review.
summary: "Plan, run, appraise, and report systematic and other evidence syntheses (PRISMA, GRADE, RoB)."
version: "1.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-07-26"
---

# Evidence Synthesis

A review is a research design, not a reading exercise. It has a protocol, a
sampling frame (the search), an eligibility rule, a measurement instrument (the
appraisal tool), an analysis, and a reporting standard. Treating it as anything
less produces a document that reads like a review and cannot be reproduced.

This skill is written to be run inside one conversation with executable checks
at the points where reviews usually break. It does not delegate to subagents and
does not depend on any other skill.

## Three rules with mechanisms behind them

**1. A citation you cannot confirm does not go in the document.** Not flagged as
uncertain, not softened with a hedge. Removed. Two distinct failures need two
distinct checks: fabrication (the work does not exist, or the DOI points
somewhere else) and retraction (the work exists but has been withdrawn). A DOI
that resolves proves only the first. Run `scripts/verify_citations.py` on every
reference list before it goes anywhere.

**2. The numbers in the flow diagram must reconcile.** Not approximately.
Records that vanish between boxes are the single most common arithmetic error in
published reviews, and it is the first thing a methods reviewer recomputes. Log
decisions as you screen with `scripts/screening_log.py`, and derive the diagram
from the log rather than counting by hand at the end.

**3. Disclose AI use where it made or informed a judgment.** Screening,
extraction, appraisal, and interpretive summarizing all qualify. This is now an
explicit expectation: Cochrane, the Campbell Collaboration, JBI and the
Collaboration for Environmental Evidence issued a joint position statement in
2025 supporting the RAISE recommendations (Thomas et al., 2025), which hold the
synthesist responsible for the output, require human oversight, and require
transparent reporting of any AI use that makes or suggests judgments. See
`references/ai-use-reporting.md` and `templates/ai-disclosure.md`.

## Step 1: choose the review type before anything else

The type determines the protocol, the reporting guideline, the appraisal tool,
and how long this will take. Getting it wrong is expensive to correct later.

| If the question is | Review type | Reporting guideline |
|---|---|---|
| Does X work, and how well | systematic review (+/- meta-analysis) | PRISMA 2020 |
| What exists in this area, what are the gaps | scoping review | PRISMA-ScR |
| Decision needed in weeks, not months | rapid review | PRISMA 2020 + stated shortcuts |
| Several systematic reviews already exist | umbrella review / overview | PRISMA 2020 + AMSTAR 2 on the reviews |
| Evidence changes fast, needs continuous updating | living systematic review | PRISMA-LSR |
| How accurate is this test | diagnostic test accuracy review | PRISMA-DTA + QUADAS-2 |
| How good are these prediction models | prediction model review | TRIPOD+AI for reporting, PROBAST+AI for appraisal, CHARMS for extraction |
| What do people experience | qualitative evidence synthesis | ENTREQ (PRISMA-QES in development) |

Full decision guidance, effort estimates, and what each type may and may not
claim are in `references/review-types.md`.

## Step 2: protocol first

Write the protocol before screening, and register it. PROSPERO for health
reviews, OSF or the Open Science Framework registries otherwise. A protocol
written after screening is a description, not a preregistration, and the
difference is visible in the timestamps.

Use `templates/protocol.md`. The elements that matter most and are most often
vague: the eligibility criteria stated so a second person would apply them
identically, the primary outcome fixed in advance, and the planned synthesis
method chosen before the data are seen.

## Step 3: build and report the search

```bash
python scripts/search_builder.py --example > search.yaml   # edit the blocks
python scripts/search_builder.py --spec search.yaml --prisma-s
```

One concept-block specification renders to PubMed, Scopus, Web of Science, IEEE
Xplore, Cochrane CENTRAL, and Ovid Embase syntax, plus a PRISMA-S reporting
record. Hand-translating a strategy per database is where strategies silently
diverge and become unreproducible.

Two checks worth two minutes each: have a librarian or second reviewer look at
the strategy (PRESS), and confirm the search retrieves the key papers you
already know about. A search that misses a known paper is broken.

`references/search-strategy.md` covers block construction, controlled vocabulary
versus free text, sensitivity against precision, grey literature, citation
chasing, and the justification a language restriction requires.

## Step 4: screen with a log

```bash
python scripts/screening_log.py init --title "..."
python scripts/screening_log.py identified --source PubMed --n 412
python scripts/screening_log.py dedup --removed 291
python scripts/screening_log.py screen --id S001 --decision exclude --reason "..."
python scripts/screening_log.py fulltext --id S002 --decision exclude --reason "..."
python scripts/screening_log.py flow            # reconciliation check
python scripts/screening_log.py exclusions      # PRISMA item 16b table
```

Dual independent screening is the standard; where a second human is unavailable,
say so as a limitation rather than implying it happened. Every full-text
exclusion needs a specific reason. "Did not meet inclusion criteria" is not a
reason, and the script flags exclusions with none recorded.

## Step 5: appraise with the right instrument

Applying one generic checklist to every design is a methodological failure, not
a simplification. Match the tool to the design:

| Included study design | Tool |
|---|---|
| Randomized trial | RoB 2 |
| Non-randomized intervention study | ROBINS-I |
| Diagnostic accuracy study | QUADAS-2 (QUADAS-C for comparative) |
| Prediction model development or validation, including ML | PROBAST+AI |
| Existing systematic review (umbrella review) | AMSTAR 2, or ROBIS for review-process bias |
| Observational cohort or case-control | ROBINS-E, or JBI / Newcastle-Ottawa with stated limits |
| Qualitative study | CASP or JBI qualitative checklist |

`references/appraisal-tools.md` gives the domains, the common misapplications,
and why PROBAST+AI (Moons et al., BMJ 2025;388:e082505) matters for any review
that includes machine-learning prediction models: it separates model development
from model evaluation and adds explicit fairness and real-world-performance
considerations that PROBAST 2019 did not cover.

## Step 6: synthesize, and do not pool by reflex

Meta-analysis is one option among several and is often the wrong one.
Clinically or methodologically diverse studies pooled into a single number
produce a precise answer to no question. When pooling is inappropriate, use a
structured narrative synthesis and report it against SWiM rather than writing an
unstructured discussion.

`references/certainty-and-synthesis.md` covers the decision to pool, fixed
versus random effects, heterogeneity interpretation (including why I-squared is
not a measure of how much heterogeneity there is), prediction intervals, small
study effects, and the SWiM elements.

## Step 7: rate certainty with GRADE, not with a pyramid

The evidence pyramid is a teaching aid for where to start looking. It is not a
verdict. A randomized trial with serious risk of bias, imprecision, and
indirectness supports a weaker conclusion than a well-conducted observational
study with a large consistent effect. GRADE encodes this: start from the design,
then rate down for risk of bias, inconsistency, indirectness, imprecision and
publication bias, and rate up for large effect, dose-response, or when plausible
confounding would reduce the observed effect.

Report certainty per outcome, not for the review as a whole.

## Step 8: verify, then report

```bash
python scripts/verify_citations.py --refs references.md --mailto you@uni.edu
python scripts/verify_citations.py --self-test    # checks the verifier's logic
```

The script queries Crossref (which has ingested the Retraction Watch database
and exposes retractions through `updated-by`) and corroborates against
OpenAlex's `is_retracted`. It reports disagreement between the two rather than
resolving it silently. A reference that could not be checked because the service
was unreachable is marked UNCHECKED, never FAIL: a firewall is not evidence of
fabrication.

Then report against the guideline for the review type, using
`templates/evidence-table.md` for the study characteristics table and
`templates/ai-disclosure.md` for the AI-use statement.

## Anti-patterns

| Anti-pattern | Why it fails | Instead |
|---|---|---|
| Searching until the answer appears | the search becomes the conclusion's evidence | fix eligibility in the protocol, then search once and report everything found |
| Citing a review's conclusion without appraising the review | reviews vary from high to critically low quality | AMSTAR 2 the review before relying on it |
| One checklist for every design | measures the wrong domains | select per design (Step 5) |
| Pooling because the data are pooled-shaped | precision without meaning | justify pooling, or use SWiM |
| A single I-squared threshold as a pooling decision rule | I-squared describes proportion, not magnitude, and depends on precision | inspect tau-squared, prediction intervals, and clinical diversity |
| Reporting review-level certainty | GRADE is per outcome | rate each outcome separately |
| "Difficult to verify" as a citation status | unverifiable and fabricated look identical in a reference list | remove it |
| Silent AI assistance in screening or extraction | breaches the 2025 joint position statement expectations | disclose per `templates/ai-disclosure.md` |
| Declaring "no studies found" as a null result | usually a search failure, not an evidence gap | test the search against known papers first |

## What this skill will not do

It will not invent a citation to fill a gap, produce a systematic review from a
single conversation without the user doing the screening, claim dual independent
screening that did not happen, or assert an effect size it did not compute from
reported data. Where a step needs a human or a second reviewer, it says so and
the limitation goes in the report.

## Files

| File | Purpose |
|---|---|
| `references/review-types.md` | choosing the review type, effort, claims each supports |
| `references/search-strategy.md` | block construction, vocabulary, grey literature, PRISMA-S |
| `references/appraisal-tools.md` | tool per design, domains, misapplications |
| `references/certainty-and-synthesis.md` | pooling decisions, heterogeneity, SWiM, GRADE |
| `references/verification-protocol.md` | fabrication and retraction checking, what the script does and does not prove |
| `references/ai-use-reporting.md` | RAISE, the 2025 joint position statement, disclosure content |
| `templates/protocol.md` | protocol and registration template |
| `templates/evidence-table.md` | study characteristics and results extraction table |
| `templates/ai-disclosure.md` | AI-use statement for methods sections |
| `scripts/verify_citations.py` | existence, metadata match, retraction status |
| `scripts/search_builder.py` | one spec, six database syntaxes, PRISMA-S record |
| `scripts/screening_log.py` | append-only decisions, reconciling PRISMA flow |

## Key sources

Page et al. (2021), PRISMA 2020, BMJ 372:n71. Tricco et al. (2018), PRISMA-ScR,
Ann Intern Med 169:467-473. Rethlefsen et al. (2021), PRISMA-S. Collins et al.
(2024), TRIPOD+AI, BMJ 385:q902. Moons et al. (2025), PROBAST+AI, BMJ
388:e082505. Thomas et al. (2025), RAISE recommendations, and the joint
Cochrane/Campbell/JBI/CEE position statement on AI use in evidence synthesis
(2025). Verify current versions before citing: reporting guidelines are revised,
and a partial update of PRISMA 2020 covering AI tool use was in development as
of mid-2026.
