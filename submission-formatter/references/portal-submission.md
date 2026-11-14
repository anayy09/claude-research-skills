# From a built package to a submitted manuscript

The package builds and `build-check` passes. What is left is the part that
has cost the most time: a portal that wants its files flat and named its way,
a form that asks twenty questions the manuscript does not answer in one
place, and a technical check that returns the submission for something small.

## Who does what

- The user signs in to every portal. Never type a password, and never create
  an account.
- The user answers the generative-AI use question and any authorship
  attestation. Prepare nothing for those unless asked.
- Stop before each irreversible control: final Submit, Approve PDF, a licence
  or consent to publish. Say what the click does and wait.
- One manuscript goes to one journal at a time. Packages for other venues are
  staged, not uploaded. If the form asks whether the work is under review
  elsewhere, the answer comes from the user.
- When the built-in browser cannot load the portal, give the user the direct
  submission link and carry on with the files.

## 1. The upload folder

Make one flat folder per venue beside the package, `submission/<venue>-upload/`,
holding exactly the files the portal takes, named for what they are:

```
Manuscript.pdf            Manuscript_source.zip (flat, no subfolders)
Figure_1.pdf ...          Supplementary_Material.pdf
Cover_Letter.pdf          Highlights.docx (Elsevier)
Response_to_Reviewers.pdf Manuscript_marked.pdf (revision rounds)
Author_Biographies.docx   Graphical_Abstract.tif (when required)
FORM_ANSWERS.md
```

The source zip has no nested folders. Springer Nature's and Elsevier's
technical checks return a LaTeX archive that has them. Flatten figure paths
in a copy of `main.tex` and recompile from the flat folder before zipping, so
what is uploaded is what was built.

## 2. The form-answers sheet

`FORM_ANSWERS.md` holds every value the form will ask for, each with the file
it came from, so the user pastes instead of composing at the portal:

| Field | Source |
|---|---|
| Title, short title | manuscript |
| Abstract, cut to the form's limit | manuscript; count words against the limit shown on the form, which can be lower than the author guide |
| Keywords, within the venue's count | manuscript |
| Authors, order, affiliations, ORCIDs, corresponding author | `AUTHORS.yaml` only |
| Funding, competing interests, ethics, consent | `AUTHORS.yaml` or the manuscript's declarations |
| Data availability and code availability | the manuscript's statements; choose the portal's template option that matches them, or paste the statement |
| Article type, section, subject classifications | venue's list, with the choice and the reason |
| Suggested and opposed reviewers | only if the user supplies them |
| Previous submission, preprint, related manuscripts | ask the user; never infer |

Anything the repository does not answer is asked once, as a short list,
before the user opens the form. Write cover letters, highlights, biographies,
and form prose with `manuscript-writing` loaded.

## 3. Checks that prevent a technical-check return

Run these before the upload, and again on any returned submission:

- Every figure and table is called out in the text, and the first callouts
  are in numerical order. A table that is never cited in the body is the
  most common return.
- The abstract has the headings the venue requires (for example Background,
  Methods, Results, Conclusions) and is inside the limit.
- Keywords are inside the venue's range; highlights exist where required and
  each is inside the character limit.
- Required statements are present under the venue's own headings: author
  contributions, funding, competing interests, data availability, ethics.
- The source archive is flat, compiles alone, and contains the `.bbl` or
  `.bib` the venue asks for. No absolute paths, no unused files.
- No placeholder survives: `build-check`'s gate, run on the upload copy.
- Figures meet the stated format and resolution; file names match callouts.
- The response letter never claims a change the manuscript does not show.
  Check each "we now" sentence against the revised file.

When a return arrives, fix the named item in every venue variant that shares
the body, not only the one that bounced, then rebuild the upload folder.

## 4. Double-anonymous venues

Build an anonymized copy; do not edit the named one.

- Remove names, affiliations, emails, ORCIDs, acknowledgements, and funding
  from the PDF and the source, and strip document metadata (PDF properties,
  Word author fields, file names).
- Refer to the authors' earlier work in the third person.
- A repository or archive link that names the authors cannot stay. Either
  give an anonymized mirror the user has approved, or state that code and
  data are held for anonymity and will be released on acceptance. Do not
  leave a visible placeholder.
- The cover letter carries no identifying detail when the venue says so.
- Keep a private note of the real author order for the user.

## 5. After the upload

- The portal builds its own PDF. Compare it with ours using `build-check`'s
  `compare_portal_pdf.py`, and check that each file sits in the right field.
- Record the submission in the project's progress log: venue, date, the
  portal's manuscript ID, and the files uploaded.
- A licence or consent form the venue supplies is filled in the supplied
  file, leaving the signature to the signing author.
