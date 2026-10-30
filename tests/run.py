"""Run the Vocal Sessions test suite.

    python tests/run.py               everything, several test files side by side (before every push)
    python tests/run.py quick         everything except the every-size layout check and the random taps (while building)
    python tests/run.py backup flows  only those files (test_backup.py, test_flows.py)
    python tests/run.py --one-at-a-time   everything, one file after another, as before
    VS_JOBS=2 python tests/run.py     how many run side by side (default: twice the processor count, at least 2)
    VS_FUZZ_STEPS=2000 python tests/run.py fuzz   a longer random-tap run
    VS_APP=path/to/index.html python tests/run.py  test another copy of the app

The layout check runs each screen size, and the random taps each seed, as its own job, so the longest single job is
about a minute. Every job has its own browser and its own copy of the app's server, so they can't affect each other.
Exits with 1 if anything fails, so GitHub shows a red cross. Screenshots go to tests/output/.
"""
import sys, os, time, json, importlib, traceback, subprocess, tempfile, concurrent.futures as cf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ORDER = ['release', 'content', 'flows', 'progress', 'edge', 'backup', 'songs', 'data', 'safety', 'changelog', 'recording', 'sections', 'recall', 'fixes', 'lyrics', 'window', 'details', 'launch', 'zoom', 'coach', 'clock', 'track', 'waveform', 'integrity', 'batch12', 'settings', 'search', 'native', 'hig', 'marks', 'layout', 'fuzz']
QUICK = [n for n in ORDER if n not in ('layout', 'fuzz')]
HERE = os.path.abspath(__file__)


def run_file(name):
    """Run one test file in this process (in a job, or one at a time). Returns its harness.T."""
    from playwright.sync_api import sync_playwright
    import harness
    with sync_playwright() as p:
        mod = importlib.import_module('test_' + name)
        t = harness.T(name)
        b = p.chromium.launch(args=getattr(mod, 'LAUNCH_ARGS', []))
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
    return t


def jobs_for(names):
    """Split the slow files into small jobs: one per layout size and one per random-tap seed."""
    out = []
    for n in names:
        if n == 'layout':
            import test_layout
            out += [(f'layout · {s[0]}', n, {'VS_LAYOUT_SIZES': s[0]}) for s in test_layout.SIZES]
        elif n == 'fuzz':
            for s in os.environ.get('VS_FUZZ_SEEDS', '11,12,13,14').split(','):
                out.append((f'fuzz · seed {s}', n, {'VS_FUZZ_SEEDS': s}))
        else:
            out.append((n, n, {}))
    # the slowest first, so they don't hold up the end
    slow = {'fuzz': 0, 'layout': 1, 'batch12': 1, 'songs': 2, 'sections': 3, 'backup': 4, 'flows': 5, 'data': 6}
    return sorted(out, key=lambda j: slow.get(j[1], 9))


def run_job(job):
    label, name, env = job
    fd, res = tempfile.mkstemp(suffix='.json'); os.close(fd)
    e = dict(os.environ, VS_RESULT=res, PYTHONUNBUFFERED='1', **env)
    s = time.time()
    p = subprocess.run([sys.executable, HERE, '--job', name], env=e, capture_output=True, text=True)
    try:
        r = json.load(open(res, encoding='utf-8'))
    except Exception:
        r = {'passed': 0, 'fails': ['the job stopped before finishing: ' + (p.stderr.strip().splitlines() or ['no output'])[-1]]}
    os.remove(res)
    return label, name, r, p.stdout + (p.stderr if p.returncode not in (0, 1) else ''), time.time() - s


def main():
    args = sys.argv[1:]
    if '--job' in args:  # inside a job: run one file and hand its results back
        t = run_file(args[args.index('--job') + 1])
        json.dump({'passed': t.passed, 'fails': t.fails}, open(os.environ['VS_RESULT'], 'w', encoding='utf-8'))
        return 0
    words = [a for a in args if not a.startswith('-')]
    picked = QUICK if words == ['quick'] else words or ORDER
    unknown = [p for p in picked if p not in ORDER]
    if unknown:
        print('Unknown test files:', ', '.join(unknown), '\nChoose from:', ', '.join(ORDER), 'or quick'); return 2
    picked = [n for n in ORDER if n in picked]
    import harness
    print(f'Testing {harness.APP_PATH}\n')
    t0, results = time.time(), []

    if '--one-at-a-time' in args:
        for name in picked:
            print(f'── {name} ' + '─' * (40 - len(name)), flush=True)
            s = time.time(); t = run_file(name)
            print(f'  {t.passed} passed, {len(t.fails)} failed in {time.time() - s:.0f}s\n', flush=True)
            results.append((name, t.passed, t.fails))
    else:
        jobs = jobs_for(picked)
        n = int(os.environ.get('VS_JOBS') or max(2, 2 * (os.cpu_count() or 1)))
        print(f'{len(jobs)} jobs, {min(n, len(jobs))} at a time\n', flush=True)
        with cf.ThreadPoolExecutor(n) as ex:
            for label, name, r, out, secs in (f.result() for f in cf.as_completed([ex.submit(run_job, j) for j in jobs])):
                print(f'── {label} ' + '─' * max(2, 40 - len(label)), flush=True)
                print(out.rstrip(), flush=True)
                print(f'  {r["passed"]} passed, {len(r["fails"])} failed in {secs:.0f}s\n', flush=True)
                results.append((label, r['passed'], r['fails']))

    failed = [(n, f) for n, _, fs in results for f in fs]
    print('═' * 44)
    print(f'{sum(p for _, p, _ in results)} passed, {len(failed)} failed in {time.time() - t0:.0f}s')
    for n, f in failed:
        print(f'  ✗ {n}: {f}')
        # on GitHub, each failure also shows as an annotation on the run's summary page
        if os.environ.get('GITHUB_ACTIONS'): print(f'::error title={n}::{f}'.replace('\n', ' '))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
