#!/usr/bin/env python3
"""
Test Progressive Memory Extraction System
Tests the enhanced memory extraction with 40 edge cases to measure improvement from 22.5% to 80-90%
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.human_memory_smart import SmartHumanLikeMemory
import json

def test_progressive_memory_extraction():
    """Test the progressive memory extraction system with 40 edge cases"""
    
    # Test user
    test_user = "progressive_test_user"
    smart_memory = SmartHumanLikeMemory(test_user)
    
    # 40 Edge Cases from the original request
    test_cases = [
        "I went to McDonald's earlier today with my friends.",
        "Yesterday, I had dinner at KFC with John.",
        "I met Sarah this morning at Starbucks.",
        "I bought a new phone yesterday at the mall.",
        "We watched Oppenheimer last night at the cinema.",
        "I played basketball with Mike earlier today.",
        "My parents visited me yesterday afternoon.",
        "I finished reading \"Dune\" last night.",
        "I drove to the beach this morning.",
        "We went camping last weekend in the mountains.",
        "I attended a concert yesterday evening.",
        "I had a job interview earlier today.",
        "I cleaned my apartment yesterday morning.",
        "We had lunch at a sushi restaurant earlier today.",
        "I went grocery shopping last night.",
        "I traveled to Sydney last weekend.",
        "I had a doctor's appointment yesterday at 3 pm.",
        "I bought a new laptop today.",
        "We celebrated Anna's birthday yesterday.",
        "I watched a football match last night.",
        "I repaired my bike earlier today.",
        "I cooked spaghetti for dinner yesterday.",
        "I went jogging this morning.",
        "We visited the zoo yesterday afternoon.",
        "I tried a new Italian restaurant last night.",
        "I attended an online AI workshop yesterday.",
        "I took my dog to the vet this morning.",
        "We had a barbecue at my house yesterday.",
        "I finished a project at work earlier today.",
        "I saw Emily at the bookstore yesterday.",
        "We had a family dinner last night.",
        "I booked a flight to New York today.",
        "I watched a new episode of The Boys yesterday.",
        "I met my cousin yesterday at the park.",
        "I planted flowers in my garden this morning.",
        "I tried sushi for the first time yesterday.",
        "I'm off to my niece's birthday next week Wednesday.",
        "dentist appointment tomorrow at 3PM, really nervous about it",
        "Grabbed some food at McDonald's with friends earlier.",
        "we went to shop last night"
    ]
    
    # Additional challenging edge cases
    additional_cases = [
        "at McDonald's",  # Location only
        "with friends",   # People only  
        "nervous about tomorrow",  # Emotion + time
        "going to see my niece",   # Future + people
        "remember I told you about the dentist?",  # Memory cue + question
        "oh yeah, that restaurant",  # Conversational reference
        "was at home",  # Location context
        "met with Sarah",  # Activity + person
        "grabbed coffee",  # Simple activity
        "excited about the party"  # Emotion + event
    ]
    
    all_test_cases = test_cases + additional_cases
    
    print("🧪 TESTING PROGRESSIVE MEMORY EXTRACTION SYSTEM")
    print("=" * 60)
    print(f"Testing {len(all_test_cases)} edge cases...")
    print()
    
    extraction_results = []
    total_extracted = 0
    
    for i, test_case in enumerate(all_test_cases, 1):
        print(f"Test {i:2d}: '{test_case}'")
        
        # Test extraction
        try:
            smart_memory.extract_and_store_human_memories(test_case)
            
            # Check if any events were detected (look for events in the last extraction)
            extracted_events = smart_memory._smart_detect_events(test_case)
            
            if extracted_events:
                total_extracted += 1
                print(f"        ✅ EXTRACTED: {len(extracted_events)} events")
                for event in extracted_events:
                    print(f"           → {event.get('type', 'unknown')}: {event.get('topic', 'unknown')}")
                extraction_results.append({
                    'case': test_case,
                    'extracted': True,
                    'events': extracted_events,
                    'count': len(extracted_events)
                })
            else:
                print(f"        ❌ NOT EXTRACTED")
                extraction_results.append({
                    'case': test_case,
                    'extracted': False,
                    'events': [],
                    'count': 0
                })
        except Exception as e:
            print(f"        ⚠️ ERROR: {e}")
            extraction_results.append({
                'case': test_case,
                'extracted': False,
                'events': [],
                'count': 0,
                'error': str(e)
            })
        
        print()
    
    # Calculate results
    extraction_rate = (total_extracted / len(all_test_cases)) * 100
    
    print("📊 PROGRESSIVE MEMORY EXTRACTION RESULTS")
    print("=" * 60)
    print(f"Total test cases: {len(all_test_cases)}")
    print(f"Successfully extracted: {total_extracted}")
    print(f"Extraction rate: {extraction_rate:.1f}%")
    print()
    
    # Compare to previous 22.5% baseline
    baseline_rate = 22.5
    improvement = extraction_rate - baseline_rate
    improvement_percent = (improvement / baseline_rate) * 100 if baseline_rate > 0 else 0
    
    print(f"Previous baseline: {baseline_rate}%")
    print(f"Improvement: +{improvement:.1f}% ({improvement_percent:.1f}% relative improvement)")
    print()
    
    # Target achievement
    target_rate = 80.0
    if extraction_rate >= target_rate:
        print(f"🎯 TARGET ACHIEVED! Extraction rate {extraction_rate:.1f}% >= {target_rate}%")
    else:
        remaining = target_rate - extraction_rate
        print(f"🔄 Progress toward 80% target: {extraction_rate:.1f}% (need +{remaining:.1f}% more)")
    
    print()
    
    # Detailed breakdown by category
    print("📋 EXTRACTION BREAKDOWN BY CATEGORY:")
    print("-" * 40)
    
    categories = {
        'food_visits': ['McDonald\'s', 'KFC', 'sushi restaurant', 'Italian restaurant', 'grabbed', 'food'],
        'social_events': ['friends', 'birthday', 'visited', 'met', 'barbecue', 'dinner'],
        'appointments': ['doctor', 'dentist', 'interview', 'appointment'],
        'activities': ['shopping', 'jogging', 'concert', 'cinema', 'beach', 'camping'],
        'future_events': ['next week', 'tomorrow', 'booked', 'flight'],
        'edge_cases': ['at McDonald\'s', 'with friends', 'nervous about', 'remember']
    }
    
    for category, keywords in categories.items():
        category_extracted = 0
        category_total = 0
        
        for result in extraction_results:
            if any(keyword.lower() in result['case'].lower() for keyword in keywords):
                category_total += 1
                if result['extracted']:
                    category_extracted += 1
        
        if category_total > 0:
            category_rate = (category_extracted / category_total) * 100
            print(f"{category:15s}: {category_extracted:2d}/{category_total:2d} ({category_rate:5.1f}%)")
    
    print()
    
    # Save detailed results
    results_file = f"memory/progressive_extraction_test_results.json"
    os.makedirs("memory", exist_ok=True)
    
    detailed_results = {
        'total_cases': len(all_test_cases),
        'extracted_cases': total_extracted,
        'extraction_rate': extraction_rate,
        'baseline_rate': baseline_rate,
        'improvement': improvement,
        'target_achieved': extraction_rate >= target_rate,
        'test_results': extraction_results,
        'timestamp': smart_memory.load_memory('smart_appointments.json')  # Just to get timestamp
    }
    
    with open(results_file, 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"💾 Detailed results saved to: {results_file}")
    
    return extraction_rate, improvement

if __name__ == "__main__":
    try:
        print("🚀 Starting Progressive Memory Extraction Test...")
        print()
        
        extraction_rate, improvement = test_progressive_memory_extraction()
        
        print()
        print("✅ Test completed successfully!")
        print(f"Final extraction rate: {extraction_rate:.1f}% (improved by +{improvement:.1f}%)")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()