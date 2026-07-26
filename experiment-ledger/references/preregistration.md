# Declaring comparisons before running them

This is a lightweight internal preregistration. It is not submitted anywhere and
takes about five minutes. Its purpose is to make the difference between
confirmatory and exploratory results visible to you, months later, when you are
writing the paper and no longer remember which was which.

## The declaration file

`comparisons/<name>.yaml`:

```yaml
name: prompt_ablation
declared_utc: 2026-07-25T13:40:00Z
declared_at_commit: 9f2a1c4

question: >
  Does structured output prompting improve patch-level classification over the
  base instruction prompt for MedGemma-27B-IT on colorectal H&E?

arms:
  - id: base
    role: reference          # exactly one reference arm
    description: minimal instruction prompt, free-text label
  - id: cot
    role: treatment
  - id: fewshot
    role: treatment
  - id: structured
    role: treatment

primary_metric: balanced_accuracy
primary_unit: patient          # the unit of analysis, not the unit of prediction
secondary_metrics: [macro_f1, ece, coverage_at_risk_0.05]

hypothesis: >
  structured raises balanced accuracy over base by more than 2 points

analysis_plan: >
  Paired bootstrap over patients, 10000 resamples, percentile CI, alpha 0.05.
  Holm correction across the three treatment arms. Noise floor established by
  rerunning the base arm once with an unchanged config.

stopping_rule: >
  All four arms run to completion over the full held-out split. No interim
  inspection of the primary metric before all arms complete.

decided_in_advance:
  - the reference arm is base, chosen because it is the minimal prompt, not
    because of its performance
  - patient-level aggregation, chosen because patches within a slide are not
    independent
```

## Why the reference arm needs justification in writing

The comparison baseline is where post hoc selection enters most easily, because
several defensible choices usually exist. Writing the justification before
seeing results forces the choice to rest on a principle (the minimal prompt, the
published method, the standard-of-care model) rather than on the outcome.

Warning signs that a reference arm was chosen after the fact:

- The baseline differs between two comparisons in the same paper without a
  stated reason.
- The baseline is the weakest of several available conditions.
- The baseline uses different preprocessing, a different split, or a different
  model revision from the treatment arms.
- The paper's own text struggles to say why that arm is the natural reference.

The last one is diagnostic. If the justification is hard to write, the choice is
probably outcome-driven.

## Unit of analysis

Declare it explicitly, because it determines the statistics and it is a common
source of inflated significance. For patch-level histopathology:

- Predictions are made per patch.
- Patches within a slide are highly correlated.
- Slides within a patient are correlated.
- Therefore the unit of analysis is the patient (or slide, if one slide per
  patient), and resampling must be at that level.

Treating 400k patches as 400k independent observations produces confidence
intervals several times too narrow. This survives internal review easily and is
caught by external reviewers at clinical venues often.

## When the pre-declared comparison fails

This is the situation the declaration exists for. Options, in order of
preference:

1. **Report it.** A pre-declared comparison that did not show the expected effect
   is a result. It is publishable, especially with a mechanism explanation.
2. **Report it and add exploratory analysis.** Clearly labeled: "the
   pre-declared comparison did not reach significance; the following
   exploratory analysis suggests X and requires confirmation on held-out data."
3. **Re-declare and re-run on fresh data.** Legitimate if genuinely fresh data
   exists. Note the previous declaration in the new one.

What not to do: quietly change the reference arm, change the primary metric to
one that reached significance, change the aggregation unit, or add arms until
one works. Each of these turns a null result into a false positive and none of
them is visible in the finished paper.

## Exploratory findings are fine

Most interesting findings are exploratory. Temperature scaling saturating,
a resolution effect that runs opposite to expectation, two related models
diverging in routing behavior: these are discoveries, not confirmations, and
the honest framing is stronger than a fake confirmation.

Structure them as: observation, candidate mechanism, the specific test that would
confirm it, and whether that test was run. A discussion section that names the
confirmatory test it did not run reads as competent. One that implies a
confirmation it did not perform is the thing reviewers are looking for.

## Oracle and upper-bound arms

An arm that uses information unavailable at deployment (best-prompt-per-item,
ground-truth-conditioned routing) is an upper bound, not a method. Declare it as
`role: oracle`. It belongs in the table as a ceiling, labeled, and never in the
abstract's headline number. The useful quantity is the gap between the deployable
method and the oracle, which measures how much headroom the selection mechanism
leaves on the table.

## Amending a declaration

Amendments are allowed and should be appended, not edited in place:

```yaml
amendments:
  - date: 2026-08-02
    at_commit: c71b0aa
    change: added arm `structured_v2` after a tokenization bug was found in `structured`
    reason: the original arm's outputs were truncated for 3 percent of items
    affects_primary: true
    rerun_required: [structured, base]
```

The append-only history is what distinguishes a correction from a rewrite. Keep
the file in version control so the timestamps are independently checkable.
