# research-ideation

> Turn existing research assets into ranked, publishable directions with a plan to submission.

[![Version](https://img.shields.io/badge/version-1.0.1-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Acts as a research strategist rather than a brainstorming partner. It reads what
you actually have (papers, code, datasets, half-finished runs, results you
never explained, the experiment that failed), inventories it, and returns a
small set of candidate *papers*, ranked, each one carrying a falsifiable claim
and the shortest honest path from today's state to a submission.

Four things separate this from free-form ideation:

- **Ideas come from operators, not from recall.** A catalog of 23 generation
  moves, each with its trigger condition, the shape of the resulting claim, the
  evidence that makes it publishable, and the objection a reviewer raises first.
  Eight to fifteen raw candidates get generated before anything is filtered.
- **Novelty is verified, not asserted.** Every surviving direction names its two
  or three closest works with venue and year. A direction whose closest work was
  never identified is capped below 70 and labelled provisional; a direction that
  turns out to be taken is reported as taken, with the paper that takes it.
- **Feasibility is a separate axis and is never negotiated upward.** If the
  compute, data access, or annotation budget does not exist, the score says so.
  It will not rescue a low score by shrinking the experiment until it no longer
  tests the claim.
- **Every direction ships a plan.** Gap ledger, the headline results table
  designed *before* any run happens, the minimum evidence set for that
  contribution type, a kill experiment with a written decision rule, predicted
  reviewer objections with answers, and a backward schedule against the real
  deadline.

The report ends with what was deliberately *not* recommended and why, usually
the most useful section for someone who has been circling the same three ideas
for a month.

## When Claude uses it

- "What should I work on next?" / "where do I take this project?"
- "Can I get a paper out of these results?" / "is this novel enough to publish?"
- "This experiment failed. Is there anything salvageable?"
- "Attack this idea and tell me where it breaks."
- "Plan my thesis chapters" / "what's the next paper before the deadline?"
- Sharing a repo, a results table, or a set of open questions and asking for direction

## Five modes

| Situation | Mode |
| :-------- | :--- |
| Existing project or results that need to become a paper | `transition` (default) |
| Assets and interests, but no project underway | `greenfield` |
| Experiments that failed, saturated, or produced a null | `salvage` |
| Thesis, grant, or multi-paper agenda across a year or more | `portfolio` |
| You already have an idea and want it stress-tested | `stress-test` |

## Scoring

Six weighted dimensions, with cap rules so an exciting direction cannot outrank
a workable one on enthusiasm.

| Dimension | Weight | Question it answers |
| :-------- | :----: | :------------------ |
| `novelty` | 25 | How large is the verified delta over the closest found work? |
| `significance` | 20 | Who changes what they do if the claim holds? |
| `feasibility` | 20 | Can this be executed with the assets, compute, and time that exist? |
| `readiness` | 15 | How much of the required evidence already exists? |
| `venue_fit` | 10 | Does it match the target venue's scope and evidence bar? |
| `durability` | 10 | Will it still be worth citing in two years? |

| Composite | Band |
| :-------: | :--- |
| 80-100 | Lead candidate: real delta, evidence largely in hand, finishable in the window |
| 65-79 | Strong contender: one open dependency, usually an experiment or a data access |
| 50-64 | Viable, gap to close: publishable, but needs a sharper claim or comparison |
| 35-49 | Needs reframing: the asset is interesting, the claim is not yet a paper |
| < 35 | Not a paper yet: said plainly, with what would change it |

Calibration matters more than the scale: a competent, well-supported incremental
extension of your own prior work is a 60, not an 85.

## What's inside

```
research-ideation/
├── SKILL.md
├── references/
│   ├── idea-operators.md      23 generation operators, incrementality test, anti-patterns
│   ├── novelty-check.md       prior-art protocol, delta taxonomy, self-overlap, recovery moves
│   ├── scoring-rubric.md      six dimensions, caps, calibration anchors, ideas.json schema
│   ├── paper-path.md          gap ledger, evidence sets, kill experiments, objections, validity
│   ├── report-format.md       required output structure, idea card format, worked example
│   └── modes.md               transition, greenfield, salvage, portfolio, stress-test
├── assets/
│   ├── asset-inventory.md     inventory template, filled before anything is generated
│   └── idea-card.md           per-direction template
└── scripts/
    ├── rank_ideas.py          weighted scoring, caps, dominance, asset overlap, portfolio
    └── plan_timeline.py       backward schedule from a deadline, with phase gates and slack
```

## Scripts

Standard library only. No dependencies, no network, no filesystem writes.

```bash
# dimensions, weights, cap rules, and the ideas.json schema
python research-ideation/scripts/rank_ideas.py --rubric

# rank a set of directions and select a portfolio
python research-ideation/scripts/rank_ideas.py --ideas ideas.json --available-months 4
python research-ideation/scripts/rank_ideas.py --ideas ideas.json --json

# phase profiles: analysis, dataset, empirical, method, negative, survey
python research-ideation/scripts/plan_timeline.py --profiles

# backward schedule against a real deadline
python research-ideation/scripts/plan_timeline.py --deadline 2026-11-15 --effort-months 3 \
    --profile method --buffer 0.2 --start 2026-08-05
```

`plan_timeline.py` reports negative slack rather than quietly compressing every
phase, and marks which phases are the honest place to take time from.

## Hands off to

[`evidence-synthesis`](../evidence-synthesis) and
[`investigating-sources`](../investigating-sources) when a direction needs a full
evidence base rather than a targeted prior-art check,
[`experiment-ledger`](../experiment-ledger) for run tracking once a direction is
chosen, [`ml-eval-statistics`](../ml-eval-statistics) for the tests and intervals
the plan specifies, [`hpc-cluster`](../hpc-cluster) for execution,
[`journal-advisor`](../journal-advisor) for venue choice,
[`research-paper-writing`](../research-paper-writing) for drafting,
[`submission-reviewer`](../submission-reviewer) before you send it out, and
[`submission-formatter`](../submission-formatter) to put it in the venue's
template.

## Changelog

- **1.0.1**: Point to `submission-formatter` for the venue template step.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
