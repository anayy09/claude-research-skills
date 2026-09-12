# build-check

> Compile, render, and inspect the built PDF: overflow, floats, page cap, fonts, stale derived files.

[![Version](https://img.shields.io/badge/version-1.1.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

"Compiles clean" describes the log, not the page. This skill makes the agent
finish a build the way an author does: build it, look at it, and say what was
seen. It gives the agent:

- **One script, one report.** `build_check.py` compiles every target
  (latexmk, or engine passes), triages the log, counts pages against the
  venue cap and body words against the guidance, measures every text line,
  image, and drawing against the text block edges the document itself
  establishes, maps every float to the page it landed on, checks that all
  fonts are embedded, compares derived PDFs (response letter, marked-up
  copy, supplement) with their sources by modification time, and renders
  every page to a thumbnail grid in `BUILD_REPORT.md`.
- **An identity and placeholder gate.** Every email and ORCID in the front
  matter is checked against `AUTHORS.yaml`, every listed author must appear,
  and the PDF text is searched for `[AUTHOR INPUT]`, `TODO`, `TBD`, DOI
  placeholders, and the `??` of an unresolved reference. A fabricated author
  block cannot reach a submission form again.
- **A hard rule.** A build is finished when the report exists and the
  flagged pages have been looked at. "Compiles clean", "zero undefined
  references", and "exit 0" are inputs to the result, never the result.
- **The reading that a script cannot do.** What a thumbnail shows (a table
  past the margin, a float in the references, a half-empty page, an
  orphaned heading), what needs a zoomed page (figure label size, caption
  and body font), and what no render shows (a number against its results
  file).
- **The fixes, in order of preference.** Why a float lands in the
  references and how to move it without `[H]` everywhere; why `[H]` is
  inert on a double-column float; how to recover pages honestly and which
  tricks a typesetter undoes.

## When Claude uses it

- "Compile the packages and check the PDFs"
- "The tables are going out of bound in the Springer build"
- "Some tables are coming in the middle of the references"
- "Cut the IEEE build to 16 pages" (measures before and after; the cuts
  themselves are `manuscript-editor`'s)
- "Did you rebuild the response letter PDF?"
- The last step of any `submission-formatter`, `manuscript-editor`, or
  `manuscript-figures` pass that ends in a build

Hands off elsewhere: [`submission-formatter`](../submission-formatter) to
put a manuscript into a template, [`manuscript-editor`](../manuscript-editor)
to decide what to cut, [`manuscript-figures`](../manuscript-figures) to fix
a figure whose text crosses its frame.

## What's inside

```
build-check/
├── SKILL.md
├── references/
│   ├── log-triage.md          every log message the checker reports, and its usual fix
│   ├── float-placement.md     why floats land in the references; fixes in order; venue notes
│   ├── page-budget.md         recovering pages honestly; what reads as a paper pushed over its cap
│   └── reading-the-page.md    what a thumbnail shows, what needs a zoom, what no render shows
├── assets/
│   └── handback-template.md   the hand-back that quotes the report instead of the log
└── scripts/
    └── build_check.py         build, triage, measure, map floats, check fonts, render pages
```

## Scripts

```bash
# one package
python build-check/scripts/build_check.py submission/cep/main.tex

# three venue packages, IEEE cap, fail the run on any FAIL
python build-check/scripts/build_check.py submission/*/main.tex --max-pages 16 --strict

# existing PDF, no rebuild, with derived artifacts that must be newer than their sources
python build-check/scripts/build_check.py paper/main.pdf --no-build \
    --derived letter/response.pdf:letter/response.md \
    --derived paper/marked-up.pdf:paper/main.tex

# machine-readable copy next to the markdown report
python build-check/scripts/build_check.py main.tex --json build-check/report.json

python build-check/scripts/build_check.py --self-test
```

Standard library only. Uses whichever tools exist: `latexmk` or a TeX
engine, poppler's `pdftotext` (`-bbox-layout`), `pdftoppm`, `pdffonts`,
`pdfinfo`, and PyMuPDF when importable. On Windows the poppler tools next
to MiKTeX or TeX Live are found when the `pdftotext` on PATH is an older
xpdf build without bounding-box output. Every check that cannot run is
reported as SKIP with its reason.

## Changelog

- **1.1.0**: Identity and placeholder checks. `--authors AUTHORS.yaml`
  (found automatically next to the target or up to two directories above):
  an email or ORCID in the front matter that is not in the file fails the
  build, a listed author missing from page 1 warns. The PDF text is searched
  for author-input markers, TODO, TBD, DOI placeholders, and unresolved `??`
  references.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
