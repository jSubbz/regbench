"""Structural checks on the item set itself.

These run in CI so that a malformed or unbalanced item set fails the build rather
than silently producing a misleading score.
"""

import pytest

from regbench.dataset import ANSWER_TYPES, VARIANTS, read_items, regbench_dataset

ITEMS = read_items()
FAMILIES = sorted({item["family"] for item in ITEMS})


def test_dataset_is_not_empty():
    assert len(ITEMS) > 0


def test_ids_are_unique():
    ids = [item["id"] for item in ITEMS]
    assert len(ids) == len(set(ids))


def test_id_matches_family_and_variant():
    for item in ITEMS:
        assert item["id"] == f"{item['family']}.{item['variant']}"


@pytest.mark.parametrize("family", FAMILIES)
def test_every_family_has_every_variant(family):
    present = {item["variant"] for item in ITEMS if item["family"] == family}
    assert present == set(VARIANTS)


def test_difficulties_are_known():
    assert {item["difficulty"] for item in ITEMS} <= {"easy", "medium", "hard"}


def test_variants_are_known():
    assert {item["variant"] for item in ITEMS} <= set(VARIANTS)


def test_answer_types_are_known():
    assert {item["answer_type"] for item in ITEMS} <= set(ANSWER_TYPES)


def test_quantity_items_declare_unit_and_tolerance():
    for item in ITEMS:
        if item["answer_type"] == "quantity":
            assert item["unit"], f"{item['id']} has no unit"
            assert item["tolerance"] > 0, f"{item['id']} has no tolerance"


def test_non_quantity_items_declare_no_unit():
    for item in ITEMS:
        if item["answer_type"] != "quantity":
            assert item["unit"] is None, f"{item['id']} declares a unit"


def test_integer_items_declare_a_radix():
    for item in ITEMS:
        if item["answer_type"] == "integer":
            assert item["radix"] in (2, 10, 16), f"{item['id']} has no usable radix"
        else:
            assert item["radix"] is None, f"{item['id']} declares a radix"


def test_declared_radix_matches_the_question():
    for item in ITEMS:
        if item["answer_type"] != "integer":
            continue
        asks_hex = "hexadecimal" in item["question"].lower()
        assert item["radix"] == (16 if asks_hex else 10), f"{item['id']} radix disagrees"


def test_every_item_has_a_rationale():
    for item in ITEMS:
        assert item["rationale"].strip(), f"{item['id']} has no rationale"


def test_questions_are_unique():
    questions = [item["question"] for item in ITEMS]
    assert len(questions) == len(set(questions))


def test_rename_variant_keeps_the_base_answer():
    """A rename is a surface rewrite, so its answer must match its base item.

    This applies to every answer type, including choice. A choice rename must
    restate the scenario without renaming the entity that is itself the answer,
    since an item whose answer string changes cannot be checked here and would
    rely entirely on review.
    """
    by_id = {item["id"]: item for item in ITEMS}
    for family in FAMILIES:
        base = by_id[f"{family}.base"]
        rename = by_id[f"{family}.rename"]
        assert base["target"] == rename["target"], f"{family}: rename changed the answer"


def test_renumber_variant_changes_the_question():
    by_id = {item["id"]: item for item in ITEMS}
    for family in FAMILIES:
        base = by_id[f"{family}.base"]
        renumber = by_id[f"{family}.renumber"]
        assert base["question"] != renumber["question"]


def test_dataset_loads_as_samples():
    dataset = regbench_dataset()
    assert len(dataset) == len(ITEMS)
    sample = dataset[0]
    assert sample.metadata["variant"] in VARIANTS
    assert sample.target


def test_domain_filter():
    dataset = regbench_dataset(domains=["i2c"])
    assert len(dataset) > 0
    assert all(s.metadata["domain"] == "i2c" for s in dataset)


def test_variant_filter():
    dataset = regbench_dataset(variants=["base"])
    assert len(dataset) == len(FAMILIES)


class TestDatasetPathResolution:
    """Inspect runs tasks from a working directory of its own choosing."""

    def test_relative_path_resolves_against_the_project_root(self, monkeypatch, tmp_path):
        from regbench.dataset import resolve_dataset_path

        monkeypatch.chdir(tmp_path)
        resolved = resolve_dataset_path("data/items.jsonl")
        assert resolved.is_absolute()
        assert resolved.exists()

    def test_absolute_path_is_returned_unchanged(self):
        from regbench.dataset import DEFAULT_DATASET, resolve_dataset_path

        assert resolve_dataset_path(DEFAULT_DATASET) == DEFAULT_DATASET

    def test_dataset_loads_from_a_relative_path_off_cwd(self, monkeypatch, tmp_path):
        from regbench.dataset import regbench_dataset

        monkeypatch.chdir(tmp_path)
        assert len(regbench_dataset("data/items.jsonl")) > 0


class TestTaskFilterArguments:
    """Inspect hands a -T value through as a string or a list of strings."""

    def test_single_value_string(self):
        from regbench.task import _as_list

        assert _as_list("base") == ["base"]

    def test_comma_separated_string(self):
        from regbench.task import _as_list

        assert _as_list("base,renumber") == ["base", "renumber"]

    def test_list_from_inspect(self):
        from regbench.task import _as_list

        assert _as_list(["base", "renumber"]) == ["base", "renumber"]

    def test_none_and_empty(self):
        from regbench.task import _as_list

        assert _as_list(None) is None
        assert _as_list("") is None

    def test_task_accepts_a_list_of_variants(self):
        from regbench.task import regbench

        built = regbench(variants=["base", "renumber"])
        assert {sample.metadata["variant"] for sample in built.dataset} == {"base", "renumber"}


def test_family_filter():
    dataset = regbench_dataset(families=["i2c-addr"])
    assert len(dataset) == len(VARIANTS)
    assert all(s.metadata["family"] == "i2c-addr" for s in dataset)


def test_family_filter_accepts_several():
    dataset = regbench_dataset(families=["i2c-addr", "spi-mode"])
    assert {s.metadata["family"] for s in dataset} == {"i2c-addr", "spi-mode"}
