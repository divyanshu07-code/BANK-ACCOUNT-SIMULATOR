# 🏦 Bank Account Simulator

A full-featured, interactive command-line bank management system built in Python. This project simulates real-world banking operations — account creation, deposits, withdrawals, transfers, interest calculation, and statement generation — all backed by persistent JSON storage.

---

## ✨ Features

- **Create Accounts** — Open a Savings or Current account with owner name, opening balance, and a 4-digit PIN
- **Deposit / Withdraw** — PIN-protected withdrawals with account-specific rules
- **Transfer Funds** — Move money between accounts securely (PIN required)
- **Search Accounts** — Find accounts by (partial) owner name
- **View Accounts** — Inspect a single account's details and transaction history, or list all accounts
- **Close Accounts** — Permanently delete an account (PIN + confirmation required)
- **Interest Application** — Apply interest across all accounts in one click
- **Statement Export** — Generate a `.txt` transaction statement for any account
- **Auto Save/Load** — All data is stored in `bank_data.json` and automatically reloaded on startup
- **Robust Input Validation** — Handles invalid input gracefully without crashing

---

## 🧠 Concepts Demonstrated

This project showcases several core and intermediate Python programming concepts:

| Concept | Where it's used |
|---|---|
| **Inheritance & Polymorphism** | `SavingsAccount` and `CurrentAccount` extend `Account`, each overriding `withdraw()` with custom rules |
| **Custom Exceptions** | `InsufficientFundsError`, `InvalidAmountError`, `AccountNotFoundError`, `InvalidPinError` |
| **Decorators** | `@log_transaction` automatically logs the outcome of every deposit/withdrawal |
| **Magic Methods** | `__str__`, `__repr__`, `__eq__`, `__len__` for readable and comparable account objects |
| **Classmethods & Staticmethods** | `Account.total_accounts_created()`, `Account.is_valid_amount()` |
| **File Handling & Persistence** | JSON-based save/load system so data survives between runs |
| **Type Hints** | Used throughout for clarity and safety |

---

## 🏛️ Account Types

### Savings Account
- Earns **4% interest**
- Enforces a **minimum balance of ₹500** — withdrawals that would drop below this are rejected

### Current Account
- **No interest**
- Comes with an **overdraft limit** (default ₹1000), allowing the balance to go negative up to that limit

---

## 🚀 Getting Started

### Requirements
- Python 3.10+ (uses `from __future__ import annotations` and modern type hints)

### Run the Program
```bash
python bank_account_simulator_final.py
```

On first run, a `bank_data.json` file will be created automatically to persist your data. On subsequent runs, existing accounts will be loaded automatically.

---

## 📋 Menu Options

```
 1. Create new account
 2. Deposit money
 3. Withdraw money (PIN required)
 4. Transfer between accounts (PIN required)
 5. View one account
 6. View all accounts
 7. Search account by owner name
 8. Close (delete) an account
 9. Apply interest to all accounts
10. Export account statement to file
11. Save data now
12. Exit (auto-saves)
```

---

## 📁 Project Structure

```
.
├── bank_account_simulator_final.py   # Main program
├── bank_data.json                    # Auto-generated data file (created on first run)
└── statement_<ACCOUNT_ID>.txt        # Generated when exporting a statement
```

---

## 💡 Example Usage

```
Welcome to Divyanshu National Bank

=============================================
 BANK MENU
=============================================
 1. Create new account
 ...
=============================================
Enter your choice (1-12): 1
Enter owner name: Priya Sharma
Account type - (s)avings or (c)urrent? s
Enter opening balance: ₹1000
Set a 4-digit PIN: 1234
  Account created: [ACC1000] Priya Sharma (SavingsAccount) | Balance: ₹1000.00
```

---

## 🔒 Security Notes

- PINs are required for withdrawals, transfers, and account closure
- PINs are stored in plain text in the JSON data file — **this is a simulation project only** and is **not suitable for real financial use** without proper encryption and security hardening

---

## 📌 Notes & Limitations

- This is an educational/demo project meant to practice OOP, exception handling, decorators, and file I/O in Python
- Data is stored unencrypted in a local JSON file
- Designed for single-user, single-session command-line use (not a networked or multi-user system)

---

## 📄 License

Free to use and modify for learning purposes.
