"""
================================================================
BANK ACCOUNT SIMULATOR - FINAL VERSION
================================================================
Full-featured interactive bank system.

Features:
- Create accounts (Savings / Current) with PIN protection
- Deposit, Withdraw, Transfer (PIN required for withdraw/transfer)
- Search account by owner name
- View one account / view all accounts
- Delete (close) an account
- Apply interest to all accounts
- Export a transaction statement to a .txt file
- Auto save/load data as JSON (data survives between runs)
- Proper input validation everywhere - won't crash on bad input

Concepts used: OOP, inheritance, custom exceptions, decorators,
magic methods, classmethod/staticmethod, file handling, type hints.

Run with: python bank_account_simulator_final.py
================================================================
"""

from __future__ import annotations
import json
import os
from functools import wraps


# ----------------------------------------------------------------
# 1. CUSTOM EXCEPTIONS
# ----------------------------------------------------------------
class InsufficientFundsError(Exception):
    pass


class InvalidAmountError(Exception):
    pass


class AccountNotFoundError(Exception):
    pass


class InvalidPinError(Exception):
    pass


# ----------------------------------------------------------------
# 2. DECORATOR - logs every transaction automatically
# ----------------------------------------------------------------
def log_transaction(func):
    @wraps(func)
    def wrapper(self, amount, *args, **kwargs):
        try:
            result = func(self, amount, *args, **kwargs)
            print(f"  [OK] {func.__name__.upper()} ₹{amount:.2f} on "
                  f"{self.account_id} | New balance: ₹{self.balance:.2f}")
            return result
        except (InsufficientFundsError, InvalidAmountError) as e:
            print(f"  [FAILED] {func.__name__.upper()} on "
                  f"{self.account_id} | Reason: {e}")
            raise
    return wrapper


# ----------------------------------------------------------------
# 3. BASE ACCOUNT CLASS
# ----------------------------------------------------------------
class Account:
    _next_id = 1000
    interest_rate: float = 0.0

    def __init__(self, owner: str, balance: float = 0.0, pin: str = "0000",
                 account_id: str | None = None):
        self.owner = owner
        self.balance = balance
        self.pin = pin
        if account_id:
            self.account_id = account_id
        else:
            self.account_id = f"ACC{Account._next_id}"
            Account._next_id += 1
        self.history: list[str] = []

    def verify_pin(self, entered_pin: str) -> None:
        if entered_pin != self.pin:
            raise InvalidPinError("Incorrect PIN")

    @log_transaction
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive")
        self.balance += amount
        self.history.append(f"Deposited ₹{amount:.2f}")

    @log_transaction
    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise InsufficientFundsError(
                f"Balance ₹{self.balance:.2f} is less than ₹{amount:.2f}"
            )
        self.balance -= amount
        self.history.append(f"Withdrew ₹{amount:.2f}")

    def apply_interest(self) -> float:
        interest = self.balance * self.interest_rate
        self.balance += interest
        if interest > 0:
            self.history.append(f"Interest added: ₹{interest:.2f}")
        return interest

    @classmethod
    def total_accounts_created(cls) -> int:
        return cls._next_id - 1000

    @staticmethod
    def is_valid_amount(amount: float) -> bool:
        return amount > 0

    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "account_id": self.account_id,
            "owner": self.owner,
            "balance": self.balance,
            "pin": self.pin,
            "history": self.history,
        }

    def __str__(self) -> str:
        return (f"[{self.account_id}] {self.owner} ({self.__class__.__name__}) "
                f"| Balance: ₹{self.balance:.2f}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.owner}', {self.balance})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Account):
            return NotImplemented
        return self.account_id == other.account_id

    def __len__(self) -> int:
        return len(self.history)


class SavingsAccount(Account):
    interest_rate = 0.04

    def __init__(self, owner: str, balance: float = 0.0, pin: str = "0000",
                 account_id: str | None = None):
        super().__init__(owner, balance, pin, account_id)
        self.min_balance = 500

    @log_transaction
    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
        if self.balance - amount < self.min_balance:
            raise InsufficientFundsError(
                f"Cannot go below minimum balance of ₹{self.min_balance}"
            )
        self.balance -= amount
        self.history.append(f"Withdrew ₹{amount:.2f}")


class CurrentAccount(Account):
    interest_rate = 0.0

    def __init__(self, owner: str, balance: float = 0.0, pin: str = "0000",
                 overdraft_limit: float = 1000, account_id: str | None = None):
        super().__init__(owner, balance, pin, account_id)
        self.overdraft_limit = overdraft_limit

    @log_transaction
    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
        if amount > self.balance + self.overdraft_limit:
            raise InsufficientFundsError(
                f"Exceeds overdraft limit of ₹{self.overdraft_limit}"
            )
        self.balance -= amount
        self.history.append(f"Withdrew ₹{amount:.2f}")


# ----------------------------------------------------------------
# 4. BANK CLASS - manages all accounts + file persistence
# ----------------------------------------------------------------
class Bank:
    def __init__(self, name: str, data_file: str = "bank_data.json"):
        self.name = name
        self.data_file = data_file
        self.accounts: dict[str, Account] = {}

    def add_account(self, account: Account) -> None:
        self.accounts[account.account_id] = account

    def get_account(self, account_id: str) -> Account:
        if account_id not in self.accounts:
            raise AccountNotFoundError(f"No account with ID {account_id}")
        return self.accounts[account_id]

    def search_by_owner(self, name: str) -> list[Account]:
        name = name.strip().lower()
        return [acc for acc in self.accounts.values() if name in acc.owner.lower()]

    def delete_account(self, account_id: str) -> None:
        acc = self.get_account(account_id)
        del self.accounts[account_id]
        print(f"  Account {acc.account_id} ({acc.owner}) has been closed.")

    def transfer(self, from_id: str, to_id: str, amount: float, pin: str) -> None:
        sender = self.get_account(from_id)
        receiver = self.get_account(to_id)
        sender.verify_pin(pin)
        sender.withdraw(amount)
        receiver.deposit(amount)
        print(f"  [TRANSFER] ₹{amount:.2f} from {from_id} to {to_id} successful")

    def apply_interest_to_all(self) -> None:
        for acc in self.accounts.values():
            interest = acc.apply_interest()
            if interest > 0:
                print(f"  [INTEREST] {acc.account_id} earned ₹{interest:.2f}")

    def total_bank_balance(self) -> float:
        return sum(acc.balance for acc in self.accounts.values())

    def save_to_file(self) -> None:
        data = [acc.to_dict() for acc in self.accounts.values()]
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

    def load_from_file(self) -> None:
        if not os.path.exists(self.data_file):
            return
        with open(self.data_file, "r") as f:
            data = json.load(f)
        max_num = 999
        for entry in data:
            acc_type = entry["type"]
            acc_id = entry["account_id"]
            pin = entry.get("pin", "0000")
            if acc_type == "SavingsAccount":
                acc = SavingsAccount(entry["owner"], entry["balance"], pin, account_id=acc_id)
            else:
                acc = CurrentAccount(entry["owner"], entry["balance"], pin, account_id=acc_id)
            acc.history = entry["history"]
            self.accounts[acc_id] = acc
            num = int(acc_id.replace("ACC", ""))
            max_num = max(max_num, num)
        Account._next_id = max_num + 1

    def export_statement(self, account_id: str) -> str:
        acc = self.get_account(account_id)
        filename = f"statement_{account_id}.txt"
        with open(filename, "w") as f:
            f.write(f"Statement for {acc.owner} ({acc.account_id})\n")
            f.write(f"Account Type: {acc.__class__.__name__}\n")
            f.write(f"Current Balance: Rs.{acc.balance:.2f}\n")
            f.write("-" * 40 + "\n")
            if not acc.history:
                f.write("No transactions yet.\n")
            for line in acc.history:
                f.write(line + "\n")
        return filename

    def __str__(self) -> str:
        return f"{self.name} | {len(self.accounts)} accounts | Total: ₹{self.total_bank_balance():.2f}"


# ----------------------------------------------------------------
# 5. INPUT HELPERS - validate everything the user types
# ----------------------------------------------------------------
def read_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print("  Amount cannot be negative.")
                continue
            return value
        except ValueError:
            print("  Please enter a valid number.")


def read_account_type() -> str:
    while True:
        choice = input("Account type - (s)avings or (c)urrent? ").strip().lower()
        if choice in ("s", "c"):
            return choice
        print("  Please enter 's' for savings or 'c' for current.")


def read_pin(prompt: str = "Set a 4-digit PIN: ") -> str:
    while True:
        pin = input(prompt).strip()
        if pin.isdigit() and len(pin) == 4:
            return pin
        print("  PIN must be exactly 4 digits.")


# ----------------------------------------------------------------
# 6. INTERACTIVE MENU
# ----------------------------------------------------------------
def show_menu():
    print("\n" + "=" * 45)
    print(" BANK MENU")
    print("=" * 45)
    print(" 1. Create new account")
    print(" 2. Deposit money")
    print(" 3. Withdraw money (PIN required)")
    print(" 4. Transfer between accounts (PIN required)")
    print(" 5. View one account")
    print(" 6. View all accounts")
    print(" 7. Search account by owner name")
    print(" 8. Close (delete) an account")
    print(" 9. Apply interest to all accounts")
    print("10. Export account statement to file")
    print("11. Save data now")
    print("12. Exit (auto-saves)")
    print("=" * 45)


def main():
    bank = Bank("Divyanshu National Bank")
    bank.load_from_file()
    print(f"Welcome to {bank.name}")
    if bank.accounts:
        print(f"Loaded {len(bank.accounts)} existing account(s) from file.")

    while True:
        show_menu()
        choice = input("Enter your choice (1-12): ").strip()

        if choice == "1":
            owner = input("Enter owner name: ").strip()
            acc_type = read_account_type()
            opening_balance = read_float("Enter opening balance: ₹")
            pin = read_pin()
            if acc_type == "s":
                acc = SavingsAccount(owner, opening_balance, pin)
            else:
                acc = CurrentAccount(owner, opening_balance, pin)
            bank.add_account(acc)
            print(f"  Account created: {acc}")

        elif choice == "2":
            acc_id = input("Enter account ID: ").strip()
            try:
                acc = bank.get_account(acc_id)
                amount = read_float("Enter deposit amount: ₹")
                acc.deposit(amount)
            except (AccountNotFoundError, InvalidAmountError) as e:
                print(f"  Error: {e}")

        elif choice == "3":
            acc_id = input("Enter account ID: ").strip()
            try:
                acc = bank.get_account(acc_id)
                pin = input("Enter PIN: ").strip()
                acc.verify_pin(pin)
                amount = read_float("Enter withdrawal amount: ₹")
                acc.withdraw(amount)
            except (AccountNotFoundError, InsufficientFundsError,
                    InvalidAmountError, InvalidPinError) as e:
                print(f"  Error: {e}")

        elif choice == "4":
            from_id = input("From account ID: ").strip()
            to_id = input("To account ID: ").strip()
            try:
                pin = input("Enter PIN for sender account: ").strip()
                amount = read_float("Enter transfer amount: ₹")
                bank.transfer(from_id, to_id, amount, pin)
            except (AccountNotFoundError, InsufficientFundsError,
                    InvalidAmountError, InvalidPinError) as e:
                print(f"  Error: {e}")

        elif choice == "5":
            acc_id = input("Enter account ID: ").strip()
            try:
                acc = bank.get_account(acc_id)
                print(" ", acc)
                print(f"  Transactions so far: {len(acc)}")
                for line in acc.history:
                    print("   -", line)
            except AccountNotFoundError as e:
                print(f"  Error: {e}")

        elif choice == "6":
            if not bank.accounts:
                print("  No accounts yet.")
            else:
                for acc in bank.accounts.values():
                    print(" ", acc)
                print(" ", bank)

        elif choice == "7":
            name = input("Enter owner name (or part of it) to search: ").strip()
            results = bank.search_by_owner(name)
            if not results:
                print("  No matching accounts found.")
            else:
                for acc in results:
                    print(" ", acc)

        elif choice == "8":
            acc_id = input("Enter account ID to close: ").strip()
            try:
                acc = bank.get_account(acc_id)
                pin = input("Enter PIN to confirm closing: ").strip()
                acc.verify_pin(pin)
                confirm = input(f"  Type YES to permanently close {acc_id}: ").strip()
                if confirm == "YES":
                    bank.delete_account(acc_id)
                else:
                    print("  Cancelled.")
            except (AccountNotFoundError, InvalidPinError) as e:
                print(f"  Error: {e}")

        elif choice == "9":
            bank.apply_interest_to_all()

        elif choice == "10":
            acc_id = input("Enter account ID: ").strip()
            try:
                filename = bank.export_statement(acc_id)
                print(f"  Statement exported to {filename}")
            except AccountNotFoundError as e:
                print(f"  Error: {e}")

        elif choice == "11":
            bank.save_to_file()
            print(f"  Data saved to {bank.data_file}")

        elif choice == "12":
            bank.save_to_file()
            print(f"  Data saved to {bank.data_file}. Goodbye!")
            break

        else:
            print("  Invalid choice, please enter a number from 1-12.")


if __name__ == "__main__":
    main()
