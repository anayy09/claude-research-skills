---
name: ml-eval-statistics
description: >-
  Choose and compute the right statistics for evaluating and comparing your own
  models: paired significance tests, clustered and patient-level bootstrap
  confidence intervals, calibration (ECE, reliability, temperature scaling),
  selective prediction and triage metrics (risk-coverage, AURC, coverage at
  fixed risk), and multiplicity control across ablation arms. Use whenever the
  user asks whether a difference is significant, which metric to report, how to
  compute a confidence interval, whether two models differ, how to show
  calibration, how to evaluate a triage or deferral system, or how to handle
  patches, slides, or repeated measures from the same patient. Also use when
  reviewing a results table, when a reviewer has raised a statistics objection,
  and whenever an accuracy number is about to be reported without an interval.
  Distinct from meta-analysis of published literature: this is for statistics on
  experiments the user ran.
summary: "The right statistics for model evaluation: significance, CIs, calibration, selective prediction."
version: "1.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-07-25"
---

# ML Evaluation Statistics

Two failures account for most statistics objections in applied ML papers:
treating correlated observations as independent, and comparing two models by
checking whether their separate confidence intervals overlap. Both inflate
apparent significance, both are easy to fix, and both are visible to any
reviewer who looks.

## Step 1: fix the unit of analysis before computing anything

Ask what would have to be independently resampled to get a new, exchangeable
dataset. That is the unit. It is almost never the prediction.

For histopathology: predictions are per patch, patches are correlated within a
slide, slides are correlated within a patient. The unit is the patient. For ICU
waveforms: windows within a stay are correlated; the unit is the stay or the
patient. For any repeated-measures design: the unit is the subject.

Consequences of getting this wrong: with 400,000 patches from 86 patients,
treating patches as independent understates the standard error by roughly the
square root of the design effect, commonly a factor of five or more. Every
interval is then too narrow and every p-value too small. Nothing else in the
analysis can compensate.

Practical rule: the resampling unit and the grouping variable in the split must
be the same variable. If the split is patient-level (as it must be to avoid
leakage), the bootstrap is patient-level too.

## Step 2: pick the test that matches the claim

| Claim | Method | Note |
|---|---|---|
| Model A beats model B, same test set | paired bootstrap over groups, or McNemar for accuracy | never compare separate CIs |
| A beats B on AUROC, independent items | DeLong | anticonservative under clustering; use clustered bootstrap instead |
| A beats B on AUROC, clustered items | paired clustered bootstrap | the default for patch or window data |
| A beats B on a rate (accuracy, sensitivity) | McNemar (exact when discordant pairs are few) | uses only the discordant pairs, which is the point |
| Interval for a single model's metric | clustered percentile bootstrap | report the interval, not the standard deviation |
| Several treatment arms vs one reference | paired bootstrap per arm + Holm correction | declare the family before looking |
| Is the model calibrated | ECE with both equal-width and equal-mass bins, plus a reliability diagram | ECE alone is bin-dependent and easy to game |
| Does deferral help | risk-coverage curve, AURC, coverage at a fixed risk | accuracy at 100 percent coverage says nothing about triage |

The unifying reason to prefer paired methods: the two models saw the same items,
so item difficulty is a shared nuisance. Pairing removes it. Comparing marginal
intervals throws that away and can fail to detect a real and consistent
difference, or manufacture one.

## Step 3: compute it

```bash
# Paired comparison of two models, resampled at the patient level
python scripts/eval_stats.py compare --csv preds.csv \
  --label y_true --a p_base --b p_structured --group patient_id \
  --metric balanced_accuracy --n-boot 10000

# Interval for one model
python scripts/eval_stats.py ci --csv preds.csv --label y_true --pred p_base \
  --group patient_id --metric auroc

# Calibration, both binning schemes
python scripts/eval_stats.py calibration --csv preds.csv --label y_true \
  --prob p_base --bins 15

# Triage behavior
python scripts/eval_stats.py selective --csv preds.csv --label y_true \
  --pred p_base --confidence conf --group patient_id --target-risk 0.05

# Multiplicity across ablation arms
python scripts/eval_stats.py holm --p 0.004,0.031,0.048,0.220
```

Every command reports the number of items and the number of groups. If those two
numbers are far apart and the group count is small, the effective sample size is
the group count, and that is what limits every conclusion in the paper.

## Step 4: establish the noise floor before claiming an effect

Rerun one arm with an unchanged configuration and measure the difference. For
LLM inference under continuous batching, GPU nondeterminism, or any stochastic
training, this is not zero. If the between-arm difference is not clearly larger
than the run-to-run difference, the ablation has measured noise.

```bash
python scripts/eval_stats.py compare --csv preds.csv --label y_true \
  --a p_base_run1 --b p_base_run2 --group patient_id --metric balanced_accuracy
```

This costs one extra run and forecloses the strongest available objection to an
LLM evaluation paper. Report it explicitly in the methods.

## Reporting

State, for every headline number: the metric, the point estimate, the interval,
the resampling unit, the number of groups, and the number of resamples. A number
without an interval is not a result, and an interval without a stated unit is
not interpretable.

For a comparison, report the paired difference and its interval, not two
separate intervals. The difference is the quantity the claim is about.

Do not report a p-value without an effect size. A difference of 0.3 points with
p = 0.01 on 100,000 patches from 20 patients is a statement about sample size,
not about clinical value.

`references/reporting-template.md` has sentence-level templates for the methods
and results sections, and the table footnote that specifies the resampling
scheme.

## Common objections and their pre-emptions

- *"Are patches independent?"* No. Say so first, in the methods, and state the
  clustered resampling scheme.
- *"Overlapping confidence intervals but you claim a difference."* Report the
  paired difference interval instead. Overlapping marginal intervals are fully
  compatible with a significant paired difference.
- *"Which comparison was planned?"* Point to the declared comparison. See the
  `experiment-ledger` skill if the project does not have one.
- *"Accuracy on an imbalanced test set."* Report balanced accuracy or per-class
  results alongside, and give the class distribution.
- *"Calibration only at one binning."* Report both equal-width and equal-mass,
  and note that ECE decreases with fewer bins for trivial reasons.
- *"Multiple arms, no correction."* Apply Holm across the declared family and say
  what the family was.

## Reference files

- `references/paired-tests.md` — bootstrap mechanics, McNemar, DeLong and when
  it is inappropriate, permutation alternatives, one-sided versus two-sided.
- `references/clustered-resampling.md` — why clustering matters, design effect,
  cluster bootstrap variants, what to do with few clusters, stratified
  resampling when a class is rare.
- `references/calibration.md` — ECE variants and their failure modes, reliability
  diagrams, temperature scaling and why it saturates, class-wise calibration,
  proper scoring rules.
- `references/selective-prediction.md` — triage and deferral metrics,
  risk-coverage curves, AURC, choosing an operating point, decision curve
  analysis, and the workload framing clinical reviewers expect.
- `references/reporting-template.md` — methods and results sentence templates,
  table footnotes, figure captions.
