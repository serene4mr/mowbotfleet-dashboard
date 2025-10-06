# sqlite_auth.py - SQLite-based authentication functions

import sqlite3
import bcrypt
import streamlit as st
from typing import Dict, Optional
from pathlib import Path

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
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def load_users(self) -> Dict[str, str]:
        """
        Load all users from SQLite database.
        
        Returns:
            Dictionary of username -> hashed_password
        """
        users = {}
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, password_hash FROM users")
                
                for row in cursor.fetchall():
                    username, password_hash = row
                    users[username] = password_hash
                    
        except Exception as e:
            st.error(f"Database error loading users: {e}")
            
        return users
    
    def save_users(self, users: Dict[str, str]) -> bool:
        """
        Save users to SQLite database.
        
        Args:
            users: Dictionary of username -> hashed_password
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Clear existing users
                cursor.execute("DELETE FROM users")
                
                # Insert all users
                for username, password_hash in users.items():
                    cursor.execute("""
                        INSERT INTO users (username, password_hash)
                        VALUES (?, ?)
                    """, (username, password_hash))
                
                conn.commit()
                return True
                
        except Exception as e:
            st.error(f"Database error saving users: {e}")
            return False
    
    def verify_user(self, username: str, password: str) -> bool:
        """
        Verify user credentials against SQLite database.
        
        Args:
            username: Username to verify
            password: Plain text password to verify
            
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT password_hash FROM users WHERE username = ?",
                    (username,)
                )
                
                result = cursor.fetchone()
                if result:
                    stored_hash = result[0]
                    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
                    
        except Exception as e:
            st.error(f"Database error verifying user: {e}")
            
        return False
    
    def add_or_update_user(self, username: str, password: str) -> bool:
        """
        Add or update user in SQLite database.
        
        Args:
            username: Username to add/update
            password: Plain text password to hash and store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Hash the password using bcrypt (same as original system)
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Insert or replace user
                cursor.execute("""
                    INSERT OR REPLACE INTO users (username, password_hash, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (username, password_hash))
                
                conn.commit()
                return True
                
        except Exception as e:
            st.error(f"Database error adding/updating user: {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """
        Delete user from SQLite database.
        
        Args:
            username: Username to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                conn.commit()
                return True
                
        except Exception as e:
            st.error(f"Database error deleting user: {e}")
            return False
    
    def user_exists(self, username: str) -> bool:
        """
        Check if user exists in database.
        
        Args:
            username: Username to check
            
        Returns:
            True if user exists, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
                return cursor.fetchone() is not None
                
        except Exception as e:
            st.error(f"Database error checking user: {e}")
            return False
    
    def get_user_count(self) -> int:
        """
        Get total number of users in database.
        
        Returns:
            Number of users
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                return cursor.fetchone()[0]
                
        except Exception as e:
            st.error(f"Database error counting users: {e}")
            return 0
    
    def list_users(self) -> list:
        """
        List all users with their creation/update timestamps.
        
        Returns:
            List of tuples (username, created_at, updated_at)
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT username, created_at, updated_at 
                    FROM users 
                    ORDER BY created_at
                """)
                return cursor.fetchall()
                
        except Exception as e:
            st.error(f"Database error listing users: {e}")
            return []

# Global SQLite auth instance
@st.cache_resource
def get_sqlite_auth():
    """Get global SQLite auth instance"""
    return SQLiteAuth()
