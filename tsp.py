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

    deadline = time.perf_counter() + 1.5

    # Precompute the distance matrix.
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = points[i]
        row_i = dist[i]
        for j in range(i + 1, n):
            xj, yj = points[j]
            d = math.hypot(xi - xj, yi - yj)
            row_i[j] = d
            dist[j][i] = d

    def tour_length(tour):
        total = 0.0
        for i in range(n):
            total += dist[tour[i]][tour[(i + 1) % n]]
        return total

    def two_opt(tour, until, max_passes=60):
        for _ in range(max_passes):
            if time.perf_counter() >= until:
                break
            improved = False
            for i in range(1, n):
                a = tour[i - 1]
                b = tour[i]
                for j in range(i + 1, n):
                    c = tour[j]
                    d = tour[(j + 1) % n]
                    delta = dist[a][c] + dist[b][d] - dist[a][b] - dist[c][d]
                    if delta < 0:
                        tour[i:j + 1] = tour[i:j + 1][::-1]
                        improved = True
            if not improved:
                break
        return tour

    def four_opt(tour, until):
        """Try 4-opt moves: split tour into 4 segments and reconnect."""
        improved = True
        while improved and time.perf_counter() < until:
            improved = False
            for i in range(1, n - 2):
                a1 = tour[i - 1]
                a2 = tour[i]
                for j in range(i + 1, n - 1):
                    b1 = tour[j - 1]
                    b2 = tour[j]
                    for k in range(j + 1, n - 1):
                        c1 = tour[k - 1]
                        c2 = tour[k]
                        for l in range(k + 1, n):
                            d1 = tour[l - 1]
                            d2 = tour[(l + 1) % n]
                            # Current edges: a1-a2, b1-b2, c1-c2, d1-d2
                            # Try reconnecting: a1-b1, a2-d1, b2-c1, c2-d2
                            delta = (dist[a1][b1] + dist[a2][d1] + dist[b2][c1] + dist[c2][d2]
                                     - dist[a1][a2] - dist[b1][b2] - dist[c1][c2] - dist[d1][d2])
                            if delta < 0:
                                # Reverse segments to reconnect
                                seg1 = tour[i:j][::-1]
                                seg2 = tour[j:k][::-1]
                                seg3 = tour[k:l][::-1]
                                tour = (tour[:i] + seg1 + seg2 + seg3 + tour[l:])
                                improved = True
                                break
                        if improved:
                            break
                    if improved:
                        break
                if improved:
                    break
        return tour

    def nearest_neighbour(start, rng):
        visited = [False] * n
        tour = [start]
        visited[start] = True
        for _ in range(n - 1):
            cur = tour[-1]
            row = dist[cur]
            best = -1
            best_d = float("inf")
            for j in range(n):
                if not visited[j] and row[j] < best_d:
                    best_d = row[j]
                    best = j
            tour.append(best)
            visited[best] = True
        return tour

    def greedy():
        """Repeatedly add the shortest edge that keeps degree <= 2 and no subtour."""
        degree = [0] * n
        adj = [set() for _ in range(n)]
        edges = []
        for i in range(n):
            for j in range(i + 1, n):
                edges.append((dist[i][j], i, j))
        edges.sort(key=lambda e: e[0])
        tour_set = set()
        for d, i, j in edges:
            if degree[i] >= 2 or degree[j] >= 2:
                continue
            if i in adj[j]:
                continue
            if len(tour_set) > 0:
                comp = set()
                stack = [i]
                while stack:
                    u = stack.pop()
                    if u in comp:
                        continue
                    comp.add(u)
                    for v in adj[u]:
                        if v not in comp:
                            stack.append(v)
                if j in comp and len(comp) < n:
                    continue
            adj[i].add(j)
            adj[j].add(i)
            degree[i] += 1
            degree[j] += 1
            tour_set.add((i, j))
            if len(tour_set) == n:
                break
        tour = [0]
        visited = [False] * n
        visited[0] = True
        while len(tour) < n:
            cur = tour[-1]
            for nxt in adj[cur]:
                if not visited[nxt]:
                    tour.append(nxt)
                    visited[nxt] = True
                    break
        return tour

    def farthest_insertion():
        """Start with shortest edge, insert farthest city each time."""
        best_edge = None
        best_d = float("inf")
        for i in range(n):
            row = dist[i]
            for j in range(i + 1, n):
                if row[j] < best_d:
                    best_d = row[j]
                    best_edge = (i, j)
        tour = [best_edge[0], best_edge[1]]
        remaining = set(range(n)) - set(best_edge)
        while remaining:
            max_dist = -1
            far_city = None
            for c in remaining:
                min_d = float("inf")
                for t in tour:
                    if dist[c][t] < min_d:
                        min_d = dist[c][t]
                if min_d > max_dist:
                    max_dist = min_d
                    far_city = c
            # insert at cheapest position
            best_pos = 0
            best_cost = float("inf")
            for k in range(len(tour)):
                a = tour[k]
                b = tour[(k + 1) % len(tour)]
                cost = dist[far_city][a] + dist[far_city][b] - dist[a][b]
                if cost < best_cost:
                    best_cost = cost
                    best_pos = k + 1
            tour.insert(best_pos, far_city)
            remaining.remove(far_city)
        return tour

    def double_bridge(tour, rng):
        a, b, c, d = sorted(rng.sample(range(1, n), 4))
        return (tour[:a] + tour[b:c] + tour[a:b] + tour[d:] + tour[c:d])

    def reverse_segment(tour, rng):
        i, j = rng.sample(range(n), 2)
        if j < i:
            i, j = j, i
        t = list(tour)
        t[i:j + 1] = t[i:j + 1][::-1]
        return t

    def multi_reverse(tour, rng):
        """Reverse 2-3 random segments."""
        t = list(tour)
        for _ in range(rng.randint(2, 3)):
            i, j = rng.sample(range(n), 2)
            if j < i:
                i, j = j, i
            t[i:j + 1] = t[i:j + 1][::-1]
        return t

    def one_run(construction, seed):
        rng = random.Random(seed)
        tour = construction()
        two_opt(tour, deadline, max_passes=30)
        best_tour = tour
        best_len = tour_length(tour)
        while time.perf_counter() < deadline - 0.05:
            r = rng.random()
            if r < 0.5:
                cand = double_bridge(best_tour, rng)
            elif r < 0.8:
                cand = reverse_segment(best_tour, rng)
            else:
                cand = multi_reverse(best_tour, rng)
            two_opt(cand, deadline, max_passes=10)
            L = tour_length(cand)
            if L < best_len:
                best_len = L
                best_tour = cand
        return best_tour, best_len

    # Multi-restart: several independent runs, keep the best.
    best_tour = None
    best_len = float("inf")

    constructions = [
        lambda: nearest_neighbour(0, random.Random(1)),
        lambda: nearest_neighbour(1, random.Random(2)),
        lambda: nearest_neighbour(50, random.Random(3)),
        lambda: greedy(),
        lambda: farthest_insertion(),
    ]

    for idx, cons in enumerate(constructions):
        if time.perf_counter() >= deadline - 0.05:
            break
        tour, L = one_run(cons, seed=100 + idx)
        if L < best_len:
            best_len = L
            best_tour = tour

    return best_tour
