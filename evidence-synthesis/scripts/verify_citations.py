#!/usr/bin/env python3
"""Verify that cited works exist, match what was claimed, and are not retracted.

This is the single most important script in this skill. Two distinct failure
modes are checked, because they need different evidence:

  Fabricated  - the work does not exist, or the DOI resolves to something else.
                Caught by metadata comparison against Crossref/OpenAlex.
  Retracted   - the work exists but has been withdrawn. Caught only by checking
                retraction status; a DOI lookup that returns a record says
                nothing about whether that record is still valid.

General-purpose language models are unreliable at both. Crossref has ingested
the Retraction Watch database and exposes it through the `updated-by` field on
the retracted record and `update-to` on the notice; OpenAlex exposes the same
signal as `is_retracted`. This script queries both and reports disagreement
rather than silently picking one.

Usage
-----
    # From a reference list (one reference per line, or a markdown list)
    python verify_citations.py --refs references.md --mailto you@uni.edu

    # From DOIs directly
    python verify_citations.py --doi 10.1136/bmj.n71 --doi 10.1136/bmj.q902 \\
        --mailto you@uni.edu

    # Structural check only, no network (parses and reports what it found)
    python verify_citations.py --refs references.md --offline

    # Verify the matching logic itself against built-in fixtures
    python verify_citations.py --self-test

Exit status is 1 if any reference fails, so this can gate a commit or a
submission checklist.

A `mailto` is required for network use. Crossref's polite pool gives
substantially better reliability, and sending an address is the courtesy that
keeps a free service free.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

CROSSREF = "https://api.crossref.org/works/"
CROSSREF_QUERY = "https://api.crossref.org/works"
OPENALEX = "https://api.openalex.org/works/doi:"

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.I)
YEAR_RE = re.compile(r"\((\d{4})[a-z]?\)|\b(19|20)\d{2}\b")

# Verdicts, ordered by severity.
OK, MINOR, FAIL, UNKNOWN = "VERIFIED", "CHECK", "FAIL", "UNCHECKED"


@dataclass
class Ref:
    raw: str
    doi: Optional[str] = None
    claimed_title: Optional[str] = None
    claimed_year: Optional[int] = None
    claimed_author: Optional[str] = None
    found_title: Optional[str] = None
    found_year: Optional[int] = None
    found_journal: Optional[str] = None
    found_authors: List[str] = field(default_factory=list)
    retracted: Optional[bool] = None
    update_notices: List[str] = field(default_factory=list)
    title_similarity: Optional[float] = None
    verdict: str = ""
    notes: List[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

def normalize_title(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)          # Crossref titles carry JATS markup
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def parse_reference(line: str) -> Ref:
    """Pull DOI, title guess, year, and first-author surname out of a reference
    string. Deliberately tolerant: reference lists arrive in every style, and a
    parser that only handles APA would silently skip most of them."""
    raw = line.strip().lstrip("-*0123456789. )").strip()
    r = Ref(raw=raw)

    m = DOI_RE.search(raw)
    if m:
        r.doi = m.group(0).rstrip(".,;)")

    ym = YEAR_RE.search(raw)
    if ym:
        r.claimed_year = int(ym.group(1) or ym.group(0))

    am = re.match(r"([A-Z][A-Za-z'\u00C0-\u024F-]+)\s*,", raw)
    if am:
        r.claimed_author = am.group(1)

    # Title heuristic: the longest sentence-like span that is not the source
    # string, the DOI, or the author block.
    body = DOI_RE.sub("", raw)
    body = re.sub(r"https?://\S+", "", body)
    parts = [p.strip() for p in re.split(r"(?<=[.?!])\s+(?=[A-Z(])|\.\s+", body)
             if len(p.strip()) > 15]
    cands = [p for p in parts if not re.match(r"^[A-Z][a-z]*,\s*[A-Z]\.", p)]
    if cands:
        r.claimed_title = max(cands, key=len).strip(" .")
    return r


def load_refs(path: str) -> List[Ref]:
    text = open(path, encoding="utf-8").read()
    if path.endswith(".bib"):
        return parse_bibtex(text)
    lines = [l for l in text.splitlines() if l.strip() and len(l.strip()) > 20]
    return [parse_reference(l) for l in lines]


def parse_bibtex(text: str) -> List[Ref]:
    out = []
    for entry in re.split(r"\n(?=@)", text):
        if not entry.strip().startswith("@"):
            continue
        def fld(name: str) -> Optional[str]:
            m = re.search(rf"{name}\s*=\s*[{{\"]+(.+?)[}}\"]+\s*,?\s*\n", entry,
                          re.I | re.S)
            return re.sub(r"\s+", " ", m.group(1)).strip() if m else None
        r = Ref(raw=re.sub(r"\s+", " ", entry)[:200])
        r.doi = fld("doi")
        r.claimed_title = fld("title")
        y = fld("year")
        r.claimed_year = int(y) if y and y.isdigit() else None
        a = fld("author")
        if a:
            r.claimed_author = re.split(r"\s+and\s+|,", a)[0].strip().split()[-1]
        out.append(r)
    return out


# --------------------------------------------------------------------------
# network
# --------------------------------------------------------------------------

def fetch_json(url: str, timeout: int = 20):
    """Returns (data, error). error is None, 'notfound' (the server answered and
    said no such record), or 'network' (we never got an answer).

    The distinction is the whole point: an unreachable API must never be
    reported as a nonexistent paper. Conflating the two would turn a firewall
    into an accusation of fabrication.
    """
    req = urllib.request.Request(url, headers={
        "User-Agent": "evidence-synthesis-skill/1.0 (citation verification)",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        return (None, "notfound") if e.code in (404, 410) else (None, "network")
    except Exception:
        return None, "network"


def crossref_by_doi(doi: str, mailto: str):
    url = CROSSREF + urllib.parse.quote(doi, safe="") + f"?mailto={mailto}"
    data, err = fetch_json(url)
    return (data.get("message") if data else None), err


def crossref_by_title(title: str, mailto: str):
    q = urllib.parse.urlencode({"query.bibliographic": title[:300],
                                "rows": 3, "mailto": mailto})
    data, err = fetch_json(f"{CROSSREF_QUERY}?{q}")
    items = (data or {}).get("message", {}).get("items", [])
    return (items[0] if items else None), err


def openalex_by_doi(doi: str, mailto: str):
    return fetch_json(OPENALEX + urllib.parse.quote(doi, safe="") + f"?mailto={mailto}")


# --------------------------------------------------------------------------
# evaluation
# --------------------------------------------------------------------------

def extract_crossref(msg: Dict[str, Any]) -> Dict[str, Any]:
    title = (msg.get("title") or [""])[0]
    year = None
    for key in ("published-print", "published-online", "issued", "created"):
        dp = (msg.get(key) or {}).get("date-parts") or []
        if dp and dp[0] and dp[0][0]:
            year = int(dp[0][0])
            break
    authors = [a.get("family", "") for a in (msg.get("author") or []) if a.get("family")]
    journal = (msg.get("container-title") or [""])[0]

    notices = []
    for u in msg.get("updated-by") or []:
        notices.append(f"{u.get('type', 'update')} ({u.get('source', '?')}) "
                       f"-> {u.get('DOI', '?')}")
    for rel_name, rels in (msg.get("relation") or {}).items():
        if "retract" in rel_name.lower() or "withdraw" in rel_name.lower():
            for rel in rels:
                notices.append(f"relation:{rel_name} -> {rel.get('id', '?')}")

    retracted = any("retract" in n.lower() or "withdraw" in n.lower() for n in notices)
    return {"title": title, "year": year, "authors": authors, "journal": journal,
            "notices": notices, "retracted": retracted,
            "type": msg.get("type", ""), "doi": msg.get("DOI", "")}


def evaluate(r: Ref, mailto: str) -> Ref:
    msg, err = None, None
    if r.doi:
        msg, err = crossref_by_doi(r.doi, mailto)
        if msg is None and err == "notfound":
            r.notes.append("DOI did not resolve in Crossref")
    if msg is None and r.claimed_title:
        msg, err2 = crossref_by_title(r.claimed_title, mailto)
        err = err if msg is None and err == "network" else err2
        if msg is not None:
            r.notes.append("matched by bibliographic search, not by DOI")

    if msg is None:
        if err == "network":
            r.verdict = UNKNOWN
            r.notes.append("could not reach Crossref; this reference was NOT "
                           "checked. Do not read this as a fabrication.")
        else:
            r.verdict = FAIL
            r.notes.append("no matching record found; treat as unverified and "
                           "remove or replace it")
        return r

    info = extract_crossref(msg)
    r.found_title = info["title"]
    r.found_year = info["year"]
    r.found_journal = info["journal"]
    r.found_authors = info["authors"][:5]
    r.update_notices = info["notices"]
    r.retracted = info["retracted"]
    if not r.doi and info["doi"]:
        r.doi = info["doi"]

    # Corroborate retraction status independently. Disagreement is reported, not
    # resolved: the two sources update on different schedules and a conflict is
    # itself the useful signal.
    if r.doi:
        oa, _oa_err = openalex_by_doi(r.doi, mailto)
        if oa is not None:
            oa_ret = bool(oa.get("is_retracted"))
            if oa_ret and not r.retracted:
                r.retracted = True
                r.notes.append("OpenAlex reports retracted; Crossref does not")
            elif r.retracted and not oa_ret:
                r.notes.append("Crossref reports a retraction notice; "
                               "OpenAlex is_retracted is false")

    if r.claimed_title and r.found_title:
        r.title_similarity = round(difflib.SequenceMatcher(
            None, normalize_title(r.claimed_title),
            normalize_title(r.found_title)).ratio(), 3)

    return assign_verdict(r)


def assign_verdict(r: Ref) -> Ref:
    """Severity ladder. A retraction outranks everything: a correctly cited
    retracted paper is still a problem, and citing one without acknowledging the
    retraction is the error this catches."""
    if r.retracted:
        r.verdict = FAIL
        r.notes.append("RETRACTED or withdrawn. Remove it, or cite it explicitly "
                       "as retracted and explain why it still belongs.")
        return r

    if r.update_notices:
        r.verdict = MINOR
        r.notes.append("has a correction or expression of concern; check whether "
                       "it affects the claim you are citing it for")

    if r.title_similarity is not None and r.title_similarity < 0.55:
        r.verdict = FAIL
        r.notes.append(f"title mismatch (similarity {r.title_similarity}): the DOI "
                       f"resolves to a different work than the one cited")
        return r
    if r.title_similarity is not None and r.title_similarity < 0.80:
        r.verdict = r.verdict or MINOR
        r.notes.append(f"title only partially matches (similarity "
                       f"{r.title_similarity})")

    if r.claimed_year and r.found_year and abs(r.claimed_year - r.found_year) > 1:
        r.verdict = r.verdict or MINOR
        r.notes.append(f"year mismatch: cited {r.claimed_year}, record says "
                       f"{r.found_year}")

    if r.claimed_author and r.found_authors:
        if not any(r.claimed_author.lower() == a.lower() for a in r.found_authors):
            r.verdict = r.verdict or MINOR
            r.notes.append(f"first author '{r.claimed_author}' not among "
                           f"{r.found_authors[:3]}")

    r.verdict = r.verdict or OK
    return r


# --------------------------------------------------------------------------
# self test
# --------------------------------------------------------------------------

FIXTURES = [
    # (description, Ref kwargs, expected verdict)
    ("clean match", dict(
        claimed_title="The PRISMA 2020 statement: an updated guideline for reporting systematic reviews",
        found_title="The PRISMA 2020 statement: an updated guideline for reporting systematic reviews",
        claimed_year=2021, found_year=2021, claimed_author="Page",
        found_authors=["Page", "McKenzie"], retracted=False), OK),
    ("retracted outranks a clean match", dict(
        claimed_title="Some study", found_title="Some study",
        claimed_year=2020, found_year=2020, retracted=True,
        update_notices=["retraction (retraction-watch) -> 10.1000/x"]), FAIL),
    ("DOI resolves to a different paper", dict(
        claimed_title="Deep learning for colorectal histopathology triage",
        found_title="A survey of medieval agricultural practice",
        claimed_year=2023, found_year=2023, retracted=False), FAIL),
    ("year off by three", dict(
        claimed_title="Identical title here for the test",
        found_title="Identical title here for the test",
        claimed_year=2018, found_year=2021, retracted=False), MINOR),
    ("author not on the paper", dict(
        claimed_title="Identical title here for the test",
        found_title="Identical title here for the test",
        claimed_year=2021, found_year=2021, claimed_author="Nobody",
        found_authors=["Page", "McKenzie"], retracted=False), MINOR),
    ("correction notice", dict(
        claimed_title="Identical title here for the test",
        found_title="Identical title here for the test",
        claimed_year=2021, found_year=2021, retracted=False,
        update_notices=["correction (publisher) -> 10.1000/y"]), MINOR),
]


def self_test() -> int:
    failures = 0
    for desc, kw, expected in FIXTURES:
        r = Ref(raw=desc, **kw)
        if r.claimed_title and r.found_title:
            r.title_similarity = round(difflib.SequenceMatcher(
                None, normalize_title(r.claimed_title),
                normalize_title(r.found_title)).ratio(), 3)
        got = assign_verdict(r).verdict
        ok = got == expected
        failures += (not ok)
        print(f"[{'pass' if ok else 'FAIL'}] {desc}: expected {expected}, got {got}")
    print(f"\n{len(FIXTURES) - failures}/{len(FIXTURES)} fixtures passed")
    return 1 if failures else 0


# --------------------------------------------------------------------------

def report(refs: List[Ref], as_json: bool) -> int:
    if as_json:
        print(json.dumps([asdict(r) for r in refs], indent=2))
    else:
        counts = {OK: 0, MINOR: 0, FAIL: 0, UNKNOWN: 0}
        for i, r in enumerate(refs, 1):
            counts[r.verdict] = counts.get(r.verdict, 0) + 1
            head = r.claimed_title or r.raw
            print(f"\n[{i}] {r.verdict}  {head[:88]}")
            if r.doi:
                print(f"     doi   : {r.doi}")
            if r.found_title and r.found_title != r.claimed_title:
                print(f"     found : {r.found_title[:88]}")
            if r.found_journal:
                print(f"     source: {r.found_journal[:70]} ({r.found_year})")
            for n in r.update_notices:
                print(f"     notice: {n}")
            for n in r.notes:
                print(f"     note  : {n}")
        print("\n" + "-" * 70)
        print(f"{counts.get(OK,0)} verified, {counts.get(MINOR,0)} to check, "
              f"{counts.get(FAIL,0)} failed, {counts.get(UNKNOWN,0)} unchecked, "
              f"{len(refs)} total")
        if counts.get(UNKNOWN):
            print("\nSome references could not be checked because the service was "
                  "unreachable. Unchecked is not the same as verified: rerun when "
                  "you have network access before treating this list as clean.")
        if counts.get(FAIL):
            print("\nA reference that cannot be confirmed does not go in the "
                  "manuscript. 'Difficult to verify' is a fail, not a caveat.")
    if any(r.verdict == FAIL for r in refs):
        return 1
    return 2 if any(r.verdict == UNKNOWN for r in refs) else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--refs", help="file with one reference per line, or a .bib")
    p.add_argument("--doi", action="append", default=[], help="repeatable")
    p.add_argument("--mailto", default="", help="your email, for the Crossref polite pool")
    p.add_argument("--offline", action="store_true",
                   help="parse only, no network; shows what would be checked")
    p.add_argument("--self-test", action="store_true",
                   help="run the verdict logic against built-in fixtures")
    p.add_argument("--json", action="store_true")
    p.add_argument("--delay", type=float, default=0.4,
                   help="seconds between requests; be polite to free services")
    a = p.parse_args()

    if a.self_test:
        return self_test()

    refs: List[Ref] = []
    if a.refs:
        refs.extend(load_refs(a.refs))
    refs.extend(Ref(raw=d, doi=d) for d in a.doi)
    if not refs:
        sys.exit("give --refs, --doi, or --self-test")

    if a.offline:
        print(f"parsed {len(refs)} references (offline; nothing verified)\n")
        for i, r in enumerate(refs, 1):
            print(f"[{i}] doi={r.doi or '-'}  year={r.claimed_year or '-'}  "
                  f"author={r.claimed_author or '-'}")
            print(f"     title guess: {(r.claimed_title or '?')[:80]}")
        print("\nRun without --offline and with --mailto to check existence, "
              "metadata match, and retraction status.")
        return 0

    if not a.mailto:
        sys.exit("--mailto is required for network use (Crossref polite pool)")

    for i, r in enumerate(refs):
        evaluate(r, a.mailto)
        if i < len(refs) - 1:
            time.sleep(a.delay)

    return report(refs, a.json)


if __name__ == "__main__":
    raise SystemExit(main())
