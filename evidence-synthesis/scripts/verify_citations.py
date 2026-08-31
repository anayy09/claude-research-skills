#!/usr/bin/env python3
"""Verify that cited works exist, match what was claimed, are peer reviewed, and
are not retracted.

This is the single most important script in this skill. Four distinct failure
modes are checked, because they need different evidence:

  Fabricated  - the work does not exist, or the DOI resolves to something else.
                Caught by metadata comparison against Crossref/DataCite/OpenAlex.
  Retracted   - the work exists but has been withdrawn. Caught only by checking
                retraction status; a DOI lookup that returns a record says
                nothing about whether that record is still valid.
  Superseded  - the citation points at a preprint that has since been published
                after peer review. The numbers in a preprint move during review,
                so citing it is citing the wrong version of the work.
  Unreviewed  - the work is a preprint or working paper with no published
                version. Legitimate to cite in some protocols, never legitimate
                to cite silently as though it were peer reviewed.

General-purpose language models are unreliable at all four. Crossref has
ingested the Retraction Watch database and exposes it through the `updated-by`
field on the retracted record; OpenAlex exposes the same signal as
`is_retracted`. This script queries both and reports disagreement rather than
silently picking one.

Peer-review status is read from the record, never inferred from the publisher.
Publisher name is not a peer-review signal: SSRN sits under Elsevier's DOI
prefix and TechRxiv under IEEE's, so a filter on publisher admits working papers
and rejects reviewed society journals. See references/peer-reviewed-sources.md.

Usage
-----
    # From a reference list (one reference per line, or a markdown list)
    python verify_citations.py --refs references.md --mailto you@uni.edu

    # Refuse to pass anything that is not peer reviewed
    python verify_citations.py --refs references.md --mailto you@uni.edu \\
        --require-peer-reviewed

    # Find the published version of every preprint in the list
    python verify_citations.py --refs references.md --mailto you@uni.edu \\
        --upgrade-preprints

    # From DOIs directly
    python verify_citations.py --doi 10.1136/bmj.n71 --doi 10.1136/bmj.q902 \\
        --mailto you@uni.edu

    # Structural check only, no network (parses and reports what it found)
    python verify_citations.py --refs references.md --offline

    # Verify the matching logic itself against built-in fixtures
    python verify_citations.py --self-test

Exit status is 1 if any reference fails and 2 if any could not be checked, so
this can gate a commit or a submission checklist.

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
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

CROSSREF = "https://api.crossref.org/works/"
CROSSREF_QUERY = "https://api.crossref.org/works"
OPENALEX = "https://api.openalex.org/works/doi:"
DATACITE = "https://api.datacite.org/dois/"
DOI_RA = "https://doi.org/ra/"
BIORXIV = "https://api.biorxiv.org/details/{server}/{doi}"

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.I)
YEAR_RE = re.compile(r"\((\d{4})[a-z]?\)|\b(19|20)\d{2}\b")

# Verdicts, ordered by severity.
OK, MINOR, FAIL, UNKNOWN = "VERIFIED", "CHECK", "FAIL", "UNCHECKED"

# Peer-review status, kept separate from the verdict so that "real but not
# reviewed" and "not real" never collapse into the same finding.
REVIEWED, PREPRINT, UNREVIEWED, STATUS_UNKNOWN = (
    "peer-reviewed", "preprint", "not-peer-reviewed", "unknown")

# Crossref record types that represent a peer-reviewed publication. Conference
# proceedings are included because in computer science and engineering the
# conference is the primary reviewed venue; the venue still has to be recorded,
# since elsewhere a "proceedings-article" can be an unreviewed abstract.
REVIEWED_TYPES = {"journal-article", "proceedings-article", "book-chapter",
                  "reference-entry", "monograph", "book", "edited-book",
                  "report-component"}
PREPRINT_TYPES = {"posted-content"}

# Offline hints only. The live checks above are authoritative; these exist so
# that --offline can still say something useful, and so an unreachable API does
# not leave a well-known preprint prefix silently unflagged.
PREPRINT_PREFIXES = {
    "10.48550": "arXiv",
    "10.1101": "bioRxiv/medRxiv",
    "10.21203": "Research Square",
    "10.2139": "SSRN",
    "10.31234": "PsyArXiv",
    "10.31235": "SocArXiv",
    "10.36227": "TechRxiv",
    "10.20944": "Preprints.org",
    "10.26434": "ChemRxiv",
    "10.31219": "OSF Preprints",
    "10.1590": "SciELO Preprints",
}


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
    record_type: Optional[str] = None
    registration_agency: Optional[str] = None
    peer_review: str = STATUS_UNKNOWN
    published_version_doi: Optional[str] = None
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


def doi_prefix(doi: str) -> str:
    return doi.split("/", 1)[0] if doi else ""


def parse_reference(line: str) -> Ref:
    """Pull DOI, title guess, year, and first-author surname out of a reference
    string. Deliberately tolerant: reference lists arrive in every style, and a
    parser that only handles APA would silently skip most of them."""
    raw = line.strip().lstrip("-*0123456789. )").strip()
    r = Ref(raw=raw)

    m = DOI_RE.search(raw)
    if m:
        r.doi = m.group(0).rstrip(".,;)")

    # arXiv IDs are frequently cited without a DOI at all. Reconstruct the
    # registered DOI so the reference can be checked rather than skipped.
    if not r.doi:
        am = re.search(r"arXiv[:\s]\s*(\d{4}\.\d{4,5})(v\d+)?", raw, re.I)
        if am:
            r.doi = f"10.48550/arXiv.{am.group(1)}"

    ym = YEAR_RE.search(raw)
    if ym:
        r.claimed_year = int(ym.group(1) or ym.group(0))

    am2 = re.match(r"([A-Z][A-Za-z'À-ɏ-]+)\s*,", raw)
    if am2:
        r.claimed_author = am2.group(1)

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
        # A BibTeX @misc with an eprint field is an uncited preprint in disguise.
        if not r.doi and fld("eprint"):
            eprint = fld("eprint") or ""
            if re.match(r"^\d{4}\.\d{4,5}", eprint):
                r.doi = f"10.48550/arXiv.{eprint.split('v')[0]}"
        out.append(r)
    return out


# --------------------------------------------------------------------------
# network
# --------------------------------------------------------------------------

def fetch_json(url: str, timeout: int = 20, retries: int = 2,
               backoff: float = 1.5) -> Tuple[Optional[Any], Optional[str]]:
    """Returns (data, error). error is None, 'notfound' (the server answered and
    said no such record), or 'network' (we never got a usable answer).

    The distinction is the whole point: an unreachable API must never be
    reported as a nonexistent paper. Conflating the two would turn a firewall
    into an accusation of fabrication.

    Transient failures are retried, because a single timeout in a run of eighty
    references otherwise produces an UNCHECKED that looks like a finding. A 404
    is never retried: the server already answered.
    """
    req = urllib.request.Request(url, headers={
        "User-Agent": "evidence-synthesis-skill/1.1 (citation verification)",
        "Accept": "application/json",
    })
    delay = backoff
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return None, "notfound"
            # 429 and 5xx are worth another try; anything else is not.
            if e.code not in (429, 500, 502, 503, 504) or attempt == retries:
                return None, "network"
        except Exception:
            if attempt == retries:
                return None, "network"
        time.sleep(delay)
        delay *= 2
    return None, "network"


def crossref_by_doi(doi: str, mailto: str):
    url = CROSSREF + urllib.parse.quote(doi, safe="") + f"?mailto={mailto}"
    data, err = fetch_json(url)
    return (data.get("message") if data else None), err


def crossref_by_title(title: str, mailto: str, peer_reviewed_only: bool = False):
    params = {"query.bibliographic": title[:300], "rows": 3, "mailto": mailto}
    if peer_reviewed_only:
        params["filter"] = "type:journal-article"
    data, err = fetch_json(f"{CROSSREF_QUERY}?{urllib.parse.urlencode(params)}")
    items = (data or {}).get("message", {}).get("items", [])
    return (items[0] if items else None), err


def openalex_by_doi(doi: str, mailto: str):
    return fetch_json(OPENALEX + urllib.parse.quote(doi, safe="") + f"?mailto={mailto}")


def datacite_by_doi(doi: str):
    """arXiv registers its DOIs with DataCite, not Crossref. Without this
    fallback every arXiv citation in a reference list is reported as a
    fabrication, which is a false accusation on a real object."""
    data, err = fetch_json(DATACITE + urllib.parse.quote(doi, safe=""))
    return ((data or {}).get("data", {}).get("attributes") if data else None), err


def registration_agency(doi: str) -> Optional[str]:
    data, _err = fetch_json(DOI_RA + urllib.parse.quote(doi_prefix(doi), safe=""))
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return data[0].get("RA")
    return None


def biorxiv_published(doi: str) -> Optional[str]:
    """bioRxiv and medRxiv expose the journal DOI of the published version once
    it exists. Crossref's is-preprint-of relation is deposited by the publisher
    and sometimes lags, so this is checked as a second opinion."""
    for server in ("biorxiv", "medrxiv"):
        data, _err = fetch_json(BIORXIV.format(server=server, doi=doi))
        coll = (data or {}).get("collection") or []
        if coll:
            pub = (coll[-1] or {}).get("published", "")
            if pub and pub.upper() != "NA":
                return pub
    return None


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
    relation = msg.get("relation") or {}
    for rel_name, rels in relation.items():
        if "retract" in rel_name.lower() or "withdraw" in rel_name.lower():
            for rel in rels:
                notices.append(f"relation:{rel_name} -> {rel.get('id', '?')}")

    retracted = any("retract" in n.lower() or "withdraw" in n.lower() for n in notices)

    # A preprint deposit names the published article through is-preprint-of.
    published = None
    for rel in relation.get("is-preprint-of") or []:
        if rel.get("id-type") == "doi" and rel.get("id"):
            published = rel["id"]
            break

    # Institution is how the preprint servers identify themselves on the record.
    institution = ""
    inst = msg.get("institution") or []
    if isinstance(inst, list) and inst:
        institution = (inst[0] or {}).get("name", "")
    elif isinstance(inst, dict):
        institution = inst.get("name", "")

    return {"title": title, "year": year, "authors": authors, "journal": journal,
            "notices": notices, "retracted": retracted, "published": published,
            "type": msg.get("type", ""), "subtype": msg.get("subtype", ""),
            "doi": msg.get("DOI", ""), "institution": institution,
            "publisher": msg.get("publisher", "")}


def classify_peer_review(record_type: str, subtype: str, doi: str,
                         journal: str) -> str:
    """Peer-review status from the record itself. Publisher is deliberately not
    consulted: SSRN is Elsevier and TechRxiv is IEEE."""
    if record_type in PREPRINT_TYPES or subtype == "preprint":
        return PREPRINT
    if doi and doi_prefix(doi) in PREPRINT_PREFIXES:
        # A preprint prefix with a non-preprint record type is unusual enough to
        # warrant the conservative reading rather than the flattering one.
        return PREPRINT
    if record_type in REVIEWED_TYPES:
        return REVIEWED
    if record_type in ("dataset", "component", "peer-review", "grant", "other"):
        return UNREVIEWED
    return STATUS_UNKNOWN


def find_published_version(r: Ref, mailto: str) -> Optional[str]:
    """Second and third opinions on the published version, used when Crossref's
    is-preprint-of relation is absent."""
    if r.published_version_doi:
        return r.published_version_doi
    if r.doi and doi_prefix(r.doi) == "10.1101":
        pub = biorxiv_published(r.doi)
        if pub:
            r.notes.append("published version found via the bioRxiv/medRxiv API")
            return pub
    if r.doi:
        oa, _err = openalex_by_doi(r.doi, mailto)
        for loc in (oa or {}).get("locations") or []:
            src = loc.get("source") or {}
            if src.get("type") == "journal" and loc.get("version") == "publishedVersion":
                cand = (oa or {}).get("doi") or ""
                cand = cand.replace("https://doi.org/", "")
                if cand and cand.lower() != r.doi.lower():
                    r.notes.append(f"OpenAlex lists a published journal version "
                                   f"in {src.get('display_name', '?')}")
                    return cand
    return None


def evaluate(r: Ref, mailto: str, require_peer_reviewed: bool = False,
             upgrade: bool = False) -> Ref:
    msg, err = None, None
    if r.doi:
        msg, err = crossref_by_doi(r.doi, mailto)
        if msg is None and err == "notfound":
            # Not a fabrication yet: the DOI may simply be registered elsewhere.
            attrs, dc_err = datacite_by_doi(r.doi)
            if attrs is not None:
                return evaluate_datacite(r, attrs, mailto, require_peer_reviewed,
                                         upgrade)
            if dc_err == "network":
                r.verdict = UNKNOWN
                r.notes.append("Crossref has no such DOI and DataCite could not "
                               "be reached; this reference was NOT checked")
                return r
            r.notes.append("DOI did not resolve in Crossref or DataCite")

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
    r.found_journal = info["journal"] or info["institution"] or info["publisher"]
    r.found_authors = info["authors"][:5]
    r.update_notices = info["notices"]
    r.retracted = info["retracted"]
    r.record_type = info["type"]
    r.registration_agency = "Crossref"
    r.published_version_doi = info["published"]
    if not r.doi and info["doi"]:
        r.doi = info["doi"]

    r.peer_review = classify_peer_review(info["type"], info["subtype"],
                                         r.doi or "", info["journal"])

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
            # OpenAlex sees repository deposits that Crossref types as articles.
            primary = oa.get("primary_location") or {}
            src = primary.get("source") or {}
            if r.peer_review == STATUS_UNKNOWN:
                if oa.get("type") == "preprint" or src.get("type") == "repository":
                    r.peer_review = PREPRINT
                elif src.get("type") == "journal":
                    r.peer_review = REVIEWED
            if src.get("display_name") and not r.found_journal:
                r.found_journal = src["display_name"]

    if r.peer_review == PREPRINT and (upgrade or require_peer_reviewed):
        r.published_version_doi = find_published_version(r, mailto)

    if r.claimed_title and r.found_title:
        r.title_similarity = round(difflib.SequenceMatcher(
            None, normalize_title(r.claimed_title),
            normalize_title(r.found_title)).ratio(), 3)

    return assign_verdict(r, require_peer_reviewed)


def evaluate_datacite(r: Ref, attrs: Dict[str, Any], mailto: str,
                      require_peer_reviewed: bool, upgrade: bool) -> Ref:
    """DataCite path, reached mainly by arXiv DOIs."""
    titles = attrs.get("titles") or []
    r.found_title = (titles[0] or {}).get("title", "") if titles else ""
    r.found_year = attrs.get("publicationYear")
    r.found_journal = attrs.get("publisher") or ""
    if isinstance(r.found_journal, dict):          # DataCite v4 publisher object
        r.found_journal = r.found_journal.get("name", "")
    r.found_authors = [c.get("familyName") or c.get("name", "")
                       for c in (attrs.get("creators") or [])][:5]
    r.registration_agency = "DataCite"
    types = attrs.get("types") or {}
    r.record_type = types.get("resourceTypeGeneral", "")
    r.peer_review = (PREPRINT if r.record_type == "Preprint"
                     or doi_prefix(r.doi or "") in PREPRINT_PREFIXES
                     else STATUS_UNKNOWN)
    r.notes.append(f"registered with DataCite, not Crossref "
                   f"(resourceTypeGeneral: {r.record_type or 'unstated'})")

    # DataCite records point at the published article through relatedIdentifiers.
    for rel in attrs.get("relatedIdentifiers") or []:
        if (rel.get("relationType") in ("IsPreviousVersionOf", "IsSupplementTo",
                                        "IsIdenticalTo", "IsPublishedIn")
                and rel.get("relatedIdentifierType") == "DOI"):
            r.published_version_doi = rel.get("relatedIdentifier")
            break

    if r.peer_review == PREPRINT and (upgrade or require_peer_reviewed) \
            and not r.published_version_doi and r.found_title:
        item, _err = crossref_by_title(r.found_title, mailto, peer_reviewed_only=True)
        if item:
            cand = extract_crossref(item)
            sim = difflib.SequenceMatcher(
                None, normalize_title(r.found_title),
                normalize_title(cand["title"])).ratio()
            if sim >= 0.90:
                r.published_version_doi = cand["doi"]
                r.notes.append(f"a peer-reviewed version appears to exist in "
                               f"{cand['journal'] or 'a journal'}; confirm the "
                               f"authors match before swapping the citation")

    if r.claimed_title and r.found_title:
        r.title_similarity = round(difflib.SequenceMatcher(
            None, normalize_title(r.claimed_title),
            normalize_title(r.found_title)).ratio(), 3)
    return assign_verdict(r, require_peer_reviewed)


def assign_verdict(r: Ref, require_peer_reviewed: bool = False) -> Ref:
    """Severity ladder. A retraction outranks everything: a correctly cited
    retracted paper is still a problem, and citing one without acknowledging the
    retraction is the error this catches. Citing a superseded preprint ranks
    next, because the reader is being pointed at numbers that changed."""
    if r.retracted:
        r.verdict = FAIL
        r.notes.append("RETRACTED or withdrawn. Remove it, or cite it explicitly "
                       "as retracted and explain why it still belongs.")
        return r

    if r.title_similarity is not None and r.title_similarity < 0.55:
        r.verdict = FAIL
        r.notes.append(f"title mismatch (similarity {r.title_similarity}): the DOI "
                       f"resolves to a different work than the one cited")
        if r.peer_review == PREPRINT:
            # Preprints get retitled between versions and the DOI stays put, so
            # a mismatch here is often version drift rather than a wrong DOI.
            r.notes.append("this is a preprint, whose title may have changed "
                           "between versions; check the version you actually read")
        if r.published_version_doi:
            r.notes.append(f"a peer-reviewed version exists at "
                           f"{r.published_version_doi}; resolve the citation "
                           f"against that record")
        return r

    if r.peer_review == PREPRINT and r.published_version_doi:
        r.verdict = FAIL
        r.notes.append(f"preprint superseded by a peer-reviewed version: cite "
                       f"{r.published_version_doi} and re-extract the data from "
                       f"it, because numbers move during review")
        return r

    if r.peer_review in (PREPRINT, UNREVIEWED) and require_peer_reviewed:
        r.verdict = FAIL
        r.notes.append("not peer reviewed, and --require-peer-reviewed is set. "
                       "Find the version of record, or drop it, or record the "
                       "protocol decision that makes preprints eligible.")
        return r

    if r.peer_review == PREPRINT:
        r.verdict = MINOR
        r.notes.append("PREPRINT, no published version found. Citable only if the "
                       "protocol says preprints are eligible; label it as a "
                       "preprint, record the version, and re-check before "
                       "submission.")
    elif r.peer_review == UNREVIEWED:
        r.verdict = r.verdict or MINOR
        r.notes.append(f"record type '{r.record_type}' is not a peer-reviewed "
                       f"publication; confirm what you are actually citing")

    if r.update_notices:
        r.verdict = r.verdict or MINOR
        r.notes.append("has a correction or expression of concern; check whether "
                       "it affects the claim you are citing it for")

    if r.title_similarity is not None and r.title_similarity < 0.80:
        r.verdict = r.verdict or MINOR
        r.notes.append(f"title only partially matches (similarity "
                       f"{r.title_similarity})")

    if r.claimed_year and r.found_year and abs(r.claimed_year - int(r.found_year)) > 1:
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
    # (description, Ref kwargs, require_peer_reviewed, expected verdict)
    ("clean match", dict(
        claimed_title="The PRISMA 2020 statement: an updated guideline for reporting systematic reviews",
        found_title="The PRISMA 2020 statement: an updated guideline for reporting systematic reviews",
        claimed_year=2021, found_year=2021, claimed_author="Page",
        found_authors=["Page", "McKenzie"], retracted=False,
        peer_review=REVIEWED), False, OK),
    ("retracted outranks a clean match", dict(
        claimed_title="Some study", found_title="Some study",
        claimed_year=2020, found_year=2020, retracted=True,
        peer_review=REVIEWED,
        update_notices=["retraction (retraction-watch) -> 10.1000/x"]), False, FAIL),
    ("DOI resolves to a different paper", dict(
        claimed_title="Deep learning for colorectal histopathology triage",
        found_title="A survey of medieval agricultural practice",
        claimed_year=2023, found_year=2023, retracted=False,
        peer_review=REVIEWED), False, FAIL),
    ("preprint with a published version is a FAIL", dict(
        claimed_title="Mechanistic statistical SIR modelling",
        found_title="Mechanistic statistical SIR modelling",
        claimed_year=2020, found_year=2020, retracted=False,
        peer_review=PREPRINT, published_version_doi="10.3390/biology9050097"),
     False, FAIL),
    ("preprint with no published version is a CHECK by default", dict(
        claimed_title="An unpublished but real preprint",
        found_title="An unpublished but real preprint",
        claimed_year=2025, found_year=2025, retracted=False,
        peer_review=PREPRINT), False, MINOR),
    ("the same preprint FAILs under --require-peer-reviewed", dict(
        claimed_title="An unpublished but real preprint",
        found_title="An unpublished but real preprint",
        claimed_year=2025, found_year=2025, retracted=False,
        peer_review=PREPRINT), True, FAIL),
    ("a peer-reviewed article passes --require-peer-reviewed", dict(
        claimed_title="Identical title here for the test",
        found_title="Identical title here for the test",
        claimed_year=2021, found_year=2021, retracted=False,
        peer_review=REVIEWED), True, OK),
    ("a dataset is not a peer-reviewed publication", dict(
        claimed_title="Identical title here for the test",
        found_title="Identical title here for the test",
        claimed_year=2021, found_year=2021, retracted=False,
        record_type="dataset", peer_review=UNREVIEWED), False, MINOR),
    ("year off by three", dict(
        claimed_title="Identical title here for the test",
        found_title="Identical title here for the test",
        claimed_year=2018, found_year=2021, retracted=False,
        peer_review=REVIEWED), False, MINOR),
    ("author not on the paper", dict(
        claimed_title="Identical title here for the test",
        found_title="Identical title here for the test",
        claimed_year=2021, found_year=2021, claimed_author="Nobody",
        found_authors=["Page", "McKenzie"], retracted=False,
        peer_review=REVIEWED), False, MINOR),
    ("correction notice", dict(
        claimed_title="Identical title here for the test",
        found_title="Identical title here for the test",
        claimed_year=2021, found_year=2021, retracted=False,
        peer_review=REVIEWED,
        update_notices=["correction (publisher) -> 10.1000/y"]), False, MINOR),
]

CLASSIFIER_FIXTURES = [
    # (record_type, subtype, doi, expected status)
    ("journal-article", "", "10.1109/TMI.2016.2528162", REVIEWED),
    ("journal-article", "", "10.1016/j.media.2017.07.005", REVIEWED),
    ("journal-article", "", "10.1038/s41586-021-03819-2", REVIEWED),
    ("proceedings-article", "", "10.1145/3292500.3330701", REVIEWED),
    ("posted-content", "preprint", "10.1101/2020.03.22.20040915", PREPRINT),
    # An Elsevier prefix that is SSRN, and an IEEE prefix that is TechRxiv:
    # the reason publisher name is never used as the signal.
    ("journal-article", "", "10.2139/ssrn.1234567", PREPRINT),
    ("journal-article", "", "10.36227/techrxiv.1234567", PREPRINT),
    ("dataset", "", "10.5281/zenodo.1234567", UNREVIEWED),
]


def self_test() -> int:
    failures = 0
    print("verdict ladder")
    for desc, kw, require, expected in FIXTURES:
        r = Ref(raw=desc, **kw)
        if r.claimed_title and r.found_title:
            r.title_similarity = round(difflib.SequenceMatcher(
                None, normalize_title(r.claimed_title),
                normalize_title(r.found_title)).ratio(), 3)
        got = assign_verdict(r, require).verdict
        ok = got == expected
        failures += (not ok)
        print(f"  [{'pass' if ok else 'FAIL'}] {desc}: expected {expected}, got {got}")

    print("\npeer-review classifier")
    for rtype, subtype, doi, expected in CLASSIFIER_FIXTURES:
        got = classify_peer_review(rtype, subtype, doi, "")
        ok = got == expected
        failures += (not ok)
        print(f"  [{'pass' if ok else 'FAIL'}] {doi} ({rtype}): "
              f"expected {expected}, got {got}")

    print("\nreference parser")
    parser_cases = [
        ("Vaswani, A. et al. (2017). Attention is all you need. arXiv:1706.03762.",
         "10.48550/arXiv.1706.03762"),
        ("Page, M. J. et al. (2021). The PRISMA 2020 statement. BMJ, 372, n71. "
         "https://doi.org/10.1136/bmj.n71", "10.1136/bmj.n71"),
    ]
    for line, expected_doi in parser_cases:
        got = parse_reference(line).doi
        ok = got == expected_doi
        failures += (not ok)
        print(f"  [{'pass' if ok else 'FAIL'}] {line[:44]}...: "
              f"expected {expected_doi}, got {got}")

    total = len(FIXTURES) + len(CLASSIFIER_FIXTURES) + len(parser_cases)
    print(f"\n{total - failures}/{total} checks passed")
    return 1 if failures else 0


# --------------------------------------------------------------------------

def report(refs: List[Ref], as_json: bool) -> int:
    if as_json:
        print(json.dumps([asdict(r) for r in refs], indent=2))
    else:
        counts: Dict[str, int] = {OK: 0, MINOR: 0, FAIL: 0, UNKNOWN: 0}
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
            if r.peer_review != STATUS_UNKNOWN:
                label = r.peer_review
                if r.record_type:
                    label += f" ({r.record_type})"
                print(f"     status: {label}")
            if r.published_version_doi:
                print(f"     cite  : {r.published_version_doi}   <- version of record")
            for n in r.update_notices:
                print(f"     notice: {n}")
            for n in r.notes:
                print(f"     note  : {n}")

        preprints = [r for r in refs if r.peer_review == PREPRINT]
        print("\n" + "-" * 70)
        print(f"{counts.get(OK,0)} verified, {counts.get(MINOR,0)} to check, "
              f"{counts.get(FAIL,0)} failed, {counts.get(UNKNOWN,0)} unchecked, "
              f"{len(refs)} total")
        if preprints:
            upgradable = [r for r in preprints if r.published_version_doi]
            print(f"{len(preprints)} preprint(s); {len(upgradable)} have a "
                  f"peer-reviewed version to cite instead")
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


def offline_report(refs: List[Ref]) -> int:
    print(f"parsed {len(refs)} references (offline; nothing verified)\n")
    hinted = 0
    for i, r in enumerate(refs, 1):
        hint = PREPRINT_PREFIXES.get(doi_prefix(r.doi or ""), "")
        if hint:
            hinted += 1
        print(f"[{i}] doi={r.doi or '-'}  year={r.claimed_year or '-'}  "
              f"author={r.claimed_author or '-'}"
              + (f"  [{hint} preprint prefix]" if hint else ""))
        print(f"     title guess: {(r.claimed_title or '?')[:80]}")
    if hinted:
        print(f"\n{hinted} reference(s) carry a known preprint DOI prefix. That is "
              f"a hint, not a verdict: run online to find whether a peer-reviewed "
              f"version exists.")
    print("\nRun without --offline and with --mailto to check existence, "
          "metadata match, peer-review status, and retraction status.")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--refs", help="file with one reference per line, or a .bib")
    p.add_argument("--doi", action="append", default=[], help="repeatable")
    p.add_argument("--mailto", default="", help="your email, for the Crossref polite pool")
    p.add_argument("--offline", action="store_true",
                   help="parse only, no network; shows what would be checked")
    p.add_argument("--require-peer-reviewed", action="store_true",
                   help="fail any reference that is not a peer-reviewed publication")
    p.add_argument("--upgrade-preprints", action="store_true",
                   help="for every preprint, look up the published version and "
                        "print the DOI to cite instead")
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
        return offline_report(refs)

    if not a.mailto:
        sys.exit("--mailto is required for network use (Crossref polite pool)")

    for i, r in enumerate(refs):
        evaluate(r, a.mailto, a.require_peer_reviewed, a.upgrade_preprints)
        if i < len(refs) - 1:
            time.sleep(a.delay)

    return report(refs, a.json)


if __name__ == "__main__":
    raise SystemExit(main())
