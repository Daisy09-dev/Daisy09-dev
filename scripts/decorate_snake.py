"""Attach two companions to the original contribution snake animation."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
SVG="http://www.w3.org/2000/svg"
ET.register_namespace("",SVG)
def tag(n): return "{"+SVG+"}"+n
def decorate(path):
    tree=ET.parse(path)
    root=tree.getroot()
    for item in list(root):
        if item.get("id")=="skyblue-snake-companions": root.remove(item)
    style=root.find(tag("style"))
    if style is None or "@keyframes s0" not in style.text: raise ValueError("Missing original snake animation")
    style.text=style.text.split("/* companion-sync */")[0]
    duration=re.search(r"\.s\{[^}]*?([0-9]+ms)",style.text)
    if not duration: raise ValueError("Missing animation duration")
    ms=int(duration.group(1)[:-2])
    layer=ET.SubElement(root,tag("g"),{"id":"skyblue-snake-companions"})
    css=[]
    for j,(color,delay) in enumerate([("#38bdf8",.075),("#a5eaff",.17)]):
        for i in reversed(range(7 if j==0 else 5)):
            name=f"comp{j}_{i}"
            lag=round(ms*(delay+i*.009))
            css.append(f".{name}{{animation:s0 {ms}ms linear -{ms-lag}ms infinite;}}")
            g=ET.SubElement(layer,tag("g"),{"class":name})
            ET.SubElement(g,tag("circle"),{"cx":"8","cy":"8","r":str(5.6-i*.32 if j==0 else 4.4-i*.28),"fill":color})
            if i==0:
                for x in (6,10): ET.SubElement(g,tag("circle"),{"cx":str(x),"cy":"6","r":"1.1","fill":"#07304a"})
    for name, delay, markup in [["ghost",0.29,"<path d=\"M2 13V7a6 6 0 0 1 12 0v6l-3-2-3 2-3-2Z\" fill=\"#f9a8d4\"/><circle cx=\"6\" cy=\"7\" r=\"1.5\" fill=\"#17263a\"/><circle cx=\"10\" cy=\"7\" r=\"1.5\" fill=\"#17263a\"/>"],["pac",0.4,"<path d=\"M14 4A7 7 0 1 0 14 12L8 8Z\" fill=\"#facc15\"/><circle cx=\"8\" cy=\"4\" r=\"1\" fill=\"#17263a\"/>"]]:
        css.append(f".friend-{name}{{animation:s0 {ms}ms linear -{ms-round(ms*delay)}ms infinite;}}")
        friend=ET.SubElement(layer,tag("g"),{"class":"friend-"+name})
        for child in ET.fromstring('<g xmlns="'+SVG+'">'+markup+'</g>'):
            friend.append(child)
    for i, delay in enumerate([.10,.35,.65]):
        css.append(f".apple{i}{{animation:s0 {ms}ms linear -{round(ms*delay)}ms infinite;}}.fruit{i}{{animation:fruitblink {ms}ms linear -{round(ms*delay)}ms infinite;}}")
        fruit=ET.SubElement(ET.SubElement(layer,tag("g"),{"class":f"apple{i}"}),tag("g"),{"class":f"fruit{i}"})
        for child in ET.fromstring('<g xmlns="'+SVG+'">'+"<path d=\"M8 4C2 0 0 8 4 12Q8 15 12 12C16 8 14 0 8 4Z\" fill=\"#ef4444\"/><path d=\"M8 4V1\" stroke=\"#a16207\" stroke-width=\"1.5\"/><path d=\"M8 3Q10 -1 13 1Q12 4 8 3\" fill=\"#4ade80\"/>"+'</g>'):
            fruit.append(child)
    css.append("@keyframes fruitblink{0%,85%{opacity:1}90%,100%{opacity:0}}")
    layer.append(ET.fromstring("<g xmlns=\"http://www.w3.org/2000/svg\" transform=\"translate(320 -27)\" font-family=\"Arial,sans-serif\"><rect width=\"210\" height=\"22\" rx=\"5\" fill=\"#17263a\" stroke=\"#58a6ff\"/><text x=\"105\" y=\"15\" text-anchor=\"middle\" font-size=\"11\" fill=\"#e0f2fe\">Hi! Feel free to explore my repos.</text></g>"))
    style.text+="/* companion-sync */"+"".join(css)
    tree.write(path,encoding="unicode")
if __name__=="__main__":
    for name in ("github-snake.svg","github-snake-dark.svg"):
        decorate(Path("dist")/name)
