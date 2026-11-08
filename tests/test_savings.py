"""Unit tests for the SavingsAccount class."""

from __future__ import annotations

import unittest

from bank_simulator.exceptions import InsufficientFundsError
from bank_simulator.models.account import Account
from bank_simulator.models.savings import SavingsAccount


class TestSavingsAccount(unittest.TestCase):
    """Test suite for :class:`SavingsAccount`."""

    def setUp(self) -> None:
        """Reset the auto-increment counter before every test."""
        Account._next_id = 1000

    # ------------------------------------------------------------------
    # Class attributes
    # ------------------------------------------------------------------

    def test_interest_rate(self) -> None:
        """SavingsAccount should have a 4 % interest rate."""
        self.assertAlmostEqual(SavingsAccount.interest_rate, 0.04)

    # ------------------------------------------------------------------
    # Withdrawal constraints
    # ------------------------------------------------------------------

    def test_withdraw_respects_min_balance(self) -> None:
        """Cannot withdraw below the minimum balance of ₹500."""
        acc = SavingsAccount("Alice", 1000.0, "1234")
        with self.assertRaises(InsufficientFundsError):
            acc.withdraw(600.0)  # would leave 400 < 500

    def test_withdraw_at_min_balance_raises(self) -> None:
        """Withdrawing any amount when balance is exactly min_balance raises."""
        acc = SavingsAccount("Alice", 500.0, "1234")
        with self.assertRaises(InsufficientFundsError):
            acc.withdraw(1.0)

    def test_withdraw_valid(self) -> None:
        """Withdrawal that leaves the balance above min_balance succeeds."""
        acc = SavingsAccount("Alice", 2000.0, "1234")
        acc.withdraw(500.0)
        self.assertAlmostEqual(acc.balance, 1500.0)

    # ------------------------------------------------------------------
    # Interest
    # ------------------------------------------------------------------

    def test_apply_interest(self) -> None:
        """₹1000 × 0.04 = ₹40 interest added to balance."""
        acc = SavingsAccount("Alice", 1000.0, "1234")
        interest = acc.apply_interest()
        self.assertAlmostEqual(interest, 40.0)
        self.assertAlmostEqual(acc.balance, 1040.0)

    # ------------------------------------------------------------------
    # Inherited behaviour
    # ------------------------------------------------------------------

    def test_deposit(self) -> None:
        """Deposit behaviour is inherited from Account and works."""
        acc = SavingsAccount("Alice", 500.0, "1234")
        acc.deposit(250.0)
        self.assertAlmostEqual(acc.balance, 750.0)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def test_to_dict_includes_min_balance(self) -> None:
        """to_dict output should contain the min_balance field."""
        acc = SavingsAccount("Alice", 1000.0, "1234")
        data = acc.to_dict()
        self.assertIn("min_balance", data)
        self.assertEqual(data["min_balance"], 500)


if __name__ == "__main__":
    unittest.main()
