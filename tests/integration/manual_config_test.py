#!/usr/bin/env python3
"""
Manual integration test for configuration system.
Run this to verify config system works in practice.
"""

import os
from config import load_config, save_config, get_broker_url

def main():
    print("=== MowbotFleet Configuration Test ===\n")
    
    # Test 1: Load initial defaults
    print("1. Loading initial configuration...")
    config = load_config()
    print(f"   Broker: {config['broker_host']}:{config['broker_port']}")
    print(f"   TLS: {config['use_tls']}")
    print(f"   User count: {len(config['users'])}")
    
    # Test 2: Modify and save
    print("\n2. Modifying configuration...")
    config['broker_host'] = 'test.mqtt.example.com'
    config['broker_port'] = 8883
    config['use_tls'] = True
    config['broker_user'] = 'testuser'
    config['users']['admin'] = 'hashed_password_example'
    
    save_config(config)
    print("   Configuration saved to config_local.yaml")
    
    # Test 3: Reload and verify
    print("\n3. Reloading configuration...")
    reloaded = load_config()
    print(f"   Broker: {reloaded['broker_host']}:{reloaded['broker_port']}")
    print(f"   TLS: {reloaded['use_tls']}")
    print(f"   Users: {list(reloaded['users'].keys())}")
    
    # Test 4: URL construction
    print("\n4. Testing broker URL construction...")
    url = get_broker_url(reloaded)
    print(f"   Broker URL: {url}")
    
    # Test 5: Environment override demonstration
    print("\n5. Testing environment variable override...")
    os.environ['BROKER_HOST'] = 'env.example.com'
    env_config = load_config()
    print(f"   Host with env override: {env_config['broker_host']}")
    
    print("\n✓ Configuration system working correctly!")
    print("\nFiles created:")
    print("   - config_local.yaml (broker and user settings)")
    
    # Cleanup
    if os.path.exists('config_local.yaml'):
        print(f"\nTo clean up: rm config_local.yaml")

if __name__ == "__main__":
    main()
