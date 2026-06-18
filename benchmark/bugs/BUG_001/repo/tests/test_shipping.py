"""Tests for shipping cost calculation."""

import pytest

from ecommerce.shipping import calculate_shipping


def test_standard_shipping_base_rate():
    assert calculate_shipping(50.0, "standard") == 5.0


def test_standard_free_over_threshold():
    assert calculate_shipping(100.0, "standard") == 0.0


def test_express_not_free_over_threshold():
    assert calculate_shipping(100.0, "express") == 15.0


def test_weight_surcharge():
    # 3kg => base 5 + (3-1)*2 = 9
    assert calculate_shipping(50.0, "standard", weight=3.0) == 9.0


def test_unknown_method_raises():
    with pytest.raises(ValueError):
        calculate_shipping(50.0, "teleport")
