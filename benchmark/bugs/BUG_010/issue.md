# Reserving more stock than available doesn't raise an error

## Summary
Calling reserve() with a quantity greater than available stock should raise
ValueError but instead allows stock to go negative.

## Steps to reproduce
1. Set stock for PROD_1 to 1
2. Call reserve("PROD_1", 2)
3. Expected: ValueError raised
4. Actual: stock becomes -1, no error
