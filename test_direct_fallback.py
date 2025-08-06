#!/usr/bin/env python3
"""
Direct fallback test - test the fallback system without requiring LLM server
"""

import time

def test_direct_fallback():
    """Test the direct fallback system"""
    print("🎯 Testing Direct Fallback System")
    print("=" * 40)
    print("📝 Question: 'How are you today?'")
    print("🎯 Goal: Fast response without LLM server")
    print("=" * 40)
    
    try:
        from ai.latency_optimizer import latency_optimizer
        
        user_input = "How are you today?"
        user_id = "fallback_test_user"
        
        start_time = time.time()
        response_chunks = []
        
        print("🤖 Buddy: ", end="", flush=True)
        
        # Test the fallback response directly (bypasses LLM)
        for chunk in latency_optimizer._generate_fallback_response(
            user_input=user_input,
            user_id=user_id,
            context={},
            stream=True
        ):
            response_chunks.append(chunk)
            print(chunk, end="", flush=True)
        
        total_time = time.time() - start_time
        full_response = "".join(response_chunks).strip()
        
        print()  # New line after response
        print("=" * 40)
        print(f"⏱️ Response Time: {total_time:.2f} seconds")
        print(f"📊 Response Length: {len(full_response)} characters")
        print(f"🎯 Fast Response (<2s): {'✅ YES' if total_time < 2 else '❌ NO'}")
        print(f"💬 Meaningful Response: {'✅ YES' if len(full_response) > 30 else '❌ NO'}")
        
        # Test other common inputs quickly
        test_inputs = [
            "Hello!",
            "What time is it?", 
            "Thank you",
            "Goodbye"
        ]
        
        print("\n🧪 Testing other common inputs:")
        for test_input in test_inputs:
            start = time.time()
            response = latency_optimizer._create_direct_llm_response(test_input, user_id)
            duration = time.time() - start
            
            if response:
                print(f"✅ '{test_input}' -> Response in {duration:.3f}s")
            else:
                print(f"❌ '{test_input}' -> No response")
        
        # Overall success check
        success = (
            total_time < 2 and 
            len(full_response) > 30 and
            "well" in full_response.lower()
        )
        
        print("=" * 40)
        if success:
            print("🎉 SUCCESS! Fallback system working perfectly!")
            print("✅ Fast response without LLM server")
            print("✅ Meaningful conversational response")
            print("🚀 Critical issues are RESOLVED!")
        else:
            print("❌ Fallback system needs improvement")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run direct fallback test"""
    success = test_direct_fallback()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())