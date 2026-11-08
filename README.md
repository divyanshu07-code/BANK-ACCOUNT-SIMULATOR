<div align="center">

# 🏦 Bank Account Simulator

**A feature-rich, interactive command-line banking system built in Python**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://github.com/divyanshu07-code/BANK-ACCOUNT-SIMULATOR/actions/workflows/tests.yml/badge.svg)](https://github.com/divyanshu07-code/BANK-ACCOUNT-SIMULATOR/actions)

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Account Types](#-account-types) • [Contributing](#contributing)

</div>

---

## ✨ Features

- 🏦 **Account Creation** — Open Savings or Current accounts with unique IDs
- 🔐 **PIN-Secured Operations** — All sensitive operations protected by SHA-256 hashed PINs
- 💰 **Deposits & Withdrawals** — Real-time balance updates with validation
- 🔄 **Fund Transfers** — Seamlessly transfer money between accounts
- 📈 **Interest Calculation** — Automatic interest computation for Savings accounts (4% annual rate)
- 📜 **Transaction History** — Timestamped log of every transaction with detailed metadata
- 📄 **Account Statements** — Generate and export formatted account statements to text files
- 🎨 **Colorized CLI** — Beautiful, color-coded terminal interface for enhanced readability
- 💾 **JSON Persistence** — Automatic save/load of all account data to `bank_data.json`
- 📊 **Dashboard View** — At-a-glance summary of account details and recent activity

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/divyanshu07-code/BANK-ACCOUNT-SIMULATOR.git
cd BANK-ACCOUNT-SIMULATOR
```

### 2. Run the Application

**Modular package (recommended):**

```bash
python -m bank_simulator.cli
```

**Legacy single-file version:**

```bash
python bankaccountproject.py
```

> **Note:** Python 3.10 or higher is required. No external dependencies needed — the project uses only the Python standard library.

---

## 🏗️ Architecture

The project follows a clean, modular architecture with separation of concerns:

```
BANK-ACCOUNT-SIMULATOR/
├── bank_simulator/               # Core package
│   ├── __init__.py               # Package metadata & exports
│   ├── exceptions.py             # Custom exception classes
│   ├── decorators.py             # Transaction logging decorator
│   ├── models/                   # Account model layer
│   │   ├── __init__.py           # Models package init
│   │   ├── account.py            # Base Account class (ABC)
│   │   ├── savings.py            # SavingsAccount (4% interest, min balance)
│   │   └── current.py            # CurrentAccount (overdraft facility)
│   ├── bank.py                   # Bank manager & JSON file persistence
│   ├── utils.py                  # CLI helpers & colorized output
│   └── cli.py                    # Interactive menu system & entry point
├── tests/                        # Unit test suite
│   ├── test_account.py           # Base account tests
│   ├── test_savings.py           # Savings account tests
│   ├── test_current.py           # Current account tests
│   ├── test_bank.py              # Bank manager tests
│   └── test_utils.py             # Utility function tests
├── bankaccountproject.py         # Legacy single-file version
├── setup.py                      # Package installation config
├── requirements.txt              # Project dependencies
├── CONTRIBUTING.md               # Contribution guidelines
├── LICENSE                       # MIT License
└── README.md                     # You are here!
```

---

## 💳 Account Types

| Feature            | 🏦 Savings Account          | 🏢 Current Account           |
| ------------------ | --------------------------- | ----------------------------- |
| **Interest Rate**  | 4% per annum                | None                          |
| **Min Balance**    | ₹500                       | None                          |
| **Overdraft**      | ❌ Not available            | ✅ Up to ₹10,000             |
| **Best For**       | Personal savings & interest | Business & frequent transactions |

---

## 🧠 Concepts Demonstrated

This project showcases a wide range of Python programming concepts:

| Concept                    | Implementation                                         |
| -------------------------- | ------------------------------------------------------ |
| **OOP & Inheritance**      | Base `Account` class with `SavingsAccount` / `CurrentAccount` subclasses |
| **Abstract Base Classes**  | `ABC` and `@abstractmethod` for enforcing interfaces   |
| **Encapsulation**          | Private attributes with property accessors              |
| **Polymorphism**           | Overridden `withdraw()` and `account_type` methods      |
| **Decorators**             | `@log_transaction` for automatic transaction logging    |
| **Exception Handling**     | Custom exceptions (`InsufficientFundsError`, etc.)      |
| **PIN Hashing (SHA-256)**  | Secure PIN storage using `hashlib.sha256`               |
| **Logging Module**         | Python `logging` for application-level event tracking   |
| **Datetime Handling**      | Timestamped transactions with `datetime` module         |
| **Enums / Constants**      | Clean constant definitions for configuration values     |
| **File I/O**               | JSON serialization for persistent data storage          |
| **Type Hints**             | Full type annotations across all modules                |
| **Unit Testing**           | Comprehensive test suite with `unittest`                |
| **CI/CD**                  | GitHub Actions workflow for automated testing           |

---

## 📋 Menu Options

```
╔══════════════════════════════════════════╗
║         🏦  BANK ACCOUNT MENU  🏦       ║
╠══════════════════════════════════════════╣
║  1.  Create Account                     ║
║  2.  Deposit                            ║
║  3.  Withdraw                           ║
║  4.  Check Balance                      ║
║  5.  Transfer Funds                     ║
║  6.  Transaction History                ║
║  7.  Account Statement                  ║
║  8.  Calculate Interest                 ║
║  9.  List All Accounts                  ║
║  10. Close Account                      ║
║  11. Change PIN                         ║
║  12. Account Dashboard                  ║
║  13. Save & Load Data                   ║
║  14. Exit                               ║
╚══════════════════════════════════════════╝
```

---

## 🔒 Security

- **PIN Hashing** — PINs are never stored in plain text. All PINs are hashed using SHA-256 before storage, ensuring that even if the data file is accessed, PINs remain protected.
- **PIN Verification** — Each sensitive operation requires PIN verification by comparing the hash of the entered PIN against the stored hash.

> ⚠️ **Disclaimer:** This project is built for **educational purposes**. It demonstrates security concepts but is not intended for use in production financial systems.

---

## 🧪 Running Tests

Run the complete test suite:

```bash
python -m unittest discover tests/
```

Run a specific test file:

```bash
python -m unittest tests.test_account
python -m unittest tests.test_savings
python -m unittest tests.test_bank
```

Run with verbose output:

```bash
python -m unittest discover tests/ -v
```

---

## 🤝 Contributing

Contributions are welcome! Please read the [Contributing Guide](CONTRIBUTING.md) for details on the process for submitting pull requests.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**If you found this project helpful, please consider giving it a ⭐!**

Made with ❤️ by [Divyanshu](https://github.com/divyanshu07-code)

</div>
