"""
prose Language — Master Benchmark Runner
Tests 10 fundamental capabilities against Python and Node.js
"""
import subprocess, sys, os, time, json

BENCHMARKS = [
    ("01_fibonacci",    "Fibonacci Recursion",    "fib(30)"),
    ("02_primes",       "Prime Sieve to 50,000",   "count primes"),
    ("03_bubblesort",   "Bubble Sort (1000 nums)", "sort list"),
    ("04_palindrome",   "Palindrome Check x10,000","string check"),
    ("05_wordcount",    "Word Frequency Count",    "dict ops"),
    ("06_factorial",    "Factorial(20) x10,000",   "math recursion"),
    ("07_fizzbuzz",     "FizzBuzz to 100,000",     "conditional loop"),
    ("08_listsum",      "List Sum (100,000 nums)", "arithmetic"),
    ("09_stringreverse","String Reverse x50,000",  "string ops"),
    ("10_power",        "Power(2,30) x50,000",     "math ops"),
]

PAD = 32
COL = 14

def run(cmd, cwd):
    t0 = time.perf_counter()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=cwd)
    elapsed = time.perf_counter() - t0
    return elapsed, result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def fmt_time(t):
    if t is None: return "N/A"
    if t < 0.001: return "< 0.001s"
    return f"{t:.4f}s"

def speedup(base, val):
    if val == 0: return "∞"
    r = base / val
    return f"{r:.1f}x"

print()
print("=" * 80)
print("  prose LANGUAGE — HEAD-TO-HEAD BENCHMARK vs Python 3 and Node.js")
print("=" * 80)
print(f"  {'Test':<{PAD}} {'Python':>{COL}} {'Node.js':>{COL}} {'prose (interp)':>{COL}} {'prose (build)':>{COL}}")
print("-" * 80)

bench_dir = os.path.dirname(os.path.abspath(__file__))
plain_py  = os.path.join(bench_dir, "..", "prose.py")

results = []
for slug, name, desc in BENCHMARKS:
    py_t,  py_ok,  _, _  = run(f"python {slug}_py.py",  bench_dir)
    js_t,  js_ok,  _, _  = run(f"node {slug}_js.js",    bench_dir)
    pi_t,  pi_ok,  _, ei = run(f"python \"{plain_py}\" {slug}_prose.prose", bench_dir)

    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    
    # build
    built_file = os.path.join(bench_dir, f"{slug}_prose.py")
    build_proc = subprocess.run(
        f"python \"{plain_py}\" build {slug}_prose.prose",
        shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, cwd=bench_dir)
    if build_proc.returncode == 0 and os.path.exists(built_file):
        pb_t, pb_ok, _, _ = run(f"python {slug}_prose.py", bench_dir)
    else:
        pb_t, pb_ok = None, False

    label = f"[{desc}] {name}"
    print(f"  {label:<{PAD}} {fmt_time(py_t):>{COL}} {fmt_time(js_t):>{COL}} {fmt_time(pi_t):>{COL}} {fmt_time(pb_t):>{COL}}")
    results.append((name, py_t, js_t, pi_t, pb_t))

print("=" * 80)
print()

# Summary
avg_py = sum(r[1] for r in results) / len(results)
avg_js = sum(r[2] for r in results) / len(results)
avg_pi = sum(r[3] for r in results) / len(results)
pb_vals = [r[4] for r in results if r[4] is not None]
avg_pb = sum(pb_vals) / len(pb_vals) if pb_vals else None

print("  AVERAGES:")
print(f"    Python:          {fmt_time(avg_py)}")
print(f"    Node.js:         {fmt_time(avg_js)}")
print(f"    prose (interp):  {fmt_time(avg_pi)}")
print(f"    prose (build):   {fmt_time(avg_pb)}")
print()
print(f"  Transpiler speedup over interpreter: {speedup(avg_pi, avg_pb)}")
print(f"  prose (build) vs Python:             {speedup(avg_pb, avg_py)} {'slower' if avg_pb > avg_py else 'FASTER'}")
print(f"  prose (build) vs Node.js:            {speedup(avg_pb, avg_js)} {'slower' if avg_pb > avg_js else 'FASTER'}")
print("=" * 80)
print()
