#!/usr/bin/env python3
"""Decorate Platane/snk SVGs with a long sky-blue serpent and a small companion.

The original contribution animation is preserved. Added creatures travel along
separate paths and use SVG animation, requiring no JavaScript in GitHub README.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
def tag(name):
    return f"{{{SVG}}}{name}"

def element(parent, name, attrs=None, text=None):
    child = ET.SubElement(parent, tag(name), attrs or {})
    if text is not None:
        child.text = text
    return child

def decorate(path):
    tree = ET.parse(path)
    root = tree.getroot()
    # Idempotent on repeated runs.
    for item in list(root):
        if item.get("id") == "skyblue-snake-companions":
            root.remove(item)
    layer = element(root, "g", {"id": "skyblue-snake-companions", "pointer-events": "none"})
    # Both paths are located in the extra upper/lower margins of the snk viewBox,
    # leaving the contribution grid and original animated snake readable.
    paths = [
        ("M 20,-18 C 190,-30 340,-5 480,-18 S 730,-26 835,-18", "16s", "#38bdf8", 1),
        ("M 835,146 C 690,161 530,137 380,150 S 140,161 20,146", "19s", "#a5eaff", 0.65),
    ]
    for i, (route, duration, color, scale) in enumerate(paths):
        creature = element(layer, "g", {"opacity": "0.98" if i == 0 else "0.88"})
        motion = element(creature, "animateMotion", {
            "dur": duration, "repeatCount": "indefinite", "rotate": "auto",
            "path": route,
        })
        # Long, tapered segmented body trailing the moving head.
        body = element(creature, "g", {"transform": f"scale({scale})"})
        for n in range(16 if i == 0 else 11, 0, -1):
            x = -n * (9 if i == 0 else 8)
            radius = (3.2 if i == 0 else 2.6) + (1 - n / (17 if i == 0 else 12)) * 2.5
            element(body, "circle", {
                "cx": str(x), "cy": str(1.5 * (n % 2)),
                "r": f"{radius:.2f}", "fill": color,
                "opacity": f"{0.48 + (1-n/20)*0.5:.2f}",
            })
        element(body, "ellipse", {"cx": "0", "cy": "0", "rx": "12", "ry": "8", "fill": color})
        element(body, "ellipse", {"cx": "6", "cy": "-3", "rx": "5", "ry": "3.6", "fill": "#d9f7ff"})
        element(body, "circle", {"cx": "7", "cy": "-3", "r": "1.9", "fill": "#07304a"})
        element(body, "circle", {"cx": "10", "cy": "2", "r": "1.2", "fill": "#07304a"})
        element(body, "path", {"d": "M 11,3 Q 18,4 20,1", "fill": "none", "stroke": "#fda4af", "stroke-width": "1.8", "stroke-linecap": "round"})
    tree.write(path, encoding="unicode", xml_declaration=False)

if __name__ == "__main__":
    for name in ("github-snake.svg", "github-snake-dark.svg"):
        file = Path("dist") / name
        if not file.exists():
            raise SystemExit(f"Missing generated asset: {file}")
        decorate(file)
        print(f"Decorated {file}")
