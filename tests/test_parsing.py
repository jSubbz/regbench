"""Tests for answer extraction and typed comparison."""

import pytest

from regbench.parsing import ParseError, compare, extract_answer, parse_integer
from regbench.units import UnitError, parse_quantity


class TestExtractAnswer:
    def test_extracts_value_after_marker(self):
        assert extract_answer("some working\nANSWER: 0x90") == "0x90"

    def test_is_case_insensitive(self):
        assert extract_answer("answer: 42") == "42"

    def test_tolerates_surrounding_whitespace_and_emphasis(self):
        assert extract_answer("  ANSWER:   **1.65 V**  ") == "1.65 V"

    def test_last_answer_wins(self):
        assert extract_answer("ANSWER: 1\nno wait\nANSWER: 2") == "2"

    def test_returns_none_when_absent(self):
        assert extract_answer("the answer is probably 42") is None

    def test_returns_none_for_empty_completion(self):
        assert extract_answer("") is None


class TestParseInteger:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("72", 72),
            ("0x48", 72),
            ("0X48", 72),
            ("48h", 72),
            ("0b1001000", 72),
            ("1001000b", 72),
            ("1_000", 1000),
            ("1,000", 1000),
            ("-5", -5),
            ("+5", 5),
        ],
    )
    def test_accepts_common_notations(self, text, expected):
        assert parse_integer(text) == expected

    def test_rejects_non_integer(self):
        with pytest.raises(ParseError):
            parse_integer("about seventy")

    @pytest.mark.parametrize(
        ("text", "radix", "expected"),
        [
            ("A6", 16, 166),
            ("a6", 16, 166),
            ("0xA6", 16, 166),
            ("10", 16, 16),
            ("10", 10, 10),
            ("0B", 16, 11),
            ("FFFFFFF0", 16, 0xFFFFFFF0),
            ("-198", 10, -198),
        ],
    )
    def test_unprefixed_digits_use_the_requested_radix(self, text, radix, expected):
        assert parse_integer(text, radix) == expected

    def test_explicit_prefix_overrides_the_radix(self):
        assert parse_integer("0b1010", 10) == 10

    def test_binary_suffix_is_not_applied_in_hexadecimal(self):
        # "1011b" is a valid hexadecimal literal; the binary-suffix reading
        # must not win when hexadecimal was requested.
        assert parse_integer("1011b", 16) == 0x1011B
        assert parse_integer("1011b", 10) == 11


class TestParseQuantity:
    def test_bare_number_takes_the_prompted_unit(self):
        assert parse_quantity("1.5", "ms").value == pytest.approx(0.0015)

    def test_explicit_unit_overrides_the_prompted_unit(self):
        assert parse_quantity("1500 us", "ms").value == pytest.approx(0.0015)

    def test_micro_sign_is_accepted(self):
        assert parse_quantity("1500 µs", "ms").value == pytest.approx(0.0015)

    def test_unit_words_are_accepted(self):
        assert parse_quantity("3.3 volts", "V").value == pytest.approx(3.3)

    def test_rejects_unknown_unit(self):
        with pytest.raises(UnitError):
            parse_quantity("5 furlongs", "V")

    def test_dimension_mismatch_is_not_close(self):
        volts = parse_quantity("1", "V")
        seconds = parse_quantity("1", "s")
        assert not volts.close_to(seconds, 0.1)


class TestCompare:
    def test_integer_across_bases(self):
        assert compare("ANSWER: 0x90", answer_type="integer", target="144").correct

    def test_bare_hex_is_accepted_when_hex_was_requested(self):
        # Regression: a response of "A6" to an item asking for hexadecimal is
        # correct and was previously rejected as an unparsable decimal.
        assert compare("ANSWER: A6", answer_type="integer", target="0xA6", radix=16).correct

    def test_bare_digits_are_read_in_the_requested_base(self):
        # "166" answering a hexadecimal item means 0x166, not decimal 166.
        assert not compare("ANSWER: 166", answer_type="integer", target="0xA6", radix=16).correct

    def test_integer_wrong_value(self):
        assert not compare("ANSWER: 0x91", answer_type="integer", target="144").correct

    def test_quantity_within_tolerance(self):
        verdict = compare(
            "ANSWER: 5.5556 ms", answer_type="quantity", target="5.5556", unit="ms", tolerance=0.005
        )
        assert verdict.correct

    def test_quantity_outside_tolerance(self):
        verdict = compare(
            "ANSWER: 6.2 ms", answer_type="quantity", target="5.5556", unit="ms", tolerance=0.005
        )
        assert not verdict.correct

    def test_quantity_accepts_equivalent_unit(self):
        verdict = compare(
            "ANSWER: 5555.6 us", answer_type="quantity", target="5.5556", unit="ms", tolerance=0.005
        )
        assert verdict.correct

    def test_quantity_rejects_wrong_dimension(self):
        verdict = compare(
            "ANSWER: 5.5556 V", answer_type="quantity", target="5.5556", unit="ms", tolerance=0.005
        )
        assert not verdict.correct

    def test_choice_is_case_insensitive(self):
        assert compare("ANSWER: task b", answer_type="choice", target="Task B").correct

    def test_choice_accepts_alias(self):
        verdict = compare(
            "ANSWER: send blocked",
            answer_type="choice",
            target="SEND-blocked",
            aliases=["SEND blocked", "send blocked"],
        )
        assert verdict.correct

    def test_missing_answer_line_is_incorrect_and_unanswered(self):
        verdict = compare("I think it is 144", answer_type="integer", target="144")
        assert not verdict.correct
        assert not verdict.answered

    def test_unparsable_answer_is_incorrect_but_answered(self):
        verdict = compare("ANSWER: seventy two", answer_type="integer", target="72")
        assert not verdict.correct
        assert verdict.answered

    def test_unknown_answer_type_raises(self):
        with pytest.raises(ValueError):
            compare("ANSWER: 1", answer_type="vibes", target="1")
