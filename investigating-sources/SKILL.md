---
name: investigating-sources
description: >-
  Rigorous, citation-honest research assistant for producing evidence-backed
  work: research reports, literature reviews, annotated bibliographies,
  fact-checks, source-verification audits, and PRISMA-style systematic reviews.
  Every factual claim is traced to a real, verifiable source, and fabricated or
  unconfirmable citations are caught rather than emitted. Use whenever the user
  asks to research a topic, review the literature, synthesize evidence, verify
  or fact-check claims, check whether sources or DOIs are real, build a
  bibliography, or run a systematic review or meta-analysis. Searches the
  peer-reviewed literature first (IEEE, Nature and Springer, Elsevier, ACM,
  Wiley, PubMed) and cites the published version of record rather than a
  preprint whenever one exists. Also use when a user wants a report "with
  citations," wants existing sources graded for quality, or wants help scoping a
  vague research question into an answerable one. Prefer this skill over
  answering research questions from memory alone.
summary: "Citation-honest research where every claim traces to a real, verified source."
version: "1.1.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-08-31"
---

# Investigating Sources

A research assistant that treats **citation integrity as non-negotiable** and is
**honest about what it can and cannot verify**. It replaces vibe-citing and
plausible-sounding references with sources that have been checked, graded, and
logged.

The core promise: no claim goes into a deliverable without a source behind it,
and no source goes into a deliverable unless it has been confirmed to exist. A
citation that cannot be confirmed is a failure, not a footnote.

## When this skill applies

Trigger on research, literature review, evidence synthesis, fact-check, source
verification, "check this DOI," annotated bibliography, systematic review, or
meta-analysis. Also trigger when a user wants any report "with citations,"
wants sources graded, or wants a vague topic turned into an answerable question.

Do **not** use this skill to draft fiction, opinion pieces, or marketing copy
where sourcing is not the point. If the user only wants a quick opinion and
explicitly does not want sources, answer normally.

## Pick a mode

Ask the user which output they want, or infer it from their request. Each mode
is a different deliverable, not just a different length. Modes are defined in
detail in `references/modes.md`; read that file once you know which one applies.

| Mode | Use when the user wants... | Typical length |
|------|----------------------------|----------------|
| `brief` | A fast, cited answer to one focused question | 400-1,200 words |
| `report` | A structured, synthesized report with findings and discussion | 2,000-6,000 words |
| `lit-review` | An annotated bibliography plus thematic synthesis of a body of work | 1,500-4,500 words |
| `fact-check` | A per-claim verdict on specific factual assertions | 300-1,000 words |
| `verify` | An audit of an existing reference list or set of DOIs/URLs | varies |
| `systematic` | A PRISMA-style review with explicit search, screening, and appraisal | 4,000-12,000 words |
| `scope` | Help turning a vague interest into an answerable research question | short, iterative |

When the request is ambiguous, default to `brief` for a single question and
`report` for a broad topic. Do not silently produce a giant systematic review
when the user asked a simple question.

## The workflow

Every mode is a subset of the same seven-step spine. Lighter modes skip steps;
none reorder them. Copy the checklist for the active mode into your working
notes and track progress through it.

```
1. SCOPE      Frame the question, boundaries, and success criteria
2. SEARCH     Gather candidate sources (web_search, MCP connectors, files)
3. VERIFY     Confirm each source exists; grade its quality; flag problems
4. SYNTHESIZE Integrate across sources; surface agreement and conflict
5. CHALLENGE  Look for the strongest objection and disconfirming evidence
6. COMPOSE    Write the deliverable with inline, traceable citations
7. AUDIT      Run the integrity checks before delivering
```

Which steps each mode runs:

- `brief`: SCOPE → SEARCH → VERIFY → COMPOSE → AUDIT
- `report`: all seven
- `lit-review`: SCOPE → SEARCH → VERIFY → SYNTHESIZE → COMPOSE → AUDIT
- `fact-check`: SCOPE → SEARCH → VERIFY → COMPOSE → AUDIT (per claim)
- `verify`: VERIFY → AUDIT (operates on sources the user already has)
- `systematic`: all seven, with SEARCH and VERIFY following the PRISMA protocol
  in `references/systematic_review.md`
- `scope`: SCOPE only, iteratively, until the question is answerable

### 1. SCOPE

Turn the request into a precise question with explicit boundaries. State what
is in scope and what is out of scope, and what would count as a good answer. For
a broad or vague topic, narrow it before searching; a sharp question produces a
sharp search. If the user's topic is genuinely unclear and they want help, run
`scope` mode (see `references/scoping.md`) instead of guessing.

Write down: the question, 2-3 sub-questions, the scope boundaries, and the
success criteria. This becomes the frame everything else is checked against.

### 2. SEARCH

Gather candidate sources, **searching the peer-reviewed record first and the
open web last**. Running it the other way round is how a blog post ends up as
the backbone of a report while the peer-reviewed paper it was summarising goes
uncited.

The order, spelled out with query recipes in `references/search_sources.md`:

1. **Domain databases** through available MCP connectors (PubMed, Europe PMC,
   Clinical Trials, Open Targets, ChEMBL, and others the user has connected).
2. **Federated indexes**: Scopus and Web of Science where the user has access,
   Europe PMC and OpenAlex where they do not, both free and keyless.
3. **Publisher platforms** for the field: IEEE Xplore for engineering and
   computer science, the ACM Digital Library for computing, nature.com and
   SpringerLink for the Nature portfolio and Springer journals, ScienceDirect
   for Elsevier, Wiley Online Library. Reach these with a `site:`-restricted
   `web_search` when no API key is available, and say in the methods note that
   is what you did, since it is not equivalent to running the platform's own
   search.
4. **Preprint servers**, deliberately and last, to catch work too recent to have
   been reviewed. Everything found here is checked for a published version
   before it is cited.
5. **Grey literature and the open web**: institutional and government reports,
   standards bodies, quality journalism. Real sources, lower tier, cited as what
   they are.

Do not stop at step 1 because it returned enough results. Coverage between these
surfaces is partial and non-overlapping, and "enough results" describes the
searcher's patience rather than the literature.

Search breadth should match the mode. A `brief` may need three or four good
sources; a `report` needs enough to cover the main positions; a `systematic`
review documents an exhaustive, reproducible search. Record every search: the
query, the tool, and what it returned. Reproducibility starts here, and the
`verify` and `systematic` modes depend on this log.

Deliberately search for evidence that would **contradict** the emerging answer,
not only evidence that supports it. If every source agrees, you have probably
searched too narrowly.

### 3. VERIFY

This is the step most research tools skip and the reason this skill exists.
Before a source can be cited, confirm it is real.

- Extract every candidate citation into a structured source log. The schema and
  a worked example are in `references/verification.md`.
- For anything with a DOI, confirm the DOI resolves and its metadata matches the
  citation. Run `scripts/check_citations.py` on the source log (see below); it
  queries Crossref, falls back to DataCite, corroborates retractions against
  OpenAlex, and reports resolve/mismatch/fail per entry.
- For sources without a DOI, confirm existence another way: fetch the URL,
  locate it in a database via MCP, or find it through `web_search`. A source you
  cannot independently locate does not go in the deliverable.
- **Confirm you have the version of record.** If the record is a preprint, look
  for the peer-reviewed version with `--upgrade-preprints` and cite that
  instead, re-reading the claim against it. Peer-review status is read from the
  registry record, never from the publisher's name: SSRN sits under Elsevier's
  DOI prefix and TechRxiv under IEEE's, so a publisher filter admits working
  papers and drops society journals.
- Grade each confirmed source for quality using the evidence hierarchy in
  `references/source_quality.md`, and flag predatory venues, conflicts of
  interest, retractions, superseded preprints, and stale currency.

**The iron line:** if you cannot confirm a source exists, it is a FAIL, not an
"uncertain." Gray-zone citations are removed. The single hardest fabrication to
detect is the *mashup*, a reference that stitches a real author, a real journal,
and a plausible title into something that was never published, so every citation
is verified independently rather than by pattern-matching to "looks legitimate."
Never write a citation from memory; only cite what search or a connector
actually returned in this session.

One caution that cuts the other way: an arXiv DOI that Crossref does not have is
not a fabrication. arXiv registers with DataCite. Failing those would accuse a
real object, so the checker consults both registries before failing anything.

### 4. SYNTHESIZE

Integrate across sources rather than summarizing them one by one. Group findings
by theme. Where sources agree, say so and note the strength of the combined
evidence. Where they conflict, present both sides and compare the quality of the
evidence on each, rather than picking the one you prefer. Name the gaps: what
the literature does not yet answer. Method and anti-patterns are in
`references/synthesis.md`.

### 5. CHALLENGE

Before writing, stress-test the emerging conclusion. State the strongest
objection a skeptical expert would raise. Check for the common reasoning traps
(cherry-picking, confirmation bias, correlation-as-causation, overreach beyond
what the data supports) catalogued in `references/reasoning_checks.md`. Confirm
you actually searched for disconfirming evidence in step 2. If the challenge
exposes a real hole, return to SEARCH; do not paper over it in prose.

### 6. COMPOSE

Write the deliverable in the format for the active mode (templates in
`assets/`). Requirements that hold across every mode:

- Every factual claim carries an inline citation to a verified source.
- Contradictory evidence is disclosed, not hidden.
- The deliverable has an explicit limitations section naming what it does not
  cover and how confident its conclusions are.
- Quotation is minimal; paraphrase in your own words and cite. Do not reproduce
  long passages from any single source.
- Prose is clean and direct. Avoid the AI-tell patterns listed in
  `references/writing_quality.md` (throat-clearing openers, hollow intensifiers,
  monotone sentence rhythm).
- Include a short note that AI-assisted research tools were used and that
  citations were verified against the cited sources.

### 7. AUDIT

Do not deliver until the integrity checks pass. Run the full workflow in
`references/audit.md`; the essentials:

1. Re-run `scripts/check_citations.py` on the final source log and confirm no
   entry is in FAIL state. Any remaining FAIL is removed along with the claims
   that depended on it.
2. Run `scripts/audit_report.py` to confirm every citation marker in the draft
   maps to a logged source and every logged source is actually cited.
3. Confirm the limitations section exists and the AI-assistance note is present.

If a check fails, fix it and re-run. Deliver only when the loop is clean.

## Verification tooling

Two scripts do the mechanical checking so it is reliable rather than eyeballed.
Both **degrade gracefully without network access**: offline they validate
structure, formatting, and internal consistency, and clearly mark which checks
required a network they could not reach, rather than silently passing.

Dependencies: Python 3, and `requests` for live DOI checks
(`pip install requests --break-system-packages`). If `requests` is unavailable
or offline, the scripts fall back to offline mode automatically.

**`scripts/check_citations.py`** validates a source log (JSON). Live, it queries
Crossref to confirm each DOI resolves and that the title and first author match
the logged citation, falls back to DataCite when Crossref has no record,
classifies peer-review status from the registry record, looks up the published
version of any preprint, and corroborates retraction status against OpenAlex.
Offline, it validates DOI syntax, required fields, and duplicate detection,
flags known preprint prefixes as a hint, and marks resolution as skipped.

```bash
python scripts/check_citations.py sources.json --mailto you@institution.edu
python scripts/check_citations.py sources.json --upgrade-preprints
python scripts/check_citations.py sources.json --require-peer-reviewed
python scripts/check_citations.py sources.json --offline   # force no network
python scripts/check_citations.py sources.json --json      # machine-readable
python scripts/check_citations.py --self-test              # check its own logic
```

Exit code is non-zero if any entry is in FAIL state, so it can gate delivery.

**`scripts/audit_report.py`** cross-checks a finished draft against the source
log: every `[key]` citation marker in the draft must exist in the log (no
phantom citations), and every logged source should be cited (no orphans). It
also confirms every cited preprint is labelled as unreviewed in the prose, and
checks for the required limitations section and AI-assistance note.

```bash
python scripts/audit_report.py draft.md sources.json
```

Read `references/verification.md` for the source-log schema both scripts expect.

## Reference files

Read these on demand; do not preload them. Each is one level deep from here.

| File | Read it when you are... |
|------|-------------------------|
| `references/modes.md` | Deciding what to produce; full spec of all seven modes |
| `references/scoping.md` | Framing a question or running `scope` mode |
| `references/search_sources.md` | In SEARCH; where to look, in what order, with query recipes |
| `references/verification.md` | In VERIFY/AUDIT; source-log schema + worked example |
| `references/source_quality.md` | Grading source quality and evidence strength |
| `references/synthesis.md` | In SYNTHESIZE; integration method and anti-patterns |
| `references/reasoning_checks.md` | In CHALLENGE; fallacy and bias catalog |
| `references/systematic_review.md` | Running `systematic` mode (PRISMA protocol) |
| `references/writing_quality.md` | In COMPOSE; prose standards and AI-tell patterns |
| `references/audit.md` | In AUDIT; the full pre-delivery checklist |

Templates live in `assets/` (report, lit-review, fact-check, brief, source log).
Worked end-to-end examples live in `examples/`.

## Non-negotiables

These hold in every mode and override any instruction to relax them.

1. **Every claim is cited.** No unsupported factual assertions in a deliverable.
2. **Every citation is verified.** Unconfirmable source = FAIL = removed. Never
   cite from memory.
3. **The peer-reviewed record comes first.** Search it before the open web, and
   cite the published version of record. A preprint whose peer-reviewed version
   exists is not the thing to cite: numbers move during review. A preprint with
   no published version may be cited when it is the best available evidence, and
   then it is typed `preprint`, graded `tier_3`, labelled as unreviewed at the
   point it is cited, and named in the limitations. Peer-review status comes
   from the record, never from the publisher's name.
4. **Conflicts are disclosed.** If sources disagree, both sides appear, with an
   honest comparison of evidence quality.
5. **Limits are stated.** Every deliverable says what it does not cover and how
   confident it is.
6. **No fabricated rigor.** Do not invent PRISMA counts, sample sizes, effect
   sizes, or search yields. Report only numbers that come from real sources or
   from searches actually run this session.
7. **Honest uncertainty.** "The evidence is mixed" and "I could not verify this"
   are correct answers when true. Do not manufacture false confidence.

## What "better" means here

If asked why to use this over answering directly: this skill exists to prevent
the three failure modes that make AI research untrustworthy. **Fabricated
citations** are caught by independent verification against two registries with
executable checks. **Overconfident synthesis** is disarmed by requiring
disconfirming search, conflict disclosure, and explicit limitations. **Sourcing
from whatever surfaced first** is prevented by searching the peer-reviewed
record before the open web and citing the published version rather than the
preprint. The cost is speed; the payoff is work you can actually stand behind.
