# Revision ledger: [short manuscript title]

Internal document. Never submitted. One file per manuscript, updated every
round. Future rounds start by reading this.

## Manuscript state

- Working file: [path or filename]
- Target venue and article type: [e.g. npj Digital Medicine, Article]
- Budget: abstract [n] words; main text [n] words incl./excl. Methods; display items [n]; references [n]
- Venue notes (derived from author guide and recent articles, see references/journal-conventions.md):
  - [e.g. Methods after references; Reporting Summary required; unstructured abstract]
- Voice and tense: [we / passive; Methods past, Results past, Discussion present]
- Version history:
  - v1 submitted [date]
  - R1 decision [date]: [major/minor], [n] reviewers
  - v2 in progress

## Canonical terminology

One form per concept. The audit script flags variants; this list says which wins.

| Concept | Use | Do not use |
|---|---|---|
| [gradient-boosted model] | gradient-boosted | gradient boosted, GBM (except in tables) |
| [dataset] | dataset | data set, data-set |

Acronyms defined at first use in body: [AUROC, ICI, ...]. Spelled out always: [...]

## Standing decisions

Do not reopen without a new reason. Record the reason so it can be judged later.

- D1 [date]: [e.g. No comparison to method X; requires paired measurements not in either cohort. R1.4]
- D2 [date]: [e.g. Single external site is stated as a limitation in Discussion para 5, once. R1.2, R2.2]
- D3 [date]: [e.g. Conclusion capped at 150 words; reviewer request for a longer one declined. E.1]

## Items (current round)

| ID | Comment (short) | Change type | Location | What changed | Status |
|---|---|---|---|---|---|
| R1.1 | Methods unclear on imputation | Edit in place | Methods, Preprocessing | Rewrote the imputation sentence; added window length | done |
| R1.2 | Only one external site | Edit in place | Discussion, para 5 | Merged two limitation sentences into one with mechanism | done |
| R2.1 | Sensitivity analysis excl. missing lactate | Insert | Methods, Sensitivity analyses; Results, para 4; Table S3 | New 2-sentence Methods para, 1 Results sentence, supplement table | done |
| R2.3 | Pediatric generalization? | Needs author input | Discussion, limitations | Placeholder inserted | open |
| E.1 | Shorten conclusion | Edit in place | Conclusion | Cut restated discussion; 190 to 150 words | done |

Change types: response only, edit in place, insert, new paragraph/subsection, supplementary, declined, needs author input.

## Placeholders outstanding

- [Section, para]: [AUTHOR INPUT: ...] (item R2.3)

## Deferred and declined

- R1.4 declined: [reason]. Response written.
- R2.5 deferred to a follow-up study: [reason]. Limitation sentence added.

## Section word counts by round

| Section | v1 | v2 | Delta | Items |
|---|---|---|---|---|
| Introduction | | | | |
| Methods | | | | |
| Results | | | | |
| Discussion | | | | |
| Conclusion | | | | |
