"""The regbench scorer.

Responses are graded on the value given on their final ``ANSWER:`` line, using
the comparison rules for the item's declared answer type. Grading is
deterministic and needs no grader model, which keeps scores reproducible and
makes the whole benchmark runnable without API credentials.
"""

from __future__ import annotations

from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState

from .metrics import (
    no_answer_rate,
    rename_consistency,
    rename_delta,
    renumber_consistency,
    renumber_delta,
    variant_accuracy,
)
from .parsing import compare


@scorer(
    metrics=[
        accuracy(),
        stderr(),
        variant_accuracy(),
        rename_delta(),
        renumber_delta(),
        rename_consistency(),
        renumber_consistency(),
        no_answer_rate(),
    ]
)
def answer_match():
    """Score a response by parsing and comparing its final ANSWER line."""

    async def score(state: TaskState, target: Target) -> Score:
        metadata = state.metadata or {}
        verdict = compare(
            state.output.completion,
            answer_type=metadata["answer_type"],
            target=target.text,
            unit=metadata.get("unit"),
            tolerance=metadata.get("tolerance") or 0.0,
            aliases=metadata.get("aliases") or [],
        )
        return Score(
            value=CORRECT if verdict.correct else INCORRECT,
            answer=verdict.extracted,
            explanation=verdict.reason,
            metadata={"answered": verdict.answered},
        )

    return score
