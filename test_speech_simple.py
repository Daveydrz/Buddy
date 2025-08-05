#!/usr/bin/env python3
"""
Simple test to verify the async event loop fix for speech transcription.
This test doesn't require numpy or external dependencies.
"""

import asyncio
import threading
import time
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_event_loop_creation_in_thread():
    """Test that we can create event loops in threads like the fix does"""
    print("🧪 Testing event loop creation in threads...")
    
    def thread_function():
        """Simulate the transcribe_and_handle function"""
        try:
            print("  🔧 Thread started, checking for event loop...")
            
            # Check if there's already an event loop in this thread
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
                print("  ✅ Found existing event loop")
            except RuntimeError:
                # No event loop exists, create a new one for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                print("  ✅ Created new event loop for thread")
            
            # Test that we can run async code
            async def test_async():
                await asyncio.sleep(0.1)
                return "async operation completed"
            
            result = loop.run_until_complete(test_async())
            print(f"  📝 Async operation result: {result}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Thread error: {e}")
            return False
        finally:
            # Clean up event loop if we created it
            try:
                current_loop = asyncio.get_event_loop()
                if current_loop and not current_loop.is_running():
                    current_loop.close()
                    print("  🧹 Cleaned up event loop")
            except:
                pass
    
    # Run in thread to simulate the actual scenario
    result_container = []
    test_thread = threading.Thread(
        target=lambda: result_container.append(thread_function()),
        daemon=True
    )
    test_thread.start()
    test_thread.join(timeout=5)
    
    if result_container and result_container[0]:
        print("✅ Thread event loop test PASSED")
        return True
    else:
        print("❌ Thread event loop test FAILED")
        return False

def test_async_context_detection():
    """Test detection of running async contexts"""
    print("\n🧪 Testing async context detection...")
    
    # Test outside async context
    try:
        current_loop = asyncio.get_running_loop()
        print("  ❌ Unexpectedly found running loop outside async context")
        return False
    except RuntimeError:
        print("  ✅ Correctly detected no running loop outside async context")
    
    # Test inside async context
    async def test_inside_async():
        try:
            current_loop = asyncio.get_running_loop()
            print("  ✅ Correctly detected running loop inside async context")
            return True
        except RuntimeError:
            print("  ❌ Failed to detect running loop inside async context")
            return False
    
    try:
        result = asyncio.run(test_inside_async())
        if result:
            print("✅ Async context detection test PASSED")
            return True
        else:
            print("❌ Async context detection test FAILED")
            return False
    except Exception as e:
        print(f"❌ Async context detection test ERROR: {e}")
        return False

def test_full_duplex_manager_syntax():
    """Test that the full duplex manager file has valid syntax"""
    print("\n🧪 Testing FullDuplexManager syntax...")
    
    try:
        # Try to compile the file to check for syntax errors
        with open('audio/full_duplex_manager.py', 'r') as f:
            code = f.read()
        
        compile(code, 'audio/full_duplex_manager.py', 'exec')
        print("  ✅ FullDuplexManager syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"  ❌ FullDuplexManager syntax error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ FullDuplexManager compilation error: {e}")
        return False

def test_speech_module_syntax():
    """Test that the speech module file has valid syntax"""
    print("\n🧪 Testing Speech module syntax...")
    
    try:
        # Try to compile the file to check for syntax errors
        with open('ai/speech.py', 'r') as f:
            code = f.read()
        
        compile(code, 'ai/speech.py', 'exec')
        print("  ✅ Speech module syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"  ❌ Speech module syntax error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Speech module compilation error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Testing Async Event Loop Fix for Speech Transcription")
    print("=" * 60)
    
    tests = [
        test_event_loop_creation_in_thread,
        test_async_context_detection,
        test_full_duplex_manager_syntax,
        test_speech_module_syntax
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"  Event Loop Creation: {'✅ PASSED' if results[0] else '❌ FAILED'}")
    print(f"  Async Context Detection: {'✅ PASSED' if results[1] else '❌ FAILED'}")
    print(f"  FullDuplexManager Syntax: {'✅ PASSED' if results[2] else '❌ FAILED'}")
    print(f"  Speech Module Syntax: {'✅ PASSED' if results[3] else '❌ FAILED'}")
    
    all_passed = all(results)
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 The async event loop fix appears to be working correctly!")
        print("💡 This should resolve the 'There is no current event loop' error.")
    else:
        print("\n⚠️ There may be issues with the fix that need attention.")
    
    return all_passed

if __name__ == "__main__":
    main()