# Selective prediction, triage, and deferral

Contents:
1. Why accuracy is the wrong headline for a triage system
2. Risk-coverage curves
3. AURC and E-AURC
4. Choosing an operating point
5. Confidence scores that can drive deferral
6. Cost framing and decision curve analysis
7. Routing between models
8. What clinical reviewers actually ask

---

## 1. Why accuracy is the wrong headline for a triage system

A triage system does not have to be right about everything. It has to be right
about the cases it keeps, and it has to keep enough of them to save work. Full
coverage accuracy answers neither question.

The two numbers that describe the product are: the error rate on retained cases,
and the fraction of cases retained. Everything else is machinery for producing
them.

---

## 2. Risk-coverage curves

Sort cases by confidence, descending. At coverage c, the system handles the top
c fraction and defers the rest. Risk at coverage c is the error rate among the
retained cases.

The curve should be monotone increasing in a well-behaved system: as you accept
less confident cases, error rises. A flat or non-monotone curve means the
confidence score is not ranking difficulty, which is a more important finding
than any single accuracy number.

Read the curve at coverage levels that correspond to plausible deployments
(10, 25, 50, 75, 90, 100 percent) rather than only summarizing it.

Every point on the curve needs an interval, resampled at the subject level. A
coverage estimate from a single draw of the test set is a point estimate of a
quantity that varies substantially across patients.

---

## 3. AURC and E-AURC

**AURC** is the area under the risk-coverage curve. Lower is better. It
summarizes the whole curve in one number, which is useful for comparing
confidence scoring functions and useless for describing a deployment.

**E-AURC** subtracts the AURC that an oracle ranking would achieve given the same
total number of errors, isolating the quality of the confidence ranking from the
quality of the underlying classifier. A model with high accuracy will have low
AURC almost automatically; E-AURC asks the separate question of whether the
confidence signal is any good.

Report both. Reporting AURC alone conflates two things a reader wants separated:
"the model is accurate" and "the model knows when it is wrong".

---

## 4. Choosing an operating point

The operating point is a clinical decision, not a statistical one. Two ways to
set it, and they must not be mixed up:

- **Fix the risk, read the coverage.** "At an error rate no worse than 5 percent
  on retained cases, the system handles 38 percent of the workload." This is the
  framing that matches how a lab would deploy it.
- **Fix the coverage, read the risk.** "Handling half the workload, the error
  rate on retained cases is 7.1 percent." Useful when capacity is the binding
  constraint.

Select the threshold on a validation split, then report performance at that fixed
threshold on the test set. Selecting the threshold on the test set and reporting
performance at it overstates both numbers, and the amount of overstatement grows
with how finely you searched.

Report the threshold value itself, so the result is reproducible and deployable.

---

## 5. Confidence scores that can drive deferral

Anything monotone in expected correctness will do. Common choices, roughly in
order of how well they usually work:

- Max softmax probability, after calibration.
- Margin between the top two class probabilities. Often better than max
  probability for multi-class, since it directly measures ambiguity.
- Entropy of the predicted distribution.
- Ensemble or multi-sample agreement. Strong but costs k inferences.
- A learned selector trained to predict correctness. Highest ceiling, needs its
  own held-out data, and easy to overfit.

For LLM classifiers, see the caveats in `calibration.md` section 6. Verbalized
confidence in particular is often too quantized to produce a usable coverage
curve: if 70 percent of cases are assigned exactly 0.9, the curve has a single
large step and no usable operating points between coverage levels.

Check the score's distribution before evaluating it. A degenerate distribution is
diagnosed in one histogram and explains an otherwise confusing risk-coverage
curve.

---

## 6. Cost framing and decision curve analysis

Clinical readers think in costs, not error rates. A false negative in cancer
triage and a false positive are not exchangeable, and a single accuracy number
assumes they are.

**Decision curve analysis** plots net benefit against threshold probability,
where the threshold encodes the implied cost ratio a decision maker holds. It
answers whether using the model beats the default strategies (treat everyone,
treat no one, review everything) across a plausible range of preferences, without
requiring the analyst to pin down one cost ratio.

Minimum version, cheap and effective: report a cost table at two or three
plausible cost ratios, showing expected cost per 1,000 cases for the model versus
review-everything. This converts a metric into a workload and cost argument,
which is what a clinical collaborator or a reviewer at a medical venue is
evaluating.

---

## 7. Routing between models

A router that sends easy cases to a small model and hard ones to a large model is
a selective prediction system with two accept regions rather than one. Evaluate
it the same way, with these additions:

- Report the routing fraction and its interval, not just aggregate accuracy.
- Report accuracy conditional on route: the small model's accuracy on cases it
  was given, and the large model's on cases it was given. Aggregate accuracy can
  look good while the router is systematically wrong about which cases are hard.
- Compare against two references: the small model alone, and the large model
  alone. The claim is usually "close to large-model accuracy at a fraction of the
  cost", and both endpoints are needed to evaluate it.
- Report cost explicitly (tokens, GPU seconds, dollars per 1,000 cases), because
  that is the axis the routing is trading against.

When two related models route differently on the same inputs, that divergence is
a finding about the confidence signal, not necessarily about capability. The
diagnostic is whether the routing decisions correlate with actual per-case
difficulty (measured by, say, agreement across many samples or by the accuracy of
a strong reference model), or only with surface features such as output length or
prompt position. Establish that before offering a mechanism explanation.

---

## 8. What clinical reviewers actually ask

- What fraction of the workload does this remove, at what error rate?
- What happens to the cases it defers? A triage system that defers the hard cases
  to a human has not eliminated the hard cases.
- What is the error rate on the retained cases in the worst-performing subgroup
  or site, not just overall?
- What is the failure mode of the retained errors? Systematic errors on one tissue
  type are much worse than scattered ones, even at the same rate.
- How was the threshold chosen, and on what data?
- What is the interval on the coverage number?

Answering these in the results section rather than in a rebuttal is the
difference between a smooth review and a long one.
