# Generative images in manuscripts

Image-generation models produce striking conceptual art and are genuinely
useful for graphical abstracts and illustrative figures.

## Invocation

Two routes, in order of preference. Route B needs only an authenticated
Codex; Route A needs `OPENAI_API_KEY` in the environment. Never ask the user
to paste a key into chat, and never echo one.

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

Codex ships its own image-generation tool, and its subscription auth covers
it, so this route needs no `OPENAI_API_KEY` at all. Run it non-interactively,
piping the prompt on stdin to avoid quoting problems:

```bash
command -v codex >/dev/null || { echo "codex CLI not found"; }
mkdir -p figures/raw
codex exec --sandbox workspace-write --skip-git-repo-check <<'PROMPT'
Generate an image with OpenAI image generation (the current image model).

Prompt: "<prompt built per the section below>"

Requirements:
- Largest available size, high quality, landscape.
- Save the PNG to figures/raw/concept_v1.png relative to your working
  directory and print the absolute path.
- If a direct image-generation tool is unavailable to you, print exactly
  UNAVAILABLE: <reason>. Do not substitute a hand-drawn SVG, a matplotlib
  render, or a placeholder image.
PROMPT
test -s figures/raw/concept_v1.png && echo OK || echo "generation failed"
```

`--sandbox workspace-write` is what permits the write; the default run is
read-only and the file never lands. `--skip-git-repo-check` is only needed
outside a git repo.

That last requirement is not boilerplate. Told to produce an image with no
image tool available, a coding agent will cheerfully draw a matplotlib
approximation and report success. Name the failure mode, then verify the file
yourself: exists, non-trivial size, and correct pixel dimensions. Never claim
an image was generated without having looked at it.

Codex flags drift between versions (`codex --help`). If image generation is
genuinely unavailable, fall back to Route A, which needs a real
`OPENAI_API_KEY`: a ChatGPT-subscription Codex login does **not** yield
credentials that `api.openai.com` accepts, so there is no bridge between the
two routes.

## Prompt craft for figure-grade output

Generated images fail as figures for predictable reasons: busy backgrounds,
style mismatch with the rest of the manuscript, and concepts described in the
abstract rather than as objects. The prompt patterns below target each.

**Always specify:**

- **Style anchor**: "flat vector-style scientific illustration", "clean
  isometric technical illustration", "minimal line-art infographic style".
  Avoid "photorealistic" for anything conceptual; it reads as evidence.
- **Background**: "plain white background" (composites into a page; anything
  else fights the manuscript).
- **Palette**: give the manuscript's hexes: "restricted palette: #0072B2
  blue, #D55E00 orange accents, light grays".
- **Text**: current image models set short text accurately, so use it rather
  than designing around it. Quote the exact strings in the prompt and say
  where each one goes: *the left block is labelled "Encoder", the arrow above
  it reads "x12"*. Keep the strings short, and give a typographic instruction
  alongside them: *labels in a clean sans-serif, sentence case, small and
  unobtrusive, no drop shadows*. You proofread every glyph at the inspection
  step below, which is where a wrong one gets caught.
  Two things still argue for keeping specific labels out and overlaying them
  in vector afterward, and both are production decisions rather than distrust
  of the model: labels that must survive a reviewer asking for a rename
  without a re-roll, and labels that must match the manuscript's typeface
  exactly. Decide which you want before generating. Half the labels baked in
  and half overlaid in a different face is what actually looks amateur.
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
> patch labelled "CGM", emitting a smooth glucose waveform. Center: the
> waveform enters a minimal geometric controller block rendered as nested
> translucent layers suggesting a predictive model, labelled "Forecast", with
> a soft cone of uncertainty fanning out ahead of the curve, labelled "95%
> interval". Right: an insulin pump icon receiving a control signal, labelled
> "Pump". All four labels in a clean sans-serif, sentence case, small and
> unobtrusive, no drop shadows, placed clear of the artwork. Restricted
> palette: #0072B2 blue, #D55E00 orange for the uncertainty cone, light grays.
> Clean, minimal, generous negative space. No watermarks, no logos.

Generate 2–4 candidates (vary seed/wording, one variable at a time), show the
user, iterate on the winner. Edits/inpainting endpoints, where available,
preserve a good composition better than re-rolling from scratch.

## Post-processing to figure quality

1. **Inspect** for artifacts: mangled geometry, extra limbs on anything
   organic, and every rendered string proofread character by character
   against what you asked for, including the ones you did not ask for.
   Artifacts that would embarrass in print mean regenerate, not retouch.
2. **Compose at final size.** Place the PNG inside an SVG (or a matplotlib
   canvas) at final mm size and add the labels you deliberately kept out of
   the generation, plus leader lines and panel labels, as vector elements per
   `svg-diagrams.md`. Convert to PDF. One editable master, with sharp vector
   text exactly where you wanted it editable.
3. **Check resolution honestly.** Effective DPI = pixel width / printed width
   in inches. 1536 px across 89 mm (3.5 in) ≈ 438 DPI: fine. Across 183 mm ≈
   213 DPI: fails the 300 floor; regenerate larger or narrow the slot. Do not
   upscale.
4. **Verify**: `python scripts/check_figure.py abstract.pdf --width single`.

## Failure modes to name for the user

- No authenticated Codex and no `OPENAI_API_KEY` → stop and ask; there is no
  credential-free path, and the two routes do not share credentials.
- The image encodes a distinction by color alone (active vs inactive, chosen
  vs not, on vs off) → it collapses in grayscale print and for colorblind
  readers. Add the second cue in the vector layer, outlining or annotating the
  marked elements. That is faster and far more reliable than re-rolling until
  the model differentiates by shape.
- Model can't hit the concept after ~4 iterations → hybrid: generate only the
  pictorial element(s) small, build the structure in SVG.
- The "illustration" is drifting toward looking like data (a fake brain scan,
  a fake pathology slide) → stop; that fails the gate regardless of intent.
