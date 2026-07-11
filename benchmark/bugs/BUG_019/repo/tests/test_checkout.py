"""Tests for the end-to-end checkout workflow."""

import pytest

from ecommerce.cart import Cart
from ecommerce.checkout import CheckoutService
from ecommerce.coupon import Coupon
from ecommerce.inventory import Inventory
from ecommerce.product import Product


def _setup():
    product = Product(name="Widget", price=40.0)
    inventory = Inventory()
    inventory.set_stock(product.product_id, 10)
    cart = Cart()
    cart.add_item(product, 2)  # subtotal 80.0
    return product, inventory, cart


def test_summary_breakdown():
    _, inventory, cart = _setup()
    service = CheckoutService(inventory)
    summary = service.summarize(cart, region="US", shipping_method="standard")
    # subtotal 80, no discount, tax 80*0.07=5.6, shipping 5 (< free threshold)
    assert summary.subtotal == 80.0
    assert summary.discount == 0.0
    assert summary.tax == 5.6
    assert summary.shipping == 5.0
    assert summary.total == 90.6


def test_summary_with_coupon():
    _, inventory, cart = _setup()
    service = CheckoutService(inventory)
    coupon = Coupon(code="SAVE10", kind="percent", value=10)
    summary = service.summarize(cart, coupon=coupon)
    # discount 8 -> discounted 72, tax 5.04, shipping 5, total 82.04
    assert summary.discount == 8.0
    assert summary.tax == 5.04
    assert summary.total == 82.04


def test_checkout_creates_paid_order_and_reserves_stock():
    product, inventory, cart = _setup()
    service = CheckoutService(inventory)
    order = service.checkout("USER_1", cart)
    assert order.status == "PAID"
    assert order.total == 90.6
    assert inventory.get_stock(product.product_id) == 8


def test_checkout_empty_cart_raises():
    _, inventory, _ = _setup()
    service = CheckoutService(inventory)
    with pytest.raises(ValueError):
        service.checkout("USER_1", Cart())


def test_checkout_insufficient_stock_raises():
    product, inventory, cart = _setup()
    inventory.set_stock(product.product_id, 1)
    service = CheckoutService(inventory)
    with pytest.raises(ValueError):
        service.checkout("USER_1", cart)
