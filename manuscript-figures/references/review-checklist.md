# Pre-submission figure review

Run per figure, then once across the whole manuscript. The automated part
first:

```bash
for f in figures/final/*; do
  python scripts/check_figure.py "$f" --journal <venue> --width <slot-or-mm>
done
```

Anything the checker reports as FAIL or UNVERIFIED gets resolved before the
human pass, and resolved by regeneration, never by resampling or cropping the
exported file.

## Per figure

**Geometry and format**
- [ ] Width matches the intended slot exactly (single/1.5/double or measured `\columnwidth`)
- [ ] Vector (PDF/EPS) for anything with lines or text; raster only where forced, at/above the DPI floor at final size
- [ ] Fonts embedded (PDF) or text-as-text (SVG master); no font substitution surprises when opened fresh
- [ ] Nothing clipped: descenders, rotated tick labels, error-bar caps, legend edges
- [ ] File named per the venue's convention; source script/SVG saved alongside

**Content**
- [ ] Every axis labeled with units; log scales visibly logarithmic
- [ ] Every colorbar labeled
- [ ] Error bars/bands present on every estimate; caption defines them (SD/SEM/CI) and gives n
- [ ] Bars start at zero, or the plot isn't bars
- [ ] Statistical annotations (\*, brackets) defined in the caption with the test named
- [ ] Legend covers no data; one legend per shared encoding
- [ ] No figure title inside the figure; the takeaway lives in the caption's bold lead sentence

**Legibility**
- [ ] Print the figure at 100% (or view at true physical size): all text ≥ 5 pt, comfortably ≥ 6 pt
- [ ] Grayscale conversion: every series still distinguishable
- [ ] Colorblind check: no red–green-only distinctions; palette is Okabe-Ito or equivalent
- [ ] Line weights ≥ 0.5 pt everywhere at final size

**Caption**
- [ ] Bold one-sentence takeaway first
- [ ] Each panel (a/b/c) described
- [ ] Abbreviations expanded on first use in the caption (captions are read standalone)
- [ ] Data/code availability statement if the venue wants it per-figure

## Across the manuscript

- [ ] One font family, one palette, one panel-label convention (case, weight, position) in every figure
- [ ] Semantic color consistency: each method/condition keeps its color everywhere
- [ ] Comparable quantities plotted on identical axis ranges across figures
- [ ] Figures numbered in citation order; every figure cited in the text; no orphan panels
- [ ] Supplementary figures held to the same standard (reviewers judge them equally)
- [ ] Any generative-AI imagery: venue allows it, nothing data-like, disclosure sentence present in the manuscript
- [ ] Photographic/scanned images: only whole-image uniform adjustments, disclosed where required

## Final artifact set per figure

1. Submission file(s) in the venue's format (e.g., `Fig2.pdf`, plus `.tif` if demanded)
2. 600 DPI PNG preview for portals and collaborators
3. The source: plotting script + data pointer, or SVG master (+ generation prompt and raw PNG for generative elements)
4. The caption text, in the manuscript
