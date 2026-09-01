# Working on regbench

Setup, the run and test loop, and how to add a family of items.

## Setup, once

```bash
cd ~/Documents/Projects/regbench
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

`-e` is editable mode, so `src/regbench` stays live as you edit. `[dev]` adds
pytest and ruff.

## Running the benchmark

**Against the mock model, no credentials:**

```bash
python tools/smoke_run.py
python tools/smoke_run.py --fail renumber
```

The mock answers from the answer key, so it measures nothing about any model.
It checks the harness is wired up and shows the shape of a report.
`--fail renumber` makes the mock fail the renumbered items, which is the quickest
way to see the perturbation metrics move.

**Against a real provider:**

```bash
export OPENAI_API_KEY=...          # or ANTHROPIC_API_KEY, etc.
inspect eval src/regbench/task.py --model openai/gpt-4o
inspect view
```

`inspect view` opens a local log browser: per sample, the prompt, full response,
extracted answer and scorer reasoning. First place to look when a score seems
wrong. Low accuracy with a high `no_answer_rate` means the format instruction is
being ignored, not that the arithmetic failed.

**Subsets**, so you are not paying for 60 samples on every iteration:

```bash
inspect eval src/regbench/task.py --model openai/gpt-4o -T domains=i2c,spi
inspect eval src/regbench/task.py --model openai/gpt-4o -T variants=base
inspect eval src/regbench/task.py --model openai/gpt-4o --limit 5
```

`-T` passes through to the `@task` function. `--limit` is Inspect's own flag and
takes the first n samples.

## The check loop

Cheapest first, since each catches a different class of mistake:

```bash
python tools/verify_answers.py     # arithmetic and transcription in the answer key
pytest -q                          # structure, parsing, metrics, end-to-end
ruff check . && ruff format --check .
```

What each covers:

| Command | Catches |
| --- | --- |
| `verify_answers.py` | An answer that disagrees with its own stored formula |
| `tests/test_dataset.py` | Missing variants, duplicate ids or questions, a rename that changed the answer, a quantity item with no unit or tolerance |
| `tests/test_parsing.py` | Answer extraction and comparison across number bases, units and aliases |
| `tests/test_metrics.py` | Metric edge cases: empty groups, incomplete families, sign of the deltas |
| `tests/test_eval_end_to_end.py` | The whole task running against scripted responses, with exact expected metric values |
| `ruff` | Lint and formatting, same as CI |

CI runs all of it on Python 3.10 and 3.12.

## Adding a family of items

A family is one calculation in three variants. Work in this order.

### 1. Decide what the family tests

One computation, one defensible answer, explainable in two sentences without
notes. If you cannot, it is too big or ambiguous. Split it or drop it.

### 2. Write the base item

Append one JSON object per line to `data/items.jsonl`. No pretty printing.

```json
{"id": "spi-mode.base", "family": "spi-mode", "variant": "base", "domain": "spi", "difficulty": "easy", "question": "...", "answer_type": "integer", "target": "2", "unit": null, "tolerance": 0.0, "aliases": [], "check": {"expr": "cpol * 2 + cpha", "vars": {"cpol": 1, "cpha": 0}}, "rationale": "..."}
```

Field by field:

| Field | Rule |
| --- | --- |
| `id` | Must be exactly `family.variant`. Enforced by a test. |
| `family` | Slug shared by all three variants. |
| `variant` | One of `base`, `rename`, `renumber`. |
| `domain` | Free-form slug used by the `-T domains=` filter. |
| `difficulty` | `easy`, `medium` or `hard`. Self-labelled, not calibrated. Reported separately by `difficulty_accuracy`. |
| `question` | The prompt. Must be unique across the whole file. State any convention that could differ, and name the unit and number base you want back. |
| `answer_type` | `integer`, `quantity` or `choice`. |
| `target` | The answer as a string, in the unit named in `unit`. |
| `unit` | The unit the question asks for, on `quantity` items. Must be `null` on the other two types. |
| `tolerance` | Relative tolerance, on `quantity` items. Must be greater than zero. |
| `radix` | Base for unprefixed digits, on `integer` items: 16 when the question asks for hexadecimal, 10 otherwise. Must be `null` on the other types, and must agree with the question wording. Both are asserted by tests. |
| `aliases` | Extra accepted spellings, on `choice` items. |
| `check` | Formula and inputs, on computational items. `null` for `choice`. |
| `rationale` | The calculation in prose, for review. |

State any convention that could differ. `V = code x Vref / 2^N` and
`V = code x Vref / (2^N - 1)` are both in use; an item that does not say which it
means is ambiguous rather than hard.

### 3. Write the rename variant

Change identifiers, peripheral names, signal names and sentence structure.
Change nothing that affects the answer. `target` must be identical to the base
item's, asserted by a test for `integer` and `quantity`.

Swapping one word is too weak: it tests a token, not presentation. Rewrite the
sentence.

This applies to `choice` items too. Restate the scenario without renaming the
entity that is itself the answer: renaming Task `A` to `t_sensor` would change
the answer string and put the item outside the check.

### 4. Write the renumber variant

Keep the structure, change the inputs, recompute. Pick values that move the
answer meaningfully rather than by rounding, and avoid numbers that already
appear in the base item.

### 5. Add the check block

`expr` is a Python expression over the names in `vars`. Only `math`, `int`,
`abs`, `min`, `max` and `round` are available besides your own variables.

```json
"check": {"expr": "fclk / (presc * (top + 1))", "vars": {"fclk": 48e6, "presc": 16, "top": 749}, "unit": "Hz"}
```

`check.unit` is the unit the expression result is in, often not the unit the
question asks for. The verifier converts before comparing, so Hz against a kHz
target is fine.

Write `expr` from the physics, not backwards from the number you already
computed. The check works because two paths reach the same answer; deriving the
formula from the target removes the only thing it catches.

`choice` items get `"check": null` and rely entirely on review.

### 6. Verify, then test

```bash
python tools/verify_answers.py
pytest -q
```

`verify_answers.py` finds arithmetic slips. `test_dataset.py` finds structural
mistakes, usually a missing third variant or a question duplicated by copy-paste.

### 7. Regenerate the checklist

```bash
python tools/build_checklist.py
```

This rewrites `docs/REVIEW_CHECKLIST.md` from the dataset and resets the boxes,
so regenerate before a review pass, not after.

### 8. Review, then commit

Walk the new family against the four checks in the checklist. An item you cannot
defend gets fixed or cut.

```bash
git add data/items.jsonl docs/REVIEW_CHECKLIST.md
git commit -m "items: add <family> family"
git push
```

## Common mistakes

- **Rename changed the answer.** `test_rename_variant_keeps_the_base_answer`
  fails. Usually a number was altered along with the wording.
- **Duplicate question.** `test_questions_are_unique` fails. Two variants were
  copied and only one was edited.
- **Quantity item with `tolerance: 0`.** Fails a test. Exact float comparison
  against a rounded target will reject correct answers.
- **Unit on a non-quantity item.** Fails a test. `integer` and `choice` items
  must have `"unit": null`.
- **`check` written backwards from the target.** Passes every test and catches
  nothing. No test can detect it.
