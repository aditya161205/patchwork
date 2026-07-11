"""Tests for the tools package."""

import os

import pytest

from patchbench.tools.file_read import read_file, list_files
from patchbench.tools.repo_search import grep_search, symbol_search
from patchbench.tools.linter import run_lint
from patchbench.tools.static_analysis import run_static_analysis

REPO_PATH = os.path.join(os.path.dirname(__file__), "..", "benchmark", "repos", "ecommerce")


def test_read_file():
    content = read_file(REPO_PATH, "ecommerce/cart.py")
    assert "class Cart" in content


def test_read_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_file(REPO_PATH, "nonexistent.py")


def test_list_files():
    files = list_files(REPO_PATH, "**/*.py")
    assert "ecommerce/cart.py" in files
    assert "ecommerce/product.py" in files


def test_grep_search():
    hits = grep_search(REPO_PATH, "class Cart")
    assert any(h.file == "ecommerce/cart.py" for h in hits)


def test_symbol_search():
    symbols = symbol_search(REPO_PATH, "Cart")
    names = [s.name for s in symbols]
    assert "Cart" in names


def test_lint_clean_repo():
    result = run_lint(REPO_PATH)
    assert result.passed


def test_static_analysis_clean_repo():
    result = run_static_analysis(REPO_PATH)
    assert result.passed
