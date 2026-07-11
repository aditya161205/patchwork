# Catalog search doesn't find products with different case

## Summary
Searching for "mug" should find "Blue Mug" but doesn't because the search
is case-sensitive.

## Steps to reproduce
1. Add Product(name="Blue Mug", price=12.5) to catalog
2. Call search("mug")
3. Expected: returns the Blue Mug
4. Actual: returns empty list
