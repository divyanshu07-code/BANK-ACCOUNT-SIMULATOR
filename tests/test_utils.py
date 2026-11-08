"""Unit tests for utility functions."""

from __future__ import annotations

import unittest

from bank_simulator.utils import colorize, format_currency, is_valid_amount


class TestColorize(unittest.TestCase):
    """Tests for :func:`colorize`."""

    def test_colorize(self) -> None:
        """Output should wrap text with ANSI escape codes."""
        result = colorize("hello", "green")
        # Must start with ESC[ and end with the reset code
        self.assertTrue(result.startswith("\033["))
        self.assertTrue(result.endswith("\033[0m"))
        self.assertIn("hello", result)


class TestFormatCurrency(unittest.TestCase):
    """Tests for :func:`format_currency`."""

    def test_format_currency(self) -> None:
        """Should format as ₹X,XXX.XX or ₹X.XX."""
        result = format_currency(1234.5)
        self.assertIn("₹", result)
        # The numeric portion should contain the value
        self.assertIn("1234", result.replace(",", ""))


class TestIsValidAmount(unittest.TestCase):
    """Tests for :func:`is_valid_amount`."""

    def test_is_valid_amount_positive(self) -> None:
        """Positive amount → True."""
        self.assertTrue(is_valid_amount(10.0))

    def test_is_valid_amount_zero(self) -> None:
        """Zero amount → False."""
        self.assertFalse(is_valid_amount(0.0))

    def test_is_valid_amount_negative(self) -> None:
        """Negative amount → False."""
        self.assertFalse(is_valid_amount(-5.0))


if __name__ == "__main__":
    unittest.main()
