"""Deterministic performance regression test for cart subtotal.

This test does not rely on wall-clock timing. Instead it counts how many times
the money-rounding helper is invoked while computing a subtotal. A linear
implementation touches each line item a constant number of times; a quadratic
one balloons super-linearly.
"""

import ecommerce.cart as cart_module
from ecommerce.cart import Cart
from ecommerce.product import Product


def test_subtotal_is_linear(monkeypatch):
    calls = {"count": 0}
    original = cart_module.round_money

    def counting_round_money(amount):
        calls["count"] += 1
        return original(amount)

    monkeypatch.setattr(cart_module, "round_money", counting_round_money)

    cart = Cart()
    n = 50
    for _ in range(n):
        cart.add_item(Product(name="Item", price=1.0), 1)

    cart.subtotal()

    # Linear: one rounding per line item plus a final rounding (~n + 1).
    # Quadratic: ~n*(n+1)/2 roundings, which blows past this bound.
    assert calls["count"] <= n + 5
