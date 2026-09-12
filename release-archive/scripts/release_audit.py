#!/usr/bin/env python3
"""
release_audit.py - Audit a directory that is about to become a public
reproducibility repository, and refuse to let it ship with the things that
must not leave the internal repo.

It walks the tree and reports:

  secrets        .env files, token-shaped strings (ghp_, sk-, ZENODO_TOKEN=,
                 AWS keys), private keys
  internal ids   decision, progress, results, and gate ids (D-012, R-0042,
                 P5G3), and the ledger and handback documents themselves
  nomenclature   milestone words in code, identifiers, and README (phase-3,
                 stage2, "kill experiment", "strengthener 10")
  local paths    absolute paths from the author's machine (C:\\Users, /home/,
                 OneDrive)
  placeholders   [AUTHOR INPUT ...], TODO, TBD, [DOI PENDING], zenodo.XXXXXXX
  data           files larger than --max-mb, and names matching --restricted
                 (default: mimic, physionet, eicu, phi, dua), which are
                 usually under a data-use agreement
  scaffolding    README.md present with an entry command, LICENSE present,
                 CITATION.cff present and carrying a DOI or a placeholder for
                 one, requirements or environment file present

FAIL on secrets, restricted data, and missing LICENSE or README; WARN on the
rest. --strict exits 1 on any WARN as well.

Usage:
    python release_audit.py path/to/public-repo
    python release_audit.py . --strict --max-mb 25 --restricted mimic,physionet
    python release_audit.py --self-test

Standard library only.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache", ".pytest_cache", "dist", "build"}
TEXT_EXT = {".py", ".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini", ".tex", ".bib", ".sh", ".ps1", ".r", ".jl", ".m", ".ipynb", ".cff", ".csv", ".rst"}
SECRET_RES = [r"\bghp_[A-Za-z0-9]{20,}", r"\bgithub_pat_[A-Za-z0-9_]{20,}", r"\bsk-[A-Za-z0-9]{20,}", r"\bAKIA[0-9A-Z]{16}\b",
              r"ZENODO_TOKEN\s*=\s*\S{10,}", r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", r"\bxox[bp]-[A-Za-z0-9-]{20,}"]
INTERNAL_ID_RE = re.compile(r"\b(?:D-\d{3,4}|R-\d{4}|P\d+G\d+|P-\d{3})\b")
INTERNAL_DOCS = re.compile(r"^(DECISIONS|PROGRESS|RESULTS-LOG|GATES|HANDBACK|HANDOFF|STARTER|START_AGENT_PROMPT|AGENT|SKILL-ROUTING|SKILL-MAP|PREREGISTRATION|RUNBOOK|REVIEWER[-_ ]CHECKLIST|LIT-REVIEW|FRAMING-PACKAGE)[^/]*\.md$", re.I)
NOMENCLATURE_RE = re.compile(r"\b(?:phase[-_ ]?\d+|stage[-_ ]?\d+|kill experiment|strengthener \d+|milestone M\d+)(?![A-Za-z0-9])", re.I)
LOCAL_PATH_RE = re.compile(r"(?:[A-Za-z]:\\Users\\|/home/[a-z]+/|/Users/[a-z]+/|OneDrive - )")
PLACEHOLDER_RE = re.compile(r"\[AUTHOR (?:INPUT|ACTION)[^\]]*\]|\bTODO\b|\bTBD\b|\[DOI PENDING\]|zenodo\.X{5,}|10\.5281/zenodo\.NNN", re.I)


def walk(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            yield Path(dirpath) / f


def audit(root: Path, max_mb: float, restricted: List[str]) -> Tuple[List[str], List[str], Dict[str, int]]:
    fails: List[str] = []
    warns: List[str] = []
    counts: Dict[str, int] = {"files": 0, "internal_ids": 0, "nomenclature": 0, "local_paths": 0, "placeholders": 0}
    for f in walk(root):
        counts["files"] += 1
        rel = f.relative_to(root).as_posix()
        name = f.name
        if name == ".env" or name.startswith(".env.") or name.endswith((".pem", ".key")) or name in ("credentials.json", "secrets.yaml", "secrets.json"):
            fails.append(f"secret file: {rel}")
            continue
        low = rel.lower()
        if any(r and r in low for r in restricted):
            fails.append(f"restricted-data name: {rel} (matches {[r for r in restricted if r in low]})")
        try:
            size_mb = f.stat().st_size / 1e6
        except OSError:
            size_mb = 0
        if size_mb > max_mb:
            warns.append(f"large file: {rel} ({size_mb:.0f} MB); data belongs in the archive, not the repository")
        if INTERNAL_DOCS.match(name):
            warns.append(f"internal document: {rel}; the public repo carries the code and results, not the ledger")
        if NOMENCLATURE_RE.search(rel):
            warns.append(f"milestone nomenclature in a path: {rel}")
            counts["nomenclature"] += 1
        if f.suffix.lower() not in TEXT_EXT or size_mb > 5:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pat in SECRET_RES:
            if re.search(pat, text):
                fails.append(f"token-shaped string in {rel} ({pat[:20]}...)")
                break
        ids = INTERNAL_ID_RE.findall(text)
        if ids:
            counts["internal_ids"] += len(ids)
            warns.append(f"internal ids in {rel}: {', '.join(sorted(set(ids))[:6])}")
        nom = NOMENCLATURE_RE.findall(text)
        if nom and f.suffix.lower() != ".md":
            counts["nomenclature"] += len(nom)
            warns.append(f"milestone nomenclature in {rel}: {', '.join(sorted(set(nom))[:4])}")
        lp = LOCAL_PATH_RE.findall(text)
        if lp:
            counts["local_paths"] += len(lp)
            warns.append(f"local absolute path in {rel}")
        ph = PLACEHOLDER_RE.findall(text)
        if ph:
            counts["placeholders"] += len(ph)
            warns.append(f"placeholders in {rel}: {', '.join(sorted(set(ph))[:4])}")
    readme = next((p for p in root.iterdir() if p.name.lower() in ("readme.md", "readme.rst", "readme.txt")), None)
    if readme is None:
        fails.append("no README at the root")
    else:
        t = readme.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"^\s*(?:\$ )?(python|make|bash|sh|Rscript|julia|snakemake|nextflow|docker|pip|conda)\b", t, re.M):
            warns.append("README has no visible entry command (a line starting with python, make, docker, ...); a reader cannot tell how to regenerate a number")
        if not re.search(r"\b(cite|citation|DOI|doi\.org)\b", t):
            warns.append("README does not say how to cite the work")
    if not any(p.name.lower().startswith("license") for p in root.iterdir()):
        fails.append("no LICENSE at the root")
    cff = root / "CITATION.cff"
    if not cff.exists():
        warns.append("no CITATION.cff; Zenodo and GitHub read it for the citation metadata")
    else:
        t = cff.read_text(encoding="utf-8", errors="replace")
        if "doi:" not in t and "identifiers:" not in t:
            warns.append("CITATION.cff has no doi; add the concept DOI after the first deposit")
    if not any((root / n).exists() for n in ("requirements.txt", "environment.yml", "pyproject.toml", "setup.py", "Pipfile", "renv.lock", "Project.toml", "Dockerfile")):
        warns.append("no environment file (requirements.txt, environment.yml, pyproject.toml, Dockerfile)")
    return fails, warns, counts


def self_test() -> int:
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    with tempfile.TemporaryDirectory() as td:
        r = Path(td)
        (r / "README.md").write_text("# Repo\n\nRun:\n\n    python run.py\n\nCite via DOI 10.1/x\n", encoding="utf-8")
        (r / "LICENSE").write_text("MIT", encoding="utf-8")
        (r / "requirements.txt").write_text("numpy\n", encoding="utf-8")
        (r / "src").mkdir()
        (r / "src" / "phase3_runner.py").write_text("# see D-041 and R-0042\nDATA = r'C:\\Users\\sinha\\Dev\\DATA'\nTOKEN='ghp_abcdefghijklmnopqrstuvwxyz1234'\n", encoding="utf-8")
        (r / "docs").mkdir()
        (r / "docs" / "HANDBACK-2026-08-30.md").write_text("x", encoding="utf-8")
        (r / "data").mkdir()
        (r / "data" / "mimic_cohort.csv").write_text("id\n", encoding="utf-8")
        (r / ".env").write_text("ZENODO_TOKEN=abc", encoding="utf-8")
        fails, warns, counts = audit(r, 50, ["mimic", "physionet"])
        check("secret file and token string are FAILs", any(".env" in f for f in fails) and any("token-shaped" in f for f in fails))
        check("restricted data name is a FAIL", any("restricted-data" in f for f in fails))
        check("internal ids, nomenclature path, local path, handback are WARNs",
              any("internal ids" in w for w in warns) and any("nomenclature in a path" in w for w in warns)
              and any("local absolute path" in w for w in warns) and any("internal document" in w for w in warns))
        check("no CITATION.cff warned", any("CITATION.cff" in w for w in warns))
        (r / "README.md").unlink()
        fails2, _, _ = audit(r, 50, [])
        check("missing README is a FAIL", any("README" in f for f in fails2))
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path", nargs="?")
    p.add_argument("--max-mb", type=float, default=50.0)
    p.add_argument("--restricted", default="mimic,physionet,eicu,phi,dua", help="comma-separated name fragments that mark data under a use agreement")
    p.add_argument("--strict", action="store_true", help="exit 1 on WARN as well as FAIL")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.path:
        p.error("give the directory to audit (or --self-test)")
    root = Path(a.path)
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2
    fails, warns, counts = audit(root, a.max_mb, [r.strip().lower() for r in a.restricted.split(",") if r.strip()])
    for f in fails:
        print(f"FAIL {f}")
    for w in warns:
        print(f"WARN {w}")
    print(f"\n{counts['files']} files; {len(fails)} failure(s), {len(warns)} warning(s); "
          f"internal ids {counts['internal_ids']}, nomenclature {counts['nomenclature']}, local paths {counts['local_paths']}, placeholders {counts['placeholders']}")
    if fails:
        return 1
    return 1 if (a.strict and warns) else 0


if __name__ == "__main__":
    raise SystemExit(main())
