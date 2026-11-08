"""Savings account model with minimum-balance constraint."""

from __future__ import annotations

from typing import Any

from ..decorators import log_transaction
from ..exceptions import InsufficientFundsError, InvalidAmountError
from .account import Account


class SavingsAccount(Account):
    """A savings account that earns interest and enforces a minimum balance."""

    interest_rate: float = 0.04

    def __init__(
        self,
        owner: str,
        balance: float = 0.0,
        pin: str = "0000",
        account_id: str | None = None,
    ) -> None:
        super().__init__(owner, balance, pin, account_id)
        self.min_balance: float = 500.0

    # ------------------------------------------------------------------
    # Withdraw override
    # ------------------------------------------------------------------

    @log_transaction
    def withdraw(self, amount: float) -> None:
        """Withdraw *amount*, ensuring the balance never drops below *min_balance*."""
        if not self.is_valid_amount(amount):
            raise InvalidAmountError("Withdrawal amount must be positive")
        if self.balance - amount < self.min_balance:
            raise InsufficientFundsError(
                f"Cannot go below minimum balance of ₹{self.min_balance:.2f}"
            )
        self.balance -= amount
        self._record("withdraw", amount)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialise including *min_balance*."""
        data = super().to_dict()
        data["min_balance"] = self.min_balance
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SavingsAccount:
        """Reconstruct a :class:`SavingsAccount` from a dictionary."""
        acc = cls.__new__(cls)
        acc.owner = data["owner"]
        acc.balance = data["balance"]
        acc._pin_hash = data["pin_hash"]
        acc.account_id = data["account_id"]
        acc.history = data.get("history", [])
        acc.min_balance = data.get("min_balance", 500.0)
        return acc
