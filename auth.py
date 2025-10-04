# auth.py
"""
Enhanced Authentication logic for MowbotFleet Dashboard.
Handles user verification and user creation/update with separate user storage.
"""

import bcrypt
import yaml
from pathlib import Path
from typing import Dict

def get_users_file_path() -> Path:
    """Get the path to the users configuration file."""
    return Path("config/users.yaml")

def load_users() -> Dict[str, str]:
    """
    Load users from the dedicated users.yaml file.
    
    Returns:
        Dictionary of username -> hashed_password
    """
    users_path = get_users_file_path()
    
    if not users_path.exists():
        return {}
    
    try:
        with open(users_path, 'r') as f:
            data = yaml.safe_load(f) or {}
            return data.get("users", {})
    except (yaml.YAMLError, IOError) as e:
        # Could not load users file - return empty dict
        return {}

def save_users(users: Dict[str, str]) -> None:
    """
    Save users to the dedicated users.yaml file.
    
    Args:
        users: Dictionary of username -> hashed_password
        
    Raises:
        IOError: If file cannot be written
        yaml.YAMLError: If YAML serialization fails
    """
    users_path = get_users_file_path()
    
    # Create config directory if it doesn't exist
    users_path.parent.mkdir(exist_ok=True)
    
    # Prepare data structure
    data = {"users": users}
    
    try:
        with open(users_path, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False, indent=2)
    except (yaml.YAMLError, IOError) as e:
        raise IOError(f"Could not save users to {users_path}: {e}")

def verify_user(username: str, password: str) -> bool:
    """
    Check if the given username/password match the stored hash.
    
    Args:
        username: Username to verify
        password: Plain text password to verify
        
    Returns:
        True if credentials are valid, False otherwise
    """
    users = load_users()
    hashed = users.get(username)
    
    if not hashed:
        return False
    
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception as e:
        # Password verification failed - return False
        return False

def add_or_update_user(username: str, password: str) -> None:
    """
    Add a new user or update existing user's password hash.
    
    Args:
        username: Username to add/update
        password: Plain text password to hash and store
        
    Raises:
        IOError: If user file cannot be written
    """
    users = load_users()
    
    # Generate secure hash
    salt = bcrypt.gensalt()
    new_hash = bcrypt.hashpw(password.encode(), salt).decode()
    
    # Update users dictionary
    users[username] = new_hash
    
    # Save to file
    save_users(users)

def delete_user(username: str) -> bool:
    """
    Delete a user from the system.
    
    Args:
        username: Username to delete
        
    Returns:
        True if user was deleted, False if user didn't exist
        
    Raises:
        IOError: If user file cannot be written
    """
    users = load_users()
    
    if username not in users:
        return False
    
    # Remove user
    del users[username]
    
    # Save to file
    save_users(users)
    return True

def list_users() -> list:
    """
    Get list of all usernames.
    
    Returns:
        List of usernames
    """
    users = load_users()
    return list(users.keys())

def ensure_default_admin() -> None:
    """
    Ensure default admin user exists. Call this after config is loaded.
    Creates admin/admin if no users exist.
    """
    users = load_users()
    
    if not users:
        add_or_update_user("admin", "admin")
        # Default admin user created - will be logged when logging system is implemented

def change_password(username: str, old_password: str, new_password: str) -> bool:
    """
    Change a user's password.
    
    Args:
        username: Username
        old_password: Current password (for verification)
        new_password: New password
        
    Returns:
        True if password changed successfully, False if old password incorrect
    """
    # Verify old password first
    if not verify_user(username, old_password):
        return False
    
    # Update with new password
    add_or_update_user(username, new_password)
    return True