#!/usr/bin/env python3
"""
check_citations.py - Verify that every source in a source log is real.

Reads a source-log JSON file (schema in references/verification.md) and checks
each entry. For entries with a DOI it queries the Crossref REST API to confirm
the DOI resolves and that the logged title and first author roughly match the
registered metadata. Entries without a DOI are validated structurally and left
for manual confirmation (url-fetch / connector / web-search).

The script is network-optional. With no network (or --offline) it validates
structure, DOI syntax, required fields, and duplicate keys, and marks DOI
resolution as SKIPPED rather than passing it silently.

Usage:
    python check_citations.py sources.json
    python check_citations.py sources.json --offline
    python check_citations.py sources.json --json

Exit codes:
    0  no entry is in FAIL state (delivery may proceed)
    1  at least one entry is in FAIL state
    2  the source log could not be read or parsed
"""

import argparse
import json
import re
import sys

# Crossref asks callers to identify themselves; a mailto in the User-Agent puts
# the request in their "polite pool" and is the documented courtesy convention.
CROSSREF_ENDPOINT = "https://api.crossref.org/works/"
USER_AGENT = "investigating-sources-skill/1.0 (citation verifier; mailto:noreply@example.com)"

# A DOI is a "10." prefix, a registrant code, a slash, then a suffix. This is the
# widely used pragmatic pattern; it rejects obvious junk without over-rejecting
# the long, punctuation-heavy suffixes real DOIs sometimes use.
DOI_PATTERN = re.compile(r"^10\.\d{4,9}/\S+$")

# Titles are compared after stripping case, punctuation, and whitespace runs.
# A match is declared when the shorter normalized title is contained in the
# longer, which tolerates trailing subtitles and registry formatting differences
# without accepting unrelated titles.
TITLE_MIN_LEN = 10  # below this, containment is too weak to be meaningful

REQUIRED_FIELDS = ("key", "type", "title", "year")
VALID_VERIFIED = {"pending", "confirmed", "fail"}

# Network timeout: Crossref usually answers in under a second; 15s absorbs a slow
# connection without hanging a batch of dozens of lookups indefinitely.
REQUEST_TIMEOUT = 15


def load_requests():
    """Return the requests module, or None if it or the network is unavailable."""
    try:
        import requests  # noqa: WPS433 (intentional optional import)
        return requests
    except ImportError:
        return None


def normalize_title(text):
    """Lowercase, strip punctuation, collapse whitespace for lenient comparison."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def titles_match(logged, registered):
    """True if the two normalized titles plausibly refer to the same work."""
    a, b = normalize_title(logged), normalize_title(registered)
    if not a or not b or min(len(a), len(b)) < TITLE_MIN_LEN:
        return False
    shorter, longer = sorted((a, b), key=len)
    return shorter in longer


def first_author_surname(author_field):
    """Extract a lowercase surname from the first entry of an author list."""
    if not author_field:
        return ""
    first = author_field[0]
    # Logs store "Surname, Given"; Crossref stores {"family": ..., "given": ...}.
    if isinstance(first, dict):
        return (first.get("family") or "").strip().lower()
    return str(first).split(",")[0].strip().lower()


def validate_structure(source, seen_keys):
    """Return a list of structural problems for one source entry."""
    problems = []
    for field in REQUIRED_FIELDS:
        if not source.get(field):
            problems.append(f"missing required field '{field}'")

    key = source.get("key", "")
    if key in seen_keys:
        problems.append(f"duplicate key '{key}'")
    seen_keys.add(key)

    verified = source.get("verified", "pending")
    if verified not in VALID_VERIFIED:
        problems.append(f"invalid 'verified' value '{verified}'")

    doi = source.get("doi", "")
    if doi and not DOI_PATTERN.match(doi):
        problems.append(f"malformed DOI '{doi}'")

    return problems


def check_doi_live(requests, doi):
    """
    Query Crossref for a DOI.

    Returns (status, detail, metadata) where status is one of:
        "resolved"    DOI exists; metadata returned for matching
        "not_found"   Crossref has no record of this DOI
        "error"       transient failure (timeout, HTTP error); inconclusive
    """
    try:
        resp = requests.get(
            CROSSREF_ENDPOINT + doi,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
    except Exception as exc:  # network stack failure; treat as inconclusive
        return "error", f"request failed: {exc}", None

    if resp.status_code == 404:
        return "not_found", "Crossref returned 404 (no such DOI)", None
    if resp.status_code != 200:
        return "error", f"Crossref returned HTTP {resp.status_code}", None

    try:
        message = resp.json().get("message", {})
    except ValueError:
        return "error", "Crossref response was not valid JSON", None

    titles = message.get("title") or []
    reg_title = titles[0] if titles else ""
    reg_authors = message.get("author") or []
    reg_surname = first_author_surname(reg_authors)
    return "resolved", "DOI resolved", {"title": reg_title, "surname": reg_surname}


def evaluate_source(source, requests, offline, seen_keys):
    """
    Decide a source's status and update it in place.

    Returns a result dict describing the outcome for reporting.
    """
    problems = validate_structure(source, seen_keys)
    key = source.get("key", "<no-key>")
    doi = source.get("doi", "")

    # Structural failure is fatal regardless of network state.
    if problems:
        source["verified"] = "fail"
        return {"key": key, "status": "FAIL", "reason": "; ".join(problems)}

    if not doi:
        # No DOI: cannot auto-verify. Respect an existing manual confirmation,
        # otherwise leave it pending for the researcher to confirm by hand.
        if source.get("verified") == "confirmed" and source.get("verify_method"):
            return {"key": key, "status": "OK",
                    "reason": f"manually confirmed via {source['verify_method']}"}
        return {"key": key, "status": "PENDING",
                "reason": "no DOI; confirm via url-fetch, connector, or web-search"}

    if offline or requests is None:
        # DOI syntax already validated; resolution needs a network we don't have.
        note = "offline" if offline else "requests unavailable"
        if source.get("verified") == "confirmed" and source.get("verify_method"):
            return {"key": key, "status": "OK",
                    "reason": f"DOI resolution SKIPPED ({note}); "
                              f"prior manual confirmation via {source['verify_method']}"}
        return {"key": key, "status": "SKIPPED",
                "reason": f"DOI syntax valid; resolution SKIPPED ({note})"}

    status, detail, meta = check_doi_live(requests, doi)

    if status == "not_found":
        source["verified"] = "fail"
        return {"key": key, "status": "FAIL", "reason": detail}

    if status == "error":
        # Inconclusive: do not fail a source over a transient network problem.
        return {"key": key, "status": "SKIPPED",
                "reason": f"{detail}; verify manually"}

    # Resolved. Confirm the metadata is consistent with the log.
    source["verified"] = "confirmed"
    source["verify_method"] = "crossref"
    mismatches = []
    if not titles_match(source.get("title", ""), meta["title"]):
        mismatches.append(f"title differs from Crossref ('{meta['title']}')")
    logged_surname = first_author_surname(source.get("authors"))
    if logged_surname and meta["surname"] and logged_surname != meta["surname"]:
        mismatches.append(
            f"first author '{logged_surname}' != Crossref '{meta['surname']}'")

    if mismatches:
        # DOI is real but points somewhere else: a classic mashup signal.
        return {"key": key, "status": "WARN",
                "reason": "DOI resolves but " + "; ".join(mismatches)}
    return {"key": key, "status": "OK", "reason": "DOI resolved; metadata matches"}


def main():
    parser = argparse.ArgumentParser(description="Verify sources in a source log.")
    parser.add_argument("source_log", help="Path to the source-log JSON file")
    parser.add_argument("--offline", action="store_true",
                        help="Skip all network calls; structural checks only")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Emit a machine-readable JSON report")
    args = parser.parse_args()

    try:
        with open(args.source_log, encoding="utf-8") as fh:
            log = json.load(fh)
    except FileNotFoundError:
        print(f"error: file not found: {args.source_log}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {args.source_log}: {exc}", file=sys.stderr)
        return 2

    sources = log.get("sources", [])
    if not isinstance(sources, list) or not sources:
        print("error: source log has no 'sources' array", file=sys.stderr)
        return 2

    requests = None if args.offline else load_requests()
    network_note = None
    if not args.offline and requests is None:
        network_note = ("requests not installed; running offline. "
                        "Install with: pip install requests --break-system-packages")

    seen_keys = set()
    results = [evaluate_source(s, requests, args.offline, seen_keys)
               for s in sources]

    failures = [r for r in results if r["status"] == "FAIL"]

    if args.as_json:
        print(json.dumps({
            "source_log": args.source_log,
            "offline": args.offline or requests is None,
            "total": len(results),
            "failures": len(failures),
            "results": results,
        }, indent=2))
    else:
        if network_note:
            print(f"NOTE: {network_note}\n")
        width = max((len(r["key"]) for r in results), default=3)
        for r in results:
            print(f"[{r['status']:<7}] {r['key']:<{width}}  {r['reason']}")
        print()
        counts = {}
        for r in results:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        summary = ", ".join(f"{k}: {v}" for k, v in sorted(counts.items()))
        print(f"Summary ({len(results)} sources): {summary}")
        if failures:
            print(f"\n{len(failures)} source(s) FAILED and must be removed "
                  f"along with any claims that depended on them.")
        elif any(r["status"] in ("PENDING", "SKIPPED", "WARN") for r in results):
            print("\nNo hard failures, but PENDING/SKIPPED/WARN entries need "
                  "manual confirmation before delivery.")
        else:
            print("\nAll sources verified. Delivery may proceed.")

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
