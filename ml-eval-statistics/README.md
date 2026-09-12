# ml-eval-statistics

> The right statistics for model evaluation: significance, CIs, calibration, selective prediction.

[![Version](https://img.shields.io/badge/version-1.0.2-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Chooses and computes the correct statistics for evaluating and comparing **your
own** models, as distinct from meta-analysis of published literature. It covers
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
    └── eval_stats.py              tests, CIs, calibration, selective prediction, MDE, self-test
```

## Scripts

```bash
python ml-eval-statistics/scripts/eval_stats.py --help
```

Computes paired tests, bootstrap confidence intervals (with clustering support),
calibration metrics, selective-prediction metrics, and the minimum detectable
effect from your predictions. Run with `--help` for the subcommands and
expected input format.

```bash
# minimum detectable effect for a paired comparison at this sample size
python ml-eval-statistics/scripts/eval_stats.py mde --csv preds.csv --label y \
  --a p_base --b p_new --group patient_id --metric auroc --power 0.8
# the estimators against synthetic data
python ml-eval-statistics/scripts/eval_stats.py --self-test
```

`mde` takes its standard error from the paired difference between two arms
under one shared group resample. An arm bootstrapped against itself with a
shared index has its sampling variance cancel exactly and reports tie-break
noise instead; that estimator once sat in a project for a week. Use the
script.

## Changelog

- **1.1.0**: `mde` subcommand: the minimum detectable effect for a paired comparison, standard error from the paired difference under one shared resample, with a marginal fallback when only one arm is given. `--self-test` checks the estimators on synthetic data (interval brackets the point, identical arms give zero, a real gap excludes zero, MDE equals the z-sum times the SE, McNemar, ECE, Holm, the normal quantile).
- **1.0.2**: The description insists on `eval_stats.py` for every interval, paired test, and minimum detectable effect rather than hand-written bootstrap code; the loading-discipline section.
- **1.0.1**: Hand off to `manuscript-figures` for drawing reliability diagrams,
  risk-coverage curves, and interval plots once the numbers exist.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
