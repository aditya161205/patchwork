# Product model accepts price=0

## Summary
Creating a Product with price=0 should raise ValueError but is accepted.

## Steps to reproduce
1. Create Product(name="Free", price=0)
2. Expected: ValueError raised
3. Actual: product created successfully
