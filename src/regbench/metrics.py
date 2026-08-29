"""Metrics that read the perturbation structure of the item set.

Every item belongs to a family and carries a variant label. ``base`` is the item
as first written; ``rename`` restates it with different identifiers and wording
but the same answer; ``renumber`` changes the input values so the answer changes
too. Comparing performance across those labels separates two failure modes that
a single accuracy figure hides:

* A drop from ``base`` to ``rename`` means the response depended on surface form,
  since the underlying question did not change.
* A drop from ``base`` to ``renumber`` means the reasoning did not transfer to
  unseen values, which is the pattern expected from a memorised instance.

Both are reported as signed deltas in percentage points, so a positive value
means the model did worse than on the base items.
"""

from __future__ import annotations

from inspect_ai.scorer import (
    Metric,
    SampleScore,
    Value,
    ValueToFloat,
    accuracy,
    grouped,
    metric,
    value_to_float,
)


def _group_by_variant(scores: list[SampleScore]) -> dict[str, list[SampleScore]]:
    """Bucket sample scores by their variant label."""
    groups: dict[str, list[SampleScore]] = {}
    for sample_score in scores:
        metadata = sample_score.sample_metadata or {}
        variant = str(metadata.get("variant", "unknown"))
        groups.setdefault(variant, []).append(sample_score)
    return groups


# Module-level singleton so the default is not constructed at each call site.
_TO_FLOAT: ValueToFloat = value_to_float()


def _mean(values: list[float]) -> float:
    """Return the mean of a list, or 0.0 when it is empty."""
    return sum(values) / len(values) if values else 0.0


def variant_accuracy() -> Metric:
    """Accuracy broken out per variant, alongside the overall figure."""
    return grouped(accuracy(), "variant", all="samples", all_label="all")


def _delta(
    comparison: str,
    reference: str = "base",
    to_float: ValueToFloat = _TO_FLOAT,
) -> Metric:
    """Accuracy lost when moving from the reference variant to a comparison variant.

    Args:
        comparison: The variant to compare against the reference.
        reference: The variant treated as the baseline.
        to_float: Converts score values to floats.

    Returns:
        A metric reporting the drop in percentage points. A positive value means
        accuracy fell on the comparison variant.
    """

    def compute(scores: list[SampleScore]) -> Value:
        groups = _group_by_variant(scores)
        reference_scores = [to_float(s.score.value) for s in groups.get(reference, [])]
        comparison_scores = [to_float(s.score.value) for s in groups.get(comparison, [])]
        if not reference_scores or not comparison_scores:
            return 0.0
        return 100.0 * (_mean(reference_scores) - _mean(comparison_scores))

    return compute


def _consistency(
    comparison: str,
    reference: str = "base",
    to_float: ValueToFloat = _TO_FLOAT,
) -> Metric:
    """Fraction of families whose reference and comparison items are graded alike.

    This is a stricter reading of robustness than the delta. A model that gets a
    different half of the item set right on each variant scores a delta near zero
    while agreeing on very few individual families, and only this metric shows it.

    Args:
        comparison: The variant to pair against the reference.
        reference: The variant treated as the baseline.
        to_float: Converts score values to floats.

    Returns:
        A metric reporting the agreeing fraction, between 0 and 1.
    """

    def compute(scores: list[SampleScore]) -> Value:
        by_family: dict[str, dict[str, float]] = {}
        for sample_score in scores:
            metadata = sample_score.sample_metadata or {}
            family = str(metadata.get("family", "unknown"))
            variant = str(metadata.get("variant", "unknown"))
            by_family.setdefault(family, {})[variant] = to_float(sample_score.score.value)

        pairs = [
            (v[reference], v[comparison])
            for v in by_family.values()
            if reference in v and comparison in v
        ]
        if not pairs:
            return 0.0
        return _mean([1.0 if a == b else 0.0 for a, b in pairs])

    return compute


@metric
def no_answer_rate() -> Metric:
    """Fraction of responses that contained no parsable ANSWER line.

    A high rate means the headline accuracy is measuring instruction following as
    much as it is measuring embedded systems reasoning, so it is reported
    separately rather than folded into the score.
    """

    def compute(scores: list[SampleScore]) -> Value:
        if not scores:
            return 0.0
        missing = [0.0 if (s.score.metadata or {}).get("answered", True) else 1.0 for s in scores]
        return _mean(missing)

    return compute


@metric
def rename_delta() -> Metric:
    """Accuracy lost between the base items and their renamed restatements.

    Reported in percentage points. A positive value means the response depended
    on surface form, since a rename leaves the underlying question unchanged.
    """
    return _delta("rename")


@metric
def renumber_delta() -> Metric:
    """Accuracy lost between the base items and their renumbered counterparts.

    Reported in percentage points. A positive value means the reasoning did not
    transfer to input values the model cannot have seen in this exact form.
    """
    return _delta("renumber")


@metric
def rename_consistency() -> Metric:
    """Fraction of families graded alike on the base and renamed items."""
    return _consistency("rename")


@metric
def renumber_consistency() -> Metric:
    """Fraction of families graded alike on the base and renumbered items."""
    return _consistency("renumber")
