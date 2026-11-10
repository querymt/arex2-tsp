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
    if n == 3:
        return [0, 1, 2]

    t_start = time.perf_counter()
    main_deadline = t_start + 1.10
    polish_deadline = t_start + 1.55

    # Distance matrix (symmetric).
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = points[i]
        row_i = dist[i]
        for j in range(i + 1, n):
            xj, yj = points[j]
            dx = xi - xj
            dy = yi - yj
            d = math.sqrt(dx * dx + dy * dy)
            row_i[j] = d
            dist[j][i] = d

    rng = random.Random(20261107)

    def tour_len(tour):
        total = 0.0
        prev = tour[-1]
        for city in tour:
            total += dist[prev][city]
            prev = city
        return total

    def nearest_neighbor(start):
        visited = [False] * n
        tour = [start]
        visited[start] = True
        cur = start
        for _ in range(n - 1):
            row = dist[cur]
            best = -1
            bd = float("inf")
            for j in range(n):
                if not visited[j] and row[j] < bd:
                    bd = row[j]
                    best = j
            visited[best] = True
            tour.append(best)
            cur = best
        return tour

    def two_opt(tour, deadline):
        tour = list(tour)
        improved = True
        while improved:
            improved = False
            for i in range(n - 1):
                a = tour[i]
                b = tour[i + 1]
                dab = dist[a][b]
                for j in range(i + 2, n):
                    c = tour[j]
                    d = tour[(j + 1) % n]
                    if dist[a][c] + dist[b][d] < dab + dist[c][d] - 1e-10:
                        tour[i + 1:j + 1] = tour[i + 1:j + 1][::-1]
                        improved = True
                        break
                if improved and time.perf_counter() > deadline:
                    return tour
        return tour

    def double_bridge(tour):
        tour = list(tour)
        edges = rng.sample(range(n), 4)
        edges.sort()
        i, j, k, l = edges
        s1 = tour[i + 1:j + 1]
        s3 = tour[k + 1:l + 1]
        tour[i + 1:j + 1] = s1[::-1]
        tour[k + 1:l + 1] = s3[::-1]
        return tour

    def three_opt(tour, deadline):
        tour = list(tour)
        improved = True
        while improved:
            improved = False
            for _ in range(2000):
                if time.perf_counter() > deadline:
                    return tour
                i, j, k = sorted(rng.sample(range(n), 3))
                a1, b1 = tour[i], tour[i + 1]
                a2, b2 = tour[j], tour[j + 1]
                a3, b3 = tour[k], tour[(k + 1) % n]
                cur = dist[a1][b1] + dist[a2][b2] + dist[a3][b3]
                c0 = dist[a1][a2] + dist[b1][b2] + dist[a3][b3]
                c1 = dist[a1][b1] + dist[a2][a3] + dist[b2][b3]
                c2 = dist[a1][a2] + dist[b1][a3] + dist[b2][b3]
                best = cur
                move = -1
                if c0 < best:
                    best, move = c0, 0
                if c1 < best:
                    best, move = c1, 1
                if c2 < best:
                    best, move = c2, 2
                if move == -1:
                    continue
                seg1 = tour[i + 1:j + 1]
                seg2 = tour[j + 1:k + 1]
                if move == 0:
                    tour[i + 1:j + 1] = seg1[::-1]
                elif move == 1:
                    tour[j + 1:k + 1] = seg2[::-1]
                else:
                    tour[i + 1:j + 1] = seg1[::-1]
                    tour[j + 1:k + 1] = seg2[::-1]
                improved = True
        return tour

    best_tour = None
    best_len = float("inf")

    def consider(tour, deadline):
        nonlocal best_tour, best_len
        tour = two_opt(tour, deadline)
        l = tour_len(tour)
        if l < best_len:
            best_len = l
            best_tour = tour

    # Phase 1: nearest neighbor from several spaced starts + 2-opt.
    step = max(1, n // 15)
    for start in range(0, n, step):
        if time.perf_counter() > main_deadline:
            break
        consider(nearest_neighbor(start), main_deadline)

    # Phase 2: double-bridge kicks + 2-opt to escape local optima.
    while time.perf_counter() < main_deadline - 0.05:
        kicked = double_bridge(best_tour)
        consider(kicked, main_deadline)

    # Final polish.
    best_tour = two_opt(best_tour, polish_deadline)
    best_tour = three_opt(best_tour, polish_deadline)
    best_tour = two_opt(best_tour, polish_deadline)
    return best_tour
