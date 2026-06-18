# Free shipping is never applied to standard orders

## Summary

Standard orders that are large enough to qualify for free shipping are still
being charged the normal shipping fee. The free-shipping perk effectively never
activates, no matter how large the order is.

## Steps to reproduce

1. Build a standard-shipping order whose value is at or above the published
   free-shipping amount.
2. Calculate the shipping cost for that order.

## Expected behavior

Once a standard order reaches the free-shipping amount, its shipping cost should
drop to 0.

## Actual behavior

The order is still charged the standard shipping fee. Free shipping is never
granted for standard orders, even well past the advertised qualifying amount.

## Scope / observations

- Smaller orders (correctly charged shipping) and express orders (never free)
  behave as expected, so the fee logic itself works.
- The problem is specifically the point at which standard orders are *supposed*
  to flip to free — that boundary is not being honored.
