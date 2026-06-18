# Cart subtotal slows down sharply as the cart grows

## Summary

Computing a cart's subtotal becomes dramatically slower as the number of line
items increases. Small carts are fine, but the time and work to price a large
cart grow far faster than the number of items — what should be a quick,
proportional operation balloons out of control on big carts.

## Steps to reproduce

1. Build a cart with a large number of line items (e.g. dozens or more).
2. Compute the cart's subtotal.
3. Compare the amount of work done against a small cart.

## Expected behavior

Pricing the subtotal should scale **linearly** with the number of items: each
item is accounted for a constant number of times, so doubling the cart roughly
doubles the work.

## Actual behavior

The work grows super-linearly. As the item count rises, the per-subtotal effort
climbs much faster than the cart size, so large carts are disproportionately
expensive to price. The final subtotal *value* is correct — the problem is purely
how much redundant work is done to arrive at it.

## Scope / observations

- This is a performance regression, not a wrong-number bug; correctness tests on
  small carts still pass.
- A guard test asserts that the work done to compute a subtotal stays
  proportional to the number of items; it currently fails because the effort
  scales much worse than that.
