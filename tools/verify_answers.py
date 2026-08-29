#!/usr/bin/env python3
"""Recompute the answer key from each item's stored formula and report disagreements.

Every computational item in ``data/items.jsonl`` carries a ``check`` block holding
the expression and the input values that produce its answer. The ``target`` field
holds the answer as it was written by hand. This script evaluates the expression
and compares the result against the hand-written target.

The two paths are not fully independent, since the same author wrote both. What
this catches is transcription slips, unit-prefix mistakes and arithmetic errors.
It does not catch a conceptual error in the formula itself, which is the job of
human review. See docs/METHODOLOGY.md.

Exit status is 0 when every checked item agrees and 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from regbench.parsing import parse_integer  # noqa: E402
from regbench.units import parse_quantity  # noqa: E402

# Names the check expressions are permitted to reference.
_ALLOWED_NAMES = {"math": math, "int": int, "abs": abs, "min": min, "max": max, "round": round}

DEFAULT_DATASET = Path(__file__).resolve().parent.parent / "data" / "items.jsonl"


def evaluate_check(check: dict) -> float:
    """Evaluate a check expression against its stored input values."""
    environment = dict(_ALLOWED_NAMES)
    environment.update(check.get("vars", {}))
    return eval(check["expr"], {"__builtins__": {}}, environment)  # noqa: S307


def verify_item(item: dict) -> str | None:
    """Return a description of the disagreement for one item, or None if it agrees."""
    check = item.get("check")
    if check is None:
        return None

    computed = evaluate_check(check)

    if item["answer_type"] == "integer":
        expected = parse_integer(item["target"])
        if int(computed) != expected:
            return f"computed {int(computed)} but target is {expected}"
        return None

    if item["answer_type"] == "quantity":
        computed_q = parse_quantity(str(computed), check["unit"])
        target_q = parse_quantity(item["target"], item["unit"])
        # The hand-written target is rounded for readability, so compare using the
        # item's own tolerance rather than demanding exact equality.
        if not target_q.close_to(computed_q, item["tolerance"]):
            return (
                f"computed {computed_q.value:g} but target is {target_q.value:g} "
                f"(rel tol {item['tolerance']:g})"
            )
        return None

    return f"answer_type {item['answer_type']!r} does not support a check block"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()

    items = [json.loads(line) for line in args.dataset.read_text().splitlines() if line.strip()]
    checked = 0
    failures: list[str] = []

    for item in items:
        if item.get("check") is None:
            continue
        checked += 1
        problem = verify_item(item)
        if problem is not None:
            failures.append(f"{item['id']}: {problem}")

    unchecked = len(items) - checked
    print(f"verified {checked} of {len(items)} items ({unchecked} have no check block)")
    for failure in failures:
        print(f"  MISMATCH {failure}")
    if failures:
        print(f"{len(failures)} mismatch(es)")
        return 1
    print("answer key agrees with recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
