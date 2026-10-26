"""Builds the stack sphere: assets/stack-sphere-{dark,light}.svg and the interactive docs/index.html.

READMEs can't run JavaScript, so the rotation is precomputed: every icon gets CSS keyframes
for one full turn, and the wireframe meridians morph with SMIL. The docs/ page is the real
3D version (drag, hover, filter), served by GitHub Pages.

Edit STACK, then:  python3 scripts/build_sphere.py
Icons live in scripts/icons/ (see SOURCES.md there).
"""
import base64, json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS = os.path.join(ROOT, 'scripts', 'icons')

# group -> icons. Neighbours in this list end up near each other on the sphere.
STACK = {
    'Platform': ['Kubernetes', 'OpenShift', 'Helm', 'ArgoCD', 'Docker', 'Cilium', 'Nginx'],
    'Security': ['Falco', 'Kali', 'RedHat', 'Linux', 'Bash'],
    'Infra & CI': ['Terraform', 'GithubActions', 'GitLab', 'Git', 'Github', 'Azure', 'AWS', 'Netlify'],
    'Observability': ['Prometheus', 'Grafana'],
    'Code': ['GoLang', 'Python', 'TypeScript', 'JavaScript', 'FastAPI', 'NodeJS', 'React', 'NextJS', 'TailwindCSS'],
}
LABELS = {'ArgoCD': 'Argo CD', 'GithubActions': 'GitHub Actions', 'Github': 'GitHub', 'GoLang': 'Go', 'NodeJS': 'Node.js',
          'NextJS': 'Next.js', 'TailwindCSS': 'Tailwind CSS', 'RedHat': 'Red Hat (RHCSA)', 'Kali': 'Kali Linux (eJPT)',
          'Kubernetes': 'Kubernetes (CKA, CKAD)', 'Azure': 'Microsoft Azure'}

W, H = 880, 540
CX, CY, R = W / 2, H / 2, 222
ICON, FRAMES, TURN = 48, 72, 32          # icon px at the front, keyframes per turn, seconds per turn
TILT = math.radians(-16)
THEMES = {
    'dark':  dict(wire='#30363d', rim='#3d444d', glow='#2dd4bf', orbit='#2dd4bf'),
    'light': dict(wire='#d0d7de', rim='#c4ccd5', glow='#0f766e', orbit='#0f766e'),
}


def names():
    return [n for group in STACK.values() for n in group]


def icon_uri(name, theme):
    for fname in (f'{name}-{theme.capitalize()}.svg', f'{name}.svg'):
        p = os.path.join(ICONS, fname)
        if os.path.exists(p):
            return 'data:image/svg+xml;base64,' + base64.b64encode(open(p, 'rb').read()).decode()
    raise SystemExit(f'no icon for {name} in scripts/icons/')


def fibonacci(n):
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        y = 1 - 2 * (i + .5) / n
        r = math.sqrt(1 - y * y)
        yield math.cos(golden * i) * r, y, math.sin(golden * i) * r


def project(p, spin):
    x, y, z = p
    x, z = x * math.cos(spin) + z * math.sin(spin), -x * math.sin(spin) + z * math.cos(spin)
    y, z = y * math.cos(TILT) - z * math.sin(TILT), y * math.sin(TILT) + z * math.cos(TILT)
    k = 1 + .18 * z
    return CX + R * x * k, CY + R * y * k, z


def sphere_svg(theme):
    c = THEMES[theme]
    css, defs, back, front = [], [], [], []
    for i, (name, p) in enumerate(zip(names(), fibonacci(len(names())))):
        kb, kf = [], []
        for k in range(FRAMES + 1):
            x, y, z = project(p, 2 * math.pi * k / FRAMES)
            depth = (z + 1) / 2
            s, o = .55 + .45 * depth, .15 + .85 * depth ** 1.4
            at, tf = f'{100 * k / FRAMES:.2f}%', f'transform:translate({x:.1f}px,{y:.1f}px) scale({s:.3f})'
            kb.append(f'{at}{{{tf};opacity:{o if z < 0 else 0:.2f}}}')
            kf.append(f'{at}{{{tf};opacity:{o if z >= 0 else 0:.2f}}}')
        css.append(f'@keyframes b{i}{{{"".join(kb)}}}@keyframes f{i}{{{"".join(kf)}}}'
                   f'.b{i}{{animation:b{i} {TURN}s linear infinite}}.f{i}{{animation:f{i} {TURN}s linear infinite}}')
        defs.append(f'<image id="i{i}" href="{icon_uri(name, theme)}" x="{-ICON / 2}" y="{-ICON / 2}" width="{ICON}" height="{ICON}"/>')
        back.append(f'<g class="b{i}"><use href="#i{i}"/></g>')
        front.append(f'<g class="f{i}"><use href="#i{i}"/></g>')

    wire = [f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#halo)" stroke="{c["rim"]}" stroke-width="1.2"/>']
    for lat in (-60, -30, 0, 30, 60):                       # latitude rings don't change while spinning
        a = math.radians(lat)
        pts = [project((math.cos(t) * math.cos(a), math.sin(a), math.sin(t) * math.cos(a)), 0)
               for t in (2 * math.pi * j / 72 for j in range(73))]
        wire.append(f'<path d="M{" L".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts)}" fill="none" stroke="{c["wire"]}" opacity=".8"/>')
    for m in range(6):                                      # meridians morph frame by frame
        phi = math.pi * m / 6
        frames = []
        for k in range(FRAMES // 2 + 1):
            pts = [project((math.cos(phi) * math.cos(t), math.sin(t), math.sin(phi) * math.cos(t)), 2 * math.pi * k / FRAMES)
                   for t in (math.pi * (j / 36 - .5) for j in range(37))]
            frames.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y, _ in pts))
        wire.append(f'<path fill="none" stroke="{c["wire"]}" opacity=".8" d="{frames[0]}">'
                    f'<animate attributeName="d" dur="{TURN / 2}s" repeatCount="indefinite" values="{";".join(frames)}"/></path>')

    # an orbit around the sphere with a signal travelling along it
    orbit = (f'<ellipse id="orb" cx="{CX}" cy="{CY}" rx="{R + 34}" ry="{(R + 34) * .26:.1f}" fill="none" stroke="{c["orbit"]}" '
             f'stroke-opacity=".35" stroke-dasharray="2 7" transform="rotate(-14 {CX} {CY})"/>'
             f'<circle r="4" fill="{c["orbit"]}"><animateMotion dur="9s" repeatCount="indefinite" rotate="auto">'
             f'<mpath href="#orbpath"/></animateMotion></circle>'
             f'<path id="orbpath" fill="none" d="M{CX + R + 34} {CY} a{R + 34} {(R + 34) * .26:.1f} 0 1 1 {-2 * (R + 34)} 0 '
             f'a{R + 34} {(R + 34) * .26:.1f} 0 1 1 {2 * (R + 34)} 0" transform="rotate(-14 {CX} {CY})"/>')
    label = ', '.join(LABELS.get(n, n) for n in names())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Rotating sphere of the tools I use: {label}">'
            f'<defs><radialGradient id="halo" cx="50%" cy="45%" r="55%"><stop offset="0" stop-color="{c["glow"]}" stop-opacity=".12"/>'
            f'<stop offset="1" stop-color="{c["glow"]}" stop-opacity="0"/></radialGradient>{"".join(defs)}</defs>'
            f'<style>{"".join(css)}g[class]{{opacity:0}}@media (prefers-reduced-motion:reduce){{g[class]{{animation-play-state:paused}}}}</style>'
            + ''.join(wire) + ''.join(back) + orbit + ''.join(front) + '</svg>')


PAGE = r'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>mella7 · stack</title>
<meta name="description" content="The tools Mohamed Ali Mellah works with, on a sphere you can spin.">
<style>
:root{--bg:#f6f8fa;--fg:#1f2328;--muted:#59636e;--line:#c4ccd5;--accent:#0f766e;--accent-rgb:15,118,110;--chip:#eaeef2}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#f0f6fc;--muted:#8b949e;--line:#30363d;--accent:#2dd4bf;--accent-rgb:45,212,191;--chip:#161b22}}
*{box-sizing:border-box}html,body{margin:0;height:100%}
body{background:var(--bg);color:var(--fg);font:15px/1.5 Inter,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif;
display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;padding:16px;overflow:hidden;user-select:none}
h1{margin:0;font:700 18px ui-monospace,"JetBrains Mono",Menlo,Consolas,monospace}h1 span{color:var(--accent)}
.hint{margin:0;color:var(--muted);font-size:13px;text-align:center}
#groups{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;max-width:620px}
#groups button{font:600 12px ui-monospace,Menlo,monospace;color:var(--fg);background:var(--chip);border:1px solid var(--line);
border-radius:999px;padding:5px 11px;cursor:pointer}
#groups button[aria-pressed=true]{border-color:var(--accent);color:var(--accent);box-shadow:0 0 0 3px rgba(var(--accent-rgb),.15)}
#stage{position:relative;width:min(92vw,600px);aspect-ratio:1;touch-action:none;cursor:grab}#stage.drag{cursor:grabbing}
canvas{position:absolute;inset:0;width:100%;height:100%}
.ico{position:absolute;left:0;top:0;width:52px;height:52px;margin:-26px 0 0 -26px;transition:filter .3s}
.ico img{width:100%;height:100%;display:block;pointer-events:none;border-radius:13px;transition:transform .25s cubic-bezier(.2,.9,.3,1.3)}
.ico:hover img{transform:scale(1.8)}
.ico.dim{filter:grayscale(1) opacity(.25)}
.tip{position:absolute;left:50%;bottom:100%;transform:translate(-50%,-14px);white-space:nowrap;pointer-events:none;opacity:0;
background:var(--fg);color:var(--bg);font:600 12px ui-monospace,Menlo,monospace;padding:4px 8px;border-radius:6px;transition:.2s}
.ico:hover .tip{opacity:1;transform:translate(-50%,-34px)}
a{color:var(--muted);font-size:13px;text-decoration:none}a:hover{color:var(--accent)}
</style></head><body>
<h1><span>mella7</span>@cluster:~/stack</h1>
<p class="hint">Drag to spin. Hover a logo for its name. Pick a group to highlight it.</p>
<div id="groups"></div>
<div id="stage"><canvas id="wire"></canvas></div>
<a href="https://github.com/mella7">github.com/mella7</a>
<script>
const DATA = __DATA__;
(() => {
  const stage = document.getElementById('stage'), cv = document.getElementById('wire'), ctx = cv.getContext('2d');
  const dark = matchMedia('(prefers-color-scheme: dark)');
  const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const N = DATA.icons.length, golden = Math.PI * (3 - Math.sqrt(5));
  let hovering = 0;
  const nodes = DATA.icons.map((ic, i) => {
    const y = 1 - 2 * (i + .5) / N, r = Math.sqrt(1 - y * y);
    const el = document.createElement('div'); el.className = 'ico';
    const img = document.createElement('img'); img.alt = ic.label;
    const tip = document.createElement('span'); tip.className = 'tip'; tip.textContent = ic.label;
    el.append(img, tip); stage.append(el);
    el.addEventListener('pointerenter', () => hovering++); el.addEventListener('pointerleave', () => hovering--);
    return {x: Math.cos(golden * i) * r, y, z: Math.sin(golden * i) * r, el, img, ic};
  });
  const paint = () => nodes.forEach(n => n.img.src = dark.matches ? n.ic.dark : n.ic.light);
  paint(); dark.addEventListener('change', paint);
  // group filter
  const bar = document.getElementById('groups'); let active = null;
  ['All', ...DATA.groups].forEach(g => {
    const b = document.createElement('button'); b.textContent = g; b.setAttribute('aria-pressed', g === 'All');
    b.onclick = () => { active = g === 'All' ? null : g;
      bar.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b));
      nodes.forEach(n => n.el.classList.toggle('dim', !!active && n.ic.group !== active)); };
    bar.append(b);
  });
  // wireframe
  const lines = [];
  for (const lat of [-60, -30, 0, 30, 60]) { const a = lat * Math.PI / 180, l = [];
    for (let j = 0; j <= 72; j++) { const t = j / 72 * 2 * Math.PI; l.push({x: Math.cos(t) * Math.cos(a), y: Math.sin(a), z: Math.sin(t) * Math.cos(a)}); } lines.push(l); }
  for (let m = 0; m < 6; m++) { const p = m * Math.PI / 6, l = [];
    for (let j = 0; j <= 72; j++) { const t = j / 72 * 2 * Math.PI; l.push({x: Math.cos(p) * Math.cos(t), y: Math.sin(t), z: Math.sin(p) * Math.cos(t)}); } lines.push(l); }
  // motion
  const AUTO = matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : .003;
  let yaw = 0, pitch = -.28, vy = AUTO, vp = 0, drag = false, lx = 0, ly = 0;
  stage.addEventListener('pointerdown', e => { drag = true; lx = e.clientX; ly = e.clientY; stage.setPointerCapture(e.pointerId); stage.classList.add('drag'); });
  stage.addEventListener('pointermove', e => { if (!drag) return; vy = (e.clientX - lx) * .006; vp = (e.clientY - ly) * .006;
    lx = e.clientX; ly = e.clientY; yaw += vy; pitch = Math.max(-1.3, Math.min(1.3, pitch + vp)); });
  const stop = () => { drag = false; stage.classList.remove('drag'); };
  stage.addEventListener('pointerup', stop); stage.addEventListener('pointercancel', stop);
  let S = 0, R = 0, dpr = 1;
  const resize = () => { S = stage.getBoundingClientRect().width; R = S * .39; dpr = devicePixelRatio || 1; cv.width = cv.height = S * dpr; };
  new ResizeObserver(resize).observe(stage); resize();
  const rot = (p, cy, sy, cp, sp) => { const x = p.x * cy + p.z * sy, z = -p.x * sy + p.z * cy; return [x, p.y * cp - z * sp, p.y * sp + z * cp]; };
  (function frame() {
    if (!drag) { vy += ((hovering ? 0 : AUTO) - vy) * .04; vp *= .92; yaw += vy; pitch += vp + (-.28 - pitch) * .01; }
    const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch), c = S / 2;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, S, S);
    const g = ctx.createRadialGradient(c, c * .9, 0, c, c, R * 1.15);
    g.addColorStop(0, `rgba(${css('--accent-rgb')},.12)`); g.addColorStop(1, `rgba(${css('--accent-rgb')},0)`);
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(c, c, R * 1.15, 0, 7); ctx.fill();
    ctx.strokeStyle = css('--line'); ctx.lineWidth = 1;
    for (const l of lines) for (let j = 1; j < l.length; j++) {
      const [x0, y0, z0] = rot(l[j - 1], cy, sy, cp, sp), [x1, y1, z1] = rot(l[j], cy, sy, cp, sp);
      ctx.globalAlpha = .15 + .55 * ((z0 + z1) / 2 + 1) / 2; ctx.beginPath();
      ctx.moveTo(c + R * x0 * (1 + .18 * z0), c + R * y0 * (1 + .18 * z0)); ctx.lineTo(c + R * x1 * (1 + .18 * z1), c + R * y1 * (1 + .18 * z1)); ctx.stroke();
    }
    ctx.globalAlpha = 1;
    for (const n of nodes) {
      const [x, y, z] = rot(n, cy, sy, cp, sp), k = 1 + .18 * z, d = (z + 1) / 2;
      n.el.style.transform = `translate(${c + R * x * k}px,${c + R * y * k}px) scale(${((.5 + .5 * d) * S / 600).toFixed(3)})`;
      n.el.style.opacity = (.15 + .85 * d ** 1.3).toFixed(3); n.el.style.zIndex = Math.round(d * 1000);
      n.el.style.pointerEvents = z > -.2 ? 'auto' : 'none';
    }
    requestAnimationFrame(frame);
  })();
})();
</script></body></html>'''


def page():
    groups = {n: g for g, ns in STACK.items() for n in ns}
    data = dict(groups=list(STACK), icons=[dict(label=LABELS.get(n, n), group=groups[n], light=icon_uri(n, 'light'),
                                                dark=icon_uri(n, 'dark')) for n in names()])
    return PAGE.replace('__DATA__', json.dumps(data))


if __name__ == '__main__':
    os.makedirs(os.path.join(ROOT, 'assets'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
    for theme in THEMES:
        svg = sphere_svg(theme)
        with open(os.path.join(ROOT, 'assets', f'stack-sphere-{theme}.svg'), 'w') as f:
            f.write(svg)
        print(f'stack-sphere-{theme}.svg', len(svg) // 1024, 'KB')
    with open(os.path.join(ROOT, 'docs', 'index.html'), 'w') as f:
        f.write(page())
    print('docs/index.html')
