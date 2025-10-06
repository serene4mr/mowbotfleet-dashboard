#!/usr/bin/env python3
"""
Migration script to move mission routes from users.db to mission_routes.db
"""

import sqlite3
import json
from pathlib import Path
from mission_route_manager import MissionRouteManager

def migrate_routes():
    """Migrate routes from users.db to mission_routes.db"""
    print("🔄 Starting route migration...")
    
    # Source and destination paths
    source_db = "data/users.db"
    dest_db = "data/mission_routes.db"
    
    # Check if source database exists
    if not Path(source_db).exists():
        print(f"❌ Source database {source_db} not found. Nothing to migrate.")
        return
    
    # Initialize new route manager (creates new database)
    route_manager = MissionRouteManager(dest_db)
    print(f"✅ Created new database: {dest_db}")
    
    # Connect to source database
    source_conn = sqlite3.connect(source_db)
    source_cursor = source_conn.cursor()
    
    try:
        # Check if mission_routes table exists in source
        source_cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='mission_routes'
        """)
        
        if not source_cursor.fetchone():
            print("ℹ️ No mission_routes table in source database. Nothing to migrate.")
            return
        
        # Get all routes from source
        source_cursor.execute("""
            SELECT id, name, description, route_data, created_by, created_at, updated_at 
            FROM mission_routes
        """)
        
        routes = source_cursor.fetchall()
        print(f"📊 Found {len(routes)} routes to migrate")
        
        if not routes:
            print("ℹ️ No routes found in source database.")
            return
        
        # Migrate each route
        migrated_count = 0
        for route in routes:
            route_id, name, description, route_data_json, created_by, created_at, updated_at = route
            
            try:
                # Parse route data to validate JSON
                route_data = json.loads(route_data_json)
                
                # Save to new database
                success = route_manager.save_mission_route(
                    name=name,
                    description=description or "",
                    route_data=route_data,
                    created_by=created_by
                )
                
                if success:
                    migrated_count += 1
                    print(f"✅ Migrated route: {name} (ID: {route_id})")
                else:
                    print(f"⚠️ Failed to migrate route: {name} (ID: {route_id}) - may already exist")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in route {name} (ID: {route_id}): {e}")
            except Exception as e:
                print(f"❌ Error migrating route {name} (ID: {route_id}): {e}")
        
        print(f"🎉 Migration completed! Migrated {migrated_count}/{len(routes)} routes")
        
        # Show summary
        if migrated_count > 0:
            print(f"📁 Routes now stored in: {dest_db}")
            print(f"🗑️ Old routes remain in: {source_db} (can be cleaned up manually)")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        source_conn.close()

def cleanup_old_routes():
    """Remove old mission_routes table from users.db"""
    print("🧹 Cleaning up old routes from users.db...")
    
    source_db = "data/users.db"
    if not Path(source_db).exists():
        print(f"❌ Source database {source_db} not found.")
        return
    
    try:
        conn = sqlite3.connect(source_db)
        cursor = conn.cursor()
        
        # Drop the mission_routes table
        cursor.execute("DROP TABLE IF EXISTS mission_routes")
        conn.commit()
        
        print("✅ Removed mission_routes table from users.db")
        
        # Show remaining tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📊 Remaining tables in users.db: {[t[0] for t in tables]}")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Mission Routes Database Migration")
    print("=" * 50)
    
    # Step 1: Migrate routes
    migrate_routes()
    
    print("\n" + "=" * 50)
    
    # Step 2: Ask about cleanup
    response = input("🗑️ Remove old mission_routes table from users.db? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        cleanup_old_routes()
    else:
        print("ℹ️ Old routes kept in users.db for backup")
    
    print("\n✅ Migration process completed!")
