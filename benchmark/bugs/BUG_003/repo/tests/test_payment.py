"""Tests for payment processing."""

import pytest

from ecommerce.payment import PaymentProcessor


def test_successful_charge():
    processor = PaymentProcessor(balance_limit=1000.0)
    result = processor.charge(250.0, "card")
    assert result.succeeded
    assert result.amount == 250.0
    assert result.method == "card"


def test_charge_over_limit_fails():
    processor = PaymentProcessor(balance_limit=100.0)
    result = processor.charge(250.0, "card")
    assert not result.succeeded


def test_non_positive_amount_raises():
    processor = PaymentProcessor()
    with pytest.raises(ValueError):
        processor.charge(0.0)


def test_unsupported_method_raises():
    processor = PaymentProcessor()
    with pytest.raises(ValueError):
        processor.charge(10.0, "cash")
