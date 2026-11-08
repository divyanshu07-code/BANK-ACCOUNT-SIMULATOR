from setuptools import setup, find_packages

setup(
    name="bank-account-simulator",
    version="2.0.0",
    description="A feature-rich CLI bank account simulator built in Python",
    author="Divyanshu",
    author_email="",
    url="https://github.com/divyanshu07-code/BANK-ACCOUNT-SIMULATOR",
    packages=find_packages(),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "bank-simulator=bank_simulator.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
