#!/usr/bin/env python3
"""Shortlist candidate journals from the bundled publisher lists.

This narrows roughly 1,850 permitted titles to a reviewable set. It does not
decide fit. The catalog's text is thin (mostly titles and subject labels), so
lexical scoring is a first pass; judging topical fit still requires reading the
manuscript against the journal's actual aims and scope.

    # shortlist across all publishers
    python find_journals.py --query "histopathology deep learning colorectal triage" -n 20

    # per-publisher shortlist, the shape the final report needs
    python find_journals.py --query "..." --per-publisher 6

    # restrict by quartile and indexing
    python find_journals.py --query "..." --max-quartile Q2 --require-quartile

    # is a specific journal inside the permitted set?
    python find_journals.py --check "Computers in Biology and Medicine"

    # what subject vocabulary exists
    python find_journals.py --list-subjects --publisher "Taylor & Francis"

Exit status is 0 even when nothing matches; an empty result is a finding, not an
error, and usually means the topic is not covered by the permitted lists.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

CATALOG = Path(__file__).resolve().parent.parent / "assets" / "journals.csv"

STOP = {
    "a", "an", "the", "of", "and", "or", "for", "in", "on", "to", "with", "from",
    "by", "at", "as", "is", "are", "we", "our", "this", "that", "these", "using",
    "used", "use", "based", "novel", "new", "study", "paper", "approach", "method",
    "methods", "results", "via", "into", "its", "it", "be", "can", "which", "than",
    "journal", "transactions", "international", "letters", "review", "reviews",
}

# Field weights. Title terms are the strongest signal because the catalog's
# titles are descriptive; subject labels come next; scope text exists for only a
# minority of rows and is treated as a bonus rather than a requirement.
WEIGHTS = {"journal_title": 3.0, "subject_area": 2.0, "acronym": 1.5,
           "scope": 1.0, "imprint": 0.3}

QRANK = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}


def tokens(text: str) -> List[str]:
    out = []
    for t in re.split(r"[^a-z0-9]+", text.lower()):
        if len(t) < 3 or t in STOP:
            continue
        # crude singularization; the vocabulary is small enough that a real
        # stemmer would add a dependency for very little gain
        if len(t) > 4 and t.endswith("s") and not t.endswith("ss"):
            t = t[:-1]
        out.append(t)
    return out


def load(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        sys.exit(f"catalog not found at {path}. Run scripts/build_catalog.py first.")
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_index(rows: List[Dict[str, str]]):
    docs, dfreq = [], Counter()
    for r in rows:
        fields = {k: tokens(r.get(k, "")) for k in WEIGHTS}
        docs.append(fields)
        for t in {t for toks in fields.values() for t in toks}:
            dfreq[t] += 1
    N = len(rows)
    idf = {t: math.log((N + 1) / (c + 0.5)) for t, c in dfreq.items()}
    return docs, idf


def score(qtoks: List[str], qbigrams: set, fields: Dict[str, List[str]],
          idf: Dict[str, float]) -> float:
    s = 0.0
    qset = set(qtoks)
    for fname, w in WEIGHTS.items():
        ftoks = fields[fname]
        if not ftoks:
            continue
        hit = qset & set(ftoks)
        if hit:
            # length normalization keeps a long scope paragraph from
            # outscoring a precisely-named journal title
            s += w * sum(idf.get(t, 1.0) for t in hit) / math.sqrt(len(ftoks))
        fbg = {f"{a} {b}" for a, b in zip(ftoks, ftoks[1:])}
        s += 0.8 * w * len(qbigrams & fbg)
    return s


def passes(r: Dict[str, str], a: argparse.Namespace) -> bool:
    if a.publisher and r["publisher"].lower() not in {p.strip().lower()
                                                      for p in a.publisher.split(",")}:
        return False
    if a.subject and a.subject.lower() not in r["subject_area"].lower():
        return False
    if a.oa and a.oa.lower() not in r["oa_model"].lower():
        return False
    bq = r["best_quartile"]
    if a.require_quartile and not bq:
        return False
    if a.max_quartile and bq and QRANK[bq] > QRANK[a.max_quartile.upper()]:
        return False
    if a.indexed_only and not (r["index_wos"] or r["scopus_covered"].lower() == "yes"):
        return False
    return True


def fmt_row(r: Dict[str, str], sc: float) -> str:
    bq = r["best_quartile"] or "--"
    basis = "" if r["best_quartile"] else "*"
    idx = r["index_wos"] or ("Scopus" if r["scopus_covered"].lower() == "yes" else "")
    return (f"{sc:6.2f}  {r['publisher']:<17} {bq:<3}{basis:<1} "
            f"{idx:<7} {r['oa_model'][:20]:<20} {r['journal_title'][:62]}")


def cmd_check(rows: List[Dict[str, str]], name: str) -> int:
    target = name.lower().strip()
    exact = [r for r in rows if r["journal_title"].lower().strip() == target]
    if exact:
        for r in exact:
            print(f"IN LIST: {r['journal_title']} ({r['publisher']})")
            print(f"  quartile   : {r['best_quartile'] or 'not stated'} "
                  f"[{r['quartile_basis']}]")
            print(f"  OA model   : {r['oa_model'] or 'not stated'}")
            print(f"  indexing   : WoS={r['index_wos'] or 'not stated'}, "
                  f"Scopus={r['scopus_covered'] or 'not stated'}")
            print(f"  source     : {r['source_file']} / {r['source_sheet']} "
                  f"row {r['source_row']}")
        return 0

    titles = [r["journal_title"] for r in rows]
    near = difflib.get_close_matches(name, titles, n=6, cutoff=0.6)
    print(f"NOT IN LIST: '{name}' does not appear in any of the five permitted lists.")
    print("Do not recommend it. Absence here means the title is outside the "
          "permitted set, not that it does not exist.")
    if near:
        print("\nSimilar titles that ARE in the lists:")
        for t in near:
            r = next(x for x in rows if x["journal_title"] == t)
            print(f"  - {t} ({r['publisher']})")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--catalog", default=str(CATALOG))
    p.add_argument("--query", default="", help="title, keywords, abstract terms")
    p.add_argument("--check", default="", help="verify one journal is in the lists")
    p.add_argument("--list-subjects", action="store_true")
    p.add_argument("--publisher", default="", help="comma separated filter")
    p.add_argument("--subject", default="", help="substring match on subject area")
    p.add_argument("--oa", default="", help="substring match on OA model")
    p.add_argument("--max-quartile", default="", choices=["", "Q1", "Q2", "Q3", "Q4"])
    p.add_argument("--require-quartile", action="store_true",
                   help="drop titles with no quartile in the source list")
    p.add_argument("--indexed-only", action="store_true",
                   help="keep only titles with stated WoS or Scopus coverage")
    p.add_argument("-n", "--top", type=int, default=25)
    p.add_argument("--per-publisher", type=int, default=0,
                   help="return this many per publisher instead of a global top-n")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    rows = load(Path(a.catalog))

    if a.check:
        return cmd_check(rows, a.check)

    if a.list_subjects:
        subs = Counter(r["subject_area"] for r in rows
                       if r["subject_area"] and passes(r, a))
        for s, c in subs.most_common():
            print(f"{c:>4}  {s}")
        if not subs:
            print("no subject labels for this filter "
                  "(ACM and Elsevier lists carry none)")
        return 0

    if not a.query:
        sys.exit("give --query, --check, or --list-subjects")

    docs, idf = build_index(rows)
    qt = tokens(a.query)
    if not qt:
        sys.exit("query reduced to zero usable terms after stopword removal")
    qbg = {f"{x} {y}" for x, y in zip(qt, qt[1:])}

    scored = []
    for r, fields in zip(rows, docs):
        if not passes(r, a):
            continue
        s = score(qt, qbg, fields, idf)
        if s > 0:
            scored.append((s, r))
    scored.sort(key=lambda t: (-t[0], t[1]["journal_title"]))

    if a.per_publisher:
        seen: Counter = Counter()
        out = []
        for s, r in scored:
            if seen[r["publisher"]] < a.per_publisher:
                seen[r["publisher"]] += 1
                out.append((s, r))
    else:
        out = scored[: a.top]

    if a.json:
        print(json.dumps([{**r, "match_score": round(s, 3)} for s, r in out], indent=2))
        return 0

    if not out:
        print("No titles matched. Either the topic is outside the permitted lists "
              "or the query terms are too specific. Try broader terms, or "
              "--list-subjects to see the available vocabulary.")
        return 0

    print(f"{len(out)} candidates from {len(scored)} matches "
          f"across {len(rows)} permitted titles\n")
    print(f"{'score':>6}  {'publisher':<17} {'Q':<4} {'index':<7} "
          f"{'OA model':<20} title")
    print("-" * 118)
    for s, r in out:
        print(fmt_row(r, s))
    print("\n*  no quartile in the source list for this publisher; do not infer one.")
    print("Lexical shortlist only. Confirm scope, article type, review speed, and "
          "APC on each journal's own page before recommending it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
