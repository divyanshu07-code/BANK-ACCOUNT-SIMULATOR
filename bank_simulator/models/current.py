"""Current account model with overdraft facility."""

from __future__ import annotations

from typing import Any

from ..decorators import log_transaction
from ..exceptions import InsufficientFundsError, InvalidAmountError
from .account import Account


class CurrentAccount(Account):
    """A current account with an overdraft limit and no interest."""

    interest_rate: float = 0.0

    def __init__(
        self,
        owner: str,
        balance: float = 0.0,
        pin: str = "0000",
        overdraft_limit: float = 1000.0,
        account_id: str | None = None,
    ) -> None:
        super().__init__(owner, balance, pin, account_id)
        self.overdraft_limit: float = overdraft_limit

    # ------------------------------------------------------------------
    # Withdraw override
    # ------------------------------------------------------------------

    @log_transaction
    def withdraw(self, amount: float) -> None:
        """Withdraw *amount*, allowing up to *overdraft_limit* below zero."""
        if not self.is_valid_amount(amount):
            raise InvalidAmountError("Withdrawal amount must be positive")
        if amount > self.balance + self.overdraft_limit:
            raise InsufficientFundsError(
                f"Exceeds overdraft limit of ₹{self.overdraft_limit:.2f}"
            )
        self.balance -= amount
        self._record("withdraw", amount)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialise including *overdraft_limit*."""
        data = super().to_dict()
        data["overdraft_limit"] = self.overdraft_limit
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CurrentAccount:
        """Reconstruct a :class:`CurrentAccount` from a dictionary."""
        acc = cls.__new__(cls)
        acc.owner = data["owner"]
        acc.balance = data["balance"]
        acc._pin_hash = data["pin_hash"]
        acc.account_id = data["account_id"]
        acc.history = data.get("history", [])
        acc.overdraft_limit = data.get("overdraft_limit", 1000.0)
        return acc
