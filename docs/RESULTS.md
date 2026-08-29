# Results

Three full runs against `claude-sonnet-5`, plus one targeted probe. Runs B and C
each exist to test a hypothesis raised by the run before it, so they are reported
together rather than as independent measurements.

## Runs

| | A | B | C | GPIO probe |
| --- | --- | --- | --- | --- |
| Commit | `412f556` | `df7a282` | `16e1ef2` | `16e1ef2` |
| Working tree | modified | clean | clean | clean |
| Time (UTC) | 16:13 | 16:32 | 16:59 | 17:03 |
| Scope | all 60 items | all 60 | all 60 | 6 gpio items |
| Epochs | 3 | 3 | 3 | 10 |
| Samples | 180 | 180 | 180 | 60 |
| Tokens in / out | 31,872 / 14,939 | 31,911 / 17,204 | 31,947 / 15,046 | 11,470 / 5,446 |
| Wall time | 18 s | 19 s | 15 s | 7 s |

All runs used `anthropic/claude-sonnet-5` (created 2026-06-29) with no model
arguments. Commits are as recorded by Inspect in each log. Run A's working tree
was modified at run time; the uncommitted changes were to module import handling
and to tests, so the item content matched `412f556`.

`claude-sonnet-5` does not accept a `temperature` parameter and runs with
adaptive thinking, so no run is deterministic and none can be pinned to a
sampling configuration. Multiple epochs were used for that reason: a single draw
cannot distinguish a stable answer from an unstable one. Reasoning content is
returned encrypted and was not available for inspection.

## Metrics

| Metric | A | B | C | GPIO probe |
| --- | --- | --- | --- | --- |
| accuracy | 0.989 | 1.000 | 0.994 | 1.000 |
| stderr | 0.011 | 0.000 | 0.006 | 0.000 |
| base | 1.000 | 1.000 | 1.000 | 1.000 |
| rename | 0.967 | 1.000 | 0.983 | 1.000 |
| renumber | 1.000 | 1.000 | 1.000 | 1.000 |
| rename_delta | 3.33 | 0.00 | 1.67 | 0.00 |
| renumber_delta | 0.00 | 0.00 | 0.00 | 0.00 |
| rename_consistency | 0.950 | 1.000 | 0.950 | 1.000 |
| renumber_consistency | 1.000 | 1.000 | 1.000 | 1.000 |
| no_answer_rate | 0.000 | 0.000 | 0.000 | 0.000 |

Failures: Run A, 2 of 180, both `spi-mode.rename`. Run C, 1 of 180,
`gpio-rmw.rename`. Runs B and the probe, none.

## Run A to B: an ambiguous item

Run A's only signal was a 3.33 point rename delta resting on two samples. Paired
consistency of 0.95 localised it to one family out of twenty, the pattern of a
single defective item rather than a general sensitivity to rewording.

`spi-mode.base` states CPOL and CPHA directly and was answered correctly in all
three epochs. The rename asked the same question behaviourally:

> An SPI master idles its clock line high and samples incoming data on the first
> clock edge of each bit period.

Clock idling high is CPOL=1; sampling on the first edge is CPHA=0; mode 2. The
model answered 3 in two epochs and 2 in the third.

That wording matches the standard definition of CPHA, usually given as "data are
sampled on the leading (first) clock edge". But Freescale AN3904 defines CPHA on
a different axis and attaches the same phrase to the opposite value: CPHA=1 is
"data transfer starts with the first edge of SCK", describing when a transfer
begins rather than which edge samples. A reader carrying that framing has a
defensible route from "first clock edge" to mode 3.

The item was reworded to remove the collision, keeping the answer at 2 and the
question behavioural:

> An SPI master idles its clock line high and captures each incoming data bit on
> the first of the two clock edges in that bit's period, rather than the second.

Run B re-ran the otherwise unchanged benchmark. The failure did not reproduce.

**The Run A rename delta was an artifact of item wording, not a property of the
model.** Run A should not be cited as evidence of surface-form sensitivity.

## Run C to the probe: sampling noise

Run C followed three further item edits (see the repository history) and produced
one failure: `gpio-rmw.rename` in one epoch of three, answering `0xD6` where the
answer is `0xA6`. The base item, with identical numbers, scored 3 of 3.

The wording is not a plausible cause. "Drive bit 1 high and bit 3 low" against
the base's "set bit 1 and clear bit 3" is standard and unambiguous, and the
incorrect answer differs from the correct one in bit 6, which the question does
not mention.

The GPIO families were re-run alone at 10 epochs: 60 of 60 correct, including 10
of 10 on `gpio-rmw.rename`. Across Run C and the probe that item stands at 12 of
13.

**Treated as sampling noise.** With no temperature control and adaptive thinking,
an occasional arithmetic slip is expected, and a targeted re-run is cheap enough
that guessing was unnecessary.

## Interpretation

**No instance dependence was detected.** `renumber_delta` was 0.00 in every run.
Every renumbered item was answered correctly, including value combinations
unlikely to exist in training data as a stored pair. On this item set the model
performs the calculations rather than recalling them.

**No surface-form dependence was detected either.** Both non-zero rename deltas
were explained: one by an ambiguous item, one by sampling noise. Neither survived
a controlled re-run.

**The benchmark is at ceiling and cannot currently detect what it was built to
detect.** With base accuracy at 100% across three runs, both deltas are
structurally incapable of returning anything but zero or noise. "No robustness
gap exists" and "the item set is too easy to reveal one" are indistinguishable
from this data. These results describe the instrument as much as the model.

**Two false positives, two different causes, both resolved by re-running.** That
is the part of this worth reproducing at larger scale: a small anomaly, a
localising metric, a hypothesis about its cause, and a cheap controlled run that
distinguishes item defect from model behaviour from noise.

## What would make the next run informative

Harder items, so base accuracy sits below ceiling and the deltas have room to
move. Multi-step calculations, and items presenting C source rather than prose,
are the obvious increments. A set where a strong model scores 80 to 90 percent
would let the perturbation metrics measure something; the present set cannot.

## Reproducing

```bash
git checkout 16e1ef2
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]" anthropic
export ANTHROPIC_API_KEY=...
inspect eval src/regbench/task.py --model anthropic/claude-sonnet-5 --epochs 3
```

Exact reproduction is not possible. The model does not accept a temperature
parameter, runs with adaptive thinking, and the alias may resolve to a different
snapshot over time. Expect variation of roughly the size seen between Runs B and
C, which differed by one sample out of 180.
