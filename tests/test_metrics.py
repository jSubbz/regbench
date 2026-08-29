"""Unit tests for the perturbation metrics, using synthetic scores.

The end-to-end tests cover the common path. These cover the edge cases that a
real run is unlikely to produce but that would silently corrupt a reported
number if handled wrongly.
"""

import pytest
from inspect_ai.scorer import CORRECT, INCORRECT, SampleScore, Score

from regbench.metrics import (
    no_answer_rate,
    rename_consistency,
    rename_delta,
    renumber_consistency,
)


def sample(family: str, variant: str, correct: bool, answered: bool = True) -> SampleScore:
    return SampleScore(
        score=Score(value=CORRECT if correct else INCORRECT, metadata={"answered": answered}),
        sample_id=f"{family}.{variant}",
        sample_metadata={"family": family, "variant": variant},
    )


class TestRenameDelta:
    def test_zero_when_variants_match(self):
        scores = [sample("f1", "base", True), sample("f1", "rename", True)]
        assert rename_delta()(scores) == pytest.approx(0.0)

    def test_positive_when_rename_is_worse(self):
        scores = [sample("f1", "base", True), sample("f1", "rename", False)]
        assert rename_delta()(scores) == pytest.approx(100.0)

    def test_negative_when_rename_is_better(self):
        scores = [sample("f1", "base", False), sample("f1", "rename", True)]
        assert rename_delta()(scores) == pytest.approx(-100.0)

    def test_zero_when_a_group_is_missing(self):
        assert rename_delta()([sample("f1", "base", True)]) == pytest.approx(0.0)

    def test_zero_for_empty_input(self):
        assert rename_delta()([]) == pytest.approx(0.0)


class TestConsistency:
    def test_agreeing_families_count(self):
        scores = [
            sample("f1", "base", True),
            sample("f1", "rename", True),
            sample("f2", "base", False),
            sample("f2", "rename", False),
        ]
        assert rename_consistency()(scores) == pytest.approx(1.0)

    def test_disagreeing_families_do_not(self):
        scores = [sample("f1", "base", True), sample("f1", "rename", False)]
        assert rename_consistency()(scores) == pytest.approx(0.0)

    def test_consistency_separates_models_the_delta_cannot(self):
        """Two families swapped between variants: delta is zero, agreement is zero."""
        scores = [
            sample("f1", "base", True),
            sample("f1", "renumber", False),
            sample("f2", "base", False),
            sample("f2", "renumber", True),
        ]
        assert renumber_consistency()(scores) == pytest.approx(0.0)

    def test_incomplete_families_are_skipped(self):
        scores = [
            sample("f1", "base", True),
            sample("f1", "rename", True),
            sample("f2", "base", True),
        ]
        assert rename_consistency()(scores) == pytest.approx(1.0)


class TestNoAnswerRate:
    def test_counts_unanswered(self):
        scores = [
            sample("f1", "base", False, answered=False),
            sample("f2", "base", True, answered=True),
        ]
        assert no_answer_rate()(scores) == pytest.approx(0.5)

    def test_zero_for_empty_input(self):
        assert no_answer_rate()([]) == pytest.approx(0.0)
