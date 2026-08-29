"""Unit parsing and normalisation for numeric benchmark answers.

Answers to computational items are physical quantities, so a string comparison
against the answer key would reject correct responses that differ only in unit
or notation. This module reduces a quantity to a canonical (dimension, value)
pair so that "1.5 ms", "1500 us" and "0.0015 s" compare equal.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Multiplier for each supported SI prefix. "u" and the micro sign are treated as
# equivalent. "K" is accepted alongside "k" because datasheets are inconsistent.
_PREFIXES: dict[str, float] = {
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "µ": 1e-6,
    "μ": 1e-6,
    "m": 1e-3,
    "": 1.0,
    "k": 1e3,
    "K": 1e3,
    "M": 1e6,
    "G": 1e9,
}

# Base unit symbol -> dimension name. Comparison is only meaningful between
# quantities of the same dimension.
_BASE_UNITS: dict[str, str] = {
    "V": "voltage",
    "A": "current",
    "Hz": "frequency",
    "s": "time",
    "ohm": "resistance",
    "W": "power",
    "B": "data",
    "bit": "data_bits",
    "%": "percent",
}

# Spellings that map onto a base unit before prefix handling.
_UNIT_ALIASES: dict[str, str] = {
    "volt": "V",
    "volts": "V",
    "amp": "A",
    "amps": "A",
    "ampere": "A",
    "amperes": "A",
    "hertz": "Hz",
    "sec": "s",
    "secs": "s",
    "second": "s",
    "seconds": "s",
    "Ω": "ohm",
    "Ω": "ohm",
    "ohms": "ohm",
    "watt": "W",
    "watts": "W",
    "byte": "B",
    "bytes": "B",
    "bits": "bit",
    "percent": "%",
}


class UnitError(ValueError):
    """Raised when a unit string cannot be resolved to a known dimension."""


@dataclass(frozen=True)
class Quantity:
    """A numeric value reduced to its base SI unit."""

    value: float
    dimension: str

    def close_to(self, other: Quantity, rel_tol: float) -> bool:
        """Report whether two quantities agree within a relative tolerance."""
        if self.dimension != other.dimension:
            return False
        if other.value == 0.0:
            return abs(self.value) <= rel_tol
        return abs(self.value - other.value) / abs(other.value) <= rel_tol


def parse_unit(unit: str) -> tuple[str, float]:
    """Resolve a unit string to its dimension and its multiplier to the base unit.

    Raises:
        UnitError: if the unit is not recognised.
    """
    unit = unit.strip()
    if not unit:
        raise UnitError("empty unit")

    lowered = unit.lower()
    if lowered in _UNIT_ALIASES:
        unit = _UNIT_ALIASES[lowered]
    if unit in _BASE_UNITS:
        return _BASE_UNITS[unit], 1.0

    # Try to peel a single prefix character off the front.
    prefix, remainder = unit[0], unit[1:]
    if remainder.lower() in _UNIT_ALIASES:
        remainder = _UNIT_ALIASES[remainder.lower()]
    if prefix in _PREFIXES and remainder in _BASE_UNITS:
        return _BASE_UNITS[remainder], _PREFIXES[prefix]

    raise UnitError(f"unrecognised unit: {unit!r}")


_NUMBER = r"[-+]?(?:\d[\d_,]*\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
_QUANTITY_RE = re.compile(rf"^\s*({_NUMBER})\s*([A-Za-z%µμΩΩ]*)\s*$")


def parse_quantity(text: str, default_unit: str) -> Quantity:
    """Parse a numeric answer, falling back to ``default_unit`` when none is given.

    A bare number is interpreted as being expressed in the unit the item asked
    for, which is the unit named in the prompt.

    Raises:
        UnitError: if the text is not a number, optionally followed by a unit.
    """
    match = _QUANTITY_RE.match(text)
    if match is None:
        raise UnitError(f"could not parse quantity: {text!r}")

    number_text, unit_text = match.group(1), match.group(2)
    number = float(number_text.replace(",", "").replace("_", ""))
    dimension, multiplier = parse_unit(unit_text or default_unit)
    return Quantity(number * multiplier, dimension)
