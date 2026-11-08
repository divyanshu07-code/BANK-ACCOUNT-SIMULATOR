"""Custom exception classes for the Bank Account Simulator."""


class InsufficientFundsError(Exception):
    """Raised when a withdrawal or transfer exceeds the available balance."""


class InvalidAmountError(Exception):
    """Raised when an invalid (non-positive) monetary amount is provided."""


class AccountNotFoundError(Exception):
    """Raised when an operation references an account ID that does not exist."""


class InvalidPinError(Exception):
    """Raised when the entered PIN does not match the stored PIN hash."""


class DuplicateAccountError(Exception):
    """Raised when attempting to add an account whose ID already exists."""
