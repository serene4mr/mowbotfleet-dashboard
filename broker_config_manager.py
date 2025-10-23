# broker_config_manager.py
"""
Secure Broker Configuration Management System
Handles MQTT broker credentials in encrypted SQLite database.
"""

import sqlite3
import json
import base64
from cryptography.fernet import Fernet
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from utils.logging_utils import get_logger

# Get logger for broker config
broker_logger = get_logger("broker_config")

class BrokerConfigManager:
    """Secure configuration management with encryption"""
    
    def __init__(self, db_path: str = "data/secure_config.db"):
        self.db_path = db_path
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
        self.init_database()
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
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
        encrypted_bytes = self.cipher.encrypt(value.encode())
        return base64.b64encode(encrypted_bytes).decode()
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a string value"""
        encrypted_bytes = base64.b64decode(encrypted_value.encode())
        decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()
    
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
            "host": "127.0.0.1",
            "port": 1883,
            "use_tls": False,
            "user": "",
            "password": "",
            "keepalive": 60,
            "client_id_prefix": "MowbotFleet"
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

# Global instance
broker_config_manager = BrokerConfigManager()
