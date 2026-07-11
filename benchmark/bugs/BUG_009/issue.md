# Order totals are higher when discounts are applied

## Summary
Applying a discount makes the order MORE expensive. The discount amount is being
added to the total instead of subtracted.

## Steps to reproduce
1. Create an order with subtotal=100, discount=10, tax=6.3, shipping=5
2. Expected total: 101.3 (100 - 10 + 6.3 + 5)
3. Actual total: 121.3 (100 + 10 + 6.3 + 5)
