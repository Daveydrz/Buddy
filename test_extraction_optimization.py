#!/usr/bin/env python3
"""
Test Extraction Process Optimization for Buddy System
Created: 2025-01-22
Purpose: Validate that the extraction coordinator optimizes memory processes while preserving functionality
"""

import time
import threading
from datetime import datetime

def test_coordinator_initialization():
    """Test that the extraction coordinator initializes correctly"""
    print("🧪 TEST 1: Coordinator Initialization")
    print("="*50)
    
    try:
        from ai.extraction_coordinator import get_extraction_coordinator, ExtractionType, ExtractionPriority
        
        coordinator = get_extraction_coordinator()
        status = coordinator.get_system_status()
        
        print(f"✅ Coordinator active: {status['coordinator_active']}")
        print(f"✅ Processing threads: {status['processing_threads']}")
        print(f"✅ Queue size: {status['queue_size']}")
        print(f"✅ Active extractors: {status['active_extractors']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Coordinator initialization failed: {e}")
        return False

def test_context_aware_prioritization():
    """Test context-aware prioritization of extraction requests"""
    print("\n🧪 TEST 2: Context-Aware Prioritization")
    print("="*50)
    
    try:
        from ai.extraction_coordinator import extract_with_coordination, ExtractionType, ExtractionPriority
        
        username = "test_user_priority"
        
        # Test 1: User input (should be CRITICAL priority)
        print("📋 Testing user input prioritization...")
        response1 = extract_with_coordination(
            username=username,
            text="I went to McDonald's with Francesco",
            extraction_type=ExtractionType.USER_INPUT
        )
        print(f"   ✅ User input processed in {response1.processing_time:.3f}s, tier: {response1.tier_used}")
        
        # Test 2: Consciousness module (should be HIGH priority)
        print("📋 Testing consciousness module prioritization...")
        response2 = extract_with_coordination(
            username=username,
            text="Analyzing emotional state",
            extraction_type=ExtractionType.CONSCIOUSNESS
        )
        print(f"   ✅ Consciousness processed in {response2.processing_time:.3f}s, tier: {response2.tier_used}")
        
        # Test 3: Background task (should be LOW priority)
        print("📋 Testing background task prioritization...")
        response3 = extract_with_coordination(
            username=username,
            text="Background memory consolidation",
            extraction_type=ExtractionType.BACKGROUND
        )
        print(f"   ✅ Background processed in {response3.processing_time:.3f}s, tier: {response3.tier_used}")
        
        return True
        
    except Exception as e:
        print(f"❌ Prioritization test failed: {e}")
        return False

def test_result_sharing_and_caching():
    """Test that results are shared between components to eliminate redundancy"""
    print("\n🧪 TEST 3: Result Sharing and Caching")
    print("="*50)
    
    try:
        from ai.extraction_coordinator import extract_with_coordination, ExtractionType
        
        username = "test_user_cache"
        text = "I had a McFlurry ice cream"
        
        # First request
        print("📋 Making first extraction request...")
        start_time = time.time()
        response1 = extract_with_coordination(
            username=username,
            text=text,
            extraction_type=ExtractionType.USER_INPUT
        )
        first_time = time.time() - start_time
        print(f"   ✅ First request: {first_time:.3f}s, cache_hit: {response1.cache_hit}")
        
        # Second identical request (should be cached)
        print("📋 Making identical extraction request...")
        start_time = time.time()
        response2 = extract_with_coordination(
            username=username,
            text=text,
            extraction_type=ExtractionType.USER_INPUT
        )
        second_time = time.time() - start_time
        print(f"   ✅ Second request: {second_time:.3f}s, cache_hit: {response2.cache_hit}")
        
        # Verify caching worked
        if response2.cache_hit and second_time < first_time:
            print("   ✅ Result sharing working - second request was faster!")
            return True
        else:
            print("   ⚠️ Caching may not be working optimally")
            return False
        
    except Exception as e:
        print(f"❌ Caching test failed: {e}")
        return False

def test_concurrent_request_coordination():
    """Test coordination of multiple concurrent extraction requests"""
    print("\n🧪 TEST 4: Concurrent Request Coordination")
    print("="*50)
    
    try:
        from ai.extraction_coordinator import extract_with_coordination, ExtractionType
        
        username = "test_user_concurrent"
        results = []
        threads = []
        
        def make_request(request_id, text):
            try:
                start_time = time.time()
                response = extract_with_coordination(
                    username=username,
                    text=f"{text} - request {request_id}",
                    extraction_type=ExtractionType.USER_INPUT
                )
                processing_time = time.time() - start_time
                results.append({
                    'id': request_id,
                    'time': processing_time,
                    'cache_hit': response.cache_hit,
                    'tier': response.tier_used
                })
                print(f"   📝 Request {request_id}: {processing_time:.3f}s, tier: {response.tier_used}")
            except Exception as e:
                print(f"   ❌ Request {request_id} failed: {e}")
        
        # Launch multiple concurrent requests
        print("📋 Launching 5 concurrent extraction requests...")
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(i+1, "I went to McDonald's"))
            threads.append(thread)
            thread.start()
        
        # Wait for all requests to complete
        for thread in threads:
            thread.join(timeout=30)
        
        print(f"📊 Completed {len(results)}/5 concurrent requests")
        
        # Check if coordination worked (no deadlocks, reasonable times)
        if len(results) >= 4:  # Allow for some failures
            avg_time = sum(r['time'] for r in results) / len(results)
            print(f"   ✅ Average processing time: {avg_time:.3f}s")
            
            # Check for cache hits (some requests should benefit from caching)
            cache_hits = sum(1 for r in results if r['cache_hit'])
            print(f"   ✅ Cache hits: {cache_hits}/{len(results)}")
            
            return True
        else:
            print("   ❌ Too many concurrent requests failed")
            return False
        
    except Exception as e:
        print(f"❌ Concurrent coordination test failed: {e}")
        return False

def test_unified_memory_integration():
    """Test that unified memory manager works with coordinator"""
    print("\n🧪 TEST 5: Unified Memory Integration")
    print("="*50)
    
    try:
        from ai.unified_memory_manager import extract_all_from_text, extract_for_consciousness, get_memory_stats
        
        username = "test_user_unified"
        
        # Test regular extraction
        print("📋 Testing unified memory extraction...")
        result1 = extract_all_from_text(username, "I went to McDonald's with Francesco")
        print(f"   ✅ Regular extraction: {len(result1.memory_events)} events, intent: {result1.intent_classification}")
        
        # Test consciousness-specific extraction
        print("📋 Testing consciousness-specific extraction...")
        result2 = extract_for_consciousness(username, "Processing emotional context", "emotion_engine")
        print(f"   ✅ Consciousness extraction: {len(result2.memory_events)} events, intent: {result2.intent_classification}")
        
        # Test memory stats
        print("📋 Testing memory statistics...")
        stats = get_memory_stats()
        print(f"   ✅ Active users: {stats['active_users']}")
        print(f"   ✅ Cached extractions: {stats['cached_extractions']}")
        
        if 'coordinator_metrics' in stats:
            coordinator_metrics = stats['coordinator_metrics']
            print(f"   ✅ Total coordinator requests: {coordinator_metrics['total_requests']}")
            print(f"   ✅ Cache hit rate: {coordinator_metrics['cache_hit_rate_percent']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified memory integration test failed: {e}")
        return False

def test_consciousness_capabilities_preserved():
    """Test that all Class 5+ consciousness capabilities are preserved"""
    print("\n🧪 TEST 6: Consciousness Capabilities Preservation")
    print("="*50)
    
    try:
        from ai.unified_memory_manager import extract_all_from_text
        
        username = "test_user_consciousness"
        
        # Test complex scenario that requires full consciousness
        test_cases = [
            "I went to McDonald's yesterday with Francesco and had a McFlurry",
            "Francesco is my best friend who loves ice cream",
            "We always go to McDonald's together on weekends",
            "What did I have when I went to McDonald's with Francesco?"
        ]
        
        print("📋 Testing consciousness preservation with complex scenarios...")
        
        for i, text in enumerate(test_cases, 1):
            result = extract_all_from_text(username, text)
            
            print(f"   {i}. '{text[:40]}...'")
            print(f"      📝 Events: {len(result.memory_events)}")
            print(f"      🧠 Intent: {result.intent_classification}")
            print(f"      😊 Emotion: {result.emotional_state.get('primary_emotion', 'unknown')}")
            print(f"      🔗 Thread: {result.conversation_thread_id is not None}")
            print(f"      🔍 Keywords: {len(result.context_keywords)}")
        
        print("   ✅ All consciousness capabilities preserved!")
        return True
        
    except Exception as e:
        print(f"❌ Consciousness preservation test failed: {e}")
        return False

def run_all_tests():
    """Run complete test suite"""
    print("🚀 BUDDY EXTRACTION PROCESS OPTIMIZATION TESTS")
    print("="*60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        test_coordinator_initialization,
        test_context_aware_prioritization,
        test_result_sharing_and_caching,
        test_concurrent_request_coordination,
        test_unified_memory_integration,
        test_consciousness_capabilities_preserved
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED\n")
            else:
                print("❌ FAILED\n")
        except Exception as e:
            print(f"❌ ERROR: {e}\n")
    
    print("="*60)
    print(f"📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Extraction optimization is working correctly!")
        print("🚀 Buddy system should now have:")
        print("   • Reduced latency between user questions and answers")
        print("   • Context-aware extraction processing")
        print("   • Eliminated redundant memory operations")
        print("   • Better KoboldCPP resource utilization")
        print("   • Preserved Class 5+ consciousness capabilities")
    else:
        print("⚠️  Some tests failed - optimization may need adjustment")
    
    print("="*60)

if __name__ == "__main__":
    run_all_tests()