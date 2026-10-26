"""Builds a looping slide preview of a talk: assets/talks/<deck>-slides.svg

Drop JPGs named <deck>-01.jpg, <deck>-02.jpg ... into assets/talks/slides/, then:
    python3 scripts/build_slides.py
Slides crossfade with CSS animations, so the preview plays on github.com. If animations
are off (prefers-reduced-motion, or a viewer without CSS), the first slide is shown.
"""
import base64, glob, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLIDES = os.path.join(ROOT, 'assets', 'talks', 'slides')
SHOW, FADE = 3.6, 0.7           # seconds each slide stays, seconds of crossfade
W, H, DOTS = 880, 495, 30       # slide area and room for the progress dots below it
LABEL = {'containerdays-2026': 'ContainerDays Hamburg 2026: How Clusters Fail Under Attack and How We Detect It at Runtime with eBPF Signals'}


def deck_svg(deck, files):
    n = len(files)
    total = n * SHOW
    pct = lambda t: f'{100 * t / total:.3f}%'
    # one shared timeline: visible at the start of the cycle, fades out, fades back in at the very end
    css = (f'@keyframes on{{0%{{opacity:1}}{pct(SHOW)}{{opacity:1}}{pct(SHOW + FADE)}{{opacity:0}}'
           f'{pct(total - FADE)}{{opacity:0}}100%{{opacity:1}}}}'
           f'.s{{animation:on {total:.2f}s linear infinite}}'
           '@media (prefers-reduced-motion:reduce){.s{animation:none}}')
    slides, dots = [], []
    for i, f in enumerate(files):
        uri = 'data:image/jpeg;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
        delay = -((total - i * SHOW + FADE) % total)    # start inside slide 1, not in a crossfade
        hidden = '' if i == 0 else 'opacity:0;'
        slides.append(f'<image class="s" style="{hidden}animation-delay:{delay:.2f}s" href="{uri}" width="{W}" height="{H}" '
                      f'preserveAspectRatio="xMidYMid slice"/>')
        cx = W / 2 + (i - (n - 1) / 2) * 18
        dots.append(f'<circle cx="{cx:.1f}" cy="{H + DOTS / 2 + 2}" r="4" fill="#8b949e" opacity=".35"/>'
                    f'<circle class="s" style="{hidden}animation-delay:{delay:.2f}s" cx="{cx:.1f}" cy="{H + DOTS / 2 + 2}" r="4" fill="#2dd4bf"/>')
    label = LABEL.get(deck, deck) + f'. A {n}-slide preview.'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H + DOTS}" viewBox="0 0 {W} {H + DOTS}" role="img" '
            f'aria-label="{label}"><style>{css}</style>'
            f'<defs><clipPath id="r"><rect width="{W}" height="{H}" rx="12"/></clipPath></defs>'
            f'<g clip-path="url(#r)"><rect width="{W}" height="{H}" fill="#161b22"/>{"".join(slides)}</g>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="#8b949e" stroke-opacity=".35"/>'
            + ''.join(dots) + '</svg>')


if __name__ == '__main__':
    decks = {}
    for f in sorted(glob.glob(os.path.join(SLIDES, '*.jpg'))):
        m = re.match(r'(.+)-\d+\.jpg$', os.path.basename(f))
        if m:
            decks.setdefault(m.group(1), []).append(f)
    for deck, files in decks.items():
        out = os.path.join(ROOT, 'assets', 'talks', f'{deck}-slides.svg')
        with open(out, 'w') as fh:
            fh.write(deck_svg(deck, files))
        print(f'{os.path.relpath(out, ROOT)}: {len(files)} slides, {os.path.getsize(out) // 1024} KB')
