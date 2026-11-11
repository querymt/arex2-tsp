import math
import random
import time

SEARCH_BUDGET = 1.4  # seconds; scorer limit is 2.0s per call


def solve(points):
    """points: list of (x, y) floats in [0, 1000]^2.

    Return the visiting order of a closed tour: a list containing every index
    0..len(points)-1 exactly once. Must finish within the time limit in
    openspec/changes/improve-tsp/objective.md.
    """
    n = len(points)
    if n <= 3:
        return list(range(n))

    t0 = time.perf_counter()
    deadline = t0 + SEARCH_BUDGET
    rng = random.Random(12345)

    # Distance matrix.
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = points[i]
        row = dist[i]
        for j in range(i + 1, n):
            xj, yj = points[j]
            d = math.hypot(xi - xj, yi - yj)
            row[j] = d
            dist[j][i] = d

    # Nearest-neighbour lists (k closest nodes per node).
    k = min(16, n - 1)
    neigh = []
    for i in range(n):
        row = dist[i]
        order = sorted(range(n), key=lambda j: row[j])
        neigh.append([j for j in order if j != i][:k])

    # --- construction: nearest neighbour from a seeded random start ---
    start = rng.randrange(n)
    unvisited = [True] * n
    unvisited[start] = False
    tour = [start]
    for _ in range(n - 1):
        cur = tour[-1]
        row = dist[cur]
        best = -1
        bd = 1e300
        for j in range(n):
            if unvisited[j] and row[j] < bd:
                bd = row[j]
                best = j
        tour.append(best)
        unvisited[best] = False

    pos = [0] * n
    for idx, node in enumerate(tour):
        pos[node] = idx

    _two_opt(tour, pos, dist, neigh, deadline)
    best_tour = tour[:]
    best_len = _tour_length(tour, dist)

    # --- iterated local search: double-bridge perturbation + re-optimise ---
    while time.perf_counter() < deadline:
        cur = best_tour[:]
        _double_bridge(cur, rng)
        cpos = [0] * n
        for idx, node in enumerate(cur):
            cpos[node] = idx
        _two_opt(cur, cpos, dist, neigh, deadline)
        length = _tour_length(cur, dist)
        if length < best_len - 1e-9:
            best_len = length
            best_tour = cur[:]

    return best_tour


def _double_bridge(tour, rng):
    n = len(tour)
    if n < 8:
        return
    cuts = sorted(rng.sample(range(1, n), 3))
    a, b, c = cuts
    new = tour[:a] + tour[b:c] + tour[:b][a:] + tour[c:]
    tour[:] = new


def _two_opt(tour, pos, dist, neigh, deadline):
    n = len(tour)
    dont_look = [False] * n
    improved = True
    while improved:
        improved = False
        for a in range(n):
            node_a = tour[a]
            if dont_look[node_a]:
                continue
            found = False
            nxt = tour[a + 1] if a + 1 < n else tour[0]
            da = dist[node_a][nxt]
            for node_b in neigh[node_a]:
                pb = pos[node_b]
                nb = tour[pb + 1] if pb + 1 < n else tour[0]
                if nb == node_a or node_b == nxt:
                    continue
                delta = dist[node_a][node_b] + dist[nxt][nb] - da - dist[node_b][nb]
                if delta < -1e-9:
                    # 2-opt: replace edges (a,a+1) and (pb,pb+1);
                    # reverse the segment between a+1 and pb (cyclically).
                    i = (a + 1) % n
                    j = pb
                    count = (j - i) % n + 1
                    for m in range(count // 2):
                        p1 = (i + m) % n
                        p2 = (j - m) % n
                        t1 = tour[p1]
                        t2 = tour[p2]
                        tour[p1] = t2
                        tour[p2] = t1
                        pos[t1] = p2
                        pos[t2] = p1
                    improved = True
                    found = True
                    break
            if not found:
                dont_look[node_a] = True
        if time.perf_counter() > deadline:
            return


def _tour_length(tour, dist):
    total = 0.0
    prev = tour[-1]
    for cur in tour:
        total += dist[prev][cur]
        prev = cur
    return total
