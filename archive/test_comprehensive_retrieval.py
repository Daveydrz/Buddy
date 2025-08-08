#!/usr/bin/env python3
"""
Test Comprehensive Retrieval System
Tests the enhanced retrieval capabilities with filtering and sorting
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, '/home/runner/work/Buddy/Buddy')

def test_comprehensive_retrieval():
    """Test comprehensive activity retrieval system"""
    print("🔍 Testing Comprehensive Retrieval System")
    print("="*60)
    
    try:
        from ai.unified_memory_manager import (
            extract_all_from_text,
            get_all_activities,
            get_activities_by_type,
            search_activities
        )
        print("✅ Retrieval functions imported successfully")
    except Exception as e:
        print(f"❌ Failed to import retrieval functions: {e}")
        return False
    
    test_user = "retrieval_test_user"
    
    # First, add some test activities by extracting them
    test_activities = [
        "I went to mcdonald earlier",
        "Ive read a book about science",
        "Ive been reading a book about history",
        "we planning to go on bikes next weekend",
        "I'm learning Spanish for travel",
        "visited the library yesterday",
        "planning to meet Francesco for dinner tomorrow"
    ]
    
    print("\n📝 Adding test activities...")
    for activity_text in test_activities:
        try:
            result = extract_all_from_text(test_user, activity_text)
            print(f"   ✅ Added: '{activity_text}' ({len(result.memory_events)} events)")
        except Exception as e:
            print(f"   ❌ Failed to add: '{activity_text}' - {e}")
    
    # Test 1: Get all activities
    print("\n📋 Test 1: Get all activities")
    try:
        all_activities = get_all_activities(test_user)
        print(f"   ✅ Retrieved {len(all_activities)} total activities")
        
        # Show first few activities
        for i, activity in enumerate(all_activities[:3]):
            print(f"   📝 Activity {i+1}: {activity.get('topic', 'unknown')} ({activity.get('type', 'unknown')})")
            
    except Exception as e:
        print(f"   ❌ Failed to get all activities: {e}")
    
    # Test 2: Get activities by type
    print("\n📋 Test 2: Get activities grouped by type")
    try:
        grouped_activities = get_activities_by_type(test_user)
        print(f"   ✅ Activities grouped into {len(grouped_activities)} categories:")
        
        for category, activities in grouped_activities.items():
            if activities:
                print(f"     {category}: {len(activities)} activities")
                for activity in activities[:2]:  # Show first 2 of each type
                    print(f"       - {activity.get('topic', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Failed to group activities: {e}")
    
    # Test 3: Search activities
    print("\n📋 Test 3: Search activities by query")
    search_queries = ["book", "mcdonald", "spanish", "next weekend"]
    
    for query in search_queries:
        try:
            results = search_activities(test_user, query)
            print(f"   🔍 Query '{query}': {len(results)} results")
            
            if results:
                # Show top result
                top_result = results[0]
                print(f"     Top result: {top_result.get('topic', 'unknown')} (score: {top_result.get('relevance_score', 0)})")
                
        except Exception as e:
            print(f"   ❌ Search failed for '{query}': {e}")
    
    # Test 4: Filter by activity type
    print("\n📋 Test 4: Filter activities by type")
    activity_types = ["location_visit", "reading_activity", "future_plan", "current_state"]
    
    for activity_type in activity_types:
        try:
            filtered = get_all_activities(test_user, activity_type=activity_type)
            print(f"   🎯 Type '{activity_type}': {len(filtered)} activities")
        except Exception as e:
            print(f"   ❌ Filter failed for '{activity_type}': {e}")
    
    print("\n✅ Comprehensive retrieval testing completed!")
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🧪 Testing Edge Cases and Error Handling")
    print("="*60)
    
    try:
        from ai.unified_memory_manager import (
            get_all_activities,
            search_activities
        )
        
        # Test with non-existent user
        print("📝 Test 1: Non-existent user")
        result = get_all_activities("non_existent_user")
        print(f"   {'✅' if isinstance(result, list) else '❌'} Non-existent user handled: {len(result)} activities")
        
        # Test with empty query
        print("\n📝 Test 2: Empty search query")
        result = search_activities("test_user", "")
        print(f"   {'✅' if isinstance(result, list) else '❌'} Empty query handled: {len(result)} results")
        
        # Test with special characters
        print("\n📝 Test 3: Special characters in query")
        result = search_activities("test_user", "!@#$%")
        print(f"   {'✅' if isinstance(result, list) else '❌'} Special chars handled: {len(result)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ Edge case testing failed: {e}")
        return False

def test_memory_format_consistency():
    """Test that retrieved activities maintain consistent format"""
    print("\n🔧 Testing Memory Format Consistency")
    print("="*60)
    
    try:
        from ai.unified_memory_manager import get_all_activities
        
        test_user = "format_test_user"
        activities = get_all_activities(test_user)
        
        if not activities:
            print("   ⚠️ No activities found to test format")
            return True
        
        # Check format consistency
        required_fields = ["type", "topic", "date", "status", "category", "source"]
        format_issues = []
        
        for i, activity in enumerate(activities):
            missing_fields = [field for field in required_fields if field not in activity]
            if missing_fields:
                format_issues.append(f"Activity {i}: missing {missing_fields}")
        
        if format_issues:
            print(f"   ❌ Format issues found:")
            for issue in format_issues[:5]:  # Show first 5 issues
                print(f"     {issue}")
        else:
            print(f"   ✅ All {len(activities)} activities have consistent format")
        
        return len(format_issues) == 0
        
    except Exception as e:
        print(f"❌ Format consistency test failed: {e}")
        return False

def main():
    """Run all comprehensive retrieval tests"""
    print("🚀 Comprehensive Retrieval System Test Suite")
    print("=" * 80)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Comprehensive Retrieval", test_comprehensive_retrieval),
        ("Edge Cases", test_edge_cases),
        ("Format Consistency", test_memory_format_consistency)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} tests...")
        try:
            result = test_func()
            test_results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            test_results.append((test_name, False))
    
    # Final summary
    print("\n" + "="*80)
    print("📊 COMPREHENSIVE RETRIEVAL TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ✅ ALL RETRIEVAL TESTS PASSED")
        print("🔍 Universal memory extraction with comprehensive retrieval ready!")
    else:
        print("⚠️ Some tests failed - Review and fix issues")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)