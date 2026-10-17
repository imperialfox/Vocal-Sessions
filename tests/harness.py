"""Shared set-up for the Vocal Sessions tests.

Every test file has a run(browser, t) function. `t` collects results:
    t.ok(condition, 'what should be true')
Run everything with:  python tests/run.py
"""
import os, json, threading, functools, datetime as dt
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_PATH = os.path.abspath(os.environ.get('VS_APP', os.path.join(ROOT, 'index.html')))

# The app is served over http://localhost, like GitHub Pages serves it (pull to refresh fetches the page,
# which a file:// address can't do). One small server per folder, started on first use.
class _Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store'); super().end_headers()
_servers = {}
def url(path):
    path = os.path.abspath(path); folder = os.path.dirname(path)
    if folder not in _servers:
        srv = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(_Quiet, directory=folder))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        _servers[folder] = srv
    return f'http://localhost:{_servers[folder].server_address[1]}/{os.path.basename(path)}'

def offline(path):
    """Switch the server for this folder off: a real "no connection" for the page and its offline helper.
    (Playwright's set_offline doesn't reach service workers.)"""
    folder = os.path.dirname(os.path.abspath(path)); srv = _servers[folder]
    srv.shutdown(); srv.server_close()

def online(path):
    """Switch it back on, on the same port, so the address (and the saved offline copy) stays the same."""
    folder = os.path.dirname(os.path.abspath(path)); port = _servers[folder].server_address[1]
    srv = ThreadingHTTPServer(('127.0.0.1', port), functools.partial(_Quiet, directory=folder))
    threading.Thread(target=srv.serve_forever, daemon=True).start(); _servers[folder] = srv
OUT = os.path.join(ROOT, 'tests', 'output')
FIX = os.path.join(ROOT, 'tests', 'fixtures')
os.makedirs(OUT, exist_ok=True)

UA_IPHONE = ('Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 '
             '(KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1')

now = dt.datetime.now()
def iso(d): return d.astimezone(dt.timezone.utc).isoformat().replace('+00:00', 'Z')

def sample():
    """Three sessions, a custom exercise and a song, shaped like data from version 3.1."""
    sess = []
    for i, (days_ago, mins, rot) in enumerate([(9, 40, {'rung': 2}), (8, 35, {'vertical': 1}), (2, 30, {'rung': 3, 'hinge': 1})]):
        d = now - dt.timedelta(days=days_ago)
        sess.append({"id": f"s{i}", "date": iso(d), "end": iso(d + dt.timedelta(minutes=mins)), "mins": mins,
                     "f": {"slides": 3, "humming": 3, "lip": 2, "straw": 3}, "fNote": "old note" if i == 0 else "",
                     "rot": rot, "rNote": "", "rotNames": {}, "songName": "", "rate": {}, "takes": []})
    return {"v2": True, "months": {now.strftime('%Y-%m'): 135},
            "ex": {"rung": {"n": 4, "last": iso(now - dt.timedelta(days=2))}, "falsetto": {"n": 1, "last": None},
                   "slides": {"n": 3, "last": iso(now - dt.timedelta(days=2))}, "humming": {"n": 3, "last": iso(now - dt.timedelta(days=2))}},
            "custom": [{"id": "c0_x", "name": "Siren", "focus": "register"}],
            "songs": [{"id": "g_1", "name": "Versace on the Floor · bridge"}],
            "sessions": sess, "lastBackup": iso(now - dt.timedelta(days=20))}

def with_song_practice():
    d = sample()
    d['songSessions'] = [{"id": "sp1", "kind": "song", "date": iso(now - dt.timedelta(days=1)), "end": iso(now - dt.timedelta(days=1)),
                          "mins": 12, "songId": "g_1", "songName": "Versace on the Floor · bridge", "takes": [], "how": ["Warm"], "howNote": ""}]
    return d

OLD_DRAFT = {"start": int((now - dt.timedelta(minutes=12)).timestamp() * 1000), "f": {"slides": 2}, "fNote": "", "fEnd": None,
             "rot": {}, "rNote": "", "rEnd": None, "song": None, "rate": {}, "takes": []}

# a small recording, so backups carry audio
ADD_TAKE = """async(id)=>{const b=new Blob([new Uint8Array(3000).map((_,i)=>i%251)],{type:'audio/mp4'});
  await putTake({id:id||'t1',songId:'g_1',created:Date.now()-864e5,len:12,size:b.size,type:'audio/mp4',blob:b,star:false,note:{w:['Breathy'],t:'Ran out of air'}});
  await refreshTakes();rerender();}"""

SEED = "o=>{localStorage.clear();if(o)localStorage.setItem('vocalTracker',JSON.stringify(o))}"


class T:
    """Collects results for one test file."""
    def __init__(self, name):
        self.name, self.passed, self.fails, self.errors = name, 0, [], []

    def ok(self, cond, msg):
        if cond: self.passed += 1
        else: self.fails.append(msg)
        print(('  pass  ' if cond else '  FAIL  ') + msg, flush=True)

    def page(self, b, w=390, h=844, sc='light', touch=False, ua=UA_IPHONE, data='sample', init=None, ctx_args=None):
        """A fresh app page. data='sample' seeds sample(); None leaves the app empty; a dict seeds that dict."""
        args = dict(viewport={'width': w, 'height': h}, device_scale_factor=2 if w < 500 else 1, color_scheme=sc,
                    has_touch=touch, accept_downloads=True, timezone_id='Europe/London', locale='en-GB')
        if ua: args['user_agent'] = ua
        args.update(ctx_args or {})
        ctx = b.new_context(**args)
        # motion off by default, so nothing waits on springs; a test can turn it back on with its own init
        ctx.add_init_script("try{localStorage.setItem('vocalMotion','0')}catch(e){}")
        if init: ctx.add_init_script(init)
        pg = ctx.new_page()
        tag = f'{self.name} {w}x{h}'
        pg.on('pageerror', lambda e: self.errors.append(f'{tag}: {str(e).splitlines()[0]}'))
        pg.on('console', lambda m: self.errors.append(f'{tag} console: {m.text}') if m.type == 'error' else None)
        pg.goto(url(APP_PATH))
        if data is not None:
            pg.evaluate(SEED, sample() if data == 'sample' else data)
        else:
            pg.evaluate(SEED, None)
        pg.reload()
        ready(pg)
        return pg

    def shot(self, pg, name, **kw):
        pg.screenshot(path=os.path.join(OUT, f'{self.name}-{name}.png'), **kw)


def ready(pg):
    """Wait for the launch screen to finish (and, with motion on, Today's launch ripple: 3.13)."""
    pg.wait_for_function("!document.getElementById('splash')&&!(typeof LAUNCH!=='undefined'&&LAUNCH.busy())", timeout=15000)
    pg.wait_for_timeout(150)

def fix(name): return os.path.join(FIX, name)
