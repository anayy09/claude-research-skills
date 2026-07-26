---
name: data-engineering
description: >-
  Use when building, reviewing, or debugging data pipelines and the code around
  them: ingestion and extraction, ETL/ELT transformations, SQL queries and
  optimization, schema and data-model design, incremental and batch loads,
  backfills and migrations, data quality and validation checks, and warehouse or
  lakehouse work. Triggers include "build a pipeline", "write/optimize this SQL",
  "design a schema", "load this data", "clean this dataset", "why is this query
  slow", "set up ingestion", or any request whose deliverable is moving,
  reshaping, validating, or storing tabular data. Stack-agnostic; adapts to
  whatever engine and language the project already uses.
summary: "Build, review, and debug data pipelines, SQL, and schemas — stack-agnostic."
version: "1.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-07-25"
---

# Data Engineering

Work like an engineer who owns the pipeline in production and will be paged when
it breaks. The goal is not code that runs once on the sample; it is code that
reruns tomorrow on dirtier, larger, later-arriving data without silent
corruption. Optimize for correctness and reproducibility first, throughput
second, cleverness never.

## Operating principles

- **Idempotent by default.** Rerunning a step on the same input must produce the
  same output and must not double-write. Prefer overwrite-by-partition, upsert
  on a stable key, or delete-and-insert within a bounded window over blind
  append. State the write semantics you chose.
- **Deterministic transforms.** No dependence on wall-clock time, row order, or
  ambient locale unless it is pinned explicitly. Sort keys, fixed time zones,
  fixed decimal precision.
- **Incremental first.** Assume the source grows. Design for processing a
  window (new or changed rows) and make full reprocessing a special case, not
  the only case. Keep a high-water mark or change marker.
- **Contracts at the boundary.** Validate schema, types, nullability, and key
  uniqueness where data enters your control. Reject or quarantine bad input
  loudly; do not let it flow downstream and surface as a confusing metric later.
- **Fail early and visibly.** A pipeline that stops with a clear error beats one
  that produces plausible wrong numbers. Assert row counts, key uniqueness, and
  referential integrity at stage boundaries.
- **Provenance.** Every output should be traceable to its source, transform
  version, and run. Preserve source identifiers; do not discard them in the
  first join.

## Workflow

Follow this order unless the task is a narrow one-off:

1. **Profile the source before writing transforms.** Row count, column types,
   null rates, cardinality of candidate keys, duplicate rate, value ranges,
   encoding, and date/number formats. Cheap profiling here prevents expensive
   wrong assumptions later. Run `scripts/profile_source.py <path> [--key col]`
   to get this in one pass (reads CSV/Parquet/JSON, uses DuckDB when available
   and falls back to pandas or stdlib) instead of hand-writing profiling code.
2. **Fix the contract.** Decide the target schema, the grain (one row = what?),
   the primary key, and which columns are required. Write the grain down; most
   pipeline bugs are grain bugs.
3. **Extract** with the source's natural pagination or change mechanism. Pull
   only what the window needs.
4. **Transform** in the engine best suited to the data size (see below). Keep
   transforms as SQL or declarative code where possible; reserve procedural code
   for logic SQL handles poorly.
5. **Validate** against the contract: schema match, key uniqueness, row-count
   sanity, null and range checks on critical columns.
6. **Load** with explicit write semantics (upsert / overwrite-partition /
   append-once) and a transaction or atomic swap so readers never see a
   half-written table.
7. **Orchestrate and observe.** Make dependencies explicit, make each step
   independently rerunnable, and emit row counts and durations per run.

## Choosing the engine

Pick the smallest tool that fits the data, not the most powerful.

- **Fits in memory (roughly < 1 GB):** a dataframe library is fine; do not spin
  up infrastructure.
- **Larger than memory but single-node (roughly 1 GB to low TB):** an embedded
  columnar SQL engine reading Parquet directly is usually faster and simpler
  than a cluster, and avoids a network hop.
- **Genuinely distributed scale or existing cluster:** use the cluster engine
  the project already runs; do not introduce a second one for one job.

Push work down to where the data lives. Filter and aggregate in the database or
file scan before pulling rows into application memory. The fastest transfer is
the row you never move.

## SQL practices

- Be explicit: name columns instead of `SELECT *` in anything persisted, qualify
  columns in joins, and alias clearly.
- Filter and project early; join on typed, indexed keys; avoid functions on join
  or filter columns that defeat index or zone-map use.
- Use window functions and `QUALIFY`/subquery filtering instead of self-joins
  for ranking and dedup.
- Make every join's cardinality intentional. After a join, assert the row count
  did not unexpectedly multiply; fan-out from a non-unique key is a top cause of
  inflated aggregates.
- Handle NULLs deliberately in aggregates, joins, and `NOT IN` (which is a
  classic NULL trap; prefer `NOT EXISTS`).
- Read the query plan before optimizing. Fix the actual bottleneck (a spill, a
  full scan, a bad join order), not a guessed one.

For copyable, dialect-aware versions of these (upsert/merge, partition
overwrite, `QUALIFY` dedup, cardinality assertion, NULL-safe anti-join), see
`references/sql-patterns.md`.

## Schema and modeling

- Define grain and key first. A table without a stated grain and a unique key is
  a bug waiting to happen.
- Normalize the source of truth; denormalize deliberately for read performance
  in serving or analytical layers, and document why.
- Use the narrowest correct type. Store timestamps as timestamps with an
  explicit time zone, money as fixed-precision decimal, categoricals as stable
  codes plus a lookup.
- For history, choose the tracking strategy on purpose: overwrite (no history),
  append event log, or slowly changing dimension with valid-from/valid-to and a
  current flag. Late-arriving and out-of-order records are the hard part; design
  for them.
- Make migrations forward-only and reversible in principle: additive changes
  first, backfill, then cut over, then remove the old path.

## Data quality and validation

Treat checks as code that ships with the pipeline, not a manual afterthought.

- **Schema checks:** column presence, types, nullability.
- **Key checks:** primary key uniqueness, no orphaned foreign keys.
- **Volume checks:** row count within an expected band; flag zero rows and
  sudden 10x swings.
- **Distribution checks:** null rate, min/max, and category domains on critical
  columns, compared against recent runs.
- **Reconciliation:** totals tie back to the source or to a control number.

Decide up front whether a failed check blocks the load (hard gate) or routes bad
rows to a quarantine table (soft gate). Prefer hard gates on keys and volume,
soft gates on individual dirty rows.

`references/validation.md` has the five check families as ready SQL and a small
Python assertion helper, plus concrete hard-gate and quarantine implementations.

## Pipeline design patterns

- **Incremental load:** track a high-water mark (max updated_at or a change
  sequence); process rows beyond it; advance the mark only after a successful,
  validated load.
- **Idempotent write:** upsert on key, or overwrite the affected partitions, so
  a retry cannot duplicate.
- **Backfill:** parameterize the run by date/window so a historical range reuses
  the same code path as the daily run.
- **Late and out-of-order data:** reprocess a trailing window (for example the
  last N days) on every run so corrections land without a full rebuild.
- **Dead-letter / quarantine:** never drop rejected rows silently; write them
  with the rejection reason so they can be inspected and replayed.

`references/incremental-and-history.md` has worked code for high-water-mark
extraction, trailing-window reprocessing, backfill on the same code path, and
SCD Type 2 (including the late/out-of-order cases that make these hard).

## Storage and file formats

- Prefer columnar formats (Parquet and friends) for analytical data: better
  compression, column pruning, and predicate pushdown than row formats or CSV.
- Partition by the column you filter on most (often a date), but avoid tiny
  files; target reasonably sized files per partition rather than thousands of
  small ones.
- Keep schema with the data (formats that embed it) so downstream readers do not
  guess types. CSV is an interchange format, not a storage format.

## Performance, in order

1. Do less work: filter earlier, read fewer columns, prune partitions.
2. Reduce data movement: push compute to the data, avoid round trips.
3. Fix the plan: address scans, spills, and bad join orders.
4. Only then tune parallelism, memory, and hardware.

Measure before and after. An optimization without a before/after number is a
guess.

## Anti-patterns to refuse or flag

- Blind `INSERT` on rerun (creates duplicates).
- Loading a large file wholesale into memory when the engine could stream or
  scan it.
- `SELECT *` into a persisted table.
- Silent row drops during cleaning with no count of what was removed and why.
- Transforms that depend on input row order.
- Overwriting a target table non-atomically so a failed run leaves it empty or
  partial.
- Premature framework abstraction over a pipeline that runs in one place.

## Output conventions

When producing pipeline code:

- State the assumed grain, key, and write semantics in a comment at the top.
- Make it runnable as-is: real imports, parameterized paths and windows, no
  pseudo-code gaps.
- Comment the *why* (the non-obvious decision), not the *what* the code already
  says.
- Include the validation checks inline or as a clearly separated step, not as a
  "left as an exercise" note.
- Prefer straightforward, readable structure over layers of abstraction the
  current scope does not need.
- When a choice depends on context you do not have (engine, scale, existing
  conventions), state the assumption you made and proceed, rather than stalling.

## Bundled resources

Load these as needed rather than reproducing their contents from memory.

- `scripts/profile_source.py` - run at workflow step 1 to profile a source
  (row count, types, null rates, candidate-key uniqueness, duplicate rate,
  ranges, samples). Read-only; auto-selects DuckDB, pandas, or a stdlib CSV
  reader. `--format json` for a structured profile you can diff across runs.
- `references/sql-patterns.md` - dialect-aware idioms: idempotent upsert/merge,
  partition overwrite, dedup, cardinality assertion, NULL-safe anti-join.
- `references/validation.md` - the five check families in SQL and Python, with
  hard-gate and quarantine implementations.
- `references/incremental-and-history.md` - high-water-mark loads, backfill,
  late/out-of-order handling, and SCD Type 2.
- `references/references.md` - the pre-flight checklist to run before declaring
  a pipeline done, plus canonical documentation sources.
