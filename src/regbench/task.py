"""The regbench Inspect task."""

from __future__ import annotations

from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.solver import generate, system_message

from regbench.dataset import DEFAULT_DATASET, regbench_dataset
from regbench.scorer import answer_match

SYSTEM_PROMPT = """You are answering questions about embedded systems hardware and \
real-time software. Work through the problem, then give your final answer on its own \
line in exactly this form:

ANSWER: <value>

Give the value in the units and number base the question asks for. Do not add commentary \
after the ANSWER line."""


@task
def regbench(
    dataset: str | Path = DEFAULT_DATASET,
    domains: str | None = None,
    variants: str | None = None,
) -> Task:
    """Register-level embedded systems reasoning, scored across paired perturbations.

    Args:
        dataset: Path to the JSONL item file.
        domains: Optional comma-separated list of domains to keep.
        variants: Optional comma-separated list of variants to keep.

    Returns:
        The configured Inspect task.
    """
    return Task(
        dataset=regbench_dataset(
            dataset,
            domains=domains.split(",") if domains else None,
            variants=variants.split(",") if variants else None,
        ),
        solver=[system_message(SYSTEM_PROMPT), generate()],
        scorer=answer_match(),
    )
