"""The version number agrees everywhere: the app, the README and the changelog."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
import release

def run(b, t):
    for msg in release.problems():
        t.ok(False, msg)
    v, d = release.current()
    t.ok(True, f'version {v} · {d} matches in the app, README and CHANGELOG')
