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
    style.text+="/* companion-sync */"+"".join(css)
    tree.write(path,encoding="unicode")
if __name__=="__main__":
    for name in ("github-snake.svg","github-snake-dark.svg"):
        decorate(Path("dist")/name)
