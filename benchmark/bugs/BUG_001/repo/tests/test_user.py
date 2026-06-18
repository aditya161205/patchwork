"""Tests for user accounts."""

import pytest

from ecommerce.user import UserRepository


def test_register_and_authenticate():
    repo = UserRepository()
    repo.register("Ada", "ada@example.com", "pw123", address="1 Main St")
    assert repo.authenticate("ada@example.com", "pw123")
    assert not repo.authenticate("ada@example.com", "wrong")


def test_email_is_case_insensitive():
    repo = UserRepository()
    repo.register("Ada", "Ada@Example.com", "pw123")
    assert repo.get("ada@example.com").name == "Ada"


def test_duplicate_email_rejected():
    repo = UserRepository()
    repo.register("Ada", "ada@example.com", "pw123")
    with pytest.raises(ValueError):
        repo.register("Ada2", "ada@example.com", "pw456")


def test_invalid_email_rejected():
    repo = UserRepository()
    with pytest.raises(ValueError):
        repo.register("NoAt", "invalid-email", "pw123")


def test_authenticate_unknown_user_returns_false():
    repo = UserRepository()
    assert not repo.authenticate("nobody@example.com", "pw")
