# Changelog

All notable changes to this repository are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the repository
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Individual
skills carry their own version in their `SKILL.md`; this log tracks the collection.

## [Unreleased]

## [0.5.2] - 2026-08-30

### Fixed
- `manuscript-figures` (1.1.0 to 1.1.1): `check_figure.py` failed any PDF that
  contains no text. It read the string `/Font` as evidence that fonts were
  referenced, but `/Font` is only a resource-dictionary key and matplotlib
  writes it even when the dictionary is empty, so a figure whose labels all
  live in an embedded raster was reported as "fonts referenced but no embedded
  FontFile found". Detection now keys on `/BaseFont`, which actually names a
  font object; the no-text case falls through to UNVERIFIED, as the tool's
  fail-closed design intends. The 1.1.0 change made this reachable in normal
  use, because letting the model render the labels is what produces a
  text-free PDF.

### Added
- `manuscript-figures`: the legibility arithmetic for model-rendered labels.
  Label size and effective DPI are locked together, since both scale with the
  printed width, so `label_pt x DPI = 100 x cap_height_px` is fixed at
  generation time and widening the figure never improves the pair. Clearing
  6 pt at 300 DPI needs a rendered cap height of at least 18 px, which is why
  the prompt guidance now asks for large labels rather than unobtrusive ones.
- `manuscript-figures`: two generative failure modes observed in practice.
  Hexes given in a prompt come back approximated rather than matched, with a
  recipe for snapping flat fills back to the exact palette; and artwork that
  encodes a distinction by color alone collapses in grayscale.

## [0.5.1] - 2026-08-30

### Changed
- `manuscript-figures` (1.0.0 to 1.1.0): generated figures may now carry their
  own text. The old rule banned text in generated images outright and required
  every label to be overlaid in vector afterward, on the assumption that models
  garble type. Current image models do not, and the ban was costing real
  capability, so the guidance now asks for the exact strings in the prompt plus
  a typographic instruction, and adds a proofread-every-glyph step to the
  inspection pass. Vector overlay remains the recommendation for labels that
  must stay editable after review or match the manuscript's typeface exactly.

### Fixed
- `manuscript-figures`: `figstyle.apply_style()` set `mathtext.fontset` to
  `dejavusans` while the rest of the figure used Arial, so any label containing
  `$...$` silently embedded a second typeface and broke the one-font rule the
  skill enforces everywhere else. Mathtext is now mapped onto whichever family
  actually resolves, with `resolve_family()` exposed for callers.
- `manuscript-figures`: the Codex CLI route is documented as it actually works.
  It needs `--sandbox workspace-write` to write the PNG at all, takes the prompt
  on stdin, and cannot fall back to the Images API, because a ChatGPT
  subscription login yields no credentials `api.openai.com` accepts.

## [0.5.0] - 2026-08-30

Thirteen active skills, one deprecated. The gap this closes is the one between
having results and having something a journal will print: figures built at final
size, in vector, with legible type and colorblind-safe color, checked
mechanically before they go up.

### Added
- `manuscript-figures` skill: produces publication-quality, journal-compliant
  figures and teaches the production discipline behind them. Three routed paths:
  data figures through a bundled matplotlib house-style module (`figstyle.py`)
  with mm-exact column sizing for Nature, Elsevier, Springer, IEEE, Science,
  NeurIPS and ICML, the Okabe-Ito cycle, panel labeling, and export helpers;
  schematics authored directly as SVG on a mm-true grid and converted to PDF;
  and conceptual art through OpenAI image generation via a local Codex CLI or
  the Images API, gated on the venue's own AI policy. `check_figure.py` is a
  standard-library checker that verifies physical dimensions against the target
  column, raster DPI, and PDF font embedding across PDF, EPS, SVG, PNG and TIFF,
  and fails closed: what it cannot verify is reported as UNVERIFIED rather than
  passed. The same style ships as `assets/manuscript.mplstyle` for anyone who
  prefers `plt.style.use()`.
- `submission-formatter` (1.0.0 to 1.1.0): recovers document structure from Word
  files that use custom style names instead of Word's built-in ones. Pandoc only
  promotes `Heading N`, so a manuscript built on a publisher template arrived
  with its outline collapsed and its reference list invisible; a second pass with
  `python-docx` reads the real style names and restores headings, which in turn
  makes the reference section findable. Numbered Word headings, which reach
  markdown as ordered-list items, are handled too.
- For LaTeX input, structural counts are now taken from the `.tex` itself and
  compared against the extraction, so anything the pandoc round-trip failed to
  reproduce is reported rather than silently undercounted.

### Changed
- `submission-formatter` (1.1.0 to 1.1.1), `submission-reviewer` (1.0.1 to
  1.0.2), `ml-eval-statistics` (1.0.0 to 1.0.1), `research-paper-writing` (2.0.0
  to 2.0.1), and `research-ideation` (1.0.1 to 1.0.2): each now hands off to
  `manuscript-figures` at the point where the artwork, rather than the prose,
  the numbers, or the template, is what needs work.

### Fixed
All found by running `submission-formatter` end to end against two real
manuscripts: a 61 KB LaTeX paper reformatted into Springer Nature `sn-jnl`, and a
DOCX review paper converted to IEEE Access.
- Figure captions were taken from Word's machine-written alt text, which put
  invented sentences ("A diagram of a process flow AI-generated content may be
  incorrect") into manuscript captions. The author's caption paragraph now wins.
- Grid tables were truncated to their first row, and the remaining rows leaked
  into the body as loose text, because the rule pattern rejected the alignment
  colons pandoc emits (`+====:+`). A 10-table paper extracted as 9, three of them
  single-row fragments.
- Figures never resolved: pandoc resolved relative image paths against the
  working directory rather than the manuscript, so `--extract-media` produced
  nothing and emitted placeholder spans that then vanished from the inventory. A
  figure whose file still cannot be found is now reported instead of dropped.
- `latexmk` was never told to run BibTeX, so a first build shipped with every
  citation undefined, and the passes that resolve citations and cross-references
  after BibTeX were not run either. The final log, not the accumulated output of
  earlier passes, is now what gets reported.
- `fidelity_check` fell back to a crude regex LaTeX reader without saying so,
  turning its own reader failure into a 24% "missing content" report. It now
  declares the fallback and frames the drift as an upper bound.
- All three scripts decoded subprocess output with the locale codec, crashing on
  Windows on the first non-ASCII byte pandoc emitted.

## [0.4.0] - 2026-08-04

Twelve active skills, one deprecated. The submission chain is now complete: pick a
venue, review the manuscript, then format it for that venue.

### Added
- `submission-formatter` skill: reformats a finished manuscript into a specific
  journal or conference template, in LaTeX or Word, without changing what it says.
  Ingests PDF, DOCX, LaTeX, Markdown, ODT, and RTF into a structured intermediate
  representation; asks once for the publisher template and otherwise locates the
  official one; inspects the template into an explicit requirements sheet; maps
  sections with merges applied automatically and splits proposed for confirmation;
  and ends with a mechanical fidelity check over the sentence stream, the numeric
  token multiset, citation markers, and structural counts. A seven-rule fidelity
  contract governs the whole pipeline: content is copied rather than regenerated,
  numbers are immutable, missing items become `TODO(author)` markers instead of
  plausible text, nothing is deleted to fit a length limit, and every deviation
  lands in `FORMAT_REPORT.md`. Template locations, class names, and quirks are
  mapped for IEEE, Elsevier, Springer Nature, Springer LNCS, MDPI, Wiley, Taylor &
  Francis, ACM, PLOS, Frontiers, IOP, APS/AIP, Oxford, SAGE, and Cambridge.

### Changed
- `journal-advisor`, `submission-reviewer`, and `research-ideation` (1.0.0 to
  1.0.1): each now hands off to `submission-formatter` at the point where the
  manuscript has to go into a venue's template.
- The README's API-surface note covers `submission-formatter`, which needs network
  access to fetch templates and shells out to `pandoc` and `latexmk`, so a
  sandboxed surface needs the template supplied and cannot run the build step.

### Fixed
- `scripts/validate_skills.py` no longer crashes on its own success message on a
  Windows console, where cp1252 cannot encode the status glyphs.

## [0.3.0] - 2026-08-02

Eleven active skills, one deprecated. Two skills were renamed in this release, so
remove the old folders from any local install.

### Added
- `research-ideation` skill: a research strategist that inventories the user's
  existing assets, generates candidate directions from a catalog of 23 ideation
  operators, verifies the novelty delta against real prior work, scores and ranks
  on six weighted dimensions with cap rules, and produces a per-direction path to
  submission (gap ledger, headline table, minimum evidence set, kill experiment,
  reviewer objections, and a backward schedule against the deadline).
- `submission-reviewer` skill: fair, constructive peer review of a paper or
  patent submission against a weighted rubric, with a score out of 100 and band,
  verified-only novelty checks against prior art, authenticity and internal
  consistency checks, cap rules for blocking flaws, partial scoring for
  incomplete submissions, and ranked fixes with a projected score.
- Prebuilt release archives. `scripts/package_skills.py` builds one uploadable
  zip per skill plus a combined bundle, rooted at the skill folder as claude.ai
  requires, and `.github/workflows/release.yml` attaches them to every tagged
  release with checksums. The README catalog links each skill's download
  directly, so installing into a Claude chat no longer means cloning and zipping
  by hand.

### Changed
- Renamed `hipergator-hpc` to `hpc-cluster` and generalized it to any HPC site
  (1.0.0 to 2.0.0). Breaking: the folder and skill name changed.
  Institution-specific paths, accounts, QoS names, and wrapper commands are gone,
  replaced by filesystem roles (`$HOME`, `$SCRATCH`, `$PROJECT`, `$TMPDIR`),
  behavior-based priority tiers, and an explicit discovery step. Added
  `references/scheduler-portability.md` mapping SLURM to PBS/Torque, LSF, and
  SGE, plus new coverage of containers, scratch purge policies, accounting units,
  and staging model weights for compute nodes without network access.
  `references/storage-and-permissions.md` is now
  `references/storage-and-scratch.md`, and `gen_sbatch.py` gained `--module` and
  `--activate` in place of hardcoded conda and filesystem assumptions.
- Renamed the `humanizer` skill to `prose-naturalizer` (1.0.0 to 2.0.0).
  Breaking: the folder and skill name changed.
- Rewrote the repository README so it is not scoped to Claude Code. Agent Skills
  is an open format, so installation is documented per surface (the Claude apps,
  filesystem agents, and the Claude API), with the caveat that skills do not sync
  between them and a note on which scripts need network access.
- `experiment-ledger` (1.0.0 to 1.0.1): the config template's example paths are
  now `${PROJECT}` and `${SCRATCH}` rather than one site's mount points.
- `data-engineering` (1.0.0 to 1.0.1): summary wording only.

### Deprecated
- `deep-research` (2.9.3 to 2.10.0) in favor of `evidence-synthesis` (formal
  reviews) and `investigating-sources` (citation-honest research). It still works
  during a transition period but will receive no further updates.

## [0.2.0] - 2026-07-26

### Added
- `evidence-synthesis` skill: plan, run, appraise, and report systematic and
  other evidence syntheses (PRISMA-S search reporting, PRISMA 2020 flow, RoB tool
  selection, GRADE certainty, executable citation/retraction verification, and
  RAISE-compliant AI-use disclosure).

## [0.1.0] - 2026-07-25

First public release of the collection.

### Added
- Nine skills: `data-engineering`, `deep-research`, `experiment-ledger`,
  `hipergator-hpc`, `humanizer`, `investigating-sources`, `journal-advisor`,
  `ml-eval-statistics`, `research-paper-writing`.
- A README per skill, and a flagship README with an auto-generated skill catalog.
- `scripts/generate_catalog.py` to keep the catalog in sync with skill frontmatter.
- Contributing guide, code of conduct, security policy, issue/PR templates, and
  a CI workflow that validates every skill's structure and frontmatter.

### Changed
- Standardized every skill's frontmatter: added `summary`, semantic `version`,
  `author`, `license`, and a consistent `metadata` block.

[Unreleased]: https://github.com/anayy09/claude-research-skills/compare/v0.5.2...HEAD
[0.5.2]: https://github.com/anayy09/claude-research-skills/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/anayy09/claude-research-skills/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/anayy09/claude-research-skills/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/anayy09/claude-research-skills/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/anayy09/claude-research-skills/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/anayy09/claude-research-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/anayy09/claude-research-skills/releases/tag/v0.1.0
