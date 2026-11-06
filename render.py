"""Render the terminal-style profile card (dark + light SVG).

Reads  profile.json and portrait.txt
Writes neofetch-dark.svg and neofetch-light.svg

Live numbers (repos, followers, member since) come from the GitHub API.
If the API cannot be reached, the values in profile.json are used instead.
Only the Python standard library is needed.
"""
import json
import os
import urllib.request
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.abspath(__file__))

THEMES = {
    "dark": dict(
        bg="#0d1117", border="#30363d", bar="#161b22", title="#8b949e",
        key="#58a6ff", val="#c9d1d9", dim="#8b949e", rule="#30363d",
        ascii_top="#a5d6ff", ascii_bot="#1f6feb",
        swatch=["#0a3069", "#0550ae", "#0969da", "#388bfd", "#58a6ff", "#79c0ff", "#a5d6ff", "#cae8ff"],
        dots=["#388bfd", "#58a6ff", "#79c0ff"],
    ),
    "light": dict(
        bg="#ffffff", border="#d0d7de", bar="#f6f8fa", title="#57606a",
        key="#0969da", val="#24292f", dim="#57606a", rule="#d0d7de",
        ascii_top="#0969da", ascii_bot="#0a3069",
        swatch=["#0a3069", "#0550ae", "#0969da", "#218bff", "#54aeff", "#80ccff", "#b6e3ff", "#ddf4ff"],
        dots=["#0969da", "#54aeff", "#80ccff"],
    ),
}
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', 'Liberation Mono', monospace"


def load_profile():
    with open(os.path.join(ROOT, "profile.json"), encoding="utf-8") as f:
        return json.load(f)


def live_stats(profile):
    stats = dict(profile.get("fallback_stats", {}))
    req = urllib.request.Request(
        f"https://api.github.com/users/{profile['username']}",
        headers={"User-Agent": "profile-card", "Accept": "application/vnd.github+json"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.load(r)
        stats["repos"] = d.get("public_repos", stats.get("repos", 0))
        stats["followers"] = d.get("followers", stats.get("followers", 0))
        stats["since"] = (d.get("created_at") or "")[:4]
    except Exception as exc:  # offline or rate limited: keep fallback numbers
        print(f"note: using fallback stats ({exc})")
    return stats


def build(theme_name, profile, stats, art):
    t = THEMES[theme_name]
    art_font, art_cw, art_lh = 10, 6.0, 10.4
    pad_x, bar_h = 28, 36
    art_x, art_y = pad_x, bar_h + 28
    art_w = max(len(line) for line in art) * art_cw
    info_x = int(art_x + art_w + 44)
    width = info_x + 400
    height = int(art_y + len(art) * art_lh + 28)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Terminal profile card for {escape(profile["name"])}">',
        "<defs>",
        f'<linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" y1="{art_y}" x2="0" y2="{art_y + len(art) * art_lh}">'
        f'<stop offset="0" stop-color="{t["ascii_top"]}"/><stop offset="1" stop-color="{t["ascii_bot"]}"/></linearGradient>',
        f'<clipPath id="c"><rect width="{width}" height="{height}" rx="12"/></clipPath>',
        "</defs>",
        f'<g clip-path="url(#c)">',
        f'<rect width="{width}" height="{height}" fill="{t["bg"]}"/>',
        f'<rect width="{width}" height="{bar_h}" fill="{t["bar"]}"/>',
        f'<line x1="0" y1="{bar_h}" x2="{width}" y2="{bar_h}" stroke="{t["border"]}"/>',
    ]
    for i, c in enumerate(t["dots"]):
        out.append(f'<circle cx="{22 + i * 20}" cy="{bar_h // 2}" r="6" fill="{c}"/>')
    out.append(
        f'<text x="{width // 2}" y="{bar_h // 2 + 4}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="12" fill="{t["title"]}">{escape(profile["username"])}@github: ~</text>'
    )

    # ASCII portrait
    out.append(f'<text font-family="{FONT}" font-size="{art_font}" fill="url(#g)" xml:space="preserve">')
    for i, line in enumerate(art):
        out.append(f'<tspan x="{art_x}" y="{art_y + i * art_lh:.1f}">{escape(line)}</tspan>')
    out.append("</text>")

    # Info panel
    handle = f'{profile["username"]}@github'
    rows = [
        ("Name", profile["name"]),
        ("Role", profile["role"]),
        ("Education", profile["education"]),
        ("Stack", profile["stack"]),
        ("Building", profile["building"]),
        ("Location", profile["location"]),
    ]
    nr, nf = stats.get("repos", 0), stats.get("followers", 0)
    stat_bits = [f'{nr} repo{"" if nr == 1 else "s"}', f'{nf} follower{"" if nf == 1 else "s"}']
    if stats.get("since"):
        stat_bits.append(f'since {stats["since"]}')
    rows.append(("GitHub", " · ".join(stat_bits)))
    rows.append(("Status", profile["status"]))

    y = art_y + 6
    lh = 24
    out.append(f'<text x="{info_x}" y="{y}" font-family="{FONT}" font-size="15" font-weight="700" fill="{t["key"]}">{escape(handle)}</text>')
    y += 10
    out.append(f'<line x1="{info_x}" y1="{y}" x2="{info_x + len(handle) * 9.2:.0f}" y2="{y}" stroke="{t["rule"]}"/>')
    y += 24
    for key, val in rows:
        out.append(
            f'<text x="{info_x}" y="{y}" font-family="{FONT}" font-size="13">'
            f'<tspan fill="{t["key"]}" font-weight="700">{escape(key)}</tspan>'
            f'<tspan fill="{t["dim"]}">: </tspan>'
            f'<tspan fill="{t["val"]}">{escape(val)}</tspan></text>'
        )
        y += lh
    y += 8
    for i, c in enumerate(t["swatch"]):
        out.append(f'<rect x="{info_x + i * 26}" y="{y}" width="26" height="16" fill="{c}"/>')

    out.append("</g>")
    out.append(f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="none" stroke="{t["border"]}"/>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    profile = load_profile()
    stats = live_stats(profile)
    with open(os.path.join(ROOT, "portrait.txt"), encoding="utf-8") as f:
        art = f.read().rstrip("\n").split("\n")
    for name in THEMES:
        path = os.path.join(ROOT, f"neofetch-{name}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(name, profile, stats, art))
        print("wrote", path)


if __name__ == "__main__":
    main()
