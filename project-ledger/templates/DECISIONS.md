# DECISIONS.md

Running decision log for `{{PROJECT}}`. Append only. To reverse a decision,
add a new entry that supersedes the old one and change the old entry's status
to `superseded by D-NNN`. Never delete an entry; never edit one beyond its
Status line.

An entry records a choice and the choices it rejected, with the cost of each.
This includes decisions the owner made against a recommendation: the
recommendation, the ruling, and the reason both go in.

Status values: `open` (needs a ruling; work that depends on it stops),
`closed`, `superseded by D-NNN`. An open entry is not a licence to proceed
past the step that depends on it.

Entry format (the script `project_ledger.py append decision` writes it):

```
## D-NNN. <short title>

- **Date:** YYYY-MM-DD
- **Status:** open | closed | superseded by D-NNN
- **Decision:** what was decided, in one or two sentences
- **Alternatives considered:** each rejected option and what it would have cost
- **Rationale:** why this one
- **Consequences:** what changes downstream; what must now appear in the paper
- **Revisit if:** the observation that would reopen it
```

---
