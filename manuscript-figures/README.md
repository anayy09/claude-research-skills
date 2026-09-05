# manuscript-figures

> Publication-grade figures: styled matplotlib, hand-authored SVG schematics, generative art.

[![Version](https://img.shields.io/badge/version-1.1.1-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

Produces manuscript figures that pass editorial checks on the first pass, and
teaches the agent the full production discipline behind them: build at final
printed size, vector-first, one type family at legible point sizes,
colorblind-safe palettes, error bars defined in the caption, fonts embedded on
export. Three production paths, routed by what the figure is:

- **Data figures** via matplotlib with a bundled house-style module
  (`figstyle.py`): mm-exact column sizing for Nature, Elsevier, Springer,
  IEEE, Science, NeurIPS, ICML and a generic profile, Okabe-Ito color cycle,
  panel labeling, and export helpers.
- **Schematics** (model architectures, pipelines, flowcharts, study designs)
  authored directly as SVG on a mm-true grid with reusable style tokens, then
  converted to PDF.
- **Conceptual/illustrative images** (graphical abstracts, cover art) via
  OpenAI image generation, called through a local Codex CLI instance or the
  Images API.

A stdlib-only checker verifies final files (dimensions vs. column, raster
DPI, PDF font embedding) and fails closed: what it can't verify is reported
as unverified, never passed.

## When Claude uses it

- "Turn this plot into Figure 2 for our Elsevier submission"
- "Make this figure publication quality / camera-ready"
- "I need an architecture diagram of the model" / "draw the pipeline"
- "Make a graphical abstract"
- Mentions of column width, DPI, artwork guidelines, TIFF/EPS requirements
- "Why did the journal reject my figures?"
- Pre-submission figure review

Hands off elsewhere: [`ml-eval-statistics`](../ml-eval-statistics) when the
numbers behind a figure still have to be computed,
[`experiment-ledger`](../experiment-ledger) when a caption has to name the run
that produced them,
[`research-paper-writing`](../research-paper-writing) for the paragraph that
cites the figure, and [`submission-formatter`](../submission-formatter) to place
the finished files in the venue's template. This skill owns the artwork and the
draft caption; everything around it belongs to those.

## What's inside

```
manuscript-figures/
├── SKILL.md
├── references/
│   ├── figure-standards.md     venue sizes, DPI, typography, color, captions
│   ├── matplotlib-recipes.md   house style + recipes for common plot types
│   ├── svg-diagrams.md         grid, tokens, patterns, SVG→PDF pipeline
│   ├── generative-images.md    Codex/API invocation, prompt craft
│   └── review-checklist.md     final pre-submission pass
├── scripts/
│   ├── figstyle.py             apply_style, fig_size, OKABE_ITO, label_panels, save_figure
│   └── check_figure.py         stdlib compliance checker (PDF/EPS/SVG/PNG/TIFF)
└── assets/
    └── manuscript.mplstyle     the same style as a matplotlib style sheet
```

## Scripts

```bash
# style module smoke test (writes figstyle_demo.pdf/.png)
python manuscript-figures/scripts/figstyle.py

# compliance check
python manuscript-figures/scripts/check_figure.py fig2.pdf --journal nature --width single
python manuscript-figures/scripts/check_figure.py fig3.tif --width 183 --min-dpi 300
```

## Dependencies

- `check_figure.py`: standard library only.
- `figstyle.py`: `matplotlib` (and `numpy` for its demo).
- SVG→PDF conversion uses whichever of `rsvg-convert`, `inkscape`, or
  `cairosvg` is installed; the skill degrades gracefully and tells you the
  command if none is.
- Generative path: an authenticated local
  [Codex CLI](https://github.com/openai/codex), which needs no API key of its
  own, or `OPENAI_API_KEY` in the environment for the direct Images API route.
  Optional; everything else works without either.

## Changelog

- **1.1.1**: `check_figure.py` no longer fails a PDF that contains no text.
  It treated the string `/Font` as proof that fonts were referenced, but that
  is only a resource-dictionary key and matplotlib emits it even when the
  dictionary is empty, so a figure whose labels all live in an embedded raster
  was reported as "fonts referenced but no embedded FontFile". Detection now
  keys on `/BaseFont`, which actually names a font object, and the no-text case
  falls through to UNVERIFIED as the fail-closed design intends. Also records
  the legibility arithmetic for model-rendered labels
  (`label_pt x DPI = 100 x cap_height_px`, so 6 pt at 300 DPI needs a cap
  height of at least 18 px) and the measured palette drift when hexes are
  specified in a prompt.
- **1.1.0**: Generated figures may now carry their own text. Current image
  models set short strings accurately, so the guidance is to quote the exact
  labels in the prompt and proofread every glyph at inspection, instead of
  banning text outright and overlaying all of it in vector. Vector overlay
  stays the recommendation only where a label must remain editable after
  review or match the manuscript's typeface exactly. The Codex CLI route is
  documented as actually invoked (`codex exec --sandbox workspace-write`,
  prompt piped on stdin) and no longer claims a subscription login can fall
  back to the Images API, which it cannot. `figstyle.apply_style()` now keeps
  mathtext on the figure's own font family, so a `$...$` in a label no longer
  embeds a second typeface into the PDF.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
