# The first ten minutes of a session

The brief that opened the session was written from the record at the end of
the last one. It is a summary. The record is the source, and the first job
is to read enough of the record to know whether the brief is still true.

## Read, in this order

1. `docs/PLAN.md`: the claim, the phase table, section 7 (entry state).
2. `docs/DECISIONS.md`: the entries the brief names, in full, then the
   open-items list. Do not skim decisions; the reason a choice was made is
   the thing a session most often gets wrong.
3. `docs/PROGRESS.md`: the last three entries, and the `Next` line of the
   last one.
4. `docs/RUNBOOK.md`: state, environment, do-not-run.
5. `docs/SKILL-ROUTING.md`: which skills to load for the steps ahead. Load
   each one before the step it governs, and say so in that step's progress
   entry.

Then run:

```bash
python <skill>/scripts/project_ledger.py state
python <skill>/scripts/project_ledger.py verify --git
git status
```

## Reconcile before acting

Disagreements are common and each has a rule:

| Brief says | Record says | Do |
|---|---|---|
| a decision is closed | its status is `open` | the record wins; the decision is open |
| a step is done | no `PROGRESS.md` entry | it is not done; find the artifact, then append the entry, or redo the step |
| next step is X | last `Next` line is Y | ask which, or take Y and say so in the first progress entry |
| the tree is clean | `git status` shows changes | inspect them; do not commit or discard until you know whose they are |
| a number | no `R-NNNN` | the number does not exist yet |
| nothing running | `progress.json` is recent | something is running; read the runbook before touching it |

`verify --git` failing is the first task of the session, before any planned
work, because every later entry inherits the defect.

## Then

Append a `SETUP` progress entry: what was read, what state was found, what
the session will do, which skills are loaded. It takes one minute and it is
what the next session's brief will be generated from.

## Do not

- Re-derive context from the codebase when the record exists. Reading
  every file "to build context" costs an hour and produces a picture the
  record already holds; read the record, then the files the step needs.
- Rewrite a document to match your understanding. If a document is stale,
  say so in a progress entry and, if it is a plan or runbook, update it
  citing the decision that changed it.
- Start a long job before the runbook has its launch and resume commands.
