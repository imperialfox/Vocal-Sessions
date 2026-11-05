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

Q54 (3.68) widened it: shadows (the parts kit's three names, or known), hex colours in rules (tokens, or known), and
in js/ times (ms: and duration: with a number of 10 or more) and keyword easings (easing: 'ease-out' …), each named
(MOTION.dur, MOTION.ms, MOTION.reducedMs, MOTION.CUE, ZOOM and LAUNCH, MOTION.EASE, a spring) or on a known list
that only shrinks. Every value left on a list carries a one-line reason.

Exempt: graphic corners of 6 px and under (bars, ticks, meters, waveform bits follow the drawing), capsules (999px)
and circles (50%); slow ambient loops (1 s and over: Today's drifting gradient, pulses); delays; spring names from
MOTION (gentle, nav, ripple, press, release); shadows that only draw a ring or a stroke (inset, or no offset and no
blur); masks' colours; proportions in code (d * 0.3); the named tables in js/motion.js.
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


# ---------------------------------------------------------------- reading the look values (Q54)

def _ring(layer):
    """A shadow layer that draws a ring or a stroke (inset, or no offset and no blur), not a shadow."""
    t = split_top(layer, ' ')
    if t and t[0] == 'inset':
        return True
    nums = [x for x in t if re.fullmatch(r'-?\d*\.?\d+(px)?', x)]
    return len(nums) >= 3 and all(float(n.replace('px', '')) == 0 for n in nums[:3])


def shadows(css):
    """Hand-written shadows, as (selector, value, line): not var(), not none, not only rings and strokes."""
    out = []
    for sel, line, p, v, _, _ in declarations(css):
        if p != 'box-shadow':
            continue
        v = re.sub(r'\s*!important$', '', v)
        if v in ('none', 'inherit', 'initial'):
            continue
        if any(not l.startswith('var(') and not _ring(l) for l in split_top(v, ',')):
            out.append((sel, v, line))
    return out


def colours(css):
    """Hex colours written in rules, as 'selector · property · #hex' with their line. Custom properties are where
    colours are named; masks are exempt (only their alpha counts)."""
    out = []
    for sel, line, p, v, _, _ in declarations(css):
        if p.startswith('--') or 'mask' in p:
            continue
        out += [(f'{sel} · {p} · {h.lower()}', line) for h in re.findall(r'#[0-9a-fA-F]{3,8}\b', v)]
    return out


# ---------------------------------------------------------------- reading the code

# the pinned libraries aren't the app's code; the parts kit's copy is checked by the kit's own value rule
# (tools/values.py in its repo), not here (Q41)
LIBS = ('pitchy.js', 'tonal.js', 'musictheory.js')
# Q54 the named tables in js/motion.js: the one place the code's own timings and easings are written as numbers
TABLES = ('EASE', 'CUE', 'ZOOM', 'LAUNCH')


def _js_files():
    return [(os.path.basename(x), open(x, encoding='utf-8').read()) for x in sorted(glob.glob(os.path.join(JSDIR, '*.js')))
            if not os.path.basename(x).startswith('parts-kit') and os.path.basename(x) not in LIBS]


def _code(name, src):
    """The code without comments, and motion.js without its named tables (returned apart)."""
    src = re.sub(r'/\*.*?\*/', lambda m: re.sub(r'[^\n]', '', m.group(0)), src, flags=re.S)
    src = re.sub(r'(^|[\s;{}(,])//[^\n]*', r'\1', src)
    tables = {}
    if name == 'motion.js':
        for t in TABLES:
            m = re.search(r'const ' + t + r' = \{.*?\};', src, re.S)
            if m:
                tables[t] = m.group(0)
                src = src[:m.start()] + src[m.end():]
    return src, tables


def js_curves(files=None):
    """cubic-bezier( in js/, as 'file · curve'. MOTION.EASE's own (the names, for code) are returned apart."""
    found, names = [], {}
    for name, src in files or _js_files():
        src, tables = _code(name, src)
        if 'EASE' in tables:
            names = {k: norm(c) for k, c in re.findall(r"(\w+): '(cubic-bezier\([^)]*\))'", tables['EASE'])}
        found += [f'{name} · {norm(c)}' for c in re.findall(r'cubic-bezier\([^)]*\)', src)]
    return found, names


def _value(src, i):
    """The expression from i to the next top-level , or closing bracket."""
    d, j = 0, i
    while j < len(src):
        c = src[j]
        if c in '([{':
            d += 1
        elif c in ')]}':
            if d == 0:
                break
            d -= 1
        elif c == ',' and d == 0:
            break
        j += 1
    return src[i:j]


def js_times(files=None):
    """Q54 times and keyword easings written in code: 'file · ms: 300' for every number of 10 or more in an ms: or
    duration: value (smaller numbers are proportions, d * 0.3), and 'file · ease-out' for every keyword easing: value."""
    times, eases = [], []
    for name, src in files or _js_files():
        src, _ = _code(name, src)
        for m in re.finditer(r'(?<![.\w$])(ms|duration)\s*:\s*', src):
            for n in re.findall(r'(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])', _value(src, m.end())):
                if float(n) >= 10:
                    times.append(f'{name} · {m.group(1)}: {n}')
        for m in re.finditer(r'(?<![.\w$])easing\s*:\s*([\'"`])([^\'"`]*)\1', src):
            e = m.group(2).strip()
            if e in KEYWORD_EASE or e.startswith('steps('):
                eases.append(f'{name} · {e}')
    return times, eases


def compare(found, known):
    """(new, gone): what's in found but not known, and what's known but no longer found (as multisets)."""
    f, k = collections.Counter(found), collections.Counter(known)
    return list((f - k).elements()), list((k - f).elements())


def same_curve(a, b):
    nums = lambda s: [float(x) for x in re.findall(r'-?\d*\.?\d+', s)]
    return nums(a) == nums(b)


# ---------------------------------------------------------------- the known lists (they may only get shorter)
# Every value here doesn't match a name, each with its reason (Q54 gave every line one). Remove a line when its value
# goes; never add one without a reason (MAINTAINING.md › Value set says how to add a value on purpose).
# Q40 (3.51) started the list with 114 values; Q54 (3.68) named all but these.

KNOWN = [
    # the floating window: Q26's 58 pt capsule with 22 pt corners (test_pip checks it), the video's own corners by size,
    # and its parts sitting concentric inside it
    ('corner · .fw · border-radius · 22px', 'Q26: the floating capsule is 58 pt with 22 pt corners'),
    ('corner · .fw .fwopen · border-radius · 17px', 'concentric inside the 22 pt capsule (22 − 5 pt)'),
    ("corner · .fw[data-kind='video'][data-size='m'] · border-radius · 15px", 'the video window keeps its own corner by size'),
    ("corner · .fw[data-kind='video'][data-size='l'] · border-radius · 16px", 'the video window keeps its own corner by size'),
    ('corner · .fwtabin · border-radius · 16px', 'the tucked window’s tab, its half capsule at the edge'),
    ('corner · .fwtabin · border-radius · 16px', 'the same tab’s other corner'),
    ('corner · .fwtab.r .fwtabin · border-radius · 16px', 'the tab tucked at the right edge'),
    ('corner · .fwtab.r .fwtabin · border-radius · 16px', 'the same tab’s other corner'),
    ('corner · .hint · border-radius · 7px', 'the pointer hint is a Mac-style tooltip (no name within 2 pt)'),
    ('duration · #lgchart .ar · transition · 0.25s', 'the Changelog chart (kept by the audit): bars dimming while picking'),
    ('duration · .spin i · transition · 0.08s', 'pull to refresh: each tick appears as the finger pulls, near instant'),
    ('duration · .sbi · transition · 0.15s', 'the iPad and Mac side bar row’s hover highlight'),
    ('duration · .w.pulse · animation · 0.9s', 'Song Clock’s own word pulse, on the beat (the audit: keep)'),
    ('ease · .w.pulse · animation · ease-out', 'the same pulse’s own easing'),
    ('duration · .meter i · transition · 0.1s', 'the microphone meter follows the level, near instant'),
    ('duration · .ring .arc · transition · 0.3s', 'the session ring turning green at its peak (a colour cue)'),
    ('duration · .cuebox · transition · 0.3s', 'the cue under a row fading in after it unfolds'),
    ('duration · .pt · transition · 0.35s', 'a pattern step’s own length (its curve is the knob’s, Q54)'),
    ('duration · .pt · transition · 0.35s', 'the step lifting (its shadow is the kit’s lifted one, Q54)'),
]

KNOWN_JS = [
    ('details.js · cubic-bezier(.4, 0, .6, 1)', 'list edits: a removed row leaving (the audit’s change row, not yet built)'),
    ('details.js · cubic-bezier(.3, .7, .3, 1)', 'the Progress chart’s line drawing in'),
]

# Q54 times and keyword easings in code (ms: and duration: with a number, and easing: 'ease-out' and the like). Named:
# MOTION.dur(spring), MOTION.ms('fade'), MOTION.reducedMs(), MOTION.CUE, ZOOM and LAUNCH, MOTION.EASE, a spring. Numbers
# under 10 are proportions (d * 0.3), not times.
KNOWN_JS_TIMES = [
    ('application.js · ms: 24', 'not a time: the ladder’s notes list (ms is their key)'),
    ('details.js · ms: 620', 'the Progress chart’s line drawing in'),
    ('details.js · ms: 220', 'a sheet whose content changes in place: its content fading over'),
    ('details.js · ms: 500', '“Last backed up” changing colour softly'),
    ('onepage.js · ms: 1350', 'the step-done flash: blue to green, then gone (a cue)'),
    ('onepage.js · duration: 1400', 'the pull-past-the-bottom message: shown, then faded (a cue)'),
    ('onepage.js · duration: 300', 'the same message when the pull is short'),
    ('track.js · ms: 460', 'the track’s line box giving a small pulse as the line changes'),
    ('ui.js · ms: 4500', 'not a motion: how long a toast with a button stays'),
]
KNOWN_JS_EASE = [
    ('application.js · ease-out', 'Application’s Reduce Motion flash (Q52 cue): a keyframed flash'),
    ('application.js · ease-out', 'Application’s step-done flash: a keyframed flash'),
    ('details.js · ease-out', 'a sheet whose content changes in place: its content fading over'),
    ('details.js · ease-out', '“Last backed up” changing colour softly'),
    ('onepage.js · ease-out', 'the one-page session’s Reduce Motion flash (Q52 cue): a keyframed flash'),
    ('onepage.js · ease-out', 'the step-done flash: a keyframed flash'),
    ('onepage.js · ease-out', 'the pull-past-the-bottom message: a keyframed fade'),
    ('track.js · ease-out', 'the track’s line box pulse: a keyframed pulse'),
]

# Q54 shadows. Rings and strokes drawn with a shadow (inset, or no offset and no blur) are exempt, like small graphic
# corners. The parts kit's three (--shadow-lifted, --shadow-floating, --shadow-glow) are the names.
KNOWN_SHADOW = [
    ('.cta', 'the capsule’s own glass depth: rim light, hairline and its drop'),
    ('.cta.ink', 'the black or white capsule’s drop, as the glass ones'),
    ('.fw.dragging', 'the floating window lifted by a finger: its glass layers (Q26)'),
    ('.sckknob', 'the session clock’s knob, as an iOS slider knob'),
    ('#splash .sp-icon', 'the app icon’s red glow on the launch screen (the app’s signature)'),
    ('#splash i', 'the icon’s sound-wave bars, drawn as on the icon'),
    ('.zm-shade', 'the card zoom’s lifted page (the app’s own zoom)'),
    ('.zm-page', 'the card zoom’s page while it moves'),
    ('.cvthumb2', 'the coach video scrubber’s frame preview, over video'),
    ('.trklv .pk-seg-ind', 'the track level control’s loop ring and its knob’s drop'),
    ('.trkpadpp', 'the track pad’s play button over the waveform'),
    ('.tkplay', 'a take’s small play button over its row'),
    ('.pplay', 'the pattern player’s play button, as the track pad’s'),
]

# Q54 colours written as hex in rules (masks are exempt: only their alpha counts). #fff on a coloured fill is
# var(--on-accent), the slider knob var(--pk-knob).
KNOWN_COLOUR = [
    ('.fw .fwvblack · background · #000', 'video: black whatever the mode'),
    ('.zm-dim · background · #000', 'the push dim is black in both modes (kit part 10’s 10%)'),
    ('#cv · background · #000', 'video: black whatever the mode'),
    ('.cv-slot · background · #000', 'video: black whatever the mode'),
    ('.cv-still · background · #000', 'video: black whatever the mode'),
    ('.cvfs · color · #fff', 'over video: white whatever the mode'),
    ('.cvthumb2 · background · #fff', 'the scrubber’s frame preview edge, over video'),
    ('.cvthumb · color · #fff', 'over a video thumbnail: white whatever the mode'),
    ('.cvthumb · background · #48484a', 'an empty video thumbnail’s dark gradient'),
    ('.cvthumb · background · #1c1c1e', 'the same gradient’s end'),
    (".fw[data-kind='video'] · background · #000", 'video: black whatever the mode'),
    ('.fw .fwvc button · color · #fff', 'over video: white whatever the mode'),
    ('.fw .fwvc .fwbtn · color · #fff', 'over video: white whatever the mode'),
    ('.fw .fwvlv button.on · color · #000', 'the video level picker: black on its white pill, over video'),
    ('.fw .fwvlv button.on::before · background · #fff', 'the same white pill'),
    (".fw[data-kind='rectrack'] · background · #d70015", 'the recording window’s own red (Q16)'),
    ('.mpsheet .mpimg · background · #fff', 'a sheet music page stays paper white in dark mode'),
]

# Q40's two fixes
GLASS_FIX = []  # Q40's two glass fixes (.phbar, .pmenu) left with their parts at Q41: the parts kit's slider and menus
PRESS_FIX = []  # Q40's six solid presses left with their :active rules at Q53: every button presses through the kit

keys = lambda lst: [k for k, _ in lst]


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
    # Q52 and the kit's own named timings (--dur-reduced, --dur-leave, --ease-accel …), from its defaults block
    kcss = open(os.path.join(ROOT, 'css', 'parts-kit.css'), encoding='utf-8').read()
    ktok = set(re.findall(r'^\s*--((?:ease|dur)-[a-z0-9-]+):', kcss, re.M))
    defined = set(got) | {f'{a}-{s}' for s in springs for a in ('ease', 'dur')} | ktok
    used = set(re.findall(r'var\(--((?:r|ease|dur)-[a-z0-9-]+|press)\b', css))
    ok(used <= defined, f'every named value used is defined, in app.css, as a parts kit spring or a kit timing ({used - defined})')
    _, names = js_curves()
    kaccel = re.search(r'--ease-accel:\s*([^;]+);', kcss).group(1)
    ok(set(names) == {'pop', 'knob', 'out', 'accel'} and all(same_curve(names[k], NAMED['ease-' + k]) for k in ('pop', 'knob', 'out'))
       and same_curve(names['accel'], kaccel), f'MOTION.EASE holds the same three easings for code, and the kit’s accel (Q54) ({names})')
    pg = t.page(b)
    vals = pg.evaluate("ks=>ks.map(k=>getComputedStyle(document.documentElement).getPropertyValue('--'+k).trim())", list(NAMED))
    ok(dict(zip(NAMED, vals)) == NAMED, f'the names resolve in the page ({dict(zip(NAMED, vals))})')
    ok(pg.evaluate("MOTION.EASE.out") == "cubic-bezier(.2,.8,.2,1)", 'MOTION.EASE.out is reachable from code')
    # Q54 MOTION.ms reads the named fixed timings from the page, so code and stylesheet can't drift apart
    got = pg.evaluate("['quick','fade','appear','leave','close'].map(n=>MOTION.ms(n))")
    ok(got == [120, 200, 250, 350, 170], f'MOTION.ms gives the named timings: quick, fade, appear, leave, close ({got})')
    pg.context.close()


def css_strays(b, t):
    ok = t.ok
    css = open(CSS, encoding='utf-8').read()
    its, shadows_all = items(css)
    shadow_vals = collections.Counter(shadows_all)
    stray = [i for i in its if not i[5]]
    new, gone = compare([key(i) for i in stray], keys(KNOWN))
    lines = collections.defaultdict(list)
    for i in stray:
        lines[key(i)].append(i[4])
    ok(not new, 'no new stray values in app.css' + ('' if not new else ': use a named value, or add one on purpose (MAINTAINING › Value set): '
       + '; '.join(f'line {lines[k][0]}: {k}' for k in new[:8]) + (f' … and {len(new) - 8} more' if len(new) > 8 else '')))
    ok(not gone, 'every known stray is still in app.css' + ('' if not gone else ': the list can shrink, so take these off KNOWN in '
       'tests/test_values.py: ' + '; '.join(gone[:8]) + (f' … and {len(gone) - 8} more' if len(gone) > 8 else '')))
    ok(all(r.strip() for _, r in KNOWN + KNOWN_SHADOW + KNOWN_COLOUR), 'every value left has its reason')
    # Q54 shadows: the kit's three names, rings and strokes, or a known one with its reason
    sh = shadows(css)
    new, gone = compare([x[0] for x in sh], keys(KNOWN_SHADOW))
    at = {x[0]: x[2] for x in sh}
    ok(not new, 'no new shadows written out in app.css' + ('' if not new else ': use the kit’s --shadow-lifted, '
       '--shadow-floating or --shadow-glow: ' + '; '.join(f'line {at[k]}: {k}' for k in new[:8])))
    ok(not gone, 'every known shadow is still in app.css' + ('' if not gone else ': the list can shrink, so take these off '
       'KNOWN_SHADOW in tests/test_values.py: ' + '; '.join(gone[:8])))
    # Q54 hex colours in rules: tokens (--on-accent, --pk-knob, --fg …), or a known one with its reason
    cl = colours(css)
    new, gone = compare([x[0] for x in cl], keys(KNOWN_COLOUR))
    at = {x[0]: x[1] for x in cl}
    ok(not new, 'no new hex colours in app.css rules' + ('' if not new else ': use a colour token: '
       + '; '.join(f'line {at[k]}: {k}' for k in new[:8])))
    ok(not gone, 'every known hex colour is still in app.css' + ('' if not gone else ': the list can shrink, so take these '
       'off KNOWN_COLOUR in tests/test_values.py: ' + '; '.join(gone[:8])))
    use = collections.Counter(i[0] for i in its if i[5])
    left = collections.Counter(k.split(' · ')[0] for k in keys(KNOWN))
    print(f'  ····  named uses: corners {use["corner"]}, presses {use["press"]}, easings {use["ease"]}, '
          f'durations {use["duration"]}')
    print(f'  ····  known strays: corners {left["corner"]}, presses {left["press"]}, easings {left["ease"]}, '
          f'durations {left["duration"]}, shadows {len(KNOWN_SHADOW)}, hex colours {len(KNOWN_COLOUR)}, curves in code '
          f'{len(KNOWN_JS)}, times in code {len(KNOWN_JS_TIMES)}, easings in code {len(KNOWN_JS_EASE)}')
    print(f'  ····  shadows written out (rings and strokes included): {len(shadows_all)}, {len(shadow_vals)} different')


def js_strays(b, t):
    ok = t.ok
    found, _ = js_curves()
    new, gone = compare(found, keys(KNOWN_JS))
    ok(not new, 'no new hand-written curves in js/' + (f': use a MOTION spring or MOTION.EASE ({new})' if new else ''))
    ok(not gone, 'every known curve in code is still there' + (f': the list can shrink, so take these off KNOWN_JS in tests/test_values.py ({gone})' if gone else ''))
    # Q54 times and keyword easings in code
    times, eases = js_times()
    new, gone = compare(times, keys(KNOWN_JS_TIMES))
    ok(not new, 'no new hand-set times in js/' + (f": use a MOTION spring, MOTION.ms('fade') and the like, MOTION.reducedMs(), "
       f'or a named table in js/motion.js ({new})' if new else ''))
    ok(not gone, 'every known time in code is still there' + (f': the list can shrink, so take these off KNOWN_JS_TIMES ({gone})' if gone else ''))
    new, gone = compare(eases, keys(KNOWN_JS_EASE))
    ok(not new, 'no new keyword easings in js/' + (f': use MOTION.EASE or a spring ({new})' if new else ''))
    ok(not gone, 'every known keyword easing in code is still there' + (f': the list can shrink, so take these off KNOWN_JS_EASE ({gone})' if gone else ''))
    ok(all(r.strip() for _, r in KNOWN_JS + KNOWN_JS_TIMES + KNOWN_JS_EASE), 'every value left in code has its reason')


def guard(b, t):
    """The guard catches what it should, on copies (the real files aren't touched)."""
    ok = t.ok
    css = open(CSS, encoding='utf-8').read()
    K = keys(KNOWN)
    extra = ('\n.vtest:active { transform: scale(0.91); border-radius: 11px; '
             'transition: opacity 0.3s cubic-bezier(0.1, 0.2, 0.3, 1); }\n')
    its, _ = items(css + extra)
    new, gone = compare([key(i) for i in its if not i[5]], K)
    kinds = sorted(k.split(' · ')[0] for k in new)
    ok(kinds == ['corner', 'duration', 'ease', 'press'] and not gone,
       f'a new corner, press, curve and duration are each caught ({new})')
    named_extra = ('\n.vtest:active { transform: scale(var(--press)); border-radius: var(--r-card); '
                   'transition: opacity var(--dur-fade) var(--ease-out), transform 2s ease-in-out infinite; '
                   'border-radius: 4px 999px 50%; }\n')
    its, _ = items(css + named_extra)
    new, _ = compare([key(i) for i in its if not i[5]], K)
    ok(not new, f'named values, small graphic corners, capsules, circles and slow loops pass ({new})')
    if K:
        k = K[0].split(' · ')
        its, _ = items(css)
        line = next(i[4] for i in its if key(i) == K[0])
        src = css.splitlines(True)
        src[line - 1] = src[line - 1].replace(k[3], 'var(--r-card)' if k[0] == 'corner' else 'var(--press)' if k[0] == 'press'
                                              else 'var(--ease-out)' if k[0] == 'ease' else 'var(--dur-fade)', 1)
        its, _ = items(''.join(src))
        new, gone = compare([key(i) for i in its if not i[5]], K)
        ok(gone == [K[0]] and not new, f'a stray taken away is noticed, so the list must shrink ({gone})')
    # Q54 shadows and colours
    look = ('\n.vtest { box-shadow: 0 5px 9px rgba(0, 0, 0, 0.2); color: #fff; }\n'
            '.vtest2 { box-shadow: var(--shadow-lifted), inset 0 0 0 1px var(--sep), 0 0 0 2px var(--accent); '
            'color: var(--on-accent); mask-image: linear-gradient(#000, transparent); }\n')
    new, _ = compare([x[0] for x in shadows(css + look)], keys(KNOWN_SHADOW))
    ok(new == ['.vtest'], f'a new shadow is caught; the kit’s names, rings and strokes pass ({new})')
    new, _ = compare([x[0] for x in colours(css + look)], keys(KNOWN_COLOUR))
    ok(new == ['.vtest · color · #fff'], f'a new hex colour is caught; tokens and masks pass ({new})')
    # code: a new curve, time and keyword easing; named ones pass
    files = _js_files()
    found, _ = js_curves(files + [('new.js', "el.animate(f, {easing: 'cubic-bezier(.1,.2,.3,1)'})")])
    new, _ = compare(found, keys(KNOWN_JS))
    ok(new == ['new.js · cubic-bezier(.1, .2, .3, 1)'], f'a new curve in code is caught ({new})')
    code = ("MOTION.animate(el, f, { ms: 300, easing: 'ease-out' }); el.animate(f, { duration: 180 * S, easing: 'linear' });\n"
            "MOTION.animate(el, f, { ms: MOTION.ms('fade'), delay: 90, easing: MOTION.EASE.out }); MOTION.animate(el, f, { ms: d * 0.3 });\n"
            "el.animate(f, { duration: MOTION.reducedMs() * MOTION.speed() }); x = a.duration ? a.duration : 300; // { ms: 999 }\n")
    times, eases = js_times(files + [('new.js', code)])
    new, _ = compare(times, keys(KNOWN_JS_TIMES))
    ok(sorted(new) == ['new.js · duration: 180', 'new.js · ms: 300'], f'a new time in code is caught; named ones, delays, '
       f'proportions, a media length and comments pass ({new})')
    new, _ = compare(eases, keys(KNOWN_JS_EASE))
    ok(sorted(new) == ['new.js · ease-out', 'new.js · linear'], f'a new keyword easing in code is caught ({new})')
    src = dict(files)['zoom.js'].replace("{ ms: MOTION.ZOOM.hand }", "{ ms: 150 }", 1)
    times, _ = js_times([(n, src if n == 'zoom.js' else c) for n, c in files])
    new, _ = compare(times, keys(KNOWN_JS_TIMES))
    ok(new == ['zoom.js · ms: 150'], f'a named time written back as a number is caught ({new})')


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
