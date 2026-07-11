# Coupons with min_order work backwards

## Summary
A coupon with min_order=100 should be invalid for orders under $100, but
it's valid for small orders and invalid for large ones.

## Steps to reproduce
1. Create Coupon with min_order=100
2. Call is_valid(coupon, 50.0)
3. Expected: False (order too small)
4. Actual: True (comparison is backwards)
