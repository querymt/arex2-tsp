# Results

## Summary

| Baseline | Best | Best round | Target | Met | Rounds | Budget used |
|---|---|---|---|---|---|---|
| 1000000.00 | 10774.65 | 4 | 10900 (min) | yes | 5 | 2m of 40m |

## What worked

- Round 2 — identity tour: replaced the stub with `return list(range(len(points)))` so
  every instance returns a valid closed tour and no instance is charged the 1,000,000
  penalty. Score 1000000.00 → 106070.23.
- Round 3 — nearest-neighbour construction: multi-start NN from a seeded random start
  (`random.Random(12345)`), picking the shortest of the tours built. Score
  106070.23 → 12725.33. Verified the task-1.2 threshold (< 14000).
- Round 4 — 2-opt with neighbour lists, don't-look bits, plus double-bridge iterated
  local search under a 1.4 s self-imposed deadline (scorer limit 2.0 s). Score
  12725.33 → 10774.65, which reaches the objective target of 10900.

## What did not work

- Nothing was reverted. Round 5 ("final") reproduced the round-4 score exactly
  (10774.65) — the solver is seeded, so it is deterministic.

## Follow-up ideas

- Or-opt moves (relocate segments of length 1–3) after 2-opt convergence; typically a
  few percent below plain 2-opt.
- Larger neighbour lists (k = 24–32) or 3-opt candidate moves if the time budget
  allows.
- Simulated-annealing acceptance in the ILS loop instead of strict improvement, to
  escape local optima that double bridging alone misses.
