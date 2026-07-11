# Expired coupons are accepted, valid coupons are rejected

## Summary
The expiry check is backwards — coupons that have expired are treated as valid,
and coupons that haven't expired yet are treated as invalid.

## Steps to reproduce
1. Create a coupon expired on 2020-01-01
2. Call is_valid(coupon, 100.0, today=date(2021, 1, 1))
3. Expected: False (expired)
4. Actual: True (comparison is backwards)
