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

A single accuracy number hides two distinct failure modes:

- **Surface-form dependence.** The response tracked how the question was worded
  rather than what it asked. Rewording moves the score.
- **Instance dependence.** The response reproduced a worked example rather than
  applying the method. Changing the input values moves the score.

regbench separates them by construction. Each family contains:

| Variant | What changes | Answer |
| --- | --- | --- |
| `base` | nothing, this is the item as written | - |
| `rename` | identifiers, peripheral names, phrasing | unchanged |
| `renumber` | the input values | recomputed |

A `rename` that costs accuracy is surface-form dependence: the question did not
change. A `renumber` that costs accuracy means the method did not transfer to
values that cannot have been memorised in that combination. Both are reported as
signed deltas in percentage points against the `base` items.

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
figure shows that.

`no_answer_rate` stays out of accuracy: ignoring the output format is a failure
of instruction following, not of embedded systems reasoning.

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

This checks transcription, unit prefixes and arithmetic, not the physics. One
author wrote both paths, so a conceptual error in a formula appears in both and
passes; `docs/REVIEW_CHECKLIST.md` covers that case by review. The first run of
this script caught a wrong hand-computed bit-field answer.

## Running it

```bash
git clone https://github.com/jSubbz/regbench && cd regbench
python3 -m venv .venv && source .venv/bin/activate
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
python tools/verify_answers.py
pytest
ruff check . && ruff format --check .
```

`docs/ADDING_ITEMS.md` covers the run and test loop in more detail, and the
procedure for adding a family of items.

## Limitations

- **Small.** 20 families demonstrates the method. The standard error on 60 items
  is too wide to rank models against each other.
- **One author.** A consistent misconception would be invisible. A second domain
  reviewer is the next step.
- **Perturbations are hand-written.** Keeps the key auditable, caps the item
  count. Generating them would scale it and move the correctness risk into the
  generator.
- **One perturbation per family.** No variance estimate. Read the aggregate over
  20 families, not an individual delta.
- **No contamination claim.** `renumber` makes a memorised instance less useful.
  It does not prove a model never saw the material.
- **Publication starts the clock.** These items are public, so future models may
  train on them, and the `renumber` signal weakens as that happens. Results are
  dated and tied to a commit for that reason. A held-out split is the standard
  fix and is not implemented here.
- **Difficulty is self-labelled**, not calibrated against measured performance.

## Scope

Built in about a week as a self-directed project, and my first using Inspect.
The embedded content comes from two years of computer engineering technology
coursework and a capstone build; the evaluation methodology is newer to me than
the subject matter. Design decisions are in `docs/METHODOLOGY.md`.

Results from two runs against `claude-sonnet-5` are in `docs/RESULTS.md`,
including an item defect the first run exposed and the controlled re-run that
resolved it.

## Licence

MIT. See `LICENSE`.
