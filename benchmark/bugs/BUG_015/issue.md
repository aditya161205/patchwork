# Users can't be looked up with different email case

## Summary
Registering with "Ada@Example.com" and looking up with "ada@example.com"
fails because email normalization is missing.

## Steps to reproduce
1. Register with email "Ada@Example.com"
2. Call get("ada@example.com")
3. Expected: returns the user
4. Actual: KeyError raised
