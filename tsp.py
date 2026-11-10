import math
import time


def _build_dist(points, n):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = xs[i], ys[i]
        row = dist[i]
        for j in range(i + 1, n):
            dx = xi - xs[j]
            dy = yi - ys[j]
            v = math.hypot(dx, dy)
            row[j] = v
            dist[j][i] = v
    return dist


def _edge_lengths(tour, dist, n):
    e = [0.0] * n
    for i in range(n - 1):
        e[i] = dist[tour[i]][tour[i + 1]]
    e[n - 1] = dist[tour[n - 1]][tour[0]]
    return e


def _nn_tour(start, dist, n):
    unvisited = set(range(n))
    unvisited.discard(start)
    tour = [start]
    cur = start
    while unvisited:
        row = dist[cur]
        best = min(unvisited, key=row.__getitem__)
        unvisited.remove(best)
        tour.append(best)
        cur = best
    return tour


def _two_opt_pass(tour, dist, n, e, deadline):
    """First-improvement 2-opt pass.

    Returns True if any improvement was applied, False when a full scan found
    none (2-opt local optimum), None when the deadline expired mid-pass.
    """
    while True:
        improved = False
        i = 0
        while i < n - 1:
            if time.monotonic() >= deadline:
                return None
            ti = tour[i]
            tni = tour[i + 1]
            row_i = dist[ti]
            row_ni = dist[tni]
            ei = e[i]
            j = i + 2
            while j < n:
                tj = tour[j]
                tnj = tour[j + 1] if j + 1 < n else tour[0]
                if row_i[tj] + row_ni[tnj] < ei + e[j] - 1e-9:
                    tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                    # Only the two boundary edges change length; the internal
                    # edge set of the reversed segment is unchanged.
                    e[i] = dist[ti][tj]
                    e[j] = dist[tni][tnj]
                    improved = True
                    break
                j += 1
            i += 1
        if not improved:
            return False


def _or_opt_pass(tour, dist, n, e, deadline):
    """Best-improvement Or-opt pass for segment lengths 1..3.

    Returns True if an improvement was applied, False on completion with none,
    None when the deadline expired mid-pass.
    """
    improved = False
    for L in (1, 2, 3):
        a = 0
        while a < n:
            if time.monotonic() >= deadline:
                return None
            b = a + L - 1
            if b >= n:
                b -= n
            wrap = b < a
            prev_a = a - 1 if a > 0 else n - 1
            next_b = b + 1 if b + 1 < n else 0
            ta = tour[a]
            tb = tour[b]
            row_tb = dist[tb]
            const = dist[tour[prev_a]][tour[next_b]] - e[prev_a] - e[b]
            if wrap:
                # Valid insertion positions are next_b..a-1, except a-1 itself
                # (its successor is inside the segment; delta formula invalid).
                rng = range(next_b, a - 1)
            else:
                # Valid insertion positions are b+1..n-1 and 0..a-2 (a-1 is
                # prev_a, whose edge is removed; delta formula invalid there).
                rng = list(range(b + 1, n)) + list(range(0, a - 1))
            best_delta = 0.0
            best_p = -1
            for p in rng:
                tp = tour[p]
                tq = tour[p + 1] if p + 1 < n else tour[0]
                d = const + dist[tp][ta] + row_tb[tq] - e[p]
                if d < best_delta:
                    best_delta = d
                    best_p = p
            if best_p >= 0:
                if wrap:
                    seg = tour[a:] + tour[:next_b]
                    rest = tour[next_b:a]
                    pos = best_p - next_b
                else:
                    seg = tour[a:b + 1]
                    rest = tour[:a] + tour[b + 1:]
                    pos = best_p if best_p < a else best_p - L
                rest[pos + 1:pos + 1] = seg
                tour[:] = rest
                e[:] = _edge_lengths(tour, dist, n)
                improved = True
            a += 1
    return improved


def _polish(tour, dist, n, e, deadline):
    """Alternate 2-opt and Or-opt passes until no improvement or deadline."""
    while time.monotonic() < deadline:
        r1 = _two_opt_pass(tour, dist, n, e, deadline)
        if r1 is None:
            return
        r2 = _or_opt_pass(tour, dist, n, e, deadline)
        if r2 is None:
            return
        if not r1 and not r2:
            return


def solve(points):
    """points: list of (x, y) floats in [0, 1000]^2.

    Return the visiting order of a closed tour: a list containing every index
    0..len(points)-1 exactly once. Must finish within the time limit in
    openspec/changes/improve-tsp/objective.md.
    """
    n = len(points)
    if n <= 2:
        return list(range(n))

    t0 = time.monotonic()
    deadline = t0 + 1.45

    dist = _build_dist(points, n)

    # Multi-start nearest-neighbor construction; keep the shortest raw tour.
    tour = None
    best_len = float("inf")
    for start in (0, n // 2, (n * 3) // 5):
        cand = _nn_tour(start, dist, n)
        e = _edge_lengths(cand, dist, n)
        l = sum(e)
        if l < best_len:
            best_len = l
            tour = cand
            best_e = e

    # Polish the best raw tour to a 2-opt + Or-opt local optimum.
    _polish(tour, dist, n, best_e, deadline)
    best_len = sum(best_e)

    # Deterministic double-bridge perturbations while time remains.
    for r1f, r2f, r3f in ((0.3, 0.7, 0.9), (0.2, 0.5, 0.8),
                          (0.25, 0.6, 0.85), (0.35, 0.75, 0.95)):
        if time.monotonic() >= deadline - 0.15:
            break
        a = int(n * r1f)
        b = int(n * r2f)
        c = int(n * r3f)
        cand = tour[:a] + tour[b:c] + tour[a:b] + tour[c:]
        e = _edge_lengths(cand, dist, n)
        _polish(cand, dist, n, e, deadline)
        l = sum(e)
        if l < best_len:
            best_len = l
            tour = cand
            best_e = e

    return tour
