"""Run the Vocal Sessions test suite.

    python tests/run.py               everything
    python tests/run.py backup flows  only those files (test_backup.py, test_flows.py)
    VS_FUZZ_STEPS=2000 python tests/run.py fuzz   a longer random-tap run
    VS_APP=path/to/index.html python tests/run.py  test another copy of the app

Exits with 1 if anything fails, so GitHub shows a red cross.
Screenshots go to tests/output/.
"""
import sys, os, time, importlib, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
import harness

ORDER = ['release', 'content', 'flows', 'progress', 'edge', 'backup', 'songs', 'data', 'changelog', 'recording', 'layout', 'fuzz']

def main():
    picked = [a for a in sys.argv[1:] if not a.startswith('-')] or ORDER
    unknown = [p for p in picked if p not in ORDER]
    if unknown:
        print('Unknown test files:', ', '.join(unknown), '\nChoose from:', ', '.join(ORDER)); return 2
    print(f'Testing {harness.APP_PATH}\n')
    results, t0 = [], time.time()
    with sync_playwright() as p:
        for name in [n for n in ORDER if n in picked]:
            mod = importlib.import_module('test_' + name)
            t = harness.T(name)
            print(f'── {name} ' + '─' * (40 - len(name)), flush=True)
            b = p.chromium.launch(args=getattr(mod, 'LAUNCH_ARGS', []))
            s = time.time()
            try:
                mod.run(b, t)
            except Exception:
                t.fails.append('crashed: ' + traceback.format_exc().strip().splitlines()[-1])
                traceback.print_exc()
            finally:
                b.close()
            for e in t.errors:
                t.fails.append('JavaScript error: ' + e)
                print('  FAIL  JavaScript error: ' + e)
            print(f'  {t.passed} passed, {len(t.fails)} failed in {time.time() - s:.0f}s\n', flush=True)
            results.append(t)
    failed = [(t.name, f) for t in results for f in t.fails]
    print('═' * 44)
    print(f'{sum(t.passed for t in results)} passed, {len(failed)} failed in {time.time() - t0:.0f}s')
    for n, f in failed:
        print(f'  ✗ {n}: {f}')
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(main())
