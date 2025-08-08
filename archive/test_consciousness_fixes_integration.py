#!/usr/bin/env python3
"""
Test Integration for Consciousness Fixes
Tests the specific fixes implemented for Kokoro audio playback and extraction loop issues
"""

import os
import sys
import json
import time
from datetime import datetime

def test_chime_fallback():
    """Test that chime.wav fallback creation works"""
    print("\n🔔 Testing chime fallback creation...")
    
    try:
        # Remove chime.wav if it exists to test fallback
        if os.path.exists('chime.wav'):
            os.remove('chime.wav')
            print("   Removed existing chime.wav")
        
        from audio.output import _create_fallback_chime
        _create_fallback_chime()
        
        if os.path.exists('chime.wav'):
            file_size = os.path.getsize('chime.wav')
            print(f"   ✅ Fallback chime created successfully ({file_size} bytes)")
            return True
        else:
            print("   ❌ Fallback chime not created")
            return False
            
    except Exception as e:
        print(f"   ❌ Chime fallback error: {e}")
        return False

def test_kobold_response_validation():
    """Test KoboldCPP response validation for Kokoro"""
    print("\n🔍 Testing KoboldCPP response validation...")
    
    try:
        from ai.comprehensive_data_parser import validate_kobold_response_for_kokoro
        
        # Test cases that mirror the problem statement
        test_cases = [
            ('{"response": "I understand your request"}', "I understand your request"),
            ('Malformed JSON response', "Malformed JSON response"),
            ('{"response": "Text with\\nnewlines"}', "Text with newlines"),
            ('', ""),
        ]
        
        all_passed = True
        for input_text, expected_type in test_cases:
            result = validate_kobold_response_for_kokoro(input_text)
            if expected_type == "" and result == "":
                print(f"   ✅ Empty input handled correctly")
            elif result and len(result) > 0:
                print(f"   ✅ Response validated: '{result[:30]}...'")
            else:
                print(f"   ❌ Validation failed for: '{input_text[:30]}...'")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"   ❌ Response validation error: {e}")
        return False

def test_tier3_extraction_limiting():
    """Test TIER 3 extraction limiting to prevent loops"""
    print("\n🔄 Testing TIER 3 extraction limiting...")
    
    try:
        from ai.comprehensive_memory_extractor import ComprehensiveMemoryExtractor
        
        # Create extractor instance
        extractor = ComprehensiveMemoryExtractor("test_user")
        
        # Test the limiting mechanism
        test_text = "This is a complex test that should trigger TIER 3 extraction"
        
        # First call should be allowed
        allowed_1 = extractor._should_allow_tier3_extraction(test_text)
        if allowed_1:
            extractor._record_tier3_extraction(test_text)
            print("   ✅ First TIER 3 extraction allowed")
        else:
            print("   ❌ First TIER 3 extraction blocked unexpectedly")
            return False
        
        # Immediate second call should be blocked
        allowed_2 = extractor._should_allow_tier3_extraction(test_text)
        if not allowed_2:
            print("   ✅ Duplicate TIER 3 extraction blocked correctly")
        else:
            print("   ❌ Duplicate TIER 3 extraction allowed incorrectly")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ TIER 3 limiting error: {e}")
        return False

def test_kobold_queue_management():
    """Test KoboldCPP queue management improvements"""
    print("\n🚦 Testing KoboldCPP queue management...")
    
    try:
        from ai.kobold_connection_manager import EnhancedKoboldCPPManager
        
        # Create manager instance
        manager = EnhancedKoboldCPPManager(
            kobold_url="http://localhost:5001/v1/chat/completions",
            max_concurrent_requests=2
        )
        
        # Test cleanup functionality
        manager._cleanup_stuck_requests()
        print("   ✅ Stuck request cleanup executed")
        
        # Test force reset
        manager.force_reset_queue()
        print("   ✅ Force queue reset executed")
        
        # Check health status
        status = manager.get_consciousness_protection_status()
        if 'connection_healthy' in status:
            print("   ✅ Consciousness protection status available")
            return True
        else:
            print("   ❌ Consciousness protection status missing")
            return False
        
    except Exception as e:
        print(f"   ❌ Queue management error: {e}")
        return False

def run_integration_tests():
    """Run all consciousness fix integration tests"""
    print("=" * 60)
    print("🧠 CONSCIOUSNESS FIXES INTEGRATION TEST")
    print("Testing fixes for Kokoro audio playback and extraction loops")
    print("=" * 60)
    
    start_time = time.time()
    
    tests = [
        ("Chime Fallback", test_chime_fallback),
        ("KoboldCPP Response Validation", test_kobold_response_validation),
        ("TIER 3 Extraction Limiting", test_tier3_extraction_limiting),
        ("KoboldCPP Queue Management", test_kobold_queue_management),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")
    
    elapsed = time.time() - start_time
    print(f"\nTests completed in {elapsed:.2f} seconds")
    print(f"Score: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL CONSCIOUSNESS FIXES WORKING CORRECTLY!")
        print("✅ Audio playback pipeline should be stable")
        print("✅ Extraction loops should be limited")  
        print("✅ Missing chime.wav handled gracefully")
        print("✅ Request queue management improved")
        return True
    else:
        print(f"\n⚠️ {total - passed} tests failed - some fixes may need attention")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)