# The editorial read

The check that the audit script cannot do. It is a paragraph-by-paragraph
pass over the whole manuscript with three questions per paragraph and three
running indexes, followed by section-level and manuscript-level tests. It
produces an editorial report with a prioritized cut list. Run it before any
revision round begins and again after the batch of changes.

Contents

1. Three questions per paragraph
2. The three indexes
3. Section-level tests
4. Manuscript-level tests
5. Cut decisions: what to do with each finding
6. The editorial report

## 1. Three questions per paragraph

Read each paragraph and write one line in a scratch table: section,
paragraph number, and the answers.

**Q1. What is this paragraph's one job?** Name it in a few words: "defines
acquisition context", "reports the primary contrast", "states limitation:
single site". A paragraph with two jobs is split. A paragraph whose job is
"reassures", "emphasizes", "restates", "explains why this paragraph exists",
or "answers an imagined objection" has no manuscript job; mark it for
deletion or extraction (section 5).

**Q2. Is this the first place that job is done?** Check the scratch table so
far. If the same job already appears, this paragraph is a restatement. Mark
which of the two is the home (the one in the section whose job it is, or
the one with the fuller evidence) and the other for merge or deletion. Do
this at the level of the claim, not the sentence: "waveform arm retains
most of its advantage under matching" is one job whether it is phrased with
0.9313, "most", or "not mostly the decision to record".

**Q3. Does the first sentence connect to what the previous paragraph
established?** The connection is a thing, not a word: the previous
paragraph introduced X, this one does something with X. If the first
sentence could open any paragraph in the section (an aphorism, a general
truth, a restatement of the section's topic), the paragraph is floating.
Mark it; the fix is usually reordering or a rewritten first sentence that
names the dependency.

While answering these, tag any sentence that belongs to families B to F in
`references/manuscript-boundary.md`: announced restraint, protocol refrain,
reader management, internal artifacts, objection frames. The audit script
will list most of them, but the read catches the paraphrased ones ("we
would not offer that as reassurance", "which is the reason to report them
rather than to treat them as a local curiosity").

## 2. The three indexes

Build these as the read proceeds. They are the instruments for the
one-home rules and they go in the revision ledger so later rounds inherit
them.

**Claim index.** Every claim the paper makes about its results, with every
location where it is stated and the strength at each location. Columns:
claim, locations, strength at each, home. The home is Results for the
number and Discussion for the interpretation; the abstract, contributions,
and conclusion may carry it once each in shortened form. Any further
location is cut. Strength must be identical everywhere.

**Justification index.** Every explanation of why something was done or why
an objection does not apply: why a threshold, why a denominator, why a
feature cannot leak, why recalibration was out of scope, why a test is
underpowered, why a reproduction gate is easy. Columns: justification,
locations, home. Home is where the choice is introduced, almost always
Methods. Every other location becomes the bare fact plus a cross-reference
("the threshold was 0.10 (Methods)"), or nothing. A justification that
appears in Methods, in Results, in Discussion, in Limitations, and in a
table note has been defended four times too many.

**Summary index.** Every paragraph that summarizes the paper: lists its
findings, its failed or met targets, its contributions, or its headline
numbers together. Budget outside the abstract: end of Introduction, first
paragraph of Discussion, Conclusion. Anything else (a Results "summary of
outcomes" prose section, a Discussion "what failed" section that re-lists
the targets with their numbers, a limitations paragraph that restates the
findings before limiting them) is cut to a table or a cross-reference.

## 3. Section-level tests

After the paragraphs of a section are tabled:

**Outline test.** Read only the first sentences of the section's
paragraphs in order. They should read as an outline of an argument that a
reader could follow without the paragraphs. If they read as a list of
independent assertions, the section is stitched; reorder, merge, or rewrite
openings until the outline holds.

**Job test.** The section does its own job and no other's. Methods that
interpret, Results that argue, a Discussion that re-explains the problem, an
Introduction that reviews methodology: each paragraph doing another
section's job is moved.

**Proportion test.** Against the venue conventions
(`references/journal-conventions.md`): Introduction plus related work under
about a quarter of the body; Discussion not much longer than Results;
Limitations a bounded part of the Discussion with one paragraph per
limitation; Conclusion under a tenth. The audit's outline gives the numbers.

**Subsection-title test.** Titles that describe what the authors did
editorially ("Two neighbouring questions, kept separate", "The gap, stated
so it can be checked", "Objections", "What failed, and why it is here") are
symptoms: the section's content is organized around the authors' conduct
rather than the study. Retitle to the content and re-read.

## 4. Manuscript-level tests

**Four mirrors.** Abstract, contributions, first Discussion paragraph,
Conclusion: same claims, same numbers, same strength, each shorter than the
last and no shared sentence (`references/coherence-audit.md`, section 4).

**Citation job test.** For each reference, which of the four jobs does it do
(gap, method, comparator or precedent, counter-example)? A reference with no
job is removed. A cluster of references from another field making a point
about research practice is reduced to one sentence. Studies asking a
neighbouring question the paper does not answer get one sentence each if a
reader would otherwise confuse the two, otherwise nothing. The literature
search method, if the paper has one, is one Methods paragraph or a
supplement, and any table of screened studies is supplementary.

**Vocabulary test.** Terms the authors coined during the project ("kill
experiment", "strengthener", "gate", decision ids, arm labels like
`R3_acqctx_pre` outside tables) are either defined once and used
consistently as manuscript terms or replaced with plain language. Internal
ids and paths are removed.

**Display-item text test.** Every caption and table note describes; none
argues, warns, or shouts; none carries plan vocabulary or decision ids. The
sentence that prevents a misreading of a table goes once in the text where
the table is cited.

**Tone test.** Count the sentences whose subject is the authors' conduct
("we would rather", "we declined", "we report X because", "we are explicit
that", "we say so"). The target is zero. Integrity is demonstrated by the
table of registered targets with measured values and by limitations stated
once. Narrating it converts a strength into a tic.

## 5. Cut decisions: what to do with each finding

| Finding | Action |
|---|---|
| Restated claim (Q2) | Keep the home; reduce others to a cross-reference or delete |
| Justification in 2+ homes | Keep in Methods; elsewhere bare fact + "(Methods)" |
| Summary paragraph beyond budget | Table if the venue wants a registered-outcomes table; otherwise delete |
| Family B sentence (self-commentary) | Delete the frame; keep any fact inside it |
| Family C sentence (protocol refrain) | Delete; ensure the one Methods statement exists |
| Family D sentence (reader management) | Replace with the claim's scope stated as fact |
| Family E (internal artifact) | Delete or move to supplement; define any term kept |
| Family F (objection frame) | Move substance to Methods rationale or Limitations; delete frame and title |
| Floating paragraph (Q3) | Reorder, or rewrite the opening to name the dependency |
| Literature-search method in Introduction | Move to Methods paragraph or supplement |
| Screened-study table in Introduction | Move to supplement; cite the finding in prose |
| Citation with no job | Remove; renumber |
| Neighbouring-question subsection | One sentence each, or nothing |
| Limitation re-explaining Methods | Cut to the limitation, mechanism, consequence, and a cross-reference |
| Caption that argues | Move the argument to text (once); caption describes |
| Aphoristic opener on every paragraph | Keep at most one per section; rewrite the rest to connect |

Apply `research-paper-writing` to whatever sentences are rewritten.

## 6. The editorial report

Deliver the read as a report before making changes in editorial-pass mode,
so the author can approve the cut list. Template in
`assets/editorial-report.md`. It contains:

1. One paragraph: what the manuscript is doing well and what the dominant
   failure pattern is (reviewer leakage, self-commentary, restatement,
   citation sprawl, stitching), with counts from the audit.
2. The three indexes, or the parts of them with more than one location.
3. Section-by-section findings with the outline test result.
4. A prioritized cut list: each item with location, action, and estimated
   words saved. Order by words saved and by damage to credibility.
5. What the read could not decide without the author: claims whose evidence
   was not found, citations whose job is unclear, terms that might be
   field-standard.
6. Before/after section word counts projected from the cut list.

The report is the deliverable in editorial-pass mode; the revised manuscript
follows only after the author has seen it, because cuts of this kind are
editorial judgments the author has to own.
