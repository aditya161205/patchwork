# Checking out with an empty cart doesn't raise an error

## Summary
Attempting to checkout with an empty cart should raise ValueError but instead
proceeds to payment and order creation with zero items.

## Steps to reproduce
1. Create a CheckoutService
2. Call checkout("USER_1", Cart())
3. Expected: ValueError raised
4. Actual: proceeds with empty order
