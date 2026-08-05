# Path to publication

How a direction becomes a submission. Everything here is built before the next
experiment runs, because the cheapest time to discover that the planned evidence
does not support the claim is before the compute is spent.

Contents:

- [1. Gap ledger](#1-gap-ledger)
- [2. Design the headline table first](#2-design-the-headline-table-first)
- [3. Minimum evidence set by contribution type](#3-minimum-evidence-set-by-contribution-type)
- [4. Kill experiment and decision gates](#4-kill-experiment-and-decision-gates)
- [5. Reviewer objection preemption](#5-reviewer-objection-preemption)
- [6. Threats to validity](#6-threats-to-validity)
- [7. Sequencing and handoffs](#7-sequencing-and-handoffs)

---

## 1. Gap ledger

One table per direction. This is the whole transition from project to paper made
explicit, and it is what makes an estimate defensible.

| Requirement | Exists | Missing | Effort | Blocking |
|---|---|---|---|---|
| e.g. patient-level split | partial: patch splits only | regrouping and re-run | 2 days | yes |

Rules that keep the ledger honest:

- List requirements from the minimum evidence set in section 3, not from what
  was going to be done anyway.
- "Exists" means it exists under conditions the paper can report. A run with an
  unrecorded config does not exist for this purpose.
- Blocking means the claim cannot be made without it. Non-blocking items are
  strengtheners and go in a separate group, because the difference determines
  what gets cut when the schedule slips.

Sum the blocking effort. That number, not the optimistic one, drives
`effort_months` in the scoring.

## 2. Design the headline table first

Every paper is carried by one table or one figure. Draw it before running
anything: rows, columns, which cell the claim lives in, and what number would
have to appear there for the claim to hold.

This forces three useful realizations early:

- **The missing column.** Usually a baseline nobody planned to run.
- **The missing row.** Usually the ablation that isolates the contribution.
- **The unfalsifiable cell.** If no value in the target cell would make the
  claim false, the claim needs restating.

Write the caption too, in one sentence, stating what the reader should conclude.
If the caption needs three sentences, the table is doing two jobs.

Then state the target value as a target. It is not a result until it is
measured, and it never appears in the report as one.

## 3. Minimum evidence set by contribution type

The floor for a reputable venue. Below this, a reviewer has a reason to reject
that is independent of how good the idea is.

**Empirical or phenomenon paper**

- The effect measured across seeds, with intervals, at the decision unit.
- Controls ruling out preprocessing, metric, and label-noise artifacts.
- At least one alternative explanation tested and excluded.
- Generalization past the setting where it was noticed: second dataset, second
  model family, or second site.

**Method paper**

- Baselines tuned with a budget comparable to the proposed method, stated.
- Ablation isolating each claimed component.
- Cost accounting: parameters, compute, latency, or annotation, whichever the
  contribution trades against.
- Variance over seeds, and a paired test rather than a comparison of means.
- Negative controls where the method should not help.

**Systems paper**

- A workload or deployment description grounded in something real.
- Measurements under contention, not only in isolation.
- Comparison to the obvious simpler architecture, which reviewers will name.
- Failure and recovery behavior.
- Artifact available, or a stated reason why not.

**Theory paper**

- Assumptions stated where a practitioner can check them.
- Proof, with the non-obvious step highlighted rather than buried.
- At least one empirical confirmation of a prediction the theory makes and the
  alternative does not.
- Explicit statement of what the result does not cover.

**Dataset or benchmark paper**

- Provenance, licensing, and consent basis.
- Inter-annotator agreement, and the protocol that produced it.
- A split protocol resistant to the leakage mode specific to the domain.
- Baselines including a trivial one and a strong one.
- Datasheet, and a stated bias and limitations section.

**Negative result paper**

- Faithful implementation, ideally reproducing the original claim first.
- A search wide enough that the null is not a tuning artifact, with the space
  stated.
- An equivalence or non-inferiority analysis, not a non-significant p-value.
- A mechanism for why the expected effect does not appear.

**Survey plus extension**

- Reproducible search with the strategy reported.
- Appraisal of included study quality.
- The original element: a common-protocol comparison, a meta-analysis, or a
  taxonomy that makes a testable prediction.
- Coordinate with `evidence-synthesis`, which carries the reporting standards.

## 4. Kill experiment and decision gates

Every direction gets one experiment, runnable early and cheaply, whose outcome
determines whether to continue. Specify it with a decision rule written before
it runs.

Format:

```
Kill experiment: <the smallest run that could show the effect is not there>
Cost: <hours or days>
Decision rule: continue if <specific, measurable condition>; otherwise <the
                specific alternative direction, or stop>
```

The rule has to be falsifiable at the stated cost. "Continue if results are
promising" is not a rule. "Continue if the deferral policy beats the
temperature-scaled baseline on the pilot split by more than the seed spread" is.

Then set gates for the rest of the schedule. Two are usually enough:

- **After the main experiments.** Does the headline cell hold, at the size the
  claim needs, with intervals that exclude the null.
- **Before writing.** Is the minimum evidence set complete. Writing before this
  gate wastes the writing when a missing baseline changes the story.

A direction without a kill criterion absorbs months and never fails clearly
enough to stop. This is the most common way a promising project fails to become
a paper.

## 5. Reviewer objection preemption

For each direction, write the three objections a competent reviewer raises
first, with the answer and where it lives in the paper. Objections that have no
answer yet are experiments, and they belong in the gap ledger.

Predictable objections by contribution type:

| Type | The three that always come |
|---|---|
| Empirical | Is it an artifact; does it generalize; is the unit of analysis right |
| Method | Was the baseline tuned; is the gain within seed variance; what does it cost |
| Systems | Why not the simpler design; does it hold under load; can we run it |
| Theory | Do the assumptions hold in practice; is the result vacuous; what is new versus known |
| Dataset | Does an existing resource cover this; how good are the labels; can it leak |
| Negative | Did you implement it correctly; did you search widely enough; is it underpowered |
| Survey | What is original here; is the search reproducible; is the taxonomy predictive |

The strongest objection goes in the paper, answered, rather than being left for
a reviewer to find. A limitations section that names the real weakness is read
as confidence. One that lists generic limitations is read as evasion.

## 6. Threats to validity

Walk these for every direction and record the ones that apply, with the
mitigation:

- **Leakage** at the relevant unit: patient, subject, site, session, time. The
  unit is domain-specific and getting it wrong invalidates everything downstream.
- **Selection** in how the evaluation cases were assembled.
- **Confounding** by site, scanner, cohort, or time period.
- **Multiplicity** across ablation arms, metrics, and operating points. Decide
  the correction before running the arms, and hand it to `ml-eval-statistics`.
- **Optimization asymmetry**: the proposed method tuned more than the baseline.
- **Temporal validity**: training and evaluation periods that could not exist in
  deployment order.
- **Construct validity**: the metric not measuring the thing the claim is about.
- **Annotation quality** setting a ceiling that the results are approaching.

## 7. Sequencing and handoffs

Order the work so that the thing most likely to kill the direction happens
first, and the thing that takes longest in wall-clock time starts earliest. Data
access requests, IRB amendments, and annotation rounds are almost always the
long poles, and they are cheap to start.

Handoffs once the direction is chosen:

- `experiment-ledger` to set up config-as-file, run manifests, and the declared
  comparison arms before the first run. Comparison arms declared after the runs
  exist are the standard route to an irreproducible results table.
- `ml-eval-statistics` for the intervals, paired tests, clustered resampling,
  calibration, and multiplicity control specified in the evidence set.
- `hpc-cluster` for job scripts and allocation planning.
- `evidence-synthesis` or `investigating-sources` when the direction needs a
  full literature base rather than the targeted prior-art check.
- `journal-advisor` once the claim and evidence set are fixed, for venue choice.
- `research-paper-writing` for drafting, then `submission-reviewer` before
  submission, then `submission-formatter` for the venue's template.

Use `scripts/plan_timeline.py` to lay the phases against the deadline and see
the slack. If slack is negative, cut a non-blocking requirement from the gap
ledger rather than compressing every phase, and say which one was cut.
