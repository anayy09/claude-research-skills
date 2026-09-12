# PREREGISTRATION.md

Pre-registration for `{{PROJECT}}`. Frozen at the commit that opens the first
phase it governs; tag that commit (`git tag prereg-v1`). After that this file
is not edited. An amendment is a dated section appended at the end, cites the
decision that made it, and says what was known when it was written.

## 0. What was known when this was written

Date {{DATE}}. What data had been seen, which baselines had been computed,
which results from earlier work motivated the design. This section is what
makes the rest honest.

## 1. Hypotheses

Numbered. Each one falsifiable, with the direction of the effect stated.

## 2. Primary endpoint and comparison

The metric, the unit of analysis, the arms, and the contrast. One primary.
Everything else is secondary or exploratory and is labelled so in every
table.

## 3. Decision rules per gate

For each gate in `PLAN.md`: the quantity, the threshold, the interval it is
read with, and the verdict for each outcome including the ambiguous case.
The rule is quoted verbatim when the gate is adjudicated, never paraphrased.
If an observation does not fit the rule cleanly, the verdict is `ambiguous`,
a decision is opened, and the phase does not advance.

## 4. Sample size and power

How the sample was chosen, the minimum detectable effect at that size, and
what will be said if an interval contains zero (not "no effect": "not
distinguishable at this sample size").

## 5. Multiplicity

The family of tests, its size, and the correction. A test designed after the
data existed is outside the family and is reported as exploratory.

## 6. Exclusions and coverage

What is excluded before analysis and why. How parse failures, missing values,
and dropped units are counted and reported. They are data, never imputed
silently.

## 7. Amendments

Appended, dated, each citing its `DECISIONS.md` entry and stating what had
been observed at the time.
