# deep-research

> A 13-agent pipeline for rigorous academic research, from question to cited report.

[![Version](https://img.shields.io/badge/version-2.9.3-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

A domain-agnostic team of 13 specialized agents that carries a research question
all the way to a defensible, cited report. It covers question formulation,
methodology design, systematic literature search, source verification,
cross-source synthesis, risk-of-bias assessment, optional meta-analysis, APA 7.0
report compilation, editorial review, a devil's-advocate challenge, and an ethics
pass. The emphasis throughout is rigor: real sources, disclosed limitations, and
reasoning you can inspect.

## Seven modes

Pick the depth the task needs — see [`references/mode_selection_guide.md`](./references/mode_selection_guide.md).

| Mode | For |
| :--- | :-- |
| **full research** | An end-to-end study with a written, cited report |
| **quick brief** | A fast, sourced answer to a focused question |
| **paper review** | Structured critique of a manuscript or paper |
| **lit-review** | A literature review across a body of work |
| **fact-check** | Verifying specific claims against real sources |
| **Socratic guided** | A dialogue that helps *you* think the problem through |
| **systematic review** | PRISMA-style review, with optional meta-analysis |

## When Claude uses it

- "Run a systematic review / PRISMA on X"
- "Do a literature review on Y"
- "Fact-check these claims"
- "Review this paper"
- "Guide my research" / "help me think through this" (Socratic)
- Anything asking for an evidence-backed answer with citations

## What's inside

```
deep-research/
├── SKILL.md
├── examples/       7 worked runs, one per mode (systematic_review, fact_check_mode,
│                   socratic_guided_research, review_mode, exploratory_research, …)
├── references/     20 on-demand guides: methodology_patterns, mode_selection_guide,
│                   equator_reporting_guidelines, logical_fallacies, ethics_checklist,
│                   irb_decision_tree, source_quality_hierarchy, apa7_style_guide, …
└── templates/      PRISMA report & protocol, preregistration, literature matrix,
                    evidence assessment, research brief
```

## Examples

Every mode ships an end-to-end walkthrough in [`examples/`](./examples) — start
with [`systematic_review.md`](./examples/systematic_review.md) or
[`socratic_guided_research.md`](./examples/socratic_guided_research.md).

## Changelog

- **2.9.3** — Current release. See [`references/changelog.md`](./references/changelog.md) for the skill's detailed history.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
