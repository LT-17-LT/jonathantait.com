# Regenerate the site favicons from the master artwork.
#
#   python make_favicon.py
#
# The master is a dark serif J on a white field. White is knocked out to
# transparency and the glyph composited on the site cream, so the icon reads as
# a mark rather than as a white chip against dark browser chrome.

import pathlib
from PIL import Image, ImageDraw

SRC = r'G:\CLAUDE EXTRAS\JONATHAN TAIT WEBSITE\Images\Favicons.png'
GROUND = (231, 226, 217)   # site cream #e7e2d9; the glyph is near-black
FILL = 0.86                # fraction of the frame the glyph spans
FLOOR = 8                  # the master's "white" is 253-255, not 255
SIZES = {'apple-touch-icon.png': 180, 'favicon-32.png': 32, 'favicon-192.png': 192}

im = Image.open(SRC).convert('RGB')
w, h = im.size

# Flood the white field inwards from every corner. Whatever it cannot reach is
# glyph - which keeps the bright nebula clouds *inside* the letterform opaque
# instead of punching holes through it.
flood = im.copy()
for xy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
    ImageDraw.floodfill(flood, xy, (255, 0, 255), thresh=30)

src, bg = im.load(), flood.load()
alpha = Image.new('L', (w, h))
a = alpha.load()
for y in range(h):
    for x in range(w):
        if bg[x, y] != (255, 0, 255):
            a[x, y] = 255                       # inside the letterform
            continue
        v = 255 - min(src[x, y])                # soft on antialiased edges
        a[x, y] = v if v > FLOOR else 0

glyph = im.copy()
glyph.putalpha(alpha)
glyph = glyph.crop(glyph.getbbox())
print('glyph', glyph.size)

for name, n in SIZES.items():
    gw, gh = glyph.size
    s = (n * FILL) / max(gw, gh)
    gw, gh = max(1, round(gw * s)), max(1, round(gh * s))
    g = glyph.resize((gw, gh), Image.LANCZOS)
    out = Image.new('RGBA', (n, n), GROUND + (255,))
    out.alpha_composite(g, ((n - gw) // 2, (n - gh) // 2))
    out.convert('RGB').save(name, optimize=True)
    print(f'{name:22} {n}x{n}  {pathlib.Path(name).stat().st_size:>6} bytes')
