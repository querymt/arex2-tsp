# Results

## Summary

| Baseline | Best | Best round | Target | Met | Rounds | Budget used |
|---|---|---|---|---|---|---|
| 1000000.00 | 10969.91 | 12 | 10900 (min) | no | 18 | 41m of 40m |

Both tasks are complete: `solve` returns a valid tour for every instance (no
penalty) and the constructive-heuristic score is far below 14000. The final
score of 10969.91 misses the 10900 target by ~70 units; the budget was spent
before closing that gap.

## What worked

- Round 2: nearest-neighbour construction gave a valid tour, score 13145.51.
- Round 3: nearest-neighbour + 2-opt local search dropped to 11454.95.
- Round 4: multi-start nearest-neighbour + 2-opt + double-bridge perturbation
  improved to 11302.45.
- Round 6: iterated local search with double-bridge + segment-reversal
  perturbations reached 11039.30.
- Round 10: multi-restart over several constructions (NN from different starts,
  greedy edge-building) reached 10988.53.
- Round 12 (best): added farthest-insertion construction and a multi-segment
  reversal perturbation; score 10969.91.

## What did not work

- Round 5: adding or-opt to the local search was no improvement (11454.95) —
  reverted.
- Round 7: cheapest-insertion construction, no improvement (11058.09) — reverted.
- Round 8: exhaustive 3-opt, no improvement (11256.48) — reverted (too slow).
- Round 9: simulated annealing, scored 1000000 (some instance too slow/invalid)
  — reverted.
- Round 11: or-opt again in the multi-restart framework, no improvement
  (11454.95) — reverted.
- Round 13: randomized 3-opt + random-tour construction, no improvement
  (11052.35) — reverted.
- Round 14: faster IL with more iterations, no improvement (11023.41) — reverted.
- Round 15: more diverse starts with time division, no improvement (11050.86) —
  reverted.
- Round 16: exhaustive 3-opt in local search, no improvement (11454.95) —
  reverted.
- Round 17: diverse perturbations + segment shuffle, no improvement (10984.23) —
  reverted.

## Follow-up ideas

- The remaining gap to target is small (~70 units). A stronger escape mechanism
  (e.g. 4-opt or Lin-Kernighan style moves) or a more careful annealing schedule
  might close it, but each attempt within the budget either regressed or was too
  slow for the 2 s per-instance limit.
- Tabu search with a short-term memory could avoid the local optima that plain
  iterated 2-opt gets stuck in.
- More aggressive time management: the per-instance 2 s limit leaves little room
  for deep search; a faster inner loop (e.g. precomputed nearest-neighbour
  lists) would allow more restarts.
