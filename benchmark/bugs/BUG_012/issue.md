# Orders that have already shipped can still be cancelled

## Summary
Calling cancel() on a shipped order should raise ValueError but instead
silently sets status to CANCELLED.

## Steps to reproduce
1. Create an order
2. Call mark_shipped()
3. Call cancel()
4. Expected: ValueError raised
5. Actual: status becomes "CANCELLED"
