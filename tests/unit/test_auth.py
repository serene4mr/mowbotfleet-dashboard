"""
Tests for authentication functionality.

This test suite covers:
- User verification for non-existent users
- User creation with password hashing and verification
- Password updates and verification of old vs new passwords
- Integration with configuration system for user storage
"""
import os, pytest, bcrypt
from config import LOCAL_CFG_PATH, load_config, save_config
from auth import verify_user, add_or_update_user

class TestAuth:
    def setup_method(self):
        # Ensure clean config
        if os.path.exists(LOCAL_CFG_PATH):
            os.remove(LOCAL_CFG_PATH)
        # Start with empty users
        save_config({"users": {}})

    def teardown_method(self):
        if os.path.exists(LOCAL_CFG_PATH):
            os.remove(LOCAL_CFG_PATH)

    def test_verify_nonexistent_user(self):
        assert not verify_user("alice", "password")

    def test_add_user_and_verify(self):
        add_or_update_user("alice", "secret123")
        cfg = load_config()
        # Stored hash should not equal plaintext
        assert cfg["users"]["alice"] != "secret123"
        assert verify_user("alice", "secret123")
        assert not verify_user("alice", "wrongpass")

    def test_update_user_password(self):
        add_or_update_user("bob", "firstpass")
        assert verify_user("bob", "firstpass")
        add_or_update_user("bob", "newpass")
        assert not verify_user("bob", "firstpass")
        assert verify_user("bob", "newpass")
