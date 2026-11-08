"""Unit tests for the Bank class."""

from __future__ import annotations

import os
import tempfile
import unittest

from bank_simulator.bank import Bank
from bank_simulator.exceptions import (
    AccountNotFoundError,
    InsufficientFundsError,
    InvalidPinError,
)
from bank_simulator.models.account import Account
from bank_simulator.models.current import CurrentAccount
from bank_simulator.models.savings import SavingsAccount


class TestBank(unittest.TestCase):
    """Test suite for :class:`Bank`."""

    def setUp(self) -> None:
        """Create a fresh Bank with a couple of accounts for each test."""
        Account._next_id = 1000
        self.bank = Bank("Test Bank")
        self.savings = SavingsAccount("Alice", 2000.0, "1111")
        self.current = CurrentAccount("Bob", 3000.0, "2222")
        self.bank.add_account(self.savings)
        self.bank.add_account(self.current)

    # ------------------------------------------------------------------
    # Adding / retrieving accounts
    # ------------------------------------------------------------------

    def test_add_and_get_account(self) -> None:
        """Added account is retrievable by its ID."""
        acc = self.bank.get_account(self.savings.account_id)
        self.assertEqual(acc.owner, "Alice")

    def test_get_nonexistent_raises(self) -> None:
        """Requesting a missing ID raises *AccountNotFoundError*."""
        with self.assertRaises(AccountNotFoundError):
            self.bank.get_account("ACC9999")

    # ------------------------------------------------------------------
    # Searching
    # ------------------------------------------------------------------

    def test_search_by_owner(self) -> None:
        """Partial, case-insensitive name match returns accounts."""
        results = self.bank.search_by_owner("ali")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].owner, "Alice")

    def test_search_no_results(self) -> None:
        """Non-matching search returns an empty list."""
        results = self.bank.search_by_owner("Charlie")
        self.assertEqual(results, [])

    # ------------------------------------------------------------------
    # Deleting
    # ------------------------------------------------------------------

    def test_delete_account(self) -> None:
        """Deleted account is no longer retrievable."""
        aid = self.savings.account_id
        self.bank.delete_account(aid)
        with self.assertRaises(AccountNotFoundError):
            self.bank.get_account(aid)

    def test_delete_nonexistent_raises(self) -> None:
        """Deleting a missing account raises *AccountNotFoundError*."""
        with self.assertRaises(AccountNotFoundError):
            self.bank.delete_account("ACC9999")

    # ------------------------------------------------------------------
    # Transfers
    # ------------------------------------------------------------------

    def test_transfer(self) -> None:
        """Transfer debits the sender and credits the receiver."""
        self.bank.transfer(
            self.savings.account_id,
            self.current.account_id,
            500.0,
            "1111",
        )
        self.assertAlmostEqual(self.savings.balance, 1500.0)
        self.assertAlmostEqual(self.current.balance, 3500.0)

    def test_transfer_wrong_pin_raises(self) -> None:
        """Transfer with wrong sender PIN raises *InvalidPinError*."""
        with self.assertRaises(InvalidPinError):
            self.bank.transfer(
                self.savings.account_id,
                self.current.account_id,
                500.0,
                "0000",
            )

    def test_transfer_insufficient_funds_raises(self) -> None:
        """Transfer exceeding balance raises *InsufficientFundsError*."""
        with self.assertRaises(InsufficientFundsError):
            self.bank.transfer(
                self.savings.account_id,
                self.current.account_id,
                100_000.0,
                "1111",
            )

    # ------------------------------------------------------------------
    # Interest
    # ------------------------------------------------------------------

    def test_apply_interest_to_all(self) -> None:
        """apply_interest_to_all returns a dict mapping IDs to amounts."""
        result = self.bank.apply_interest_to_all()
        self.assertIsInstance(result, dict)
        # SavingsAccount at 4 %: 2000 * 0.04 = 80
        self.assertAlmostEqual(result[self.savings.account_id], 80.0)
        # CurrentAccount at 0 %: interest = 0
        self.assertAlmostEqual(result[self.current.account_id], 0.0)

    # ------------------------------------------------------------------
    # Aggregate helpers
    # ------------------------------------------------------------------

    def test_total_bank_balance(self) -> None:
        """Total balance is the sum of all accounts."""
        expected = self.savings.balance + self.current.balance
        self.assertAlmostEqual(self.bank.total_bank_balance(), expected)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def test_save_and_load(self) -> None:
        """Save to a temp file, load into a new Bank, verify accounts."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp:
            tmp_path = tmp.name

        try:
            self.bank.data_file = tmp_path
            self.bank.save_to_file()

            new_bank = Bank("Loaded Bank", data_file=tmp_path)
            new_bank.load_from_file()

            self.assertEqual(len(new_bank.accounts), 2)
            loaded = new_bank.get_account(self.savings.account_id)
            self.assertEqual(loaded.owner, "Alice")
            self.assertAlmostEqual(loaded.balance, self.savings.balance)
        finally:
            os.unlink(tmp_path)

    def test_export_statement(self) -> None:
        """export_statement creates a file with correct content."""
        self.savings.deposit(100.0)
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = self.bank.export_statement(
                self.savings.account_id, directory=tmpdir
            )
            self.assertTrue(os.path.isfile(filepath))
            with open(filepath, "r", encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("Alice", content)
            self.assertIn(self.savings.account_id, content)

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def test_get_dashboard(self) -> None:
        """get_dashboard returns a dict with summary keys."""
        dash = self.bank.get_dashboard()
        self.assertIsInstance(dash, dict)
        self.assertIn("total_accounts", dash)
        self.assertIn("total_balance", dash)
        self.assertEqual(dash["total_accounts"], 2)
        self.assertAlmostEqual(
            dash["total_balance"],
            self.savings.balance + self.current.balance,
        )

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def test_str_representation(self) -> None:
        """__str__ mentions bank name and account count."""
        text = str(self.bank)
        self.assertIn("Test Bank", text)
        self.assertIn("2", text)


if __name__ == "__main__":
    unittest.main()
