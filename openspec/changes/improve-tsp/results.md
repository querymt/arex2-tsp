# Results

## Summary

| Baseline | Best | Best round | Target | Met | Rounds | Budget used |
|---|---|---|---|---|---|---|
| 1000000.00 | 10755.83 | 4 | 10900 (min) | yes | 5 | 10m of 40m |

## What worked

- Round 2 — identity tour stub replacement (`return list(range(n))`): valid
  permutation, score 106070.23 (no instance charged the penalty). Task 1.1.
- Round 3 — nearest-neighbor construction + full-sweep 2-opt: score 11412.17,
  under the 14000 task threshold. Task 1.2.
- Round 4 — the decisive change: replaced the full-sweep local search with a
  node-based worklist search (2-opt + Or-opt for segments of length 1–3 with
  reversed-segment variants, don't-look bits, sorted candidate lists with an
  exact early-break bound), and iterated it with double-bridge perturbation
  (greedy acceptance, 0.2% annealing window, seeded RNG, 1.4 s cut-off).
  Iterations per solve went from ~170 to ~1700 and the score dropped from
  11412.17 to 10755.83, below the 10900 target.

## What did not work

- First draft of the worklist solver (offline experiment, not scored): the
  Or-opt gain formula omitted the new `dist[p][e]` edge created by removing
  the segment, so the search accepted length-increasing moves and oscillated
  until the deadline (~28000 mean on self-made test seeds). Fixed the formula
  and dropped buggy wraparound segment handling (covered as the tour shifts).
- Full-sweep variants tested offline on self-generated seeds (never beat the
  baseline beyond run-to-run noise, so not kept): Or-opt segment lengths up to
  5, union of candidate lists of both endpoints in 2-opt, multiple NN starts,
  reversed-only Or-opt. Multi-start randomized-NN construction (best of many
  local optima) scored worse than ILS on test seeds (~11345 vs ~11133).

## Follow-up ideas

- Replace the annealing-lite acceptance with proper simulated annealing or a
  record-to-record travel threshold tuned on more seeds.
- Add 2.5-opt / node-insertion moves between the 2-opt and Or-opt passes.
- Restart-IKS style: perturb a small pool of diverse local optima instead of
  only the current base.
