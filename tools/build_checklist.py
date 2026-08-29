#!/usr/bin/env python3
"""Regenerate docs/REVIEW_CHECKLIST.md from the item set.

The checklist is derived from data/items.jsonl and goes stale when the dataset
changes. Regenerating preserves boxes already ticked: the existing file is parsed
first and each family's state is carried over. Use --reset to clear them.

The summary table at the top is rendered from the per-family boxes, so ticking a
box below and rerunning this script updates the table.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATASET = ROOT / "data" / "items.jsonl"
DEFAULT_OUTPUT = ROOT / "docs" / "REVIEW_CHECKLIST.md"

CHECKS = ("Correct", "Unambiguous", "Rename holds", "Renumber holds")
VARIANT_ORDER = ("base", "rename", "renumber")
TICKED, UNTICKED = "✓", ""

PREAMBLE = """# Item review checklist

Review record for the item set. An item that cannot be explained on the spot
gets fixed or cut, not kept because the answer happens to be right.

Four checks per family:

- **Correct** - the answer is right and the rationale is why.
- **Unambiguous** - no other reading gives a different defensible answer.
- **Rename holds** - the rewrite changes nothing that affects the answer.
- **Renumber holds** - new inputs, recomputed correctly, same structure.

`tools/verify_answers.py` covers arithmetic and transcription on items with a
check block. It cannot judge whether a formula is the right formula or whether a
question is ambiguous. Families marked **manual** have no recomputed answer key,
so their answers rest on this review.

Each family below shows all three variants with their answers, so every check can
be made from this file alone.

- **Correct**: does the stated reasoning produce the base answer?
- **Unambiguous**: could another reading give a different defensible answer? Is
  every convention that could differ stated in the question?
- **Rename holds**: read the rename against the base. Same question underneath?
  (The answers are asserted identical by the test suite, so what you are judging
  is whether the rewrite changed what is being asked.)
- **Renumber holds**: same structure, new inputs, answer recomputed correctly?

Tick the boxes under each family, then rerun `tools/build_checklist.py` to update
the summary table. Ticks survive regeneration; `--reset` clears them.

"""

_SECTION_RE = re.compile(r"^### (\S+)\s*$", re.MULTILINE)
_BOX_RE = re.compile(r"^- \[([ xX])\] (.+?)\s*$", re.MULTILINE)


def read_state(path: Path) -> dict[str, set[str]]:
    """Parse an existing checklist and return the ticked checks per family."""
    if not path.exists():
        return {}

    text = path.read_text()
    state: dict[str, set[str]] = {}
    sections = list(_SECTION_RE.finditer(text))

    for index, match in enumerate(sections):
        family = match.group(1)
        end = sections[index + 1].start() if index + 1 < len(sections) else len(text)
        body = text[match.end() : end]
        state[family] = {name for mark, name in _BOX_RE.findall(body) if mark.lower() == "x"}

    return state


def build(items: list[dict], state: dict[str, set[str]]) -> str:
    """Render the checklist markdown, applying previously ticked boxes."""
    families: dict[str, dict[str, dict]] = {}
    for item in items:
        families.setdefault(item["family"], {})[item["variant"]] = item

    rows = []
    sections = ["\n## Families\n"]
    complete = 0

    for family, variants in families.items():
        base = variants["base"]
        ticked = state.get(family, set())
        check = "auto" if base.get("check") else "**manual**"

        marks = " | ".join(TICKED if name in ticked else UNTICKED for name in CHECKS)
        rows.append(f"| [`{family}`](#{family}) | {base['domain']} | {check} | {marks} |")
        if len(ticked & set(CHECKS)) == len(CHECKS):
            complete += 1

        unit = f" {base['unit']}" if base["unit"] else ""
        sections.append(f"\n### {family}\n")
        sections.append(f"{base['domain']}, {base['difficulty']}, {check}\n")

        # All three variants, so every check can be made without opening the JSONL.
        for variant in VARIANT_ORDER:
            item = variants.get(variant)
            if item is None:
                continue
            item_unit = f" {item['unit']}" if item["unit"] else ""
            sections.append(f"\n**{variant}** -> `{item['target']}`{item_unit}\n")
            sections.append(f"\n> {item['question']}\n")

        sections.append(f"\nWhy `{base['target']}`{unit}: {base['rationale']}\n")
        sections.append(
            "\n"
            + "\n".join(f"- [{'x' if name in ticked else ' '}] {name}" for name in CHECKS)
            + "\n"
        )

    progress = f"**{complete} of {len(families)} families reviewed.**\n\n"
    header = (
        "| Family | Domain | Check | Correct | Unambiguous | Rename | Renumber |\n"
        "| --- | --- | --- | :-: | :-: | :-: | :-: |\n"
    )
    return PREAMBLE + progress + header + "\n".join(rows) + "\n" + "".join(sections)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reset", action="store_true", help="clear all ticked boxes")
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the output file is out of date instead of rewriting it",
    )
    args = parser.parse_args()

    items = [json.loads(line) for line in args.dataset.read_text().splitlines() if line.strip()]
    state = {} if args.reset else read_state(args.output)
    rendered = build(items, state)

    if args.check:
        current = args.output.read_text() if args.output.exists() else ""
        if current != rendered:
            print(f"{args.output} is out of date; run tools/build_checklist.py", file=sys.stderr)
            return 1
        print(f"{args.output} is up to date")
        return 0

    args.output.write_text(rendered)
    families = len({item["family"] for item in items})
    print(f"wrote {args.output} ({families} families, {len(items)} items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
