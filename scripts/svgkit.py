"""Shared helpers for the SVG builders: font metrics, text wrapping, and font embedding.

Fonts are subset to the characters each SVG actually uses, so a card stays a few KB
while still rendering in JetBrains Mono and Inter on every machine.
"""
import base64, html, io, os
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, 'scripts', 'fonts')
FONTS = {
    'Mono4': 'jetbrains-mono-latin-400-normal.woff2',
    'Mono8': 'jetbrains-mono-latin-800-normal.woff2',
    'Inter4': 'inter-latin-400-normal.woff2',
    'Inter6': 'inter-latin-600-normal.woff2',
}
_tt = {}


def tt(name):
    if name not in _tt:
        _tt[name] = TTFont(os.path.join(FONT_DIR, FONTS[name]))
    return _tt[name]


def width(font, s, size):
    f = tt(font); cmap = f.getBestCmap(); hmtx = f['hmtx']; upm = f['head'].unitsPerEm
    return sum(hmtx[cmap[ord(ch)]][0] if ord(ch) in cmap else upm * .55 for ch in s) * size / upm


def wrap(font, s, size, max_w):
    lines, cur = [], ''
    for word in s.split():
        trial = f'{cur} {word}'.strip()
        if not cur or width(font, trial, size) <= max_w:
            cur = trial
        else:
            lines.append(cur); cur = word
    return lines + ([cur] if cur else [])


class Text:
    """Collects <text> elements and remembers which glyphs each font needs."""

    def __init__(self):
        self.used = {}

    def __call__(self, x, y, s, font, size, fill, anchor='start', extra=''):
        self.used.setdefault(font, set()).update(s)
        return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" fill="{fill}" '
                f'text-anchor="{anchor}"{extra}>{html.escape(s, quote=False)}</text>')

    def font_faces(self):
        faces = []
        for name, chars in self.used.items():
            o = subset.Options(); o.flavor = 'woff2'; o.layout_features = ['kern']
            f = TTFont(os.path.join(FONT_DIR, FONTS[name]))
            sb = subset.Subsetter(o); sb.populate(text=''.join(chars) + ' '); sb.subset(f)
            buf = io.BytesIO(); f.flavor = 'woff2'; f.save(buf)
            faces.append(f"@font-face{{font-family:'{name}';src:url(data:font/woff2;base64,"
                         f"{base64.b64encode(buf.getvalue()).decode()}) format('woff2')}}")
        return ''.join(faces) + 'text{font-variant-ligatures:none}'
