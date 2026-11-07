# Objective

## Metric
Mean closed-tour length over 5 fixed random instances of 200 points in [0, 1000]^2, as
printed by `python3 tests/score.py` (lower is better). Details per instance go to stderr.

## Baseline
1000000.00 (the stub raises, so every instance is charged the 1,000,000 penalty).

## Target and budget
10900 or lower, within 40 minutes. A simple constructive tour is far above the target;
reaching it needs local search and then a way to escape local optima.

## Constraints
- Each `solve()` call must return within 2.0 seconds wall clock (the scorer measures it;
  a slower call is charged the penalty). Stop your own search at about 1.5 s.
- Python 3 standard library only.
- Seed any RNG you use, so that rounds are comparable and a "new best" is not luck.

## Protected
`tests/*` defines the score.

## Anti-gaming rules
- Do not read the instances' seeds or coordinates out of `tests/score.py`, and do not
  hard-code or cache tours: `solve()` must work for any list of points.
- No special-casing the instance size.
