"""Builds the GitHub activity graphics from the GraphQL API:

  assets/activity-{dark,light}.svg   contributions per day over the last 31 days
  assets/stats-{dark,light}.svg      a stats panel and top languages, generated here instead of
                                     relying on a public stats service that gets rate-limited

    GITHUB_TOKEN=$(gh auth token) python3 scripts/build_activity.py
In Actions, GITHUB_TOKEN is provided by the workflow. Without a token, sample data is drawn
so the layout can be checked locally:  python3 scripts/build_activity.py --preview /tmp/out
"""
import datetime as dt, html, json, os, sys, urllib.request
from svgkit import ROOT, Text, width

USER = 'mella7'
DAYS = 31
THEMES = {
    'dark':  dict(bg='#161b22', border='#30363d', title='#2dd4bf', text='#c9d1d9', muted='#8b949e', grid='#30363d',
                  line='#2dd4bf', point='#a5d6ff', bar='#21262d'),
    'light': dict(bg='#f6f8fa', border='#d0d7de', title='#0f766e', text='#24292f', muted='#59636e', grid='#d0d7de',
                  line='#0f766e', point='#0a3069', bar='#eaeef2'),
}


def gql(query, variables):
    req = urllib.request.Request('https://api.github.com/graphql', json.dumps({'query': query, 'variables': variables}).encode(),
                                 {'Authorization': f'bearer {os.environ["GITHUB_TOKEN"]}', 'Content-Type': 'application/json'})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    if 'errors' in data:
        raise SystemExit(data['errors'])
    return data['data']['user']


def fetch():
    now = dt.datetime.now(dt.timezone.utc)
    start = (now - dt.timedelta(days=DAYS - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    u = gql('''query($u:String!,$from:DateTime!,$to:DateTime!,$year:DateTime!){ user(login:$u){
      recent: contributionsCollection(from:$from,to:$to){ contributionCalendar{ weeks{ contributionDays{ date contributionCount } } } }
      thisYear: contributionsCollection(from:$year,to:$to){ totalCommitContributions totalPullRequestContributions
        totalIssueContributions totalPullRequestReviewContributions }
      pullRequests{ totalCount } followers{ totalCount } issues{ totalCount }
      publicRepos: repositories(ownerAffiliations:OWNER, privacy:PUBLIC){ totalCount }
      repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST,ISSUE], first:1){ totalCount }
      repositories(ownerAffiliations:OWNER, isFork:false, first:100){ nodes{ stargazerCount
        languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name color } } } } } } }''',
            {'u': USER, 'from': start.isoformat(), 'to': now.isoformat(), 'year': year.isoformat()})
    days = sorted((d['date'], d['contributionCount']) for w in u['recent']['contributionCalendar']['weeks'] for d in w['contributionDays'])[-DAYS:]
    langs = {}
    for repo in u['repositories']['nodes']:
        for e in repo['languages']['edges']:
            n = e['node']['name']
            langs.setdefault(n, [0, e['node']['color'] or '#8b949e'])[0] += e['size']
    y = u['thisYear']
    total = sum(n for _, n in (sorted((d['date'], d['contributionCount']) for w in u['recent']['contributionCalendar']['weeks']
                                      for d in w['contributionDays'])))
    # candidates in order of preference; zeros are skipped so the panel never shows empty numbers
    pool = [('Commits this year', y['totalCommitContributions']), ('Pull requests', u['pullRequests']['totalCount']),
            ('Contributed to', u['repositoriesContributedTo']['totalCount']),
            ('Stars earned', sum(r['stargazerCount'] for r in u['repositories']['nodes'])),
            ('Reviews this year', y['totalPullRequestReviewContributions']), ('Issues opened', u['issues']['totalCount']),
            ('Public repos', u['publicRepos']['totalCount']), ('Followers', u['followers']['totalCount']),
            (f'Contributions, {DAYS} days', total)]
    stats = [kv for kv in pool if kv[1]][:6]
    return days, stats, sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]


def sample():
    today = dt.date.today()
    days = [((today - dt.timedelta(days=DAYS - 1 - i)).isoformat(), [0, 2, 5, 1, 0, 7, 3, 9, 4, 2, 6][i % 11]) for i in range(DAYS)]
    stats = [('Commits this year', 412), ('Pull requests', 37), ('Reviews this year', 12), ('Issues this year', 19),
             ('Contributed to', 9), ('Stars earned', 24)]
    langs = [('Go', [52, '#00ADD8']), ('Python', [31, '#3572A5']), ('TypeScript', [22, '#3178c6']), ('HCL', [11, '#844FBA']),
             ('Shell', [6, '#89e051']), ('Dockerfile', [3, '#384d54'])]
    return days, stats, langs


def frame(c, w, h, title, right, text):
    return (f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="{c["bg"]}" stroke="{c["border"]}"/>'
            + text(24, 36, title, 'Inter6', 17, c['title']) + (text(w - 24, 36, right, 'Inter4', 13, c['muted'], 'end') if right else ''))


def wrap_svg(w, h, label, text, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{html.escape(label)}"><style>{text.font_faces()}</style>{body}</svg>')


def activity(theme, days):
    c, text = THEMES[theme], Text()
    W, H, L, R, T, B = 900, 300, 54, 28, 62, 44
    total = sum(n for _, n in days)
    top = max(4, -(-max(n for _, n in days) // 4) * 4)
    pw, ph = W - L - R, H - T - B
    px = lambda i: L + pw * i / (len(days) - 1)
    py = lambda n: T + ph * (1 - n / top)
    pts = [(px(i), py(n)) for i, (_, n) in enumerate(days)]
    line = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    els = [frame(c, W, H, f'Contributions in the last {DAYS} days', f'{total} total', text),
           f'<defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c["line"]}" stop-opacity=".35"/>'
           f'<stop offset="1" stop-color="{c["line"]}" stop-opacity="0"/></linearGradient></defs>']
    for k in range(5):
        v = top * k // 4
        els.append(f'<line x1="{L}" x2="{W - R}" y1="{py(v):.1f}" y2="{py(v):.1f}" stroke="{c["grid"]}" stroke-dasharray="3 4"/>')
        els.append(text(L - 10, py(v) + 4, str(v), 'Inter4', 11, c['muted'], 'end'))
    for i in range(0, len(days), 5):
        els.append(text(px(i), H - 16, dt.date.fromisoformat(days[i][0]).strftime('%b %-d'), 'Inter4', 11, c['muted'], 'middle'))
    els.append(f'<polygon points="{px(0):.1f},{py(0):.1f} {line} {px(len(days) - 1):.1f},{py(0):.1f}" fill="url(#fill)"/>')
    els.append(f'<polyline points="{line}" fill="none" stroke="{c["line"]}" stroke-width="2.5" stroke-linejoin="round"/>')
    els += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{c["point"]}"><title>{days[i][0]}: {days[i][1]}</title></circle>'
            for i, (x, y) in enumerate(pts)]
    return wrap_svg(W, H, f'{total} contributions over the last {DAYS} days', text, ''.join(els))


def stats_card(theme, stats, langs):
    c, text = THEMES[theme], Text()
    W, H = 900, 230
    els = [frame(c, W, H, 'GitHub stats', None, text)]
    # left: two columns of numbers
    for i, (k, v) in enumerate(stats):
        col, row = i // 3, i % 3
        x, y = 24 + col * 205, 82 + row * 50
        els.append(text(x, y, f'{v:,}', 'Mono8', 22, c['text']))
        els.append(text(x, y + 19, k, 'Inter4', 12.5, c['muted']))
    # right: language bar + legend
    x0, x1 = 470, W - 24
    els.append(text(x0, 36, 'Top languages', 'Inter6', 17, c['title']))
    total = sum(v for _, (v, _) in langs) or 1
    x, bw = x0, x1 - x0
    els.append(f'<clipPath id="bar"><rect x="{x0}" y="58" width="{bw}" height="12" rx="6"/></clipPath><g clip-path="url(#bar)">'
               f'<rect x="{x0}" y="58" width="{bw}" height="12" fill="{c["bar"]}"/>')
    for name, (v, color) in langs:
        w = bw * v / total
        els.append(f'<rect x="{x:.1f}" y="58" width="{w:.1f}" height="12" fill="{color}"/>'); x += w
    els.append('</g>')
    for i, (name, (v, color)) in enumerate(langs):
        lx, ly = x0 + (i % 2) * 215, 104 + (i // 2) * 36
        els.append(f'<circle cx="{lx + 6}" cy="{ly - 5}" r="6" fill="{color}"/>')
        els.append(text(lx + 20, ly, name, 'Inter6', 14, c['text']))
        els.append(text(lx + 20 + width('Inter6', name, 14) + 8, ly, f'{100 * v / total:.1f}%', 'Inter4', 13, c['muted']))
    label = 'GitHub stats: ' + ', '.join(f'{k} {v}' for k, v in stats) + '. Top languages: ' + ', '.join(n for n, _ in langs)
    return wrap_svg(W, H, label, text, ''.join(els))


if __name__ == '__main__':
    preview = '--preview' in sys.argv
    if os.environ.get('GITHUB_TOKEN') and not preview:
        days, stats, langs = fetch()
    elif preview:
        days, stats, langs = sample()
    else:
        raise SystemExit('Set GITHUB_TOKEN (or pass --preview to draw sample data).')
    out = sys.argv[sys.argv.index('--preview') + 1] if preview else os.path.join(ROOT, 'assets')
    os.makedirs(out, exist_ok=True)
    for theme in THEMES:
        with open(os.path.join(out, f'activity-{theme}.svg'), 'w') as f:
            f.write(activity(theme, days))
        with open(os.path.join(out, f'stats-{theme}.svg'), 'w') as f:
            f.write(stats_card(theme, stats, langs))
    print(f'activity: {sum(n for _, n in days)} contributions in {len(days)} days; stats: {stats}; langs: {[n for n, _ in langs]}')
