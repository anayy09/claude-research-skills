# Building the Word submission

Word output is required when the venue accepts Word only, when the template is a
`.docx` or `.dotx`, or when the author asks for it. The mechanism is pandoc's
`--reference-doc`, which applies the template's styles to converted content.

## Contents

- [Reference-doc workflow](#reference-doc-workflow)
- [Style mapping](#style-mapping)
- [Front matter](#front-matter)
- [Figures and captions](#figures-and-captions)
- [Tables](#tables)
- [Equations](#equations)
- [References](#references)
- [Page setup requirements](#page-setup-requirements)
- [Direct manipulation with python-docx](#direct-manipulation-with-python-docx)
- [Verification](#verification)

## Reference-doc workflow

```bash
# 1. see what styles the template defines
python scripts/inspect_template.py template/journal-template.docx

# 2. build from the extracted markdown, applying the template's styles
pandoc build/extracted.md \
  --reference-doc=template/journal-template.docx \
  --from=markdown \
  --resource-path=build \
  -o build/manuscript.docx
```

Two facts about `--reference-doc` that drive everything else:

- It applies **styles**, not content. Placeholder text, sample headings, and
  instructions inside the template do not carry over, which is what you want.
- It maps pandoc's built-in style names (`Title`, `Author`, `Abstract`,
  `Heading 1`..`Heading 6`, `Body Text`, `Image Caption`, `Table Caption`,
  `Compact`, `Source Code`) to whatever the template defines under those names.
  When the journal uses different names ("MDPI_1.1_title", "Els-body-text"),
  pandoc will not find them, and the style has to be applied after the fact.

When names do not match, two options: rename the styles in a working copy of the
template so they match pandoc's expectations, or post-process with `python-docx`
to reassign styles paragraph by paragraph. Renaming is faster and less
error-prone; note it in the report either way.

If no journal `.docx` template exists, build with a clean default and set page
setup, spacing, and line numbering from the requirements sheet.

## Style mapping

Write the mapping into the report before building:

| Content | Pandoc style | Template style |
|---|---|---|
| Title | Title | e.g. "Article Title" |
| Authors | Author | e.g. "Author Names" |
| Affiliations | Author | e.g. "Affiliation" |
| Abstract body | Abstract | e.g. "Abstract Text" |
| Section heading | Heading 1 | e.g. "Heading 1" |
| Body paragraph | Body Text / First Paragraph | e.g. "Paragraph" |
| Figure caption | Image Caption | e.g. "Figure Caption" |
| Table caption | Table Caption | e.g. "Table Caption" |
| Reference entry | Bibliography | e.g. "References" |

Journals distinguish first paragraphs (not indented) from subsequent ones
(indented). Pandoc's `First Paragraph` and `Body Text` cover this when the
template defines both.

## Front matter

Word templates rarely have front-matter macros, so the front matter is ordinary
paragraphs with specific styles. Build it in the template's order, which
`inspect_template.py` prints from the template's own headings.

Every element required by the template that does not exist in the source becomes
a visible marker paragraph, not invented text. See `fidelity-protocol.md`.

## Figures and captions

- Insert images from `build/media/` at original resolution. Set display width
  only; do not resample.
- Caption text is verbatim. Caption position (above or below) follows the
  template.
- Word auto-numbering fields are not worth reconstructing for a submission.
  Literal numbers matching the source are correct and stable. If the author
  wants live fields, that is a Word-side task for them.
- Several journals want figures at the end of the file or as separate uploads
  with only a caption list in the manuscript. Requirements-sheet item.

## Tables

- Pandoc builds tables with the template's `Table` style when one is defined.
- Merged cells do not survive markdown round-tripping. When the source has
  merged cells, either build the table with `python-docx` directly or rebuild it
  in the output and verify cell by cell against the source.
- Keep cell contents, row order, column order, and significant digits exactly.
- Table footnotes usually become a plain paragraph under the table in the
  template's footnote style.

## Equations

- Pandoc converts LaTeX math to OMML, which Word renders as native editable
  equations. This is the good path.
- Equations that arrived as images stay images. Flag them.
- Check every converted equation visually. OMML conversion is reliable for
  standard constructs and less so for custom macros, `\substack`, aligned
  multi-line environments, and unusual delimiters.

## References

- Plain text reference list in the required style, in the required order.
- Do not attempt to recreate reference-manager field codes. If the author needs
  them live, they re-link in Word; say so once.
- In-text markers must match the list. When the style changes (numeric to
  author-year or the reverse), verify the mapping end to end, sampling at least
  the first, last, and any marker inside a caption or footnote.

## Page setup requirements

Common submission requirements that live outside the template file:

- double or 1.5 line spacing during review
- continuous line numbers (Word: Layout, Line Numbers, Continuous)
- specific margins, page size (A4 versus Letter), and font
- page numbers in a specific position
- headers stripped for blinded review

`python-docx` sets margins, page size, and spacing directly. Line numbering
requires editing the section properties XML, which is worth doing when the
journal demands it, since reviewers often check.

## Direct manipulation with python-docx

Use it when pandoc's output needs style reassignment, when tables have merged
cells, or when page setup has to be enforced:

```python
import docx
d = docx.Document("build/manuscript.docx")

for p in d.paragraphs:
    if p.style.name == "Heading 1":
        p.style = d.styles["Els-1storder-head"]

s = d.sections[0]
s.left_margin = s.right_margin = docx.shared.Cm(2.5)

d.save("build/manuscript.docx")
```

Only structure and styling are edited this way. Text runs are not rewritten.

## Verification

```bash
python scripts/fidelity_check.py \
  --source build/manuscript.json \
  --output build/manuscript.docx \
  --json report/fidelity.json
```

Then open the file and confirm what the checker cannot see: styles actually
applied rather than defaulting, figures at the right position and size, tables
not overflowing the page, equations rendering, and the front matter in the
template's order.
