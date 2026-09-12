# investigating-sources

> Citation-honest research: verified sources, version of record, related-work tables, reference diets.

[![Version](https://img.shields.io/badge/version-1.2.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

A rigorous research assistant that produces evidence-backed deliverables:
briefs, reports, literature reviews, fact-checks, source-verification audits,
and PRISMA-style reviews, under two hard rules: **every claim is traced to a
real, verified source, and unconfirmable citations are caught rather than
emitted**, and **the peer-reviewed version of record is what gets cited**. It
searches IEEE Xplore, the Nature portfolio and SpringerLink, Elsevier, ACM,
Wiley, and PubMed before the open web, and upgrades a preprint to its published
version rather than citing numbers the authors revised during review.

It also owns the two reference chores that arrive before every submission:
the **related-work summary table**, rendered from the verified source log so
every row is a real source and every empty cell is marked for the author, and
the **reference diet**, which brings a list down to a venue's cap by upgrading
preprints to their version of record and removing what the rules allow, and
hands the author anything the rules do not.

This skill owns the collection's one citation checker. `evidence-synthesis`
calls it through a shim and is reserved for the formal review design
(protocol, screening log, appraisal, GRADE).

## Why it exists

Three failure modes make AI research untrustworthy: fabricated citations,
overconfident synthesis, and sourcing from whatever surfaced first. This skill
attacks all three. It catches fabricated sources with independent verification
against two registries plus executable checks. It disarms overconfidence by
requiring disconfirming search, disclosure of conflicting evidence, and explicit
limitations. And it fixes sourcing by searching the peer-reviewed record before
the open web, reading peer-review status from the registry rather than from the
publisher's name, and citing the published version rather than the preprint.

## When Claude uses it

- "Research this topic, with citations"
- "Find peer-reviewed sources on X" / "are any of these preprints published now?"
- "Verify / fact-check these claims"
- "Are these sources (or DOIs) real?"
- "Build a bibliography" / "grade these sources"
- "Add a summary table of the related work"
- "Trim the references to around 40, preprints first" / "replace the arXiv citations with the published versions"
- "Help me scope this vague question into an answerable one"

## Modes

`brief` · `report` · `lit-review` · `fact-check` · `verify` · `systematic` ·
`scope` · `related-work-table` · `reference-diet`. Pick one per run; see
[`references/modes.md`](./references/modes.md).

## What's inside

```
investigating-sources/
├── SKILL.md               the 7-step workflow + 9 modes
├── references/            loaded on demand
│   ├── modes.md           full spec of every output mode
│   ├── scoping.md         framing answerable questions
│   ├── search_sources.md  where to look, in what order, with query recipes
│   ├── verification.md    source-log schema (with summary fields) + verification decisions
│   ├── source_quality.md  evidence hierarchy and quality flags
│   ├── synthesis.md       integrating across sources
│   ├── reasoning_checks.md fallacy and bias catalog
│   ├── systematic_review.md PRISMA protocol (light form; the formal design is evidence-synthesis)
│   ├── writing_quality.md  prose standards, AI-tell patterns
│   └── audit.md           pre-delivery checklist
├── scripts/
│   ├── check_citations.py     verify a source log (Crossref + DataCite + OpenAlex); the collection's one checker
│   ├── audit_report.py        cross-check a draft against its source log
│   ├── related_work_table.py  render the comparative table from the verified log (md or LaTeX)
│   └── reference_diet.py      plan a cut to a cap: upgrade, remove by rule, hand the rest to the author
├── assets/                output templates + blank source log
└── examples/
    └── brief_walkthrough.md full pipeline on a real question
```

## Scripts

All four are standard library and network-optional; structural checks run
offline and network-dependent checks are marked *skipped*, never silently
passed.

```bash
# Verify every source in a log; non-zero exit if any FAILs
python investigating-sources/scripts/check_citations.py sources.json --mailto you@institution.edu

# Find the peer-reviewed version of every preprint and record it in the log
python investigating-sources/scripts/check_citations.py sources.json --upgrade-preprints --write

# Refuse anything that is not peer reviewed
python investigating-sources/scripts/check_citations.py sources.json --require-peer-reviewed

# Confirm a finished draft's citations all map to verified sources
python investigating-sources/scripts/audit_report.py draft.md sources.json

# The related-work table, LaTeX form, rows only for keys the draft cites
python investigating-sources/scripts/related_work_table.py sources.json --format tex --only-cited paper/main.tex

# The reference diet: plan a cut to 40, write the pruned .bib
python investigating-sources/scripts/reference_diet.py refs.bib paper/main.tex --cap 40 \
    --sources sources.json --write-bib refs.pruned.bib

# Each script checks its own logic without a network
python investigating-sources/scripts/check_citations.py --self-test
python investigating-sources/scripts/related_work_table.py --self-test
python investigating-sources/scripts/reference_diet.py --self-test
```

Live DOI resolution needs `requests` (`pip install requests`). The checker falls
back to DataCite when Crossref has no record, because arXiv registers there;
without that fallback every arXiv citation reads as a fabrication.

## Changelog

- **1.2.0**: Two chore modes. `related-work-table` renders the comparative
  table that closes a related-work section from the verified source log
  (`related_work_table.py`, Markdown or LaTeX `tabularx`, rows only for
  confirmed sources, `[AUTHOR INPUT]` for any cell not extracted at reading
  time, preprints marked with their version of record). `reference-diet` plans
  a cut to a venue's cap (`reference_diet.py`): upgrade preprints with a
  published version, remove failed or unconfirmed sources, then
  related-work-only preprints and related-work-only once-cited sources oldest
  first, and never cut a Methods, Results, or Discussion citation by rule. The
  source-log schema gains optional `summary` fields. This skill's
  `check_citations.py` is now the collection's one citation checker;
  `evidence-synthesis` delegates to it. The description names the prompts
  these modes answer and the boundary with `evidence-synthesis`.
- **1.1.0**: Peer-reviewed-first sourcing, DataCite fallback, peer-review
  classification from the record, `--upgrade-preprints`,
  `--require-peer-reviewed`, retraction checking, `--self-test`.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
