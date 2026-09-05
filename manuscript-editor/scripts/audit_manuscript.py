#!/usr/bin/env python3
"""
audit_manuscript.py - mechanical checks for manuscript coherence and boundary leaks.

Stdlib only. Reads .md, .tex, .txt, or .docx and reports:

  1. Section outline with word counts and share of body text
  2. Revision-commentary leaks (reviewer-facing language inside the manuscript)
  3. Near-duplicate sentences across the manuscript
  4. Terminology variants (hyphenation, spacing, US/UK spelling)
  5. Acronym problems (defined more than once, used before definition, defined but rare)
  6. Display-item references (figures/tables referenced but no caption, captioned but never referenced, out-of-order first mention)
  7. Hedge and meta-commentary density, with hedge-stacked sentences
  8. Numbers in the abstract that do not appear in the body
  9. Outstanding placeholders

Everything here is a pointer for a human-quality read, not a verdict. The script
cannot see semantic duplication or a contradiction in claim strength; the
coherence pass in references/coherence-audit.md covers those by hand.

Usage:
  python audit_manuscript.py paper.md
  python audit_manuscript.py paper.tex --report report.md
  python audit_manuscript.py paper.docx --json > audit.json
  python audit_manuscript.py paper.md --strict      # exit 1 if any leak is found
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from xml.etree import ElementTree as ET

# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

HEADING_WORDS = {
    "abstract", "summary", "introduction", "background", "related work",
    "methods", "materials and methods", "method", "methodology", "results",
    "discussion", "conclusion", "conclusions", "limitations", "acknowledgements",
    "acknowledgments", "references", "supplementary", "appendix",
    "data availability", "code availability", "author contributions",
    "competing interests", "funding", "ethics", "experiments", "evaluation",
    "experimental setup", "future work", "conclusion and future work",
}

SKIP_SECTIONS = {
    "references", "bibliography", "acknowledgements", "acknowledgments",
    "author contributions", "competing interests", "funding",
    "conflict of interest", "declarations",
}


def read_docx(path: str) -> list[tuple[str, str]]:
    """Return list of (kind, text) where kind is 'heading' or 'para'."""
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    out = []
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    for p in root.iter("{%s}p" % ns["w"]):
        style = p.find("w:pPr/w:pStyle", ns)
        style_val = style.get("{%s}val" % ns["w"]) if style is not None else ""
        text = "".join(t.text or "" for t in p.iter("{%s}t" % ns["w"])).strip()
        if not text:
            continue
        kind = "heading" if re.match(r"(?i)heading\d|title", style_val or "") else "para"
        out.append((kind, text))
    return out


def strip_tex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)  # comments
    text = re.sub(r"\\begin\{(equation|align|figure|table|tabular)\*?\}.*?\\end\{\1\*?\}",
                  lambda m: keep_captions(m.group(0)), text, flags=re.S)
    text = re.sub(r"\\(?:cite[tp]?|citep|citet|parencite|textcite)\*?(?:\[[^\]]*\])*\{([^}]*)\}", r" CITE:\1 ", text)
    text = re.sub(r"\\(?:ref|eqref|autoref|cref|Cref|pageref)\*?\{([^}]*)\}", lambda m: " " + " ".join("REF:" + k.strip() for k in m.group(1).split(",")) + " ", text)
    text = re.sub(r"\\label\{([^}]*)\}", r" LABEL:\1 ", text)
    text = re.sub(r"\\(textbf|textit|emph|texttt|underline)\{([^}]*)\}", r"\2", text)
    text = re.sub(r"\$[^$]*\$", " EQN ", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", text)
    text = re.sub(r"[{}]", "", text)
    return text


def keep_captions(block: str) -> str:
    caps = re.findall(r"\\caption\{(.*?)\}\s*(?:\\label\{([^}]*)\})?", block, flags=re.S)
    labels = re.findall(r"\\label\{([^}]*)\}", block)
    parts = []
    for cap, _ in caps:
        parts.append("CAPTION: " + cap)
    for lab in labels:
        parts.append(" LABEL:%s " % lab)
    return "\n".join(parts)


def read_tex(path: str) -> list[tuple[str, str]]:
    raw = open(path, encoding="utf-8", errors="replace").read()
    out = []
    pattern = re.compile(r"\\(section|subsection|subsubsection|paragraph|chapter)\*?\{([^}]*)\}")
    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", raw, flags=re.S)
    if abstract:
        out.append(("heading", "Abstract"))
        for para in split_paras(strip_tex(abstract.group(1))):
            out.append(("para", para))
        raw = raw.replace(abstract.group(0), "")
    pos = 0
    for m in pattern.finditer(raw):
        chunk = raw[pos:m.start()]
        for para in split_paras(strip_tex(chunk)):
            out.append(("para", para))
        out.append(("heading", m.group(2).strip()))
        pos = m.end()
    for para in split_paras(strip_tex(raw[pos:])):
        out.append(("para", para))
    return out


def read_md(path: str) -> list[tuple[str, str]]:
    out = []
    buf = []
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        h = re.match(r"^(#{1,6})\s+(.*)$", line)
        if h:
            if buf:
                out.append(("para", " ".join(buf).strip()))
                buf = []
            out.append(("heading", h.group(2).strip()))
        elif not line.strip():
            if buf:
                out.append(("para", " ".join(buf).strip()))
                buf = []
        else:
            buf.append(line.strip())
    if buf:
        out.append(("para", " ".join(buf).strip()))
    return [(k, t) for k, t in out if t]


def read_txt(path: str) -> list[tuple[str, str]]:
    out = []
    buf = []
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.rstrip("\n")
        s = line.strip()
        looks_heading = (
            s and len(s.split()) <= 8 and not s.endswith((".", ",", ";", ":"))
            and (s.lower().rstrip(".") in HEADING_WORDS
                 or re.match(r"^(\d+(\.\d+)*\.?|[IVX]+\.)\s+\S", s))
        )
        if looks_heading:
            if buf:
                out.append(("para", " ".join(buf).strip()))
                buf = []
            out.append(("heading", re.sub(r"^(\d+(\.\d+)*\.?|[IVX]+\.)\s+", "", s)))
        elif not s:
            if buf:
                out.append(("para", " ".join(buf).strip()))
                buf = []
        else:
            buf.append(s)
    if buf:
        out.append(("para", " ".join(buf).strip()))
    return out


def split_paras(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def load(path: str) -> list[tuple[str, str]]:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return read_docx(path)
    if ext == ".tex":
        return read_tex(path)
    if ext in (".md", ".markdown"):
        return read_md(path)
    return read_txt(path)


# --------------------------------------------------------------------------- #
# Structure
# --------------------------------------------------------------------------- #

class Section:
    def __init__(self, title: str, index: int):
        self.title = title
        self.index = index
        self.paras: list[str] = []

    @property
    def text(self) -> str:
        return "\n".join(self.paras)

    @property
    def words(self) -> int:
        return len(re.findall(r"\b\w+\b", self.text))

    @property
    def key(self) -> str:
        return re.sub(r"^[\d.\s]+", "", self.title).strip().lower()


def build_sections(blocks: list[tuple[str, str]]) -> list[Section]:
    sections: list[Section] = []
    current = Section("(front matter)", 0)
    for kind, text in blocks:
        if kind == "heading":
            if current.paras or sections:
                sections.append(current)
            current = Section(text, len(sections) + 1)
        else:
            current.paras.append(text)
    sections.append(current)
    return [s for s in sections if s.paras or s.title != "(front matter)"]


def sentences(text: str) -> list[str]:
    text = re.sub(r"\b(e\.g|i\.e|et al|Fig|Figs|Eq|Eqs|vs|cf|approx|resp|Dr|Prof|No)\.", r"\1<DOT>", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(\[\"'])", text)
    return [p.replace("<DOT>", ".").strip() for p in parts if p.strip()]


def is_body_section(sec: Section) -> bool:
    k = sec.key
    return not any(k == s or k.startswith(s) for s in SKIP_SECTIONS)


def find_abstract(sections: list[Section]) -> Section | None:
    for s in sections:
        if s.key in ("abstract", "summary"):
            return s
    return None


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

LEAK_PATTERNS = [
    # attribution to the review process
    r"\b(the|a|one|this|another|our)\s+(reviewer|referee)s?\b",
    r"\breviewer\s*#?\s*\d\b", r"\breferee\s*#?\s*\d\b",
    r"\bas\s+(suggested|requested|recommended|pointed out|noted|raised)\s+by\b",
    r"\bin\s+response\s+to\b", r"\bper\s+the\s+(reviewer|referee|editor)",
    r"\bto\s+address\s+(this|the|a)\s+(concern|comment|point|criticism|reviewer)",
    r"\bthe\s+editor\b", r"\bwe\s+thank\b", r"\bwe\s+are\s+grateful\b",
    # narration of the editing history
    r"\bwe\s+have\s+(now\s+)?(added|revised|clarified|expanded|rewritten|updated|corrected|included|removed|moved|reworded|modified|reorganized|reorganised)\b",
    r"\bhas\s+been\s+(added|revised|clarified|expanded|rewritten|updated|corrected|reworded|moved|reorganized|reorganised)\b",
    r"\bhave\s+been\s+(added|revised|clarified|expanded|rewritten|updated|corrected|reworded|moved)\b",
    r"\b(newly|now)\s+(added|included|clarified|revised|expanded|reported)\b",
    r"\bin\s+(the|this)\s+(revised|current|new|updated)\s+(version|manuscript|draft|submission)\b",
    r"\b(previous|original|earlier|initial|first)\s+(version|submission|draft|manuscript)\b",
    r"\bin\s+this\s+revision\b", r"\bupon\s+revision\b", r"\bafter\s+revision\b",
    r"\bfor\s+clarity,?\s+we\s+(have|now)\b",
    r"\bto\s+clarify\s+(this|the)\s+(point|issue|concern)\b",
    r"\bwe\s+agree\s+that\b", r"\bwe\s+acknowledge\s+the\s+(reviewer|referee|concern|comment)",
    r"\b(page|line)s?\s+\d+\s*[-,]\s*\d+\b",   # page/line references belong in the response letter
]

HEDGE_PATTERNS = [
    r"\bit\s+is\s+(important|worth|interesting|crucial|essential|necessary)\s+to\s+(note|mention|emphasi[sz]e|highlight|point\s+out)\b",
    r"\bit\s+should\s+be\s+(noted|emphasi[sz]ed|mentioned|highlighted|stressed)\b",
    r"\bnote\s+that\b", r"\bnotably\b", r"\bimportantly\b", r"\binterestingly\b",
    r"\bwe\s+(would\s+like\s+to\s+)?(emphasi[sz]e|stress|highlight|note|point\s+out|acknowledge|recogni[sz]e)\s+that\b",
    r"\bto\s+the\s+best\s+of\s+our\s+knowledge\b", r"\bas\s+(mentioned|noted|discussed|described|stated|shown)\s+(above|earlier|previously|before)\b",
    r"\bit\s+is\s+(clear|evident|obvious)\s+that\b",
    r"\bmay\s+potentially\b", r"\bcould\s+possibly\b", r"\bmight\s+possibly\b",
    r"\bin\s+this\s+(section|subsection|paragraph),?\s+we\b",
    r"\bthis\s+(section|subsection)\s+(describes|presents|discusses|clarifies|explains)\b",
    r"\bwhile\s+(we|our|this|it)\b.*\b(may|might|could)\b.*\b(however|nevertheless|nonetheless)\b",
]

SOFT_HEDGES = [r"\bmay\b", r"\bmight\b", r"\bcould\b", r"\bpossibly\b", r"\bpotentially\b",
               r"\bperhaps\b", r"\bsomewhat\b", r"\brelatively\b", r"\bto some extent\b",
               r"\bit is possible that\b", r"\bappears? to\b", r"\bseems? to\b"]

PLACEHOLDER_PATTERNS = [r"\[AUTHOR[ _-]?INPUT[^\]]*\]", r"\[(TODO|TBD|CITE|CITATION NEEDED|VERIFY|XX+)[^\]]*\]",
                        r"\bTODO\b", r"\bTBD\b", r"\bXXX+\b", r"\?\?\?", r"\[\?\]", r"\\todo\{"]

UK_US = [
    ("analyse", "analyze"), ("analysed", "analyzed"), ("analysing", "analyzing"),
    ("behaviour", "behavior"), ("colour", "color"), ("centre", "center"),
    ("modelling", "modeling"), ("modelled", "modeled"), ("labelled", "labeled"),
    ("labelling", "labeling"), ("optimisation", "optimization"), ("optimise", "optimize"),
    ("normalisation", "normalization"), ("normalise", "normalize"), ("generalisation", "generalization"),
    ("generalise", "generalize"), ("characterise", "characterize"), ("characterisation", "characterization"),
    ("minimise", "minimize"), ("maximise", "maximize"), ("randomised", "randomized"),
    ("randomisation", "randomization"), ("standardised", "standardized"), ("utilisation", "utilization"),
    ("visualisation", "visualization"), ("organisation", "organization"), ("recognise", "recognize"),
    ("programme", "program"), ("tumour", "tumor"), ("favour", "favor"), ("grey", "gray"),
    ("fibre", "fiber"), ("litre", "liter"), ("metre", "meter"), ("haemoglobin", "hemoglobin"),
    ("oedema", "edema"), ("anaemia", "anemia"), ("paediatric", "pediatric"), ("oestrogen", "estrogen"),
]

COMMON_ACRONYMS = {"USA", "UK", "EU", "US", "AI", "ML", "DNA", "RNA", "PCR", "MRI", "CT", "ECG", "EEG",
                   "CPU", "GPU", "API", "HTML", "PDF", "URL", "ID", "IQR", "SD", "CI", "SE", "OR",
                   "HR", "RR", "AUC", "ROC", "ANOVA", "IRB", "NIH", "WHO", "FDA", "GDPR", "HIPAA",
                   "ICU", "ED", "EHR", "EMR", "BMI", "IEEE", "ACM", "ISO", "GPT", "LLM", "CNN", "RNN",
                   "LSTM", "SVM", "MLP", "ReLU", "GAN", "VAE", "SGD", "ADAM", "MSE", "MAE", "RMSE",
                   "MAP", "NLP", "OCR", "GIS", "GPS", "IT", "PhD", "MD", "BSc", "MSc", "III", "II", "IV",
                   "VI", "VII", "EQN", "CAPTION"}


def mask_placeholders(text: str) -> str:
    """Placeholders are author-facing notes and may legitimately name reviewers."""
    return re.sub(r"\[(AUTHOR[ _-]?INPUT|TODO|TBD|CITE|VERIFY)[^\]]*\]", " PLACEHOLDER ", text, flags=re.I)


def check_leaks(sections: list[Section]) -> list[dict]:
    hits = []
    compiled = [re.compile(p, re.I) for p in LEAK_PATTERNS]
    for sec in sections:
        if not is_body_section(sec):
            continue
        for pi, para in enumerate(sec.paras):
            for sent in sentences(mask_placeholders(para)):
                for rx in compiled:
                    m = rx.search(sent)
                    if m:
                        hits.append({"section": sec.title, "para": pi + 1, "match": m.group(0),
                                     "sentence": sent[:240]})
                        break
    return hits


def normalize_sentence(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\b(cite|ref|label):\S+|\[\d+(,\s*\d+)*\]|\(\w+ et al\.,? \d{4}\)", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def shingles(tokens: list[str], k: int = 4) -> set[tuple[str, ...]]:
    return {tuple(tokens[i:i + k]) for i in range(max(0, len(tokens) - k + 1))}


def check_duplicates(sections: list[Section], threshold: float = 0.72, min_words: int = 9) -> list[dict]:
    """Candidate pairs share at least two 4-gram shingles; confirm with SequenceMatcher."""
    items = []
    for sec in sections:
        if not is_body_section(sec):
            continue
        for pi, para in enumerate(sec.paras):
            for sent in sentences(para):
                norm = normalize_sentence(sent)
                toks = norm.split()
                if len(toks) < min_words:
                    continue
                items.append({"section": sec.title, "para": pi + 1, "sentence": sent, "norm": norm,
                              "toks": toks})
    index: dict[tuple[str, ...], list[int]] = defaultdict(list)
    for i, it in enumerate(items):
        for sh in shingles(it["toks"]):
            index[sh].append(i)
    pair_counts: Counter = Counter()
    for sh, ids in index.items():
        if len(ids) > 12:  # boilerplate n-gram, ignore
            continue
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                pair_counts[(ids[a], ids[b])] += 1
    dups = []
    seen = set()
    for (a, b), c in pair_counts.items():
        if c < 2 or (a, b) in seen:
            continue
        seen.add((a, b))
        ratio = SequenceMatcher(None, items[a]["norm"], items[b]["norm"]).ratio()
        if ratio >= threshold:
            same_place = items[a]["section"] == items[b]["section"] and items[a]["para"] == items[b]["para"]
            abstract_pair = any(it["section"].strip().lower() in ("abstract", "summary") for it in (items[a], items[b]))
            dups.append({"similarity": round(ratio, 2), "same_paragraph": same_place,
                         "involves_abstract": abstract_pair,
                         "a": {"section": items[a]["section"], "para": items[a]["para"],
                               "sentence": items[a]["sentence"][:200]},
                         "b": {"section": items[b]["section"], "para": items[b]["para"],
                               "sentence": items[b]["sentence"][:200]}})
    dups.sort(key=lambda d: (d["involves_abstract"], -d["similarity"]))
    return dups


def check_terminology(full_text: str) -> list[dict]:
    text = full_text
    lower = text.lower()
    findings = []
    # hyphen / space / joined variants of compounds
    words = re.findall(r"[A-Za-z]+(?:-[A-Za-z]+)+|[A-Za-z]+", text)
    joined_forms: dict[str, Counter] = defaultdict(Counter)
    for w in words:
        if "-" in w:
            joined_forms[w.replace("-", "").lower()][w.lower()] += 1
    # count unhyphenated joined and spaced forms for those compounds
    for key, forms in joined_forms.items():
        n_joined = len(re.findall(r"\b%s\b" % re.escape(key), lower))
        if n_joined:
            forms[key] += n_joined
        parts = list(forms)[0].split("-")
        spaced = " ".join(parts)
        n_spaced = len(re.findall(r"\b%s\b" % re.escape(spaced), lower))
        if n_spaced:
            forms[spaced] += n_spaced
        if len([f for f, c in forms.items() if c > 0]) > 1 and sum(forms.values()) >= 2:
            findings.append({"type": "compound", "forms": dict(forms)})
    # spelling variants
    for uk, us in UK_US:
        n_uk = len(re.findall(r"\b%s\b" % uk, lower))
        n_us = len(re.findall(r"\b%s\b" % us, lower))
        if n_uk and n_us:
            findings.append({"type": "spelling", "forms": {uk: n_uk, us: n_us}})
    # capitalisation variants of multiword proper-ish terms (e.g. Random Forest vs random forest)
    caps: dict[str, Counter] = defaultdict(Counter)
    for m in re.finditer(r"\b([A-Za-z][a-z]+(?:\s[A-Za-z][a-z]+){1,2})\b", text):
        phrase = m.group(1)
        if any(ch.isupper() for ch in phrase[1:]):
            caps[phrase.lower()][phrase] += 1
    for key, forms in caps.items():
        n_lower = len(re.findall(r"\b%s\b" % re.escape(key), text))
        if n_lower:
            forms[key] += n_lower
        if len(forms) > 1 and sum(forms.values()) >= 3 and max(forms.values()) < sum(forms.values()):
            findings.append({"type": "capitalization", "forms": dict(forms)})
    return findings


def check_acronyms(sections: list[Section]) -> dict:
    definitions: dict[str, list[str]] = defaultdict(list)
    first_use: dict[str, str] = {}
    use_count: Counter = Counter()
    order = []
    for sec in sections:
        if not is_body_section(sec):
            continue
        for m in re.finditer(r"\(([A-Z][A-Za-z0-9]{1,7})s?\)", sec.text):
            acr = m.group(1)
            if acr in COMMON_ACRONYMS or not any(c.isupper() for c in acr[1:]):
                continue
            definitions[acr].append(sec.title)
        for m in re.finditer(r"\b([A-Z][A-Z0-9]{1,6})s?\b", sec.text):
            acr = m.group(1)
            if acr in COMMON_ACRONYMS or acr.isdigit():
                continue
            use_count[acr] += 1
            if acr not in first_use:
                first_use[acr] = sec.title
                order.append(acr)
    abstract = find_abstract(sections)
    abstract_title = abstract.title if abstract else None
    multi = {a: secs for a, secs in definitions.items() if len(secs) > 1
             and not (abstract_title and secs[0] == abstract_title and len(secs) == 2)}
    undefined = [a for a in order if a not in definitions and use_count[a] >= 3]
    rare_defined = [a for a in definitions if use_count[a] <= 2]
    return {"defined_more_than_once": multi, "used_3plus_never_defined": undefined,
            "defined_but_rarely_used": rare_defined}


def check_display_items(sections: list[Section]) -> dict:
    refs_order: list[str] = []
    captions: set[str] = set()
    label_map: dict[str, str] = {}
    body = "\n".join(s.text for s in sections if is_body_section(s))
    # captions
    for m in re.finditer(r"(?:^|(?<=\n)|(?<=[.!?] )|CAPTION:\s*)(Fig(?:ure)?\.?|Table|Extended Data Fig(?:ure)?\.?|Supplementary (?:Fig(?:ure)?\.?|Table))\s*(S?\d+)[.:]", body):
        kind = "Table" if m.group(1).startswith("Table") else ("Fig" if m.group(1).startswith("Fig") else m.group(1))
        captions.add("%s %s" % (kind, m.group(2)))
    for m in re.finditer(r"LABEL:((fig|tab|table|figure)[:_-]?\S*)", body):
        label_map[m.group(1)] = "Table" if m.group(2).startswith("tab") else "Fig"
    # references
    for m in re.finditer(r"\b(Fig(?:ure)?s?\.?|Tables?)\s*~?\s*(S?\d+)", body):
        kind = "Table" if m.group(1).startswith("Table") else "Fig"
        key = "%s %s" % (kind, m.group(2))
        if key not in refs_order:
            refs_order.append(key)
    for m in re.finditer(r"REF:((fig|tab|table|figure)[:_-]?\S*)", body):
        key = m.group(1)
        if key not in refs_order:
            refs_order.append(key)
    if label_map:
        captions |= set(label_map)
    referenced_no_caption = [r for r in refs_order if r not in captions and not r.startswith(("fig", "tab"))]
    if label_map:
        referenced_no_caption += [r for r in refs_order if r.startswith(("fig", "tab")) and r not in label_map]
    captioned_not_referenced = sorted(c for c in captions if c not in refs_order)
    out_of_order = []
    for kind in ("Fig", "Table"):
        nums = [int(re.sub(r"\D", "", r)) for r in refs_order if r.startswith(kind) and re.search(r"\d", r)
                and not r.startswith(kind + " S")]
        for i in range(1, len(nums)):
            if nums[i] < max(nums[:i]) and nums[i] not in nums[:i]:
                out_of_order.append("%s %d first mentioned after %s %d" % (kind, nums[i], kind, max(nums[:i])))
    return {"first_mention_order": refs_order, "referenced_without_caption": referenced_no_caption,
            "captioned_never_referenced": captioned_not_referenced, "out_of_order_first_mention": out_of_order}


def check_hedges(sections: list[Section]) -> dict:
    compiled = [re.compile(p, re.I) for p in HEDGE_PATTERNS]
    soft = [re.compile(p, re.I) for p in SOFT_HEDGES]
    meta_hits = []
    stacked = []
    total_words = 0
    per_section = {}
    for sec in sections:
        if not is_body_section(sec):
            continue
        total_words += sec.words
        count = 0
        for pi, para in enumerate(sec.paras):
            for sent in sentences(para):
                for rx in compiled:
                    m = rx.search(sent)
                    if m:
                        count += 1
                        meta_hits.append({"section": sec.title, "para": pi + 1, "match": m.group(0),
                                          "sentence": sent[:200]})
                        break
                n_soft = sum(1 for rx in soft if rx.search(sent))
                if n_soft >= 3:
                    stacked.append({"section": sec.title, "para": pi + 1, "hedges": n_soft,
                                    "sentence": sent[:200]})
        per_section[sec.title] = round(1000.0 * count / sec.words, 1) if sec.words else 0.0
    density = round(1000.0 * len(meta_hits) / total_words, 1) if total_words else 0.0
    return {"meta_commentary_per_1000_words": density, "per_section": per_section,
            "meta_commentary": meta_hits, "hedge_stacked_sentences": stacked}


def check_abstract_numbers(sections: list[Section]) -> list[str]:
    abstract = find_abstract(sections)
    if not abstract:
        return []
    body = " ".join(s.text for s in sections if s is not abstract and is_body_section(s))
    body = re.sub(r"(\d),(\d{3})", r"\1\2", body)
    nums = set(re.findall(r"(?<![\w.])\d{1,3}(?:,\d{3})+(?:\.\d+)?%?|(?<![\w.])\d+(?:\.\d+)?%?(?![\w.])", abstract.text))
    missing = []
    for n in sorted(nums, key=lambda x: float(x.rstrip("%").replace(",", ""))):
        bare = n.rstrip("%").replace(",", "")
        if float(bare) < 3 and "." not in bare:  # skip 1, 2 (counts of things, section numbers)
            continue
        if not re.search(r"(?<![\w.])%s(?![\w.])" % re.escape(bare), body):
            missing.append(n)
    return missing


def check_placeholders(sections: list[Section]) -> list[dict]:
    hits = []
    compiled = [re.compile(p, re.I) for p in PLACEHOLDER_PATTERNS]
    for sec in sections:
        for pi, para in enumerate(sec.paras):
            for rx in compiled:
                for m in rx.finditer(para):
                    hits.append({"section": sec.title, "para": pi + 1, "text": m.group(0)[:120]})
    return hits


def section_proportions(sections: list[Section]) -> list[str]:
    notes = []
    body = {s.key: s.words for s in sections if is_body_section(s)}
    total = sum(v for k, v in body.items() if k not in ("abstract", "summary"))
    if not total:
        return notes

    def w(*keys):
        return sum(v for k, v in body.items() if any(k == kk or k.startswith(kk) for kk in keys))

    intro = w("introduction", "background")
    results = w("results", "experiments", "evaluation", "findings")
    disc = w("discussion")
    concl = w("conclusion")
    if intro and intro / total > 0.28:
        notes.append("Introduction/Background is %d%% of body text; above roughly a quarter usually means background that belongs in Related Work, Discussion, or nowhere." % round(100 * intro / total))
    if results and disc and disc > 1.5 * results:
        notes.append("Discussion (%d words) is more than 1.5x Results (%d words); check for restated results or restated background." % (disc, results))
    if concl and concl / total > 0.10:
        notes.append("Conclusion is %d%% of body text; conclusions above ~10%% usually repeat the Discussion." % round(100 * concl / total))
    return notes


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #

def run(path: str) -> dict:
    blocks = load(path)
    sections = build_sections(blocks)
    full_text = "\n".join(s.text for s in sections if is_body_section(s))
    result = {
        "file": os.path.basename(path),
        "outline": [{"index": s.index, "title": s.title, "words": s.words} for s in sections],
        "total_body_words": sum(s.words for s in sections if is_body_section(s)),
        "proportion_notes": section_proportions(sections),
        "revision_commentary_leaks": check_leaks(sections),
        "near_duplicate_sentences": check_duplicates(sections),
        "terminology_variants": check_terminology(full_text),
        "acronyms": check_acronyms(sections),
        "display_items": check_display_items(sections),
        "hedging": check_hedges(sections),
        "abstract_numbers_missing_from_body": check_abstract_numbers(sections),
        "placeholders": check_placeholders(sections),
    }
    return result


def to_markdown(r: dict) -> str:
    L = []
    L.append("# Manuscript audit: %s" % r["file"])
    L.append("")
    L.append("Body words (excluding references, acknowledgements, declarations): %d" % r["total_body_words"])
    L.append("")
    L.append("## 1. Outline")
    L.append("")
    L.append("| # | Section | Words | Share |")
    L.append("|---|---|---|---|")
    tot = r["total_body_words"] or 1
    for s in r["outline"]:
        L.append("| %d | %s | %d | %d%% |" % (s["index"], s["title"], s["words"], round(100 * s["words"] / tot)))
    for n in r["proportion_notes"]:
        L.append("")
        L.append("- " + n)
    L.append("")
    leaks = r["revision_commentary_leaks"]
    L.append("## 2. Revision-commentary leaks (%d)" % len(leaks))
    L.append("")
    if not leaks:
        L.append("None found. This check is pattern-based; still read Discussion and Methods for narrated changes.")
    for h in leaks:
        L.append("- **%s**, para %d, matched `%s`: %s" % (h["section"], h["para"], h["match"], h["sentence"]))
    L.append("")
    dups = r["near_duplicate_sentences"]
    L.append("## 3. Near-duplicate sentences (%d pairs)" % len(dups))
    L.append("")
    if not dups:
        L.append("None at the lexical level. Semantic duplication (same point, different words) needs the manual pass.")
    for d in dups[:40]:
        tag = " (same paragraph)" if d["same_paragraph"] else ""
        if d["involves_abstract"]:
            tag += " (abstract restatement: acceptable if the abstract stays self-contained and the body version carries the detail)"
        L.append("- similarity %.2f%s" % (d["similarity"], tag))
        L.append("  - %s, para %d: %s" % (d["a"]["section"], d["a"]["para"], d["a"]["sentence"]))
        L.append("  - %s, para %d: %s" % (d["b"]["section"], d["b"]["para"], d["b"]["sentence"]))
    if len(dups) > 40:
        L.append("- ... %d more pairs (see --json)" % (len(dups) - 40))
    L.append("")
    terms = r["terminology_variants"]
    L.append("## 4. Terminology variants (%d)" % len(terms))
    L.append("")
    for t in terms:
        forms = ", ".join("%s (%d)" % (f, c) for f, c in sorted(t["forms"].items(), key=lambda x: -x[1]))
        L.append("- %s: %s" % (t["type"], forms))
    if not terms:
        L.append("No hyphenation, spacing, spelling, or capitalization variants detected.")
    L.append("")
    a = r["acronyms"]
    L.append("## 5. Acronyms")
    L.append("")
    if a["defined_more_than_once"]:
        L.append("- Defined more than once: " + "; ".join("%s (%s)" % (k, ", ".join(v)) for k, v in a["defined_more_than_once"].items()))
    if a["used_3plus_never_defined"]:
        L.append("- Used 3+ times, never defined in text: " + ", ".join(a["used_3plus_never_defined"]))
    if a["defined_but_rarely_used"]:
        L.append("- Defined but used at most twice (consider spelling out): " + ", ".join(a["defined_but_rarely_used"]))
    if not any(a.values()):
        L.append("No acronym issues detected.")
    L.append("")
    d = r["display_items"]
    L.append("## 6. Display items")
    L.append("")
    L.append("- First-mention order: " + (", ".join(d["first_mention_order"]) or "none referenced"))
    if d["referenced_without_caption"]:
        L.append("- Referenced but no caption/label found: " + ", ".join(d["referenced_without_caption"]))
    if d["captioned_never_referenced"]:
        L.append("- Captioned/labelled but never referenced in text: " + ", ".join(d["captioned_never_referenced"]))
    for o in d["out_of_order_first_mention"]:
        L.append("- Out of order: " + o)
    L.append("")
    h = r["hedging"]
    L.append("## 7. Meta-commentary and hedging")
    L.append("")
    L.append("- Meta-commentary phrases per 1000 body words: %.1f (above ~3 usually reads defensive)" % h["meta_commentary_per_1000_words"])
    for m in h["meta_commentary"][:30]:
        L.append("  - %s, para %d, `%s`: %s" % (m["section"], m["para"], m["match"], m["sentence"]))
    if len(h["meta_commentary"]) > 30:
        L.append("  - ... %d more (see --json)" % (len(h["meta_commentary"]) - 30))
    if h["hedge_stacked_sentences"]:
        L.append("- Sentences with 3+ hedges (pick one hedge, or commit):")
        for s in h["hedge_stacked_sentences"][:20]:
            L.append("  - %s, para %d: %s" % (s["section"], s["para"], s["sentence"]))
    L.append("")
    L.append("## 8. Abstract numbers not found in body")
    L.append("")
    L.append(", ".join(r["abstract_numbers_missing_from_body"]) or "All abstract numbers appear in the body (or no abstract detected).")
    L.append("")
    p = r["placeholders"]
    L.append("## 9. Placeholders outstanding (%d)" % len(p))
    L.append("")
    for x in p:
        L.append("- %s, para %d: %s" % (x["section"], x["para"], x["text"]))
    if not p:
        L.append("None.")
    L.append("")
    L.append("---")
    L.append("Pattern-based checks only. Contradictions, claim-strength drift, broken transitions, and semantic duplication need the manual coherence pass (references/coherence-audit.md).")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="manuscript file (.md, .tex, .txt, .docx)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument("--report", help="write the markdown report to this path")
    ap.add_argument("--strict", action="store_true", help="exit 1 if any revision-commentary leak is found")
    args = ap.parse_args()
    if not os.path.exists(args.path):
        print("file not found: %s" % args.path, file=sys.stderr)
        return 2
    r = run(args.path)
    if args.json:
        print(json.dumps(r, indent=2))
    else:
        md = to_markdown(r)
        if args.report:
            with open(args.report, "w", encoding="utf-8") as f:
                f.write(md)
            print("report written to %s" % args.report)
        else:
            print(md)
    if args.strict and r["revision_commentary_leaks"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
