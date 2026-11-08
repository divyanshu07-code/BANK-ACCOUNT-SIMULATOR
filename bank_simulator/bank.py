"""Bank manager class — holds accounts, handles persistence and operations."""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from .exceptions import AccountNotFoundError
from .models.account import Account
from .models.current import CurrentAccount
from .models.savings import SavingsAccount

logger = logging.getLogger(__name__)

# Mapping from serialised type name to the concrete class
_ACCOUNT_TYPES: dict[str, type[Account]] = {
    "SavingsAccount": SavingsAccount,
    "CurrentAccount": CurrentAccount,
    "Account": Account,
}


class Bank:
    """Manages a collection of bank accounts with JSON file persistence."""

    def __init__(self, name: str, data_file: str = "bank_data.json") -> None:
        self.name: str = name
        self.data_file: str = data_file
        self.accounts: dict[str, Account] = {}

    # ------------------------------------------------------------------
    # Account management
    # ------------------------------------------------------------------

    def add_account(self, account: Account) -> None:
        """Register *account* in the bank."""
        self.accounts[account.account_id] = account
        logger.info("Account %s added for %s", account.account_id, account.owner)

    def get_account(self, account_id: str) -> Account:
        """Return the account with *account_id* or raise."""
        if account_id not in self.accounts:
            raise AccountNotFoundError(f"No account with ID {account_id}")
        return self.accounts[account_id]

    def search_by_owner(self, name: str) -> list[Account]:
        """Return accounts whose owner name contains *name* (case-insensitive)."""
        name = name.strip().lower()
        return [acc for acc in self.accounts.values() if name in acc.owner.lower()]

    def delete_account(self, account_id: str) -> None:
        """Remove the account with *account_id* from the bank."""
        acc = self.get_account(account_id)
        del self.accounts[account_id]
        logger.info("Account %s (%s) closed.", acc.account_id, acc.owner)

    # ------------------------------------------------------------------
    # Transfers
    # ------------------------------------------------------------------

    def transfer(
        self, from_id: str, to_id: str, amount: float, pin: str
    ) -> None:
        """Transfer *amount* from one account to another (PIN required)."""
        sender = self.get_account(from_id)
        receiver = self.get_account(to_id)
        sender.verify_pin(pin)
        sender.withdraw(amount)
        receiver.deposit(amount)
        # Record transfer-specific entries in history
        sender.history[-1]["type"] = "transfer_out"
        receiver.history[-1]["type"] = "transfer_in"
        logger.info(
            "[TRANSFER] ₹%.2f from %s to %s successful", amount, from_id, to_id
        )

    # ------------------------------------------------------------------
    # Interest
    # ------------------------------------------------------------------

    def apply_interest_to_all(self) -> dict[str, float]:
        """Apply interest to every account. Return {account_id: interest_earned}."""
        results: dict[str, float] = {}
        for acc in self.accounts.values():
            interest = acc.apply_interest()
            results[acc.account_id] = interest
            if interest > 0:
                logger.info(
                    "[INTEREST] %s earned ₹%.2f", acc.account_id, interest
                )
        return results

    # ------------------------------------------------------------------
    # Aggregate helpers
    # ------------------------------------------------------------------

    def total_bank_balance(self) -> float:
        """Return the sum of all account balances."""
        return sum(acc.balance for acc in self.accounts.values())

    def get_dashboard(self) -> dict[str, Any]:
        """Return a summary dictionary of bank statistics."""
        savings_count = sum(
            1 for acc in self.accounts.values() if isinstance(acc, SavingsAccount)
        )
        current_count = sum(
            1 for acc in self.accounts.values() if isinstance(acc, CurrentAccount)
        )
        other_count = len(self.accounts) - savings_count - current_count
        return {
            "total_accounts": len(self.accounts),
            "total_balance": self.total_bank_balance(),
            "savings_count": savings_count,
            "current_count": current_count,
            "other_count": other_count,
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_to_file(self) -> None:
        """Serialise all accounts to *self.data_file* as JSON."""
        data = [acc.to_dict() for acc in self.accounts.values()]
        with open(self.data_file, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        logger.info("Data saved to %s", self.data_file)

    def load_from_file(self) -> None:
        """Load accounts from *self.data_file*.  No-op if the file is absent."""
        if not os.path.exists(self.data_file):
            return
        with open(self.data_file, "r", encoding="utf-8") as fh:
            data: list[dict[str, Any]] = json.load(fh)

        max_num = 999
        for entry in data:
            acc_type_name = entry.get("type", "Account")
            cls = _ACCOUNT_TYPES.get(acc_type_name, Account)
            acc = cls.from_dict(entry)
            self.accounts[acc.account_id] = acc
            num = int(acc.account_id.replace("ACC", ""))
            max_num = max(max_num, num)
        Account._next_id = max_num + 1
        logger.info("Loaded %d account(s) from %s", len(self.accounts), self.data_file)

    # ------------------------------------------------------------------
    # Statement export
    # ------------------------------------------------------------------

    def export_statement(
        self,
        account_id: str,
        last_n: int = 0,
        directory: str = ".",
    ) -> str:
        """Generate a text statement file and return the file path.

        Parameters
        ----------
        account_id:
            The account to export.
        last_n:
            How many recent transactions to include (0 = all).
        directory:
            Directory in which to write the file (default: current dir).
        """
        acc = self.get_account(account_id)
        filename = os.path.join(directory, f"statement_{account_id}.txt")
        statement = acc.get_statement(last_n)

        with open(filename, "w", encoding="utf-8") as fh:
            fh.write(f"{'=' * 50}\n")
            fh.write(f"  Statement for {acc.owner} ({acc.account_id})\n")
            fh.write(f"{'=' * 50}\n")
            fh.write(f"  Account Type   : {acc.__class__.__name__}\n")
            fh.write(f"  Current Balance: ₹{acc.balance:,.2f}\n")
            fh.write(f"{'-' * 50}\n")
            if not statement:
                fh.write("  No transactions yet.\n")
            for txn in statement:
                ts = txn.get("timestamp", "N/A")
                txn_type = txn.get("type", "unknown").upper()
                amount = txn.get("amount", 0.0)
                bal_after = txn.get("balance_after", 0.0)
                fh.write(
                    f"  [{ts}] {txn_type:15s}  ₹{amount:>12,.2f}  "
                    f"Balance: ₹{bal_after:>12,.2f}\n"
                )
            fh.write(f"{'-' * 50}\n")

        logger.info("Statement exported to %s", filename)
        return filename

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"{self.name} | {len(self.accounts)} account(s) "
            f"| Total: ₹{self.total_bank_balance():,.2f}"
        )

