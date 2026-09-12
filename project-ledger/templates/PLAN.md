# PLAN.md

Plan for `{{PROJECT}}`. Created {{DATE}}. This file is edited in place, but
every change of claim, phase, or gate is recorded as a `DECISIONS.md` entry
first and the entry is cited here.

## 1. The claim under test

One paragraph. What the paper will assert if everything goes as planned, in
a form a reviewer could falsify. Name the comparison, the primary endpoint,
and the unit of analysis. The pre-registered version lives in
`PREREGISTRATION.md`; this section may be more current, and says so when it is.

## 2. Phases and gates

| Phase | Deliverable | Gate that closes it | Depends on |
|---|---|---|---|
| P0 | staging, data audit, provenance, ledger wired | P0G1 to P0Gn in `GATES.md` | nothing |
| P1 | the kill experiment: the cheapest test whose negative result ends the project | G1: the pre-declared rule in `PREREGISTRATION.md` | P0 |
| P2 | ... | ... | P1 |

A phase opens when its dependencies have `PHASE-CLOSE` entries in
`PROGRESS.md` and the gate above has a `GATE` entry with a recorded verdict.
An experiment that was planned and never run is not deleted from this table;
its row says it was retired and cites the decision.

## 3. Kill criteria

What result, at which phase, ends the project or reframes it. Written before
the phase runs. When it fires, the reframing is a decision entry and the
original claim stays in the record.

## 4. Outturn table

Filled in as phases close. Pre-declared target, measured value with
interval, outcome. A failed target stays in this table and goes in the
abstract.

| Target | Pre-declared | Measured | Outcome |
|---|---|---|---|

## 5. Statistical protocol

Unit of resampling, interval method, multiplicity family and correction,
noise floor, minimum detectable effect. Decided before the first run;
`ml-eval-statistics` governs the choices. Changes are decisions.

## 6. Anticipated objections

The three to five things a reviewer will say, and which phase answers each.

## 7. Entry state for the next phase

Rewritten at every phase close: what exists, what is open, what the next
session should read first. `project_ledger.py handoff` reads the ledger, not
this section; keep them consistent.
