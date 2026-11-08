"""Base Account model with SHA-256 PIN hashing and rich transaction history."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

from ..decorators import log_transaction
from ..exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    InvalidPinError,
)


class Account:
    """A general-purpose bank account.

    PINs are stored as SHA-256 hex-digests.  Transaction history entries are
    dictionaries containing ``type``, ``amount``, ``timestamp`` (ISO 8601) and
    ``balance_after``.
    """

    _next_id: int = 1000
    interest_rate: float = 0.0

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    def __init__(
        self,
        owner: str,
        balance: float = 0.0,
        pin: str = "0000",
        account_id: str | None = None,
    ) -> None:
        self.owner: str = owner
        self.balance: float = balance
        self._pin_hash: str = self._hash_pin(pin)

        if account_id:
            self.account_id: str = account_id
        else:
            self.account_id = f"ACC{Account._next_id}"
            Account._next_id += 1

        self.history: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # PIN handling
    # ------------------------------------------------------------------

    @staticmethod
    def _hash_pin(pin: str) -> str:
        """Return the SHA-256 hex digest of *pin*."""
        return hashlib.sha256(pin.encode()).hexdigest()

    def verify_pin(self, entered_pin: str) -> None:
        """Raise :class:`InvalidPinError` if *entered_pin* does not match."""
        if self._hash_pin(entered_pin) != self._pin_hash:
            raise InvalidPinError("Incorrect PIN")

    def change_pin(self, old_pin: str, new_pin: str) -> None:
        """Change the PIN after verifying the current one."""
        self.verify_pin(old_pin)
        self._pin_hash = self._hash_pin(new_pin)

    # ------------------------------------------------------------------
    # Transaction recording
    # ------------------------------------------------------------------

    def _record(self, txn_type: str, amount: float) -> None:
        """Append a transaction record to *self.history*."""
        self.history.append(
            {
                "type": txn_type,
                "amount": amount,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "balance_after": self.balance,
            }
        )

    # ------------------------------------------------------------------
    # Deposits & withdrawals
    # ------------------------------------------------------------------

    @log_transaction
    def deposit(self, amount: float) -> None:
        """Deposit *amount* into this account."""
        if not self.is_valid_amount(amount):
            raise InvalidAmountError("Deposit amount must be positive")
        self.balance += amount
        self._record("deposit", amount)

    @log_transaction
    def withdraw(self, amount: float) -> None:
        """Withdraw *amount* from this account."""
        if not self.is_valid_amount(amount):
            raise InvalidAmountError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise InsufficientFundsError(
                f"Balance ₹{self.balance:.2f} is less than ₹{amount:.2f}"
            )
        self.balance -= amount
        self._record("withdraw", amount)

    # ------------------------------------------------------------------
    # Interest
    # ------------------------------------------------------------------

    def apply_interest(self) -> float:
        """Apply interest and return the amount earned."""
        interest = self.balance * self.interest_rate
        if interest > 0:
            self.balance += interest
            self._record("interest", interest)
        return interest

    # ------------------------------------------------------------------
    # Statement / history
    # ------------------------------------------------------------------

    def get_statement(self, last_n: int = 0) -> list[dict[str, Any]]:
        """Return the last *last_n* transactions (0 means all)."""
        if last_n <= 0:
            return list(self.history)
        return list(self.history[-last_n:])

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialise the account to a JSON-friendly dictionary."""
        return {
            "type": self.__class__.__name__,
            "account_id": self.account_id,
            "owner": self.owner,
            "balance": self.balance,
            "pin_hash": self._pin_hash,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Account:
        """Reconstruct an :class:`Account` from a dictionary."""
        acc = cls.__new__(cls)
        acc.owner = data["owner"]
        acc.balance = data["balance"]
        acc._pin_hash = data["pin_hash"]
        acc.account_id = data["account_id"]
        acc.history = data.get("history", [])
        return acc

    # ------------------------------------------------------------------
    # Class / static methods
    # ------------------------------------------------------------------

    @classmethod
    def total_accounts_created(cls) -> int:
        """Return the total number of accounts ever created."""
        return cls._next_id - 1000

    @staticmethod
    def is_valid_amount(amount: float) -> bool:
        """Return ``True`` if *amount* is strictly positive."""
        return amount > 0

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"[{self.account_id}] {self.owner} ({self.__class__.__name__}) "
            f"| Balance: ₹{self.balance:.2f}"
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.owner}', {self.balance})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Account):
            return NotImplemented
        return self.account_id == other.account_id

    def __len__(self) -> int:
        return len(self.history)
