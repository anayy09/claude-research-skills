# Asset inventory

Fill this from what the user supplied. Read the code, papers, and results files
that are available rather than inferring their contents. Mark anything not
supplied as `unknown`, never as a guess: an invented asset produces an
unexecutable plan, and the user will not notice the invention until the
experiment fails.

Give every asset a short id. The ids feed the `assets` field in `ideas.json` and
drive the overlap analysis that finds directions sharing an experiment cycle.

## Data

| id | Dataset | Size and unit | Access terms | Splits | Notes |
|---|---|---|---|---|---|
| | | | own / public / DUA / IRB | patient, site, time | leakage risks, known biases |

Record the unit at which the data clusters (patient, subject, site, session).
Getting this wrong invalidates every downstream statistic, and it is the single
most common source of an inflated result.

## Models and code

| id | What | State | Runs where | Notes |
|---|---|---|---|---|
| | model, endpoint, pipeline, script | prototype / working / published | laptop, cluster, API | reproducibility, config recorded |

## Results already in hand

| id | What was run | Outcome | Reportable | Claimed by a paper |
|---|---|---|---|---|
| | | positive / null / inconclusive / surprising | yes / no, and why | yes / no |

Reportable means the run happened under conditions the paper can describe:
recorded config, no since-fixed bug, no since-changed preprocessing. Runs that
are not reportable do not count toward readiness even when the number looks
right.

### Anomalies

List separately, because these are the highest-yield raw material in the whole
inventory. For each: what was observed, what was expected, what would explain
it, whether anyone else has reported it.

| id | Observation | Expectation it violates | Status |
|---|---|---|---|
| | | | unexplained / partly explained / artifact suspected |

### Unclaimed sunk evidence

Experiments already run that no paper currently uses. This is what makes a
direction cheap without making it incremental.

| id | Experiment | Which claim it could support |
|---|---|---|

## Access and collaborators

| id | What | Who | Constraint |
|---|---|---|---|
| | cohort, annotator time, clinical site, instrument, expert reader | | availability, cost, approval status |

## Compute and budget

| Resource | Amount | Constraint |
|---|---|---|
| GPU hours | | queue, QoS, allocation expiry |
| Storage | | quota, retention |
| API or annotation budget | | per-unit cost |

## Prior work by the user

| Citation | Central claim | Overlap risk with new directions |
|---|---|---|

Needed for the self-overlap check in `references/novelty-check.md`. Two papers
sharing a central claim is a salami-slicing problem regardless of how different
the experiments look.

## Constraints and timeline

| Item | Value | Source |
|---|---|---|
| Deadline | | venue, funding, degree milestone |
| Working time per week | | stated or assumed |
| Target venue or class | | stated or assumed |
| Contribution type wanted | | theory, empirical, systems, dataset, survey plus extension |
| Ethics or DUA constraints | | |

State which of these were assumed rather than supplied. Assumptions that change
the ranking get one line in the report; assumptions that do not can stay here.
