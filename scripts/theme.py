"""Colours, fonts and small helpers shared by every profile card."""
import json
import os
import urllib.request

LOGIN = os.environ.get("PROFILE_USER", "cheah20")

# dark navy with blue neon edges
BG = "#070b18"
PANEL = "#0b1430"
EDGE = "#2b5cff"
GLOW = "#3b82f6"
INK = "#dbe4ff"
SOFT = "#a9b6d8"
FAINT = "#6f7da3"
TITLE = "#8ea2ff"
CYAN = "#38bdf8"
GREEN = "#34d399"
GOLD = "#fbbf24"
PINK = "#f472b6"
RED = "#f87171"

FONT = "Segoe UI, Ubuntu, Helvetica, Arial, sans-serif"
MONO = "JetBrains Mono, Consolas, Menlo, monospace"


def gql(query, **variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    data = json.load(urllib.request.urlopen(req, timeout=30))
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]


def svg_open(w, h, font=FONT):
    # one glow filter and one edge gradient, used by frame()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{font}">'
        f'<defs><filter id="glow" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="3"/></filter>'
        f'<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{EDGE}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient></defs>'
    )


def frame(x, y, w, h, r=14, fill=BG):
    """A panel with a soft neon edge."""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{GLOW}" stroke-width="4" stroke-opacity="0.55" filter="url(#glow)"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="url(#edge)" stroke-width="1.6"/>'
    )


def chip(x, y, text, color, mono=True, size=12):
    """A small outlined label like the badges on the hero card."""
    w = len(text) * size * 0.62 + 24
    return (
        f'<rect x="{x}" y="{y}" width="{w:.0f}" height="26" rx="5" fill="{PANEL}" stroke="{color}" stroke-opacity="0.8"/>'
        f'<text x="{x + w / 2:.0f}" y="{y + 17.5}" text-anchor="middle" fill="{INK}" font-size="{size}" font-family="{MONO if mono else FONT}">{text}</text>'
    ), w
