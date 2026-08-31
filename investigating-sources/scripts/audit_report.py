#!/usr/bin/env python3
"""
audit_report.py - Cross-check a finished draft against its source log.

Confirms citation integrity between a written deliverable (markdown) and the
source log it was built from:

  * Phantom citations - a [key] marker in the draft with no matching source.
    These are the fabrication signature: a citation to something that was never
    logged or verified. Any phantom is a hard failure.
  * Orphan sources     - a logged source that is never cited. Usually dead
    weight or a sign a claim was dropped without dropping its source. A warning.
  * Unverified sources - a cited source whose log status is not 'confirmed'.
    Citing a source that failed or was never confirmed is a hard failure.
  * Superseded preprints - a cited preprint whose peer-reviewed version exists
    (the log's 'superseded_by' field). Citing the preprint reports numbers the
    authors revised during review. A hard failure.
  * Unlabelled preprints - a cited preprint that the prose never identifies as
    unreviewed. The reader must not have to check the DOI to learn that the
    evidence has not been peer reviewed. A warning, because the label may be
    phrased in a way this check does not recognise.
  * Structural checks  - the deliverable must contain a limitations section and
    an AI-assistance note.

This script is fully offline; it needs no network.

Usage:
    python audit_report.py draft.md sources.json

Exit codes:
    0  no hard failures (delivery may proceed)
    1  at least one hard failure (phantom or unverified citation)
    2  an input file could not be read or parsed
"""

import argparse
import json
import re
import sys

# Inline citations use square-bracket keys: [smith2021] or grouped [a; b; c].
# Keys are the kebab/alphanumeric handles defined in the source log. The pattern
# deliberately ignores markdown links [text](url) by requiring the bracket
# contents to look like citation keys, not arbitrary prose.
CITATION_BLOCK = re.compile(r"\[([^\[\]]+?)\]")
KEY_TOKEN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*\d*[A-Za-z0-9_-]*$")

# A markdown link is [text](url); its bracket group is followed immediately by
# "(". We strip these before scanning so link text is never read as a citation.
MARKDOWN_LINK = re.compile(r"\[[^\[\]]*\]\([^)]*\)")

# Words that count as telling the reader a source has not been peer reviewed.
# Checked in the paragraph containing the citation, not document-wide and not in
# a fixed character window. A fixed window leaks across short markdown
# paragraphs, so labelling one preprint would silently excuse the next one.
PREPRINT_LABELS = ("preprint", "pre-print", "not peer reviewed",
                   "not peer-reviewed", "unreviewed", "not yet peer reviewed",
                   "not yet peer-reviewed", "awaiting peer review")

# Section-presence checks are lenient: match the concept, not one exact heading.
LIMITATIONS_HINTS = ("limitation", "caveat", "scope and limits", "what this does not")
AI_NOTE_HINTS = ("ai-assisted", "ai assisted", "ai-assistance", "assisted research tools",
                 "assisted by claude", "generative ai", "verified against")


def extract_citation_keys(text):
    """Return the set of citation keys referenced in the draft."""
    # Remove markdown links first so their bracket text is not misread.
    cleaned = MARKDOWN_LINK.sub(" ", text)
    keys = set()
    for block in CITATION_BLOCK.findall(cleaned):
        # A block may group several keys separated by ; or ,
        for token in re.split(r"[;,]", block):
            token = token.strip()
            if token and KEY_TOKEN.match(token):
                keys.add(token)
    return keys


def is_preprint(source):
    """True if either the log's type or the checker's peer_reviewed field says so."""
    return (source.get("type") == "preprint"
            or source.get("peer_reviewed") == "preprint")


def preprint_labelled(text, key):
    """True if every paragraph citing `key` also says the source is unreviewed.

    Every, not any: a preprint labelled in one paragraph and cited bare in
    another leaves the second reader misinformed, which is the case this exists
    to catch.
    """
    low_key = key.lower()
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    citing = []
    for para in paragraphs:
        low = para.lower()
        # Match the key inside a bracket group, so [a; bare2025] counts too.
        for block in CITATION_BLOCK.findall(low):
            if low_key in [t.strip() for t in re.split(r"[;,]", block)]:
                citing.append(low)
                break
    if not citing:
        # Cited somewhere this paragraph scan did not reach (a table row, a
        # figure caption). Fall back to the document-wide check rather than
        # reporting a label that may well be there.
        return any(lab in text.lower() for lab in PREPRINT_LABELS)
    return all(any(lab in para for lab in PREPRINT_LABELS) for para in citing)


def section_present(text, hints):
    """True if any hint phrase appears in the draft (case-insensitive)."""
    low = text.lower()
    return any(hint in low for hint in hints)


def main():
    parser = argparse.ArgumentParser(
        description="Audit a draft against its source log.")
    parser.add_argument("draft", help="Path to the finished draft (markdown)")
    parser.add_argument("source_log", help="Path to the source-log JSON file")
    args = parser.parse_args()

    try:
        with open(args.draft, encoding="utf-8") as fh:
            draft = fh.read()
    except FileNotFoundError:
        print(f"error: draft not found: {args.draft}", file=sys.stderr)
        return 2

    try:
        with open(args.source_log, encoding="utf-8") as fh:
            log = json.load(fh)
    except FileNotFoundError:
        print(f"error: source log not found: {args.source_log}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {args.source_log}: {exc}", file=sys.stderr)
        return 2

    sources = {s.get("key"): s for s in log.get("sources", []) if s.get("key")}
    cited_keys = extract_citation_keys(draft)

    phantom = sorted(k for k in cited_keys if k not in sources)
    orphan = sorted(k for k in sources if k not in cited_keys)
    unverified = sorted(
        k for k in cited_keys
        if k in sources and sources[k].get("verified") != "confirmed"
    )
    superseded = sorted(
        k for k in cited_keys
        if k in sources and sources[k].get("superseded_by")
    )
    cited_preprints = [k for k in cited_keys
                       if k in sources and is_preprint(sources[k])]
    unlabelled_preprints = sorted(
        k for k in cited_preprints if not preprint_labelled(draft, k)
    )

    has_limitations = section_present(draft, LIMITATIONS_HINTS)
    has_ai_note = section_present(draft, AI_NOTE_HINTS)

    hard_failures = 0

    print("Citation audit")
    print("=" * 60)
    print(f"Draft:      {args.draft}")
    print(f"Source log: {args.source_log}")
    print(f"Sources logged: {len(sources)}   Citations in draft: {len(cited_keys)}")
    print()

    if phantom:
        hard_failures += len(phantom)
        print(f"FAIL  Phantom citations ({len(phantom)}): cited but not in log")
        for k in phantom:
            print(f"        [{k}]  -> add & verify this source, or remove the claim")
    else:
        print("OK    No phantom citations")

    if unverified:
        hard_failures += len(unverified)
        print(f"FAIL  Unverified citations ({len(unverified)}): cited but "
              f"status != confirmed")
        for k in unverified:
            state = sources[k].get("verified", "pending")
            print(f"        [{k}]  status='{state}' -> verify or remove")
    else:
        print("OK    Every cited source is confirmed")

    if superseded:
        hard_failures += len(superseded)
        print(f"FAIL  Superseded preprints ({len(superseded)}): a peer-reviewed "
              f"version exists")
        for k in superseded:
            print(f"        [{k}]  -> cite {sources[k]['superseded_by']} and "
                  f"re-read the claim against it")
    elif cited_preprints:
        print("OK    No cited preprint has a published version")

    if unlabelled_preprints:
        print(f"WARN  Unlabelled preprints ({len(unlabelled_preprints)}): cited "
              f"without telling the reader they are unreviewed")
        for k in unlabelled_preprints:
            print(f"        [{k}]  -> say 'in a preprint that has not been peer "
                  f"reviewed, ...' where it is cited")
    elif cited_preprints:
        print(f"OK    All {len(cited_preprints)} cited preprint(s) labelled as "
              f"unreviewed")

    if orphan:
        print(f"WARN  Orphan sources ({len(orphan)}): logged but never cited")
        for k in orphan:
            print(f"        [{k}]  -> cite it or drop it from the log")
    else:
        print("OK    No orphan sources")

    print("OK    Limitations section present" if has_limitations
          else "WARN  No limitations section found -> add one before delivery")
    print("OK    AI-assistance note present" if has_ai_note
          else "WARN  No AI-assistance note found -> add one before delivery")

    print()
    if hard_failures:
        print(f"RESULT: {hard_failures} hard failure(s). Do not deliver until "
              f"phantom, unverified, and superseded citations are resolved.")
        return 1
    if orphan or unlabelled_preprints or not has_limitations or not has_ai_note:
        print("RESULT: No hard failures, but warnings above should be resolved "
              "before delivery.")
        return 0
    print("RESULT: Clean. Citation integrity checks pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
