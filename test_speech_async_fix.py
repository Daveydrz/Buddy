#!/usr/bin/env python3
"""
Test script to verify the async event loop fix for speech transcription.
This test simulates the threading scenario that was causing the error.
"""

import asyncio
import threading
import time
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_speech_async_event_loop_fix():
    """Test that speech transcription works properly in threads with event loops"""
    print("🧪 Testing async event loop fix for speech transcription...")
    
    # Mock the external dependencies
    mock_audio_data = np.array([1, 2, 3, 4, 5] * 1000, dtype=np.int16)
    
    # Test 1: Simulate the original threading scenario
    print("\n📋 Test 1: Threading scenario with no event loop")
    
    def transcribe_in_thread():
        """Simulate the transcribe_and_handle function behavior"""
        try:
            # Import the fixed function
            from ai.speech import transcribe_audio
            
            # This should now handle the event loop properly
            print("  🔧 Creating event loop in thread...")
            
            # Create a new event loop for this thread (like the fix does)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            print("  ✅ Event loop created successfully")
            
            # Mock the actual transcription call since we don't have the server
            with patch('ai.speech.whisper_stt_async') as mock_whisper:
                mock_whisper.return_value = asyncio.coroutine(lambda: "test transcription")()
                
                result = transcribe_audio(mock_audio_data)
                print(f"  📝 Transcription result: '{result}'")
                
                if result != "Audio transcription unavailable":
                    print("  ✅ Transcription succeeded!")
                    return True
                else:
                    print("  ⚠️ Transcription fell back to unavailable")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Thread transcription error: {e}")
            return False
        finally:
            # Clean up event loop
            try:
                current_loop = asyncio.get_event_loop()
                if current_loop and not current_loop.is_running():
                    current_loop.close()
            except:
                pass
    
    # Run in thread to simulate the actual scenario
    result_container = []
    test_thread = threading.Thread(
        target=lambda: result_container.append(transcribe_in_thread()),
        daemon=True
    )
    test_thread.start()
    test_thread.join(timeout=10)
    
    if result_container and result_container[0]:
        print("  ✅ Test 1 PASSED: Thread-based transcription works")
        test1_passed = True
    else:
        print("  ❌ Test 1 FAILED: Thread-based transcription failed")
        test1_passed = False
    
    # Test 2: Test the fallback mechanism
    print("\n📋 Test 2: Fallback mechanism")
    
    try:
        from ai.speech import _transcribe_audio_fallback
        
        fallback_result = _transcribe_audio_fallback(mock_audio_data)
        print(f"  📝 Fallback result: '{fallback_result}'")
        
        if fallback_result == "Audio transcription unavailable":
            print("  ✅ Test 2 PASSED: Fallback mechanism works")
            test2_passed = True
        else:
            print("  ❌ Test 2 FAILED: Unexpected fallback result")
            test2_passed = False
            
    except Exception as e:
        print(f"  ❌ Test 2 FAILED: Fallback error: {e}")
        test2_passed = False
    
    # Test 3: Test with running event loop (main thread scenario)
    print("\n📋 Test 3: Main thread with running event loop")
    
    async def test_with_running_loop():
        """Test transcription when called from within an async context"""
        try:
            from ai.speech import transcribe_audio
            
            with patch('ai.speech.whisper_stt_async') as mock_whisper:
                mock_whisper.return_value = "async test transcription"
                
                # This should use the ThreadPoolExecutor path
                result = transcribe_audio(mock_audio_data)
                print(f"  📝 Async context result: '{result}'")
                
                if result != "Audio transcription unavailable":
                    print("  ✅ Test 3 PASSED: Async context transcription works")
                    return True
                else:
                    print("  ⚠️ Async context fell back to unavailable")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Async context error: {e}")
            return False
    
    # Run the async test
    try:
        test3_result = asyncio.run(test_with_running_loop())
        test3_passed = test3_result
    except Exception as e:
        print(f"  ❌ Test 3 FAILED: Async test error: {e}")
        test3_passed = False
    
    # Summary
    print(f"\n📊 Test Results Summary:")
    print(f"  Test 1 (Threading): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  Test 2 (Fallback): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"  Test 3 (Async Context): {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("🎉 The async event loop fix should resolve the speech transcription issue!")
    else:
        print("⚠️ There may still be issues with the speech transcription fix.")
    
    return all_passed

if __name__ == "__main__":
    test_speech_async_event_loop_fix()