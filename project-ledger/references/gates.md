# Gates

A gate is a claim about the project that a command can check. Its purpose is
to replace "I confirmed that X" with "this command, run from the repository
root, printed this". The ticked box is not the evidence; the EVIDENCE line
is.

## Writing a gate

```
- [ ] P1G3: the leakage guard passes the honest fixture and fails a poisoned positive control
  CHECK: python scripts/checks/check_leakage_guard.py
  EXPECT: LEAKAGE GUARD OK
```

- **The claim** is stated so a stranger could check it, and it is one claim.
  "Data is fine" is not a gate; "no row-level data is tracked by git" is.
- **CHECK** is one command, run from the repository root, deterministic,
  and fast enough to run before every commit. A check that takes an hour
  belongs in the runbook with its own gate that reads the artifact it
  produced.
- **EXPECT** is a string the output must contain, ideally the last line the
  check prints on success. A check that exits 0 and prints nothing
  distinctive can pass by accident; make it print its verdict.
- **Positive control.** A guard that has never failed has never been
  tested. Every guard-type gate (leakage, hygiene, provenance, no-placeholder)
  carries a positive control: the check also runs against a deliberately
  bad input and must fail there. The claim says so.

## What evidence is

`project_ledger.py gates --run --record` writes:

```
  EVIDENCE: shell=powershell cwd=C:\...\repo exit=0; run 2026-09-12; stdout ended 'LEAKAGE GUARD OK'
```

That is evidence: it names the shell, the working directory, the exit code,
the date, and what was printed. A box ticked by hand with no such line is
reverted by the next `verify`-minded reader, and rightly.

## Gate discipline

- A phase does not close while any of its gates is unmet.
- A gate that fails is not re-worded to pass. Either the project is fixed
  or a decision entry records why the gate is retired, and the gate's line
  says `retired, see D-NNN`.
- A pre-registered decision rule (GATE A, GATE B) is a gate too, with the
  rule quoted verbatim in the claim and the check being the script that
  computes the quantity. Its verdict entry in `PROGRESS.md` is of type
  `GATE`, and `ambiguous` opens a decision.
- Run all gates before the hand-off. The hand-off states the count met and
  names any that are not.

## Gates every project should have

| Claim | Why |
|---|---|
| the pre-registration commit predates every run manifest | proves the comparison was declared first |
| the ledger verifies clean (`project_ledger.py verify --git`) | append-only history holds |
| every manuscript number has a results-log entry | no number without a run |
| no credentialed, derived, or row-level data is tracked | data hygiene, with a positive control |
| no placeholder (`[AUTHOR INPUT`, `TODO`, `TBD`) in the built manuscript | no fabricated fill |
| the author block matches `AUTHORS.yaml` | identity comes from the owner |
| the build report has no FAIL (`build_check.py --strict`) | the PDF was looked at |
| the citation audit passes (`audit_report.py`) | no phantom or orphan citations |
