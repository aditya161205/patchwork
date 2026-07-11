"""Shipping cost calculation."""

from __future__ import annotations

from .utils import require_non_negative, round_money

FREE_SHIPPING_THRESHOLD = 100.0
SHIPPING_RATES = {
    "standard": 5.0,
    "express": 15.0,
}
# Extra charge per kilogram above the first kilogram.
WEIGHT_SURCHARGE_PER_KG = 2.0


def calculate_shipping(
    subtotal: float, method: str = "standard", weight: float = 1.0
) -> float:
    """Return the shipping cost for an order.

    Standard shipping is free once ``subtotal`` reaches the free-shipping
    threshold. Otherwise the cost is the method's base rate plus a surcharge for
    every kilogram over the first.
    """
    require_non_negative(subtotal, "subtotal")
    require_non_negative(weight, "weight")
    if method not in SHIPPING_RATES:
        raise ValueError(f"Unknown shipping method: {method}")
    if method == "standard" and subtotal >= FREE_SHIPPING_THRESHOLD:
        return 0.0
    base = SHIPPING_RATES[method]
    surcharge = weight * WEIGHT_SURCHARGE_PER_KG
    return round_money(base + surcharge)
