"""Daily telemetry panels for the profile README, from the public GitHub API.

Runs in GitHub Actions every day (see .github/workflows/telemetry.yml):

    GITHUB_TOKEN=... python scripts/build_stats.py [login]

Writes assets/telemetry/{languages,hours}.svg. Locally it falls back
to `gh auth token` when GITHUB_TOKEN is not set.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from lettering import (AMBER, BLUE, CLAY, COND, COND_MED, CYAN, DIM, EDGE, GREEN, MUTED, PANEL,
                       RED, REG, TEXT, Doc, Iso, ramp, shade)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "telemetry"
LOGIN = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PROFILE_LOGIN", "Paul-Lai0111")
TZ = ZoneInfo("America/Los_Angeles")
LANG_COLORS = [CYAN, BLUE, AMBER, GREEN, CLAY, RED, "#B58CFF", MUTED]


def token() -> str:
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if t:
        return t
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def gql(query: str, **variables) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token()}", "User-Agent": "profile-telemetry"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]


def fetch():
    data = gql("""
    query($login: String!) {
      user(login: $login) {
        id
        contributionsCollection {
          contributionCalendar { totalContributions weeks { contributionDays { date contributionCount weekday } } }
        }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
          nodes { name languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } }
        }
      }
    }""", login=LOGIN)["user"]
    days = [d for w in data["contributionsCollection"]["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    langs: Counter = Counter()
    for repo in data["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"]

    since = (datetime.now(timezone.utc) - timedelta(days=365)).isoformat()
    hours: Counter = Counter()
    for repo in data["repositories"]["nodes"]:
        cursor = None
        while True:
            h = gql("""
            query($login: String!, $name: String!, $author: ID!, $since: GitTimestamp!, $cursor: String) {
              repository(owner: $login, name: $name) { defaultBranchRef { target { ... on Commit {
                history(first: 100, after: $cursor, since: $since, author: {id: $author}) {
                  pageInfo { hasNextPage endCursor } nodes { committedDate } } } } } }
            }""", login=LOGIN, name=repo["name"], author=data["id"], since=since, cursor=cursor)
            ref = h["repository"]["defaultBranchRef"]
            if not ref:
                break
            hist = ref["target"]["history"]
            for n in hist["nodes"]:
                hours[datetime.fromisoformat(n["committedDate"].replace("Z", "+00:00")).astimezone(TZ).hour] += 1
            if not hist["pageInfo"]["hasNextPage"]:
                break
            cursor = hist["pageInfo"]["endCursor"]
    return days, langs, hours


def streaks(days):
    counts = [d["contributionCount"] for d in days]
    longest = cur = 0
    for c in counts:
        cur = cur + 1 if c else 0
        longest = max(longest, cur)
    current = 0
    for c in reversed(counts[:-1] if counts and counts[-1] == 0 else counts):
        if not c:
            break
        current += 1
    return longest, current


def stamp() -> str:
    return datetime.now(TZ).strftime("updated %b %d, %Y")


# ----------------------------------------------------------------------------- calendar
def calendar(days) -> str:
    W, H = 1280, 420
    total = sum(d["contributionCount"] for d in days)
    longest, current = streaks(days)
    active = sum(1 for d in days if d["contributionCount"])
    busiest = max(days, key=lambda d: d["contributionCount"])
    doc = Doc(W, H, f"Contribution calendar for the last year: {total} contributions on {active} days, longest streak {longest} days.")
    doc.add(COND_MED.text(doc, "CONTRIBUTIONS  ·  LAST 12 MONTHS", 28, 44, 15, MUTED, track=1.1))
    doc.add(REG.text(doc, stamp(), W - 28, 44, 13, DIM, anchor="end"))

    class Oblique(Iso):
        def p(self, x, y, z=0):
            return self.ox + x * 0.98 - y * 0.6, self.oy + x * 0.12 + y * 0.42 - z

    iso = Oblique(112, 136)
    peak = max(1, max(d["contributionCount"] for d in days))
    start_wd = days[0]["weekday"]
    for idx, d in enumerate(days):
        wk, wd = divmod(idx + start_wd, 7)
        c = d["contributionCount"]
        h = 4 + (c / peak) ** 0.7 * 72 if c else 2.5
        color = ramp((c / peak) ** 0.6, [(0, "#1A4766"), (.5, "#1E8FB0"), (1, CYAN)]) if c else "#18243A"
        doc.add(iso.box(wk * 20, wd * 18, 0, 15, 14, h, AMBER if c == peak else color))
    stats = [(str(total), "contributions"), (str(active), "active days"),
             (f"{longest} d", "longest streak"), (f"{current} d", "current streak"),
             (str(busiest["contributionCount"]), "busiest day, " + date.fromisoformat(busiest["date"]).strftime("%b %d"))]
    for i, (v, label) in enumerate(stats):
        x = 28 + i * 168
        doc.add(COND.text(doc, v, x, 362, 38, AMBER if i == 0 else TEXT))
        doc.add(REG.text(doc, label, x, 386, 14, MUTED))
    doc.add(REG.text(doc, "amber bar = busiest day", W - 28, 386, 13, DIM, anchor="end"))
    return doc.render()


# ----------------------------------------------------------------------------- languages
def languages(langs: Counter) -> str:
    W, H = 630, 300
    doc = Doc(W, H, "Languages across public repositories: " + ", ".join(f"{k} {v / max(1, sum(langs.values())):.0%}" for k, v in langs.most_common(5)))
    doc.add(COND_MED.text(doc, "LANGUAGES  ·  PUBLIC REPOS", 24, 42, 15, MUTED, track=1.1))
    total = sum(langs.values()) or 1
    top = langs.most_common(6)
    other = total - sum(v for _, v in top)
    if other > 0:
        top.append(("Other", other))
    x, bw = 24, W - 48
    for i, (name, v) in enumerate(top):
        w = bw * v / total
        doc.add(f'<rect x="{x:.1f}" y="62" width="{max(w - 2, 1):.1f}" height="18" rx="3" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>')
        x += w
    for i, (name, v) in enumerate(top):
        col, row = divmod(i, 4)
        x0, y0 = 24 + col * 300, 118 + row * 40
        doc.add(f'<circle cx="{x0 + 7}" cy="{y0 - 6}" r="6" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>')
        doc.add(REG.text(doc, name, x0 + 22, y0, 17, TEXT))
        doc.add(COND.text(doc, f"{v / total:.1%}", x0 + 270, y0, 19, MUTED, anchor="end"))
    doc.add(REG.text(doc, stamp(), W - 24, H - 18, 12.5, DIM, anchor="end"))
    return doc.render()


# ----------------------------------------------------------------------------- hours
def hours_clock(hours: Counter) -> str:
    import math
    W, H = 630, 300
    total = sum(hours.values())
    peak_h = max(range(24), key=lambda h: hours[h]) if total else 0
    doc = Doc(W, H, f"Commit hours, Pacific time, last 12 months: busiest around {peak_h:02d}:00.")
    doc.add(COND_MED.text(doc, "COMMIT CLOCK  ·  PACIFIC TIME", 24, 42, 15, MUTED, track=1.1))
    cx, cy, r0, r1 = 170, 180, 32, 92
    mx = max(1, max(hours.values(), default=1))
    doc.add(f'<circle cx="{cx}" cy="{cy}" r="{r1 + 8}" fill="none" stroke="{EDGE}"/>')
    doc.add(f'<circle cx="{cx}" cy="{cy}" r="{r0 - 4}" fill="{PANEL}" stroke="{EDGE}"/>')
    for h in range(24):
        a = (h / 24) * 2 * math.pi - math.pi / 2
        v = hours[h] / mx
        rr = r0 + 6 + v * (r1 - r0 - 6)
        color = AMBER if h == peak_h and total else ramp(v, [(0, "#1B2A40"), (1, CYAN)])
        x0, y0 = cx + r0 * math.cos(a), cy + r0 * math.sin(a)
        x1, y1 = cx + rr * math.cos(a), cy + rr * math.sin(a)
        doc.add(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{color}" stroke-width="7" stroke-linecap="round"/>')
    for h, label in ((0, "0"), (6, "6"), (12, "12"), (18, "18")):
        a = (h / 24) * 2 * math.pi - math.pi / 2
        doc.add(COND_MED.text(doc, label, cx + (r1 + 22) * math.cos(a), cy + (r1 + 22) * math.sin(a) + 5, 14, DIM, anchor="middle"))
    night = sum(hours[h] for h in list(range(22, 24)) + list(range(0, 6)))
    day = sum(hours[h] for h in range(9, 18))
    persona = "night owl" if night > day else "daylight coder"
    doc.add(COND.text(doc, f"{peak_h:02d}:00", 340, 132, 44, AMBER))
    doc.add(REG.text(doc, "busiest hour", 340, 156, 15, MUTED))
    doc.add(COND.text(doc, str(total), 340, 208, 34, TEXT))
    doc.add(REG.text(doc, "commits in public repos", 340, 230, 15, MUTED))
    doc.add(REG.text(doc, f"verdict: {persona}", 340, 258, 15, CYAN))
    doc.add(REG.text(doc, stamp(), W - 24, H - 18, 12.5, DIM, anchor="end"))
    return doc.render()


def main() -> None:
    days, langs, hours = fetch()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "languages.svg").write_text(languages(langs))
    (OUT / "hours.svg").write_text(hours_clock(hours))
    print(f"{sum(d['contributionCount'] for d in days)} contributions, {len(langs)} languages, {sum(hours.values())} commits")


if __name__ == "__main__":
    main()
