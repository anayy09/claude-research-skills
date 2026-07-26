#!/usr/bin/env python3
"""Validate that every skill follows the repository's structure and frontmatter spec.

Run locally before opening a PR, or let CI run it:

    python scripts/validate_skills.py

Exits non-zero and prints every problem it finds (not just the first one).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required. Install it with: pip install pyyaml")

REPO_ROOT = Path(__file__).resolve().parent.parent
NON_SKILL_DIRS = {"scripts", "docs", "assets", ".github", ".git"}

REQUIRED_TOP_LEVEL = ["name", "description", "summary", "version", "author", "license"]
SEMVER = re.compile(r"^\d+\.\d+\.\d+([-+].+)?$")


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.lstrip().startswith("---"):
        raise ValueError("missing YAML frontmatter")
    body = text.split("---", 2)
    if len(body) < 3:
        raise ValueError("malformed frontmatter (need opening and closing '---')")
    data = yaml.safe_load(body[1])
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    name = skill_dir.name

    if not (skill_dir / "README.md").exists():
        errors.append(f"{name}: missing README.md")

    skill_md = skill_dir / "SKILL.md"
    try:
        fm = parse_frontmatter(skill_md)
    except (OSError, ValueError) as exc:
        return errors + [f"{name}: SKILL.md {exc}"]

    for field in REQUIRED_TOP_LEVEL:
        if not fm.get(field):
            errors.append(f"{name}: SKILL.md frontmatter missing '{field}'")

    if fm.get("name") and fm["name"] != name:
        errors.append(f"{name}: frontmatter name '{fm['name']}' does not match folder name")

    version = str(fm.get("version", ""))
    if version and not SEMVER.match(version):
        errors.append(f"{name}: version '{version}' is not semantic (expected MAJOR.MINOR.PATCH)")

    metadata = fm.get("metadata")
    if not isinstance(metadata, dict) or not metadata.get("status"):
        errors.append(f"{name}: SKILL.md frontmatter missing 'metadata.status'")

    return errors


def main() -> int:
    skill_dirs = [
        d
        for d in sorted(REPO_ROOT.iterdir(), key=lambda p: p.name.lower())
        if d.is_dir()
        and not d.name.startswith(".")
        and d.name not in NON_SKILL_DIRS
        and (d / "SKILL.md").exists()
    ]

    if not skill_dirs:
        sys.exit("No skills found. Are you running this from the repository root?")

    all_errors: list[str] = []
    for d in skill_dirs:
        all_errors.extend(validate_skill(d))

    if all_errors:
        print(f"✗ Validation failed with {len(all_errors)} problem(s):\n", file=sys.stderr)
        for err in all_errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"✓ All {len(skill_dirs)} skills valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
