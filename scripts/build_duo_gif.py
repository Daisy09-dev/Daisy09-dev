"""Render a GitHub-compatible terminal card with ONLY its ASCII face animated."""
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "animated-duo.gif"  # Retained path for existing README compatibility
W, H = 1024, 430
FRAMES = 32
rng = random.Random(909)

def font(size, bold=False):
    base = "/usr/share/fonts/truetype/dejavu/"
    name = "DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"
    return ImageFont.truetype(base + name, size)

mono = font(16)
small = font(11)
heading = font(20, True)
title = font(17, True)
lines = (ROOT / "portrait.txt").read_text(encoding="utf-8").splitlines()
face = []
for row, line in enumerate(lines):
    for col, ch in enumerate(line):
        if ch != " ":
            face.append((ch, 47 + col * 8.5, 78 + row * 10.0,
                         rng.uniform(-90, 90), rng.uniform(-85, 85),
                         rng.uniform(0, .05)))

def smooth(t):
    t = max(0., min(1., t))
    return t*t*(3-2*t)

def assembled(t, offset):
    t = (t - offset) % 1.
    if t < .30: return smooth(t/.30)
    if t < .67: return 1.
    if t < .85: return 1.-smooth((t-.67)/.18)
    return 0.

frames = []
for f in range(FRAMES):
    phase = f / FRAMES
    im = Image.new("RGB", (W, H), (8, 13, 22))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, W-9, H-9), radius=18, outline=(46, 59, 74), width=2)
    d.rounded_rectangle((9, 9, W-10, 49), radius=17, fill=(20, 27, 37))
    d.rectangle((9, 31, W-10, 49), fill=(20, 27, 37))
    d.line((9, 49, W-10, 49), fill=(46, 59, 74), width=1)
    for j, col in enumerate([(56, 139, 253), (89, 172, 255), (125, 211, 252)]):
        d.ellipse((29 + j*23, 25, 41 + j*23, 37), fill=col)
    d.text((386, 22), "daisy09-dev@github: ~", font=small, fill=(160, 174, 192))
    d.text((565, 80), "daisy09-dev@github", font=heading, fill=(96, 165, 250))
    d.line((565, 112, 870, 112), fill=(48, 63, 78), width=2)
    rows = [
        ("Name", "Syrah Fundal"),
        ("Role", "Aspiring Software Engineer"),
        ("Education", "BSIT · 2nd year"),
        ("Stack", "Python · Flask · SQLite · Git"),
        ("Building", "RCG Routine"),
        ("Location", "Philippines"),
        ("GitHub", "Daisy09-dev"),
        ("Status", "Learning · Building · Contributing"),
    ]
    for j, (key, value) in enumerate(rows):
        y = 133 + j*29
        d.text((565, y), key, font=mono, fill=(96, 165, 250))
        d.text((665, y), ": " + value, font=mono, fill=(203, 213, 225))
    for j, color in enumerate([(12,50,108),(12,75,158),(18,108,210),(56,139,253),
                                (96,165,250),(125,190,250),(186,230,253)]):
        d.rectangle((565+j*34, 386, 599+j*34, 399), fill=color)
    for ch, x, y, dx, dy, delay in face:
        a = assembled(phase, delay)
        if a > .10:
            d.text((x+(1-a)*dx, y+(1-a)*dy), ch, font=small,
                   fill=(int(30+66*a), int(65+100*a), int(105+145*a)))
    frames.append(im.quantize(colors=128, method=Image.Quantize.FASTOCTREE))

OUT.parent.mkdir(parents=True, exist_ok=True)
frames[0].save(OUT, save_all=True, append_images=frames[1:],
               duration=250, loop=0, optimize=True, disposal=2)
print(f"Created {OUT}: animated ASCII face, static profile information")
