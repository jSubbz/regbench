"""End-to-end runs of the task against a scripted mock model.

These exercise the wiring between dataset, solver, scorer and metrics without
contacting any provider, so the suite runs in CI with no credentials. The mock
answers each item from the answer key, which lets the tests assert exact metric
values for a known response pattern.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from inspect_ai import eval as inspect_eval
from inspect_ai.model import ModelOutput

from regbench.dataset import read_items
from regbench.task import regbench

MODEL = "mockllm/model"
ITEMS = read_items()
TARGET_BY_QUESTION = {item["question"]: item for item in ITEMS}


def _responder(decide: Callable[[dict], bool]) -> Callable:
    """Build a mock model that answers correctly only when ``decide`` says so."""

    def respond(messages, tools, tool_choice, config) -> ModelOutput:
        question = messages[-1].text
        item = TARGET_BY_QUESTION[question]
        if decide(item):
            content = f"Working through it.\nANSWER: {item['target']}"
        else:
            content = "Working through it.\nANSWER: definitely-wrong"
        return ModelOutput.from_content(model=MODEL, content=content)

    return respond


def run(decide: Callable[[dict], bool], tmp_path) -> dict[str, float]:
    """Run the task against a scripted model and return its metric values."""
    logs = inspect_eval(
        regbench(),
        model=MODEL,
        model_args={"custom_outputs": _responder(decide)},
        log_dir=str(tmp_path),
        display="none",
    )
    assert logs[0].status == "success", logs[0].error
    scores = logs[0].results.scores
    assert len(scores) == 1
    return {name: metric.value for name, metric in scores[0].metrics.items()}


@pytest.fixture(scope="module")
def all_correct(tmp_path_factory):
    return run(lambda item: True, tmp_path_factory.mktemp("all_correct"))


@pytest.fixture(scope="module")
def renumber_fails(tmp_path_factory):
    return run(lambda item: item["variant"] != "renumber", tmp_path_factory.mktemp("renumber"))


class TestAllCorrect:
    def test_accuracy_is_one(self, all_correct):
        assert all_correct["accuracy"] == pytest.approx(1.0)

    def test_no_answer_rate_is_zero(self, all_correct):
        assert all_correct["no_answer_rate"] == pytest.approx(0.0)

    def test_both_deltas_are_zero(self, all_correct):
        assert all_correct["rename_delta"] == pytest.approx(0.0)
        assert all_correct["renumber_delta"] == pytest.approx(0.0)

    def test_both_consistencies_are_one(self, all_correct):
        assert all_correct["rename_consistency"] == pytest.approx(1.0)
        assert all_correct["renumber_consistency"] == pytest.approx(1.0)

    def test_per_variant_accuracies_are_one(self, all_correct):
        for variant in ("base", "rename", "renumber"):
            assert all_correct[variant] == pytest.approx(1.0)


class TestRenumberFails:
    def test_accuracy_reflects_the_failing_third(self, renumber_fails):
        assert renumber_fails["accuracy"] == pytest.approx(2 / 3)

    def test_rename_is_unaffected(self, renumber_fails):
        assert renumber_fails["rename_delta"] == pytest.approx(0.0)
        assert renumber_fails["rename_consistency"] == pytest.approx(1.0)

    def test_renumber_delta_is_a_full_hundred_points(self, renumber_fails):
        assert renumber_fails["renumber_delta"] == pytest.approx(100.0)

    def test_renumber_consistency_collapses(self, renumber_fails):
        assert renumber_fails["renumber_consistency"] == pytest.approx(0.0)

    def test_per_variant_accuracies_split(self, renumber_fails):
        assert renumber_fails["base"] == pytest.approx(1.0)
        assert renumber_fails["rename"] == pytest.approx(1.0)
        assert renumber_fails["renumber"] == pytest.approx(0.0)


def test_unparsable_answers_are_marked_unanswered(tmp_path):
    def respond(messages, tools, tool_choice, config) -> ModelOutput:
        return ModelOutput.from_content(model=MODEL, content="I am not going to say.")

    logs = inspect_eval(
        regbench(variants="base"),
        model=MODEL,
        model_args={"custom_outputs": respond},
        log_dir=str(tmp_path),
        display="none",
    )
    metrics = logs[0].results.scores[0].metrics
    assert metrics["accuracy"].value == pytest.approx(0.0)
    assert metrics["no_answer_rate"].value == pytest.approx(1.0)
