# project-ledger

> Decision, progress, results, and gate ledgers for multi-session research projects, plus the session hand-off.

[![Version](https://img.shields.io/badge/version-1.1.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Keeps the operating record of a research project that an agent works on
across many sessions, so that decisions are not silently reversed, numbers in
the paper trace to the run that produced them, gates are run rather than
ticked, and each new session starts from the record instead of from memory.
It gives the agent:

- **Nine documents with a contract each**: PLAN, PREREGISTRATION (frozen at
  a tag), DECISIONS (`D-NNN`, with rejected alternatives and their cost),
  PROGRESS (`NNNN`, typed, gap-free, append-only), RESULTS-LOG (`R-NNNN`,
  one per metric, interval required), GATES (`CHECK`, `EXPECT`, `EVIDENCE`),
  RUNBOOK (stop, resume, do-not-run), AGENT (roles and the ten operating
  rules), SKILL-ROUTING (which skill governs which step). Templates for all.
- **A script that enforces the contract**: allocates ids, appends validated
  entries, refuses a result without an interval, verifies append-only
  history against git, runs gate checks and writes their evidence, prints a
  one-screen state summary, and generates the next session's continuation
  brief from the record.
- **Three modes with a procedure each**: start of a project, start of a
  session (bootstrap: read order, verify, load routed skills), end of a
  session (hand-off entry, runbook state, generated brief that is never
  committed).
- **Long-run discipline** for jobs that outlive a turn: `STOP` files,
  progress files, resume commands recorded beside launch commands, polling
  instead of sleeping, and handing a command to the owner when the machine
  cannot take it.

## When Claude uses it

- "Read the whole directory and build your context before we start"
- "Give me a starter prompt to continue this in a new session"
- "Where did we leave off?" / "what is the progress?"
- "How do I stop this and resume it peacefully?"
- "Record this decision" / "open a decision, this is the owner's call"
- "Did gate G3 pass?"
- Any repository with `docs/DECISIONS.md`, `docs/PROGRESS.md`, or `docs/GATES.md`

Hands off elsewhere: [`experiment-ledger`](../experiment-ledger) for runs,
manifests, and generated results tables (the results log here cites its run
ids), [`ml-eval-statistics`](../ml-eval-statistics) for the intervals the
results log demands, [`hpc-cluster`](../hpc-cluster) for scheduler jobs,
[`manuscript-editor`](../manuscript-editor) to keep the ledger's vocabulary
out of the paper, [`build-check`](../build-check) for the build gate.

## What's inside

```
project-ledger/
├── SKILL.md
├── templates/
│   ├── PLAN.md                 claim, phases and gates, kill criteria, protocol, entry state
│   ├── PREREGISTRATION.md      hypotheses, endpoint, decision rules, power, multiplicity, amendments
│   ├── DECISIONS.md            D-NNN format and rules
│   ├── PROGRESS.md             NNNN format, closed type set, rules
│   ├── RESULTS-LOG.md          R-NNNN format, interval rule, run id rule
│   ├── GATES.md                CHECK / EXPECT / EVIDENCE format with two starter gates
│   ├── RUNBOOK.md              state, environment, long-running work, do-not-run
│   ├── AGENT.md                ten operating rules and the orchestrator role
│   └── SKILL-ROUTING.md        the routing table for this collection
├── references/
│   ├── ledger-entries.md       what a good entry contains; the errors verify catches
│   ├── gates.md                writing checkable claims; positive controls; what evidence is
│   ├── long-runs.md            stop files, progress files, memory limits, handing commands over
│   ├── session-bootstrap.md    the first ten minutes of a session
│   └── session-handoff.md      the last ten minutes; what the generated brief cannot know
└── scripts/
    └── project_ledger.py       init, next, append, verify, state, gates, handoff
```

## Scripts

```bash
python project-ledger/scripts/project_ledger.py init --name my-project
python project-ledger/scripts/project_ledger.py next D
python project-ledger/scripts/project_ledger.py append result --run-id RUN-20260901-E1-01 \
    --metric AUROC --value 0.812 --interval "[0.790, 0.833]" --method "patient-bootstrap(B=2000)"
python project-ledger/scripts/project_ledger.py verify --git      # before every commit
python project-ledger/scripts/project_ledger.py gates --run --record
python project-ledger/scripts/project_ledger.py state
python project-ledger/scripts/project_ledger.py handoff           # paste into the next session; do not commit
python project-ledger/scripts/project_ledger.py --self-test
```

Standard library only. `verify --git` and `handoff` use `git` when it is on
PATH and say so when it is not.

## Changelog

- **1.1.0**: `AUTHORS.yaml` joins the scaffolded documents as the only source of author identity, with a P0 gate that it is filled and a submission gate that runs `build-check` with `--authors`; the loading-discipline section.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
