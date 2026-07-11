"""Tests for tax calculation."""

import pytest

from ecommerce.tax import TaxCalculator


def test_calculate_default_region():
    calc = TaxCalculator()
    assert calc.calculate(100.0, "US") == 7.0


def test_calculate_other_region():
    calc = TaxCalculator()
    assert calc.calculate(100.0, "EU") == 20.0


def test_none_region_is_tax_free():
    calc = TaxCalculator()
    assert calc.calculate(100.0, "NONE") == 0.0


def test_unknown_region_raises():
    calc = TaxCalculator()
    with pytest.raises(KeyError):
        calc.calculate(100.0, "MARS")


def test_custom_rates():
    calc = TaxCalculator({"LOCAL": 0.05})
    assert calc.calculate(200.0, "LOCAL") == 10.0
