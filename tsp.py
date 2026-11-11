import math
import random
import time


def solve(points):
    """points: list of (x, y) floats in [0, 1000]^2.

    Return the visiting order of a closed tour: a list containing every index
    0..len(points)-1 exactly once. Must finish within the time limit in
    openspec/changes/improve-tsp/objective.md.

    Iterated local search: nearest-neighbor construction, then a node-based
    local search (2-opt + Or-opt with reversed-segment variants) driven by
    don't-look bits over a worklist, escaping local optima with double-bridge
    perturbation. All randomness is seeded; the search stops well before the
    2 s wall-clock limit.
    """
    n = len(points)
    if n <= 2:
        return list(range(n))

    deadline = time.perf_counter() + 1.4  # keep clear of the 2.0 s limit
    rng = random.Random(12345)

    # Distance matrix and per-node distance-sorted neighbor order.
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = points[i]
        di = dist[i]
        for j in range(i + 1, n):
            d = math.hypot(xi - points[j][0], yi - points[j][1])
            di[j] = d
            dist[j][i] = d
    order = [sorted(range(n), key=lambda j: dist[i][j]) for i in range(n)]
    cand = [order[i][1:11] for i in range(n)]  # 10 nearest, self excluded

    def tl(tour):
        return sum(dist[tour[i]][tour[i - 1]] for i in range(n))

    def ls(t):
        """Node-based local search (2-opt + Or-opt 1..3, reversed variants)
        with don't-look bits driven by a worklist."""
        pos = [0] * n
        for idx, node in enumerate(t):
            pos[node] = idx
        in_work = [True] * n
        work = list(range(n))
        wl = 0
        while wl < len(work):
            a = work[wl]
            wl += 1
            in_work[a] = False
            if time.perf_counter() > deadline:
                return t
            ai = pos[a]
            b = t[(ai + 1) % n]
            # --- 2-opt around a: reconnect the a--b edge to a--c ---
            moved = False
            for c in cand[a]:
                ci = pos[c]
                d = t[(ci + 1) % n]
                if d == b or d == a or c == b:
                    continue
                if dist[a][b] + dist[c][d] - dist[a][c] - dist[b][d] > 1e-10:
                    lo = min(ai, ci) + 1
                    hi = max(ai, ci) + 1
                    t[lo:hi] = reversed(t[lo:hi])
                    for idx in range(lo, hi):
                        pos[t[idx]] = idx
                    ai = pos[a]
                    b = t[(ai + 1) % n]
                    for u in (a, b, c, d):
                        if not in_work[u]:
                            in_work[u] = True
                            work.append(u)
                    moved = True
            # --- Or-opt: relocate the segment starting at a (length 1..3) ---
            for sl in (1, 2, 3):
                ss = pos[a]
                if ss + sl >= n:
                    continue  # skip wrapping segments (covered as the tour shifts)
                seg = t[ss:ss + sl]
                e = t[ss + sl]
                p = t[ss - 1]
                removed = dist[p][seg[0]] + dist[seg[-1]][e] - dist[p][e]
                if removed <= 1e-10:
                    continue
                seg_set = set(seg)
                done = False
                for sgv in (seg, seg[::-1]):
                    for c in cand[sgv[0]]:
                        if dist[c][sgv[0]] >= removed - 1e-10:
                            break  # candidates sorted: no improvement further on
                        ci = pos[c]
                        d = t[(ci + 1) % n]
                        if c in seg_set or d in seg_set or c == p or c == e:
                            continue
                        if removed - dist[c][sgv[0]] - dist[sgv[-1]][d] > 1e-10:
                            del t[ss:ss + sl]
                            ci = pos[c]
                            t[ci + 1:ci + 1] = sgv
                            lo = min(ci + 1, ss)
                            for idx in range(lo, n):
                                pos[t[idx]] = idx
                            for u in (p, e, c, d) + tuple(seg):
                                if not in_work[u]:
                                    in_work[u] = True
                                    work.append(u)
                            moved = True
                            done = True
                            break
                    if done:
                        break
            # If nothing was accepted around a, it is simply not re-queued
            # (that is the don't-look mechanism).
        return t

    def nn(first):
        unv = set(range(n))
        unv.discard(first)
        tour = [first]
        cur = first
        while unv:
            for j in order[cur]:
                if j in unv:
                    nxt = j
                    break
            tour.append(nxt)
            unv.discard(nxt)
            cur = nxt
        return tour

    best = ls(nn(0))
    bl = tl(best)

    def dbl(t):
        i = rng.randint(1, n - 3)
        j = rng.randint(i + 1, n - 2)
        kk = rng.randint(j + 1, n - 1)
        return t[:i] + t[j:kk] + t[i:j] + t[kk:]

    # Iterated local search: double-bridge perturbation + local search, greedy
    # acceptance with a small chance of keeping a near-best base to diversify.
    base = best[:]
    while time.perf_counter() < deadline:
        ct = ls(dbl(base))
        cl = tl(ct)
        if cl < bl - 1e-10:
            best = ct[:]
            bl = cl
            base = ct
        elif cl < bl * 1.002 and rng.random() < 0.5:
            base = ct

    return best
