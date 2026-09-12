---
name: build-check
description: >-
  Build a LaTeX manuscript or submission package and inspect the result the
  way a human would before saying it is done: compile every target, triage
  the log, render every page, measure tables, figures, and lines against the
  text block, map every float to the page it landed on, count pages against
  the venue cap and words against the guidance, confirm fonts are embedded,
  and check that derived PDFs (response letter, marked-up copy, supplement)
  are newer than their sources. Use whenever a PDF is about to be reported as
  built, rebuilt, compiled, or ready; whenever the user says "compile",
  "rebuild the PDF", "check the PDF", "tables are going out of bound", "the
  figure text exceeds the outline", "tables are in the middle of the
  references", "use [H]", "cut it to N pages", "does it fit the page limit",
  or "did you check the PDF"; and at the end of any submission-formatter,
  manuscript-editor, or manuscript-figures pass that ends in a build. Never
  report a build as clean without this report and a look at the flagged pages.
summary: "Compile, render, and inspect the built PDF: overflow, floats, page cap, fonts, stale derived files."
version: "1.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-09-12"
---

# Build Check

"Compiles clean" describes the log, not the page. A build can exit 0 with a
table running past the margin, a figure sitting inside the references, a page
count one over the venue's cap, a caption whose text crosses its frame, and a
response letter PDF older than the markdown it came from. Every one of those
has reached an author who was told the build was fine. This skill exists so
that the sentence "the PDF is ready" is never written from the log alone.

The rule it enforces: **a build is finished when the report exists and the
flagged pages have been looked at**, not when the compiler exits.

## Scope, and what belongs elsewhere

This skill builds and inspects. It does not:

- Put a manuscript into a template. `submission-formatter` does that, then
  hands the built package here.
- Decide what to cut when the page count is over. `manuscript-editor` owns
  the cut list; this skill measures the overage and re-measures after each
  cut.
- Draw or restyle figures. `manuscript-figures`. This skill reports a figure
  whose text crosses the frame or whose box crosses the margin; the fix is
  made there.
- Write prose. `research-paper-writing`.

## The workflow

### 1. Run the checker on every target

```bash
python scripts/build_check.py submission/cep/main.tex
python scripts/build_check.py submission/*/main.tex --max-pages 16 --strict
python scripts/build_check.py paper/main.tex --max-words 4500 \
    --derived letter/response.pdf:letter/response.md \
    --derived paper/marked-up.pdf:paper/main.tex
```

A target is a `main.tex`, a directory holding one, or a PDF (checked without
rebuilding). One run covers several venue packages and writes one report.
`--no-build` inspects an existing PDF and log without compiling.

The script writes `build-check/BUILD_REPORT.md` next to the first target,
with a page thumbnail grid, and prints a PASS, WARN, or FAIL line per target.
`--json` adds a machine-readable copy; `--strict` makes any FAIL exit
non-zero so the run can gate a commit or a package.

### 2. Read the report top to bottom

Each check is one of:

| Check | What it measures | FAIL when |
|---|---|---|
| build | the compile itself | no PDF produced |
| log | errors, undefined references and citations, missing files, multiply defined labels, "labels may have changed", float warnings, overfull boxes above `--overfull-pt` (default 5) | an error, undefined ref or cite, or missing file |
| pages | page count | over `--max-pages` |
| words | body words before the references | over `--max-words` |
| overflow | every text line, image, and drawing against the text block edges the document establishes, and against the page edge | content more than three times `--margin-pt` (default 3) past an edge; smaller overhangs WARN |
| floats | each figure, table, and algorithm: the page it landed on, whether that is inside the references, and whether it is inside the section that first cites it | a float in the references |
| fonts | embedding | any font not embedded (Type 3 fonts WARN) |
| derived | `--derived OUT:SRC` pairs by modification time | the source is newer than the output |

`references/log-triage.md` explains each log message and its usual fix.
`references/float-placement.md` covers why a float lands in the references,
why `[H]` is inert on a double-column float, and the fixes in order of
preference. `references/page-budget.md` covers what to do when the count is
over the cap without degrading the paper.

### 3. Look at the flagged pages, then at every page

The thumbnail grid marks the pages the checks flagged. Open those first. Then
scan every page at thumbnail size; a table past the margin, a figure in the
wrong place, a half-empty page before a float, and a heading orphaned at the
bottom of a column are all visible at 45 dpi. `references/reading-the-page.md`
lists what to look for and what a thumbnail cannot show (text legibility
inside figures, caption and body font mismatch, which needs a zoomed page).

Do not skip this step because every check passed. The checks find what a
script can measure; the read finds the rest.

### 4. Fix, rebuild, re-run

Every FAIL is fixed before the package is reported as done. Every WARN is
either fixed or named in the hand-back with the reason it stays. Then run
the checker again; the second report is the one the hand-back quotes.

When the fix belongs to another skill (cutting words, redrawing a figure,
moving a table to the supplement), hand off, then come back here.

### 5. Hand back with the report, never with the log

The hand-back says, per target: pages against the cap, the overflow count,
the float check result, fonts, words, and the path to the report. It names
every remaining WARN with its reason. It does not say "compiles clean",
"builds without errors", or "zero undefined references" as if those were the
result; those are inputs to the result.

## What the checker cannot see

Say these in the hand-back rather than implying they were checked:

- **Legibility inside figures.** A label that is 4 pt at print size passes
  every check here. `manuscript-figures` owns type size at final width.
- **Semantic placement.** A float inside its citing section but three pages
  after the citation is a WARN only if it crosses a section boundary.
- **Colour and greyscale.** Nothing here renders in greyscale.
- **The venue's own checker.** Elsevier, Springer, and IEEE run their own
  technical checks on upload (nested folders, file naming, missing
  declarations). `submission-formatter` covers the package manifest.

## Dependencies

Standard-library Python. Uses whichever of these exist: `latexmk` or
`pdflatex`/`xelatex`/`lualatex` for the build, poppler's `pdftotext`
(with `-bbox-layout`), `pdftoppm`, `pdffonts`, `pdfinfo`, and PyMuPDF if
importable. On Windows the poppler tools next to MiKTeX or TeX Live are found
automatically when the copy on PATH is an older xpdf build. Every check that
cannot run is reported as SKIP with the reason; nothing passes silently.
