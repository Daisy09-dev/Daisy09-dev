import json, math, os, urllib.request
from pathlib import Path
from collections import Counter
from xml.sax.saxutils import escape
def get(url):
    req=urllib.request.Request(url,headers={"Authorization":"Bearer "+os.environ["GH_TOKEN"],"Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(req) as res: return json.load(res)
totals=Counter()
page=1
while True:
    repos=get(f"https://api.github.com/users/{os.environ['GH_USER']}/repos?per_page=100&page={page}")
    for repo in repos:
        if not repo["fork"] and not repo["private"] and repo["name"]!=os.environ["GH_USER"]:
            totals.update(get(repo["languages_url"]))
    if len(repos)<100: break
    page+=1
top=totals.most_common(6)
if len(top)<3: raise SystemExit("Not enough languages for radar")
n=len(top); total=sum(totals.values()); maximum=top[0][1]
def point(i,r):
    a=2*math.pi*i/n-math.pi/2
    return 320+r*math.cos(a),180+r*math.sin(a)
def polygon(radii):
    return " ".join(f"{x:.1f},{y:.1f}" for x,y in [point(i,r) for i,r in enumerate(radii)])
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="640" height="370" viewBox="0 0 640 370"><rect x="1" y="1" width="638" height="368" rx="14" fill="#0d1117" stroke="#30363d"/><g font-family="Arial,sans-serif"><text x="24" y="30" fill="#58a6ff" font-size="17" font-weight="bold">Language distribution</text>']
for level in range(1,6):
    parts.append(f'<polygon points="{polygon([110*level/5]*n)}" fill="none" stroke="#30363d"/>')
for i,(lang,count) in enumerate(top):
    x,y=point(i,110); lx,ly=point(i,140)
    anchor="middle" if abs(lx-320)<5 else ("start" if lx>320 else "end")
    parts.append(f'<line x1="320" y1="180" x2="{x}" y2="{y}" stroke="#30363d"/><text x="{lx}" y="{ly}" text-anchor="{anchor}" fill="#c9d1d9" font-size="12">{escape(lang)} {count/total:.1%}</text>')
parts.append(f'<polygon points="{polygon([110*c/maximum for _,c in top])}" fill="#38bdf8" fill-opacity=".23" stroke="#58a6ff" stroke-width="2"/>')
parts.append('<text x="320" y="350" text-anchor="middle" fill="#8b949e" font-size="11">Public non-fork repositories · code bytes · relative to largest language</text></g></svg>')
Path("assets/language-radar.svg").write_text("".join(parts))
