#!/usr/bin/env python3
"""Run the benchmark against the built-in mock model and print the metrics.

This needs no API credentials. The mock answers every item from the answer key
except the variants named with ``--fail``, which makes it a demonstration of what
the perturbation metrics do rather than a measurement of anything. Use it to
check an installation, or to see the shape of a report before spending tokens.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from inspect_ai import eval as inspect_eval  # noqa: E402
from inspect_ai.model import ModelOutput  # noqa: E402

from regbench.dataset import read_items  # noqa: E402
from regbench.task import regbench  # noqa: E402

MODEL = "mockllm/model"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail",
        default="",
        help="comma-separated variants the mock should answer incorrectly, e.g. renumber",
    )
    parser.add_argument("--log-dir", default="logs/smoke")
    args = parser.parse_args()

    failing = {v.strip() for v in args.fail.split(",") if v.strip()}
    items = {item["question"]: item for item in read_items()}

    def respond(messages, tools, tool_choice, config) -> ModelOutput:
        item = items[messages[-1].text]
        answer = "unanswerable" if item["variant"] in failing else item["target"]
        return ModelOutput.from_content(model=MODEL, content=f"Reasoning.\nANSWER: {answer}")

    logs = inspect_eval(
        regbench(),
        model=MODEL,
        model_args={"custom_outputs": respond},
        log_dir=args.log_dir,
        display="none",
    )
    log = logs[0]
    if log.status != "success":
        print(f"run failed: {log.error}", file=sys.stderr)
        return 1

    label = f"mock, failing variants: {', '.join(sorted(failing)) or 'none'}"
    print(f"\nregbench smoke run ({label})")
    print(f"{log.results.total_samples} samples\n")
    for name, metric in log.results.scores[0].metrics.items():
        print(f"  {name:24s} {metric.value:8.4f}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
