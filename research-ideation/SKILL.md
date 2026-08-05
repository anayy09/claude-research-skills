---
name: research-ideation
description: >-
  Act as a research strategist: read the user's existing research assets
  (papers, projects, code, datasets, preliminary or negative results, open
  questions) and produce ranked research directions, each with a verified
  novelty delta, a falsifiable claim, the minimum evidence set that makes it
  publishable, an experiment plan from the current state to a submission-ready
  paper, and honest risks. Use whenever the user asks what to work on next, what
  the paper should claim, how to turn a project, prototype, side result,
  surprising finding, or failed experiment into a publication, how to get a
  paper out of existing results, what is novel enough to publish, how to plan a
  thesis or multi-paper agenda, whether an idea is worth doing, or how to
  strengthen an idea they have. Also use when someone shares a repo or results
  table and asks where to take it, or plans the next paper against a deadline.
  Prefer this over free-form brainstorming: ideas must be grounded in the user's
  real assets and checked against real prior work.
summary: "Turn existing research assets into ranked, publishable directions with a plan to submission."
version: "1.0.1"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-08-04"
---

# Research Ideation

Generate research directions that are worth doing and can actually be finished.
The output is not a list of topics. It is a small set of candidate papers, each
one anchored to a falsifiable claim, a verified gap in the literature, the
specific assets the user already has, and the shortest honest path from where
the work stands today to a submission.

Two failure modes bracket this task. Sterile ideation produces safe increments:
new dataset, same method, plus 1.2 points. Ungrounded ideation produces exciting
directions that need a cohort, a cluster, or a year the user does not have. The
job is the narrow band between them, and it is reached by scoring novelty and
feasibility as separate axes and refusing to trade one silently for the other.

## Scope, and what belongs elsewhere

This skill decides what to work on and how to get it to a submission. It does
not:

- Run the literature review itself. Use `evidence-synthesis` for a systematic or
  scoping review, and `investigating-sources` when the direction needs a full
  evidence base rather than a targeted prior-art check.
- Pick the venue. Hand off to `journal-advisor` once a direction is chosen.
- Score a finished manuscript. That is `submission-reviewer`.
- Compute the statistics. Specify what test or interval is required, then hand
  off to `ml-eval-statistics`.
- Write the paper. Hand off to `research-paper-writing`, then
  `submission-formatter` for the venue's template.
- Design the run tracking. Hand off to `experiment-ledger` once the experiment
  plan is agreed, and to `hpc-cluster` for cluster execution.

## Workflow

### 1. Build the asset inventory before generating anything

Ideas are only as good as the assets they can stand on, so catalog the assets
first. Fill `assets/asset-inventory.md` from whatever the user supplied, and
read code, papers, notebooks, and results files that are available rather than
inferring their contents.

Record: datasets and their access terms, models and endpoints, compute budget,
code that already runs, results that already exist including negative and
inconclusive ones, prior papers by the user, collaborators and their access,
IRB or data use agreements, and the timeline.

Two entries matter more than the rest and are usually underreported by the user:

- **Anomalies.** Any result the user found surprising, could not explain, or set
  aside. These are the highest-yield raw material in the inventory, because a
  documented unexplained effect is a paper thesis that nobody else can write
  without the same runs.
- **Sunk evidence.** Experiments already run that are not yet claimed by any
  paper. This is what makes a direction cheap without making it incremental.

Ask for what is missing only when it changes the ranking. If the user gave no
timeline or venue, assume a working default, state the assumption in one line,
and proceed.

### 2. Pick the mode

| Situation | Mode | Reference |
|---|---|---|
| Existing project or results, needs to become a paper | `transition` (default) | `references/modes.md` |
| Assets and interests but no project underway | `greenfield` | same |
| Experiments that failed, saturated, or produced a null | `salvage` | same |
| Thesis, grant, or multi-paper agenda across a year or more | `portfolio` | same |
| User already has an idea and wants it attacked and strengthened | `stress-test` | same |

Modes change what step 3 emphasizes and what the report leads with. Everything
else in the workflow is shared.

### 3. Generate candidates with the operators, not from memory

Work through `references/idea-operators.md`. Each operator is a move that turns
an asset into a claim, with the trigger condition that makes it applicable, the
shape of the resulting central claim, the evidence that makes it publishable,
and the objection a reviewer raises first.

Generate broadly here: aim for eight to fifteen raw candidates across at least
four different operators before filtering anything. Diversity across operators
matters more than diversity across topics, because two ideas from the same
operator usually collapse into one paper.

Then compress. Merge candidates that share a central claim, and drop the ones
that fail the incrementality test in the operator file. Carry four to seven
survivors into scoring.

For each survivor, write the claim in one falsifiable sentence before writing
anything else about it. If the claim cannot be stated in a sentence that could
turn out false, the candidate is a topic, not a direction, and it does not
survive.

### 4. Check novelty against real prior work

Follow `references/novelty-check.md`. Search rather than recalling: web search,
Google Scholar, arXiv, PubMed for clinical and biomedical work, OpenReview and
dblp for machine learning venues, and patent databases when there is a filing
angle.

For each surviving direction, record the two or three closest works with title,
venue, year, and one sentence naming the overlap, then classify the delta using
the taxonomy in that file. A direction whose closest work is unknown has not
been checked, and its novelty score is provisional.

When a direction turns out to be taken, do not delete it silently. Apply one of
the four recovery moves in the novelty file, or report it as excluded with the
paper that excludes it. Both outcomes are useful to the user.

Also check self-overlap against the user's own prior papers. Two papers that
share a claim are a salami-slicing problem regardless of how different the
experiments look.

### 5. Score and rank

Score each direction on the six dimensions in `references/scoring-rubric.md`,
then compute the ranking with the script so arithmetic, banding, dominance, and
portfolio selection are deterministic:

```bash
python scripts/rank_ideas.py --rubric                      # dimensions, weights, caps
python scripts/rank_ideas.py --ideas ideas.json            # ranked table + portfolio
python scripts/rank_ideas.py --ideas ideas.json --available-months 4
python scripts/rank_ideas.py --ideas ideas.json --json     # machine-readable
```

The script reads a small JSON file with one entry per direction. Its schema is
documented in `--rubric` output and in `references/scoring-rubric.md`. Effort is
supplied in months of the user's actual working time, not idealized time.

Caps exist so an exciting direction cannot outrank a workable one on enthusiasm.
Apply a cap when a direction is anticipated by found prior work, depends on data
the user cannot obtain, cannot be evaluated with any available ground truth, or
would violate a data use agreement or ethics constraint.

### 6. Build the path to publication for each surviving direction

Follow `references/paper-path.md`. For every direction that survives scoring,
produce the gap ledger, the headline results table designed before any run
happens, the minimum evidence set for its contribution type, the kill experiment
with its decision rule, the predictable reviewer objections with answers, and
the schedule.

Schedule against the real deadline:

```bash
python scripts/plan_timeline.py --deadline 2026-11-15 --effort-months 3
python scripts/plan_timeline.py --deadline 2026-11-15 --effort-months 3 \
    --profile method --buffer 0.2 --start 2026-08-05
```

If the schedule shows negative slack, say so and cut scope explicitly rather
than compressing every phase by a fifth on paper. The phases the script marks
compressible are the only honest place to take time from.

### 7. Write the report

Use the exact structure in `references/report-format.md`. The lead direction
gets a full idea card. Runners-up get compressed cards. The report ends with
what was deliberately not recommended and why, which is often the most useful
section for a user who has been circling the same three ideas for a month.

## Ranking bands

| Composite | Band | What it means |
|---|---|---|
| 80 to 100 | Lead candidate | Real delta, evidence largely in hand, finishable in the stated window. Start here. |
| 65 to 79 | Strong contender | Genuine contribution with one open dependency, usually an experiment or a data access. |
| 50 to 64 | Viable, gap to close | Publishable somewhere as it stands, needs a sharper claim or a stronger comparison to be competitive. |
| 35 to 49 | Needs reframing | The asset is interesting, the claim is not yet a paper. Apply a different operator. |
| Below 35 | Not a paper yet | Say so plainly, and say what would change that. |

**Calibration.** A competent, well-supported incremental extension of the user's
own prior work is a 60, not an 85. Reserve 80 and above for directions where the
novelty delta was verified against named prior work, most of the required
evidence already exists or is a single experiment cycle away, and the claim
survives the strongest objection listed against it. Do not put a direction above
70 when its closest prior work was never identified.

## Hard constraints

- **No invented prior work.** Every paper named as closest work is one that was
  actually found and can be cited with venue and year. If a search found
  nothing, report the queries and say nothing was found.
- **No invented numbers.** Do not assert acceptance rates, impact factors,
  effect sizes, or expected gains that were not measured or sourced. Projected
  results are labeled as targets, never as findings.
- **Ideas are grounded in named assets.** Every direction lists the assets it
  consumes and the assets it still needs. A direction requiring an asset the
  user does not have says so in its first three lines.
- **Every direction is falsifiable.** State what result would sink the claim. A
  direction that cannot fail cannot be evaluated and is not research.
- **Feasibility is not negotiated upward.** If the compute, data access, or
  annotation cost does not exist, the score reflects that. Do not fix a low
  feasibility score by assuming a smaller experiment that no longer tests the
  claim.
- **Respect data terms.** Redistribution limits, DUAs, and IRB scope constrain
  which directions are legal to pursue. Flag them before ranking, not after.
- **Say when a direction is taken.** A recommendation that ignores a scooping
  paper costs the user months.
- **No motivational framing.** No transformative, no paradigm shift, no game
  changing. State the claim and what it would change if true.

## Reference files

- `references/idea-operators.md`: the generation catalog, roughly twenty
  operators grouped by the asset they start from, plus the incrementality test
  and the anti-pattern list.
- `references/novelty-check.md`: prior-art search protocol, query construction,
  the delta taxonomy, self-overlap check, and the four recovery moves when a
  direction is already taken.
- `references/scoring-rubric.md`: the six dimensions, level descriptors, cap
  rules, calibration anchors, and the `ideas.json` schema.
- `references/paper-path.md`: gap ledger, headline table design, minimum
  evidence set by contribution type, kill experiments and gates, reviewer
  objection preemption, and threats to validity.
- `references/report-format.md`: required output structure, the idea card
  format, and a worked example.
- `references/modes.md`: how the five modes change the workflow.
- `assets/asset-inventory.md`: the inventory template to fill in step 1.
- `assets/idea-card.md`: the per-direction template.
- `scripts/rank_ideas.py`: weighted scoring, banding, caps, dominance detection,
  asset overlap, and portfolio selection.
- `scripts/plan_timeline.py`: backward schedule from a deadline with phase
  gates, buffer, and slack.
