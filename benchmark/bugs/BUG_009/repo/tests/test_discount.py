"""Tests for discount calculations."""

import pytest

from ecommerce.discount import apply_discount, fixed_discount, percentage_discount


def test_percentage_discount():
    assert percentage_discount(200.0, 10) == 20.0


def test_percentage_discount_out_of_range():
    with pytest.raises(ValueError):
        percentage_discount(100.0, 150)


def test_fixed_discount_capped_at_amount():
    assert fixed_discount(30.0, 50.0) == 30.0
    assert fixed_discount(30.0, 10.0) == 10.0


def test_apply_discount_clamps_at_zero():
    assert apply_discount(100.0, 30.0) == 70.0
    assert apply_discount(20.0, 50.0) == 0.0
