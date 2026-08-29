# Methodology

## What the benchmark is trying to measure

The target construct is the ability to carry out routine register-level and
timing calculations that embedded firmware work depends on: converting between
an address and the byte on the wire, sizing an ADC step, deriving a PWM period
from a prescaler and a period register, deciding which task a preemptive
scheduler runs next.

These are deliberately not research problems. They are the calculations that get
done many times a day in firmware work, where being right matters and being
almost right produces a device that misbehaves in the field. That makes them a
reasonable probe of whether a model is usable as an assistant in that setting,
and it makes the answer key checkable, which a harder item set would not.

## Why paired variants

An accuracy figure on a fixed item set conflates several things. Two are
separable with a small amount of structure in the dataset, so regbench separates
them.

**Surface-form dependence.** If restating a question with different identifiers
and phrasing changes the score, the response was keyed to the surface rather than
the content. The `rename` variant holds the computation and the answer fixed and
changes only how the question is written: peripheral names, signal names,
register names, and sentence structure. Any accuracy difference between `base`
and `rename` is attributable to presentation.

**Instance dependence.** If changing the input values changes the score, the
method did not transfer. The `renumber` variant keeps the structure of the
question and substitutes different values, recomputing the answer. This is a
weaker signal than it may look: it makes memorisation of one exact instance less
useful, but it does not establish that the model never saw the material. It is
reported as a robustness figure, not as a contamination measurement.

## Item construction rules

Every family holds exactly three items, one per variant. The rules below are
enforced by `tests/test_dataset.py` where they can be checked mechanically.

1. **`rename` must not change the answer.** For `integer` and `quantity` items
   this is asserted in the test suite. `choice` items are exempt, because a
   rename may rename the entity that is itself the answer (a task called `A`
   becomes a thread called `t_sensor`).
2. **`rename` must change more than one word.** The rewrite covers identifiers
   and sentence structure, not a single substitution, so that it tests
   presentation rather than one token.
3. **`renumber` must change the question text**, and its answer is recomputed
   from the new inputs rather than carried over.
4. **Conventions are stated in the item, not assumed.** ADC items name the
   convention `V = code x Vref / 2^N` explicitly, because the alternative
   convention using `2^N - 1` is also in use and an unstated choice would make
   the item ambiguous rather than difficult. Bit numbering states that bit 0 is
   the least significant. Timer items state that a period spans `TOP + 1` ticks.
5. **The requested unit and number base are named in the question**, so that a
   correct calculation reported in a different unit is not marked wrong by
   accident. The scorer also accepts equivalent units, so this is redundancy
   rather than a load-bearing rule.
6. **Every item carries a rationale** giving the calculation, so a reviewer can
   check the reasoning and not just the final value.

## Tolerances

`quantity` items declare a relative tolerance rather than being compared exactly,
because the answer key is written to a readable number of significant figures.
Tolerances are set per item, tight enough that a wrong method fails and loose
enough that correct work rounded differently passes. Most are 0.002 to 0.005
relative, which admits ordinary rounding at four significant figures and rejects
an error of one part in a hundred.

Unit conversion happens before comparison, so a response in `us` against a key in
`ms` is graded on the physical quantity. A response in the wrong dimension is
marked incorrect rather than converted.

## Two-path answer key checking

Each computational item stores a `check` block holding the expression and input
values that produce its answer. `tools/verify_answers.py` evaluates the
expression and compares against the hand-written `target`.

The honest description of what this buys: the two paths are not independent,
since one author wrote both, so a conceptual error in the formula appears in both
and passes. What it does catch is transcription slips, unit-prefix mistakes and
arithmetic errors, which are the errors most likely to occur when writing sixty
answers by hand. On its first run it caught one: a bit-field extraction whose
hand-computed answer was `0x3C` where the correct value is `0x3D`.

Six items are `choice` type and carry no check block, since there is no formula
to recompute. Those depend entirely on review.

## Scoring design

Grading is deterministic, with no grader model. This was a deliberate trade.
A model-graded scorer would accept a wider range of response formats, at the cost
of making scores depend on the grader's own behaviour and on the grader's
version, and of requiring credentials to reproduce a number. For an item set
whose answers are integers, physical quantities and short fixed strings, parsing
is sufficient and reproducibility is worth more than format flexibility.

The cost is real and shows up in `no_answer_rate`: a model that reasons correctly
but ignores the `ANSWER:` convention scores zero on that item. Reporting the rate
separately means a reader can tell the two apart, and a high rate is a signal to
revisit the prompt rather than to conclude anything about capability.

## Metric definitions

Let `A(v)` be accuracy over the items of variant `v`.

- `rename_delta = 100 x (A(base) - A(rename))`
- `renumber_delta = 100 x (A(base) - A(renumber))`

Positive values mean the perturbed variant scored worse. Both can be negative,
and a small negative value on 20 families is noise rather than evidence that a
rewrite helped.

Paired consistency is the fraction of families where the `base` item and the
compared item receive the same grade, both correct or both incorrect. It is
strictly more informative than the delta: any model whose consistency is below 1
has families it gets right one way and wrong the other, and a delta near zero
with low consistency means the score is stable only in aggregate.

## What a reader should not conclude

- Not a capability ranking. 60 items with one perturbation each gives standard
  errors too wide to separate models that are close.
- Not a contamination measurement. See the `renumber` discussion above.
- Not a claim about firmware engineering ability in general. The items are
  closed-form calculations with single correct answers, which is a narrow slice
  of the work.

## What I would do next, with more time

1. Several perturbations per family rather than one, so robustness is a
   distribution with a reportable variance instead of a single difference.
2. A second domain reviewer, to catch a consistent misconception that one author
   cannot see in their own items.
3. Harder items that require multiple steps, once the current set establishes a
   floor. The present set is deliberately calibrated to be solvable, which
   limits its power to separate strong models.
4. Difficulty calibrated against measured performance rather than self-labelled.
5. A distractor variant that adds irrelevant but plausible datasheet detail, to
   test whether accuracy survives information that has to be ignored.
