# Reporting AI use in evidence synthesis

## The current expectation

In 2025, Cochrane, the Campbell Collaboration, JBI, and the Collaboration for
Environmental Evidence issued a joint position statement on AI use in evidence
synthesis, published across their journals. Its substance:

1. The synthesist is responsible for the synthesis, including the decision to
   use AI and compliance with legal and ethical standards.
2. All four organizations support the RAISE recommendations (Thomas et al.,
   2025), which set out responsibilities across roles in the evidence synthesis
   ecosystem: synthesists, methodologists, tool developers, producing
   organizations, publishers, funders, users, and trainers.
3. AI and automation may be used, provided the author can demonstrate that it
   does not compromise methodological rigour or integrity.
4. Human oversight is required.
5. Any AI use that makes or suggests judgments must be reported fully and
   transparently.

RAISE itself is published in parts: recommendations for practice, guidance on
building and evaluating AI tools for evidence synthesis, and guidance on
selecting and using them. It is designed as living guidance and will change;
check the current version before citing it in a methods section.

A partial update of PRISMA 2020 to incorporate guidance on AI tool use in the
review process was under development as of mid-2026. When it lands, it becomes
the reporting reference and this section should be revised.

## Which uses need disclosure

The test is whether the AI made or informed a judgment. Formatting a table does
not; deciding what goes in it does.

| Stage | Disclose? |
|---|---|
| Generating or translating search strings | yes: the search is a method |
| Deduplication by an automated tool | yes: name the tool and settings |
| Title/abstract screening decisions or prioritization | yes |
| Full-text eligibility decisions | yes |
| Data extraction | yes |
| Risk-of-bias judgments | yes |
| Certainty (GRADE) judgments | yes |
| Drafting interpretive summaries or the discussion | yes |
| Language editing of text whose content the authors determined | generally no, though some journals ask; check the journal policy |
| Reference formatting | no |

When in doubt, disclose. A disclosed use that turned out not to need disclosure
costs two lines. An undisclosed judgment-making use discovered later is a
research integrity problem.

## What a disclosure has to contain

RAISE-aligned reporting asks for four things:

1. **Tool identity**: name, version, and provider. "An AI assistant" is not an
   identification. Model versions change behavior, so the version matters.
2. **Dates of use**: because tools change under a stable name.
3. **Purpose and stage**: which part of the synthesis, doing what.
4. **How it was used, and how it was checked**: the human verification
   procedure, the proportion checked if not all, and what happened to
   disagreements.

The fourth is the one most often omitted and the one reviewers care about. "We
used an LLM for screening" describes nothing. "One reviewer screened all titles;
an LLM independently screened the same set; a second human adjudicated all
disagreements and a random 10 percent of agreements" describes a method that can
be evaluated.

## Validation before use, not after

Before letting a tool make or suggest judgments on your review, measure it on
your data: take a sample you have already screened or extracted by hand and
compare. Report sensitivity for screening (missing an includable study is the
costly error, so sensitivity matters more than precision), and agreement
statistics for extraction or appraisal.

A tool that performed well in a published evaluation on someone else's corpus
has not been validated on yours. Topic, terminology, and inclusion criteria all
affect performance.

## Sensible defaults

- **Screening**: acceptable as a second screener alongside a human, or for
  prioritization, with human adjudication of all disagreements. Not acceptable as
  the only screener for an includable/excludable decision.
- **Extraction**: acceptable as a first pass with human verification of every
  extracted field that enters an analysis. Numbers entering a meta-analysis
  should be checked against the source by a human, every time.
- **Appraisal**: acceptable as a draft with human confirmation per domain.
  Domain judgments require reading the methods section; a model summarizing an
  abstract is not doing that.
- **Interpretation and conclusions**: the authors', with AI assistance disclosed.
- **Citations**: never trusted. Verified mechanically
  (`references/verification-protocol.md`).

## Template

`templates/ai-disclosure.md` contains a statement to adapt. Place it in the
methods section, not only in an acknowledgements line, when the use touched a
judgment. Journals increasingly require both.

## Two failure modes worth naming

**Laundering.** Producing a judgment with a model, checking it superficially, and
reporting it as a human judgment. This is the failure the position statement's
oversight requirement exists to prevent, and it is undetectable in the finished
paper, which is exactly why the disclosure obligation is on the author.

**Blanket disclaiming.** A generic sentence saying AI was used somewhere, without
saying where or how. It satisfies nobody: it neither describes a method nor
protects the author, and reviewers read it as an admission with the details
withheld.
