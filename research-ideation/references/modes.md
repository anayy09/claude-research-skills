# Modes

Five modes. They share the workflow in SKILL.md and differ in which operators
get priority, what the ranking optimizes for, and what the report leads with.
Pick one at step 2 and say which one was picked.

---

## transition (default)

**When.** A project exists: code that runs, results in hand, maybe a half-drafted
paper. The user wants it to become a submission.

**Operator priority.** A1 anomaly promotion, A5 headroom decomposition, A3
boundary mapping, B1 unit shift, then the rest. Start from what the runs already
show, because that is where the readiness score comes from.

**Ranking emphasis.** `readiness` and `feasibility` are doing the real work
here. A direction that reuses four existing experiments and needs one more beats
a more novel direction that needs six, unless the novelty gap is large.

**What the report leads with.** The single strongest claim the existing results
can already support, before any new direction. Users in this mode frequently
have a paper already and do not know it, because the claim they are chasing is
weaker than the one they can prove.

**Specific trap.** Framing the paper around the thing that took the most work
rather than the thing that is most interesting. Engineering effort and
contribution are unrelated. If the pipeline took four months and the interesting
result is a two-line observation from an ablation, the paper is about the
observation.

---

## greenfield

**When.** Assets and interests exist, no project underway. Common at the start
of a degree, a new lab role, or after a paper ships.

**Operator priority.** C2 resource, E1 access-dependent extension, B2 constraint
inversion, C1 protocol, D1 transfer with an obstacle. Start from what the user
has structural access to, since that is the only durable advantage available
before any results exist.

**Ranking emphasis.** `novelty` and `durability` weigh more, `readiness` less,
since nothing is ready by definition. Feasibility still binds hard.

**What the report leads with.** The asset that constitutes an unfair advantage,
and the two or three questions only that asset can answer.

**Specific trap.** Choosing by topic interest and backing into feasibility. Run
the feasibility scoring before the user commits emotionally to a direction, and
be explicit when a direction needs an asset acquisition before it is real.

---

## salvage

**When.** Experiments failed, saturated, produced a null, or the effect vanished
at scale. Often arrives phrased as a request for help fixing something.

**Operator priority.** A4 negative result formalization, A2 mechanism, A6
saturation characterization, A3 boundary mapping.

**Ranking emphasis.** `significance` and `durability`, because a null is only
worth publishing when the assumption it kills was widely held. A negative result
about something nobody believed is not a contribution.

**What the report leads with.** An honest read on whether the null is publishable
at all. The test: was the effect assumed by a body of work, was the
implementation faithful, and is the search wide enough that the null is not a
tuning artifact. If any of the three fails, say so first and pivot to a
different operator on the same assets rather than dressing up an underpowered
failure.

**Specific trap.** Publishing a null that is really a bug. Before anything else,
budget for reproducing the original positive result the method is supposed to
achieve. If that reproduction fails, the problem is the implementation, not the
field's assumption.

---

## portfolio

**When.** A thesis, a grant, a lab agenda, or a promotion case spanning a year or
more. Multiple papers, shared assets, ordering matters.

**Operator priority.** All of them, but generate across at least six distinct
operators, since a portfolio of one operator is one paper split into pieces.

**Ranking emphasis.** Asset overlap and sequencing. The script's overlap analysis
and portfolio picks are the main output. A direction that unlocks two others is
worth more than its own composite suggests, and the report says so explicitly.

**What the report leads with.** The dependency graph: which paper must exist for
the next one to be citable, which experiment cycle serves two papers, and which
long-lead item (data access, IRB, annotation) has to start this month regardless
of what is written first.

**Specific traps.** Two: salami slicing, which the self-overlap check in
`novelty-check.md` catches; and a portfolio where every paper depends on the
same unproven premise, which means one negative result kills the whole plan.
Diversify the premise, not just the topic.

---

## stress-test

**When.** The user has an idea and wants it attacked. Also the right mode when a
user asks whether an idea is good, which is a request for adversarial review
rather than for encouragement.

**Operator priority.** None initially. Start by reconstructing their claim in one
falsifiable sentence and confirming it is what they meant. A large share of weak
ideas are strong ideas stated badly, and this step resolves those before any
criticism lands.

**Ranking emphasis.** Score their idea against the rubric, then generate two or
three alternatives from different operators on the same assets and score those
too. The comparison is the deliverable. Scoring an idea alone tells the user
little, since they have no reference point.

**What the report leads with.** The reconstructed claim, then the strongest
objection to it, then whether the objection is fatal or fixable, then the
alternatives. Not a score.

**Specific trap.** Both directions of miscalibration. Agreeable review costs the
user months of work on a direction that will not land. Reflexive contrarianism
costs them a good idea. Score against the same rubric used for directions the
skill generated itself, and if their idea beats the alternatives, say so plainly
and move to the paper path.
