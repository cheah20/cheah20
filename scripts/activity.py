"""Draw one framed GitHub activity card (assets/activity.svg) from live GitHub data.

Needs a token in GITHUB_TOKEN (the Actions token is enough).
"""
import json
import os
import sys
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

LOGIN = os.environ.get("PROFILE_USER", "cheah20")
TOKEN = os.environ["GITHUB_TOKEN"]
FONT = "Segoe UI, Ubuntu, Helvetica, Arial, sans-serif"
BG, PANEL, EDGE, INK, SOFT, FAINT = "#1a1b27", "#1f2235", "#3b3f5c", "#c0caf5", "#a9b1d6", "#737aa2"
GOLD, PINK, TEAL, BLUE = "#e0af68", "#f7768e", "#73daca", "#7aa2f7"


def gql(query, **variables):
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": query, "variables": variables}).encode(),
                                 headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def fetch():
    u = gql("""query($login:String!){ user(login:$login){ name login createdAt
      repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100, isFork:false){ totalCount
        nodes{ stargazerCount languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name color } } } } }
      contributionsCollection{ totalCommitContributions totalPullRequestContributions totalIssueContributions
        totalRepositoriesWithContributedCommits
        contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } } } }""", login=LOGIN)
    days = {}
    joined = datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    for year in range(joined.year, date.today().year + 1):
        y = gql("""query($login:String!, $from:DateTime!, $to:DateTime!){ user(login:$login){
          contributionsCollection(from:$from, to:$to){ contributionCalendar{ weeks{ contributionDays{ date contributionCount } } } } } }""",
                login=LOGIN, **{"from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"})
        for w in y["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
    return u, joined, dict(sorted(days.items()))


def streaks(days):
    today = date.today().isoformat()
    seq = [(d, c) for d, c in days.items() if d <= today]
    longest = run = 0
    for _, c in seq:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    for d, c in reversed(seq):
        if c:
            current += 1
        elif d != today:
            break
    return current, longest


def line(points, x, y, w, h, color, fill_id):
    """A smooth-ish line chart with a soft fill under it."""
    top = max(max(points), 1)
    step = w / max(len(points) - 1, 1)
    pts = [(x + i * step, y + h - p / top * h) for i, p in enumerate(points)]
    path = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    area = path + f" L{x + w:.1f},{y + h} L{x},{y + h} Z"
    dots = "".join(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.2" fill="{color}"/>' for px, py in pts)
    return (f'<path d="{area}" fill="url(#{fill_id})"/><path d="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>{dots}'
            f'<text x="{x + w + 6}" y="{y + 4}" fill="{FAINT}" font-size="10">{top}</text><text x="{x + w + 6}" y="{y + h}" fill="{FAINT}" font-size="10">0</text>')


def build():
    u, joined, days = fetch()
    cc = u["contributionsCollection"]
    repos = u["repositories"]
    stars = sum(r["stargazerCount"] for r in repos["nodes"])
    langs = defaultdict(lambda: [0, "#888"])
    for r in repos["nodes"]:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]][0] += e["size"]
            langs[e["node"]["name"]][1] = e["node"]["color"] or "#888"
    total_size = sum(v[0] for v in langs.values()) or 1
    top_langs = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    current, longest = streaks(days)
    total_all = sum(days.values())
    last12 = cc["contributionCalendar"]["totalContributions"]
    today = date.today().isoformat()
    months = defaultdict(int)
    for d, c in days.items():
        if d <= today:  # the calendar also lists the rest of this year
            months[d[:7]] += c
    month_keys = sorted(months)[-12:]
    daily = list(days.items())
    daily = [c for d, c in daily if d <= today][-30:]
    years = (datetime.now(timezone.utc) - joined).days // 365
    joined_txt = f"Joined GitHub {years} year{'s' if years != 1 else ''} ago" if years else "Joined GitHub this year"
    name = escape(u["name"] or u["login"])

    W, H = 860, 640
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">',
         f'<defs><linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>'
         f'<linearGradient id="fa" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GOLD}" stop-opacity="0.35"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient>'
         f'<linearGradient id="fb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{TEAL}" stop-opacity="0.3"/><stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></linearGradient></defs>',
         f'<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18" fill="{BG}" stroke="url(#edge)" stroke-width="2.5"/>',
         f'<text x="{W / 2}" y="46" text-anchor="middle" fill="{GOLD}" font-size="26" font-weight="700">{name}</text>',
         f'<text x="{W / 2}" y="68" text-anchor="middle" fill="{FAINT}" font-size="12">@{escape(u["login"])}</text>']
    # facts and monthly chart
    for i, t in enumerate([f"{last12:,} contributions in the last 12 months", f"{repos['totalCount']} public repositories", joined_txt]):
        y = 112 + i * 28
        s.append(f'<circle cx="44" cy="{y - 4}" r="4" fill="{[PINK, BLUE, TEAL][i]}"/><text x="58" y="{y}" fill="{INK}" font-size="13">{escape(t)}</text>')
    s.append(f'<text x="460" y="96" fill="{SOFT}" font-size="11" font-weight="700">Monthly contributions (last 12 months)</text>')
    s.append(line([months[k] for k in month_keys], 460, 110, 340, 70, GOLD, "fa"))
    s.append(f'<text x="460" y="198" fill="{FAINT}" font-size="10">{month_keys[0]}</text><text x="800" y="198" text-anchor="end" fill="{FAINT}" font-size="10">{month_keys[-1]}</text>')

    def panel(x, y, w, h, title, color):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{PANEL}" stroke="{PINK}" stroke-opacity="0.45"/>'
                f'<text x="{x + 18}" y="{y + 28}" fill="{color}" font-size="14" font-weight="700">{title}</text>')
    # stats and languages
    s.append(panel(30, 220, 390, 170, "GitHub Stats", PINK))
    for i, (k, v) in enumerate([("Total stars earned", stars), ("Commits (12 months)", cc["totalCommitContributions"]),
                                ("Pull requests (12 months)", cc["totalPullRequestContributions"]),
                                ("Issues (12 months)", cc["totalIssueContributions"]),
                                ("Repos contributed to (12 months)", cc["totalRepositoriesWithContributedCommits"])]):
        y = 274 + i * 23
        s.append(f'<text x="50" y="{y}" fill="{SOFT}" font-size="12.5">{k}</text><text x="400" y="{y}" text-anchor="end" fill="{INK}" font-size="12.5" font-weight="700">{v:,}</text>')
    s.append(panel(440, 220, 390, 170, "Most Used Languages", PINK))
    bx, bw = 460, 350
    for lname, (size, col) in top_langs:
        w = size / total_size * bw
        s.append(f'<rect x="{bx:.1f}" y="262" width="{max(w, 2):.1f}" height="8" fill="{col}"/>')
        bx += w
    for i, (lname, (size, col)) in enumerate(top_langs):
        cx, cy = 466 + (i % 2) * 180, 298 + (i // 2) * 26
        s.append(f'<circle cx="{cx}" cy="{cy - 4}" r="5" fill="{col}"/><text x="{cx + 12}" y="{cy}" fill="{SOFT}" font-size="12">{escape(lname)} {size / total_size * 100:.1f}%</text>')
    # streak tiles
    first_day = next((d for d, c in days.items() if c), today)
    for i, (title, val, sub, col) in enumerate([("Total contributions", total_all, f"{first_day[:7]} to now", GOLD),
                                               ("Current streak", current, "days in a row", PINK), ("Longest streak", longest, "days", TEAL)]):
        x = 30 + i * 273
        s.append(f'<rect x="{x}" y="408" width="254" height="96" rx="12" fill="{PANEL}" stroke="{PINK}" stroke-opacity="0.45"/>'
                 f'<text x="{x + 127}" y="450" text-anchor="middle" fill="{col}" font-size="28" font-weight="700">{val:,}</text>'
                 f'<text x="{x + 127}" y="472" text-anchor="middle" fill="{INK}" font-size="12.5" font-weight="700">{title}</text>'
                 f'<text x="{x + 127}" y="490" text-anchor="middle" fill="{FAINT}" font-size="10.5">{sub}</text>')
    # daily line
    s.append(panel(30, 522, 800, 100, "Daily contributions (last 30 days)", GOLD))
    s.append(line(daily, 50, 560, 740, 46, TEAL, "fb"))
    s.append("</svg>")
    return "".join(s)


out = Path(sys.argv[1] if len(sys.argv) > 1 else "assets/activity.svg")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(build(), encoding="utf-8")
print("wrote", out)
