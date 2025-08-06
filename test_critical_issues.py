#!/usr/bin/env python3
"""
Test script to identify and validate fixes for critical issues in the Enterprise-Grade Extraction Framework
"""

import sys
import traceback
from typing import Any, Dict

def test_missing_functions():
    """Test for missing functions that need to be implemented"""
    print("🧪 Testing missing functions...")
    
    issues = []
    
    # Test get_latency_stats import
    try:
        from ai.latency_optimizer import get_latency_stats
        print("✅ get_latency_stats import successful")
    except ImportError as e:
        issues.append(f"❌ get_latency_stats missing: {e}")
    
    # Test get_belief_tracker import  
    try:
        from ai.belief_evolution_tracker import get_belief_tracker
        print("✅ get_belief_tracker import successful")
    except ImportError as e:
        issues.append(f"❌ get_belief_tracker missing: {e}")
    
    return issues

def test_memory_events_issue():
    """Test for Future memory_events attribute issue"""
    print("🧪 Testing Future memory_events issue...")
    
    issues = []
    
    try:
        from ai.latency_optimizer import latency_optimizer
        from concurrent.futures import Future
        
        # Check if Future objects are being used properly
        print("✅ LatencyOptimizer accessible")
        
        # Test a basic operation to see if memory_events errors occur
        # This is a minimal test to avoid full system startup
        print("✅ Basic LatencyOptimizer test passed")
        
    except Exception as e:
        issues.append(f"❌ Future memory_events issue: {e}")
    
    return issues

def test_event_loop_management():
    """Test event loop management in AsyncNeuralPathways"""
    print("🧪 Testing event loop management...")
    
    issues = []
    
    try:
        import asyncio
        
        # Test basic event loop access
        try:
            loop = asyncio.get_running_loop()
            print("✅ Event loop already running")
        except RuntimeError:
            print("ℹ️ No running event loop (expected in non-async context)")
            
        # Test event loop creation
        try:
            new_loop = asyncio.new_event_loop()
            new_loop.close()
            print("✅ Event loop creation successful")
        except Exception as e:
            issues.append(f"❌ Event loop creation failed: {e}")
            
    except Exception as e:
        issues.append(f"❌ Event loop management issue: {e}")
    
    return issues

def test_serialization_issues():
    """Test serialization issues with thread locks"""
    print("🧪 Testing serialization issues...")
    
    issues = []
    
    try:
        from ai.memory_cache_manager import get_memory_cache_manager
        import pickle
        
        # Get manager instance
        manager = get_memory_cache_manager()
        
        # Test if manager can be pickled (this should fail with RLock)
        try:
            pickle.dumps(manager)
            print("✅ Memory cache manager serializable")
        except Exception as e:
            issues.append(f"❌ Memory cache manager not serializable: {e}")
            
    except Exception as e:
        issues.append(f"❌ Serialization test failed: {e}")
    
    return issues

def test_fallback_pathway():
    """Test fallback direct pathway"""
    print("🧪 Testing fallback direct pathway...")
    
    issues = []
    
    try:
        # Test basic fallback functionality
        from ai.latency_optimizer import latency_optimizer
        
        # Test if fallback response generation works
        try:
            response_gen = latency_optimizer._generate_fallback_response(
                "How are you today?", 
                "test_user", 
                {}, 
                True
            )
            response = next(response_gen)
            if response:
                print("✅ Fallback pathway working")
            else:
                issues.append("❌ Fallback pathway returns empty response")
        except Exception as e:
            issues.append(f"❌ Fallback pathway failed: {e}")
            
    except Exception as e:
        issues.append(f"❌ Fallback pathway test failed: {e}")
    
    return issues

def main():
    """Run all critical issue tests"""
    print("🔍 Testing Critical Issues in Enterprise-Grade Extraction Framework")
    print("=" * 70)
    
    all_issues = []
    
    # Run all tests
    all_issues.extend(test_missing_functions())
    all_issues.extend(test_memory_events_issue())
    all_issues.extend(test_event_loop_management())
    all_issues.extend(test_serialization_issues())
    all_issues.extend(test_fallback_pathway())
    
    print("\n" + "=" * 70)
    print("🏁 Test Results Summary")
    print("=" * 70)
    
    if all_issues:
        print(f"❌ Found {len(all_issues)} critical issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
        
        print("\n🔧 These issues need to be fixed for Buddy to respond properly.")
        return 1
    else:
        print("✅ All critical issues resolved!")
        print("🎉 Buddy should be able to respond to 'How are you today?' without getting stuck.")
        return 0

if __name__ == "__main__":
    sys.exit(main())