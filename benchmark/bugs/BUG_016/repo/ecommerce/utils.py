"""Shared helper utilities used across the e-commerce backend."""

from __future__ import annotations

import hashlib
import itertools
from typing import Iterator

# Per-prefix monotonic counters used to mint readable, unique ids.
_id_counters: dict[str, Iterator[int]] = {}


def round_money(amount: float) -> float:
    """Round a monetary amount to 2 decimal places."""
    return round(float(amount), 2)


def require_positive(value: float, name: str = "value") -> float:
    """Return ``value`` if it is strictly positive, else raise ``ValueError``."""
    if value <= 0:
        raise ValueError(f"{name} must be positive, got {value}")
    return value


def require_non_negative(value: float, name: str = "value") -> float:
    """Return ``value`` if it is zero or positive, else raise ``ValueError``."""
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")
    return value


def hash_password(password: str) -> str:
    """Return a deterministic SHA-256 hex digest of a password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def next_id(prefix: str) -> str:
    """Return the next sequential id for ``prefix``, e.g. ``"PROD_0001"``."""
    counter = _id_counters.setdefault(prefix, itertools.count(1))
    return f"{prefix}_{next(counter):04d}"
