"""Vocal Sessions · the element sheet (Q48): every named part, written from the screen register.

    python3 tools/reference/elements.py           write reference/elements.md
    python3 tools/reference/elements.py --check   exit 1 if reference/elements.md is out of date (the tests run this)

Reads js/register.js only (no browser): the shared parts, the names by action and each screen's own parts, with the
screen's ID and name, how the part is found, the parts kit part it is (its pk- class) and its status. Values (sizes,
springs, corners) come later, with the element sheet's own plan. See MAINTAINING › Screen IDs › Naming rules.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, 'js', 'register.js')
OUT = os.path.join(ROOT, 'reference', 'elements.md')
PART = re.compile(r"\{ name: '([a-z0-9-]+)', sel: '((?:[^'\\]|\\.)*)'(?:, was: \[([^\]]*)\])?(?:, status: '([^']+)')? \}")


def kit(sel):
    k = sorted(set(re.findall(r'\.(pk-[a-z-]+)', sel)))
    return ', '.join('`' + x + '`' for x in k) if k else ''


def status(st):
    return 'In use' if not st or st == 'Live' else st.replace('Retired in', 'Retired ·')


def rows(text):
    """(area comment, name, sel, was, status) for every part in a slice of the register."""
    out, area = [], ''
    for line in text.split('\n'):
        c = re.match(r'\s*// (.+)', line)
        if c and 'name:' not in line: area = c.group(1)
        m = PART.search(line)
        if m:
            was = ', '.join(re.findall(r"'([a-z0-9-]+)'", m.group(3) or ''))
            out.append((area, m.group(1), m.group(2).replace('\\', ''), was, status(m.group(4))))
    return out


def build():
    src = open(REG, encoding='utf-8').read()
    shared = src[src.index('  shared: ['):src.index('  actions: [')]
    actions = src[src.index('  actions: ['):src.index('  screens: [')]
    screens = src[src.index('  screens: ['):src.index('  flows: [')]
    esc = lambda s: s.replace('|', '\\|')
    L = ['# Element sheet · Vocal Sessions', '',
         'Every named part in the app: its name, where it is named, how the app finds it, the parts kit part it is and its status. '
         'Written by `tools/reference/elements.py` from `js/register.js`; don\'t edit by hand. Values (sizes, springs, corners) '
         'come later. The naming rules: [MAINTAINING › Screen IDs › Naming rules](../MAINTAINING.md#naming-rules).', '',
         'A note points at a part as `VS-009 › song-row`; a shared or by-action part is named the same on every screen it shows on.', '']
    sh = rows(shared)
    ac = rows(actions)
    n_screen = 0
    body = []
    for blk in re.split(r"\n {6}id: '", screens)[1:]:
        sid = blk[:6]
        nm = re.search(r"\n {6}name: '((?:[^'\\]|\\.)*)'", blk)
        st = re.search(r"\n {6}status: '([^']+)'", blk)
        parts = rows(blk.split('parts: [', 1)[1]) if 'parts: [' in blk else []
        if not parts: continue
        n_screen += len(parts)
        body += ['### ' + sid + ' · ' + (nm.group(1).replace("\\'", "'") if nm else '') + ('' if not st or st.group(1) == 'Live' else ' (' + st.group(1) + ')'), '',
                 '| Name | Found by | Kit part | Status | Was |', '|---|---|---|---|---|']
        body += ['| `%s` | `%s` | %s | %s | %s |' % (r[1], esc(r[2]), kit(r[2]), r[4], r[3]) for r in parts] + ['']
    L += ['**%d shared parts, %d names by action, %d parts named on their screens.**' % (len(sh), len(ac), n_screen), '']
    L += ['## Shared', '', 'Named wherever they show: the tab bar, Back, Close, the standard roles, fields and links.', '',
          '| Name | Found by | Kit part | Status |', '|---|---|---|---|']
    L += ['| `%s` | `%s` | %s | %s |' % (r[1], esc(r[2]), kit(r[2]), r[4]) for r in sh] + ['']
    L += ['## By action', '', 'Wherever the action shows, its button gets this name. A screen\'s own parts and the shared ones win over these.', '']
    area = None
    for r in ac:
        if r[0] != area:
            area = r[0]
            L += ['', '### ' + area, '', '| Name | Found by | Status |', '|---|---|---|']
        L.append('| `%s` | `%s` | %s |' % (r[1], esc(r[2]), r[4]))
    L += ['', '## On their screens', ''] + body
    return '\n'.join(L).rstrip() + '\n'


if __name__ == '__main__':
    text = build()
    if '--check' in sys.argv:
        same = os.path.exists(OUT) and open(OUT, encoding='utf-8').read() == text
        print('reference/elements.md is ' + ('up to date' if same else 'out of date: run python3 tools/reference/elements.py'))
        sys.exit(0 if same else 1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(text)
    print('wrote reference/elements.md')
