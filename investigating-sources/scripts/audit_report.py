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
              f"phantom/unverified citations are resolved.")
        return 1
    if orphan or not has_limitations or not has_ai_note:
        print("RESULT: No hard failures, but warnings above should be resolved "
              "before delivery.")
        return 0
    print("RESULT: Clean. Citation integrity checks pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
