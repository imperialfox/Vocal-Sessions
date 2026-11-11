"""Vocal Sessions · the element sheet (Q48, values since Q55): every named part, with its kit part and its values.

    python3 tools/reference/elements.py           write reference/elements.md (opens the app in a headless browser)
    python3 tools/reference/elements.py --check   exit 1 if reference/elements.md is out of date

Reads js/register.js for the parts: the shared parts, the names by action and each screen's own parts, with the
screen's ID and name, how the part is found and its status. Since Q55 it then opens the app (headless Chromium, the
tests' sample data, motion off, a fixed date) on every screen and sheet the sample data reaches, and reads each named
part from the page: its parts kit part (gallery number, from its pk- classes, the control it sits in and its press),
how it presses (KITPRESS, or a row's highlight), its corner and its motion, each mapped back to its name (`--r-card`,
`gentle`, part 12). An app's own part (no kit part) takes its reason from REASONS below. Parts the sample data doesn't
reach keep a dash and are listed at the end. Since Q53 it also reads js/gestures.js › KITPRESS for the Presses
section, and since Q54 a Named motion section lists the animations that took a named value or spring. The tests
(test_screens.py › reference) collect the same way and fail when the sheet is out of date, or when a part has neither
a kit part nor a reason. See MAINTAINING › Screen IDs › The element sheet.
"""
import os
import re
import sys
import datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, 'js', 'register.js')
GEST = os.path.join(ROOT, 'js', 'gestures.js')
OUT = os.path.join(ROOT, 'reference', 'elements.md')
PART = re.compile(r"\{ name: '([a-z0-9-]+)', sel: '((?:[^'\\]|\\.)*)'(?:, was: \[([^\]]*)\])?(?:, status: '([^']+)')? \}")

# ---------------------------------------------------------------- the kit's parts, by gallery number
# Each pk- class (or a class starting with it and a hyphen) and the gallery part it belongs to, from
# tools/parts-kit/README.md › Parts. State classes (pk-on, pk-pressed …) and base classes (pk-btn, pk-circle) aren't parts.
KIT_PARTS = [
    ('pk-glass', 1, 'Glass'), ('pk-strong', 1, 'Glass'), ('pk-clear', 1, 'Glass'),
    ('pk-topbar', 2, 'Top bar'), ('pk-bar-slot', 2, 'Top bar'), ('pk-edge', 51, 'Soft edge'),
    ('pk-large-title', 3, 'Large title'), ('pk-date-line', 3, 'Large title'),
    ('pk-dock', 4, 'Tab bar'), ('pk-tabbar', 4, 'Tab bar'), ('pk-tab', 4, 'Tab bar'),
    ('pk-search-circle', 6, 'Tab bar search'), ('pk-search-field', 6, 'Tab bar search'), ('pk-search-close', 6, 'Tab bar search'),
    ('pk-push', 10, 'Pushed page'), ('pk-tinted', 13, 'Prominent button'),
    ('pk-press', 12, 'Glass button'), ('pk-press-solid', 14, 'Solid press'), ('pk-solid', 14, 'Solid press'),
    ('pk-press-bar', 15, 'Buttons on a bar'), ('pk-group', 15, 'Buttons on a bar'),
    ('pk-menu', 16, 'Pull-down menu'), ('pk-chips', 18, 'Chips'), ('pk-chip', 18, 'Chips'),
    ('pk-badged', 19, 'Badges'), ('pk-badge', 19, 'Badges'), ('pk-tag', 19, 'Badges'),
    ('pk-switch', 21, 'Switch'), ('pk-slider', 22, 'Slider'), ('pk-seg', 23, 'Segmented control'),
    ('pk-stepper', 24, 'Stepper'), ('pk-progress', 25, 'Progress'), ('pk-ring', 25, 'Progress'), ('pk-spinner', 25, 'Progress'),
    ('pk-search', 26, 'Search field'), ('pk-field', 27, 'Text field'), ('pk-area', 29, 'Text area'),
    ('pk-container', 33, 'Glass container'), ('pk-card', 34, 'Card'),
    ('pk-row', 35, 'List row'), ('pk-tile', 35, 'List row'), ('pk-chev', 35, 'List row'), ('pk-list', 36, 'Grouped section'),
    ('pk-divider', 38, 'Divider'), ('pk-swipe', 39, 'Swipe actions'), ('pk-reorder', 40, 'Reorderable list'), ('pk-grip', 40, 'Reorderable list'),
    ('pk-sheet', 41, 'Sheet'), ('pk-grabber', 41, 'Sheet'), ('pk-cover', 43, 'Full-screen cover'), ('pk-popover', 44, 'Popover'),
    ('pk-hold', 46, 'Long-press menu'), ('pk-actions', 47, 'Action sheet'), ('pk-action', 47, 'Action sheet'), ('pk-cancel', 47, 'Action sheet'),
    ('pk-alert', 48, 'Alert'), ('pk-toast', 49, 'Toast'),
]
LABEL = {}
for _c, _n, _l in KIT_PARTS: LABEL.setdefault(_n, _l)
# a button inside one of these is that part's (a segment, a tab, an alert's button); a row holding one of the
# controls in CONTROLS is that control's (a switch row)
INSIDE = '.pk-seg, .pk-stepper, .pk-chips, .pk-tabbar, .pk-alert, .pk-actions, .pk-menu, .pk-swipe-actions, .pk-search-field, .pk-search, .pk-group'
CONTROLS = '.pk-switch, .pk-seg, .pk-slider, .pk-stepper'
# how a part presses: KITPRESS's kinds (js/gestures.js) and a row's highlight (D06, the kit's row.press)
PRESSES = {'pk-press': (12, 'Glass, grows'), 'pk-press-solid': (14, 'Solid, shrinks'), 'pk-press-bar': (15, 'On a bar, lights up'),
           'row': (35, 'Row, highlights')}

# ---------------------------------------------------------------- an app's own part: why it isn't a kit part
# The first selector the part matches gives its reason. Kept short; a part with a kit part needs none.
REASONS = [
    ('.field', 'The app\'s own text field, not kit part 27'),
    ('.ghost, .swdel', 'A plain text button; the kit has no plain text button'),
    ('.sorthdr, .hdrsort', 'A list heading that opens the sort menu; the kit has no heading button'),
    ('.opfin, .addnote, .exmore', 'A small text link on the page; the kit has no text link'),
    ('.pnav', 'The Progress chart\'s own arrows, drawn with the chart'),
    ('.act', 'The song list\'s own swipe buttons, not kit part 39'),
    ('.exlvl', 'The exercise page\'s level buttons, the coach video\'s levels; the kit has no level picker'),
    ('.apsing, [data-a="apNoRec"]', 'Application card\'s own buttons, drawn with the card'),
    ('.cklen', 'Song Clock\'s song length line, drawn with its header'),
    ('.tkplay, .tkpp, .tkhead, .tkas, .tkad, .lbl.tk, .ibtn', 'A take\'s own controls, drawn with its row in the takes list'),
    ('.mkchip', 'The Marks layer chips, the app\'s own, not kit part 18'),
    ('.sgsec', 'A lyric section: a tap focuses it on the song page, so it isn\'t a list row'),
]


def part_no(classes):
    """The gallery parts for a list of pk- classes, as {number: label}."""
    out = {}
    for c in classes:
        hits = [(len(p), n, label) for p, n, label in KIT_PARTS if c == p or c.startswith(p + '-')]
        if hits:
            _, n, label = max(hits)  # the longest match: pk-press-bar is 15, not pk-press's 12
            out[n] = label
    return out


def kit(sel):
    """Kit part from a selector's own pk- classes: used for a part the sample data doesn't reach."""
    return kit_cell(part_no(re.findall(r'\.(pk-[a-z-]+)', sel)))


def kit_cell(parts):
    return ', '.join('%d %s' % (n, parts[n]) for n in sorted(parts))


# ---------------------------------------------------------------- reading the app
# The date the sample data and the page's clock use, so the parts reached (and so the sheet) never depend on the day
FIXED = dt.datetime(2026, 11, 4, 12, 0)

# Run on one screen or sheet: every visible part with a data-name inside the roots, with the register line it comes
# from and what the page says about it. The named values are read once, by applying each name to a probe element,
# so a computed value maps back to the name that gives it.
READ_JS = r"""(arg) => {
  if (!window.__REF) {
    const probe = document.createElement('div');
    probe.style.position = 'absolute';
    document.body.appendChild(probe);
    const names = new Set();
    for (const sh of document.styleSheets) {
      let rs; try { rs = sh.cssRules } catch (e) { continue }
      for (const r of rs) if (r.selectorText === ':root' || r.selectorText === 'html') for (const p of r.style) if (p.startsWith('--')) names.add(p);
    }
    for (const p of document.documentElement.style) if (p.startsWith('--')) names.add(p); // the kit writes the springs here
    const read = (prop, n) => { probe.style[prop] = 'var(' + n + ')'; return getComputedStyle(probe)[prop] };
    const springs = Object.keys(Parts.motion.springs());
    const ease = {}, corner = {}, dur = {};
    [...names].sort().forEach((n) => {
      if (n.startsWith('--ease-')) { const v = read('transitionTimingFunction', n), k = n.slice(7); if (!(v in ease) || springs.includes(k)) ease[v] = springs.includes(k) ? k : n }
      if (n.startsWith('--r-')) { const v = read('borderTopLeftRadius', n); if (v !== '0px' && !(v in corner)) corner[v] = n }
      if (n.startsWith('--dur-')) { const v = read('transitionDuration', n); if (v !== '0s' && !(v in dur)) dur[v] = n }
    });
    probe.remove();
    // rows that highlight while pressed (D06): the app's :active rules that use the kit's row press colour
    const rows = [];
    for (const sh of document.styleSheets) {
      let rs; try { rs = sh.cssRules } catch (e) { continue }
      for (const r of rs) if (r.selectorText && r.selectorText.includes(':active') && r.style.cssText.includes('--pk-row-press')) rows.push(r.selectorText.replace(/:active/g, ''));
    }
    window.__REF = { ease, corner, dur, rows: rows.join(', ') };
  }
  const N = window.__REF, live = (p) => !p.status || p.status === 'Live';
  const scr = SCREENS.screens.find((s) => s.id === arg.screen), own = scr ? scr.parts.filter(live) : [];
  const shared = SCREENS.shared.filter(live), acts = SCREENS.actions.filter(live);
  const is = (el, sel) => { try { return el.matches(sel) } catch (e) { return false } };
  const line = (el) => {
    const n = el.dataset.name;
    let p = own.find((p) => p.name === n && is(el, p.sel)); if (p) return [arg.screen, n, p.sel];
    p = shared.find((p) => p.name === n && is(el, p.sel)); if (p) return ['shared', n, p.sel];
    p = acts.find((p) => p.name === n && is(el, p.sel)); if (p) return ['action', n, p.sel];
    return null;
  };
  const pk = (el) => (el ? [...el.classList].filter((c) => c.startsWith('pk-')) : []);
  const els = new Set();
  arg.roots.forEach((q) => document.querySelectorAll(q).forEach((r) => { if (r.dataset.name) els.add(r); r.querySelectorAll('[data-name]').forEach((e) => els.add(e)) }));
  const out = [];
  els.forEach((el) => {
    const key = line(el);
    if (!key || !el.getClientRects().length) return;
    const cs = getComputedStyle(el), b = el.getBoundingClientRect();
    const kit = pk(el).concat(pk(el.parentElement && el.parentElement.closest(arg.inside)), pk(el.querySelector(arg.controls)));
    // KITPRESS's kind, a kit press class the markup already has (the kit's own buttons), or a row's highlight
    const press = KITPRESS.kind(el) || ['pk-press-solid', 'pk-press-bar', 'pk-press'].find((c) => el.classList.contains(c)) || (N.rows && is(el, N.rows) ? 'row' : null);
    const r = cs.borderTopLeftRadius, px = parseFloat(r);
    let corner = 'none';
    // a named corner first (so a size that changes with the font never changes the answer), then a capsule or circle
    if (px) corner = N.corner[r] || ((r.endsWith('%') ? px >= 50 : px >= Math.min(b.width, b.height) / 2 - 0.5) ? (Math.abs(b.width - b.height) < 1 ? 'circle' : 'capsule') : r);
    const props = cs.transitionProperty.split(', '), durs = cs.transitionDuration.split(', '), eases = cs.transitionTimingFunction.split(/, (?![^(]*\))/);
    const motion = new Set();
    props.forEach((p, i) => {
      const d = durs[i % durs.length], e = eases[i % eases.length];
      if ((p === 'all' || p === 'none') && d === '0s') return;
      if (N.ease[e]) motion.add(N.ease[e]);
      if (d !== '0s') motion.add(N.dur[d] || d);
      if (!N.ease[e] && d !== '0s') motion.add(e);
    });
    if (cs.animationName !== 'none') motion.add('@' + cs.animationName);
    const reason = arg.reasons.findIndex((s) => is(el, s));
    out.push({ key, kit, press, corner, motion: [...motion].sort(), reason });
  });
  return out;
}"""


def open_app(b, w=390, h=844):
    """The app with the tests' sample data and the river song, motion off, the clock at FIXED (an iPhone unless w is wider)."""
    sys.path.insert(0, os.path.join(ROOT, 'tests'))
    import harness
    from test_guide import song
    ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2 if w < 500 else 1, color_scheme='light',
                        timezone_id='Europe/London', locale='en-GB', user_agent=harness.UA_IPHONE if w < 500 else None)
    ctx.clock.install(time=FIXED)
    ctx.add_init_script("try{localStorage.setItem('vocalMotion','0')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(harness.url(harness.APP_PATH))
    was, harness.now = harness.now, FIXED  # sample() dates its sessions from harness.now; put back after, for the tests
    try:
        data = harness.sample()
    finally:
        harness.now = was
    pg.evaluate(harness.SEED, data)
    pg.reload()
    harness.ready(pg)
    song(pg, marks=True)
    return pg


def with_track(pg):
    """The sample song (g_1) with a synthetic track (the tests' tones) and two takes, through the song page's door."""
    import harness
    from test_track import track, loaded
    pg.evaluate("go(()=>{U.tab='songs';U.view='lyr';U.songId='g_1';U.sheet=null})"); pg.wait_for_timeout(200)
    for t in ('t1', 't2'): pg.evaluate(harness.ADD_TAKE, t)
    with pg.expect_file_chooser() as fc: pg.click('#app [data-a=trkAdd]')
    fc.value.set_files(track())
    loaded(pg)


SHEET_JS = """k=>{const ks=[null,'g_1','s0','s2','sp1',FOUND[0].id,'c0_x'];
  for(const withX of [false,true]){if(withX&&!X)newSession();
    for(const kk of ks){U.view=null;U.tab='today';U.sheet=k;U.sd={k:kk};try{render()}catch(e){}
      const sh=document.querySelector('#layer :is(.sheet,.pk-alert,.pk-actions):not(.pk-leaving)');if(U.sheet===k&&sh)return sh.dataset.screen}}
  return null}"""
CLEAR_JS = "(()=>{document.querySelectorAll('#layer .pk-alert,#layer .pk-actions').forEach(e=>e.remove());U.sheet=null;U.sd={};if(X){X=null;saveDraft()}render()})()"


def collect(b):
    """Every reached part's values, read from the app: {(scope, name, sel): [what the page says, one per time seen]}.
    scope is 'shared', 'action' or the screen's ID. Three passes, each opening every screen, sub-page and tab, then
    (on the iPhone) every sheet, alert and action sheet the sample data opens, as test_screens.py › coverage does:
    the iPhone; the iPhone with a session running; the iPhone with a track and two takes on the sample song; the iPad.
    The later passes only add parts the first didn't show, so the values are the plain iPhone's wherever it has the part."""
    sys.path.insert(0, os.path.join(ROOT, 'tests'))
    from test_screens import state_js, REG
    arg = {'inside': INSIDE, 'controls': CONTROLS, 'reasons': [s for s, _ in REASONS]}
    seen = {}
    for w, h, state in ((390, 844, ''), (390, 844, 'session'), (390, 844, 'track'), (820, 1180, '')):
        pg = open_app(b, w, h)
        R = pg.evaluate(REG)
        got = {}

        def read(sid, roots):
            for r in pg.evaluate(READ_JS, dict(arg, screen=sid, roots=roots)):
                got.setdefault(tuple(r['key']), []).append(r)
        if state == 'session': pg.evaluate("newSession()")
        if state == 'track': with_track(pg)
        for s in R['screens']:
            if s['kind'] not in ('Tab', 'Screen', 'Sub-page') or s['status'] != 'Live': continue
            pg.evaluate(state_js(s['key'])); pg.wait_for_timeout(60)
            if pg.evaluate("document.getElementById('app').dataset.screen") == s['id']:
                read(s['id'], ['#app', '#bar', '#dock', '#side'])
        if w < 500 and state != 'session':
            for s in R['screens']:
                if s['kind'] not in ('Sheet', 'Alert', 'Action sheet') or s['status'] != 'Live': continue
                if pg.evaluate(SHEET_JS, s['key'][6:]) == s['id']:
                    pg.wait_for_timeout(60)
                    read(s['id'], ["#layer :is(.sheet,.pk-alert,.pk-actions):not(.pk-leaving)"])
                pg.evaluate(CLEAR_JS)
                pg.wait_for_timeout(30)
        pg.context.close()
        for k, recs in got.items(): seen.setdefault(k, recs)
    return seen


def values(seen):
    """One row of values per register line: {(scope, name, sel): {kit, press, corner, motion, reason}}. A part seen
    in more than one place lists each different value once, so the sheet shows where it varies."""
    out = {}
    many = lambda xs: ' · '.join(sorted(set(xs))) if len(set(xs)) <= 3 else 'varies (%d)' % len(set(xs))
    for key, recs in seen.items():
        parts = {}
        for r in recs: parts.update(part_no(r['kit']))
        press = {r['press'] for r in recs if r['press']}
        for p in press: parts.setdefault(PRESSES[p][0], LABEL[PRESSES[p][0]])
        reasons = [REASONS[r['reason']][1] for r in recs if r['reason'] >= 0]
        out[key] = {
            'kit': kit_cell(parts),
            'press': many([PRESSES[r['press']][1] if r['press'] else 'none' for r in recs]),
            'corner': many(['`' + r['corner'] + '`' if r['corner'].startswith('--') else r['corner'] for r in recs]),
            'motion': many([', '.join('`' + m + '`' for m in r['motion']) or 'none' for r in recs]),
            'reason': '' if parts else (reasons[0] if reasons else ''),
        }
    return out


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


def presses():
    """Q53 the Presses section: KITPRESS's three kinds, read from js/gestures.js, plus the kit's chips and stepper."""
    src = open(GEST, encoding='utf-8').read()
    kp = src[src.index('const KITPRESS = '):]

    def sel(name):
        m = re.search(r'const ' + name + r' =\s*((?:\s*\+?\s*\'[^\']*\')+);', kp)
        return ''.join(re.findall(r"'([^']*)'", m.group(1))) if m else ''
    esc = lambda s: s.replace('|', '\\|')
    rows = [('Glass button', '12 · `.pk-press`', sel('GLASS'), 'Grows 17 pt on its longest side, lights up'),
            ('Button on a glass bar', '15 · `.pk-press-bar`', sel('BAR'), 'Lights up, same size'),
            ('Solid button', '14 · `.pk-press-solid`', sel('SOLID'), 'Shrinks to `--press` (0.93), back on `release`'),
            ('Picking chip', '18 · `.pk-chip` in `.pk-chips.pk-static`', '.chip.pk-chip', 'No press; the colour fades as it\'s picked'),
            ('Note stepper', '24 · `.pk-stepper.pk-glass`', '.pvstep .pk-stepper', 'Its halves are buttons on a glass bar (15)'),
            ('Tab bar bubble', '4 · `.pk-tabbar` (Parts kit 1.4)', '#dock .pk-tabbar > .pk-tab',
             'Touched, a separate Liquid Glass bubble rises out of the tab and follows the finger; the icons under it turn the accent colour, the bar swells (Q58, 3.72)')]
    L = ['## Presses', '',
         'How each kind of button presses (Q53, 3.67). `KITPRESS` in `js/gestures.js` gives a button its kit class by what it is, '
         'so a new button with one of these classes gets the press for free. Every press is the kit\'s own: reused, none new. '
         'Rows highlight instead (D06, `row.press`).', '',
         '| Kind | Kit part | Buttons | Press | Animation | Status |', '|---|---|---|---|---|---|']
    L += ['| %s | %s | `%s` | %s | Reused (the kit\'s) | In use |' % (k, p, esc(s), d) for k, p, s, d in rows]
    L += ['', '<details><summary>Retired (2)</summary>', '',
          '| Kind | Was | Replaced by | Status |', '|---|---|---|---|',
          '| The old tab press | Parts kit 1.3\'s tab bar (part 4): the picked tab\'s highlight swelled 12 × 8 pt into clear glass and the icon under the finger grew to ×1.15 | '
          'The kit\'s Liquid Glass bubble (part 4, Parts kit 1.4.0, `tabBar.bubble`) | Retired · 3.72 |',
          '| The app\'s own press | `PRESS` in `js/gestures.js` (Q33): glass grew on `press`, settled on `release`, lit up with a registered `--lift`; '
          'solid buttons shrank on `:active` with a 0.5 s `--ease-pop` release | The kit\'s parts 12, 14, 15 (`tools/parts-kit/REPLACED.md`) | Retired · 3.67 |',
          '', '</details>', '']
    return L


def motion():
    """Q54 (3.68): the app's own animations that took a named value or a kit spring. Each is reused, none new. Q54's
    record, last checked 5 Nov 2026; each part's own values are read from the app since Q55 (the tables above and below)."""
    rows = [
        ('Row moves', '`.rowc`, `.crow`, `.tkfg`, `.sw .fg`', 'own bounce, 0.22 to 0.35 s', '`gentle` spring'),
        ('Pattern dots and vowel swap', '`.pdraw .pnt`, `.pdraw .prip`, `.pvowel b.swap`', '0.25 to 0.6 s, own bounces', '`ripple` spring'),
        ('Pattern steps', '`.pt`', 'own bounce', '`--ease-knob`'),
        ('Pattern player bubble and dim', '`.phbub`, `#pHud .phscrim`, `.pt .pst > span`', '0.25 to 0.45 s', '`gentle`, `--dur-fade`'),
        ('Pull to refresh', '`#ptr.go .spin`, `main.ptr-snap`', '0.8 s spin, 0.42 s snap', 'kit spinner (`--dur-spin`, `--ease-steps`), `gentle`'),
        ('Launch screen (motion off)', '`#splash`, `#splash .sp-icon`', '0.35 s, 0.45 s', '`--dur-leave`, `--ease-accel`'),
        ('Launch ripple', '`MOTION.LAUNCH` (js/launch.js)', 'numbers in launch.js', 'its own timings, named once in `MOTION.LAUNCH`'),
        ('Card zoom fades', '`MOTION.ZOOM` (js/zoom.js)', '24 numbers in zoom.js', '`MOTION.ms(\'quick\')`, `(\'fade\')` and its own, named in `MOTION.ZOOM`'),
        ('Session clock', '`#layer .sck`, `.clockscrim`', '140 to 300 ms', 'kit part 50: `appear` 250, `leave` 350; Reduce Motion `--dur-reduced`'),
        ('Recall\'s hidden words', '`.hx`, `.hxin .hx`, `.rl.peeking .hx`', '0.22 to 0.35 s', '`--dur-fade`, `--ease-out`'),
        ('Sideways scroll fade, pointer hint', '`[data-edge-fade]`, `.hint`', '0.18 s, 0.25 s', '`--dur-fade`, `--ease-out`'),
        ('Note box', '`.notebox`', '0.3 s', '`--dur-appear`'),
        ('Takes closing', '`VS-054`', '140 ms', '`MOTION.ms(\'close\')`, `MOTION.EASE.accel`'),
        ('Changelog timeline', '`.tl-card`, `.tl-in.seen`, `.tl-more svg.i`', '0.3 to 0.6 s', '`gentle`'),
        ('Changelog now dot', '`.tl-item.now .tl-node::after`', 'pulsed forever', 'three pulses, then rests (as the exercise glow)'),
        ('Rung nudge', '`.rgi.rneed > .rgrow`', '1.1 s', 'the same 1.2 s as `.rgi.rnudge`'),
    ]
    L = ['## Named motion', '',
         'Animations that took a named value or a kit spring in Q54 (3.68), so the app keeps one feel. Every one is reused, '
         'none new. What\'s left written by hand, with its reason, is in `tests/test_values.py`. Last checked 5 Nov 2026.', '',
         '| Animation | Parts | Was | Now | Animation | Status |', '|---|---|---|---|---|---|']
    L += ['| %s | %s | %s | %s | Reused | In use |' % r for r in rows]
    L += ['', '<details><summary>Retired (4)</summary>', '',
          '| Animation | Was | Status |', '|---|---|---|',
          '| `pop` keyframes | unused since the parts kit | Retired · 3.68 |',
          '| `up` keyframes | unused | Retired · 3.68 |',
          '| `pmIn` keyframes | the old pull-up menu, unused since the parts kit\'s menus | Retired · 3.68 |',
          '| The Changelog now dot\'s endless pulse | `lgpulse` infinite | Retired · 3.68 |',
          '', '</details>', '']
    return L


def register():
    """Every part in js/register.js, in order: (scope, name, sel, status, was, group). scope is 'shared', 'action' or
    the screen's ID; group is the area for names by action and 'VS-009 · Song' for a screen's own parts."""
    src = open(REG, encoding='utf-8').read()
    out = [('shared', r[1], r[2], r[4], r[3], '') for r in rows(src[src.index('  shared: ['):src.index('  actions: [')])]
    out += [('action', r[1], r[2], r[4], r[3], r[0]) for r in rows(src[src.index('  actions: ['):src.index('  screens: [')])]
    for blk in re.split(r"\n {6}id: '", src[src.index('  screens: ['):src.index('  flows: [')])[1:]:
        sid = blk[:6]
        nm = re.search(r"\n {6}name: '((?:[^'\\]|\\.)*)'", blk)
        st = re.search(r"\n {6}status: '([^']+)'", blk)
        group = sid + ' · ' + (nm.group(1).replace("\\'", "'") if nm else '') + ('' if not st or st.group(1) == 'Live' else ' (' + st.group(1) + ')')
        if 'parts: [' in blk:
            out += [(sid, r[1], r[2], r[4], r[3], group) for r in rows(blk.split('parts: [', 1)[1])]
    return out


def problems(vals, reg=None):
    """Q55 the sheet's rule: every part the sample data reaches has a kit part or a reason. The parts that break it."""
    return ['%s › %s' % (p[0], p[1]) for p in (reg or register()) if (p[0], p[1], p[2]) in vals
            and not vals[(p[0], p[1], p[2])]['kit'] and not vals[(p[0], p[1], p[2])]['reason']]


def build(vals, reg=None):
    """The sheet's text, from the register (or reg, for the tests) and the values read from the app (values(collect(b)))."""
    esc = lambda s: s.replace('|', '\\|')
    reg = reg or register()
    DASH = {'kit': '', 'press': '—', 'corner': '—', 'motion': '—', 'reason': ''}

    def cells(p):
        v = vals.get((p[0], p[1], p[2]))
        if not v: v = dict(DASH, kit=kit(p[2]))
        return '%s | %s | %s | %s | %s' % (v['kit'], v['press'], v['corner'], v['motion'], v['reason'])
    live = [p for p in reg if p[3] == 'In use']
    missed = [p for p in live if (p[0], p[1], p[2]) not in vals]
    sh = [p for p in reg if p[0] == 'shared']
    ac = [p for p in reg if p[0] == 'action']
    on = [p for p in reg if p[0] not in ('shared', 'action')]
    head = '| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status |'
    L = ['# Element sheet · Vocal Sessions', '',
         'Every named part in the app: its name, where it is named, how the app finds it, the parts kit part it is (by its '
         'gallery number), how it presses, its corner and its motion, and its status. An app\'s own part, with no kit part, '
         'says why. Written by `tools/reference/elements.py` from `js/register.js` and from the app itself (headless, the '
         'tests\' sample data, motion off), so the values are what the page really uses, mapped back to their names; '
         'don\'t edit by hand. The naming rules: [MAINTAINING › Screen IDs › Naming rules](../MAINTAINING.md#naming-rules).', '',
         'A note points at a part as `VS-009 › song-row`; a shared or by-action part is named the same on every screen it shows on.', '',
         '**How to read the values.** Kit part: the gallery number in `tools/parts-kit/README.md` › Parts. Press: how it '
         'presses (the Presses section below). Corner: a named corner (`--r-card` …), `capsule`, `circle` or `none`. Motion: '
         'the springs and named timings its own transitions use (`gentle`, `--ease-out` …), `none` when it doesn\'t move at '
         'rest; a press\'s own motion is in Presses. A part that shows in more than one place lists each value it has '
         '(`a · b`). A dash: the sample data doesn\'t reach it ([Not reached](#not-reached)).', '',
         '**%d shared parts, %d names by action, %d parts named on their screens. %d of %d in use read from the app.**'
         % (len(sh), len(ac), len(on), len(live) - len(missed), len(live)), '']
    L += ['## Shared', '', 'Named wherever they show: the tab bar, Back, Close, the standard roles, fields and links.', '',
          head, '|---|---|---|---|---|---|---|---|']
    L += ['| `%s` | `%s` | %s | %s |' % (p[1], esc(p[2]), cells(p), p[3]) for p in sh] + ['']
    L += ['## By action', '', 'Wherever the action shows, its button gets this name. A screen\'s own parts and the shared ones win over these.', '']
    area = None
    for p in ac:
        if p[5] != area:
            area = p[5]
            L += ['', '### ' + area, '', head, '|---|---|---|---|---|---|---|---|']
        L.append('| `%s` | `%s` | %s | %s |' % (p[1], esc(p[2]), cells(p), p[3]))
    L += [''] + presses() + [''] + motion()
    L += ['## On their screens', '']
    group = None
    for p in on:
        if p[5] != group:
            if group: L.append('')
            group = p[5]
            L += ['### ' + group, '', '| Name | Found by | Kit part | Press | Corner | Motion | Reason | Status | Was |',
                  '|---|---|---|---|---|---|---|---|---|']
        L.append('| `%s` | `%s` | %s | %s | %s |' % (p[1], esc(p[2]), cells(p), p[3], p[4]))
    L += ['', '## Not reached', '',
          'Parts in use that the sample data doesn\'t show (an iPad or Mac layout, a state such as recording, the floating '
          'window, the session clock), so their values are a dash. Their kit part, if any, is read from how they\'re found. '
          'Reaching more of them is a change to `collect()` in `tools/reference/elements.py`.', '',
          '<details><summary>Not reached (%d)</summary>' % len(missed), '']
    L += ['- `%s`' % (p[1] if p[0] in ('shared', 'action') else p[0] + ' › ' + p[1]) + (' (by action: `%s`)' % esc(p[2]) if p[0] == 'action' else '') for p in missed]
    L += ['', '</details>']
    return '\n'.join(L).rstrip() + '\n'


def sheet(b=None):
    """Collect from the app and build the sheet's text. Opens its own headless Chromium when b is None."""
    if b is not None:
        v = values(collect(b))
        return build(v), v
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        try:
            return sheet(br)
        finally:
            br.close()


if __name__ == '__main__':
    text, vals = sheet()
    bad = problems(vals)
    if bad: print('no kit part and no reason (add one to REASONS): ' + ', '.join(bad))
    if '--check' in sys.argv:
        same = os.path.exists(OUT) and open(OUT, encoding='utf-8').read() == text
        print('reference/elements.md is ' + ('up to date' if same else 'out of date: run python3 tools/reference/elements.py'))
        sys.exit(0 if same else 1)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(text)
    print('wrote reference/elements.md')
