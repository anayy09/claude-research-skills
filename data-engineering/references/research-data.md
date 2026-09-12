# Research data pipelines

The data work in a research repository is a pipeline with three contracts
that a warehouse pipeline does not have: a cohort definition that a reviewer
will reproduce, a feature table whose every value was knowable at prediction
time, and a split that is disjoint at the unit that carries appearance
(patient, subject, site, slide). Each is a check that runs, with a positive
control, not a paragraph in the methods.

## The cohort builder

- One script, one config, one output. `build_cohort.py --config configs/cohort.yaml`
  writes `cohort.parquet` and `cohort_counts.json`, and nothing else touches
  the cohort.
- The config states every inclusion and exclusion criterion with its
  parameter (age floor, window length, minimum record count). Prose in the
  paper is generated from the counts file, never typed.
- Counts at every step (identified, after each exclusion, final) are written
  and become the flow diagram. Counts that do not reconcile are a bug.
- Ids are stable and never re-issued; an internal id maps to the source id in
  a file that does not ship.

## The feature table contract

A feature table has, for every feature column `F`, a companion
`F__available_at` (or a mapping file naming the availability column, or
`constant` for demographics). The availability time is when the value became
known to the system, not when the measurement was taken: a lab drawn at 09:00
and resulted at 09:40 is available at 09:40. The index time per row is the
prediction time.

```bash
python scripts/leakage_guard.py features.parquet --index-time index_time --group patient_id --fold fold --poison
```

The guard fails on any value available after its index time and on any group
shared across folds, and `--poison` runs the positive control: it corrupts
one timestamp and one fold assignment in memory and confirms the guard
catches both. A guard whose positive control passes is reported as broken.
Run it as a gate (`project-ledger` GATES.md) before every training run.

Blocks that are separated by construction (`ACQ_PRE` versus `ACQ_WINDOW`,
pre-triage versus post-triage) are separate tables or separate column
prefixes with the boundary stated in the schema contract, so a join cannot
mix them silently.

## The split

- The unit of the split is the unit that carries appearance: patient, not
  stay; slide, not patch; site, when generalization across sites is the claim.
- The split is written to a file with the split's config hash and is never
  recomputed at training time. Training reads the file.
- The guard's `disjoint` check runs on the final table, not on the split
  file, so a join that duplicates rows across folds is caught.
- When the source provides folds (a benchmark's `strat_fold`), use them and
  say so; when it does not, stratify on the outcome at the group level and
  record the seed.

## The schema contract

A `schema.yaml` per table: column, type, unit, allowed range or categories,
nullable, availability rule, source. `profile_source.py` reports what a table
actually contains; the contract says what it must contain; the difference is
the check. A column that appears in the table and not in the contract fails
the check, because that is how a leaking feature usually arrives.

## What the paper gets

Counts from the cohort builder, the leakage guard's report as a supplementary
statement, the split's unit and seed in Methods, and no number that was not
produced by a script from the tables the checks passed.
