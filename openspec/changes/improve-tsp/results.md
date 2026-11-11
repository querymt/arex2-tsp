# Results

## Summary

| Baseline | Best | Best round | Target | Met | Rounds | Budget used |
|---|---|---|---|---|---|---|
| 1000000.00 | 10849.88 | 6 | 10900 | yes | 7 | 4m of 40m |

## What worked

- Round 2: identity tour — made `solve` valid, no penalty charged (106070.23).
- Round 3: nearest-neighbor construction, best of 20 starts (12725.33).
- Round 4: 2-opt local search on the best of 10 NN starts, with a distance
  matrix (11223.68).
- Round 5: Or-opt segment relocations (length 1–3) alternated with 2-opt until
  convergence (10903.54).
- Round 6: iterated local search — double-bridge perturbation of the best tour
  with a seeded RNG (`random.Random(20260101)`), using the remaining time
  budget (10849.88, target 10900 reached).

## What did not work

- Nothing was reverted. Round 7 ("final") reproduced the round-6 score
  (10849.88) with no improvement, confirming determinism rather than a
  regression.

## Follow-up ideas

- Neighbor lists (k-nearest) with don't-look bits to make 2-opt/Or-opt faster
  and fit more ILS iterations in the 1.5 s budget.
- Or-opt acceptance of equal-length moves plus segment inversion (Or-3opt) to
  escape local optima that pure relocation cannot.
- Lambda-interchange or 3-opt moves before perturbation for a stronger local
  optimum.
