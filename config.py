"""
Backward-compatible config.py that re-exports from modular config system
This maintains compatibility while allowing gradual migration to new architecture
"""

# First import all modular config values
from config.core import *
from config.audio import *
from config.models import *

# Import the remaining variables that aren't yet modularized
# These will be gradually moved to appropriate modules

# ==== SYSTEM INFORMATION ====
SYSTEM_USER = "Daveydrz"

# ==== PRECISE LOCATION INTELLIGENCE ====
PRECISE_LOCATION_DETECTION_ENABLED = True
AUTO_TIMEZONE_DETECTION = True
LOCATION_CACHE_DURATION = 1800  # 30 minutes for precise location
STREET_LEVEL_ACCURACY = True
WEATHER_API_READY = True
REVERSE_GEOCODING_ENABLED = True
LOCATION_AWARENESS_IN_RESPONSES = True

# GPS location settings
GPS_LOCATION_PRIORITY = True
GPS_LOCATION_FILES = [
    'buddy_gps_location.json',
    'buddy_gps_location_birtinya.json', 
    'buddy_gps_location_2025-07-06.json'
]

# ==== LANGUAGE SETTINGS ====
DEFAULT_LANG = "en"

# ==== FILE PATHS ====
KNOWN_USERS_PATH = "voice_profiles/known_users_v2.json"
CONVERSATION_HISTORY_PATH = "conversation_history_v2.json"
CHIME_PATH = "chime.wav"

# ==== WEBSOCKET URLS ====
# Already handled in models.py: FASTER_WHISPER_WS

# ==== WAKE WORD CONFIGURATION ====  
PORCUPINE_ACCESS_KEY = "/PLJ88d4+jDeVO4zaLFaXNkr6XLgxuG7dh+6JcraqLhWQlk3AjMy9Q=="
WAKE_WORD_PATH = r"hey-buddy_en_windows_v3_0_0.ppn"

# ==== VOICE RECOGNITION SETTINGS ====
# Most moved to audio.py, but some advanced settings remain
ANONYMOUS_CLUSTERING_THRESHOLD = 0.1
CLUSTER_SIMILARITY_THRESHOLD = 0.23 
MINIMUM_CLUSTER_SIZE = 3
MAXIMUM_CLUSTER_SIZE = 25
MAXIMUM_CLUSTERS = 10
CLUSTER_UPDATE_FREQUENCY = 5
MIN_SAMPLES_FOR_CLUSTER = 2
CLUSTER_CONFIDENCE_BOOST = 0.05
CLUSTER_DECAY_RATE = 0.98
MINIMUM_CLUSTER_SIZE_FOR_CENTROID = 1

# ==== CONVERSATION FLOW ====
CONVERSATION_TURN_BASED = True
VOICE_FINGERPRINTING = False

# ==== MEMORY SYSTEM SETTINGS ====
MEMORY_EXTRACTION_ENABLED = True
MEMORY_DEBUG = True

# Foolproof voice recognition settings
SIMILARITY_GAP_THRESHOLD = 0.08
SIMILARITY_DROP_DETECTION = True
ANOMALY_PATTERN_DETECTION = True
FORCE_VERIFICATION_AFTER_DROP = True
ENHANCED_SIMILARITY_PATTERN_ANALYSIS = True
PREDICTIVE_SIMILARITY_MODELING = True
FALSE_POSITIVE_PROTECTION = True
VERIFICATION_BIAS = True

# Similarity pattern tracking
MAX_SIMILARITY_HISTORY = 20
NORMAL_RANGE_WINDOW = 10
OUTLIER_DETECTION_SIGMA = 2.0
MIN_SAMPLE_SIZE_FOR_RANGE = 5
CONFIDENCE_ADJUSTMENT_FACTOR = 0.1

# Multi-layer verification system
VERIFICATION_LAYER_1_CONFIDENCE = True
VERIFICATION_LAYER_2_GAP_ANALYSIS = True  
VERIFICATION_LAYER_3_PATTERN_ANOMALY = True
VERIFICATION_LAYER_4_RANGE_CHECK = True

# Adaptive learning settings
ADAPTIVE_THRESHOLD_LEARNING = True
PATTERN_RECOGNITION_WEIGHT = 0.3
RECENT_PATTERN_WEIGHT = 0.7

# Enhanced conversation memory settings
ENHANCED_CONVERSATION_MEMORY = True
MAX_CONVERSATION_HISTORY = 25
CONVERSATION_CONTEXT_SIZE = 10
CONVERSATION_TOPICS_TO_TRACK = 6

# Advanced AI assistant system
ADVANCED_AI_ASSISTANT = True
ALEXA_SIRI_LEVEL_INTELLIGENCE = True
ANONYMOUS_CLUSTERING_ENABLED = True
SAME_NAME_COLLISION_HANDLING = True
SPONTANEOUS_INTRODUCTION_DETECTION = True
BEHAVIORAL_VOICE_PATTERNS = True
CONTEXT_ENHANCED_RECOGNITION = True
CLUSTERING_OPTIMIZED_TRAINING = True
ANALYTICS_ENABLED = True
AUTO_MAINTENANCE_ENABLED = True

# LLM Guard System
LLM_GUARD_SYSTEM = True
BLOCK_LLM_DURING_VOICE_ID = True

# Enhanced voice system  
ENHANCED_VOICE_SYSTEM = True
MULTI_EMBEDDING_PROFILES = True
VOICE_QUALITY_ANALYSIS = True
RAW_AUDIO_STORAGE = True
SPEECHBRAIN_INTEGRATION = True
PASSIVE_VOICE_LEARNING = True
DYNAMIC_VOICE_THRESHOLDS = True
UNCERTAIN_SAMPLE_STORAGE = True

# Voice profile storage paths
VOICE_PROFILES_DIR = "voice_profiles"
RAW_AUDIO_DIR = "voice_profiles/raw_audio"
UNCERTAIN_SAMPLES_DIR = "voice_profiles/uncertain"
PROFILE_BACKUPS_DIR = "voice_profiles/backups"
ANONYMOUS_CLUSTERS_DIR = "voice_profiles/clusters"

# Enhanced training
ENHANCED_TRAINING_PHRASES = True
MAX_EMBEDDINGS_PER_USER = 15
MAX_RAW_SAMPLES_PER_USER = 10
AUTO_DISCARD_POOR_AUDIO = True
SNR_ANALYSIS_ENABLED = True
SPECTRAL_VOICE_ANALYSIS = True

# SpeechBrain settings
SPEECHBRAIN_MODEL_PATH = "models/speechbrain_ecapa"
DUAL_MODEL_WEIGHT_RESEMBLYZER = 0.6
DUAL_MODEL_WEIGHT_SPEECHBRAIN = 0.4

# Passive learning settings
PASSIVE_LEARNING_MIN_CONFIDENCE = 0.8
PASSIVE_LEARNING_UPDATE_INTERVAL = 3
PASSIVE_LEARNING_SAMPLE_LIMIT = 50

# Threshold tuning
THRESHOLD_TUNING_ENABLED = True
RECOGNITION_HISTORY_LENGTH = 50
MULTI_CANDIDATE_SCORING = True

# Analytics & monitoring
ADVANCED_ANALYTICS_ENABLED = True
VOICE_ANALYTICS_ENABLED = True
PERFORMANCE_MONITORING_ENABLED = True

# Print startup summary
print(f"[Config] 📍 FINAL ADDRESS:")
print(f"  City: {USER_LOCATION}")
print(f"  State: {USER_STATE}")  
print(f"  Postal: {USER_POSTAL_CODE}")
print(f"  Coordinates: {USER_COORDINATES}")
print(f"  Source: {LOCATION_SOURCE}")

print(f"[Config] 🚀 ADVANCED AI ASSISTANT SYSTEM:")
print(f"  🎯 Alexa/Siri-level Intelligence: {ALEXA_SIRI_LEVEL_INTELLIGENCE}")
print(f"  🔍 Anonymous Clustering: {ANONYMOUS_CLUSTERING_ENABLED}")
print(f"  🎤 Passive Audio Buffering: {PASSIVE_AUDIO_BUFFERING}")
print(f"  🛡️ LLM Guard System: {LLM_GUARD_SYSTEM}")
print(f"  👥 Same Name Collision Handling: {SAME_NAME_COLLISION_HANDLING}")
print(f"  🎭 Spontaneous Introduction: {SPONTANEOUS_INTRODUCTION_DETECTION}")
print(f"  🧠 Behavioral Pattern Learning: {BEHAVIORAL_VOICE_PATTERNS}")
print(f"  📊 Context-Aware Recognition: {CONTEXT_ENHANCED_RECOGNITION}")
print(f"  🎓 Clustering-Optimized Training: {CLUSTERING_OPTIMIZED_TRAINING}")
print(f"  📈 Voice Analytics: {VOICE_ANALYTICS_ENABLED}")
print(f"  🔧 Auto Maintenance: {AUTO_MAINTENANCE_ENABLED}")

print(f"[Config] 🎯 Enhanced Voice System: {ENHANCED_VOICE_SYSTEM}")
print(f"[Config] 📊 Multi-Embedding Profiles: {MULTI_EMBEDDING_PROFILES}")
print(f"[Config] 🔍 Voice Quality Analysis: {VOICE_QUALITY_ANALYSIS}")
print(f"[Config] 💾 Raw Audio Storage: {RAW_AUDIO_STORAGE}")
print(f"[Config] 🧠 SpeechBrain Integration: {SPEECHBRAIN_INTEGRATION}")
print(f"[Config] 🌱 Passive Learning: {PASSIVE_VOICE_LEARNING}")
print(f"[Config] 🎯 Dynamic Thresholds: {DYNAMIC_VOICE_THRESHOLDS}")
print(f"[Config] 🎓 Enhanced Training: {ENHANCED_TRAINING_PHRASES}")
print(f"[Config] 📈 Max Embeddings/User: {MAX_EMBEDDINGS_PER_USER}")
print(f"[Config] 💾 Max Raw Samples/User: {MAX_RAW_SAMPLES_PER_USER}")

print(f"[Config] 🎯 OPTIMIZED Conversation Memory: {ENHANCED_CONVERSATION_MEMORY}")
print(f"[Config] 💾 Stores: {MAX_CONVERSATION_HISTORY} exchanges")
print(f"[Config] 🧠 Uses: {CONVERSATION_CONTEXT_SIZE} exchanges for context")
print(f"[Config] 🎯 Topics: {CONVERSATION_TOPICS_TO_TRACK}")

print(f"[Config] 🧠 Memory System: {'ENABLED' if MEMORY_EXTRACTION_ENABLED else 'DISABLED'}")
print(f"[Config] ⚡ Optimized for Speed & Quality Balance")
print(f"[Config] 💾 Memory Extraction: {MEMORY_EXTRACTION_ENABLED}")
print(f"[Config] 🔍 Memory Debug: {MEMORY_DEBUG}")

print(f"[Config] ✅ ADVANCED AI ASSISTANT + PRECISE LOCATION + KOKORO-FASTAPI + SMART STREAMING LOADED")
print(f"[Config] 🕐 Current Time: {CURRENT_TIMESTAMP} (AUTO-TIME)")
print(f"[Config] 📍 Precise Location: {USER_SUBURB}, {USER_STATE} ({LOCATION_SOURCE})")
print(f"[Config] 🎯 Confidence: {LOCATION_CONFIDENCE}")
print(f"[Config] 📏 Accuracy: {LOCATION_ACCURACY} meters")
print(f"[Config] 🌡️ Weather API Ready: {WEATHER_API_READY}")
print(f"[Config] 🌏 Coordinates: {USER_COORDINATES}")
print(f"[Config] 🕰️ Timezone: {USER_TIMEZONE} ({USER_TIMEZONE_OFFSET})")
print(f"[Config] 📡 Source: {LOCATION_SOURCE}")
print(f"[Config] 🏠 GPS Priority: {GPS_LOCATION_PRIORITY}")

print(f"[Config] ✅ PRECISE LOCATION: Fully operational")
print(f"[Config] 🎯 Street-level accuracy: {STREET_LEVEL_ACCURACY}")
print(f"[Config] 🔍 Ready for weather API integration")
print(f"[Config] 📮 Postal Code: {USER_POSTAL_CODE}")

print(f"[Config] 📅 CURRENT DATE & TIME: Auto-detected Brisbane time - System properly configured")
print(f"[Config] 🚀 ADVANCED AI ASSISTANT BUDDY READY with ALEXA/SIRI-LEVEL INTELLIGENCE")