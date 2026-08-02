# Changelog

All notable changes to this repository are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the repository
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Individual
skills carry their own version in their `SKILL.md`; this log tracks the collection.

## [Unreleased]

Nothing yet.

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

[Unreleased]: https://github.com/anayy09/claude-research-skills/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/anayy09/claude-research-skills/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/anayy09/claude-research-skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/anayy09/claude-research-skills/releases/tag/v0.1.0
