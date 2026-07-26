# Choosing the review type

The type is a commitment about what the review can claim. Pick it from the
question, not from the time available, and if the time available does not
support the type the question needs, change the question or state the shortcuts
taken.

## Decision path

1. **Is there an existing systematic review that answers this?** Search for one
   first. If a good one exists and is current, the useful contributions are an
   update, an umbrella review, or a different question. Appraise it with AMSTAR 2
   before concluding it is good.
2. **Is the question about effect, or about extent?** Effect questions ("does it
   work", "how accurate is it") take a systematic review. Extent questions
   ("what has been studied", "what definitions are in use", "where are the gaps")
   take a scoping review.
3. **Does the evidence change faster than a review cycle?** Then a living review,
   or accept that the review is a snapshot and date it prominently.
4. **What designs will be included?** This determines the appraisal tool and
   often the feasibility. A question that admits trials, cohorts, and modelling
   studies needs three tools and a synthesis that can hold them together.

## Types

### Systematic review
Answers a focused effect question with a preregistered protocol, an exhaustive
search, dual screening, formal appraisal, and a synthesis that may or may not be
a meta-analysis. Report against PRISMA 2020.

Realistic effort: 6 to 18 months with a team. Claims it supports: what the
current body of evidence shows about the specified outcomes, with stated
certainty.

### Meta-analysis
Not a separate review type but an analysis method used inside one. A
meta-analysis without a systematic review behind it is a pooled convenience
sample. See `certainty-and-synthesis.md` for when pooling is appropriate.

### Scoping review
Maps the literature: what exists, what designs, what definitions, where the
gaps are. Does not appraise quality by default and does not answer effect
questions. Report against PRISMA-ScR (Tricco et al., 2018). The most common
error is a scoping review that draws effectiveness conclusions it has no basis
for; the second most common is calling a scoping review "systematic" in the
abstract.

### Rapid review
A systematic review with declared shortcuts to meet a decision deadline: fewer
databases, single-reviewer screening with verification, restricted date range,
no grey literature. Legitimate when the shortcuts are stated and their likely
effect discussed. Illegitimate when it is presented as a full systematic review.

State each shortcut explicitly: "single reviewer screened titles with a 20
percent independent check", not "screening was performed".

### Umbrella review / overview of reviews
Synthesizes existing systematic reviews. Appraise the included reviews with
AMSTAR 2 (methodological quality) or ROBIS (risk of bias in the review process).
Watch for primary study overlap: the same trials appearing in several included
reviews inflate apparent evidence, and a citation matrix quantifying overlap is
expected.

### Living systematic review
A review kept current through ongoing surveillance and scheduled updates. Report
against PRISMA-LSR (BMJ 2024, doi:10.1136/bmj-2024-079183), which adds reporting
of the living status, search frequency, and update triggers. Requires a
maintenance commitment: a living review that stops being updated but retains the
label is worse than a dated snapshot, because readers assume currency.

### Diagnostic test accuracy review
Sensitivity and specificity are correlated and threshold-dependent, so the
synthesis needs bivariate or HSROC models rather than separate pooling of each.
Report against PRISMA-DTA and appraise with QUADAS-2, or QUADAS-C when comparing
tests.

### Prediction model review
Reviews of models that estimate risk for individuals. Use CHARMS to structure
extraction, PROBAST+AI to appraise, and expect TRIPOD+AI as the reporting
standard the included studies should have met. These reviews almost always find
the same things, and finding them is still worth reporting: predominance of
development over external validation, discrimination reported without
calibration, and small effective sample sizes relative to the number of
candidate predictors.

Do not pool C-statistics across models developed on different populations with
different predictor sets without an explicit argument for why that quantity
means anything.

### Qualitative evidence synthesis
Thematic synthesis, meta-ethnography, framework synthesis. Report against ENTREQ
(a PRISMA extension for QES was in development as of mid-2026). Appraise with
CASP or the JBI qualitative checklist, and use GRADE-CERQual rather than GRADE
for confidence in findings.

### Mixed methods review
Combines quantitative and qualitative evidence, usually in a segregated design
(synthesize separately, then integrate) or a convergent one. Name the
integration approach; "we combined the findings" is not a method.

## What to write in the abstract

Name the type in the first sentence and use the term accurately. A reader who
sees "systematic review" expects a protocol, an exhaustive search, dual
screening, and formal appraisal. If any of those are absent, the accurate label
is a scoping review, a rapid review, or a narrative review, and using the
accurate label costs nothing while using the wrong one is a reviewer's first
objection.

## Effort reality check

| Type | Typical effort with a small team |
|---|---|
| Narrative or background review | days to weeks |
| Rapid review | 4 to 12 weeks |
| Scoping review | 3 to 9 months |
| Systematic review with meta-analysis | 6 to 18 months |
| Umbrella review | 4 to 10 months |
| Living review | initial review plus ongoing commitment |

If the available time is a fraction of this, the honest move is to narrow the
question until the type fits the time, not to keep the question and quietly drop
the method.
