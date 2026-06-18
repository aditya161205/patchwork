"""Tests for stock management."""

import pytest

from ecommerce.inventory import Inventory


def test_set_and_get_stock():
    inv = Inventory()
    inv.set_stock("PROD_1", 10)
    assert inv.get_stock("PROD_1") == 10
    assert inv.get_stock("PROD_unknown") == 0


def test_is_available():
    inv = Inventory()
    inv.set_stock("PROD_1", 3)
    assert inv.is_available("PROD_1", 3)
    assert not inv.is_available("PROD_1", 4)


def test_reserve_reduces_stock():
    inv = Inventory()
    inv.set_stock("PROD_1", 5)
    inv.reserve("PROD_1", 2)
    assert inv.get_stock("PROD_1") == 3


def test_reserve_insufficient_raises():
    inv = Inventory()
    inv.set_stock("PROD_1", 1)
    with pytest.raises(ValueError):
        inv.reserve("PROD_1", 2)


def test_restock_adds_stock():
    inv = Inventory()
    inv.set_stock("PROD_1", 1)
    inv.restock("PROD_1", 4)
    assert inv.get_stock("PROD_1") == 5
