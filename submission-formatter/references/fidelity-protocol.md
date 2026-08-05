# Fidelity protocol

How to mark what is missing, how to interpret the drift report, and what the
delivered report has to contain.

## Contents

- [Marker convention](#marker-convention)
- [Running the check](#running-the-check)
- [Drift classes](#drift-classes)
- [Thresholds](#thresholds)
- [Limit overage](#limit-overage)
- [FORMAT_REPORT.md template](#format_reportmd-template)

## Marker convention

When the template requires something the manuscript does not contain, emit a
marker. A marker is visible, greppable, and obviously not content.

LaTeX:

```latex
%% TODO(author): Data Availability Statement required by <journal>.
%% The manuscript does not contain one. Add it here before submission.
\section*{Data Availability}
[[TODO(author): data availability statement]]
```

Word and markdown:

```
[[TODO(author): funding statement required by <journal>; not present in source]]
```

Rules:

- One marker per missing item, at the position it belongs.
- The marker names what is missing, why it is required, and that it was absent
  from the source. It never contains a suggested draft, not even a generic one,
  because generic text gets submitted.
- Every marker appears in `FORMAT_REPORT.md` under "What the author must supply",
  with its file and location.
- Before delivery, grep the output for `TODO(author)` and confirm the count
  matches the report.

Items that are almost always markers rather than content: ORCID identifiers,
funding and grant numbers, ethics approval numbers, informed consent statements,
data and code availability statements, conflict of interest declarations, CRediT
author contribution roles, highlights, graphical abstracts, corresponding-author
addresses, and ACM CCS concepts and DOIs.

Suspected errors in the source get a marker too, and the original value stays
untouched:

```latex
%% NOTE(author): Table 3 reports n=412; the cohort paragraph says n=380.
%% Value left exactly as in the source.
```

## Running the check

```bash
python scripts/fidelity_check.py \
  --source build/manuscript.json \
  --output build/main.tex \
  --json report/fidelity.json
```

Run it against the built source file, and again against the compiled PDF when
one exists. The PDF check catches content that the source contains but the build
silently dropped: a figure that failed to include, a section commented out, text
overrunning a fixed-height box, a `\input` that did not resolve.

Boilerplate the template legitimately adds can be excluded from the added list:

```bash
printf '%s\n' '^data availability' '^conflict of interest' > report/ignore.txt
python scripts/fidelity_check.py --source ... --output ... --ignore-added report/ignore.txt
```

## Drift classes

**Missing sentences.** Content in the source that is absent from the output.
Usual causes: a section skipped during assembly, a table or figure environment
that swallowed a caption, a `\input` not included, text inside a Word text box,
a PDF column not extracted. Always fix, never explain away. The one benign case
is a sentence that was pure template boilerplate in the source (a journal's own
instruction text left in the author's file), which gets a written justification.

**Altered sentences.** Near-matches below full identity. Usual causes: escaping
changes, hyphenation, ligatures, a Unicode symbol replaced by ASCII, or a real
edit that should not have happened. Inspect each one. Encoding and escaping
differences are justified in the report; anything that changes a word is fixed.

**Added sentences.** Content in the output not present in the source. Legitimate
sources: template headings, required section titles, markers, the class's own
sample text that was not fully removed. Anything else is a fabrication and gets
deleted. Check specifically for leftover template placeholder text, which is a
common and embarrassing submission error.

**Numeric drift.** Any numeric token present in one and absent from the other.
This is the highest-severity class. Causes: a table row lost, a value reformatted
(thousands separators, unit spacing, exponent notation), or a genuinely changed
number. Reformatting is justified only when the value is provably identical.

**Citation drift.** A citation key or marker present in one and absent from the
other. Causes: a `\cite` that did not survive, renumbering, a reference dropped
from the list, or a style change from author-year to numeric that the checker
cannot align. When the style changed deliberately, the counts still have to
reconcile: the number of distinct markers and the number of reference entries
must match the source.

**Structural drift.** Figure, table, or equation counts differ. Always
investigate; these are rarely benign.

**Word count delta.** A large negative delta means content is missing. A large
positive delta means template text was added or content was duplicated. Small
deltas are normal because command syntax differs between formats.

## Thresholds

| Metric | Pass |
|---|---|
| Missing sentences | 0, or each individually justified in writing |
| Altered sentences | 0 unchanged in meaning; encoding-only alterations justified |
| Numeric tokens missing | 0 |
| Citation markers missing | 0 |
| Figure and table counts | equal to source |
| Reference count | equal to source |
| Word count delta | within roughly 5 percent, and explained beyond that |

Ship only when every line passes or carries a written justification. "The
checker is being noisy" is not a justification; if a class of difference is
genuinely expected, name it and say why in the report.

## Limit overage

When the manuscript exceeds a venue limit, measure it in the venue's own unit
and report it. Do not cut.

- Count words the way the journal counts them. Some exclude the abstract,
  references, captions, and tables; some count everything. State which rule was
  applied.
- For page limits, the count only means something after the real class compiles.
  If the class could not be compiled locally, say the page count is unverified.
- List candidate reduction sites with their sizes: a specific subsection, a
  table that duplicates a figure, a related-work paragraph, an appendix that
  could move to supplementary material. Sizes let the author choose.
- Decide nothing. Hand off to `research-paper-writing` if the author wants the
  cutting done.

## FORMAT_REPORT.md template

```markdown
# Format report: <manuscript title>

**Target venue:** <journal>, <publisher>
**Template:** <file or URL> (accessed <date>)
**Author instructions:** <URL> (accessed <date>)
**Output:** <format>, built <date>
**Source:** <input file> (<format>, lossy: yes/no)

## What the author must supply

| Item | Location | Why required |
|---|---|---|
| Data availability statement | main.tex line 412 | required by <journal> |
| ORCID for second author | main.tex line 38 | required by <journal> |

## Limits

| Limit | Venue rule | This manuscript | Status |
|---|---|---|---|
| Word count | 8000 excl. references | 8640 | over by 640 |
| Figures | 8 | 6 | ok |

Candidate reductions, if the author chooses to cut: <list with sizes>.

## Requirements sheet

| Requirement | Value | Applied |
|---|---|---|
| Document class | sn-jnl, [pdflatex,sn-vancouver-num] | yes |
| Line numbers | required at submission | yes, [lineno] |
| Abstract | unstructured, 250 words max | 238 words, unchanged |
| Citation style | Vancouver numbered | converted from author-year |
| Figure resolution | 300 dpi minimum | 3 figures below, listed below |

## Section mapping

| Source | Target | Action |
|---|---|---|

## Changes made

Formatting changes only. Each entry states what changed and why.

## Fidelity check

`report/fidelity.json`, status: <clean/drift>

| Metric | Source | Output | Note |
|---|---|---|---|
| Words | | | |
| Sentences | | | |
| Numeric tokens | | | |
| Citation markers | | | |
| Figures / tables | | | |

Justified differences:

- <difference> : <why it is expected>

## Build

Status: <built / blocked by missing class / failed>
Engine: <engine>
Package: <path>

## Author checklist before upload

- [ ] fill every TODO(author) marker
- [ ] confirm the reference list renders in the required style
- [ ] confirm figures meet the resolution requirement
- [ ] check the compiled PDF against the source for the items flagged above
- [ ] confirm the portal's file manifest
```

Keep the report factual. It is a record of what was done to the manuscript, and
the author should be able to audit any line of it against the files.
