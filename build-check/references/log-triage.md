# Reading the LaTeX log

The log is the first thing the checker reads and the last thing to trust on
its own. Each message below is reported by `build_check.py`; the fix column
is the usual one, not the only one.

## Errors

| Message | Meaning | Usual fix |
|---|---|---|
| `! Undefined control sequence.` | a macro the class or a package does not define | a package is missing from the preamble, or the venue class does not provide the command; check the template's sample file |
| `! LaTeX Error: File 'x.sty' not found.` | package not installed | install it in the TeX distribution, or vendor it next to `main.tex` when the venue's zip must be self-contained |
| `! Missing $ inserted.` | math outside math mode, often an underscore in text | escape `_` and `&`, or wrap the token in `\texttt{}` |
| `! Package pdftex.def Error: File 'fig.png' not found` | figure path wrong relative to the build directory | paths are relative to the directory latexmk runs in; use `\graphicspath{}` |
| `! Dimension too large` or `TeX capacity exceeded` | a table or `latexdiff` markup exceeded TeX's limits | split the table; run `latexdiff` with tables treated as atomic |
| `! LaTeX Error: Something's wrong--perhaps a missing \item` | list environment misused, often `tabular` inside `itemize` | check the environment nesting at the reported line |

Any error is a FAIL even when a PDF was produced: `nonstopmode` keeps going
and the page after the error is usually wrong.

## Warnings that are failures

| Message | Meaning | Usual fix |
|---|---|---|
| `Reference 'x' on page N undefined` | `\ref` to a label that was never set, or the build needs another pass | a missing `\label`, a typo, or a label inside a float that was dropped; rebuild once, then fix the label |
| `Citation 'x' on page N undefined` | key not in the `.bib`, or the bibliography pass did not run | check the key; run `bibtex`/`biber`; check the `.bst` exists |
| `Label 'x' multiply defined` | two `\label{x}` | rename one; often a copy-pasted float |
| `Label(s) may have changed. Rerun` | the last pass moved something | run the build again before reading any number from the PDF |
| `File 'x' not found` (non-fatal) | a missing include, template asset, or figure | usually a path or a file left out of the package |

## Overfull boxes

`Overfull \hbox (23.4pt too wide) in alignment at lines 120--131` is a table
or an `align` environment wider than the text block by 23.4 pt: it will
print past the margin. `in paragraph` is a line that could not be broken,
usually a long URL, DOI, code token, or an unhyphenatable word.

Anything under about 3 pt is invisible. The checker reports 5 pt and above
by default (`--overfull-pt`). A journal's technical check flags what it can
see, so treat 10 pt and above as a defect.

Fixes, in order of preference:

- Tables: `\small` or `\footnotesize` inside the float, `tabularx` or
  `\resizebox{\linewidth}{!}{...}` as a last resort, `p{}` columns for prose
  cells, `\setlength{\tabcolsep}{4pt}`, or move to `table*` in a
  double-column class, or to the supplement.
- Equations: `multline`, `split`, or `aligned`; break at an operator.
- Paragraph lines: `\url{}` with the `hyphens` option of `url`, `\-` in a
  long word, `\seqsplit` for identifiers, `\sloppy` for one paragraph only.

`Overfull \vbox` on a page is a page that could not be filled properly,
usually a float too tall for the text height; shrink it or move it.

## Float warnings

| Message | Meaning |
|---|---|
| `Float too large for page by Npt` | the float is taller than the text height; it will be pushed and may land at the end |
| `'h' float specifier changed to 'ht'` | `[h]` alone was refused; the float will go where LaTeX wants |
| `Float(s) lost` | usually a float inside an environment that cannot hold one |

See `float-placement.md` for what these do to the page.

## Font warnings

`Font shape 'T1/ptm/m/scit' undefined` means a small-caps italic was asked
for and substituted; cosmetic unless the venue's checker reports it. `Missing
character` means a glyph is absent from the font: an em dash in a monospace
font, a Unicode symbol without `\usepackage[utf8]{inputenc}` or a font that
carries it. The checker also runs `pdffonts` on the output: a font that is
not embedded is a FAIL, because every publisher's technical check rejects it.

## What the log cannot tell you

Whether the PDF looks right. A page count, a clean log, and zero undefined
references are consistent with a table that overflows by 40 pt (the log
reported it as one line among two hundred), a figure that landed in the
references, and a caption that no longer matches the figure. The rest of the
report exists for that.
