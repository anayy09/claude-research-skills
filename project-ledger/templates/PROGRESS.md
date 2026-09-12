# PROGRESS.md

Append-only step log for `{{PROJECT}}`. Newest entries at the bottom. One
entry per step. Never edit an existing entry; to correct one, append an entry
of type `CORRECTION` whose Refs field names the entry it corrects.

Entry format (the script `project_ledger.py append progress` writes it):

```
### <SEQ> | <ISO-8601 UTC> | <TYPE> | <ROLE> | <PHASE>
- What: one sentence, past tense
- Result: what came out, with counts, or "n/a"
- Artifacts: paths created or modified, or "none"
- Refs: run ids, D-NNN, R-NNNN, other SEQs, or "none"
- Status: done | blocked | abandoned
- Next: the immediate next step, or "awaiting <gate or decision>"
```

Rules.

- `SEQ` is zero-padded, monotonically increasing, never reused, never
  skipped. An entry abandoned mid-write is completed with `Status: abandoned`.
- `TYPE` is one of: `PHASE-OPEN`, `PHASE-CLOSE`, `SETUP`, `RUN`, `ANALYSIS`,
  `GATE`, `DECISION`, `LIT`, `WRITE`, `BUILD`, `CORRECTION`, `BLOCKED`,
  `HANDOFF`.
- `ROLE` is a role from `AGENT.md`, or `human`.
- `PHASE` is a phase from `PLAN.md`, or `meta`.
- `Result` never carries a bare point estimate. A number here has an interval
  or points at the `RESULTS-LOG.md` entry that does.
- A step that cannot meet its done criterion appends a `BLOCKED` entry naming
  the missing input, and stops. It does not substitute a weaker deliverable.
- Every session ends with a `HANDOFF` entry: what was done, what is open, the
  commit hash if anything was committed.
