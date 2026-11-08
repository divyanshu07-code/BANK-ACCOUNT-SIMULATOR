"""Unit tests for the CurrentAccount class."""

from __future__ import annotations

import unittest

from bank_simulator.exceptions import InsufficientFundsError
from bank_simulator.models.account import Account
from bank_simulator.models.current import CurrentAccount


class TestCurrentAccount(unittest.TestCase):
    """Test suite for :class:`CurrentAccount`."""

    def setUp(self) -> None:
        """Reset the auto-increment counter before every test."""
        Account._next_id = 1000

    # ------------------------------------------------------------------
    # Class attributes
    # ------------------------------------------------------------------

    def test_interest_rate(self) -> None:
        """CurrentAccount should have 0 % interest."""
        self.assertAlmostEqual(CurrentAccount.interest_rate, 0.0)

    # ------------------------------------------------------------------
    # Overdraft behaviour
    # ------------------------------------------------------------------

    def test_overdraft_allowed(self) -> None:
        """Can go negative up to the overdraft limit."""
        acc = CurrentAccount("Alice", 500.0, "1234")
        acc.withdraw(1000.0)  # 500 balance + 1000 limit → allowed
        self.assertAlmostEqual(acc.balance, -500.0)

    def test_overdraft_exceeded_raises(self) -> None:
        """Exceeding the overdraft limit raises *InsufficientFundsError*."""
        acc = CurrentAccount("Alice", 500.0, "1234")
        with self.assertRaises(InsufficientFundsError):
            acc.withdraw(2000.0)  # 500 + 1000 = 1500 < 2000

    def test_default_overdraft_limit(self) -> None:
        """Default overdraft limit should be ₹1000."""
        acc = CurrentAccount("Alice", 0.0, "1234")
        self.assertAlmostEqual(acc.overdraft_limit, 1000.0)

    def test_custom_overdraft_limit(self) -> None:
        """Custom overdraft limit is respected."""
        acc = CurrentAccount("Alice", 0.0, "1234", overdraft_limit=5000.0)
        self.assertAlmostEqual(acc.overdraft_limit, 5000.0)

    # ------------------------------------------------------------------
    # Normal withdrawal
    # ------------------------------------------------------------------

    def test_withdraw_valid(self) -> None:
        """A standard withdrawal within available balance works."""
        acc = CurrentAccount("Alice", 2000.0, "1234")
        acc.withdraw(800.0)
        self.assertAlmostEqual(acc.balance, 1200.0)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def test_to_dict_includes_overdraft_limit(self) -> None:
        """to_dict output should contain the overdraft_limit field."""
        acc = CurrentAccount("Alice", 0.0, "1234", overdraft_limit=2500.0)
        data = acc.to_dict()
        self.assertIn("overdraft_limit", data)
        self.assertAlmostEqual(data["overdraft_limit"], 2500.0)


if __name__ == "__main__":
    unittest.main()
