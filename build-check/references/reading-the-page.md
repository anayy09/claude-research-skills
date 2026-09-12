# Reading the page images

The thumbnails exist so that the pages are looked at, not so that they can
be said to exist. At 45 dpi a page is about 280 by 360 pixels: enough to see
shape, not enough to read. Read the flagged pages first, then every page.

## What a thumbnail shows

- **A table or figure past the margin.** The grey block extends beyond the
  column of text, or the right edge of the text block. The checker's
  overflow finding names the page and the overhang; the thumbnail confirms
  it is a table and not a URL.
- **A float in the wrong place.** A table on a page that is otherwise
  references, or a figure at the end of the document.
- **Half-empty pages.** A page that ends a third of the way down before a
  float or a section: a placement problem, and a page of budget wasted.
- **A heading orphaned at the bottom of a page or column**, with its text
  on the next.
- **Figures at the wrong width.** A single-column figure spanning both
  columns or the reverse; a figure much smaller than its column.
- **Two figures or tables stacked on one page with no text**, which venues
  permit but reviewers dislike.
- **Missing figures**: a caption with blank space above it.

## What needs a zoomed page

Render the page at 150 dpi or more (`pdftoppm -r 150 -f N -l N`) when:

- The overflow finding is a figure or drawing: check whether the artwork
  itself crosses the frame or only a label does.
- A figure has text: labels must be legible at print size, at least the
  venue's minimum (usually 6 to 8 pt after scaling). `manuscript-figures`
  measures this on the figure file; the page render shows it as placed.
- A caption seems to sit on the wrong figure, or a table caption is above
  the table when the venue wants it below.
- The letter, the marked-up copy, or the supplement needs a spot check of a
  specific change: open the page and read the sentence, since a byte-newer
  PDF proves it was rebuilt, not that the edit landed.

## What no render shows

- Whether a number in a table matches the results file.
- Whether the abstract and the conclusion agree.
- Whether the response letter's "see Section 3.2" points at the right text.

Those belong to `manuscript-editor` and the project's own checks.

## Writing the hand-back

Quote the report, page by page where something was found, and say what was
done about each finding. Say which pages were looked at (all of them) and
what was seen that the checks did not report. If nothing was seen, say that
in one sentence; the report is the evidence, the sentence is not.
