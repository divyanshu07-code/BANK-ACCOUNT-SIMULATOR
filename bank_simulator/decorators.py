"""Decorator utilities for the Bank Account Simulator."""

from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable

from .exceptions import InsufficientFundsError, InvalidAmountError

logger = logging.getLogger(__name__)


def log_transaction(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that logs deposit / withdrawal outcomes via the logging module.

    On success the decorator logs the function name, amount, account ID and
    the resulting balance at INFO level.  On failure it logs the error at
    WARNING level and re-raises the exception so callers can handle it.
    """

    @wraps(func)
    def wrapper(self: Any, amount: float, *args: Any, **kwargs: Any) -> Any:
        try:
            result = func(self, amount, *args, **kwargs)
            logger.info(
                "[OK] %s ₹%.2f on %s | New balance: ₹%.2f",
                func.__name__.upper(),
                amount,
                self.account_id,
                self.balance,
            )
            return result
        except (InsufficientFundsError, InvalidAmountError) as exc:
            logger.warning(
                "[FAILED] %s on %s | Reason: %s",
                func.__name__.upper(),
                self.account_id,
                exc,
            )
            raise

    return wrapper
