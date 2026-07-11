"""Stock management for products."""

from __future__ import annotations

from .utils import require_non_negative


class Inventory:
    """Tracks available stock per product id."""

    def __init__(self) -> None:
        self._stock: dict[str, int] = {}

    def set_stock(self, product_id: str, quantity: int) -> None:
        require_non_negative(quantity, "quantity")
        self._stock[product_id] = quantity

    def get_stock(self, product_id: str) -> int:
        return self._stock.get(product_id, 0)

    def is_available(self, product_id: str, quantity: int) -> bool:
        return self.get_stock(product_id) >= quantity

    def reserve(self, product_id: str, quantity: int) -> None:
        """Deduct ``quantity`` from stock, refusing to go negative."""
        require_non_negative(quantity, "quantity")
        self._stock[product_id] -= quantity

    def restock(self, product_id: str, quantity: int) -> None:
        require_non_negative(quantity, "quantity")
        self._stock[product_id] = self.get_stock(product_id) + quantity
