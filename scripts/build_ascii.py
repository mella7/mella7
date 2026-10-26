"""Draws the ASCII art on the left of the profile card (scripts/ascii_dark.txt, ascii_light.txt).

    pip install pillow && python3 scripts/build_ascii.py && python3 scripts/update_card.py

Two modes:
  * assets/me.jpg exists  -> ASCII portrait of the photo. Tune BOX (crop, in photo pixels) and GAMMA.
  * no photo              -> a security shield with a keyhole.
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 60, 37                   # glyph grid; the card draws 7.2 x 14 px cells
CELL_W, CELL_H = 7.2, 14
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"   # light -> dense

# portrait mode
PHOTO = os.path.join(ROOT, 'assets', 'me.jpg')
BOX = None                      # (left, top, right, bottom); None = centred crop at the grid's aspect ratio
GAMMA = 0.7
BG_TOLERANCE = 38               # how far a pixel must be from the backdrop colour to count as "you"


def to_ascii(tone, mask=None):
    """tone: W x H floats in 0..1 (1 = densest glyph). Returns dark and light variants."""
    out = {}
    for theme, invert in (('dark', False), ('light', True)):
        rows = []
        for y in range(H):
            row = ''
            for x in range(W):
                t = tone[y][x]
                if (mask and not mask[y][x]) or t < 0.035:
                    row += ' '
                else:
                    v = 1 - t if invert and mask else t      # emblem keeps its shape in both themes
                    row += RAMP[max(1, round(v * (len(RAMP) - 1)))]
            rows.append(row.rstrip())
        out[theme] = '\n'.join(rows)
    return out


def portrait():
    img = Image.open(PHOTO).convert('RGB')
    if BOX:
        img = img.crop(BOX)
    else:
        target = (W * CELL_W) / (H * CELL_H)
        w, h = img.size
        if w / h > target:
            nw = int(h * target); img = img.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
        else:
            nh = int(w / target); img = img.crop((0, 0, w, nh))     # keep the top: that's where the face is
    small = img.resize((W, H), Image.BOX)
    corners = [small.getpixel(p) for p in ((0, 0), (W - 1, 0), (0, H // 2), (W - 1, H // 2))]
    bg = tuple(sum(c[i] for c in corners) / 4 for i in range(3))
    mask = []
    for y in range(H):
        row = [math.dist(small.getpixel((x, y)), bg) > BG_TOLERANCE for x in range(W)]
        xs = [x for x, on in enumerate(row) if on]
        mask.append([bool(xs) and xs[0] <= x <= xs[-1] for x in range(W)])
    tones = img.convert('L').filter(ImageFilter.UnsharpMask(6, 140, 1)).resize((W, H), Image.BOX)
    vals = sorted(tones.getpixel((x, y)) for y in range(H) for x in range(W) if mask[y][x])
    lo, hi = vals[int(len(vals) * .02)], vals[int(len(vals) * .99)]
    tone = [[min(1, max(0, (tones.getpixel((x, y)) - lo) / max(1, hi - lo))) ** GAMMA for x in range(W)] for y in range(H)]
    return to_ascii(tone, mask)


def emblem():
    S = 4                                                   # supersampling
    pw, ph = int(W * CELL_W * S), int(H * CELL_H * S)
    img = Image.new('L', (pw, ph), 0)
    d = ImageDraw.Draw(img)
    cx = pw / 2

    def shield(scale, top):
        hw = 150 * S * scale
        y0 = top
        pts = []
        for i in range(21):                                  # gently arched top edge
            t = i / 20
            x = cx - hw + 2 * hw * t
            pts.append((x, y0 + 14 * S * scale * (1 - math.sin(math.pi * t))))
        side = y0 + 200 * S * scale
        tip = y0 + 400 * S * scale
        for i in range(1, 25):                               # curved flanks down to the point
            t = i / 24
            pts.append((cx + hw * (1 - t ** 1.7), side + (tip - side) * t))
        for i in range(24, 0, -1):
            t = i / 24
            pts.append((cx - hw * (1 - t ** 1.7), side + (tip - side) * t))
        pts.append((cx - hw, y0 + 14 * S * scale))
        return pts

    top = 58 * S
    d.polygon(shield(1.0, top), fill=255)                    # outer shield
    d.line(shield(0.86, top + 26 * S) + [shield(0.86, top + 26 * S)[0]], fill=60, width=int(7 * S))   # inner rim

    # keyhole cut-out
    ky = top + 160 * S
    r = 38 * S
    d.ellipse([cx - r, ky - r, cx + r, ky + r], fill=0)
    d.polygon([(cx - 17 * S, ky + 18 * S), (cx + 17 * S, ky + 18 * S), (cx + 30 * S, ky + 130 * S), (cx - 30 * S, ky + 130 * S)], fill=0)

    # shading: light from the upper left, so the shield reads as raised
    shade = Image.new('L', img.size)
    sp = shade.load()
    for y in range(0, ph, S):
        for x in range(0, pw, S):
            v = 1 - 0.45 * ((x / pw) * 0.6 + (y / ph) * 0.8)
            for dy in range(S):
                for dx in range(S):
                    sp[x + dx, y + dy] = int(255 * max(0.25, min(1, v)))
    from PIL import ImageChops
    img = ImageChops.multiply(img, shade).filter(ImageFilter.GaussianBlur(1.2 * S))

    small = img.resize((W, H), Image.BOX)
    tone = [[small.getpixel((x, y)) / 255 for x in range(W)] for y in range(H)]
    return to_ascii(tone)


if __name__ == '__main__':
    art = portrait() if os.path.exists(PHOTO) else emblem()
    for theme, txt in art.items():
        with open(os.path.join(ROOT, 'scripts', f'ascii_{theme}.txt'), 'w') as f:
            f.write(txt + '\n')
    print('mode:', 'portrait' if os.path.exists(PHOTO) else 'emblem', '-> scripts/ascii_dark.txt, ascii_light.txt')
    print(art['dark'])
