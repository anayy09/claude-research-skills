#!/usr/bin/env python3
"""Deterministic scoring for submission-reviewer.

Computes the weighted total out of 100 for a paper or patent submission,
applies band labels and cap rules, supports partial scoring when a dimension
cannot be assessed, and renders the score table used in the review.

Usage:
    python scripts/score.py --rubric --type paper
    python scripts/score.py --type paper --scores novelty=17 rigor=15 \
        application=11 integrity=12 readiness=14
    python scripts/score.py --type paper --scores novelty=17 rigor=na ... \
        --cap-total 55 --cap-reason "unresolved test-set leakage"
    python scripts/score.py --type paper --scores ... --projected novelty=20 rigor=20
    python scripts/score.py --type paper --scores ... --json

Standard library only. No network, no filesystem writes.
"""

import argparse
import json
import sys

RUBRICS = {
    "paper": [
        ("novelty", "Novelty and contribution", 25),
        ("rigor", "Technical rigor and validity of evidence", 25),
        ("application", "Practical application and impact", 15),
        ("integrity", "Authenticity of the contribution", 15),
        ("readiness", "Publication readiness", 20),
    ],
    "patent": [
        ("novelty", "Novelty over prior art", 25),
        ("inventive_step", "Inventive step, non-obviousness", 20),
        ("claims", "Claim quality and scope", 20),
        ("enablement", "Enablement and sufficiency of disclosure", 15),
        ("application", "Industrial applicability and commercial value", 12),
        ("eligibility", "Subject-matter eligibility and disclosure integrity", 8),
    ],
}

# (lower bound inclusive, label, outlook line)
BANDS = [
    (85, "strong", "Competitive at a selective venue as it stands."),
    (70, "solid, revise first", "Submittable to a selective or mid-tier venue after the listed fixes."),
    (55, "promising, gap to close", "One substantive gap short of a competitive submission."),
    (40, "early", "Needs new work before it is a submission: experiments, repositioning, or a rebuilt claim set."),
    (0, "not yet a submission", "Identify the salvageable core and the shortest path to a minimal publishable claim."),
]

CAPS = {
    "paper": [
        ("Unresolved leakage between train and test at the relevant unit", 55),
        ("Headline claim anticipated by prior work found in the search", 50),
        ("Required baseline for the claim is absent", 65),
        ("Human-subject data with no ethics approval or provenance stated", 60),
        ("Direct evidence of fabrication, plagiarism, or figure manipulation", 30),
        ("Core method not described in enough detail to reproduce", 60),
    ],
    "patent": [
        ("Applicant's own public disclosure predates filing under an absolute novelty bar", 45),
        ("All independent claims anticipated by a single found reference", 50),
        ("Claims do not correspond to the disclosed invention", 50),
        ("Specification does not enable the claimed scope", 60),
        ("Inventorship or ownership materially unclear", 60),
    ],
}


def parse_scores(pairs, rubric, allow_partial=True):
    """Parse key=value pairs into {key: int or None}. None means not assessable."""
    dims = {k: m for k, _, m in rubric}
    out = {}
    for pair in pairs:
        if "=" not in pair:
            sys.exit(f"error: expected key=value, got '{pair}'")
        key, raw = pair.split("=", 1)
        key, raw = key.strip(), raw.strip().lower()
        if key not in dims:
            sys.exit(f"error: unknown dimension '{key}'. Valid: {', '.join(dims)}")
        if raw in ("na", "n/a", "none", "-"):
            if not allow_partial:
                sys.exit(f"error: '{key}=na' is not allowed here")
            out[key] = None
            continue
        try:
            value = int(round(float(raw)))
        except ValueError:
            sys.exit(f"error: '{raw}' is not a number for dimension '{key}'")
        if not 0 <= value <= dims[key]:
            sys.exit(f"error: {key}={value} is outside 0..{dims[key]}")
        out[key] = value
    return out


def compute(scores, rubric):
    """Return raw total, assessed max, normalized total out of 100, partial flag."""
    assessed = [(k, m) for k, _, m in rubric if scores.get(k) is not None]
    missing = [k for k, _, _ in rubric if k not in scores]
    if missing:
        sys.exit(f"error: missing scores for: {', '.join(missing)} (use 'key=na' if not assessable)")
    raw = sum(scores[k] for k, _ in assessed)
    assessed_max = sum(m for _, m in assessed)
    if assessed_max == 0:
        sys.exit("error: no dimension could be assessed")
    partial = assessed_max != sum(m for _, _, m in rubric)
    total = round(raw / assessed_max * 100)
    return raw, assessed_max, total, partial


def band_for(total):
    for lower, label, outlook in BANDS:
        if total >= lower:
            return label, outlook
    return BANDS[-1][1], BANDS[-1][2]


def render_table(scores, rubric):
    width = max(len(name) for _, name, _ in rubric)
    lines = ["| Dimension | Score |", "|---|---|"]
    for key, name, maximum in rubric:
        value = scores[key]
        cell = "not assessed" if value is None else f"{value}/{maximum}"
        lines.append(f"| {name.ljust(width)} | {cell} |")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="Score a paper or patent submission.")
    p.add_argument("--type", choices=sorted(RUBRICS), default="paper",
                   help="rubric to use (default: paper)")
    p.add_argument("--scores", nargs="*", default=[], metavar="KEY=VALUE",
                   help="per-dimension raw scores; use KEY=na when not assessable")
    p.add_argument("--projected", nargs="*", default=[], metavar="KEY=VALUE",
                   help="revised scores after the priority fixes land")
    p.add_argument("--cap-total", type=int, default=None,
                   help="cap the reported total (see rubric cap rules)")
    p.add_argument("--cap-reason", default=None,
                   help="required with --cap-total: why the score cannot be read as final")
    p.add_argument("--rubric", action="store_true",
                   help="print the dimensions, weights, bands, and cap rules, then exit")
    p.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    args = p.parse_args()

    rubric = RUBRICS[args.type]

    if args.rubric:
        print(f"# {args.type} rubric\n")
        for key, name, maximum in rubric:
            print(f"  {key:<16} {name:<52} {maximum:>3}")
        print(f"  {'':<16} {'TOTAL':<52} {sum(m for _, _, m in rubric):>3}\n")
        print("Bands:")
        for lower, label, _ in BANDS:
            print(f"  >= {lower:<3} {label}")
        print("\nCap rules:")
        for reason, cap in CAPS[args.type]:
            print(f"  {cap:>3}  {reason}")
        return

    if not args.scores:
        p.error("--scores is required unless --rubric is given")
    if args.cap_total is not None and not args.cap_reason:
        p.error("--cap-reason is required with --cap-total")

    scores = parse_scores(args.scores, rubric)
    raw, assessed_max, total, partial = compute(scores, rubric)

    capped = False
    if args.cap_total is not None and total > args.cap_total:
        uncapped, total, capped = total, args.cap_total, True
    else:
        uncapped = total

    label, outlook = band_for(total)

    projected = None
    if args.projected:
        merged = dict(scores)
        merged.update(parse_scores(args.projected, rubric, allow_partial=False))
        _, _, proj_total, _ = compute(merged, rubric)
        proj_label, proj_outlook = band_for(proj_total)
        projected = {
            "scores": merged,
            "total": proj_total,
            "band": proj_label,
            "outlook": proj_outlook,
            "delta": proj_total - total,
        }

    if args.json:
        print(json.dumps({
            "type": args.type,
            "scores": scores,
            "raw": raw,
            "assessed_max": assessed_max,
            "total": total,
            "uncapped_total": uncapped,
            "capped": capped,
            "cap_reason": args.cap_reason,
            "partial": partial,
            "band": label,
            "outlook": outlook,
            "projected": projected,
        }, indent=2))
        return

    print(render_table(scores, rubric))
    print()
    if partial:
        print(f"Partial assessment: {raw}/{assessed_max} on assessed dimensions, "
              f"normalized to {uncapped}/100. Report confidence as reduced and name "
              "the dimensions that could not be assessed.")
    if capped:
        print(f"**Total: {total}/100 ({label}), capped.** Uncapped rubric total is "
              f"{uncapped}. Cap reason: {args.cap_reason}")
    else:
        print(f"**Total: {total}/100 ({label}).**")
    print(f"Outlook: {outlook}")

    if projected:
        print()
        print(f"Projected after fixes: {projected['total']}/100 ({projected['band']}), "
              f"{projected['delta']:+d} points.")
        for key, name, maximum in rubric:
            before, after = scores[key], projected["scores"][key]
            if before != after:
                shown = "not assessed" if before is None else before
                print(f"  {name}: {shown} -> {after}/{maximum}")
        print("State what each uplift depends on so the projection reads as a plan.")


if __name__ == "__main__":
    main()
