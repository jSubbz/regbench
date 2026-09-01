# Results

Runs against `claude-sonnet-5`. Later runs exist to test hypotheses raised by
earlier ones, so they are reported as a sequence rather than as independent
measurements. Predictions for the hard tier were registered in
`docs/PREDICTIONS.md` and committed before the first run against it.

## Stages, and what was claimed when

This work was done in two stages, and the repository has been extended since the
first stage's conclusions were written. Anyone arriving here from material dated
before 2026-09-01 is reading a superset of what that material described.

**Stage 1 - 2026-08-29, commits `412f556` through `16e1ef2`.** 20 families, 60
items, easy and medium tiers only. Conclusion: no robustness gap was detected,
and the item set saturates, so the perturbation deltas cannot carry information.
Three apparent signals appeared and all three were defects in the instrument.

**Stage 2 - 2026-09-01, commits `575c15b` through `3a5b342`.** Six harder
C-source families added, taking the set to 26 families and 78 items. Conclusion:
five of the six hard families saturate as well. One, `c-w1c`, has measurable
variance. A controlled probe showed it measures bit-level bookkeeping rather than
the construct it is named for: asked the same question with no byte to assemble,
the model was correct 105 out of 105.

**Stage 1's conclusions are not retracted.** They remain accurate for the 20
families they describe, and stage 2 did not contradict them. What changed is
scope: a harder tier was added, and it produced a finding stage 1 could not have
produced because it had no items with variance.

Applications and other external material submitted before 2026-09-01 referenced
stage 1 only. This note exists so that a reader coming from one of those does not
have to reconstruct which conclusions existed when.

## Runs

### 2026-08-29, easy and medium tiers only (60 items, 20 families)

| | A | B | C | GPIO probe |
| --- | --- | --- | --- | --- |
| Commit | `412f556` | `df7a282` | `16e1ef2` | `16e1ef2` |
| Working tree | modified | clean | clean | clean |
| Samples | 180 | 180 | 180 | 60 |
| accuracy | 0.989 | 1.000 | 0.994 | 1.000 |
| rename_delta | 3.33 | 0.00 | 1.67 | 0.00 |
| renumber_delta | 0.00 | 0.00 | 0.00 | 0.00 |

### 2026-09-01, with the hard tier added (78 items, 26 families)

| | D | E | C-probe | Notation probe 1 | Notation probe 2 |
| --- | --- | --- | --- | --- | --- |
| Commit | `575c15b` | `3a5b342` | `3a5b342` | `3a5b342` | `3a5b342` |
| Samples | 234 | 234 | 180 | 60 | 120 |
| Scope | all | all | `c-source` | w1c notation | w1c notation |
| Epochs | 3 | 3 | 10 | 10 | 30 |
| accuracy | 0.996 | 0.996 | 0.972 | 0.950 | 0.908 |
| hard | 1.000 | 0.981 | 0.972 | 0.950 | 0.908 |

The two notation probes ran against `data/probes/w1c-notation.jsonl` and are not
part of the item set. The last two runs record a modified working tree; the
uncommitted changes were harness fixes described below, not item content.

`claude-sonnet-5` does not accept a `temperature` parameter and runs with
adaptive thinking. None of the runs above sent one; an earlier 3-sample check at
`412f556` did, and the provider returned:

    anthropic model 'claude-sonnet-5' does not support the 'temperature'
    parameter (adaptive thinking only)

which is the evidence for the claim that sampling cannot be pinned. Multiple
epochs were used for that reason.

## The easy and medium tiers saturate

Base accuracy was 1.000 in every run. Both perturbation deltas are therefore
structurally incapable of returning anything but zero or noise on those tiers:
"no robustness gap exists" and "the item set is too easy to reveal one" are
indistinguishable from that data.

Three non-zero deltas appeared on those tiers. All three were the instrument:

| Run | Signal | Cause |
| --- | --- | --- |
| A | `rename_delta` 3.33 | An ambiguous item. "First clock edge" collides with Freescale AN3904, which attaches that phrase to CPHA=1. Reworded; the failure did not reproduce in B. |
| C | `rename_delta` 1.67 | Sampling noise. A 10-epoch probe returned 60/60. |
| D | `rename_delta` 1.28 | A scorer defect. The model answered `A6` to an item requesting hexadecimal; the parser required an explicit `0x`, tried decimal, and marked a correct answer wrong. |

Zero model findings on 60 items across four runs.

## The prediction, and a premature call

Both predictions ranked `c-w1c` most likely to fail. Run D returned `hard` =
1.000 and I recorded that as falsifying both. That call was wrong.

`c-w1c` contributes 9 samples to a 3-epoch run. At the failure rate later
measured, roughly 12%, the probability of a clean sweep across 9 samples is
about 0.30. Run D had power to detect a near-certain failure, not a one-in-eight
one. Treating a null result from an underpowered measurement as a falsification
is the same error the rest of this document is about.

Run E, at the same three epochs, produced one `c-w1c` failure. The 10-epoch probe
produced five, all in `c-w1c`, with the other five C families at 150/150.

## c-w1c: what actually fails

Pooled across every run, `c-w1c` in its original binary notation fails **11 of 80
base and renumber samples, 13.75%**. Every other family in the set, easy or hard,
is perfect.

Reading the failing transcripts, the concept is not what breaks. From a failing
hex-notation sample, the model produced a complete and entirely correct bit table,
then added:

> "Note the irony: the firmware intended to clear bit 1, but because bit1 was
> already 0 in the *value written* (0x68 has bit1=0), the write-1-to-clear
> hardware doesn't touch bit 1. Meanwhile bits 6 and 3 (which were 1 in the
> written value) get cleared unintentionally."

That is a correct and complete account of the trap the item was built around. Its
own table gives `0000 0010`. It then reported `0001 0010 = 0x12`, contradicting
the table it had just written.

Two failure mechanisms appear across the transcripts:

1. **Misreading the input.** Asserting bit 4 of `0x6A` is set when it is not,
   which is equivalent to treating the register as `0x7A`.
2. **Misassembling the output.** Deriving every bit correctly and then serialising
   them to the wrong byte, as above.

Neither is a misunderstanding of write-1-to-clear. One transcript in thirty showed
the intended conceptual error, believing only the OR operand reaches the register.

## The notation probe

`data/probes/w1c-notation.jsonl` holds two families identical in every respect
except how the register value is written: `0b01101010` against `0x6A`. Same code,
same semantics, same answers.

| Arm | base | renumber | Total |
| --- | --- | --- | --- |
| Binary | 5/40 (12.5%) | 6/40 (15.0%) | **11/80 (13.75%)** |
| Hex | 0/40 (0.0%) | 3/40 (7.5%) | **3/80 (3.75%)** |

Fisher's exact: one-tailed p = 0.023, two-tailed p = 0.047.

**Notation matters and does not explain the failures.** Writing the register in
hexadecimal cuts the error rate by roughly two thirds, which is a real effect at
this sample size. It does not remove it: the hex arm still fails 3.75%, entirely
on the `renumber` variant.

## The isolation probe: separating the concept from the bookkeeping

`data/probes/w1c-isolation.jsonl` holds three arms carrying the same trap with
decreasing bookkeeping load. All three use hexadecimal notation.

| Arm | Bits set | Answer requires |
| --- | --- | --- |
| `w1c-yesno` | 4 | nothing but the concept: "is bit 1 still set?" |
| `w1c-minimal` | 2 | track 2 bits, assemble a byte |
| `w1c-control` | 4 | track 8 bits, assemble a byte |

Pooled across both isolation runs and the notation probes:

| Condition | Failures | Rate |
| --- | --- | --- |
| Concept only, no byte to assemble | 0/105 | **0.00%** |
| Two bits set, byte assembled | 1/45 | 2.22% |
| Four bits set, byte assembled, hexadecimal | 13/195 | 6.67% |
| Four bits set, byte assembled, binary literal | 11/80 | **13.75%** |

Fisher's exact, one-tailed:

- binary against concept-only: **p = 0.00007**
- hexadecimal against concept-only: **p = 0.003** (two-tailed 0.005)
- binary against hexadecimal: **p = 0.046**

**The concept is intact.** Asked directly whether bit 1 survives - the exact
counterintuitive consequence of the trap - the model was correct 105 times out of
105. Failure rate then rises monotonically with how much bit-level bookkeeping the
answer format demands, from 0% to 13.75%, and every step of that rise concerns
representation rather than semantics.

Every comparison in that ladder is significant. Byte assembly alone, holding
notation constant, accounts for a rise from 0% to 6.67%; binary notation roughly
doubles it again.

The single `w1c-minimal` failure is the clearest illustration in the whole set.
The model wrote:

> "STATUS (read) = 0x05 = 0000 0101, Mask = 0xFB = 1111 1011, AND result =
> 0000 0101 = 0x05"

`0x05 & 0xFB` is `0x01`, not `0x05`. It then applied write-1-to-clear correctly to
its own incorrect intermediate value. A two-bit AND, wrong, inside otherwise sound
hardware reasoning.

Across every probe, no failure examined was a misunderstanding of write-1-to-clear.
One transcript in thirty showed the intended conceptual error early on; everything
since has been arithmetic, transcription, or serialisation.

## What this says about the item



`c-w1c` does not measure what it was designed to measure, and this is now
established by experiment rather than inferred from reading transcripts. It was
built to test whether a model understands write-1-to-clear semantics. Asked that
question with no byte to assemble, the model is correct 105 out of 105. The item's
failures come from bit-level bookkeeping: reading a literal, performing a mask,
and assembling derived bits into a byte. Binary notation roughly doubles the rate
again without being its cause.

That is a construct-validity failure, and it is the substantive result here. An
item that discriminates is not automatically an item that measures the construct
it names, and the only way to tell the difference is to build the controlled
comparison and run it.

It is not a harmless failure mode in practice. A model that explains a register
trap correctly and then reports the wrong byte is more dangerous than one that is
plainly confused, because the reasoning reads as authoritative.

## Harness defects found by running it

Three, none affecting the answer key, all affecting what could be measured:

1. **The scorer rejected bare hexadecimal.** `A6` answering an item that asked for
   hexadecimal was marked wrong. Integer items now declare the base their question
   requests, and unprefixed digits are read in it.
2. **Relative `-T dataset=` paths failed.** Inspect runs a task from a working
   directory of its own, so relative paths did not resolve against the shell's
   cwd. They now fall back to the project root.
3. **Comma-separated `-T` arguments crashed.** Inspect parses them into a list;
   the task called `.split(",")` on the value. Both forms are now accepted.

## Next

- `c-w1c` **keeps its name**. It was designed to test write-1-to-clear semantics,
  and that is what the record should say it was designed to test. Renaming it now
  to match what it turned out to measure would present a post-hoc observation as
  an intent, and would erase the finding that an item can discriminate while
  measuring something other than its label. The mismatch is documented above and
  in `docs/METHODOLOGY.md` instead.
- A separate item isolating write-1-to-clear from bit-level bookkeeping is the
  constructive fix: same construct, fewer bits to track, built and tested as a new
  item rather than as a retitling of this one.
- The easy and medium tiers remain saturated and carry no information about
  robustness. The hard tier has one item with variance out of six.
- `c-wraparound` has never failed and was flagged at authoring time as the weakest
  item. It is the first candidate for replacement.
