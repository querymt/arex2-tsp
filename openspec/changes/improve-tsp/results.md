# Results

## Summary

| Baseline | Best | Best round | Target | Met | Rounds | Budget used |
|---|---|---|---|---|---|---|
| 1000000.00 | 10951.59 | 7 | 10900 | no | 18 | 42m of 40m |

## What worked

- Round 2: valid tour (sorted by x) got below the 100000 penalty threshold (70663.56).
- Round 3: nearest-neighbor constructive heuristic dropped to 12584.55, clearing task 1.2 (<14000).
- Round 4: 2-opt + random restarts reached 11197.75.
- Round 7 (best): nearest neighbor from spaced starts + 2-opt, then double-bridge kicks + 2-opt,
  final 2-opt/3-opt/2-opt polish, reached 10951.59.

## What did not work

- Simulated annealing (round 9), or-opt relocation (round 10), 4-opt sampling (round 11),
  varied kick sizes (round 15), limited 2-opt passes on kicks (round 16), double 3-opt polish
  (round 17), cheapest insertion start (round 13), more NN starts with different seed (round 12),
  3-opt inside consider (round 14): all scored at or above the round-7 best and were not kept.
- The target of 10900 was never reached; best stayed at 10951.59 (round 7).

## Follow-up ideas

- Faster inner loops (e.g. precomputed neighbor ordering, C extensions) to allow more restarts
  or deeper search within the 2s limit.
- Lin-Kernighan style variable neighborhood search.
- Better escape mechanisms (e.g. multi-fragment reunification) instead of double-bridge kicks.
