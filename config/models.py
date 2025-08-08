"""
Model endpoints configuration for Buddy Voice Assistant
Handles Kobold LLM, Kokoro TTS, and Faster-Whisper STT endpoints and settings
"""

# ==== LLM SETTINGS (KOBOLD) ====
KOBOLD_URL = "http://localhost:5001/v1/chat/completions"
KOBOLD_TIMEOUT = 60                    # KoboldCpp connection timeout
KOBOLD_MAX_RETRIES = 3                 # Maximum connection retries  
KOBOLD_RETRY_DELAY = 2                 # Delay between retries in seconds

# ==== STT SETTINGS (FASTER-WHISPER) ====
FASTER_WHISPER_WS = "ws://localhost:9090"
WHISPER_TIMEOUT = 30                   # Whisper transcription timeout
WHISPER_MAX_RETRIES = 2                # Whisper retry attempts
WHISPER_RETRY_DELAY = 1                # Delay between Whisper retries

# ==== TTS SETTINGS (KOKORO) ====
KOKORO_API_BASE_URL = "http://127.0.0.1:8880"
KOKORO_API_TIMEOUT = 10
KOKORO_DEFAULT_VOICE = "af_heart"      # Australian female voice
KOKORO_STREAMING_ENABLED = True        # Enable streaming TTS
KOKORO_CHUNK_SIZE = 512               # Audio chunk size for streaming

# Voice mapping for different languages (FastAPI voices)
KOKORO_API_VOICES = {
    "en": "af_heart",     # Australian English (Female)
    "de": "df_bella",     # German (Female)  
    "es": "ef_sofia",     # Spanish (Female)
    "fr": "ff_emma",      # French (Female)
    "hi": "hf_aboli",     # Hindi (Female)
    "it": "if_sara",      # Italian (Female)
    "ja": "jf_rei",       # Japanese (Female)
    "ko": "kf_anna",      # Korean (Female)
    "pl": "pl_voice",     # Polish
    "pt": "pf_lara",      # Portuguese (Female)
    "ru": "rf_nova",      # Russian (Female)
    "tr": "tf_elif",      # Turkish (Female)
    "zh": "zf_lily"       # Chinese (Female)
}

# Kokoro voice parameters
KOKORO_VOICE_SPEED = 1.0               # Speech speed (0.5-2.0)
KOKORO_VOICE_STABILITY = 0.8           # Voice stability
KOKORO_VOICE_CLARITY = 0.9             # Voice clarity

# Streaming TTS Configuration
STREAMING_TTS_ENABLED = True           # Enable streaming TTS responses
STREAMING_TTS_CHUNK_SIZE = 1024       # Chunk size for streaming
STREAMING_TTS_BUFFER_SIZE = 4096      # Buffer size for streaming
STREAMING_TTS_TIMEOUT = 15            # Streaming timeout

# Legacy Kokoro settings (fallback only)
KOKORO_MODEL_PATH = "kokoro-v1.0.onnx"
KOKORO_VOICES_PATH = "voices-v1.0.bin"
KOKORO_VOICES = {"pl": "af_heart", "en": "af_heart", "it": "if_sara"}
KOKORO_LANGS = {"pl": "pl", "en": "en-us", "it": "it"}

# ==== SMART LLM STREAMING SETTINGS ====  
STREAMING_LLM_ENABLED = True           # Enable smart LLM streaming
STREAMING_LLM_CHUNK_WORDS = 8          # Wait for meaningful chunks
STREAMING_LLM_TIMEOUT = 60             # LLM streaming timeout
STREAMING_LLM_BUFFER_SIZE = 128        # Balanced buffering

# ==== SMART RESPONSE SETTINGS ====
SMART_RESPONSE_TIMING = True           # Smart response timing
RESPONSE_DELAY = 0.08                  # Response delay
TARGET_COMPLETION_PERCENTAGE = 45.0    # Target completion percentage
MIN_WORDS_FIRST_CHUNK = 8             # Min words for first chunk
COMPLETE_PHRASES_ONLY = True          # Complete phrases only
NATURAL_SPEECH_FLOW = True            # Natural speech flow
OVERLAPPED_GENERATION = True          # Overlap LLM generation with speech

# ==== SERVICE HEALTH CHECK INTERVALS ====
LLM_HEALTH_CHECK_INTERVAL = 30        # Check LLM health every 30s
TTS_HEALTH_CHECK_INTERVAL = 60        # Check TTS health every 60s  
STT_HEALTH_CHECK_INTERVAL = 45        # Check STT health every 45s

# ==== CONNECTION POOL SETTINGS ====
MAX_CONNECTIONS_PER_ENDPOINT = 5      # Max connections per service
CONNECTION_POOL_TIMEOUT = 10          # Connection pool timeout
KEEP_ALIVE_CONNECTIONS = True         # Keep connections alive

def get_default_endpoints():
    """Return dictionary of default service endpoints"""
    return {
        'llm': KOBOLD_URL,
        'tts': KOKORO_API_BASE_URL,  
        'stt': FASTER_WHISPER_WS
    }

def get_service_timeouts():
    """Return dictionary of service timeouts"""
    return {
        'llm': KOBOLD_TIMEOUT,
        'tts': KOKORO_API_TIMEOUT,
        'stt': WHISPER_TIMEOUT
    }

def get_kokoro_voice_config():
    """Return Kokoro voice configuration"""
    return {
        'default_voice': KOKORO_DEFAULT_VOICE,
        'voices': KOKORO_API_VOICES,
        'speed': KOKORO_VOICE_SPEED,
        'stability': KOKORO_VOICE_STABILITY,
        'clarity': KOKORO_VOICE_CLARITY,
        'streaming': KOKORO_STREAMING_ENABLED,
        'chunk_size': KOKORO_CHUNK_SIZE
    }

def startup_summary():
    """Print startup summary for model endpoints"""
    print(f"[Config-Models] 🤖 SERVICE ENDPOINTS:")
    print(f"  LLM (Kobold): {KOBOLD_URL}")
    print(f"  TTS (Kokoro): {KOKORO_API_BASE_URL}")
    print(f"  STT (Whisper): {FASTER_WHISPER_WS}")
    print(f"[Config-Models] 🎭 TTS CONFIGURATION:")
    print(f"  Default Voice: {KOKORO_DEFAULT_VOICE}")
    print(f"  Streaming: {KOKORO_STREAMING_ENABLED}")
    print(f"  Timeout: {KOKORO_API_TIMEOUT}s")
    print(f"  Voices Available: {len(KOKORO_API_VOICES)}")
    print(f"[Config-Models] 🧠 LLM STREAMING:")
    print(f"  Enabled: {STREAMING_LLM_ENABLED}")
    print(f"  Chunk Words: {STREAMING_LLM_CHUNK_WORDS}")
    print(f"  Timeout: {STREAMING_LLM_TIMEOUT}s")
    print(f"  Smart Timing: {SMART_RESPONSE_TIMING}")