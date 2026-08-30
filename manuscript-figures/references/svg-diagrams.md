# Authoring schematics as SVG

Architecture diagrams, pipelines, flowcharts, and study-design figures are
best written directly as SVG: exact control, perfect crispness, trivially
editable when a reviewer wants one box renamed, and no policy questions. This
file is the system for doing it well rather than producing the loose,
inconsistent SVG that ad hoc generation tends to give.

## Canvas: mm-true from the first line

Set the SVG so 1 user unit = 1 mm at the final printed size. Everything after
that is drawn in real millimeters, and font sizes can be reasoned in pt
(1 pt = 0.3528 mm).

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     width="183mm" height="70mm" viewBox="0 0 183 70"
     font-family="Arial, Helvetica, sans-serif">
```

- Double column: width 183 (or the venue's value). Single column: 89.
- Height: whatever the content needs; keep it tight, no dead bands.
- Useful font sizes in these units: panel label `font-size="2.8"` (~8 pt),
  node labels `2.5` (~7 pt), annotations `2.1` (~6 pt). Never below `1.76`
  (5 pt).
- Stroke widths: 0.25 for box outlines and arrows (~0.7 pt), 0.4 for emphasis,
  0.15 for guides/brackets. Consistent everywhere.

## Layout discipline

- **Grid.** Place everything on a 2 mm grid; centers and edges land on grid
  lines. Misalignment is the single biggest "amateur diagram" tell.
- **Flow direction.** One dominant direction (left→right for pipelines and
  architectures, top→bottom for flowcharts). Skip/residual connections route
  above or below the main axis with rounded orthogonal paths, never diagonal
  spaghetti.
- **Sizing encodes meaning or nothing.** Equal-role blocks are equal-sized.
  If block area encodes something (parameter count, data volume), say so in
  the caption; otherwise keep uniform.
- **Density.** If it needs more than ~12 primary blocks, it needs grouping
  (containers with light fills) or a second figure.
- **Color.** Same Okabe-Ito hexes as the plots, used sparingly: light fills
  (add `fill-opacity="0.15"`) with solid strokes, and reserve one saturated
  color for the element the figure is about. Grays carry the rest.

## Reusable tokens

Define once in `<defs>`, use everywhere; this is what keeps the diagram
consistent.

```xml
<defs>
  <marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4"
          markerWidth="5" markerHeight="5" orient="auto-start-reverse">
    <path d="M0,0 L8,4 L0,8 z" fill="#333333"/>
  </marker>
  <style>
    .node  { fill:#0072B2; fill-opacity:0.12; stroke:#0072B2; stroke-width:0.25; }
    .op    { fill:#ffffff; stroke:#333333; stroke-width:0.25; }
    .hl    { fill:#D55E00; fill-opacity:0.15; stroke:#D55E00; stroke-width:0.4; }
    .edge  { fill:none; stroke:#333333; stroke-width:0.25; marker-end:url(#arrow); }
    .lbl   { font-size:2.5; fill:#111111; text-anchor:middle; }
    .ann   { font-size:2.1; fill:#555555; text-anchor:middle; }
  </style>
</defs>
```

## Patterns

**Block with centered label** (rounded corners read as "component"; sharp as
"data"):

```xml
<rect class="node" x="20" y="24" width="24" height="12" rx="1.5"/>
<text class="lbl" x="32" y="30.9">Encoder</text>
<text class="ann" x="32" y="34.2">12 × Transformer</text>
```

Vertical centering: `y = box_center + font_size * 0.35`. With a sub-line,
shift the pair up/down by half the line pitch (~3.2 for these sizes).

**Straight edge and orthogonal skip:**

```xml
<line class="edge" x1="44" y1="30" x2="52" y2="30"/>
<path class="edge" d="M 32 24 V 16 H 96 V 24"/>   <!-- residual over the top -->
```

Edges stop at box borders (the marker's `refX` handles the tip). Label an
edge with a small `.ann` text just above its midpoint.

**Container/group:**

```xml
<rect x="16" y="18" width="76" height="26" rx="2"
      fill="#999999" fill-opacity="0.08" stroke="#999999"
      stroke-width="0.2" stroke-dasharray="1.2 0.8"/>
<text class="ann" x="18" y="21.5" text-anchor="start">Feature extraction</text>
```

**Stacked-layers glyph** (the "repeated block" idiom): three offset
rectangles, back ones at `fill-opacity` 0.06/0.09, front one normal, with a
`× N` annotation.

**Decision diamond (flowcharts):** `<path d="M x,y-h l w,h l -w,h l -w,-h z">`
with yes/no labels on the outgoing edges, placed near the diamond, not
mid-edge.

**Tensor-shape annotations** in architectures: `.ann` text under each edge
(`B × 197 × 768`); use `×`, not `x`.

## Workflow

1. **Agree on structure in text first.** List blocks, order, branches, skips,
   and annotations with the user before writing any SVG. Editing a list is
   cheap; re-laying-out a diagram is not.
2. **Compute the layout as numbers, then emit.** Decide column x-positions
   and row y-positions once (on the grid), and derive every coordinate from
   them. For anything beyond ~10 elements, generate the SVG from a short
   Python script with those positions as variables; hand-editing 40 magic
   numbers is how misalignment happens, and the script becomes the editable
   source for revisions.
3. **Render and look.** Convert to PNG or PDF and inspect the actual output
   (see below); do not ship SVG that was only ever read as code. Check:
   nothing overlapping, text inside boxes, arrows touching borders,
   consistent gaps.
4. **Iterate with the user** on wording and emphasis, then export.

## Conversion and delivery

Journals want PDF/EPS/TIFF; almost none accept raw SVG. Convert preserving
size:

```bash
rsvg-convert -f pdf -o arch.pdf arch.svg          # librsvg; best fidelity/effort
# or
inkscape arch.svg --export-type=pdf --export-filename=arch.pdf
# or (Python, pip install cairosvg)
python -c "import cairosvg; cairosvg.svg2pdf(url='arch.svg', write_to='arch.pdf')"
# preview raster for portals
rsvg-convert -f png --dpi-x 600 --dpi-y 600 -o arch.png arch.svg
```

If none of these tools is installed and installation isn't possible, say so
and deliver the SVG with the exact command the user should run; do not
silently deliver only SVG as if it were submission-ready.

After converting, run the checker
(`python scripts/check_figure.py arch.pdf --width double`) and open the PDF
once: font substitution during conversion is the common failure. If the
target system lacks Arial/Helvetica, either accept the DejaVu substitution
consistently, or outline text for the submission copy
(`inkscape ... --export-text-to-path`) while keeping the text-as-text master.

## When not to hand-author

- Data-driven node-link graphs (dozens of nodes, computed layout): use
  `graphviz` or `networkx` + matplotlib, then restyle to the house tokens.
- Statistical/flow diagrams the venue templatizes (CONSORT, PRISMA): start
  from the official template structure; the `evidence-synthesis` skill covers
  PRISMA content.
- Pictorial/3D-illustrated concept art: that is the generative path; read
  `references/generative-images.md`.
