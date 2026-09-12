# data-engineering

> Build, review, and debug data pipelines, SQL, and schemas, whatever the stack.

[![Version](https://img.shields.io/badge/version-1.0.2-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Helps Claude do the everyday work of moving and shaping tabular data well:
ingestion and extraction, ETL/ELT transformations, SQL that is correct *and*
fast, schema and data-model design, incremental and batch loads, backfills and
migrations, and the validation checks that keep a warehouse trustworthy. It is
deliberately stack-agnostic and adapts to whatever engine and language your
project already uses rather than imposing a new one.

## When Claude uses it

- "Build a pipeline" / "set up ingestion" for a source
- "Write this SQL" or "why is this query slow?"
- "Design a schema" / data-model review
- "Load this data" / "clean this dataset"
- Incremental vs. batch loads, backfills, and migrations
- Adding data-quality and validation checks

## What's inside

```
data-engineering/
├── SKILL.md
├── references/
│   ├── sql-patterns.md            reusable query patterns and anti-patterns
│   ├── incremental-and-history.md incremental loads, SCDs, history tracking
│   ├── validation.md              data-quality checks that catch real bugs
│   ├── references.md              pointers to deeper material
│   └── research-data.md           cohort builder, feature availability, split, schema contract
└── scripts/
    ├── profile_source.py          profile a source dataset before you model it
    └── leakage_guard.py           availability and disjointness checks, with a positive control
```

## Scripts

```bash
python data-engineering/scripts/profile_source.py --help
```

Profiles a source table or file so you understand its shape, nulls, and
distributions before designing the load. Run with `--help` for options.

```bash
python data-engineering/scripts/leakage_guard.py features.parquet \
  --index-time index_time --group patient_id --fold fold --poison
python data-engineering/scripts/leakage_guard.py --self-test
```

Checks a feature table against the two contracts a research pipeline has to
meet: every feature's availability time is at or before the row's index
time (`F__available_at` columns, or a JSON mapping), and no group appears in
more than one fold. `--poison` plants a future-dated value and a shared
group and proves the guard fails on them, so a passing run means something.
Standard library plus `pandas` (and `pyarrow` for parquet).

## Changelog

- **1.1.0**: `references/research-data.md` (the cohort builder, the `F__available_at` feature contract, the split, the schema contract) and `scripts/leakage_guard.py`, which checks feature availability against the index time and group disjointness across folds, with `--poison` as the positive control. SKILL.md gains a research-data section that runs it as a gate before training.
- **1.0.2**: The description names the research-repository work this skill governs (cohort builder, feature pipeline, schema contract, leakage guard); the loading-discipline section.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
