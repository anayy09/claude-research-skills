# Reporting templates

Sentence-level patterns for the methods, results, tables, and figures. Adapt the
wording; keep the content, since each element exists to close a specific
reviewer objection.

---

## Methods: statistical analysis paragraph

> Model performance was evaluated on a held-out set of {N_items} patches from
> {N_groups} patients, with no patient contributing to more than one split.
> Because patches from the same patient are not independent, all confidence
> intervals and hypothesis tests use a cluster bootstrap resampling patients with
> replacement ({B} resamples, percentile intervals, alpha = {alpha}). Paired
> comparisons between models reuse the same resampled patients for both models,
> and we report the interval on the paired difference rather than on each model
> separately. The primary comparison, its reference arm, and the primary metric
> were fixed before the runs were executed; comparisons introduced afterward are
> labeled exploratory. {If applicable:} Because inference used continuous
> batching, results are not bitwise reproducible; run-to-run variation on an
> unchanged configuration was {X} points on the primary metric, which we report
> alongside all reported differences.

Every clause is load-bearing. The patient-level clause pre-empts the independence
objection, the paired clause pre-empts the overlapping-intervals objection, the
pre-specification clause pre-empts the post-hoc-baseline objection, and the
noise-floor clause pre-empts the strongest objection specific to LLM evaluation.

---

## Results: a single model

> {Model} achieved a balanced accuracy of {0.812} (95% CI {0.784} to {0.839};
> cluster bootstrap over {60} patients).

Not: "achieved 81.2% accuracy", with no interval, no unit, no resampling scheme.

---

## Results: a comparison

> {Treatment} improved balanced accuracy over {reference} by {1.9} points
> ({0.019}; 95% CI {0.007} to {0.031}; paired cluster bootstrap, p = {0.002}).
> The improvement exceeded the run-to-run variation of {0.004} points measured on
> an unchanged configuration.

Lead with the difference and its interval. The two individual values belong in
the table, not in the sentence making the claim.

---

## Results: a null or inconclusive comparison

> The pre-specified comparison did not detect a difference between {A} and {B}
> (difference {0.003}; 95% CI {-0.011} to {0.017}). The interval excludes
> differences larger than about {1.7} points in either direction, so a
> clinically meaningful advantage for either method is unlikely at this sample
> size, though the study is not powered to establish equivalence at a
> pre-specified margin.

Say what was ruled out. An interval reported without that reading gives the
reader nothing to do with it.

---

## Results: calibration

> Before calibration, {model} was overconfident (ECE {0.084}, 15 equal-mass bins;
> Brier {0.134}). Temperature scaling fit on a held-out calibration split of
> {N} cases (T = {1.62}) reduced ECE to {0.029} with no change to AUROC, as
> expected for a monotone transformation. Further reduction was not achieved:
> ECE was flat within {0.003} for T between {1.4} and {1.9}, and the residual
> reliability gap was region-dependent rather than a constant offset, indicating
> that the remaining miscalibration is not correctable by a single global scale
> parameter.

---

## Results: triage or selective prediction

> At an error rate of at most {5}% on retained cases, the system handled {38.4}%
> of the workload (95% CI {25.7} to {56.3}; threshold {0.87} selected on the
> validation split). AURC was {0.078} against an optimal-ranking AURC of
> {0.019}, giving an excess of {0.059}, which indicates that the confidence
> ranking captures a substantial but incomplete share of the achievable
> separation between correct and incorrect cases.

---

## Table footnote

> Values are point estimates with 95% percentile confidence intervals from a
> cluster bootstrap over {N} patients ({B} resamples). Bold indicates the best
> value per column. Differences and their intervals are computed paired, reusing
> the same resampled patients for all methods; marginal intervals in this table
> should not be compared to each other directly. The {oracle} row uses
> information unavailable at inference time and is an upper bound, not a method.

The last two sentences prevent the two most common misreadings of a results
table, including by co-authors.

---

## Figure caption: reliability diagram

> Reliability diagram for {model} on the held-out set, using {15} equal-mass
> bins. Points show observed accuracy against mean predicted probability;
> vertical bars are 95% cluster bootstrap intervals; the histogram gives the
> fraction of cases per bin. The diagonal is perfect calibration.

---

## Figure caption: risk-coverage curve

> Risk-coverage curve on the held-out set. Coverage is the fraction of cases
> handled without deferral, at descending confidence; risk is the error rate
> among retained cases. The shaded band is a 95% cluster bootstrap interval over
> {N} patients. The dashed line marks the operating point selected on the
> validation split ({5}% risk, {38}% coverage).

---

## Sentences to avoid

| Avoid | Why | Instead |
|---|---|---|
| "significantly better" with no interval | significance without magnitude is uninformative | give the difference and its interval |
| "the intervals do not overlap, so the difference is significant" | wrong test, and the pairing is discarded | give the paired difference interval |
| "12,000 samples" for 12,000 patches from 60 patients | implies independence that does not hold | "12,000 patches from 60 patients" |
| "state of the art" | ages badly, invites a comparison the paper may not support | name the comparison and the venue conditions |
| "the model demonstrates strong performance" | asserts a conclusion in place of a number | state the number |
| "calibration was improved" | improved by which measure, at which binning | give the measure, the binning, and the interval |
| "our method achieves 94% accuracy" for an oracle arm | presents an upper bound as a result | label the row as an upper bound wherever it appears |
