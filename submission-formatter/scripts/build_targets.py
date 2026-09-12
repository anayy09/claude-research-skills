#!/usr/bin/env python3
"""
build_targets.py - One manuscript body, several venue packages, rebuilt from a
spec on every edit, with the per-venue differences held in the spec rather
than in the prose.

A paper that is being kept ready for two or three venues at once decays when
each package is a hand-edited copy: a fix lands in one, a co-author is added
to another, and the bodies drift. This script renders each target from the
same body, abstract, keyword, and author sources, and refuses to overwrite a
main.tex that was edited by hand after the last render.

The spec (targets.yaml, or JSON):

    body: paper/body.tex              # shared: no \\documentclass, no \\begin{document}
    abstract: paper/abstract.tex
    keywords: paper/keywords.tex      # one keyword per line
    authors: docs/AUTHORS.yaml        # the only source of author identity
    bib: paper/refs.bib
    figures: paper/figures            # copied into each target
    targets:
      cep:
        template: templates/elsarticle-main.tex   # {{ABSTRACT}} {{KEYWORDS}} {{AUTHORS}} {{BODY}} {{BIBFILE}}
        out: submission/cep
        class: elsarticle             # elsarticle | sn-jnl | ieeetran | generic
        assets: [templates/elsarticle.cls, templates/elsarticle-num.bst]
        drop: [appendix, extended]    # regions marked % {{begin:NAME}} ... % {{end:NAME}} in the body
        page_cap: 0
      tcst:
        template: templates/ieeetran-main.tex
        out: submission/tcst
        class: ieeetran
        drop: [appendix]
        page_cap: 16

Regions in the body are marked with comment lines:

    % {{begin:appendix}}
    ...
    % {{end:appendix}}

and dropped for a target that lists the name. Everything else is identical
across targets; the only per-venue prose difference the script permits is
the citation command (\\citep for natbib classes, \\cite otherwise), which it
rewrites from a neutral \\citep in the body.

Guard: after a render, the script records the rendered main.tex as
<out>/.main.tex.rendered. On the next run, if <out>/main.tex differs from
that record (someone edited it by hand), it refuses to overwrite, writes
<out>/main.tex.regenerated beside it, and says so. --force overwrites.

    python build_targets.py targets.yaml                # render every target
    python build_targets.py targets.yaml --only cep     # one target
    python build_targets.py targets.yaml --check        # then run build-check on each with its page cap
    python build_targets.py --self-test

Standard library; PyYAML when the spec is YAML.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional


def load_spec(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
        except ImportError:
            sys.exit("PyYAML is needed to read a YAML spec (pip install pyyaml), or give JSON")
        return yaml.safe_load(text)
    return json.loads(text)


def load_authors(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except ImportError:
        authors: List[dict] = []
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
        return {"authors": authors}


def tex_escape(s: str) -> str:
    return re.sub(r"([&%$#_{}])", r"\\\1", s or "")


def render_authors(authors_doc: dict, cls: str) -> str:
    authors = [a for a in (authors_doc.get("authors") or []) if a.get("name")]
    corr = int(authors_doc.get("corresponding") or 1) - 1
    if not authors:
        return "% [AUTHOR INPUT: no authors in AUTHORS.yaml]\n"
    affils: List[str] = []
    for a in authors:
        for key in ("affiliation", "affiliation2"):
            if a.get(key) and a[key] not in affils:
                affils.append(a[key])
    idx = {aff: i + 1 for i, aff in enumerate(affils)}
    out: List[str] = []
    if cls == "elsarticle":
        for i, a in enumerate(authors):
            labels = ",".join(str(idx[a[k]]) for k in ("affiliation", "affiliation2") if a.get(k))
            corref = "\\corref{cor1}" if i == corr else ""
            out.append(f"\\author[{labels}]{{{tex_escape(a['name'])}{corref}}}")
            if a.get("email"):
                out.append(f"\\ead{{{a['email']}}}")
        out.append("\\cortext[cor1]{Corresponding author}")
        for aff, i in idx.items():
            out.append(f"\\affiliation[{i}]{{organization={{{tex_escape(aff)}}}}}")
    elif cls == "sn-jnl":
        for i, a in enumerate(authors):
            parts = a["name"].split()
            fnm, sur = " ".join(parts[:-1]), parts[-1]
            labels = ",".join(str(idx[a[k]]) for k in ("affiliation", "affiliation2") if a.get(k))
            star = "*" if i == corr else ""
            line = f"\\author{star}[{labels}]{{\\fnm{{{tex_escape(fnm)}}} \\sur{{{tex_escape(sur)}}}}}"
            if a.get("email"):
                line += f"\\email{{{a['email']}}}"
            out.append(line)
        for aff, i in idx.items():
            star = "*" if authors[corr].get("affiliation") == aff else ""
            out.append(f"\\affil{star}[{i}]{{\\orgname{{{tex_escape(aff.rstrip('.'))}}}}}")
    elif cls == "ieeetran":
        names = []
        for a in authors:
            thanks = f"\\thanks{{{tex_escape(a['name'])} is with {tex_escape(a.get('affiliation', ''))}" + (f" (e-mail: {a['email']})" if a.get("email") else "") + ".}"
            names.append(tex_escape(a["name"]) + thanks)
        out.append("\\author{" + ", ".join(names) + "}")
    else:
        out.append("\\author{" + " \\and ".join(tex_escape(a["name"]) + (f"\\\\{tex_escape(a.get('affiliation', ''))}" if a.get("affiliation") else "") for a in authors) + "}")
    return "\n".join(out) + "\n"


def drop_regions(body: str, names: List[str]) -> str:
    for n in names:
        body = re.sub(r"%\s*\{\{begin:" + re.escape(n) + r"\}\}.*?%\s*\{\{end:" + re.escape(n) + r"\}\}\s*", "", body, flags=re.S)
    return body


def cite_style(body: str, cls: str) -> str:
    if cls in ("elsarticle", "sn-jnl"):
        return body
    return re.sub(r"\\citep\b", r"\\cite", re.sub(r"\\citet\b", r"\\cite", body))


def render_target(spec: dict, name: str, t: dict, root: Path, force: bool) -> Optional[Path]:
    out = root / t["out"]
    out.mkdir(parents=True, exist_ok=True)
    template = (root / t["template"]).read_text(encoding="utf-8")
    body = (root / spec["body"]).read_text(encoding="utf-8")
    body = cite_style(drop_regions(body, t.get("drop") or []), t.get("class", "generic"))
    abstract = (root / spec["abstract"]).read_text(encoding="utf-8").strip() if spec.get("abstract") else ""
    keywords = [k.strip() for k in (root / spec["keywords"]).read_text(encoding="utf-8").splitlines() if k.strip()] if spec.get("keywords") else []
    if t.get("max_keywords") and len(keywords) > int(t["max_keywords"]):
        print(f"  {name}: {len(keywords)} keywords exceeds the cap {t['max_keywords']}; the extra are dropped from this target and listed in the report")
        keywords = keywords[:int(t["max_keywords"])]
    authors = render_authors(load_authors(root / spec["authors"]), t.get("class", "generic")) if spec.get("authors") else "% [AUTHOR INPUT: authors]\n"
    bibfile = Path(spec["bib"]).stem if spec.get("bib") else "refs"
    kw_sep = t.get("keyword_sep", ", ")
    main = (template.replace("{{ABSTRACT}}", abstract).replace("{{KEYWORDS}}", kw_sep.join(keywords))
            .replace("{{AUTHORS}}", authors).replace("{{BODY}}", body).replace("{{BIBFILE}}", bibfile))
    # unresolved placeholders in the template are a spec error, not a manuscript placeholder
    left = re.findall(r"\{\{[A-Z_]+\}\}", main)
    if left:
        print(f"  {name}: template still has {sorted(set(left))}; add them to the spec or remove them from the template")
    target = out / "main.tex"
    record = out / ".main.tex.rendered"
    if target.exists() and record.exists() and target.read_text(encoding="utf-8") != record.read_text(encoding="utf-8") and not force:
        (out / "main.tex.regenerated").write_text(main, encoding="utf-8", newline="\n")
        print(f"  {name}: main.tex was edited by hand since the last render; wrote main.tex.regenerated instead. "
              f"Move the hand edit into the body or the template, or pass --force.")
        return None
    target.write_text(main, encoding="utf-8", newline="\n")
    record.write_text(main, encoding="utf-8", newline="\n")
    for asset in t.get("assets") or []:
        src = root / asset
        if src.is_dir():
            shutil.copytree(src, out / src.name, dirs_exist_ok=True)
        elif src.exists():
            shutil.copy2(src, out / src.name)
        else:
            print(f"  {name}: asset {asset} not found")
    if spec.get("bib"):
        shutil.copy2(root / spec["bib"], out / Path(spec["bib"]).name)
    if spec.get("figures") and (root / spec["figures"]).is_dir():
        shutil.copytree(root / spec["figures"], out / "figures", dirs_exist_ok=True)
    print(f"  {name}: rendered {target} ({len(main.split())} words incl. markup)")
    return target


def self_test() -> int:
    ok = True

    def check(desc: str, cond: bool) -> None:
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + desc)
        ok = ok and cond

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "paper").mkdir(); (root / "templates").mkdir(); (root / "docs").mkdir()
        (root / "paper" / "body.tex").write_text("\\section{Intro}\nText \\citep{a}.\n% {{begin:appendix}}\n\\section{Appendix}\nlong\n% {{end:appendix}}\n", encoding="utf-8")
        (root / "paper" / "abstract.tex").write_text("An abstract.", encoding="utf-8")
        (root / "paper" / "keywords.tex").write_text("one\ntwo\nthree\n", encoding="utf-8")
        (root / "paper" / "refs.bib").write_text("@article{a, title={T}}", encoding="utf-8")
        (root / "docs" / "AUTHORS.yaml").write_text("corresponding: 2\nauthors:\n  - name: Anay Sinhal\n    email: sinhal.anay@ufl.edu\n    affiliation: University of Florida\n  - name: Arpana Sinhal\n    email: arpana.sinhal@jaipur.manipal.edu\n    affiliation: Manipal University Jaipur\n", encoding="utf-8")
        (root / "templates" / "els.tex").write_text("\\documentclass{elsarticle}\n{{AUTHORS}}\\begin{abstract}{{ABSTRACT}}\\end{abstract}\\begin{keyword}{{KEYWORDS}}\\end{keyword}\n\\begin{document}{{BODY}}\\bibliography{{{BIBFILE}}}\\end{document}", encoding="utf-8")
        (root / "templates" / "ieee.tex").write_text("\\documentclass{IEEEtran}\n{{AUTHORS}}\n\\begin{document}{{BODY}}\\end{document}", encoding="utf-8")
        spec = {"body": "paper/body.tex", "abstract": "paper/abstract.tex", "keywords": "paper/keywords.tex", "authors": "docs/AUTHORS.yaml", "bib": "paper/refs.bib",
                "targets": {"cep": {"template": "templates/els.tex", "out": "sub/cep", "class": "elsarticle", "max_keywords": 2},
                            "tcst": {"template": "templates/ieee.tex", "out": "sub/tcst", "class": "ieeetran", "drop": ["appendix"]}}}
        t1 = render_target(spec, "cep", spec["targets"]["cep"], root, False)
        t2 = render_target(spec, "tcst", spec["targets"]["tcst"], root, False)
        m1 = t1.read_text(encoding="utf-8"); m2 = t2.read_text(encoding="utf-8")
        check("elsarticle: corref on author 2, ead lines, affiliations, keywords capped", "Arpana Sinhal\\corref{cor1}" in m1 and "\\ead{sinhal.anay@ufl.edu}" in m1 and "organization={University of Florida}" in m1 and "one, two" in m1 and "three" not in m1.split("keyword}")[1])
        check("elsarticle keeps citep; appendix kept", "\\citep{a}" in m1 and "Appendix" in m1)
        check("ieee: cite rewritten, appendix dropped, thanks blocks", "\\cite{a}" in m2 and "Appendix" not in m2 and "\\thanks{Anay Sinhal is with University of Florida" in m2)
        check("bib copied", (root / "sub" / "cep" / "refs.bib").exists())
        t1.write_text(m1 + "\n% hand edit\n", encoding="utf-8")
        r = render_target(spec, "cep", spec["targets"]["cep"], root, False)
        check("guard: hand-edited main.tex not overwritten; .regenerated written", r is None and (root / "sub" / "cep" / "main.tex.regenerated").exists() and "% hand edit" in t1.read_text(encoding="utf-8"))
        r2 = render_target(spec, "cep", spec["targets"]["cep"], root, True)
        check("--force overwrites", r2 is not None and "% hand edit" not in t1.read_text(encoding="utf-8"))
        sn = render_authors(load_authors(root / "docs" / "AUTHORS.yaml"), "sn-jnl")
        check("sn-jnl: starred corresponding author and affil", "\\author*[2]{\\fnm{Arpana} \\sur{Sinhal}}" in sn and "\\affil*[2]" in sn)
    print("\nself-test " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):
            pass
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("spec", nargs="?", help="targets.yaml or .json")
    p.add_argument("--only", action="append", default=[], help="render only this target; repeatable")
    p.add_argument("--force", action="store_true", help="overwrite a hand-edited main.tex")
    p.add_argument("--check", action="store_true", help="run build-check on each rendered target with its page_cap")
    p.add_argument("--build-check", default="", help="path to build_check.py (default: sibling build-check skill)")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.spec:
        p.error("give the spec (or --self-test)")
    spec_path = Path(a.spec)
    spec = load_spec(spec_path)
    root = spec_path.parent
    rendered: Dict[str, Path] = {}
    for name, t in (spec.get("targets") or {}).items():
        if a.only and name not in a.only:
            continue
        r = render_target(spec, name, t, root, a.force)
        if r is not None:
            rendered[name] = r
    if a.check and rendered:
        bc = Path(a.build_check) if a.build_check else Path(__file__).resolve().parent.parent.parent / "build-check" / "scripts" / "build_check.py"
        if not bc.exists():
            print(f"build-check not found at {bc}; pass --build-check")
            return 1
        rc_all = 0
        for name, main in rendered.items():
            cap = int((spec["targets"][name].get("page_cap") or 0))
            cmd = [sys.executable, str(bc), str(main)] + (["--max-pages", str(cap)] if cap else [])
            if spec.get("authors"):
                cmd += ["--authors", str(root / spec["authors"])]
            print(f"\n== build-check {name}")
            rc_all |= subprocess.call(cmd)
        return 1 if rc_all else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
