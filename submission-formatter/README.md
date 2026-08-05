# submission-formatter

> Reformat a finished manuscript into a venue's LaTeX or Word template without changing a word.

[![Version](https://img.shields.io/badge/version-1.1.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Takes a manuscript that is already written and puts it into the exact shape a
venue expects. Input can be PDF, DOCX, LaTeX source, Markdown, ODT, or RTF.
Output is a compilable LaTeX submission or a styled DOCX in the publisher's
template, plus a `FORMAT_REPORT.md` and a machine-checked fidelity report.

The hard part is not the typesetting, it is proving nothing changed on the way.
A conversion that silently drops a table row, reflows a hyphenated word into a
new one, renumbers a citation, or "tidies" a sentence has corrupted the
scientific record in a way nobody catches during a portal upload at 11pm. So the
workflow ends with a mechanical diff between source and output, not with a
rendered PDF.

## The fidelity contract

Seven rules that override any formatting convenience:

| | Rule |
| :-- | :--- |
| 1 | Body text is **copied, never regenerated**. Prose is extracted mechanically and moved as a string, never retyped from reading a PDF. |
| 2 | Numbers, units, statistics, gene and model names, and identifiers are **immutable**. No rounding, no unit normalization, no fixing an apparent typo in a value. |
| 3 | Citations keep their identity. Renumbering only when the target style demands it, and only with the mapping verified end to end. |
| 4 | Tables and figures move **whole**. Figures are re-embedded from the original image data, never re-rendered from a screenshot. |
| 5 | **Nothing is invented.** Missing ORCIDs, funding statements, ethics approvals, and CRediT roles become explicit `TODO(author)` markers, never plausible text. |
| 6 | **Nothing is deleted to fit.** Over a length limit, it builds anyway, measures the overage in the venue's own unit, and lists candidate cut sites for you to decide on. |
| 7 | Every deviation is reported, including the ones that were necessary. |

Allowed changes, for clarity: template-mandated section order and heading case,
citation and reference restyling, figure and table placement, macro substitution,
hyphenation, and structural scaffolding that carries no content.

The rule that does the most work in practice is #5. A required section that does
not exist yet is a marker and a handoff, never a draft, because generic text gets
submitted.

## When Claude uses it

- "Format this for IEEE Access" / "prepare this for Springer submission"
- "Convert my Word paper to the Elsevier LaTeX template" / "convert my DOCX to LaTeX"
- "Make the camera-ready" / "build the submission package"
- "Does this comply with the author instructions?" (a pre-submission compliance check)
- Moving a paper from one venue's format to another after a rejection

Hands off elsewhere: [`journal-advisor`](../journal-advisor) when the venue is not
chosen yet, [`submission-reviewer`](../submission-reviewer) for a quality read,
[`research-paper-writing`](../research-paper-writing) when the template requires a
section that has to be written, [`prose-naturalizer`](../prose-naturalizer) for
de-AI-ing text, and [`ml-eval-statistics`](../ml-eval-statistics) when a table has
to be regenerated rather than moved. This skill moves existing content into a new
container. The moment a task needs sentences the author has not written, it stops
and says so.

## What's inside

```
submission-formatter/
├── SKILL.md
├── references/
│   ├── template-sources.md     official template locations, class names, quirks
│   ├── extraction.md           per-format extraction recipes and their hazards
│   ├── assembly-latex.md       preamble remapping, front matter, math, bibliography
│   ├── assembly-docx.md        reference-doc workflow, style mapping, page setup
│   └── fidelity-protocol.md    markers, drift classes, the FORMAT_REPORT template
└── scripts/
    ├── extract_manuscript.py   any input format to a structured IR, inventory, media
    ├── inspect_template.py     template zip/dir/.tex/.docx to a requirements sheet
    ├── compile_tex.py          engine choice, latexmk build, log triage, submission zip
    └── fidelity_check.py       sentence, number, citation, and structure drift
```

## Scripts

Standard library, plus `python-docx`, `pdfplumber`, and `pypdf` when present, and
they shell out to `pandoc`, `pdftotext`, `pdfimages`, and `latexmk` when
available. Each degrades to a documented fallback rather than failing, and prints
what it could not do.

```bash
# 1. ingest: writes manuscript.json (the IR), inventory.md, and media/ at original resolution
python submission-formatter/scripts/extract_manuscript.py paper.docx -o build

# 2. inspect the publisher template: class options, front-matter macros, required sections
python submission-formatter/scripts/inspect_template.py sn-article-templates.zip

# 3. build, and package whether or not the local compile succeeds
python submission-formatter/scripts/compile_tex.py build/main.tex --package report/submission.zip

# 4. prove nothing drifted
python submission-formatter/scripts/fidelity_check.py \
  --source build/manuscript.json --output build/main.tex --json report/fidelity.json
```

`pandoc` is the one dependency worth installing before you start: without it,
only `.md`, `.txt`, and `.pdf` input can be read. A missing `.cls` is not a
problem, see below.

For Word input, install `python-docx` too. Pandoc only recognizes Word's
built-in `Heading N` styles, and manuscripts built on a publisher template
usually carry custom names (`heading1`, `referenceitem`). Without that second
pass the section outline collapses and the reference list stops being findable.

## Two things that surprise people

**A local compile failure is usually not a defect.** Publisher classes are rarely
installed in a normal TeX environment, so `compile_tex.py` separates
missing-dependency failures from real LaTeX errors and always writes the
submission zip. A build that fails only because `sn-jnl.cls` is absent locally
will compile in Overleaf or on the publisher's portal.

**PDF input is lossy and gets declared as such.** Two-column reading order,
ligatures, hyphenation across line breaks, footnotes, and math rendered as glyphs
all corrupt silently. If the DOCX or TeX source exists, the skill asks for it
once. If a PDF is genuinely all there is, it proceeds, marks the job lossy, and
puts a math-and-tables review checklist in the report. A scanned or image-only
PDF stops the pipeline: OCR output cannot meet the fidelity contract without a
full author proofread.

## Publishers with template locations mapped

IEEE (including IEEE Access), Elsevier (`elsarticle` and CAS), Springer Nature
(`sn-jnl`), Springer LNCS/LNNS/CCIS, MDPI, Wiley, Taylor & Francis, ACM
(`acmart`), PLOS, Frontiers, IOP, APS/AIP (REVTeX), Oxford, SAGE, Cambridge, and
the preprint servers. `references/template-sources.md` carries the class names,
typical class lines, bibliography styles, and the quirks that cause most desk
rejections, plus a search strategy for a journal that is not listed.

Two rules govern fetching: the class from the downloaded template always wins
over the table, and the author instructions page always wins over the template
file, because the template does not encode word limits, blinding rules, or
required declaration sections.

## Changelog

- **1.1.0**: Recover headings, reference lists, and figure captions from Word
  files that use custom style names, and fix extraction and build defects found
  by running the skill against two real manuscripts (a LaTeX paper into
  `sn-jnl`, a DOCX paper into IEEE Access).
  - Figure captions come from the author's caption paragraph, never from Word's
    machine-written alt text.
  - Grid tables whose rules carry alignment colons are no longer truncated to
    their first row.
  - Figures resolve relative to the manuscript, so media actually extracts.
  - LaTeX input is counted from the `.tex` itself, and any structure the pandoc
    round-trip failed to reproduce is reported instead of silently undercounted.
  - `latexmk` is told to run BibTeX, and the passes after it are run, so a first
    build no longer ships with every citation undefined.
  - `fidelity_check` says when it fell back to its crude LaTeX reader, rather
    than reporting the shortfall as missing content.
  - All three scripts decode subprocess output as UTF-8, fixing a crash on
    Windows consoles for any manuscript containing non-ASCII characters.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
