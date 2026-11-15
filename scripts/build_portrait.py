"""Draws the portrait on the left of the profile card as a dot screen (scripts/portrait_*.svgfrag).

    pip install pillow && python3 scripts/build_portrait.py && python3 scripts/update_card.py

The photo (assets/me.png, transparent background) is sampled on a staggered grid. Every sample
becomes one round dot whose size and colour follow the tone, like a newspaper halftone. Unlike
ASCII art it keeps the eyes, the beard and the hair readable, and it needs no font.

Dark card: bright areas get the big, bright dots. Light card: dark areas get them (ink on paper).
Tune BOX (crop), PITCH (dot spacing: smaller = finer and a heavier file) and ERODE (halo removal).
"""
import math, os
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTO = os.path.join(ROOT, 'assets', 'me.png')
BOX = (24, 8, 336, 382)         # (left, top, right, bottom) in photo pixels
PW, PH = 368, 442               # size on the card, px
PITCH = 4.0                     # distance between dots, px
ERODE = 9                       # px shaved off the cut-out edge, removes the pale halo of the old backdrop
FADE = 0.18                     # bottom share that fades out, so the collar doesn't end in a hard line
LEVELS = 9                      # tone steps; each step is one <path>
COLOURS = {                     # (faintest dot, strongest dot)
    'dark':  ('#1b4a4a', '#7ff2de'),
    'light': ('#b9d8d4', '#0b5c56'),
}


def mix(c1, c2, t):
    a, b = ([int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in (c1, c2))
    return '#%02x%02x%02x' % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def tones():
    img = Image.open(PHOTO).convert('RGBA').crop(BOX)
    mask = img.getchannel('A').resize((PW, PH), Image.LANCZOS).filter(ImageFilter.MinFilter(ERODE))
    mask = mask.point(lambda v: 255 if v > 128 else 0)
    grey = img.convert('RGB').convert('L').resize((PW, PH), Image.LANCZOS)
    inside = [grey.getpixel((x, y)) for y in range(0, PH, 3) for x in range(0, PW, 3) if mask.getpixel((x, y))]
    # outside the mask becomes the average tone, so sharpening can't drag the old backdrop back in
    grey = Image.composite(grey, Image.new('L', grey.size, sum(inside) // len(inside)), mask)
    grey = (grey.filter(ImageFilter.UnsharpMask(14, 70, 0))            # local contrast: eyes, brows, beard
                .filter(ImageFilter.GaussianBlur(PITCH * .2))          # no detail finer than the dots
                .filter(ImageFilter.UnsharpMask(3, 90, 0)))
    inside = sorted(grey.getpixel((x, y)) for y in range(0, PH, 3) for x in range(0, PW, 3) if mask.getpixel((x, y)))
    lo, hi = inside[int(len(inside) * .02)], inside[int(len(inside) * .97)]
    return grey, mask, lo, hi


def fragment(theme, grey, mask, lo, hi):
    faint, strong = COLOURS[theme]
    buckets = {}
    row_h = PITCH * math.sqrt(3) / 2
    row, y = 0, row_h / 2
    while y < PH:
        x = PITCH / 2 + (PITCH / 2 if row % 2 else 0)                  # every other row is shifted half a step
        while x < PW:
            if mask.getpixel((int(x), int(y))):
                t = min(1, max(0, (grey.getpixel((int(x), int(y))) - lo) / (hi - lo)))
                ink = t if theme == 'dark' else 1 - t
                fade = round(min(1, (PH - y) / (PH * FADE)) * 5)
                if fade:
                    buckets.setdefault((round(ink * (LEVELS - 1)), fade), []).append((x, y))
            x += PITCH
        y += row_h
        row += 1
    out = ''
    for (level, fade), pts in sorted(buckets.items()):
        ink = level / (LEVELS - 1)
        size = PITCH * (0.34 + 0.56 * ink) * fade / 5
        # a zero-length line with round caps is a dot, and far shorter to write than a <circle>
        out += (f'<path stroke="{mix(faint, strong, ink ** .9)}" stroke-width="{size:.2f}" d="'
                + ''.join(f'M{x:.1f} {y:.1f}h0' for x, y in pts) + '"/>')
    return out, sum(len(p) for p in buckets.values())


if __name__ == '__main__':
    data = tones()
    for theme in COLOURS:
        frag, n = fragment(theme, *data)
        with open(os.path.join(ROOT, 'scripts', f'portrait_{theme}.svgfrag'), 'w') as f:
            f.write(f'<!-- {PW}x{PH} -->\n{frag}\n')
        print(f'{theme}: {n} dots, {len(frag) // 1024} kB -> scripts/portrait_{theme}.svgfrag')
