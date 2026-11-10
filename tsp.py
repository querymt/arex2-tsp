import math
import random
import time


def solve(points):
    """points: list of (x, y) floats in [0, 1000]^2.

    Return the visiting order of a closed tour: a list containing every index
    0..len(points)-1 exactly once. Must finish within the time limit in
    openspec/changes/improve-tsp/objective.md.
    """
    n = len(points)
    if n <= 2:
        return list(range(n))

    # Precompute distance matrix for fast delta evaluations.
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = points[i]
        for j in range(i + 1, n):
            xj, yj = points[j]
            d = math.hypot(xi - xj, yi - yj)
            dist[i][j] = d
            dist[j][i] = d

    def tour_length(tour):
        total = 0.0
        for i in range(n):
            total += dist[tour[i]][tour[(i + 1) % n]]
        return total

    def two_opt(tour, deadline):
        improved = True
        while improved:
            improved = False
            for i in range(n - 1):
                if time.perf_counter() > deadline:
                    return tour
                a = tour[i]
                b = tour[(i + 1) % n]
                for j in range(i + 2, n):
                    c = tour[j]
                    d = tour[(j + 1) % n]
                    delta = dist[a][c] + dist[b][d] - dist[a][b] - dist[c][d]
                    if delta < -1e-10:
                        tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                        improved = True
        return tour

    def nearest_neighbour(start):
        remaining = set(range(n))
        tour = [start]
        remaining.remove(start)
        while remaining:
            nxt = min(remaining, key=lambda j: dist[tour[-1]][j])
            tour.append(nxt)
            remaining.remove(nxt)
        return tour

    def cheapest_insertion():
        best_d = float('inf')
        best_pair = (0, 1)
        for i in range(n):
            for j in range(i + 1, n):
                if dist[i][j] < best_d:
                    best_d = dist[i][j]
                    best_pair = (i, j)
        tour = [best_pair[0], best_pair[1]]
        remaining = set(range(n)) - set(best_pair)
        while remaining:
            best_cost = float('inf')
            best_pt = None
            best_pos = None
            for p in remaining:
                for pos in range(len(tour)):
                    a = tour[pos]
                    b = tour[(pos + 1) % len(tour)]
                    cost = dist[p][a] + dist[p][b] - dist[a][b]
                    if cost < best_cost:
                        best_cost = cost
                        best_pt = p
                        best_pos = pos
            tour.insert(best_pos + 1, best_pt)
            remaining.remove(best_pt)
        return tour

    def double_bridge_kick(tour, rng):
        cuts = sorted(rng.sample(range(n), 4))
        a, b, c, d = cuts
        seg1 = tour[:a + 1]
        seg2 = tour[a + 1:b + 1]
        seg3 = tour[b + 1:c + 1]
        seg4 = tour[c + 1:]
        return seg1 + seg3 + seg2 + seg4

    def or_opt_kick(tour, rng):
        length = rng.choice([1, 2, 3])
        start = rng.randrange(n)
        seg = tour[start:start + length]
        rest = tour[:start] + tour[start + length:]
        pos = rng.randrange(len(rest))
        if rng.random() < 0.5:
            seg = list(reversed(seg))
        return rest[:pos] + seg + rest[pos:]

    def random_k_opt(tour, rng, k):
        cuts = sorted(rng.sample(range(n), k))
        segs = []
        prev = 0
        for c in cuts:
            segs.append(tour[prev:c + 1])
            prev = c + 1
        segs.append(tour[prev:])
        perm = list(range(len(segs)))
        rng.shuffle(perm)
        new_tour = []
        for idx, s in enumerate(perm):
            seg = segs[s]
            if idx % 2 == 1:
                seg = list(reversed(seg))
            new_tour.extend(seg)
        return new_tour

    def segment_reverse_kick(tour, rng):
        length = rng.randint(3, min(50, n - 1))
        start = rng.randrange(n - length + 1)
        seg = tour[start:start + length]
        return tour[:start] + list(reversed(seg)) + tour[start + length:]

    def multi_fragment_kick(tour, rng, num_frags):
        cuts = sorted(rng.sample(range(n), num_frags))
        segs = []
        prev = 0
        for c in cuts:
            segs.append(tour[prev:c + 1])
            prev = c + 1
        segs.append(tour[prev:])
        perm = list(range(len(segs)))
        rng.shuffle(perm)
        new_tour = []
        for idx, s in enumerate(perm):
            seg = segs[s]
            if idx % 2 == 1:
                seg = list(reversed(seg))
            new_tour.extend(seg)
        return new_tour

    deadline = time.perf_counter() + 1.5
    rng = random.Random(54321)

    # Build diverse initial tours and 2-opt each.
    candidates = []

    start = min(range(n), key=lambda i: (points[i][0], points[i][1]))
    candidates.append(two_opt(nearest_neighbour(start), deadline))

    for _ in range(4):
        if time.perf_counter() > deadline:
            break
        candidates.append(two_opt(nearest_neighbour(rng.randrange(n)), deadline))

    if time.perf_counter() < deadline:
        candidates.append(two_opt(cheapest_insertion(), deadline))

    best = min(candidates, key=tour_length)
    best_len = tour_length(best)

    # Escape local optima: varied kicks + 2-opt, keep best.
    kick_types = [double_bridge_kick, or_opt_kick,
                  lambda t, r: random_k_opt(t, r, 3),
                  lambda t, r: random_k_opt(t, r, 5),
                  segment_reverse_kick,
                  lambda t, r: multi_fragment_kick(t, r, 6)]
    while time.perf_counter() < deadline:
        kicked = rng.choice(kick_types)(best, rng)
        improved = two_opt(kicked, deadline)
        length = tour_length(improved)
        if length < best_len:
            best = improved
            best_len = length

    return best
