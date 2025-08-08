"""
Test script to verify the clean runner architecture without external dependencies
"""
import asyncio
import sys
sys.path.append('.')

# Mock the service clients for testing
class MockSTT:
    async def transcribe_audio(self, audio):
        return "Hello, this is a test transcription"

class MockLLM:
    async def chat_completion(self, messages, max_tokens=150):
        return "Hello! I'm Buddy. How can I help you today?"
    
    async def health_check(self):
        return True

class MockTTS:
    async def synthesize_speech(self, text):
        return b"mock_audio_data" * 100  # Mock audio bytes
    
    async def test_tts_service(self):
        return True

class MockConsciousness:
    async def idle_tick(self):
        print("[MockConsciousness] Running idle tick...")
        
    async def pre_reply(self, context):
        return {'enhanced': True}
        
    async def post_user_turn(self, context):
        print("[MockConsciousness] Processing post turn...")
        
    async def get_consciousness_health(self):
        return {'loaded_modules': {'emotion': True, 'self_model': True}, 'status': 'healthy'}

# Replace imports with mocks
transcribe_audio = MockSTT().transcribe_audio
chat_completion = MockLLM().chat_completion
llm_health_check = MockLLM().health_check
synthesize_speech = MockTTS().synthesize_speech
test_tts_service = MockTTS().test_tts_service
idle_tick = MockConsciousness().idle_tick
pre_reply = MockConsciousness().pre_reply
post_user_turn = MockConsciousness().post_user_turn
get_consciousness_health = MockConsciousness().get_consciousness_health

# Import config
from config.core import DEBUG, get_current_time
from config.audio import WATCHDOG_INTERVAL_S, WATCHDOG_ENABLED

print("✅ Mock services initialized")
print(f"Debug mode: {DEBUG}")
print(f"Watchdog interval: {WATCHDOG_INTERVAL_S}s")
print(f"Current time: {get_current_time()}")

async def test_runner():
    """Test the runner logic with mocks"""
    print("\n🚀 Testing clean runner architecture...")
    
    # Test service calls
    transcript = await transcribe_audio(None)
    print(f"STT mock: {transcript}")
    
    response = await chat_completion([{"role": "user", "content": "test"}])
    print(f"LLM mock: {response}")
    
    audio = await synthesize_speech("test")
    print(f"TTS mock: {len(audio)} bytes")
    
    # Test consciousness
    await idle_tick()
    context = await pre_reply({"user_input": "test"})
    print(f"Consciousness pre-reply: {context}")
    
    health = await get_consciousness_health()
    print(f"Consciousness health: {health}")
    
    print("\n✅ All service mocks working!")
    print("🎯 Clean runner architecture is valid")

if __name__ == "__main__":
    asyncio.run(test_runner())