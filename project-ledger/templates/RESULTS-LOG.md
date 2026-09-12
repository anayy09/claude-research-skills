# RESULTS-LOG.md

Results for `{{PROJECT}}`. Append only. One entry per reported metric, not
one per run: a run that produces six metrics produces six entries, so that
each number in the manuscript has exactly one row to point at.

Entry format (the script `project_ledger.py append result` writes it and
refuses a value without an interval and a method):

```
### R-<NNNN> | <run_id>
- Date:
- Phase:
- Metric:
- n:
- Value:
- Interval:
- Interval method:
- Comparison:
- Notes:
- Supersedes:
```

Rules.

- `R-NNNN` is zero-padded, monotonically increasing, never reused. The
  manuscript's trace table cites it.
- `run_id` names the run directory registered by `experiment-ledger`
  (`ledger.py new`), whose manifest pins the config hash, code commit, data,
  and environment. A number with no run behind it does not get an entry.
- `Interval` is two-sided 95 percent unless stated. `n/a` is valid only for
  exact counts.
- `Interval method` names the procedure and its size: `paired-bootstrap(B=2000)`,
  `bca-bootstrap(B=2000)`, `seed-percentile(S=30)`, `wilson`, `exact`.
- `Comparison` names the pre-declared comparison from `PREREGISTRATION.md`
  this entry belongs to, or `exploratory`.
- `Supersedes` names the entry this one replaces, when a defect was found. The
  old entry stays; its number is never reused.
- A number that appears in the paper, a figure, or a caption and has no entry
  here is a defect to fix before anything else.
