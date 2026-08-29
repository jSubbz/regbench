# Results

Two runs against `claude-sonnet-5`, reported together because the second exists
to test a hypothesis raised by the first.

## Run metadata

| | Run A | Run B |
| --- | --- | --- |
| Commit | `412f556` | `df7a282` |
| Date | 2026-08-29 16:13 UTC | 2026-08-29 16:32 UTC |
| Model | `anthropic/claude-sonnet-5` (created 2026-06-29) | same |
| Samples | 60 items x 3 epochs = 180 | 180 |
| Tokens | 31,872 in / 14,939 out | 31,911 in / 17,204 out |
| Wall time | 18 s | 19 s |

`claude-sonnet-5` does not accept a `temperature` parameter and runs with
adaptive thinking, so neither run is deterministic and neither can be pinned to a
sampling configuration. Three epochs per item were used for that reason: a single
draw would not distinguish a stable answer from an unstable one. No other model
arguments were passed; reasoning content is returned encrypted and was not
available for inspection.

## Metrics

| Metric | Run A | Run B |
| --- | --- | --- |
| accuracy | 0.989 | 1.000 |
| stderr | 0.011 | 0.000 |
| base | 1.000 | 1.000 |
| rename | 0.967 | 1.000 |
| renumber | 1.000 | 1.000 |
| rename_delta | 3.33 | 0.00 |
| renumber_delta | 0.00 | 0.00 |
| rename_consistency | 0.950 | 1.000 |
| renumber_consistency | 1.000 | 1.000 |
| no_answer_rate | 0.000 | 0.000 |

Run A: 178 of 180 correct. Both failures were the same item, `spi-mode.rename`,
in two of its three epochs.

Run B: 180 of 180.

## What happened between the runs

Run A's only signal was a 3.33 point rename delta resting on two samples. The
paired consistency of 0.95 localised it to one family out of twenty, which is the
pattern expected from a single defective item rather than from a general
sensitivity to rewording.

The item asked the same question as its base in behavioural terms. The base
states CPOL and CPHA directly and was answered correctly in all three epochs. The
rename read:

> An SPI master idles its clock line high and samples incoming data on the first
> clock edge of each bit period.

Clock idling high is CPOL=1. Sampling on the first edge is CPHA=0. Mode 2. The
model answered 3 twice and 2 once.

That wording matches the standard definition of CPHA, usually given as "data are
sampled on the leading (first) clock edge". But Freescale AN3904 defines CPHA on
a different axis and attaches the same phrase to the opposite value: CPHA=1 is
"data transfer starts with the first edge of SCK", which describes when a
transfer begins rather than which edge samples data. A reader carrying that
framing has a defensible route from "first clock edge" to CPHA=1, and therefore
to mode 3.

The item was reworded to remove the collision:

> An SPI master idles its clock line high and captures each incoming data bit on
> the first of the two clock edges in that bit's period, rather than the second.

The answer is unchanged at 2, and the question is still posed behaviourally, so
it still tests the same translation. Run B re-ran the unchanged benchmark against
the same model with only this wording different.

The failure did not reproduce.

## Interpretation

**The rename delta in Run A was an artifact of item wording, not a property of
the model.** Removing an ambiguity that existed in the item removed the signal.
Run A should not be cited as evidence of surface-form sensitivity.

**Neither run detected instance dependence.** `renumber_delta` was 0.00 in both.
Every renumbered item was answered correctly, including value combinations
unlikely to appear in training data as a stored pair. On this item set the model
is performing the calculations rather than recalling them.

**The benchmark is at ceiling and cannot currently detect what it was built to
detect.** With base accuracy at 100%, both deltas are structurally incapable of
returning anything but zero or noise. "No robustness gap exists" and "the item
set is too easy to reveal one" are indistinguishable from this data. The Run B
result is therefore a statement about the instrument as much as about the model.

**The review process worked.** A single ambiguous phrase produced a false
positive, the paired-consistency metric localised it to one family, review
identified a competing definition in vendor documentation, and a controlled
re-run eliminated it. That sequence is the part of this worth reproducing at
larger scale.

## What would make the next run informative

Harder items, so that base accuracy sits below ceiling and the deltas have room
to move. Multi-step calculations, and items presenting C source rather than prose,
are the obvious increments. A set where a strong model scores 80 to 90 percent
would let the perturbation metrics measure something; the present set cannot.

## Reproducing

```bash
git checkout df7a282
pip install -e ".[dev]" anthropic
export ANTHROPIC_API_KEY=...
inspect eval src/regbench/task.py --model anthropic/claude-sonnet-5 --epochs 3
```

Exact reproduction is not possible. The model does not accept a temperature
parameter, runs with adaptive thinking, and the alias may resolve to a different
snapshot over time. Expect variation, particularly on items near the boundary of
what the model answers consistently.
