"""Payment processing (simulated)."""

from __future__ import annotations

from dataclasses import dataclass

from .utils import next_id, require_positive

SUPPORTED_METHODS = ("card", "paypal", "wallet")


@dataclass
class PaymentResult:
    """The outcome of a charge attempt."""

    payment_id: str
    amount: float
    method: str
    status: str  # "SUCCESS" or "FAILED"

    @property
    def succeeded(self) -> bool:
        return self.status == "SUCCESS"


class PaymentProcessor:
    """A stand-in payment gateway that approves charges within a limit."""

    def __init__(self, balance_limit: float = 10_000.0) -> None:
        self._balance_limit = balance_limit

    def charge(self, amount: float, method: str = "card") -> PaymentResult:
        require_positive(amount, "amount")
        if method not in SUPPORTED_METHODS:
            raise ValueError(f"Unsupported payment method: {method}")
        status = "SUCCESS" if amount <= self._balance_limit else "FAILED"
        return PaymentResult(next_id("PAY"), amount, method, status)
