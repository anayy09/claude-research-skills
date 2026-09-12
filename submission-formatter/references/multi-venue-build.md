# One body, several venues

A manuscript kept ready for two or three venues is a build pipeline, not a
set of copies. The body is written once; every per-venue difference lives in
a spec and in per-venue templates; every package is regenerated from them
after each editorial pass; and the built PDFs go through `build-check`.

## What differs per venue and where it goes

| Difference | Where it lives |
|---|---|
| document class, options, packages | the venue template (`templates/<venue>-main.tex`) |
| author block macros (`\author[1]{}`+`\ead`, `\fnm\sur`+`\affil`, `\thanks`) | rendered by `build_targets.py` from `AUTHORS.yaml` per class |
| abstract length, keyword count | `max_keywords` in the spec; the abstract is one file and its length is an editorial decision made once |
| appendices, extended results, a summary table the cap cannot afford | `% {{begin:NAME}} ... % {{end:NAME}}` regions in the body, dropped per target |
| citation command | `\citep`/`\citet` in the body; rewritten to `\cite` for non-natbib classes |
| bibliography style | the venue template |
| page cap | `page_cap` in the spec; `build_targets.py --check` measures against it |
| class and `.bst` files the TeX tree lacks | `assets` in the spec, copied into the package (Springer's `sn-jnl` needs the class and its `.bst` files beside `main.tex`) |

Nothing else differs. A sentence that has to read differently for one venue
is a sign the body is carrying venue-specific prose; move it to a region or
rewrite it so one version serves all.

## The guard

`build_targets.py` records what it rendered. If `main.tex` was edited by
hand since, it refuses to overwrite, writes `main.tex.regenerated` beside
it, and says so. That guard exists because a rebuild once silently reverted
co-authors that had been added to one package by hand. The fix for the
refusal is never `--force` by reflex: move the hand edit into the body or
the template, then render again.

## Symbolic numbering

Write `Table~\ref{tab:arms}` and `Figure~\ref{fig:flow}`, never a printed
number. Each class places floats differently, so a number typed into the
prose is right in at most one package. Body tables written inline need
labels too, or `build-check` reports them as never cited.

## The loop

1. Edit the body, the abstract, the keywords, or `AUTHORS.yaml`. Never a
   package.
2. `python scripts/build_targets.py targets.yaml --check`.
3. Read each `BUILD_REPORT.md`: pages against the cap, overflow, floats,
   identity, placeholders.
4. When a package is over its cap, the cut is made in the body or by adding
   a region to that target's `drop` list, then step 2 again
   (`manuscript-editor`, budget mode).
5. Commit the body, the spec, the templates, and the rendered packages
   together, so a package never carries prose the body does not.

## Cover letters and per-venue front matter

Highlights, a graphical abstract, CRediT roles, declarations, and the cover
letter are venue items, not body items. Keep each as a file under
`submission/<venue>/`, generated from `AUTHORS.yaml` where the content is
identity, and listed in `FORMAT_REPORT.md` as author actions where it is
not. Page and word counts quoted in a cover letter come from the last
`build-check` report, not from memory.
