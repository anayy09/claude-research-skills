# Novelty check

Novelty is the dimension most often scored from memory, and memory is the wrong
instrument: a model's sense of what exists lags the literature by months to
years, and the papers that anticipate a direction are usually the ones that were
never famous enough to be memorable. Search, record, classify.

The goal is not to prove the direction is new. It is to find the work that would
sink it, early enough that finding it is cheap.

## 1. Decompose the claim into search components

Take the one-sentence central claim and split it into the parts that a competing
paper would have to share:

- **Phenomenon or task.** What is being measured or decided.
- **Method or intervention.** What is being done.
- **Population, domain, or regime.** Where it applies.
- **Outcome and unit.** What is reported, at what granularity.

A paper only anticipates the direction if it matches on phenomenon, method, and
regime. Matching on task alone is a related work, not an anticipation. Most
false alarms come from searching the topic instead of the claim.

## 2. Search in this order

1. **The obvious query.** The claim in plain words, in a general web search.
   This catches preprints, blog posts, and industry reports that indexed
   databases miss.
2. **Scholarly databases.** Google Scholar for coverage, arXiv for recency,
   dblp and OpenReview for machine learning venues, PubMed for clinical and
   biomedical work. Semantic Scholar when citation graph traversal helps.
3. **Forward and backward from the closest hit.** The single most productive
   move once one close paper is found: read its related work and its citing
   papers. Anticipating work clusters.
4. **The negative query.** Search for the direction's own conclusion as if it
   were already known, for example "X does not improve Y". Papers reporting the
   result you expect to find often use vocabulary the positive query misses.
5. **Venue-targeted.** Recent proceedings of the two or three venues where this
   work would go. Scooping usually happens at the venue you are aiming for.
6. **Patents** when there is a filing or commercialization angle. Also worth one
   query when the direction has an obvious product form, because a filing can
   constrain what is publishable and when.

Stop when two consecutive searches return only work already seen. If a direction
survives that, the search was adequate for an ideation pass, though not for a
related work section.

## 3. Record the closest work

For each surviving direction, log the two or three closest works:

| Field | Content |
|---|---|
| Citation | Authors, title, venue, year, identifier |
| Overlap | One sentence: exactly what it shares with the direction |
| Difference | One sentence: exactly what the direction adds |
| Threat | `anticipates`, `constrains`, `supports`, or `context` |

`anticipates` means the direction as stated is already done. `constrains` means
part of it is done and the claim has to narrow. `supports` means the prior work
establishes a premise the direction needs, which is good news. `context` means
it is related work and nothing more.

A direction with no logged closest work has an unverified novelty score. Say so
in the report and cap the score per `scoring-rubric.md`.

## 4. Classify the delta

Say which kind of contribution the direction makes. Reviewers evaluate different
kinds against different bars, and stating the kind explicitly prevents a paper
being judged as a method paper when it is an analysis paper.

| Delta type | The contribution is | Bar it is judged against |
|---|---|---|
| New phenomenon | An effect nobody has reported | Reproducibility and ruling out artifacts |
| New mechanism | An explanation for a known effect | Causal separation from rival explanations |
| New method | A way to do something better | Fair, tuned baselines and ablations |
| New regime | A known method under a constraint nobody enforced | Realism of the constraint |
| New evaluation | A protocol, metric, or measurement instrument | Adoption cost and demonstrated failure of the old one |
| New resource | Data, annotations, or a benchmark | Provenance, agreement, and the question it unblocks |
| New consolidation | A synthesis producing a conclusion no single paper supports | Search reproducibility and the original element |
| New negative | A well-powered failure of an assumed effect | Implementation fidelity and statistical adequacy |

If a direction fits no row, it is probably not a contribution yet. If it fits
three, it is probably two papers.

## 5. When the direction is already taken

Do not drop it silently, and do not water it down until the overlap is
technically deniable. Apply one of four recovery moves, or report the exclusion:

- **Extend.** The prior work established the effect; the direction now tests
  where it breaks, at what scale, or under which constraint. Cite it as the
  premise. This is the most common successful recovery.
- **Contradict.** Attempt the reproduction, and if it fails, the failure is the
  paper. Only viable if the assets can execute the original setup faithfully.
- **Generalize.** The prior work covered one instance; the direction shows the
  effect is an instance of something broader, with a second and third instance
  as evidence.
- **Deepen.** The prior work reported the effect; the direction explains it.
  Operator A2, and usually the strongest of the four when it is available.

If none of the four applies, report the direction as excluded, name the paper
that excludes it, and move on. Knowing which idea is dead is worth as much as
knowing which is alive, and it is the cheapest possible outcome of an hour of
searching.

## 6. Self-overlap check

Search the user's own prior papers and preprints for the same claim. Two of
their papers sharing a central claim is a salami-slicing problem regardless of
how different the experiments look, and journals increasingly check.

Test: could the two papers' central claims appear as two bullets in the same
contributions list without one being redundant? If not, they are one paper.

Also check whether the new direction requires content the user has already
published. Reuse of methods text is normal and must be cited. Reuse of results
across papers is not, unless explicitly labeled as a secondary analysis of the
same data.

## 7. Reporting the result

State what was searched, not just what was found:

> Searched Scholar, arXiv, and PubMed for the claim components (selective
> deferral, histopathology, vision-language model), plus the 2025 and 2026
> proceedings of the two target venues. Closest work: Author et al., venue,
> year, which reports the effect at slide level without patient-level
> aggregation. Threat: constrains. The direction narrows to the patient-level
> claim.

An unverified novelty claim is worth less than a verified narrow one. If no
search tool is available, say so once, score novelty on the strength of the
user's own related-work knowledge only, and mark confidence low. Never fill the
gap with a plausible-sounding citation. A fabricated closest work is worse than
no search, because it produces confident wrong strategy.
