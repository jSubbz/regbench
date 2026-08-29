# regbench

[![CI](https://github.com/jSubbz/regbench/actions/workflows/ci.yml/badge.svg)](https://github.com/jSubbz/regbench/actions/workflows/ci.yml)

A small benchmark for register-level embedded systems reasoning, implemented with
[Inspect](https://inspect.aisi.org.uk/). Every question exists in three paired
forms, so a run reports not only how often a model is right but how much of that
score survives a change of wording or a change of numbers.

60 items across 20 families, covering I2C addressing, SPI configuration, UART
framing and baud generation, ADC quantization, PWM and timer configuration,
GPIO read-modify-write, register field extraction, and real-time scheduling and
QNX Neutrino message-passing IPC.

## The idea

A single accuracy number on a static question set answers "how often was the
model right", which is not quite the question worth asking. Two failure modes
hide inside it, and they call for different responses:

- The model was following the **surface form** of the question rather than its
  content, so a rewrite that changes nothing of substance moves the score.
- The model had the **specific instance** rather than the method, so the score
  falls once the input values change.

regbench separates them by construction. Each family contains:

| Variant | What changes | Answer |
| --- | --- | --- |
| `base` | nothing, this is the item as written | - |
| `rename` | identifiers, peripheral names, phrasing | unchanged |
| `renumber` | the input values | recomputed |

A `rename` that costs accuracy is a surface-form dependency, because the question
is the same question. A `renumber` that costs accuracy means the method did not
transfer to values that cannot have been memorised in that exact combination.
Both are reported as signed deltas in percentage points against the `base` items.

## Metrics

| Metric | Meaning |
| --- | --- |
| `accuracy`, `stderr` | overall, across all 60 items |
| `base`, `rename`, `renumber`, `all` | accuracy per variant |
| `rename_delta` | percentage points lost from `base` to `rename` |
| `renumber_delta` | percentage points lost from `base` to `renumber` |
| `rename_consistency` | fraction of families graded alike on both variants |
| `renumber_consistency` | same, for `base` against `renumber` |
| `no_answer_rate` | fraction of responses with no parsable `ANSWER:` line |

The consistency metrics exist because the deltas can be fooled. A model that
answers a different half of the item set correctly on each variant reports a
delta near zero while agreeing on almost no individual family. Only the paired
figure shows that, and it is the honest measure of whether the same knowledge is
being used both times.

`no_answer_rate` is reported separately rather than folded into accuracy, because
a response that ignores the output format is a failure of instruction following
rather than of embedded systems reasoning, and conflating the two makes the
headline number mean less.

## Scoring

Items declare one of three answer types, each with its own equality rule:

- `integer` - compared by numeric value, so `0x90`, `144` and `0b10010000` are
  the same answer. Decimal, hex and binary notations are all accepted.
- `quantity` - converted to a base SI unit and compared within a per-item
  relative tolerance, so `1.5 ms`, `1500 us` and `0.0015 s` are the same answer.
  A bare number is read as being in the unit the question asked for.
- `choice` - compared after case folding, with per-item aliases for spellings
  such as `SEND-blocked` against `SEND blocked`.

Grading is deterministic and uses no grader model. Scores are therefore
reproducible, and the whole benchmark runs with no API credentials.

## Answer key verification

Every computational item stores the formula and inputs that produce its answer
alongside the hand-written answer itself. `tools/verify_answers.py` recomputes
the key and reports disagreements, and it runs in CI:

```
$ python tools/verify_answers.py
verified 54 of 60 items (6 have no check block)
answer key agrees with recomputation
```

This is a check on transcription, unit prefixes and arithmetic, not on the
physics. Both paths were written by the same author, so a conceptual error in a
formula would appear in both. What catches that is human review, and
`docs/REVIEW_CHECKLIST.md` records how each item was reviewed. The first run of
this script found a genuine error in a hand-computed bit-field answer.

## Running it

```bash
git clone https://github.com/jSubbz/regbench && cd regbench
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

No credentials needed, against the built-in mock model:

```bash
python tools/smoke_run.py
```

Against a real provider:

```bash
export OPENAI_API_KEY=...
inspect eval src/regbench/task.py --model openai/gpt-4o
inspect view
```

Subsets:

```bash
inspect eval src/regbench/task.py --model openai/gpt-4o -T domains=i2c,spi
inspect eval src/regbench/task.py --model openai/gpt-4o -T variants=base
```

Tests and lint:

```bash
pytest
ruff check . && ruff format --check .
python tools/verify_answers.py
```

## Limitations

Stated plainly, because a benchmark that oversells itself is worse than no
benchmark.

- **It is small.** 20 families is enough to demonstrate the method and to
  separate the two failure modes at a coarse grain. It is not enough to rank
  frontier models against each other with confidence, and the standard error on
  60 items is wide.
- **One author.** Every item was written and reviewed by one person, so a
  consistent misconception would be invisible. A second reviewer from the domain
  is the obvious next step.
- **The perturbations are hand-written, not generated.** That keeps the answer
  key auditable, and it caps the item count. Generating perturbations
  programmatically would scale it but would move the correctness risk into the
  generator.
- **`rename` and `renumber` are single samples, not distributions.** A proper
  robustness estimate would draw several perturbations per family and report the
  variance across them. With one of each, an individual delta is noisy; the
  aggregate over 20 families is the number to read.
- **No contamination claim.** `renumber` makes memorisation of an exact instance
  less likely to help. It does not prove a model never saw the source material,
  and nothing here should be read as a contamination measurement.
- **Difficulty is uneven and self-labelled.** The `easy`/`medium` tags are the
  author's judgement, not calibrated against measured model performance.

## Scope

This was built in about a week as a self-directed project, and it is my first
project using Inspect. The embedded systems content comes from two years of
computer engineering technology coursework and a capstone build; the evaluation
methodology is newer to me than the subject matter is. Design decisions and the
reasoning behind them are in `docs/METHODOLOGY.md`.

No model results are published here. The repository ships the item set, the
harness and the metrics; running it against a provider needs your own key.

## Licence

MIT. See `LICENSE`.
