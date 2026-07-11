# Zero-amount charges don't raise an error

## Summary
Charging $0 should raise ValueError but is silently accepted.

## Steps to reproduce
1. Create a PaymentProcessor
2. Call charge(0.0) — should raise ValueError but doesn't

## Root cause
Using require_non_negative instead of require_positive for the amount check.
