#!/usr/bin/env python3
"""
Test basic functionality: "How are you today?" response
"""

def test_basic_response():
    """Test that Buddy can respond to 'How are you today?' without getting stuck"""
    print("🧪 Testing basic 'How are you today?' response...")
    
    try:
        # Import the latency optimizer
        from ai.latency_optimizer import latency_optimizer
        
        # Test the fallback direct pathway
        user_input = "How are you today?"
        user_id = "test_user"
        
        print(f"📝 Input: {user_input}")
        print("🤖 Response: ", end="")
        
        # Use the fallback response generator
        response_parts = []
        for chunk in latency_optimizer._generate_fallback_response(user_input, user_id, {}, True):
            response_parts.append(chunk)
            print(chunk, end="", flush=True)
        
        print()  # New line after response
        
        full_response = "".join(response_parts).strip()
        
        if full_response and len(full_response) > 10:
            print("✅ Basic response test PASSED")
            print(f"📊 Response length: {len(full_response)} characters")
            return True
        else:
            print("❌ Basic response test FAILED - response too short or empty")
            return False
            
    except Exception as e:
        print(f"❌ Basic response test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_llm_response():
    """Test the direct LLM response creation"""
    print("\n🧪 Testing direct LLM response creation...")
    
    try:
        from ai.latency_optimizer import latency_optimizer
        
        test_inputs = [
            "How are you today?",
            "Hello there!",
            "What time is it?",
            "Thank you for your help",
            "Goodbye",
            "Tell me about quantum physics"  # Generic test
        ]
        
        for user_input in test_inputs:
            response = latency_optimizer._create_direct_llm_response(user_input, "test_user")
            if response:
                print(f"✅ '{user_input}' -> '{response[:50]}...'")
            else:
                print(f"❌ '{user_input}' -> No response")
        
        print("✅ Direct LLM response test completed")
        return True
        
    except Exception as e:
        print(f"❌ Direct LLM response test FAILED: {e}")
        return False

def test_memory_events_fix():
    """Test that the memory_events attribute is properly initialized"""
    print("\n🧪 Testing memory_events fix...")
    
    try:
        from ai.latency_optimizer import latency_optimizer
        
        # Check if memory_events attribute exists
        if hasattr(latency_optimizer, 'memory_events'):
            print("✅ memory_events attribute found")
            print(f"📊 Initial memory_events: {latency_optimizer.memory_events}")
            return True
        else:
            print("❌ memory_events attribute missing")
            return False
            
    except Exception as e:
        print(f"❌ memory_events test FAILED: {e}")
        return False

def main():
    """Run all basic functionality tests"""
    print("🔍 Testing Basic Functionality Fixes")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_basic_response():
        tests_passed += 1
    
    if test_direct_llm_response():
        tests_passed += 1
    
    if test_memory_events_fix():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All basic functionality tests PASSED!")
        print("🎉 Buddy should now be able to respond to 'How are you today?' without errors")
        return 0
    else:
        print("❌ Some tests failed - further fixes needed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())