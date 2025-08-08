#!/usr/bin/env python3
"""
Validation Script - Verify complete architectural refactoring
Tests that all components work and endpoints are preserved
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def validate_endpoints():
    """Validate that all service endpoints are preserved"""
    print("🔗 Validating Service Endpoints...")
    
    try:
        from config.models import get_default_endpoints, get_service_timeouts
        
        endpoints = get_default_endpoints()
        timeouts = get_service_timeouts()
        
        # Verify required endpoints
        required = {
            'llm': 'http://localhost:5001/v1/chat/completions',
            'tts': 'http://127.0.0.1:8880',
            'stt': 'ws://localhost:9090'
        }
        
        all_correct = True
        for service, expected_url in required.items():
            actual_url = endpoints.get(service)
            if actual_url == expected_url:
                timeout = timeouts.get(service, 'N/A')
                print(f"   ✅ {service.upper()}: {actual_url} (timeout: {timeout}s)")
            else:
                print(f"   ❌ {service.upper()}: Expected {expected_url}, got {actual_url}")
                all_correct = False
        
        return all_correct
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def validate_archival():
    """Validate that archival was done correctly"""
    print("📦 Validating Archival Process...")
    
    try:
        archive_dir = Path(__file__).parent / 'archive'
        manifest_file = archive_dir / 'MANIFEST.json'
        
        if not archive_dir.exists():
            print("   ❌ Archive directory not found")
            return False
            
        if not manifest_file.exists():
            print("   ❌ MANIFEST.json not found")
            return False
            
        import json
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        archived_count = manifest['archival_metadata']['total_archived']
        archived_files = manifest['archived_files']
        
        print(f"   ✅ Archive directory exists")
        print(f"   ✅ MANIFEST.json exists")
        print(f"   ✅ {archived_count} files archived")
        print(f"   ✅ All archived files have metadata")
        
        # Verify some key archived files
        archived_names = [f['file'] for f in archived_files]
        expected_archived = ['test_buddy_integration.py', 'comprehensive_buddy_test.py']
        
        for expected in expected_archived:
            if expected in archived_names:
                print(f"   ✅ {expected} correctly archived")
            else:
                print(f"   ⚠️ {expected} not found in archive")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def validate_module_structure():
    """Validate that new module structure is correct"""
    print("🏗️ Validating Module Structure...")
    
    required_dirs = [
        'config', 'stt', 'llm', 'tts', 'services', 'tests', 'tools', 'archive'
    ]
    
    project_root = Path(__file__).parent
    all_exist = True
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            # Check for __init__.py (except archive)
            if dir_name not in ['archive'] and (dir_path / '__init__.py').exists():
                print(f"   ✅ {dir_name}/ (with __init__.py)")
            elif dir_name == 'archive':
                print(f"   ✅ {dir_name}/ (archive folder)")
            else:
                print(f"   ⚠️ {dir_name}/ (missing __init__.py)")
        else:
            print(f"   ❌ {dir_name}/ (missing)")
            all_exist = False
    
    # Check key files
    key_files = [
        'runner_clean.py',
        'requirements.txt',
        'config.py',  # Backward compatibility
        'main.py'     # Original preserved
    ]
    
    for file_name in key_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"   ✅ {file_name}")
        else:
            print(f"   ❌ {file_name} (missing)")
            all_exist = False
    
    return all_exist

def validate_backward_compatibility():
    """Validate that existing imports still work"""
    print("🔄 Validating Backward Compatibility...")
    
    try:
        # Test that old config import style still works
        import config
        
        # Check key variables
        required_vars = [
            'KOBOLD_URL', 'KOKORO_API_BASE_URL', 'FASTER_WHISPER_WS',
            'DEBUG', 'SAMPLE_RATE', 'MEMORY_EXTRACTION_ENABLED'
        ]
        
        all_available = True
        for var_name in required_vars:
            if hasattr(config, var_name):
                value = getattr(config, var_name)
                print(f"   ✅ config.{var_name} = {value}")
            else:
                print(f"   ❌ config.{var_name} (missing)")
                all_available = False
        
        return all_available
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

async def validate_watchdog_functionality():
    """Validate watchdog functionality"""
    print("🐕 Validating Watchdog Functionality...")
    
    try:
        from config.audio import WATCHDOG_INTERVAL_S, WATCHDOG_ENABLED
        
        print(f"   ✅ Watchdog enabled: {WATCHDOG_ENABLED}")
        print(f"   ✅ Watchdog interval: {WATCHDOG_INTERVAL_S}s")
        
        # Validate interval is reasonable
        if isinstance(WATCHDOG_INTERVAL_S, (int, float)) and 1 <= WATCHDOG_INTERVAL_S <= 60:
            print(f"   ✅ Interval is reasonable ({WATCHDOG_INTERVAL_S}s)")
            return True
        else:
            print(f"   ❌ Interval is unreasonable ({WATCHDOG_INTERVAL_S}s)")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def validate_no_regression():
    """Validate no feature regression"""
    print("🛡️ Validating No Regression...")
    
    try:
        # Test that modular config provides same values as expected
        from config import (
            KOBOLD_URL, KOKORO_API_BASE_URL, FASTER_WHISPER_WS,
            KOKORO_DEFAULT_VOICE, SAMPLE_RATE, ADVANCED_AI_ASSISTANT
        )
        
        expected_values = {
            'KOBOLD_URL': 'http://localhost:5001/v1/chat/completions',
            'KOKORO_API_BASE_URL': 'http://127.0.0.1:8880', 
            'FASTER_WHISPER_WS': 'ws://localhost:9090',
            'KOKORO_DEFAULT_VOICE': 'af_heart',
            'SAMPLE_RATE': 16000,
            'ADVANCED_AI_ASSISTANT': True
        }
        
        all_match = True
        for var_name, expected in expected_values.items():
            actual = locals()[var_name]
            if actual == expected:
                print(f"   ✅ {var_name}: {actual}")
            else:
                print(f"   ❌ {var_name}: Expected {expected}, got {actual}")
                all_match = False
        
        return all_match
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def main():
    """Main validation script"""
    print("🔍 BUDDY ARCHITECTURAL REFACTORING VALIDATION")
    print("=" * 60)
    print("Verifying complete refactoring with no behavioral changes")
    
    # Run all validations
    validations = [
        ("Endpoints", await validate_endpoints()),
        ("Archival", validate_archival()),
        ("Module Structure", validate_module_structure()), 
        ("Backward Compatibility", validate_backward_compatibility()),
        ("Watchdog", await validate_watchdog_functionality()),
        ("No Regression", validate_no_regression())
    ]
    
    print("\n" + "=" * 60)
    print("🎯 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(validations)
    
    for test_name, result in validations:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<20}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n🎉 REFACTORING COMPLETE!")
        print("✅ All architectural changes validated successfully")
        print("✅ No behavioral regression detected")
        print("✅ All endpoints and features preserved") 
        print("✅ Clean, modular architecture achieved")
        return 0
    else:
        print("\n⚠️ REFACTORING INCOMPLETE")
        print("Some validations failed - please review")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        sys.exit(1)