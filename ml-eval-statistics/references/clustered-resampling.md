# Clustered resampling

Contents:
1. The problem in one number
2. Choosing the unit
3. The cluster bootstrap
4. Design effect and effective sample size
5. Few clusters
6. Stratification and rare classes
7. Nested clustering
8. Leakage, which is the same problem at training time

---

## 1. The problem in one number

Take 12,000 patches from 60 patients, with patient-level difficulty variation.
Bootstrap AUROC two ways:

- Resampling patches: 95 percent interval [0.868, 0.879], width 0.012.
- Resampling patients: 95 percent interval [0.848, 0.902], width 0.054.

Same point estimate, same data. The patch-level interval is about four and a half
times too narrow. Every p-value computed under the patch-level assumption is
correspondingly too small, and the effect compounds with more patches per
patient: adding patches from the same 60 patients shrinks the wrong interval and
leaves the right one essentially unchanged, which is the correct behavior since
no new independent information arrived.

This is the single highest-yield correction available in a patch-level
evaluation.

---

## 2. Choosing the unit

Ask: what would I have to sample independently to get another dataset from the
same population? That is the unit.

| Data | Unit | Not the unit |
|---|---|---|
| WSI patches | patient (or slide if one per patient) | patch |
| ICU waveform windows | ICU stay, or patient if stays repeat | window |
| Longitudinal EHR visits | patient | visit |
| Multi-site cohort, site effects of interest | site for site-level claims, patient within site otherwise | row |
| One image per subject | subject, which equals the item | — |

When the grouping variable and the split variable differ, the analysis is
already inconsistent. Use the same variable for both.

---

## 3. The cluster bootstrap

Resample whole clusters with replacement, keeping every observation inside a
selected cluster, and let the resampled dataset have a different size than the
original. Do not resample within clusters: the within-cluster structure is what
the procedure is preserving.

Equivalent and faster formulation: draw multinomial counts over the G clusters,
then compute the metric with those counts as weights. For metrics that are
ratios of sums this is a matrix product and costs nothing.

Variants:

- **Percentile interval.** Default. Simple, adequate when the bootstrap
  distribution is roughly symmetric.
- **BCa.** Bias-corrected and accelerated; better coverage for skewed statistics
  such as AUROC near 1 or precision at low prevalence. Worth the extra code when
  the metric is bounded and the estimate is close to the bound.
- **Basic (reverse percentile).** Rarely better in practice here.

Report which variant was used and the number of resamples.

---

## 4. Design effect and effective sample size

A useful summary for the methods section:

    DEFF ≈ 1 + (m - 1) * ICC

where m is the average cluster size and ICC is the intra-cluster correlation of
the outcome. The effective sample size is roughly N / DEFF. With m = 200 and even
a modest ICC of 0.05, DEFF is about 11, so 12,000 patches carry the information
of roughly 1,100 independent observations.

You do not need to estimate the ICC to do the analysis correctly, since the
cluster bootstrap handles it implicitly. It is worth computing once as a sentence
for the paper, because it makes the sample size argument concrete: reviewers
respond much better to "12,000 patches from 60 patients, effective n ≈ 1,100"
than to an unqualified "12,000 samples".

---

## 5. Few clusters

Below roughly 20 clusters the cluster bootstrap becomes unreliable: the
resampling distribution is coarse, and coverage degrades. Options:

- Report the cluster count prominently and treat intervals as indicative.
- Use a t-based interval on cluster-level statistics with G-1 degrees of
  freedom, which is conservative and transparent.
- Use a permutation test if the design allows it, since permutation does not
  need the bootstrap's asymptotics.
- Say plainly that the study is underpowered at the level that matters. A paper
  with 12 patients and 400,000 patches is a 12-patient study, and reviewers at
  clinical venues will read it that way whatever the abstract says.

Do not respond to few clusters by reverting to item-level resampling. That
replaces a wide honest interval with a narrow wrong one.

---

## 6. Stratification and rare classes

With imbalanced classes, plain cluster resampling can produce a resample missing
a rare class entirely, making per-class recall undefined. Handle it by:

- Stratifying the cluster resampling by a cluster-level characteristic (site,
  scanner, class-majority) so each stratum is represented; or
- Discarding resamples where the metric is undefined, and reporting how many
  were discarded. If a large fraction are discarded, the rare class is too small
  for the metric being reported, which is itself the finding.

Never silently impute a value for an undefined per-class metric. Reporting
`nan`-mean without saying so quietly changes the metric's definition.

---

## 7. Nested clustering

Patches within slides within patients. Resample at the outermost level
(patients), carrying all nested data along. Resampling at both levels is
possible but rarely necessary and easy to get wrong; the outermost level
dominates the variance.

If the claim is about slides rather than patients (for example, slide-level
triage performance), aggregate to the slide first, then resample slides, but
still keep slides from one patient together if a patient contributes several.

---

## 8. Leakage is the same problem at training time

The evaluation-side error has a training-side twin: patches from the same slide
appearing in both train and test. This inflates test performance directly and is
not fixable by any statistical treatment afterward.

Checks worth running once and asserting in code:

```python
assert set(train_df.patient_id) & set(test_df.patient_id) == set()
```

Also check the non-obvious channels: augmented copies of the same image, near
duplicate slides scanned twice, tiles overlapping across a split boundary, and
normalization statistics computed over the full dataset before splitting. The
last one is subtle and common: fitting a stain normalizer or a feature scaler on
all data before splitting leaks test information into training.

State the leakage control in the paper explicitly. Its absence is one of the
first things a careful reviewer looks for.
