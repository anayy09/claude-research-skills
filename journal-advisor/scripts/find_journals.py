#!/usr/bin/env python3
"""Shortlist journals from the fee-route catalog by topic, route, and eligibility.

This narrows a dated multidisciplinary catalog to a reviewable set. It does not
decide fit. The catalog's text is thin (mostly titles and subject labels), so
lexical scoring is a first pass; judging topical fit still requires reading the
manuscript against the journal's actual aims and scope.

    # universal routes plus one institution's agreements
    python find_journals.py --query "histopathology deep learning triage" --institution UF -n 20

    # isolate one fee route
    python find_journals.py --query "materials physics" --institution UF --route institutional_oa

    # no affiliation assumed, open access only, no ancillary fees declared
    python find_journals.py --query "statistics" --institution none --open-access-only --no-other-fees

    # eligibility as it will stand at submission time
    python find_journals.py --query "robotics" --institution MUJ,JKLU --as-of 2026-10-01

    # every known route for one title or ISSN
    python find_journals.py --check "Computers in Biology and Medicine" --institution UF
    python find_journals.py --check "2632-2153" --json

    # what subject vocabulary exists under the current filters
    python find_journals.py --list-subjects --institution UF

Exit status is 0 even when nothing matches; an empty result is a finding, not an
error. A catalog miss requires live discovery, not a conclusion about quality.
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
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

CATALOG = Path(__file__).resolve().parent.parent / "assets" / "journals.csv"

ROUTES = ("institutional_oa", "no_apc_oa", "s2o", "subscription_no_apc")
INSTITUTIONS = ("UF", "MUJ", "JKLU", "NONE")

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

# The routes attached to each grouped candidate. Fee terms belong to the route
# that carries them and are never copied across routes or institutions.
ROUTE_FIELDS = ("route_id", "fee_route", "institution", "other_fees",
                "evidence_status", "eligibility", "agreement_start",
                "agreement_end", "annual_cap", "policy_url", "checked_on")

# Display widths. The catalog carries publisher names up to 209 characters and
# titles up to 170, so every column is truncated rather than allowed to shift
# the ones after it.
W_PUB, W_OA, W_TITLE = 25, 15, 58


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


def build_index(rows: Iterable[Dict[str, str]]):
    """Tokenize the searchable fields and derive idf over the given rows.

    Called after filtering, so a routed or institution-scoped search pays for
    the rows it can actually return rather than for the whole catalog. The idf
    describes the filtered pool, which is the pool being ranked.
    """
    docs, dfreq = [], Counter()
    for r in rows:
        fields = {k: tokens(r.get(k, "")) for k in WEIGHTS}
        docs.append(fields)
        for t in {t for toks in fields.values() for t in toks}:
            dfreq[t] += 1
    n = len(docs)
    idf = {t: math.log((n + 1) / (c + 0.5)) for t, c in dfreq.items()}
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
    """Whether one fee-route record is usable under the chosen filters and date.

    Eligibility never transfers: a record naming an institution is kept only
    when that institution was asked for. Records marked superseded or excluded,
    and agreements outside their term on --as-of, stay out of ordinary search.
    """
    if not a.include_inactive:
        if r.get("record_status") in {"excluded", "superseded"}:
            return False
        end, start = r.get("agreement_end", ""), r.get("agreement_start", "")
        if (end and end < a.as_of) or (start and start > a.as_of):
            return False
    inst = r.get("institution", "any")
    if a.institutions and inst != "any" and inst not in a.institutions:
        return False
    if a.routes and r.get("fee_route", "") not in a.routes:
        return False
    if a.open_access_only and r.get("fee_route") == "subscription_no_apc":
        return False
    if a.no_other_fees and r.get("other_fees") != "no":
        return False
    if a.publishers and r.get("publisher", "").lower() not in a.publishers:
        return False
    if a.subject and a.subject.lower() not in r.get("subject_area", "").lower():
        return False
    if a.oa and a.oa.lower() not in r.get("oa_model", "").lower():
        return False
    bq = r.get("best_quartile", "")
    if a.require_quartile and not bq:
        return False
    if a.max_quartile and bq and QRANK[bq] > QRANK[a.max_quartile.upper()]:
        return False
    if a.indexed_only and not indexing(r):
        return False
    return True


def indexing(r: Dict[str, str]) -> str:
    """Stated WoS or Scopus coverage, or empty. Absence is silence, not a no."""
    wos = r.get("index_wos", "")
    if wos.lower() in {"", "no", "false", "not covered"}:
        wos = ""
    if r.get("scopus_covered", "").lower() == "yes":
        return f"{wos}, Scopus" if wos else "Scopus"
    return wos


def fmt_row(r: Dict[str, str], sc: float) -> str:
    """Two lines per candidate: what it is, then how it could be paid for."""
    bq = r.get("best_quartile") or "--"
    flag = "" if r.get("best_quartile") else "*"
    head = (f"{sc:6.2f}  {r.get('publisher', '')[:W_PUB]:<{W_PUB}} {bq:<2}{flag:<1} "
            f"{r.get('oa_model', '')[:W_OA]:<{W_OA}} {r.get('journal_title', '')[:W_TITLE]}")
    routes = r.get("available_routes") or [r]
    paid = "; ".join(sorted({f"{x.get('fee_route', '?')}/{x.get('institution', '?')}"
                             for x in routes}))
    detail = [f"routes={paid}",
              f"other_fees={r.get('other_fees', 'unknown')}",
              f"evidence={r.get('evidence_status', '?')}"]
    if r.get("annual_cap"):
        detail.append(f"cap={r['annual_cap']}/year")
    idx = indexing(r)
    if idx:
        detail.append(f"indexed={idx}")
    return head + "\n        " + "  ".join(detail)


def group_by_journal(scored: List[Tuple[float, Dict[str, str]]]):
    """One candidate per journal, carrying every route that passed the filters.

    Grouping is by the catalog's `journal_id`, which links print and electronic
    ISSNs. It attaches routes; it never merges their fee terms.
    """
    groups: Dict[object, Tuple[float, Dict[str, str]]] = {}
    for s, r in scored:
        key = r.get("journal_id") or (r.get("publisher"), r.get("journal_title"))
        if key not in groups:
            groups[key] = (s, {**r, "available_routes": []})
        groups[key][1]["available_routes"].append(
            {k: r.get(k, "") for k in ROUTE_FIELDS})
    return list(groups.values())


def find_records(rows: List[Dict[str, str]], name: str) -> List[Dict[str, str]]:
    """Every record for a title or ISSN, including the journal's other routes."""
    target = name.lower().strip()
    wanted_issn = re.sub(r"[^0-9x]", "", target)
    hits = [
        i for i, r in enumerate(rows)
        if r.get("journal_title", "").lower().strip() == target
        or (len(wanted_issn) == 8 and wanted_issn in {
            re.sub(r"[^0-9x]", "", r.get(k, "").lower()) for k in ("issn", "eissn")})
    ]
    if not hits:
        return []
    picked = set(hits)
    ids = {rows[i].get("journal_id") for i in hits} - {None, ""}
    if ids:
        picked |= {i for i, r in enumerate(rows) if r.get("journal_id") in ids}
    return [rows[i] for i in sorted(picked)]


def cmd_check(rows: List[Dict[str, str]], name: str, a: argparse.Namespace) -> int:
    found = find_records(rows, name)

    if a.json:
        print(json.dumps([{**r, "matches_filters": passes(r, a)} for r in found],
                         ensure_ascii=True, indent=2))
        return 0

    if found:
        for r in found:
            print(f"IN CATALOG: {r.get('journal_title')} ({r.get('publisher')})")
            print(f"  fee route  : {r.get('fee_route')} / {r.get('institution')}; "
                  f"APC payable={r.get('apc_payable') or 'not stated'}; "
                  f"other fees={r.get('other_fees') or 'unknown'}")
            print(f"  eligibility: {r.get('eligibility') or 'not stated'}")
            print(f"  term / cap : {r.get('agreement_start') or '?'} to "
                  f"{r.get('agreement_end') or '?'}; "
                  f"{r.get('annual_cap') or 'no cap stated'}")
            print(f"  evidence   : {r.get('evidence_status')} "
                  f"({r.get('record_status')}); checked {r.get('checked_on')}")
            print(f"  OA model   : {r.get('oa_model') or 'not stated'}")
            print(f"  quartile   : {r.get('best_quartile') or 'not stated'} "
                  f"[{r.get('quartile_basis')}]")
            print(f"  indexing   : {indexing(r) or 'not stated'}")
            print(f"  policy     : {r.get('policy_url') or 'user-supplied list'}")
            print(f"  source     : {r.get('source_file')} / "
                  f"{r.get('source_sheet') or '-'} row {r.get('source_row')}")
            print(f"  notes      : {r.get('notes') or '-'}")
            print(f"  in pool    : {passes(r, a)} under the chosen filters and "
                  f"--as-of {a.as_of}; not a funding approval")
        return 0

    print(f"NOT IN CATALOG: '{name}' does not appear in the bundled records.")
    print("Check the journal's current scope and fee policy. A verified no-APC "
          "route may still be recommended; absence is not a quality judgment.")
    near = difflib.get_close_matches(
        name, sorted({r.get("journal_title", "") for r in rows}), n=6, cutoff=0.6)
    if near:
        print("\nSimilar titles that ARE in the catalog:")
        for t in near:
            r = next(x for x in rows if x.get("journal_title") == t)
            print(f"  - {t} ({r.get('publisher')})")
    return 0


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--catalog", default=str(CATALOG))
    p.add_argument("--query", default="", help="title, keywords, abstract terms")
    p.add_argument("--check", default="", help="show every known route for one title or ISSN")
    p.add_argument("--list-subjects", action="store_true",
                   help="subject vocabulary available under the current filters")
    p.add_argument("--institution", default="",
                   help="UF,MUJ,JKLU or none; universal routes are always included")
    p.add_argument("--route", default="",
                   help="comma-separated: " + ",".join(ROUTES))
    p.add_argument("--open-access-only", action="store_true",
                   help="exclude subscription routes")
    p.add_argument("--no-other-fees", action="store_true",
                   help="only records explicitly declaring no ancillary fees")
    p.add_argument("--as-of", default=date.today().isoformat(),
                   help="eligibility date YYYY-MM-DD; defaults to today")
    p.add_argument("--include-inactive", action="store_true",
                   help="audit only: include expired, future and superseded records")
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
                   help="cap results per publisher so one large publisher cannot "
                        "fill the shortlist")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)

    try:
        date.fromisoformat(a.as_of)
    except ValueError:
        p.error("--as-of must be YYYY-MM-DD")
    a.routes = {x.strip() for x in a.route.split(",") if x.strip()}
    if not a.routes <= set(ROUTES):
        p.error("--route accepts " + ", ".join(ROUTES))
    a.institutions = {x.strip().upper() for x in a.institution.split(",") if x.strip()}
    if not a.institutions <= set(INSTITUTIONS):
        p.error("--institution accepts UF, MUJ, JKLU or none")
    a.publishers = {x.strip().lower() for x in a.publisher.split(",") if x.strip()}
    return a


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    a = parse_args()
    rows = load(Path(a.catalog))

    if a.check:
        return cmd_check(rows, a.check, a)

    if a.list_subjects:
        subs = Counter(r["subject_area"] for r in rows
                       if r.get("subject_area") and passes(r, a))
        for s, c in subs.most_common():
            print(f"{c:>4}  {s}")
        if not subs:
            print("no subject labels under this filter; several source lists "
                  "carry none")
        return 0

    if not a.query:
        sys.exit("give --query, --check, or --list-subjects")

    qt = tokens(a.query)
    if not qt:
        sys.exit("query reduced to zero usable terms after stopword removal")
    qbg = {f"{x} {y}" for x, y in zip(qt, qt[1:])}

    # Filter first: a routed or institution-scoped search then tokenizes only
    # the records it can return.
    pool = [r for r in rows if passes(r, a)]
    docs, idf = build_index(pool)

    scored = [(s, r) for r, fields in zip(pool, docs)
              if (s := score(qt, qbg, fields, idf)) > 0]
    scored.sort(key=lambda t: (-t[0], t[1]["journal_title"]))
    candidates = group_by_journal(scored)

    if a.per_publisher:
        seen: Counter = Counter()
        out = []
        for s, r in candidates:
            if seen[r["publisher"]] < a.per_publisher:
                seen[r["publisher"]] += 1
                out.append((s, r))
    else:
        out = candidates[: a.top]

    if a.json:
        print(json.dumps([{**r, "match_score": round(s, 3)} for s, r in out],
                         indent=2))
        return 0

    if not out:
        print("No titles matched. Either the topic is outside the catalog, or "
              "the filters are too narrow, or the query terms are too specific. "
              "Try broader terms, relax --institution or --route, or "
              "--list-subjects to see the available vocabulary.")
        return 0

    print(f"{len(out)} shown of {len(candidates)} distinct journals matched from "
          f"{len(pool)} fee-route records in scope ({len(rows)} in the catalog, "
          f"as of {a.as_of})\n")
    print(f"{'score':>6}  {'publisher':<{W_PUB}} {'Q':<3} {'OA model':<{W_OA}} title")
    print("-" * (10 + W_PUB + W_OA + W_TITLE))
    for s, r in out:
        print(fmt_row(r, s))
    print("\n*  no quartile in the source list for this record; do not infer one.")
    print("Lexical shortlist only. Confirm scope, article type, review speed, "
          "fee route and eligibility on each journal's own page before "
          "recommending it.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # piping into head closes stdout early; that is not a failure
        sys.stderr.close()
        raise SystemExit(0)
