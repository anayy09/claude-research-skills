# experiment-ledger

> Reproducible ML experiment tracking: config-as-file, hashed manifests, honest baselines.

[![Version](https://img.shields.io/badge/version-1.0.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Sets up and maintains a tracking discipline that makes ML results reproducible
and comparisons honest. The core ideas: every run is defined by a **config file**,
each run produces a **content-hashed manifest**, runs are recorded in an
**append-only registry**, and the **comparison arms are declared before the run**
rather than cherry-picked afterward. The result is that you can always answer
"which config produced this number?" and trust that a reported baseline was not
chosen to flatter the method.

## When Claude uses it

- Designing or running an ablation, sweep, or baseline comparison
- "Which config produced this number?"
- "Why do these two runs disagree?"
- "How should I organize these experiments?" / "what should the baseline be?"
- About to write results into a paper table
- Setting up a new research repo that will run experiments

## What's inside

```
experiment-ledger/
├── SKILL.md
├── assets/
│   └── config_template.yaml        the config-as-file starting point
├── references/
│   ├── manifest-spec.md            what goes in a content-hashed run manifest
│   ├── preregistration.md          declaring comparison arms up front
│   └── reproducibility-checklist.md the pre-publication gate
└── scripts/
    └── ledger.py                   create, hash, and query run manifests
```

## Scripts

```bash
python experiment-ledger/scripts/ledger.py --help
```

Manages the append-only run registry: register a run from its config, compute
its manifest hash, and query which run produced a given result. Run with
`--help` for the subcommands.

## Changelog

- **1.0.0** — Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
