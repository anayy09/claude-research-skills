#!/usr/bin/env python3
"""Deterministic ranking for research-ideation.

Computes weighted composites for candidate research directions, applies bands
and cap rules, supports partial scoring when a dimension cannot be assessed,
detects dominated directions, measures asset overlap between directions, and
selects a portfolio (lead, fast, high-ceiling).

Usage:
    python scripts/rank_ideas.py --rubric
    python scripts/rank_ideas.py --ideas ideas.json
    python scripts/rank_ideas.py --ideas ideas.json --available-months 4
    python scripts/rank_ideas.py --ideas ideas.json --json

Schema for ideas.json is documented in references/scoring-rubric.md and printed
by --rubric.

Standard library only. No network, no filesystem writes.
"""

import argparse
import json
import sys

# (key, label, max points)
DIMENSIONS = [
    ("novelty", "Verified delta over closest found work", 25),
    ("significance", "Who changes what they do if the claim holds", 20),
    ("feasibility", "Executable with the assets, compute, and time available", 20),
    ("readiness", "Share of required evidence that already exists", 15),
    ("venue_fit", "Match to the target venue's scope and evidence bar", 10),
    ("durability", "Still worth citing in two years", 10),
]

# (lower bound inclusive, label, meaning)
BANDS = [
    (80, "lead candidate",
     "Real delta, evidence largely in hand, finishable in the stated window."),
    (65, "strong contender",
     "Genuine contribution with one open dependency, usually an experiment or a data access."),
    (50, "viable, gap to close",
     "Publishable somewhere as it stands; needs a sharper claim or a stronger comparison."),
    (35, "needs reframing",
     "The asset is interesting, the claim is not yet a paper. Apply a different operator."),
    (0, "not a paper yet",
     "Say so plainly, and say what would change that."),
]

CAP_RULES = [
    ("Central claim anticipated by found prior work, no recovery move applied", 35),
    ("Required data cannot be obtained within the timeline", 40),
    ("No ground truth or evaluation exists that could test the claim", 40),
    ("Would violate a data use agreement, license, or IRB scope", 30),
    ("Overlaps a claim in the user's own prior or in-review paper", 45),
    ("Claim is not falsifiable as stated", 45),
    ("Compute required exceeds the available allocation by more than 3x", 50),
    ("Direction depends on an unrecorded or unreproducible prior run", 55),
]

SCHEMA_HELP = """\
ideas.json schema

{
  "context": "short label",
  "target_venue": "optional free text",
  "available_months": 4,
  "ideas": [
    {
      "id": "D1",
      "title": "the claim in plain words",
      "operators": ["A1", "A2"],
      "scores": {"novelty": 21, "significance": 16, "feasibility": 15,
                 "readiness": 12, "venue_fit": 8, "durability": 8},
      "effort_months": 2.5,
      "p_complete": 0.8,
      "assets": ["asset-id", "asset-id"],
      "cap": {"total": 45, "reason": "why"}
    }
  ]
}

Notes
  scores        any dimension may be "na"; remaining dimensions are reweighted
  effort_months real working months including writing
  p_complete    optional; derived from feasibility when omitted
  assets        ids from the asset inventory, used for overlap analysis
  cap           optional; caps the composite and prints the reason
"""


def band_for(score):
    for lower, label, meaning in BANDS:
        if score >= lower:
            return label, meaning
    return BANDS[-1][1], BANDS[-1][2]


def parse_scores(raw, idea_id):
    """Return {key: int or None}. None means the dimension is not assessable."""
    if not isinstance(raw, dict):
        sys.exit("error: idea %s has no 'scores' object" % idea_id)
    out = {}
    for key, _, maximum in DIMENSIONS:
        if key not in raw:
            sys.exit("error: idea %s is missing dimension '%s'" % (idea_id, key))
        value = raw[key]
        if isinstance(value, str) and value.strip().lower() == "na":
            out[key] = None
            continue
        try:
            value = int(value)
        except (TypeError, ValueError):
            sys.exit("error: idea %s dimension '%s' is not an integer or 'na'"
                     % (idea_id, key))
        if not 0 <= value <= maximum:
            sys.exit("error: idea %s dimension '%s' = %d is outside 0..%d"
                     % (idea_id, key, value, maximum))
        out[key] = value
    if all(v is None for v in out.values()):
        sys.exit("error: idea %s has no assessable dimension" % idea_id)
    return out


def composite(scores):
    """Weighted total out of 100, reweighting over the assessed dimensions."""
    assessed = [(k, m) for k, _, m in DIMENSIONS if scores[k] is not None]
    earned = sum(scores[k] for k, _ in assessed)
    available = sum(m for _, m in assessed)
    return round(earned * 100.0 / available, 1), available


def derive_p_complete(scores):
    """Default completion probability from the feasibility score.

    Feasibility is the only dimension that speaks to whether a started
    direction reaches submission. Mapped into 0.35..0.95 so that a low
    feasibility score never zeroes a direction out and a high one never
    promises certainty.
    """
    f = scores.get("feasibility")
    if f is None:
        return 0.6
    return round(0.35 + 0.60 * (f / 20.0), 2)


def evaluate(idea):
    idea_id = idea.get("id") or idea.get("title") or "<unnamed>"
    scores = parse_scores(idea.get("scores"), idea_id)
    raw_total, available = composite(scores)

    cap = idea.get("cap") or {}
    cap_total = cap.get("total")
    capped = cap_total is not None and raw_total > cap_total
    total = float(cap_total) if capped else raw_total

    effort = idea.get("effort_months")
    if effort is None:
        sys.exit("error: idea %s is missing 'effort_months'" % idea_id)
    try:
        effort = float(effort)
    except (TypeError, ValueError):
        sys.exit("error: idea %s has a non-numeric 'effort_months'" % idea_id)
    if effort <= 0:
        sys.exit("error: idea %s has effort_months <= 0" % idea_id)

    p = idea.get("p_complete")
    p = derive_p_complete(scores) if p is None else float(p)
    if not 0 < p <= 1:
        sys.exit("error: idea %s has p_complete outside (0, 1]" % idea_id)

    label, meaning = band_for(total)
    risk_adjusted = round(total * p, 1)

    return {
        "id": idea_id,
        "title": idea.get("title", ""),
        "operators": idea.get("operators", []),
        "assets": sorted(set(idea.get("assets", []))),
        "scores": scores,
        "raw_total": raw_total,
        "total": round(total, 1),
        "capped": capped,
        "cap_total": cap_total,
        "cap_reason": cap.get("reason", ""),
        "partial": [k for k, _, _ in DIMENSIONS if scores[k] is None],
        "weight_assessed": available,
        "effort_months": effort,
        "p_complete": p,
        "risk_adjusted": risk_adjusted,
        "throughput": round(risk_adjusted / effort, 1),
        "band": label,
        "band_meaning": meaning,
    }


def find_dominated(results):
    """A dominates B when A is at least as good on every assessed dimension,
    costs no more, and is strictly better somewhere. Dominated directions are
    not worth arguing about; drop them or change their scope."""
    dominated = {}
    for b in results:
        for a in results:
            if a["id"] == b["id"]:
                continue
            keys = [k for k, _, _ in DIMENSIONS
                    if a["scores"][k] is not None and b["scores"][k] is not None]
            if not keys:
                continue
            if all(a["scores"][k] >= b["scores"][k] for k in keys) and \
               a["effort_months"] <= b["effort_months"] and \
               (any(a["scores"][k] > b["scores"][k] for k in keys) or
                    a["effort_months"] < b["effort_months"]):
                dominated[b["id"]] = a["id"]
                break
    return dominated


def jaccard(a, b):
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return round(len(sa & sb) / float(len(sa | sb)), 2)


def pick_portfolio(results):
    """Lead, fast, and high-ceiling picks. Distinct where possible."""
    if not results:
        return {}
    ranked = sorted(results, key=lambda r: -r["risk_adjusted"])
    lead = ranked[0]

    viable = [r for r in results if r["total"] >= 50 and r["id"] != lead["id"]]
    fast = min(viable, key=lambda r: (r["effort_months"], -r["total"])) if viable else None

    def ceiling(r):
        n = r["scores"]["novelty"] or 0
        s = r["scores"]["significance"] or 0
        return n + s

    others = [r for r in results
              if r["id"] not in {lead["id"], fast["id"] if fast else None}]
    moonshot = max(others, key=ceiling) if others else None

    picks = {"lead": lead["id"]}
    if fast:
        picks["fast"] = fast["id"]
    if moonshot:
        picks["high_ceiling"] = moonshot["id"]
    return picks


def print_rubric():
    print("Dimensions (weighted total = 100)\n")
    width = max(len(k) for k, _, _ in DIMENSIONS)
    for key, label, maximum in DIMENSIONS:
        print("  %-*s  %2d   %s" % (width, key, maximum, label))
    print("\nBands\n")
    for lower, label, meaning in BANDS:
        print("  >= %3d  %-20s %s" % (lower, label, meaning))
    print("\nCap rules (pass as \"cap\": {\"total\": N, \"reason\": \"...\"})\n")
    for reason, cap in CAP_RULES:
        print("  %3d  %s" % (cap, reason))
    print()
    print(SCHEMA_HELP)


def print_report(data, results, dominated, picks, available_months):
    context = data.get("context", "")
    venue = data.get("target_venue", "")
    header = "Ranked directions"
    if context:
        header += ": %s" % context
    print(header)
    if venue:
        print("Target venue: %s" % venue)
    if available_months:
        print("Available time: %.1f months" % available_months)
    print()

    ranked = sorted(results, key=lambda r: (-r["risk_adjusted"], r["effort_months"]))

    cols = "%-5s %-34s %4s %4s %4s %4s %4s %4s %7s %6s %6s %7s"
    print(cols % ("id", "title", "nov", "sig", "fea", "rdy", "ven", "dur",
                  "total", "risk", "mo", "per-mo"))
    print("-" * 108)
    for r in ranked:
        s = r["scores"]

        def cell(key):
            return "na" if s[key] is None else str(s[key])

        print(cols % (
            r["id"], r["title"][:34],
            cell("novelty"), cell("significance"), cell("feasibility"),
            cell("readiness"), cell("venue_fit"), cell("durability"),
            "%.1f%s" % (r["total"], "*" if r["capped"] else ""),
            "%.1f" % r["risk_adjusted"],
            "%.1f" % r["effort_months"],
            "%.1f" % r["throughput"],
        ))
    print("-" * 108)
    print("risk = total x p_complete; per-mo = risk / effort_months; * = capped")
    print()

    print("Bands")
    for r in ranked:
        print("  %-5s %-24s %s" % (r["id"], r["band"], r["title"][:50]))
    print()

    flagged = [r for r in ranked if r["capped"] or r["partial"] or
               (available_months and r["effort_months"] > available_months)]
    if flagged:
        print("Flags")
        for r in flagged:
            if r["capped"]:
                print("  %-5s capped at %s (rubric total %.1f): %s"
                      % (r["id"], r["cap_total"], r["raw_total"], r["cap_reason"]))
            if r["partial"]:
                print("  %-5s scored on %d of 100 points of rubric weight; "
                      "not assessed: %s"
                      % (r["id"], r["weight_assessed"], ", ".join(r["partial"])))
            if available_months and r["effort_months"] > available_months:
                print("  %-5s effort %.1f months exceeds the %.1f available"
                      % (r["id"], r["effort_months"], available_months))
        print()

    if dominated:
        print("Dominated")
        for loser, winner in sorted(dominated.items()):
            print("  %-5s is dominated by %s (no better on any dimension, "
                  "costs no less)" % (loser, winner))
        print()

    pairs = []
    for i, a in enumerate(ranked):
        for b in ranked[i + 1:]:
            j = jaccard(a["assets"], b["assets"])
            if j > 0:
                pairs.append((j, a["id"], b["id"], sorted(set(a["assets"]) & set(b["assets"]))))
    if pairs:
        print("Shared assets (one experiment cycle may serve both)")
        for j, x, y, shared in sorted(pairs, reverse=True):
            print("  %.2f  %s + %s: %s" % (j, x, y, ", ".join(shared)))
        print()

    if picks:
        print("Portfolio")
        labels = {"lead": "lead (highest risk-adjusted)",
                  "fast": "fast (lowest effort among viable)",
                  "high_ceiling": "high ceiling (novelty + significance)"}
        width = max(len(v) for v in labels.values())
        for key in ("lead", "fast", "high_ceiling"):
            if key in picks:
                pid = picks[key]
                title = next(r["title"] for r in results if r["id"] == pid)
                print("  %-*s %-5s %s" % (width, labels[key], pid, title[:48]))
        print()


def main():
    ap = argparse.ArgumentParser(description="Rank candidate research directions.")
    ap.add_argument("--ideas", help="path to ideas.json")
    ap.add_argument("--rubric", action="store_true",
                    help="print dimensions, bands, cap rules, and the schema")
    ap.add_argument("--available-months", type=float, default=None,
                    help="flag directions whose effort exceeds this")
    ap.add_argument("--json", action="store_true", dest="as_json",
                    help="machine-readable output")
    args = ap.parse_args()

    if args.rubric:
        print_rubric()
        return

    if not args.ideas:
        ap.error("provide --ideas <file> or --rubric")

    try:
        with open(args.ideas) as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        sys.exit("error: could not read %s: %s" % (args.ideas, exc))

    ideas = data.get("ideas")
    if not ideas:
        sys.exit("error: no 'ideas' array in %s" % args.ideas)

    seen = set()
    for idea in ideas:
        iid = idea.get("id")
        if iid in seen:
            sys.exit("error: duplicate idea id '%s'" % iid)
        seen.add(iid)

    results = [evaluate(i) for i in ideas]
    dominated = find_dominated(results)
    picks = pick_portfolio(results)
    available = args.available_months or data.get("available_months")

    if args.as_json:
        print(json.dumps({
            "context": data.get("context", ""),
            "target_venue": data.get("target_venue", ""),
            "available_months": available,
            "results": sorted(results, key=lambda r: -r["risk_adjusted"]),
            "dominated": dominated,
            "portfolio": picks,
        }, indent=2))
        return

    print_report(data, results, dominated, picks, available)


if __name__ == "__main__":
    main()
