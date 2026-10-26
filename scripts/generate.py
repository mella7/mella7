#!/usr/bin/env python3
"""
Generates the animated SVGs for the mella7 profile README.

    python3 scripts/generate.py

Writes light and dark versions of:
    assets/header-{light,dark}.svg   terminal running `kubectl describe engineer mella7`
    assets/stack-{light,dark}.svg    tech stack drawn as a cluster: control plane + node pools

Edit the CONTENT section below, re-run, commit. No dependencies.
"""

from html import escape
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# ---------------------------------------------------------------- CONTENT

PROMPT_USER = "mella7@cluster"
COMMAND = "kubectl describe engineer mella7"

# (key, value, style) - style picks the value color
DESCRIBE = [
    ("Name:", "Mohamed Ali Mellah", "strong"),
    ("Role:", "Cloud Security Engineer", "text"),
    ("Focus:", "K8s security, eBPF runtime detection", "text"),
    ("Also:", "platform engineering, CI/CD identity risk", "text"),
    ("Certs:", "CKA  CKAD  RHCSA  eJPT  (CKS: pending)", "accent"),
    ("Studying:", "MSc Informatik @ Uni Passau", "text"),
]
STATUS = "Running"

# runtime events shown in the side panel: (event, verdict, ok?)
EVENTS = [
    ("process_exec", "allowed", True),
    ("tcp_connect", "allowed", True),
    ("sys_setuid", "blocked", False),
    ("file_open", "allowed", True),
]

# node pools for the stack diagram: (pool name, [items])
POOLS = [
    ("orchestration", ["Kubernetes", "OpenShift", "Helm", "Operators"]),
    ("runtime-security", ["eBPF", "Tetragon", "Falco", "RBAC audit"]),
    ("infra-as-code", ["Terraform", "CloudStack", "GitOps"]),
    ("languages", ["Go", "Python", "TypeScript", "Bash"]),
    ("apps", ["FastAPI", "React", "Next.js", "MCP"]),
    ("linux", ["RHEL", "Fedora", "systemd", "networking"]),
]

# ---------------------------------------------------------------- THEMES

THEMES = {
    "dark": dict(
        bg="#0d1117", panel="#161b22", panel2="#0d1117", border="#30363d",
        text="#c9d1d9", strong="#f0f6fc", muted="#8b949e",
        accent="#2dd4bf", green="#3fb950", red="#f85149", amber="#d29922",
        pill="#1f2a37", pill_text="#c9d1d9", edge="#2dd4bf",
        dot1="#f85149", dot2="#d29922", dot3="#3fb950",
    ),
    "light": dict(
        bg="#ffffff", panel="#f6f8fa", panel2="#ffffff", border="#d0d7de",
        text="#24292f", strong="#0d1117", muted="#57606a",
        accent="#0f766e", green="#1a7f37", red="#cf222e", amber="#9a6700",
        pill="#eaeef2", pill_text="#24292f", edge="#0f766e",
        dot1="#ff5f57", dot2="#febc2e", dot3="#28c840",
    ),
}

MONO = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, 'Liberation Mono', monospace"


# ---------------------------------------------------------------- HEADER

def header_svg(t: dict) -> str:
    W, H = 900, 330
    fs = 15
    cw = fs * 0.62           # generous monospace char width, used for the typing clip
    x0, y0, lh = 28, 84, 27
    key_x = x0
    val_x = x0 + 11 * cw

    type_start, type_dur = 0.5, 1.4
    line_start, line_gap = type_start + type_dur + 0.35, 0.22

    prompt = f"{PROMPT_USER} ~ $ "
    cmd_x = x0 + len(prompt) * cw * 0.97
    cmd_w = len(COMMAND) * cw + 12
    steps = len(COMMAND)
    widths = ";".join(f"{(i / steps) * cmd_w:.1f}" for i in range(steps + 1))

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Terminal: kubectl describe engineer mella7. Mohamed Ali Mellah, Cloud Security Engineer.">')
    out.append(f"""<style>
  text {{ font-family: {MONO}; font-size: {fs}px; }}
  .muted {{ fill: {t['muted']}; }}
  .text {{ fill: {t['text']}; }}
  .strong {{ fill: {t['strong']}; font-weight: 700; }}
  .accent {{ fill: {t['accent']}; font-weight: 600; }}
  .green {{ fill: {t['green']}; }}
  .red {{ fill: {t['red']}; font-weight: 700; }}
  .small {{ font-size: 12px; }}
  .tiny {{ font-size: 11px; letter-spacing: .04em; }}
  .in {{ opacity: 0; animation: in .35s ease-out forwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateY(4px); }} to {{ opacity: 1; transform: none; }} }}
  .cursor {{ animation: blink 1.1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .scroll {{ animation: scroll 6s linear infinite; }}
  @keyframes scroll {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-240px); }} }}
  .flash {{ animation: flash 2.4s ease-in-out infinite; }}
  @keyframes flash {{ 0%, 100% {{ opacity: .15; }} 50% {{ opacity: .55; }} }}
  @media (prefers-reduced-motion: reduce) {{
    .in {{ animation: none; opacity: 1; }}
    .cursor, .scroll, .flash {{ animation: none; }}
  }}
</style>""")

    # window
    out.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{t["bg"]}" stroke="{t["border"]}"/>')
    out.append(f'<path d="M1 13 a12 12 0 0 1 12 -12 H{W-13} a12 12 0 0 1 12 12 V38 H1 Z" fill="{t["panel"]}"/>')
    out.append(f'<line x1="1" y1="38" x2="{W-1}" y2="38" stroke="{t["border"]}"/>')
    for i, c in enumerate((t["dot1"], t["dot2"], t["dot3"])):
        out.append(f'<circle cx="{22 + i * 20}" cy="20" r="6" fill="{c}"/>')
    out.append(f'<text x="{W/2}" y="25" text-anchor="middle" class="muted small">{escape(PROMPT_USER)}: ~ (zsh)</text>')

    # prompt + typed command
    out.append(f'<text x="{x0}" y="{y0}"><tspan class="green">{escape(PROMPT_USER)}</tspan><tspan class="muted"> ~ $</tspan></text>')
    out.append(f'<clipPath id="type"><rect x="{cmd_x:.1f}" y="{y0-18}" width="0" height="26">'
               f'<animate attributeName="width" values="{widths}" begin="{type_start}s" dur="{type_dur}s" '
               f'calcMode="discrete" fill="freeze"/></rect></clipPath>')
    out.append(f'<text x="{cmd_x:.1f}" y="{y0}" class="strong" clip-path="url(#type)">{escape(COMMAND)}</text>')

    # describe output
    y = y0
    delay = line_start
    for key, val, style in DESCRIBE:
        y += lh
        out.append(f'<g class="in" style="animation-delay:{delay:.2f}s">'
                   f'<text x="{key_x}" y="{y}" class="muted">{escape(key)}</text>'
                   f'<text x="{val_x:.1f}" y="{y}" class="{style}" xml:space="preserve">{escape(val)}</text></g>')
        delay += line_gap

    # status with pulsing dot
    y += lh
    out.append(f'<g class="in" style="animation-delay:{delay:.2f}s">'
               f'<text x="{key_x}" y="{y}" class="muted">Status:</text>'
               f'<circle cx="{val_x + 5:.1f}" cy="{y - 5}" r="5" fill="{t["green"]}">'
               f'<animate attributeName="opacity" values="1;.35;1" dur="1.8s" repeatCount="indefinite"/></circle>'
               f'<circle cx="{val_x + 5:.1f}" cy="{y - 5}" r="5" fill="none" stroke="{t["green"]}">'
               f'<animate attributeName="r" values="5;12" dur="1.8s" repeatCount="indefinite"/>'
               f'<animate attributeName="opacity" values=".7;0" dur="1.8s" repeatCount="indefinite"/></circle>'
               f'<text x="{val_x + 18:.1f}" y="{y}" class="green">{escape(STATUS)}</text></g>')
    delay += line_gap + 0.2

    # final prompt + blinking cursor
    y += lh + 4
    out.append(f'<g class="in" style="animation-delay:{delay:.2f}s">'
               f'<text x="{x0}" y="{y}"><tspan class="green">{escape(PROMPT_USER)}</tspan><tspan class="muted"> ~ $</tspan></text>'
               f'<rect class="cursor" x="{cmd_x:.1f}" y="{y - 14}" width="9" height="18" fill="{t["accent"]}"/></g>')

    # side panel: live runtime signals
    px, py, pw, ph = 612, 58, 268, 252
    out.append(f'<g class="in" style="animation-delay:{line_start - 0.2:.2f}s">')
    out.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="{t["panel"]}" stroke="{t["border"]}"/>')
    out.append(f'<circle cx="{px + 18}" cy="{py + 21}" r="4" fill="{t["green"]}">'
               f'<animate attributeName="opacity" values="1;.3;1" dur="1.4s" repeatCount="indefinite"/></circle>')
    out.append(f'<text x="{px + 30}" y="{py + 25}" class="muted tiny">RUNTIME SIGNALS</text>')
    out.append(f'<text x="{px + pw - 16}" y="{py + 25}" text-anchor="end" class="muted tiny">eBPF</text>')

    # scrolling waveform (two identical 240px tiles, translated by one tile)
    wx, wy, ww, wh = px + 14, py + 40, pw - 28, 70
    out.append(f'<clipPath id="wave"><rect x="{wx}" y="{wy}" width="{ww}" height="{wh}"/></clipPath>')
    out.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="6" fill="{t["panel2"]}"/>')
    rnd = random.Random(7)
    tile = 240
    mid = wy + wh / 2
    pts = []
    for i in range(0, tile + 1, 4):
        v = rnd.uniform(-4, 4)
        if i in (64, 172):
            v = -26
        elif i in (68, 176):
            v = 18
        pts.append((i, v))
    pts[-1] = (tile, pts[0][1])  # seamless tile
    d = " ".join(f"{'M' if k == 0 else 'L'}{wx + x + off:.1f} {mid + v:.1f}"
                 for off in (0, tile) for k, (x, v) in enumerate(pts) if not (off and k == 0))
    out.append(f'<g clip-path="url(#wave)"><g class="scroll">'
               f'<path d="{d}" fill="none" stroke="{t["accent"]}" stroke-width="1.6" stroke-linejoin="round"/>'
               f'</g></g>')

    # event list
    ey = wy + wh + 26
    for i, (ev, verdict, ok) in enumerate(EVENTS):
        yy = ey + i * 24
        if not ok:
            out.append(f'<rect class="flash" x="{px + 8}" y="{yy - 16}" width="{pw - 16}" height="22" rx="4" fill="{t["red"]}"/>')
        out.append(f'<text x="{px + 16}" y="{yy}" class="text small">{escape(ev)}</text>')
        out.append(f'<text x="{px + pw - 16}" y="{yy}" text-anchor="end" class="small {"green" if ok else "red"}">{escape(verdict)}</text>')
    out.append("</g>")

    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------- STACK

def text_w(s: str, fs: float) -> float:
    return len(s) * fs * 0.62


def stack_svg(t: dict) -> str:
    W, H = 900, 430
    pool_w, pool_h = 262, 112
    cx, cy = W / 2, H / 2 + 4
    lefts = [(20, 22), (20, 160), (20, 298)]
    rights = [(W - 20 - pool_w, 22), (W - 20 - pool_w, 160), (W - 20 - pool_w, 298)]
    slots = lefts + rights

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack: ' +
               escape("; ".join(f"{p}: {', '.join(items)}" for p, items in POOLS)) + '">')
    out.append(f"""<style>
  text {{ font-family: {MONO}; }}
  .pool {{ font-size: 12px; fill: {t['muted']}; letter-spacing: .02em; }}
  .pill {{ font-size: 12px; fill: {t['pill_text']}; }}
  .hub {{ font-size: 18px; font-weight: 700; fill: {t['strong']}; }}
  .hubs {{ font-size: 11px; fill: {t['muted']}; letter-spacing: .06em; }}
  .ready {{ font-size: 11px; fill: {t['green']}; }}
  .flow {{ stroke-dasharray: 3 11; animation: flow 1.6s linear infinite; }}
  @keyframes flow {{ to {{ stroke-dashoffset: -28; }} }}
  @media (prefers-reduced-motion: reduce) {{ .flow {{ animation: none; }} }}
</style>""")

    # edges first so pools/hub sit on top
    for i, (x, y) in enumerate(slots):
        left = x < cx
        ex = x + pool_w if left else x
        ey = y + pool_h / 2
        hx = cx - 62 if left else cx + 62
        mx = (ex + hx) / 2
        d = f"M{hx:.1f} {cy:.1f} C{mx:.1f} {cy:.1f} {mx:.1f} {ey:.1f} {ex:.1f} {ey:.1f}"
        out.append(f'<path d="{d}" fill="none" stroke="{t["border"]}" stroke-width="1.5"/>')
        out.append(f'<path class="flow" style="animation-delay:-{i * 0.27:.2f}s" d="{d}" fill="none" stroke="{t["edge"]}" stroke-width="2" stroke-linecap="round"/>')

    # hub (control plane hexagon)
    r = 66
    hexpts = " ".join(f"{cx + r * c:.1f},{cy + r * s:.1f}" for c, s in
                      [(1, 0), (.5, .866), (-.5, .866), (-1, 0), (-.5, -.866), (.5, -.866)])
    # pulse ring: a hexagon centred on the origin, scaled up and faded, then moved to the hub
    ring = " ".join(f"{r * c:.1f},{r * s:.1f}" for c, s in
                    [(1, 0), (.5, .866), (-.5, .866), (-1, 0), (-.5, -.866), (.5, -.866)])
    out.append(f'<g transform="translate({cx} {cy})"><polygon points="{ring}" fill="none" stroke="{t["accent"]}" stroke-width="1.5">'
               f'<animateTransform attributeName="transform" type="scale" values="1;1.25" dur="2.4s" repeatCount="indefinite"/>'
               f'<animate attributeName="opacity" values=".7;0" dur="2.4s" repeatCount="indefinite"/></polygon></g>')
    out.append(f'<polygon points="{hexpts}" fill="{t["panel"]}" stroke="{t["accent"]}" stroke-width="2"/>')
    out.append(f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" class="hub">mella7</text>')
    out.append(f'<text x="{cx}" y="{cy + 18}" text-anchor="middle" class="hubs">CONTROL-PLANE</text>')

    # pools
    for i, ((name, items), (x, y)) in enumerate(zip(POOLS, slots)):
        out.append("<g>")
        out.append(f'<rect x="{x}" y="{y}" width="{pool_w}" height="{pool_h}" rx="10" fill="{t["panel"]}" stroke="{t["border"]}"/>')
        out.append(f'<text x="{x + 14}" y="{y + 24}" class="pool">pool/{escape(name)}</text>')
        out.append(f'<circle cx="{x + pool_w - 58}" cy="{y + 20}" r="3.5" fill="{t["green"]}"/>')
        out.append(f'<text x="{x + pool_w - 14}" y="{y + 24}" text-anchor="end" class="ready">Ready</text>')
        # pills, wrapped
        px, py = x + 14, y + 38
        for item in items:
            w = text_w(item, 12) + 18
            if px + w > x + pool_w - 12:
                px, py = x + 14, py + 32
            out.append(f'<rect x="{px:.1f}" y="{py}" width="{w:.1f}" height="24" rx="12" fill="{t["pill"]}"/>')
            out.append(f'<text x="{px + w / 2:.1f}" y="{py + 16}" text-anchor="middle" class="pill">{escape(item)}</text>')
            px += w + 6
        out.append("</g>")

    out.append("</svg>")
    return "\n".join(out)


def main():
    ASSETS.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (ASSETS / f"header-{name}.svg").write_text(header_svg(t))
        (ASSETS / f"stack-{name}.svg").write_text(stack_svg(t))
    print("wrote", ", ".join(sorted(p.name for p in ASSETS.glob("*.svg"))))


if __name__ == "__main__":
    main()
