"""Tests for coupon validation and redemption."""

from datetime import date

import pytest

from ecommerce.coupon import Coupon, coupon_discount, is_valid


def test_unknown_kind_rejected():
    with pytest.raises(ValueError):
        Coupon(code="BAD", kind="bogus", value=10)


def test_percent_coupon_discount():
    coupon = Coupon(code="SAVE10", kind="percent", value=10)
    assert coupon_discount(coupon, 200.0) == 20.0


def test_fixed_coupon_discount():
    coupon = Coupon(code="MINUS5", kind="fixed", value=5)
    assert coupon_discount(coupon, 50.0) == 5.0


def test_min_order_not_met_is_invalid():
    coupon = Coupon(code="BIG", kind="percent", value=10, min_order=100.0)
    assert not is_valid(coupon, 50.0)
    assert coupon_discount(coupon, 50.0) == 0.0


def test_expired_coupon_is_invalid():
    coupon = Coupon(
        code="OLD", kind="percent", value=10, expires_on=date(2020, 1, 1)
    )
    assert not is_valid(coupon, 100.0, today=date(2021, 1, 1))
    assert coupon_discount(coupon, 100.0, today=date(2021, 1, 1)) == 0.0
