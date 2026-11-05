"""Make the score reader's test prints (Q57): made-up tunes engraved as vector PDFs the way UG's own Download PDF
looks (MuseScore-style): music symbols as text in the Leland font (SMuFL), tab numbers, words, title and marks as text,
staff lines, bar lines, stems, ledger lines and brackets as stroked lines, beams and the multi-bar rest as filled
shapes, and ties as filled curves. Pages are the size UG's file uses (9921 x 14031 units), so the Recon's PyMuPDF
test reader can read them too and its numbers can be compared with the app's.

    python3 tools/make_score_fixtures.py     writes tests/fixtures/melody/score-*.pdf and score.json

Needs PyMuPDF and the DejaVu fonts (for the words and marks). Leland is in tools/fonts/ with its OFL licence
(tools/fonts/Leland-OFL.txt). Its output is committed, so the tests need none of these. Every tune, word and title here
is made up: no real music.

score.json holds what each print should read as, worked out here from the tune itself (not from any reader), in the
tests' bar format: "n:eighths|notes (name/eighths)|rests|flags".
"""
import json, os, re
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'tests', 'fixtures', 'melody')
LELAND = os.path.join(HERE, 'fonts', 'Leland.otf')
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SANS_I = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'
SANS_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

PW, PH = 9921, 14031          # UG's page, in PDF units
SP, TSP = 82.7, 124.0         # notation and tab line spacing
X0, X1 = 600, 9321            # the staff's ends
MUS = 4 * SP                  # the music font's size: one em is four staff spaces (SMuFL)
TUNE = [64, 59, 55, 50, 45, 40]
NAMES = 'CDEFGAB'
STEP = [0, 2, 4, 5, 7, 9, 11]
SHARPS, FLATS = 'FCGDAEB', 'BEADGCF'
KEY_SHARP_IDX = [38, 35, 39, 36, 33, 37, 34]   # F5 C5 G5 D5 A4 E5 B4 on a treble staff
KEY_FLAT_IDX = [34, 37, 33, 36, 32, 35, 31]    # B4 E5 A4 D5 G4 C5 F4
HEAD = {8: 0xE0A2, 4: 0xE0A3}                  # whole, half; everything shorter is black
REST = {8: 0xE4E3, 4: 0xE4E4, 2: 0xE4E5, 1: 0xE4E6, 0.5: 0xE4E7, 0.25: 0xE4E8}
BASE = [8, 4, 2, 1, 0.5, 0.25]


def parse_pitch(p):
    m = re.fullmatch(r'([A-G])(#|b|n)?(-?\d)', p)
    name, acc, octv = m.group(1), m.group(2) or '', int(m.group(3))
    alter = {'#': 1, 'b': -1}.get(acc, 0)
    idx = octv * 7 + NAMES.index(name)
    return idx, alter, 12 * (octv + 1) + STEP[NAMES.index(name)] + alter


def nm(m):
    return ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][m % 12] + str(m // 12 - 1)


def base_of(d):
    """written duration (eighths) -> (base, dots)"""
    for b in BASE:
        for dots, k in ((0, 1), (1, 1.5), (2, 1.75)):
            if abs(b * k - d) < 1e-6: return b, dots
    raise ValueError(d)


def parse_bar(s):
    """A bar of tokens. Note: PITCH:EIGHTHS with ~ (tie on), =syl (a word; end it with - when the word goes on),
    chords as TOP+LOWER:d, [ ] beam groups, t3( ) a triplet, g:PITCH a grace note before the next note; r:d a rest;
    m:N a multi-bar rest. Bar marks: T3/4 (a time signature here), Q120 (a tempo mark), E1 (a first ending), :| (a
    repeat sign at its end), C (a coda sign)."""
    bar = {'ev': [], 'time': None, 'tempo': None, 'ending': None, 'repeat': False, 'coda': False}
    beam, tup, grace = None, None, None
    for tok in s.split():
        if tok.startswith('T') and '/' in tok: bar['time'] = tuple(int(v) for v in tok[1:].split('/')); continue
        if re.fullmatch(r'Q\d+', tok): bar['tempo'] = int(tok[1:]); continue
        if re.fullmatch(r'E\d', tok): bar['ending'] = int(tok[1:]); continue
        if tok == ':|': bar['repeat'] = True; continue
        if tok == 'C': bar['coda'] = True; continue
        if tok == 't3(': tup = len(bar['ev']); continue
        if tok == ')': bar['ev'][-1]['tup_end'] = True; bar['ev'][tup]['tup_start'] = True; tup = None; continue
        if tok.startswith('g:'): grace = tok[2:]; continue
        if tok.startswith('m:'): bar['ev'].append({'t': 'M', 'n': int(tok[2:])}); continue
        start = tok.startswith('[')
        tok = tok.lstrip('[')
        end = tok.endswith(']')
        tok = tok.rstrip(']')
        syl = None
        if '=' in tok: tok, syl = tok.split('=', 1)
        tie = tok.endswith('~'); tok = tok.rstrip('~')
        what, d = tok.split(':')
        d = float(d)
        if what == 'r': ev = {'t': 'R', 'd': d}
        else: ev = {'t': 'N', 'p': what.split('+'), 'd': d, 'tie': tie, 'syl': syl}
        if tup is not None: ev['tup'] = True
        if grace: ev['grace'] = grace; grace = None
        if start: beam = []
        if beam is not None: beam.append(ev); ev['beam'] = beam
        if end: beam = None
        bar['ev'].append(ev)
    return bar


class Page:
    def __init__(self, doc):
        self.p = doc.new_page(width=PW, height=PH)
        self.fonts = set()

    def font(self, name):
        if name not in self.fonts:  # only the fonts a page uses, so each one is cut down to what it needs
            self.p.insert_font(fontname=name, fontfile={'lel': LELAND, 'sans': SANS, 'sansi': SANS_I, 'sansb': SANS_B}[name])
            self.fonts.add(name)
        return name

    def line(self, a, b, w=8):
        self.p.draw_line(a, b, color=(0, 0, 0), width=w)

    def sym(self, code, x, y, size=MUS):
        self.p.insert_text((x, y), chr(code), fontname=self.font('lel'), fontsize=size)

    def text(self, s, x, y, size, font='sans', centre=False):
        if centre:
            w = pymupdf.Font(fontfile={'sans': SANS, 'sansi': SANS_I, 'sansb': SANS_B}[font]).text_length(s, fontsize=size)
            x -= w / 2
        self.p.insert_text((x, y), s, fontname=self.font(font), fontsize=size)

    def fill(self, pts):
        self.p.draw_polyline(pts, color=None, fill=(0, 0, 0), closePath=True)

    def tie(self, xa, xb, y, up):
        k = -1 if up else 1
        sh = self.p.new_shape()
        sh.draw_bezier((xa, y), (xa + (xb - xa) * 0.25, y + k * 0.8 * SP), (xb - (xb - xa) * 0.25, y + k * 0.8 * SP), (xb, y))
        sh.draw_bezier((xb, y), (xb - (xb - xa) * 0.25, y + k * 0.6 * SP), (xa + (xb - xa) * 0.25, y + k * 0.6 * SP), (xa, y))
        sh.finish(color=None, fill=(0, 0, 0), closePath=True)
        sh.commit()


def engrave(spec):
    """Draw one print and work out what it should read as."""
    doc = pymupdf.open()
    lines = [[parse_bar(b) for b in L] for L in spec['lines']]
    key, time, tab = spec['key'], tuple(spec['time']), spec.get('tab', True)
    keyset = set(SHARPS[:key]) if key > 0 else set(FLATS[:-key]) if key < 0 else set()
    sung_off = -12 if tab else 0
    pg = Page(doc)
    pg.text(spec['title'], PW / 2, 900, 600, 'sans', True)
    pg.text(spec['artist'], PW / 2, 1400, 350, 'sans', True)
    y = 2600
    expect, tick_bar, barno, words = [], [], 1, []
    cur_time = time
    ties_open = None
    for li, L in enumerate(lines):
        staves = []  # [(kind, top)]
        top = y
        if spec.get('parts'):
            staves.append(('other', top)); top += 4 * SP + 7 * SP
        vocal = top
        staves.append(('vocal', vocal))
        tabtop = vocal + 4 * SP + 6 * SP
        if tab: staves.append(('tab', tabtop))
        bottom = tabtop + 5 * TSP if tab else vocal + 4 * SP
        for kind, t0 in staves:
            n, gap = (6, TSP) if kind == 'tab' else (5, SP)
            for i in range(n): pg.line((X0, t0 + i * gap), (X1, t0 + i * gap), 8)
        if len(staves) > 1: pg.line((X0, staves[0][1]), (X0, bottom), 10)  # the system's left line
        nl = [vocal + i * SP for i in range(5)]
        tl = [tabtop + i * TSP for i in range(6)]
        # the head of the line: clef, key, the first line's time signature
        for kind, t0 in staves:
            if kind == 'tab': pg.sym(0xE06D, X0 + 0.6 * SP, t0 + 2.5 * TSP); continue
            pg.sym(0xE050, X0 + 0.6 * SP, t0 + 3 * SP)
            for k in range(abs(key)):
                idx = (KEY_SHARP_IDX if key > 0 else KEY_FLAT_IDX)[k]
                pg.sym(0xE262 if key > 0 else 0xE260, X0 + 3.4 * SP + k * 1.0 * SP, t0 + 4 * SP - (idx - 30) * SP / 2)
        hx = X0 + 3.4 * SP + abs(key) * SP + 0.6 * SP
        if li == 0:
            for kind, t0 in staves:
                if kind == 'tab': continue
                pg.sym(0xE080 + time[0], hx, t0 + 1 * SP); pg.sym(0xE080 + time[1], hx, t0 + 3 * SP)
            hx += 2.6 * SP
        hx += 1.4 * SP
        if li > 0: pg.text(str(barno), X0, nl[0] - 1.6 * SP, 150, 'sansi')
        # bar widths: by how many things are in each
        weights = [max(2, sum(max(1.0, 1.1 * len((e.get('syl') or '').rstrip('-')) + 2) for e in B['ev'] if e['t'] != 'M') + (1.5 if B['time'] else 0)) + 1 for B in L]
        avail = X1 - hx
        bx = hx
        for B, wgt in zip(L, weights):
            bw = avail * wgt / sum(weights)
            a, b = bx, bx + bw
            bx = b
            for kind, t0 in staves:
                n, gap = (6, TSP) if kind == 'tab' else (5, SP)
                pg.line((b, t0), (b, t0 + (n - 1) * gap), 10)
                if B['repeat'] and kind != 'tab':
                    pg.line((b - 0.4 * SP, t0), (b - 0.4 * SP, t0 + 4 * SP), 40)
                    pg.sym(0xE044, b - 1.3 * SP, t0 + 1.5 * SP); pg.sym(0xE044, b - 1.3 * SP, t0 + 2.5 * SP)
            if B['ending']:
                pg.line((a + 0.3 * SP, nl[0] - 3.2 * SP), (b - 0.3 * SP, nl[0] - 3.2 * SP), 10)
                pg.line((a + 0.3 * SP, nl[0] - 3.2 * SP), (a + 0.3 * SP, nl[0] - 2.2 * SP), 10)
                pg.text('%d.' % B['ending'], a + 0.7 * SP, nl[0] - 2.4 * SP, 170, 'sans')
            if B['coda']: pg.sym(0xE048, b - 2 * SP, nl[0] - 2.5 * SP, MUS * 0.7)
            x = a + 1.2 * SP
            if B['time']:
                cur_time = B['time']
                for kind, t0 in staves:
                    if kind == 'tab': continue
                    pg.sym(0xE080 + cur_time[0], x, t0 + 1 * SP); pg.sym(0xE080 + cur_time[1], x, t0 + 3 * SP)
                x += 2.4 * SP
            if B['tempo']:
                tx = a + (0.6 * SP if B is not L[0] or li else 0)
                pg.sym(0xE1D5, tx, nl[0] - 3.4 * SP, MUS * 0.55)
                pg.text('= %d' % B['tempo'], tx + 0.9 * SP, nl[0] - 3.4 * SP, 220, 'sans')
            target = cur_time[0] * 8 / cur_time[1]
            evs = [e for e in B['ev'] if e['t'] != 'M']
            ew = [max(1.0, 1.1 * len((e.get('syl') or '').rstrip('-')) + 2) for e in evs]
            unit = (b - x - 0.8 * SP) / max(1, sum(ew))
            for e, w_ in zip(evs, ew): e['_step'] = unit * w_
            # the other part (top staff): a held chord in every bar
            if spec.get('parts'):
                o = staves[0][1]
                for i, (p1) in enumerate(['E5', 'C5']):
                    idx = parse_pitch(p1)[0]
                    pg.sym(0xE0A2, a + 1.5 * SP, o + 4 * SP - (idx - 30) * SP / 2)
            # the expected bar
            exp_n = barno
            multi = next((e for e in B['ev'] if e['t'] == 'M'), None)
            if multi:
                pg.fill([(a + 1.2 * SP, nl[2] - 0.5 * SP), (b - 1.2 * SP, nl[2] - 0.5 * SP), (b - 1.2 * SP, nl[2] + 0.5 * SP), (a + 1.2 * SP, nl[2] + 0.5 * SP)])
                pg.line((a + 1.2 * SP, nl[1] + 0.2 * SP), (a + 1.2 * SP, nl[3] - 0.2 * SP), 10)
                pg.line((b - 1.2 * SP, nl[1] + 0.2 * SP), (b - 1.2 * SP, nl[3] - 0.2 * SP), 10)
                ds = str(multi['n'])
                for k, ch in enumerate(ds): pg.sym(0xE080 + int(ch), (a + b) / 2 - len(ds) * 0.9 * SP + k * 1.8 * SP, nl[0] - 1.2 * SP)
                expect.append({'n': barno, 'len': multi['n'] * target, 'notes': [], 'rests': [multi['n'] * target], 'f': []})
                barno += multi['n']
                continue
            row = {'n': barno, 'len': target, 'notes': [], 'rests': [], 'f': ['repeat'] if B['repeat'] else []}
            expect.append(row)
            carried = {}
            heads = []  # drawn notes, for beams, ties, tuplets, lyrics
            only_whole_rest = len(evs) == 1 and evs[0]['t'] == 'R' and evs[0]['d'] == 8
            for e in evs:
                step = e['_step']
                ex = x + min(step * 0.3, 1.5 * SP)
                k = 2 / 3 if e.get('tup') else 1
                if e['t'] == 'R':
                    d = target if only_whole_rest else e['d']
                    base, dots = base_of(e['d'])
                    rx = (a + b) / 2 - 0.6 * SP if only_whole_rest else ex
                    ry = nl[1] if base == 8 else nl[2]
                    pg.sym(REST[base], rx, ry)
                    if dots: pg.sym(0xE1E7, rx + 1.6 * SP, nl[2] - 0.5 * SP)
                    row['rests'].append(round(d * k, 3))
                    e['x'] = rx
                    x += step
                    continue
                base, dots = base_of(e['d'])
                ps = [parse_pitch(p) for p in e['p']]
                idx, alter, midi = ps[0]
                up = idx < 34
                hw = 1.49 * SP if base == 8 else 1.3 * SP
                if e.get('grace'):
                    gi, ga, gm = parse_pitch(e['grace'])
                    gx, gy = ex - 2.2 * SP, nl[4] - (gi - 30) * SP / 2
                    pg.sym(0xE0A4, gx, gy, MUS * 0.6)
                    pg.line((gx + 0.75 * SP, gy), (gx + 0.75 * SP, gy - 2.4 * SP), 6)
                    pg.sym(0xE240, gx + 0.72 * SP, gy - 2.4 * SP, MUS * 0.6)
                    pg.line((gx + 0.2 * SP, gy - 0.6 * SP), (gx + 1.4 * SP, gy - 1.6 * SP), 6)
                    if tab:
                        s, fret = fret_of(gm + sung_off)
                        pg.text(str(fret), gx + 0.2 * SP, tl[s] + 0.35 * 110, 110, 'sans')
                ys = []
                for (pi, pa, pm) in ps:
                    hy = nl[4] - (pi - 30) * SP / 2
                    ys.append(hy)
                    nmn = NAMES[pi % 7]
                    want = pa
                    have = carried.get((nmn, pi // 7), (1 if nmn in keyset and key > 0 else -1 if nmn in keyset else 0))
                    if want != have and not (ties_open and pm == ties_open['m']):
                        pg.sym({1: 0xE262, -1: 0xE260, 0: 0xE261}[want], ex - 1.2 * SP, hy)
                    carried[(nmn, pi // 7)] = want
                    pg.sym(HEAD.get(base, 0xE0A4), ex, hy)
                    for li2 in ledger(pi): pg.line((ex - 0.4 * SP, nl[4] - (li2 - 30) * SP / 2), (ex + hw + 0.4 * SP, nl[4] - (li2 - 30) * SP / 2), 9)
                    if dots: pg.sym(0xE1E7, ex + hw + 0.4 * SP, hy - (SP / 2 if pi % 2 == 0 else 0))
                    if tab and not (ties_open and pm == ties_open['m'] and pi == idx):
                        s, fret = fret_of(pm + sung_off)
                        txt = str(fret)
                        pg.text(txt, ex + hw / 2 - len(txt) * 0.3 * 150, tl[s] + 0.35 * 150, 150, 'sans')
                hy = ys[0]
                # sung pitch, tie into the previous note
                sung = midi + sung_off
                if ties_open and ties_open['m'] == midi:
                    ties_open['row']['notes'][ties_open['i']][1] += round(e['d'] * k, 3)
                    pg.tie(ties_open['x'] + 0.9 * SP, ex + 0.4 * SP, ties_open['y'] + (0.7 * SP if ties_open['up'] else -0.7 * SP), not ties_open['up'])
                    nref = None
                else:
                    row['notes'].append([nm(sung), round(e['d'] * k, 3)])
                    nref = (row, len(row['notes']) - 1)
                    words.append(e['syl'])
                ties_open = None
                if e['tie'] and nref: ties_open = {'m': midi, 'row': nref[0], 'i': nref[1], 'x': ex, 'y': hy, 'up': up}
                elif e['tie']: pass
                e.update({'x': ex, 'y': hy, 'ylo': max(ys), 'yhi': min(ys), 'up': up, 'hw': hw, 'base': base})
                heads.append(e)
                if e['syl']:
                    s = e['syl']
                    tw = pymupdf.Font(fontfile=SANS).text_length(s.rstrip('-'), fontsize=200)
                    pg.text(s.rstrip('-'), ex + hw / 2, nl[4] + 3.6 * SP, 200, 'sans', True)
                    e['sx0'], e['sx1'] = ex + hw / 2 - tw / 2, ex + hw / 2 + tw / 2
                    if s.endswith('-'): e['dash'] = True
                x += step
            # stems, flags, beams
            for e in heads:
                if e['base'] >= 8: continue
                if e.get('beam'): continue
                sx = e['x'] + e['hw'] - 0.06 * SP if e['up'] else e['x'] + 0.06 * SP
                y0 = e['ylo'] if e['up'] else e['yhi']
                y1 = (e['yhi'] - 3.5 * SP) if e['up'] else (e['ylo'] + 3.5 * SP)
                pg.line((sx, y0), (sx, y1), 10)
                nb = {1: 1, 0.5: 2, 0.25: 3}.get(e['base'], 0)
                if nb: pg.sym((0xE240, 0xE242, 0xE244)[nb - 1] + (0 if e['up'] else 1), sx - 0.05 * SP, y1)
            groups = []
            for e in heads:
                if e.get('beam') and (not groups or groups[-1] is not e['beam']): groups.append(e['beam'])
            for g in groups:
                g = [e for e in g if 'x' in e]
                up = sum(e['y'] for e in g) / len(g) > nl[2]
                slope = 0.12 * SP if spec.get('slant') and len(g) > 1 else 0
                ends = []
                for i, e in enumerate(g):
                    sx = e['x'] + e['hw'] - 0.06 * SP if up else e['x'] + 0.06 * SP
                    base = (min(f['yhi'] for f in g) - 3.5 * SP) if up else (max(f['ylo'] for f in g) + 3.5 * SP)
                    ye = base - slope * i * (1 if up else -1)
                    pg.line((sx, e['ylo'] if up else e['yhi']), (sx, ye), 10)
                    ends.append((sx, ye, {1: 1, 0.5: 2, 0.25: 3}[e['base']]))
                for lev in range(3):
                    off = lev * 0.75 * SP * (1 if up else -1)
                    for i, (sx, ye, nb) in enumerate(ends):
                        if nb <= lev: continue
                        nx = ends[i + 1] if i + 1 < len(ends) else None
                        if nx and nx[2] > lev:
                            xa, ya, xb, yb = sx - 0.05 * SP, ye + off, nx[0] + 0.05 * SP, nx[1] + off
                        elif not (i and ends[i - 1][2] > lev):
                            if nx: xa, ya, xb, yb = sx - 0.05 * SP, ye + off, sx + 1.2 * SP, ye + off - slope * 1.2 / max(1, step / SP)
                            else: xa, ya, xb, yb = sx - 1.2 * SP, ye + off, sx + 0.05 * SP, ye + off
                        else: continue
                        t = 0.5 * SP * (1 if up else -1)
                        pg.fill([(xa, ya), (xb, yb), (xb, yb + t), (xa, ya + t)])
            # a triplet: its number and bracket above
            for i, e in enumerate(B['ev']):
                if not e.get('tup_start'): continue
                j = next(k for k in range(i, len(B['ev'])) if B['ev'][k].get('tup_end'))
                g = [B['ev'][k] for k in range(i, j + 1)]
                xa, xb = g[0]['x'] - 0.2 * SP, g[-1]['x'] + 1.5 * SP
                ty = min(min(f.get('yhi', nl[2]) for f in g) - 5.2 * SP, nl[0] - 1.6 * SP)
                cx = (xa + xb) / 2
                pg.sym(0xE883, cx - 0.5 * SP, ty + 0.5 * SP, MUS * 0.75)
                pg.line((xa, ty), (cx - 0.9 * SP, ty), 8); pg.line((cx + 0.9 * SP, ty), (xb, ty), 8)
                pg.line((xa, ty), (xa, ty + 0.6 * SP), 8); pg.line((xb, ty), (xb, ty + 0.6 * SP), 8)
            # word dashes
            for e, f in zip(heads, heads[1:]):
                if e.get('dash') and f.get('sx0'): pg.text('-', (e['sx1'] + f['sx0']) / 2, nl[4] + 3.6 * SP, 200, 'sans', True)
            barno += 1
        y = bottom + 7 * SP + (2 * SP if spec.get('parts') else 0)
    doc.subset_fonts()
    return doc, expect, words


def ledger(idx):
    out = []
    i = 28
    while i >= idx: out.append(i); i -= 2
    i = 40
    while i <= idx: out.append(i); i += 2
    return out


def fret_of(m):
    for s, base in enumerate(TUNE):
        if 0 <= m - base <= 14: return s, m - base
    return 5, max(0, m - TUNE[5])


def as_text(rows):
    out = []
    for r in rows:
        fmt = lambda v: ('%g' % round(v, 3))
        s = '%d:%s|%s|%s' % (r['n'], fmt(r['len']), ' '.join('%s/%s' % (a, fmt(b)) for a, b in r['notes']), ' '.join('r' + fmt(v) for v in r['rests']))
        if r['f']: s += '|' + ','.join(r['f'])
        out.append(s)
    return out


def tempos_of(spec):
    # every tempo mark with the number of the bar it's in
    out, n = [], 1
    for L in spec['lines']:
        for b in L:
            B = parse_bar(b)
            if B['tempo'] and (not out or out[-1][1] != B['tempo']): out.append([n, B['tempo']])
            m = next((e for e in B['ev'] if e['t'] == 'M'), None)
            n += m['n'] if m else 1
    return out


# made-up tunes (titles, words and notes are invented)
PRINTS = [
    {'file': 'score-lantern-walk.pdf', 'title': 'Lantern Walk', 'artist': 'The Made Up Band', 'key': 2, 'time': [4, 4], 'tempo': 96, 'slant': True,
     'lines': [
         ['Q96 D5:2=Moon- [D5:1=light A4:1=on] F#5+D5:2=the A4:2=hill',
          '[G4:0.5=Lan- A4:0.5=terns B4:0.5=swing- A4:0.5=ing] G4:2~ G4:2 r:1 [F#4:1=home]',
          't3( [E4:1=slow- F#4:1=ly E4:1=we] ) g:C#4 D4:4=go r:2',
          'r:8'],
         ['m:4',
          '[E4:0.25=Ev- F#4:0.25=er- G4:0.5=y] A4:3=step B4:2=we C#5:2=climb',
          'D5:6=on r:2'],
     ]},
    {'file': 'score-ferry-lights.pdf', 'title': 'Ferry Lights', 'artist': 'Nobody In Particular', 'key': -3, 'time': [4, 4], 'tempo': 88,
     'lines': [
         ['Q88 Eb4:2=Lights G4:2=on Bb4:2=the Bn4:2=bay',
          'An4:2=ris- Ab4:2=ing An4:2=a- Ab4:2=gain',
          'T2/4 G4:2=we F4:2=go',
          'T4/4 Q120 E1 [Eb4:1=Out G4:1=to] Bb4:4=sea r:2 :|'],
         ['C D5:4=Home Bb4:4=late', 'Eb5:8=now'],
     ]},
    {'file': 'score-two-voices.pdf', 'title': 'Two Voices', 'artist': 'The Pretend Duo', 'key': 0, 'time': [4, 4], 'tempo': 100, 'parts': True,
     'lines': [['Q100 C4:2=One D4:2=two E4:2=three F4:2=four', 'G4:4=and A4:4=more', 'G4:2=end- F4:2=ing E4:4=now']]},
    {'file': 'score-no-tab.pdf', 'title': 'Quiet Kitchen', 'artist': 'Made Up Trio', 'key': 1, 'time': [3, 4], 'tempo': 72, 'tab': False,
     'lines': [['Q72 D4:2=Ket- G4:2=tle B4:2=sings', 'A4:3=soft- G4:1=ly F#4:2=it', 'G4:6=hums'],
               ['B4:2=Plates [A4:1=are G4:1=stacked] F#4:2=up', 'E4:2=Spoons D4:4=rest', 'G4:6=here']]},
    {'file': 'score-guitar-part.pdf', 'title': 'Strum Along', 'artist': 'The Imaginary Guitars', 'key': 0, 'time': [4, 4], 'tempo': 110,
     'lines': [['Q110 E4+C4:2 G4+E4:2 A4+F4:2 G4+E4:2', 'C5+G4:4 B4+G4:4', 'A4+F4:2 G4+E4:2 F4+D4:2 E4+C4:2']]},
]


if __name__ == '__main__':
    made = {}
    for spec in PRINTS:
        doc, rows, words = engrave(spec)
        doc.save(os.path.join(OUT, spec['file']), garbage=4, deflate=True)
        made[spec['file']] = {'title': spec['title'], 'artist': spec['artist'], 'key': spec['key'], 'time': spec['time'], 'tempo': spec['tempo'], 'tempos': tempos_of(spec), 'bars': as_text(rows), 'words': words}
        print(spec['file'], len(rows), 'bars')
    with open(os.path.join(OUT, 'score.json'), 'w') as f:
        json.dump(made, f, indent=1)
