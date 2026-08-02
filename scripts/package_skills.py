#!/usr/bin/env python3
"""Package each skill into a zip that can be uploaded straight to claude.ai.

claude.ai accepts a zip whose *root* is the skill folder, not the folder's
contents. Zipping by hand gets this wrong often enough that it is worth
automating, so this script produces archives that are correct by construction:

    dist/evidence-synthesis.zip
    └── evidence-synthesis/
        ├── SKILL.md
        └── ...

It also writes `dist/claude-research-skills-all.zip` containing every skill, for
people installing into a filesystem agent rather than uploading one at a time.

Usage
-----
    python scripts/package_skills.py                  # build everything into dist/
    python scripts/package_skills.py --out build      # different output directory
    python scripts/package_skills.py --skill hpc-cluster --skill journal-advisor
    python scripts/package_skills.py --no-bundle      # skip the all-skills archive

Standard library only. Deterministic: file order is sorted and timestamps are
fixed, so rebuilding an unchanged skill produces a byte-identical archive.
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NON_SKILL_DIRS = {"scripts", "docs", "assets", ".github", ".git", "dist", "build"}

# Fixed timestamp (1980-01-01, the zip epoch) so archives are reproducible.
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)

# Never ship these, even if they exist locally.
EXCLUDE_NAMES = {".DS_Store", "Thumbs.db", "__pycache__", ".pytest_cache", ".ipynb_checkpoints"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".swp"}


def discover_skills() -> list[Path]:
    return [
        d
        for d in sorted(REPO_ROOT.iterdir(), key=lambda p: p.name.lower())
        if d.is_dir()
        and not d.name.startswith(".")
        and d.name not in NON_SKILL_DIRS
        and (d / "SKILL.md").exists()
    ]


def files_in(skill_dir: Path) -> list[Path]:
    """Every shippable file under a skill, sorted for determinism."""
    out = []
    for path in sorted(skill_dir.rglob("*"), key=lambda p: p.as_posix()):
        if not path.is_file():
            continue
        if any(part in EXCLUDE_NAMES for part in path.parts):
            continue
        if path.suffix in EXCLUDE_SUFFIXES:
            continue
        out.append(path)
    return out


def add(zf: zipfile.ZipFile, path: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname, date_time=ZIP_EPOCH)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    zf.writestr(info, path.read_bytes())


def package_one(skill_dir: Path, out_dir: Path) -> tuple[Path, int, int]:
    target = out_dir / f"{skill_dir.name}.zip"
    paths = files_in(skill_dir)
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in paths:
            # Root the archive at the skill folder itself: claude.ai requires it.
            add(zf, path, f"{skill_dir.name}/{path.relative_to(skill_dir).as_posix()}")
    return target, len(paths), target.stat().st_size


def package_bundle(skill_dirs: list[Path], out_dir: Path) -> tuple[Path, int, int]:
    target = out_dir / "claude-research-skills-all.zip"
    count = 0
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for skill_dir in skill_dirs:
            for path in files_in(skill_dir):
                add(zf, path, f"{skill_dir.name}/{path.relative_to(skill_dir).as_posix()}")
                count += 1
    return target, count, target.stat().st_size


def human(size: int) -> str:
    return f"{size / 1024:.0f} KB" if size < 1024 * 1024 else f"{size / 1024 / 1024:.1f} MB"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default="dist", help="output directory (default: dist)")
    p.add_argument("--skill", action="append", default=[],
                   help="package only this skill; repeatable")
    p.add_argument("--no-bundle", action="store_true",
                   help="skip the combined all-skills archive")
    a = p.parse_args()

    skills = discover_skills()
    if not skills:
        sys.exit("No skills found. Are you running this from the repository root?")

    if a.skill:
        by_name = {d.name: d for d in skills}
        unknown = [s for s in a.skill if s not in by_name]
        if unknown:
            sys.exit(f"Unknown skill(s): {', '.join(unknown)}\n"
                     f"Available: {', '.join(by_name)}")
        selected = [by_name[s] for s in a.skill]
    else:
        selected = skills

    if not a.out.strip():
        sys.exit("--out must name a directory; refusing to write into the repository root")
    out_dir = Path(a.out) if Path(a.out).is_absolute() else (REPO_ROOT / a.out)
    if out_dir.resolve() == REPO_ROOT:
        sys.exit("--out must not be the repository root")
    out_dir.mkdir(parents=True, exist_ok=True)

    for skill_dir in selected:
        target, n, size = package_one(skill_dir, out_dir)
        print(f"{target.name:<44} {n:>4} files  {human(size):>8}")

    if not a.no_bundle and not a.skill:
        target, n, size = package_bundle(selected, out_dir)
        print(f"{target.name:<44} {n:>4} files  {human(size):>8}")

    print(f"\nWrote {a.out}/ ({len(selected)} skill(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
