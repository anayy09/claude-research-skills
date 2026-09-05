# Coherence audit

How to check a manuscript as a whole after a batch of changes. Two layers:
the script for what patterns can find, then a manual pass for what they
cannot.

Contents

1. Running and reading the audit script
2. What the script cannot see
3. The manual pass, in order
4. The four mirrors: abstract, contributions, discussion, conclusion
5. Decision rules for what the pass finds
6. Comparing before and after

## 1. Running and reading the audit script

```bash
python scripts/audit_manuscript.py paper.md --report audit.md   # markdown report
python scripts/audit_manuscript.py paper.tex --json > audit.json # machine-readable
python scripts/audit_manuscript.py paper.docx --strict           # exit 1 on any leak
```

Formats: `.md` (headings by `#`), `.tex` (`\section` family, `\begin{abstract}`,
captions and labels from figure/table environments, `\ref` and `\cite`
tokenized), `.docx` (Heading styles), `.txt` (heuristic headings). For a PDF,
extract text first (`submission-formatter/scripts/extract_manuscript.py` or
`pdftotext -layout`) and audit the `.txt`.

Report sections and how to read them:

| Section | What it is | How to act |
|---|---|---|
| 1 Outline | Word count and share per section, with proportion warnings | Compare to the venue budget and to the previous audit. Growth needs a ledger reason. |
| 2 Leaks | Pattern hits for reviewer-facing language | Every hit is repaired or consciously kept (rare; see boundary reference, section 6). Zero is the target. |
| 3 Near-duplicates | Sentence pairs with high lexical overlap | Same-paragraph pairs are usually a botched edit. Cross-section pairs: keep one. Abstract pairs are flagged as expected restatement. |
| 4 Terminology | Hyphenation, spacing, UK/US, capitalization variants | Pick one form, record it in the ledger, replace globally. |
| 5 Acronyms | Multiple definitions, undefined, defined-but-rare | Define once at first use in the body (the abstract can define separately). Spell out anything used twice or less. |
| 6 Display items | First-mention order, missing captions, orphan captions | Number in order of first mention. Every item is cited in text; every citation has an item. |
| 7 Hedging | Meta-commentary phrases per 1000 words; hedge-stacked sentences | Above roughly 3 per 1000 reads as defensive. Stacked hedges: pick one or commit. |
| 8 Abstract numbers | Numbers in the abstract absent from the body | Either the abstract or the body is stale. Fix the one that is wrong. |
| 9 Placeholders | `[AUTHOR INPUT ...]`, TODO, TBD, XXX | All must be resolved or listed in the change summary. |

The script is conservative on purpose: it reports candidates, not verdicts.
False positives are cheap to dismiss; a missed leak costs a round.

## 2. What the script cannot see

- The same point made in different words (semantic duplication).
- A claim stated at one strength in Results and another in Discussion.
- A number changed in one place and not another, if the two places used
  different phrasing (the abstract check catches the common case only).
- A paragraph that only exists to reassure.
- A transition broken by an insertion above it.
- A section that has drifted from its job (Methods that interprets, Results
  that argues, Discussion that re-explains the problem).
- Whether a limitation is stated in the right place and only once.
- Whether new citations are real. Any reference added during revision that
  was not supplied by the author is verified with
  `investigating-sources` or `evidence-synthesis`, or left as a
  `[CITE: ...]` placeholder.

## 3. The manual pass, in order

Do this after the whole batch of changes, reading the manuscript from the
top. Keep a scratch list; fix at the end so the read stays continuous.

1. **Read the abstract, then the contributions list, then the first
   paragraph of the Discussion, then the Conclusion.** These four should
   tell the same story with the same numbers. See section 4.
2. **Read each section for its job.** Introduction: problem, gap,
   contribution. Methods: what was done, enough to reproduce, with the
   reasons for non-obvious choices. Results: what was found, with numbers,
   interpreted only enough to follow. Discussion: what it means, against
   prior work, with limitations. Conclusion: shortest true summary. Mark any
   paragraph doing another section's job.
3. **Read every paragraph that was touched this round together with the
   paragraph before and after it.** Check the opening connective still has
   an antecedent, "this"/"these"/"such" still refer to the right thing, and
   the tense matches.
4. **Build a claim index.** List each claim in the abstract and
   contributions. For each, find the Results evidence and the Discussion
   interpretation. A claim with no Results support is either overclaimed or
   has a missing result. A result never claimed anywhere may be
   unnecessary or under-sold.
5. **Build a limitation index.** List each limitation statement in the
   manuscript with its location. Each limitation appears once, in the
   Discussion (or a Limitations subsection if the venue uses one). Merge
   duplicates; move strays.
6. **Check terminology against the ledger.** The ledger's canonical-term
   list is the reference; the audit's terminology section is the detector.
7. **Check display items in reading order.** Each figure and table is
   cited in numerical order, each caption stands alone, and captions were
   updated when the analysis changed (a caption that still describes the
   old panel layout is a common round-2 error).
8. **Check that new evidence has provenance.** Every number added this
   round traces to a result the author supplied or a placeholder. Every
   new citation is real and says what it is cited for.
9. **Check the response letter against the manuscript.** For every "we
   changed X in Section Y", open Section Y and confirm. For every quoted
   passage in the letter, confirm the manuscript text is identical.

## 4. The four mirrors: abstract, contributions, discussion, conclusion

These four places each summarize the paper for a different reader, and they
drift apart under revision because each gets edited when a reviewer looks at
it. The check:

| Element | Abstract | Contributions (Intro) | Discussion para 1 | Conclusion |
|---|---|---|---|---|
| Headline result and number | yes | as claim | yes, interpreted | yes |
| Comparator or baseline | yes | optional | yes | optional |
| Scope condition | yes if short | yes | yes | yes |
| Main limitation | often | no | in limitations para | one clause at most |
| Strength of the claim | identical | identical | identical | identical |

"Identical strength" means: if the abstract says "improves", the discussion
does not say "may improve", and the conclusion does not say "demonstrates
substantial improvement". Pick the strength the evidence supports and use it
in all four.

## 5. Decision rules for what the pass finds

- **Duplicate point, two sections.** Keep it where the reader needs it to
  follow the argument. Results wins for numbers; Discussion wins for
  interpretation; Methods wins for rationale. Delete the other, then check
  the surrounding transition.
- **Duplicate point, same section.** Almost always a failed edit. Merge into
  the better sentence.
- **Contradiction in numbers.** Find the source of truth (the results file,
  the table). Fix all occurrences. If the source is unavailable, placeholder
  both and flag.
- **Contradiction in claim strength.** Use the weaker form that the evidence
  supports, everywhere, unless the evidence changed this round.
- **Paragraph doing another section's job.** Move it, then check both
  sections' transitions. If it is a Methods paragraph that interprets, split:
  the procedure stays, the interpretation goes to Discussion (once).
- **Reassurance paragraph.** Delete. If it contains a fact, extract the fact
  per the boundary reference's repair procedure.
- **Section grew without a corresponding item.** Read the additions; they are
  usually restated context or expanded caveats. Cut back.
- **Orphan transition.** Rewrite the opening of the following paragraph to
  connect to what now precedes it, or remove the connective entirely.
- **Terminology drift.** Global replace to the ledger's canonical form,
  including in captions and the supplement.

## 6. Comparing before and after

Run the audit before the first edit and after the coherence pass. Put the
two outlines side by side:

```
Section        before   after   delta   ledger items touching it
Introduction     612     640     +28    R1.3 (one sentence on prior transfer results)
Methods         1480    1610    +130    R2.1 (sensitivity analysis), R2.4 (ICI)
Results         1120    1205     +85    R2.1, R1.5 (age subgroups)
Discussion      1310    1290     -20    R1.2 (cut restated background), R2.2
Conclusion       190     150     -40    E.1 (removed restated discussion)
```

Every positive delta has an item next to it. If it does not, the growth is
unexplained and probably unnecessary. This table goes in the change summary
to the user; it is the fastest way for them to see what the round did to the
paper's shape.
