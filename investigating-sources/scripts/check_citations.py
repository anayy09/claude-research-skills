#!/usr/bin/env python3
"""
check_citations.py - Verify that every source in a source log is real, is the
version of record, and has not been retracted.

Reads a source-log JSON file (schema in references/verification.md) and checks
each entry against free, keyless metadata APIs:

  * Existence      Crossref for the great majority of DOIs, DataCite for the
                   rest. arXiv registers with DataCite, so a Crossref-only
                   checker reports every arXiv citation as a fabrication, which
                   is a false accusation on a real object.
  * Metadata match Title and first author compared against the registered
                   record. A DOI that resolves to a different work is the
                   mashup signature.
  * Peer review    Record type from Crossref, DataCite, and OpenAlex. Read from
                   the record, never from the publisher: SSRN sits under
                   Elsevier's DOI prefix and TechRxiv under IEEE's.
  * Supersession   A preprint whose peer-reviewed version exists is not the
                   version to cite. Found through Crossref's is-preprint-of
                   relation, the bioRxiv/medRxiv API, and OpenAlex locations.
  * Retraction     Crossref update notices, corroborated by OpenAlex
                   is_retracted.

The script is network-optional. With no network (or --offline) it validates
structure, DOI syntax, required fields, and duplicate keys, flags known preprint
prefixes as a hint, and marks resolution as SKIPPED rather than passing it
silently.

Usage:
    python check_citations.py sources.json
    python check_citations.py sources.json --mailto you@institution.edu
    python check_citations.py sources.json --upgrade-preprints
    python check_citations.py sources.json --require-peer-reviewed
    python check_citations.py sources.json --offline
    python check_citations.py sources.json --json
    python check_citations.py --self-test

Exit codes:
    0  no entry is in FAIL state (delivery may proceed)
    1  at least one entry is in FAIL state
    2  the source log could not be read or parsed
"""

import argparse
import json
import re
import sys

# Crossref asks callers to identify themselves; a mailto puts the request in
# their "polite pool" and is the documented courtesy convention.
CROSSREF_ENDPOINT = "https://api.crossref.org/works/"
CROSSREF_SEARCH = "https://api.crossref.org/works"
DATACITE_ENDPOINT = "https://api.datacite.org/dois/"
OPENALEX_ENDPOINT = "https://api.openalex.org/works/doi:"
BIORXIV_ENDPOINT = "https://api.biorxiv.org/details/{server}/{doi}"
USER_AGENT = "investigating-sources-skill/1.1 (citation verifier)"

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

# Source-log types that assert peer review. If the log says journal-article and
# the registry says posted-content, the log is wrong and the checker says so.
PEER_REVIEWED_LOG_TYPES = {"journal-article", "conference-paper", "book",
                           "book-chapter"}

# Crossref record types that represent a peer-reviewed publication. Conference
# proceedings are included because in computing the conference is the reviewed
# venue of record; the venue still has to be recorded, since elsewhere a
# proceedings entry can be an unreviewed abstract.
REVIEWED_CROSSREF_TYPES = {"journal-article", "proceedings-article",
                           "book-chapter", "book", "monograph", "edited-book",
                           "reference-entry"}

# Offline hints only; the live record type is authoritative. These exist so that
# --offline can still say something useful, and so an unreachable API does not
# leave a well-known preprint prefix silently unflagged. Note that two of these
# belong to major publishers, which is exactly why publisher name is never used
# as the signal.
PREPRINT_PREFIXES = {
    "10.48550": "arXiv",
    "10.1101": "bioRxiv/medRxiv",
    "10.21203": "Research Square",
    "10.2139": "SSRN (Elsevier)",
    "10.31234": "PsyArXiv",
    "10.31235": "SocArXiv",
    "10.36227": "TechRxiv (IEEE)",
    "10.20944": "Preprints.org (MDPI)",
    "10.26434": "ChemRxiv (ACS)",
    "10.31219": "OSF Preprints",
}

# Network timeout: Crossref usually answers in under a second; 15s absorbs a slow
# connection without hanging a batch of dozens of lookups indefinitely.
REQUEST_TIMEOUT = 15
MAX_RETRIES = 2


def load_requests():
    """Return the requests module, or None if it is unavailable."""
    try:
        import requests  # noqa: WPS433 (intentional optional import)
        return requests
    except ImportError:
        return None


def doi_prefix(doi):
    return doi.split("/", 1)[0] if doi else ""


def normalize_title(text):
    """Lowercase, strip punctuation, collapse whitespace for lenient comparison."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def titles_match(logged, registered):
    """True if the two normalized titles plausibly refer to the same work.

    Containment, so that a logged title missing its subtitle still matches.
    This is the right leniency when checking a DOI the user already has, and
    the wrong leniency when picking a replacement DOI out of a search: see
    strict_title_match.
    """
    a, b = normalize_title(logged), normalize_title(registered)
    if not a or not b or min(len(a), len(b)) < TITLE_MIN_LEN:
        return False
    shorter, longer = sorted((a, b), key=len)
    return shorter in longer


def strict_title_match(a, b, threshold=0.90):
    """Near-identity, used when a search result is about to replace a citation.

    Containment is dangerous here. "Attention is all you need" is contained in
    "Attention is all you need: utilizing attention in AI-enabled drug
    discovery", which is a different paper by different authors in a different
    field. Promoting that to a version of record would fabricate a citation
    while appearing to fix one.
    """
    import difflib
    x, y = normalize_title(a), normalize_title(b)
    if not x or not y:
        return False
    return difflib.SequenceMatcher(None, x, y).ratio() >= threshold


def first_author_surname(author_field):
    """Extract a lowercase surname from the first entry of an author list."""
    if not author_field:
        return ""
    first = author_field[0]
    # Logs store "Surname, Given"; Crossref stores {"family": ..., "given": ...}.
    if isinstance(first, dict):
        return (first.get("family") or first.get("familyName") or "").strip().lower()
    return str(first).split(",")[0].strip().lower()


def classify_peer_review(record_type, subtype, doi):
    """Peer-review status from the record itself, not from the publisher."""
    if record_type in ("posted-content", "Preprint") or subtype == "preprint":
        return "preprint"
    if doi and doi_prefix(doi) in PREPRINT_PREFIXES:
        # A preprint prefix with a non-preprint record type is unusual enough to
        # warrant the conservative reading rather than the flattering one.
        return "preprint"
    if record_type in REVIEWED_CROSSREF_TYPES:
        return "peer-reviewed"
    if record_type in ("dataset", "component", "peer-review", "grant",
                       "report", "other", "Text", "Dataset"):
        return "not-peer-reviewed"
    return "unknown"


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


# ---------------------------------------------------------------------------
# network
# ---------------------------------------------------------------------------

def get_json(requests, url, mailto=""):
    """
    Fetch JSON with retries.

    Returns (status, payload) where status is one of:
        "ok"          payload is the decoded JSON
        "not_found"   the server answered and said no such record
        "error"       transient or unreachable; inconclusive, never a failure

    The distinction between not_found and error is the whole point. An
    unreachable API must never be reported as a nonexistent paper, or a firewall
    becomes an accusation of fabrication.
    """
    headers = {"User-Agent": USER_AGENT
               + (f" (mailto:{mailto})" if mailto else ""),
               "Accept": "application/json"}
    last = "request failed"
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        except Exception as exc:  # network stack failure; inconclusive
            last = f"request failed: {exc}"
            if attempt == MAX_RETRIES:
                return "error", last
            continue
        if resp.status_code in (404, 410):
            return "not_found", f"registry returned {resp.status_code}"
        if resp.status_code == 200:
            try:
                return "ok", resp.json()
            except ValueError:
                return "error", "response was not valid JSON"
        last = f"registry returned HTTP {resp.status_code}"
        if resp.status_code not in (429, 500, 502, 503, 504):
            return "error", last
    return "error", last


def crossref_lookup(requests, doi, mailto):
    status, payload = get_json(
        requests, CROSSREF_ENDPOINT + doi
        + (f"?mailto={mailto}" if mailto else ""), mailto)
    if status != "ok":
        return status, payload, None
    message = (payload or {}).get("message", {}) or {}
    titles = message.get("title") or []
    relation = message.get("relation") or {}

    published = None
    for rel in relation.get("is-preprint-of") or []:
        if rel.get("id-type") == "doi" and rel.get("id"):
            published = rel["id"]
            break

    notices = []
    for u in message.get("updated-by") or []:
        notices.append(f"{u.get('type', 'update')} -> {u.get('DOI', '?')}")
    retracted = any("retract" in n.lower() or "withdraw" in n.lower()
                    for n in notices)

    container = message.get("container-title") or []
    institution = message.get("institution") or []
    if isinstance(institution, dict):
        institution = [institution]
    venue = (container[0] if container else
             (institution[0] or {}).get("name", "") if institution else "")

    return "ok", "DOI resolved via Crossref", {
        "title": titles[0] if titles else "",
        "surname": first_author_surname(message.get("author") or []),
        "type": message.get("type", ""),
        "subtype": message.get("subtype", ""),
        "venue": venue,
        "published_version": published,
        "notices": notices,
        "retracted": retracted,
        "registry": "crossref",
    }


def datacite_lookup(requests, doi):
    """arXiv and most repository DOIs live here, not in Crossref."""
    status, payload = get_json(requests, DATACITE_ENDPOINT + doi)
    if status != "ok":
        return status, payload, None
    attrs = ((payload or {}).get("data") or {}).get("attributes") or {}
    titles = attrs.get("titles") or []
    publisher = attrs.get("publisher") or ""
    if isinstance(publisher, dict):
        publisher = publisher.get("name", "")
    published = None
    for rel in attrs.get("relatedIdentifiers") or []:
        if (rel.get("relatedIdentifierType") == "DOI"
                and rel.get("relationType") in ("IsPreviousVersionOf",
                                                "IsPublishedIn",
                                                "IsIdenticalTo")):
            published = rel.get("relatedIdentifier")
            break
    return "ok", "DOI resolved via DataCite", {
        "title": (titles[0] or {}).get("title", "") if titles else "",
        "surname": first_author_surname(attrs.get("creators") or []),
        "type": (attrs.get("types") or {}).get("resourceTypeGeneral", ""),
        "subtype": "",
        "venue": publisher,
        "published_version": published,
        "notices": [],
        "retracted": False,
        "registry": "datacite",
    }


def openalex_lookup(requests, doi, mailto):
    status, payload = get_json(
        requests, OPENALEX_ENDPOINT + doi + (f"?mailto={mailto}" if mailto else ""),
        mailto)
    if status != "ok":
        return None
    return payload


def find_published_version(requests, source, meta, mailto):
    """Crossref relation, then the bioRxiv API, then OpenAlex locations."""
    if meta.get("published_version"):
        return meta["published_version"], "crossref is-preprint-of"

    doi = source.get("doi", "")
    if doi_prefix(doi) == "10.1101":
        for server in ("biorxiv", "medrxiv"):
            status, payload = get_json(
                requests, BIORXIV_ENDPOINT.format(server=server, doi=doi))
            if status == "ok":
                coll = (payload or {}).get("collection") or []
                if coll:
                    pub = (coll[-1] or {}).get("published", "")
                    if pub and pub.upper() != "NA":
                        return pub, "bioRxiv/medRxiv API"

    work = openalex_lookup(requests, doi, mailto)
    for loc in (work or {}).get("locations") or []:
        src = loc.get("source") or {}
        if src.get("type") == "journal" and loc.get("version") == "publishedVersion":
            cand = ((work or {}).get("doi") or "").replace("https://doi.org/", "")
            if cand and cand.lower() != doi.lower():
                return cand, f"OpenAlex ({src.get('display_name', 'journal')})"

    # Last resort: a title search restricted to peer-reviewed journal articles.
    # Both the title and the first author must match, and the title match is the
    # strict one. A same-title paper by different authors is a different paper,
    # and promoting it would fabricate a citation while appearing to fix one.
    title = source.get("title") or meta.get("title") or ""
    logged_surname = first_author_surname(source.get("authors")) or meta.get("surname", "")
    if len(title) > 20:
        status, payload = get_json(
            requests,
            f"{CROSSREF_SEARCH}?query.bibliographic="
            f"{requests.utils.quote(title[:300])}"
            f"&filter=type:journal-article&rows=3"
            + (f"&mailto={mailto}" if mailto else ""), mailto)
        if status == "ok":
            for item in ((payload or {}).get("message") or {}).get("items") or []:
                cand_title = (item.get("title") or [""])[0]
                cand_surname = first_author_surname(item.get("author") or [])
                if not strict_title_match(title, cand_title):
                    continue
                if logged_surname and cand_surname and logged_surname != cand_surname:
                    continue
                return item.get("DOI"), "Crossref title search (confirm before citing)"
    return None, ""


# ---------------------------------------------------------------------------
# evaluation
# ---------------------------------------------------------------------------

def evaluate_source(source, requests, offline, seen_keys, mailto="",
                    upgrade=False, require_peer_reviewed=False):
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

    hint = PREPRINT_PREFIXES.get(doi_prefix(doi), "")

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
        suffix = f"; {hint} preprint prefix (hint only)" if hint else ""
        if source.get("verified") == "confirmed" and source.get("verify_method"):
            return {"key": key, "status": "OK",
                    "reason": f"resolution SKIPPED ({note}); prior manual "
                              f"confirmation via {source['verify_method']}{suffix}"}
        return {"key": key, "status": "SKIPPED",
                "reason": f"DOI syntax valid; resolution SKIPPED ({note}){suffix}"}

    status, detail, meta = crossref_lookup(requests, doi, mailto)

    if status == "not_found":
        # Not a fabrication yet: the DOI may be registered with DataCite.
        status, detail, meta = datacite_lookup(requests, doi)
        if status == "not_found":
            source["verified"] = "fail"
            return {"key": key, "status": "FAIL",
                    "reason": "DOI not found in Crossref or DataCite"}
        if status == "error":
            return {"key": key, "status": "SKIPPED",
                    "reason": f"not in Crossref and DataCite unreachable "
                              f"({detail}); verify manually"}

    if status == "error":
        # Inconclusive: do not fail a source over a transient network problem.
        return {"key": key, "status": "SKIPPED",
                "reason": f"{detail}; verify manually"}

    # Resolved somewhere. Record what the registry says.
    source["verified"] = "confirmed"
    source["verify_method"] = meta["registry"]
    source["venue_type"] = meta.get("venue", "") or source.get("venue", "")

    peer_review = classify_peer_review(meta["type"], meta["subtype"], doi)

    # OpenAlex sees repository deposits that Crossref types as articles, and is
    # the second opinion on retraction.
    work = openalex_lookup(requests, doi, mailto)
    if work:
        if work.get("is_retracted") and not meta["retracted"]:
            meta["retracted"] = True
            meta["notices"].append("OpenAlex reports retracted; Crossref does not")
        primary = work.get("primary_location") or {}
        src = primary.get("source") or {}
        if peer_review == "unknown":
            if work.get("type") == "preprint" or src.get("type") == "repository":
                peer_review = "preprint"
            elif src.get("type") == "journal":
                peer_review = "peer-reviewed"

    source["peer_reviewed"] = peer_review

    if peer_review == "preprint" and (upgrade or require_peer_reviewed):
        pub_doi, how = find_published_version(requests, source, meta, mailto)
        if pub_doi:
            source["superseded_by"] = pub_doi

    # Retraction outranks everything else.
    if meta["retracted"]:
        source["verified"] = "fail"
        return {"key": key, "status": "FAIL",
                "reason": "RETRACTED or withdrawn: "
                          + ("; ".join(meta["notices"]) or "see publisher notice")}

    # Metadata consistency. A DOI that resolves elsewhere is a mashup signal.
    mismatches = []
    if not titles_match(source.get("title", ""), meta["title"]):
        mismatches.append(f"title differs from registry ('{meta['title']}')")
    logged_surname = first_author_surname(source.get("authors"))
    if logged_surname and meta["surname"] and logged_surname != meta["surname"]:
        mismatches.append(
            f"first author '{logged_surname}' != registry '{meta['surname']}'")

    if mismatches:
        if peer_review == "preprint":
            # Preprints get retitled between versions while the DOI stays put,
            # so a mismatch here is often version drift, not a wrong DOI.
            mismatches.append("this is a preprint, whose title may have changed "
                              "between versions")
        if source.get("superseded_by"):
            mismatches.append(f"a peer-reviewed version exists at "
                              f"{source['superseded_by']}; resolve against that")
        return {"key": key, "status": "WARN",
                "reason": "DOI resolves but " + "; ".join(mismatches)}

    # The log claiming peer review that the registry contradicts is its own bug.
    logged_type = source.get("type", "")
    if peer_review == "preprint" and logged_type in PEER_REVIEWED_LOG_TYPES:
        return {"key": key, "status": "WARN",
                "reason": f"log says type '{logged_type}' but the registry says "
                          f"this is a preprint; correct the log to 'preprint'"}

    if peer_review == "preprint" and source.get("superseded_by"):
        source["verified"] = "fail"
        return {"key": key, "status": "FAIL",
                "reason": f"preprint superseded by the peer-reviewed version "
                          f"{source['superseded_by']}; cite that instead and "
                          f"re-read the claim against it"}

    if peer_review in ("preprint", "not-peer-reviewed") and require_peer_reviewed:
        source["verified"] = "fail"
        return {"key": key, "status": "FAIL",
                "reason": f"not peer reviewed ({peer_review}) and "
                          f"--require-peer-reviewed is set"}

    if peer_review == "preprint":
        return {"key": key, "status": "WARN",
                "reason": "PREPRINT with no published version found; grade tier_3, "
                          "label it as unreviewed in the prose, and name it in "
                          "the limitations"}

    if meta["notices"]:
        return {"key": key, "status": "WARN",
                "reason": "has a correction or expression of concern: "
                          + "; ".join(meta["notices"])}

    if peer_review == "not-peer-reviewed":
        return {"key": key, "status": "WARN",
                "reason": f"record type '{meta['type']}' is not a peer-reviewed "
                          f"publication; confirm what you are citing"}

    return {"key": key, "status": "OK",
            "reason": f"resolved via {meta['registry']}; metadata matches; "
                      f"peer-reviewed"}


# ---------------------------------------------------------------------------
# self test
# ---------------------------------------------------------------------------

def self_test():
    """Check the offline logic against fixtures. No network required."""
    failures = 0

    def check(desc, ok):
        nonlocal failures
        failures += (not ok)
        print(f"  [{'pass' if ok else 'FAIL'}] {desc}")

    print("peer-review classifier reads the record, not the publisher")
    cases = [
        ("journal-article", "", "10.1109/TMI.2016.2528162", "peer-reviewed"),
        ("journal-article", "", "10.1016/j.media.2017.07.005", "peer-reviewed"),
        ("journal-article", "", "10.1038/s41586-021-03819-2", "peer-reviewed"),
        ("proceedings-article", "", "10.1145/3292500.3330701", "peer-reviewed"),
        ("posted-content", "preprint", "10.1101/2020.03.22.1", "preprint"),
        ("Preprint", "", "10.48550/arXiv.1706.03762", "preprint"),
        # An Elsevier prefix that is SSRN, and an IEEE prefix that is TechRxiv.
        ("journal-article", "", "10.2139/ssrn.1234567", "preprint"),
        ("journal-article", "", "10.36227/techrxiv.1234567", "preprint"),
        ("dataset", "", "10.5281/zenodo.1234567", "not-peer-reviewed"),
    ]
    for rtype, subtype, doi, expected in cases:
        got = classify_peer_review(rtype, subtype, doi)
        check(f"{doi} ({rtype}) -> {expected}", got == expected)

    print("\ntitle matching tolerates subtitles but not unrelated works")
    check("subtitle tolerated",
          titles_match("Attention is all you need",
                       "Attention Is All You Need: A Retrospective"))
    check("unrelated rejected",
          not titles_match("Deep learning for histopathology",
                           "A survey of medieval agriculture"))
    check("too-short titles rejected", not titles_match("AI", "AI"))

    print("\nstrict matching refuses a same-titled but different paper")
    # Regression: the lenient containment check promoted "Attention Is All You
    # Need" to a Briefings in Bioinformatics paper whose title begins with the
    # same phrase. That would have replaced a correct citation with a wrong one.
    check("containment would have accepted it",
          titles_match("Attention Is All You Need",
                       "Attention is all you need: utilizing attention in "
                       "AI-enabled drug discovery"))
    check("strict matching rejects it",
          not strict_title_match("Attention Is All You Need",
                                 "Attention is all you need: utilizing attention "
                                 "in AI-enabled drug discovery"))
    check("strict matching still accepts a real match",
          strict_title_match("Attention Is All You Need",
                             "Attention is all you need"))

    print("\nstructural validation")
    seen = set()
    check("missing fields caught",
          bool(validate_structure({"key": "a"}, seen)))
    check("duplicate key caught",
          any("duplicate" in p for p in validate_structure(
              {"key": "a", "type": "journal-article", "title": "T", "year": 2020},
              seen)))
    check("malformed DOI caught",
          any("malformed" in p for p in validate_structure(
              {"key": "b", "type": "journal-article", "title": "T", "year": 2020,
               "doi": "not-a-doi"}, set())))
    check("clean entry passes",
          not validate_structure(
              {"key": "c", "type": "journal-article", "title": "T", "year": 2020,
               "doi": "10.1136/bmj.n71"}, set()))

    print("\noffline preprint hints")
    seen2 = set()
    res = evaluate_source(
        {"key": "arx", "type": "preprint", "title": "Some preprint", "year": 2024,
         "doi": "10.48550/arXiv.2401.00001"}, None, True, seen2)
    check("arXiv prefix flagged offline",
          "arXiv" in res["reason"] and res["status"] == "SKIPPED")

    print(f"\n{'all checks passed' if not failures else str(failures) + ' check(s) FAILED'}")
    return 1 if failures else 0


# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Verify sources in a source log.")
    parser.add_argument("source_log", nargs="?",
                        help="Path to the source-log JSON file")
    parser.add_argument("--offline", action="store_true",
                        help="Skip all network calls; structural checks only")
    parser.add_argument("--mailto", default="",
                        help="Your email, for the Crossref and OpenAlex polite pools")
    parser.add_argument("--upgrade-preprints", action="store_true",
                        help="For each preprint, look up the peer-reviewed "
                             "version and record it as 'superseded_by'")
    parser.add_argument("--require-peer-reviewed", action="store_true",
                        help="FAIL any source that is not a peer-reviewed "
                             "publication")
    parser.add_argument("--self-test", action="store_true",
                        help="Check the checker's own logic against fixtures")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Emit a machine-readable JSON report")
    parser.add_argument("--write", action="store_true",
                        help="Write the updated statuses back to the source log")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.source_log:
        parser.error("source_log is required (or use --self-test)")

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
    results = [evaluate_source(s, requests, args.offline, seen_keys,
                               args.mailto, args.upgrade_preprints,
                               args.require_peer_reviewed)
               for s in sources]

    failures = [r for r in results if r["status"] == "FAIL"]
    preprints = [s for s in sources if s.get("peer_reviewed") == "preprint"]
    upgradable = [s for s in preprints if s.get("superseded_by")]

    if args.write:
        with open(args.source_log, "w", encoding="utf-8") as fh:
            json.dump(log, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

    if args.as_json:
        print(json.dumps({
            "source_log": args.source_log,
            "offline": args.offline or requests is None,
            "total": len(results),
            "failures": len(failures),
            "preprints": len(preprints),
            "upgradable_preprints": len(upgradable),
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
        if preprints:
            print(f"{len(preprints)} preprint(s); {len(upgradable)} have a "
                  f"peer-reviewed version recorded in 'superseded_by'")
        if not args.upgrade_preprints and preprints:
            print("Run again with --upgrade-preprints to look for published "
                  "versions of these.")
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
