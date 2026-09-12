#!/usr/bin/env python3
"""
doi_writeback.py - Put a minted DOI into every place that was waiting for it,
and report every site so nothing is left as a placeholder.

Replaces, in the files given:
    10.5281/zenodo.XXXXXXX   10.5281/zenodo.NNNNNNN   [DOI PENDING]   [ZENODO DOI]
    DOI: TBD                 https://doi.org/10.5281/zenodo.XXXXXXX

with the DOI (or its https://doi.org/ URL where the placeholder was a URL).

--check lists the remaining placeholders without writing. --version-doi also
replaces [VERSION DOI] with the version DOI, keeping the concept DOI for the
availability statement, which is the one a manuscript cites.

Usage:
    python doi_writeback.py --doi 10.5281/zenodo.1234567 paper/main.tex CITATION.cff letter/response.md
    python doi_writeback.py --doi 10.5281/zenodo.1234567 --version-doi 10.5281/zenodo.1234568 paper/*.md
    python doi_writeback.py --check paper/main.tex CITATION.cff
    python doi_writeback.py --self-test

Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

PLACEHOLDERS = [r"https?://doi\.org/10\.5281/zenodo\.[XN]{5,}", r"10\.5281/zenodo\.[XN]{5,}", r"\[DOI PENDING\]", r"\[ZENODO DOI\]", r"\[CONCEPT DOI\]", r"DOI:\s*TBD"]
VERSION_PH = [r"\[VERSION DOI\]"]


def writeback(text: str, doi: str, version_doi: str = "") -> Tuple[str, List[str]]:
    sites: List[str] = []

    def rep_url(m: "re.Match[str]") -> str:
        sites.append(m.group(0))
        return f"https://doi.org/{doi}"

    def rep(m: "re.Match[str]") -> str:
        sites.append(m.group(0))
        return doi

    text = re.sub(PLACEHOLDERS[0], rep_url, text)
    for pat in PLACEHOLDERS[1:]:
        text = re.sub(pat, rep, text)
    if version_doi:
        for pat in VERSION_PH:
            text = re.sub(pat, lambda m: (sites.append(m.group(0)), version_doi)[1], text)
    return text, sites


def remaining(text: str) -> List[str]:
    out = []
    for pat in PLACEHOLDERS + VERSION_PH + [r"\[AUTHOR (?:INPUT|ACTION)[^\]]*\]"]:
        out += re.findall(pat, text)
    return out


def self_test() -> int:
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    src = "Code is archived at https://doi.org/10.5281/zenodo.XXXXXXX (concept) and this version at [VERSION DOI]. cff: doi: 10.5281/zenodo.NNNNNNN. Also [DOI PENDING]."
    out, sites = writeback(src, "10.5281/zenodo.1", "10.5281/zenodo.2")
    check("url placeholder became a url", "https://doi.org/10.5281/zenodo.1 (concept)" in out)
    check("bare and bracket placeholders replaced", "doi: 10.5281/zenodo.1." in out and "Also 10.5281/zenodo.1." in out)
    check("version placeholder replaced separately", "this version at 10.5281/zenodo.2" in out)
    check("four sites reported", len(sites) == 4)
    check("nothing remains", remaining(out) == [])
    check("author input counts as remaining", remaining("x [AUTHOR INPUT: y]") == ["[AUTHOR INPUT: y]"])
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("files", nargs="*")
    p.add_argument("--doi", help="the concept DOI (what the manuscript cites)")
    p.add_argument("--version-doi", default="")
    p.add_argument("--check", action="store_true", help="list remaining placeholders; write nothing")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.files:
        p.error("give the files to update (or --self-test)")
    if not a.check and not a.doi:
        p.error("--doi is required unless --check")
    if a.doi and not re.match(r"^10\.\d{4,9}/\S+$", a.doi):
        print(f"error: {a.doi} is not a DOI", file=sys.stderr)
        return 2
    total_sites = 0
    left = 0
    for f in a.files:
        path = Path(f)
        if not path.exists():
            print(f"error: {f} not found", file=sys.stderr)
            return 2
        text = path.read_text(encoding="utf-8", errors="replace")
        if a.check:
            r = remaining(text)
            left += len(r)
            if r:
                print(f"{f}: " + ", ".join(sorted(set(r))))
            continue
        new, sites = writeback(text, a.doi, a.version_doi)
        if sites:
            path.write_text(new, encoding="utf-8", newline="\n" if "\r\n" not in text else "\r\n")
            total_sites += len(sites)
            print(f"{f}: {len(sites)} site(s): " + ", ".join(sorted(set(sites))))
        r = remaining(new)
        if r:
            left += len(r)
            print(f"{f}: still has " + ", ".join(sorted(set(r))))
    if a.check:
        print(f"\n{left} placeholder(s) remaining")
        return 1 if left else 0
    print(f"\n{total_sites} site(s) written; {left} placeholder(s) remaining")
    return 1 if left else 0


if __name__ == "__main__":
    raise SystemExit(main())
