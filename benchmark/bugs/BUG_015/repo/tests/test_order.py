"""Tests for order creation and lifecycle."""

import pytest

from ecommerce.order import create_order


def _order():
    return create_order(
        user_id="USER_1",
        items=[],
        subtotal=100.0,
        discount=10.0,
        tax=6.3,
        shipping=5.0,
    )


def test_total_is_subtotal_minus_discount_plus_tax_and_shipping():
    order = _order()
    # 100 - 10 + 6.3 + 5 = 101.3
    assert order.total == 101.3
    assert order.status == "CREATED"


def test_mark_paid():
    order = _order()
    order.mark_paid()
    assert order.status == "PAID"


def test_cancel_unshipped_order():
    order = _order()
    order.cancel()
    assert order.status == "CANCELLED"


def test_cannot_cancel_shipped_order():
    order = _order()
    order.mark_shipped()
    with pytest.raises(ValueError):
        order.cancel()
