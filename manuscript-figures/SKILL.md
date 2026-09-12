---
name: manuscript-figures
description: >-
  Produce publication-quality, journal-compliant manuscript figures end to end:
  data figures with matplotlib in a consistent house style, vector schematics
  (model architectures, pipelines, flowcharts, study designs) authored directly
  as SVG, and generative images for conceptual
  art via a local Codex CLI or the OpenAI Images API. Covers venue sizing
  (single/double column, mm-exact), typography, colorblind-safe palettes,
  multi-panel assembly, export (PDF/EPS/TIFF/PNG at correct DPI with embedded
  fonts), and an automated pre-submission compliance check. Use whenever the
  user asks to make, restyle, polish, or fix a figure for a paper, poster,
  thesis, or camera-ready version; mentions publication quality, column width,
  DPI, figure guidelines for Nature, Elsevier, IEEE, Springer, or an ML
  conference; wants a graphical abstract, architecture diagram, or pipeline
  figure; or asks why a figure was rejected. Also use when converting
  exploratory plots into final manuscript figures and when reviewing figures
  before submission, and for "plot", "chart", "matplotlib figure for the
  paper", "make the figures publishable", or "the figures are too bad to look
  at". For print figures this skill takes precedence over any general
  charting or dataviz skill, whose palettes and interaction rules are for
  screens.
summary: "Publication-grade figures: styled matplotlib, hand-authored SVG schematics, generative art."
version: "1.2.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-09-12"
---

# Manuscript Figures

Editors and reviewers reject figures for a short list of reasons: fonts that are
illegible at print size, rasterized plots that should be vector, colors that
collapse for colorblind readers or in grayscale, inconsistent style across
figures, and dimensions that don't fit the column. Every one of these is
preventable at creation time and expensive to fix after review. This skill makes
figures that pass on the first pass.

The core discipline: **build every figure at its final printed size, in vector
format, with the real fonts, from the start.** A figure designed at 12 inches
and scaled down to 89 mm in LaTeX has 3 pt text and hairline axes. A figure
built at 89 mm with 7 pt text is correct forever.

## Scope, and what belongs elsewhere

This skill makes the artwork. It does not:

- Compute the numbers a figure plots. Hand off to `ml-eval-statistics` for
  significance tests, confidence intervals, calibration curves, and
  risk-coverage data, then plot exactly what it returns.
- Decide which run a figure is drawn from. Hand off to `experiment-ledger` when
  the caption has to name a config or a manifest hash, so the figure traces
  back to something reproducible.
- Write the prose. Captions get a draft here, but the paragraph that cites the
  figure belongs to `manuscript-writing`.
- Place figures in a venue's template or convert the manuscript around them.
  Hand off to `submission-formatter`; this skill supplies the files it embeds.

A figure whose underlying numbers are wrong is worse when it is beautiful, so
when the statistics look unsettled, say so before styling anything.

## Step 0: pin the constraints

Before drawing anything, establish four facts. Ask the user only for what the
conversation doesn't already reveal; otherwise use the safe defaults and state
the assumption.

1. **Venue.** Determines column widths, DPI floors, and file formats. Default: the generic profile in
   `references/figure-standards.md` (89 mm single / 183 mm double column).
2. **Slot.** Single column, 1.5 column, or double column? Default to single
   column unless the figure has 3+ panels across or a wide heatmap/timeline.
3. **Format.** Vector (PDF/EPS) unless the venue demands TIFF. Always keep the
   source (script or SVG) next to the output so revisions are one edit away.
4. **Color budget.** Some venues charge for print color or require figures to
   survive grayscale. Default: colorblind-safe palette that also survives
   grayscale conversion.

For LaTeX camera-ready work, the exact column width beats any table: have the
user drop `\the\columnwidth` or `\the\textwidth` into their document, take the
pt value, and divide by 72.27 for inches.

## Step 1: route the figure

Three production paths. Pick by what the figure *is*, not by what tool is
convenient.

| Figure type | Path | Reference |
|---|---|---|
| Data/results: plots, curves, distributions, heatmaps, benchmark tables-as-figures | matplotlib via `scripts/figstyle.py` | `references/matplotlib-recipes.md` |
| Schematic: model architecture, pipeline, flowchart, study design (CONSORT/PRISMA-style), system overview | Hand-authored SVG, converted to PDF | `references/svg-diagrams.md` |
| Conceptual/illustrative: graphical abstract, cover art, pictorial concept figure | Generative image (Codex CLI or OpenAI Images API) | `references/generative-images.md` |
| Multi-panel composite | Assemble in matplotlib (`subplot_mosaic`) or in one SVG; never paste exported panels together as rasters | both of the above |

Hard boundaries between the paths:

- **Schematics default to SVG, not image generation.** SVG is crisp at any
  size, editable in one line when a reviewer asks for a rename, and carries no
  policy risk. Reach for image generation only when the user explicitly wants
  a pictorial or 3D-illustrated quality that flat vector can't deliver, and
  the venue allows it.
- **Data figures are code.** The script that produces a figure is part of the
  figure. Save it, and regenerate rather than retouch.

## Step 2: apply the non-negotiables

These hold across all three paths. They are the difference between "looks fine
on my screen" and "prints correctly in the journal."

**Size and resolution.** Build at final size in mm. Vector for anything with
lines or text. If raster is forced: 300 DPI minimum for color/halftone, 600 for
combination art (image + labels), 1000+ for pure line art. Never upscale a
small raster to hit a DPI number; the pixels don't come back.

**Typography.** One sans-serif family everywhere (Arial or Helvetica; DejaVu
Sans is the honest fallback when neither is installed). At final size: ~7 pt
for axis labels, 6 pt for tick labels, 5 pt absolute floor anywhere, 8 pt bold
for panel labels. Panel labels are lowercase bold **a, b, c** for Nature-family
journals, uppercase **A, B, C** for most others; check the venue. No figure
titles inside the figure; the caption does that job.

**Color.** Default to the Okabe-Ito palette (built into `figstyle.py`); it is
distinguishable under the common color-vision deficiencies. Sequential data:
`viridis`/`cividis`. Diverging data: `RdBu_r` or `coolwarm` centered on the
meaningful zero. Never `jet`/`rainbow`. Redundantly encode anything critical
(marker shape or line style in addition to color) so grayscale print still
reads.

**Honesty of the plot itself.** Error bars or bands on every estimate, with
the caption stating what they are (SD, SEM, 95% CI, and n). Bar charts of
means start at zero or become dot/box plots. Show distributions, not just
summaries, when n is small (overlay points on boxes). Log scales labeled as
such. No truncated axes without a visible break.

**Export.** Fonts embedded: `pdf.fonttype = 42` (already set by
`figstyle.apply_style()`), text kept as text in SVG until final conversion.
Deliver PDF plus a 600 DPI PNG for the submission portal preview; add
LZW-compressed TIFF only if the venue demands it.

## Step 3: verify before you hand it over

Run the compliance checker on every final file:

```bash
python scripts/check_figure.py figures/fig2.pdf --journal nature --width single
python scripts/check_figure.py figures/fig3.tif --min-dpi 300 --width 183
```

It verifies physical dimensions against the target column, DPI for rasters,
font embedding for PDFs, and flags rasterized content inside a nominally
vector file. It is standard-library only and fails closed: anything it cannot
verify is reported as UNVERIFIED, never silently passed.

Then do the human pass with `references/review-checklist.md`: caption
completeness, panel-label consistency across the whole manuscript, grayscale
survival, and the small-but-fatal items (missing units, unlabeled colorbars,
legend covering data).

The checker also reads the placed text: every label's box against the
figure frame (a label running off the edge is a FAIL), every label's size at
the target width (`--min-font-pt`, default 6; a 3 mm label on a 182 mm
drawing printed at 89 mm is 4.2 pt and fails), and label boxes that overlap
(a legend over an axis, colliding tick labels). PDF text comes from poppler's
`pdftotext` or PyMuPDF; SVG text from the `<text>` elements against the
viewBox, with a width estimate, so a collision report on an SVG is a prompt
to render and look. Text converted to outlines is not measurable here and is
reported as such.

Once the figure is placed in the manuscript, `build-check` renders the built
PDF and reports a figure or its labels running past the text block; a label
that crosses its frame at print size comes back here to fix.

## Typical session shapes

**"Turn this exploratory plot into Figure 2 for our Elsevier submission."**
Pin venue and slot → port the plotting code onto `figstyle.apply_style()` and
`fig_size("single", journal="elsevier")` → restyle per the recipes → export
PDF + PNG → run `check_figure.py` → deliver figure, source script, and a draft
caption.

**"I need an architecture diagram of our model."** Sketch the block structure
in text with the user first (blocks, ordering, skip connections, annotations)
→ author the SVG per `references/svg-diagrams.md` on its grid system → convert
to PDF → check → deliver SVG source + PDF.

**"Make a graphical abstract."** Check the venue's generative-AI policy first
and tell the user what it says. If prohibited: build it as an SVG composition
instead. If allowed with disclosure: follow `references/generative-images.md`
(Codex/API invocation, prompt patterns, in-image versus overlaid text,
disclosure line for the manuscript).

**"Why did the journal bounce my figures?"** Run `check_figure.py` on each
file, map the failures to the venue's requirements in
`references/figure-standards.md`, and fix by regeneration, not by resampling.

## What's in this skill

- `references/figure-standards.md` — venue size/DPI/format tables, typography
  and color rules, panel and caption conventions. Read when pinning
  constraints or diagnosing a rejection.
- `references/matplotlib-recipes.md` — the house style in practice: setup,
  panel layouts, and recipes for the plot types papers actually use. Read
  before writing plotting code.
- `references/svg-diagrams.md` — the grid, tokens, and patterns for authoring
  schematics as SVG, plus the SVG→PDF conversion pipeline. Read before any
  architecture/flowchart figure.
- `references/generative-images.md` — Codex CLI and OpenAI API
  invocation, prompt patterns, post-processing. Read before any generative
  work, every time.
- `references/review-checklist.md` — the final pre-submission pass.
- `scripts/figstyle.py` — importable style module: `apply_style()`,
  `fig_size()`, `OKABE_ITO`, `label_panels()`, `save_figure()`.
- `scripts/check_figure.py` — stdlib-only compliance checker for
  PDF/EPS/SVG/PNG/TIFF outputs.
- `assets/manuscript.mplstyle` — the same style as a matplotlib style sheet,
  for users who prefer `plt.style.use()`.

## Loading discipline

Load this skill once per session, before the step it governs, and do not
invoke it again when it is already in context; a second load re-injects the
same text and nothing else. When a repository carries `docs/SKILL-ROUTING.md`
(`project-ledger`), it names the skill for each step and file; follow it, and
record the skill in that step's progress entry. When a brief names several
skills, each is loaded at the step it governs, not all at the start.
