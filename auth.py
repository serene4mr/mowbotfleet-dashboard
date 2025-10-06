# auth.py
"""
Enhanced Authentication logic for MowbotFleet Dashboard.
Handles user verification and user creation/update with SQLite database storage.
"""

import bcrypt
from typing import Dict
from utils.logging_utils import get_logger
from sqlite_auth import get_sqlite_auth

# Get logger for auth operations
auth_logger = get_logger("auth")

# Global SQLite auth instance
_sqlite_auth = None

def _get_sqlite_auth():
    """Get SQLite auth instance"""
    global _sqlite_auth
    if _sqlite_auth is None:
        _sqlite_auth = get_sqlite_auth()
    return _sqlite_auth

def load_users() -> Dict[str, str]:
    """
    Load users from the SQLite database.
    
    Returns:
        Dictionary of username -> hashed_password
    """
    try:
        sqlite_auth = _get_sqlite_auth()
        return sqlite_auth.load_users()
    except Exception as e:
        auth_logger.warning(f"Could not load users from database: {e}")
        return {}

def save_users(users: Dict[str, str]) -> None:
    """
    Save users to the SQLite database.
    
    Args:
        users: Dictionary of username -> hashed_password
        
    Raises:
        Exception: If database operation fails
    """
    try:
        sqlite_auth = _get_sqlite_auth()
        success = sqlite_auth.save_users(users)
        if not success:
            raise Exception("Failed to save users to database")
    except Exception as e:
        auth_logger.error(f"Could not save users to database: {e}")
        raise

def verify_user(username: str, password: str) -> bool:
    """
    Verify user credentials against the SQLite database.
    
    Args:
        username: Username to verify
        password: Plain text password to verify
        
    Returns:
        True if credentials are valid, False otherwise
    """
    try:
        sqlite_auth = _get_sqlite_auth()
        return sqlite_auth.verify_user(username, password)
    except Exception as e:
        auth_logger.error(f"Error verifying user {username}: {e}")
        return False

def add_or_update_user(username: str, password: str) -> bool:
    """
    Add or update user in the SQLite database.
    
    Args:
        username: Username to add/update
        password: Plain text password to hash and store
        
    Returns:
        True if successful, False otherwise
    """
    try:
        sqlite_auth = _get_sqlite_auth()
        return sqlite_auth.add_or_update_user(username, password)
    except Exception as e:
        auth_logger.error(f"Error adding/updating user {username}: {e}")
        return False

def ensure_default_admin() -> None:
    """
    Ensure default admin user exists in the SQLite database.
    Creates admin user with password 'admin' if no users exist.
    """
    try:
        sqlite_auth = _get_sqlite_auth()
        
        # Check if any users exist
        user_count = sqlite_auth.get_user_count()
        
        if user_count == 0:
            # Create default admin user
            success = sqlite_auth.add_or_update_user("admin", "admin")
            if success:
                auth_logger.info("Default admin user created successfully")
            else:
                auth_logger.error("Failed to create default admin user")
        else:
            auth_logger.info(f"Users already exist in database ({user_count} users)")
            
    except Exception as e:
        auth_logger.error(f"Error ensuring default admin: {e}")

def delete_user(username: str) -> bool:
    """
    Delete user from the SQLite database.
    
    Args:
        username: Username to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        sqlite_auth = _get_sqlite_auth()
        return sqlite_auth.delete_user(username)
    except Exception as e:
        auth_logger.error(f"Error deleting user {username}: {e}")
        return False

def user_exists(username: str) -> bool:
    """
    Check if user exists in the SQLite database.
    
    Args:
        username: Username to check
        
    Returns:
        True if user exists, False otherwise
    """
    try:
        sqlite_auth = _get_sqlite_auth()
        return sqlite_auth.user_exists(username)
    except Exception as e:
        auth_logger.error(f"Error checking if user {username} exists: {e}")
        return False

def get_user_count() -> int:
    """
    Get total number of users in the SQLite database.
    
    Returns:
        Number of users
    """
    try:
        sqlite_auth = _get_sqlite_auth()
        return sqlite_auth.get_user_count()
    except Exception as e:
        auth_logger.error(f"Error getting user count: {e}")
        return 0

def list_users() -> list:
    """
    List all users with their creation/update timestamps.
    
    Returns:
        List of tuples (username, created_at, updated_at)
    """
    try:
        sqlite_auth = _get_sqlite_auth()
        return sqlite_auth.list_users()
    except Exception as e:
        auth_logger.error(f"Error listing users: {e}")
        return []

# Backward compatibility - these functions are now just aliases
def get_users_file_path():
    """Backward compatibility - returns database path instead of YAML file path"""
    return "users.db"

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False