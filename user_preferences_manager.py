# user_preferences_manager.py
"""
User Preferences Management System
Handles user-specific settings that should be isolated per user.
"""

import sqlite3
import json
from typing import Dict, Any, Optional
from pathlib import Path
from utils.logging_utils import get_logger

# Get logger for user preferences
prefs_logger = get_logger("user_preferences")

class UserPreferencesManager:
    """User-specific preferences management system"""
    
    def __init__(self, db_path: str = "data/user_preferences.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the user preferences table"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create user preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    username TEXT PRIMARY KEY,
                    preferences TEXT NOT NULL,  -- JSON string of user preferences
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            prefs_logger.info("User preferences database initialized")
    
    def get_user_preferences(self, username: str) -> Dict[str, Any]:
        """Get user preferences"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT preferences FROM user_preferences WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            
            if result:
                return json.loads(result[0])
            else:
                # Return default preferences for new user
                return self._get_default_preferences()
    
    def save_user_preferences(self, username: str, preferences: Dict[str, Any]) -> bool:
        """Save user preferences"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Merge with existing preferences
                existing = self.get_user_preferences(username)
                existing.update(preferences)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO user_preferences (username, preferences, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (username, json.dumps(existing)))
                
                conn.commit()
                prefs_logger.info(f"Saved preferences for user: {username}")
                return True
                
        except Exception as e:
            prefs_logger.error(f"Failed to save preferences for {username}: {e}")
            return False
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences"""
        return {
            "dashboard": {
                "map_center": {"lat": 37.5075, "lon": 127.0567},
                "map_zoom": 15,
                "map_style": "default"
            },
            "missions": {
                "default_manufacturer": "MowbotAI",
                "auto_save_routes": True
            },
            "ui": {
                "theme": "light",
                "auto_refresh": True,
                "show_debug_info": False
            }
        }

# Global instance
user_prefs_manager = UserPreferencesManager()
