"""Render a GitHub-compatible terminal card with ONLY its ASCII face animated."""
from pathlib import Path
import random
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "animated-terminal-card.gif"
W, H = 1024, 430
FRAMES = 60
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
            face.append((ch, 38 + col * 7.2, 78 + row * 9.7,
                         rng.uniform(-170, 170), rng.uniform(-130, 130),
                         rng.uniform(0, .05)))

def smooth(t):
    t = max(0., min(1., t))
    return t*t*(3-2*t)

def assembled(t, offset):
    t = (t - offset) % 1.
    if t < .32: return smooth(t/.32)
    if t < .72: return 1.
    if t < .92: return 1.-smooth((t-.72)/.20)
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
    # Eight coordinated effects, confined to the portrait area:
    # matrix rain, particle assembly, blinking, hologram scan,
    # glitch, rotation illusion, terminal cursor and HUD pulse.
    scan_y = 78 + int((phase * 2.7 % 1) * 292)
    pulse = .5 + .5 * math.sin(phase * 2 * math.pi * 3)
    d.rounded_rectangle((25, 65, 524, 390), radius=12,
                        outline=(15, int(58 + 40*pulse), int(92 + 70*pulse)), width=2)
    for k in range(13):
        rain_x = 39 + k * 36
        rain_y = 74 + ((f * (4 + k % 4) * 3 + k * 43) % 290)
        for j in range(5):
            yy = rain_y - j * 15
            if 75 < yy < 375:
                d.text((rain_x, yy), "01@#%+"[(k+j+f//3) % 6], font=small,
                       fill=(14, 43 + j*6, 69 + j*11))
    d.line((27, scan_y, 519, scan_y), fill=(18, 94, 149), width=2)
    # Subtle faux 3D head turn: shift only face glyphs, never the card.
    turn = math.sin(phase * 2 * math.pi) * 5
    blink = .48 < phase < .51 or .80 < phase < .825
    glitch = .70 < phase < .75
    for index, (ch, x, y, dx, dy, delay) in enumerate(face):
        a = assembled(phase, delay)
        if a <= .08:
            continue
        angle = phase * 4 * math.pi + index * .11
        orbit = (1-a) * 36
        xx = x + (1-a)*dx + orbit*math.cos(angle) + turn * ((x-260)/260)
        yy = y + (1-a)*dy + orbit*math.sin(angle)
        # Eye-line blinking illusion via temporary horizontal compression.
        if blink and 185 < y < 221:
            yy = 204 + (yy-204)*.18
        # A short, localized horizontal glitch near the end of the loop.
        if glitch and int(y)//14 % 3 == 0:
            xx += 13 if index % 2 else -9
        # Keep particles inside the portrait panel; never cross into details.
        if not (29 <= xx <= 512 and 68 <= yy <= 378):
            continue
        shimmer = max(0, 1-abs(scan_y-y)/20)
        glow = min(1, .65*a + .35*shimmer + .08*pulse)
        d.text((xx, yy), ch, font=small,
               fill=(int(20+95*glow), int(59+146*glow), int(100+148*glow)))
    d.text((38, 399), "ASCII // NEURAL RECONSTRUCTION", font=small,
           fill=(56, 189, 248))
    if f % 8 < 5:
        d.rectangle((261, 400, 268, 411), fill=(56, 189, 248))
    frames.append(im.quantize(colors=128, method=Image.Quantize.FASTOCTREE))

OUT.parent.mkdir(parents=True, exist_ok=True)
frames[0].save(OUT, save_all=True, append_images=frames[1:],
               duration=150, loop=0, optimize=True, disposal=2)
print(f"Created {OUT}: animated ASCII face, static profile information")
