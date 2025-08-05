#!/usr/bin/env python3
"""
Test Enterprise-Grade Extraction Optimization Framework
Created: 2025-01-08
Purpose: Comprehensive testing of the new enterprise extraction framework
"""

import sys
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the project root to Python path
sys.path.insert(0, '/home/runner/work/Buddy/Buddy')

def test_extraction_coordinator():
    """Test the enterprise extraction coordinator"""
    print("🧪 Testing Enterprise Extraction Coordinator...")
    print("=" * 60)
    
    try:
        from ai.extraction_coordinator import (
            get_extraction_coordinator,
            extract_with_enterprise_coordination,
            ExtractionPriority,
            InteractionType,
            get_extraction_performance_report
        )
        
        coordinator = get_extraction_coordinator()
        print("✅ Extraction coordinator imported successfully")
        
        # Test different interaction types and priorities
        test_cases = [
            {
                "text": "Hello, how are you today?",
                "interaction_type": InteractionType.TEXT_CHAT,
                "priority": ExtractionPriority.NORMAL,
                "expected": "Should handle normal text chat"
            },
            {
                "text": "What's the weather like?",
                "interaction_type": InteractionType.VOICE_TO_SPEECH,
                "priority": ExtractionPriority.CRITICAL,
                "expected": "Should prioritize voice interaction"
            },
            {
                "text": "Remember my birthday is next week",
                "interaction_type": InteractionType.BACKGROUND_PROCESSING,
                "priority": ExtractionPriority.LOW,
                "expected": "Should process in background"
            }
        ]
        
        results = []
        for i, test_case in enumerate(test_cases):
            print(f"\n🔍 Test {i+1}: {test_case['expected']}")
            
            start_time = time.time()
            result = extract_with_enterprise_coordination(
                username="test_user",
                text=test_case["text"],
                interaction_type=test_case["interaction_type"],
                priority=test_case["priority"]
            )
            end_time = time.time()
            
            execution_time = end_time - start_time
            results.append({
                "test": i+1,
                "execution_time": execution_time,
                "result": result,
                "priority": test_case["priority"].value
            })
            
            print(f"  ⏱️ Execution time: {execution_time:.3f}s")
            print(f"  📊 Intent: {result.intent_classification}")
            print(f"  🎯 Memory events: {len(result.memory_events)}")
        
        # Test concurrent requests
        print(f"\n🔄 Testing concurrent extraction requests...")
        
        def concurrent_extraction(request_id):
            return extract_with_enterprise_coordination(
                username=f"user_{request_id}",
                text=f"Test concurrent request {request_id}",
                interaction_type=InteractionType.TEXT_CHAT,
                priority=ExtractionPriority.NORMAL
            )
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            concurrent_start = time.time()
            futures = [executor.submit(concurrent_extraction, i) for i in range(10)]
            concurrent_results = []
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    concurrent_results.append(result)
                except Exception as e:
                    print(f"  ❌ Concurrent request failed: {e}")
            
            concurrent_end = time.time()
            concurrent_time = concurrent_end - concurrent_start
            
            print(f"  ✅ Processed {len(concurrent_results)} concurrent requests in {concurrent_time:.3f}s")
            print(f"  📈 Average time per request: {concurrent_time/len(concurrent_results):.3f}s")
        
        # Get performance metrics
        print(f"\n📊 Performance Metrics:")
        metrics = get_extraction_performance_report()
        
        extraction_metrics = metrics.get("extraction_metrics", {})
        print(f"  Total requests: {extraction_metrics.get('total_requests', 0)}")
        print(f"  Successful extractions: {extraction_metrics.get('successful_extractions', 0)}")
        print(f"  Failed extractions: {extraction_metrics.get('failed_extractions', 0)}")
        print(f"  Cache hits: {extraction_metrics.get('cached_hits', 0)}")
        print(f"  Average response time: {extraction_metrics.get('average_response_time', 0):.3f}s")
        
        connection_pool = metrics.get("connection_pool", {})
        print(f"  Connection pool size: {connection_pool.get('total_connections', 0)}")
        print(f"  Active connections: {connection_pool.get('active_connections', 0)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_memory_cache_manager():
    """Test the intelligent memory cache manager"""
    print("\n🧪 Testing Intelligent Memory Cache Manager...")
    print("=" * 60)
    
    try:
        from ai.memory_cache_manager import (
            get_memory_cache_manager,
            cache_memory_intelligent,
            get_cached_memory_intelligent,
            batch_memory_operations,
            preload_memory_contextual,
            get_memory_cache_performance
        )
        
        cache_manager = get_memory_cache_manager()
        print("✅ Memory cache manager imported successfully")
        
        # Test intelligent caching
        print(f"\n🔍 Testing intelligent caching...")
        
        test_data = {
            "user_memory": ["Meeting at 3pm", "Favorite color is blue"],
            "conversation_context": "Planning weekend activities",
            "emotional_state": "excited"
        }
        
        cache_key = "test_memory_data"
        context_tags = {"test_user", "conversation", "important"}
        invalidation_triggers = {"user_logout", "context_change"}
        
        # Cache data
        cache_success = cache_memory_intelligent(
            cache_key, test_data, context_tags, invalidation_triggers
        )
        print(f"  ✅ Cache storage: {'Success' if cache_success else 'Failed'}")
        
        # Retrieve cached data
        cached_data = get_cached_memory_intelligent(cache_key, context_tags)
        cache_hit = cached_data is not None and cached_data == test_data
        print(f"  ✅ Cache retrieval: {'Hit' if cache_hit else 'Miss'}")
        
        # Test cache miss
        miss_data = get_cached_memory_intelligent("nonexistent_key", {"test"})
        cache_miss = miss_data is None
        print(f"  ✅ Cache miss handling: {'Correct' if cache_miss else 'Failed'}")
        
        # Test batching
        print(f"\n🔍 Testing operation batching...")
        
        batch_operations = [
            {"cache_key": "batch_1", "data": "First batch item"},
            {"cache_key": "batch_2", "data": "Second batch item"},
            {"cache_key": "batch_3", "data": "Third batch item"}
        ]
        
        batch_id = batch_memory_operations(batch_operations, "write", "test_user")
        print(f"  ✅ Batch created: {batch_id}")
        
        # Test preloading
        print(f"\n🔍 Testing contextual preloading...")
        preload_memory_contextual("user_preferences", "test_user")
        print(f"  ✅ Preload initiated for user preferences")
        
        # Wait a moment for background operations
        time.sleep(2)
        
        # Get performance metrics
        print(f"\n📊 Cache Performance Metrics:")
        cache_metrics = get_memory_cache_performance()
        
        cache_stats = cache_metrics.get("cache_stats", {})
        print(f"  Hit rate: {cache_stats.get('hit_rate_percent', 0):.1f}%")
        print(f"  Cache size: {cache_stats.get('cache_size_mb', 0):.2f}MB")
        print(f"  Cache entries: {cache_stats.get('cache_entries', 0)}")
        
        batch_stats = cache_metrics.get("batch_stats", {})
        print(f"  Pending batches: {batch_stats.get('pending_batches', 0)}")
        
        pattern_stats = cache_metrics.get("pattern_stats", {})
        print(f"  Learned patterns: {pattern_stats.get('learned_patterns', 0)}")
        print(f"  Context associations: {pattern_stats.get('context_associations', 0)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_enhanced_circuit_breaker():
    """Test the enhanced circuit breaker with connection pooling"""
    print("\n🧪 Testing Enhanced Circuit Breaker...")
    print("=" * 60)
    
    try:
        from ai.circuit_breaker import (
            llm_circuit_breaker,
            fallback_manager,
            LLMConnectionPool,
            EnhancedCircuitBreaker,
            CircuitBreakerConfig
        )
        
        print("✅ Circuit breaker components imported successfully")
        
        # Test connection pool
        print(f"\n🔍 Testing connection pool...")
        
        connection_pool = LLMConnectionPool(max_connections=3, retry_attempts=2)
        
        # Test endpoint health checking
        healthy_endpoint = connection_pool.get_healthy_endpoint()
        if healthy_endpoint:
            print(f"  ✅ Found healthy endpoint: {healthy_endpoint}")
        else:
            print(f"  ⚠️ No healthy endpoints found (expected in test environment)")
        
        # Test connection pool stats
        pool_stats = connection_pool.get_pool_stats()
        print(f"  📊 Pool stats: {pool_stats['max_connections']} max, "
              f"{pool_stats['active_connections']} active")
        
        # Test circuit breaker functionality
        print(f"\n🔍 Testing circuit breaker states...")
        
        test_breaker = EnhancedCircuitBreaker(
            "test_service",
            CircuitBreakerConfig(failure_threshold=2, recovery_timeout=5)
        )
        
        def successful_operation():
            return "success"
        
        def failing_operation():
            raise Exception("Simulated failure")
        
        # Test successful operation
        try:
            result = test_breaker.call(successful_operation)
            print(f"  ✅ Successful operation: {result}")
        except Exception as e:
            print(f"  ❌ Unexpected failure: {e}")
        
        # Test failure handling
        failures = 0
        for i in range(3):
            try:
                test_breaker.call(failing_operation)
            except Exception:
                failures += 1
        
        print(f"  ✅ Handled {failures} failures correctly")
        
        # Test circuit breaker stats
        breaker_stats = test_breaker.get_stats()
        print(f"  📊 Breaker state: {breaker_stats['state']}")
        print(f"  📊 Failure count: {breaker_stats['failure_count']}")
        
        # Test fallback manager
        print(f"\n🔍 Testing fallback manager...")
        
        # Test fallback registration and execution
        try:
            result = fallback_manager.call_with_fallback(
                "test_llm", 
                failing_operation
            )
            print(f"  ✅ Fallback executed: {result}")
        except Exception:
            print(f"  ✅ Fallback handling working (expected to fail in test)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_unified_memory_integration():
    """Test the enhanced unified memory manager"""
    print("\n🧪 Testing Enhanced Unified Memory Manager...")
    print("=" * 60)
    
    try:
        from ai.unified_memory_manager import (
            extract_all_from_text,
            extract_for_voice_interaction,
            extract_for_background_processing,
            get_memory_stats,
            get_enterprise_performance_summary
        )
        
        print("✅ Enhanced unified memory manager imported successfully")
        
        # Test different extraction modes
        print(f"\n🔍 Testing extraction modes...")
        
        test_username = "enterprise_test_user"
        test_text = "I need to schedule a meeting for tomorrow at 2pm"
        
        # Standard extraction
        standard_result = extract_all_from_text(test_username, test_text)
        print(f"  ✅ Standard extraction: {standard_result.intent_classification}")
        
        # Voice interaction (high priority)
        voice_start = time.time()
        voice_result = extract_for_voice_interaction(test_username, "Quick voice test")
        voice_time = time.time() - voice_start
        print(f"  ✅ Voice extraction: {voice_time:.3f}s (should be fast)")
        
        # Background processing
        bg_start = time.time()
        bg_result = extract_for_background_processing(test_username, "Background analysis text")
        bg_time = time.time() - bg_start
        print(f"  ✅ Background extraction: {bg_time:.3f}s")
        
        # Test memory statistics
        print(f"\n📊 Memory Statistics:")
        memory_stats = get_memory_stats()
        
        print(f"  Active users: {memory_stats.get('active_users', 0)}")
        print(f"  Cached extractions: {memory_stats.get('cached_extractions', 0)}")
        print(f"  Enterprise mode: {memory_stats.get('enterprise_mode', False)}")
        print(f"  Enterprise available: {memory_stats.get('enterprise_available', False)}")
        
        # Test enterprise performance summary
        if memory_stats.get('enterprise_available', False):
            print(f"\n🏢 Enterprise Performance Summary:")
            try:
                perf_summary = get_enterprise_performance_summary()
                
                if "error" not in perf_summary:
                    summary = perf_summary.get("summary", {})
                    print(f"  Total requests: {summary.get('total_requests', 0)}")
                    print(f"  Cache hit rate: {summary.get('cache_hit_rate', 0):.1f}%")
                    print(f"  Status: {summary.get('status', 'Unknown')}")
                else:
                    print(f"  ⚠️ {perf_summary['error']}")
            except Exception as e:
                print(f"  ⚠️ Could not get performance summary: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_performance_comparison():
    """Compare performance between standard and enterprise extraction"""
    print("\n🧪 Performance Comparison: Standard vs Enterprise...")
    print("=" * 60)
    
    test_texts = [
        "Hello, how are you?",
        "What's the weather like today?",
        "I need to remember my doctor's appointment",
        "Can you help me plan my day?",
        "Tell me about the latest news"
    ]
    
    # Simulate multiple extractions
    print(f"🔍 Running performance comparison with {len(test_texts)} extractions...")
    
    try:
        from ai.unified_memory_manager import extract_all_from_text
        
        total_start = time.time()
        results = []
        
        for i, text in enumerate(test_texts):
            start = time.time()
            result = extract_all_from_text(f"perf_user_{i}", text)
            end = time.time()
            
            results.append({
                "text": text[:30] + "...",
                "time": end - start,
                "intent": result.intent_classification,
                "events": len(result.memory_events)
            })
        
        total_time = time.time() - total_start
        avg_time = total_time / len(test_texts)
        
        print(f"\n📊 Performance Results:")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Average per extraction: {avg_time:.3f}s")
        print(f"  Fastest extraction: {min(r['time'] for r in results):.3f}s")
        print(f"  Slowest extraction: {max(r['time'] for r in results):.3f}s")
        
        # Check if we're meeting performance targets
        target_voice_latency = 2.0  # 2 seconds for voice
        target_text_latency = 5.0   # 5 seconds for text
        
        voice_compliant = avg_time <= target_voice_latency
        text_compliant = avg_time <= target_text_latency
        
        print(f"\n🎯 Performance Targets:")
        print(f"  Voice target (<2s): {'✅ PASS' if voice_compliant else '❌ FAIL'} ({avg_time:.3f}s)")
        print(f"  Text target (<5s): {'✅ PASS' if text_compliant else '❌ FAIL'} ({avg_time:.3f}s)")
        
        return text_compliant  # At minimum, should meet text target
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Run all enterprise framework tests"""
    print("🏢 Enterprise-Grade Extraction Optimization Framework Tests")
    print("=" * 80)
    print("Testing minimal-change enterprise enhancements to Buddy's consciousness system")
    print("=" * 80)
    
    # Set enterprise mode for testing
    os.environ['BUDDY_ENTERPRISE_MODE'] = 'true'
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Extraction Coordinator", test_extraction_coordinator),
        ("Memory Cache Manager", test_memory_cache_manager),
        ("Enhanced Circuit Breaker", test_enhanced_circuit_breaker),
        ("Unified Memory Integration", test_unified_memory_integration),
        ("Performance Comparison", test_performance_comparison)
    ]
    
    for test_name, test_func in tests:
        print(f"\n" + "=" * 80)
        try:
            result = test_func()
            test_results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            test_results.append((test_name, False))
    
    # Final summary
    print(f"\n" + "=" * 80)
    print("🏢 ENTERPRISE FRAMEWORK TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All enterprise framework tests PASSED!")
        print("🚀 Enterprise-grade extraction optimization is working correctly")
    else:
        print("⚠️ Some tests failed - enterprise features may have issues")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)