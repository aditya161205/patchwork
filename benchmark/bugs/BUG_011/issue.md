# Emails without @ are accepted during registration

## Summary
Registering with an email like "invalid-email" (no @ sign) should raise
ValueError but is silently accepted.

## Steps to reproduce
1. Create a UserRepository
2. Call register("NoAt", "invalid-email", "pw123")
3. Expected: ValueError raised
4. Actual: user is created successfully
