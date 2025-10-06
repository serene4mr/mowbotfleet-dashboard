# migrate_auth.py - Migration from YAML to SQLite authentication

import yaml
import streamlit as st
from pathlib import Path
from sqlite_auth import get_sqlite_auth
from auth import load_users as load_yaml_users

def migrate_users_yaml_to_sqlite() -> bool:
    """
    Migrate users from YAML file to SQLite database.
    
    Returns:
        True if migration successful, False otherwise
    """
    try:
        # Get SQLite auth instance
        sqlite_auth = get_sqlite_auth()
        
        # Load users from YAML
        yaml_users = load_yaml_users()
        
        if not yaml_users:
            st.info("ℹ️ No users found in YAML file to migrate")
            return True
        
        st.info(f"📦 Found {len(yaml_users)} users in YAML file")
        
        # Check if SQLite database already has users
        existing_count = sqlite_auth.get_user_count()
        if existing_count > 0:
            st.warning(f"⚠️ SQLite database already has {existing_count} users")
            
            # Show existing users
            existing_users = sqlite_auth.list_users()
            st.write("**Existing SQLite users:**")
            for username, created_at, updated_at in existing_users:
                st.write(f"- {username} (created: {created_at})")
            
            # Ask for confirmation
            if not st.checkbox("🔄 Proceed with migration (will add/update users)"):
                st.info("❌ Migration cancelled by user")
                return False
        
        # Migrate each user
        migrated_count = 0
        for username, password_hash in yaml_users.items():
            try:
                # Insert user into SQLite (preserving the existing hash)
                with sqlite_auth.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO users (username, password_hash, updated_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                    """, (username, password_hash))
                    conn.commit()
                    
                migrated_count += 1
                st.success(f"✅ Migrated user: {username}")
                
            except Exception as e:
                st.error(f"❌ Failed to migrate user {username}: {e}")
                return False
        
        st.success(f"🎉 Migration completed! {migrated_count} users migrated to SQLite")
        
        # Verify migration
        final_count = sqlite_auth.get_user_count()
        st.info(f"📊 SQLite database now contains {final_count} users")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Migration failed: {e}")
        return False

def verify_migration() -> bool:
    """
    Verify that migration was successful by checking user credentials.
    
    Returns:
        True if verification successful, False otherwise
    """
    try:
        sqlite_auth = get_sqlite_auth()
        
        # Get users from both systems
        yaml_users = load_yaml_users()
        sqlite_users = sqlite_auth.load_users()
        
        st.subheader("🔍 Migration Verification")
        
        # Check if all YAML users exist in SQLite
        missing_users = []
        for username in yaml_users.keys():
            if username not in sqlite_users:
                missing_users.append(username)
        
        if missing_users:
            st.error(f"❌ Missing users in SQLite: {missing_users}")
            return False
        
        # Check if password hashes match
        hash_mismatches = []
        for username, yaml_hash in yaml_users.items():
            sqlite_hash = sqlite_users.get(username)
            if yaml_hash != sqlite_hash:
                hash_mismatches.append(username)
        
        if hash_mismatches:
            st.error(f"❌ Password hash mismatches for: {hash_mismatches}")
            return False
        
        st.success("✅ Migration verification passed!")
        st.info(f"📊 All {len(yaml_users)} users successfully migrated")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Verification failed: {e}")
        return False

def show_migration_status():
    """Show current migration status"""
    st.subheader("📊 Migration Status")
    
    # Check YAML file
    yaml_path = Path("config/users.yaml")
    if yaml_path.exists():
        yaml_users = load_yaml_users()
        st.info(f"📁 YAML file: {len(yaml_users)} users")
        for username in yaml_users.keys():
            st.write(f"  - {username}")
    else:
        st.warning("📁 YAML file: Not found")
    
    # Check SQLite database
    sqlite_auth = get_sqlite_auth()
    sqlite_count = sqlite_auth.get_user_count()
    st.info(f"🗄️ SQLite database: {sqlite_count} users")
    
    if sqlite_count > 0:
        sqlite_users = sqlite_auth.list_users()
        for username, created_at, updated_at in sqlite_users:
            st.write(f"  - {username} (updated: {updated_at})")

def run_migration_ui():
    """Run migration UI in Streamlit"""
    st.title("🔄 Authentication Migration: YAML → SQLite")
    
    st.markdown("""
    This tool migrates user authentication data from the YAML file to SQLite database.
    
    **What this does:**
    - Reads users from `config/users.yaml`
    - Copies them to SQLite database (`users.db`)
    - Preserves existing password hashes
    - Verifies migration was successful
    """)
    
    # Show current status
    show_migration_status()
    
    st.markdown("---")
    
    # Migration controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Run Migration", type="primary"):
            if migrate_users_yaml_to_sqlite():
                st.balloons()
    
    with col2:
        if st.button("🔍 Verify Migration"):
            verify_migration()
    
    with col3:
        if st.button("📊 Show Status"):
            st.rerun()

if __name__ == "__main__":
    run_migration_ui()
