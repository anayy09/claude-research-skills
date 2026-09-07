# Changelog

All notable changes to this repository are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the repository
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Individual
skills carry their own version in their `SKILL.md`; this log tracks the collection.

## [Unreleased]

## [0.7.1] - 2026-09-06

### Changed
- `manuscript-editor` (1.0.0 to 1.1.0): the check is now a paragraph-level
  editorial read, with the audit script as its instrument rather than its
  substitute. The skill previously treated reviewer-facing language as the
  thing to catch; that is the rarest failure in a careful draft. Five more
  families of non-manuscript text are now named, none of which mentions a
  reviewer: editorial self-commentary ("we would rather say so than bank the
  pass"), protocol refrain ("declared before the first run", restated at every
  result), reader management ("this must not be read as"), internal workflow
  artifacts (decision ids, plan vocabulary, repository paths), and pre-emptive
  objection sections. Adds rules for the summary budget, the job a citation has
  to do, paragraph continuity, and what a caption may say.
- `manuscript-editor`: `audit_manuscript.py` gains ten checks: one per new
  family, plus recurring distinctive phrases (one argument living in several
  homes, which the sentence-level duplicate check cannot see), summary
  paragraphs, captions that argue, citation density with once-only references,
  and limitations length.
- `manuscript-editor`: new `references/editorial-read.md` (three questions per
  paragraph, three running indexes, section and manuscript tests, cut
  decisions) and `assets/editorial-report.md` for the prioritized cut list,
  which is delivered before any cut is made.

### Fixed
- `manuscript-editor`: a decimal that ended a sentence was invisible to the
  abstract-number check, because the guard after the number rejected a
  following full stop as well as a following digit. A body sentence reading
  "The external AUROC was 0.812." did not satisfy the search, so a headline
  number that was present in the body was reported as missing from it, in the
  check whose whole job is catching a number that was dropped in revision. The
  same guard also hid those numbers from the new summary-paragraph check.
- `manuscript-editor`: the pre-emptive-objection detector did not match the
  objection frame the skill itself documents as the family F example, because
  the anchored patterns did not allow for the markdown emphasis the device is
  normally typeset with, and required "your X is/are" rather than any
  accusation. It now tolerates leading markup and recognizes a fully
  emphasized opening sentence followed by a rebuttal.
- `manuscript-editor`: section detection no longer splits a bibliography into
  one section per citation line, and no longer reads a PDF axis label or table
  stub as a heading.

## [0.7.0] - 2026-09-05

A new skill for the part of publishing that happens after the reviews arrive,
and the boundary drawn between it and the skill that writes the sentences.

### Added
- `manuscript-editor` (1.0.0): manuscript-level editorial discipline for
  revision rounds. Three containers with a hard boundary (manuscript, response
  to reviewers, internal revision ledger) and the test for which one a sentence
  belongs in; a workflow that audits before touching anything, triages comments
  into atomic items with an explicit change type, locates the single home for a
  point before writing, makes the smallest complete change, and ends with a
  whole-manuscript coherence pass; redundancy and length rules; and integrity
  rules that put `[AUTHOR INPUT: ...]` where a number, reference, or decision
  is missing rather than inventing one.
- `manuscript-editor`: `audit_manuscript.py`, a standard-library audit for
  `.md`, `.tex`, `.docx`, and `.txt`. Reports the section outline with word
  counts, revision-commentary leaks, near-duplicate sentences, terminology
  variants, acronym problems, display-item order and orphans, hedge density,
  abstract numbers absent from the body, and outstanding placeholders. `--strict`
  exits non-zero while any leak remains, so it works as a submission gate.
- `manuscript-editor`: four references covering the leak catalog with
  before/after pairs by section, the manual coherence pass the script cannot
  do, venue conventions separated into general principles and family-specific
  rules (Nature, Science, Cell, medical journals, IEEE, ACM, Elsevier,
  Springer/PLOS, ML conferences), and the structure of the response letter;
  plus ledger and response templates.

### Changed
- `research-paper-writing` (2.0.1 to 2.1.0): gains a scope section stating that
  it owns the prose and not placement, scope of change, or whole-manuscript
  coherence. The rebuttal section now says the account of what changed lives
  only in the response letter, and the revised manuscript never narrates its own
  revision. Rewriting starts by checking whether the manuscript already makes
  the point somewhere else, since a point stated twice reads as patching and the
  two copies drift apart in later rounds.
- `submission-reviewer` (1.0.2 to 1.0.3) and `submission-formatter` (1.1.1 to
  1.1.2) hand off to `manuscript-editor` at the point where the revision itself,
  rather than the score or the template, is the work. The marked-up copy stays
  with `submission-formatter`, built from an already-revised manuscript.

- `prose-naturalizer` (2.0.0 to 2.0.1): rewritten in plainer language. The same
  31 patterns in the same order, with headings that name the problem rather
  than label it, an explicit rewrite process, and a check that the rewrite
  neither added nor lost a fact, number, quote, or citation.

### Fixed
- `prose-naturalizer`: the frontmatter description was a block scalar whose
  first line was indented one space and the rest two, so every continuation
  line loaded with a stray leading space, and its last sentence ended mid-quote.
- Version badges in `data-engineering` and `manuscript-figures` READMEs had
  drifted behind the versions in their `SKILL.md`.

## [0.6.0] - 2026-08-31

Both research skills now prefer the peer-reviewed record over preprints, and
both citation checkers were hardened against the failure modes that made them
either miss real problems or invent them.

### Added
- `evidence-synthesis` (1.0.0 to 1.1.0): new reference `peer-reviewed-sources.md`
  covering the version of record, the mechanical preprint-to-published upgrade,
  publisher-native search surfaces, and Crossref member IDs for publisher-scoped
  queries (IEEE 263, Elsevier 78, Springer Nature 297, ACM 320, Wiley 311, all
  confirmed against the live API).
- `evidence-synthesis`: `search_builder.py` renders seven more platforms, for
  thirteen total. Added SpringerLink and the Nature portfolio, Elsevier
  ScienceDirect, the ACM Digital Library, Wiley Online Library, Europe PMC, and
  a Crossref REST supplement. A new `--peer-reviewed-only` mode emits each
  platform's publication-type restriction (`NOT preprint[pt]`, `DOCTYPE`, `DT=`,
  `NOT SRC:PPR`, `filter=type:journal-article`) and names the UI facet where the
  platform has no query-syntax equivalent.
- `evidence-synthesis`: `search_builder.py` warns about the platform quirks that
  return a plausible but wrong result set rather than an error: SpringerLink has
  no truncation operator, ScienceDirect caps Boolean connectors per field, and
  IEEE Xplore command search silently truncates long OR-chains.
- `evidence-synthesis`: `verify_citations.py` gains `--upgrade-preprints`
  (Crossref `is-preprint-of`, the bioRxiv/medRxiv API, OpenAlex `locations`),
  `--require-peer-reviewed`, and a per-reference peer-review status reported
  separately from the verdict.
- `investigating-sources` (1.0.0 to 1.1.0): new reference `search_sources.md`
  giving the search order (domain databases, federated indexes, publisher
  platforms, preprints last, web last) with query recipes and a table of the
  keyless APIs a script can actually call.
- `investigating-sources`: `check_citations.py` gains `--upgrade-preprints`,
  `--require-peer-reviewed`, `--mailto`, `--write`, `--self-test`, retraction
  checking against Crossref and OpenAlex, and peer-review classification.
- `investigating-sources`: `audit_report.py` now hard-fails a cited preprint
  whose peer-reviewed version exists, and warns when a cited preprint is not
  described as unreviewed in the paragraph that cites it.
- Both skills: `--self-test` on every script, covering the verdict ladders, the
  peer-review classifier, the reference parser, and the platform renderers.

### Fixed
- Both citation checkers reported **every arXiv DOI as nonexistent**. arXiv
  registers with DataCite, not Crossref, so a Crossref-only lookup 404s on a
  real paper and the scripts read that as fabrication. Both now fall back to
  DataCite before failing anything, and `verify_citations.py` reconstructs the
  registered DOI from a bare `arXiv:2401.01234` string so those references get
  checked rather than skipped.
- `investigating-sources`: the title-comparison used for finding a replacement
  DOI accepted containment, which matched "Attention Is All You Need" to
  "Attention is all you need: utilizing attention in AI-enabled drug discovery",
  a different paper by different authors in a different field. Promoting that
  would have fabricated a citation while appearing to fix one. Replacement now
  requires near-identity plus a first-author match; the lenient containment
  check is kept for verifying a DOI the user already has, where it is correct.
- Both skills: transient network failures are retried with backoff instead of
  producing an `UNCHECKED` that reads like a finding. A 404 is never retried,
  since the server already answered.

### Changed
- Peer-review status is read from the registry record (`type`, `subtype`,
  `resourceTypeGeneral`, `primary_location.source.type`), never from the
  publisher's name. SSRN sits under Elsevier's DOI prefix and TechRxiv under
  IEEE's, so a publisher filter admits working papers while excluding
  peer-reviewed society journals.
- `investigating-sources`: the source-log schema gains `peer_reviewed` and
  `superseded_by`. Existing logs keep working; the fields are written by the
  checker.
- `investigating-sources`: the SEARCH step now specifies an explicit search
  order rather than "prefer primary and peer-reviewed sources", and the
  non-negotiables gain "the peer-reviewed record comes first".
- `evidence-synthesis`: "Three rules" became four, with the version-of-record
  rule added, and the anti-pattern table gained five entries.

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

[Unreleased]: https://github.com/anayy09/claude-research-skills/compare/v0.7.1...HEAD
[0.7.1]: https://github.com/anayy09/claude-research-skills/compare/v0.7.0...v0.7.1
[0.7.0]: https://github.com/anayy09/claude-research-skills/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/anayy09/claude-research-skills/compare/v0.5.2...v0.6.0
[0.5.2]: https://github.com/anayy09/claude-research-skills/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/anayy09/claude-research-skills/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/anayy09/claude-research-skills/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/anayy09/claude-research-skills/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/anayy09/claude-research-skills/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/anayy09/claude-research-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/anayy09/claude-research-skills/releases/tag/v0.1.0
