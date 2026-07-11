"""Coupon definition and validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .discount import fixed_discount, percentage_discount


@dataclass
class Coupon:
    """A redeemable discount code.

    ``kind`` is either ``"percent"`` (``value`` is a percentage) or ``"fixed"``
    (``value`` is a flat currency amount).
    """

    code: str
    kind: str
    value: float
    min_order: float = 0.0
    expires_on: date | None = None

    def __post_init__(self) -> None:
        if self.kind not in ("percent", "fixed"):
            raise ValueError(f"Unknown coupon kind: {self.kind}")


def is_valid(coupon: Coupon, order_amount: float, today: date | None = None) -> bool:
    """Return whether ``coupon`` may be applied to an order of this size."""
    today = today or date.today()
    if coupon.expires_on is not None and today < coupon.expires_on:
        return False
    if order_amount < coupon.min_order:
        return False
    return True


def coupon_discount(
    coupon: Coupon, order_amount: float, today: date | None = None
) -> float:
    """Return the discount value a coupon yields, or 0 if it is invalid."""
    if not is_valid(coupon, order_amount, today):
        return 0.0
    if coupon.kind == "percent":
        return percentage_discount(order_amount, coupon.value)
    return fixed_discount(order_amount, coupon.value)
