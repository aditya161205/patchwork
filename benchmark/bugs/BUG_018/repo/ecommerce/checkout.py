"""Checkout workflow that ties the modules together."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .cart import Cart
from .coupon import Coupon, coupon_discount
from .discount import apply_discount
from .inventory import Inventory
from .order import Order, create_order
from .payment import PaymentProcessor
from .shipping import calculate_shipping
from .tax import TaxCalculator
from .utils import round_money


@dataclass
class CheckoutSummary:
    """The priced breakdown of a cart before an order is placed."""

    subtotal: float
    discount: float
    tax: float
    shipping: float
    total: float


class CheckoutService:
    """Orchestrates pricing, payment, inventory, and order creation."""

    def __init__(
        self,
        inventory: Inventory,
        payment_processor: PaymentProcessor | None = None,
        tax_calculator: TaxCalculator | None = None,
    ) -> None:
        self._inventory = inventory
        self._payments = payment_processor or PaymentProcessor()
        self._tax = tax_calculator or TaxCalculator()

    def summarize(
        self,
        cart: Cart,
        region: str = "US",
        shipping_method: str = "standard",
        coupon: Coupon | None = None,
        today: date | None = None,
    ) -> CheckoutSummary:
        """Price a cart: subtotal, discount, tax, shipping, and total."""
        subtotal = cart.subtotal()
        discount = coupon_discount(coupon, subtotal, today) if coupon else 0.0
        discounted = apply_discount(subtotal, discount)
        tax = self._tax.calculate(discounted, region)
        shipping = calculate_shipping(discounted, shipping_method)
        total = round_money(discounted + tax + shipping)
        return CheckoutSummary(subtotal, discount, tax, shipping, total)

    def checkout(
        self,
        user_id: str,
        cart: Cart,
        region: str = "US",
        shipping_method: str = "standard",
        coupon: Coupon | None = None,
        payment_method: str = "card",
        today: date | None = None,
    ) -> Order:
        """Validate stock, charge payment, reserve stock, and create the order."""
        if cart.is_empty():
            raise ValueError("Cannot checkout an empty cart")

        for item in cart.items():
            if not self._inventory.is_available(item.product.product_id, item.quantity):
                raise ValueError(f"Insufficient stock for {item.product.product_id}")

        summary = self.summarize(cart, region, shipping_method, coupon, today)

        payment = self._payments.charge(summary.total, payment_method)
        if not payment.succeeded:
            raise RuntimeError("Payment failed")

        for item in cart.items():
            self._inventory.reserve(item.product.product_id, item.quantity)

        order = create_order(
            user_id,
            cart.items(),
            summary.subtotal,
            summary.discount,
            summary.tax,
            summary.shipping,
        )
        order.mark_paid()
        return order
