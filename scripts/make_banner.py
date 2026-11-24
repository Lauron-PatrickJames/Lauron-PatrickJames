"""Generate the animated GitHub-profile banner: the portfolio's glowing tile 'wafer' as a self-contained SVG.

GitHub shows README images through a proxy as <img>, so the SVG can't load web fonts or scripts:
animation is pure CSS inside the SVG, and text uses widely installed fonts.
"""
import math
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets/banner.svg"  # run from the repo root: python scripts/make_banner.py
W, H = 1200, 400

# same light model as the site (src/features/mosaic.ts)
LIGHTS = [
    ((255, 70, 140), .35, .15, .00031, .00023, 0.0),
    ((255, 150, 50), .65, .05, .00027, .00019, 1.7),
    ((255, 220, 70), .55, .25, .00022, .00029, 3.1),
    ((50, 230, 140), .85, .45, .00019, .00025, 4.4),
    ((40, 190, 240), .50, .60, .00025, .00017, 2.2),
    ((90, 80, 255), .20, .75, .00021, .00027, 5.3),
]

def colour(x, y, t):
    r = g = b = w = 0.0
    for rgb, lx, ly, sx, sy, ph in LIGHTS:
        cx = lx + math.sin(t * sx + ph) * .22
        cy = ly + math.cos(t * sy + ph) * .18
        k = math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / .03) ** 2 + 1e-4
        r += rgb[0] * k; g += rgb[1] * k; b += rgb[2] * k; w += k
    lum = min(1, .35 + math.sqrt(w) * .9)
    r = r / w * lum + 14 * (1 - lum); g = g / w * lum + 12 * (1 - lum); b = b / w * lum + 30 * (1 - lum)
    return '#%02x%02x%02x' % (int(r), int(g), int(b))

COLS, ROWS = 16, 9
CUT = [7, 5, 4, 3, 2, 1, 1, 0, 0]          # stepped wafer outline, as on the site
TW, TH, GAP = 36, 46, 5                    # tile size
X0 = W - COLS * (TW + GAP) + 10            # bleed slightly off the right edge
Y0 = 34
FRAMES = [0, 5200, 10400, 15600]           # sample times along the drift; the loop returns to frame 0
DUR = 14                                   # seconds per loop

tiles, keyframes = [], []
n = 0
for r in range(ROWS):
    for c in range(COLS):
        if c < CUT[r] or (r == 0 and c == COLS - 1):
            continue
        x, y = c / (COLS - 1), r / (ROWS - 1)
        fade = min(1, .35 + (c - CUT[r]) / 4) * min(1, 1.3 - r / ROWS)
        cols = [colour(x, y, t) for t in FRAMES]
        stops = [0, 25, 50, 75]
        frames = ' '.join(f'{p}%{{fill:{cl}}}' for p, cl in zip(stops, cols)) + f' 100%{{fill:{cols[0]}}}'
        keyframes.append(f'@keyframes k{n}{{{frames}}}')
        px, py = X0 + c * (TW + GAP), Y0 + r * (TH + GAP)
        tiles.append(
            f'<g opacity="{fade:.2f}"><rect class="t" style="animation-name:k{n};fill:{cols[0]}" x="{px}" y="{py}" width="{TW}" height="{TH}" rx="2"/>'
            f'<rect x="{px}" y="{py}" width="{TW}" height="{TH}" rx="2" fill="url(#chip)"/></g>')
        n += 1

SERIF = "Georgia, 'Times New Roman', Times, serif"
MONO = "ui-monospace, 'SFMono-Regular', Menlo, Consolas, 'Liberation Mono', monospace"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">Pat Lauron — 2026 Annual Report</title>
<desc id="d">A dark annual-report cover with a glowing, colour-shifting grid of tiles, the monogram PJL and the words 2026 Annual Report.</desc>
<defs>
  <radialGradient id="bg" cx="70%" cy="40%" r="90%">
    <stop offset="0" stop-color="#17131f"/><stop offset=".6" stop-color="#0b0a10"/>
  </radialGradient>
  <linearGradient id="fadeB" x1="0" y1="0" x2="0" y2="1">
    <stop offset=".55" stop-color="#0b0a10" stop-opacity="0"/><stop offset=".95" stop-color="#0b0a10"/>
  </linearGradient>
  <linearGradient id="fadeL" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#0b0a10"/><stop offset=".42" stop-color="#0b0a10" stop-opacity=".85"/><stop offset=".62" stop-color="#0b0a10" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="sheen" x1="0" x2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".35" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity=".1"/>
  </linearGradient>
  <!-- the dark "chip" lines inside each tile -->
  <pattern id="chip" width="1" height="1" patternContentUnits="objectBoundingBox">
    <rect x=".46" y="0" width=".08" height="1" fill="#06050a" opacity=".75"/>
    <rect x="0" y=".24" width="1" height=".045" fill="#06050a" opacity=".7"/>
    <rect x="0" y=".49" width="1" height=".045" fill="#06050a" opacity=".7"/>
    <rect x="0" y=".74" width="1" height=".045" fill="#06050a" opacity=".7"/>
  </pattern>
  <radialGradient id="gloss" cx="30%" cy="10%" r="80%">
    <stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>
<style>
  .t {{ animation-duration: {DUR}s; animation-timing-function: ease-in-out; animation-iteration-count: infinite; }}
  .sheen {{ animation: glint 7s ease-in-out infinite; }}
  @keyframes glint {{ 0%,100% {{ opacity: .35 }} 50% {{ opacity: 1 }} }}
  {' '.join(keyframes)}
  @media (prefers-reduced-motion: reduce) {{ .t, .sheen {{ animation: none; }} }}
</style>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g>{''.join(tiles)}</g>
  <rect width="{W}" height="{H}" fill="url(#fadeL)"/>
  <rect width="{W}" height="{H}" fill="url(#fadeB)"/>
  <path class="sheen" d="M560 150 C 720 70, 930 44, 1190 58" fill="none" stroke="url(#sheen)" stroke-width="2"/>

  <!-- monogram -->
  <rect x="60" y="56" width="104" height="58" fill="none" stroke="#e9e4f2" stroke-width="1.6"/>
  <text x="112" y="98" text-anchor="middle" font-family="{SERIF}" font-size="38" font-weight="700" fill="#e9e4f2">P<tspan font-style="italic" font-weight="400">J</tspan>L</text>

  <text x="60" y="190" font-family="{SERIF}" font-size="52" fill="#f1ecf7">Pat Lauron</text>
  <text x="62" y="232" font-family="{SERIF}" font-size="25" fill="#e9e4f2">2026 Annual Report</text>
  <text x="62" y="266" font-family="{SERIF}" font-size="18" font-style="italic" fill="#a59fb6">Web development, backend AI &amp; visual media</text>

  <text x="62" y="364" font-family="{MONO}" font-size="12.5" letter-spacing="2.4" fill="#a59fb6">VOL. 01  ·  FISCAL YEAR 2026  ·  BACOOR, CAVITE</text>
  <text x="{W - 40}" y="364" text-anchor="end" font-family="{MONO}" font-size="12.5" letter-spacing="2.4" fill="#e9e4f2">PATJEYMS.DEV  →</text>
</g>
</svg>
'''
open(OUT, 'w', encoding='utf-8').write(svg)
print(f'{n} tiles, {len(svg)/1024:.1f} KB -> {OUT}')
