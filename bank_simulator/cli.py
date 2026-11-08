"""Interactive CLI for the Bank Account Simulator."""

from __future__ import annotations

import logging
import sys

from .bank import Bank
from .exceptions import (
    AccountNotFoundError,
    InsufficientFundsError,
    InvalidAmountError,
    InvalidPinError,
)
from .models.current import CurrentAccount
from .models.savings import SavingsAccount
from .utils import (
    BOLD,
    CYAN,
    GREEN,
    RED,
    RESET,
    YELLOW,
    colorize,
    format_currency,
    print_dashboard,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
    read_account_type,
    read_float,
    read_pin,
)

# Configure root logger so transaction decorator messages are visible
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)

BANK_NAME = "Divyanshu National Bank"


# ------------------------------------------------------------------
# Menu display
# ------------------------------------------------------------------
def show_menu() -> None:
    """Display the main menu with colourised options."""
    print_header(f"🏦  {BANK_NAME}  —  MENU")
    options = [
        (" 1", "Create new account"),
        (" 2", "Deposit money"),
        (" 3", "Withdraw money", "(PIN required)"),
        (" 4", "Transfer between accounts", "(PIN required)"),
        (" 5", "View one account"),
        (" 6", "View all accounts"),
        (" 7", "Search account by owner name"),
        (" 8", "Close (delete) an account"),
        (" 9", "Apply interest to all accounts"),
        ("10", "Export account statement to file"),
        ("11", "Change PIN"),
        ("12", "Dashboard — bank stats"),
        ("13", "Save data now"),
        ("14", "Exit (auto-saves)"),
    ]
    for parts in options:
        num = parts[0]
        desc = parts[1]
        tag = parts[2] if len(parts) > 2 else ""
        line = f"  {colorize(num, CYAN)}.  {desc}"
        if tag:
            line += f"  {colorize(tag, YELLOW)}"
        print(line)
    print(colorize("─" * 52, CYAN))


# ------------------------------------------------------------------
# Main loop
# ------------------------------------------------------------------
def main() -> None:
    """Entry point for the Bank Account Simulator CLI."""
    bank = Bank(BANK_NAME)
    bank.load_from_file()

    print()
    print_header(f"Welcome to {bank.name}")
    if bank.accounts:
        print_info(f"Loaded {len(bank.accounts)} existing account(s) from file.")

    while True:
        show_menu()
        choice = input(f"\n  {colorize('Enter your choice (1-14):', BOLD)} ").strip()

        # ---- 1. Create account -----------------------------------
        if choice == "1":
            owner = input("  Enter owner name: ").strip()
            if not owner:
                print_error("Owner name cannot be empty.")
                continue
            acc_type = read_account_type()
            opening = read_float("  Enter opening balance: ₹")
            pin = read_pin()
            if acc_type == "s":
                acc = SavingsAccount(owner, opening, pin)
            else:
                overdraft_input = input(
                    "  Overdraft limit (default 1000): ₹"
                ).strip()
                overdraft = float(overdraft_input) if overdraft_input else 1000.0
                acc = CurrentAccount(owner, opening, pin, overdraft_limit=overdraft)
            bank.add_account(acc)
            print_success(f"Account created: {acc}")

        # ---- 2. Deposit ------------------------------------------
        elif choice == "2":
            acc_id = input("  Enter account ID: ").strip().upper()
            try:
                acc = bank.get_account(acc_id)
                amount = read_float("  Enter deposit amount: ₹")
                acc.deposit(amount)
                print_success(
                    f"Deposited {format_currency(amount)} | "
                    f"New balance: {format_currency(acc.balance)}"
                )
            except (AccountNotFoundError, InvalidAmountError) as e:
                print_error(str(e))

        # ---- 3. Withdraw -----------------------------------------
        elif choice == "3":
            acc_id = input("  Enter account ID: ").strip().upper()
            try:
                acc = bank.get_account(acc_id)
                pin = input("  Enter PIN: ").strip()
                acc.verify_pin(pin)
                amount = read_float("  Enter withdrawal amount: ₹")
                acc.withdraw(amount)
                print_success(
                    f"Withdrew {format_currency(amount)} | "
                    f"New balance: {format_currency(acc.balance)}"
                )
            except (
                AccountNotFoundError,
                InsufficientFundsError,
                InvalidAmountError,
                InvalidPinError,
            ) as e:
                print_error(str(e))

        # ---- 4. Transfer -----------------------------------------
        elif choice == "4":
            from_id = input("  From account ID: ").strip().upper()
            to_id = input("  To account ID: ").strip().upper()
            try:
                pin = input("  Enter PIN for sender account: ").strip()
                amount = read_float("  Enter transfer amount: ₹")
                bank.transfer(from_id, to_id, amount, pin)
                print_success(
                    f"Transferred {format_currency(amount)} "
                    f"from {from_id} → {to_id}"
                )
            except (
                AccountNotFoundError,
                InsufficientFundsError,
                InvalidAmountError,
                InvalidPinError,
            ) as e:
                print_error(str(e))

        # ---- 5. View one account ---------------------------------
        elif choice == "5":
            acc_id = input("  Enter account ID: ").strip().upper()
            try:
                acc = bank.get_account(acc_id)
                print()
                print(f"  {colorize(str(acc), BOLD)}")
                print(f"  Transactions: {len(acc)}")
                if acc.history:
                    print(f"  {'─' * 46}")
                    for txn in acc.history:
                        ts = txn.get("timestamp", "N/A")[:19]
                        txn_type = txn.get("type", "?").upper()
                        amt = txn.get("amount", 0.0)
                        bal = txn.get("balance_after", 0.0)
                        colour = GREEN if txn_type in ("DEPOSIT", "INTEREST", "TRANSFER_IN") else RED
                        sign = "+" if txn_type in ("DEPOSIT", "INTEREST", "TRANSFER_IN") else "-"
                        print(
                            f"    {ts}  {colorize(txn_type:>14s, colour)}  "
                            f"{sign}₹{amt:>10,.2f}  → ₹{bal:>10,.2f}"
                        )
                    print(f"  {'─' * 46}")
            except AccountNotFoundError as e:
                print_error(str(e))

        # ---- 6. View all accounts --------------------------------
        elif choice == "6":
            if not bank.accounts:
                print_warning("No accounts yet.")
            else:
                print()
                for acc in bank.accounts.values():
                    print(f"  {acc}")
                print()
                print_info(str(bank))

        # ---- 7. Search by owner ----------------------------------
        elif choice == "7":
            name = input("  Enter owner name (or part): ").strip()
            results = bank.search_by_owner(name)
            if not results:
                print_warning("No matching accounts found.")
            else:
                for acc in results:
                    print(f"  {acc}")

        # ---- 8. Close account ------------------------------------
        elif choice == "8":
            acc_id = input("  Enter account ID to close: ").strip().upper()
            try:
                acc = bank.get_account(acc_id)
                pin = input("  Enter PIN to confirm closing: ").strip()
                acc.verify_pin(pin)
                confirm = input(
                    f"  Type {colorize('YES', RED)} to permanently close "
                    f"{acc_id}: "
                ).strip()
                if confirm == "YES":
                    bank.delete_account(acc_id)
                    print_success(f"Account {acc_id} ({acc.owner}) has been closed.")
                else:
                    print_warning("Cancelled.")
            except (AccountNotFoundError, InvalidPinError) as e:
                print_error(str(e))

        # ---- 9. Apply interest -----------------------------------
        elif choice == "9":
            results = bank.apply_interest_to_all()
            any_earned = False
            for aid, interest in results.items():
                if interest > 0:
                    print_success(
                        f"{aid} earned {format_currency(interest)} interest"
                    )
                    any_earned = True
            if not any_earned:
                print_info("No interest earned on any account.")

        # ---- 10. Export statement --------------------------------
        elif choice == "10":
            acc_id = input("  Enter account ID: ").strip().upper()
            try:
                filepath = bank.export_statement(acc_id)
                print_success(f"Statement exported to {filepath}")
            except AccountNotFoundError as e:
                print_error(str(e))

        # ---- 11. Change PIN --------------------------------------
        elif choice == "11":
            acc_id = input("  Enter account ID: ").strip().upper()
            try:
                acc = bank.get_account(acc_id)
                old_pin = input("  Enter current PIN: ").strip()
                new_pin = read_pin("  Set new 4-digit PIN: ")
                confirm_pin = read_pin("  Confirm new PIN: ")
                if new_pin != confirm_pin:
                    print_error("PINs do not match.")
                    continue
                acc.change_pin(old_pin, new_pin)
                print_success("PIN changed successfully.")
            except (AccountNotFoundError, InvalidPinError) as e:
                print_error(str(e))

        # ---- 12. Dashboard ---------------------------------------
        elif choice == "12":
            dash = bank.get_dashboard()
            print_dashboard(dash)

        # ---- 13. Save now ----------------------------------------
        elif choice == "13":
            bank.save_to_file()
            print_success(f"Data saved to {bank.data_file}")

        # ---- 14. Exit --------------------------------------------
        elif choice == "14":
            bank.save_to_file()
            print_success(f"Data saved to {bank.data_file}. Goodbye!")
            break

        else:
            print_error("Invalid choice, please enter a number from 1-14.")


if __name__ == "__main__":
    main()

