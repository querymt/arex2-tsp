# Results

## Summary

| Baseline | Best | Best round | Target | Met | Rounds | Budget used |
|---|---|---|---|---|---|---|
| 1000000.00 | 10942.32 | 6 | 10900 | no (close) | 7 | 58m of 40m |

## What worked

- Round 2: nearest-neighbour greedy dropped score from 1000000 to 13606.
- Round 3: 2-opt local search on the greedy tour dropped to 11718.
- Round 4: double-bridge kicks + 2-opt reached 11013.
- Round 5: adding or-opt and random k-opt kicks improved to 11003.
- Round 6 (best): more diverse initial tours (5 nearest-neighbour starts + cheapest insertion) plus segment-reverse and multi-fragment kicks reached **10942.32**.

## What did not work

- 3-opt local search (rounds with 3-opt): consistently worse, likely because it consumes time budget without finding better tours from these starting points.
- Simulated annealing: worse than iterated local search with kicks.
- Farthest insertion as initial tour: no improvement over cheapest insertion.
- More randomized nearest-neighbour starts (round 7): 11024, slightly worse than round 6.

## Follow-up ideas

- Tabu search with a short-term memory to escape local optima more effectively.
- Lin-Kernighan style variable-depth k-opt.
- Better use of time: adaptive kick strength based on stagnation.
- The target of 10900 is very close (10942); a small improvement in kick diversity or local search depth might reach it.
