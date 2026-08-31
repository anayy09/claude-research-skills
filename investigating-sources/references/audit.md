# Audit

The pre-delivery gate. Nothing ships until these checks pass. This is the last
line of defense against the two failure modes the skill exists to prevent:
fabricated citations and overconfident synthesis.

## Contents

- The audit loop
- Automated checks
- Manual checks
- What to do on failure

## The audit loop

Audit is a loop, not a single pass: check → fix → re-check, until clean. Copy
this checklist into your working notes and work through it.

```
Audit Progress:
- [ ] 1. check_citations.py passes (no FAIL entries)
- [ ] 2. No preprint is cited that has a peer-reviewed version
- [ ] 3. Every surviving preprint is labelled as unreviewed in the prose
- [ ] 4. audit_report.py passes (no phantom/unverified citations)
- [ ] 5. Every claim in the draft has a citation
- [ ] 6. Conflicting evidence is disclosed, not hidden
- [ ] 7. Limitations section is present and honest
- [ ] 8. No fabricated numbers (counts, effect sizes, yields)
- [ ] 9. AI-assistance note is present
- [ ] 10. Writing quality pass done (references/writing_quality.md)
```

## Automated checks

**1. Source log is clean.**

```bash
python scripts/check_citations.py sources.json --mailto you@institution.edu     --upgrade-preprints
```

Every entry must be OK (or a legitimately manually-confirmed PENDING/SKIPPED
with a recorded `verify_method`). Any FAIL entry, and any WARN whose metadata
mismatch is unresolved, is removed from the deliverable along with the claims
that depended on it. Re-run until no FAIL remains. The script's non-zero exit
code on FAIL makes this gate scriptable.

**2. No preprint stands in for a published paper.**

`--upgrade-preprints` populates `superseded_by` for every preprint whose
peer-reviewed version exists, and the checker FAILs those entries. Swap the DOI,
update the venue and year, and re-read the claim against the published paper
before keeping the sentence. Numbers move during review, so a swapped DOI with
an unrevised sentence is still a misattribution.

Preprints with no published version may stay. Confirm each one is typed
`preprint` in the log, graded `tier_3`, described as unreviewed at the point it
is cited, and named in the limitations. A reader must never learn that the
evidence was unreviewed only by checking the DOI themselves.

**3. Draft matches the log.**

```bash
python scripts/audit_report.py draft.md sources.json
```

This must show no phantom citations (a `[key]` in the draft absent from the log)
and no unverified citations (a cited source whose status is not `confirmed`).
Both are hard failures: a phantom citation is the fabrication signature.
Resolve orphan-source and missing-section warnings too.

## Manual checks

Some checks need judgment and cannot be scripted:

- **Every claim cited (5).** Read the draft and confirm each factual assertion
  carries a citation at the point it is made. The script confirms citations map
  to sources; only a human read confirms that every claim *has* one.
- **Conflicts disclosed (6).** Confirm that where sources disagreed, both sides
  appear with an honest quality comparison, and that no contradicting evidence
  found during SEARCH was quietly dropped.
- **Limitations honest (7).** The section exists, names what the work does not
  cover, and states confidence calibrated to the evidence, not a boilerplate
  disclaimer.
- **No fabricated numbers (8).** Every count, percentage, sample size, effect
  size, and search yield traces to a real source or a search actually run this
  session. This is the check most worth doing slowly.
- **Writing quality (10).** Run the self-check in `references/writing_quality.md`.

## What to do on failure

- **A FAIL source** → remove it and its dependent claims; re-source if another
  confirmed source supports the claim; re-run check_citations.py.
- **A superseded preprint** → swap in the DOI from `superseded_by`, update the
  venue, year, and type, then re-read the claim against the published version.
  This is the one FAIL fixed by swapping rather than deleting.
- **A phantom citation** → either the source exists and was never logged (log
  and verify it) or it does not (remove the claim). Never resolve a phantom by
  inventing a plausible source.
- **A missing limitations section or AI note** → add it.
- **A fabricated number** → replace with the real figure from a source, or cut
  the claim. If the honest answer is "the exact number is unknown," say that.

Deliver only when the loop is clean. A clean audit is the difference between
research someone can rely on and research that merely looks reliable.
