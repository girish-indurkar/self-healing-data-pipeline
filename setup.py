from setuptools import setup, find_packages

setup(
    name="self-healing-pipeline",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "pandas>=2.0.0",
        "duckdb>=0.9.0",
        "streamlit>=1.30.0",
        "pyyaml>=6.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "self-heal=interactive:main",
        ],
    },
    python_requires=">=3.9",
)

