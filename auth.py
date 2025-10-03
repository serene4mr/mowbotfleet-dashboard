# auth.py
"""
Authentication logic for MowbotFleet Dashboard.
Handles user verification and user creation/update.
"""

import bcrypt
from typing import Dict
from config import load_config, save_config

def verify_user(username: str, password: str) -> bool:
    """
    Check if the given username/password match the stored hash.
    """
    cfg = load_config()
    users: Dict[str,str] = cfg.get("users", {})
    hashed = users.get(username)
    if not hashed:
        return False
    return bcrypt.checkpw(password.encode(), hashed.encode())

def add_or_update_user(username: str, password: str) -> None:
    """
    Add a new user or update existing user’s password hash.
    """
    cfg = load_config()
    users: Dict[str,str] = cfg.setdefault("users", {})
    new_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = new_hash
    save_config(cfg)
