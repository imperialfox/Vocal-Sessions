"""Q40 · Interface: Value Set and Test (3.51). One named set of look and motion values, and a guard against new
strays, so the app stops drifting (Ivan's app look skill, 6b).

1 the named set at the top of css/app.css has the agreed numbers (corners, the solid press, three easings, two fade
timings) and resolves in the page; MOTION.EASE in js/motion.js holds the same three easings for code;
2 in css/app.css every corner above 6 px (not 999px or 50%), every :active press scale(), and every transition and
animation easing and duration is a named value (var(--r-…), var(--press), var(--ease-…), var(--dur-…)) or on the
known list below; in js/ every cubic-bezier( is on the known list (MOTION.EASE's own three are the names);
3 the known list may only get shorter: a new stray fails, and a stray that's gone and still listed fails too, with a
"list can shrink" message;
4 the guard itself works (a raw curve, corner and press added to a copy of the stylesheet are caught; a stray taken
away is noticed);
5 Q40's two fixes: the pattern player's speed bar and menu use the glass tokens, and the listed solid presses use
var(--press).

Exempt: graphic corners of 6 px and under (bars, ticks, meters, waveform bits follow the drawing), capsules (999px)
and circles (50%); slow ambient loops (1 s and over: Today's drifting gradient, pulses); delays; spring names from
MOTION (gentle, nav, ripple, press, release). Shadows are counted in the report only.
How to add a value on purpose, and why the list only shrinks: MAINTAINING.md › Value set (Q40).
VS_VALUES=named,css,js,guard,fixes runs only those parts."""
import os, re, glob, collections
from harness import ROOT

_only = [x for x in os.environ.get('VS_VALUES', '').split(',') if x]
wanted = lambda k: not _only or k in _only
CSS = os.path.join(ROOT, 'css', 'app.css')
JSDIR = os.path.join(ROOT, 'js')

# the agreed set (Render 3 Nov 2026, 08:08); change a number here and in app.css together, on purpose
NAMED = {
    'r-small': '10px', 'r-medium': '14px', 'r-card': '20px', 'r-large': '26px', 'r-sheet': '46px',
    'press': '0.93',
    'ease-pop': 'cubic-bezier(0.3, 1.7, 0.45, 1)', 'ease-knob': 'cubic-bezier(0.3, 1.35, 0.5, 1)',
    'ease-out': 'cubic-bezier(0.2, 0.8, 0.2, 1)',
    'dur-quick': '120ms', 'dur-fade': '200ms',
}

# ---------------------------------------------------------------- reading the stylesheet

AT_SKIP = ('@media', '@supports', '@container', '@layer')


def declarations(css):
    """Every declaration in the stylesheet: (selector, line, property, value, start, end), where start/end are the
    value's place in the text (so a tool can rewrite it). Comments are skipped; nested @media keeps its selector."""
    src = re.sub(r'/\*.*?\*/', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), css, flags=re.S)
    out, stack = [], []
    start, line, paren = 0, 1, 0
    for i, c in enumerate(src):
        if c == '(':
            paren += 1
        elif c == ')':
            paren -= 1
        elif paren == 0 and c in '{};':
            chunk = src[start:i]
            if c == '{':
                stack.append(' '.join(chunk.split()))
            else:
                d = _decl(stack, chunk, start, src)
                if d:
                    out.append(d)
                if c == '}' and stack:
                    stack.pop()
            start = i + 1
    return out


def _decl(stack, chunk, start, src):
    if ':' not in chunk:
        return None
    k = chunk.index(':')
    p = chunk[:k].strip().lower()
    if not re.fullmatch(r'-?[a-z][a-z-]*', p):
        return None
    lead = len(chunk) - len(chunk.lstrip())
    line = src.count('\n', 0, start + lead) + 1
    vs = start + k + 1
    ve = start + len(chunk.rstrip())
    sel = ' › '.join(s for s in stack if not s.startswith(AT_SKIP))
    return sel, line, p, ' '.join(src[vs:ve].split()), vs, ve


def split_top(v, sep):
    """Split at sep outside brackets."""
    out, depth, cur = [], 0, ''
    for c in v:
        depth += c == '('
        depth -= c == ')'
        if depth == 0 and (c == sep if sep != ' ' else c.isspace()):
            if cur.strip():
                out.append(cur.strip())
            cur = ''
        else:
            cur += c
    if cur.strip():
        out.append(cur.strip())
    return out


TIME = re.compile(r'^(-?\d*\.?\d+)(ms|s)$')
KEYWORD_EASE = {'ease', 'ease-in', 'ease-out', 'ease-in-out', 'linear', 'step-start', 'step-end'}


def ms(tok):
    m = TIME.match(tok)
    return float(m.group(1)) * (1 if m.group(2) == 'ms' else 1000) if m else None


def is_ease(tok):
    return tok in KEYWORD_EASE or tok.startswith(('cubic-bezier(', 'steps(', 'linear('))


def norm(tok):
    return re.sub(r'\s*,\s*', ', ', re.sub(r'\(\s*', '(', re.sub(r'\s*\)', ')', tok)))


def items(css):
    """Every value the guard looks at: (kind, selector, property, token, line, named?) where kind is corner, press,
    ease or duration. Exempt values aren't listed. Also returns the shadows written out by hand (report only)."""
    out, shadows = [], []
    for sel, line, p, v, s, e in declarations(css):
        if p.startswith('--'):
            continue
        v = re.sub(r'\s*!important$', '', v)
        if p == 'box-shadow' and v not in ('none', 'inherit') and not v.startswith('var('):
            shadows.append(v)
        if 'radius' in p:
            for tok in split_top(v.replace('/', ' '), ' '):
                if tok.startswith('var('):
                    out.append(('corner', sel, p, tok, line, tok.startswith('var(--r-')))
                    continue
                m = re.fullmatch(r'(\d*\.?\d+)px', tok)
                if tok in ('0', '999px', '50%', 'inherit', 'initial') or (m and float(m.group(1)) <= 6):
                    continue
                out.append(('corner', sel, p, tok, line, False))
        if ':active' in sel and p in ('transform', 'scale'):
            args = re.findall(r'\bscale\(((?:[^()]|\([^()]*\))*)\)', v) if p == 'transform' else [v]
            for a in args:
                a = a.strip()
                if a == 'var(--press)':
                    out.append(('press', sel, p, 'scale(var(--press))', line, True))
                elif re.fullmatch(r'\d*\.?\d+', a) and float(a) >= 1:
                    continue
                else:
                    out.append(('press', sel, p, f'scale({a})', line, False))
        if p.startswith(('transition', 'animation')):
            if p.endswith('-delay') or p.endswith(('-name', '-property', '-fill-mode', '-iteration-count',
                                                   '-direction', '-play-state', '-behavior')):
                continue
            for seg in split_top(v, ','):
                toks = split_top(seg, ' ')
                if p.endswith('-timing-function'):
                    toks, durs = toks, []
                    eases = toks
                elif p.endswith('-duration'):
                    durs, eases = toks, []
                else:
                    times = [t for t in toks if ms(t) is not None or t.startswith(('var(--dur-', 'calc('))]
                    durs = times[:1]  # the second time in a shorthand is a delay
                    eases = [t for t in toks if is_ease(t) or t.startswith('var(--ease-')]
                if any(ms(d) is not None and ms(d) >= 1000 for d in durs):
                    continue  # a slow ambient loop
                for d in durs:
                    if ms(d) == 0:
                        continue
                    out.append(('duration', sel, p, d, line, ms(d) is None and 'var(--dur-' in d))
                for t in eases:
                    out.append(('ease', sel, p, norm(t), line, t.startswith('var(--ease-')))
    return out, shadows


def key(it):
    return ' · '.join(it[:4])


# ---------------------------------------------------------------- reading the code

def js_curves(files=None):
    """cubic-bezier( in js/, as 'file · curve'. MOTION.EASE's own (the names, for code) are returned apart."""
    found, names = [], {}
    # the parts kit's pinned copy is checked by the kit's own value rule (tools/values.py in its repo), not here (Q41)
    for f in files or sorted(x for x in glob.glob(os.path.join(JSDIR, '*.js')) if not os.path.basename(x).startswith('parts-kit')):
        src = open(f, encoding='utf-8').read() if isinstance(f, str) and os.path.exists(f) else f[1]
        name = os.path.basename(f) if isinstance(f, str) else f[0]
        ease = re.search(r'const EASE = \{(.*?)\};', src, re.S) if name == 'motion.js' else None
        if ease:
            names = {k: norm(c) for k, c in re.findall(r"(\w+): '(cubic-bezier\([^)]*\))'", ease.group(1))}
            src = src[:ease.start()] + src[ease.end():]
        found += [f'{name} · {norm(c)}' for c in re.findall(r'cubic-bezier\([^)]*\)', src)]
    return found, names


def compare(found, known):
    """(new, gone): what's in found but not known, and what's known but no longer found (as multisets)."""
    f, k = collections.Counter(found), collections.Counter(known)
    return list((f - k).elements()), list((k - f).elements())


def same_curve(a, b):
    nums = lambda s: [float(x) for x in re.findall(r'-?\d*\.?\d+', s)]
    return nums(a) == nums(b)


# ---------------------------------------------------------------- the known list (it may only get shorter)
# Every value here was in the app at Q40 (3.51) and doesn't match a name. They leave as their parts move onto the
# parts kit, so nothing is tidied twice. Remove a line when its value goes; never add one without a reason
# (MAINTAINING.md › Value set (Q40) says how to add a value on purpose).
# Rows and row-like cards lost their 0.98 / 0.96 shrink at Q41: decision D06 turned it into a highlight.

KNOWN = [
    'corner · body.sheet-open .wrap · border-radius · 28px',
    'corner · .lgcard · border-radius · 22px',
    'corner · .bkstat · border-radius · 16px',
    'corner · .arch · border-radius · 24px',
    'corner · .tile.big · border-radius · 18px',
    'corner · .fw · border-radius · 22px',
    'corner · .fw .fwopen · border-radius · 17px',
    'corner · .nudge · border-radius · 16px',
    'corner · .addnote · border-radius · 16px',
    'corner · .sckrows · border-radius · 18px',
    'corner · .sbi · border-radius · 12px',
    'corner · body.reg .shead · border-radius · 28px',
    'corner · body.reg .shead · border-radius · 28px',
    'corner · .pcard · border-radius · 22px',
    'corner · .sfield.inl · border-radius · 12px',
    'corner · .sgwarn · border-radius · 12px',
    'corner · .blk · border-radius · 16px',
    'corner · .rl · border-radius · 8px',
    'corner · .zm-shade · border-radius · 22px',
    'corner · .cv-slot · border-radius · 16px',
    'corner · .cvthumb · border-radius · 8px',
    'corner · .cvthumb.big · border-radius · 9px',
    "corner · .fw[data-kind='video'][data-size='m'] · border-radius · 15px",
    "corner · .fw[data-kind='video'][data-size='l'] · border-radius · 16px",
    'corner · .fwtabin · border-radius · 16px',
    'corner · .fwtabin · border-radius · 16px',
    'corner · .fwtab.r .fwtabin · border-radius · 16px',
    'corner · .fwtab.r .fwtabin · border-radius · 16px',
    'corner · .cklen.ed · border-radius · 8px',
    'corner · .sgl.ckcur · border-radius · 8px',
    'corner · .ckpop · border-radius · 22px',
    'corner · .ckband · border-radius · 9px',
    'corner · .ckwcol:focus-visible · border-radius · 9px',
    'corner · body.reg .trkroll · border-radius · 12px',
    'corner · .trksong · border-radius · 18px',
    'corner · .trktl · border-radius · 18px',
    'corner · .trkpad · border-radius · 24px',
    'corner · .sglenv · border-radius · 12px',
    'corner · .setfoot img · border-radius · 13.5px',
    'corner · .hint · border-radius · 7px',
    'corner · .mksheet · border-radius · 28px',
    'corner · .sgl.mknow · border-radius · 8px',
    'corner · .mkpeek · border-radius · 24px',
    'corner · .rgi.big .tile · border-radius · 12px',
    'corner · .aphead .tile · border-radius · 12px',
    'corner · .prange.bad · border-radius · 12px',
    'corner · .extip · border-radius · 16px',
    'corner · .pstep · border-radius · 24px',
    'corner · .prep · border-radius · 24px',
    'corner · .pplay · border-radius · 24px',
    'corner · .pwin · border-radius · 22px',
    'corner · .preset · border-radius · 16px',
    'ease · .wrap · transition · cubic-bezier(0.3, 1.3, 0.5, 1)',
    'ease · .tl-in.seen · transition · ease',
    'ease · .tabbar · transition · cubic-bezier(0.3, 1.3, 0.5, 1)',
    'ease · .tabbar button · transition · cubic-bezier(0.3, 1.25, 0.5, 1)',
    'ease · .sw .fg · transition · ease',
    'ease · .notebox · animation · ease',
    'ease · #ptr.go .spin · animation · steps(8)',
    'ease · main.ptr-snap · transition · cubic-bezier(0.25, 0.8, 0.3, 1)',
    'ease · #splash · transition · ease',
    'ease · #splash .sp-icon · transition · cubic-bezier(0.3, 0.9, 0.4, 1)',
    'ease · html.motion-reduced *, html.motion-reduced *::before, html.motion-reduced *::after · transition-timing-function · ease-out',
    'ease · .rowc · transition · cubic-bezier(0.3, 1.2, 0.5, 1)',
    'ease · .w.pulse · animation · ease-out',
    'ease · .crow · transition · cubic-bezier(0.3, 1.2, 0.5, 1)',
    'ease · .hx · transition · ease',
    'ease · .hx::after · transition · ease',
    'ease · .hxin .hx · animation · ease',
    'ease · .hxin .hx::after · animation · ease',
    'ease · .fw .fwvc · transition · linear',
    'ease · .tkfg · transition · cubic-bezier(0.3, 1.2, 0.5, 1)',
    'ease · [data-edge-fade] · transition · ease-out',
    'ease · [data-edge-fade] · transition · ease-out',
    'ease · .hint · transition · ease-out',
    'ease · html.motion-reduced .mksheet · animation · ease',
    'ease · .pdraw .pnt · transition · cubic-bezier(0.3, 1.6, 0.5, 1)',
    'ease · .pdraw .prip · animation · ease-out',
    'ease · .pvowel b.swap · animation · cubic-bezier(0.3, 1.4, 0.5, 1)',
    'ease · .pt · transition · cubic-bezier(0.3, 1.5, 0.5, 1)',
    'duration · .wrap · transition · 0.45s',
    'duration · #lgchart .ar · transition · 0.25s',
    'duration · .tl-card · transition · 0.4s',
    'duration · .tl-more svg.i · transition · 0.3s',
    'duration · .tl-in.seen · transition · 0.5s',
    'duration · .tl-in.seen · transition · 0.6s',
    'duration · .arch · transition · 0.5s',
    'duration · .cta, .circ, .row, .chip, .calbtn, .cal button · transition · 0.5s',
    'duration · .tabbar · transition · 0.45s',
    'duration · .tabbar button · transition · 0.5s',
    'duration · .tabbar button · transition · 0.45s',
    'duration · .tabbar button · transition · 0.25s',
    'duration · .tabbar button · transition · 0.35s',
    'duration · .sw .fg · transition · 0.22s',
    'duration · .fw .fwbtn · transition · 0.5s',
    'duration · .nudge · transition · 0.5s',
    'duration · .notebox · animation · 0.3s',
    'duration · .shbtn · transition · 0.5s',
    'duration · .spin i · transition · 0.08s',
    'duration · #ptr.go .spin · animation · 0.8s',
    'duration · main.ptr-snap · transition · 0.42s',
    'duration · .sbi · transition · 0.15s',
    'duration · #splash · transition · 0.35s',
    'duration · #splash .sp-icon · transition · 0.45s',
    'duration · .txtbtn · transition · 0.5s',
    'duration · .rowc · transition · 0.35s',
    'duration · .w.pulse · animation · 0.9s',
    'duration · .crow · transition · 0.25s',
    'duration · .meter i · transition · 0.1s',
    'duration · .hx · transition · 0.35s',
    'duration · .hx::after · transition · 0.35s',
    'duration · .hxin .hx · animation · 0.25s',
    'duration · .hxin .hx::after · animation · 0.25s',
    'duration · .rl.peeking .hx · transition-duration · 0.22s',
    'duration · .rl.peeking .hx::after · transition-duration · 0.22s',
    'duration · .cvpp · transition · 0.5s',
    'duration · .cvpill · transition · 0.5s',
    'duration · .ckpi · transition · 0.5s',
    'duration · .ckc · transition · 0.5s',
    'duration · .trkb · transition · 0.5s',
    'duration · .trkpp · transition · 0.5s',
    'duration · .trkpill · transition · 0.5s',
    'duration · .trkpad · transition · 0.5s',
    'duration · .sgplay · transition · 0.5s',
    'duration · .sgtkb · transition · 0.5s',
    'duration · .tkfg · transition · 0.35s',
    'duration · .tkbig · transition · 0.5s',
    'duration · [data-edge-fade] · transition · 0.25s',
    'duration · [data-edge-fade] · transition · 0.25s',
    'duration · .setfoot · transition · 0.5s',
    'duration · .hint.show · transition-duration · 0.18s',
    'duration · .osum · transition · 0.5s',
    'duration · .ring .arc · transition · 0.3s',
    'duration · .cuebox · transition · 0.3s',
    'duration · .apsing · transition · 0.5s',
    'duration · .apsoft · transition · 0.5s',
    'duration · .apstop · transition · 0.5s',
    'duration · .pdraw .pnt · transition · 0.25s',
    'duration · .pdraw .prip · animation · 0.6s',
    'duration · .pvowel b.swap · animation · 0.45s',
    'duration · .pplay · transition · 0.5s',
    'duration · .pt · transition · 0.35s',
    'duration · .pt · transition · 0.35s',
    'duration · .pt .pst > span · transition · 0.25s',
    'duration · #pHud .phscrim · transition · 0.3s',
    'duration · .phbub · transition · 0.45s',
]

KNOWN_JS = [
    'details.js · cubic-bezier(.4, 0, .6, 1)',
    'details.js · cubic-bezier(.3, .7, .3, 1)',
    'launch.js · cubic-bezier(.3, .7, .4, 1)',
    'launch.js · cubic-bezier(.3, .7, .4, 1)',
]

# Q40's two fixes
GLASS_FIX = []  # Q40's two glass fixes (.phbar, .pmenu) left with their parts at Q41: the parts kit's slider and menus
PRESS_FIX = ['.ckpi:active', '.cktile:active .ckc', '.sgplay:active',
             '.trkpad:not(.glass):active, .trkpill:not(.glass):active',
             '.pplay:active, .prep:not(.glass):active, .ppill:not(.glass):active', '.nudge:active']


# ---------------------------------------------------------------- the checks

def named(b, t):
    ok = t.ok
    css = open(CSS, encoding='utf-8').read()
    root = css[css.index(':root {'):css.index('}', css.index(':root {'))]
    got = {k: ' '.join(v.split()) for k, v in re.findall(r'--([a-z0-9-]+):\s*([^;]+);', root)}
    bad = {k: got.get(k) for k, v in NAMED.items() if got.get(k) != v}
    ok(not bad, f'the named set at the top of app.css has the agreed values ({bad})')
    ok(root.index('--r-small') > root.index('--t-num-l'), 'it sits beside the text sizes')
    # Q41 the springs are the parts kit's (MOTION reads them from Parts.motion)
    kit = open(os.path.join(JSDIR, 'parts-kit.js'), encoding='utf-8').read()
    kit = kit[kit.index('const SPRINGS = {'):]
    kit = kit[:kit.index('};')]
    springs = re.findall(r"^\s{4}'?([\w-]+)'?: ", kit, re.M)
    defined = set(got) | {f'{a}-{s}' for s in springs for a in ('ease', 'dur')}
    used = set(re.findall(r'var\(--((?:r|ease|dur)-[a-z0-9-]+|press)\b', css))
    ok(used <= defined, f'every named value used is defined, in app.css or as a parts kit spring ({used - defined})')
    _, names = js_curves()
    ok(set(names) == {'pop', 'knob', 'out'} and all(same_curve(names[k], NAMED['ease-' + k]) for k in names),
       f'MOTION.EASE holds the same three easings for code ({names})')
    pg = t.page(b)
    vals = pg.evaluate("ks=>ks.map(k=>getComputedStyle(document.documentElement).getPropertyValue('--'+k).trim())", list(NAMED))
    ok(dict(zip(NAMED, vals)) == NAMED, f'the names resolve in the page ({dict(zip(NAMED, vals))})')
    ok(pg.evaluate("MOTION.EASE.out") == "cubic-bezier(.2,.8,.2,1)", 'MOTION.EASE.out is reachable from code')
    pg.context.close()


def css_strays(b, t):
    ok = t.ok
    css = open(CSS, encoding='utf-8').read()
    its, shadows = items(css)
    shadow_vals = collections.Counter(shadows)
    stray = [i for i in its if not i[5]]
    new, gone = compare([key(i) for i in stray], KNOWN)
    lines = collections.defaultdict(list)
    for i in stray:
        lines[key(i)].append(i[4])
    ok(not new, 'no new stray values in app.css' + ('' if not new else ': use a named value, or add one on purpose (MAINTAINING › Value set): '
       + '; '.join(f'line {lines[k][0]}: {k}' for k in new[:8]) + (f' … and {len(new) - 8} more' if len(new) > 8 else '')))
    ok(not gone, 'every known stray is still in app.css' + ('' if not gone else ': the list can shrink, so take these off KNOWN in '
       'tests/test_values.py: ' + '; '.join(gone[:8]) + (f' … and {len(gone) - 8} more' if len(gone) > 8 else '')))
    use = collections.Counter(i[0] for i in its if i[5])
    left = collections.Counter(k.split(' · ')[0] for k in KNOWN)
    print(f'  ····  named uses: corners {use["corner"]}, presses {use["press"]}, easings {use["ease"]}, '
          f'durations {use["duration"]}')
    print(f'  ····  known strays: corners {left["corner"]}, presses {left["press"]}, easings {left["ease"]}, '
          f'durations {left["duration"]}, curves in code {len(KNOWN_JS)}')
    print(f'  ····  shadows written out by hand (not enforced): {len(shadows)}, {len(shadow_vals)} different, '
          f'{sum(1 for v in shadow_vals.values() if v == 1)} used once')


def js_strays(b, t):
    ok = t.ok
    found, _ = js_curves()
    new, gone = compare(found, KNOWN_JS)
    ok(not new, 'no new hand-written curves in js/' + (f': use a MOTION spring or MOTION.EASE ({new})' if new else ''))
    ok(not gone, 'every known curve in code is still there' + (f': the list can shrink, so take these off KNOWN_JS in tests/test_values.py ({gone})' if gone else ''))


def guard(b, t):
    """The guard catches what it should, on copies (the real files aren't touched)."""
    ok = t.ok
    css = open(CSS, encoding='utf-8').read()
    extra = ('\n.vtest:active { transform: scale(0.91); border-radius: 11px; '
             'transition: opacity 0.3s cubic-bezier(0.1, 0.2, 0.3, 1); }\n')
    its, _ = items(css + extra)
    new, gone = compare([key(i) for i in its if not i[5]], KNOWN)
    kinds = sorted(k.split(' · ')[0] for k in new)
    ok(kinds == ['corner', 'duration', 'ease', 'press'] and not gone,
       f'a new corner, press, curve and duration are each caught ({new})')
    named_extra = ('\n.vtest:active { transform: scale(var(--press)); border-radius: var(--r-card); '
                   'transition: opacity var(--dur-fade) var(--ease-out), transform 2s ease-in-out infinite; '
                   'border-radius: 4px 999px 50%; }\n')
    its, _ = items(css + named_extra)
    new, _ = compare([key(i) for i in its if not i[5]], KNOWN)
    ok(not new, f'named values, small graphic corners, capsules, circles and slow loops pass ({new})')
    if KNOWN:
        k = KNOWN[0].split(' · ')
        its, _ = items(css)
        line = next(i[4] for i in its if key(i) == KNOWN[0])
        src = css.splitlines(True)
        src[line - 1] = src[line - 1].replace(k[3], 'var(--r-card)' if k[0] == 'corner' else 'var(--press)' if k[0] == 'press'
                                              else 'var(--ease-out)' if k[0] == 'ease' else 'var(--dur-fade)', 1)
        its, _ = items(''.join(src))
        new, gone = compare([key(i) for i in its if not i[5]], KNOWN)
        ok(gone == [KNOWN[0]] and not new, f'a stray taken away is noticed, so the list must shrink ({gone})')
    found, _ = js_curves([(os.path.basename(f), open(f, encoding='utf-8').read()) for f in glob.glob(os.path.join(JSDIR, '*.js'))
                          if not os.path.basename(f).startswith('parts-kit')]
                         + [('new.js', "el.animate(f, {easing: 'cubic-bezier(.1,.2,.3,1)'})")])
    new, _ = compare(found, KNOWN_JS)
    ok(new == ['new.js · cubic-bezier(.1, .2, .3, 1)'], f'a new curve in code is caught ({new})')


def fixes(b, t):
    ok = t.ok
    pg = t.page(b)
    rules = pg.evaluate("""sels=>{const o={};for(const sh of document.styleSheets){for(const r of sh.cssRules){
      if(r.selectorText&&sels.includes(r.selectorText))o[r.selectorText]=[(r.style.backdropFilter||r.style.webkitBackdropFilter),r.style.transform]}}return o}""",
                        GLASS_FIX + PRESS_FIX)
    for s in GLASS_FIX:
        bf = (rules.get(s) or [''])[0]
        ok('var(--glass-blur)' in bf and 'var(--glass-sat)' in bf and '26px' not in bf,
           f'{s}: the pattern player’s glass uses the glass tokens ({bf})')
    for s in PRESS_FIX:
        tf = (rules.get(s) or ['', ''])[1]
        ok(tf == 'scale(var(--press))', f'{s}: a solid press at --press, 0.93 ({tf})')
    pg.context.close()


def run(b, t):
    if wanted('named'): named(b, t)
    if wanted('css'): css_strays(b, t)
    if wanted('js'): js_strays(b, t)
    if wanted('guard'): guard(b, t)
    if wanted('fixes'): fixes(b, t)
