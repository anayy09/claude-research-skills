# submission-reviewer

> Peer-review a paper or patent against a weighted rubric: score out of 100, ranked fixes, projected score.

[![Version](https://img.shields.io/badge/version-1.0.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Reviews a research paper or a patent submission the way a good senior reviewer
does: reads the full text, builds a claim map, checks novelty against prior art
that was actually searched for, scores each rubric dimension, and returns a
score out of 100 with a band, ranked fixes, and a projected score if those fixes
land.

Two rubrics, picked automatically from the artifact:

| Submission | Dimensions (weight) |
| :--------- | :------------------ |
| **Paper**: journal, conference, preprint, thesis chapter, technical report | novelty (25) · rigor (25) · readiness (20) · application (15) · integrity (15) |
| **Patent**: disclosure, provisional or complete specification, claim set | novelty (25) · inventive step (20) · claims (20) · enablement (15) · application (12) · eligibility (8) |

Three things keep the number honest:

- **Cap rules.** A blocking flaw (train/test leakage, a claim anticipated by a
  found reference, a missing required baseline) caps the total regardless of
  the rubric arithmetic, and the cap reason is printed alongside the score.
- **Verified novelty only.** Novelty is scored against prior art that was
  actually found and can be cited with venue and year. No search tool available
  means the dimension is scored on internal evidence and flagged low-confidence,
  never padded with a plausible-sounding citation.
- **Partial submissions score partially.** A dimension that cannot be assessed
  from what was supplied is marked `na` and the review reports reduced
  confidence, rather than inventing a methods section.

The tone contract is collegial and the numbers are not: every problem carries a
repair path, priority, and effort estimate, and a blocking flaw goes first
rather than being buried in the minor comments.

## When Claude uses it

- "Review this paper" / "score this manuscript" / "what would a reviewer say?"
- "Is this novel enough?" / "is this publishable?" / "is this patentable?"
- "Pre-submission check before I send this out"
- "Give me a second opinion on this invention disclosure"
- Screening someone else's submission for a lab, journal, or review committee

Hands off afterwards: [`journal-advisor`](../journal-advisor) for venue choice,
[`research-paper-writing`](../research-paper-writing) for drafting and rebuttals,
[`prose-naturalizer`](../prose-naturalizer) for de-AI-ing text, and
[`ml-eval-statistics`](../ml-eval-statistics) when a fix needs a significance
test or a confidence interval. It does not give legal advice; patent review
here is a technical appraisal, and the report says so once.

## What's inside

```
submission-reviewer/
├── SKILL.md
├── references/
│   ├── rubric-paper.md            five paper dimensions, level descriptors, cap rules
│   ├── rubric-patent.md           six patent dimensions, claim reading, anticipation vs obviousness
│   ├── authenticity-checks.md     integrity checklist and the severity phrasing ladder
│   └── report-format.md           required output structure and a worked example
└── scripts/
    └── score.py                   deterministic weighted scoring, banding, caps, projections
```

## Scripts

`scripts/score.py` is standard library only: no dependencies, no network, no
filesystem writes.

```bash
# show a rubric's dimensions, weights, bands, and cap rules
python submission-reviewer/scripts/score.py --rubric --type paper

# score a paper
python submission-reviewer/scripts/score.py --type paper \
  --scores novelty=17 rigor=15 application=11 integrity=12 readiness=14

# score a patent
python submission-reviewer/scripts/score.py --type patent \
  --scores novelty=16 inventive_step=12 claims=11 enablement=10 application=8 eligibility=6

# a dimension that can't be assessed from what was supplied
python submission-reviewer/scripts/score.py --type paper \
  --scores novelty=18 rigor=na application=12 integrity=11 readiness=13

# a blocking flaw caps the total, and the reason travels with the score
python submission-reviewer/scripts/score.py --type paper \
  --scores novelty=20 rigor=9 application=13 integrity=8 readiness=15 \
  --cap-total 55 --cap-reason "test set overlaps training set"
```

Add `--projected novelty=20 rigor=20` for the after-fixes score, or `--json` for
machine-readable output.

## Score bands

| Score | Band | What it means |
| :---: | :--- | :------------ |
| 85–100 | Strong | Real contribution, complete evidence, competitive at a selective venue. |
| 70–84 | Solid, revise first | Genuine contribution with specific gaps; submittable after targeted work. |
| 55–69 | Promising, gap to close | Core is there, one substantive element missing. |
| 40–54 | Early | Needs new experiments, a repositioned claim, or a rebuilt claim set. |
| < 40 | Not yet a submission | Identify the salvageable core and the shortest path to it. |

Calibration matters more than the scale: most complete, competent first drafts
land between 58 and 75, and a well-executed but incremental paper is a 70, not
an 85.

## Changelog

- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
