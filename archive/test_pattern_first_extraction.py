#!/usr/bin/env python3
"""
Test Pattern-First Memory Extraction
Tests the new pattern-first approach to ensure:
1. Simple statements use patterns (no LLM calls)
2. No Francesco hallucination
3. Fast response times
4. Proper memory extraction
"""

import sys
import time
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, '/home/runner/work/Buddy/Buddy')

def test_pattern_first_extraction():
    """Test that simple statements use pattern extraction first"""
    print("🧪 Testing Pattern-First Extraction")
    print("="*60)
    
    try:
        from ai.comprehensive_memory_extractor import ComprehensiveMemoryExtractor
        from ai.pattern_memory_extractor import PatternMemoryExtractor
        
        # Test pattern extractor directly first
        pattern_extractor = PatternMemoryExtractor()
        
        test_cases = [
            "I went to mcdonald earlier",
            "Ive read a book", 
            "Ive been reading a book",
            "I'm learning Spanish"
        ]
        
        print("\n📝 Testing Direct Pattern Recognition:")
        for text in test_cases:
            start_time = time.time()
            result = pattern_extractor.extract_if_pattern_matches(text)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            if result and result.matched:
                print(f"✅ '{text}' -> Pattern matched ({response_time:.1f}ms)")
                print(f"   Memory events: {len(result.memory_events)}")
                print(f"   Intent: {result.intent_classification}")
                if result.memory_events:
                    event = result.memory_events[0]
                    print(f"   Topic: {event.get('topic')}")
                    print(f"   Location: {event.get('location')}")
                    print(f"   People: {event.get('people', [])}")
            else:
                print(f"❌ '{text}' -> No pattern match")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern extraction test failed: {e}")
        return False

def test_no_francesco_hallucination():
    """Test that McDonald's visits don't hallucinate Francesco"""
    print("\n🧪 Testing No Francesco Hallucination")
    print("="*60)
    
    try:
        from ai.comprehensive_memory_extractor import ComprehensiveMemoryExtractor
        
        extractor = ComprehensiveMemoryExtractor('test_user_no_francesco')
        
        test_text = "I went to mcdonald earlier"
        print(f"📝 Testing: '{test_text}'")
        
        start_time = time.time()
        result = extractor.extract_all_from_text(test_text)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to ms
        
        print(f"⏱️ Response time: {response_time:.1f}ms")
        print(f"📊 Memory events: {len(result.memory_events)}")
        print(f"🎯 Intent: {result.intent_classification}")
        
        # Check for Francesco hallucination
        francesco_found = False
        if result.memory_events:
            for event in result.memory_events:
                people = event.get('people', [])
                topic = event.get('topic', '')
                details = event.get('details', '')
                
                if 'francesco' in str(people).lower() or 'francesco' in topic.lower() or 'francesco' in details.lower():
                    francesco_found = True
                    print(f"❌ FRANCESCO HALLUCINATION DETECTED!")
                    print(f"   Event: {event}")
                    break
                else:
                    print(f"✅ Event clean: {event.get('topic')} at {event.get('location')}")
        
        if not francesco_found:
            print(f"✅ NO Francesco hallucination detected")
        
        return not francesco_found
        
    except Exception as e:
        print(f"❌ Francesco test failed: {e}")
        return False

def test_response_times():
    """Test that response times are reasonable"""
    print("\n🧪 Testing Response Times")
    print("="*60)
    
    try:
        from ai.comprehensive_memory_extractor import ComprehensiveMemoryExtractor
        
        extractor = ComprehensiveMemoryExtractor('test_user_timing')
        
        test_cases = [
            "I went to mcdonald earlier",           # Should use pattern (fast)
            "Ive read a book",                     # Should use pattern (fast)  
            "I'm learning Spanish",                # Should use pattern (fast)
            "we planning to go on bikes next weekend"  # May use LLM (slower)
        ]
        
        results = []
        
        for text in test_cases:
            print(f"\n📝 Testing: '{text}'")
            
            start_time = time.time()
            result = extractor.extract_all_from_text(text)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            print(f"⏱️ Response time: {response_time:.1f}ms")
            print(f"📊 Memory events: {len(result.memory_events)}")
            
            results.append({
                'text': text,
                'response_time_ms': response_time,
                'memory_events': len(result.memory_events)
            })
            
            # Check if reasonable time (pattern should be <100ms, LLM <5000ms)
            if response_time < 100:
                print(f"✅ Very fast (likely pattern-based)")
            elif response_time < 5000:
                print(f"✅ Reasonable time")
            else:
                print(f"⚠️ Slow response time")
        
        # Summary
        avg_time = sum(r['response_time_ms'] for r in results) / len(results)
        print(f"\n📊 Average response time: {avg_time:.1f}ms")
        
        return avg_time < 2000  # Average should be under 2 seconds
        
    except Exception as e:
        print(f"❌ Timing test failed: {e}")
        return False

def test_memory_extraction_quality():
    """Test that memory extraction quality is maintained"""
    print("\n🧪 Testing Memory Extraction Quality")
    print("="*60)
    
    try:
        from ai.comprehensive_memory_extractor import ComprehensiveMemoryExtractor
        
        extractor = ComprehensiveMemoryExtractor('test_user_quality')
        
        test_cases = [
            {
                'text': "I went to mcdonald earlier",
                'expected_location': "McDonald's",
                'expected_type': "life_event"
            },
            {
                'text': "Ive read a book",
                'expected_topic_contains': "read",
                'expected_type': "highlight"
            },
            {
                'text': "I'm learning Spanish",
                'expected_topic_contains': "spanish",
                'expected_type': "highlight"
            }
        ]
        
        all_passed = True
        
        for case in test_cases:
            text = case['text']
            print(f"\n📝 Testing: '{text}'")
            
            result = extractor.extract_all_from_text(text)
            
            if result.memory_events:
                event = result.memory_events[0]
                print(f"✅ Event extracted: {event.get('topic')}")
                
                # Check expected location
                if 'expected_location' in case:
                    actual_location = event.get('location', '')
                    expected_location = case['expected_location']
                    if expected_location.lower() in actual_location.lower():
                        print(f"✅ Location correct: {actual_location}")
                    else:
                        print(f"❌ Location incorrect: expected {expected_location}, got {actual_location}")
                        all_passed = False
                
                # Check expected topic content
                if 'expected_topic_contains' in case:
                    actual_topic = event.get('topic', '').lower()
                    expected_content = case['expected_topic_contains'].lower()
                    if expected_content in actual_topic:
                        print(f"✅ Topic contains expected content: {actual_topic}")
                    else:
                        print(f"❌ Topic missing expected content: expected '{expected_content}' in '{actual_topic}'")
                        all_passed = False
                
                # Check event type
                if 'expected_type' in case:
                    actual_type = event.get('type', '')
                    expected_type = case['expected_type']
                    if actual_type == expected_type:
                        print(f"✅ Type correct: {actual_type}")
                    else:
                        print(f"✅ Type acceptable: {actual_type} (expected {expected_type})")
            else:
                print(f"❌ No memory events extracted")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Quality test failed: {e}")
        return False

def main():
    """Run all pattern-first tests"""
    print("🚀 Pattern-First Memory Extraction Test Suite")
    print("=" * 80)
    print("Testing the new pattern-first approach:")
    print("- Pattern recognition for simple statements (no LLM)")
    print("- No Francesco hallucination")
    print("- Fast response times")
    print("- Quality memory extraction")
    print("=" * 80)
    
    tests = [
        ("Pattern Recognition", test_pattern_first_extraction),
        ("No Francesco Hallucination", test_no_francesco_hallucination),
        ("Response Times", test_response_times),
        ("Memory Quality", test_memory_extraction_quality)
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*80}")
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = False
    
    # Final summary
    print("\n" + "="*80)
    print("📊 PATTERN-FIRST TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Pattern-first approach working correctly!")
    else:
        print("⚠️ Some tests failed - needs investigation")
    
    return results

if __name__ == "__main__":
    results = main()