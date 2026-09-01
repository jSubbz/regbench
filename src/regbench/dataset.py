"""Loading of the regbench item set.

The dataset of record is ``data/items.jsonl``. Each line is one item: a question,
its answer key, and the metadata needed to score it and to group it for the
robustness metrics. Items are organised into families of three variants; see
docs/METHODOLOGY.md for the construction rules.
"""

from __future__ import annotations

import json
from pathlib import Path

from inspect_ai.dataset import MemoryDataset, Sample

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_DATASET = DATA_DIR / "items.jsonl"

VARIANTS = ("base", "rename", "renumber")
ANSWER_TYPES = ("integer", "quantity", "choice")

# Metadata keys copied verbatim from each record onto its Sample.
_METADATA_KEYS = (
    "family",
    "variant",
    "domain",
    "difficulty",
    "answer_type",
    "unit",
    "tolerance",
    "radix",
    "aliases",
    "rationale",
)


def resolve_dataset_path(path: Path | str) -> Path:
    """Resolve a dataset path, falling back to one relative to the project root.

    Inspect runs a task with a working directory that is not necessarily the one
    the command was typed in, so a relative ``-T dataset=`` argument does not
    resolve against the shell's cwd. Anything relative that is not found as given
    is retried against the project root, which is what a caller passing
    ``data/probes/x.jsonl`` from the repository means.
    """
    candidate = Path(path)
    if candidate.is_absolute() or candidate.exists():
        return candidate
    from_root = PROJECT_ROOT / candidate
    if from_root.exists():
        return from_root
    # Report the path the caller asked for rather than the rewritten one.
    return candidate


def read_items(path: Path | str = DEFAULT_DATASET) -> list[dict]:
    """Read the raw item records from a JSONL file."""
    text = resolve_dataset_path(path).read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def record_to_sample(record: dict) -> Sample:
    """Convert one raw record into an Inspect Sample."""
    return Sample(
        id=record["id"],
        input=record["question"],
        target=record["target"],
        metadata={key: record.get(key) for key in _METADATA_KEYS},
    )


def regbench_dataset(
    path: Path | str = DEFAULT_DATASET,
    *,
    domains: list[str] | None = None,
    variants: list[str] | None = None,
    families: list[str] | None = None,
) -> MemoryDataset:
    """Build the benchmark dataset, optionally restricted to domains or variants.

    Args:
        path: Location of the JSONL item file.
        domains: If given, keep only items whose domain appears in this list.
        variants: If given, keep only items whose variant appears in this list.
        families: If given, keep only items whose family appears in this list.

    Returns:
        A MemoryDataset of scored samples.
    """
    records = read_items(path)
    if domains is not None:
        records = [r for r in records if r["domain"] in domains]
    if variants is not None:
        records = [r for r in records if r["variant"] in variants]
    if families is not None:
        records = [r for r in records if r["family"] in families]
    return MemoryDataset(
        samples=[record_to_sample(r) for r in records],
        name="regbench",
        location=str(resolve_dataset_path(path)),
    )
