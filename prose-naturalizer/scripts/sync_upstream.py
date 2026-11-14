#!/usr/bin/env python3
"""Rebuild SKILL.md from upstream blader/humanizer plus this repository's local additions.

    git clone --depth 1 https://github.com/blader/humanizer /tmp/humanizer
    python scripts/sync_upstream.py /tmp/humanizer

The upstream body is copied unchanged. Three things are local: the frontmatter
(name, routing sentences, repository fields), the H1 title, and the block in
local-additions.md, which is inserted before the upstream "## Source" section.
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent

LOCAL_ROUTING = (
    "  Also for emails, chat replies, cover letters, and posts sent in the user's name.\n"
    "  On a research manuscript, thesis, or response letter it applies manuscript-writing's\n"
    "  lint and rules without comment. Mirrors blader/humanizer; local rules sit in one\n"
    "  section at the end.\n"
)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    upstream = Path(sys.argv[1])
    text = (upstream / "SKILL.md").read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        print("upstream SKILL.md has no frontmatter")
        return 1
    front, body = parts[1], parts[2]

    m = re.search(r'version:\s*"?([0-9]+\.[0-9]+\.[0-9]+)"?', front)
    if not m:
        print("upstream version not found")
        return 1
    version = m.group(1)

    d = re.search(r"description:\s*\|\n((?:  .*\n)+)", front)
    if not d:
        print("upstream description block not found")
        return 1
    description = d.group(1)

    try:
        sha = subprocess.run(
            ["git", "-C", str(upstream), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        sha = "unknown"

    new_front = (
        "\nname: prose-naturalizer\n"
        "description: |\n" + description + LOCAL_ROUTING +
        'summary: "Rewrite AI-sounding prose so it reads like the writer; mirrors blader/humanizer."\n'
        f'version: "{version}"\n'
        "author: anayy09\n"
        "license: MIT\n"
        "metadata:\n"
        "  status: active\n"
        f'  last_updated: "{date.today().isoformat()}"\n'
        f'  upstream: "blader/humanizer {version} ({sha})"\n'
        "compatibility: claude-code opencode\n"
    )

    body, n = re.subn(r"^# Humanizer: .*$", "# Prose Naturalizer: remove AI writing patterns",
                      body, count=1, flags=re.M)
    if n != 1:
        print("upstream H1 not found")
        return 1

    local = (HERE / "local-additions.md").read_text(encoding="utf-8").rstrip() + "\n\n"
    marker = "## Source"
    idx = body.rfind(marker)
    if idx < 0:
        body = body.rstrip() + "\n\n" + local
    else:
        body = body[:idx] + local + body[idx:]

    out = "---" + new_front + "---" + body
    desc_len = len((description + LOCAL_ROUTING).strip())
    if desc_len > 1024:
        print(f"description is {desc_len} characters; the portal cap is 1024")
        return 1
    (HERE / "SKILL.md").write_text(out, encoding="utf-8", newline="\n")
    print(f"SKILL.md rebuilt from humanizer {version} ({sha}); description {desc_len} chars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
