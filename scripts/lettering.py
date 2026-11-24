"""Shared drawing helpers: Barlow lettering as outlines, the palette, an SVG document."""

from __future__ import annotations

import math
from html import escape
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

FONTS = Path(__file__).resolve().parent / "fonts"

# control-room palette
BG = "#0A0E15"
PANEL = "#101724"
PANEL_HI = "#152034"
EDGE = "#22324A"
GRID = "#141D2B"
TEXT = "#E7EDF6"
MUTED = "#8C9BB2"
DIM = "#52627C"
CYAN = "#3FD7F2"
BLUE = "#5B8CFF"
AMBER = "#FFB547"
GREEN = "#47E08C"
RED = "#FF5C61"
CLAY = "#E38A52"


class Doc:
    def __init__(self, width: int, height: int, title: str, background: str | None = BG, radius: int = 16):
        self.w, self.h, self.title = width, height, title
        self.parts: list[str] = []
        self.glyphs: dict[str, str] = {}
        self.styles: list[str] = []
        if background:
            self.add(f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{radius}" fill="{background}" stroke="{EDGE}"/>')

    def add(self, *parts: str) -> None:
        self.parts.extend(p for p in parts if p)

    def style(self, css: str) -> None:
        self.styles.append(css)

    def render(self) -> str:
        defs = "".join(f'<path id="{k}" d="{d}"/>' for k, d in self.glyphs.items() if d)
        css = "".join(self.styles)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{escape(self.title)}">'
            f"<title>{escape(self.title)}</title>"
            f"<style>{css}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>"
            f"<defs>{defs}</defs>\n" + "\n".join(self.parts) + "\n</svg>\n"
        )


class Face:
    def __init__(self, filename: str):
        font = TTFont(FONTS / filename)
        self.key = Path(filename).stem.replace("-", "").lower()
        self.glyphs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.upm = font["head"].unitsPerEm
        self.hmtx = font["hmtx"]
        self._cache: dict[str, str] = {}

    def _names(self, text: str) -> list[str]:
        missing = [c for c in text if ord(c) not in self.cmap]
        if missing:
            raise ValueError(f"glyphs missing for {missing!r} in {text!r}")
        return [self.cmap[ord(c)] for c in text]

    def width(self, text: str, size: float, track: float = 0) -> float:
        names = self._names(text)
        return sum(self.hmtx[n][0] for n in names) * size / self.upm + track * max(0, len(names) - 1)

    def fit(self, text: str, size: float, max_w: float, track: float = 0) -> float:
        while self.width(text, size, track) > max_w and size > 8:
            size -= 0.5
        return size

    def _outline(self, name: str) -> str:
        if name not in self._cache:
            pen = SVGPathPen(self.glyphs, ntos=lambda v: str(round(v)))
            self.glyphs[name].draw(pen)
            self._cache[name] = pen.getCommands()
        return self._cache[name]

    def text(self, doc: Doc, text: str, x: float, y: float, size: float, fill: str = TEXT,
             anchor: str = "start", track: float = 0, attrs: str = "") -> str:
        if anchor != "start":
            w = self.width(text, size, track)
            x -= w if anchor == "end" else w / 2
        s = size / self.upm
        uses, adv = [], 0.0
        for name in self._names(text):
            d = self._outline(name)
            if d:
                gid = f"{self.key}-{name}".replace(".", "_")
                doc.glyphs[gid] = d
                uses.append(f'<use href="#{gid}" x="{round(adv)}"/>')
            adv += self.hmtx[name][0] + track / s
        return (f'<g fill="{fill}" {attrs} transform="translate({x:.1f} {y:.1f}) scale({s:.5f} {-s:.5f})">'
                + "".join(uses) + "</g>")


REG = Face("Barlow-Regular.ttf")
SEMI = Face("Barlow-SemiBold.ttf")
COND = Face("BarlowCondensed-SemiBold.ttf")
COND_MED = Face("BarlowCondensed-Medium.ttf")


def shade(hex_color: str, factor: float) -> str:
    """factor < 1 darkens, > 1 lightens toward white."""
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    if factor <= 1:
        r, g, b = (round(c * factor) for c in (r, g, b))
    else:
        t = factor - 1
        r, g, b = (round(c + (255 - c) * t) for c in (r, g, b))
    return f"#{r:02X}{g:02X}{b:02X}"


def ramp(v: float, stops: list[tuple[float, str]]) -> str:
    v = max(0.0, min(1.0, v))
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        if v <= b:
            t = (v - a) / (b - a) if b > a else 0
            c1 = [int(ca[i:i + 2], 16) for i in (1, 3, 5)]
            c2 = [int(cb[i:i + 2], 16) for i in (1, 3, 5)]
            return "#" + "".join(f"{round(p + (q - p) * t):02X}" for p, q in zip(c1, c2))
    return stops[-1][1]


class Iso:
    """Isometric projection: x runs down-right, y runs down-left, z up."""

    def __init__(self, ox: float, oy: float, scale: float = 1.0):
        self.ox, self.oy, self.k = ox, oy, scale
        self.c, self.s = math.cos(math.pi / 6) * scale, 0.5 * scale

    def p(self, x: float, y: float, z: float = 0) -> tuple[float, float]:
        return self.ox + (x - y) * self.c, self.oy + (x + y) * self.s - z * self.k

    def poly(self, pts, fill, stroke=None, extra="") -> str:
        d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (self.p(*q) for q in pts))
        st = f' stroke="{stroke}" stroke-width="1" stroke-linejoin="round"' if stroke else ""
        return f'<polygon points="{d}" fill="{fill}"{st} {extra}/>'

    def box(self, x, y, z, w, d, h, color, stroke=None) -> str:
        top = [(x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)]
        front = [(x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h)]
        side = [(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h)]
        sc = stroke or shade(color, 0.45)
        return (self.poly(front, shade(color, 0.72), sc) + self.poly(side, shade(color, 0.55), sc)
                + self.poly(top, color, sc))
