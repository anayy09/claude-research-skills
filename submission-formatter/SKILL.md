---
name: submission-formatter
description: >-
  Reformat a finished manuscript into a specific journal or conference
  submission template, in LaTeX or Word, preserving every word, number, table,
  figure, and citation exactly as written. Accepts PDF, DOCX, LaTeX source,
  Markdown, ODT, and RTF input, asks once for the publisher template, and
  locates and downloads the official one when none is supplied. Use whenever a
  manuscript has to be put into a venue's format: "format this for IEEE
  Access", "convert my Word paper to the Elsevier LaTeX template", "prepare
  this for Springer, MDPI, Wiley, ACM, or PLOS submission", "make the
  camera-ready", "convert my DOCX to LaTeX", "reformat to the journal
  guidelines", "does this comply with the author instructions", or "build the
  submission package". Also use when moving a paper from one venue's format to
  another after a rejection, and for pre-submission template compliance checks.
  Never rewrites, condenses, paraphrases, or invents content: missing items are
  marked for the author, never filled in.
summary: "Reformat a finished manuscript into a venue's LaTeX or Word template without changing a word."
version: "1.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-08-04"
---

# Submission Formatter

Take a manuscript that is already written and put it into the exact shape a
venue expects, without changing what it says. Two things are being produced at
once: a document that compiles or opens cleanly in the journal's template, and
evidence that nothing was lost, added, or altered on the way there.

The second part is what makes this hard. A format conversion that silently drops
a table row, reflows a hyphenated word into a new one, renumbers a citation, or
"tidies" a sentence has corrupted the scientific record in a way the author is
unlikely to catch during a portal upload at 11pm. So the workflow ends with a
mechanical fidelity check, not with a rendered PDF.

## Scope, and what belongs elsewhere

This skill converts and typesets. It does not:

- Choose the venue. Hand off to `journal-advisor` when the target is not decided
  yet, then come back with the journal name.
- Judge the science. Hand off to `submission-reviewer` for a quality read.
- Write or rewrite prose. If the manuscript is over a length limit, or a
  required section (data availability, author contributions) does not exist yet,
  report it and hand off to `research-paper-writing`. Do not compose it here.
- Fix statistics or regenerate tables. Hand off to `ml-eval-statistics`.

The line is simple: this skill moves existing content into a new container. The
moment a task requires producing sentences the author has not written, it stops
and says so.

## The fidelity contract

These rules hold for every step and override any formatting convenience.

1. **Body text is copied, never regenerated.** Do not retype prose from a PDF by
   reading it. Extract it mechanically, then move the extracted string. If a
   character cannot be extracted, flag the location, do not guess it.
2. **Numbers, units, statistics, gene and drug names, model names, and
   identifiers are immutable.** No rounding, no unit normalization, no
   "0.05" to "0.050", no fixing an apparent typo in a value. Report suspected
   errors in the format report and leave the value alone.
3. **Citations keep their identity.** Renumbering is allowed only when the
   target style requires it and the mapping is verified end to end. The set of
   references cited, and which sentence cites which reference, does not change.
4. **Tables and figures are moved whole.** Cell contents, row and column order,
   significant digits, and captions are preserved verbatim. Figures are
   re-embedded from the original image data, never re-drawn or re-rendered from
   a screenshot when the original is available.
5. **Nothing is invented.** Missing ORCIDs, affiliations, funding statements,
   ethics approvals, highlights, graphical abstracts, keywords, and CRediT roles
   are emitted as explicit author-facing markers, never as plausible text. See
   the marker convention in `references/fidelity-protocol.md`.
6. **Nothing is deleted to fit.** If the manuscript exceeds a word, page, figure,
   or reference limit, build it anyway, measure the overage, and list candidate
   reduction sites for the author to decide on.
7. **Every deviation is reported.** The deliverable includes `FORMAT_REPORT.md`
   listing every change made, every gap left, and the result of the fidelity
   check.

Allowed changes, for clarity: section ordering mandated by the template,
heading capitalization mandated by the style, citation and reference formatting,
figure and table placement and numbering scheme, macro and environment
substitution, hyphenation and line breaking, and the addition of required
structural scaffolding that carries no content.

## Workflow

### 1. Set up a workspace

```bash
mkdir -p work/{source,template,build,report}
```

Keep the original input untouched in `source/`. Everything downstream is
regenerated, so intermediate files can be rebuilt at any time.

### 2. Ingest the manuscript and take inventory

```bash
python scripts/extract_manuscript.py work/source/paper.docx -o work/build
```

This writes `work/build/manuscript.json` (the intermediate representation),
`work/build/inventory.md` (human readable), and `work/build/media/` (extracted
figures at original resolution). It handles `.tex`, `.docx`, `.pdf`, `.md`,
`.odt`, `.rtf`, and `.html`.

Read `references/extraction.md` before trusting the output of any PDF input, and
before handling a LaTeX input. Two rules that matter most:

- **LaTeX input is remapped, not rebuilt.** When the source is `.tex`, the body
  stays as the author's LaTeX and only the preamble, class-specific macros, and
  front matter are rewritten for the target class. Round-tripping a LaTeX body
  through an intermediate format loses math subtleties, custom macros, and
  `\label` structure. The extractor is still run on `.tex` input, but only to
  produce the inventory and the fidelity baseline.
- **PDF input is lossy and must be declared as such.** Two-column reading order,
  ligatures, hyphenation across line breaks, footnotes, and math rendered as
  glyphs all corrupt silently. If the author has the DOCX or TeX source, ask for
  it once before proceeding. If a PDF is genuinely all there is, proceed, mark
  `lossy: true` in the report, and put a review checklist for math and tables in
  `FORMAT_REPORT.md`.

Report the inventory back to the user in three lines: word count, structural
counts (sections, figures, tables, equations, references), and anything the
extractor flagged.

### 3. Get the template: ask once, then act

Ask the user, in one message, whether they have the journal's template, and say
what is acceptable so the answer can be complete on the first try:

> Do you have the template for <journal>? A publisher zip, a `.cls` or `.docx`
> file, an Overleaf link, or a link to the author instructions page all work.
> If you would rather I fetch the official one, say so and I will.

Do not stall the pipeline waiting for it. If the user says to fetch it, does not
have it, or does not answer the question in their reply, move on to fetching.

**Fetching rules.** Read `references/template-sources.md` for the per-publisher
map of official template locations, class names, and known quirks. The
constraints on fetching:

- Prefer, in order: the journal's own author-instructions page on the publisher
  domain, the publisher's central template hub, the publisher's official
  Overleaf gallery entry, a template mirror. Record the exact URL and the access
  date for the report.
- Verify the artifact matches the target venue before using it. Journals inside
  one publisher differ (IEEE journals use `IEEEtran` with `journal` options,
  IEEE conferences use `conference`; Springer's `sn-jnl` is not LNCS `llncs`).
  Open the bundled sample `.tex` or README and confirm the journal or series
  name appears.
- If the template is behind a login, is unavailable, or nothing official exists,
  say so plainly, then fall back to the closest official family template and
  mark the substitution in the report. Never silently improvise a look-alike.
- Always fetch and read the author instructions page even when a template is
  supplied. The template does not encode word limits, section requirements,
  figure resolution, blinding rules, or the required declaration sections.

### 4. Inspect the template and build the requirements sheet

```bash
python scripts/inspect_template.py work/template/sn-article-templates.zip
```

This unpacks the artifact, identifies the main `.tex` and document class or the
`.docx` styles, and prints the structural inventory: class options, front-matter
macros, expected environments, bibliography style, and any placeholder sections.

Turn that plus the author instructions into an explicit requirements sheet in
the report, covering: document class and options, section order and required
sections, abstract and keyword limits, citation style, reference style file,
figure format and resolution, table style, line numbering and spacing, blinding,
length limits, and the file manifest the portal expects. Every later decision
refers back to this sheet.

### 5. Choose the output format

| Situation | Output |
|---|---|
| User asked for LaTeX, in any wording | LaTeX, always. This overrides everything below. |
| Source is `.tex` | LaTeX |
| Template is a LaTeX class and the user expressed no preference | LaTeX, and say why in one line |
| User asked for DOCX, or the venue accepts Word only, or the template is `.docx`/`.dotx` | DOCX |
| User asked for a PDF | Build LaTeX or DOCX per the rows above, then render the PDF from it, and deliver both |

When both a LaTeX and a Word template exist and the user has no preference,
default to LaTeX and offer the Word build as a follow-up rather than producing
both unasked.

Then read `references/assembly-latex.md` or `references/assembly-docx.md`.

### 6. Map content to the template structure

Before writing any output file, write the mapping table into the report: source
section, target section, and the action taken. This is where structural
mismatches surface, and they need a decision rather than a default.

| Source | Target | Action |
|---|---|---|
| Introduction | 1 Introduction | move as is |
| Related Work | 2 Related Work | move as is |
| Methods + Implementation | 3 Materials and Methods | merge under the required heading, subsections preserved |
| Results and Discussion | 4 Results / 5 Discussion | template requires them split; propose the split point, ask before applying |
| (absent) | Data Availability Statement | required by venue, insert marker |

Rules for the hard cases:

- **Merging is safe, splitting is not.** Merging two sections under a mandated
  heading keeps every sentence. Splitting one section into two requires a
  judgment about where the boundary falls, which is an editorial act. Propose
  the split point with the sentence it would fall on and confirm it.
- **Required-but-absent sections get markers, not drafts.** See the marker
  convention in `references/fidelity-protocol.md`.
- **Content with no home in the template** (an extra appendix, a section the
  template forbids) moves to supplementary material and is listed in the report.
  It is never dropped.

### 7. Assemble

Follow the assembly reference for the chosen format. The invariants both share:

- Build the front matter from extracted values only. Leave a marker where a
  value does not exist in the source.
- Move body content by copying strings from the extraction, not by retyping.
- Re-embed figures from `media/` at original resolution. Convert formats only
  when the class requires it (`references/assembly-latex.md` covers EPS and PDF
  cases), and keep the original file alongside the converted one.
- Rebuild tables into the template's table style with cell contents unchanged.
- Convert the bibliography to the required style. When the source references are
  unstructured text, keep them as a `thebibliography` list or a plain reference
  list in original order rather than parsing them into fields and risking
  fabricated metadata. Only build a `.bib` when structured data exists or the
  entries can be verified.

### 8. Compile or render

```bash
python scripts/compile_tex.py work/build/main.tex --package work/report/submission.zip
```

`compile_tex.py` selects the engine, runs `latexmk` with bibliography passes,
summarizes the first errors from the log, and always produces the submission zip
even when compilation fails locally, which is common because publisher classes
are frequently not installed in a minimal TeX environment. A build that fails
only because a `.cls` is missing locally is not a defect in the output: say so,
ship the zip, and note that Overleaf or the author's TeX installation will
compile it.

For DOCX, render with pandoc using the publisher `--reference-doc`, then open
the result to confirm styles applied rather than assuming they did.

### 9. Verify fidelity, then fix what drifted

```bash
python scripts/fidelity_check.py \
  --source work/build/manuscript.json \
  --output work/build/main.tex \
  --json work/report/fidelity.json
```

This compares the normalized sentence stream, the numeric token multiset, the
citation markers, and the structural counts between input and output. Every
reported difference gets resolved before delivery, into exactly one of:

- **Fix it.** Anything missing, truncated, or altered goes back into the output.
- **Justify it.** An expected difference (a template heading added, a citation
  marker restyled) is recorded in the report with its reason.

Do not deliver with unexplained drift. Re-run until the report is clean or every
remaining item has a written justification. `references/fidelity-protocol.md`
lists each drift class and its usual cause.

### 10. Deliver

```
work/report/
├── submission.zip          # or the .docx
├── main.pdf                # if it compiled
├── FORMAT_REPORT.md
└── fidelity.json
```

`FORMAT_REPORT.md` uses the structure in `references/fidelity-protocol.md`. Lead
the chat response with the three things the author has to act on: the markers
they must fill in, any limit overage, and any unresolved fidelity item. Then the
one-line status of everything else. Do not summarize the paper back to them.

## Degradation, and when to stop

| Situation | Response |
|---|---|
| Scanned or image-only PDF | Report that text extraction is not possible without OCR, and that OCR output cannot meet the fidelity contract without a full author proofread. Ask for the source file. |
| Publisher class not installed locally | Expected. Ship the zip, note it, do not substitute a different class to force a local build. |
| Template requires content that does not exist | Marker, report, handoff. Never draft it. |
| Manuscript is over the length limit | Build it, measure the overage in the venue's own unit (words, pages, or characters), list candidate cut sites, decide nothing. |
| Word citations are field-based (EndNote, Mendeley, Zotero) | Extract the rendered text, and tell the author the field codes are gone, so the reference manager link must be re-established or the list checked manually. |
| Math was rendered as images in the source | Flag every instance with its location. Do not transcribe equations by sight into LaTeX. |
| Two venues' requirements conflict with an author instruction | The author instruction page wins over the template file. Note the conflict. |

## Reference files

- `references/template-sources.md` - where the official template for each major
  publisher lives, class names, options, and per-venue quirks. Read before
  fetching anything.
- `references/extraction.md` - per-input-format extraction recipes and the
  specific hazards of each. Read before ingesting PDF or LaTeX.
- `references/assembly-latex.md` - preamble remapping, front matter macros by
  class, figures, tables, math, and bibliography conversion.
- `references/assembly-docx.md` - reference-doc workflow, style mapping,
  captions, equations, and the page-setup requirements journals impose.
- `references/fidelity-protocol.md` - marker conventions, drift classes and
  their fixes, thresholds, and the `FORMAT_REPORT.md` template.

## Scripts

All four are standard library plus `python-docx`, `pdfplumber`, and `pypdf` when
present, and shell out to `pandoc`, `pdftotext`, `pdfimages`, and `latexmk` when
available. Each degrades to a documented fallback rather than failing, and each
prints what it could not do.

| Script | Purpose |
|---|---|
| `scripts/extract_manuscript.py` | Any input format to `manuscript.json` + `inventory.md` + extracted media |
| `scripts/inspect_template.py` | Template zip, directory, `.tex`, or `.docx` to a structural requirements inventory |
| `scripts/compile_tex.py` | Engine selection, `latexmk` build, log triage, and the submission zip |
| `scripts/fidelity_check.py` | Sentence, number, citation, and structure drift between source and output |

Run any of them with `--help` for exact arguments.
