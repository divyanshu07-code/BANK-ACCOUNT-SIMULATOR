"""Input helpers and colour utilities for the Bank Account Simulator CLI."""

from __future__ import annotations


# ------------------------------------------------------------------
# ANSI colour constants
# ------------------------------------------------------------------
GREEN: str = "\033[92m"
RED: str = "\033[91m"
YELLOW: str = "\033[93m"
CYAN: str = "\033[96m"
BOLD: str = "\033[1m"
RESET: str = "\033[0m"

_COLOR_MAP: dict[str, str] = {
    "green": GREEN,
    "red": RED,
    "yellow": YELLOW,
    "cyan": CYAN,
    "bold": BOLD,
    "reset": RESET,
}


# ------------------------------------------------------------------
# Colour helpers
# ------------------------------------------------------------------
def colorize(text: str, color: str) -> str:
    """Wrap *text* with an ANSI colour code and reset."""
    code = _COLOR_MAP.get(color.lower(), color)
    return f"{code}{text}{RESET}"


def is_valid_amount(amount: float) -> bool:
    """Return True if *amount* is strictly positive."""
    return amount > 0



def print_success(msg: str) -> None:
    """Print a green success message."""
    print(colorize(f"  ✔ {msg}", GREEN))


def print_error(msg: str) -> None:
    """Print a red error message."""
    print(colorize(f"  ✘ {msg}", RED))


def print_info(msg: str) -> None:
    """Print a cyan informational message."""
    print(colorize(f"  ℹ {msg}", CYAN))


def print_warning(msg: str) -> None:
    """Print a yellow warning message."""
    print(colorize(f"  ⚠ {msg}", YELLOW))


# ------------------------------------------------------------------
# Formatting
# ------------------------------------------------------------------
def format_currency(amount: float) -> str:
    """Return *amount* formatted as an Indian Rupee string."""
    return f"₹{amount:,.2f}"


def print_header(title: str) -> None:
    """Print a decorative box header around *title*."""
    width = max(len(title) + 4, 50)
    border = "═" * width
    print(colorize(f"\n╔{border}╗", CYAN))
    print(colorize(f"║  {title:<{width - 2}}║", CYAN))
    print(colorize(f"╚{border}╝", CYAN))


def print_dashboard(dashboard: dict) -> None:
    """Pretty-print the bank dashboard statistics dictionary."""
    print_header("BANK DASHBOARD")
    print(colorize(f"  Total Accounts  : {dashboard.get('total_accounts', 0)}", BOLD))
    print(colorize(
        f"  Total Balance   : {format_currency(dashboard.get('total_balance', 0.0))}",
        BOLD,
    ))
    print(colorize(
        f"  Savings Accounts: {dashboard.get('savings_count', 0)}",
        GREEN,
    ))
    print(colorize(
        f"  Current Accounts: {dashboard.get('current_count', 0)}",
        YELLOW,
    ))
    print(colorize(
        f"  Other Accounts  : {dashboard.get('other_count', 0)}",
        CYAN,
    ))


# ------------------------------------------------------------------
# Input helpers
# ------------------------------------------------------------------
def read_float(prompt: str) -> float:
    """Repeatedly prompt the user until a non-negative float is entered."""
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print_warning("Amount cannot be negative.")
                continue
            return value
        except ValueError:
            print_error("Please enter a valid number.")


def read_account_type() -> str:
    """Ask the user to choose between savings (s) and current (c)."""
    while True:
        choice = input("Account type - (s)avings or (c)urrent? ").strip().lower()
        if choice in ("s", "c"):
            return choice
        print_warning("Please enter 's' for savings or 'c' for current.")


def read_pin(prompt: str = "Set a 4-digit PIN: ") -> str:
    """Prompt the user for a 4-digit PIN and validate its format."""
    while True:
        pin = input(prompt).strip()
        if pin.isdigit() and len(pin) == 4:
            return pin
        print_error("PIN must be exactly 4 digits.")
