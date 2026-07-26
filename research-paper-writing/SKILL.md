---
name: research-paper-writing
description: >
  Use this skill whenever the user asks you to write, rewrite, edit, or extend
  academic research prose: paper sections (introduction, related work, method,
  results, discussion, conclusion), thesis chapters, rebuttals and response
  letters, conference or journal submissions, and technical reports. Also use
  it for requests like "make this sound less like AI wrote it", "tighten this
  paragraph", "write the related work", "help me phrase this contribution", or
  any request to produce or repair scholarly writing that has to read as if a
  working researcher wrote it. Do not use for casual summaries, blog posts,
  marketing copy, slide bullet text, or code generation.
summary: "Scholarly prose that reads like a working researcher wrote it."
version: "2.0.0"
author: anayy09
license: MIT
metadata:
  status: active
  last_updated: "2026-07-25"
---

# Research Paper Writing

## What this skill is for

The output should read like it was written by someone who did the work, cares
about being right, and is writing to be understood by a skeptical reviewer in
the same field. That person is not trying to sound impressive. They are trying
to make a claim, support it, and be honest about where it breaks.

Most detectable-AI writing fails not because of specific banned words but
because it has no argument underneath it. It states things at a uniform level
of confidence, never commits to a position on the literature, treats every
result as good news, and pads transitions to sound coherent. Fix the substance
and most surface tells disappear on their own. Everything below serves that
goal; treat it as reasoning to internalize, not a checklist to satisfy.

## The one thing that matters most: have a real claim per paragraph

Before writing a paragraph, know what it is asserting and what backs it up. A
paragraph is doing one of a small number of jobs:

- Making a claim and justifying it.
- Explaining a design decision and the reason behind it.
- Reporting a result and saying what it means, not just what it is.
- Stating a limitation and why it happens.
- Positioning against prior work: what they did, where it held, where it did
  not, and what that leaves open.

If a paragraph is not doing one of these, it is probably filler. The most
common filler paragraph is the one that announces what the next section will
cover. Cut it unless the section is genuinely long enough that a reader needs
a map.

This is also the deepest fix for AI tone. Text that is organized around real
claims naturally varies in rhythm, commits to positions, and stops when the
point is made, because the content is driving the prose instead of a template.

## Technical honesty

This is what separates credible research writing from the rest.

- When a method works, say so and say *why*, specifically. "The model improved
  recall because the auxiliary loss forced it to attend to the minority class"
  is useful. "The results demonstrate strong performance" is not.
- When something fails or is limited, name it plainly. Do not hedge a real
  limitation into invisibility. A results section with no failure modes reads
  as either naive or dishonest, and reviewers notice.
- Match confidence to evidence. If the data support a conclusion, state it
  without armor. If they only suggest it, use "suggests", "appears to", "is
  consistent with", and mean it. The failure mode to avoid is uniform hedging,
  where every sentence carries the same "may potentially" cushion regardless of
  how strong the evidence actually is.
- Preserve the user's technical claims exactly. Do not invent numbers, soften a
  stated result, strengthen a hedged one, or add a comparison the user did not
  make. If a claim seems wrong or unsupported, flag it to the user rather than
  silently editing it.
- Use the correct technical term rather than a friendlier paraphrase. Precision
  is not the enemy of readability here; the audience knows the vocabulary.

## Positioning against prior work

Cite by what a paper *did*, not by a number floating in a sentence.

Weak: "Prior work [3] has addressed this problem."
Better: "Lin et al. [3] handled occlusion by training on synthetic depth maps,
which worked in simulation but needed paired RGB-D data that is expensive to
collect at scale."

The gap you are filling should be visible through your reading of what came
before, not bolted on as a separate "however, a gap remains" sentence. Be
willing to be mildly critical. Uniformly positive summaries of the literature
are both less informative and an obvious tell, because no working researcher
believes every prior method was impressive.

## On sentence variety (read this carefully, it is easy to get wrong)

Good research prose has varied rhythm, but you cannot get there by targeting
percentages or by deliberately inserting short punchy sentences. That produces
its own recognizable pattern: prose that visibly performs "humanness" and reads
as try-hard. It is as detectable as the uniform version, just differently.

The reliable route to natural rhythm is to let the ideas set the length. A
qualification that genuinely needs three clauses gets a long sentence. A point
that lands hard gets a short one. If you are writing to real content and one
idea per sentence, variety follows.

Two things to actually watch for, because they are failure modes rather than
targets:
- Do not let three or four sentences in a row share the same subject-verb shape
  ("The model does X. The model achieves Y. The model outperforms Z."). That
  monotony is real and worth breaking, but break it by reordering the
  *thought*, not by cosmetic reshuffling.
- Do not open consecutive paragraphs with the same word, especially "The",
  "This", "We", "These". If two in a row start the same way, one of them is
  probably not starting where its actual point starts.

## Connectives and transitions

The problem with "Furthermore", "Moreover", "It is worth noting that",
"Notably", "Importantly" is not that the words are forbidden. It is that they
usually paper over a missing logical link. If sentence B follows from sentence
A, the reader can often see it without a signpost, or the real relationship is
more specific than "furthermore" ("which also means", "the same effect shows
up in", "this breaks down when").

So the instruction is not "never use these words." It is: when you reach for a
generic connective, check whether there is a real relationship to state
instead. Often there is, and stating it is more informative. Sometimes a plain
"and" or a new sentence with no connective at all is best. A stray "however" or
"in addition" is fine; a paragraph held together entirely by them is the tell.

Avoid the review-bait vocabulary that adds heat but no information:
groundbreaking, revolutionary, novel (unless the novelty is the specific claim
and you can defend it), state-of-the-art as an adjective, robust and efficient,
seamless, powerful, cutting-edge, "sheds light on", "delves into", "plays a
vital role", "leverages" (use "uses"), "utilize" (use "use"), "in order to"
(use "to"). These are not banned tokens to grep for; they are symptoms of
describing importance instead of stating content. Replace the *move*, not just
the word.

## Voice

Pick first-person convention per section and hold it. "We" is the default for
methods and results in most fields. "I" is fine for a single-author thesis if
the user writes that way. Do not switch mid-section. Match whatever convention
the user's existing text or field uses; when unsure, ask or default to "we".

## Section-specific notes

**Introduction.** Open on the actual problem, not on why the field matters in
general. One sentence at most on broad importance, then get to the specific
gap. End on concrete contributions stated as what was done, not "this paper
aims to". "We show that X, and that the standard assumption Y fails under Z" is
a contribution; "this paper aims to explore X" is not.

**Related work.** Organize by idea or approach, not by date, unless the
chronology is itself the point. Every entry: what they did, where it worked,
where it did not. Let the gap emerge from the critique.

**Method.** Explain decisions, not just choices. Why this architecture, this
loss, this split, this hyperparameter. If a choice was empirical (you tried it
and it worked better), say that plainly; it is honest and it is useful to a
reader trying to reproduce or build on the work.

**Results.** Lead with what the numbers mean, then the numbers. Name the
baseline, name the gap, interpret the gap. Include failure cases and edge
conditions; their absence undermines credibility.

**Discussion.** Interpret and extend; do not restate results. This is where
tentative explanation is allowed, but flag it: "one likely explanation is",
"we suspect this is because". Distinguish what you showed from what you infer.

**Conclusion.** No new claims or numbers. Summarize tightly. One forward-looking
sentence is plenty; a full future-work paragraph belongs in the discussion if
it belongs anywhere.

## Rebuttals and response letters

When the user is responding to reviewers: address each point directly, concede
what is correct without groveling, and push back on what is wrong with evidence
rather than deference. State exactly what changed in the manuscript and where.
Keep the register professional and factual, not defensive and not effusive.

## When rewriting existing text

1. Read the whole passage first and work out what it is trying to claim.
2. Rewrite from that understanding, not sentence by sentence. Sentence-level
   rephrasing keeps the original's structure and usually its problems.
3. Keep every technical claim intact. Do not add, drop, soften, or strengthen a
   claim without being asked. Flag anything that looks wrong instead of
   quietly changing it.
4. Preserve the user's voice and terminology. Make the minimum changes that fix
   the actual problem. If they asked to fix tone, fix tone; do not also rewrite
   correct content.
5. If the result comes out suspiciously smooth and uniform, the fix is not to
   sprinkle in short sentences. Go back and check that each paragraph is built
   on a real claim; uniformity is almost always a symptom of prose that is
   describing rather than arguing.

## A worked contrast

Weak (uniform, describes importance, no real claim):
> Our proposed method achieves state-of-the-art performance. It is worth noting
> that the model demonstrates robust results across all benchmarks.
> Furthermore, it plays a key role in advancing the field.

Better (commits, explains, admits a boundary):
> Our method beats the 2D CNN baseline by 6 points of F1 on ISL-50. The gain
> comes almost entirely from the temporal module: on static signs the two
> models are within noise of each other, and the advantage only shows up on
> signs with motion. Cross-signer accuracy still drops about 12 points, which
> is the limitation we care most about and have not solved.

Notice what changed. The second version has a number tied to a baseline, an
explanation of where the gain comes from, a scope condition (static vs.
motion), and an honest limitation. The varied rhythm is a byproduct of that
content, not something added on top.

## Before returning output

Do not perform a mechanical checklist or announce that you did. Instead, reread
the draft once as a skeptical reviewer in the field and ask: is every paragraph
making a real claim with real support? Is anything overclaimed or any real
limitation buried? Does the reading of prior work commit to a position? If the
prose feels generic, the fix is upstream in the argument, not in the word
choice. Repair the substance, then hand it over without commentary about your
process.
