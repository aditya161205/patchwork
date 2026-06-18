# Adding the same product twice loses the earlier quantity

## Summary

When a customer adds the **same product to their cart more than once**, the cart
does not keep the combined quantity. Instead of building up the total, the most
recent add seems to replace whatever was already there, so the earlier quantity
is silently lost.

## Steps to reproduce

1. Start with an empty cart.
2. Add a product with quantity 1.
3. Add the **same** product again with quantity 2.

## Expected behavior

The cart should now hold a quantity of 3 for that product (1 + 2), and the
subtotal should reflect all three units.

## Actual behavior

The cart reports a quantity of 2 — only the latest add is remembered. The units
added earlier are gone, and the subtotal is too low.

## Scope / observations

- Adding two *different* products works fine; the problem only appears when the
  same product is added again.
- This points at how the cart updates an item that is already present, rather
  than at price or subtotal math.
