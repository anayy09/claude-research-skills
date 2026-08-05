# Getting content out of the source without damaging it

The extraction step decides how much fidelity is available downstream. Nothing
later can recover content that was mangled here, so the effort belongs at the
front.

## Contents

- [Format ranking](#format-ranking)
- [LaTeX source](#latex-source)
- [DOCX](#docx)
- [PDF](#pdf)
- [Markdown, ODT, RTF, HTML](#markdown-odt-rtf-html)
- [Figures](#figures)
- [Tables](#tables)
- [Equations](#equations)
- [Citations and references](#citations-and-references)
- [Manual checks before assembly](#manual-checks-before-assembly)

## Format ranking

Ask for the best available source before starting. In descending fidelity:

1. LaTeX source with figures and `.bib`
2. DOCX, especially with a reference manager still attached
3. ODT, RTF, HTML, Markdown
4. PDF built from the above
5. Scanned PDF: not usable under the fidelity contract without a full author
   proofread of OCR output

If the user supplies a PDF and the paper obviously came from Word or LaTeX, ask
once for the source. One question costs a minute; PDF extraction costs the
author a proofread of the whole manuscript.

## LaTeX source

**Remap, do not rebuild.** Round-tripping LaTeX through markdown loses custom
macros, math spacing, `\label` and `\ref` structure, table tuning, and package
behaviour. The body is already in the target language.

Procedure:

1. Run `extract_manuscript.py` on the `.tex` anyway. Its output is the inventory
   and the fidelity baseline, not the build input.
2. Copy the author's `\begin{document}` to `\end{document}` body into the
   template's sample file, replacing the sample body.
3. Rewrite the preamble: keep the author's `\usepackage` lines minus anything
   the target class already loads or forbids, keep `\newcommand` definitions,
   drop the old class line and old geometry, margin, and font settings.
4. Rebuild the front matter with the target class's macros, using the author's
   values.
5. Resolve macro collisions. Common ones: `\keywords` defined by both, `subfig`
   versus `subcaption`, `natbib` loaded twice, `algorithm2e` versus `algorithmic`,
   `hyperref` load order, `\thanks` semantics differing between classes.
6. Multi-file projects: follow every `\input` and `\include`, and keep the file
   structure unless the portal requires a single file. When flattening, do it
   mechanically rather than by retyping.

Watch for: `\def` redefinitions that clash with the class, `\bibliographystyle`
left pointing at the old journal's `.bst`, hard-coded `\vspace` tuning that no
longer applies, and `\usepackage{times}` or similar font packages that fight the
new class.

## DOCX

`extract_manuscript.py` uses pandoc, which handles styles, tables, footnotes,
OMML equations, and embedded media.

Specific hazards:

- **Field-based citations.** EndNote, Mendeley, and Zotero citations render as
  text when the field codes are stripped. The text is correct, the live link is
  gone. Tell the author explicitly, since re-establishing the link later is
  their job.
- **Tracked changes.** Pandoc accepts them by default. If the file has unaccepted
  revisions, confirm which version is intended before proceeding, and say which
  one was used. `--track-changes=all` shows what is at stake.
- **Text boxes and grouped shapes.** Content inside these is often dropped
  entirely. Open the source and check for figure captions, callouts, or
  side-panels that did not appear in the extraction.
- **Equations as images.** Old documents carry MathType or pasted images. These
  extract as image files, not math. Flag every one; do not transcribe them by
  sight.
- **Auto-numbering.** Word's automatic figure, table, and heading numbers may
  flatten to literal numbers or vanish. Check the caption sequence in the
  inventory against the source.
- **Two-column layouts and section breaks** can reorder content. Verify the
  section order in `inventory.md` matches the document.

For style-level detail pandoc discards, a second pass with `python-docx` reads
paragraph style names, which is useful for identifying which paragraphs were
captions, block quotes, or code.

## PDF

Mark `lossy: true`, and treat every one of these as a required check:

- **Reading order.** Two-column PDFs can interleave columns. The extractor uses
  pdftotext's reading-order mode rather than `-layout` for this reason, but
  verify the first paragraph of each section reads continuously.
- **Hyphenation.** Line-final hyphens are joined by the extractor. This is
  wrong for genuinely hyphenated compounds broken at a line end. Scan for
  words like "selfsupervised" or "nonlinear" that should have kept the hyphen.
- **Ligatures.** fi, fl, ffi may extract as single glyphs or vanish. Search the
  extraction for missing letter pairs.
- **Headers, footers, page numbers, and running heads** interleave with body
  text and appear as stray paragraphs.
- **Footnotes** land at a page boundary, detached from their anchor.
- **Math** extracts as a garbled character sequence. Every equation must be
  identified and re-entered by the author, or recovered from the source file.
- **Tables** lose their grid. `pdfplumber` recovers ruled tables reasonably and
  whitespace-aligned tables badly. Every table needs a cell-by-cell visual check
  against the PDF.
- **Figures.** `pdfimages` extracts raster objects, which may be fragments,
  page backgrounds, or CMYK separations rather than the figure the author drew.
  Always ask for the original figure files.

Put every check above into `FORMAT_REPORT.md` as an author checklist when the
source is a PDF.

## Markdown, ODT, RTF, HTML

Handled by pandoc with no special hazards beyond the usual. HTML from a journal
site carries navigation chrome, cookie banners, and reference-list markup that
needs pruning; prune structurally, not by rewriting text.

## Figures

- Keep the original file. Never re-render, screenshot, crop, or "clean up" a
  figure. Resolution loss is invisible in a chat and fatal at print.
- Record for each figure: original filename, format, pixel dimensions, and
  caption. Journals impose minimum DPI (commonly 300 for halftone, 600 to 1000
  for line art), and only the original tells you whether the requirement is met.
- If a figure is below the journal's resolution requirement, report it and ask
  for the source file or the plotting script. Do not upscale.
- Vector originals (PDF, EPS, SVG) beat raster. If only a raster version is in
  the manuscript but the author has a vector original, ask.
- Multi-panel figures assembled in Word arrive as separate images. Reassembly is
  an authoring decision; ask rather than composing a layout.

## Tables

Preserve, in order of importance: cell contents exactly, row and column order,
merged-cell structure, significant digits, footnote markers and their notes,
and alignment. Convert the presentation (rules, spacing, `booktabs` styling)
freely, since that is layout.

Watch for numbers that Word or the PDF rendered with non-breaking spaces,
thousands separators, or minus signs that are Unicode U+2212 rather than ASCII
hyphen. Normalizing these is allowed only when it does not change the value,
and it should be noted in the report.

## Equations

- LaTeX source: keep verbatim.
- DOCX with OMML: pandoc produces LaTeX math, which is usually correct but needs
  a read-through for `\text{}` versus italics, multi-line alignment, and matrix
  delimiters.
- Images or PDF text: flag with location, do not transcribe.

Equation numbering and labels are structure and may be regenerated. Equation
content is not.

## Citations and references

- Detect the source style before converting: numeric brackets, superscript
  numeric, or author-year.
- Build the citation map: for each in-text marker, the reference it points to.
  Verify the map end to end after conversion. Renumbering that shifts one entry
  silently corrupts every citation after it.
- If the source has a `.bib`, reuse it and change only the style.
- If the references are unstructured text, keep them as text in original order.
  Parsing free text into BibTeX fields invites fabricated volume numbers, wrong
  years, and invented DOIs. Only build structured entries from structured data,
  or from a lookup the author can verify.
- Count the references before and after. The count must match, and the fidelity
  check enforces it.

## Manual checks before assembly

Read `inventory.md` and confirm:

- the section outline matches the source document
- figure and table counts match
- the abstract and keywords were detected, or are known to be absent
- the reference count matches the source
- nothing in the warnings list is unresolved

Report the counts to the user in one line before building. It is the cheapest
place to catch an extraction failure.
