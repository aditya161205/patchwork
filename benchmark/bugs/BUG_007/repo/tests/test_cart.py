"""Tests for cart operations."""

import pytest

from ecommerce.cart import Cart
from ecommerce.product import Product


def _product(price=10.0):
    return Product(name="Item", price=price)


def test_add_item_and_subtotal():
    cart = Cart()
    cart.add_item(_product(10.0), 2)
    assert cart.item_count() == 2
    assert cart.subtotal() == 20.0


def test_add_same_product_accumulates_quantity():
    cart = Cart()
    product = _product(5.0)
    cart.add_item(product, 1)
    cart.add_item(product, 2)
    assert cart.item_count() == 3
    assert cart.subtotal() == 15.0


def test_update_quantity():
    cart = Cart()
    product = _product(4.0)
    cart.add_item(product, 1)
    cart.update_quantity(product.product_id, 5)
    assert cart.subtotal() == 20.0


def test_update_quantity_unknown_raises():
    cart = Cart()
    with pytest.raises(KeyError):
        cart.update_quantity("PROD_missing", 2)


def test_remove_and_clear():
    cart = Cart()
    product = _product()
    cart.add_item(product, 1)
    cart.remove_item(product.product_id)
    assert cart.is_empty()


def test_add_non_positive_quantity_raises():
    cart = Cart()
    with pytest.raises(ValueError):
        cart.add_item(_product(), 0)
