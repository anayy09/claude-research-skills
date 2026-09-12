#!/usr/bin/env python3
"""
verify_citations.py - Verify a reference list against the registries, using
the one citation checker this collection maintains.

This script used to carry its own copy of the verification logic. It now
parses the reference list (one reference per line, or a .bib) into the
source-log schema that `check_citations.py` (investigating-sources) reads,
and delegates the checking to that script, so that the DataCite fallback for
arXiv, the preprint-to-published upgrade, the retraction check, and the
peer-review classification are implemented once and fixed once.

The checker is found, in order: next to this file (the release zip ships a
copy), in the sibling `investigating-sources/scripts/` directory of a
skills folder, or at --checker.

Usage:
    python verify_citations.py --refs references.md --mailto you@uni.edu
    python verify_citations.py --refs refs.bib --mailto you@uni.edu --upgrade-preprints --require-peer-reviewed
    python verify_citations.py --doi 10.1136/bmj.n71 --mailto you@uni.edu
    python verify_citations.py --refs references.md --offline
    python verify_citations.py --refs references.md --write-log sources.json   # keep the source log for audit_report.py
    python verify_citations.py --self-test

Exit codes follow check_citations.py: 0 clean, 1 at least one FAIL, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.I)
YEAR_RE = re.compile(r"\((\d{4})[a-z]?\)|\b(19|20)\d{2}\b")
PREPRINT_PREFIXES = ("10.48550", "10.1101", "10.21203", "10.2139", "10.31234", "10.31235",
                     "10.36227", "10.20944", "10.26434", "10.31219", "10.1590")


def find_checker(explicit: Optional[str]) -> Optional[Path]:
    here = Path(__file__).resolve().parent
    cands = [Path(explicit)] if explicit else []
    cands += [here / "check_citations.py",
              here.parent.parent / "investigating-sources" / "scripts" / "check_citations.py",
              Path.home() / ".claude" / "skills" / "investigating-sources" / "scripts" / "check_citations.py",
              Path.home() / ".agents" / "skills" / "investigating-sources" / "scripts" / "check_citations.py"]
    for c in cands:
        if c.exists():
            return c
    return None


def parse_reference(line: str) -> dict:
    raw = line.strip().lstrip("-*0123456789. )").strip()
    doi = None
    m = DOI_RE.search(raw)
    if m:
        doi = m.group(0).rstrip(".,;)")
    if not doi:
        am = re.search(r"arXiv[:\s]\s*(\d{4}\.\d{4,5})(v\d+)?", raw, re.I)
        if am:
            doi = f"10.48550/arXiv.{am.group(1)}"
    ym = YEAR_RE.search(raw)
    year = int(ym.group(1) or ym.group(0)) if ym else None
    am2 = re.match(r"([A-Z][A-Za-z'À-ɏ-]+)\s*,", raw)
    author = am2.group(1) if am2 else ""
    body = DOI_RE.sub("", raw)
    body = re.sub(r"https?://\S+", "", body)
    parts = [p.strip() for p in re.split(r"(?<=[.?!])\s+(?=[A-Z(])|\.\s+", body) if len(p.strip()) > 15]
    cands = [p for p in parts if not re.match(r"^[A-Z][a-z]*,\s*[A-Z]\.", p)]
    title = max(cands, key=len).strip(" .") if cands else raw[:120]
    return {"raw": raw, "doi": doi or "", "title": title, "year": year, "author": author}


def parse_bibtex(text: str) -> List[dict]:
    out = []
    for entry in re.split(r"\n(?=@)", text):
        if not entry.strip().startswith("@"):
            continue

        def fld(name: str) -> Optional[str]:
            m = re.search(rf"{name}\s*=\s*[{{\"]+(.+?)[}}\"]+\s*,?\s*\n", entry, re.I | re.S)
            return re.sub(r"\s+", " ", m.group(1)).strip() if m else None

        km = re.match(r"@\w+\s*\{\s*([^,\s]+)", entry)
        doi = fld("doi") or ""
        if not doi and fld("eprint") and re.match(r"^\d{4}\.\d{4,5}", fld("eprint") or ""):
            doi = f"10.48550/arXiv.{(fld('eprint') or '').split('v')[0]}"
        y = fld("year")
        a = fld("author")
        out.append({"raw": re.sub(r"\s+", " ", entry)[:200], "doi": doi, "title": fld("title") or "",
                    "year": int(y) if y and y.isdigit() else None,
                    "author": re.split(r"\s+and\s+|,", a)[0].strip().split()[-1] if a else "",
                    "key": km.group(1) if km else None})
    return out


def load_refs(path: str) -> List[dict]:
    text = open(path, encoding="utf-8").read()
    if path.endswith(".bib"):
        return parse_bibtex(text)
    return [parse_reference(l) for l in text.splitlines() if l.strip() and len(l.strip()) > 20]


def to_source_log(refs: List[dict], topic: str = "reference list") -> dict:
    sources = []
    for i, r in enumerate(refs, 1):
        doi = r.get("doi") or ""
        sources.append({
            "key": r.get("key") or f"ref{i:03d}",
            "type": "preprint" if doi.startswith(PREPRINT_PREFIXES) else "journal-article",
            "authors": [r["author"]] if r.get("author") else [],
            "year": r.get("year") or 0,
            "title": r.get("title") or r.get("raw", "")[:120],
            "venue": "",
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else "",
            "verified": "pending", "verify_method": "", "peer_reviewed": "", "superseded_by": "",
            "tier": "", "notes": r.get("raw", "")[:200],
        })
    return {"topic": topic, "generated": "", "sources": sources}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--refs", help="file with one reference per line, or a .bib")
    p.add_argument("--doi", action="append", default=[], help="repeatable")
    p.add_argument("--mailto", default="")
    p.add_argument("--offline", action="store_true")
    p.add_argument("--require-peer-reviewed", action="store_true")
    p.add_argument("--upgrade-preprints", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--write-log", help="keep the generated source log here (for audit_report.py)")
    p.add_argument("--checker", help="path to check_citations.py if it is not next to this file or in a sibling skill")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()

    checker = find_checker(a.checker)
    if checker is None:
        print("error: check_citations.py not found. Install the investigating-sources skill next to this one, "
              "or pass --checker /path/to/check_citations.py. The release zip of evidence-synthesis ships a copy.", file=sys.stderr)
        return 2

    if a.self_test:
        ok = True
        r = parse_reference("Page MJ, et al. (2021). The PRISMA 2020 statement. BMJ 372:n71. https://doi.org/10.1136/bmj.n71")
        ok &= r["doi"] == "10.1136/bmj.n71" and r["year"] == 2021
        r2 = parse_reference("Vaswani A. (2017). Attention is all you need. arXiv:1706.03762")
        ok &= r2["doi"] == "10.48550/arXiv.1706.03762"
        log = to_source_log([r, r2])
        ok &= log["sources"][1]["type"] == "preprint" and log["sources"][0]["key"] == "ref001"
        print(("  ok   " if ok else "  FAIL ") + "reference parsing and source-log conversion", flush=True)
        rc = subprocess.call([sys.executable, str(checker), "--self-test"])
        return 0 if (ok and rc == 0) else 1

    refs: List[dict] = []
    if a.refs:
        refs.extend(load_refs(a.refs))
    refs.extend({"raw": d, "doi": d, "title": "", "year": None, "author": ""} for d in a.doi)
    if not refs:
        p.error("give --refs, --doi, or --self-test")

    log = to_source_log(refs, topic=a.refs or "dois")
    log_path = Path(a.write_log) if a.write_log else Path(tempfile.mkstemp(suffix=".json")[1])
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")

    cmd = [sys.executable, str(checker), str(log_path), "--write"]
    if a.mailto:
        cmd += ["--mailto", a.mailto]
    if a.offline:
        cmd.append("--offline")
    if a.upgrade_preprints:
        cmd.append("--upgrade-preprints")
    if a.require_peer_reviewed:
        cmd.append("--require-peer-reviewed")
    if a.json:
        cmd.append("--json")
    rc = subprocess.call(cmd)
    if a.write_log:
        print(f"\nsource log with statuses: {log_path}", file=sys.stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
