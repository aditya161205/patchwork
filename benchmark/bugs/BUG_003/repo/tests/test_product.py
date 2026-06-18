"""Tests for the product model and catalog."""

import pytest

from ecommerce.product import Catalog, Product


def test_product_requires_positive_price():
    with pytest.raises(ValueError):
        Product(name="Free", price=0)


def test_catalog_add_and_get():
    catalog = Catalog()
    product = catalog.add(Product(name="Mug", price=12.5))
    assert catalog.get(product.product_id) is product
    assert len(catalog) == 1


def test_catalog_get_unknown_raises():
    catalog = Catalog()
    with pytest.raises(KeyError):
        catalog.get("PROD_9999")


def test_catalog_search_is_case_insensitive():
    catalog = Catalog()
    catalog.add(Product(name="Blue Mug", price=12.5))
    catalog.add(Product(name="Red Hat", price=20.0))
    results = catalog.search("mug")
    assert len(results) == 1
    assert results[0].name == "Blue Mug"
