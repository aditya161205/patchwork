# Tax calculator produces wrong values

## Summary
Tax amounts are nonsensical — a 7% tax on $100 should be $7.00 but we get $100.07.

## Steps to reproduce
1. Create a TaxCalculator with default rates
2. Call calculate(100.0, "US")
3. Expected: 7.0, Got: 100.07

## Root cause
The tax formula uses addition instead of multiplication with the rate.
