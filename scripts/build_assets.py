"""Draw the hand-authored artwork of the profile README.

    pip install fonttools
    python scripts/build_assets.py

Outputs assets/plant.svg (hero), assets/panel.svg (instrument panel) and
assets/monitors/*.svg (one animated monitor per project). The daily stats
panels come from scripts/build_stats.py.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from lettering import (AMBER, BG, BLUE, CLAY, COND, COND_MED, CYAN, DIM, EDGE, GREEN, GRID, MUTED,
                       PANEL, PANEL_HI, RED, REG, SEMI, TEXT, Doc, Iso, ramp, shade)

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
W = 1280


def wrap(face, text: str, size: float, max_w: float) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if face.width(trial, size) > max_w and cur:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + ([cur] if cur else [])


# ----------------------------------------------------------------------------- icons
def icon_wafer(cx, cy, r, color) -> str:
    out = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{shade(color, 0.35)}" stroke="{color}" stroke-width="2"/>']
    step = r / 2.6
    for i in range(-2, 3):
        for j in range(-2, 3):
            x, y = cx + i * step, cy + j * step
            if (x - cx) ** 2 + (y - cy) ** 2 < (r - 4) ** 2:
                out.append(f'<rect x="{x - step / 2 + 1:.1f}" y="{y - step / 2 + 1:.1f}" width="{step - 2:.1f}" height="{step - 2:.1f}" fill="{color}" opacity=".75"/>')
    return "".join(out)


def icon_wave(cx, cy, r, color) -> str:
    pts = " ".join(f"{cx - r + i:.1f},{cy + math.sin(i / r * 3 * math.pi) * r * 0.55 * math.sin(i / (2 * r) * math.pi):.1f}" for i in range(0, int(2 * r) + 1, 2))
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{shade(color, 0.3)}" stroke="{color}" stroke-width="2"/>'
            f'<polyline points="{pts}" fill="none" stroke="{TEXT}" stroke-width="2.2" stroke-linecap="round"/>')


def icon_ball(cx, cy, r, color) -> str:
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="#F4F1EA" stroke="{shade(color, .8)}" stroke-width="1.5"/>'
            f'<path d="M{cx - r * .55:.1f} {cy - r * .8:.1f} q {r * .45:.1f} {r * .8:.1f} 0 {r * 1.6:.1f}" fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="2.5 2"/>'
            f'<path d="M{cx + r * .55:.1f} {cy - r * .8:.1f} q {-r * .45:.1f} {r * .8:.1f} 0 {r * 1.6:.1f}" fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="2.5 2"/>')


def icon_sherd(cx, cy, r, color) -> str:
    pts = [(-.9, -.3), (-.4, -.9), (.5, -.75), (.95, -.1), (.6, .7), (-.2, .9), (-.85, .45)]
    d = " ".join(f"{cx + a * r:.1f},{cy + b * r:.1f}" for a, b in pts)
    return (f'<polygon points="{d}" fill="{color}" stroke="{shade(color, 1.35)}" stroke-width="1.5"/>'
            f'<circle cx="{cx - r * .2:.1f}" cy="{cy - r * .1:.1f}" r="2" fill="{shade(color, .5)}"/>'
            f'<circle cx="{cx + r * .35:.1f}" cy="{cy + r * .3:.1f}" r="1.6" fill="{shade(color, .5)}"/>'
            f'<circle cx="{cx + r * .1:.1f}" cy="{cy - r * .45:.1f}" r="1.4" fill="{shade(color, 1.4)}"/>')


STREAMS = [
    ("fab sensors", CYAN, icon_wafer),
    ("hydrophone", BLUE, icon_wave),
    ("Statcast", RED, icon_ball),
    ("pottery", CLAY, icon_sherd),
]

COMMON_CSS = (
    ".led{animation:led 2s steps(2,end) infinite}@keyframes led{50%{opacity:.25}}"
    ".bob{animation:bob 3s ease-in-out infinite}@keyframes bob{50%{transform:translateY(-6px)}}"
)


# ----------------------------------------------------------------------------- hero
def plant() -> str:
    H = 560
    doc = Doc(W, H, "Paul Lai, M.S. Data Science at UC San Diego: an animated data factory where sensor, audio, baseball and pottery data ride conveyor belts into one machine and come out validated.")
    iso = Iso(840, 66)

    doc.add(iso.box(0, 0, -14, 470, 400, 14, "#121B2A"))
    for gx in range(40, 470, 40):
        a, b = iso.p(gx, 0), iso.p(gx, 400)
        doc.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')
    for gy in range(40, 400, 40):
        a, b = iso.p(0, gy), iso.p(470, gy)
        doc.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{GRID}"/>')

    item_iso = Iso(0, 0)
    hop_y = [24, 118, 212, 306]
    mx0, mx1 = 290, 380

    for i, ((label, color, icon), y) in enumerate(zip(STREAMS, hop_y)):
        doc.add(iso.box(20, y, 0, 70, 62, 58, PANEL_HI))
        doc.add(iso.box(20, y, 58, 70, 62, 8, color))
        yc = y + 31
        doc.add(iso.box(90, y + 18, 0, mx0 - 90, 26, 8, "#1A2537"))
        a, b = iso.p(92, yc, 8), iso.p(mx0, yc, 8)
        doc.add(f'<line class="roll" x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{DIM}" stroke-width="2" stroke-dasharray="3 9"/>')
        cube = item_iso.box(-7, -7, 0, 14, 14, 14, color)
        p0, p1 = iso.p(98, yc, 8), iso.p(mx0 + 6, yc, 8)
        dur = 4.8
        for k in range(3):
            begin = -(k * dur / 3 + i * 0.4)
            doc.add(f'<g opacity="0">{cube}'
                    f'<animateMotion dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite" path="M{p0[0]:.1f} {p0[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f}"/>'
                    f'<animate attributeName="opacity" dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite" values="0;1;1;0" keyTimes="0;.06;.9;1"/></g>')
        ix, iy = iso.p(55, y + 31, 58 + 46)
        doc.add(f'<g class="bob" style="animation-delay:{-i * 0.6:.1f}s">{icon(ix, iy, 15, color)}</g>')
        doc.add(COND_MED.text(doc, label, ix, iy - 24, 14, TEXT, anchor="middle", track=0.4))

    doc.add(iso.box(mx0, 14, 0, mx1 - mx0, 372, 118, "#1B2639"))
    doc.add(iso.box(mx0, 14, 118, mx1 - mx0, 372, 6, "#26334B"))
    doc.add(iso.box(mx1 - 12, 14, 124, 12, 372, 3, AMBER))
    doc.add(iso.box(318, 40, 124, 26, 26, 46, "#2A3852"))
    sx, sy = iso.p(331, 53, 172)
    for k in range(4):
        doc.add(f'<circle class="smoke" style="animation-delay:{-k * 0.9:.1f}s" cx="{sx:.1f}" cy="{sy:.1f}" r="7" fill="#3A4A66"/>')

    def face_x(y, z):
        return iso.p(mx1, y, z)

    for n, y in enumerate(range(40, 370, 22)):
        px, py = face_x(y, 100)
        doc.add(f'<circle class="led" style="animation-delay:{(n * 0.37) % 2:.2f}s" cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{GREEN if n % 4 else AMBER}"/>')

    def face_poly(y0, y1, z0, z1, fill):
        pts = [face_x(y0, z0), face_x(y1, z0), face_x(y1, z1), face_x(y0, z1)]
        return '<polygon points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'" fill="{fill}" stroke="{EDGE}"/>'

    doc.add(face_poly(50, 180, 26, 82, "#08131F"))
    wave = []
    for t in range(0, 121, 3):
        px, py = face_x(56 + t, 54 + 18 * math.sin(t / 9) * math.cos(t / 31))
        wave.append(f"{px:.1f},{py:.1f}")
    doc.add(f'<polyline class="trace" points="{" ".join(wave)}" fill="none" stroke="{CYAN}" stroke-width="1.8"/>')
    doc.add(face_poly(205, 345, 26, 82, "#08131F"))
    rnd = random.Random(4)
    for c, (cy0, cz0) in zip((CYAN, AMBER, GREEN), ((240, 62), (290, 44), (318, 66))):
        for _ in range(9):
            px, py = face_x(cy0 + rnd.gauss(0, 9), cz0 + rnd.gauss(0, 5))
            doc.add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.8" fill="{c}"/>')

    gx, gy = iso.p(mx0 + 45, 386, 60)
    teeth = []
    for t in range(12):
        a0 = t * math.pi / 6
        for a, rr in ((a0 - .14, 20), (a0 - .1, 26), (a0 + .1, 26), (a0 + .14, 20)):
            teeth.append(f"{rr * math.cos(a):.1f},{rr * math.sin(a):.1f}")
    doc.add(f'<g transform="matrix({iso.c:.3f} {iso.s:.3f} 0 1 {gx:.1f} {gy:.1f})">'
            f'<g class="spin"><polygon points="{" ".join(teeth)}" fill="{shade(AMBER, .8)}" stroke="{shade(AMBER, .45)}"/>'
            f'<circle r="7" fill="#1B2639"/></g></g>')

    doc.add(iso.box(mx1, 176, 0, 52, 28, 8, "#1A2537"))
    doc.add(iso.box(430, 150, 0, 34, 80, 30, shade(GREEN, .45)))
    doc.add(iso.box(430, 150, 30, 34, 80, 4, GREEN))
    cube = item_iso.box(-7, -7, 0, 14, 14, 14, GREEN)
    p0, p1 = iso.p(mx1 + 2, 190, 8), iso.p(446, 190, 36)
    for k in range(2):
        doc.add(f'<g opacity="0">{cube}'
                f'<animateMotion dur="2.4s" begin="{-k * 1.2:.1f}s" repeatCount="indefinite" path="M{p0[0]:.1f} {p0[1]:.1f} L{p1[0]:.1f} {p1[1]:.1f}"/>'
                f'<animate attributeName="opacity" dur="2.4s" begin="{-k * 1.2:.1f}s" repeatCount="indefinite" values="0;1;1;0" keyTimes="0;.1;.85;1"/></g>')
    bx, by = iso.p(447, 190, 150)
    sx0, sy0 = iso.p(447, 190, 34)
    doc.add(f'<line x1="{sx0:.1f}" y1="{sy0:.1f}" x2="{bx:.1f}" y2="{by + 28:.1f}" stroke="{EDGE}" stroke-width="2" stroke-dasharray="4 4"/>')
    doc.add(f'<g class="bob" style="animation-delay:-1.3s"><rect x="{bx - 62:.1f}" y="{by - 34:.1f}" width="124" height="62" rx="8" fill="{PANEL}" stroke="{GREEN}"/>'
            f'<polyline class="trace" points="{bx - 48:.1f},{by + 14:.1f} {bx - 26:.1f},{by + 4:.1f} {bx - 8:.1f},{by + 8:.1f} {bx + 14:.1f},{by - 6:.1f} {bx + 46:.1f},{by - 12:.1f}" fill="none" stroke="{GREEN}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
            + COND.text(doc, "VALIDATED", bx, by - 16, 15, GREEN, anchor="middle", track=1.4) + "</g>")

    bot = (item_iso.box(-9, -9, 0, 18, 18, 20, "#C9D6E8")
           + f'<circle cx="-4" cy="-24" r="3.2" fill="{CYAN}" class="blink"/>'
           + '<line x1="0" y1="-38" x2="0" y2="-48" stroke="#C9D6E8" stroke-width="2"/>'
           + f'<circle cx="0" cy="-50" r="3" fill="{RED}" class="led"/>')
    a, b = iso.p(408, 250), iso.p(408, 372)
    doc.add(f'<g>{bot}<animateMotion dur="7s" repeatCount="indefinite" path="M{a[0]:.1f} {a[1]:.1f} L{b[0]:.1f} {b[1]:.1f} L{a[0]:.1f} {a[1]:.1f}"/></g>')

    # identity
    doc.add(f'<circle class="led" cx="54" cy="56" r="5" fill="{GREEN}"/>')
    doc.add(COND_MED.text(doc, "PLANT ONLINE  ·  4 LINES RUNNING", 68, 61.5, 15, GREEN, track=1.2))
    doc.add(COND.text(doc, "Paul Lai", 44, 150, 100, track=-0.8))
    doc.add(SEMI.text(doc, "Data & ML for messy, real-world data", 48, 192, 23, CYAN))
    doc.add(REG.text(doc, "M.S. Data Science  ·  UC San Diego", 48, 224, 19, MUTED))
    x, y = 48, 252
    for chip in ["AI data solutions", "smart manufacturing", "big data processing", "machine learning"]:
        w = REG.width(chip, 15) + 26
        if x + w > 470:
            x, y = 48, y + 38
        doc.add(f'<rect x="{x}" y="{y}" width="{w:.0f}" height="28" rx="14" fill="{PANEL}" stroke="{EDGE}"/>')
        doc.add(REG.text(doc, chip, x + w / 2, y + 19, 15, TEXT, anchor="middle"))
        x += w + 10

    lx, ly, lw, lh = 44, 352, 420, 172
    doc.add(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="10" fill="{PANEL}" stroke="{EDGE}"/>')
    doc.add(f'<path d="M{lx} {ly + 30} h{lw}" stroke="{EDGE}"/>')
    for k, c in enumerate((RED, AMBER, GREEN)):
        doc.add(f'<circle cx="{lx + 18 + k * 16}" cy="{ly + 15}" r="4.5" fill="{c}" opacity=".85"/>')
    doc.add(COND_MED.text(doc, "plant.log", lx + lw / 2, ly + 20, 14, MUTED, anchor="middle", track=0.6))
    logs = [
        ("yield", CYAN, "590 sensors  ·  beats MSPC 5 vs 2  ·  drift watched"),
        ("ocean", BLUE, "4 GB/day streamed  ·  r 0.99 vs MBARI"),
        ("pitch", RED, "2.14M rows to 17 MB  ·  Stuff+ out-of-sample"),
        ("sherd", CLAY, "257 samples  ·  silhouette 0.64"),
    ]
    total = 12.0
    for k, (tag, c, msg) in enumerate(logs):
        yy = ly + 62 + k * 28
        full = lw - 28
        t0, t1 = k * 1.4 / total, (k * 1.4 + 1.0) / total
        doc.add(f'<clipPath id="log{k}"><rect x="{lx + 14}" y="{yy - 18}" height="26" width="{full}">'
                f'<animate attributeName="width" dur="{total}s" repeatCount="indefinite" values="0;0;{full};{full};0" keyTimes="0;{t0:.3f};{t1:.3f};.94;1"/></rect></clipPath>')
        doc.add(f'<g clip-path="url(#log{k})">'
                + COND_MED.text(doc, f"[{tag}]", lx + 16, yy, 16, c, track=0.6)
                + REG.text(doc, msg, lx + 76, yy, 15.5, TEXT)
                + COND.text(doc, "OK", lx + lw - 18, yy, 15, GREEN, anchor="end", track=1) + "</g>")
    doc.style(
        COMMON_CSS
        + ".roll{animation:roll .9s linear infinite}@keyframes roll{to{stroke-dashoffset:-12}}"
        ".smoke{animation:smoke 3.6s ease-out infinite;transform-box:fill-box;transform-origin:center}"
        "@keyframes smoke{0%{transform:translate(0,0) scale(.6);opacity:.9}100%{transform:translate(14px,-58px) scale(2.2);opacity:0}}"
        ".blink{animation:blink 4s infinite}@keyframes blink{0%,92%,100%{opacity:1}95%{opacity:0}}"
        ".spin{animation:spin 6s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}"
        ".trace{stroke-dasharray:6 4;animation:trace 1.2s linear infinite}@keyframes trace{to{stroke-dashoffset:-20}}"
    )
    return doc.render()


# ----------------------------------------------------------------------------- instrument panel
def panel() -> str:
    H = 250
    doc = Doc(W, H, "Instrument panel: 590 sensors per run, 4 GB of audio per day, 2.14 million pitches processed, clustering silhouette 0.64.")
    cw = (W - 40 - 3 * 16) / 4
    cells = [20 + i * (cw + 16) for i in range(4)]
    for x in cells:
        doc.add(f'<rect x="{x:.0f}" y="20" width="{cw:.0f}" height="{H - 40}" rx="12" fill="{PANEL}" stroke="{EDGE}"/>')

    def head(x, title, sub):
        doc.add(COND_MED.text(doc, title, x + 18, 48, 15, MUTED, track=1.1))
        doc.add(REG.text(doc, sub, x + 18, H - 36, 14, DIM))

    x = cells[0]
    head(x, "SENSOR MATRIX", "Semiconductor Yield  ·  UCI SECOM")
    rnd = random.Random(12)
    cols, rows = 59, 10
    pitch = (cw - 36) / cols
    for r in range(rows):
        for c in range(cols):
            v = rnd.random()
            color = RED if v < 0.025 else AMBER if v < 0.07 else GREEN
            doc.add(f'<circle class="m{rnd.randrange(6)}" cx="{x + 18 + pitch * (c + .5):.1f}" cy="{70 + r * pitch:.1f}" r="{pitch * .32:.2f}" fill="{color}" opacity=".9"/>')
    doc.add(COND.text(doc, "590", x + 18, 178, 40, TEXT))
    doc.add(REG.text(doc, "sensors per run", x + 18 + COND.width("590", 40) + 10, 178, 16, MUTED))

    x = cells[1]
    head(x, "AUDIO INTAKE", "Ocean Soundscape  ·  MBARI MARS")
    tx, ty, tw, th = x + 18, 62, 92, 128
    doc.add(f'<clipPath id="tank"><rect x="{tx:.0f}" y="{ty}" width="{tw}" height="{th}" rx="10"/></clipPath>')
    doc.add(f'<rect x="{tx:.0f}" y="{ty}" width="{tw}" height="{th}" rx="10" fill="#0B1220" stroke="{EDGE}"/>')
    def wave(amp, off):
        return "M0 0 " + " ".join(f"L{i} {amp * math.sin((i + off) * 2 * math.pi / 88):.1f}" for i in range(0, 2 * 88 + 1, 4)) + " L176 200 L0 200 Z"
    doc.add(f'<g clip-path="url(#tank)"><g transform="translate({tx:.0f} {ty + 46})">'
            f'<g class="tide"><path d="{wave(5, 0)}" fill="{shade(BLUE, .55)}"/></g>'
            f'<g transform="translate(0 6)"><g class="tide2"><path d="{wave(4, 30)}" fill="{BLUE}" opacity=".7"/></g></g></g></g>')
    for k in range(5):
        yy = ty + 16 + k * 24
        doc.add(f'<line x1="{tx + tw - 14:.0f}" y1="{yy}" x2="{tx + tw:.0f}" y2="{yy}" stroke="{MUTED}" stroke-width="1.5"/>')
    doc.add(COND.text(doc, "4 GB", tx + tw + 22, 120, 40, TEXT))
    doc.add(REG.text(doc, "of audio per day,", tx + tw + 22, 146, 16, MUTED))
    doc.add(REG.text(doc, "streamed for a year", tx + tw + 22, 168, 16, MUTED))

    x = cells[2]
    head(x, "PITCHES PROCESSED", "DeepPitch  ·  Statcast 2024–26")
    digits = "2140000"
    dx, dy, dw, dh = x + 18, 70, 31, 54
    positions = []
    for k, ch in enumerate(digits):
        gx = dx + k * (dw + 4) + (10 if k >= 1 else 0) + (10 if k >= 4 else 0)
        positions.append(gx)
        doc.add(f'<rect x="{gx:.0f}" y="{dy}" width="{dw}" height="{dh}" rx="6" fill="#0B1220" stroke="{EDGE}"/>')
        doc.add(COND.text(doc, ch, gx + dw / 2, dy + 40, 36, TEXT, anchor="middle"))
    for k in (1, 4):
        doc.add(COND.text(doc, ",", positions[k] - 5, dy + dh - 2, 22, MUTED, anchor="middle"))
    doc.add(REG.text(doc, "pitches turned into physics", x + 18, 158, 16, MUTED))
    doc.add(REG.text(doc, "and an out-of-sample Stuff+ grade", x + 18, 180, 16, MUTED))

    x = cells[3]
    head(x, "CLUSTER QUALITY", "Archaeological Ceramics  ·  Sinica")
    gcx, gcy, gr = x + cw / 2, 158, 82

    def ang(v):  # silhouette -1..1 onto 180°..0°
        return math.pi * (1 - (v + 1) / 2)

    def arc(v0, v1, color):
        a0, a1 = ang(v0), ang(v1)
        p0 = (gcx + gr * math.cos(a0), gcy - gr * math.sin(a0))
        p1 = (gcx + gr * math.cos(a1), gcy - gr * math.sin(a1))
        return f'<path d="M{p0[0]:.1f} {p0[1]:.1f} A{gr} {gr} 0 0 1 {p1[0]:.1f} {p1[1]:.1f}" fill="none" stroke="{color}" stroke-width="12"/>'

    doc.add(arc(-1, 0, shade(RED, .7)) + arc(0, .5, shade(AMBER, .8)) + arc(.5, 1, shade(GREEN, .75)))
    for v in (-1, -0.5, 0, 0.5, 1):
        a = ang(v)
        doc.add(f'<line x1="{gcx + (gr - 18) * math.cos(a):.1f}" y1="{gcy - (gr - 18) * math.sin(a):.1f}" x2="{gcx + (gr - 10) * math.cos(a):.1f}" y2="{gcy - (gr - 10) * math.sin(a):.1f}" stroke="{MUTED}" stroke-width="1.5"/>')
    rot = 90 - math.degrees(ang(0.64))
    doc.add(f'<g transform="translate({gcx:.1f} {gcy})"><g transform="rotate({rot:.1f})"><g class="needle">'
            f'<path d="M-4 0 L0 {-gr + 6} L4 0 Z" fill="{TEXT}"/></g></g><circle r="7" fill="{TEXT}"/></g>')
    doc.add(COND.text(doc, "0.64", gcx, gcy + 36, 30, TEXT, anchor="middle"))
    doc.style("".join(f".m{i}{{animation:m 2.4s steps(2,end) infinite;animation-delay:{-i * 0.4:.1f}s}}" for i in range(6))
              + "@keyframes m{50%{opacity:.25}}"
              + ".tide{animation:tide 3s linear infinite}.tide2{animation:tide2 4s linear infinite}"
              + "@keyframes tide{to{transform:translateX(-88px)}}@keyframes tide2{from{transform:translateX(-88px)}to{transform:translateX(0)}}"
              + ".needle{animation:jit 2.8s ease-in-out infinite}@keyframes jit{50%{transform:rotate(3deg)}}")
    return doc.render()


# ----------------------------------------------------------------------------- project monitors
def screen(doc, title: str, live: bool):
    doc.add(f'<rect x="20" y="20" width="480" height="240" rx="12" fill="#0B1220" stroke="{EDGE}"/>')
    doc.add(COND_MED.text(doc, title, 40, 46, 14, MUTED, track=1.1))
    if live:
        doc.add(f'<circle class="led" cx="478" cy="41" r="4.5" fill="{GREEN}"/>')
        doc.add(COND_MED.text(doc, "LIVE", 466, 46, 13, GREEN, anchor="end", track=1))


def viz_wafer(doc):
    screen(doc, "WAFER BIN MAP  ·  INSPECTION QUEUE", True)
    cx, cy, r = 172, 154, 90
    rnd = random.Random(31)
    step = 12
    doc.add(f'<circle cx="{cx}" cy="{cy}" r="{r + 5}" fill="#101A2A" stroke="{EDGE}" stroke-width="2"/>')
    for i in range(-8, 9):
        for j in range(-8, 9):
            x, y = cx + i * step, cy + j * step
            if (abs(x - cx) + step / 2) ** 2 + (abs(y - cy) + step / 2) ** 2 >= r ** 2:
                continue
            v = rnd.random()
            color = RED if v < .05 else AMBER if v < .2 else "#1E6B4A"
            extra = f' class="die" style="animation-delay:{-rnd.random() * 3:.2f}s"' if color != "#1E6B4A" else ""
            doc.add(f'<rect{extra} x="{x - step / 2 + 1}" y="{y - step / 2 + 1}" width="{step - 2}" height="{step - 2}" rx="1.5" fill="{color}"/>')
    doc.add(f'<rect x="{cx - 9}" y="{cy + r + 1}" width="18" height="6" fill="#0B1220"/>')
    doc.add(f'<clipPath id="wafer"><circle cx="{cx}" cy="{cy}" r="{r + 5}"/></clipPath>')
    doc.add(f'<g clip-path="url(#wafer)"><rect class="scan" x="{cx - r - 6}" y="{cy - r - 6}" width="3" height="{2 * r + 12}" fill="{CYAN}" opacity=".9"/></g>')
    for k, (c, t) in enumerate(((RED, "recorded failure"), (AMBER, "flagged for review"), ("#1E6B4A", "pass"))):
        doc.add(f'<rect x="300" y="{96 + k * 30}" width="14" height="14" rx="2" fill="{c}"/>')
        doc.add(REG.text(doc, t, 324, 108 + k * 30, 14, MUTED))
    doc.add(REG.text(doc, "illustration of the review policy", 300, 214, 12.5, DIM))
    doc.style(".die{animation:die 3s steps(2,end) infinite}@keyframes die{50%{opacity:.35}}"
              f".scan{{animation:scan 4s ease-in-out infinite alternate}}@keyframes scan{{to{{transform:translateX({2 * r + 9}px)}}}}")


def viz_spectrogram(doc):
    screen(doc, "LONG-TERM SPECTROGRAM  ·  JUL 2018 – JUN 2019", True)
    rnd = random.Random(7)
    cols, rows, cw_, ch_ = 49, 17, 9, 9
    x0, y0 = 40, 64
    cells = []
    for c in range(cols):
        season = .5 + .5 * math.sin(2 * math.pi * c / cols)
        stripe = rnd.random() < .1
        for r in range(rows):
            f = r / rows
            v = (.15 + .25 * rnd.random() + .25 * (1 - f) ** 2 + .6 * season * math.exp(-((f - .12) / .06) ** 2)
                 + .35 * season * math.exp(-((f - .32) / .02) ** 2) + (.25 if stripe else 0))
            color = ramp((v - .3) / .9, [(0, "#0B1220"), (.45, "#14607A"), (.75, CYAN), (1, AMBER)])
            cells.append(f'<rect x="{c * cw_}" y="{(rows - 1 - r) * ch_}" width="{cw_ - 1}" height="{ch_ - 1}" fill="{color}"/>')
    tile = "".join(cells)
    doc.add(f'<clipPath id="sp"><rect x="{x0}" y="{y0}" width="440" height="{rows * ch_}"/></clipPath>')
    doc.add(f'<g clip-path="url(#sp)"><g class="specscroll"><g>{tile}</g><g transform="translate({cols * cw_} 0)">{tile}</g></g></g>')
    doc.add(REG.text(doc, "20 Hz fin whale chorus", 40, 238, 13, AMBER))
    doc.add(REG.text(doc, "illustrative rendering", 480, 238, 13, DIM, anchor="end"))
    doc.style(f".specscroll{{animation:ss 30s linear infinite;transform:translate({x0}px,{y0}px)}}@keyframes ss{{from{{transform:translate({x0}px,{y0}px)}}to{{transform:translate({x0 - cols * cw_}px,{y0}px)}}}}")


def viz_pitch(doc):
    screen(doc, "PITCH FLIGHT  ·  SIDE VIEW, 60.5 FT", True)
    doc.add('<path d="M40 214 q 20 -14 52 -14 q 30 0 50 14 Z" fill="#2A2018"/>')
    doc.add(f'<rect x="420" y="128" width="36" height="52" fill="none" stroke="{MUTED}" stroke-width="1.5"/>')
    doc.add(f'<line x1="300" y1="70" x2="300" y2="222" stroke="{AMBER}" stroke-dasharray="4 5" opacity=".7"/>')
    doc.add(REG.text(doc, "commit point, 175 ms", 306, 82, 12.5, AMBER))
    for k, (c, end_y, bend) in enumerate([(CYAN, 140, -6), (RED, 165, 18), (BLUE, 152, -24), (GREEN, 172, 34)]):
        d = f"M86 150 Q 260 {118 + bend} 438 {end_y}"
        doc.add(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="2" opacity=".45"/>')
        doc.add(f'<circle r="5.5" fill="#F4F1EA" stroke="{c}" stroke-width="2"><animateMotion dur="1.8s" begin="{k * 0.45:.2f}s" repeatCount="indefinite" path="{d}" keyPoints="0;1;1" keyTimes="0;.7;1" calcMode="linear"/></circle>')
    doc.add(REG.text(doc, "four-seam  ·  sinker  ·  cutter  ·  sweeper  (illustrative)", 40, 238, 13, MUTED))


def viz_clusters(doc):
    screen(doc, "PCA SPACE  ·  SHERDS BY MINERAL MAKEUP", False)
    rnd = random.Random(9)
    for k, (c, (cx, cy)) in enumerate(((AMBER, (150, 118)), (CYAN, (340, 112)), (CLAY, (250, 186)))):
        doc.add(f'<ellipse class="hull" style="animation-delay:{-k}s" cx="{cx}" cy="{cy}" rx="68" ry="36" fill="{c}" fill-opacity=".07" stroke="{c}" stroke-opacity=".5" stroke-dasharray="4 4"/>')
        pts = "".join(f'<circle cx="{cx + rnd.gauss(0, 22):.1f}" cy="{cy + rnd.gauss(0, 11):.1f}" r="3.2" fill="{c}"/>' for _ in range(26))
        doc.add(f'<g class="drift" style="animation-delay:{-k * 1.3:.1f}s">{pts}</g>')
    for _ in range(6):
        doc.add(f'<circle class="noise" style="animation-delay:{-rnd.random() * 2:.2f}s" cx="{rnd.uniform(50, 470):.1f}" cy="{rnd.uniform(70, 222):.1f}" r="3.4" fill="none" stroke="{MUTED}" stroke-width="1.5"/>')
    doc.add(REG.text(doc, "K-Means groups  ·  open rings: DBSCAN noise  (illustrative)", 40, 238, 13, MUTED))
    doc.style(".drift{animation:drift 5s ease-in-out infinite}@keyframes drift{50%{transform:translate(3px,-2px)}}"
              ".hull{animation:hull 4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}@keyframes hull{50%{transform:scale(1.04)}}"
              ".noise{animation:noise 2s steps(2,end) infinite}@keyframes noise{50%{opacity:.2}}")


def viz_wake(doc):
    screen(doc, "STREAMLIT APP  ·  CHECKED EVERY 6 HOURS", False)
    wx, wy, ww, wh = 90, 66, 340, 160
    doc.add(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="10" fill="{PANEL}" stroke="{EDGE}"/>')
    doc.add(f'<path d="M{wx} {wy + 26} h{ww}" stroke="{EDGE}"/>')
    for k in range(3):
        doc.add(f'<circle cx="{wx + 16 + k * 14}" cy="{wy + 13}" r="4" fill="{DIM}"/>')
    asleep = ('<g class="sleep">'
              + COND.text(doc, "Zzz", wx + ww / 2, wy + 92, 40, DIM, anchor="middle", track=2)
              + REG.text(doc, "This app has gone to sleep", wx + ww / 2, wy + 124, 14, DIM, anchor="middle") + "</g>")
    bars = "".join(f'<rect x="{wx + 40 + i * 30}" y="{wy + wh - 22 - h}" width="18" height="{h}" rx="2" fill="{c}"/>'
                   for i, (h, c) in enumerate(zip((40, 70, 55, 95, 80, 106, 90, 64, 100), (CYAN, BLUE) * 5)))
    awake = f'<g class="awake">{bars}' + COND.text(doc, "awake", wx + ww - 16, wy + 52, 16, GREEN, anchor="end", track=1) + "</g>"
    doc.add(asleep, awake)
    doc.add(f'<g class="cursor"><path d="M0 0 L0 18 L5 13 L9 21 L12 20 L8 12 L15 12 Z" fill="{TEXT}" stroke="{BG}"/></g>')
    doc.style(".sleep{animation:sl 6s infinite}@keyframes sl{0%,45%{opacity:1}55%,100%{opacity:0}}"
              ".awake{opacity:0;animation:aw 6s infinite}@keyframes aw{0%,48%{opacity:0}58%,95%{opacity:1}100%{opacity:0}}"
              f".cursor{{transform:translate(470px,236px);animation:cur 6s infinite}}@keyframes cur{{0%{{transform:translate(470px,236px)}}35%,45%{{transform:translate({wx + ww / 2:.0f}px,{wy + 110}px)}}60%,100%{{transform:translate(470px,236px)}}}}")


MONITORS = [
    dict(slug="yield", viz=viz_wafer, accent=CYAN, title="Semiconductor Yield",
         summary="Which units should a fab inspect when only 20% of a batch can be reviewed? A frozen model search, the MSPC baseline fabs run today, drift and retraining, shipped as an API and a live monitor.",
         metric="5 vs 2", metric_label="failures caught vs MSPC at a 20% budget", chips=["scikit-learn", "MSPC", "FastAPI", "Docker", "Streamlit"]),
    dict(slug="ocean", viz=viz_spectrogram, accent=BLUE, title="Ocean Soundscape",
         summary="A year of deep-ocean audio sorted without labels into whale song, wind, ships and one earthquake, each checked against outside data.",
         metric="r 0.99", metric_label="monthly agreement with MBARI's fin whale index", chips=["SciPy", "scikit-learn", "soundfile", "S3", "Streamlit"]),
    dict(slug="deeppitch", viz=viz_pitch, accent=RED, title="DeepPitch",
         summary="Every MLB pitch from 2024 to 2026 rebuilt as physics: flight replay, spin, approach angle, tunneling and an out-of-sample Stuff+ model.",
         metric="2.14M", metric_label="pitches, served from 17 MB of Parquet", chips=["pybaseball", "pandas", "Parquet", "LightGBM", "Plotly"]),
    dict(slug="ceramics", viz=viz_clusters, accent=CLAY, title="Archaeological Ceramics",
         summary="Where did Penghu's early settlers come from? Grouping 257 pottery sherds from 28 sites by the minerals in their clay.",
         metric="0.50 to 0.64", metric_label="silhouette after leak-proof feature design", chips=["pandas", "PCA", "K-Means", "DBSCAN"]),
    dict(slug="wake", viz=viz_wake, accent=GREEN, title="streamlit-wake",
         summary="A GitHub Action that opens each Streamlit app in a real browser and presses the wake button, so a demo never greets a recruiter asleep.",
         metric="6 h", metric_label="between wake-up rounds, MIT licensed", chips=["GitHub Actions", "Playwright", "pytest"]),
]


def monitor(m) -> str:
    H = 280
    doc = Doc(W, H, f"{m['title']}: {m['summary']}")
    m["viz"](doc)
    x = 536
    doc.add(f'<rect x="{x}" y="40" width="5" height="40" rx="2.5" fill="{m["accent"]}"/>')
    doc.add(COND.text(doc, m["title"], x + 20, 76, 44, TEXT, track=-0.3))
    for k, line in enumerate(wrap(REG, m["summary"], 17, W - x - 50)[:3]):
        doc.add(REG.text(doc, line, x, 112 + k * 24, 17, MUTED))
    doc.add(COND.text(doc, m["metric"], x, 206, 36, m["accent"]))
    doc.add(REG.text(doc, m["metric_label"], x + COND.width(m["metric"], 36) + 14, 204, 15, TEXT))
    cx = x
    for chip in m["chips"]:
        w = REG.width(chip, 14) + 22
        doc.add(f'<rect x="{cx:.0f}" y="226" width="{w:.0f}" height="26" rx="13" fill="{PANEL}" stroke="{EDGE}"/>')
        doc.add(REG.text(doc, chip, cx + w / 2, 244, 14, TEXT, anchor="middle"))
        cx += w + 8
    doc.style(COMMON_CSS)
    return doc.render()


def button(label: str, kind: str, accent: str) -> str:
    w = round(REG.width(label, 17) + 70)
    doc = Doc(w, 44, label, background=PANEL, radius=22)
    ic = {
        "doc": f'<path d="M20 12 h10 l6 6 v14 h-16 z" fill="none" stroke="{accent}" stroke-width="2" stroke-linejoin="round"/><path d="M24 22 h8 M24 26 h8" stroke="{accent}" stroke-width="2"/>',
        "web": f'<circle cx="28" cy="22" r="10" fill="none" stroke="{accent}" stroke-width="2"/><ellipse cx="28" cy="22" rx="4.5" ry="10" fill="none" stroke="{accent}" stroke-width="1.6"/><path d="M18 22 h20" stroke="{accent}" stroke-width="1.6"/>',
        "in": f'<rect x="18" y="12" width="20" height="20" rx="4" fill="{accent}"/><path d="M22.5 20 v8 M22.5 16.5 v.5 M26.5 28 v-8 M26.5 23 q0 -3 3 -3 q3 0 3 3 v5" stroke="{PANEL}" stroke-width="2.4" stroke-linecap="round" fill="none"/>',
        "mail": f'<rect x="17" y="14" width="22" height="16" rx="3" fill="none" stroke="{accent}" stroke-width="2"/><path d="M18 16 l10 8 l10 -8" fill="none" stroke="{accent}" stroke-width="2" stroke-linejoin="round"/>',
    }[kind]
    doc.add(ic, REG.text(doc, label, 50, 28, 17, TEXT))
    return doc.render()


def main() -> None:
    (ASSETS / "buttons").mkdir(parents=True, exist_ok=True)
    for slug, label, kind, accent in (("resume", "Resume (PDF)", "doc", AMBER), ("portfolio", "Portfolio", "web", CYAN),
                                      ("linkedin", "LinkedIn", "in", BLUE), ("email", "holai@ucsd.edu", "mail", GREEN)):
        (ASSETS / "buttons" / f"{slug}.svg").write_text(button(label, kind, accent))
    (ASSETS / "monitors").mkdir(parents=True, exist_ok=True)
    (ASSETS / "plant.svg").write_text(plant())
    (ASSETS / "panel.svg").write_text(panel())
    for m in MONITORS:
        (ASSETS / "monitors" / f"{m['slug']}.svg").write_text(monitor(m))
    for p in sorted(ASSETS.rglob("*.svg")):
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
