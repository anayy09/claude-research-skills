# References

## In this skill

- `scripts/profile_source.py` - profile a source before writing transforms.
- `sql-patterns.md` - idempotent writes, dedup, cardinality, NULL-safe joins.
- `validation.md` - the five check families and hard/soft gates in code.
- `incremental-and-history.md` - incremental loads, backfill, SCD Type 2.
- Pre-flight checklist and canonical docs below.

## Pre-flight checklist

Run through this before declaring a pipeline done.

**Contract**
- [ ] Grain stated (one row = what?)
- [ ] Primary key chosen and asserted unique
- [ ] Required (non-null) columns identified
- [ ] Types pinned, including time zone and decimal precision

**Correctness**
- [ ] Rerun produces identical output (idempotent)
- [ ] No dependence on row order or wall-clock time
- [ ] Join cardinality checked; no accidental fan-out
- [ ] NULL handling deliberate in joins, aggregates, and NOT IN / NOT EXISTS

**Incrementality**
- [ ] High-water mark or change marker tracked
- [ ] Mark advances only after a validated load
- [ ] Trailing window reprocessed for late/corrected rows
- [ ] Backfill uses the same code path as the routine run

**Validation**
- [ ] Schema, key-uniqueness, and volume checks in place
- [ ] Hard vs soft gate decided per check
- [ ] Rejected rows quarantined with a reason, not dropped silently

**Load**
- [ ] Write semantics explicit (upsert / overwrite-partition / append-once)
- [ ] Atomic swap or transaction so readers never see a partial table

**Observability**
- [ ] Row counts and durations emitted per run
- [ ] Failures stop the run with a clear message
- [ ] Output traceable to source, transform version, and run

## Canonical documentation

These are stable primary sources. Verify against the current version for your
engine rather than trusting memory.

- Parquet format: https://parquet.apache.org/docs/
- Apache Arrow: https://arrow.apache.org/docs/
- DuckDB (embedded columnar SQL): https://duckdb.org/docs/
- dbt best practices (transformation, testing, modeling): https://docs.getdbt.com/best-practices
- Great Expectations (data validation): https://docs.greatexpectations.io/
- OpenLineage (lineage and provenance): https://openlineage.io/docs/
- Anthropic Agent Skills standard: https://www.anthropic.com/news/skills

## Concepts worth reading up on

- Dimensional modeling and slowly changing dimensions (Kimball).
- Data contracts as an enforced boundary between producers and consumers.
- Idempotent and exactly-once-effect writes in batch pipelines.
- Predicate pushdown and partition pruning in columnar scans.
- Change-data-capture patterns for incremental extraction.
