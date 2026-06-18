# Percentage coupons produce incorrect order totals

## Summary

When a **percentage-based** coupon (for example, "10% off") is applied during
checkout, the order total comes out wrong. Instead of lowering the price by the
expected percentage, the checkout reports a nonsensical discount and an
incorrect total. Customers applying a valid percentage coupon are not charged
the right amount.

## Steps to reproduce

1. Add items to a cart so it has a non-trivial subtotal (e.g. a subtotal of 80).
2. Apply a percentage coupon such as `SAVE10` (10% off).
3. Ask the checkout for its priced summary (subtotal, discount, tax, shipping,
   total).

## Expected behavior

A 10% coupon on a subtotal of 80 should produce a discount of `8.00`, and the
rest of the totals (tax, shipping, grand total) should follow from the reduced
amount.

## Actual behavior

The reported discount is far larger than the order itself (roughly the size of
the whole subtotal), so the downstream totals are meaningless. The order is not
discounted in any sensible way.

## Scope / observations

- Only **percentage** discounts are affected. Flat / fixed-amount coupons
  appear to behave correctly.
- The wrong value shows up everywhere a percentage reduction is used — the raw
  reduction calculation, coupon redemption, and the checkout summary all report
  the same bad number, which suggests a single shared root cause rather than
  three independent problems.
