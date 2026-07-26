# Desk-reject risk rubric

A desk reject is an editor's decision before peer review, usually made in
minutes. It is driven by a small number of checkable properties, most of which
the author can fix. Assess each finalist as low, medium, or high and name the one
or two factors driving the rating. A rating without reasons is not usable advice.

## The factors, roughly in order of how often they decide the outcome

**1. Scope fit.** The most common cause by a wide margin. The test is not whether
the topic is adjacent but whether the journal's stated aims name this kind of
contribution. A clinical journal publishing applied AI evaluations is a different
proposition from a methods journal publishing new architectures, even when both
say "machine learning in medicine".

**2. Article type mismatch.** The manuscript's form must be a type the journal
accepts and must meet that type's expectations. A 12-page methods paper submitted
where only short communications are accepted is rejected on arrival. A benchmark
or dataset paper submitted to a journal with no such category is too.

**3. Novelty expectation.** Journals differ in what they require:
   - *Soundness-based*: technically correct and adequately reported is enough.
   - *Incremental-tolerant*: a solid advance over prior work.
   - *Significance-gated*: requires a substantial or broadly interesting advance.
   A new application of an existing method sent to a significance-gated venue is
   a high-risk submission regardless of execution quality.

**4. Empirical standard.** Clinical and health-informatics venues frequently
require external validation, a defined patient cohort, or a reporting-guideline
checklist. A single-dataset internal-validation study sent to a venue expecting
external validation is often desk rejected with a one-line note.

**5. Reporting and compliance.** Missing ethics approval statement, absent data
availability statement, no conflict-of-interest declaration, missing consent
language for human data, or no reporting checklist where the journal mandates
one. Cheap to fix, and each is individually sufficient for a desk reject.

**6. Format and length.** Over the word or page limit, wrong template, figures
below the stated resolution, references in the wrong style, an abstract exceeding
the word cap, or a structured-abstract requirement ignored.

**7. Presentation quality.** Editors read the abstract and the introduction. If
the contribution is not stated clearly in the first page, or the English needs
substantial editing, some journals reject on that alone.

**8. Prior publication and overlap.** Substantial overlap with a prior conference
paper without a declared extension, a preprint where the journal disallows them,
or salami slicing across related submissions.

**9. Submission gates.** Special-issue-only journals, presubmission enquiry
requirements, member sponsorship. Missing a gate produces an immediate return.

## Rating scale

**Low.** Scope is squarely inside the journal's stated aims, the article type is
accepted and appropriately sized, novelty class matches the journal's stated
expectation, and all compliance elements are present or trivially addable. The
manuscript would go to review absent bad luck.

**Medium.** One material gap. Typically: scope is adjacent rather than central,
or the novelty class sits at the boundary of what the journal expects, or the
empirical standard is one element short (single-site validation at a venue that
prefers multi-site but does not require it), or the format needs real work. The
submission is defensible; the cover letter has to do some work.

**High.** Two or more material gaps, or one disqualifying gap: article type not
accepted, novelty class clearly below the stated bar, missing an empirical
requirement the journal states as mandatory, or an unmet submission gate. Advise
against submitting as-is and say what would have to change.

Do not use "medium" as a default for uncertainty. If the evidence is thin,
assess from what is known and say which fact would change the rating.

## Common patterns by manuscript type

**Applied AI on clinical data.** Highest-frequency causes: no external
validation; patient-level leakage not addressed; metrics reported without
intervals; no reporting-guideline checklist where required; framed as a methods
contribution at a clinical venue, or as a clinical contribution at a methods
venue. The first and last are the ones that decide it.

**New method, standard benchmarks.** Causes: insufficient delta over strong
baselines; missing comparison to the obvious recent competitor; evaluation on a
single dataset; venue expects theory and the paper is empirical.

**Benchmark, dataset, or resource papers.** Causes: no matching article type at
the venue; data not actually released or release blocked by terms; no license
stated; no baseline results included.

**Negative or replication results.** Causes: most venues have no category for
them. Check explicitly whether the journal states that it publishes them; several
do, and it is stated when true.

**Review or survey.** Causes: unsolicited surveys are disallowed at some venues;
no systematic methodology where the journal expects PRISMA; overlap with a recent
survey in the same venue.

## Reducing risk before submission

Ranked by effect per unit of effort:

1. Reframe the abstract and introduction to speak the journal's language, naming
   the contribution in the terms the journal's scope uses.
2. Add the compliance elements: ethics statement, data availability, conflicts,
   reporting checklist, author contributions.
3. Match the template and the length limit exactly before submitting, not after
   a return.
4. Write a cover letter that names the fit explicitly and preempts the one
   obvious objection.
5. Where the gap is empirical (external validation, a missing baseline), decide
   whether to add it or to move to a venue whose stated bar the work already
   meets. Moving is often the better use of a month.

## What to write in the report

One sentence with the rating and the drivers:

> Desk-reject risk: **medium**. Scope fit is strong, but the journal's author
> guidelines state a preference for externally validated clinical studies and
> this work reports single-cohort internal validation. Adding an external test
> set or reframing as a methods contribution would move this to low.

That form gives the rating, the reason, and the remedy in three clauses.
