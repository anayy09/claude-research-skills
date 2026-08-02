# Scoring rubric

Six dimensions, 100 points. Score each from the level descriptors, then run
`scripts/rank_ideas.py` for the arithmetic, banding, caps, dominance, and
portfolio selection.

The dimensions are deliberately separable. Novelty and feasibility pull in
opposite directions and the whole point of scoring them apart is to see the
trade explicitly rather than resolving it with a vibe.

| Dimension | Weight | Question it answers |
|---|---|---|
| `novelty` | 25 | How large is the verified delta over the closest found work |
| `significance` | 20 | Who changes what they do if the claim holds |
| `feasibility` | 20 | Can this be executed with the assets, compute, and time that exist |
| `readiness` | 15 | How much of the required evidence already exists |
| `venue_fit` | 10 | Does it match the target venue's scope and evidence bar |
| `durability` | 10 | Will it still be worth citing in two years |

---

## novelty (0 to 25)

Scored against the claim, not the topic. An important area does not raise
novelty.

- **22 to 25.** New phenomenon, mechanism, or negative result, with closest work
  identified and clearly not anticipating. Nobody could write this paper without
  redoing the work.
- **17 to 21.** Clear delta of a named type from the taxonomy in
  `novelty-check.md`, with two or three closest works logged and the difference
  stated in a sentence. Another group could do it but has not.
- **12 to 16.** Real but narrow: a new regime, a new unit of analysis, or an
  extension the closest work explicitly leaves open.
- **6 to 11.** Increment. Passes the incrementality test only after an upgrade
  move, or the delta rests mostly on a dataset or a domain change.
- **0 to 5.** Anticipated by found work, or the delta cannot be stated without
  reference to which components were combined.

Cap at 15 when no prior-art search was performed. An unverified novelty score is
a guess, and the report says so.

## significance (0 to 20)

Ask who behaves differently if the claim holds, and be concrete about who.
"Advances understanding" scores nothing.

- **17 to 20.** Changes a practice, a protocol, or a budget allocation for a
  identifiable group. Other work has to account for it.
- **12 to 16.** Changes how a subfield evaluates or reports something, or
  supplies a resource that unblocks a known question.
- **7 to 11.** Useful to people working on the same task. Cited by the immediate
  neighbors.
- **3 to 6.** Correct and reportable, with no identifiable consumer beyond the
  authors.
- **0 to 2.** The claim holding would change nothing.

Significance is not impact factor. A narrow claim that redirects one lab's
experimental budget scores above a broad claim nobody can act on.

## feasibility (0 to 20)

Score against the assets in the inventory, at the user's real working rate, not
an idealized one. This score is not negotiated upward by shrinking the
experiment until the claim is no longer tested.

- **17 to 20.** Everything needed exists: data in hand with usable terms, code
  that runs, compute allocated, and the analysis is standard. The remaining work
  is execution.
- **12 to 16.** One dependency to resolve, and it is under the user's control:
  one new experiment, one implementation, one allocation request.
- **7 to 11.** A dependency outside the user's control with a plausible path: a
  data request in progress, a collaborator's time, an annotation round, an IRB
  amendment.
- **3 to 6.** Multiple external dependencies, or the experiment exceeds the
  compute budget by a factor rather than a margin.
- **0 to 2.** Requires an asset that does not exist and has no acquisition path
  in the timeline.

Score annotation cost honestly. Expert labeling is the single most common reason
a plausible direction fails, and it is the one most often left out of the plan.

## readiness (0 to 15)

The share of the minimum evidence set (see `paper-path.md`) that already exists.
This is what makes a direction cheap without making it incremental, and it is
the dimension that separates a transition-mode recommendation from a greenfield
one.

- **13 to 15.** Most required experiments are already run. The work is analysis,
  a confirmatory run, and writing.
- **9 to 12.** Core results exist; baselines, ablations, or statistics are
  missing.
- **5 to 8.** Pilot evidence exists showing the effect is plausible; the main
  experiments are not run.
- **2 to 4.** Infrastructure exists, results do not.
- **0 to 1.** Starting from nothing but an idea.

Sunk experiments only count when they were run under conditions the paper can
report. Runs with a since-changed preprocessing pipeline, an unrecorded config,
or a since-fixed bug do not count. Check against the run registry if
`experiment-ledger` is in use.

## venue_fit (0 to 10)

Against the stated target, or against the default venue class for the user's
field if none was given. Note the assumption when it is defaulted.

- **9 to 10.** Squarely in scope, matches an article type the venue publishes,
  and the evidence plan meets its bar without extra work.
- **6 to 8.** In scope, needs one venue-specific addition: an external
  validation cohort, an artifact release, a reporting checklist, a human study.
- **3 to 5.** Adjacent scope. Would need reframing, or a different venue class.
- **0 to 2.** Out of scope, or the evidence bar is unreachable within the
  timeline.

Do not name specific journals here. That is `journal-advisor`'s job, and it does
it against real catalogs.

## durability (0 to 10)

Whether the contribution survives the next model release, the next dataset, or
the next fashion cycle. This dimension exists to penalize leaderboard chasing,
which otherwise scores well on feasibility and readiness.

- **9 to 10.** A phenomenon, a protocol, a resource, or an analysis method.
  Still true and still consumed when today's models are obsolete.
- **6 to 8.** A mechanism or a boundary result tied to a model family that will
  persist for a few years.
- **3 to 5.** A method whose advantage depends on the current best model or the
  current benchmark.
- **0 to 2.** A number on a leaderboard that a routine release would erase.

---

## Cap rules

Apply a cap when a structural problem means the composite would otherwise
mislead. Pass it to the script with `--cap` in the idea entry so the reason
prints alongside the score.

| Condition | Cap |
|---|---|
| Central claim anticipated by found prior work, no recovery move applied | 35 |
| Required data cannot be obtained within the timeline | 40 |
| No ground truth or evaluation exists that could test the claim | 40 |
| Would violate a data use agreement, license, or IRB scope | 30 |
| Overlaps a claim in the user's own prior or in-review paper | 45 |
| Claim is not falsifiable as stated | 45 |
| Compute required exceeds the available allocation by more than 3x | 50 |
| Direction depends on an unrecorded or unreproducible prior run | 55 |

A capped direction is not necessarily dead. The cap reason is the thing to fix,
and it belongs in the report next to the score.

## Calibration anchors

Read these before writing numbers down, because unanchored scoring drifts high.

- A competent extension of the user's own prior work, new dataset, same method,
  no new phenomenon: **around 55 to 62**. Feasibility and readiness carry it;
  novelty and durability do not.
- An anomaly the user already observed, promoted to a thesis, with the mechanism
  experiments still to run: **around 75 to 85**. High novelty, high readiness,
  feasibility depends on the mechanism experiments.
- A well-powered negative result on an assumed effect, with the reproduction
  budget accounted for: **around 65 to 75**. Novelty and durability are strong,
  venue fit is the risk.
- A dataset contribution without a question attached: **below 45**, regardless
  of how much work the data took.
- An ambitious direction requiring data access not yet secured: **capped at 40**
  until access exists, however high it would otherwise score.

If the number and the prose disagree, the prose is usually right. Rewrite the
number.

---

## ideas.json schema

```json
{
  "context": "short label for the project or agenda",
  "target_venue": "optional, free text; affects venue_fit only",
  "available_months": 4,
  "ideas": [
    {
      "id": "D1",
      "title": "one line, the claim in plain words",
      "operators": ["A1", "A2"],
      "scores": {
        "novelty": 21,
        "significance": 16,
        "feasibility": 15,
        "readiness": 12,
        "venue_fit": 8,
        "durability": 8
      },
      "effort_months": 2.5,
      "p_complete": 0.8,
      "assets": ["asset-id", "asset-id"],
      "cap": {"total": 45, "reason": "why"}
    }
  ]
}
```

Field notes:

- `scores` accepts `"na"` for a dimension that cannot be assessed. The script
  reweights the remaining dimensions and reports reduced confidence.
- `effort_months` is the user's real working months, including writing. When in
  doubt, take the estimate that feels right and multiply by 1.5.
- `p_complete` is optional. It is the probability the direction reaches
  submission at all, given that it is started. Omit it and the script derives a
  value from the feasibility score.
- `assets` are ids from the asset inventory. They drive the overlap analysis
  that finds directions sharing an experiment cycle.
- `operators` are ids from `idea-operators.md`, used to check that the candidate
  set is not all one operator in different clothes.
