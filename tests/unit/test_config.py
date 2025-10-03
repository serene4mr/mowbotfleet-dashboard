"""
Tests for configuration management functionality.

This test suite covers:
- Default configuration loading when no config file exists
- Configuration save/load roundtrip data integrity
- Environment variable overrides for broker settings
- MQTT broker URL construction (TLS vs non-TLS)
- Graceful handling of corrupt YAML configuration files
"""

import os
import yaml
import tempfile
import pytest
from config import load_config, save_config, get_broker_url, LOCAL_CFG_PATH

class TestConfigManagement:
    def setup_method(self):
        """Clean up before each test."""
        # Remove config file if it exists
        if os.path.exists(LOCAL_CFG_PATH):
            os.remove(LOCAL_CFG_PATH)
        
        # Clear environment variables
        env_vars = ["BROKER_HOST", "BROKER_PORT", "BROKER_TLS", "BROKER_USER", "BROKER_PASS"]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
    
    def teardown_method(self):
        """Clean up after each test."""
        if os.path.exists(LOCAL_CFG_PATH):
            os.remove(LOCAL_CFG_PATH)
    
    def test_load_config_defaults(self):
        """Test loading defaults when no config file exists."""
        config = load_config()
        
        assert config["broker_host"] == "localhost"
        assert config["broker_port"] == 1883
        assert config["use_tls"] == False
        assert config["broker_user"] == ""
        assert config["broker_pass"] == ""
        assert config["users"] == {}
    
    def test_save_and_load_config(self):
        """Test save/load roundtrip maintains data integrity."""
        sample_config = {
            "broker_host": "test.example.com",
            "broker_port": 8883,
            "use_tls": True,
            "broker_user": "testuser",
            "broker_pass": "testpass",
            "users": {"admin": "hashed_password_123"}
        }
        
        # Save config
        save_config(sample_config)
        
        # Load and verify
        loaded_config = load_config()
        assert loaded_config == sample_config
    
    def test_environment_variable_overrides(self):
        """Test that environment variables override file settings."""
        # Create base config file
        base_config = {
            "broker_host": "file.example.com",
            "broker_port": 1883,
            "use_tls": False,
            "broker_user": "fileuser",
            "broker_pass": "filepass",
            "users": {}
        }
        save_config(base_config)
        
        # Set environment variables
        os.environ["BROKER_HOST"] = "env.example.com"
        os.environ["BROKER_PORT"] = "8883"
        os.environ["BROKER_TLS"] = "true"
        os.environ["BROKER_USER"] = "envuser"
        os.environ["BROKER_PASS"] = "envpass"
        
        # Load config and verify overrides
        config = load_config()
        assert config["broker_host"] == "env.example.com"
        assert config["broker_port"] == 8883
        assert config["use_tls"] == True
        assert config["broker_user"] == "envuser"
        assert config["broker_pass"] == "envpass"
        assert config["users"] == {}  # Should remain from file
    
    def test_broker_url_construction(self):
        """Test broker URL construction for different TLS settings."""
        # Test non-TLS URL
        config_no_tls = {
            "broker_host": "mqtt.example.com",
            "broker_port": 1883,
            "use_tls": False
        }
        url = get_broker_url(config_no_tls)
        assert url == "mqtt://mqtt.example.com:1883"
        
        # Test TLS URL
        config_tls = {
            "broker_host": "mqtts.example.com",
            "broker_port": 8883,
            "use_tls": True
        }
        url = get_broker_url(config_tls)
        assert url == "mqtts://mqtts.example.com:8883"
    
    def test_corrupt_config_file_handling(self):
        """Test graceful handling of corrupt YAML files."""
        # Create corrupt YAML file
        with open(LOCAL_CFG_PATH, 'w') as f:
            f.write("invalid: yaml: content: [unclosed")
        
        # Should load defaults without crashing
        config = load_config()
        assert config["broker_host"] == "localhost"
        assert config["broker_port"] == 1883

if __name__ == "__main__":
    # Simple test runner for standalone execution
    import sys
    
    test_instance = TestConfigManagement()
    tests = [
        test_instance.test_load_config_defaults,
        test_instance.test_save_and_load_config,
        test_instance.test_environment_variable_overrides,
        test_instance.test_broker_url_construction,
        test_instance.test_corrupt_config_file_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_instance.setup_method()
            test_func()
            test_instance.teardown_method()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
            test_instance.teardown_method()  # Cleanup even on failure
    
    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
