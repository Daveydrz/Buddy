#!/usr/bin/env python3
"""
Test Extended Memory Extraction and Injection Flow
Tests if Buddy can extract and recall who they went with.
"""

import os
import sys
sys.path.append('/home/runner/work/Newbudd/Newbudd')

def test_extended_memory_flow():
    """Test memory flow with WHO and WHERE details"""
    
    print("🧠 Testing Extended Memory Flow: 'I went to McDonald's with friends yesterday'")
    print("=" * 70)
    
    try:
        from ai.memory import get_user_memory
        from ai.human_memory_smart import SmartHumanLikeMemory
        
        test_user = "test_extended_memory_user"
        print(f"👤 Test user: {test_user}")
        
        # Get memory systems
        user_memory = get_user_memory(test_user)
        smart_memory = SmartHumanLikeMemory(test_user)
        
        # Test the extended statement
        test_statement = "I went to McDonald's with friends yesterday"
        print(f"\n💬 User says: '{test_statement}'")
        print("🧠 Extracting memories...")
        
        # Extract with both systems
        user_memory.extract_memories_from_text(test_statement)
        smart_memory.extract_and_store_human_memories(test_statement)
        
        print("✅ Memory extraction completed")
        
        # Test WHERE question
        where_question = "Where did I go yesterday?"
        print(f"\n❓ User asks: '{where_question}'")
        where_memories = user_memory.retrieve_relevant_memories(where_question)
        where_context = user_memory.get_contextual_memory_for_response(where_question)
        
        print(f"📋 WHERE memories: {len(where_memories)}")
        for i, memory in enumerate(where_memories):
            print(f"  {i+1}. {memory['content']} (relevance: {memory['relevance']:.2f})")
        print(f"📝 WHERE context: '{where_context}'")
        
        # Test WITH WHO question
        who_question = "Who did I go with yesterday?"
        print(f"\n❓ User asks: '{who_question}'")
        who_memories = user_memory.retrieve_relevant_memories(who_question)
        who_context = user_memory.get_contextual_memory_for_response(who_question)
        
        print(f"📋 WHO memories: {len(who_memories)}")
        for i, memory in enumerate(who_memories):
            print(f"  {i+1}. {memory['content']} (relevance: {memory['relevance']:.2f})")
        print(f"📝 WHO context: '{who_context}'")
        
        # Test both questions together
        print("\n🔬 Flow Verification:")
        
        where_working = where_memories and len(where_memories) > 0 and any("mcdonald" in m['content'].lower() for m in where_memories)
        who_working = who_memories and len(who_memories) > 0 and any("friend" in m['content'].lower() for m in who_memories)
        
        if where_working:
            print("✅ WHERE recall: WORKING - Buddy can recall McDonald's")
        else:
            print("❌ WHERE recall: NOT WORKING - Buddy cannot recall McDonald's")
            
        if who_working:
            print("✅ WHO recall: WORKING - Buddy can recall friends")
        else:
            print("❌ WHO recall: NOT WORKING - Buddy cannot recall friends")
            
        if where_working and who_working:
            print("✅ COMPLETE FLOW: WORKING - Buddy can answer both WHERE and WHO questions!")
        elif where_working:
            print("⚠️ PARTIAL FLOW: Only WHERE working")
        elif who_working:
            print("⚠️ PARTIAL FLOW: Only WHO working")
        else:
            print("❌ COMPLETE FLOW: NOT WORKING")
            
        # Show actual memories stored
        print("\n📋 All stored memories:")
        for fact_key, fact in user_memory.personal_facts.items():
            print(f"  {fact_key}: {fact.value}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_extended_memory_flow()