# manuscript-editor

> Keeps manuscripts coherent through revision: checklist, right content in the right document, minimal changes, cuts to a budget, the letter.

[![Version](https://img.shields.io/badge/version-1.2.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

A paper that has been through several review rounds is often worse written
than the first submission, even though every individual change was
justified: reviewer explanations leak into the text ("as suggested by
Reviewer 2, we have now added"), points get restated where the reviewer
looked instead of where they belong, every comment becomes a paragraph, and
the result reads as a record of peer review rather than as a research
article.

This skill is the editorial discipline that prevents that. It gives the
agent:

- **A revision checklist first.** `make_checklist.py` turns the reviewer and
  editor files, and the fix list of a `submission-reviewer` report, into one
  table of atomic items with stable ids, the affected section or table or
  experiment, the change type, the evidence needed, dependencies, a projected
  time, and a status carried forward from the last round. The round stops
  for approval there and nowhere else.
- **A paragraph-level editorial read** as the actual check: three questions
  per paragraph, three running indexes (claims, justifications, summaries),
  an outline test per section, a citation job test, and an editorial report
  with a prioritized cut list delivered before any cut is made.
- **Six families of non-manuscript text**, five of which never mention a
  reviewer: review-process narration, editorial self-commentary, protocol
  refrain, reader management, internal workflow artifacts, and pre-emptive
  objection sections.
- **Three containers with a hard boundary.** Manuscript, response to
  reviewers, and a revision ledger, with a leak catalog of before/after
  pairs showing what moves where.
- **A revision-round workflow.** Audit, triage into atomic items with a
  change type, locate the single home for each point before writing, make
  the smallest complete change, record it, then a whole-manuscript coherence
  pass and the package.
- **A budget mode.** A page cap or word guidance to meet: measure with
  `build-check`, apply cut classes in order of yield per unit of damage
  (supplement moves, reference diet, surplus summaries, the six families,
  duplicated justifications, limitations that re-explain methods, captions
  that repeat the body), re-measure after each, and hand evidence-bearing
  cuts to the owner.
- **The letter, built and checked.** `build_letter.py` verifies every
  section, table, and figure number the letter cites against the
  manuscript's `.aux`, every quoted passage against the manuscript text, and
  the absence of reviewer narration in the manuscript, then builds the PDF.
- **Word manuscripts.** What can be scripted (audit, extraction, the red
  `[AUTHOR ACTION]` markers via `docx_markers.py`, the letter) and what
  cannot (tracked changes, which Word's Compare produces from the submitted
  and revised files).
- **Integrity rules.** No invented evidence, references, or justifications;
  author identity only from `AUTHORS.yaml` or the owner; `[AUTHOR INPUT: ...]`
  where the author must decide.
- **Venue conventions**, general principles and then the Nature, Science,
  Cell, medical, Elsevier, IEEE, ACM, ML conference, and Springer/PLOS
  families.
- **A stdlib-only audit script** (`audit_manuscript.py`) for `.md`, `.tex`,
  `.docx`, `.txt`.

## When Claude uses it

- "I have received the first-round decision; here are the editor and two reviewers"
- "Create a consolidated reviewer checklist before we change anything"
- "External Review 3: score 79/100 ..." (pasted report)
- "Draft the response to reviewers" / "format the response letter as a PDF"
- "Cut the IEEE build to 16 pages" / "cut 3,000 words from sections 2 and 5"
- "The manuscript is horrendously long and reads like stitched work"
- "The round-two revision is in Word; mark what the authors have to fill"
- Any resubmission, camera-ready, or multi-round revision

Hands off elsewhere: [`manuscript-writing`](../manuscript-writing) for the
sentences themselves, [`build-check`](../build-check) for the page count and
the built PDF, [`submission-reviewer`](../submission-reviewer) to score the
science (its fix list feeds the checklist), [`submission-formatter`](../submission-formatter)
for templates and marked copies, [`journal-advisor`](../journal-advisor) to
choose the venue, [`investigating-sources`](../investigating-sources) for the
reference diet a page cut needs, [`ml-eval-statistics`](../ml-eval-statistics)
and [`manuscript-figures`](../manuscript-figures) when a reviewer request
needs new numbers or artwork, [`project-ledger`](../project-ledger) for the
ids and vocabulary this skill keeps out of the paper.

## What's inside

```
manuscript-editor/
├── SKILL.md
├── references/
│   ├── editorial-read.md          paragraph-level read: three questions, three indexes, section tests, cut decisions
│   ├── manuscript-boundary.md     three containers, families A to F with before/after pairs, repair procedure
│   ├── coherence-audit.md         reading the audit, the whole-manuscript pass, decision rules
│   ├── journal-conventions.md     general principles vs. venue families, section rules, reporting guidelines
│   ├── response-to-reviewers.md   structure, per-item template, disagreement, consistency check
│   ├── cutting-to-a-budget.md     measure, rank cut classes by yield, apply in batches, re-measure
│   └── docx-revision.md           Word manuscripts: what scripts can do, what needs Word's Compare
├── assets/
│   ├── revision-ledger.md         internal ledger template
│   ├── response-template.md       response letter template
│   └── editorial-report.md        editorial report template (indexes, cut list, projected lengths)
└── scripts/
    ├── audit_manuscript.py        stdlib-only mechanical audit (md/tex/docx/txt)
    ├── make_checklist.py          reviewer files and a reviewer report -> the revision checklist
    ├── build_letter.py            check the letter against the manuscript, then build the PDF
    └── docx_markers.py            list/add/clear [AUTHOR ACTION] markers; extract text from .docx
```

## Scripts

```bash
python manuscript-editor/scripts/audit_manuscript.py paper.md --report audit_before.md
python manuscript-editor/scripts/audit_manuscript.py paper.md --strict
python manuscript-editor/scripts/make_checklist.py reviews/Reviewer1.txt reviews/Reviewer2.txt reviews/Editor.txt \
    --from-review reviews/external-review-02.md --from-checklist docs/REVISION_CHECKLIST_R1.md \
    --out docs/REVISION_CHECKLIST_R2.md
python manuscript-editor/scripts/build_letter.py letter/response.md --out letter/response.pdf \
    --aux paper/main.aux --manuscript paper/main.tex --date "12 September 2026"
python manuscript-editor/scripts/docx_markers.py list working/manuscript.docx
python manuscript-editor/scripts/docx_markers.py extract working/manuscript.docx --out working/manuscript.txt

# each script checks its own logic
python manuscript-editor/scripts/make_checklist.py --self-test
python manuscript-editor/scripts/build_letter.py --self-test
python manuscript-editor/scripts/docx_markers.py --self-test
```

Standard library only, except `docx_markers.py` (python-docx) and the build
step of `build_letter.py` (pandoc plus a TeX engine; its checks run without
them). All are pattern-based by design and say so; the editorial read decides.

## Changelog

- **1.2.0**: Four modes and three scripts for the parts of a revision round
  that kept being done by hand. Revision checklist (`make_checklist.py`:
  atomic items with stable ids from reviewer files and from a
  `submission-reviewer` fix list, statuses carried forward across rounds),
  budget (a page cap or word guidance met by ranked cut classes with
  re-measurement through `build-check`, `references/cutting-to-a-budget.md`),
  letter build (`build_letter.py`: cited numbers checked against the `.aux`,
  quoted passages against the manuscript, no placeholders, then pandoc), and
  Word manuscripts (`docx_markers.py`, `references/docx-revision.md`). Adds
  the identity rule for front matter. The description now names the prompts
  that used to bypass the skill (a pasted decision letter or external
  review, "cut it to N pages", "format the response letter as a PDF").
- **1.1.1**: Hand off to `build-check` for the compiled PDF and name
  `project-ledger` as the home of the vocabulary this skill strips.
- **1.1.0**: The check is now a paragraph-level editorial read, with the script
  as its instrument rather than its substitute; five more families of
  non-manuscript text; ten new detectors; rules for citation jobs,
  continuity, captions, and the summary budget.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
