# Float placement

A float is a figure, table, or algorithm that LaTeX is allowed to move. It
moves for two reasons: the float does not fit where it was written, or the
placement rules for the class forbid the position. The checker reports where
every float actually landed, read from the `.aux` file, and compares that to
the section that first cites it and to the page where the references begin.

## Why a table ends up in the references

Floats queue in the order they are written. When one does not fit, everything
behind it waits, and LaTeX flushes the queue at the end of the document,
which is after the bibliography. The usual causes:

- A float taller or wider than the text area (`Float too large for page`).
- Too many floats in a row with too little text between them; the class
  limits floats per page (`totalnumber`, `topfraction`).
- A starred float in a double-column class: `figure*` and `table*` go only
  to the top of a page, and only on a page after the one where they appear
  in the source.
- A float placed after the last paragraph of text, with nothing left to
  flow around it.

## Fixes, in order of preference

1. **Move the source position.** Put the float's source right after the
   paragraph that first cites it, not before, and not at the end of the
   section. This fixes most cases and changes nothing about the layout rules.
2. **Shrink the float** so it fits a page: font size inside the table,
   figure width, or split a tall table.
3. **`\FloatBarrier`** (package `placeins`) at the end of each section, or
   `\usepackage[section]{placeins}` to add one after every `\section`. This
   keeps floats inside their section without pinning them to a spot.
4. **`[!t]` or `[!tb]`** on the float: the `!` relaxes the fraction rules,
   `t` sends it to the top of the next page. This is what IEEE and most
   two-column venues expect.
5. **`[H]`** (package `float`) pins the float where it is written. It works
   on single-column floats. **It is inert on `figure*` and `table*`**: a
   double-column float cannot be placed mid-column, so `[H]` is ignored and
   the float still goes to the next page top. For a double-column class, use
   `stfloats` with `[!b]`, or `\FloatBarrier`, or accept the page-top rule.
6. **Move the float to the supplement**, and keep a one-line pointer.

`[H]` everywhere is a last resort, not a first one. It produces half-empty
pages when a float does not fit the space left on the page, and it moves
text away from the reader instead of the float. A journal's typesetter will
remove it anyway.

## What the checker reports

- **FAIL: float on or after the references page.** Read from the `.aux`
  page of the float's label against the page of the References heading (from
  the table of contents, or from the page text when the heading is
  unnumbered). Labels beginning `app`, `supp`, or `s` are exempt, since
  appendices and supplements legitimately follow the references.
- **WARN: float placed outside its citing section.** The section containing
  the first `\ref`, `\cref`, `\autoref`, or `\Cref` of the label, with its
  page range from the table of contents, against the float's page. One page
  before the section start is tolerated (a page-top float).
- **WARN: never cited.** A float with a label that no `\ref` command names.
  Either the citation is missing, which a reviewer will notice, or the
  reference uses a form the checker does not read (a hand-typed "Table 4",
  which is also fragile). A body table written inline without a label is not
  seen at all.
- **WARN: `[H]` on a starred float** in a two-column class, which does
  nothing.

The `.aux` is written by the last build, so the check is only as fresh as
the PDF. If the log says labels may have changed, build again first.

## Venue notes

- **IEEEtran** (journal option): floats go to page tops; `figure*` spans
  both columns and appears at the earliest the next page. IEEE's own guide
  asks for `[!t]`. Tables at the top, figures at the top, nothing at the
  bottom unless `stfloats` is loaded.
- **Elsevier `elsarticle`**: single column in `preprint` mode, so `[H]`
  works, but `\FloatBarrier` is cleaner. In `3p`/`5p` two-column modes the
  IEEE rules apply.
- **Springer `sn-jnl`**: floats respect `[t]` and `[h]`; the class discards
  `[H]` silently in some versions, so check the placement rather than the
  source. Nine `.bst` files and the class must be in the build directory.
- **Nature-family templates** expect figures at the end for submission and
  in place for the proof; check the current author instructions rather than
  assuming either.
