#!/usr/bin/env python3
"""List the incorrectly scored samples from an eval log.

The viewer shows this too, but a printed list is easier to work from when
deciding whether a failure is a model error or a defect in the item.

Defaults to the most recent log in logs/.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from inspect_ai.log import list_eval_logs, read_eval_log
from inspect_ai.scorer import CORRECT

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG_DIR = ROOT / "logs"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", nargs="?", help="path to an .eval log (default: most recent)")
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--full", action="store_true", help="print the full model response")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="also search subdirectories of --log-dir, such as logs/smoke",
    )
    args = parser.parse_args()

    if args.log:
        log_file = args.log
    else:
        logs = list_eval_logs(str(args.log_dir), recursive=args.recursive)
        if not logs:
            print(f"no logs found in {args.log_dir}")
            return 1
        # Sort by modification time. Sorting on the path would rank a log in a
        # subdirectory above a newer one in the root, since the directory name
        # is compared before the timestamp in the filename.
        log_file = max(logs, key=lambda entry: entry.mtime or 0).name

    log = read_eval_log(log_file)
    print(f"{log_file}\nmodel: {log.eval.model}\n")
    if log.eval.model.startswith("mockllm/"):
        print("NOTE: this is a mock run and measures nothing about any model.\n")

    failures = 0
    for sample in log.samples or []:
        for scorer_name, score in (sample.scores or {}).items():
            if score.value == CORRECT:
                continue
            failures += 1
            metadata = sample.metadata or {}
            print(f"{sample.id}  epoch {sample.epoch}  [{scorer_name}]")
            print(f"  variant   {metadata.get('variant')}")
            print(f"  expected  {sample.target}")
            print(f"  answered  {score.answer!r}")
            print(f"  scorer    {score.explanation}")
            if args.full:
                print(f"  response  {sample.output.completion}\n")
            print()

    total = len(log.samples or [])
    print(f"{failures} incorrect of {total} samples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
