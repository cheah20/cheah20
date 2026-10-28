"""Draw the skill chips card (assets/skills.svg).

Icons come from Simple Icons and are copied into the SVG, because GitHub
does not load images linked from inside an SVG.
"""
import re
import sys
import urllib.request
from html import escape
from pathlib import Path

GROUPS = [
    ("AI / ML", [("scikit-learn", "scikitlearn"), ("PyTorch", "pytorch"), ("Hugging Face", "huggingface"),
                 ("ONNX", "onnx"), ("pandas", "pandas"), ("NumPy", "numpy")]),
    ("NLP / LLM", [("DeepSeek", "deepseek"), ("Transformers", "huggingface"), ("Tokenizers", None),
                   ("RapidOCR", None), ("Prompting", None)]),
    ("AI SYSTEMS", [("Fuzzy Logic", None), ("ANFIS", None), ("SVM", None), ("Agent pipeline", None)]),
    ("BACKEND", [("Python", "python"), ("FastAPI", "fastapi"), ("Flask", "flask"), ("Supabase", "supabase"),
                 ("PostgreSQL", "postgresql"), ("pytest", "pytest")]),
    ("FRONTEND", [("Flutter", "flutter"), ("Dart", "dart"), ("HTML", "html5"), ("CSS", "css"),
                  ("JavaScript", "javascript"), ("React", "react")]),
    ("TOOLS", [("Git", "git"), ("GitHub Actions", "githubactions"), ("Linux", "linux"), ("Ubuntu", "ubuntu"),
               ("ROS", "ros"), ("Conda", "anaconda")]),
]

BG, CARD_EDGE, INK, LABEL, CHIP_BG = "#1a1b27", "#2a2e45", "#c0caf5", "#7aa2f7", "#22243a"
FONT = "Segoe UI, Ubuntu, Helvetica, Arial, sans-serif"


def icon(slug):
    """Path and brand colour of one Simple Icons logo."""
    req = urllib.request.Request(f"https://cdn.simpleicons.org/{slug}", headers={"User-Agent": "profile-readme"})
    svg = urllib.request.urlopen(req, timeout=20).read().decode()
    d = re.search(r'<path[^>]* d="([^"]+)"', svg).group(1)
    fill = re.search(r'fill="(#[0-9a-fA-F]{3,6})"', svg)
    return d, fill.group(1) if fill else INK


def dark(hex_color):
    """True when a colour is too dark to see on the card."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.3


def build():
    cache = {}
    width, x0, row_h, top = 860, 150, 44, 24
    rows = []
    for gi, (label, items) in enumerate(GROUPS):
        y = top + gi * row_h
        rows.append(f'<text x="24" y="{y + 18}" fill="{LABEL}" font-size="11" font-weight="700" letter-spacing="1.5">{escape(label)}</text>')
        x = x0
        for name, slug in items:
            w = len(name) * 7.2 + (40 if slug else 26)
            if slug:
                cache.setdefault(slug, icon(slug))
                d, col = cache[slug]
            else:
                d, col = None, "#9ece6a"
            if dark(col):
                col = INK  # dark logos would vanish on the dark card
            parts = [f'<rect x="{x}" y="{y}" width="{w:.0f}" height="28" rx="14" fill="{CHIP_BG}" stroke="{col}" stroke-opacity="0.55"/>']
            tx = x + 14
            if d:
                parts.append(f'<g transform="translate({x + 11},{y + 7}) scale(0.5833)"><path d="{d}" fill="{col}"/></g>')
                tx = x + 31
            else:
                parts.append(f'<circle cx="{x + 13}" cy="{y + 14}" r="3" fill="{col}"/>')
                tx = x + 22
            parts.append(f'<text x="{tx}" y="{y + 18.5}" fill="{INK}" font-size="12.5" font-weight="600">{escape(name)}</text>')
            rows.append("".join(parts))
            x += w + 8
    height = top + len(GROUPS) * row_h + 10
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{FONT}">'
            f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{BG}" stroke="{CARD_EDGE}"/>'
            + "".join(rows) + "</svg>")


out = Path(sys.argv[1] if len(sys.argv) > 1 else "assets/skills.svg")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(build(), encoding="utf-8")
print("wrote", out)
