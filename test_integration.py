#!/usr/bin/env python3
"""
Comprehensive integration test for all critical fixes
Tests the complete "How are you today?" scenario to ensure Buddy responds properly
"""

import time
import sys

def test_complete_response_system():
    """Test the complete response system end-to-end"""
    print("🧪 Testing complete response system end-to-end...")
    
    try:
        # Test optimized response generation
        from ai.latency_optimizer import generate_optimized_buddy_response
        
        user_input = "How are you today?"
        user_id = "integration_test_user"
        
        print(f"📝 Testing input: '{user_input}'")
        print("🤖 Buddy's response: ", end="")
        
        start_time = time.time()
        response_parts = []
        
        # Use the optimized response generator with fallback
        for chunk in generate_optimized_buddy_response(
            user_input=user_input,
            user_id=user_id,
            context={},
            stream=True
        ):
            response_parts.append(chunk)
            print(chunk, end="", flush=True)
        
        response_time = time.time() - start_time
        print()  # New line
        
        full_response = "".join(response_parts).strip()
        
        print(f"⏱️ Response time: {response_time:.2f} seconds")
        print(f"📊 Response length: {len(full_response)} characters")
        
        # Validate response quality
        if len(full_response) > 20 and response_time < 10:
            print("✅ Complete response system test PASSED")
            return True
        else:
            print("❌ Complete response system test FAILED")
            print(f"   Response too short: {len(full_response) <= 20}")
            print(f"   Response too slow: {response_time >= 10}")
            return False
            
    except Exception as e:
        print(f"❌ Complete response system test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling and fallback systems"""
    print("\n🧪 Testing error handling and fallback systems...")
    
    try:
        from ai.latency_optimizer import latency_optimizer
        
        # Test fallback mode enablement
        latency_optimizer.enable_fallback_mode()
        print("✅ Fallback mode enabled successfully")
        
        # Test emergency response
        emergency_response = latency_optimizer._create_emergency_response("Test input")
        if emergency_response and len(emergency_response) > 10:
            print("✅ Emergency response system working")
        else:
            print("❌ Emergency response system failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test FAILED: {e}")
        return False

def test_all_functions_available():
    """Test that all required functions are available"""
    print("\n🧪 Testing all required functions availability...")
    
    try:
        # Test latency optimizer functions
        from ai.latency_optimizer import get_latency_stats, generate_optimized_buddy_response
        stats = get_latency_stats()
        print("✅ get_latency_stats() working")
        
        # Test belief tracker functions  
        from ai.belief_evolution_tracker import get_belief_tracker
        tracker = get_belief_tracker("test_user")
        print("✅ get_belief_tracker() working")
        
        # Test memory cache manager
        from ai.memory_cache_manager import get_memory_cache_manager
        manager = get_memory_cache_manager()
        print("✅ MemoryCacheManager working")
        
        # Test async neural pathways
        from ai.reactive_neural_architecture import AsyncNeuralPathways
        pathways = AsyncNeuralPathways()
        print("✅ AsyncNeuralPathways working")
        
        return True
        
    except Exception as e:
        print(f"❌ Function availability test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_metrics():
    """Test performance metrics and monitoring"""
    print("\n🧪 Testing performance metrics and monitoring...")
    
    try:
        from ai.latency_optimizer import get_latency_stats
        from ai.memory_cache_manager import get_memory_cache_performance
        
        # Get latency stats
        latency_stats = get_latency_stats()
        if latency_stats and 'current_optimization_mode' in latency_stats:
            print("✅ Latency statistics available")
        else:
            print("❌ Latency statistics missing")
            return False
        
        # Get memory cache performance
        cache_performance = get_memory_cache_performance()
        if cache_performance and 'cache_stats' in cache_performance:
            print("✅ Memory cache performance metrics available")
        else:
            print("❌ Memory cache performance metrics missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Performance metrics test FAILED: {e}")
        return False

def main():
    """Run comprehensive integration tests"""
    print("🔍 Comprehensive Integration Test for Critical Fixes")
    print("=" * 60)
    print("🎯 Goal: Ensure Buddy can respond to 'How are you today?' without errors")
    print("=" * 60)
    
    tests = [
        ("All Functions Available", test_all_functions_available),
        ("Error Handling & Fallbacks", test_error_handling), 
        ("Performance Metrics", test_performance_metrics),
        ("Complete Response System", test_complete_response_system),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        if test_func():
            passed_tests += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print("🏁 Integration Test Results")
    print("=" * 60)
    print(f"📊 Tests Passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Buddy should now respond properly to 'How are you today?' without getting stuck")
        print("🚀 Enterprise-Grade Extraction Framework fixes are working correctly")
        return 0
    else:
        failed_tests = total_tests - passed_tests
        print(f"❌ {failed_tests} test(s) failed - some issues still need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())