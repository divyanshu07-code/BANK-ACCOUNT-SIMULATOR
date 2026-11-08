"""Unit tests for the base Account class."""

from __future__ import annotations

import hashlib
import re
import unittest
from datetime import datetime

from bank_simulator.exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    InvalidPinError,
)
from bank_simulator.models.account import Account


class TestAccount(unittest.TestCase):
    """Test suite for :class:`Account`."""

    # ------------------------------------------------------------------
    # Fixtures
    # ------------------------------------------------------------------

    def setUp(self) -> None:
        """Reset the auto-increment counter before every test."""
        Account._next_id = 1000

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def test_create_account(self) -> None:
        """Owner, balance and account_id format are set correctly."""
        acc = Account("Alice", 1000.0, "1234")
        self.assertEqual(acc.owner, "Alice")
        self.assertEqual(acc.balance, 1000.0)
        self.assertRegex(acc.account_id, r"^ACC\d+$")

    def test_auto_increment_id(self) -> None:
        """Two accounts created in sequence get different IDs."""
        a1 = Account("Alice", 0.0, "1234")
        a2 = Account("Bob", 0.0, "5678")
        self.assertNotEqual(a1.account_id, a2.account_id)

    # ------------------------------------------------------------------
    # Deposits
    # ------------------------------------------------------------------

    def test_deposit_valid(self) -> None:
        """A valid deposit increases the balance."""
        acc = Account("Alice", 500.0, "1234")
        acc.deposit(500.0)
        self.assertAlmostEqual(acc.balance, 1000.0)

    def test_deposit_zero_raises(self) -> None:
        """Depositing zero raises *InvalidAmountError*."""
        acc = Account("Alice", 500.0, "1234")
        with self.assertRaises(InvalidAmountError):
            acc.deposit(0)

    def test_deposit_negative_raises(self) -> None:
        """Depositing a negative amount raises *InvalidAmountError*."""
        acc = Account("Alice", 500.0, "1234")
        with self.assertRaises(InvalidAmountError):
            acc.deposit(-100)

    # ------------------------------------------------------------------
    # Withdrawals
    # ------------------------------------------------------------------

    def test_withdraw_valid(self) -> None:
        """A valid withdrawal decreases the balance."""
        acc = Account("Alice", 1000.0, "1234")
        acc.withdraw(300.0)
        self.assertAlmostEqual(acc.balance, 700.0)

    def test_withdraw_insufficient_raises(self) -> None:
        """Withdrawing more than the balance raises *InsufficientFundsError*."""
        acc = Account("Alice", 100.0, "1234")
        with self.assertRaises(InsufficientFundsError):
            acc.withdraw(200.0)

    def test_withdraw_negative_raises(self) -> None:
        """Withdrawing a negative amount raises *InvalidAmountError*."""
        acc = Account("Alice", 1000.0, "1234")
        with self.assertRaises(InvalidAmountError):
            acc.withdraw(-50.0)

    # ------------------------------------------------------------------
    # PIN verification
    # ------------------------------------------------------------------

    def test_verify_pin_correct(self) -> None:
        """Correct PIN does not raise."""
        acc = Account("Alice", 0.0, "1234")
        try:
            acc.verify_pin("1234")
        except InvalidPinError:
            self.fail("verify_pin raised InvalidPinError on a correct PIN")

    def test_verify_pin_wrong(self) -> None:
        """Wrong PIN raises *InvalidPinError*."""
        acc = Account("Alice", 0.0, "1234")
        with self.assertRaises(InvalidPinError):
            acc.verify_pin("0000")

    def test_change_pin(self) -> None:
        """After changing the PIN the old one fails and the new one works."""
        acc = Account("Alice", 0.0, "1234")
        acc.change_pin("1234", "5678")

        with self.assertRaises(InvalidPinError):
            acc.verify_pin("1234")

        # New PIN should work without raising
        try:
            acc.verify_pin("5678")
        except InvalidPinError:
            self.fail("verify_pin raised InvalidPinError after PIN change")

    # ------------------------------------------------------------------
    # Interest
    # ------------------------------------------------------------------

    def test_apply_interest(self) -> None:
        """Base Account has 0 % interest; applying it should yield 0."""
        acc = Account("Alice", 1000.0, "1234")
        interest = acc.apply_interest()
        self.assertAlmostEqual(interest, 0.0)
        self.assertAlmostEqual(acc.balance, 1000.0)

    # ------------------------------------------------------------------
    # Transaction history
    # ------------------------------------------------------------------

    def test_transaction_history(self) -> None:
        """Deposit then withdraw should produce 2 history entries."""
        acc = Account("Alice", 1000.0, "1234")
        acc.deposit(500.0)
        acc.withdraw(200.0)
        self.assertEqual(len(acc.history), 2)

        types = [entry["type"] for entry in acc.history]
        self.assertIn("deposit", types)
        self.assertIn("withdraw", types)

    def test_history_has_timestamps(self) -> None:
        """Each history entry should contain an ISO-formatted timestamp."""
        acc = Account("Alice", 1000.0, "1234")
        acc.deposit(100.0)
        entry = acc.history[0]
        self.assertIn("timestamp", entry)
        # Should parse without error
        datetime.fromisoformat(entry["timestamp"])

    # ------------------------------------------------------------------
    # Serialisation round-trip
    # ------------------------------------------------------------------

    def test_to_dict_and_from_dict(self) -> None:
        """Round-trip through to_dict / from_dict preserves data."""
        acc = Account("Alice", 1500.0, "1234")
        acc.deposit(500.0)
        data = acc.to_dict()

        restored = Account.from_dict(data)
        self.assertEqual(restored.owner, acc.owner)
        self.assertAlmostEqual(restored.balance, acc.balance)
        self.assertEqual(restored.account_id, acc.account_id)
        self.assertEqual(len(restored.history), len(acc.history))

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def test_str_representation(self) -> None:
        """__str__ should mention the owner and balance."""
        acc = Account("Alice", 750.0, "1234")
        text = str(acc)
        self.assertIn("Alice", text)
        self.assertIn("750", text)

    def test_len_returns_history_count(self) -> None:
        """len(account) returns the number of history entries."""
        acc = Account("Alice", 1000.0, "1234")
        self.assertEqual(len(acc), 0)
        acc.deposit(100.0)
        self.assertEqual(len(acc), 1)

    def test_eq_same_id(self) -> None:
        """Accounts with the same ID are equal."""
        a = Account("Alice", 100.0, "1234", account_id="ACC9999")
        b = Account("Bob", 200.0, "5678", account_id="ACC9999")
        self.assertEqual(a, b)

    def test_eq_different_id(self) -> None:
        """Accounts with different IDs are not equal."""
        a = Account("Alice", 100.0, "1234")
        b = Account("Bob", 100.0, "1234")
        self.assertNotEqual(a, b)

    # ------------------------------------------------------------------
    # Class-level helpers
    # ------------------------------------------------------------------

    def test_total_accounts_created(self) -> None:
        """total_accounts_created tracks auto-generated accounts."""
        before = Account.total_accounts_created()
        Account("X", 0.0, "0000")
        Account("Y", 0.0, "0000")
        after = Account.total_accounts_created()
        self.assertEqual(after - before, 2)

    def test_is_valid_amount(self) -> None:
        """Positive amounts are valid; zero and negative are not."""
        self.assertTrue(Account.is_valid_amount(1.0))
        self.assertFalse(Account.is_valid_amount(0.0))
        self.assertFalse(Account.is_valid_amount(-5.0))


if __name__ == "__main__":
    unittest.main()
