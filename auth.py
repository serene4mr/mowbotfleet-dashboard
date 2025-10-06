# auth.py
"""
Enhanced Authentication logic for MowbotFleet Dashboard.
Handles user verification and user creation/update with SQLite database storage.
"""

import bcrypt
import sqlite3
from typing import Dict, Optional, List, Tuple
from pathlib import Path
from utils.logging_utils import get_logger

# Get logger for auth operations
auth_logger = get_logger("auth")

class SQLiteAuth:
    """SQLite-based authentication system"""
    
    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with users table"""
        # Ensure the data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            auth_logger.info("SQLite users table initialized")
    
    def add_user(self, username: str, password: str) -> bool:
        """Add a new user to the database"""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, hashed_password)
                )
                conn.commit()
                auth_logger.info(f"User '{username}' added successfully")
                return True
            except sqlite3.IntegrityError:
                auth_logger.warning(f"User '{username}' already exists")
                return False
            except Exception as e:
                auth_logger.error(f"Error adding user '{username}': {e}")
                return False
    
    def get_user(self, username: str) -> Optional[Dict[str, str]]:
        """Get user information by username"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, password_hash, created_at, updated_at FROM users WHERE username = ?",
                (username,)
            )
            user = cursor.fetchone()
            
            if user:
                return {
                    'username': user[0],
                    'password_hash': user[1],
                    'created_at': user[2],
                    'updated_at': user[3]
                }
            return None
    
    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials"""
        user = self.get_user(username)
        if user:
            return bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8'))
        return False
    
    def update_user(self, username: str, password: str) -> bool:
        """Update user password"""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE username = ?",
                (hashed_password, username)
            )
            
            if cursor.rowcount > 0:
                conn.commit()
                auth_logger.info(f"User '{username}' updated successfully")
                return True
            else:
                auth_logger.warning(f"User '{username}' not found for update")
                return False
    
    def delete_user(self, username: str) -> bool:
        """Delete a user from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            
            if cursor.rowcount > 0:
                conn.commit()
                auth_logger.info(f"User '{username}' deleted successfully")
                return True
            else:
                auth_logger.warning(f"User '{username}' not found for deletion")
                return False
    
    def list_users(self) -> List[Tuple[str, str, str]]:
        """List all users with their timestamps"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, created_at, updated_at FROM users ORDER BY username")
            return cursor.fetchall()
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]

# Global SQLite auth instance
_sqlite_auth = None

def _get_sqlite_auth():
    """Get SQLite auth instance"""
    global _sqlite_auth
    if _sqlite_auth is None:
        _sqlite_auth = SQLiteAuth()
    return _sqlite_auth

# Public API functions - these maintain backward compatibility

def verify_user(username: str, password: str) -> bool:
    """Verify user credentials against SQLite database"""
    try:
        auth = _get_sqlite_auth()
        return auth.verify_user(username, password)
    except Exception as e:
        auth_logger.error(f"Error verifying user '{username}': {e}")
        return False

def add_or_update_user(username: str, password: str) -> bool:
    """Add new user or update existing user password"""
    try:
        auth = _get_sqlite_auth()
        user = auth.get_user(username)
        
        if user:
            # User exists, update password
            return auth.update_user(username, password)
        else:
            # User doesn't exist, add new user
            return auth.add_user(username, password)
    except Exception as e:
        auth_logger.error(f"Error adding/updating user '{username}': {e}")
        return False

def get_user_count() -> int:
    """Get total number of users in database"""
    try:
        auth = _get_sqlite_auth()
        return auth.get_user_count()
    except Exception as e:
        auth_logger.error(f"Error getting user count: {e}")
        return 0

def list_users() -> List[Tuple[str, str, str]]:
    """List all users with timestamps"""
    try:
        auth = _get_sqlite_auth()
        return auth.list_users()
    except Exception as e:
        auth_logger.error(f"Error listing users: {e}")
        return []

def delete_user(username: str) -> bool:
    """Delete a user from the database"""
    try:
        auth = _get_sqlite_auth()
        return auth.delete_user(username)
    except Exception as e:
        auth_logger.error(f"Error deleting user '{username}': {e}")
        return False

def ensure_default_admin() -> None:
    """Ensure default admin user exists"""
    try:
        auth = _get_sqlite_auth()
        if not auth.get_user("admin"):
            auth_logger.info("Creating default admin user...")
            auth.add_user("admin", "admin")
            auth_logger.info("Default admin user created")
    except Exception as e:
        auth_logger.error(f"Error ensuring default admin: {e}")

# Backward compatibility - these functions are now just aliases
def get_users_file_path():
    """Backward compatibility - returns database path instead of YAML file path"""
    return "data/users.db"

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')