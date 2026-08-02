#!/usr/bin/env python3
"""Regenerate the skill catalog in README.md from each skill's SKILL.md frontmatter.

The catalog is the single source of truth for "what skills exist," and it is
derived automatically so the README never drifts from reality. Adding a new
skill is therefore a two-step ritual: drop the skill folder in, then run this.

Usage
-----
    python scripts/generate_catalog.py            # rewrite README.md in place
    python scripts/generate_catalog.py --check    # exit 1 if README.md is stale (CI)

Contract
--------
The README must contain a table region delimited by:

    <!-- SKILLS:START -->
    ...generated table...
    <!-- SKILLS:END -->

and a skills-count badge of the form `badge/skills-<n>-...`, which is kept in
sync with the number of discovered skills.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required. Install it with: pip install pyyaml")

REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"

# Release assets are built by .github/workflows/release.yml. This URL always
# resolves to the newest release, so the table never needs a version bump.
REPO_SLUG = "anayy09/claude-research-skills"
DOWNLOAD_URL = f"https://github.com/{REPO_SLUG}/releases/latest/download/{{name}}.zip"

# Top-level directories that are repo infrastructure, not skills.
NON_SKILL_DIRS = {"scripts", "docs", "assets", ".github", ".git"}

TABLE_START = "<!-- SKILLS:START -->"
TABLE_END = "<!-- SKILLS:END -->"


def parse_frontmatter(path: Path) -> dict:
    """Return the YAML frontmatter of a Markdown file as a dict."""
    text = path.read_text(encoding="utf-8")
    if not text.lstrip().startswith("---"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    body = text.split("---", 2)
    if len(body) < 3:
        raise ValueError(f"{path}: malformed frontmatter (need opening and closing '---')")
    data = yaml.safe_load(body[1])
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter is not a mapping")
    return data


def first_sentence(text: str) -> str:
    text = " ".join((text or "").split())
    match = re.search(r"(.+?[.!?])(\s|$)", text)
    return match.group(1) if match else text


def discover_skills() -> list[dict]:
    """Find every skill (a directory containing SKILL.md) and read its metadata."""
    skills: list[dict] = []
    for child in sorted(REPO_ROOT.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir() or child.name.startswith(".") or child.name in NON_SKILL_DIRS:
            continue
        skill_md = child / "SKILL.md"
        if not skill_md.exists():
            continue
        fm = parse_frontmatter(skill_md)
        meta = fm.get("metadata") or {}
        skills.append(
            {
                "dir": child.name,
                "name": fm.get("name", child.name),
                "summary": fm.get("summary") or first_sentence(fm.get("description", "")),
                "version": str(fm.get("version", "—")),
                "status": meta.get("status") or "active",
                "replaced_by": meta.get("replaced_by") or [],
                "deprecated_since": meta.get("deprecated_since"),
            }
        )
    return skills


def build_table(skills: list[dict]) -> str:
    rows = [
        "| Skill | What it does | Version | Download |",
        "| :---- | :----------- | :-----: | :------: |",
    ]
    for s in skills:
        summary = s["summary"].replace("|", "\\|")
        zip_url = DOWNLOAD_URL.format(name=s["dir"])
        rows.append(
            f"| [`{s['name']}`](./{s['dir']}) | {summary} | `{s['version']}` "
            f"| [`.zip`]({zip_url}) |"
        )
    return "\n".join(rows)


def build_deprecated_table(skills: list[dict]) -> str:
    rows = [
        "| Skill | Replaced by | Since |",
        "| :---- | :---------- | :---: |",
    ]
    for s in skills:
        replaced = ", ".join(f"[`{r}`](./{r})" for r in s["replaced_by"]) or "—"
        since = str(s.get("deprecated_since") or "—")
        rows.append(f"| ~~[`{s['name']}`](./{s['dir']})~~ | {replaced} | {since} |")
    return "\n".join(rows)


def render(readme_text: str, skills: list[dict]) -> str:
    active = [s for s in skills if s["status"] != "deprecated"]
    deprecated = [s for s in skills if s["status"] == "deprecated"]

    table = build_table(active)
    if deprecated:
        table += (
            "\n\n**Deprecated.** Retained during a transition period; prefer the "
            "replacements.\n\n" + build_deprecated_table(deprecated)
        )

    pattern = re.compile(re.escape(TABLE_START) + r".*?" + re.escape(TABLE_END), re.DOTALL)
    if not pattern.search(readme_text):
        raise ValueError(f"Could not find the {TABLE_START} / {TABLE_END} markers in README.md")
    updated = pattern.sub(f"{TABLE_START}\n{table}\n{TABLE_END}", readme_text)
    # Keep the skills-count badge honest (active skills only).
    updated = re.sub(r"(badge/skills-)\d+", rf"\g<1>{len(active)}", updated)
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate the README skill catalog.")
    parser.add_argument("--check", action="store_true", help="exit 1 if README.md is out of date")
    args = parser.parse_args()

    skills = discover_skills()
    if not skills:
        sys.exit("No skills found. Are you running this from the repository root?")

    original = README.read_text(encoding="utf-8")
    updated = render(original, skills)

    active = sum(1 for s in skills if s["status"] != "deprecated")
    deprecated = len(skills) - active
    label = f"{active} active" + (f", {deprecated} deprecated" if deprecated else "")

    if args.check:
        if updated != original:
            print("README.md is out of date. Run: python scripts/generate_catalog.py", file=sys.stderr)
            return 1
        print(f"README.md is up to date ({label}).")
        return 0

    if updated != original:
        README.write_text(updated, encoding="utf-8", newline="\n")
        print(f"Updated README.md catalog ({label}).")
    else:
        print(f"README.md already up to date ({label}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
