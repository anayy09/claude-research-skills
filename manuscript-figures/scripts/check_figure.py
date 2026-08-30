#!/usr/bin/env python3
"""Check a figure file against manuscript submission requirements.

Standard library only. Fails closed: anything it cannot verify is reported as
UNVERIFIED, never silently passed.

Checks by format:
  PDF   page width vs target column, font embedding, embedded raster warning
  EPS   bounding-box width vs target
  SVG   declared width vs target, mm-true viewBox hint
  PNG   pixel dims, DPI (pHYs chunk) vs floor, effective DPI at target width
  TIFF  pixel dims, DPI (resolution tags) vs floor, effective DPI at target

Usage:
  python check_figure.py fig2.pdf --journal nature --width single
  python check_figure.py fig3.tif --width 183 --min-dpi 300
  python check_figure.py arch.svg --width double

Exit code 0 if no FAIL, 1 otherwise (UNVERIFIED does not fail the exit code
but is printed prominently; treat it as unresolved).
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
import zlib

MM_PER_INCH = 25.4
PT_PER_INCH = 72.0

COLUMN_WIDTHS_MM = {
    "default":  {"single": 89.0,  "onehalf": 136.0, "double": 183.0},
    "nature":   {"single": 89.0,  "onehalf": 136.0, "double": 183.0},
    "elsevier": {"single": 90.0,  "onehalf": 140.0, "double": 190.0},
    "springer": {"single": 84.0,  "onehalf": 129.0, "double": 174.0},
    "ieee":     {"single": 88.9,  "onehalf": 135.0, "double": 181.9},
    "science":  {"single": 57.0,  "onehalf": 121.0, "double": 184.0},
    "neurips":  {"single": 139.7, "onehalf": 139.7, "double": 139.7},
    "icml":     {"single": 82.55, "onehalf": 127.0, "double": 171.45},
}

WIDTH_TOL_MM = 2.0


class Report:
    def __init__(self) -> None:
        self.lines: list[tuple[str, str]] = []

    def add(self, level: str, msg: str) -> None:
        self.lines.append((level, msg))

    def ok(self, msg): self.add("PASS", msg)
    def warn(self, msg): self.add("WARN", msg)
    def fail(self, msg): self.add("FAIL", msg)
    def unverified(self, msg): self.add("UNVERIFIED", msg)

    def emit(self) -> int:
        worst = 0
        for level, msg in self.lines:
            print(f"[{level:>10}] {msg}")
            if level == "FAIL":
                worst = 1
        n_unv = sum(1 for lv, _ in self.lines if lv == "UNVERIFIED")
        if n_unv:
            print(f"[{'NOTE':>10}] {n_unv} item(s) could not be verified by this "
                  f"tool; verify them manually before submission.")
        return worst


# ---------------------------------------------------------------- PNG / TIFF

def inspect_png(data: bytes) -> dict:
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    out: dict = {}
    pos = 8
    while pos + 8 <= len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        if ctype == b"IHDR":
            out["width_px"], out["height_px"] = struct.unpack(">II", body[:8])
        elif ctype == b"pHYs" and length >= 9:
            ppux, ppuy, unit = struct.unpack(">IIB", body[:9])
            if unit == 1 and ppux:  # pixels per meter
                out["dpi"] = ppux * 0.0254
        elif ctype == b"IEND":
            break
        pos += 12 + length
    return out


def inspect_tiff(data: bytes) -> dict:
    if data[:2] == b"II":
        endian = "<"
    elif data[:2] == b"MM":
        endian = ">"
    else:
        raise ValueError("not a TIFF")
    (magic,) = struct.unpack(endian + "H", data[2:4])
    if magic != 42:
        raise ValueError("not a classic TIFF")
    (ifd_off,) = struct.unpack(endian + "I", data[4:8])
    (n_entries,) = struct.unpack(endian + "H", data[ifd_off:ifd_off + 2])
    out: dict = {}
    xres = unit = None
    for i in range(n_entries):
        e = data[ifd_off + 2 + 12 * i: ifd_off + 14 + 12 * i]
        tag, typ, count = struct.unpack(endian + "HHI", e[:8])
        val_bytes = e[8:12]
        if tag in (256, 257):  # ImageWidth / ImageLength
            fmt = endian + ("H" if typ == 3 else "I")
            v = struct.unpack(fmt, val_bytes[: struct.calcsize(fmt)])[0]
            out["width_px" if tag == 256 else "height_px"] = v
        elif tag == 282 and typ == 5:  # XResolution, RATIONAL at offset
            (off,) = struct.unpack(endian + "I", val_bytes)
            num, den = struct.unpack(endian + "II", data[off:off + 8])
            xres = num / den if den else None
        elif tag == 296:  # ResolutionUnit: 2 = inch, 3 = cm
            (unit,) = struct.unpack(endian + "H", val_bytes[:2])
    if xres:
        if unit == 3:
            out["dpi"] = xres * 2.54
        else:  # inch (2) or unspecified (1) -> assume inch, as writers do
            out["dpi"] = xres
    return out


# ---------------------------------------------------------------- PDF / EPS

def _pdf_decompressed_tail(data: bytes, limit: int = 40) -> bytes:
    """Concatenate data with best-effort inflated streams (for MediaBox/Font
    keys hidden inside object streams). Best effort only."""
    chunks = [data]
    for i, m in enumerate(re.finditer(rb"stream\r?\n", data)):
        if i >= limit:
            break
        start = m.end()
        end = data.find(b"endstream", start)
        if end == -1:
            continue
        try:
            chunks.append(zlib.decompress(data[start:end]))
        except Exception:
            pass
    return b"\n".join(chunks)


def inspect_pdf(data: bytes) -> dict:
    if not data.startswith(b"%PDF"):
        raise ValueError("not a PDF")
    blob = _pdf_decompressed_tail(data)
    out: dict = {}
    m = re.search(
        rb"/MediaBox\s*\[\s*([\d.+-]+)\s+([\d.+-]+)\s+([\d.+-]+)\s+([\d.+-]+)\s*\]",
        blob)
    if m:
        x0, y0, x1, y1 = (float(v) for v in m.groups())
        out["width_mm"] = abs(x1 - x0) / PT_PER_INCH * MM_PER_INCH
        out["height_mm"] = abs(y1 - y0) / PT_PER_INCH * MM_PER_INCH
    out["has_font"] = b"/Font" in blob or b"/BaseFont" in blob
    out["fonts_embedded"] = any(k in blob for k in
                                (b"/FontFile", b"/FontFile2", b"/FontFile3"))
    out["has_image_xobject"] = bool(
        re.search(rb"/Subtype\s*/Image", blob))
    return out


def inspect_eps(data: bytes) -> dict:
    m = re.search(rb"%%BoundingBox:\s*([\d.+-]+)\s+([\d.+-]+)\s+([\d.+-]+)\s+([\d.+-]+)",
                  data)
    out: dict = {}
    if m:
        x0, y0, x1, y1 = (float(v) for v in m.groups())
        out["width_mm"] = (x1 - x0) / PT_PER_INCH * MM_PER_INCH
        out["height_mm"] = (y1 - y0) / PT_PER_INCH * MM_PER_INCH
    return out


# ---------------------------------------------------------------- SVG

_UNIT_TO_MM = {"mm": 1.0, "cm": 10.0, "in": MM_PER_INCH,
               "pt": MM_PER_INCH / 72.0, "px": MM_PER_INCH / 96.0, "": MM_PER_INCH / 96.0}


def inspect_svg(data: bytes) -> dict:
    text = data.decode("utf-8", errors="replace")
    m = re.search(r"<svg\b[^>]*>", text, re.DOTALL)
    out: dict = {}
    if not m:
        raise ValueError("no <svg> element found")
    tag = m.group(0)
    for attr in ("width", "height"):
        am = re.search(attr + r'\s*=\s*"([\d.]+)\s*([a-z%]*)"', tag)
        if am and am.group(2) != "%":
            unit = am.group(2)
            if unit in _UNIT_TO_MM:
                out[attr + "_mm"] = float(am.group(1)) * _UNIT_TO_MM[unit]
                out[attr + "_unit"] = unit or "px"
    out["has_text_elements"] = "<text" in text
    return out


# ---------------------------------------------------------------- evaluation

def resolve_target_mm(args) -> float | None:
    if args.width is None:
        return None
    try:
        return float(args.width)
    except ValueError:
        pass
    try:
        return COLUMN_WIDTHS_MM[args.journal.lower()][args.width]
    except KeyError:
        sys.exit(f"error: unknown --journal/--width combination "
                 f"({args.journal!r}, {args.width!r}). Journals: "
                 f"{sorted(COLUMN_WIDTHS_MM)}; slots: single, onehalf, double; "
                 f"or pass a numeric width in mm.")


def check_width(rep: Report, width_mm: float | None, target: float | None,
                label: str = "width") -> None:
    if target is None:
        if width_mm is not None:
            rep.ok(f"{label}: {width_mm:.1f} mm (no target given)")
        return
    if width_mm is None:
        rep.unverified(f"{label}: could not read physical width from file "
                       f"(target {target:.1f} mm)")
        return
    if width_mm > target + WIDTH_TOL_MM:
        rep.fail(f"{label}: {width_mm:.1f} mm exceeds target {target:.1f} mm; "
                 f"it will be scaled down and all text shrinks with it")
    elif width_mm < target - WIDTH_TOL_MM:
        rep.warn(f"{label}: {width_mm:.1f} mm is under target {target:.1f} mm; "
                 f"fine only if intentionally narrow (it will not be scaled up)")
    else:
        rep.ok(f"{label}: {width_mm:.1f} mm matches target {target:.1f} mm "
               f"(±{WIDTH_TOL_MM:.0f} mm)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--journal", default="default",
                    help="venue key for --width slots (default: default)")
    ap.add_argument("--width", default=None,
                    help="target width: single | onehalf | double | <mm>")
    ap.add_argument("--min-dpi", type=float, default=300.0,
                    help="DPI floor for raster formats (default 300; use 600 "
                         "for combination art, 1000 for pure line art)")
    args = ap.parse_args()

    # A Windows console defaults to cp1252, which cannot encode the glyphs in
    # the report lines below, so the checker would crash on its own output.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError):  # pragma: no cover - non-standard stream
            pass

    try:
        with open(args.file, "rb") as f:
            data = f.read()
    except OSError as e:
        sys.exit(f"error: {e}")

    target = resolve_target_mm(args)
    rep = Report()
    name = args.file.lower()

    try:
        if data.startswith(b"%PDF"):
            info = inspect_pdf(data)
            check_width(rep, info.get("width_mm"), target, "page width")
            if "height_mm" in info:
                rep.ok(f"page height: {info['height_mm']:.1f} mm "
                       f"(check venue max height)")
            if info["has_font"]:
                if info["fonts_embedded"]:
                    rep.ok("fonts referenced and embedded (FontFile present)")
                else:
                    rep.fail("fonts referenced but no embedded FontFile found; "
                             "set pdf.fonttype=42 / embed on conversion and re-export")
            else:
                rep.unverified("no font objects found: text may be outlined, "
                               "absent, or inside streams this tool couldn't "
                               "inflate; confirm text renders and is intended")
            if info["has_image_xobject"]:
                rep.warn("embedded raster image(s) inside the PDF: fine for "
                         "deliberate rasterization (heatmaps, photos, generative "
                         "elements), a defect if the whole plot is a screenshot")
        elif name.endswith(".eps") or data.startswith(b"%!PS"):
            info = inspect_eps(data)
            check_width(rep, info.get("width_mm"), target, "bounding-box width")
            if "width_mm" not in info:
                rep.unverified("no %%BoundingBox found")
        elif data[:8] == b"\x89PNG\r\n\x1a\n" or data[:2] in (b"II", b"MM"):
            info = inspect_png(data) if data[:1] == b"\x89" else inspect_tiff(data)
            w_px = info.get("width_px")
            dpi = info.get("dpi")
            if w_px:
                rep.ok(f"pixel size: {w_px} × {info.get('height_px', '?')} px")
            else:
                rep.unverified("could not read pixel dimensions")
            if dpi:
                if dpi + 1 < args.min_dpi:
                    rep.fail(f"embedded resolution {dpi:.0f} DPI is below the "
                             f"{args.min_dpi:.0f} DPI floor")
                else:
                    rep.ok(f"embedded resolution {dpi:.0f} DPI ≥ "
                           f"{args.min_dpi:.0f} DPI floor")
                if w_px:
                    check_width(rep, w_px / dpi * MM_PER_INCH, target,
                                "physical width at embedded DPI")
            else:
                rep.unverified("no embedded resolution metadata")
            if w_px and target:
                eff = w_px / (target / MM_PER_INCH)
                if eff + 1 < args.min_dpi:
                    rep.fail(f"effective resolution at {target:.0f} mm would be "
                             f"{eff:.0f} DPI (< {args.min_dpi:.0f}); regenerate "
                             f"larger, do not upscale")
                else:
                    rep.ok(f"effective resolution at {target:.0f} mm: "
                           f"{eff:.0f} DPI")
            rep.warn("raster format: acceptable only where the venue forces it; "
                     "prefer vector for plots and diagrams")
        elif b"<svg" in data[:4096] or name.endswith(".svg"):
            info = inspect_svg(data)
            check_width(rep, info.get("width_mm"), target, "declared width")
            if info.get("width_unit") not in ("mm", "cm", "in", None):
                rep.warn(f"width declared in {info.get('width_unit')}; declare "
                         f"physical units (mm) so conversion is size-true")
            if info.get("has_text_elements"):
                rep.ok("text present as <text> elements (editable master)")
            rep.warn("SVG is a working format: convert to PDF for submission "
                     "and re-check the PDF")
        else:
            rep.unverified("unrecognized format; this tool checks "
                           "PDF/EPS/SVG/PNG/TIFF")
    except ValueError as e:
        rep.unverified(f"parse error: {e}")

    print(f"-- {args.file}")
    return rep.emit()


if __name__ == "__main__":
    sys.exit(main())
