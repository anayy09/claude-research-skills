# Revising a manuscript that lives in Word

Some venues and some co-authors work in `.docx`. The editorial discipline is
the same; the mechanics differ, and some of them cannot be automated.

## What can be done from here

- **Read and audit.** `audit_manuscript.py` and `prose_lint.py` read `.docx`
  directly (paragraph text). Table cells and headings come through
  `docx_markers.py extract`, which writes a plain-text copy with `#`
  headings and `[Table n]` blocks for the audit.
- **Edit paragraph text** with python-docx, run by run, keeping styles. A
  paragraph rewritten as a whole loses its runs' formatting (italics on a
  gene name, a superscript); edit the run that carries the sentence, or
  rewrite the whole paragraph and reapply the formatting deliberately.
- **Author-action markers.** The convention the round-two Word manuscripts
  used: a red, bold, highlighted `[AUTHOR ACTION: what is needed]` at the
  place the author has to act. `docx_markers.py add`, `list`, and `clear`
  manage them; `list` exits non-zero while any remain, so it works as the
  same gate as `[AUTHOR INPUT]` in a Markdown or LaTeX manuscript.
- **The response letter** in Markdown, built to PDF with `build_letter.py`,
  whose quotation check needs the manuscript text: extract it first.

## What cannot be done from here, and what to do instead

- **Tracked changes.** python-docx cannot author Word revisions. The marked
  copy a venue asks for is produced by Word's Compare (Review, Compare, the
  submitted file against the clean revised file) or by LibreOffice's
  Compare Document. Say this in the hand-back and leave the two clean files
  ready: the submitted `.docx` untouched, the revised `.docx` finished.
- **Equations and fields.** Equation objects, cross-reference fields, and
  citation-manager fields are opaque to python-docx. Do not touch a
  paragraph that contains one from a script; edit it in Word, or ask the
  author to.
- **Comments.** Reviewer comments in the margin are not paragraphs. Export
  them (`docx_markers.py` does not; Word's Review pane or a `comments.xml`
  read does) into the reviewer text files `make_checklist.py` consumes.

## Procedure for a Word round

1. Keep three files: `submitted.docx` (never edited), `working.docx` (the
   revision), `response.md` (the letter).
2. `docx_markers.py extract working.docx` and run the audit on the text.
3. Build the checklist from the reviews; approve it.
4. Edit `working.docx`; add `[AUTHOR ACTION]` markers for every author-only
   item; append a ledger row per item.
5. `docx_markers.py list working.docx` until it is clean, or the remaining
   markers are listed in the hand-back.
6. `build_letter.py response.md --manuscript working.txt` (the extracted
   text) so every quoted passage is checked.
7. Hand back: the clean revised file, the letter PDF, and the instruction
   for the marked copy (Compare submitted.docx against working.docx).

## Co-authors' copies

When co-authors return their own edited `.docx`, do not merge by hand.
Compare each against `working.docx` in Word, accept or reject per change,
and record what was taken in the ledger with the co-author's initials. A
co-author's file is treated as a review: its changes are items.
