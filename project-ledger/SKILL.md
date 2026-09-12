---
name: project-ledger
description: >-
  The operating record of a multi-session research project, kept append-only
  and checked mechanically: a decision log with ids and rejected alternatives,
  a typed progress log, a results log that refuses a value without an
  interval, a gate ledger whose checks are run rather than ticked, a runbook
  for long-running jobs with stop and resume, and a continuation brief for
  the next session generated from the record. Use at the start of any
  research project that will span sessions, whenever the user says "read the
  whole directory and build context", "where did we leave off", "give me a
  starter prompt for a new session", "continue from here", "commit
  systematically", "how do I stop and resume this", "what is the progress",
  "open a decision", "record this in the log", or "did the gate pass"; when a
  project has PLAN, DECISIONS, PROGRESS, RESULTS-LOG, GATES, or RUNBOOK
  files; and at the end of every session, to write the hand-off. Composes
  with experiment-ledger, which owns runs and manifests.
summary: "Decision, progress, results, and gate ledgers for multi-session research projects, plus the session hand-off."
version: "1.1.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-09-12"
---

# Project Ledger

A research project run across many agent sessions decays in a predictable
way. A decision gets reversed in session nine because nobody remembers why
it was made in session three. A number in the paper stops matching the run
that produced it. A gate is declared passed without its check being run. A
session starts from a brief written from memory, and the brief is wrong
about what is open. The record that prevents all of this is not hard to
keep; it is hard to keep *consistently*, which is what this skill and its
script are for.

Six documents, three ids, one script, and a rule for every failure above.

## Scope, and what belongs elsewhere

This skill owns the project record: decisions, progress, results log, gates,
runbook, roles, and the session bootstrap and hand-off. It does not:

- Register runs or generate results tables. `experiment-ledger` owns run
  directories, manifests, config hashes, and pre-declared comparisons; the
  results log here points at its run ids.
- Choose statistics. `ml-eval-statistics`.
- Write cluster job scripts. `hpc-cluster`. This skill covers local
  long-running jobs: stop files, progress files, resume commands, and when
  to hand a command to the owner instead of running it.
- Write the paper. `manuscript-writing` and `manuscript-editor`, which
  also strips this skill's vocabulary (decision ids, gate names, run ids)
  out of the manuscript.

## The documents

| File | What it holds | Who edits it |
|---|---|---|
| `PLAN.md` | the claim, phases and gates, kill criteria, statistical protocol, entry state for the next phase | edited in place; every change cites a decision |
| `PREREGISTRATION.md` | hypotheses, primary endpoint, decision rules per gate, sample size, multiplicity | frozen at a tag; amendments appended, dated, cited |
| `DECISIONS.md` | `D-NNN` entries: decision, alternatives with their cost, rationale, consequences, revisit condition, status | append only; only the Status line may change |
| `PROGRESS.md` | `NNNN` entries, one per step, typed; result with interval or pointer; next step | append only, gap-free; corrections are new entries |
| `RESULTS-LOG.md` | `R-NNNN` entries, one per reported metric, with interval and method and the `experiment-ledger` run id | append only; supersessions are new entries |
| `GATES.md` | `- [ ] G1: claim` with `CHECK`, `EXPECT`, `EVIDENCE` | the script ticks a box only after running the check |
| `RUNBOOK.md` | state, environment, launch, pause, resume, and check commands for long work; a do-not-run list | by hand, at every hand-off |
| `AGENT.md` | roles with inputs, outputs, done criteria, and the ten operating rules | by hand |
| `SKILL-ROUTING.md` | which skill governs which step and file | by hand |
| `AUTHORS.yaml` | every author's name, email, affiliation, ORCID, CRediT role; funding, competing interests, ethics text | by the owner only; `build-check` fails a front matter that disagrees with it |

Templates for all of them are in `templates/`; `project_ledger.py init`
scaffolds them without overwriting anything that exists.

## The script

```bash
python scripts/project_ledger.py init --name my-project        # scaffold docs/
python scripts/project_ledger.py next D                         # D-013
python scripts/project_ledger.py append decision --title "..." --decision "..." \
    --alternatives "..." --rationale "..." --consequences "..." [--status open]
python scripts/project_ledger.py append progress --type RUN --role R4 --phase P2 \
    --what "..." --result "..." --artifacts "..." --refs "D-007, R-0042" --status done --next "..."
python scripts/project_ledger.py append result --run-id <experiment-ledger id> \
    --metric AAUC --value 0.4123 --interval "[0.3987, 0.4251]" --method "paired-bootstrap(B=2000)"
python scripts/project_ledger.py verify --git                   # gate for every commit
python scripts/project_ledger.py state                          # one screen, session start
python scripts/project_ledger.py gates --run --record           # run every CHECK, write EVIDENCE
python scripts/project_ledger.py handoff                        # the next session's brief, to stdout
python scripts/project_ledger.py --self-test
```

`append` refuses a result without an interval and a method, a correction
that does not name what it corrects, and a progress type outside the closed
set. `verify --git` fails when a committed progress or results entry was
edited in place, when a decision entry changed beyond its Status line, when
a sequence has a gap, or when a reference names an entry that does not
exist. It is meant to run before every commit; the templates' `P0G2` gate
runs it.

## Modes

### Start of a project

Run `init`, then write `PLAN.md` sections 1 to 3 and `PREREGISTRATION.md`
before any data is analysed, and open `D-001` for the direction (from
`research-ideation` if it was used). Tag the pre-registration commit. Wire
`experiment-ledger` for runs. Add the first gates to `GATES.md` with real
`CHECK` commands. Commit, with `verify --git` clean.

### Start of a session (bootstrap)

Before touching anything:

1. Read, in this order: `PLAN.md`, the decisions the hand-off names (or the
   last five), the last three `PROGRESS.md` entries, `RUNBOOK.md` state.
   The record wins over any brief where they disagree.
2. Run `state` and `verify --git`. A failing verify is the first task.
3. Load the skills `SKILL-ROUTING.md` names for the steps ahead.
4. Append a `PROGRESS.md` entry of type `SETUP` saying what was read and
   what the session will do.

`references/session-bootstrap.md` has the full procedure and what to do when
the record and the working tree disagree.

### During the work

- Every step ends with a `PROGRESS.md` entry. Every number ends with a
  `RESULTS-LOG.md` entry pointing at its run id. Every resolved question
  ends with a `DECISIONS.md` entry that records the rejected alternatives.
- A gate is adjudicated by quoting the rule from `PREREGISTRATION.md` and
  running its `CHECK`; `gates --run --record` writes the evidence. A verdict
  of `ambiguous` opens a decision and stops the phase.
- Escalate rather than reinterpret: an open decision is the owner's to rule
  on. Work that depends on it stops; work that does not continues.
- Long-running jobs follow `references/long-runs.md`: a `STOP` file, a
  progress file, a resume command in `RUNBOOK.md`, polling instead of
  sleeping, and a hand-off of the command to the owner when the machine
  cannot take the job.
- Commits are deliberate: `git status`, stage the paths the step touched,
  never `git add -A`, never a hand-off brief, never `.claude/` or `.env`.
  Commit messages explain the reasoning, like the entries.

### End of a session (hand-off)

1. Append the `HANDOFF` progress entry: what was done, what is open, the
   commit hash if anything was committed.
2. Update `RUNBOOK.md` state and `PLAN.md` section 7.
3. Run `verify --git` and `gates --run` one last time.
4. Run `handoff` and give its output to the user in the conversation. It is
   generated from the record: repository state, open decisions, last steps,
   the recorded next step, next ids, read order, and the standing rules.
   **It is never committed.** A brief is for a person to paste once; the
   repository holds the record it was generated from.

`references/session-handoff.md` covers what to add by hand (a defect the
next session inherits, a decision the owner has to make first) and what a
brief must never do (redefine a rule, restate a number without its entry).

## Rules that hold in every mode

- Append, never rewrite. Corrections are entries.
- No value without an interval and its method.
- The pre-registration is frozen. Anything designed after the data existed
  is exploratory and says so in every table it appears in.
- A gate is met when its check ran and its evidence is written.
- Escalate rather than reinterpret.
- Author identity, affiliation, email, ORCID, funding, and ethics text come
  from the owner or a project file, never from session context.
- Internal vocabulary (ids, gate names, phase labels, run ids, paths) never
  appears in the manuscript, in code identifiers, in commit subjects, or in
  branch names. It lives in `docs/`.
- A step that cannot meet its done criterion writes a `BLOCKED` entry and
  stops. It does not deliver less and call it done.

## Reference files

| File | Read it when |
|---|---|
| `references/ledger-entries.md` | writing a decision, progress, or results entry by hand; what a good entry contains and the errors verify catches |
| `references/gates.md` | writing a gate: claims a command can check, positive controls, what evidence is |
| `references/long-runs.md` | anything that runs longer than a turn: stop files, progress files, memory limits, handing commands to the owner, PowerShell on Windows |
| `references/session-bootstrap.md` | the first ten minutes of a session; reconciling record and tree |
| `references/session-handoff.md` | the last ten minutes; what the generated brief cannot know |

## Loading discipline

Load this skill once per session, before the step it governs, and do not
invoke it again when it is already in context; a second load re-injects the
same text and nothing else. When a repository carries `docs/SKILL-ROUTING.md`
(`project-ledger`), it names the skill for each step and file; follow it, and
record the skill in that step's progress entry. When a brief names several
skills, each is loaded at the step it governs, not all at the start.
