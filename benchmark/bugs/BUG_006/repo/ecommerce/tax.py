"""Tax calculation by region."""

from __future__ import annotations

from .utils import require_non_negative, round_money

DEFAULT_TAX_RATES = {
    "US": 0.07,
    "EU": 0.20,
    "IN": 0.18,
    "NONE": 0.0,
}


class TaxCalculator:
    """Computes tax on an amount using per-region rates."""

    def __init__(self, rates: dict[str, float] | None = None) -> None:
        self._rates = dict(rates) if rates else dict(DEFAULT_TAX_RATES)

    def rate_for(self, region: str) -> float:
        if region not in self._rates:
            raise KeyError(f"Unknown tax region: {region}")
        return self._rates[region]

    def calculate(self, amount: float, region: str = "US") -> float:
        require_non_negative(amount, "amount")
        return round_money(amount + self.rate_for(region))
