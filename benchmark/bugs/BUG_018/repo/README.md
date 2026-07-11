# ecommerce — healthy baseline repo

A small, self-contained mini e-commerce backend used as a **healthy baseline**
for PatchBench. It is clean, fully tested, and contains **no injected bugs**.
Buggy variants for the benchmark are derived from this repo.

## Modules

| Module | Responsibility |
|---|---|
| `product.py` | Product model and catalog |
| `cart.py` | Cart operations |
| `inventory.py` | Stock management |
| `discount.py` | Discount calculations |
| `coupon.py` | Coupon validation |
| `checkout.py` | Checkout workflow |
| `payment.py` | Payment processing |
| `order.py` | Order creation |
| `shipping.py` | Shipping calculation |
| `user.py` | User accounts |
| `tax.py` | Tax calculation |
| `utils.py` | Shared helpers |

## Layout

```
ecommerce/        package source (one file per module above)
tests/            one pytest file per module
conftest.py       puts the package on sys.path for the tests
```

## Running the tests

From this directory (`benchmark/repos/ecommerce/`):

```bash
pip install pytest
pytest
```

All tests should pass with no warnings.
