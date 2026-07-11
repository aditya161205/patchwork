"""A small, self-contained e-commerce backend.

This is a *healthy* baseline repository for PatchBench: clean, fully tested,
and free of injected bugs. Later milestones derive buggy variants from it.
"""

from .cart import Cart, CartItem
from .checkout import CheckoutService, CheckoutSummary
from .coupon import Coupon, coupon_discount, is_valid
from .discount import apply_discount, fixed_discount, percentage_discount
from .inventory import Inventory
from .order import Order, create_order
from .payment import PaymentProcessor, PaymentResult
from .product import Catalog, Product
from .shipping import calculate_shipping
from .tax import TaxCalculator
from .user import User, UserRepository

__all__ = [
    "Cart",
    "CartItem",
    "CheckoutService",
    "CheckoutSummary",
    "Coupon",
    "coupon_discount",
    "is_valid",
    "apply_discount",
    "fixed_discount",
    "percentage_discount",
    "Inventory",
    "Order",
    "create_order",
    "PaymentProcessor",
    "PaymentResult",
    "Catalog",
    "Product",
    "calculate_shipping",
    "TaxCalculator",
    "User",
    "UserRepository",
]
