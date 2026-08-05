# Where the official template lives, per publisher

Template details change. Treat this file as a starting point that tells you what
to look for and what usually goes wrong, then confirm against the journal's own
author instructions page before building anything. Record the URL used and the
access date in `FORMAT_REPORT.md`.

## Contents

- [Search strategy for an unlisted journal](#search-strategy-for-an-unlisted-journal)
- [Provenance rules](#provenance-rules)
- [Publisher table](#publisher-table)
- [Per-publisher notes](#per-publisher-notes)
- [What the template never tells you](#what-the-template-never-tells-you)

## Search strategy for an unlisted journal

1. `"<journal name>" author guidelines` or `instructions for authors`. Land on
   the journal's own page on the publisher domain, not a third-party summary.
2. From there follow the link to the template. Most publishers keep one central
   template hub and journals link into it.
3. If no link exists: `"<journal name>" latex template site:<publisher domain>`,
   then `"<journal name>" overleaf template`.
4. Identify the publisher from the journal's homepage and fall back to the
   publisher family template in the table below.
5. As a last resort, the venue may genuinely be format-free at initial
   submission (many Nature Portfolio journals, PLOS, eLife). If the instructions
   say so, say so in the report and build to the general submission requirements
   (double spacing, line numbers, figures at end, references in the house style)
   rather than inventing a house template.

## Provenance rules

- Publisher domain first, publisher-run Overleaf gallery second, mirrors last.
- Confirm the artifact matches the venue before use: open the sample `.tex` or
  the README and check that the journal name, series name, or society appears.
  A template downloaded for the wrong sibling journal compiles fine and is
  rejected at the portal.
- Check the version. `elsarticle.cls`, `acmart.cls`, and `sn-jnl.cls` are all
  actively revised, and the copy bundled with a TeX distribution is often years
  behind what the submission system expects. Prefer the class file shipped
  inside the downloaded template and keep it next to the main `.tex`.
- If the download is paywalled, login-gated, or gone, say so once, use the
  closest official family template, and mark the substitution in the report.

## Publisher table

| Publisher | LaTeX class | Typical class line | Bibliography | Entry point |
|---|---|---|---|---|
| IEEE | `IEEEtran.cls` | `\documentclass[journal]{IEEEtran}`, `[conference]` for conferences | `IEEEtran.bst`, numeric | IEEE Author Center template selector |
| IEEE Access | Access-specific class shipped with the template | per template README | numeric | IEEE Access author page |
| Elsevier | `elsarticle.cls`; CAS journals use `cas-sc.cls` / `cas-dc.cls` | `\documentclass[preprint,12pt]{elsarticle}` | `elsarticle-num.bst`, `elsarticle-harv.bst`, `elsarticle-num-names.bst` | elsevier.com researcher LaTeX instructions |
| Springer Nature journals | `sn-jnl.cls` (legacy `svjour3.cls`) | `\documentclass[pdflatex,sn-vancouver-num]{sn-jnl}` | style selected by class option, `.bst` in the `bst/` folder | Springer Nature LaTeX author support |
| Springer LNCS / LNNS / CCIS | `llncs.cls` | `\documentclass{llncs}` | `splncs04.bst` | Springer conference proceedings guidelines |
| MDPI | `Definitions/mdpi.cls` | `\documentclass[journal,article,submit,moreauthors,pdftex]{Definitions/mdpi}` | `Definitions/mdpi.bst` | mdpi.com layout page, per-journal LaTeX zip |
| Wiley | `WileyNJD-v2.cls` | `\documentclass[<journal option>]{WileyNJD-v2}` | `WileyNJD-AMA.bst` and siblings | Wiley Author Services preparation guidelines |
| Taylor & Francis | `interact.cls` | `\documentclass[]{interact}` | `tfq.bst`, `tfnlm.bst`, `interactapasty.bst`, `interactnumsty.bst` | T&F Author Services LaTeX page |
| ACM | `acmart.cls` | `\documentclass[sigconf]{acmart}`, also `acmsmall`, `manuscript`, `review`, `anonymous` | ACM Reference Format via `\bibliographystyle{ACM-Reference-Format}` | acm.org proceedings template |
| PLOS | `plos_latex_template.tex` | class is `article` with PLOS preamble | `plos2015.bst` | journals.plos.org submission guidelines |
| Frontiers | `frontiersSCNS.cls`, `frontiersENG.cls`, `frontiersHLTH.cls` | `\documentclass[utf8]{frontiersSCNS}` | `frontiersinHLTH&FPHY.bst` etc. | frontiersin.org author guidelines |
| IOP | `iopart.cls` | `\documentclass[12pt]{iopart}` | `iopart-num.bst` | IOP publishing author LaTeX page |
| APS / AIP | `revtex4-2.cls` | `\documentclass[aps,prl,reprint]{revtex4-2}`, `[aip,jap]` for AIP | REVTeX built-in | journals.aps.org / publishing.aip.org |
| Oxford (OUP) | `oup-authoring-template.cls` | `\documentclass[unnumsec,webpdf,contemporary,large]{oup-authoring-template}` | per-journal `.bst` in the zip | OUP author resources |
| SAGE | `sagej.cls` | `\documentclass[times,sageh]{sagej}` | `SageH.bst`, `SageV.bst` | SAGE manuscript submission guidelines |
| Cambridge | per-series CUP class | per template README | per template | CUP author publishing guides |
| arXiv / bioRxiv / medRxiv | none required | any class that produces a clean PDF | any | arxiv.org help |

Class names and options move. When the table disagrees with the downloaded
template, the downloaded template wins.

## Per-publisher notes

**IEEE.** Journal and conference layouts are the same class with different
options, and mixing them is the most common IEEE formatting error. Journals
want `[journal]`, conferences want `[conference]`, and the compsoc and
transmag options change the look substantially. Author blocks use
`\IEEEauthorblockN` and `\IEEEauthorblockA` in conference mode but plain
`\author{}` with `\thanks{}` in journal mode. Keywords go in the
`IEEEkeywords` environment. IEEE requires the biography sections for some
transactions, and PDF eXpress compliance checking at the end.

**Elsevier.** `[preprint,12pt]` is the submission layout; the `1p/3p/5p` options
produce journal-like layouts that are not what the portal wants at submission.
`[review]` gives double spacing. Editorial Manager is strict about file roles at
upload: the `.bib` must be uploaded as a LaTeX file, figures must be at the top
level rather than in subfolders, and the `.cls` should be uploaded alongside the
manuscript when it is not the version the server carries. Elsevier journals also
commonly require highlights (3 to 5 bullets, character-limited), a declaration
of competing interest, CRediT author statements, and a graphical abstract. None
of these exist in a generic manuscript: they are author-supplied and become
markers, not drafted content.

**Springer Nature.** One class, many reference styles selected by class option:
`sn-basic`, `sn-mathphys-num`, `sn-mathphys-ay`, `sn-aps`, `sn-vancouver-num`,
`sn-vancouver-ay`, `sn-apa`, `sn-chicago`, `sn-nature`. Pick the one the journal
names, copy the matching `.bst` from the template's `bst/` folder next to the
main `.tex`, and note that `[referee]` gives double spacing for review and
`[lineno]` adds line numbers, both of which several journals require at
submission. `[iicol]` switches to two columns. Some journals still document the
older `svjour3` while production expects `sn-jnl`; when the instructions and the
submission system disagree, note both in the report and build `sn-jnl` unless
told otherwise. LNCS is a different class entirely (`llncs`) with its own
`\institute` and `splncs04.bst` conventions.

**MDPI.** The template is a directory, not a single file: the class lives at
`Definitions/mdpi.cls` and the class line references that path, so the folder
structure must be preserved in the zip. The journal is a class option
(for example `jimaging`, `sensors`, `applsci`), the `submit` option is for
submission and `accept` for the accepted version, and `moreauthors` versus
`oneauthor` changes the author block. MDPI requires an explicit
`\Title`, `\Author`, `\AuthorNames`, `\isAPAStyle`-type set of front-matter
macros and a set of back-matter statements (author contributions, funding,
institutional review board, informed consent, data availability, conflicts of
interest) that the template lists with placeholder text. Every one the author
has not written is a marker.

**ACM.** `acmart` needs `\acmConference`, `\acmDOI`, `\copyrightyear`,
`\acmISBN`, and the CCS concepts block from the ACM CCS tool. These come from
the acceptance email and the author, never from inference. `[review,anonymous]`
handles double-blind submission, and anonymization changes what the front matter
may contain.

**Frontiers, PLOS, eLife, Nature Portfolio.** Several of these are format-free
or nearly so at initial submission. Do not force a house template where the
instructions say format is free: build the clean submission-ready manuscript
they describe, which usually means continuous line numbers, double spacing,
figures and tables where the instructions say to put them, and the specified
reference style.

**Word-first venues.** Some journals distribute only a `.docx` or `.dotx`. Use
it directly as the pandoc `--reference-doc`. Do not translate a Word-only
journal into LaTeX because LaTeX is nicer to build: the portal validates against
the Word template.

## What the template never tells you

The class file encodes layout. The author instructions encode the rules that
actually get manuscripts desk-rejected. Fetch and read the instructions page
even when a template was supplied, and record:

- word, page, character, figure, table, and reference limits, and the unit each
  limit is counted in
- abstract type (structured with mandated subheadings, or unstructured) and its
  limit
- keyword count and whether a controlled vocabulary applies
- required declaration sections: data availability, code availability, ethics
  approval, consent, funding, conflicts of interest, author contributions
- blinding requirements, and what has to be stripped from the manuscript to
  satisfy them
- figure format, minimum resolution, colour mode, and whether figures go inline
  or at the end
- reference style and whether DOIs are required
- line numbering and line spacing at submission
- the file manifest the portal expects, including cover letter, highlights,
  graphical abstract, and supplementary files
