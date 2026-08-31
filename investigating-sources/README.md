# investigating-sources

> Citation-honest research where every claim traces to a real, verified source.

[![Version](https://img.shields.io/badge/version-1.1.0-6E56CF)](../CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)

Part of **[claude-research-skills](../)** · by [@anayy09](https://github.com/anayy09)

## What it does

A rigorous research assistant that produces evidence-backed deliverables:
briefs, reports, literature reviews, fact-checks, source-verification audits, and
PRISMA-style systematic reviews, under two hard rules: **every claim is traced to
a real, verified source, and unconfirmable citations are caught rather than
emitted**, and **the peer-reviewed version of record is what gets cited**. It
searches IEEE Xplore, the Nature portfolio and SpringerLink, Elsevier, ACM,
Wiley, and PubMed before the open web, and upgrades a preprint to its published
version rather than citing numbers the authors revised during review.

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
- "Run a systematic review or meta-analysis"
- "Help me scope this vague question into an answerable one"

## Modes

`brief` · `report` · `lit-review` · `fact-check` · `verify` · `systematic` ·
`scope`. Pick one per run; see [`references/modes.md`](./references/modes.md).

## What's inside

```
investigating-sources/
├── SKILL.md               the 7-step workflow + 7 modes
├── references/            loaded on demand
│   ├── modes.md           full spec of every output mode
│   ├── scoping.md         framing answerable questions
│   ├── search_sources.md  where to look, in what order, with query recipes
│   ├── verification.md    source-log schema + verification decisions
│   ├── source_quality.md  evidence hierarchy and quality flags
│   ├── synthesis.md       integrating across sources
│   ├── reasoning_checks.md fallacy and bias catalog
│   ├── systematic_review.md PRISMA protocol
│   ├── writing_quality.md  prose standards, AI-tell patterns
│   └── audit.md           pre-delivery checklist
├── scripts/
│   ├── check_citations.py verify a source log (Crossref + DataCite + OpenAlex)
│   └── audit_report.py    cross-check a draft against its source log
├── assets/                output templates + blank source log
└── examples/
    └── brief_walkthrough.md full pipeline on a real question
```

## Scripts

Both are network-optional and degrade gracefully offline: structural checks still
run, and network-dependent checks are marked *skipped*, never silently passed.

```bash
# Verify every source in a log; non-zero exit if any FAILs
python investigating-sources/scripts/check_citations.py sources.json     --mailto you@institution.edu

# Find the peer-reviewed version of every preprint in the log
python investigating-sources/scripts/check_citations.py sources.json     --upgrade-preprints

# Refuse anything that is not peer reviewed
python investigating-sources/scripts/check_citations.py sources.json     --require-peer-reviewed

# Confirm a finished draft's citations all map to verified sources,
# and that every cited preprint is labelled as unreviewed in the prose
python investigating-sources/scripts/audit_report.py draft.md sources.json

# Check the checker's own logic, no network needed
python investigating-sources/scripts/check_citations.py --self-test
```

Live DOI resolution needs `requests` (`pip install requests`). The checker falls
back to DataCite when Crossref has no record, because arXiv registers there;
without that fallback every arXiv citation reads as a fabrication.

## Changelog

- **1.1.0**: Peer-reviewed-first sourcing. New `references/search_sources.md`
  gives the search order (domain databases, federated indexes, publisher
  platforms, preprints last) with query recipes for IEEE Xplore, the Nature
  portfolio and SpringerLink, Elsevier, ACM, Wiley, Europe PMC, and Crossref.
  `check_citations.py` gains a DataCite fallback so arXiv DOIs stop reading as
  fabrications, peer-review classification read from the registry record rather
  than the publisher's name, `--upgrade-preprints` to find the published version
  of record, `--require-peer-reviewed`, retraction checking against Crossref and
  OpenAlex, retries with backoff, `--mailto`, `--write`, and a `--self-test`.
  `audit_report.py` now fails a cited preprint whose published version exists
  and warns when a cited preprint is not labelled as unreviewed in the prose.
  The source-log schema gains `peer_reviewed` and `superseded_by`.
- **1.0.0**: Initial release.

---

Part of the **[claude-research-skills](../)** collection.
[Report an issue »](https://github.com/anayy09/claude-research-skills/issues/new/choose)
