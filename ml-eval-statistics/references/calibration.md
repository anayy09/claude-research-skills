# Calibration

Contents:
1. What calibration is and is not
2. Proper scoring rules first
3. ECE and its failure modes
4. Reliability diagrams
5. Temperature scaling, and why it saturates
6. Calibration for LLM classifiers
7. Class-wise and conditional calibration
8. Reporting

---

## 1. What calibration is and is not

A model is calibrated if, among cases assigned probability 0.8, about 80 percent
are positive. Calibration is orthogonal to discrimination: a model can be
perfectly calibrated and useless (always predict the base rate), or highly
discriminative and badly calibrated (any uncalibrated deep network).

Both matter for triage, and for different reasons. Discrimination determines
whether the ranking is any good, which is what a coverage threshold depends on.
Calibration determines whether a stated confidence can be handed to a clinician
or used in a downstream decision rule. Report both. Reporting only AUROC and then
using a probability threshold is a gap reviewers notice.

---

## 2. Proper scoring rules first

Brier score and negative log-likelihood are proper scoring rules: they are
minimized by the true probabilities, need no binning, and cannot be improved by
a favorable analysis choice. Report at least one alongside any binned measure.

- **Brier** = mean squared difference between probability and outcome. Bounded,
  interpretable, less sensitive to extreme predictions.
- **NLL** punishes confident mistakes harshly, which is often what you want in a
  clinical setting, but is unbounded and dominated by a few cases.

A useful decomposition: Brier = reliability - resolution + uncertainty. It
separates miscalibration from discriminative power and from the irreducible
difficulty of the base rate.

---

## 3. ECE and its failure modes

Expected Calibration Error bins predictions by confidence and averages the
absolute gap between mean confidence and mean accuracy, weighted by bin count.
It is intuitive, universally reported, and fragile:

- **Bin-count dependence.** ECE generally decreases as bins get wider, because
  averaging within a wide bin cancels opposite-signed errors. A model can look
  better calibrated purely by using fewer bins. Always report the bin count, and
  report ECE across several bin counts if the number is doing real work.
- **Binning scheme dependence.** Equal-width bins are nearly empty in the middle
  when predictions cluster near 0 and 1, which is typical. Equal-mass (quantile)
  bins fix that but change the number. Report both.
- **It is not a proper scoring rule.** A model can reduce ECE while getting worse
  by the measures that matter.
- **It cancels signed errors.** Overconfidence in one region and
  underconfidence in another can partially cancel within a bin.
- **It has no interval by default.** ECE estimated on a finite test set is noisy,
  and small differences in ECE between methods are frequently within noise.
  Bootstrap it at the cluster level like everything else.

None of this means ECE should not be reported. It means it should not be reported
alone, and a small improvement in ECE should not be presented as a finding
without an interval.

---

## 4. Reliability diagrams

Plot mean predicted probability against observed frequency per bin, with the
diagonal as reference. Include:

- Bin counts, as a histogram on a secondary axis or as annotations. A bin holding
  0.3 percent of the data should not draw the eye as much as one holding 40
  percent.
- Confidence intervals per bin (binomial, or clustered bootstrap if items are
  clustered). Without them, a reader cannot tell a real deviation from a small-bin
  artifact.
- Equal-mass binning, so every plotted point rests on a comparable amount of data.

A reliability diagram with unlabeled bin counts is the most common way a
calibration figure misleads, usually unintentionally.

---

## 5. Temperature scaling, and why it saturates

Temperature scaling divides logits by a single scalar T fit on a validation set
by minimizing NLL. It is a single-parameter, monotone transformation, so:

- It cannot change the ranking, therefore cannot change AUROC, AURC, or any
  threshold-free ranking metric. Reporting an AUROC change after temperature
  scaling indicates a bug.
- It can only apply one global correction. If the model is overconfident in one
  region and underconfident in another, no single T fixes both, and the fitted T
  lands at a compromise.

**Saturation.** Beyond a certain point, further scaling stops improving ECE and
the curve of ECE against T flattens near its minimum. Common causes:

1. The residual miscalibration is not a global scale error. The remaining gap is
   region-dependent, and one parameter cannot address it. Diagnose by plotting
   the reliability gap against confidence: a roughly constant offset is
   scale-fixable, an S-shape is not.
2. The residual error is aleatoric. Some of the gap reflects genuine label noise
   or irreducible ambiguity, and no post-hoc transformation removes it.
3. The validation set is too small or unrepresentative. The fitted T is noisy and
   the flat region is partly estimation error.
4. Discretization floor. With coarse probability outputs, ECE cannot fall below
   the resolution of the outputs.

When temperature scaling saturates, the informative report is: the fitted T, the
ECE before and after with intervals, the shape of the residual reliability gap,
and a statement of which of the above explanations the evidence supports. That
turns a negative result into a mechanism claim. Vector or matrix scaling, isotonic
regression, or histogram binning are the natural next steps if the residual is
region-dependent; note that isotonic regression can overfit on small validation
sets and does change the ranking through its ties.

Fit any calibration map on a held-out calibration split, never on the test set.
Reporting test-set-fitted calibration is circular and is caught immediately.

---

## 6. Calibration for LLM classifiers

An LLM emitting a class label does not directly emit a probability. Options, each
with a caveat:

- **Token logprobs** over the label tokens, renormalized across the class set.
  Closest to a real probability. Requires logprob access, and is sensitive to
  tokenization: labels that tokenize into different numbers of tokens are not
  directly comparable.
- **Verbalized confidence** ("how confident are you, 0 to 100"). Widely
  overconfident, heavily quantized to round numbers, and unstable across prompt
  phrasings. Report the distribution before using it; it is often concentrated on
  a handful of values, which makes ECE binning nearly meaningless.
- **Self-consistency** across samples at nonzero temperature. Sample k times, use
  the vote fraction. Well behaved but costs k times the inference, and the
  fraction is bounded by 1/k in resolution.

Whichever is used, state it precisely. "Confidence" without a definition is not
reportable, and the three options behave differently enough that a reader cannot
infer which was meant.

---

## 7. Class-wise and conditional calibration

Aggregate calibration can hide large per-class errors, especially with class
imbalance. Report class-wise ECE for the classes that matter clinically.

Conditional calibration is the stronger and more relevant property for
deployment: is the model calibrated within each site, scanner, stain batch, or
demographic subgroup? A model calibrated overall but overconfident at one site
will fail there specifically. If subgroup labels are available, report at least
the range of subgroup-wise calibration error, since this is what a clinical
reviewer will ask about.

---

## 8. Reporting

Minimum reportable set for a calibration claim:

- Brier or NLL (no binning).
- ECE with the bin count and binning scheme stated, plus a bin-count sensitivity
  line.
- A reliability diagram with bin counts and per-bin intervals.
- The calibration split used to fit any post-hoc map, and its size.
- For temperature scaling: the fitted T and the before/after comparison.
- Intervals on every calibration number, resampled at the cluster level.
