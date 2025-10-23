# broker_config_manager.py
"""
Secure Broker Configuration Management System
Handles MQTT broker credentials in encrypted SQLite database.
"""

import sqlite3
import json
import base64
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from utils.logging_utils import get_logger

# Try to import cryptography, fallback to base64 encoding if not available
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    print("⚠️ cryptography not available, using base64 encoding (less secure)")

# Get logger for broker config
broker_logger = get_logger("broker_config")

class BrokerConfigManager:
    """Secure configuration management with encryption"""
    
    def __init__(self, db_path: str = "data/secure_config.db"):
        self.db_path = db_path
        self.cryptography_available = CRYPTOGRAPHY_AVAILABLE
        
        if self.cryptography_available:
            self.key = self._get_or_create_key()
            self.cipher = Fernet(self.key)
        else:
            self.key = None
            self.cipher = None
            
        self.init_database()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        if not self.cryptography_available:
            return None
            
        key_file = Path("data/encryption.key")
        
        if key_file.exists():
            return key_file.read_bytes()
        else:
            # Generate new key
            key = Fernet.generate_key()
            key_file.parent.mkdir(parents=True, exist_ok=True)
            key_file.write_bytes(key)
            # Set restrictive permissions (owner only)
            key_file.chmod(0o600)
            broker_logger.info("Generated new encryption key")
            return key
    
    def init_database(self):
        """Initialize the secure configuration database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create secure config table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS secure_config (
                    config_key TEXT PRIMARY KEY,
                    encrypted_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            broker_logger.info("Broker configuration database initialized")
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a string value"""
        if self.cryptography_available and self.cipher:
            encrypted_bytes = self.cipher.encrypt(value.encode())
            return base64.b64encode(encrypted_bytes).decode()
        else:
            # Fallback to base64 encoding (less secure but functional)
            return base64.b64encode(value.encode()).decode()
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a string value"""
        if self.cryptography_available and self.cipher:
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        else:
            # Fallback to base64 decoding
            return base64.b64decode(encrypted_value.encode()).decode()
    
    def get_broker_config(self) -> Dict[str, Any]:
        """Get broker configuration (decrypted)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT encrypted_value FROM secure_config WHERE config_key = 'broker'")
            result = cursor.fetchone()
            
            if result:
                encrypted_data = result[0]
                decrypted_json = self._decrypt_value(encrypted_data)
                return json.loads(decrypted_json)
            else:
                # Return default broker config
                return self._get_default_broker_config()
    
    def save_broker_config(self, broker_config: Dict[str, Any]) -> bool:
        """Save broker configuration (encrypted)"""
        try:
            # Encrypt the broker configuration
            config_json = json.dumps(broker_config)
            encrypted_config = self._encrypt_value(config_json)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO secure_config (config_key, encrypted_value, updated_at)
                    VALUES ('broker', ?, CURRENT_TIMESTAMP)
                """, (encrypted_config,))
                
                conn.commit()
                broker_logger.info("Broker configuration saved securely")
                return True
                
        except Exception as e:
            broker_logger.error(f"Failed to save broker config: {e}")
            return False
    
    def _get_default_broker_config(self) -> Dict[str, Any]:
        """Get default broker configuration"""
        return {
            "host": "localhost",
            "port": 1883,
            "use_tls": False,
            "user": "",
            "password": ""
        }
    
    def get_broker_credentials(self) -> Tuple[str, str]:
        """Get broker credentials (username, password)"""
        config = self.get_broker_config()
        return config.get("user", ""), config.get("password", "")
    
    def get_broker_url(self) -> str:
        """Get broker URL with protocol"""
        config = self.get_broker_config()
        protocol = "mqtts" if config.get("use_tls", False) else "mqtt"
        return f"{protocol}://{config['host']}:{config['port']}"
    
    def delete_broker_config(self) -> bool:
        """Delete broker configuration from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM secure_config WHERE config_key = 'broker'")
                conn.commit()
                
                if cursor.rowcount > 0:
                    broker_logger.info("Broker configuration deleted")
                    return True
                else:
                    broker_logger.warning("No broker configuration found to delete")
                    return False
                    
        except Exception as e:
            broker_logger.error(f"Failed to delete broker config: {e}")
            return False
    
    def broker_config_exists(self) -> bool:
        """Check if broker configuration exists in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM secure_config WHERE config_key = 'broker'")
                result = cursor.fetchone()
                return result is not None
                
        except Exception as e:
            broker_logger.error(f"Failed to check broker config existence: {e}")
            return False
    
    def list_all_configs(self) -> Dict[str, Any]:
        """List all configuration keys and their metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT config_key, created_at, updated_at 
                    FROM secure_config 
                    ORDER BY updated_at DESC
                """)
                results = cursor.fetchall()
                
                configs = {}
                for row in results:
                    config_key, created_at, updated_at = row
                    configs[config_key] = {
                        "created_at": created_at,
                        "updated_at": updated_at,
                        "exists": True
                    }
                
                return configs
                
        except Exception as e:
            broker_logger.error(f"Failed to list configurations: {e}")
            return {}
    
    def get_config_metadata(self) -> Dict[str, Any]:
        """Get metadata about broker configuration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT created_at, updated_at 
                    FROM secure_config 
                    WHERE config_key = 'broker'
                """)
                result = cursor.fetchone()
                
                if result:
                    created_at, updated_at = result
                    return {
                        "exists": True,
                        "created_at": created_at,
                        "updated_at": updated_at
                    }
                else:
                    return {"exists": False}
                    
        except Exception as e:
            broker_logger.error(f"Failed to get config metadata: {e}")
            return {"exists": False, "error": str(e)}

# Global instance
broker_config_manager = BrokerConfigManager()
