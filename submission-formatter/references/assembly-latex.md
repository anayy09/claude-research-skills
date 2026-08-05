# Building the LaTeX submission

The target is a directory that compiles on the publisher's system with the
publisher's class, containing the author's content and nothing invented.

## Contents

- [Working method](#working-method)
- [Preamble](#preamble)
- [Front matter by class](#front-matter-by-class)
- [Body](#body)
- [Figures](#figures)
- [Tables](#tables)
- [Math](#math)
- [Bibliography](#bibliography)
- [Compile and triage](#compile-and-triage)
- [Submission package layout](#submission-package-layout)

## Working method

Start from the publisher's sample `.tex`, not from a blank file. The sample
carries the class options, the front-matter macro order, and the comments that
document them. Replace its content with the author's content, section by
section, keeping the scaffolding.

Copy strings mechanically. When moving a paragraph, move the extracted string,
do not retype it or "lightly clean" it while moving. Retyping is where words
change.

Build incrementally and compile often. A class error found after twenty sections
have been pasted costs more to isolate than one found after two.

## Preamble

Order that avoids most conflicts:

```latex
\documentclass[<options from the requirements sheet>]{<class>}

% packages the class does not already load
\usepackage{graphicx}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{algorithm,algpseudocode}
\usepackage{url}
% hyperref late, unless the class loads or forbids it
```

Rules:

- Drop the author's geometry, fontenc, font, margin, spacing, and header
  packages. The class owns page layout, and overriding it is what makes a
  submission look wrong to a production editor.
- Keep the author's `\newcommand` and `\DeclareMathOperator` definitions. These
  are content-bearing shorthand and removing them breaks the body.
- Check what the class already loads before adding a package. `elsarticle`
  loads `graphicx`; `IEEEtran` prefers `cite` over `natbib`; `acmart` loads
  `hyperref` and `booktabs` itself and errors on some redefinitions;
  `sn-jnl` documents its package dependencies in the bundled user manual.
- If a package the author used is incompatible with the class, replace it with
  the class-sanctioned equivalent and note the substitution in the report. Do
  not silently drop functionality that changes how content displays.

## Front matter by class

Build these from extracted values only. Every value that does not exist in the
source becomes a marker (see `fidelity-protocol.md`).

**IEEEtran, journal mode**

```latex
\title{...}
\author{First Author,~\IEEEmembership{Member,~IEEE,} Second Author%
\thanks{Manuscript received ...; affiliations; funding}}
\maketitle
\begin{abstract} ... \end{abstract}
\begin{IEEEkeywords} ... \end{IEEEkeywords}
```

**IEEEtran, conference mode** uses `\IEEEauthorblockN` and `\IEEEauthorblockA`
inside `\author{}` instead.

**elsarticle**

```latex
\begin{frontmatter}
\title{...}
\author[inst1]{Name\corref{cor1}}
\ead{email}
\affiliation[inst1]{organization={...}, city={...}, country={...}}
\cortext[cor1]{Corresponding author}
\begin{abstract} ... \end{abstract}
\begin{keyword} kw1 \sep kw2 \end{keyword}
\end{frontmatter}
```

**sn-jnl**

```latex
\title[Short title]{Full title}
\author*[1]{\fnm{Given}\sur{Family}}\email{...}
\author[2]{\fnm{Given}\sur{Family}}
\affil*[1]{\orgdiv{...}, \orgname{...}, \orgaddress{\city{}, \country{}}}
\abstract{...}
\keywords{kw1, kw2}
\maketitle
```

**acmart** requires `\acmConference`, `\copyrightyear`, `\acmDOI`, `\acmISBN`,
and CCS concepts. All come from the acceptance email or the author.

**mdpi** requires `\Title`, `\Author`, `\AuthorNames`, `\address`,
`\corres`, `\abstract`, `\keyword`, plus the back-matter statement blocks.

**llncs** uses `\institute{}` and `\email{}`, and has no keywords environment in
some versions; check the bundled sample.

When in doubt, copy the macro order from the sample file exactly. Several
classes are order-sensitive and fail obscurely when front matter is rearranged.

## Body

- Map heading levels to `\section`, `\subsection`, `\subsubsection` following
  the source's hierarchy, not the template sample's example headings.
- Keep the author's `\label` names when the source was LaTeX. Cross-references
  break silently otherwise.
- Where the source had no labels (DOCX, PDF origin), add `\label{sec:...}`,
  `\label{fig:...}`, `\label{tab:...}`, `\label{eq:...}` and convert literal
  in-text numbers ("as shown in Figure 3") to `\ref{}` only when the mapping is
  unambiguous. When it is not, leave the literal text alone.
- Preserve emphasis, subscripts, superscripts, and special characters. Escape
  `& % $ # _ { } ~ ^ \` when they arrived as literal characters from a DOCX or
  PDF source, and do not escape them when they arrived as LaTeX markup.
- Non-ASCII characters: `pdflatex` needs `\usepackage[utf8]{inputenc}` on older
  distributions; `xelatex` and `lualatex` handle them natively. Never substitute
  a similar-looking ASCII character for a symbol in a name, a unit, or a
  chemical formula.

## Figures

```latex
\begin{figure}[!t]
  \centering
  \includegraphics[width=\linewidth]{figures/fig1.pdf}
  \caption{Caption text exactly as written.}
  \label{fig:overview}
\end{figure}
```

- Two-column classes use `figure*` for full-width figures. Single-column figures
  in a two-column class must fit `\columnwidth`, not `\textwidth`.
- `pdflatex` reads PDF, PNG, JPG. It does not read EPS without `epstopdf`.
  `latex` + `dvips` needs EPS. Convert if the class requires it, keep the
  original alongside, and note the conversion.
- Never scale a raster figure up. Scaling down is layout; scaling up is data
  loss.
- Some journals require figures at the end of the manuscript, one per page,
  captions on a separate list. That is a requirements-sheet item, not a default.
- Keep figure files in a `figures/` subdirectory unless the portal forbids
  subdirectories, which Elsevier's Editorial Manager effectively does.

## Tables

```latex
\begin{table}[!t]
  \centering
  \caption{Caption above the table, as most journals require.}
  \label{tab:results}
  \begin{tabular}{lrr}
    \toprule
    Method & Accuracy & F1 \\
    \midrule
    ...
    \bottomrule
  \end{tabular}
\end{table}
```

- Caption placement is a journal rule: most put table captions above and figure
  captions below. Follow the sample file.
- Cell contents are copied verbatim, including significant digits and any
  markers such as bold best values, asterisks, and dagger footnotes.
- Wide tables: `table*`, `\resizebox`, `adjustbox`, or landscape. Prefer the one
  the class supports; `\resizebox` on a `tabular` shrinks fonts below the
  journal minimum and gets flagged in production.
- Table footnotes have class-specific mechanisms. Use the sample's mechanism, and
  keep every footnote marker attached to the same cell it was attached to.

## Math

- Move display math verbatim into `equation`, `align`, or the class-sanctioned
  environment. Do not renumber by hand; let LaTeX number.
- `amsmath` conflicts with a few classes that provide their own math handling.
  Check the sample before adding it.
- Keep the author's operator names, symbol choices, and spacing macros. A
  changed symbol is a changed claim.

## Bibliography

Decide between three paths, in order of preference:

1. **The author has a `.bib`.** Keep it. Change `\bibliographystyle{}` to the
   journal's `.bst`, copy the `.bst` next to the main file, and compile through
   BibTeX. Verify that every `\cite` key resolves and that the rendered list
   matches the source list entry for entry.
2. **The author has structured references** (a reference manager export, a
   consistent numbered list with complete fields). Build the `.bib` from that
   data only. Do not fill in a missing DOI, page range, volume, or publisher by
   memory or by inference. Leave the field out, and list the incomplete entries
   in the report for the author to complete.
3. **The references are free text of uncertain completeness.** Use
   `thebibliography` with `\bibitem` entries carrying the original text in the
   original order, restyled only as far as the target style's punctuation
   requires. This preserves the record and produces a submittable document.

Style conversion notes:

- Numeric to author-year: the in-text markers change from `[3]` to
  `(Smith et al., 2020)`, which requires the reference metadata to exist. If it
  does not, path 3 above is the honest answer.
- Author-year to numeric: numbering follows citation order or alphabetical
  order depending on the `.bst`. Verify a sample of markers against the final
  rendered list, including the first, the last, and any in a footnote.
- `natbib` and `biblatex` cannot both be loaded. Several publisher classes load
  `natbib` internally.
- Some journals require DOIs on every reference and some forbid them. This is a
  requirements-sheet item.

## Compile and triage

```bash
python scripts/compile_tex.py build/main.tex --package report/submission.zip
```

Failure classes and what they mean:

| Symptom | Cause | Action |
|---|---|---|
| `File 'x.cls' not found` | class not installed locally | expected; copy the class from the template into the build directory, or ship the zip for Overleaf |
| `Undefined control sequence` on a class macro | wrong class, wrong option, or macro from the old template left behind | check the sample's macro list |
| `Citation 'key' undefined` | BibTeX pass missing, or key absent from the `.bib` | rerun with bibliography passes; verify the key |
| `Overfull \hbox` | a table, a URL, or a long token runs into the margin | fix layout, never by deleting text |
| Figures missing | wrong path, wrong format for the engine | check `\graphicspath` and the format |
| Unicode error under `pdflatex` | non-ASCII character without `inputenc` | add `inputenc` or switch to `xelatex` |

A local failure caused only by a missing class is not a defect. Say so, ship the
package, and note that it compiles on Overleaf or the author's installation.

## Submission package layout

```
submission/
├── main.tex
├── <class>.cls              # when the publisher ships it with the template
├── <style>.bst
├── refs.bib
├── main.bbl                 # some portals require the compiled .bbl
├── figures/
└── BUILD_NOTES.txt
```

Match the manifest in the requirements sheet: portals differ on whether the PDF,
the `.bbl`, the class file, and supplementary files belong in the archive or are
uploaded separately.
