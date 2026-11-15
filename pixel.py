#!/usr/bin/env python3
"""Spaceflight-themed pixel banner for Awesome Craft Space."""
import random
from pathlib import Path

random.seed(42)
P = 8
W = 100
H = 34  # 800x272
out = []


def r(x, y, w, h, c, cls=None, extra=""):
    a = f' class="{cls}"' if cls else ""
    out.append(
        f'<rect x="{x*P}" y="{y*P}" width="{w*P}" height="{h*P}" fill="{c}"{a}{extra}/>'
    )


# 3x5 pixel font
F = {
    "A": ["010", "101", "111", "101", "101"],
    "C": ["011", "100", "100", "100", "011"],
    "E": ["111", "100", "110", "100", "111"],
    "F": ["111", "100", "110", "100", "100"],
    "P": ["110", "101", "110", "100", "100"],
    "R": ["110", "101", "110", "101", "101"],
    "S": ["011", "100", "010", "001", "110"],
    "T": ["111", "010", "010", "010", "010"],
    " ": ["000", "000", "000", "000", "000"],
}

style = """
<style>
.tw{animation:tw 2.4s steps(2) infinite}
.tw2{animation:tw 3.1s steps(2) infinite .8s}
.tw3{animation:tw 1.9s steps(2) infinite 1.4s}
@keyframes tw{0%,100%{opacity:1}50%{opacity:.15}}
.glow{animation:glow 1.6s steps(3) infinite}
@keyframes glow{0%,100%{opacity:.35}50%{opacity:1}}
.flame{animation:flame .28s steps(2) infinite}
.flame2{animation:flame .32s steps(2) infinite .12s}
@keyframes flame{0%,100%{opacity:1}50%{opacity:.35}}
.arm{animation:arm 3.6s steps(4) infinite}
@keyframes arm{0%,25%{transform:translate(0,0)}50%,75%{transform:translate(-16px,0)}100%{transform:translate(0,0)}}
.blink{animation:tw 1s steps(1) infinite}
.sat{animation:sat 8s linear infinite}
@keyframes sat{0%{transform:translate(0,0);opacity:0}8%{opacity:1}90%{opacity:1}100%{transform:translate(240px,24px);opacity:0}}
</style>
"""

# Night sky
sky = ["#050814", "#070b1c", "#0a1028", "#0d1734", "#111e42", "#14244c", "#182a56"]
for i, c in enumerate(sky):
    r(0, i * 4, W, 4, c)

# Horizon glow
r(0, 24, W, 1, "#1a2a4a")
r(0, 25, W, 1, "#243656")

# Stars, keep the title band clear
for i in range(42):
    while True:
        x = random.randrange(W)
        y = random.randrange(12)
        if not (20 <= x <= 80 and y <= 8):
            break
    r(x, y, 1, 1, random.choice(["#e2e8f0", "#fff7c2", "#93c5fd", "#cbd5e1"]), random.choice(["tw", "tw2", "tw3"]))

# Title: CRAFT SPACE
t = "CRAFT SPACE"
tx = (W - len(t) * 4) // 2
ty = 2
for k, ch in enumerate(t):
    for yy, row in enumerate(F[ch]):
        for xx, b in enumerate(row):
            if b == "1":
                r(tx + k * 4 + xx + 0.25, ty + yy + 0.25, 1, 1, "#000", None, ' opacity=".55"')
                r(tx + k * 4 + xx, ty + yy, 1, 1, "#fde68a")

# Distant hills / dune line
for x in range(W):
    hgt = 1 + (1 if (x // 7 + x // 3) % 5 == 0 else 0)
    r(x, 26 - hgt, 1, hgt, "#142033")

# Small dish / ground station on the left
r(6, 22, 1, 4, "#64748b")
r(5, 21, 3, 1, "#94a3b8")
r(4, 20, 5, 1, "#cbd5e1")
r(6, 19, 1, 1, "#38bdf8", "glow")

# Generic catch tower (left of the rocket): lattice mast + swinging arm
# mast
r(54, 10, 3, 15, "#334155")
r(54, 10, 3, 1, "#94a3b8")
r(54, 10, 1, 15, "#475569")
r(56, 10, 1, 15, "#1e293b")
# cross braces
for yy in range(12, 24, 3):
    r(55, yy, 1, 1, "#64748b")
# arm (animates sideways toward the rocket, generic, no markings)
out.append('<g class="arm">')
r(57, 12, 6, 1, "#94a3b8")
r(57, 13, 6, 1, "#64748b")
r(62, 11, 2, 4, "#cbd5e1")
r(62, 12, 2, 2, "#e2e8f0")
out.append("</g>")
# tower base
r(52, 24, 7, 2, "#475569")
r(53, 23, 5, 1, "#64748b")

# Generic two-stage rocket on the pad (no wordmarks)
# body
r(67, 11, 5, 12, "#e2e8f0")
r(68, 11, 3, 12, "#f8fafc")
r(69, 11, 1, 12, "#cbd5e1")
# nose
r(68, 9, 3, 2, "#f8fafc")
r(69, 8, 1, 1, "#e2e8f0")
# window
r(69, 13, 1, 1, "#38bdf8", "glow")
# interstage band
r(67, 17, 5, 1, "#64748b")
# fins
r(66, 20, 1, 3, "#475569")
r(72, 20, 1, 3, "#475569")
# flame under the vehicle
r(68, 23, 3, 2, "#f97316", "flame")
r(69, 23, 1, 3, "#fde047", "flame2")
r(68, 25, 1, 1, "#fb923c", "flame")
r(70, 25, 1, 1, "#fb923c", "flame2")

# Pad / flame trench
r(64, 24, 11, 2, "#475569")
r(65, 23, 9, 1, "#64748b")
r(66, 26, 7, 1, "#334155")
r(68, 23, 3, 1, "#f59e0b", "glow")

# Tiny operator on the right of the pad
r(78, 21, 2, 2, "#f1c27d")
r(79, 22, 1, 1, "#0f172a")
r(78, 23, 2, 3, "#1e3a5f")
r(78, 26, 1, 1, "#111827")
r(79, 26, 1, 1, "#111827")

# Passing satellite (generic)
out.append('<g class="sat">')
r(8, 9, 3, 1, "#e2e8f0")
r(7, 9, 1, 1, "#94a3b8")
r(11, 9, 1, 1, "#94a3b8")
r(9, 9, 1, 1, "#38bdf8", "glow")
out.append("</g>")

# Metal grid floor
for x in range(W):
    r(x, 27, 1, 1, "#1e3a5f" if x % 4 == 0 else "#0f172a")
    for y in range(28, H):
        if (x + y) % 4 == 0:
            r(x, y, 1, 1, "#1e293b")
        else:
            r(x, y, 1, 1, "#0b1220")

# Status bar
out.append(
    f'<text x="{8}" y="{H*P-8}" font-family="monospace" font-size="12" fill="#fde68a">'
    f"&gt; facts solid, goals dashed, estimates dotted"
    f'<tspan class="blink">_</tspan></text>'
)

svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W*P} {H*P}" '
    f'width="{W*P}" height="{H*P}" shape-rendering="crispEdges">'
    + style
    + "".join(out)
    + "</svg>"
)

dest = Path(__file__).resolve().parent / "assets" / "craft-space.svg"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(svg)
print(f"wrote {dest} ({dest.stat().st_size} bytes)")
