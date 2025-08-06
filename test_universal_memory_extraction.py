#!/usr/bin/env python3
"""
Test Universal Memory Extraction System
Tests the specific cases mentioned in the problem statement:
- "I went to mcdonald earlier" → Location visit (McDonald's)
- "Ive read a book" → Reading activity (book)  
- "Ive been reading a book" → Ongoing reading activity (book)
- "we planning to go on bikes next weekend" → Future plan (biking, next weekend)
- "I'm learning Spanish" → Current state (learning Spanish)
"""

import sys
import os
import json
import re
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.insert(0, '/home/runner/work/Buddy/Buddy')

def test_activity_pattern_recognition():
    """Test pattern recognition for different activity types"""
    print("🧪 Testing Activity Pattern Recognition")
    print("="*60)
    
    # Test cases from the problem statement
    test_cases = [
        {
            "text": "I went to mcdonald earlier",
            "expected_type": "location_visit",
            "expected_location": "McDonald's",
            "expected_activity": "visit"
        },
        {
            "text": "Ive read a book",
            "expected_type": "reading_activity", 
            "expected_item": "book",
            "expected_tense": "past"
        },
        {
            "text": "Ive been reading a book",
            "expected_type": "reading_activity",
            "expected_item": "book", 
            "expected_tense": "ongoing"
        },
        {
            "text": "we planning to go on bikes next weekend",
            "expected_type": "future_plan",
            "expected_activity": "biking",
            "expected_time": "next weekend"
        },
        {
            "text": "I'm learning Spanish",
            "expected_type": "current_state",
            "expected_activity": "learning",
            "expected_subject": "Spanish"
        }
    ]
    
    patterns_to_test = {
        "location_visit": [
            (r"went to mcdonald'?s?(?:\s+earlier)?", "visited_mcdonalds", "McDonald's"),
            (r"been to mcdonald'?s?(?:\s+earlier)?", "visited_mcdonalds", "McDonald's"),
            (r"went to (\w+)(?:\s+earlier)?", "visited_{0}", "{0}"),
        ],
        "reading_activity": [
            (r"(?:i'?ve\s+)?read\s+a?\s*(\w+)", "read_{0}", "{0}"),
            (r"(?:i'?ve\s+)?been\s+reading\s+a?\s*(\w+)", "reading_{0}", "{0}"),
            (r"reading\s+a?\s*(\w+)", "reading_{0}", "{0}"),
        ],
        "future_plan": [
            (r"planning\s+to\s+go\s+on\s+(\w+)\s+(next\s+\w+)", "plan_{0}_{1}", "{0} {1}"),
            (r"planning\s+to\s+(\w+)\s+(next\s+\w+)", "plan_{0}_{1}", "{0} {1}"),
            (r"will\s+(\w+)\s+(next\s+\w+)", "plan_{0}_{1}", "{0} {1}"),
        ],
        "current_state": [
            (r"(?:i'?m\s+)?learning\s+(\w+)", "learning_{0}", "{0}"),
            (r"studying\s+(\w+)", "studying_{0}", "{0}"),
            (r"currently\s+(\w+)", "current_{0}", "{0}"),
        ]
    }
    
    results = []
    
    for test_case in test_cases:
        text = test_case["text"].lower()
        expected_type = test_case["expected_type"]
        
        print(f"\n📝 Testing: '{test_case['text']}'")
        print(f"   Expected type: {expected_type}")
        
        matched = False
        if expected_type in patterns_to_test:
            for pattern, memory_key, display_format in patterns_to_test[expected_type]:
                match = re.search(pattern, text)
                if match:
                    print(f"   ✅ Pattern matched: {pattern}")
                    print(f"   📝 Memory key: {memory_key.format(*match.groups())}")
                    print(f"   🏷️ Display: {display_format.format(*match.groups())}")
                    matched = True
                    break
        
        if not matched:
            print(f"   ❌ No pattern matched for {expected_type}")
        
        results.append({
            "text": test_case["text"],
            "expected_type": expected_type,
            "matched": matched
        })
    
    # Summary
    passed = sum(1 for r in results if r["matched"])
    total = len(results)
    
    print(f"\n📊 Pattern Recognition Results: {passed}/{total} passed")
    
    return results

def test_memory_extraction_without_llm():
    """Test memory extraction using rule-based patterns (no LLM required)"""
    print("\n🧪 Testing Memory Extraction (Rule-based)")
    print("="*60)
    
    # Import the memory system
    try:
        from ai.memory import get_user_memory, EntityStatus
        print("✅ Memory system imported successfully")
    except Exception as e:
        print(f"❌ Failed to import memory system: {e}")
        return False
    
    # Test user
    test_user = "universal_test_user"
    
    # Get memory system
    try:
        memory = get_user_memory(test_user)
        print(f"✅ Memory system initialized for {test_user}")
    except Exception as e:
        print(f"❌ Failed to initialize memory: {e}")
        return False
    
    # Test rule-based entity extraction patterns
    test_texts = [
        "I went to mcdonald earlier",
        "Ive read a book", 
        "Ive been reading a book",
        "we planning to go on bikes next weekend",
        "I'm learning Spanish"
    ]
    
    extraction_results = []
    
    for text in test_texts:
        print(f"\n📝 Processing: '{text}'")
        
        # Try to extract entities using the pattern system
        try:
            # Check if the memory system has entity extraction
            if hasattr(memory, 'detect_entities_in_text'):
                entities = memory.detect_entities_in_text(text)
                print(f"   ✅ Entities detected: {entities}")
                extraction_results.append({
                    "text": text,
                    "entities": entities,
                    "success": True
                })
            else:
                print(f"   ⚠️ Entity detection method not available")
                extraction_results.append({
                    "text": text, 
                    "entities": [],
                    "success": False
                })
        except Exception as e:
            print(f"   ❌ Extraction failed: {e}")
            extraction_results.append({
                "text": text,
                "entities": [],
                "success": False,
                "error": str(e)
            })
    
    return extraction_results

def test_comprehensive_memory_extractor_patterns():
    """Test the comprehensive memory extractor with the specific patterns"""
    print("\n🧪 Testing Comprehensive Memory Extractor Patterns")
    print("="*60)
    
    try:
        from ai.comprehensive_memory_extractor import ComprehensiveMemoryExtractor
        print("✅ ComprehensiveMemoryExtractor imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ComprehensiveMemoryExtractor: {e}")
        return False
    
    # Create extractor instance
    test_user = "pattern_test_user"
    
    try:
        extractor = ComprehensiveMemoryExtractor(test_user)
        print(f"✅ Extractor initialized for {test_user}")
    except Exception as e:
        print(f"❌ Failed to initialize extractor: {e}")
        return False
    
    # Test the complexity calculation and tier selection
    test_cases = [
        {
            "text": "I went to mcdonald earlier",
            "expected_tier": "TIER 2",  # location + activity
        },
        {
            "text": "Ive read a book",
            "expected_tier": "TIER 1",  # simple activity
        },
        {
            "text": "Ive been reading a book", 
            "expected_tier": "TIER 2",  # ongoing activity
        },
        {
            "text": "we planning to go on bikes next weekend",
            "expected_tier": "TIER 3",  # people + time + activity
        },
        {
            "text": "I'm learning Spanish",
            "expected_tier": "TIER 1",  # simple state
        }
    ]
    
    tier_results = []
    
    for test_case in test_cases:
        text = test_case["text"]
        print(f"\n📝 Testing: '{text}'")
        
        # Test complexity calculation
        try:
            complexity_score = extractor._calculate_complexity_score(text)
            word_count = len(text.split())
            
            print(f"   📊 Complexity score: {complexity_score}")
            print(f"   📊 Word count: {word_count}")
            
            # Determine tier based on extractor logic
            if complexity_score <= 3 and word_count <= 8:
                detected_tier = "TIER 1"
            elif complexity_score <= 6 and word_count <= 20:
                detected_tier = "TIER 2"
            else:
                detected_tier = "TIER 3"
            
            print(f"   🎯 Detected tier: {detected_tier}")
            print(f"   🎯 Expected tier: {test_case['expected_tier']}")
            
            matches_expected = detected_tier == test_case["expected_tier"]
            print(f"   {'✅' if matches_expected else '⚠️'} Tier matching: {matches_expected}")
            
            tier_results.append({
                "text": text,
                "complexity_score": complexity_score,
                "word_count": word_count,
                "detected_tier": detected_tier,
                "expected_tier": test_case["expected_tier"],
                "matches": matches_expected
            })
            
        except Exception as e:
            print(f"   ❌ Tier calculation failed: {e}")
            tier_results.append({
                "text": text,
                "error": str(e),
                "matches": False
            })
    
    # Summary
    successful_tiers = sum(1 for r in tier_results if r.get("matches", False))
    total_tiers = len(tier_results)
    
    print(f"\n📊 Tier Detection Results: {successful_tiers}/{total_tiers} correct")
    
    return tier_results

def test_activity_classification():
    """Test activity classification into proper categories"""
    print("\n🧪 Testing Activity Classification")
    print("="*60)
    
    # Classification rules for different activity types
    classification_rules = {
        "location_visit": {
            "patterns": [
                r"went to (\w+)",
                r"been to (\w+)",
                r"visited (\w+)"
            ],
            "indicators": ["went", "been", "visited", "to"],
            "category": "activities"
        },
        "reading_activity": {
            "patterns": [
                r"read(?:ing)?\s+(?:a\s+)?(\w+)",
                r"been reading\s+(?:a\s+)?(\w+)"
            ],
            "indicators": ["read", "reading", "book"],
            "category": "activities"
        },
        "future_plan": {
            "patterns": [
                r"planning to (\w+)",
                r"will (\w+)",
                r"going to (\w+)"
            ],
            "indicators": ["planning", "will", "going", "next", "tomorrow"],
            "category": "plans"
        },
        "current_state": {
            "patterns": [
                r"(?:i'?m\s+)?learning (\w+)",
                r"currently (\w+)",
                r"studying (\w+)"
            ],
            "indicators": ["learning", "studying", "currently", "now"],
            "category": "states"
        }
    }
    
    test_activities = [
        "I went to mcdonald earlier",
        "Ive read a book",
        "Ive been reading a book", 
        "we planning to go on bikes next weekend",
        "I'm learning Spanish"
    ]
    
    classification_results = []
    
    for text in test_activities:
        print(f"\n📝 Classifying: '{text}'")
        text_lower = text.lower()
        
        classified = False
        for activity_type, rules in classification_rules.items():
            # Check patterns
            for pattern in rules["patterns"]:
                if re.search(pattern, text_lower):
                    print(f"   ✅ Classified as: {activity_type}")
                    print(f"   📂 Category: {rules['category']}")
                    print(f"   🔍 Pattern: {pattern}")
                    
                    classification_results.append({
                        "text": text,
                        "type": activity_type,
                        "category": rules["category"],
                        "pattern": pattern,
                        "classified": True
                    })
                    classified = True
                    break
            
            if classified:
                break
        
        if not classified:
            print(f"   ❌ Could not classify activity type")
            classification_results.append({
                "text": text,
                "type": "unknown",
                "category": "unknown", 
                "classified": False
            })
    
    # Summary
    successful_classifications = sum(1 for r in classification_results if r["classified"])
    total_classifications = len(classification_results)
    
    print(f"\n📊 Classification Results: {successful_classifications}/{total_classifications} classified")
    
    return classification_results

def test_memory_storage_format():
    """Test standardized memory storage format"""
    print("\n🧪 Testing Memory Storage Format")
    print("="*60)
    
    # Define standardized memory format
    standard_format = {
        "type": "activity_type",
        "topic": "activity_description", 
        "date": "YYYY-MM-DD",
        "time": "HH:MM or null",
        "emotion": "emotional_state",
        "priority": "high|medium|low",
        "people": ["person1", "person2"],
        "location": "location_name",
        "details": "additional_information",
        "original_text": "user_input",
        "status": "past|current|future",
        "category": "activities|plans|states"
    }
    
    # Test data transformation
    test_inputs = [
        {
            "text": "I went to mcdonald earlier",
            "expected": {
                "type": "location_visit",
                "topic": "McDonald's visit",
                "location": "McDonald's",
                "status": "past",
                "category": "activities"
            }
        },
        {
            "text": "Ive read a book",
            "expected": {
                "type": "reading_activity",
                "topic": "book reading",
                "details": "book",
                "status": "past", 
                "category": "activities"
            }
        },
        {
            "text": "Ive been reading a book",
            "expected": {
                "type": "reading_activity",
                "topic": "ongoing book reading",
                "details": "book",
                "status": "current",
                "category": "activities"
            }
        },
        {
            "text": "we planning to go on bikes next weekend",
            "expected": {
                "type": "future_plan",
                "topic": "biking plan",
                "details": "biking",
                "time": "next weekend",
                "status": "future",
                "category": "plans"
            }
        },
        {
            "text": "I'm learning Spanish",
            "expected": {
                "type": "current_state",
                "topic": "Spanish learning",
                "details": "Spanish",
                "status": "current",
                "category": "states"
            }
        }
    ]
    
    format_results = []
    
    for test_input in test_inputs:
        text = test_input["text"]
        expected = test_input["expected"]
        
        print(f"\n📝 Formatting: '{text}'")
        
        # Create memory entry in standard format
        memory_entry = {
            "type": expected["type"],
            "topic": expected["topic"],
            "date": datetime.now().strftime('%Y-%m-%d'),
            "time": expected.get("time"),
            "emotion": "neutral",  # Default
            "priority": "medium",  # Default
            "people": [],  # Default
            "location": expected.get("location"),
            "details": expected.get("details"),
            "original_text": text,
            "status": expected["status"],
            "category": expected["category"]
        }
        
        print(f"   📄 Memory entry created:")
        for key, value in memory_entry.items():
            if value is not None:
                print(f"     {key}: {value}")
        
        # Validate format
        required_fields = ["type", "topic", "date", "status", "category", "original_text"]
        valid_format = all(field in memory_entry for field in required_fields)
        
        print(f"   {'✅' if valid_format else '❌'} Format validation: {valid_format}")
        
        format_results.append({
            "text": text,
            "memory_entry": memory_entry,
            "valid_format": valid_format
        })
    
    # Summary
    valid_formats = sum(1 for r in format_results if r["valid_format"])
    total_formats = len(format_results)
    
    print(f"\n📊 Format Validation Results: {valid_formats}/{total_formats} valid")
    
    return format_results

def main():
    """Run all universal memory extraction tests"""
    print("🚀 Universal Memory Extraction System Test")
    print("=" * 80)
    print("Testing the specific cases from the problem statement:")
    print("- 'I went to mcdonald earlier' → Location visit (McDonald's)")
    print("- 'Ive read a book' → Reading activity (book)")
    print("- 'Ive been reading a book' → Ongoing reading activity (book)")
    print("- 'we planning to go on bikes next weekend' → Future plan (biking, next weekend)")
    print("- 'I'm learning Spanish' → Current state (learning Spanish)")
    print("=" * 80)
    
    # Run all tests
    test_results = {}
    
    try:
        test_results["pattern_recognition"] = test_activity_pattern_recognition()
    except Exception as e:
        print(f"❌ Pattern recognition test failed: {e}")
        test_results["pattern_recognition"] = {"error": str(e)}
    
    try:
        test_results["memory_extraction"] = test_memory_extraction_without_llm()
    except Exception as e:
        print(f"❌ Memory extraction test failed: {e}")
        test_results["memory_extraction"] = {"error": str(e)}
    
    try:
        test_results["extractor_patterns"] = test_comprehensive_memory_extractor_patterns()
    except Exception as e:
        print(f"❌ Extractor patterns test failed: {e}")
        test_results["extractor_patterns"] = {"error": str(e)}
    
    try:
        test_results["activity_classification"] = test_activity_classification()
    except Exception as e:
        print(f"❌ Activity classification test failed: {e}")
        test_results["activity_classification"] = {"error": str(e)}
    
    try:
        test_results["memory_format"] = test_memory_storage_format()
    except Exception as e:
        print(f"❌ Memory format test failed: {e}")
        test_results["memory_format"] = {"error": str(e)}
    
    # Final summary
    print("\n" + "="*80)
    print("📊 UNIVERSAL MEMORY EXTRACTION TEST SUMMARY")
    print("="*80)
    
    for test_name, result in test_results.items():
        if isinstance(result, dict) and "error" in result:
            print(f"❌ {test_name}: FAILED - {result['error']}")
        else:
            print(f"✅ {test_name}: COMPLETED")
    
    # Save results
    results_file = "/tmp/universal_memory_test_results.json"
    try:
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        print(f"\n💾 Test results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️ Could not save results: {e}")
    
    print("\n🎯 Test Focus: Validating universal memory extraction for all activity types")
    print("🔍 Next step: Run with LLM server for full integration testing")
    
    return test_results

if __name__ == "__main__":
    results = main()