# Changelog

All notable changes to this repository are documented here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the repository
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Individual
skills carry their own version in their `SKILL.md`; this log tracks the collection.

## [Unreleased]

## [0.10.0] - 2026-09-12

The third release from the usage audit: the P2 items. Each one closes a gap
a transcript showed and none of them is large.

### Added
- `submission-formatter` (1.1.4 to 1.2.0): `build_targets.py` and
  `references/multi-venue-build.md`. One body, several venue packages from a
  spec: the author block per class from `AUTHORS.yaml` (elsarticle, sn-jnl,
  IEEEtran, generic), regions of the body dropped per target, `\citep`
  rewritten for non-natbib classes, assets and figures copied, and a guard
  that refuses to overwrite a `main.tex` edited by hand since the last
  render. `--check` runs `build-check` on each package with its page cap.
  `assets/targets.example.yaml` is the spec shape. This is the pipeline one
  paper repository had built by hand, generalized.
- `manuscript-figures` (1.1.3 to 1.2.0): placed-text checks in
  `check_figure.py`. Every label's box against the figure frame, its size at
  the target width (`--min-font-pt`, default 6), and label collisions, from
  poppler or PyMuPDF for PDFs and from `<text>` elements for SVGs. On a real
  schematic it reports a 194 mm drawing against a 174 mm Springer double
  column and confirms the labels survive the scaling. `--self-test`.
- `ml-eval-statistics` (1.0.2 to 1.1.0): `mde`, the minimum detectable
  effect for a paired comparison, with its standard error from the paired
  difference under one shared resample; the docstring says why an arm
  bootstrapped against itself understates it. `--self-test` runs the
  estimators on synthetic data (interval brackets the point, identical arms
  give zero, a real gap excludes zero, MDE equals the z-sum times the SE,
  Holm, ECE, the normal quantile).
- `data-engineering` (1.0.2 to 1.1.0): `references/research-data.md` (the
  cohort builder, the `F__available_at` feature contract, the split, the
  schema contract) and `scripts/leakage_guard.py`, which checks feature
  availability against the index time and group disjointness across folds,
  with `--poison` as the positive control that proves the guard fails on
  leaking data.
- `journal-advisor` (1.0.2 to 1.1.0): `assets/list-provenance.yaml` names
  what each bundled list is (a publisher list or an institution's agreement
  list, whose, exported when, and what that means for fees).
  `build_catalog.py` writes `list_kind`, `coverage_note`, and `fee_note`
  onto every row, the field block gains a "list and fee coverage" line, and
  the data notes name the lists. A strong journal outside them is outside
  the permitted set, not a poor fit.

### Changed
- `manuscript-editor` (1.2.0 to 1.2.1): the nine worked examples in
  SKILL.md are cut to three, since `references/manuscript-boundary.md`
  carries the full set by section and family; the skill file is back under
  its size before 1.2.0.
- `hpc-cluster` (2.0.1 to 2.0.2): a "not on a cluster?" section pointing
  local long jobs at `project-ledger`'s runbook discipline, with the job
  script patterns that transfer.
- Outside the repository: a global `~/.claude/CLAUDE.md` on the author's
  machine now carries the Windows shell rules (heredoc backslashes, cp1252
  stdout, PowerShell 5.1, the two pdftotext builds), the git staging rule,
  the no-dash and identity rules, and the skill routing convention. About a
  third of the failed tool calls in the audit were shell friction.

## [0.9.0] - 2026-09-12

The second release from the usage audit: the P1 items. A new skill for the
release-and-archive workflow, an identity gate against fabricated front
matter, the four revision chores that had been done by hand, a rename, the
prompts that used to bypass each skill written into its description, one
loading rule for the whole collection, and a fix for the runtime mirror
Codex reads.

### Added
- `release-archive` (1.0.0): from an internal research repository to a
  public reproducibility release with a DOI. `release_audit.py` fails a tree
  on secrets, restricted-data names, and a missing README or LICENSE, and
  warns on internal ids, milestone nomenclature, local paths, placeholders,
  ledger documents, large files, and a missing CITATION.cff.
  `zenodo_deposit.py` creates, versions, inspects, and validates deposits
  with the token from the environment only and creators from `AUTHORS.yaml`.
  `doi_writeback.py` puts the concept DOI into every waiting site and
  reports what is still a placeholder. References cover curation, Zenodo
  (concept versus version DOI, the GitHub integration), and availability
  statements by venue family including restricted data.
- `build-check` (1.0.0 to 1.1.0): identity and placeholder checks. Every
  email and ORCID in the front matter is checked against `AUTHORS.yaml`
  (`--authors`, or found automatically) and every listed author must appear;
  the PDF text is searched for author-input markers, TODO, TBD, DOI
  placeholders, and unresolved `??` references. Added after a fabricated
  author block derived from a login email reached a compiled PDF and a
  submission form.
- `manuscript-editor` (1.1.1 to 1.2.0): four modes and three scripts.
  Revision checklist (`make_checklist.py`: atomic items with stable ids from
  reviewer files and from a `submission-reviewer` fix list, statuses carried
  forward across rounds; the only approval stop in a round), budget (a page
  cap or word guidance met by ranked cut classes with re-measurement through
  `build-check`, `references/cutting-to-a-budget.md`), letter build
  (`build_letter.py`: cited section, table, and figure numbers checked
  against the `.aux`, quoted passages against the manuscript, no
  placeholders, no reviewer narration in the manuscript, then pandoc), and
  Word manuscripts (`docx_markers.py` for the red author-action markers and
  text extraction, `references/docx-revision.md` for what needs Word's
  Compare). Adds the identity rule for front matter.
- `submission-reviewer` (1.0.3 to 1.1.0): the report ends with a
  machine-readable fix list that `manuscript-editor` turns into the
  revision checklist, so the review and the revision share ids.
- `project-ledger` (1.0.0 to 1.1.0): `AUTHORS.yaml` template as the only
  source of author identity, scaffolded by `init`, with a P0 gate that it
  is filled and a submission gate that runs `build-check` with `--authors`.
- `scripts/sync_runtimes.py`: replaces stale copies of this repository's
  skills under other runtimes' roots (Codex reads `~/.agents/skills`) with
  directory junctions or symlinks to the folders here, leaves third-party
  skills alone, and retires renamed or deleted names. The Codex mirror had
  been seven commits behind main.

### Changed
- `research-paper-writing` renamed to `manuscript-writing` (3.0.0 to 4.0.0,
  breaking): the folder and name now match `manuscript-editor` and
  `manuscript-figures`. Every reference in the collection is updated; a
  `/research-paper-writing` invocation and a project routing file that names
  the old folder need the new name.
- Every skill: a loading-discipline section (load once per session, before
  the step it governs, never twice in one session; follow the repository's
  `docs/SKILL-ROUTING.md` when there is one; a brief that names several
  skills loads each at its step). PATCH bumps across the collection.
- Descriptions rewritten to match the prompts that used to bypass the
  skills: `manuscript-editor` (a pasted decision letter or external review,
  "cut it to N pages", "format the response letter as a PDF", Word
  manuscripts), `submission-reviewer` ("external review", "adversarial
  review", "score out of 100", re-running a pass), `manuscript-figures`
  ("plot", "chart", "make the figures publishable", precedence over general
  dataviz skills for print), `submission-formatter` (technical-check bounces,
  multi-venue packaging, identity from `AUTHORS.yaml`), `ml-eval-statistics`
  (use `eval_stats.py`, never hand-written bootstrap code),
  `data-engineering` (cohort builder, feature pipeline, leakage guard),
  `hpc-cluster` (local long jobs are `project-ledger`'s), `journal-advisor`
  (what the bundled lists are; fee coverage depends on the institution).
- Root README: usage example for `release-archive`; issue template gains the
  new skill.

## [0.8.0] - 2026-09-12

The first release shaped by a usage audit: 130 Claude Code sessions and 20
Codex sessions over the collection, read for what recurred and what failed.
Two new skills for the two workflows that had none, one merge, one rescope,
one removal.

### Added
- `build-check` (1.0.0): compile a manuscript or submission package and
  inspect the result the way an author would. `build_check.py` builds every
  target, triages the log (errors, undefined references, missing files,
  overfull boxes above a threshold, float warnings), counts pages against the
  venue cap and body words against the guidance, measures every text line,
  image, and drawing against the column edges the document itself
  establishes (so a table past the margin is reported by page with its
  overhang), maps every float to the page it landed on and flags floats in
  the references or outside their citing section, checks font embedding,
  compares derived PDFs with their sources by modification time, and renders
  every page into a thumbnail grid in `BUILD_REPORT.md`. The rule the skill
  enforces: a build is finished when the report exists and the flagged pages
  have been looked at, never when the compiler exits. References cover log
  triage, float placement (including why `[H]` is inert on a double-column
  float), recovering pages honestly, and reading the page images.
- `project-ledger` (1.0.0): the operating record of a multi-session research
  project. Templates for PLAN, PREREGISTRATION, DECISIONS (`D-NNN` with
  rejected alternatives and their cost), PROGRESS (`NNNN`, typed, gap-free),
  RESULTS-LOG (`R-NNNN`, interval required, citing `experiment-ledger` run
  ids), GATES (`CHECK`, `EXPECT`, `EVIDENCE`), RUNBOOK, AGENT, and
  SKILL-ROUTING. `project_ledger.py` scaffolds them, allocates ids, appends
  validated entries (a result without an interval is refused), verifies
  append-only history against git, runs gate checks and writes their
  evidence, prints a one-screen state, and generates the next session's
  continuation brief from the record, which is never committed. References
  cover ledger entries, gates with positive controls, long-running jobs
  (stop files, progress files, handing a command to the owner), the session
  bootstrap, and the hand-off.
- `investigating-sources` (1.1.0 to 1.2.0): two chore modes.
  `related-work-table` renders the comparative table that closes a
  related-work section from the verified source log
  (`related_work_table.py`, Markdown or LaTeX, `[AUTHOR INPUT]` for any
  cell not extracted at reading time). `reference-diet` plans a cut to a
  venue's cap (`reference_diet.py`): upgrade preprints with a published
  version, remove failed or unconfirmed sources, then related-work-only
  preprints and once-cited sources oldest first, and never a Methods,
  Results, or Discussion citation by rule. The source-log schema gains
  optional `summary` fields.
- `research-paper-writing` (2.1.0 to 3.0.0): `scripts/prose_lint.py`, which
  counts the mechanical tells per section (dashes, stock vocabulary,
  not-X-but-Y contrasts, triads, repeated openers, bold labels, announcing,
  one-line closers, hedge stacks, chatbot residue, revision narration) on
  `.md`, `.tex`, and `.txt`, stripping code, math, tables, and citations
  first.

### Changed
- `research-paper-writing` (3.0.0): absorbs the manuscript subset of
  `prose-naturalizer`. The skill now ends with a tell sweep ordered by how
  much one sighting justifies an edit, with em and en dashes, revision
  narration, and chatbot residue as hard rules. Adds the identity and
  metadata rule (author names, affiliations, emails, ORCIDs, funding, and
  ethics text come only from the user or a project file, never from session
  context) after a fabricated author block reached a compiled PDF. The
  description names the prompts that used to bypass the skill ("remove the
  em dashes", "AI-like sentences") and says not to load `prose-naturalizer`
  for a manuscript.
- `prose-naturalizer` (3.0.0, by hand, then 3.0.1): rewritten around why the
  tells exist, 25 patterns ordered strongest first with graded confidence;
  then scoped to non-academic prose, with the description saying not to load
  it for a manuscript.
- `evidence-synthesis` (1.1.0 to 2.0.0): rescoped to the formal review
  design (protocol, PRISMA-S search, screening log, appraisal, GRADE) and put
  on the collection's one citation checker. `verify_citations.py` is now a
  shim that parses a reference list or `.bib` into the source-log schema and
  delegates to `investigating-sources/scripts/check_citations.py`; the
  release zip ships a copy of the checker so the skill installs alone
  (`package_skills.py` gains a shared-files map). Same flags, plus
  `--write-log` and `--checker`.
- `submission-formatter` (1.1.3), `manuscript-figures` (1.1.2),
  `manuscript-editor` (1.1.1): hand off to `build-check` for the built PDF.
  `manuscript-editor` also names `project-ledger` as the home of the
  workflow vocabulary it strips from manuscripts.
- `experiment-ledger` (1.0.2): names `project-ledger` as the project record
  its run registry sits inside.
- Root README: usage examples for the new skills and the writing split, the
  one-checker note, and `build-check`'s tooling in the surface notes.

### Removed
- `deep-research`: deprecated since 0.2.0 and replaced by `evidence-synthesis`
  and `investigating-sources`; its 376 KB were still on disk, still in the
  catalog, and still being invoked by subagents. Deleted from the tree, the
  catalog, the issue template, and the release assets.

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
