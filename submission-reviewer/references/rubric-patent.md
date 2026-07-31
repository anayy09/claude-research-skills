# Patent rubric

Six dimensions, 100 points. This is a technical appraisal of a disclosure and
its claims. It is not a legal opinion, and the review says so once in the data
notes line. Filing strategy, claim drafting for prosecution, and
freedom-to-operate opinions belong with a registered patent attorney or agent.

| Key | Dimension | Max |
|---|---|---|
| `novelty` | Novelty over prior art | 25 |
| `inventive_step` | Inventive step, non-obviousness | 20 |
| `claims` | Claim quality and scope | 20 |
| `enablement` | Enablement and sufficiency of disclosure | 15 |
| `application` | Industrial applicability and commercial value | 12 |
| `eligibility` | Subject-matter eligibility and disclosure integrity | 8 |

---

## Read the claims first

Everything is scored against the independent claims, not the abstract or the
summary. Before scoring:

1. List each independent claim and its type: apparatus, method, system,
   composition, computer-readable medium.
2. Break the broadest independent claim into its elements, one per line. This
   element list is what prior art is compared against.
3. Note which elements are the point of novelty, according to the applicant.
4. Note the dependent claims that add a fallback position if the broadest claim
   falls. A claim set with no meaningful fallbacks is fragile even when the
   invention is strong.

A claim is anticipated only if a single prior reference discloses every element.
Obviousness is different: a combination of references, with a reason a skilled
person would have combined them. Keep the two separate in the review; conflating
them is the most common error in informal patent review.

---

## 1. Novelty over prior art (25)

Search patent literature (Google Patents, Espacenet, USPTO full text, WIPO
Patentscope) and non-patent literature. Academic papers, preprints, product
documentation, and the applicant's own prior publications are all prior art.

| Points | Level |
|---|---|
| 22 to 25 | No reference found disclosing all elements of any independent claim. The distinguishing elements are concrete and structural, not phrased as intended results. |
| 17 to 21 | Close art exists but each independent claim has at least one element not disclosed by any single reference. |
| 12 to 16 | The broadest claim is anticipated or nearly so, but narrower independent or dependent claims survive. Amendable. |
| 6 to 11 | All independent claims are anticipated by references found; only routine variations remain. |
| 0 to 5 | Anticipated by a reference the applicant should have known, including the applicant's own prior publication or a disclosure that may have started a grace period or barred filing. |

**Always check for the applicant's own prior disclosure.** A conference paper,
preprint, thesis, demo, or public repository published before the filing date is
prior art in most jurisdictions and is an absolute bar in many of them. Flag any
date risk immediately, in the snapshot, with the specific date and artifact. This
is time-critical in a way that no other finding in this rubric is.

---

## 2. Inventive step, non-obviousness (20)

| Points | Level |
|---|---|
| 18 to 20 | Solves a problem others in the field tried and failed to solve, or achieves an unexpected technical effect that the specification demonstrates with data. Secondary indicia present, for example long-felt need or commercial success. |
| 14 to 17 | Combination is not suggested by the art, and the specification explains the technical effect that follows from it. |
| 9 to 13 | A skilled person could plausibly reach it by combining two known references, but the specification argues a non-trivial reason it was not obvious to do so. |
| 4 to 8 | Straightforward combination of known elements with a predictable result. Design choice, routine optimization, or automating a known manual process. |
| 0 to 3 | Explicitly suggested by a reference found in the search. |

Look for the technical effect. An invention whose only advantage is convenience
or a business outcome usually scores low here and in eligibility. The strongest
argument is a measured effect the art would not have predicted, with the data in
the specification rather than added later.

---

## 3. Claim quality and scope (20)

| Points | Level |
|---|---|
| 17 to 20 | Independent claims broad enough to cover commercial variants, narrow enough to be supported by the disclosure. Clean antecedent basis, one inventive concept per independent claim, useful fallback dependents in graded steps, multiple statutory categories covered where appropriate. |
| 13 to 16 | Sound claims with fixable defects: a missing intermediate dependent, an unnecessary limitation in the independent claim, or one ambiguous term. |
| 9 to 12 | Scope problems that matter: the independent claim reads on the preferred embodiment only, so a competitor avoids it with a trivial change, or it is so broad that the disclosure does not support it. |
| 4 to 8 | Structural defects: indefinite terms without a definition in the specification, no antecedent basis, mixed statutory categories in one claim, a claimed result rather than a means, or dependents that do not narrow. |
| 0 to 3 | No claims, or claims that do not correspond to the described invention. |

**Specific things to check.**

- Every term in an independent claim has antecedent basis and, if relative
  ("substantially", "about", "high"), a definition or a numeric range in the
  specification.
- The independent claim does not import limitations that only the preferred
  embodiment needs. Each imported limitation is a design-around invitation.
- Numeric ranges claimed are supported by working examples across the range.
- Dependents step down in graded fashion so prosecution has room to retreat.
- Method and apparatus claims both present where the invention supports both.

---

## 4. Enablement and sufficiency of disclosure (15)

| Points | Level |
|---|---|
| 13 to 15 | A skilled person could build it without undue experimentation. Working examples, parameters and ranges, drawings matching the claim elements, and failure modes discussed. Best mode described. |
| 10 to 12 | Enabled for the main embodiment, thin at the edges of the claimed range. |
| 6 to 9 | Key implementation detail missing: a parameter given as "suitable", an algorithm described only by its output, or a training procedure without data or objective. |
| 3 to 5 | Aspirational disclosure. The claim covers substantially more than the specification teaches. |
| 0 to 2 | Not reproducible from the specification. |

For software and machine-learning inventions, enablement usually turns on
whether the specification describes the data, the architecture, the training
objective, and the inference procedure specifically enough that the described
effect can be reproduced. Naming a model family is not enablement.

---

## 5. Industrial applicability and commercial value (12)

| Points | Level |
|---|---|
| 10 to 12 | Concrete industrial use, an identified market and buyer, a manufacturing or deployment path, and an advantage the buyer would pay for. Detectable infringement, meaning a competitor's use could be observed from the product. |
| 7 to 9 | Clear utility, market plausible but not sized. Deployment path has known obstacles, for example regulatory clearance, stated with the timeline. |
| 4 to 6 | Utility stated in general terms. No identified buyer, or the advantage is marginal against existing solutions. |
| 1 to 3 | Utility is speculative, or the value depends on components that do not yet exist. |
| 0 | No industrial application. |

Note detectability explicitly. A process claim that can only be practiced behind
a competitor's closed doors is hard to enforce, which affects the commercial
value of the filing even when the invention is strong.

---

## 6. Subject-matter eligibility and disclosure integrity (8)

| Points | Level |
|---|---|
| 7 to 8 | Clearly eligible: a technical solution to a technical problem, tied to a specific implementation with a concrete effect. Inventorship, ownership, prior disclosures, and funding obligations all stated. |
| 5 to 6 | Eligible with an argument to make. The specification supports a technical-effect framing but does not foreground it. |
| 3 to 4 | Eligibility risk: an abstract idea, a mathematical method, a business method, or a mental process with generic computer implementation. Or a disclosure gap, for example unclear inventorship or unstated funding obligations. |
| 1 to 2 | Substantial eligibility problem in the primary target jurisdiction, and the specification does not supply the technical detail needed to fix it. |
| 0 | Excluded subject matter, or a material misstatement in the disclosure. |

Jurisdictions differ. If the target jurisdiction is stated, apply its standard
and say which. If not, note the delta between US and EPO treatment in one line
for software and diagnostic inventions rather than assuming one of them.

---

## Cap rules

| Condition | Cap |
|---|---|
| The applicant's own public disclosure predates filing, in a jurisdiction with an absolute novelty bar | 45, and flag in the snapshot |
| All independent claims anticipated by a single found reference | 50 |
| Claims do not correspond to the disclosed invention | 50 |
| Specification does not enable the claimed scope | 60 |
| Inventorship or ownership materially unclear | 60 |

One cap applies, the lowest. Report the reason and what resolves it. A prior
disclosure cap can sometimes be lifted by a grace period in some jurisdictions,
which is exactly the kind of question the review routes to an attorney rather
than answering itself.
