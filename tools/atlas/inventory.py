"""Visual App Atlas (Q30) · reading the app's code and docs, with no browser.

- inventory(): every screen the code can show, read from render() and renderSheet() (and the functions renderSheet
  hands sheets to), plus the Settings pages and every U.tab / U.view / U.sheet the code sets.
- doc_sections(): the sections of README.md and MAINTAINING.md, with the address GitHub gives each one.
- changelog(): each version's headline, queue ID and address.
"""
import os, re

GH = 'https://github.com/imperialfox/Vocal-Sessions/blob/main/'


# ---------- reading JavaScript ----------
def _skip(src, i):
    """If src[i] starts a string or comment, the index just after it; else None."""
    c = src[i]
    if c in '\'"`':
        j = i + 1
        while j < len(src):
            if src[j] == '\\': j += 2; continue
            if src[j] == c: return j + 1
            if c == '`' and src.startswith('${', j):  # a template's ${…}: skip the code inside it
                j = _block_end(src, j + 1) + 1; continue
            j += 1
        return j
    if src.startswith('//', i):
        j = src.find('\n', i); return len(src) if j < 0 else j
    if src.startswith('/*', i):
        j = src.find('*/', i + 2); return len(src) if j < 0 else j + 2
    return None


def _block_end(src, i):
    """src[i] is '{': the index of the '}' that closes it (strings, comments and templates skipped)."""
    depth = 0
    while i < len(src):
        k = _skip(src, i)
        if k is not None: i = k; continue
        if src[i] == '{': depth += 1
        elif src[i] == '}':
            depth -= 1
            if depth == 0: return i
        i += 1
    return len(src) - 1


def function_body(src, name):
    """The body of `function name(...) {...}` (top level or nested), or '' if there's none."""
    m = re.search(r'function\s+' + re.escape(name) + r'\s*\([^)]*\)\s*\{', src)
    if not m: return ''
    start = m.end() - 1
    return src[start:_block_end(src, start) + 1]


def app_source(repo):
    src = {}
    for f in sorted(os.listdir(os.path.join(repo, 'js'))):
        if f.endswith('.js'): src[f] = open(os.path.join(repo, 'js', f), encoding='utf-8').read()
    return src


def inventory(repo):
    """Every screen state the code can show, as {'Kind:name': {'kind', 'name', 'where'}}.

    Kinds: Tab (U.tab), Screen (U.view), Sheet (U.sheet), Sub-page (Settings pages, U.setPg).
    Sources, so nothing the drawing code can show is missed:
      - render(): each `v === 'x'` and the tab table `{today: scrToday, ...}`
      - renderSheet(): each `s === 'x'`, and the sheets of the functions it hands a family of sheets to
        (a `/^sg[A-Z]/` test hands every 'sg…' sheet named in that function, and so on)
      - Settings' TITLE table (its pages)
      - every `U.tab = 'x'`, `U.view = 'x'`, `U.sheet = 'x'`, `U.setPg = 'x'` and `data-a="sheet" data-v="x"` in the code
    """
    src = app_source(repo)
    allsrc = '\n'.join(src.values())
    found = {}

    def add(kind, name, where):
        k = kind + ':' + name
        if k not in found: found[k] = {'kind': kind, 'name': name, 'where': where}

    r = function_body(src.get('ui.js', allsrc), 'render')
    for v in re.findall(r"\bv\s*===\s*'([A-Za-z]\w*)'", r): add('Screen', v, 'render()')
    tabs = re.search(r"\{\s*((?:\s*\w+\s*:\s*[\w.]+\s*,?)+)\s*\}\s*\[\s*U\.tab\s*\]", r)
    if tabs:
        for t in re.findall(r'(\w+)\s*:', tabs.group(1)): add('Tab', t, 'render()')
    # a view drawn by a fall-through (scrFlow) is named in config's FLOW table
    flow = re.search(r'const FLOW\s*=\s*\{([^}]*)\}', allsrc)
    if flow and 'scrFlow' in r:
        for v in re.findall(r'(\w+)\s*:', flow.group(1)): add('Screen', v, 'render() › scrFlow (FLOW)')

    rs = function_body(src.get('ui.js', allsrc), 'renderSheet')
    for s in re.findall(r"\bs\s*===\s*'([A-Za-z]\w*)'", rs): add('Sheet', s, 'renderSheet()')
    # families handed on: `s && /^sg[A-Z]/.test(s)) h = songSheet(s)`
    for pre, fn in re.findall(r"/\^(\w+)(?:\[[^\]]*\])?/\.test\(s\)\)\s*h\s*=\s*([\w.]+)\(", rs):
        name = fn.split('.')[-1]
        for f, code in src.items():  # every function by that name (TRACK.sheet is a `function sheet` in track.js)
            body = function_body(code, name)
            for s in re.findall(r"(?:\b\w\s*===?\s*|case\s+)'(" + pre + r"[A-Z]\w*)'", body):
                add('Sheet', s, 'renderSheet() › ' + fn + '()')

    title = re.search(r'const TITLE\s*=\s*\{(.*?)\};', src.get('settings.js', ''), re.S)
    if title:
        for k in re.findall(r"(\w+)\s*:\s*'", title.group(1)): add('Sub-page', k, 'Settings TITLE')

    for kind, rx in [('Tab', r"U\.tab\s*=\s*'([a-z]\w*)'"), ('Screen', r"U\.view\s*=\s*'([A-Za-z]\w*)'"),
                     ('Sheet', r"U\.sheet\s*=\s*'([A-Za-z]\w*)'"), ('Sub-page', r"U\.setPg\s*=\s*'([a-z]\w*)'"),
                     ('Sheet', r'data-a=\\?"sheet\\?"\s+data-v=\\?"([A-Za-z]\w*)\\?"')]:
        for f, code in src.items():
            for m in re.findall(rx, code): add(kind, m, f)
    return found


# ---------- docs ----------
def gh_slug(heading):
    """The anchor GitHub gives a Markdown heading: lower case, punctuation dropped (letters, digits, '-', '_' and
    spaces kept), spaces to '-'. Links and code marks count as their text."""
    h = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', heading)
    h = h.replace('`', '').strip().lower()
    h = re.sub(r'[^\w\- ]', '', h)
    return h.replace(' ', '-')


def doc_sections(repo, files=('README.md', 'MAINTAINING.md')):
    """Every ## and ### heading, with its GitHub address, plus README's bold sub-heads (like **Today** under Tabs),
    which have no address of their own: they link to the heading they sit under, labelled 'Tabs › Today'."""
    out = []
    for fname in files:
        seen, parent = {}, None
        in_code = False
        for i, line in enumerate(open(os.path.join(repo, fname), encoding='utf-8')):
            if line.startswith('```'): in_code = not in_code
            if in_code: continue
            m = re.match(r'^(#{1,6}) (.+?)\s*#*\s*$', line)
            if m:
                h = m.group(2).strip(); s = gh_slug(h)
                n = seen.get(s, 0); seen[s] = n + 1
                anchor = s if n == 0 else s + '-' + str(n)
                if len(m.group(1)) in (2, 3):
                    parent = {'file': fname, 'heading': h, 'label': h, 'anchor': anchor, 'line': i + 1,
                              'url': GH + fname + '#' + anchor}
                    out.append(parent)
                continue
            b = re.match(r'^\*\*([^*]+)\*\*', line)
            if b and parent and fname == 'README.md' and parent['heading'] == 'Tabs':
                out.append(dict(parent, heading=b.group(1).strip(), label=parent['heading'] + ' › ' + b.group(1).strip(),
                                line=i + 1, sub=True))
    return out


def changelog(repo):
    """Each version: number, date, headline, queue ID (if any), its own text and address on GitHub."""
    txt = open(os.path.join(repo, 'CHANGELOG.md'), encoding='utf-8').read()
    heads = list(re.finditer(r'^## (\d[\d.]*) · ([^\n]+)\n\*([^*\n]+)\*', txt, re.M))
    out = []
    for i, m in enumerate(heads):
        q = re.search(r'\((Q\d+)\)', m.group(3))
        out.append({'version': m.group(1), 'date': m.group(2).strip(), 'title': m.group(3).strip(),
                    'q': q.group(1) if q else None, 'url': GH + 'CHANGELOG.md#' + gh_slug(m.group(1) + ' · ' + m.group(2))})
    return out
