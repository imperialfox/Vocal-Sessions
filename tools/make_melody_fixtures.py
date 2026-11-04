"""Make the sheet music reader's test prints (Q42): made-up tunes drawn the way an Ultimate Guitar print of the
notation plus tab view looks, at 277 pixels an inch, saved as PDFs with one picture per line of music and a UG-style
footer, as Safari writes them.

    python3 tools/make_melody_fixtures.py            writes tests/fixtures/melody/*.pdf and expect.json
    python3 tools/make_melody_fixtures.py --raw DIR  also writes each line picture as DIR/<name>-<i>.gray (for a quick
                                                     look with the reader in Node)

Needs Pillow and the DejaVu fonts (for the made-up words, section names and dynamics) and qpdf (for the locked print).
Its output is committed, so the tests need none of these. Every tune, word and title here is made up: no real music.

The digits are drawn from the reader's own digit shapes (js/melodyread.js), scaled to the size UG prints them, so a
pass means the reader finds and measures everything around them: staves, bars, heads, stems, beams, flags, dots,
rests, ties, triplets, time and key signatures, multi-bar rests and their counts, bar numbers, repeats and endings.
"""
import json, math, os, re, subprocess, sys, zlib
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'tests', 'fixtures', 'melody')
FONT = '/usr/share/fonts/truetype/dejavu/'

W = 2214                 # a line picture's width (8 inches at 277 ppi)
SP, TSP = 19.2, 28.8     # notation and tab line spacing
TOP = 125                # notation top line
GAP = 112                # notation bottom line to tab top line
TUNE = [64, 59, 55, 50, 45, 40]
X0, X1 = 36, 2190        # the staff's ends
DIGIT_H = 21             # tab digits, in pixels
NAMES = 'CDEFGAB'


def templates():
    src = open(os.path.join(ROOT, 'js', 'melodyread.js'), encoding='utf-8').read()
    tpl = json.loads(re.search(r'const TPL = (\{.*?\});', src, re.S).group(1))
    multi = json.loads(re.search(r'const MULTI_TPL = (\[\[.*?\]\]);', src, re.S).group(1))
    digits = {}
    for v, lab in zip(tpl['cen'], tpl['label']):
        if lab is not None and lab not in digits:
            digits[lab] = v
    return digits, {str(i): v for i, v in enumerate(multi)}


DIG, BOLD = templates()


def glyph(vals, h):
    """A template (18 x 26, 0..255) cropped to its shape and scaled to h pixels tall, as a 1-bit mask."""
    im = Image.new('L', (18, 26))
    im.putdata([int(v) for v in vals])
    bb = im.point(lambda v: 255 if v > 90 else 0).getbbox()
    im = im.crop(bb)
    w = max(3, round(im.width * h / im.height))
    return im.resize((w, h), Image.LANCZOS).point(lambda v: 255 if v > 120 else 0)


class Line:
    """One line of music: the notation staff, the words between, and the tab staff."""

    def __init__(self, extra_top=0, notation=True, tab=True):
        self.top = TOP + extra_top
        self.nl = [self.top + i * SP for i in range(5)]
        self.tl = [self.nl[4] + GAP + i * TSP for i in range(6)]
        self.notation, self.tab = notation, tab
        h = (self.tl[5] if tab else self.nl[4] + 90) + 26
        self.im = Image.new('L', (W, int(h)), 255)
        self.d = ImageDraw.Draw(self.im)
        if notation:
            for y in self.nl:
                self.d.rectangle([X0, round(y) - 1, X1, round(y)], fill=0)
        if tab:
            for y in self.tl:
                self.d.rectangle([X0, round(y) - 1, X1, round(y)], fill=0)

    # ---- the shapes ----
    def paste(self, mask, x, y):
        """Paste a 1-bit mask with its top left at (x, y), dark where the mask is."""
        self.im.paste(0, (int(round(x)), int(round(y))), mask)

    def digits(self, text, cx, cy, h=DIGIT_H, bold=False, clear=True):
        gl = [glyph((BOLD if bold else DIG)[c], h) for c in text]
        wd = sum(g.width for g in gl) + 3 * (len(gl) - 1)
        x = cx - wd / 2
        if clear:
            self.d.rectangle([x - 3, cy - h / 2 - 2, x + wd + 3, cy + h / 2 + 2], fill=255)
        for g in gl:
            self.paste(g, x, cy - h / 2)
            x += g.width + 3
        return wd

    def barline(self, x, thick=2):
        if self.notation:
            self.d.rectangle([x - thick // 2, self.nl[0], x - thick // 2 + thick - 1, self.nl[4]], fill=0)
        if self.tab:
            self.d.rectangle([x - thick // 2, self.tl[0], x - thick // 2 + thick - 1, self.tl[5]], fill=0)

    def clef(self):
        n = self.nl
        self.d.line([(52, n[0] - 24), (52, n[4] + 16)], fill=0, width=3)
        self.d.ellipse([40, n[2] - 4, 66, n[4] + 2], outline=0, width=3)
        self.d.arc([46, n[0] - 26, 62, n[0] - 6], 180, 360, fill=0, width=3)

    def key(self, nsh):
        n = self.nl
        order = ['F5', 'C5', 'G5', 'D5', 'A4', 'E5', 'B4'] if nsh > 0 else ['B4', 'E5', 'A4', 'D5', 'G4', 'C5', 'F4']
        for i in range(abs(nsh)):
            x, y = 80 + 24 * i, self.ypos(order[i])
            if nsh > 0:
                self.d.rectangle([x + 3, y - 24, x + 5, y + 22], fill=0)
                self.d.rectangle([x + 11, y - 26, x + 13, y + 20], fill=0)
                self.d.polygon([(x, y - 6), (x + 17, y - 11), (x + 17, y - 6), (x, y - 1)], fill=0)
                self.d.polygon([(x, y + 6), (x + 17, y + 1), (x + 17, y + 6), (x, y + 11)], fill=0)
            else:
                self.d.rectangle([x + 2, y - 30, x + 4, y + 8], fill=0)
                self.d.ellipse([x + 1, y - 4, x + 13, y + 9], outline=0, width=3)
        return 80 + 24 * abs(nsh)

    def metre(self, n, d, x):
        h = round(1.9 * SP)
        self.digits(str(n), x, (self.nl[0] + self.nl[2]) / 2, h, bold=True, clear=False)
        self.digits(str(d), x, (self.nl[2] + self.nl[4]) / 2, h, bold=True, clear=False)

    def ypos(self, name):
        """The y of a written note, 'F5' and so on (the reader's step 38 is the top line, F5)."""
        idx = int(name[-1]) * 7 + NAMES.index(name[0])
        return self.nl[0] - (idx - 38) * SP / 2

    def head(self, x, y, hollow=False, small=False):
        rx, ry = (7, 5) if small else (12, 8.5)
        pts = []
        for k in range(40):
            a = 2 * math.pi * k / 40
            px, py = rx * math.cos(a), ry * math.sin(a)
            r = math.radians(-20)
            pts.append((x + px * math.cos(r) - py * math.sin(r), y + px * math.sin(r) + py * math.cos(r)))
        self.d.polygon(pts, fill=0)
        if hollow:
            inner = [(x + (px - x) * 0.72, y + (py - y) * 0.56) for px, py in pts]
            self.d.polygon(inner, fill=255)
        # ledger lines
        n = self.nl
        y0 = n[4] + SP
        while y >= y0 - 4:
            self.d.rectangle([x - 17, round(y0) - 1, x + 17, round(y0)], fill=0)
            y0 += SP
        y0 = n[0] - SP
        while y <= y0 + 4:
            self.d.rectangle([x - 17, round(y0) - 1, x + 17, round(y0)], fill=0)
            y0 -= SP

    def stem(self, x, y, up, length=3.5 * SP, small=False):
        if small:
            sx = x + 6
            self.d.rectangle([sx, y - 36, sx + 1, y], fill=0)
            self.d.line([(sx - 7, y - 14), (sx + 8, y - 30)], fill=0, width=2)
            return
        if up:
            sx = x + 10
            self.d.rectangle([sx, y - length, sx + 2, y - 2], fill=0)
            return (sx + 1, y - length)
        sx = x - 12
        self.d.rectangle([sx, y + 2, sx + 2, y + length], fill=0)
        return (sx + 1, y + length)

    def flags(self, end, up, k):
        ex, ey = end
        for i in range(k):
            if up:
                y = ey + 11 * i
                self.d.line([(ex, y), (ex + 16, y + 24)], fill=0, width=6)
            else:
                y = ey - 11 * i
                self.d.line([(ex, y), (ex + 16, y - 24)], fill=0, width=6)

    def beam(self, a, b, up, level):
        (ax, ay), (bx, by) = a, b
        off = 13 * level if up else -13 * level
        t = 9
        if up:
            self.d.polygon([(ax - 1, ay + off), (bx + 2, by + off), (bx + 2, by + off + t), (ax - 1, ay + off + t)], fill=0)
        else:
            self.d.polygon([(ax - 1, ay + off - t), (bx + 2, by + off - t), (bx + 2, by + off), (ax - 1, ay + off)], fill=0)

    def dot(self, x, y, k):
        for i in range(k):
            dx = x + 6 + 12 * i
            self.d.ellipse([dx, y - 4, dx + 7, y + 3], fill=0)

    def rest(self, kind, x):
        n = self.nl
        if kind == 'whole':
            self.d.rectangle([x - 13, n[1], x + 13, n[1] + 10], fill=0)
        elif kind == 'half':
            self.d.rectangle([x - 13, n[2] - 10, x + 13, n[2]], fill=0)
        elif kind == 'quarter':
            y = n[0] + 8
            self.d.line([(x - 4, y), (x + 6, y + 14), (x - 4, y + 27), (x + 6, y + 40), (x - 2, y + 52)], fill=0, width=5)
        elif kind == 'eighth':
            y = n[1] + 4
            self.d.ellipse([x - 9, y - 1, x - 1, y + 7], fill=0)
            self.d.line([(x - 5, y + 5), (x + 8, y + 1)], fill=0, width=4)
            self.d.line([(x + 8, y + 1), (x - 1, y + 31)], fill=0, width=4)
        elif kind == 'sixteenth':
            y = n[1] - 2
            self.d.ellipse([x - 9, y - 1, x - 1, y + 7], fill=0)
            self.d.line([(x - 5, y + 5), (x + 9, y + 1)], fill=0, width=4)
            self.d.ellipse([x - 11, y + 17, x - 3, y + 25], fill=0)
            self.d.line([(x - 7, y + 23), (x + 6, y + 19)], fill=0, width=4)
            self.d.line([(x + 9, y + 1), (x - 3, y + 64)], fill=0, width=4)

    def multirest(self, x0, x1, count):
        n = self.nl
        a, b = x0 + 30, x1 - 30
        self.d.rectangle([a, n[2] - 7, b, n[2] + 7], fill=0)
        self.d.rectangle([a - 1, n[1], a + 1, n[3]], fill=0)
        self.d.rectangle([b - 1, n[1], b + 1, n[3]], fill=0)
        cx = (a + b) / 2
        self.digits(str(count), cx, n[0] - 8 - 15, 30, bold=True, clear=False)
        if self.tab:
            self.digits(str(count), cx, self.tl[0] - 8 - 15, 30, bold=True, clear=False)

    def text(self, s, x, y, size=22, face='DejaVuSans.ttf'):
        f = ImageFont.truetype(FONT + face, size)
        self.d.text((x, y), s, fill=0, font=f)


# ---------- a tune ----------
def spell(midi_written, nsh):
    pc = midi_written % 12
    letter = ('CDDEEFGGAABB' if nsh < 0 else 'CCDDEFFGGAAB')[pc]
    return letter + str(midi_written // 12 - 1)


def place_tab(midi, string=None):
    if string is not None:
        return string, midi - TUNE[string]
    for s in range(6):
        f = midi - TUNE[s]
        if 0 <= f <= 12:
            return s, f
    raise ValueError(midi)


VIS = {8: ('hollow', 0, 0, False), 4: ('hollow', 1, 0, False), 2: ('filled', 1, 0, False), 1: ('filled', 1, 1, False),
       0.5: ('filled', 1, 2, False), 6: ('hollow', 1, 0, 1), 3: ('filled', 1, 0, 1), 1.5: ('filled', 1, 1, 1),
       3.5: ('filled', 1, 0, 2), 0.75: ('filled', 1, 2, 1), 12: ('hollow', 0, 0, 1)}
REST = {8: 'whole', 4: 'half', 2: 'quarter', 1: 'eighth', 0.5: 'sixteenth'}


def draw_line(L, bars, nsh, opts):
    """Draw bars on a line. Each bar: {'ev': [...], 'metre': (n, d), 'name': str, 'repeat_end': bool, 'ending': '1',
    'coda': bool, 'multi': count}. Events: ('n', sung, dur, {..}) or ('r', dur) or ('t', [notes...]) a triplet."""
    if L.notation:
        L.clef()
        x = L.key(nsh) + 8
    else:
        x = 90
    if opts.get('metre') and L.notation:
        L.metre(*opts['metre'], x + 18)
        x += 52
    if opts.get('num') is not None and L.notation:
        L.digits(str(opts['num']), 52, L.nl[0] - 43, 18, clear=False)
    L.barline(X0)
    head_x0 = max(x + 40, 300 if opts.get('first') else 260)
    # widths: share of the line by each bar's length
    lens = [b.get('w', 1) for b in bars]
    total = sum(lens)
    edges = [head_x0 - 40]
    for w_ in lens:
        edges.append(edges[-1] + (X1 - head_x0 + 40) * w_ / total)
    prev_note = None
    prev_tab = None
    notes_drawn = []
    for bi, b in enumerate(bars):
        bx0, bx1 = edges[bi], edges[bi + 1]
        if bi:
            if b.get('repeat_start'):
                L.barline(bx0 - 3, 6)
                L.barline(bx0 + 6, 2)
            pass
        if b.get('repeat_end'):
            L.barline(bx1 - 9, 2)
            L.barline(bx1 - 1, 6)
            for yy in ((L.nl[1] + L.nl[2]) / 2, (L.nl[2] + L.nl[3]) / 2):
                L.d.ellipse([bx1 - 22, yy - 4, bx1 - 14, yy + 4], fill=0)
        elif bi + 1 < len(bars):
            L.barline(round(bx1))
        if b.get('name') and L.notation:
            L.text(b['name'], bx0 + 22, L.nl[0] - 80, 20, 'DejaVuSans-Bold.ttf')
        if b.get('ending') and L.notation:
            y = L.nl[0] - 52
            L.d.rectangle([bx0 + 6, y, bx1 - 8, y + 1], fill=0)
            L.d.rectangle([bx0 + 6, y, bx0 + 7, y + 24], fill=0)
            L.digits(b['ending'], bx0 + 22, y + 15, 18, clear=False)
            L.d.ellipse([bx0 + 30, y + 21, bx0 + 33, y + 24], fill=0)
        if b.get('coda') and L.notation:
            cx, cy = bx0 + (bx1 - bx0) * 0.6, L.nl[0] - 50
            L.d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=0, width=4)
            L.d.rectangle([cx - 24, cy - 1, cx + 24, cy + 1], fill=0)
            L.d.rectangle([cx - 1, cy - 24, cx + 1, cy + 24], fill=0)
        if b.get('metre') and L.notation and not (bi == 0 and opts.get('metre')):
            L.metre(*b['metre'], bx0 + 28)
            bx0 += 50
        if b.get('multi'):
            L.multirest(bx0, bx1, b['multi'])
            continue
        evs = b['ev']
        flat = []
        for e in evs:
            if e[0] == 't':
                for k, sub in enumerate(e[1]):
                    flat.append(sub + ({'trip': id(e), 'tk': k},) if len(sub) == 3 else (sub[0], sub[1], sub[2], dict(sub[3], trip=id(e), tk=k)))
            else:
                flat.append(e)
        # x of each event: spaced by length, with room before the first and after the last
        units = [max(0.8, (e[2] if e[0] == 'n' else e[1]) ** 0.6) for e in flat]
        span = bx1 - bx0 - 70
        xs = []
        acc = 36
        tot = sum(units)
        for u in units:
            xs.append(bx0 + acc + span * (u / 2) / tot)
            acc += span * u / tot
        groups = {}
        for e, ex in zip(flat, xs):
            if e[0] == 'r':
                if L.notation:
                    L.rest(REST[e[1]], ex)
                continue
            _, sung, dur, o = e if len(e) == 4 else (*e, {})
            o = dict(o)
            vis_dur = 1 if 'trip' in o else dur
            kind, has_stem, nflag, ndot = VIS[vis_dur]
            if L.notation:
                written = sung + 12
                y = L.ypos(spell(written, nsh))
                up = y > L.nl[2] - 1
                if o.get('grace'):
                    L.head(ex - 26, L.ypos(spell(o['grace'] + 12, nsh)), small=True)
                    L.stem(ex - 26, L.ypos(spell(o['grace'] + 12, nsh)), True, small=True)
                L.head(ex, y, hollow=(kind == 'hollow'))
                if o.get('harm'):
                    L.head(ex, L.ypos(spell(o['harm'] + 12, nsh)))
                end = L.stem(ex, y, up) if has_stem else None
                if ndot:
                    on_line = round((y - L.nl[0]) / (SP / 2)) % 2 == 0
                    L.dot(ex + 12, y - SP / 2 if on_line else y, ndot)
                g = o.get('beam') or o.get('trip')
                if g and end:
                    groups.setdefault(g, []).append((end, up, nflag, ex, y))
                elif nflag and end:
                    L.flags(end, up, nflag)
                if o.get('slide') and prev_note is not None:
                    L.d.line([(prev_note[0] + 13, prev_note[1]), (ex - 13, y)], fill=0, width=2)
                if o.get('tie') and prev_note is not None:
                    px, py = prev_note
                    L.d.arc([px + 4, py + 6, ex - 4, py + 24], 20, 160, fill=0, width=3)
                prev_note = (ex, y)
                notes_drawn.append((ex, y, o))
            if L.tab:
                s, f = place_tab(sung, o.get('string'))
                if o.get('tab_off'):
                    s, f = place_tab(sung + o['tab_off'])
                ty = L.tl[s]
                if o.get('fret_text'):
                    L.digits(o['fret_text'], ex, ty)
                    prev_tab = (ex, ty, 30)
                    continue
                if o.get('tie'):
                    w_ = L.digits(str(f), ex, ty)
                    L.d.rectangle([ex - w_ / 2 - 14, ty - 13, ex + w_ / 2 + 14, ty + 13], fill=255)
                    L.d.arc([ex - w_ / 2 - 13, ty - 12, ex - w_ / 2 - 5, ty + 12], 110, 250, fill=0, width=3)
                    L.d.arc([ex + w_ / 2 + 5, ty - 12, ex + w_ / 2 + 13, ty + 12], -70, 70, fill=0, width=3)
                    L.digits(str(f), ex, ty, clear=False)
                else:
                    w_ = L.digits(str(f), ex, ty)
                if o.get('harm'):
                    hs = o.get('hstring')
                    if hs is None:
                        hs = next(k for k in range(s + 1, 6) if 0 <= o['harm'] - TUNE[k] <= 12)
                    hs, hf = place_tab(o['harm'], hs)
                    L.digits(str(hf), ex, L.tl[hs])
                if o.get('grace'):
                    gs, gf = place_tab(o['grace'], s)
                    L.digits(str(gf), ex - 30, L.tl[gs], 15)
                if o.get('bend'):
                    # a "¼" bend label on the string above, smaller than a fret number
                    by = L.tl[max(0, s - 1)]
                    L.d.rectangle([ex - 18, by - 10, ex + 18, by + 10], fill=255)
                    L.digits('1', ex - 9, by - 2, 16, clear=False)
                    L.d.line([(ex - 3, by + 7), (ex + 3, by - 8)], fill=0, width=2)
                    L.digits('4', ex + 10, by + 1, 16, clear=False)
                if o.get('slide') and prev_tab:
                    # a slide: a line from the last fret number to this one, touching both (H51)
                    pex, pty, pw = prev_tab
                    L.d.line([(pex + pw / 2 + 1, pty + 4), (ex - w_ / 2 - 1, ty - 4)], fill=0, width=3)
                prev_tab = (ex, ty, w_)
        for g, members in groups.items():
            if len(members) < 2:
                for end, up, nflag, ex, y in members:
                    if nflag:
                        L.flags(end, up, nflag)
                continue
            up = members[0][1]
            # one direction for the group: re-draw stems to a common end
            ys = [m[4] for m in members]
            for i in range(len(members) - 1):
                a, b2 = members[i], members[i + 1]
                lev = min(a[2] or 1, b2[2] or 1)
                for k in range(lev):
                    L.beam(a[0], b2[0], a[1], k)
                for m, other, sgn in ((a, b2, 1), (b2, a, -1)):
                    for k in range(lev, m[2] or 1):
                        (mx, my) = m[0]
                        L.beam((mx, my) if sgn > 0 else (mx - 18, my), (mx + 18, my) if sgn > 0 else (mx, my), m[1], k)
            if any(isinstance(g, int) and g > 1000 for g in [g]) and L.notation:
                pass
        # triplet brackets
        trips = {}
        for e, ex in zip(flat, xs):
            if e[0] == 'n' and len(e) == 4 and 'trip' in e[3]:
                trips.setdefault(e[3]['trip'], []).append(ex)
        for t, pts in trips.items():
            if not L.notation:
                continue
            y = L.nl[0] - 40
            a, c = pts[0] - 14, pts[-1] + 14
            m = (a + c) / 2
            L.d.rectangle([a, y, m - 16, y + 1], fill=0)
            L.d.rectangle([m + 16, y, c, y + 1], fill=0)
            L.d.rectangle([a, y, a + 1, y + 13], fill=0)
            L.d.rectangle([c - 1, y, c, y + 13], fill=0)
            L.digits('3', m, y, 18, clear=False)
    L.barline(X1 - 1, 4)
    if opts.get('words') and L.notation:
        for (wx, w) in opts['words']:
            L.text(w, wx, L.nl[4] + 46, 22)
    if opts.get('dyn') and L.notation:
        for (wx, w) in opts['dyn']:
            L.text(w, wx, L.nl[4] + 46, 24, 'DejaVuSerif-BoldItalic.ttf')
    return L


# ---------- PDF writing ----------
def pdf(path, pages, footer):
    """pages: [[Image (L), ...], ...]. Each picture is drawn full width, top to bottom, as Safari does, with the
    footer text at the bottom of every page and a title at the top of the first."""
    objs = []

    def add(b):
        objs.append(b)
        return len(objs)

    catalog = add(None)
    pages_obj = add(None)
    font = add(b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>')
    kids = []
    for pi, pics in enumerate(pages):
        res_imgs, draw = [], []
        y = 842 - (70 if pi == 0 else 30)
        for k, im in enumerate(pics):
            rgb = im.convert('RGB')
            data = zlib.compress(rgb.tobytes(), 9)
            n = add(b'<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length %d >>\nstream\n' % (im.width, im.height, len(data)) + data + b'\nendstream')
            res_imgs.append((k, n))
            w = im.width * 72 / 277
            h = im.height * 72 / 277
            y -= h + 6
            draw.append(b'q %.3f 0 0 %.3f %.3f %.3f cm /Im%d Do Q\n' % (w, h, (595 - w) / 2, y, k))
        text = b''
        if pi == 0 and footer.get('title'):
            text += b'BT /F1 16 Tf 40 800 Td (%s) Tj ET\n' % footer['title'].encode('latin-1')
        if footer.get('link') is not None:
            text += b'BT /F1 8 Tf 40 20 Td (%s) Tj ET\n' % footer['link'].encode('latin-1')
        text += b'BT /F1 8 Tf 540 20 Td (%d/%d) Tj ET\n' % (pi + 1, len(pages))
        content = b''.join(draw) + text
        c = add(b'<< /Length %d >>\nstream\n' % len(content) + content + b'\nendstream')
        xo = b' '.join(b'/Im%d %d 0 R' % (k, n) for k, n in res_imgs)
        p = add(b'<< /Type /Page /Parent %d 0 R /MediaBox [0 0 595 842] /Contents %d 0 R /Resources << /Font << /F1 %d 0 R >> /XObject << %s >> >> >>' % (pages_obj, c, font, xo))
        kids.append(p)
    objs[catalog - 1] = b'<< /Type /Catalog /Pages %d 0 R >>' % pages_obj
    objs[pages_obj - 1] = b'<< /Type /Pages /Kids [%s] /Count %d >>' % (b' '.join(b'%d 0 R' % k for k in kids), len(kids))
    out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    offs = []
    for i, o in enumerate(objs):
        offs.append(len(out))
        out += b'%d 0 obj\n' % (i + 1) + o + b'\nendobj\n'
    x = len(out)
    out += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objs) + 1)
    for o in offs:
        out += b'%010d 00000 n \n' % o
    out += b'trailer\n<< /Size %d /Root %d 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objs) + 1, catalog, x)
    open(path, 'wb').write(out)


def ug(artist, title, tid):
    return {'title': '%s by %s' % (title.replace('-', ' ').title(), artist.replace('-', ' ').title()),
            'link': 'https://www.ultimate-guitar.com/tab/%s/%s-official-%d   Printed from Ultimate Guitar' % (artist, title, tid)}


def N(sung, dur, **o):
    return ('n', sung, dur, o)


def R(dur):
    return ('r', dur)


def T(*notes):
    return ('t', list(notes))


def build(lines_spec, nsh, metre, notation=True, tab=True):
    pics = []
    for i, (bars, o) in enumerate(lines_spec):
        o = dict(o)
        if i == 0:
            o['first'] = True
            o['metre'] = metre
        L = Line(notation=notation, tab=tab)
        draw_line(L, bars, nsh, o)
        pics.append(L.im)
    return pics


# ---------- the tunes (all made up) ----------
def tune_a():
    """'Paper Lanterns' (made up): D major (2 sharps), 4/4. A pickup, a 4-bar rest with its count and the printed bar
    numbers, a tie across a bar line, a triplet, dotted and double-dotted notes, a sixteenth rest, two-digit frets, a
    bend label, dynamics in the words' band, a grace note and a slide, a harmony stack, a 2/4 bar, section names."""
    l1 = [
        {'ev': [N(57, 2)], 'w': 0.5},                                                  # pickup: one beat (A3)
        {'multi': 4, 'w': 1.1, 'name': 'Intro'},                                       # bars 1-4
        {'ev': [N(62, 2), N(64, 2), N(66, 3), N(64, 1)], 'name': 'Verse'},           # bar 5 (D4 E4 F#4. E4)
        {'ev': [N(62, 4), N(62, 4, tie=True)]},                                        # bar 6 (tie inside the bar)
    ]
    l2 = [
        {'ev': [N(66, 2), T(N(64, 1), N(62, 1), N(64, 1)), N(66, 2), R(2)]},          # bar 7: a triplet and a quarter rest
        {'ev': [N(69, 3.5), N(67, 0.5), N(66, 2), N(64, 2)]},                          # bar 8: double-dotted
        {'ev': [N(67, 2, string=2), N(69, 2, string=2), N(71, 2, string=2, bend=True), N(69, 2, string=2)]},  # bar 9: frets 12 14 16 14, a bend label
        {'ev': [N(66, 1.5, beam='a'), N(64, 0.5, beam='a'), N(62, 2), N(64, 2), N(66, 2, tie=False)]},         # bar 10
    ]
    l3 = [
        {'ev': [N(64, 8)]},                                                           # bar 11 whole note, tied over
        {'ev': [N(64, 4, tie=True), N(62, 1, beam='b'), N(61, 1, beam='b'), N(59, 2)], 'name': 'Chorus'},  # bar 12: the tie across the bar line
        {'ev': [N(62, 2, grace=64), N(64, 2), N(66, 2, slide=True), N(67, 2)]},   # bar 13: a grace note
        {'ev': [N(69, 2, harm=66), N(67, 2), N(66, 4)], 'metre': None},                 # bar 14: a harmony stack
    ]
    l4 = [
        {'ev': [N(64, 2), N(62, 2)], 'metre': (2, 4), 'w': 0.6},                       # bar 15: 2/4
        {'ev': [N(62, 2), N(64, 1, beam='c'), N(66, 1, beam='c'), R(0.5), N(64, 0.5, beam=None, string=1), N(62, 1), N(61, 2)], 'metre': (4, 4)},  # bar 16: a sixteenth rest
        {'ev': [N(62, 6), R(2)]},                                                     # bar 17: dotted half
        {'ev': [R(8)]},                                                               # bar 18: whole rest
    ]
    # a slide on bar 13: the line between its second and third notes is drawn in tab and notation
    spec = [(l1, {'dyn': [(560, 'mf')], 'words': [(340, 'Oh'), (900, 'Pa-'), (1100, 'per'), (1350, 'lan-'), (1520, 'terns'), (1800, 'glow')]}),
            (l2, {'num': 7, 'words': [(320, 'up'), (460, 'a-'), (560, 'bove'), (900, 'the'), (1250, 'qui-'), (1400, 'et'), (1750, 'town')], 'dyn': [(1150, 'f')]}),
            (l3, {'num': 11, 'words': [(320, 'Home'), (900, 'we'), (1300, "can't"), (1700, 'stay')]}),
            (l4, {'num': 15, 'words': [(330, 'la'), (900, 'la'), (1300, 'la')]})]
    return spec


def expected_a():
    return {'bars': 18, 'pickup': True, 'multi': [4], 'key': 2, 'time': [4, 4]}


def tune_flat():
    """'Rain On The Ferry' (made up): E flat major (3 flats), 4/4, plain."""
    l1 = [{'ev': [N(63, 2), N(65, 2), N(67, 2), N(68, 2)]}, {'ev': [N(70, 4), N(67, 4)]},
          {'ev': [N(68, 2), N(67, 2), N(65, 2), N(63, 2)]}, {'ev': [N(65, 6), R(2)]}]
    l2 = [{'ev': [N(67, 2), N(68, 1, beam='a'), N(70, 1, beam='a'), N(72, 2), N(70, 2)]}, {'ev': [N(68, 4), N(65, 4)]},
          {'ev': [N(63, 2), N(65, 2), N(67, 2), N(65, 2)]}, {'ev': [N(63, 8)]}]
    return [(l1, {'words': [(330, 'Rain'), (700, 'on')]}), (l2, {'num': 5})]


def tune_repeat():
    """'Lighthouse Steps' (made up): C major, 4/4, with an end repeat, a first ending and a coda sign."""
    l1 = [{'ev': [N(60, 2), N(62, 2), N(64, 2), N(65, 2)]}, {'ev': [N(67, 4), N(64, 4)], 'repeat_end': True, 'ending': '1'},
          {'ev': [N(65, 2), N(64, 2), N(62, 2), N(60, 2)], 'coda': True}, {'ev': [N(60, 8)]}]
    return [(l1, {})]


def tune_numbers():
    """'Night Bus Home' (made up): a 3-bar rest, then the next line's printed bar number says 7 where the count
    reaches 6, so that line is flagged (H1)."""
    l1 = [{'ev': [N(60, 2), N(62, 2), N(64, 2), N(62, 2)]}, {'multi': 3, 'w': 1.2}, {'ev': [N(64, 4), N(62, 4)]}]
    l2 = [{'ev': [N(60, 2), N(62, 2), N(64, 4)]}, {'ev': [N(62, 8)]}]
    # the catcher: an unreadable fret (27), a tab an octave off the notation (a spike), a tab two semitones off (unsure),
    # and a tab far below the tune (outside its range)
    l3 = [{'ev': [N(60, 2), N(62, 2, fret_text='27'), N(64, 2), N(62, 2)]},
          {'ev': [N(60, 2), N(62, 2, tab_off=12), N(64, 2), N(65, 2, tab_off=2)]},
          {'ev': [N(64, 2), N(62, 2, tab_off=-17), N(60, 4)]}]
    return [(l1, {}), (l2, {'num': 7}), (l3, {'num': 9})]


def tune_guitar():
    """A made-up guitar part: three-note chords on every beat."""
    def C(m):
        return ('n', m, 2, {'harm': m - 3, 'hstring': None})
    bars = []
    for k in range(4):
        bars.append({'ev': [N(64, 2, harm=60, hstring=1), N(64, 2, harm=59, hstring=1), N(62, 2, harm=59, hstring=1), N(62, 2, harm=57, hstring=2)]})
    return [(bars, {})]


def tune_few():
    """Bars that mostly don't add up (made up): too little to keep."""
    bars = [{'ev': [N(60, 2), N(62, 2), N(64, 2), N(65, 2), N(67, 2)]}, {'ev': [N(64, 4), N(62, 1)]}, {'ev': [N(60, 2), N(62, 2), N(64, 2), N(65, 2)]},
            {'ev': [N(67, 1), N(65, 1), N(64, 1)]}]
    return [(bars, {}), (bars, {'num': 5})]


def main():
    raw = None
    if '--raw' in sys.argv:
        raw = sys.argv[sys.argv.index('--raw') + 1]
        os.makedirs(raw, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    made = {}

    def save(name, pics_pages, foot):
        pdf(os.path.join(OUT, name + '.pdf'), pics_pages, foot)
        made[name] = sum(len(p) for p in pics_pages)
        if raw:
            for i, im in enumerate([p for pg in pics_pages for p in pg]):
                open(os.path.join(raw, '%s-%d.gray' % (name, i)), 'wb').write(b'%d %d\n' % (im.width, im.height) + im.tobytes())

    a = build(tune_a(), 2, (4, 4))
    save('paper-lanterns', [a[:2], a[2:]], ug('the-made-up-band', 'paper-lanterns', 9000001))
    f = build(tune_flat(), -3, (4, 4))
    save('rain-on-the-ferry', [f], ug('nobody-real', 'rain-on-the-ferry', 9000002))
    r = build(tune_repeat(), 0, (4, 4))
    save('lighthouse-steps', [r], ug('nobody-real', 'lighthouse-steps', 9000003))
    nb = build(tune_numbers(), 0, (4, 4))
    save('night-bus-home', [nb], ug('nobody-real', 'night-bus-home', 9000010))
    g = build(tune_guitar(), 0, (4, 4))
    save('guitar-part', [g], ug('nobody-real', 'paper-lanterns', 9000004))
    w = build(tune_few(), 0, (4, 4))
    save('few-bars', [w], ug('nobody-real', 'few-bars', 9000005))
    nt = build(tune_flat(), -3, (4, 4), tab=False)
    save('notation-only', [nt], ug('nobody-real', 'rain-on-the-ferry', 9000006))
    tb = build(tune_flat(), -3, (4, 4), notation=False)
    save('tab-only', [tb], ug('nobody-real', 'rain-on-the-ferry', 9000007))
    save('no-footer', [f], {'title': 'Rain On The Ferry', 'link': 'Printed from somewhere else'})
    save('no-music', [[]], ug('nobody-real', 'empty', 9000008))
    # a long PDF (41 empty pages) and a locked one
    pdf(os.path.join(OUT, 'long.pdf'), [[] for _ in range(41)], ug('nobody-real', 'long', 9000009))
    made['long'] = 0
    lock = os.path.join(OUT, 'locked.pdf')
    subprocess.run(['qpdf', '--encrypt', 'open-sesame', 'owner-pass', '256', '--', os.path.join(OUT, 'rain-on-the-ferry.pdf'), lock], check=True)
    made['locked'] = 0
    json.dump(made, open(os.path.join(OUT, 'made.json'), 'w'), indent=1)
    print('\n'.join('%s: %d lines' % kv for kv in made.items()))


if __name__ == '__main__':
    main()
