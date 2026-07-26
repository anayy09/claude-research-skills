# Modes

Full specification of the seven output modes. Read this once you know which mode
applies, then follow the workflow steps for that mode from SKILL.md.

## Contents

- brief
- report
- lit-review
- fact-check
- verify
- systematic
- scope
- Choosing when unsure

## brief

A fast, cited answer to one focused question. Not a stripped essay: a direct
answer supported by a handful of solid sources.

- Steps: SCOPE → SEARCH → VERIFY → COMPOSE → AUDIT.
- Sources: enough to ground the answer, typically three to six confirmed.
- Output: `assets/brief_template.md`. Lead with the answer, then the evidence,
  then a one-line statement of confidence and any caveat.
- Skip formal synthesis and challenge sections, but still search for at least
  one disconfirming source and disclose it if it exists.

Use for: "What's the current evidence on X?", "Is it true that Y?", single
questions with a knowable answer.

## report

A structured, synthesized report. The default for a broad topic.

- Steps: all seven.
- Sources: enough to cover the main positions in the literature; more than a
  brief, fewer than an exhaustive systematic review.
- Output: `assets/report_template.md` — question, background, methods note,
  findings organized by theme, discussion, limitations, references.
- Synthesis and challenge are mandatory. Conflicting evidence is presented with
  a comparison of quality, not resolved by preference.

Use for: "Research the impact of X on Y", "Give me a report on Z with citations."

## lit-review

An annotated bibliography plus a thematic synthesis of a body of work. The
emphasis is on mapping what exists and where it agrees, conflicts, and leaves
gaps — not on answering a single question.

- Steps: SCOPE → SEARCH → VERIFY → SYNTHESIZE → COMPOSE → AUDIT.
- Sources: broad; aim to represent the major strands of the literature.
- Output: `assets/lit_review_template.md` — an annotated bibliography (each
  entry: citation, relevance, key finding, method, quality grade) followed by a
  synthesis organized by theme, with an explicit gap analysis.

Use for: "Literature review on X", "What does the research say about Y?",
"Annotated bibliography for Z."

## fact-check

A per-claim verdict on specific factual assertions the user supplies or that
appear in a text.

- Steps: SCOPE → SEARCH → VERIFY → COMPOSE → AUDIT, run once per claim.
- For each claim, produce: the claim as stated, a verdict
  (Supported / Partly supported / Not supported / Unverifiable / Misleading),
  the evidence with citations, and a one-line rationale.
- Output: `assets/fact_check_template.md`.
- "Unverifiable" is a legitimate verdict. Do not force a Supported/Not-supported
  call when the evidence does not exist. Distinguish "false" from "no evidence."

Use for: "Check these claims", "Is this article accurate?", "Fact-check this."

## verify

An audit of an existing reference list the user already has. No new research;
the job is to confirm what they hand you.

- Steps: VERIFY → AUDIT only.
- Load the user's references into the source-log schema
  (`references/verification.md`), run `scripts/check_citations.py`, and report
  which sources resolve, which have metadata mismatches, and which are
  unconfirmable. Grade quality where useful.
- Output: a table keyed to the user's list, one row per source, with status and
  any flag (predatory venue, retraction, COI, mismatch).

Use for: "Are these citations real?", "Check my bibliography", "Do these DOIs
resolve?", "I think an AI may have made up some of these references."

## systematic

A PRISMA-style systematic review with an explicit, reproducible search and
screening process, and optional narrative or quantitative synthesis.

- Steps: all seven; SEARCH and VERIFY follow the protocol in
  `references/systematic_review.md`.
- Only report screening counts and yields that reflect searches actually run.
  Do not fabricate a PRISMA flow diagram with invented numbers. If the search
  cannot be exhaustive in this environment, say so and scope the claim to what
  was done.
- Output: protocol (question, eligibility criteria, search strategy), a PRISMA
  flow of real counts, per-study appraisal, synthesis, and a GRADE-style
  certainty statement where applicable.

Use for: "Systematic review of X", "PRISMA review", "meta-analysis of Y."

## scope

Help turning a vague interest into an answerable research question. Iterative
and conversational; produces a question, not a report.

- Steps: SCOPE only, repeated. Follow `references/scoping.md`.
- Ask genuine clarifying questions that surface the user's actual interest,
  constraints, and what would count as an answer. Do not lead them to a
  predetermined conclusion.
- Output: a refined research question with sub-questions and scope boundaries,
  plus a recommendation of which mode to run next.

Use for: "Help me figure out what to research", "I'm interested in X but don't
have a specific question", "Where should I start?"

## Choosing when unsure

- One specific question → `brief`.
- Broad topic, wants a written result → `report`.
- Wants to map a field → `lit-review`.
- Has claims to check → `fact-check`.
- Has a reference list to validate → `verify`.
- Explicitly wants PRISMA / meta-analysis → `systematic`.
- Has no question yet → `scope`.

When still ambiguous, ask. Do not default to the heaviest mode; producing a
12,000-word systematic review for someone who asked a yes/no question is a
failure of judgment, not thoroughness.
