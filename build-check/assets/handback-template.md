# Build hand-back

Use after the second (post-fix) run of `build_check.py`. Quote numbers from
the report, not from memory.

## Result

| Target | Pages / cap | Overflow | Floats | Fonts | Words / guidance | Report |
|---|---|---|---|---|---|---|
| `submission/<venue>/main.tex` | 16 / 16 | none | in section | embedded | 7,900 / none | `build-check/BUILD_REPORT.md` |

## What was found and fixed

- Page 5: Table 3 ran 41 pt past the column; reset with `\footnotesize` and
  `tabcolsep` 4 pt. Now inside the edge.
- Figure 2 was on page 14, inside the references; moved its source to
  follow the citing paragraph in Section 3.2. Now page 6.

## Warnings that remain, and why

- Overfull 6 pt on page 9: a DOI in the reference list; the `.bst` cannot
  break it and the venue's typesetter will reflow it.

## Pages looked at

All N, at thumbnail size; pages 5, 6, 9, and 14 at 150 dpi. Nothing else
seen.

## Derived artifacts

- `letter/response.pdf` rebuilt from `letter/response.md` (newer by 2 min).
- `paper/marked-up.pdf` rebuilt after the last edit.

## Not checked here

Figure label sizes at print width (`manuscript-figures`), venue upload
checks (`submission-formatter`).
