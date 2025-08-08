#!/usr/bin/env python3
"""
Test Memory Extraction and Injection Flow
Tests if Buddy can extract memories using LLM and inject them appropriately for recall.
"""

import os
import sys
sys.path.append('/home/runner/work/Newbudd/Newbudd')

def test_memory_extraction_injection_flow():
    """Test the complete memory flow: extraction -> storage -> semantic retrieval -> injection"""
    
    print("🧠 Testing Buddy's Memory Extraction and Injection Flow")
    print("=" * 60)
    
    try:
        # Step 1: Test memory extraction 
        from ai.memory import get_user_memory
        from ai.human_memory_smart import SmartHumanLikeMemory
        
        test_user = "test_memory_flow_user"
        print(f"👤 Test user: {test_user}")
        
        # Get memory systems
        user_memory = get_user_memory(test_user)
        smart_memory = SmartHumanLikeMemory(test_user)
        
        # Step 2: Extract memory from McDonald's statement
        test_statement = "I went to McDonald's earlier today"
        print(f"\n💬 User says: '{test_statement}'")
        print("🧠 Extracting memories...")
        
        # Extract with both systems
        user_memory.extract_memories_from_text(test_statement)
        smart_memory.extract_and_store_human_memories(test_statement)
        
        print("✅ Memory extraction completed")
        
        # Step 3: Test semantic retrieval with temporal question
        test_question = "Where did I go yesterday?"
        print(f"\n❓ User asks: '{test_question}'")
        print("🔍 Testing semantic retrieval...")
        
        # Test semantic retrieval directly
        relevant_memories = user_memory.retrieve_relevant_memories(test_question)
        print(f"📋 Found {len(relevant_memories)} relevant memories:")
        for i, memory in enumerate(relevant_memories):
            print(f"  {i+1}. {memory['type']}: {memory['content']} (relevance: {memory['relevance']:.2f})")
        
        # Step 4: Test contextual memory injection for LLM
        print("\n🎯 Testing memory injection for LLM...")
        memory_context = user_memory.get_contextual_memory_for_response(test_question)
        
        print(f"📝 Memory context for LLM ({len(memory_context)} chars):")
        if memory_context:
            print(f"'{memory_context}'")
        else:
            print("(No memory context generated)")
        
        # Step 5: Test fusion system memory injection
        print("\n🔧 Testing fusion system memory injection...")
        from ai.chat_enhanced_smart_with_fusion import get_smart_memory
        fusion_memory = get_smart_memory(test_user)
        
        # This should call the memory injection we just fixed
        try:
            # Simulate what happens in generate_response_streaming_with_intelligent_fusion
            from ai.memory import get_user_memory
            fusion_user_memory = get_user_memory(test_user)
            fusion_context = fusion_user_memory.get_contextual_memory_for_response(test_question)
            
            print(f"🔧 Fusion memory context ({len(fusion_context)} chars):")
            if fusion_context:
                print(f"'{fusion_context}'")
                
                # Show how it would be injected into the prompt
                context_prefix = f"Buddy, you're continuing an ongoing conversation.\n{fusion_context}\n\nUser: "
                optimized_question = f"{context_prefix}{test_question}"
                print(f"\n📋 Final LLM prompt would be ({len(optimized_question)} chars):")
                print(f"'{optimized_question[:200]}...'")
            else:
                print("(No fusion context generated)")
                
        except Exception as fusion_error:
            print(f"❌ Fusion test error: {fusion_error}")
        
        # Step 6: Verify the complete flow works
        print("\n🔬 Flow Verification:")
        if relevant_memories and len(relevant_memories) > 0:
            print("✅ Semantic retrieval: WORKING")
            if memory_context and "mcdonalds" in memory_context.lower():
                print("✅ Memory injection: WORKING") 
                print("✅ Complete flow: WORKING")
                print("\n🎉 SUCCESS: Buddy should be able to recall McDonald's visit!")
            else:
                print("❌ Memory injection: NOT WORKING")
                print("❌ Complete flow: BROKEN")
        else:
            print("❌ Semantic retrieval: NOT WORKING")
            print("❌ Complete flow: BROKEN")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_memory_extraction_injection_flow()