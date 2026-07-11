# Fixed discounts can exceed the order amount

## Summary
A fixed discount of $50 on a $30 order should cap at $30 but returns $50.

## Steps to reproduce
1. Call fixed_discount(30.0, 50.0)
2. Expected: 30.0, Got: 50.0

## Scope
Only fixed discounts are affected. The capping logic is missing.
