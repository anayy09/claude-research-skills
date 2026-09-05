# Response to reviewers

The response letter is where the account of change lives. Its reader is the
editor, who decides in minutes whether the revision is complete, and the
reviewers, who check whether their specific point was handled. Its function
is traceability: every comment, one answer, one location in the manuscript.
Register (concede without groveling, push back with evidence) is covered in
`research-paper-writing`; this file covers structure and content.

Contents

1. Structure of the document
2. The per-item template
3. What goes in the response and not in the manuscript
4. Handling disagreement
5. Handling requests that cannot be met
6. Consistency with the manuscript
7. Length and tone calibration
8. Template

## 1. Structure of the document

1. **Opening paragraph.** One or two sentences: thanks, and the one or two
   most substantial changes in the revision (a new analysis, a restructured
   section). Editors read this first.
2. **Summary of major changes.** A short list, if the revision was major.
   Omit for minor revisions.
3. **Point-by-point responses**, grouped by reviewer in the order the
   comments arrived, then editor comments. Each comment is reproduced or
   closely paraphrased, then answered.
4. **List of other changes** not prompted by any comment (typos fixed,
   updated references, a renumbered figure). Short.

Number items to match the ledger (R1.1, R1.2, R2.1, E.1). The reviewer's
own numbering, if any, is preserved in the reproduced comment.

## 2. The per-item template

```
R2.3  [comment reproduced or closely paraphrased]

Response: [one sentence: what was done, or the position taken]
[one to three sentences: the substance, with the key evidence]
Changes: [Section and subsection, and the new or revised text quoted
verbatim, or "No change to the manuscript" with the reason]
```

Quote the revised manuscript text in the response. This is the correct
place for "we have added", "we revised", and "now reads". The quoted text
must be identical to the manuscript; copy it after the manuscript is final.

Give locations by section and subsection name, and by page and line if the
journal requires line numbers. Page and line references go here and never
in the manuscript.

## 3. What goes in the response and not in the manuscript

- The fact that a change was made, and that it was prompted by the comment.
- Why the authors agree or disagree.
- Justifications a reviewer asked for that a general reader does not need
  (why 5 folds is enough, why a comparison to method X was not run).
- Explanations of what a reviewer misread, with the existing passage
  quoted.
- Analyses run to satisfy a comment whose result did not change any
  conclusion and does not belong in the paper: report the number here,
  with a sentence on why it is not in the manuscript, or put it in the
  supplement and point to it.
- Anything about the review itself: appreciation, apologies for unclear
  text, notes on other reviewers' overlapping comments.

If a justification is one a reader in the field would also want, it belongs
in the manuscript as one sentence of rationale, and the response points to
it.

## 4. Handling disagreement

Disagree with evidence, in the same register as agreement. State the
position in one sentence, give the reason with data or citation, and say
what (if anything) was changed as a result, often a clarifying sentence in
the manuscript so the next reader does not have the same objection.

```
R1.4  The authors should compare against method X.

Response: We did not add this comparison. Method X requires paired
measurements that are not recorded in either cohort, so a comparison would
have to use an approximation that method X's authors advise against [ref].
We added one sentence to Related Work explaining why the comparison is not
possible on routinely collected data.
Changes: Section 2.2, paragraph 3, now reads: "..."
```

Never concede a point that is wrong in order to close the item; a wrong
concession becomes a wrong sentence in the manuscript. Never argue past the
evidence; if the reviewer is right, say so in one clause and move on.

## 5. Handling requests that cannot be met

When a request needs data, experiments, or decisions only the author can
supply, the response cannot be finished by the editor skill. The
manuscript gets a placeholder; the response gets a placeholder; the ledger
gets a row with status "needs author input". The change summary to the user
lists each one with what is needed. Do not draft a plausible answer to
stand in for the author's decision.

When a request is out of scope for the paper (a new study, a different
population), say so, give the reason, and offer what is possible (a
limitation statement, a future-work sentence, a supplementary analysis on
available data).

## 6. Consistency with the manuscript

Before the package is delivered, check each item:

- The location cited exists and contains the change.
- The quoted text is identical to the manuscript text.
- The manuscript text contains no trace of the response framing (no "as
  requested", no "we agree").
- If the response says an analysis was added, its Methods, Results, and any
  figure or table are all present.
- If the response says no change was made, the manuscript in fact still
  says what the response claims it already said.

Springer's guidance notes that reviewers see the response letter in the
next round. Anything in it that a reviewer could test against the
manuscript will be tested.

## 7. Length and tone calibration

- Response items are usually shorter than the reviewer's comment plus the
  quoted change. A three-paragraph response to a one-line comment signals
  defensiveness.
- Thank once, at the top. Not per item.
- No hedging in the response either: "we have addressed this" not "we
  hope this addresses the reviewer's concern".
- Match the reviewer's technical level; do not explain what they clearly
  know.

## 8. Template

A fill-in version is in `assets/response-template.md`. Build it from the
ledger, then run the consistency check in section 6.
