# data-engineering

> Build, review, and debug data pipelines, SQL, and schemas — stack-agnostic.

[![Version](https://img.shields.io/badge/version-1.0.0-6E56CF)](../CHANGELOG.md)
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
│   └── references.md              pointers to deeper material
└── scripts/
    └── profile_source.py          profile a source dataset before you model it
```

## Scripts

```bash
python data-engineering/scripts/profile_source.py --help
```

Profiles a source table or file so you understand its shape, nulls, and
distributions before designing the load. Run with `--help` for options.

## Changelog

- **1.0.0** — Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
