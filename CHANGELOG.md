# Changelog

All notable changes to this repository are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the repository
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Individual
skills carry their own version in their `SKILL.md`; this log tracks the collection.

## [Unreleased]

### Added
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

[Unreleased]: https://github.com/anayy09/claude-research-skills/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/anayy09/claude-research-skills/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/anayy09/claude-research-skills/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/anayy09/claude-research-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/anayy09/claude-research-skills/releases/tag/v0.1.0
