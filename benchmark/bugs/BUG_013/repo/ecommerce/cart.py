"""Shopping cart operations."""

from __future__ import annotations

from dataclasses import dataclass

from .product import Product
from .utils import require_positive, round_money


@dataclass
class CartItem:
    """A product plus the quantity requested in a cart."""

    product: Product
    quantity: int

    @property
    def line_total(self) -> float:
        return round_money(self.product.price * self.quantity)


class Cart:
    """A collection of cart items keyed by product id."""

    def __init__(self) -> None:
        self._items: dict[str, CartItem] = {}

    def add_item(self, product: Product, quantity: int = 1) -> None:
        require_positive(quantity, "quantity")
        if product.product_id in self._items:
            self._items[product.product_id].quantity += quantity
        else:
            self._items[product.product_id] = CartItem(product, quantity)

    def remove_item(self, product_id: str) -> None:
        self._items.pop(product_id, None)

    def update_quantity(self, product_id: str, quantity: int) -> None:
        require_positive(quantity, "quantity")
        if product_id not in self._items:
            raise KeyError(f"Product not in cart: {product_id}")
        self._items[product_id].quantity = quantity

    def items(self) -> list[CartItem]:
        return list(self._items.values())

    def item_count(self) -> int:
        return sum(item.quantity for item in self._items.values())

    def subtotal(self) -> float:
        return round_money(sum(item.line_total for item in self._items.values()))

    def is_empty(self) -> bool:
        return not self._items

    def clear(self) -> None:
        self._items.clear()
