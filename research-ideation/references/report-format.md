# Report format

Use this structure. It is ordered so a user who stops reading after the lead
direction still knows what to start on Monday.

---

## Required structure

```
## Situation read
Three to five lines: what the user has, what state it is in, what the binding
constraint is (time, data, compute, access), and the assumption made about
anything they did not specify. If one direction is clearly ahead, say so here in
one sentence rather than making the reader find it.

## Asset inventory
Compact table of what the recommendations stand on: datasets, models, code,
existing results including negative ones, access, compute, timeline. Mark the
anomalies and the unclaimed sunk evidence, since these carry most of the value.
Anything the user did not supply and that matters is listed as unknown, not
guessed.

## Candidate directions
The ranked table from rank_ideas.py: id, title, the six dimension scores,
composite, band, effort, and any cap with its reason. Directions flagged as
dominated appear with the direction that dominates them.

## Lead direction
One full idea card (format below).

## Runner-up directions
Two to four compressed cards: claim, delta and closest work, what exists, what
is missing, kill experiment, and the one line on why it is not the lead.

## Portfolio and sequencing
Which directions share assets or experiment cycles, what order to run them in,
and what one experiment cycle can serve two papers. If a direction must come
first for positioning or citation reasons, say which and why.

## What I would not do, and why
Two to four directions considered and dropped, each with one line of reason:
anticipated by named work, infeasible on the assets, fails the incrementality
test, or not falsifiable. This section prevents the user from re-proposing them
next month.

## Verification notes
What was searched and where, what could not be checked, which dimensions were
scored without evidence, and the confidence level. One or two lines.
```

---

## Idea card format

```
### D<n>. <Title, the claim in plain words>

**Claim.** One falsifiable sentence. What is asserted, over what population or
regime, measured how.

**Why it is not obvious.** One or two sentences: the assumption it violates or
the gap it fills. Not a restatement of the claim.

**Closest work.** Two or three citations with venue and year, each with the one
sentence of overlap and the one sentence of difference. If nothing was found,
say what was searched.

**Delta type.** From the taxonomy in novelty-check.md.

**Assets used.** Named, from the inventory.
**Assets still needed.** Named, with how they would be obtained and the cost.

**Headline table.** The rows, columns, and the cell the claim lives in, with the
target value stated as a target.

**Evidence plan.** The blocking items from the gap ledger, in execution order,
with effort per item. Note which statistics are required and that they hand off
to ml-eval-statistics.

**Kill experiment.** The smallest run that could show the effect is not there,
its cost, and the decision rule written before it runs.

**Top three reviewer objections.** Each with the answer, or with the experiment
that would produce the answer.

**Risks.** Two or three, each with the mitigation or the early signal that it is
materializing. Include the scooping risk if the area is active.

**Score.** Composite with band, and the one dimension that limits it.

**Timeline.** Phases against the deadline from plan_timeline.py, with the slack.
```

---

## Worked example of a lead card, compressed

> ### D1. Deferral gain in patch-level triage comes from routing, not from calibration
>
> **Claim.** In patch-level colorectal triage, the risk reduction attributed to
> calibrated confidence is produced by the routing behaviour of the
> domain-adapted model, and holds when calibration is removed entirely, measured
> as risk at 60 percent coverage at the patient level.
>
> **Why it is not obvious.** The selective prediction literature treats
> calibration as the mechanism that makes deferral work, so a result showing the
> gain survives removing it reassigns the credit and changes what practitioners
> should tune.
>
> **Closest work.** Author et al., venue, 2025: reports deferral gains with
> temperature scaling in histopathology, does not separate routing from
> calibration. Author et al., venue, 2024: separates them in natural images,
> different failure regime.
>
> **Delta type.** New mechanism.
>
> **Assets used.** Existing temperature-scaling sweep, existing routing traces
> for both model families, patch-level splits.
> **Assets still needed.** Patient-level regrouping of the current splits, two
> days. No new data.
>
> **Headline table.** Rows: full coverage, calibrated deferral, uncalibrated
> deferral, calibration-only. Columns: risk at 60 and 80 percent coverage, AURC,
> all with patient-clustered intervals. The claim lives in the uncalibrated
> deferral row matching the calibrated row within the interval. Target: overlap
> at both coverage levels.
>
> **Kill experiment.** Recompute the existing sweep at patient level for one
> model family, one day. Continue if the uncalibrated and calibrated risk
> intervals overlap at 60 percent coverage. If they separate cleanly, the claim
> inverts and the direction becomes a calibration-necessity result, which is
> weaker but still publishable.
>
> **Top three objections.** (1) The temperature-scaled baseline was undertuned:
> answer with the existing sweep, which covers the range. (2) Patch-level
> clustering inflates the interval: answer with the patient-level clustered
> bootstrap. (3) It is specific to one model: answer with the second family,
> already run.
>
> **Score.** 81, lead candidate. Limited by venue fit at 7, since the target
> journal expects an external cohort.

Note what the example does: the claim names its unit and its metric, the closest
work is separated into overlap and difference, the kill experiment has a rule
and a stated fallback direction, and the target value is labeled as a target.

---

## Style rules

- One falsifiable sentence per claim, and it comes first in the card.
- Name assets, never "existing data". The user should recognize the file.
- Effort in the user's real working time, and say when it is an estimate.
- No em dashes. No transformative, groundbreaking, or novel-and-innovative.
- Projected numbers are labeled as targets. Do not write a result that has not
  been measured.
- Tables for the ranking and the inventory, prose for the cards. The reasoning
  in a card has to be visible or the user cannot disagree with it.
- Keep the whole report readable in about ten minutes. If it runs longer, the
  runner-up cards are doing too much and should compress to five lines each.
- Do not restate the user's project back to them beyond the situation read.
- No venue names, no acceptance probabilities. The band carries the outlook and
  `journal-advisor` carries the venue.
