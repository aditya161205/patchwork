# Checkout crashes when pricing an order

## Summary

Checkout is completely broken: as soon as the system tries to produce the priced
summary of a cart (subtotal, discount, tax, shipping, total), it raises a
`TypeError` and the request fails. Customers cannot get a quote or place an
order.

## Steps to reproduce

1. Put one or more in-stock items in a cart.
2. Ask checkout for the order summary (or run a full checkout).

## Expected behavior

Checkout returns a complete priced breakdown and can proceed to place the order.

## Actual behavior

A `TypeError` is raised while the summary is being assembled. The message
indicates that one of the internal pricing calls is being given an argument that
the receiving function does not accept — i.e. the caller and the function it
calls no longer agree on the interface.

## Scope / observations

- The failure happens during summary/pricing, before any payment is attempted.
- Paths that bail out earlier (empty cart, out-of-stock) still behave correctly,
  which suggests the problem is in the pricing step itself rather than in
  validation.
- The mismatch is on the calling side: the receiving function is unchanged and
  works when called correctly elsewhere.
