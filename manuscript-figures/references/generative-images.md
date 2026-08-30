# Generative images in manuscripts

Image-generation models produce striking conceptual art and are genuinely
useful for graphical abstracts and illustrative figures.

## Invocation

Two routes, in order of preference. Both need `OPENAI_API_KEY` in the
environment (or Codex authenticated); never ask the user to paste a key into
chat, and never echo it.

### Route A: OpenAI Images API directly

Simplest and most controllable when a key is available:

```bash
curl -s https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "<current-image-model>",
    "prompt": "<prompt built per the section below>",
    "size": "1536x1024",
    "quality": "high"
  }' | python3 -c "
import sys, json, base64
r = json.load(sys.stdin)
if 'data' not in r: raise SystemExit(json.dumps(r.get('error', r), indent=2))
open('figures/raw/concept_v1.png','wb').write(base64.b64decode(r['data'][0]['b64_json']))
print('wrote figures/raw/concept_v1.png')"
```

Model names, sizes, and response fields drift; if the call errors, check the
current API reference rather than retrying blind. Request the largest size
the API offers; more pixels means more headroom for the 300 DPI floor.

### Route B: local Codex CLI (Recommended)

When the user works through Codex (its subscription auth covers the API), run
it non-interactively and delegate the API call to it:

```bash
command -v codex >/dev/null || { echo "codex CLI not found"; }
codex exec "Generate an image with OpenAI image generation (the
current image model). Prompt: '<prompt>'. Largest available size, high
quality. Save the PNG to $(pwd)/figures/raw/concept_v1.png and print the path.
If direct image generation is unavailable, write and run a minimal script
calling the OpenAI Images API with the environment's credentials."
test -s figures/raw/concept_v1.png && echo OK || echo "generation failed"
```

Codex flags and capabilities vary by version (`codex --help`; some versions
want an approval/sandbox flag such as `--full-auto` for non-interactive
writes). Treat Codex as a subcontractor: give it the prompt, the exact output
path, and the size requirement; verify the file exists and is non-trivial
afterward. Never claim the image was generated without having verified the
file.

## Prompt craft for figure-grade output

Generated images fail as figures for predictable reasons: garbled text, busy
backgrounds, style mismatch with the rest of the manuscript. The prompt
patterns below target each.

**Always specify:**

- **Style anchor**: "flat vector-style scientific illustration", "clean
  isometric technical illustration", "minimal line-art infographic style".
  Avoid "photorealistic" for anything conceptual; it reads as evidence.
- **Background**: "plain white background" (composites into a page; anything
  else fights the manuscript).
- **Palette**: give the manuscript's hexes: "restricted palette: #0072B2
  blue, #D55E00 orange accents, light grays".
- **NO TEXT**: "no text, no labels, no letters, no numbers, no watermarks".
  Models still typo text in images; all wording gets overlaid in vector
  afterward, which also keeps labels editable and crisp.
- **Composition**: aspect and reading direction: "wide 3:2 composition, main
  subject center-left, negative space on the right for labels".
- **Content, concretely**: name the objects and their relationships, not the
  abstraction. Not "federated learning" but "five stylized hospital
  buildings arranged in a ring, each connected by glowing arcs to a central
  abstract neural-network sphere, data symbolized as small geometric
  particles flowing along the arcs".

**Example (graphical abstract, uncertainty-aware glucose control):**

> Flat vector-style scientific illustration, plain white background, wide 3:2
> composition. Left: a stylized human torso silhouette with a small sensor
> patch, emitting a smooth glucose waveform. Center: the waveform enters a
> minimal geometric controller block rendered as nested translucent layers
> suggesting a predictive model, with a soft cone of uncertainty fanning out
> ahead of the curve. Right: an insulin pump icon receiving a control signal.
> Restricted palette: #0072B2 blue, #D55E00 orange for the uncertainty cone,
> light grays. Clean, minimal, generous negative space. No text, no labels,
> no letters, no watermarks.

Generate 2–4 candidates (vary seed/wording, one variable at a time), show the
user, iterate on the winner. Edits/inpainting endpoints, where available,
preserve a good composition better than re-rolling from scratch.

## Post-processing to figure quality

1. **Inspect** for artifacts: mangled geometry, accidental text-like glyphs,
   extra limbs on anything organic. Artifacts that would embarrass in print
   mean regenerate, not retouch.
2. **Compose in vector.** Place the PNG inside an SVG at final mm size and
   add all text, arrows, and panel labels as vector elements per
   `svg-diagrams.md`. Convert to PDF. This yields sharp text over the raster
   and one editable master.
3. **Check resolution honestly.** Effective DPI = pixel width / printed width
   in inches. 1536 px across 89 mm (3.5 in) ≈ 438 DPI: fine. Across 183 mm ≈
   213 DPI: fails the 300 floor; regenerate larger or narrow the slot. Do not
   upscale.
4. **Verify**: `python scripts/check_figure.py abstract.pdf --width single`.

## Failure modes to name for the user

- No `OPENAI_API_KEY` and no authenticated Codex → stop and ask; there is no
  key-free path.
- Model can't hit the concept after ~4 iterations → hybrid: generate only the
  pictorial element(s) small, build the structure in SVG.
- The "illustration" is drifting toward looking like data (a fake brain scan,
  a fake pathology slide) → stop; that fails the gate regardless of intent.
