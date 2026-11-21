"""Generate a GitHub-compatible synchronized ASCII-face + Chinese capybara GIF."""
from pathlib import Path
import math
import random
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "animated-duo.gif"
W, H = 960, 350
FRAMES = 32
DURATION = 250  # 8-second loop, both subjects share one timeline
BG = (5, 12, 28)
BLUE = (56, 189, 248)
ICE = (186, 230, 253)
rng = random.Random(909)

def font(size, cjk=False):
    options = (
        ["/usr/share/fonts/truetype/arphic/ukai.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]
        if cjk else
        ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
    )
    for path in options:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def ease(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)

def assembly(phase, delay):
    t = (phase - delay) % 1
    if t < .29:
        return ease(t / .29)
    if t < .68:
        return 1.
    if t < .85:
        return 1 - ease((t - .68) / .17)
    return 0.

def blend(a, b, t):
    return a + (b - a) * t

# Portrait is rendered character by character, preserving the exact ASCII source.
face = []
lines = (ROOT / "portrait.txt").read_text(encoding="utf-8").splitlines()
for row, line in enumerate(lines):
    for col, char in enumerate(line):
        if char != " ":
            x, y = 42 + col * 7.1, 78 + row * 8.0
            face.append((char, x, y, rng.uniform(-130, 130), rng.uniform(-105, 105), rng.random() * .06))

# Parse the existing capybara SVG so its actual Chinese characters define the silhouette.
capy = []
tree = ET.parse(ROOT / "assets" / "capybara.svg")
for el in tree.iter():
    if el.tag.endswith("text") and el.get("x") and el.get("y"):
        content = (el.text or "").strip()
        if len(content) == 1 and ord(content) > 127:
            x, y = float(el.get("x")), float(el.get("y"))
            capy.append((content, 520 + (x - 116) * .77, 69 + (y - 63) * .78,
                         rng.uniform(-120, 120), rng.uniform(-100, 100), rng.random() * .06))

font_face = font(12)
font_cjk = font(15, cjk=True)
font_title = font(19)
font_small = font(13)
frames = []

for frame in range(FRAMES):
    phase = frame / FRAMES
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, W - 10, H - 10), radius=18, outline=(29, 75, 110), width=2)
    d.text((34, 23), "DAISY09 // SYNCED CHARACTER ASSEMBLY", font=font_title, fill=ICE)
    d.line((34, 54, W - 34, 54), fill=(29, 75, 110), width=1)
    d.text((110, 312), "ASCII PORTRAIT", font=font_small, fill=BLUE)
    d.text((660, 312), "TYPOGRAPHY CAPYBARA", font=font_small, fill=BLUE)
    for char, x, y, dx, dy, delay in face:
        a = assembly(phase, delay)
        xx = blend(x + dx, x, a)
        yy = blend(y + dy, y, a)
        if a > .12:
            d.text((xx, yy), char, font=font_face, fill=(int(18 + 38*a), int(70 + 119*a), int(120 + 128*a)))
    for char, x, y, dx, dy, delay in capy:
        a = assembly(phase, delay)
        if a > .12:
            d.text((blend(x+dx,x,a), blend(y+dy,y,a)), char, font=font_cjk,
                   fill=(int(22+164*a), int(70+160*a), int(120+133*a)))
    frames.append(im.quantize(colors=96, method=Image.Quantize.FASTOCTREE))

OUT.parent.mkdir(parents=True, exist_ok=True)
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=DURATION,
               loop=0, optimize=True, disposal=2)
print(f"Wrote {OUT} with {FRAMES} synchronized frames")
