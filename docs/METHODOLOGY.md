# Methodology

## What the benchmark measures

Routine register-level and timing calculations that firmware work depends on:
converting an address to the byte on the wire, sizing an ADC step, deriving a PWM
period from a prescaler and period register, deciding which task a preemptive
scheduler runs next.

These are not research problems. They are calculations performed many times a day
in firmware work, where being almost right produces a device that misbehaves in
the field. That makes them a reasonable probe of whether a model is usable as an
assistant in that setting, and it keeps the answer key checkable.

The original 20 families are easy on purpose. On an easy set the ceiling is
otherwise reachable, so a drop under perturbation is visible. On a set that is
too hard, accuracy is already low and a robustness delta is buried in noise.

That reasoning has a failure mode, and the first three runs hit it: if the easy
tier saturates completely, the deltas cannot move either, because there is no
headroom for a drop. Six harder families presenting C source were added for that
reason, and `difficulty_accuracy` reports the tiers separately so a saturated
tier cannot hide the behaviour of the other. The hard families target constructs
where correct-looking code is wrong: integer promotion widening an operand before
a bitwise operation, a read-modify-write on a write-1-to-clear register, sign
extension of a sub-word two's-complement field, Q15 requantisation, struct
padding, and modular arithmetic across a counter wrap.

Answers for the C families were verified by compiling and running the constructs
during authoring, in addition to the stored check expressions.

## Why paired variants

An accuracy figure on a fixed item set conflates several things. Two are
separable with a small amount of dataset structure.

**Surface-form dependence.** The claim is that an item measures a capability. It
may instead measure one particular string. Those are indistinguishable from a
single score. The `rename` variant holds the computation and the answer fixed and
changes only presentation: peripheral names, signal names, register names,
sentence structure. Any difference between `base` and `rename` is therefore
attributable to presentation, which is an inference an unpaired item set cannot
support.

**Instance dependence.** Public benchmarks leak into training data, and retrieval
of a memorised answer is byte-identical to computing it. The `renumber` variant
keeps the structure and substitutes new input values, so the specific
input-to-answer pair is unlikely to exist as a stored association. This is a
weaker signal than it looks: it makes a memorised instance less useful, but does
not establish that a model never saw the material. It is reported as a robustness
figure, not as a contamination measurement.

## Item construction rules

Every family holds three items, one per variant. Rules that can be checked
mechanically are enforced by `tests/test_dataset.py`.

1. **`rename` does not change the answer.** Asserted for every answer type,
   including `choice`. A choice rename restates the scenario without renaming
   the entity that is itself the answer. An earlier version of `rtos-preempt`
   renamed its tasks to threads, which changed the answer string and put the
   item outside this check; it was rewritten to keep the task names and restate
   the scheduler's behaviour instead.
2. **`rename` changes more than one word.** The rewrite covers identifiers and
   sentence structure, so it tests presentation rather than one token.
3. **`renumber` changes the question text**, and its answer is recomputed from
   the new inputs.
4. **Conventions are stated, not assumed.** ADC items name `V = code x Vref /
   2^N` explicitly, since the `2^N - 1` convention is also in use and an unstated
   choice makes an item ambiguous rather than hard. Bit numbering states that bit
   0 is least significant. Timer items state that a period spans `TOP + 1` ticks.
5. **The requested unit and number base are named in the question.** The scorer
   also accepts equivalent units, so this is redundancy rather than load-bearing.
6. **Every item carries a rationale**, so a reviewer can check the reasoning and
   not just the value.

### Terminology collisions

Rule 4 covers conventions that differ in substance. A second failure mode is
wording that is correct but collides with vendor terminology for a different
concept, which makes an item ambiguous without making it wrong.

The `spi-mode` rename originally read "samples incoming data on the first clock
edge". That matches the standard definition of CPHA=0, phrased as "data are
sampled on the leading (first) clock edge". But Freescale AN3904 defines CPHA on
a different axis entirely, and attaches the phrase to the opposite value:
CPHA=1 is "data transfer starts with the first edge of SCK", describing when a
transfer begins rather than which edge samples. A reader carrying that framing
has a defensible route to the wrong answer.

The item now reads "captures each incoming data bit on the first of the two clock
edges in that bit's period, rather than the second", which cannot be confused
with transfer start. When checking an item for ambiguity, it is not enough that
the wording is correct: check whether the same phrase means something else
elsewhere in the domain's documentation.

## Tolerances

`quantity` items declare a relative tolerance, because the answer key is written
to a readable number of significant figures. Tolerances are per item: tight
enough that a wrong method fails, loose enough that correct work rounded
differently passes. Most are 0.002 to 0.005, which admits rounding at four
significant figures and rejects an error of one part in a hundred.

Units are converted before comparison, so a response in `us` against a key in
`ms` is graded on the physical quantity. A response in the wrong dimension is
marked incorrect rather than converted.

## Two-path answer key checking

Each computational item stores a `check` block holding the expression and inputs
that produce its answer. `tools/verify_answers.py` evaluates it and compares
against the hand-written `target`.

What this buys: the two paths are not independent, since one author wrote both,
so a conceptual error in a formula appears in both and passes. It catches
transcription slips, unit-prefix mistakes and arithmetic errors, which are the
errors most likely when writing sixty answers by hand. On its first run it caught
one: a bit-field extraction hand-computed as `0x3C` where the value is `0x3D`.

Six `choice` items carry no check block, since there is no formula to recompute.
Their answers depend on review. They are still covered by the rename assertion
above, so no item in the set is entirely unchecked.

## Scoring design

Grading is deterministic, with no grader model. A model-graded scorer would
accept a wider range of response formats, at the cost of making scores depend on
the grader's behaviour and version, and of requiring credentials to reproduce a
number. For answers that are integers, physical quantities and short fixed
strings, parsing is sufficient.

Integer items declare the base their question asks for. Digits with no explicit
notation are read in that base, so a response of `A6` to an item requesting
hexadecimal is scored correct. This was added after a run in which the scorer
rejected exactly that response as an unparsable decimal: the instrument marked a
correct answer wrong and inflated the rename delta by a full item. The converse
follows from the same rule, and is deliberate: `166` answering a hexadecimal item
is read as `0x166` and scored wrong, because the item named the base.

The cost shows up in `no_answer_rate`: a model that reasons correctly but ignores
the `ANSWER:` convention scores zero on that item. Reporting the rate separately
keeps the two distinguishable, and a high rate is a signal to revisit the prompt
rather than a conclusion about capability.

## Metric definitions

Let `A(v)` be accuracy over the items of variant `v`.

- `rename_delta = 100 x (A(base) - A(rename))`
- `renumber_delta = 100 x (A(base) - A(renumber))`

Positive means the perturbed variant scored worse. Both can be negative, and a
small negative value over 20 families is noise.

Paired consistency is the fraction of families where the `base` item and the
compared item receive the same grade. It is strictly more informative than the
delta: a model whose consistency is below 1 has families it gets right one way
and wrong the other, and a delta near zero with low consistency means the score
is stable only in aggregate.

## What a reader should not conclude

- **Not a capability ranking.** 60 items with one perturbation each gives
  standard errors too wide to separate close models.
- **Not a contamination measurement.** See the `renumber` discussion above.
- **Not a claim about firmware engineering ability.** The items are closed-form
  calculations with single correct answers, a narrow slice of the work.

## Next steps

1. Several perturbations per family, so robustness has a reportable variance
   rather than a single difference.
2. A second domain reviewer, to catch a consistent misconception one author
   cannot see in their own items.
3. Harder multi-step items, once the current set establishes a floor.
4. Difficulty calibrated against measured performance rather than self-labelled.
5. A distractor variant adding irrelevant but plausible datasheet detail, to test
   whether accuracy survives information that has to be ignored.
