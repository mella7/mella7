"""Builds the terminal card at the top of the profile (dark_mode.svg, light_mode.svg).

The card plays a short shell session: `whoami`, `neofetch` with the ASCII art from
scripts/ascii_*.txt, then a few scenes, each one starting with `clear`. Everything is SMIL,
so it animates on github.com without JavaScript, and loops forever.

    pip install fonttools brotli && python3 scripts/update_card.py
In Actions, GITHUB_TOKEN is set and the GitHub stats are fetched live from the GraphQL API.
"""
import base64, html, io, json, os, urllib.request
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER = 'mella7'

# ============================================================ content (edit freely)
HOST = 'mella7@cluster'
WHOAMI = 'Mohamed Ali Mellah, Cloud Security Engineer'

INFO = [   # neofetch block. None = blank line. Dots are added automatically.
    ('OS', 'Linux, Kubernetes, OpenShift'),
    ('Host', 'Germany, from Tunisia'),
    ('Kernel', 'Cloud Security Engineer'),
    ('Packages', 'kubectl, helm, tetragon, falco'),
    ('Shell', 'zsh on ghostty, Fedora'),
    None,
    ('Languages.Code', 'Go, Python, TypeScript'),
    ('Languages.Infra', 'HCL, YAML, Bash'),
    ('Languages.Spoken', 'ar, fr, en, de (B1)'),
    None,
    ('Focus.Runtime', 'eBPF detection, Tetragon'),
    ('Focus.Identity', 'CI/CD and workload identity'),
    ('Focus.Platform', 'operators, GitOps'),
    None,
    ('Certs', 'CKA, CKAD, RHCSA, eJPT'),
    ('Award', 'Huawei ICT, Global 1st'),
]
CONTACT = [
    ('Web', 'mella7.me'),
    ('LinkedIn', 'MellahMedAli'),
    ('Medium', '@mellahmohamedali'),
]

# colour keys for scene output
T, D, K, V, OK, BAD, WARN = 'text', 'cc', 'key', 'value', 'ok', 'bad', 'warn'

SCENES = [
    [   # 1. who I am
        ('kubectl get pods -n mella7', [
            [('NAME                          READY   STATUS              RESTARTS', D)],
            [('runtime-security-7f4c9        ', V), ('1/1     ', T), ('Running             ', OK), ('0', T)],
            [('platform-engineering-5d2a8    ', V), ('1/1     ', T), ('Running             ', OK), ('0', T)],
            [('identity-audit-9b1e3          ', V), ('1/1     ', T), ('Running             ', OK), ('0', T)],
            [('msc-informatik-passau-3c7f    ', V), ('1/1     ', T), ('Running             ', OK), ('0', T)],
            [('deutsch-b1-6a3d0              ', V), ('1/1     ', T), ('Running             ', OK), ('1  (was A2)', D)],
            [('cks-exam-2c8f1                ', V), ('0/1     ', T), ('ContainerCreating   ', WARN), ('0', T)],
        ]),
        ('kubectl get certifications', [
            [('NAME    ISSUER              STATUS', D)],
            [('cka     ', V), ('Linux Foundation    ', T), ('Certified', OK)],
            [('ckad    ', V), ('Linux Foundation    ', T), ('Certified', OK)],
            [('rhcsa   ', V), ('Red Hat             ', T), ('Certified', OK)],
            [('ejpt    ', V), ('INE Security        ', T), ('Certified', OK)],
            [('cks     ', V), ('Linux Foundation    ', T), ('In progress', WARN)],
        ]),
        ('git log --oneline', [
            [('7e3a91c ', K), ('feat: MSc Informatik, University of Passau', T)],
            [('4b0d2f8 ', K), ('feat: Cloud Security Engineer', T)],
            [('a1f9e64 ', K), ('feat: Global 1st Prize, Huawei ICT Competition (Shenzhen)', T)],
            [('9c52b07 ', K), ('feat: Diplôme d\'Ingénieur, Informatique, TEK-UP (Mention Bien)', T)],
            [('2d8e1aa ', K), ('init: Licence, Réseaux et Services Informatiques, ISET Radès', T)],
        ]),
    ],
    [   # 2. the eBPF talk, live
        ('cat talks.txt', [
            [('ContainerDays Hamburg 2026   ', V), ('How Clusters Fail Under Attack and How We Detect', T)],
            [('                             ', V), ('It at Runtime with eBPF Signals', T)],
            [('Cloud Identity Summit 2026   ', V), ('Your CI/CD Pipeline Is Over-Privileged:', T)],
            [('                             ', V), ('Identity Risks in Modern Cloud Platforms', T)],
        ]),
        ('tetra getevents -o compact --pods web', [
            [('process  ', K), ('default/web-7d9f  ', V), ('/bin/sh -i', T)],
            [('connect  ', K), ('default/web-7d9f  ', V), ('/bin/sh  tcp 10.0.2.15:41522 -> 203.0.113.7:4444', T)],
            [('setuid   ', K), ('default/web-7d9f  ', V), ('/usr/bin/su  uid 1000 -> 0', T)],
            [('sigkill  ', BAD), ('default/web-7d9f  ', V), ('/bin/sh  ', T), ('enforced by TracingPolicy block-revshell', BAD)],
        ]),
        ('falco-mcp triage --since 24h', [
            [('alerts grouped by workload, deduplicated, joined with RBAC', D)],
            [('3 incidents need a human. ', OK), ('The rest was noise.', T)],
        ]),
    ],
    [   # 3. identity, then contact
        ('kubectl auth can-i get secrets -A --as=system:serviceaccount:ci:deployer', [
            [('yes', BAD)],
            [('# and that is the problem. Pipelines are identities too.', D)],
        ]),
        ('mcp-sentinel audit -n agents', [
            [('CRITICAL  ', BAD), ('mcp-github   ', V), ('ServiceAccount can read secrets cluster-wide', T)],
            [('HIGH      ', WARN), ('mcp-slack    ', V), ('long-lived token, never rotated', T)],
            [('fix       ', OK), ('scoped Role written to roles/mcp-github.yaml', T)],
        ]),
        ('cat ~/.contact', [
            [('web       ', K), ('https://mella7.me', V)],
            [('linkedin  ', K), ('MellahMedAli', V)],
            [('medium    ', K), ('@mellahmohamedali', V)],
            [('mail      ', K), ('mellah.mohamedali@outlook.com', V)],
        ]),
        ('./open-to-work.sh', [
            [('Junior DevOps, DevSecOps and Platform Engineering roles.', OK)],
            [('Switzerland, Luxembourg, Germany. Say hi on ', T), ('mella7.me', V)],
        ]),
    ],
]

# ============================================================ style
FS, LH, CW = 16, 20, 9.6          # JetBrains Mono: advance is 0.6 em
AFS, ALH, ACW = 12, 14, 7.2       # ASCII art is drawn smaller
PAD, GAP, COLS = 18, 28, 54
TYPE, LINE, PAUSE, READ, HOLD = 0.085, 0.09, 1.2, 4.5, 8.0
THEMES = {
    'dark':  dict(bg='#161b22', border='#30363d', text='#c9d1d9', cc='#5c6672', key='#2dd4bf', value='#a5d6ff',
                  ok='#3fb950', bad='#ff7b72', warn='#e3b341', prompt='#2dd4bf', art='#2a9d8f'),
    'light': dict(bg='#f6f8fa', border='#d0d7de', text='#24292f', cc='#a8b3bf', key='#0f766e', value='#0a3069',
                  ok='#1a7f37', bad='#cf222e', warn='#9a6700', prompt='#0f766e', art='#3d8f86'),
}
FALLBACK = None   # stats shown as "-" when they can't be fetched


def fetch_stats():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        return FALLBACK
    q = '''query($u:String!){ user(login:$u){ followers{totalCount}
      repositories(ownerAffiliations:OWNER, privacy:PUBLIC, first:100){ totalCount nodes{ stargazerCount } }
      repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST,ISSUE], first:1){ totalCount }
      contributionsCollection{ contributionCalendar{ totalContributions } } } }'''
    try:
        req = urllib.request.Request('https://api.github.com/graphql', json.dumps({'query': q, 'variables': {'u': USER}}).encode(),
                                     {'Authorization': f'bearer {token}', 'Content-Type': 'application/json'})
        u = json.load(urllib.request.urlopen(req, timeout=30))['data']['user']
        return dict(repos=u['repositories']['totalCount'], stars=sum(n['stargazerCount'] for n in u['repositories']['nodes']),
                    followers=u['followers']['totalCount'], contributed=u['repositoriesContributedTo']['totalCount'],
                    contributions=u['contributionsCollection']['contributionCalendar']['totalContributions'])
    except Exception as err:
        print('stats unavailable, keeping placeholders:', err)
        return FALLBACK


esc = lambda s: html.escape(s, quote=False)


def dots(k, v, width):
    return max(width - len(k) - len(v) - 5, 2)


def info_lines(stats):
    lines = [[(HOST, 'title'), (' ' + '-' * (COLS - len(HOST) - 1), 'cc')]]
    for item in INFO:
        lines.append([] if item is None else kv(*item))
    lines += [[], [('- Contact ' + '-' * (COLS - 10), 'cc')]] + [kv(k, v) for k, v in CONTACT]
    s = stats or {}
    g = lambda k: f'{s[k]:,}' if k in s else '-'
    lines += [[], [('- GitHub ' + '-' * (COLS - 9), 'cc')], pair('Repos', g('repos'), 'Stars', g('stars')),
              pair('Followers', g('followers'), 'Contributions', g('contributions'))]
    return lines


def kv(k, v, width=COLS):
    return [('. ', 'cc'), (k, 'key'), (':', 'text'), (' ' + '.' * dots(k, v, width) + ' ', 'cc'), (v, 'value')]


def pair(k1, v1, k2, v2):
    half = 25
    return kv(k1, v1, half) + [(' | ', 'text'), (k2, 'key'), (':', 'text'),
                               (' ' + '.' * dots(k2, v2, COLS - half - 1) + ' ', 'cc'), (v2, 'value')]


class Card:
    def __init__(self, theme, art):
        self.c = THEMES[theme]
        self.art = art
        self.els, self.t, self.n = [], 0.6, 0
        self.chars = set()
        aw = max(len(l) for l in art) * ACW
        self.rx = PAD + aw + GAP
        self.W = int(self.rx + COLS * CW + PAD)

    def row(self, r):
        return PAD + 14 + r * LH

    # --- primitives
    def show_at(self, at):
        return (f'<set attributeName="opacity" to="0" begin="clk.begin" fill="freeze"/>'
                f'<set attributeName="opacity" to="1" begin="clk.begin+{at:.2f}s" fill="freeze"/>')

    def spans(self, segs):
        out = ''
        for text, col in segs:
            self.chars.update(text)
            w = ' font-weight="800"' if col == 'title' else ''
            fill = self.c['prompt'] if col == 'title' else self.c[col]
            out += f'<tspan fill="{fill}"{w}>{esc(text)}</tspan>'
        return out

    def line(self, x, y, segs, size=None):
        fs = f' font-size="{size}"' if size else ''
        self.els.append(f'<text x="{x:.1f}" y="{y:.1f}"{fs} opacity="0">{self.show_at(self.t)}{self.spans(segs)}</text>')

    def prompt(self, y):
        self.line(PAD, y, [(HOST, 'title'), (':', 'cc'), ('~', 'value'), ('$ ', 'text')])
        return PAD + (len(HOST) + 4) * CW

    def command(self, y, cmd):
        x0 = self.prompt(y)
        self.chars.update(cmd)
        n, start = len(cmd), self.t + 0.5
        self.n += 1
        widths = ';'.join('0' if k == 0 else f'{k * CW + 2:.1f}' for k in range(n + 1))
        xs = ';'.join(f'{x0 + k * CW:.1f}' for k in range(n + 1))
        self.els.append(
            f'<clipPath id="k{self.n}"><rect x="{x0:.1f}" y="{y - 15}" height="21" width="0">'
            f'<set attributeName="width" to="0" begin="clk.begin" fill="freeze"/>'
            f'<animate attributeName="width" values="{widths}" calcMode="discrete" begin="clk.begin+{start:.2f}s" dur="{n * TYPE:.2f}s" fill="freeze"/>'
            f'</rect></clipPath>'
            f'<text x="{x0:.1f}" y="{y}" fill="{self.c["text"]}" clip-path="url(#k{self.n})">{esc(cmd)}</text>'
            f'<rect y="{y - 14}" width="{CW}" height="18" fill="{self.c["prompt"]}" opacity="0" x="{x0:.1f}">'
            f'<set attributeName="opacity" to="1" begin="clk.begin+{self.t:.2f}s" dur="{start + n * TYPE + .2 - self.t:.2f}s"/>'
            f'<animate attributeName="x" values="{xs}" calcMode="discrete" begin="clk.begin+{start:.2f}s" dur="{n * TYPE:.2f}s" fill="freeze"/></rect>')
        self.t = start + n * TYPE + 0.45

    def screen_end(self, since, at):
        """Wrap everything drawn since index `since` in a group that vanishes at `at` (the `clear`)."""
        body = ''.join(self.els[since:])
        del self.els[since:]
        self.els.append(f'<g><set attributeName="opacity" to="1" begin="clk.begin" fill="freeze"/>'
                        f'<set attributeName="opacity" to="0" begin="clk.begin+{at:.2f}s" fill="freeze"/>{body}</g>')

    # --- session
    def build(self, stats):
        info = info_lines(stats)
        block_h = max(len(info) * LH, len(self.art) * ALH)
        first = len(self.els)
        # whoami
        self.command(self.row(0), 'whoami')
        self.line(PAD, self.row(1), [(WHOAMI, 'text')]); self.t += PAUSE
        # neofetch
        self.command(self.row(2), 'neofetch')
        top = self.row(3) - 6
        t0 = self.t
        ay = top + (block_h - len(self.art) * ALH) / 2 + ALH * .8
        for i, l in enumerate(self.art):
            self.t = t0 + i * .035
            self.line(PAD, ay + i * ALH, [(l, 'art')], size=AFS)
        for j, segs in enumerate(info):
            self.t = t0 + j * LINE
            if segs:
                self.line(self.rx, top + 15 + j * LH, segs)
        self.t = t0 + max(len(self.art) * .035, len(info) * LINE) + 0.6
        r = int((top + block_h - PAD - 14) / LH) + 2
        heights = [self.row(r)]
        for scene in SCENES:
            self.t += READ
            self.command(self.row(r), 'clear')
            self.screen_end(first, self.t)
            first = len(self.els)
            self.t += .3
            r = 0
            for cmd, out in scene:
                self.command(self.row(r), cmd); r += 1
                for segs in out:
                    self.line(PAD, self.row(r), segs); self.t += LINE * 1.5; r += 1
                r += 1; self.t += PAUSE
            heights.append(self.row(r))
        # idle prompt, blinking cursor, then the whole session replays
        x0 = self.prompt(self.row(r))
        self.els.append(f'<rect x="{x0:.1f}" y="{self.row(r) - 14}" width="{CW}" height="18" fill="{self.c["prompt"]}" opacity="0">'
                        f'<animate attributeName="opacity" values="1;0" calcMode="discrete" dur="1.1s" begin="clk.begin+{self.t:.2f}s" repeatDur="{HOLD}s"/></rect>')
        H = int(max(heights) + LH + PAD - 6)
        return self.svg(H, self.t + HOLD)

    def svg(self, H, cycle):
        fonts = ''
        for weight in (400, 800):
            f = TTFont(os.path.join(ROOT, 'scripts', 'fonts', f'jetbrains-mono-latin-{weight}-normal.woff2'))
            o = subset.Options(); o.flavor = 'woff2'; o.layout_features = []
            sb = subset.Subsetter(o); sb.populate(text=''.join(self.chars) + ' :~$.-|'); sb.subset(f)
            b = io.BytesIO(); f.flavor = 'woff2'; f.save(b)
            fonts += (f"@font-face{{font-family:'JBM';font-weight:{weight};"
                      f"src:url(data:font/woff2;base64,{base64.b64encode(b.getvalue()).decode()}) format('woff2')}}")
        label = (f'Terminal session. whoami: {WHOAMI}. Certifications: CKA, CKAD, RHCSA, eJPT, CKS in progress. '
                 'Talks: ContainerDays Hamburg 2026, Cloud Identity Summit 2026. Global 1st Prize, Huawei ICT Competition. '
                 'Open to junior DevOps, DevSecOps and Platform Engineering roles. Web: mella7.me')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{H}" viewBox="0 0 {self.W} {H}" '
                f'font-family="JBM,ui-monospace,Consolas,monospace" font-size="{FS}" role="img" aria-label="{html.escape(label)}">'
                f'<style>{fonts}text,tspan{{white-space:pre;font-variant-ligatures:none}}</style>'
                f'<rect x=".5" y=".5" width="{self.W - 1}" height="{H - 1}" rx="14" fill="{self.c["bg"]}" stroke="{self.c["border"]}"/>'
                f'<rect width="0" height="0"><animate id="clk" attributeName="x" from="0" to="0" dur="{cycle:.2f}s" begin="0s;clk.end"/></rect>'
                + ''.join(self.els) + '</svg>')


if __name__ == '__main__':
    stats = fetch_stats()
    for theme in THEMES:
        art = open(os.path.join(ROOT, 'scripts', f'ascii_{theme}.txt')).read().rstrip('\n').split('\n')
        with open(os.path.join(ROOT, f'{theme}_mode.svg'), 'w') as f:
            f.write(Card(theme, art).build(stats))
    print('card built, stats:', stats)
