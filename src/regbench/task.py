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


def _as_list(value: str | list[str] | None) -> list[str] | None:
    """Normalise a task filter argument to a list of names.

    Inspect parses a comma-separated ``-T`` value into a list but leaves a single
    value as a string, so a filter argument arrives as either type depending on
    how many values the caller passed.
    """
    if value is None:
        return None
    if isinstance(value, str):
        names = [name.strip() for name in value.split(",")]
    else:
        names = [str(name).strip() for name in value]
    return [name for name in names if name] or None


@task
def regbench(
    dataset: str | Path = DEFAULT_DATASET,
    domains: str | list[str] | None = None,
    variants: str | list[str] | None = None,
) -> Task:
    """Register-level embedded systems reasoning, scored across paired perturbations.

    Args:
        dataset: Path to the JSONL item file.
        domains: Domains to keep, as a comma-separated string or a list.
        variants: Variants to keep, as a comma-separated string or a list.

    Returns:
        The configured Inspect task.
    """
    return Task(
        dataset=regbench_dataset(
            dataset,
            domains=_as_list(domains),
            variants=_as_list(variants),
        ),
        solver=[system_message(SYSTEM_PROMPT), generate()],
        scorer=answer_match(),
    )
