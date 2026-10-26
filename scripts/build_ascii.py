"""Draws the ASCII art on the left of the profile card (scripts/ascii_dark.txt, ascii_light.txt).

    pip install pillow && python3 scripts/build_ascii.py && python3 scripts/update_card.py

Two modes:
  * assets/me.png (transparent background) or assets/me.jpg exists -> ASCII portrait.
    A transparent PNG gives the cleanest outline; with a JPG the backdrop colour is guessed
    from the corners. Tune BOX (crop), GAMMA (shadow lift) and EQUALISE (facial detail).
  * no photo -> a security shield with a keyhole.
"""
import math, os
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 60, 37                   # glyph grid; the card draws 7.2 x 14 px cells
CELL_W, CELL_H = 7.2, 14
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"   # light -> dense

# portrait mode
PHOTOS = [os.path.join(ROOT, 'assets', f) for f in ('me.png', 'me.jpg')]
BOX = (24, 8, 336, 382)         # (left, top, right, bottom) in photo pixels; None = centred crop
FADE = 0.22                     # bottom share of the portrait that fades out, so the collar doesn't turn into a block
PORTRAIT_RAMP = " .,:;i1tfLCG08@"  # fewer, clearly stepped glyphs read better for a flat-lit face
GAMMA = 0.75                    # < 1 lifts the shadows, so dark hair still gets glyphs on the dark card
EQUALISE = 0.3                  # share of rank-equalised tone mixed in, brings out eyes, brows and beard
BG_TOLERANCE = 38               # JPG only: distance from the backdrop colour that still counts as backdrop


def photo():
    return next((p for p in PHOTOS if os.path.exists(p)), None)


def to_ascii(tone, mask=None, ramp=None):
    """tone: W x H floats in 0..1 (1 = brightest). Dark card: bright = dense. Light card: dark = dense.
    The emblem (no mask) keeps its shape in both themes."""
    ramp = ramp or RAMP
    out = {}
    for theme, invert in (('dark', False), ('light', True)):
        rows = []
        for y in range(H):
            row = ''
            for x in range(W):
                t = tone[y][x]
                if mask is not None and not mask[y][x]:
                    row += ' '
                elif mask is None and t < 0.035:
                    row += ' '
                else:
                    v = 1 - t if (invert and mask is not None) else t
                    row += ramp[max(1, round(v * (len(ramp) - 1)))]
            rows.append(row.rstrip())
        out[theme] = '\n'.join(rows)
    return out


def portrait(path):
    img = Image.open(path)
    alpha = img.getchannel('A') if img.mode in ('RGBA', 'LA') else None
    img = img.convert('RGB')
    if BOX:
        img = img.crop(BOX); alpha = alpha.crop(BOX) if alpha else None
    else:
        target = (W * CELL_W) / (H * CELL_H)
        w, h = img.size
        if w / h > target:
            nw = int(h * target); box = ((w - nw) // 2, 0, (w + nw) // 2, h)
        else:
            box = (0, 0, w, int(w / target))                 # keep the top: that's where the face is
        img = img.crop(box); alpha = alpha.crop(box) if alpha else None
    if alpha:
        a = alpha.resize((W, H), Image.BOX)
        mask = [[a.getpixel((x, y)) > 110 for x in range(W)] for y in range(H)]
    else:
        small = img.resize((W, H), Image.BOX)
        corners = [small.getpixel(p) for p in ((0, 0), (W - 1, 0), (0, H // 2), (W - 1, H // 2))]
        bg = tuple(sum(c[i] for c in corners) / 4 for i in range(3))
        mask = []
        for y in range(H):
            row = [math.dist(small.getpixel((x, y)), bg) > BG_TOLERANCE for x in range(W)]
            xs = [x for x, on in enumerate(row) if on]
            mask.append([bool(xs) and xs[0] <= x <= xs[-1] for x in range(W)])
    tones = (img.convert('L').filter(ImageFilter.GaussianBlur(1.2))
             .filter(ImageFilter.UnsharpMask(3, 120, 2)).resize((W, H), Image.BOX))
    cells = sorted(((y, x) for y in range(H) for x in range(W) if mask[y][x]), key=lambda c: tones.getpixel((c[1], c[0])))
    rank = {c: i / max(1, len(cells) - 1) for i, c in enumerate(cells)}
    vals = [tones.getpixel((x, y)) for y, x in cells]
    lo, hi = vals[int(len(vals) * .02)], vals[int(len(vals) * .99)]
    tone = [[0.0] * W for _ in range(H)]
    for (y, x) in cells:
        linear = min(1, max(0, (tones.getpixel((x, y)) - lo) / max(1, hi - lo))) ** GAMMA
        tone[y][x] = (1 - EQUALISE) * linear + EQUALISE * rank[(y, x)]
    start = int(H * (1 - FADE))
    for y in range(start, H):
        keep = 1 - (y - start + 1) / (H - start + 1)
        for x in range(W):
            if mask[y][x]:
                # thin the collar out from the edges inwards, and soften what is left
                edge = min(x, W - 1 - x) / (W / 2)
                if edge < (1 - keep) * 1.1:
                    mask[y][x] = False
                tone[y][x] = 0.15 + (tone[y][x] - 0.15) * keep
    return to_ascii(tone, mask, PORTRAIT_RAMP)


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
    src = photo()
    art = portrait(src) if src else emblem()
    for theme, txt in art.items():
        with open(os.path.join(ROOT, 'scripts', f'ascii_{theme}.txt'), 'w') as f:
            f.write(txt + '\n')
    print('mode:', f'portrait from {os.path.basename(src)}' if src else 'emblem', '-> scripts/ascii_dark.txt, ascii_light.txt')
    print(art['dark'])
