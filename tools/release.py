"""Set the version number everywhere at once, or check that it agrees.

    python tools/release.py                 check: app, README and CHANGELOG agree
    python tools/release.py 3.7             release 3.7 dated today
    python tools/release.py 3.7 --date "16 Oct 2026"

Releasing updates APP_VERSION and RELEASE_DATE in index.html, the README badge and
"Current version" line, and adds a "## 3.7 · date" section to CHANGELOG.md if there isn't one.
The tests fail until that section has real notes in place of the placeholder.
"""
import os, re, sys, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda f: os.path.join(ROOT, f)
PLACEHOLDER = '- Describe what changed.'
VER_RE = r"const APP_VERSION='([^']+)', RELEASE_DATE='([^']+)'"

def read(f): return open(P(f), encoding='utf-8').read()
def write(f, s): open(P(f), 'w', encoding='utf-8').write(s)
def key(v): return tuple(int(x) for x in v.split('.'))

def current():
    m = re.search(VER_RE, read('index.html'))
    if not m: raise SystemExit('Could not find APP_VERSION in index.html')
    return m.group(1), m.group(2)

def problems():
    v, d = current(); out = []
    readme, log = read('README.md'), read('CHANGELOG.md')
    if f'version-{v}-blue' not in readme: out.append(f'README badge does not say {v}')
    if f'**Current version: {v} · {d}.**' not in readme: out.append(f'README "Current version" line does not say {v} · {d}')
    heads = re.findall(r'^## (.+)$', log, re.M)
    if not heads or heads[0].strip() != f'{v} · {d}': out.append(f'the newest CHANGELOG section is "{heads[0] if heads else "missing"}", not "{v} · {d}"')
    top = log.split('\n## ', 2)[1] if '\n## ' in log else ''
    if PLACEHOLDER in top: out.append(f'CHANGELOG {v} still has the placeholder; write what changed')
    if f'*Headline for {v}*' in top: out.append(f'CHANGELOG {v} still has the placeholder headline')
    out += changelog_problems(log)
    return out

AREAS = {'practice', 'progress', 'recordings', 'backup', 'look', 'fixes'}

def changelog_problems(log):
    """The app's Changelog page is built from CHANGELOG.md, so check the format it relies on."""
    out, lines = [], log.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('## '):
            if not re.fullmatch(r'## \d+(\.\d+)+ · \d{1,2} [A-Z][a-z]{2,3} \d{4}', line):
                out.append(f'CHANGELOG heading "{line}" should look like "## 3.7 · 15 Oct 2026"')
            nxt = next((l for l in lines[i + 1:] if l.strip()), '')
            if not re.fullmatch(r'\*[^*].*\*', nxt.strip()):
                out.append(f'CHANGELOG {line[3:]} needs an *italic headline* on the line after the heading')
    for a in re.findall(r'<!--\s*area:\s*([a-z]+)\s*-->', log):
        if a not in AREAS: out.append(f'CHANGELOG uses unknown area "{a}" (use {", ".join(sorted(AREAS))})')
    return out

def release(v, d):
    old, old_d = current()
    if not re.fullmatch(r'\d+\.\d+(\.\d+)?', v): raise SystemExit(f'"{v}" is not a version like 3.7 or 3.7.1')
    if key(v) <= key(old): raise SystemExit(f'{v} is not newer than the current {old}')
    html = read('index.html')
    write('index.html', html.replace(f"const APP_VERSION='{old}', RELEASE_DATE='{old_d}'", f"const APP_VERSION='{v}', RELEASE_DATE='{d}'"))
    readme = read('README.md')
    readme = re.sub(r'version-[\d.]+-blue', f'version-{v}-blue', readme)
    readme = re.sub(r'!\[Version [\d.]+\]', f'![Version {v}]', readme)
    readme = re.sub(r'\*\*Current version: [^*]+\.\*\*', f'**Current version: {v} · {d}.**', readme)
    write('README.md', readme)
    log = read('CHANGELOG.md')
    if f'\n## {v} · ' not in log:
        i = log.index('\n## ')
        log = log[:i] + f'\n## {v} · {d}\n*Headline for {v}*\n\n{PLACEHOLDER}\n' + log[i:]
        write('CHANGELOG.md', log)
        print(f'Added a {v} section to CHANGELOG.md. Write what changed there.')
    print(f'{old} → {v} · {d}')

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        v, d = current(); pr = problems()
        print(f'Version {v} · {d}')
        for p in pr: print('  ✗ ' + p)
        if not pr: print('  ✓ the app, README and CHANGELOG agree')
        sys.exit(1 if pr else 0)
    date = args[args.index('--date') + 1] if '--date' in args else (lambda t: f'{t.day} {t.strftime("%b %Y")}')(dt.date.today())
    release(args[0], date)
