# AGENT.md

Roles for `{{PROJECT}}`. Every role names its inputs, its outputs, and the
condition under which it is finished. A role should be executable without
reading the other roles.

## Operating rules that bind every role

1. **Append, never rewrite.** `PROGRESS.md` and `RESULTS-LOG.md` are
   append-only. Corrections are new entries that name the entry they correct.
2. **No metric without an interval** and the method that produced it.
3. **No new inference before the gate above it has passed.** Gate rules are
   frozen in `PREREGISTRATION.md` and quoted verbatim when adjudicated.
4. **Config first.** Every run reads a config file; the config is hashed into
   the run id (`experiment-ledger`).
5. **Failures are data.** Parse failures, endpoint errors, and truncated
   outputs are counted and reported, never dropped or retried into
   invisibility.
6. **Inputs are immutable once used.** A prompt, config, or split that
   produced a run is never edited; add a new file.
7. **Escalate rather than reinterpret.** When a rule does not cleanly apply,
   open a `DECISIONS.md` entry with status `open` and stop that thread. Do
   not resolve the ambiguity in favour of continuing.
8. **Author identity comes from the owner.** Names, affiliations, emails,
   ORCIDs, funding, and ethics text come from the owner or a project file,
   never from session context, login identity, or memory.
9. **A build is looked at, not trusted** (`build-check`). A gate is run, not
   ticked. A hand-off is generated from the record, not from memory, and is
   never committed.
10. **Internal vocabulary stays internal.** Decision ids, gate names, run
    ids, plan phases, and repository paths do not appear in the manuscript
    (`manuscript-editor`).

## R1. orchestrator

**Purpose.** Owns the phase sequence, enforces gates, and is the only role
that declares a phase complete.

**Inputs.** `PLAN.md`, `DECISIONS.md`, `PROGRESS.md`, `RESULTS-LOG.md`, `GATES.md`.

**Outputs.** `PHASE-OPEN`, `GATE`, and `PHASE-CLOSE` entries. New decisions
when a gate outcome forces a scope change.

**Done when** the phase's gate has a recorded verdict and the next phase's
entry state in `PLAN.md` section 7 is current.

## R2. <role>

**Purpose.**

**Inputs.**

**Outputs.**

**Subtasks.** Each with its done criterion.

**Never.** The action this role is forbidden.
