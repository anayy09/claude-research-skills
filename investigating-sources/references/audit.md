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
- [ ] 2. audit_report.py passes (no phantom/unverified citations)
- [ ] 3. Every claim in the draft has a citation
- [ ] 4. Conflicting evidence is disclosed, not hidden
- [ ] 5. Limitations section is present and honest
- [ ] 6. No fabricated numbers (counts, effect sizes, yields)
- [ ] 7. AI-assistance note is present
- [ ] 8. Writing quality pass done (references/writing_quality.md)
```

## Automated checks

**1. Source log is clean.**

```bash
python scripts/check_citations.py sources.json
```

Every entry must be OK (or a legitimately manually-confirmed PENDING/SKIPPED
with a recorded `verify_method`). Any FAIL entry, and any WARN whose metadata
mismatch is unresolved, is removed from the deliverable along with the claims
that depended on it. Re-run until no FAIL remains. The script's non-zero exit
code on FAIL makes this gate scriptable.

**2. Draft matches the log.**

```bash
python scripts/audit_report.py draft.md sources.json
```

This must show no phantom citations (a `[key]` in the draft absent from the log)
and no unverified citations (a cited source whose status is not `confirmed`).
Both are hard failures — a phantom citation is the fabrication signature.
Resolve orphan-source and missing-section warnings too.

## Manual checks

Some checks need judgment and cannot be scripted:

- **Every claim cited (3).** Read the draft and confirm each factual assertion
  carries a citation at the point it is made. The script confirms citations map
  to sources; only a human read confirms that every claim *has* one.
- **Conflicts disclosed (4).** Confirm that where sources disagreed, both sides
  appear with an honest quality comparison, and that no contradicting evidence
  found during SEARCH was quietly dropped.
- **Limitations honest (5).** The section exists, names what the work does not
  cover, and states confidence calibrated to the evidence — not a boilerplate
  disclaimer.
- **No fabricated numbers (6).** Every count, percentage, sample size, effect
  size, and search yield traces to a real source or a search actually run this
  session. This is the check most worth doing slowly.
- **Writing quality (8).** Run the self-check in `references/writing_quality.md`.

## What to do on failure

- **A FAIL source** → remove it and its dependent claims; re-source if another
  confirmed source supports the claim; re-run check_citations.py.
- **A phantom citation** → either the source exists and was never logged (log
  and verify it) or it does not (remove the claim). Never resolve a phantom by
  inventing a plausible source.
- **A missing limitations section or AI note** → add it.
- **A fabricated number** → replace with the real figure from a source, or cut
  the claim. If the honest answer is "the exact number is unknown," say that.

Deliver only when the loop is clean. A clean audit is the difference between
research someone can rely on and research that merely looks reliable.
