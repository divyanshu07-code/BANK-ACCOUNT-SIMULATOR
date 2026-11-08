# Contributing to Bank Account Simulator

Thank you for your interest in contributing to the Bank Account Simulator! This document provides guidelines and instructions for contributing to this project.

---

## 📋 How to Contribute

There are several ways you can contribute to this project:

- **Report bugs** — Found something broken? Open an issue!
- **Suggest features** — Have an idea? We'd love to hear it.
- **Fix bugs** — Browse open issues and submit a fix.
- **Improve documentation** — Help make the docs clearer and more complete.
- **Add tests** — Increase test coverage and reliability.

---

## 🛠️ Setting Up the Development Environment

1. **Fork the repository** on GitHub.

2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-username>/BANK-ACCOUNT-SIMULATOR.git
   cd BANK-ACCOUNT-SIMULATOR
   ```

3. **Create a virtual environment** and activate it:
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🧪 Running Tests

Run the full test suite before submitting any changes:

```bash
python -m unittest discover tests/
```

Make sure all tests pass. If you add new functionality, please include corresponding unit tests.

---

## 🎨 Code Style

This project follows strict Python coding standards:

- **PEP 8** — Follow the [PEP 8 Style Guide](https://peps.python.org/pep-0008/) for all Python code.
- **Type Hints** — Use type hints for all function signatures and return types.
- **Docstrings** — Include docstrings for all public classes, methods, and functions.
- **Naming Conventions**:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_SNAKE_CASE` for constants
- **Line Length** — Keep lines to a maximum of 99 characters.

---

## 🚀 Submitting Changes

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit with clear, descriptive messages:
   ```bash
   git add .
   git commit -m "Add: brief description of your change"
   ```

3. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request** against the `main` branch of the original repository.

5. **Describe your changes** in the PR description. Include:
   - What the change does
   - Why the change is needed
   - Any relevant issue numbers (e.g., `Closes #42`)

---

## 🐛 Reporting Bugs

When reporting a bug, please include:

- **Python version** (`python --version`)
- **Operating system** and version
- **Steps to reproduce** the bug
- **Expected behavior** vs. **actual behavior**
- **Error messages** or tracebacks (if any)
- **Screenshots** (if applicable)

Open a new issue on GitHub with the label `bug` and provide as much detail as possible.

---

## 💡 Tips

- Keep pull requests focused — one feature or fix per PR.
- Write tests for new code whenever possible.
- Update documentation if your changes affect usage.
- Be respectful and constructive in discussions.

Thank you for helping improve the Bank Account Simulator! 🎉
