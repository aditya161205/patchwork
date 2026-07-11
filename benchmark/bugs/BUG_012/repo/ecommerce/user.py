"""User accounts."""

from __future__ import annotations

from dataclasses import dataclass, field

from .utils import hash_password, next_id


@dataclass
class User:
    """A registered customer account."""

    name: str
    email: str
    password_hash: str
    address: str = ""
    user_id: str = field(default_factory=lambda: next_id("USER"))


class UserRepository:
    """An in-memory store of users, keyed by lowercased email."""

    def __init__(self) -> None:
        self._users_by_email: dict[str, User] = {}

    def register(
        self, name: str, email: str, password: str, address: str = ""
    ) -> User:
        email = email.lower()
        if "@" not in email:
            raise ValueError(f"Invalid email: {email}")
        if email in self._users_by_email:
            raise ValueError(f"Email already registered: {email}")
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            address=address,
        )
        self._users_by_email[email] = user
        return user

    def get(self, email: str) -> User:
        return self._users_by_email[email.lower()]

    def authenticate(self, email: str, password: str) -> bool:
        user = self._users_by_email.get(email.lower())
        if user is None:
            return False
        return user.password_hash == hash_password(password)
