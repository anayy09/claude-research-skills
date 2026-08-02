# Idea operators

A catalog of moves that turn an existing asset into a paper-shaped claim. Each
operator states the trigger that makes it applicable, the shape of the resulting
claim, the evidence that makes it publishable, and the objection a reviewer
raises first. Work through the groups that match the assets in the inventory
rather than reading the whole file every time.

Contents:

- [A. Starting from a result you already have](#a-starting-from-a-result-you-already-have)
- [B. Reframing the problem](#b-reframing-the-problem)
- [C. Building shared infrastructure](#c-building-shared-infrastructure)
- [D. Transferring and combining](#d-transferring-and-combining)
- [E. Exploiting position and access](#e-exploiting-position-and-access)
- [The incrementality test](#the-incrementality-test)
- [Anti-patterns](#anti-patterns)
- [Combining operators](#combining-operators)

A note on how to use these. The operator is a generator, not a template. Two
directions produced by the same operator on the same asset are usually the same
paper, so breadth comes from applying different operators to the same asset, not
from varying the wording of one.

---

## A. Starting from a result you already have

### A1. Anomaly promotion

**Trigger.** A result the user found surprising, could not explain, or set aside
as a side note. Saturation where improvement was expected, a non-monotonic
relationship, two models behaving differently on the same input, a metric moving
the wrong way.

**Claim shape.** "Effect X occurs under condition C, contrary to the assumption
that Y, and it is caused by M."

**Why it publishes.** An unexplained effect that others can reproduce is a
contribution in itself, and the person holding the runs has a head start nobody
can close by reading the paper. This is usually the highest-value operator
available to someone with a project already underway, because the expensive part
is already done.

**Evidence needed.** The effect measured with intervals across seeds and
conditions, a demonstration that it is not an artifact of preprocessing or
metric choice, at least one alternative explanation ruled out, and evidence that
it generalizes past the single setting where it was noticed.

**First objection.** That it is a bug or a hyperparameter accident. Preempt with
the controls that rule out the mundane explanations, before the mechanism story.

### A2. Mechanism attribution

**Trigger.** A known empirical effect, the user's own or the field's, that
everybody reports and nobody explains.

**Claim shape.** "The gain attributed to A is actually produced by B, and the
following intervention separates them."

**Why it publishes.** Explanation is scarcer than performance. A causal
decomposition of an effect that many papers rely on is cited by all of them.

**Evidence needed.** An intervention that isolates the proposed mechanism, a
prediction the mechanism makes that the rival explanation does not, and a test
of that prediction.

**First objection.** Correlational evidence dressed as causal. The intervention
has to break the mechanism and the effect together.

### A3. Boundary mapping

**Trigger.** A method that works in the user's setting, with an untested
assumption about where it stops working.

**Claim shape.** "Method M holds up to condition c*, degrades in this specific
way past it, and the transition is predicted by quantity q."

**Why it publishes.** Practitioners need operating limits more than they need
another point of accuracy. Boundary papers age well because they are consumed as
reference rather than as competition.

**Evidence needed.** A parameter sweep across the boundary variable, degradation
characterized rather than just observed, and a predictor of the transition that
works out of sample.

**First objection.** That the boundary is specific to one dataset. Two settings
minimum, ideally with different failure causes.

### A4. Negative result formalization

**Trigger.** Something that did not work: a method that failed to transfer, an
expected gain that did not materialize, a fine-tune that matched its baseline.

**Claim shape.** "Approach A, widely assumed to help in setting S, does not, and
the reason is R."

**Why it publishes.** Only when the null is well powered and diagnosed. A null
with a shrug is unpublishable. A null with an adequate search over the design
space, an equivalence or non-inferiority analysis, and an explanation of why the
intuition fails is a service to the field.

**Evidence needed.** Evidence that the approach was implemented competently,
including a reproduction of its original reported result where possible; a
search wide enough that the failure is not a tuning artifact; a statistical test
appropriate for a null rather than a non-significant p-value; and a mechanism
for the failure.

**First objection.** "You did it wrong." Budget for the reproduction of the
original claim before anything else. See `paper-path.md` on evidence sets.

### A5. Oracle and headroom decomposition

**Trigger.** Any pipeline with several stages, especially one where a prompt,
retrieval, or routing choice varies performance.

**Claim shape.** "Of the total achievable gain, fraction f is recoverable by
component C, and the remaining headroom is bounded by limitation L."

**Why it publishes.** It tells the field where to spend effort, and it converts
a set of ablations that were run anyway into an analysis paper. Cheap to
execute, hard to argue with, and durable.

**Evidence needed.** A defensible oracle for each stage, the gap between
achieved and oracle performance measured per stage, and a demonstration that the
oracle is attainable in principle rather than a selection artifact on the test
set.

**First objection.** That the oracle is chosen post hoc on the evaluation data.
Compute oracles on held-out data with the selection rule fixed in advance.

### A6. Saturation and scaling characterization

**Trigger.** A knob that stops paying: more data, more parameters, longer
calibration, more retrieved context, higher resolution.

**Claim shape.** "Performance saturates at scale s under regime R, and the
binding constraint past that point is B."

**Why it publishes.** Saturation results redirect budgets. They are also
defensible, because the curve either exists in the data or does not.

**Evidence needed.** Enough points on the curve to distinguish saturation from
noise, intervals on each point, and evidence that the plateau is not a ceiling
of the metric or the annotation quality.

**First objection.** Metric ceiling and label noise. Address both explicitly.

---

## B. Reframing the problem

### B1. Unit-of-analysis shift

**Trigger.** Results reported at one granularity while the decision happens at
another: patch versus slide versus patient, token versus document, request
versus session, sensor window versus episode.

**Claim shape.** "Conclusions drawn at unit u do not transfer to decision unit
U, and the correct aggregation changes the ranking of methods."

**Why it publishes.** It frequently overturns a comparison the field takes for
granted, and it forces the statistics to be done at the right level, which many
prior papers did not do.

**Evidence needed.** The same models evaluated at both units, clustered
resampling at the decision unit, and a demonstration that the ranking changes or
provably does not.

**First objection.** That the aggregation rule was chosen to produce the
reversal. Pre-specify it and show several.

### B2. Constraint inversion

**Trigger.** A constraint the literature assumes away: label budget, latency,
memory, privacy, connectivity, cost per inference, clinician time, energy.

**Claim shape.** "Under constraint K at realistic level k, the ranking of
existing methods changes, and approach P is preferred."

**Why it publishes.** It creates a new operating regime with its own leaderboard
and its own baselines, rather than joining an existing queue.

**Evidence needed.** A defensible level for the constraint sourced from
deployment reality, methods re-evaluated under it with the constraint enforced
rather than reported, and cost accounting that a practitioner can reuse.

**First objection.** That the constraint level is arbitrary. Source it, and show
the conclusion is stable across a range.

### B3. Deployment-condition framing

**Trigger.** A model evaluated on clean held-out data when its real setting has
shift, missingness, a human in the loop, or a workflow with an existing decision
point.

**Claim shape.** "Under the conditions the system actually meets, reported
performance degrades by d, and the following change recovers r of it."

**Why it publishes.** Clinical, industrial, and policy venues weight this
heavily, and the resulting paper is hard to scoop because it depends on domain
access.

**Evidence needed.** A realistic perturbation or external cohort, degradation
quantified, and a mitigation evaluated under the same conditions.

**First objection.** That the simulated conditions are not the real ones. Cite
the source of the shift model, or use real external data.

### B4. Objective substitution

**Trigger.** The field optimizes a metric that does not match the decision:
accuracy where the cost is asymmetric, AUC where the operating point is fixed,
BLEU where the user cares about a downstream task, mean error where the tail is
what hurts.

**Claim shape.** "Optimizing O misranks methods relative to decision-relevant
objective O', and re-ranking under O' changes the conclusion."

**Why it publishes.** It reframes a whole literature with one analysis, and the
data often already exist in published results.

**Evidence needed.** A defensible derivation of the decision-relevant objective
including its cost structure, re-evaluation of several existing methods under
it, and sensitivity of the conclusion to the cost assumptions.

**First objection.** That the cost structure is invented. Source it from
guidelines, published utilities, or a stakeholder elicitation, and run
sensitivity analysis.

### B5. Abstention and selective prediction

**Trigger.** Any system that must be right or must escalate, where full coverage
is not required.

**Claim shape.** "Deferring fraction q of cases by rule r attains risk R, which
full-coverage prediction cannot reach at any operating point."

**Why it publishes.** Selective prediction converts an accuracy problem into a
deployment problem with a workload argument attached, which reviewers in applied
venues find concrete. It also has established evaluation machinery, so the
methods bar is clear.

**Evidence needed.** Risk-coverage curves with intervals, AURC or risk at fixed
coverage, comparison against confidence-thresholding baselines, and a workload
argument in units the domain uses. Hand the statistics to `ml-eval-statistics`.

**First objection.** That a temperature-scaled softmax baseline does as well.
Include it, tuned.

### B6. Cost-sensitive and decision-theoretic reframing

**Trigger.** Asymmetric consequences that the evaluation ignores.

**Claim shape.** "Under the cost matrix implied by the deployment, the optimal
policy is not the argmax classifier, and net benefit improves by b."

**Why it publishes.** Decision-curve and net-benefit analyses are expected in
clinical venues and rare in machine learning ones, which makes the crossover
paper valuable and easy to differentiate.

**Evidence needed.** Explicit cost or utility elicitation, decision curves
across threshold probabilities, and calibration reported alongside, because
decision analysis on an uncalibrated model is meaningless.

**First objection.** Miscalibration invalidating the analysis. Report
calibration first.

---

## C. Building shared infrastructure

### C1. Evaluation protocol contribution

**Trigger.** A field where results are not comparable: different splits,
leakage, inconsistent aggregation, unreported variance.

**Claim shape.** "The standard protocol P admits failure F, which inflates
reported performance by roughly i, and protocol P' removes it."

**Why it publishes.** Protocol papers get adopted and cited long after method
papers are superseded, and the work is mostly analysis rather than new modeling.

**Evidence needed.** A demonstration of the failure on real published setups, a
quantification of its size, a corrected protocol, and re-evaluation of several
existing methods under it.

**First objection.** That the flaw is known and already avoided. Show it in
recent published work, by class rather than by accusation.

### C2. Dataset, benchmark, or annotation contribution

**Trigger.** The user has data access, annotation capacity, or a curation
pipeline others lack.

**Claim shape.** "Resource D supports question Q, which no existing resource can
answer, and baseline results establish the achievable range."

**Why it publishes.** Only with a question attached. A dataset without a
question the field is blocked on is a download link, not a paper.

**Evidence needed.** Documented provenance and licensing, inter-annotator
agreement, an explicit split protocol resistant to leakage, baselines including
a trivial one, a datasheet, and a statement of known biases and limits.

**First objection.** That an existing resource covers it. Name and compare
against the closest three.

### C3. Reproduction and audit study

**Trigger.** A widely cited claim that the user can test with assets already
built, especially across models, seeds, or sites.

**Claim shape.** "Claim C reproduces under conditions X, fails under Y, and the
difference is explained by Z."

**Why it publishes.** Reproducibility tracks exist at many venues and the work
is bounded and predictable, which makes it a strong choice under deadline
pressure. It also builds credibility fast for a new group.

**Evidence needed.** Faithful reimplementation with the original settings, a
systematic variation grid, and an explanation rather than a scoreboard.

**First objection.** Perceived hostility. Frame around conditions and
generalization, never around the original authors.

### C4. Failure-mode taxonomy with a diagnostic suite

**Trigger.** Errors the user has looked at closely enough to see structure in.

**Claim shape.** "Errors partition into k mechanisms with frequencies f, and
diagnostic suite S detects each one."

**Why it publishes.** It turns qualitative intuition into a reusable instrument,
and it gives every subsequent method paper in the area something to report
against.

**Evidence needed.** A coding protocol with a second rater and agreement
statistics, frequencies with intervals, and the suite validated by showing it
separates models that aggregate metrics do not.

**First objection.** That the taxonomy is one person's opinion. Agreement
statistics answer this.

---

## D. Transferring and combining

### D1. Transfer with an obstacle solved

**Trigger.** A method from another field that the user can bring across, where
something specific breaks on arrival.

**Claim shape.** "Method M fails in domain D because of property p; modification
M' resolves it, and the modification is the contribution."

**Why it publishes.** The transfer alone is not a contribution. The obstacle is.
State the obstacle in the abstract, or the paper reads as an application note.

**Evidence needed.** A demonstration that unmodified M actually fails and why, a
modification tied to the diagnosed cause, and an ablation showing the
modification is what recovers performance.

**First objection.** "Novel application of X to Y" with no obstacle. If you
cannot name the obstacle, do not use this operator.

### D2. Hybridization justified by complementary failure

**Trigger.** Two available components with different error profiles.

**Claim shape.** "A and B fail on disjoint cases, and combination rule C
exploits the disjointness for gain g, which neither can reach alone."

**Why it publishes.** Only when the complementarity is demonstrated before the
combination is built. Otherwise this is the kitchen-sink anti-pattern.

**Evidence needed.** Error overlap analysis first, an oracle combination showing
the ceiling, then the practical rule and its gap to the oracle.

**First objection.** That the gain comes from added capacity. Control for
parameters, compute, and ensembling.

### D3. Theory for a working heuristic

**Trigger.** Something practitioners already do that nobody has characterized:
why a schedule works, when a heuristic is optimal, what a scoring rule is
implicitly assuming.

**Claim shape.** "Heuristic H is the solution to problem P under assumptions A,
which explains its behavior and predicts where it fails."

**Why it publishes.** It gives a body of practice a foundation, and the
predictions of failure are directly testable with existing code.

**Evidence needed.** Assumptions stated and checked against practice, a proof or
derivation, and empirical confirmation of at least one non-obvious prediction.

**First objection.** Assumptions strong enough to make the result vacuous. Show
they hold approximately in real settings.

### D4. Survey plus original synthesis

**Trigger.** A fragmented area the user has already read exhaustively, usually
as a byproduct of a related-work section.

**Claim shape.** "The area organizes along axes A, and a common-protocol
comparison shows conclusion C that individual papers cannot support."

**Why it publishes.** Only with original content: a reproducible comparison, a
quantitative meta-analysis, or a taxonomy that makes a testable prediction. A
narrative summary of fifty papers is not publishable in a reputable venue.
Coordinate with `evidence-synthesis` for the search and appraisal, which have
their own reporting standards.

**Evidence needed.** A documented and reproducible search, an appraisal of study
quality, and the original element stated in the abstract.

**First objection.** That it is a reading list. The original element answers it.

---

## E. Exploiting position and access

### E1. Access-dependent extension

**Trigger.** Data, cohorts, instruments, sites, or expert time available to the
user and not to the field.

**Claim shape.** "Effect E, established in setting S, holds or fails in setting
S', which only this cohort can test."

**Why it publishes.** It is close to unscoopable, and external validation is
what applied venues most often say is missing.

**Evidence needed.** A pre-specified analysis to avoid the appearance of
fishing, a fair comparison to the original setting, and honest reporting of
population differences.

**First objection.** Confounding by site or population. Pre-specify adjustments.

### E2. Human-factors study on an existing model

**Trigger.** A working model plus access to the experts who would use it.

**Claim shape.** "Presenting the model's output as V changes expert decision
quality by d relative to no assistance and to alternative presentation V'."

**Why it publishes.** Reader and user studies are rare, hard to replicate, and
weighted heavily in applied venues. The model itself does not need to be new.

**Evidence needed.** A pre-registered design with a power calculation, an ethics
approval, appropriate randomization and counterbalancing, and analysis at the
right unit.

**First objection.** Underpowering. Do the power calculation before recruiting,
and hand the analysis plan to `ml-eval-statistics`.

### E3. Pipeline stage ablation

**Trigger.** A multi-stage pipeline that the field runs by convention.

**Claim shape.** "Of the k stages in the standard pipeline, only stages i and j
affect the outcome; the rest can be removed at no cost."

**Why it publishes.** Simplification results are practical, easy to verify, and
give a reusable recommendation. They also tend to be cheap, because each stage
already runs.

**Evidence needed.** Full leave-one-out over stages, interaction effects for the
stages that matter, and confirmation on a second dataset.

**First objection.** That the removed stage matters in a setting not tested. Be
explicit about the scope of the recommendation.

---

## The incrementality test

Run every candidate through this before it is scored. If the honest one-sentence
summary of the delta matches one of these, the candidate is a least publishable
unit and needs a different operator or an upgrade:

- Same method, new dataset, no new phenomenon.
- Existing architecture with one module added, evaluated on the standard
  benchmark, gain within the range of seed variance.
- A benchmark number improved with no explanation of what changed.
- A survey with no original comparison, taxonomy, or synthesis.
- An application of a general method to a domain with no domain-specific
  obstacle.
- A pipeline described but never compared to the obvious simpler alternative.

Upgrade paths, in rough order of how often they work: attach a mechanism (A2),
map the boundary where the increment stops helping (A3), decompose the headroom
so the increment is placed in context (A5), or shift to the decision-relevant
objective or unit (B1, B4). An increment that comes with an explanation is a
contribution. An increment that comes with a table is a workshop paper.

## Anti-patterns

- **Novelty by combination.** Three known components stacked, with the novelty
  claim resting on the fact that nobody stacked exactly these. Reviewers see
  through this in a paragraph.
- **Benchmark chasing.** Choosing a direction because a leaderboard exists.
  Gains evaporate on the next model release and the paper dies with them, which
  is a durability problem as well as a novelty one.
- **Buzzword attachment.** Adding an agent, a foundation model, or a graph
  because it is current, without a problem property that requires it.
- **Salami slicing.** Splitting one contribution into three papers. Check
  self-overlap in `novelty-check.md`.
- **Assumed access.** A direction that needs a cohort, an annotation budget, or
  a cluster allocation that does not exist yet, presented as if it does.
- **Unfalsifiable framing.** Claims like "we explore the potential of X". There
  is no result that could make this false, so there is no finding.
- **The infinite pilot.** A direction with no kill criterion, which absorbs
  months without ever failing clearly enough to stop.

## Combining operators

The strongest directions usually stack two operators where one supplies the
phenomenon and the other supplies the framing. Common pairings that work:

- A1 with A2: an anomaly plus its mechanism. This is the standard shape of a
  strong empirical paper.
- A5 with B1: headroom decomposed at the decision unit, which converts an
  ablation set into an analysis paper.
- B2 with C1: a constraint that also exposes a protocol flaw, because the
  constraint was never enforced in prior evaluations.
- A4 with A2: a null plus an explanation, which is the only reliably publishable
  form of a negative result.
- C2 with E1: a resource plus the question that only that resource answers.

Avoid stacking more than two. A direction that needs three operators to sound
interesting is usually two papers, or none.
