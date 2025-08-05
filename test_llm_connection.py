#!/usr/bin/env python3
"""
Test LLM Connection - Verify the LLM server is running and responding
"""

import requests
import json
import time

def test_llm_server():
    """Test if the LLM server at localhost:5001 is working"""
    
    print("🔍 Testing LLM Server Connection...")
    print("="*50)
    
    # Test 1: Check if server is running
    try:
        print("📡 Testing server connectivity...")
        response = requests.get("http://localhost:5001/v1/models", timeout=5)
        
        if response.status_code == 200:
            print("✅ LLM server is responding!")
            models = response.json()
            print(f"📋 Available models: {json.dumps(models, indent=2)}")
        else:
            print(f"⚠️ Server responded with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ LLM SERVER IS NOT RUNNING!")
        print()
        print("💡 To fix this, start your LLM server:")
        print("   Option 1 (vLLM):")
        print("   python -m vllm.entrypoints.openai.api_server --model microsoft/DialoGPT-medium --host 0.0.0.0 --port 5001")
        print()
        print("   Option 2 (Ollama):")
        print("   ollama serve")
        print("   # Then in another terminal:")
        print("   ollama run llama2  # or your preferred model")
        print()
        print("   Option 3 (Text Generation WebUI):")
        print("   python server.py --api --listen --port 5001")
        print()
        return False
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    
    # Test 2: Try a simple chat completion
    try:
        print()
        print("🧠 Testing chat completion...")
        
        test_payload = {
            "model": "default",  # This should work with most servers
            "messages": [
                {"role": "user", "content": "Hello! This is a connection test."}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        
        response = requests.post(
            "http://localhost:5001/v1/chat/completions",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                reply = result['choices'][0]['message']['content']
                print(f"✅ LLM responded: '{reply.strip()}'")
                print("🎉 LLM server is working correctly!")
                return True
            else:
                print(f"⚠️ Unexpected response format: {result}")
                return False
        else:
            print(f"❌ Chat completion failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat completion test failed: {e}")
        return False

def test_whisper_to_llm_flow():
    """Test the complete Whisper -> LLM flow"""
    
    print()
    print("🔄 Testing Whisper to LLM Flow...")
    print("="*50)
    
    try:
        # Test LLM handler import
        print("📦 Testing LLM handler import...")
        from ai.llm_handler import process_user_input_with_consciousness, generate_consciousness_integrated_response
        print("✅ LLM handler imported successfully")
        
        # Test user input processing
        print("🧠 Testing user input processing...")
        test_text = "Hello, can you hear me?"
        test_user = "test_user"
        
        analysis = process_user_input_with_consciousness(test_text, test_user)
        print(f"✅ Input analysis completed: {type(analysis)}")
        
        # Test response generation
        print("💬 Testing response generation...")
        response_gen = generate_consciousness_integrated_response(test_text, test_user)
        
        print("🎯 Attempting to get first response chunk...")
        first_chunk = next(response_gen)
        
        if first_chunk and first_chunk.strip():
            print(f"✅ LLM generated response: '{first_chunk.strip()[:100]}...'")
            print("🎉 Complete Whisper -> LLM flow is working!")
            return True
        else:
            print("❌ LLM returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 LLM Connection Test for Buddy Voice Assistant")
    print("="*60)
    
    # Test LLM server
    server_ok = test_llm_server()
    
    if server_ok:
        # Test complete flow
        flow_ok = test_whisper_to_llm_flow()
        
        if flow_ok:
            print()
            print("🎉 ALL TESTS PASSED!")
            print("✅ Your LLM server is working correctly")
            print("✅ Buddy should be able to process voice input and respond")
            print()
            print("💡 You can now run main.py - speech recognition should work!")
        else:
            print()
            print("⚠️ LLM server is running but flow test failed")
            print("Check the error messages above for details")
    else:
        print()
        print("❌ LLM server is not running or not responding correctly")
        print("Please start your LLM server first, then run this test again")
    
    print()
    print("="*60)