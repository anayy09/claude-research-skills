# ml-eval-statistics

> The right statistics for model evaluation: significance, CIs, calibration, selective prediction.

[![Version](https://img.shields.io/badge/version-1.0.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Chooses and computes the correct statistics for evaluating and comparing **your
own** models — as distinct from meta-analysis of published literature. It covers
paired significance tests, clustered and patient-level bootstrap confidence
intervals, calibration (ECE, reliability curves, temperature scaling), selective
prediction and triage metrics (risk-coverage, AURC, coverage at fixed risk), and
multiplicity control across ablation arms. Its standing rule: no accuracy number
ships without an interval.

## When Claude uses it

- "Is the gap between these two models significant?"
- "Which metric should I report?" / "compute a confidence interval"
- "Show calibration" / "is my model well-calibrated?"
- "Evaluate this triage or deferral system"
- Data with repeated measures from the same patient/slide/patch (clustering)
- A reviewer raised a statistics objection
- A results table about to be reported without intervals

## What's inside

```
ml-eval-statistics/
├── SKILL.md
├── references/
│   ├── paired-tests.md            significance for paired model comparisons
│   ├── clustered-resampling.md    patient/cluster-level bootstrap CIs
│   ├── calibration.md             ECE, reliability, temperature scaling
│   ├── selective-prediction.md    risk-coverage, AURC, coverage at fixed risk
│   └── reporting-template.md      how to report results honestly
└── scripts/
    └── eval_stats.py              compute the tests, CIs, and calibration metrics
```

## Scripts

```bash
python ml-eval-statistics/scripts/eval_stats.py --help
```

Computes paired tests, bootstrap confidence intervals (with clustering support),
and calibration metrics from your predictions. Run with `--help` for the
subcommands and expected input format.

## Changelog

- **1.0.0** — Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
