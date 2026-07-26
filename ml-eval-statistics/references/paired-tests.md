# Paired comparisons

Contents:
1. Why paired
2. Paired bootstrap
3. McNemar
4. DeLong and its assumption
5. Permutation alternative
6. One-sided versus two-sided
7. Equivalence and non-inferiority
8. Reading a null result

---

## 1. Why paired

Both models were evaluated on the same items. Item difficulty is therefore a
shared nuisance: a hard patch is hard for both. Pairing removes it and leaves the
quantity of interest, which is the difference.

Comparing two marginal confidence intervals discards the pairing and is
misleading in both directions. Overlapping intervals do not imply no difference;
non-overlapping intervals are a conservative but crude signal. The correct object
is the interval on the difference.

Worked illustration: two models each with a 95 percent interval of roughly
[0.84, 0.90], intervals almost fully overlapping, can still have a paired
difference of +0.018 with interval [+0.012, +0.025]. Both statements are true at
once, and the second is the one the claim is about.

---

## 2. Paired bootstrap

Procedure:

1. Resample the analysis units (patients, subjects, stays) with replacement.
2. Use the **same** resampled units for both models.
3. Recompute the metric for each model on that resample.
4. Store the difference.
5. Repeat B times. The percentile interval of the stored differences is the
   confidence interval; the two-sided p is twice the smaller tail proportion.

Point 2 is the entire method. Resampling independently for each model produces
an interval on the difference of two independent estimates, which is wider than
the truth and defeats the purpose.

Choice of B: 2,000 is enough for an interval, 10,000 for a p-value near a
threshold. The bootstrap p cannot resolve below about 1/(B+1); reporting
"p < 0.001" from 1,000 resamples is claiming resolution the procedure does not
have.

Implementation detail worth knowing: for metrics that are ratios of sums over
items (accuracy, recall, precision, F1, balanced accuracy), the cluster
bootstrap can be computed by reweighting per-group confusion counts with
multinomial weights instead of materializing resampled index arrays. This is
exact, not an approximation, and turns an intractable computation on a large
patch set into a matrix product. `scripts/eval_stats.py` does this.

---

## 3. McNemar

For comparing two classifiers' accuracy on the same items. Build the 2x2 table
of paired correctness and use only the discordant cells:

|  | B correct | B wrong |
|---|---|---|
| **A correct** | n11 (ignored) | n01 |
| **A wrong** | n10 | n00 (ignored) |

Under the null, each discordant pair is equally likely to favor either model, so
n10 ~ Binomial(n01 + n10, 0.5).

- Discordant count under about 25: exact binomial test.
- Larger: chi-square with continuity correction.

The concordant cells are ignored by design. Two models that agree on 98 percent
of items can still differ significantly, because the evidence lives entirely in
the disagreements. This is a feature: it is the paired structure doing its job.

McNemar assumes the pairs are independent. With patches from the same slide they
are not, and the p-value is too small. Use the clustered paired bootstrap
instead. Reporting McNemar on patch-level data is one of the most common
statistics errors in computational pathology papers.

---

## 4. DeLong and its assumption

DeLong gives an analytic variance for the difference of two correlated AUROCs
using the covariance of the placement values. It is fast, standard, and correct
under one assumption: independent observations.

That assumption fails for patch-level, window-level, or any repeated-measures
data. When it fails, DeLong is anticonservative, sometimes dramatically. On a
representative clustered synthetic dataset with 60 subjects and 200 items each,
DeLong returned p on the order of 1e-10 for a difference the clustered bootstrap
placed at p around 0.003 with a materially wider interval. Both describe the same
+0.018 AUROC difference. Only one of them describes it honestly.

Use DeLong when observations are genuinely independent (one item per subject).
Use the clustered paired bootstrap otherwise, and say in the methods which one
was used and why.

---

## 5. Permutation alternative

For a paired comparison, the exact-in-spirit alternative is to permute the model
labels within each unit:

1. For each analysis unit, with probability 0.5 swap which model's predictions
   are called A and which B.
2. Recompute the difference.
3. Repeat; the p-value is the proportion of permuted differences at least as
   extreme as the observed one.

This tests the sharp null that the two models are exchangeable, which is a
slightly different null than the bootstrap's. It is a good confirmation when a
bootstrap p sits near the threshold, and it is cheap. Agreement between the two
is reassuring; disagreement means the result is fragile and should be reported
as such.

---

## 6. One-sided versus two-sided

Default to two-sided. A one-sided test is defensible only when the direction was
declared before the data were seen and a difference in the other direction would
lead to the same decision as no difference. That is rare in ML papers, where a
surprising reversal is usually the interesting finding.

Switching to one-sided after seeing a two-sided p of 0.08 halves it and is
indefensible.

---

## 7. Equivalence and non-inferiority

"No significant difference" is not "the models are equivalent". To claim
equivalence, declare a margin first: the largest difference that would be
practically irrelevant. Then check whether the entire confidence interval on the
difference lies inside the margin.

This matters for the common claim that a smaller or cheaper model matches a
larger one. Without a stated margin, the claim rests on a failure to detect,
which is a statement about sample size. With a margin of, say, 2 points and an
interval of [-0.4, +1.1], the claim is supported and reviewable.

---

## 8. Reading a null result

A pre-declared comparison whose interval contains zero is a result worth
reporting. What to include:

- The point estimate and interval, so a reader can see how much was ruled out.
- The number of analysis units, since that is what bounds the power.
- Whether the interval excludes a practically meaningful effect. An interval of
  [-0.002, +0.003] rules out anything worth having; [-0.05, +0.06] rules out
  nothing and means the experiment was underpowered.

The second case is honest to report as inconclusive rather than as negative.
