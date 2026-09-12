#!/usr/bin/env python3
"""Keep every agent runtime reading the same skill folders as this repository.

Claude Code reads ~/.claude/skills, which is this repository. Codex and other
Agent Skills clients read ~/.agents/skills. A copy there goes stale the moment
main moves, and a stale copy runs rules that have since been fixed. This script
replaces each copied skill folder under a runtime root with a directory
junction (Windows) or symlink (POSIX) to the folder here, and leaves anything
that is not one of this repository's skills alone.

    python scripts/sync_runtimes.py --check      # report per runtime, exit 1 if anything is stale
    python scripts/sync_runtimes.py --apply      # replace stale copies with links (copies are moved aside)
    python scripts/sync_runtimes.py --apply --root ~/.agents/skills --root ~/.codex/skills

Standard library only. Junctions need no elevation on Windows.
"""
from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NON_SKILL_DIRS = {"scripts", "docs", "assets", ".github", ".git", "dist", "build"}
DEFAULT_ROOTS = [Path.home() / ".agents" / "skills"]


def skills() -> list[Path]:
    return [d for d in sorted(REPO_ROOT.iterdir()) if d.is_dir() and not d.name.startswith(".")
            and d.name not in NON_SKILL_DIRS and (d / "SKILL.md").exists()]


def is_link(p: Path) -> bool:
    if p.is_symlink():
        return True
    if os.name == "nt":
        try:
            return bool(os.lstat(p).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)  # type: ignore[attr-defined]
        except (OSError, AttributeError):
            return False
    return False


def points_here(link: Path, target: Path) -> bool:
    try:
        return Path(os.path.realpath(link)).resolve() == target.resolve()
    except OSError:
        return False


def make_link(link: Path, target: Path) -> None:
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], check=True, capture_output=True)
    else:
        os.symlink(target, link, target_is_directory=True)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", action="append", default=[], help="runtime skills root; repeatable (default ~/.agents/skills)")
    p.add_argument("--check", action="store_true")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--retire", action="append", default=[], metavar="NAME",
                   help="a former skill name whose stale copy should be moved aside (e.g. a renamed or deleted skill); repeatable")
    a = p.parse_args()
    if not a.check and not a.apply:
        p.error("give --check or --apply")
    roots = [Path(os.path.expanduser(r)) for r in a.root] or DEFAULT_ROOTS
    stale = 0
    for root in roots:
        print(f"== {root}" + ("" if root.exists() else " (missing; will be created on --apply)"))
        if not root.exists():
            if a.apply:
                root.mkdir(parents=True, exist_ok=True)
            else:
                stale += len(skills())
                continue
        if root.resolve() == REPO_ROOT.resolve():
            print("   is the repository itself; nothing to do")
            continue
        aside = root / f".replaced-{time.strftime('%Y%m%d')}"
        for s in skills():
            dst = root / s.name
            if dst.exists() or is_link(dst):
                if is_link(dst) and points_here(dst, s):
                    print(f"   ok      {s.name} -> repo")
                    continue
                stale += 1
                if a.apply:
                    aside.mkdir(exist_ok=True)
                    target = aside / s.name
                    if target.exists():
                        shutil.rmtree(target, ignore_errors=True)
                    if is_link(dst):
                        os.rmdir(dst)
                    else:
                        shutil.move(str(dst), str(target))
                    make_link(dst, s)
                    print(f"   linked  {s.name} (copy moved to {aside.name}/)")
                else:
                    print(f"   STALE   {s.name} is a copy, not a link")
            else:
                stale += 1
                if a.apply:
                    make_link(dst, s)
                    print(f"   linked  {s.name} (was missing)")
                else:
                    print(f"   MISSING {s.name}")
        for old in a.retire:
            dst = root / old
            if dst.exists() or is_link(dst):
                stale += 1
                if a.apply:
                    aside.mkdir(exist_ok=True)
                    if is_link(dst):
                        os.rmdir(dst)
                    else:
                        target = aside / old
                        if target.exists():
                            shutil.rmtree(target, ignore_errors=True)
                        shutil.move(str(dst), str(target))
                    print(f"   retired {old} (moved to {aside.name}/)")
                else:
                    print(f"   RETIRE  {old} is still present")
        others = [d.name for d in root.iterdir() if d.is_dir() and d.name not in {s.name for s in skills()} and not d.name.startswith(".")]
        if others:
            print("   left alone (not this repository's): " + ", ".join(others))
    if a.check:
        print(f"\n{stale} folder(s) stale or missing" if stale else "\nall runtimes read this repository")
        return 1 if stale else 0
    print("\ndone; run --check to confirm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
