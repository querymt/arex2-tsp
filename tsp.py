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

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    # Symmetric distance matrix (list of lists for fast row access).
    d = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = xs[i], ys[i]
        di = d[i]
        for j in range(i + 1, n):
            dist = math.hypot(xi - xs[j], yi - ys[j])
            di[j] = dist
            d[j][i] = dist

    def tour_len(tour):
        total = 0.0
        prev = tour[-1]
        for cur in tour:
            total += d[prev][cur]
            prev = cur
        return total

    def nn(start):
        unvisited = set(range(n))
        unvisited.remove(start)
        tour = [start]
        cur = start
        while unvisited:
            row = d[cur]
            nxt = min(unvisited, key=row.__getitem__)
            unvisited.remove(nxt)
            tour.append(nxt)
            cur = nxt
        return tour

    def two_opt_pass(tour):
        improved = False
        for i in range(n - 1):
            a = tour[i]
            b = tour[i + 1]
            da = d[a]
            dab = da[b]
            for j in range(i + 2, n):
                c = tour[j]
                e = tour[(j + 1) % n]
                if i == 0 and j == n - 1:
                    continue
                if da[c] + d[b][e] < dab + d[c][e]:
                    tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                    b = tour[i + 1]
                    dab = da[b]
                    improved = True
        return improved

    def or_opt_pass(tour):
        """Move segments of length 1..3 to their best new position.

        Returns the (possibly new) tour and whether any move was made.
        """
        improved = False
        for L in (1, 2, 3):
            i = 0
            while i < n:
                p = tour[(i - 1) % n]
                a = tour[i]
                b = tour[(i + L - 1) % n]
                s = tour[(i + L) % n]
                # Cost change if the segment is removed and the gap closed.
                rem = d[p][s] + d[a][b] - d[p][a] - d[b][s]
                if rem < 0:
                    best_j = -1
                    best_delta = 0.0
                    for j in range(n):
                        if i <= j < i + L:
                            continue
                        x = tour[j]
                        y = tour[(j + 1) % n]
                        if y == a or x == b:
                            continue  # would put the segment back where it was
                        ins = d[x][b] + d[a][y] - d[x][y]
                        delta = rem + ins
                        if delta < best_delta:
                            best_delta = delta
                            best_j = j
                    if best_j >= 0:
                        seg = [tour[(i + k) % n] for k in range(L)]
                        rest = tour[i + L:] + tour[:i]
                        pos = best_j - L if best_j >= i + L else best_j + (n - L)
                        tour = rest[:pos + 1] + seg + rest[pos + 1:]
                        improved = True
                        i = 0  # rescan from the start after a move
                else:
                    i += 1
        return tour, improved

    deadline = time.monotonic() + 1.45
    rng = random.Random(20261110)

    starts = list(range(n))
    rng.shuffle(starts)
    best = None
    best_len = float("inf")
    for s in starts:
        if time.monotonic() > deadline - 0.1:
            break
        tour = nn(s)
        while time.monotonic() < deadline - 0.05:
            did2 = two_opt_pass(tour)
            if time.monotonic() > deadline - 0.05:
                break
            tour, dido = or_opt_pass(tour)
            if not (did2 or dido):
                break
        L_ = tour_len(tour)
        if L_ < best_len:
            best_len = L_
            best = tour

    if best is not None and time.monotonic() < deadline:
        while time.monotonic() < deadline:
            did2 = two_opt_pass(best)
            if time.monotonic() > deadline:
                break
            _, dido = or_opt_pass(best)
            if not (did2 or dido):
                break
    return best
