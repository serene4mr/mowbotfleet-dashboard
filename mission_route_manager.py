# mission_route_manager.py
"""
Mission Route Management System
Handles saving, loading, and managing reusable mission routes.
"""

import sqlite3
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from utils.logging_utils import get_logger

# Get logger for route management operations
route_logger = get_logger("mission_route_manager")

class MissionRouteManager:
    """Mission route management system"""
    
    def __init__(self, db_path: str = "data/mission_routes.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the mission routes table"""
        # Ensure the data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create mission_routes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mission_routes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    route_data TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            route_logger.info("Mission routes table initialized")
    
    def save_mission_route(self, name: str, description: str, route_data: dict, created_by: str) -> bool:
        """Save a mission route to the database"""
        try:
            # Validate inputs
            if not name or not name.strip():
                route_logger.error("Route name cannot be empty")
                return False
            
            if not route_data:
                route_logger.error("Route data cannot be empty")
                return False
            
            # Convert route_data to JSON string
            route_json = json.dumps(route_data)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if route name already exists for this user
                cursor.execute(
                    "SELECT id FROM mission_routes WHERE name = ? AND created_by = ?",
                    (name.strip(), created_by)
                )
                
                if cursor.fetchone():
                    route_logger.warning(f"Route name '{name}' already exists for user '{created_by}'")
                    return False
                
                # Insert new route
                cursor.execute("""
                    INSERT INTO mission_routes (name, description, route_data, created_by)
                    VALUES (?, ?, ?, ?)
                """, (name.strip(), description.strip() if description else "", route_json, created_by))
                
                conn.commit()
                route_logger.info(f"Mission route '{name}' saved successfully for user '{created_by}'")
                return True
                
        except Exception as e:
            route_logger.error(f"Error saving mission route '{name}': {e}")
            return False
    
    def load_mission_route(self, route_id: int) -> Optional[Dict]:
        """Load a mission route by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, description, route_data, created_by, created_at, updated_at
                    FROM mission_routes WHERE id = ?
                """, (route_id,))
                
                route = cursor.fetchone()
                if route:
                    # Parse route_data JSON
                    route_data = json.loads(route[3])
                    
                    return {
                        'id': route[0],
                        'name': route[1],
                        'description': route[2],
                        'route_data': route_data,
                        'created_by': route[4],
                        'created_at': route[5],
                        'updated_at': route[6]
                    }
                return None
                
        except Exception as e:
            route_logger.error(f"Error loading mission route ID {route_id}: {e}")
            return None
    
    def list_mission_routes(self, created_by: Optional[str] = None) -> List[Tuple[int, str, str, str, str, str]]:
        """List all mission routes, optionally filtered by user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if created_by:
                    cursor.execute("""
                        SELECT id, name, description, created_by, created_at, updated_at
                        FROM mission_routes WHERE created_by = ?
                        ORDER BY updated_at DESC
                    """, (created_by,))
                else:
                    cursor.execute("""
                        SELECT id, name, description, created_by, created_at, updated_at
                        FROM mission_routes
                        ORDER BY updated_at DESC
                    """)
                
                return cursor.fetchall()
                
        except Exception as e:
            route_logger.error(f"Error listing mission routes: {e}")
            return []
    
    def delete_mission_route(self, route_id: int, created_by: str) -> bool:
        """Delete a mission route (only by the user who created it)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if route exists and user owns it
                cursor.execute("""
                    SELECT id FROM mission_routes 
                    WHERE id = ? AND created_by = ?
                """, (route_id, created_by))
                
                if not cursor.fetchone():
                    route_logger.warning(f"Route ID {route_id} not found or not owned by user '{created_by}'")
                    return False
                
                # Delete the route
                cursor.execute("DELETE FROM mission_routes WHERE id = ?", (route_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    route_logger.info(f"Mission route ID {route_id} deleted by user '{created_by}'")
                    return True
                else:
                    route_logger.warning(f"No route found with ID {route_id}")
                    return False
                    
        except Exception as e:
            route_logger.error(f"Error deleting mission route ID {route_id}: {e}")
            return False
    
    def search_mission_routes(self, query: str, created_by: Optional[str] = None) -> List[Tuple[int, str, str, str, str, str]]:
        """Search mission routes by name or description"""
        try:
            search_pattern = f"%{query.strip()}%"
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if created_by:
                    cursor.execute("""
                        SELECT id, name, description, created_by, created_at, updated_at
                        FROM mission_routes 
                        WHERE (name LIKE ? OR description LIKE ?) AND created_by = ?
                        ORDER BY updated_at DESC
                    """, (search_pattern, search_pattern, created_by))
                else:
                    cursor.execute("""
                        SELECT id, name, description, created_by, created_at, updated_at
                        FROM mission_routes 
                        WHERE name LIKE ? OR description LIKE ?
                        ORDER BY updated_at DESC
                    """, (search_pattern, search_pattern))
                
                return cursor.fetchall()
                
        except Exception as e:
            route_logger.error(f"Error searching mission routes for '{query}': {e}")
            return []

# Global route manager instance
_route_manager = None

def get_route_manager():
    """Get the global route manager instance"""
    global _route_manager
    if _route_manager is None:
        _route_manager = MissionRouteManager()
    return _route_manager

# Public API functions
def save_mission_route(name: str, description: str, route_data: dict, created_by: str) -> bool:
    """Save a mission route"""
    manager = get_route_manager()
    return manager.save_mission_route(name, description, route_data, created_by)

def load_mission_route(route_id: int) -> Optional[Dict]:
    """Load a mission route by ID"""
    manager = get_route_manager()
    return manager.load_mission_route(route_id)

def list_mission_routes(created_by: Optional[str] = None) -> List[Tuple[int, str, str, str, str, str]]:
    """List mission routes"""
    manager = get_route_manager()
    return manager.list_mission_routes(created_by)

def delete_mission_route(route_id: int, created_by: str) -> bool:
    """Delete a mission route"""
    manager = get_route_manager()
    return manager.delete_mission_route(route_id, created_by)

def search_mission_routes(query: str, created_by: Optional[str] = None) -> List[Tuple[int, str, str, str, str, str]]:
    """Search mission routes"""
    manager = get_route_manager()
    return manager.search_mission_routes(query, created_by)
