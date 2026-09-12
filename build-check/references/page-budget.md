# When the page count is over the cap

A page cap is a hard rule at most venues that have one: IEEE Transactions
return an over-length paper without review, conference templates reject at
upload, and a journal with a word guidance will ask for cuts at revision. The
checker reports the count and the overage; deciding what to cut is editorial
work and belongs to `manuscript-editor`. This file is about buying room
honestly and measuring it.

## Measure first

Run the checker on the current build and record: pages, body words, the page
the references start on, and the number of floats. Then identify what kind
of overage it is:

- **Word-bound.** Page density is uniform and the spill is the last section
  or the reference list. The only real fix is fewer words. Everything else
  buys a fraction of a page.
- **Float-bound.** One or more pages are half empty because a float did not
  fit, or floats queued to the end. Fix placement first (see
  `float-placement.md`); it often recovers a page without touching prose.
- **Table-bound.** A wide or tall table takes a page it does not need. Move
  it to the supplement or reset it.

## Ways to recover space, cheapest and least damaging first

1. Fix float placement and half-empty pages.
2. Move supplementary-grade tables and the appendix to a supplement file,
   with one-line pointers. Venues that have a page cap almost always accept
   a supplement.
3. Remove references that are cited once in related work only, and preprint
   citations that have a version of record (`investigating-sources` has the
   reference-diet mode). A reference list is often 1 to 2 pages.
4. Convert a body table that summarizes prose into the prose it summarizes,
   or the reverse: keep one.
5. Shorten captions that repeat the body text.
6. Then, and only then, cut prose: `manuscript-editor` produces the ranked
   cut list from the audit's redundancy and summary signals.

## Ways that read as a paper pushed over its limit

Do not: shrink figures below the venue's minimum type size, set the
bibliography in a smaller font than the class allows, reduce margins or
`\baselineskip`, use `\vspace{-...}` around floats, or `\small` the body.
Typesetters undo all of these and reviewers recognise them. The checker's
overflow and font checks will not catch them; the editor will.

## Re-measure after every cut

Page counts do not shrink linearly with words. A cut of 600 words can
recover zero pages if a float then moves, or two pages if a page break
clears. Run the checker after each batch of cuts, not at the end, and quote
the last report in the hand-back.

## Word guidance versus page cap

A word guidance ("about 4,500 words") is softer than a cap, but the
checker still measures it. Body words are counted before the references
heading; abstracts, captions, and tables are included because most venues
include them. When a venue counts differently, say which count you used.
