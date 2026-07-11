"""Product model and in-memory catalog."""

from __future__ import annotations

from dataclasses import dataclass, field

from .utils import next_id, require_non_negative, require_positive


@dataclass
class Product:
    """A sellable item in the catalog."""

    name: str
    price: float
    category: str = "general"
    weight: float = 1.0
    product_id: str = field(default_factory=lambda: next_id("PROD"))

    def __post_init__(self) -> None:
        require_positive(self.price, "price")
        require_non_negative(self.weight, "weight")


class Catalog:
    """An in-memory collection of products keyed by id."""

    def __init__(self) -> None:
        self._products: dict[str, Product] = {}

    def add(self, product: Product) -> Product:
        self._products[product.product_id] = product
        return product

    def get(self, product_id: str) -> Product:
        if product_id not in self._products:
            raise KeyError(f"Unknown product: {product_id}")
        return self._products[product_id]

    def list(self) -> list[Product]:
        return list(self._products.values())

    def search(self, term: str) -> list[Product]:
        term = term.lower()
        return [p for p in self._products.values() if term in p.name]

    def __len__(self) -> int:
        return len(self._products)
