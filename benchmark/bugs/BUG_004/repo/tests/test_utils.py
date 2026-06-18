"""Tests for shared helpers."""

import pytest

from ecommerce.utils import (
    hash_password,
    next_id,
    require_non_negative,
    require_positive,
    round_money,
)


def test_round_money_rounds_to_two_places():
    assert round_money(10.005 + 0.005) == 10.01
    assert round_money(3) == 3.0


def test_require_positive_accepts_and_rejects():
    assert require_positive(5) == 5
    with pytest.raises(ValueError):
        require_positive(0)


def test_require_non_negative():
    assert require_non_negative(0) == 0
    with pytest.raises(ValueError):
        require_non_negative(-1)


def test_hash_password_is_deterministic():
    assert hash_password("secret") == hash_password("secret")
    assert hash_password("secret") != hash_password("other")


def test_next_id_is_sequential_and_prefixed():
    first = next_id("TST")
    second = next_id("TST")
    assert first.startswith("TST_")
    assert first != second
