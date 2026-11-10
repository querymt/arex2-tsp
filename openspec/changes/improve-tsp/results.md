# Results

## Summary

| Baseline | Best | Best round | Target | Met | Rounds | Budget used |
|---|---|---|---|---|---|---|
| 1000000.00 | 10926.55 | 10 | 10900 (min) | no | 13 | 44m of 40m (exceeded at round 12) |

## What worked

- **Round 2 — angular-order tour (29682.33):** first valid tour for every instance;
  completed task 1.1 (score < 100000, no penalties).
- **Round 4 — nearest-neighbor + first-improvement 2-opt (11480.27):** completed task
  1.2 (score < 14000). A sign error in the 2-opt delta in round 3 (87855.84) was the
  only real bug found; fixing it dropped the score by an order of magnitude.
- **Round 6 — ILS with double-bridge + or-opt perturbations (11149.06):** escaping
  local optima paid off; pure 2-opt/constructor plateaus were left behind.
- **Round 7 — more diverse construction starts (11042.74).**
- **Round 8 — cheapest-insertion candidates + multi-candidate local search (11040.50).**
- **Round 10 — or-opt extended to k<=4 with both segment orientations, plus a composite
  perturbation (random 2-opt reversal + double bridge + random or-opt move)
  (10926.55, best).** Stronger local search and stronger escape were the last gains.

## What did not work

- **Round 3 — initial 2-opt with a sign error in the improvement delta (87855.84):**
  it "improved" toward longer tours until the time limit; fixed in round 4.
- **Round 5 — first or-opt + ILS attempt (802286.92):** the or-opt insertion position
  for gaps before the removed segment was off by one, corrupting tours on some
  instances; rewritten from scratch in round 6.
- **Round 9 — extending the internal deadline from 1.6 s to 1.85 s (11040.50):** no
  improvement; the extra time was spent on redundant passes, not new optima.
- **Round 11 — more construction candidates (7 random insertions + NN) (10967.75):**
  worse than round 10; local search dominated the budget and the extra candidates
  mostly duplicated the cheapest-insertion basin. Reverted to the round-10 state.
- **Round 12 — micro-optimized or-opt pass (split q-loops, no continue) (10926.55):**
  no measurable gain; the algorithm, not Python loop overhead, was the bottleneck.

## Follow-up ideas

- Or-opt with k up to ~6 and a 2-opt/Or-opt alternating schedule to squeeze the last
  few percent (target 10900 missed by 26.55 on the best round).
- Replace the Python or-opt pass with a vectorized NumPy-free approach is impossible
  under the stdlib-only constraint; instead, cache per-gap best insertions and only
  re-scan affected gaps after each move (O(n) instead of O(n^2) per move).
- Simulated annealing over 2-opt/Or-opt moves with an acceptance probability may
  escape the local optima that double bridge + or-opt perturbations miss.
- Use a spatial grid to bound the j-range in 2-opt (points within ~100 of the edge
  rarely improve), cutting the dominant cost and buying more ILS restarts per call.
- Multi-start with different RNG seeds per instance index is disallowed (no
  hard-coding), but per-call seeded randomness from a hash of the points would keep
  rounds comparable while diversifying starts.
