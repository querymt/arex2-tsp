#!/usr/bin/env python3
"""Scorer: mean closed-tour length over fixed random instances (lower is better).

usage: python3 tests/score.py [solver_file]     (default: tsp.py in the repo root)
The LAST stdout line is the score. Per-instance details go to stderr.
"""
import json
import operator
import os
import random
import subprocess
import sys

N = 200                      # points per instance
SEEDS = (11, 22, 33, 44, 55)  # fixed instances
LIMIT = 2.0                  # seconds allowed for one solve() call
PENALTY = 1_000_000.0        # length charged for an invalid / failed / too slow instance
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHILD = r'''
import importlib.util, json, sys, time
req = json.load(sys.stdin)
sys.path.insert(0, req["root"])
spec = importlib.util.spec_from_file_location("solver", req["path"])
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
pts = [tuple(p) for p in req["points"]]
t0 = time.perf_counter()
tour = mod.solve(pts)
dt = time.perf_counter() - t0
sys.stdout.write("\n" + json.dumps({"tour": [int(i) for i in tour], "dt": dt}) + "\n")
'''


def instance(seed):
    rng = random.Random(seed)
    return [(rng.random() * 1000.0, rng.random() * 1000.0) for _ in range(N)]


def tour_length(points, tour):
    total = 0.0
    for i in range(len(tour)):
        ax, ay = points[tour[i]]
        bx, by = points[tour[(i + 1) % len(tour)]]
        total += ((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5
    return total


def run_one(points, path):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    req = json.dumps({"points": points, "path": path, "root": ROOT})
    try:
        proc = subprocess.run([sys.executable, "-c", CHILD], input=req, capture_output=True,
                              text=True, timeout=LIMIT + 10, cwd=ROOT, env=env)
    except subprocess.TimeoutExpired:
        return None, "killed: far over the %.1fs limit" % LIMIT
    if proc.returncode != 0:
        tail = proc.stderr.strip().splitlines()[-3:]
        return None, "solver crashed: " + " | ".join(tail)
    try:
        out = json.loads(proc.stdout.strip().splitlines()[-1])
        tour = [operator.index(i) for i in out["tour"]]
    except Exception as exc:  # noqa: BLE001
        return None, "unreadable result: %r" % (exc,)
    if out["dt"] > LIMIT:
        return None, "too slow: %.2fs > %.1fs" % (out["dt"], LIMIT)
    if sorted(tour) != list(range(len(points))):
        return None, "not a permutation of 0..%d" % (len(points) - 1)
    return (tour_length(points, tour), out["dt"]), None


def main():
    path = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(ROOT, "tsp.py")
    lengths = []
    for k, seed in enumerate(SEEDS):
        res, err = run_one(instance(seed), path)
        if err:
            print("instance %d: INVALID (%s) -> penalty" % (k, err), file=sys.stderr)
            lengths.append(PENALTY)
        else:
            print("instance %d: length=%.1f time=%.2fs" % (k, res[0], res[1]), file=sys.stderr)
            lengths.append(res[0])
    print("%.2f" % (sum(lengths) / len(lengths)))


if __name__ == "__main__":
    main()
