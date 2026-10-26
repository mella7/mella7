"""Builds the link buttons under the card (assets/buttons/*-light.svg, *-dark.svg).

Edit LINKS, then:  pip install fonttools brotli && python3 scripts/build_buttons.py
The script prints the matching README block.
"""
import html, os, re
from svgkit import ROOT, Text, width

# label, handle shown, url, tile colour ('mono' follows the theme), icon
LINKS = [
    ('LinkedIn', 'MellahMedAli', 'https://www.linkedin.com/in/MellahMedAli', '#0A66C2', 'si:linkedin'),
    ('Medium', '@mellahmohamedali', 'https://medium.com/@mellahmohamedali', 'mono', 'si:medium'),
    ('Website', 'mella7.me', 'https://mella7.me', 'accent', 'globe'),
    ('Email', 'say hello', 'mailto:mellah.mohamedali@outlook.com', 'accent', 'mail'),
]
THEMES = {
    'dark':  dict(bg='#161b22', border='#30363d', title='#f0f6fc', muted='#8b949e', mono_bg='#f0f6fc', mono_fg='#0d1117',
                  accent='#2dd4bf', accent_fg='#0d1117', arrow='#2dd4bf'),
    'light': dict(bg='#f6f8fa', border='#d0d7de', title='#1f2328', muted='#59636e', mono_bg='#1f2328', mono_fg='#ffffff',
                  accent='#0f766e', accent_fg='#ffffff', arrow='#0f766e'),
}
W, H = 224, 58

# simple line icons on a 24x24 grid, drawn with a stroke
STROKE_ICONS = {
    'globe': 'M12 2.5a9.5 9.5 0 1 0 0 19a9.5 9.5 0 1 0 0-19M2.5 12h19M12 2.5c2.6 2.7 3.9 5.9 3.9 9.5s-1.3 6.8-3.9 9.5'
             'M12 2.5c-2.6 2.7-3.9 5.9-3.9 9.5s1.3 6.8 3.9 9.5',
    'mail': 'M3.5 5.5h17a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1h-17a1 1 0 0 1-1-1v-11a1 1 0 0 1 1-1zM3 6.5l9 7l9-7',
}


def icon(spec, fg):
    if spec.startswith('si:'):
        svg = open(os.path.join(ROOT, 'scripts', 'icons', f'si-{spec[3:]}.svg')).read()
        d = re.search(r'<path d="([^"]+)"', svg).group(1)
        return f'<g transform="translate(19 19) scale(.8333)"><path fill="{fg}" d="{d}"/></g>'
    return (f'<g transform="translate(17 17)"><path fill="none" stroke="{fg}" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" d="{STROKE_ICONS[spec]}"/></g>')


def button(name, handle, color, spec, theme):
    c = THEMES[theme]; text = Text()
    if color == 'mono':
        bg, fg = c['mono_bg'], c['mono_fg']
    elif color == 'accent':
        bg, fg = c['accent'], c['accent_fg']
    else:
        bg, fg = color, '#ffffff'
    size = 11.5
    while width('Mono4', handle, size) > W - 58 - 30:
        size -= .25
    body = (f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{c["bg"]}" stroke="{c["border"]}"/>'
            f'<rect x="12" y="12" width="34" height="34" rx="9" fill="{bg}"/>' + icon(spec, fg)
            + text(58, 27, name, 'Inter6', 15, c['title'])
            + text(58, 44, handle, 'Mono4', size, c['muted'])
            + f'<path d="M{W - 24} {H / 2 - 5} l5 5 -5 5" fill="none" stroke="{c["arrow"]}" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{name}: {html.escape(handle)}"><style>{text.font_faces()}</style>{body}</svg>')


def readme_block():
    cells = []
    for name, handle, url, *_ in LINKS:
        s = name.lower()
        cells.append(f'<a href="{url}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/buttons/{s}-dark.svg">'
                     f'<img src="assets/buttons/{s}-light.svg" width="23.5%" alt="{name}: {html.escape(handle)}"></picture></a>')
    return '<p align="center">\n  ' + '\n  '.join(cells) + '\n</p>'


if __name__ == '__main__':
    out = os.path.join(ROOT, 'assets', 'buttons'); os.makedirs(out, exist_ok=True)
    for name, handle, url, color, spec in LINKS:
        for theme in THEMES:
            with open(os.path.join(out, f'{name.lower()}-{theme}.svg'), 'w') as f:
                f.write(button(name, handle, color, spec, theme))
    print(readme_block())
