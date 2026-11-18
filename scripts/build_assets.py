"""Draw the profile README's process sheets as SVG.

Each side project is drawn as a process line: raw data in, equipment (the
tools that did the work) in the middle, a measured result and an output at
the end. Text is converted to outlines with the Barlow typeface (SIL OFL),
so the drawings look the same on every machine and need no web fonts.

    pip install fonttools
    # put Barlow-Regular, Barlow-SemiBold, BarlowCondensed-Medium and
    # BarlowCondensed-SemiBold .ttf files in scripts/fonts/
    # (https://github.com/google/fonts/tree/main/ofl/barlow, .../barlowcondensed)
    python scripts/build_assets.py
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
FONTS = Path(__file__).resolve().parent / "fonts"

INK = "#16191D"
SOFT = "#5A636E"
RULE = "#A9B1BA"
PAPER = "#FFFFFF"
FLOW = "#EE5A1B"

W = 1280


_USED: dict[str, str] = {}  # glyph id -> outline, collected per drawing


class Face:
    def __init__(self, filename: str):
        font = TTFont(FONTS / filename)
        self.key = Path(filename).stem.replace("-", "").lower()
        self.glyphs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.upm = font["head"].unitsPerEm
        self.hmtx = font["hmtx"]

    def _names(self, text: str) -> list[str]:
        missing = [c for c in text if ord(c) not in self.cmap]
        if missing:
            raise ValueError(f"glyphs missing for {missing!r} in {text!r}")
        return [self.cmap[ord(c)] for c in text]

    def width(self, text: str, size: float, track: float = 0) -> float:
        names = self._names(text)
        adv = sum(self.hmtx[n][0] for n in names) * size / self.upm
        return adv + track * max(0, len(names) - 1)

    def _glyph(self, name: str) -> str | None:
        gid = f"{self.key}-{name}".replace(".", "_")
        if gid not in _USED:
            pen = SVGPathPen(self.glyphs, ntos=lambda v: str(round(v)))
            self.glyphs[name].draw(pen)
            _USED[gid] = pen.getCommands()
        return gid if _USED[gid] else None

    def text(self, text: str, x: float, y: float, size: float, fill: str = INK,
             anchor: str = "start", track: float = 0) -> str:
        if anchor != "start":
            w = self.width(text, size, track)
            x -= w if anchor == "end" else w / 2
        s = size / self.upm
        uses, adv = [], 0.0
        for name in self._names(text):
            gid = self._glyph(name)
            if gid:
                uses.append(f'<use href="#{gid}" x="{round(adv)}"/>')
            adv += self.hmtx[name][0] + track / s
        return (f'<g fill="{fill}" transform="translate({x:.1f} {y:.1f}) scale({s:.5f} {-s:.5f})">'
                + "".join(uses) + "</g>")


REG = Face("Barlow-Regular.ttf")
SEMI = Face("Barlow-SemiBold.ttf")
COND = Face("BarlowCondensed-SemiBold.ttf")
COND_MED = Face("BarlowCondensed-Medium.ttf")


def fit(face: Face, text: str, size: float, max_w: float) -> float:
    while face.width(text, size) > max_w and size > 9:
        size -= 0.5
    return size


def document(height: int, title: str, body: list[str]) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" '
        f'viewBox="0 0 {W} {height}" role="img" aria-label="{escape(title)}">\n'
        f"<title>{escape(title)}</title>\n"
        "<style>"
        ".flow{fill:none;stroke:" + FLOW + ";stroke-width:3;stroke-dasharray:9 23;"
        "stroke-linecap:round;animation:flow 1.6s linear infinite}"
        "@keyframes flow{to{stroke-dashoffset:-32}}"
        "@media (prefers-reduced-motion:reduce){.flow{animation:none}}"
        "</style>\n<defs>" + "".join(f'<path id="{k}" d="{d}"/>' for k, d in _USED.items() if d)
        + "</defs>\n" + "\n".join(body) + "\n</svg>\n"
    )


def sheet(height: int, inset: int = 14) -> list[str]:
    return [
        f'<rect x="1" y="1" width="{W - 2}" height="{height - 2}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>',
        f'<rect x="{inset}" y="{inset}" width="{W - 2 * inset}" height="{height - 2 * inset}" fill="none" stroke="{INK}" stroke-width="1"/>',
    ]


def pipe(points: list[tuple[float, float]], arrow: bool = False) -> list[str]:
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in points)
    out = [f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2"/>',
           f'<path class="flow" d="{d}"/>']
    if arrow:
        x1, y1 = points[-1]
        out.append(f'<path d="M{x1:.1f} {y1:.1f} l-14 -7 v14 z" fill="{INK}"/>')
    return out


def vessel(x, y, w, h, line1, line2) -> list[str]:
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>']
    out.append(SEMI.text(line1, x + w / 2, y + h / 2 - 3, fit(SEMI, line1, 17, w - 40), anchor="middle"))
    out.append(REG.text(line2, x + w / 2, y + h / 2 + 18, fit(REG, line2, 15, w - 40), SOFT, anchor="middle"))
    return out


def unit(x, y, w, h, tool, action) -> list[str]:
    out = [f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>',
           f'<line x1="{x + 8:.1f}" y1="{y + h - 8}" x2="{x + w - 8:.1f}" y2="{y + h - 8}" stroke="{RULE}" stroke-width="1"/>']
    out.append(SEMI.text(tool, x + w / 2, y + h / 2 - 4, fit(SEMI, tool, 19, w - 20), anchor="middle"))
    out.append(REG.text(action, x + w / 2, y + h / 2 + 18, fit(REG, action, 15.5, w - 16), SOFT, anchor="middle"))
    return out


def instrument(cx, cy, r, value, label) -> list[str]:
    """ISA-style instrument bubble: the reading above the bar, what it measures below."""
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>',
           f'<line x1="{cx - r}" y1="{cy}" x2="{cx + r}" y2="{cy}" stroke="{INK}" stroke-width="1.5"/>']
    out.append(COND.text(value, cx, cy - 8, fit(COND, value, 28, 2 * r - 14), anchor="middle"))
    out.append(REG.text(label, cx, cy + 22, fit(REG, label, 14, 2 * r - 16), SOFT, anchor="middle"))
    return out


# ------------------------------------------------------------------ overview sheet
def overview() -> str:
    _USED.clear()
    H = 470
    b = sheet(H, 18)
    for i in range(8):  # zone markers, as on a drawing frame
        x0 = i * W / 8
        if i:
            b.append(f'<line x1="{x0:.0f}" y1="1" x2="{x0:.0f}" y2="18" stroke="{INK}"/>')
            b.append(f'<line x1="{x0:.0f}" y1="{H - 18}" x2="{x0:.0f}" y2="{H - 1}" stroke="{INK}"/>')
        b.append(COND_MED.text(str(8 - i), x0 + W / 16, 14, 11, SOFT, anchor="middle"))
        b.append(COND_MED.text(str(8 - i), x0 + W / 16, H - 5, 11, SOFT, anchor="middle"))
    for j, letter in enumerate("CBA"):
        y0 = 18 + j * (H - 36) / 3
        if j:
            b.append(f'<line x1="1" y1="{y0:.0f}" x2="18" y2="{y0:.0f}" stroke="{INK}"/>')
            b.append(f'<line x1="{W - 18}" y1="{y0:.0f}" x2="{W - 1}" y2="{y0:.0f}" stroke="{INK}"/>')
        b.append(COND_MED.text(letter, 9.5, y0 + (H - 36) / 6 + 4, 11, SOFT, anchor="middle"))
        b.append(COND_MED.text(letter, W - 9.5, y0 + (H - 36) / 6 + 4, 11, SOFT, anchor="middle"))

    b.append(COND.text("Paul Lai", 50, 142, 112, track=-1))
    b.append(REG.text("I turn large, messy, real-world data into results that hold up.", 54, 190, 27))
    b.append(SEMI.text("M.S. Data Science, UC San Diego", 54, 232, 20))
    b.append(REG.text("AI data solutions  ·  smart manufacturing  ·  big data processing  ·  machine learning", 54, 262, 18.5, SOFT))

    tx, ty, tw, rh = 912, 40, 334, 32
    rows = [("DRAWING", "Side projects, process view"), ("ENGINEER", "Paul Lai"),
            ("CONTACT", "holai@ucsd.edu"), ("WEB", "paul-lai.vercel.app"), ("REV", "2026-11  ·  sheet 1 of 1")]
    b.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{rh * len(rows)}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<line x1="{tx + 92}" y1="{ty}" x2="{tx + 92}" y2="{ty + rh * len(rows)}" stroke="{INK}"/>')
    for i, (k, v) in enumerate(rows):
        if i:
            b.append(f'<line x1="{tx}" y1="{ty + i * rh}" x2="{tx + tw}" y2="{ty + i * rh}" stroke="{INK}"/>')
        b.append(COND_MED.text(k, tx + 12, ty + i * rh + 21, 13, SOFT, track=0.8))
        b.append(REG.text(v, tx + 104, ty + i * rh + 22, 16))

    feeds = ["590 fab sensors", "4 GB/day of hydrophone audio", "2.14M MLB pitches", "257 pottery sherds"]
    fy0, fgap, fh, fx, fw = 300, 38, 30, 52, 230
    mx, hy = 318, 366
    for i, name in enumerate(feeds):
        y = fy0 + i * fgap
        b.append(f'<rect x="{fx}" y="{y}" width="{fw}" height="{fh}" rx="15" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>')
        b.append(REG.text(name, fx + fw / 2, y + 20.5, fit(REG, name, 15, fw - 28), anchor="middle"))
        b += pipe([(fx + fw, y + fh / 2), (mx, y + fh / 2), (mx, hy)])
    stages = [("INGEST", "stream, chunk, hash-check"), ("CLEAN", "gaps, leaks, time order"),
              ("FEATURES", "physics, acoustics, sensors"), ("MODEL", "rank, cluster, predict")]
    sx, sw, sgap, sy, sh = 362, 140, 38, 334, 64
    b += pipe([(mx, hy), (sx, hy)])
    for i, (name, note) in enumerate(stages):
        x = sx + i * (sw + sgap)
        b.append(f'<rect x="{x}" y="{sy}" width="{sw}" height="{sh}" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>')
        b.append(COND.text(name, x + sw / 2, sy + 29, 22, anchor="middle", track=1.2))
        b.append(REG.text(note, x + sw / 2, sy + 50, fit(REG, note, 13.5, sw - 16), SOFT, anchor="middle"))
        if i < len(stages) - 1:
            b += pipe([(x + sw, hy), (x + sw + sgap, hy)])
    last = sx + 3 * (sw + sgap) + sw
    cx = last + 74
    b += pipe([(last, hy), (cx - 38, hy)])
    b += instrument(cx, hy, 38, "VAL", "outside data")
    b += pipe([(cx + 38, hy), (W - 40, hy)], arrow=True)
    b.append(SEMI.text("validated", W - 40, hy - 30, 16, anchor="end"))
    b.append(SEMI.text("decisions", W - 40, hy - 12, 16, anchor="end"))
    b.append(REG.text("every result is checked against something the model never saw", W - 40, 438, 14, SOFT, anchor="end"))
    return document(H, "Paul Lai. M.S. Data Science, UC San Diego. AI data solutions, smart manufacturing, big data processing, machine learning. Contact holai@ucsd.edu", b)


# ------------------------------------------------------------------ project lines
@dataclass
class Line:
    slug: str
    name: str
    summary: str
    source: tuple[str, str]
    units: list[tuple[str, str]]
    reading: tuple[str, str] | None
    output: str
    note: str


LINES = [
    Line("yield", "Semiconductor Yield",
         "Which wafer runs should engineers inspect first when only 20% of a batch can be reviewed?",
         ("UCI SECOM", "1,567 runs × 590 sensors"),
         [("pandas", "time-ordered split"), ("scikit-learn", "impute, scale, select"),
          ("XGBoost, SVM, KNN", "50 configurations"), ("Frozen recipe", "locked before test")],
         ("5 / 17", "at 20% review"),
         "inspection priority list",
         "Validated on later runs that played no part in choosing the model."),
    Line("ocean", "Ocean Soundscape",
         "A year of deep-ocean audio, sorted without labels into whale song, wind, ships and one earthquake.",
         ("MBARI hydrophone", "1 year, 4 GB per day"),
         [("soundfile + S3", "streamed audio"), ("SciPy", "16 acoustic features"),
          ("scikit-learn", "PCA + clustering"), ("Streamlit", "live dashboard")],
         ("r 0.99", "vs MBARI"),
         "whale-song seasons, an M3.3 quake",
         "Checked against NOAA buoy wind, the USGS quake catalog and MBARI's published indices."),
    Line("deeppitch", "DeepPitch",
         "Every MLB pitch from 2024 to 2026, rebuilt as physics: flight, spin, approach angle and Stuff+.",
         ("Baseball Savant", "2.14M pitches, 2024–26"),
         [("pybaseball", "chunked fetch"), ("pandas + Parquet", "2.14M rows to 17 MB"),
          ("LightGBM", "out-of-sample Stuff+"), ("Streamlit", "bilingual app")],
         ("r 0.45", "next season"),
         "public scouting app",
         "Physics unit-tested against public benchmarks; every model grade is out-of-sample."),
    Line("ceramics", "Archaeological Ceramics",
         "Where did Penghu's early settlers come from? Grouping pottery by the minerals in its clay.",
         ("Academia Sinica", "257 sherds, 28 sites"),
         [("pandas", "leak-proof features"), ("scikit-learn", "PCA, K-Means, DBSCAN"),
          ("matplotlib", "mineral fingerprints")],
         ("0.64", "silhouette"),
         "provenance groups for archaeologists",
         "Both methods, both regions, both feature sets; noise sherds flagged for re-examination."),
    Line("wake", "streamlit-wake",
         "Keeps free Streamlit apps awake, so a recruiter never lands on a sleeping demo.",
         ("apps.txt", "your Streamlit URLs"),
         [("GitHub Actions", "every 6 hours"), ("Playwright", "presses wake"),
          ("pytest", "tested in CI")],
         None,
         "apps awake for visitors",
         "Reusable template and composite action, MIT licensed."),
]


def line_sheet(ln: Line) -> str:
    _USED.clear()
    H = 300
    b = sheet(H, 12)
    b.append(COND.text(ln.name, 42, 74, 46, track=-0.3))
    b.append(REG.text(ln.summary, 44, 110, fit(REG, ln.summary, 19.5, W - 90)))

    y, h = 146, 82
    cy = y + h / 2
    vx, vw = 42, 224
    b += vessel(vx, y, vw, h, *ln.source)

    end_x = 1004 if ln.reading else 1120
    gap = 34
    n = len(ln.units)
    start = vx + vw + gap
    uw = (end_x - start - gap * (n - 1)) / n
    b += pipe([(vx + vw, cy), (start, cy)])
    for i, (tool, action) in enumerate(ln.units):
        x = start + i * (uw + gap)
        b += unit(x, y, uw, h, tool, action)
        if i < n - 1:
            b += pipe([(x + uw, cy), (x + uw + gap, cy)])
    if ln.reading:
        cx, r = end_x + gap + 48, 48
        b += pipe([(end_x, cy), (cx - r, cy)])
        b += instrument(cx, cy, r, *ln.reading)
        b += pipe([(cx + r, cy), (W - 42, cy)], arrow=True)
        b.append(SEMI.text(ln.output, W - 42, y + h + 34, 15.5, anchor="end"))
    else:
        b += pipe([(end_x, cy), (W - 42, cy)], arrow=True)
        b.append(SEMI.text(ln.output, W - 42, y + h + 34, 15.5, anchor="end"))
    b.append(REG.text(ln.note, 44, 268, fit(REG, ln.note, 15.5, 760), SOFT))
    return document(H, f"{ln.name}: {ln.summary}", b)


def main() -> None:
    (ASSETS / "lines").mkdir(parents=True, exist_ok=True)
    (ASSETS / "overview.svg").write_text(overview())
    for ln in LINES:
        (ASSETS / "lines" / f"{ln.slug}.svg").write_text(line_sheet(ln))
    for p in sorted(ASSETS.rglob("*.svg")):
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
