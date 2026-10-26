"""Builds the talk cards (assets/talks/<slug>-light.svg, -dark.svg).

Add a talk to TALKS, then:  pip install fonttools brotli && python3 scripts/build_talks.py
The script prints the matching README block.
"""
import html, os
from svgkit import ROOT, Text, width, wrap

TALKS = [
    dict(slug='containerdays-2026', event='ContainerDays', where='Hamburg, 2026',
         title='How Clusters Fail Under Attack and How We Detect It at Runtime with eBPF Signals',
         blurb='Reverse shells and privilege escalation caught live with Tetragon, then blocked.',
         tags=['ebpf', 'tetragon', 'runtime'], status='slides',
         url='https://mella7.me/en/talks/containerdays-2026-ebpf'),
    dict(slug='cloud-identity-summit-2026', event='Cloud Identity Summit', where='Frankfurt, 3 Nov 2026',
         title='Your CI/CD Pipeline Is Over-Privileged: Identity Risks in Modern Cloud Platforms',
         blurb='Pipelines are identities too. What they can really reach, and how to scope them down.',
         tags=['ci-cd', 'iam', 'rbac'], status='upcoming',
         url='https://mella7.me/en/talks/cloud-identity-summit-2026-cicd'),
]
THEMES = {
    'dark':  dict(bg='#161b22', border='#30363d', title='#f0f6fc', text='#c9d1d9', muted='#8b949e', path='#2dd4bf',
                  chip='#a5d6ff', chipbg='#1f3048', slides='#3fb950', upcoming='#e3b341'),
    'light': dict(bg='#f6f8fa', border='#d0d7de', title='#1f2328', text='#24292f', muted='#59636e', path='#0f766e',
                  chip='#0a3069', chipbg='#ddf4ff', slides='#1a7f37', upcoming='#9a6700'),
}
W, H = 440, 196


def card(t, theme):
    c = THEMES[theme]; text = Text(); els = []
    els.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="{c["bg"]}" stroke="{c["border"]}"/>')
    # header: microphone glyph + path-like slug, place and date on the right
    els.append(f'<g transform="translate(18 19)" fill="none" stroke="{c["muted"]}" stroke-width="1.5" stroke-linecap="round">'
               '<rect x="4.5" y="0" width="7" height="11" rx="3.5"/><path d="M1.5 8a6.5 6.5 0 0 0 13 0M8 14.5v3"/></g>')
    path = '~/talks/' + t['slug']
    size = 14
    while width('Mono8', path, size) > W - 60 - width('Inter6', t['where'], 12) - 20:
        size -= .25
    els.append(text(42, 33, path, 'Mono8', size, c['path']))
    els.append(text(W - 18, 33, t['where'], 'Inter6', 12, c['muted'], 'end'))
    # title, then one line of context
    y = 64
    for ln in wrap('Inter6', t['title'], 15.5, W - 36)[:3]:
        els.append(text(18, y, ln, 'Inter6', 15.5, c['title'])); y += 21
    y += 2
    for ln in wrap('Inter4', t['blurb'], 13, W - 36)[:2]:
        els.append(text(18, y, ln, 'Inter4', 13, c['text'])); y += 18
    # footer: event + status dot, tags on the right
    fy = H - 20
    col = c[t['status']]
    els.append(f'<circle cx="24" cy="{fy - 4.5}" r="5" fill="{col}"/>')
    els.append(text(36, fy, t['event'], 'Inter6', 12.5, c['text']))
    sx = 36 + width('Inter6', t['event'], 12.5) + 8
    els.append(text(sx, fy, t['status'], 'Inter4', 12, col))
    tx = W - 18
    left_edge = sx + width('Inter4', t['status'], 12) + 12      # never let tags run into the status
    for tag in reversed(t['tags']):
        tw = width('Mono4', tag, 11) + 16
        if tx - tw < left_edge:
            break
        tx -= tw
        els.append(f'<rect x="{tx:.1f}" y="{fy - 15}" width="{tw:.1f}" height="21" rx="10.5" fill="{c["chipbg"]}"/>')
        els.append(text(tx + tw / 2, fy - .5, tag, 'Mono4', 11, c['chip'], 'middle'))
        tx -= 6
    label = html.escape(f'Talk at {t["event"]}, {t["where"]}: {t["title"]}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">'
            f'<style>{text.font_faces()}</style>' + ''.join(els) + '</svg>')


def readme_block():
    cells = []
    for t in TALKS:
        alt = html.escape(f'{t["event"]}: {t["title"]}')
        cells.append(f'<a href="{t["url"]}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/talks/{t["slug"]}-dark.svg">'
                     f'<img src="assets/talks/{t["slug"]}-light.svg" width="49%" alt="{alt}"></picture></a>')
    return '<p align="center">\n  ' + '\n  '.join(cells) + '\n</p>'


if __name__ == '__main__':
    out = os.path.join(ROOT, 'assets', 'talks'); os.makedirs(out, exist_ok=True)
    for t in TALKS:
        for theme in THEMES:
            with open(os.path.join(out, f'{t["slug"]}-{theme}.svg'), 'w') as f:
                f.write(card(t, theme))
    print(readme_block())
