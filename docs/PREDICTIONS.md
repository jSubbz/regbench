# Pre-run predictions: hard tier

Recorded before the first run against the six C-source families, and committed
before that run so the timestamp is checkable. The point is to make the result
falsifiable: a prediction written afterwards is not a prediction.

Both predictions concern which families `claude-sonnet-5` will answer incorrectly
on at least one epoch of three.

## Author (Jay)

1. `c-w1c` - most likely miss. Read-modify-write on a write-1-to-clear register
   requires reasoning about the register's contract rather than the C operator.
2. `c-signext` - second most likely.
3. `c-padding` - expected to pass.

## Assistant (Claude)

1. `c-w1c` - most likely miss, same reasoning.
2. `c-promotion` - second most likely. Integer promotion before `~` contradicts
   the declared type, which is the trap.
3. `c-wraparound` - expected to pass, and judged the weakest item in the set:
   unsigned modular arithmetic is well drilled and the naive reading does not
   produce a distinctive wrong answer. Candidate for replacement if the hard
   tier lands near ceiling.

## Agreement and divergence

Both rank `c-w1c` first, for the same reason. The predictions diverge on second
place: `c-signext` against `c-promotion`. Both expect `c-padding` and
`c-wraparound` to pass.

## What each outcome would mean

- **Hard tier near 100%.** Sonnet-5 handles these constructs. The next increment
  must be harder still; the difficulty band that discriminates has not been found
  yet.
- **Hard tier between 60% and 90%.** The item set has usable variance and the
  perturbation deltas can carry information for the first time.
- **Hard tier below about 30%.** A floor effect, the mirror of the saturation
  problem the easy tier already showed. The deltas flatten for the opposite
  reason and the tier needs easing.
