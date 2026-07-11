# Express shipping becomes free for large orders

## Summary
Only standard shipping should be free over the threshold, but express
shipping also becomes free.

## Steps to reproduce
1. Call calculate_shipping(100.0, "express")
2. Expected: 15.0
3. Actual: 0.0

## Root cause
The free shipping condition doesn't check the method.
