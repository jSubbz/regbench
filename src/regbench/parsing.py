"""Extraction and normalisation of model answers.

Items instruct the model to end its response with a line of the form
``ANSWER: <value>``. Everything before that line is treated as working and is
ignored by the scorer. Three answer types are supported, each with its own
notion of equality:

``integer``
    Register values, addresses and bit masks. Decimal, hexadecimal and binary
    notations are accepted and compared by numeric value, so ``0x48``, ``72``
    and ``0b1001000`` are the same answer.

``quantity``
    Physical quantities, compared within a relative tolerance after conversion
    to a base SI unit. See :mod:`regbench.units`.

``choice``
    A selection from a fixed set of options, compared after case folding and
    whitespace collapsing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .units import Quantity, UnitError, parse_quantity

ANSWER_PREFIX = "ANSWER:"

_ANSWER_RE = re.compile(
    r"^[^\S\n]*answer[^\S\n]*:[^\S\n]*(.+?)[^\S\n]*$", re.IGNORECASE | re.MULTILINE
)

# Markdown emphasis and trailing punctuation that models commonly append.
_STRIP_CHARS = " \t*_`.,;"


class ParseError(ValueError):
    """Raised when an extracted answer cannot be interpreted as its declared type."""


@dataclass(frozen=True)
class Verdict:
    """The outcome of comparing one model response against one answer key."""

    correct: bool
    extracted: str | None
    reason: str

    @property
    def answered(self) -> bool:
        """Report whether an ``ANSWER:`` line was found at all."""
        return self.extracted is not None


def extract_answer(completion: str) -> str | None:
    """Return the value on the last ``ANSWER:`` line, or None if there is none.

    The last match wins so that a model which restates and then corrects itself
    is scored on its final answer.
    """
    matches = _ANSWER_RE.findall(completion or "")
    if not matches:
        return None
    return matches[-1].strip(_STRIP_CHARS).strip()


def parse_integer(text: str, radix: int = 10) -> int:
    """Parse an integer, interpreting unprefixed digits in ``radix``.

    An explicit notation always wins: ``0x``/``0b`` prefixes and an ``h`` suffix
    are honoured whatever ``radix`` says. Digits with no notation are read in
    ``radix``, which is the base the item's question asked for. Without that,
    a response of ``A6`` to a question requesting hexadecimal would be rejected
    even though it is correct, and the scorer would mark down a right answer.

    Args:
        text: The extracted answer.
        radix: Base for unprefixed digits. 16 for items requesting hexadecimal.

    Raises:
        ParseError: if the text is not a single integer literal in that base.
    """
    token = text.strip().replace("_", "").replace(" ", "")
    token = token.removeprefix("+")
    negative = token.startswith("-")
    if negative:
        token = token[1:]

    try:
        if token.lower().startswith("0x"):
            value = int(token, 16)
        elif token.lower().startswith("0b") and token[2:] and set(token[2:]) <= {"0", "1"}:
            # "0B" alone is a hexadecimal digit pair, not an empty binary literal.
            value = int(token, 2)
        elif token.lower().endswith("h"):
            value = int(token[:-1], 16)
        elif (
            radix != 16
            and token.lower().endswith("b")
            and set(token[:-1]) <= {"0", "1"}
            and token[:-1]
        ):
            # A trailing "b" means binary only when b is not a valid digit in
            # the requested base; in hexadecimal it is one.
            value = int(token[:-1], 2)
        else:
            value = int(token.replace(",", ""), radix)
    except ValueError as exc:
        raise ParseError(f"could not parse integer in base {radix}: {text!r}") from exc

    return -value if negative else value


def _normalise_choice(text: str) -> str:
    """Collapse whitespace and case so that choice answers compare loosely."""
    return re.sub(r"\s+", " ", text).strip(_STRIP_CHARS).strip().casefold()


def compare(
    completion: str,
    *,
    answer_type: str,
    target: str,
    unit: str | None = None,
    tolerance: float = 0.0,
    radix: int = 10,
    aliases: list[str] | None = None,
) -> Verdict:
    """Compare a model completion against an answer key.

    Args:
        completion: The full model response.
        answer_type: One of ``integer``, ``quantity`` or ``choice``.
        target: The correct answer, as written in the dataset.
        unit: Canonical unit for ``quantity`` items; the unit the prompt asks for.
        tolerance: Relative tolerance for ``quantity`` items.
        radix: Base for unprefixed digits on ``integer`` items.
        aliases: Additional accepted spellings for ``choice`` items.

    Returns:
        A :class:`Verdict` recording correctness, the extracted answer and a
        short reason suitable for display in an eval log.
    """
    extracted = extract_answer(completion)
    if extracted is None:
        return Verdict(False, None, "no ANSWER: line found in response")

    if answer_type == "integer":
        try:
            got = parse_integer(extracted, radix)
        except ParseError as exc:
            return Verdict(False, extracted, str(exc))
        want = parse_integer(target, radix)
        return Verdict(got == want, extracted, f"parsed {got}, expected {want}")

    if answer_type == "quantity":
        if unit is None:
            raise ValueError("quantity items require a unit")
        try:
            got_q = parse_quantity(extracted, unit)
        except UnitError as exc:
            return Verdict(False, extracted, str(exc))
        want_q: Quantity = parse_quantity(target, unit)
        ok = got_q.close_to(want_q, tolerance)
        return Verdict(
            ok,
            extracted,
            f"parsed {got_q.value:g}, expected {want_q.value:g} (rel tol {tolerance:g})",
        )

    if answer_type == "choice":
        accepted = {_normalise_choice(target)} | {_normalise_choice(a) for a in (aliases or [])}
        got_c = _normalise_choice(extracted)
        return Verdict(
            got_c in accepted, extracted, f"parsed {got_c!r}, expected one of {sorted(accepted)}"
        )

    raise ValueError(f"unknown answer_type: {answer_type!r}")
