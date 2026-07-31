# Paper rubric

Five dimensions, 100 points. Weights reflect what actually decides reviews:
whether the contribution is new, and whether the evidence supports it.

| Key | Dimension | Max |
|---|---|---|
| `novelty` | Novelty and contribution | 25 |
| `rigor` | Technical rigor and validity of evidence | 25 |
| `application` | Practical application and impact | 15 |
| `integrity` | Authenticity of the contribution | 15 |
| `readiness` | Publication readiness | 20 |

Score each dimension on its own evidence. Do not let a strong method section
rescue a novelty score, or a clean writing style rescue a rigor score. Halo
effects between dimensions are the main source of inflated totals.

---

## 1. Novelty and contribution (25)

**What it measures.** Whether the central claim is new relative to the closest
existing work, and whether the delta is large enough to be worth a paper.

**Judge against the claim map**, not the topic. "LLMs for pathology triage" is a
topic. "A patch-level triage policy that reaches 92 percent sensitivity while
deferring 40 percent of patches" is a claim.

| Points | Level |
|---|---|
| 22 to 25 | New problem, new method, or a result that overturns an accepted finding. Nothing found in the search anticipates the claim. The delta is stated explicitly and is defensible. |
| 17 to 21 | Meaningful advance on known work: a new combination that is non-obvious, a known method applied to a domain where it was not known to work and where that transfer is itself hard, or a substantially better result with an explained mechanism. |
| 12 to 16 | Incremental but real. Known method, new dataset or new domain, modest improvement. Publishable in the right venue if the evaluation is strong. This is where most competent papers sit. |
| 6 to 11 | Delta is thin or unstated: parameter tuning presented as method, a domain transfer where the transfer is trivial, or a survey of one's own prior work. |
| 0 to 5 | Anticipated by prior work that the paper does not cite, or the claim restates a known result. |

**Evidence to look for.** A related-work section that names the closest two or
three works and states the difference in one sentence each. Its absence is
itself a signal: authors who cannot name the closest work usually have not
established the delta.

**Common failure modes.** Novelty asserted in the introduction and never
revisited. Related work organized as a bibliography instead of a comparison.
The delta being an engineering convenience rather than a scientific claim.

---

## 2. Technical rigor and validity of evidence (25)

**What it measures.** Whether the experiments, proofs, or analyses actually
establish the claim, over the scope the claim is asserted at.

| Points | Level |
|---|---|
| 22 to 25 | Design matches the claim. Appropriate baselines, held-out or external validation, ablations isolating the contributing component, uncertainty quantified, negative results reported. Reproducible from what is written. |
| 17 to 21 | Solid: correct splits, credible baselines, sensible metrics. Gaps are specific and fixable, for example missing ablations or missing confidence intervals. |
| 12 to 16 | Adequate but under-evidenced. Weak or dated baselines, single split, no uncertainty estimates, or metrics that do not measure what the claim asserts. |
| 6 to 11 | Design does not support the claim: no baseline, tuned on the test set, evaluated on one small sample, or conclusions drawn well beyond the tested scope. |
| 0 to 5 | Result is not interpretable as reported. Leakage, a broken protocol, or a metric computed incorrectly. |

**Checks that catch most problems.**

- Does the split protocol prevent leakage at the right unit? Patient, slide,
  subject, and site level leakage all survive a random patch or record split.
- Are the baselines what a reviewer in this subfield would demand, at
  comparable tuning effort? An untuned baseline against a tuned method is not a
  comparison.
- Does the metric match the claim? Accuracy on an imbalanced set, AUROC for a
  deployment threshold decision, and BLEU for factuality are all common
  mismatches.
- Is there any uncertainty estimate? Single-number comparisons across runs
  cannot support a claim of improvement. Point to `ml-eval-statistics` when the
  fix is a paired test or a bootstrap interval.
- Are the hyperparameters, seeds, and selection procedure stated well enough to
  reproduce the number?

---

## 3. Practical application and impact (15)

**What it measures.** Whether anyone can use the result, and what changes if
they do. Reward demonstrated applicability over asserted potential.

| Points | Level |
|---|---|
| 13 to 15 | Deployable or directly usable: realistic constraints respected (latency, cost, data availability, regulatory path), an end-to-end demonstration, released code or data, and a named user or workflow that benefits. |
| 10 to 12 | Clear path to use with a stated gap, for example validated retrospectively with the prospective step described. Practical constraints are acknowledged with numbers. |
| 6 to 9 | Plausible application asserted in the discussion but not demonstrated. Compute, data, or deployment requirements not addressed. |
| 3 to 5 | Application section is generic. The same paragraph would fit any paper in the field. |
| 0 to 2 | No applicability argument, or the stated application is contradicted by the paper's own constraints. |

Theory papers are not penalized for lacking a deployment story. Score them on
whether the result is usable by other researchers: does it give a bound, a
method, or an impossibility result that changes what others build?

---

## 4. Authenticity of the contribution (15)

**What it measures.** Whether the reported work was actually done as described,
and whether credit and provenance are honest. This is the dimension that
protects the record. Run `references/authenticity-checks.md` before scoring it.

| Points | Level |
|---|---|
| 13 to 15 | Everything checks: numbers consistent across abstract, text, tables, and figures. Citations verified and used correctly. Data provenance, ethics approval, and licensing stated. Contributions, funding, and conflicts declared. Code or data available or a stated reason why not. |
| 10 to 12 | Minor inconsistencies of the typo class, or missing availability statement, with no effect on the claim. |
| 6 to 9 | Material gaps: unverifiable citations, missing ethics or provenance for human data, results that cannot be traced to a described procedure, or overclaiming that the results do not support. |
| 3 to 5 | Several unverifiable references or citations that do not support the sentence citing them, undisclosed overlap with the authors' prior papers, or numbers that change between sections without explanation. |
| 0 to 2 | Direct evidence of fabricated data, invented references, duplicated or manipulated figures, or plagiarism. |

Scoring low here is a serious statement. Score on what is observable and write
the observation, not the inference. If the evidence supports only a question,
ask the question in the review and score in the 6 to 9 range rather than lower.

---

## 5. Publication readiness (20)

**What it measures.** Whether an editor would send this out for review, and
whether a reviewer can follow it without reconstructing it.

| Points | Level |
|---|---|
| 17 to 20 | Clear structure, an abstract that states the actual result with numbers, self-contained figures and tables, complete and correctly formatted references, and language that does not slow the reader. Meets standard length and formatting expectations. |
| 13 to 16 | Readable with specific weak spots: an unclear method subsection, figures needing labels or captions, or an abstract that undersells the result. |
| 9 to 12 | Substantial editing needed: buried contribution, disorganized results, inconsistent notation, figures that cannot be read at print size, or reference formatting that must be redone. |
| 5 to 8 | Would likely be desk-rejected on presentation alone, independent of the science. |
| 0 to 4 | Incomplete draft: placeholder sections, missing method or results, or missing references. |

Readiness is the cheapest dimension to fix and the most common reason a good
paper stalls. Say what specifically to fix and in what order.

---

## Cap rules

Apply with `--cap-total` and always name the reason. A cap is not a punishment,
it is a statement that the score cannot be interpreted until the issue is
resolved.

| Condition | Cap |
|---|---|
| Leakage between train and test at the relevant unit, unresolved | 55 |
| The headline claim is anticipated by prior work found in the search | 50 |
| Required baseline for the claim is absent | 65 |
| Human-subject or patient data with no ethics approval or provenance stated | 60 |
| Direct evidence of fabrication, plagiarism, or figure manipulation | 30 |
| Core method not described in enough detail to reproduce | 60 |

Only one cap applies, the lowest. Report the cap in the snapshot, state what
lifting it would require, and give the projected score in the after-fixes
section so the author can see what the work is worth once the issue is fixed.
