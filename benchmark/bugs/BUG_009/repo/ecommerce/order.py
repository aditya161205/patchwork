"""Order creation and lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field

from .cart import CartItem
from .utils import next_id, round_money

VALID_STATUSES = ("CREATED", "PAID", "SHIPPED", "CANCELLED")


@dataclass
class Order:
    """A placed order with its computed monetary breakdown."""

    user_id: str
    items: list[CartItem]
    subtotal: float
    discount: float
    tax: float
    shipping: float
    total: float
    status: str = "CREATED"
    order_id: str = field(default_factory=lambda: next_id("ORD"))

    def mark_paid(self) -> None:
        self.status = "PAID"

    def mark_shipped(self) -> None:
        self.status = "SHIPPED"

    def cancel(self) -> None:
        if self.status == "SHIPPED":
            raise ValueError("Cannot cancel a shipped order")
        self.status = "CANCELLED"


def create_order(
    user_id: str,
    items: list[CartItem],
    subtotal: float,
    discount: float,
    tax: float,
    shipping: float,
) -> Order:
    """Build an order, computing the grand total from its components."""
    total = round_money(subtotal + discount + tax + shipping)
    return Order(
        user_id=user_id,
        items=list(items),
        subtotal=round_money(subtotal),
        discount=round_money(discount),
        tax=round_money(tax),
        shipping=round_money(shipping),
        total=total,
    )
