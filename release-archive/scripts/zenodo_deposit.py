#!/usr/bin/env python3
"""
zenodo_deposit.py - Create, version, and publish a Zenodo deposit for a code
or artifact release, with the token read from the environment and never from
the command line.

Commands:
    create       new deposition: metadata from flags or --metadata JSON, files uploaded,
                 optionally published
    new-version  a new version of an existing concept: --concept-doi or --deposition-id,
                 new files, new version string, optionally published
    inspect      print a deposition's metadata, files, DOIs, and state; changes nothing
    metadata     print the metadata JSON that would be sent, and validate it (no network)

Token: ZENODO_TOKEN in the environment, or ZENODO_TOKEN=... in a .env file
in the current directory (or --env-file). It is never accepted as an
argument, never printed, and never written.

Creators come from AUTHORS.yaml (--authors, default ./AUTHORS.yaml) so the
deposit cannot carry a name or affiliation the owner did not supply.

Usage:
    python zenodo_deposit.py metadata --title "..." --version v1.0.0 --description-file README.md
    python zenodo_deposit.py create --title "..." --version v1.0.0 --upload release.zip --sandbox
    python zenodo_deposit.py create --metadata zenodo.json --upload release.zip --publish
    python zenodo_deposit.py new-version --concept-doi 10.5281/zenodo.1234567 --version v1.1.0 \\
        --upload release.zip --replace --publish
    python zenodo_deposit.py inspect --deposition-id 1234568
    python zenodo_deposit.py --self-test

Concept DOI versus version DOI: the concept DOI always resolves to the newest
version and is what a manuscript cites; each version has its own DOI for a
frozen artifact. The script prints both after every publish.

Uses `requests` when importable, else urllib. Standard library otherwise.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

LICENSES = {"mit": "mit", "apache-2.0": "apache-2.0", "apache": "apache-2.0", "gpl-3.0": "gpl-3.0", "bsd-3": "bsd-3-clause",
            "cc-by-4.0": "cc-by-4.0", "cc-by": "cc-by-4.0", "cc0": "cc0-1.0"}


def load_token(env_file: Optional[str]) -> str:
    tok = os.environ.get("ZENODO_TOKEN", "").strip()
    if tok:
        return tok
    for cand in ([Path(env_file)] if env_file else [Path(".env"), Path("..") / ".env"]):
        if cand.exists():
            for ln in cand.read_text(encoding="utf-8", errors="replace").splitlines():
                m = re.match(r"^\s*(?:export\s+)?ZENODO_TOKEN\s*=\s*['\"]?([^'\"\s#]+)", ln)
                if m:
                    return m.group(1)
    return ""


def load_authors(path: Path) -> List[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    authors: List[dict] = []
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text) or {}
        authors = list(data.get("authors") or [])
    except Exception:
        cur: Optional[dict] = None
        for ln in text.splitlines():
            m = re.match(r"^\s*-\s*name:\s*(.+)$", ln)
            if m:
                cur = {"name": m.group(1).strip().strip("'\"")}
                authors.append(cur)
                continue
            m = re.match(r"^\s+(\w+):\s*(.+)$", ln)
            if m and cur is not None:
                cur[m.group(1)] = m.group(2).strip().strip("'\"")
    return authors


def creators_from_authors(authors: List[dict]) -> List[dict]:
    out = []
    for a in authors:
        name = str(a.get("name", "")).strip()
        if not name:
            continue
        parts = name.split()
        zname = f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else name
        c: Dict[str, str] = {"name": zname}
        if a.get("affiliation"):
            c["affiliation"] = str(a["affiliation"])
        if a.get("orcid"):
            c["orcid"] = str(a["orcid"])
        out.append(c)
    return out


def build_metadata(a: argparse.Namespace, creators: List[dict]) -> dict:
    if a.metadata:
        md = json.loads(Path(a.metadata).read_text(encoding="utf-8"))
        md = md.get("metadata", md)
    else:
        desc = Path(a.description_file).read_text(encoding="utf-8") if a.description_file else (a.description or "")
        md = {"title": a.title or "", "upload_type": a.upload_type, "description": desc,
              "version": a.version or "", "access_right": "open",
              "license": LICENSES.get((a.license or "mit").lower(), a.license or "mit"),
              "keywords": [k.strip() for k in (a.keywords or "").split(",") if k.strip()]}
        if a.upload_type == "software" and not desc:
            md["description"] = "Code and artifacts for the associated manuscript."
        if a.related_doi:
            md["related_identifiers"] = [{"identifier": d, "relation": "isSupplementTo", "resource_type": "publication-article"} for d in a.related_doi]
    if creators:
        md["creators"] = creators
    return md


def validate_metadata(md: dict) -> List[str]:
    problems = []
    for k in ("title", "upload_type", "description", "creators"):
        if not md.get(k):
            problems.append(f"missing {k}")
    if md.get("upload_type") not in (None, "software", "dataset", "publication", "poster", "presentation", "image", "video", "other", "lesson", "physicalobject"):
        problems.append(f"unknown upload_type {md.get('upload_type')}")
    for c in md.get("creators") or []:
        if "," not in c.get("name", ""):
            problems.append(f"creator name should be 'Family, Given': {c.get('name')}")
        if c.get("orcid") and not re.match(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$", c["orcid"]):
            problems.append(f"bad ORCID for {c.get('name')}")
    if re.search(r"\[AUTHOR (INPUT|ACTION)|TODO|TBD", json.dumps(md), re.I):
        problems.append("placeholder text in the metadata")
    if not md.get("version"):
        problems.append("no version string (use the git tag)")
    return problems


class Api:
    def __init__(self, token: str, sandbox: bool):
        self.base = "https://sandbox.zenodo.org/api" if sandbox else "https://zenodo.org/api"
        self.token = token
        try:
            import requests  # type: ignore
            self.requests = requests
        except ImportError:
            self.requests = None

    def call(self, method: str, url: str, data: Optional[dict] = None, raw: Optional[bytes] = None) -> dict:
        headers = {"Authorization": f"Bearer {self.token}"}
        if self.requests:
            if raw is not None:
                r = self.requests.request(method, url, headers=headers, data=raw, timeout=600)
            else:
                r = self.requests.request(method, url, headers={**headers, "Content-Type": "application/json"},
                                          data=json.dumps(data) if data is not None else None, timeout=120)
            if r.status_code >= 400:
                raise RuntimeError(f"{method} {url} -> {r.status_code}: {r.text[:600]}")
            return r.json() if r.text.strip() else {}
        body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
        if raw is None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                t = resp.read().decode("utf-8", errors="replace")
                return json.loads(t) if t.strip() else {}
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{method} {url} -> {e.code}: {e.read().decode('utf-8', errors='replace')[:600]}")

    def upload(self, bucket: str, path: Path) -> dict:
        return self.call("PUT", f"{bucket}/{path.name}", raw=path.read_bytes())


def print_dois(dep: dict) -> None:
    md = dep.get("metadata", {})
    print(f"deposition id : {dep.get('id')}")
    print(f"state         : {dep.get('state')} (submitted={dep.get('submitted')})")
    print(f"version DOI   : {dep.get('doi') or md.get('prereserve_doi', {}).get('doi', '(reserved on publish)')}")
    print(f"concept DOI   : {dep.get('conceptdoi', '(assigned on first publish)')}")
    if dep.get("links", {}).get("html"):
        print(f"page          : {dep['links']['html']}")


def cmd_metadata(a: argparse.Namespace) -> int:
    creators = creators_from_authors(load_authors(Path(a.authors))) if Path(a.authors).exists() else []
    md = build_metadata(a, creators)
    problems = validate_metadata(md)
    print(json.dumps({"metadata": md}, indent=2, ensure_ascii=False))
    if problems:
        print("\nproblems: " + "; ".join(problems), file=sys.stderr)
        return 1
    print("\nmetadata valid", file=sys.stderr)
    return 0


def cmd_create(a: argparse.Namespace) -> int:
    token = load_token(a.env_file)
    if not token:
        print("error: no ZENODO_TOKEN in the environment or .env", file=sys.stderr)
        return 2
    creators = creators_from_authors(load_authors(Path(a.authors))) if Path(a.authors).exists() else []
    if not creators:
        print("error: no creators; supply AUTHORS.yaml (--authors). Creators are never typed from memory.", file=sys.stderr)
        return 2
    md = build_metadata(a, creators)
    problems = validate_metadata(md)
    if problems:
        print("error: " + "; ".join(problems), file=sys.stderr)
        return 2
    for f in a.upload:
        if not Path(f).exists():
            print(f"error: {f} not found", file=sys.stderr)
            return 2
    api = Api(token, a.sandbox)
    if a.dry_run:
        print(json.dumps({"metadata": md, "files": a.upload, "publish": a.publish, "sandbox": a.sandbox}, indent=2))
        return 0
    dep = api.call("POST", f"{api.base}/deposit/depositions", {"metadata": md})
    bucket = dep["links"]["bucket"]
    for f in a.upload:
        api.upload(bucket, Path(f))
        print(f"uploaded {f}")
    if a.publish:
        dep = api.call("POST", f"{api.base}/deposit/depositions/{dep['id']}/actions/publish")
    print_dois(dep)
    if not a.publish:
        print("draft only; add --publish to mint the DOI, or publish from the page above")
    return 0


def cmd_new_version(a: argparse.Namespace) -> int:
    token = load_token(a.env_file)
    if not token:
        print("error: no ZENODO_TOKEN in the environment or .env", file=sys.stderr)
        return 2
    api = Api(token, a.sandbox)
    dep_id = a.deposition_id
    if not dep_id and a.concept_doi:
        recs = api.call("GET", f"{api.base}/deposit/depositions?q=conceptdoi:%22{a.concept_doi}%22&all_versions=true&sort=mostrecent")
        if not recs:
            print(f"error: no deposition found for concept DOI {a.concept_doi}", file=sys.stderr)
            return 2
        dep_id = recs[0]["id"]
    if not dep_id:
        print("error: give --deposition-id or --concept-doi", file=sys.stderr)
        return 2
    if a.dry_run:
        print(json.dumps({"new_version_of": dep_id, "version": a.version, "files": a.upload, "replace": a.replace, "publish": a.publish}, indent=2))
        return 0
    nv = api.call("POST", f"{api.base}/deposit/depositions/{dep_id}/actions/newversion")
    new_id = nv["links"]["latest_draft"].rstrip("/").split("/")[-1]
    draft = api.call("GET", f"{api.base}/deposit/depositions/{new_id}")
    md = draft["metadata"]
    if a.version:
        md["version"] = a.version
    if a.description_file:
        md["description"] = Path(a.description_file).read_text(encoding="utf-8")
    api.call("PUT", f"{api.base}/deposit/depositions/{new_id}", {"metadata": md})
    if a.replace:
        for f in draft.get("files", []):
            api.call("DELETE", f"{api.base}/deposit/depositions/{new_id}/files/{f['id']}")
    bucket = draft["links"]["bucket"]
    for f in a.upload:
        api.upload(bucket, Path(f))
        print(f"uploaded {f}")
    dep = api.call("GET", f"{api.base}/deposit/depositions/{new_id}")
    if a.publish:
        dep = api.call("POST", f"{api.base}/deposit/depositions/{new_id}/actions/publish")
    print_dois(dep)
    return 0


def cmd_inspect(a: argparse.Namespace) -> int:
    token = load_token(a.env_file)
    if not token:
        print("error: no ZENODO_TOKEN in the environment or .env", file=sys.stderr)
        return 2
    api = Api(token, a.sandbox)
    dep = api.call("GET", f"{api.base}/deposit/depositions/{a.deposition_id}")
    print_dois(dep)
    print("files         : " + ", ".join(f"{f['filename']} ({int(f.get('filesize', 0)) / 1e6:.1f} MB)" for f in dep.get("files", [])))
    print("title         : " + dep.get("metadata", {}).get("title", ""))
    print("version       : " + str(dep.get("metadata", {}).get("version", "")))
    return 0


def self_test() -> int:
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    with tempfile.TemporaryDirectory() as td:
        env = Path(td) / ".env"
        env.write_text("OTHER=1\nZENODO_TOKEN='abc123def456'\n", encoding="utf-8")
        old = os.environ.pop("ZENODO_TOKEN", None)
        check("token read from .env, quotes stripped", load_token(str(env)) == "abc123def456")
        if old:
            os.environ["ZENODO_TOKEN"] = old
        auth = Path(td) / "AUTHORS.yaml"
        auth.write_text("authors:\n  - name: Anay Sinhal\n    affiliation: University of Florida\n    orcid: 0009-0008-8328-2336\n  - name: Amit Sinhal\n", encoding="utf-8")
        cr = creators_from_authors(load_authors(auth))
        check("creators in Family, Given form with affiliation and orcid", cr[0]["name"] == "Sinhal, Anay" and cr[0]["orcid"].startswith("0009") and cr[1]["name"] == "Sinhal, Amit")
        ns = argparse.Namespace(metadata=None, description_file=None, description="Code for the paper.", title="Paper code", upload_type="software",
                                version="v1.0.0", license="MIT", keywords="a, b", related_doi=["10.1000/paper"])
        md = build_metadata(ns, cr)
        check("metadata valid", validate_metadata(md) == [] and md["license"] == "mit" and md["related_identifiers"][0]["relation"] == "isSupplementTo")
        md["description"] = "TODO write"
        md["version"] = ""
        pr = validate_metadata(md)
        check("placeholder and missing version rejected", any("placeholder" in p for p in pr) and any("version" in p for p in pr))
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", nargs="?", choices=["create", "new-version", "inspect", "metadata"])
    p.add_argument("--title"); p.add_argument("--description"); p.add_argument("--description-file")
    p.add_argument("--version"); p.add_argument("--upload-type", default="software"); p.add_argument("--license", default="mit")
    p.add_argument("--keywords"); p.add_argument("--related-doi", action="append", default=[], help="DOI of the manuscript this supplements; repeatable")
    p.add_argument("--metadata", help="JSON file with the full metadata instead of flags")
    p.add_argument("--authors", default="AUTHORS.yaml")
    p.add_argument("--upload", action="append", default=[], help="file to upload; repeatable")
    p.add_argument("--replace", action="store_true", help="new-version: drop the files carried over from the previous version")
    p.add_argument("--publish", action="store_true")
    p.add_argument("--deposition-id"); p.add_argument("--concept-doi")
    p.add_argument("--sandbox", action="store_true", help="use sandbox.zenodo.org")
    p.add_argument("--env-file")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.command:
        p.print_help()
        return 2
    return {"create": cmd_create, "new-version": cmd_new_version, "inspect": cmd_inspect, "metadata": cmd_metadata}[a.command](a)


if __name__ == "__main__":
    raise SystemExit(main())
