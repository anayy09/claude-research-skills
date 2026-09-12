# The last ten minutes of a session

The next session will be as good as its starting brief, and a brief written
from memory is wrong in the places that matter: which decisions are open,
what the last step actually produced, what is running. So the brief is
generated from the record, after the record has been brought up to date.

## In order

1. **Log the last step.** Every step of the session has a `PROGRESS.md`
   entry; every number has an `R-NNNN`; every ruling has a `D-NNN`. If the
   session ended mid-step, the entry says so with `Status: blocked` or
   `abandoned` and what the next session inherits.
2. **Update `RUNBOOK.md` state.** What is running, paused, or nothing. The
   resume command beside anything paused.
3. **Update `PLAN.md` section 7** (entry state for the next phase) if the
   phase changed.
4. **Run the checks.** `verify --git`, `gates --run`, and `build_check.py
   --strict` if a PDF was touched. Fix or record what fails.
5. **Commit deliberately.** `git status`; stage the paths the session
   touched; commit with a message that explains the reasoning. Never `git
   add -A`; never commit `.env`, `.claude/`, scratch files, or the brief.
6. **Append the `HANDOFF` entry** with the commit hash.
7. **Generate the brief** with `project_ledger.py handoff` and put its text
   in the conversation for the user to paste into the next session.

## What the generated brief contains

Repository state (branch, commit, clean or not, unpushed commits), ledger
counts, next ids, the last three steps with their results, the recorded next
step, open decisions, unmet gates, the read order, and the standing rules.

## What to add by hand

The generator reads the record; it cannot know:

- a defect the next session inherits that has no decision yet ("the MDE
  function measures tie-break variance; every MDE before 0085 is suspect");
- a ruling the owner must make before work can continue, stated as the
  question with the options and their cost;
- a warning about the environment ("the eval scripts still point at the old
  data root");
- what not to redo ("Phases 0 and 1 are complete and committed on branch
  `p0-p1`; do not repeat them").

Add these as short sections after the generated text. Keep the generated
sections as generated.

## What a brief must never do

- Restate a number without its `R-NNNN`.
- Close a decision the record holds open, or open one the record does not.
- Redefine a rule. The rules are in `AGENT.md`; the brief carries them
  unchanged.
- Be committed. It is a message to a person, generated from files the
  repository already holds. Committing briefs leaves a trail of stale
  summaries that later readers mistake for the record.

## Length

Long enough to be right, no longer. A brief that names the read order and
the open items and quotes the last `Next` line is complete; the record does
the rest.
