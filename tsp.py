"""Euclidean TSP heuristic solver.

Strategy: nearest-neighbor construction (best of several starts) followed by
local search alternating 2-opt edge exchanges and Or-opt segment relocations,
bounded by a wall-clock deadline.
"""

import math
import random
import time

TIME_BUDGET = 1.5  # seconds; scorer limit is 2.0s per solve() call

_deadline = 0.0  # set at the start of each solve() call


def _dist_matrix(points):
    n = len(points)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = points[i]
        di = dist[i]
        for j in range(i + 1, n):
            d = math.hypot(xi - points[j][0], yi - points[j][1])
            di[j] = d
            dist[j][i] = d
    return dist


def _tour_length(points, tour):
    total = 0.0
    n = len(tour)
    for i in range(n):
        ax, ay = points[tour[i]]
        bx, by = points[tour[(i + 1) % n]]
        total += math.hypot(ax - bx, ay - by)
    return total


def _nearest_neighbor(dist, start):
    n = len(dist)
    unvisited = bytearray(n)
    for i in range(n):
        unvisited[i] = 1
    tour = [start]
    unvisited[start] = 0
    cur = start
    row = dist[cur]
    remaining = n - 1
    while remaining:
        best_j = -1
        best_d = float("inf")
        for j in range(n):
            if unvisited[j]:
                d = row[j]
                if d < best_d:
                    best_d = d
                    best_j = j
        tour.append(best_j)
        unvisited[best_j] = 0
        cur = best_j
        row = dist[cur]
        remaining -= 1
    return tour


def _two_opt(tour, dist):
    """2-opt edge exchanges in place; returns True if the tour changed."""
    n = len(tour)
    changed = False
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            a = tour[i]
            b = tour[i + 1]
            ab = dist[a][b]
            for j in range(i + 2, n):
                c = tour[j]
                d = tour[(j + 1) % n]
                if a == d:
                    continue
                if dist[a][c] + dist[b][d] < ab + dist[c][d] - 1e-9:
                    tour[i + 1:j + 1] = tour[i + 1:j + 1][::-1]
                    ab = dist[a][b]
                    improved = True
                    changed = True
            if time.perf_counter() > _deadline:
                return changed
    return changed


def _or_opt(tour, dist):
    """Relocate segments of length 1..3 to better positions (first improvement)."""
    n = len(tour)
    improved = True
    while improved:
        improved = False
        for seg_len in (1, 2, 3):
            for i in range(n):
                seg = [tour[(i + k) % n] for k in range(seg_len)]
                if len(set(seg)) < seg_len or n - seg_len < 1:
                    continue
                prev = tour[(i - 1) % n]
                nxt = tour[(i + seg_len) % n]
                if prev in seg or nxt in seg:
                    continue
                removal_cost = (dist[prev][seg[0]] + dist[seg[-1]][nxt]
                                - dist[prev][nxt])
                if removal_cost <= 1e-9:
                    continue
                seg_set = set(seg)
                others = [x for x in tour if x not in seg_set]
                mm = len(others)
                if mm < 2:
                    continue
                gain = 0.0
                best_p = -1
                for p in range(mm):
                    u = others[p]
                    v = others[(p + 1) % mm]
                    insert_cost = (dist[u][seg[0]] + dist[seg[-1]][v]
                                   - dist[u][v])
                    g = removal_cost - insert_cost
                    if g > gain + 1e-9:
                        gain = g
                        best_p = p + 1
                if best_p >= 0:
                    tour[:] = others[:best_p] + seg + others[best_p:]
                    improved = True
                    break
        if time.perf_counter() > _deadline:
            return True
    return False


def _local_search(tour, dist):
    """Alternate 2-opt and Or-opt until neither improves (or deadline)."""
    while True:
        c1 = _two_opt(tour, dist)
        c2 = _or_opt(tour, dist)
        if time.perf_counter() > _deadline or not (c1 or c2):
            return tour


def _double_bridge(tour, rng):
    n = len(tour)
    if n < 5:
        return tour[:]
    p1, p2, p3 = sorted(rng.sample(range(1, n), 3))
    return tour[0:p1] + tour[p2:p3] + tour[p1:p2] + tour[p3:]


def solve(points):
    """points: list of (x, y) floats in [0, 1000]^2.

    Return the visiting order of a closed tour: a list containing every index
    0..len(points)-1 exactly once. Must finish within the time limit in
    openspec/changes/improve-tsp/objective.md.
    """
    global _deadline
    n = len(points)
    if n <= 1:
        return list(range(n))
    _deadline = time.perf_counter() + TIME_BUDGET
    dist = _dist_matrix(points)
    best_tour = None
    best_len = float("inf")
    for start in range(min(n, 3)):
        tour = _nearest_neighbor(dist, start)
        tour = _local_search(tour, dist)
        length = _tour_length(points, tour)
        if length < best_len:
            best_len = length
            best_tour = tour[:]
        if time.perf_counter() > _deadline:
            break
    # Iterated local search: double-bridge perturbation of the best tour,
    # seeded so rounds are comparable.
    rng = random.Random(20260101)
    while time.perf_counter() < _deadline:
        cand = _double_bridge(best_tour, rng)
        cand = _local_search(cand, dist)
        length = _tour_length(points, cand)
        if length < best_len - 1e-9:
            best_len = length
            best_tour = cand[:]
    return best_tour
