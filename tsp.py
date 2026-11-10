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

    t0 = time.perf_counter()
    deadline = t0 + 1.85
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    # Precomputed symmetric distance matrix.
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = xs[i], ys[i]
        row_i = dist[i]
        for j in range(i + 1, n):
            dd = math.hypot(xi - xs[j], yi - ys[j])
            row_i[j] = dd
            dist[j][i] = dd

    def tour_len(tour):
        total = 0.0
        dd = dist
        for i in range(n - 1):
            total += dd[tour[i]][tour[i + 1]]
        total += dd[tour[n - 1]][tour[0]]
        return total

    # --- Construction: cheapest insertion and random-order insertions. ---
    def insertion_tour(order):
        tour = [order[0], order[1]]
        for c in order[2:]:
            row_c = dist[c]
            m = len(tour)
            bc = float("inf")
            bp = 0
            for pos in range(m):
                a = tour[pos]
                b = tour[(pos + 1) % m]
                cost = row_c[a] + row_c[b] - dist[a][b]
                if cost < bc:
                    bc = cost
                    bp = pos
            tour.insert(bp + 1, c)
        return tour

    def cheapest_insertion():
        bi, bj = min(((i, j) for i in range(n) for j in range(i + 1, n)),
                     key=lambda ij: dist[ij[0]][ij[1]])
        remaining = list(range(n))
        remaining.remove(bi)
        remaining.remove(bj)
        tour = [bi, bj]
        while remaining:
            best_c = -1
            best_cost = float("inf")
            best_pos = 0
            for c in remaining:
                row_c = dist[c]
                m = len(tour)
                bc = float("inf")
                bp = 0
                for pos in range(m):
                    a = tour[pos]
                    b = tour[(pos + 1) % m]
                    cost = row_c[a] + row_c[b] - dist[a][b]
                    if cost < bc:
                        bc = cost
                        bp = pos
                if bc < best_cost:
                    best_cost = bc
                    best_c = c
                    best_pos = bp
            tour.insert(best_pos + 1, best_c)
            remaining.remove(best_c)
        return tour

    rng = random.Random(12345)
    cx = sum(xs) / n
    cy = sum(ys) / n
    farthest = max(range(n), key=lambda i: (xs[i] - cx) ** 2 + (ys[i] - cy) ** 2)

    candidates = [cheapest_insertion()]
    for _ in range(3):
        order = [farthest]
        rest = list(range(n))
        rest.remove(farthest)
        rng.shuffle(rest)
        order += rest
        candidates.append(insertion_tour(order))

    d = dist

    def two_opt_pass(tour):
        improved = False
        for i in range(n - 1):
            a = tour[i]
            b = tour[i + 1]
            ab = d[a][b]
            row_a = d[a]
            row_b = d[b]
            for j in range(i + 2, n):
                c = tour[j]
                dn = tour[0] if j == n - 1 else tour[j + 1]
                cd = d[c][dn]
                if row_a[c] + row_b[dn] - ab - cd < 0.0:
                    tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                    b = tour[i + 1]
                    ab = d[a][b]
                    row_b = d[b]
                    improved = True
        return improved

    def or_opt_pass(tour):
        # Move a segment of k consecutive cities to another gap (either
        # orientation); first improvement.
        for k in (1, 2, 3, 4):
            for i in range(n - k):
                s0 = tour[i]
                sl = tour[i + k - 1]
                prev = tour[i - 1]
                nxt = tour[i + k]
                base_remove = d[prev][s0] + d[sl][nxt]
                keep = d[prev][nxt]
                row_s0 = d[s0]
                row_sl = d[sl]
                for q in range(n):
                    if i <= q <= i + k:
                        continue
                    left = tour[q - 1]
                    right = tour[q]
                    lr = d[left][right]
                    delta_f = row_s0[left] + row_sl[right] - lr + keep - base_remove
                    delta_r = row_sl[left] + row_s0[right] - lr + keep - base_remove
                    if delta_f < 0.0 or delta_r < 0.0:
                        seg = tour[i:i + k]
                        rest = tour[:i] + tour[i + k:]
                        pos = q - k if q > i else q
                        if delta_r < delta_f:
                            seg = seg[::-1]
                        rest[pos:pos] = seg
                        tour[:] = rest
                        return True
        return False

    def local_search(tour):
        while time.perf_counter() < deadline:
            if not two_opt_pass(tour) and not or_opt_pass(tour):
                break

    def perturb(tour):
        # Strong composite perturbation: optional random 2-opt reversal, a
        # double bridge, and a random or-opt move.
        t = tour
        if rng.random() < 0.35:
            i, j = sorted(rng.sample(range(n), 2))
            if j > i + 1:
                t = t[:i] + t[i:j + 1][::-1] + t[j + 1:]
        a, b, c = sorted(rng.sample(range(1, n), 3))
        t = t[:a] + t[b:c] + t[a:b] + t[c:]
        k = rng.choice((1, 2, 3))
        i = rng.randrange(n - k)
        seg = t[i:i + k]
        rest = t[:i] + t[i + k:]
        q = rng.randrange(n - k)
        pos = q - k if q > i else q
        rest[pos:pos] = seg
        return rest

    # Local search the best raw candidate, then any other candidate that fits.
    candidates.sort(key=tour_len)
    cur = candidates[0][:]
    local_search(cur)
    best_len = tour_len(cur)
    best_tour = cur[:]
    for cand in candidates[1:]:
        if time.perf_counter() > deadline - 0.5:
            break
        local_search(cand)
        L = tour_len(cand)
        if L < best_len:
            best_len = L
            best_tour = cand[:]

    # ILS: perturb, re-optimize, keep the best.
    cur = best_tour[:]
    restart = 0
    while time.perf_counter() < deadline - 0.3:
        local_search(cur)
        L = tour_len(cur)
        if L < best_len:
            best_len = L
            best_tour = cur[:]
        if time.perf_counter() > deadline - 0.3:
            break
        restart += 1
        cur = perturb(cur)

    # Final polish of the best tour found so far.
    local_search(best_tour)
    return best_tour
