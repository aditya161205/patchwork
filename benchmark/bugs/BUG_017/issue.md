# Shipping weight surcharge starts from 0kg instead of 1kg

## Summary
The first kilogram should be free but the surcharge applies to the full weight.

## Steps to reproduce
1. Call calculate_shipping(50.0, "standard", weight=3.0)
2. Expected: 5 + (3-1)*2 = 9.0
3. Actual: 5 + 3*2 = 11.0
