# Writing ledger entries

The script writes entries in the right shape. This file is about what goes
in them, and the errors `verify` reports when an entry was written by hand.

## Decisions

A decision entry is the only place a rejected alternative is recorded. That
is its whole value: six sessions later, when the same alternative looks
attractive again, the entry says what it would have cost and why it lost.

What a good entry contains:

- **Decision** in one or two sentences, stated so that a reader can tell
  whether a later action complied with it.
- **Alternatives considered**, each with its cost. "Rejected" without a cost
  is not a record of a decision; it is a record of a preference.
- **Rationale** that would convince a skeptical co-author, with numbers
  where numbers exist (and their `R-NNNN`).
- **Consequences**: what changes downstream, and what must now appear in the
  paper (a limitation, a disclosure, a sensitivity analysis).
- **Revisit if**: the observation that would reopen it.

When the owner overrules a recommendation, the entry records the
recommendation, the ruling, and the owner's reason. The record is not the
agent's opinion of what should have happened.

Status is the only field that changes after the entry is written. `open`
means work that depends on it stops. Closing it is a new line in the same
entry; reversing it is a new entry, and the old one becomes `superseded by
D-NNN`.

An entry is never deleted and its number is never reused.

## Progress

One entry per step, written when the step ends, not batched at the end of
the session. The `What` line is past tense and fits in one sentence. The
`Result` line has counts (`1,800 of 1,800 parsed`, `12 gates green`), never
a bare metric; a metric goes in the results log and is cited here by id.

The type is from the closed set, and two of them carry obligations:

- `CORRECTION` names the entry it corrects in `Refs`. The corrected entry is
  not edited.
- `BLOCKED` names the specific missing input (a file, a decision, a
  credential, a number the owner has to supply) and sets `Status: blocked`.
  A blocked step does not deliver a weaker version of itself and call it
  done.

`Next` is the step the next session starts from; `handoff` quotes it. Write
it as an action, not a hope ("run P3 with configs/p3.yaml; the launch
command is in RUNBOOK.md", not "continue P3").

Sequence numbers have no gaps. An entry started and abandoned is completed
with `Status: abandoned` so the sequence stays continuous.

## Results

One entry per reported metric. A run that produces six metrics produces six
entries, so that each number in a table has exactly one row to point at.

The entry refuses to exist without an interval and a method. `n/a` is valid
only for exact counts. The run id is the directory `experiment-ledger`
registered, whose manifest pins config hash, code commit, data, and
environment; a number with no run behind it does not get an entry.

`Comparison` says which pre-declared comparison the entry belongs to, or
`exploratory`. That word follows the number into every table and figure.

When a defect is found in an entry, a new entry is appended with
`Supersedes: R-NNNN`. The old entry stays; anything that cited it is
updated to cite the new one, and that update is a `CORRECTION` in progress.

## What verify catches

| Report | Cause | Fix |
|---|---|---|
| gaps in the sequence | an entry was deleted or a number skipped | restore it, or append an `abandoned` entry with the missing number |
| ids not in increasing order | entries pasted out of order | reorder; the file is chronological |
| refers to D-NNN, which does not exist | a reference to an entry never written, or a typo | write the decision, or fix the id |
| CORRECTION with no entry named | the correction does not say what it corrects | add the id to `Refs` |
| value with no interval / no interval method | a hand-written result skipped the rule | compute the interval with `ml-eval-statistics` and append a superseding entry |
| committed entry edited in place | someone corrected history | revert the edit; append a `CORRECTION` |
| decision edited beyond its Status line | a decision was rewritten | revert; supersede it with a new entry |
| open decisions (note) | not an error; the owner has rulings pending | list them in the hand-off |
