# Figure standards by venue

Numbers below are the widely published author-guideline values. Publishers
revise them, and individual journals within a family sometimes differ, so for a
real submission confirm against the journal's current artwork instructions.
When the venue is unknown, use the **generic** profile; it fits inside almost
everything.

## Physical dimensions

| Venue / family | Single column | 1.5 column | Double / full width | Max height | Notes |
|---|---|---|---|---|---|
| Generic (default) | 89 mm | 136 mm | 183 mm | 240 mm | Safe everywhere |
| Nature family | 89 mm | 120–136 mm | 183 mm | 247 mm | Fonts 5–7 pt at final size |
| Science / AAAS | ~57 mm | ~121 mm | ~184 mm | ~230 mm | Three-column layout |
| Elsevier | 90 mm | 140 mm | 190 mm | 240 mm | Sizes in their artwork guide |
| Springer | 84 mm | — | 174 mm | 234 mm | |
| IEEE journals | 88.9 mm (3.5 in) | — | 181.9 mm (7.16 in) | text height | |
| PLOS | — | — | max 190.5 mm (7.5 in) | 223.5 mm | Width may be anything up to max |
| ACM | 85 mm approx. | — | 178 mm approx. | — | Depends on template; measure |
| NeurIPS (single col) | — | — | 139.7 mm (5.5 in) | — | `\textwidth` |
| ICML / two-col conf. | 82.6 mm (3.25 in) | — | 171.4 mm (6.75 in) | — | `\columnwidth` / `\textwidth` |
| CVPR / ICCV | ~84 mm | — | ~178 mm | — | Measure `\columnwidth` |

For any LaTeX venue, the authoritative width is what the class file says.
Have the author compile `\the\columnwidth` (or `\the\textwidth`) once; the
result in pt ÷ 72.27 = inches. Then use `\includegraphics[width=\columnwidth]`
with **no scaling factor**, because the figure was built at exactly that width.

## Resolution and format

| Content | Minimum DPI (raster) | Preferred format |
|---|---|---|
| Line art (plots, diagrams) | 1000–1200 | **Vector: PDF/EPS/SVG** |
| Combination (image + labels/lines) | 500–600 | Vector with embedded raster |
| Halftone / photo / heatmap-as-image | 300 | TIFF (LZW) or high-quality PNG |

- Vector always beats raster for anything containing text or lines. Submit
  raster only when the venue's system forces it.
- Never inflate DPI by resampling. If the source raster is 150 DPI at final
  size, the figure must be regenerated, not upscaled.
- TIFF: LZW compression, flattened, no alpha. RGB is accepted nearly
  everywhere now; convert to CMYK only if the journal explicitly requires it,
  and re-check colors after conversion because saturated RGB blues and greens
  shift.
- Name files exactly as required (`Fig1.pdf`, `Figure_1.tif`, etc. per venue).

## Typography at final size

| Element | Size | Weight |
|---|---|---|
| Panel labels (a/b/c or A/B/C) | 8 pt | bold |
| Axis labels, in-figure annotations | 7 pt | regular |
| Tick labels, legend entries | 6 pt | regular |
| Absolute floor anywhere | 5 pt | — |

- One family per manuscript: Arial or Helvetica. If neither is installed,
  DejaVu Sans (matplotlib's default) is metrically similar and acceptable at
  most venues; don't mix families across figures.
- Panel label case: lowercase bold for Nature-family; uppercase for most
  biomedical and IEEE venues. Position: outside the axes, top-left of each
  panel, aligned consistently across every figure in the manuscript.
- No bold or italic for emphasis inside plots except gene/species conventions.
- Units in parentheses in axis labels: `Latency (ms)`, `Δ AUROC`. SI spacing:
  `5 mm`, not `5mm`.
- Text must remain selectable text in PDFs (fonts embedded, not outlined)
  unless the venue asks for outlined text; keep an un-outlined master either
  way.

## Color

- Categorical: Okabe-Ito (in `figstyle.OKABE_ITO`):
  `#0072B2` blue, `#D55E00` vermillion, `#009E73` green, `#E69F00` orange,
  `#56B4E9` sky, `#CC79A7` pink, `#F0E442` yellow, `#000000` black.
  Use at most 6–7 categories; beyond that, restructure the plot (facet, rank,
  highlight-one-gray-the-rest).
- Sequential: `viridis` or `cividis`. Diverging: `RdBu_r`/`coolwarm`, center
  fixed at the meaningful midpoint (0, chance level, baseline).
- Banned: `jet`, `rainbow`, red–green pairings as the only distinction.
- Grayscale test: convert the figure to grayscale; every series must remain
  distinguishable via line style, marker, or lightness ordering.
- Semantic consistency across the manuscript: if the proposed method is blue
  in Figure 2, it is blue in every figure and table highlight thereafter.

## Panels and composition

- Multi-panel figures are one file, assembled programmatically (matplotlib
  `subplot_mosaic`) or in one SVG. Shared axes share limits and ticks;
  redundant axis labels dropped on interior panels.
- Legend: inside the axes only if it covers no data; otherwise above or right
  of the panel. One legend for panels sharing an encoding.
- Whitespace: consistent margins; nothing clipped (check descenders, error
  bar caps, rotated labels). `bbox_inches="tight"` hides sizing mistakes, so
  prefer correct layout at the declared size (`constrained_layout`).
- Aspect ratio: default to ~golden (h ≈ 0.62 w) for single plots; square for
  scatter with equal-unit axes, ROC, calibration, confusion matrices.

## Captions

The caption makes the figure self-contained. Template:

> **Figure N. Bolded one-sentence takeaway.** Sentence(s) describing what is
> plotted, per panel: **(a)** … **(b)** …. Error bars/bands: definition and n
> (e.g., mean ± 95% CI over 5 seeds; n = 412 patients). Abbreviations.
> Statistical annotations defined (\*p < 0.05, test named). Data/code
> availability if the venue wants it here.

Never restate the takeaway only in the caption while the figure shows
something the caption doesn't explain, and never explain in the caption what
the figure should have labeled.

## Accessibility and integrity

- Colorblind-safe palette + redundant encoding (above) is the accessibility
  baseline; some venues now also request alt text at submission.
- No image-editor retouching of data figures. Adjustments (crop, uniform
  brightness/contrast on photos) must be applied to the whole image and
  disclosed where required.
- Every data figure regenerates from a script checked into the project. Pair
  this with the `experiment-ledger` skill so the figure's numbers trace to a
  run manifest.
