"""Discount calculations."""

from __future__ import annotations

from .utils import require_non_negative, round_money


def percentage_discount(amount: float, percent: float) -> float:
    """Return the discount value for taking ``percent`` off ``amount``."""
    require_non_negative(amount, "amount")
    if not 0 <= percent <= 100:
        raise ValueError(f"percent must be between 0 and 100, got {percent}")
    return round_money(amount * percent / 100)


def fixed_discount(amount: float, value: float) -> float:
    """Return a flat discount, never exceeding the amount itself."""
    require_non_negative(amount, "amount")
    require_non_negative(value, "value")
    return round_money(value)


def apply_discount(amount: float, discount_value: float) -> float:
    """Subtract a discount from an amount, clamped at zero."""
    require_non_negative(amount, "amount")
    require_non_negative(discount_value, "discount_value")
    return round_money(max(0.0, amount - discount_value))
