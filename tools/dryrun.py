#!/usr/bin/env python3
"""
Dry Run Tool - Test Buddy without microphone
Sends test prompts to LLM, calls TTS, and reports results
"""

import asyncio
import sys
import time
import os
from typing import Dict, Any

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock numpy for systems without it
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ numpy not available - using mock implementation")

async def test_llm_service():
    """Test LLM service connection and response"""
    print("\n🤖 Testing LLM Service (Kobold)...")
    
    try:
        from llm import chat_completion, health_check
        
        # Health check first
        healthy = await health_check()
        print(f"   Health Check: {'✅ Healthy' if healthy else '❌ Unhealthy'}")
        
        if not healthy:
            print("   ⚠️ LLM service not available - skipping response test")
            return False
        
        # Test chat completion
        messages = [
            {"role": "system", "content": "You are Buddy, a helpful AI assistant. Respond briefly."},
            {"role": "user", "content": "Hello, this is a test. Please respond with a short greeting."}
        ]
        
        print("   Sending test prompt...")
        start_time = time.time()
        
        response = await chat_completion(messages, max_tokens=50)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response and response.strip():
            print(f"   ✅ Response ({response_time:.2f}s): {response[:100]}...")
            return True
        else:
            print("   ❌ Empty or no response received")
            return False
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def test_tts_service():
    """Test TTS service connection and synthesis"""
    print("\n🎵 Testing TTS Service (Kokoro)...")
    
    try:
        from tts import synthesize_speech, test_tts_service, get_voice_for_language
        
        # Health check first
        healthy = await test_tts_service()
        print(f"   Health Check: {'✅ Healthy' if healthy else '❌ Unhealthy'}")
        
        if not healthy:
            print("   ⚠️ TTS service not available - skipping synthesis test")
            return False
        
        # Test voice selection
        voice = get_voice_for_language('en')
        print(f"   Voice for English: {voice}")
        
        # Test speech synthesis
        test_text = "Hello, this is a test of the text to speech system."
        print(f"   Synthesizing: '{test_text}'")
        
        start_time = time.time()
        audio_bytes = await synthesize_speech(test_text)
        end_time = time.time()
        
        synthesis_time = end_time - start_time
        
        if audio_bytes and len(audio_bytes) > 0:
            print(f"   ✅ Synthesis ({synthesis_time:.2f}s): {len(audio_bytes)} bytes generated")
            return True
        else:
            print("   ❌ No audio data generated")
            return False
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def test_stt_service():
    """Test STT service connection (without actual audio)"""
    print("\n📝 Testing STT Service (Whisper)...")
    
    try:
        # We can't test STT without actual audio and numpy
        if not NUMPY_AVAILABLE:
            print("   ⚠️ numpy not available - cannot test STT with mock audio")
            return False
            
        from stt import transcribe_audio
        import numpy as np
        
        # Create test audio (1 second of silence)
        test_audio = np.array([0] * 16000, dtype=np.int16)
        print("   Testing with 1 second of silence...")
        
        start_time = time.time()
        transcript = await transcribe_audio(test_audio)
        end_time = time.time()
        
        transcription_time = end_time - start_time
        
        if transcript is not None:
            print(f"   ✅ Transcription ({transcription_time:.2f}s): '{transcript}'")
            return True
        else:
            print("   ❌ No transcription received")
            return False
            
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def test_consciousness_service():
    """Test consciousness facade"""
    print("\n🧠 Testing Consciousness Service...")
    
    try:
        from services import get_consciousness_health, idle_tick, pre_reply
        
        # Health check
        health = await get_consciousness_health()
        print(f"   Health Check: {health}")
        
        # Test idle tick
        print("   Running idle tick...")
        await idle_tick()
        print("   ✅ Idle tick completed")
        
        # Test context enhancement
        test_context = {"user_input": "Hello"}
        enhanced = await pre_reply(test_context)
        print(f"   Context enhancement: {enhanced}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def test_configuration():
    """Test configuration system"""
    print("\n⚙️ Testing Configuration System...")
    
    try:
        from config.models import get_default_endpoints, get_service_timeouts, get_kokoro_voice_config
        from config.core import startup_summary as core_startup
        from config.audio import startup_summary as audio_startup
        
        endpoints = get_default_endpoints()
        timeouts = get_service_timeouts()
        voice_config = get_kokoro_voice_config()
        
        print("   ✅ Service Endpoints:")
        for service, endpoint in endpoints.items():
            timeout = timeouts.get(service, 'N/A')
            print(f"     {service.upper()}: {endpoint} (timeout: {timeout}s)")
        
        print(f"   ✅ Voice Config: {voice_config['default_voice']} ({len(voice_config['voices'])} voices)")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def main():
    """Main dry run test"""
    print("🧪 BUDDY DRY RUN TOOL")
    print("=" * 50)
    print("Testing Buddy services without microphone input")
    
    results = {}
    
    # Test all services
    results['config'] = await test_configuration()
    results['consciousness'] = await test_consciousness_service()
    results['llm'] = await test_llm_service()
    results['tts'] = await test_tts_service()
    results['stt'] = await test_stt_service()
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 DRY RUN SUMMARY")
    print("=" * 50)
    
    for service, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {service.upper():<15}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All systems operational!")
        return 0
    else:
        print("⚠️ Some systems need attention")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Dry run interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Dry run failed: {e}")
        sys.exit(1)