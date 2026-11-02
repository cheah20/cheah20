"""Draw the hero, whoami, project and trophy cards into one folder.

usage: python scripts/cards.py dist
"""
import sys
from datetime import date
from html import escape
from pathlib import Path

from theme import (BG, CYAN, EDGE, FAINT, FONT, GLOW, GOLD, GREEN, INK, LOGIN, MONO, PANEL, PINK, RED, SOFT, TITLE,
                   chip, frame, gql, svg_open)

PROJECTS = [
    ("CareerBridgeAI", "CareerBridge AI", "Reads a resume, scores how well it fits a job and suggests what to learn next.",
     ["Flutter", "FastAPI", "Supabase", "scikit-learn"], "Y3S1 · Team project"),
    ("NeuralTrade", "NeuralTrade", "Trading helper with fuzzy logic, ANFIS and an AI step that must pass a rule check.",
     ["Python", "Flask", "Fuzzy logic", "ANFIS"], "Y2S2 · Fuzzy Logic"),
    ("PayrollSystem", "Payroll System", "Payroll with EPF, SOCSO, EIS and PCB, payslips and bank files.",
     ["HTML", "CSS", "JavaScript", "MySQL"], "Diploma internship"),
    ("StudentManagementSystem", "Student Management", "Admin, teacher and student views for fees, receipts and grades.",
     ["HTML", "CSS", "JavaScript", "MySQL"], "Diploma internship"),
    ("FaceRecognitionDoorLock", "Face Recognition Door Lock", "Raspberry Pi 4 door lock that opens for known faces, with a web dashboard.",
     ["Python", "OpenCV", "Flask", "Raspberry Pi"], "Diploma Final Year Project"),
    ("DigitalIncubation", "AI Engineer 90 Days", "A 90 day self-study plan with a bilingual logbook.",
     ["Python", "GitHub Pages", "Logbook"], "Self-study"),
]


def wrap(text, width):
    lines, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    return lines + [cur]


_clips = []


def typed(text, x, y, size, color, start, dur, mono=True):
    """Text that appears letter by letter once, using a growing clip."""
    w = len(text) * size * 0.62
    _clips.append(text)
    cid = f"type{len(_clips)}"
    return (
        f'<clipPath id="{cid}"><rect x="{x - w / 2:.0f}" y="{y - size}" width="0" height="{size * 1.5}">'
        f'<animate attributeName="width" from="0" to="{w + 8:.0f}" begin="{start}s" dur="{dur}s" fill="freeze" calcMode="discrete" keyTimes="{";".join(f"{i / len(text):.3f}" for i in range(len(text) + 1))}" values="{";".join(f"{i / len(text) * (w + 8):.0f}" for i in range(len(text) + 1))}"/></rect></clipPath>'
        f'<text x="{x}" y="{y}" text-anchor="middle" fill="{color}" font-size="{size}" font-family="{MONO if mono else FONT}" clip-path="url(#{cid})">{escape(text)}</text>'
    )


def hero():
    W, H = 860, 200
    s = [svg_open(W, H), frame(2, 2, W - 4, H - 4)]
    s.append(typed("Hi, I'm Cheah. An AI engineer in training", W / 2, 54, 24, TITLE, 0.3, 2.2))
    s.append(typed("A curious coder, always learning", W / 2, 92, 20, CYAN, 2.8, 1.6))
    s.append(f'<text x="{W / 2}" y="126" text-anchor="middle" fill="{SOFT}" font-size="14">Interested in NLP, LLM apps and tools that help people decide.</text>')
    chips = [("UTeM · Year 3 CS (AI)", TITLE), ("Malaysia", CYAN), ("Taking freelance jobs for experience", GREEN)]
    widths = [len(t) * 12 * 0.62 + 24 for t, _ in chips]
    x = (W - sum(widths) - 12 * (len(chips) - 1)) / 2
    for (t, col), w in zip(chips, widths):
        s.append(chip(x, 148, escape(t), col)[0])
        x += w + 12
    s.append("</svg>")
    return "".join(s)


def whoami():
    W, H = 540, 300
    lines = [
        ("$ whoami", CYAN), ("cheah", INK), ("", INK), ("$ current_focus", CYAN),
        ("- Building CareerBridge AI, resume to job match", INK),
        ("- NLP and LLM apps with Python and FastAPI", INK),
        ("- Fuzzy logic and ML for decision support", INK),
        ("- Learning robotics with ROS on the side", INK), ("", INK),
        ("$ stack", CYAN), ("Python / FastAPI / Flutter / Supabase / sklearn", GOLD),
    ]
    s = [svg_open(W, H, MONO), frame(2, 2, W - 4, H - 4, fill=PANEL)]
    for i, col in enumerate([RED, GOLD, GREEN]):
        s.append(f'<circle cx="{22 + i * 18}" cy="22" r="5.5" fill="{col}"/>')
    s.append(f'<text x="{W / 2}" y="26" text-anchor="middle" fill="{FAINT}" font-size="12">cheah@utem: ~</text>')
    for i, (text, col) in enumerate(lines):
        y = 58 + i * 21
        # each line shows up one after another, once
        s.append(f'<text x="22" y="{y}" fill="{col}" font-size="13.5" opacity="0">{escape(text)}'
                 f'<animate attributeName="opacity" from="0" to="1" begin="{0.3 + i * 0.35:.2f}s" dur="0.2s" fill="freeze"/></text>')
    y = 58 + len(lines) * 21
    s.append(f'<rect x="22" y="{y - 13}" width="9" height="16" fill="{CYAN}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>')
    s.append("</svg>")
    return "".join(s)


def project(repo, info, title, desc, tags, label):
    W, H = 420, 170
    s = [svg_open(W, H), frame(2, 2, W - 4, H - 4)]
    s.append(f'<text x="22" y="38" fill="{TITLE}" font-size="18" font-weight="700">{escape(title)}</text>')
    s.append(f'<text x="{W - 22}" y="37" text-anchor="end" fill="{FAINT}" font-size="11.5">{escape(label)}</text>')
    for i, ln in enumerate(wrap(desc, 52)[:2]):
        s.append(f'<text x="22" y="{64 + i * 19}" fill="{SOFT}" font-size="13">{escape(ln)}</text>')
    x = 22
    for t in tags:
        c, w = chip(x, 100, escape(t), EDGE, mono=False, size=11.5)
        s.append(c)
        x += w + 8
    lang = info.get("primaryLanguage") or {}
    foot = [f'<circle cx="28" cy="148" r="5" fill="{lang.get("color") or SOFT}"/><text x="40" y="152" fill="{SOFT}" font-size="12">{escape(lang.get("name", ""))}</text>',
            f'<text x="150" y="152" fill="{GOLD}" font-size="12">★ {info.get("stargazerCount", 0)}</text>']
    if info.get("homepageUrl"):
        foot.append(f'<rect x="{W - 112}" y="136" width="90" height="24" rx="12" fill="{GREEN}" fill-opacity="0.15" stroke="{GREEN}"/>'
                    f'<text x="{W - 67}" y="152" text-anchor="middle" fill="{GREEN}" font-size="12" font-weight="700">Live demo</text>')
    s += foot
    s.append("</svg>")
    return "".join(s)


def cup(x, y, color):
    return (f'<path d="M{x - 16},{y} h32 v10 a16,16 0 0 1 -32,0 z" fill="{color}" fill-opacity="0.25" stroke="{color}" stroke-width="2"/>'
            f'<path d="M{x - 16},{y + 4} h-6 a6,7 0 0 0 6,10 M{x + 16},{y + 4} h6 a6,7 0 0 1 -6,10" fill="none" stroke="{color}" stroke-width="2"/>'
            f'<path d="M{x - 3},{y + 26} h6 v8 h8 v5 h-22 v-5 h8 z" fill="{color}"/>')


def rank(value, steps):
    for letter, need in zip(["S", "A", "B", "C"], steps):
        if value >= need:
            return letter
    return "?"


def trophies(stats):
    W, H = 860, 180
    s = [svg_open(W, H), frame(2, 2, W - 4, H - 4)]
    s.append(f'<text x="{W / 2}" y="32" text-anchor="middle" fill="{TITLE}" font-size="16" font-weight="700">My GitHub Trophies</text>')
    colors = {"S": GOLD, "A": CYAN, "B": TITLE, "C": SOFT, "?": FAINT}
    items = [("Commits", stats["commits"], (1000, 400, 100, 20)), ("Contributions", stats["total"], (2000, 800, 200, 50)),
             ("Repositories", stats["repos"], (30, 15, 6, 2)), ("Pull requests", stats["prs"], (100, 40, 10, 1)),
             ("Stars", stats["stars"], (100, 30, 5, 1)), ("Longest streak", stats["longest"], (100, 30, 10, 3))]
    for i, (name, val, steps) in enumerate(items):
        cx = 72 + i * 143
        r = rank(val, steps)
        col = colors[r]
        s.append(f'<rect x="{cx - 62}" y="46" width="124" height="118" rx="10" fill="{PANEL}" stroke="{col}" stroke-opacity="0.6"/>')
        s.append(cup(cx, 62, col))
        s.append(f'<text x="{cx}" y="80" text-anchor="middle" fill="{BG}" font-size="13" font-weight="800">{r}</text>')
        s.append(f'<text x="{cx}" y="128" text-anchor="middle" fill="{INK}" font-size="12.5" font-weight="700">{name}</text>')
        s.append(f'<text x="{cx}" y="148" text-anchor="middle" fill="{FAINT}" font-size="11.5">{val:,}</text>')
    s.append("</svg>")
    return "".join(s)


def fetch():
    q = """query($login:String!){ user(login:$login){ createdAt followers{ totalCount }
      repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100, isFork:false){ totalCount nodes{ name stargazerCount homepageUrl primaryLanguage{ name color } } } } }"""
    u = gql(q, login=LOGIN)["user"]
    repos = {r["name"]: r for r in u["repositories"]["nodes"]}
    commits = prs = total = 0
    days = {}
    for year in range(int(u["createdAt"][:4]), date.today().year + 1):
        c = gql("""query($login:String!,$from:DateTime!,$to:DateTime!){ user(login:$login){ contributionsCollection(from:$from,to:$to){
          totalCommitContributions totalPullRequestContributions contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } } } }""",
                login=LOGIN, **{"from": f"{year}-01-01T00:00:00Z", "to": f"{year}-12-31T23:59:59Z"})["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"]
        prs += c["totalPullRequestContributions"]
        total += c["contributionCalendar"]["totalContributions"]
        for w in c["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = d["contributionCount"]
    longest = run = 0
    for d in sorted(days):
        if d > date.today().isoformat():
            break
        run = run + 1 if days[d] else 0
        longest = max(longest, run)
    stats = {"commits": commits, "prs": prs, "total": total, "repos": u["repositories"]["totalCount"],
             "stars": sum(r["stargazerCount"] for r in repos.values()), "longest": longest}
    return repos, stats


out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
out.mkdir(parents=True, exist_ok=True)
repos, stats = fetch()
(out / "hero.svg").write_text(hero(), encoding="utf-8")
(out / "whoami.svg").write_text(whoami(), encoding="utf-8")
(out / "trophies.svg").write_text(trophies(stats), encoding="utf-8")
for repo, title, desc, tags, label in PROJECTS:
    (out / f"project-{repo.lower()}.svg").write_text(project(repo, repos.get(repo, {}), title, desc, tags, label), encoding="utf-8")
print("wrote cards to", out, stats)
