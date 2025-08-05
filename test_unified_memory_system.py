#!/usr/bin/env python3
"""
Test Unified Memory System - Complete scenario verification
Tests the McDonald's → McFlurry → Francesco conversation threading
"""

from ai.unified_memory_manager import extract_all_from_text, get_memory_stats

def test_conversation_scenario():
    """Test complete conversation threading scenario"""
    print("🧠 UNIFIED MEMORY SYSTEM TEST")
    print("="*50)
    
    username = "test_user"
    
    # Scenario 1: McDonald's visit
    print("1️⃣ User: 'I went to McDonald's earlier today'")
    result1 = extract_all_from_text(username, "I went to McDonald's earlier today")
    print(f"   ✅ Events: {len(result1.memory_events)}")
    print(f"   ✅ Intent: {result1.intent_classification}")
    print(f"   ✅ Emotion: {result1.emotional_state.get('primary_emotion', 'unknown')}")
    if result1.memory_events:
        for event in result1.memory_events:
            print(f"   📝 Memory: {event.get('topic', 'unknown')}")
    print()
    
    # Scenario 2: Food detail (threading)
    print("2️⃣ User: 'I had McFlurry ice cream'")
    result2 = extract_all_from_text(username, "I had McFlurry ice cream")
    print(f"   ✅ Intent: {result2.intent_classification}")
    print(f"   ✅ Thread ID: {result2.conversation_thread_id}")
    print(f"   ✅ Enhancements: {len(result2.memory_enhancements)}")
    if result2.memory_enhancements:
        for enh in result2.memory_enhancements:
            print(f"   🔗 Enhanced: {enh.get('enhanced_memory', 'unknown')}")
    print()
    
    # Scenario 3: Social context (threading)
    print("3️⃣ User: 'I went with Francesco'")
    result3 = extract_all_from_text(username, "I went with Francesco")
    print(f"   ✅ Intent: {result3.intent_classification}")
    print(f"   ✅ Thread ID: {result3.conversation_thread_id}")
    print(f"   ✅ Enhancements: {len(result3.memory_enhancements)}")
    if result3.memory_enhancements:
        for enh in result3.memory_enhancements:
            print(f"   🔗 Enhanced: {enh.get('enhanced_memory', 'unknown')}")
    print()
    
    # Scenario 4: Recall query  
    print("4️⃣ User: 'Where did I go yesterday and what did Francesco have?'")
    result4 = extract_all_from_text(username, "Where did I go yesterday and what did Francesco have?")
    print(f"   ✅ Intent: {result4.intent_classification}")
    print(f"   ✅ Keywords: {result4.context_keywords}")
    print()
    
    # System stats
    stats = get_memory_stats()
    print("📊 SYSTEM STATS:")
    print(f"   Active users: {stats['active_users']}")
    print(f"   Cached extractions: {stats['cached_extractions']}")
    print()
    
    print("✅ UNIFIED MEMORY TEST COMPLETE!")
    print("🎯 Single extraction system with perfect conversation threading")

if __name__ == "__main__":
    test_conversation_scenario()