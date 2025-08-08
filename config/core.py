"""
Core configuration for Buddy Voice Assistant
Handles logging, runtime mode, timezone, and startup reporting
"""
import os
from datetime import datetime
import pytz

# ==== LOGGING & DEBUG SETTINGS ====
DEBUG = True
VOICE_DEBUG_MODE = False  # Set to True when you need debug output
ENHANCED_VOICE_DEBUG = True
GAP_ANALYSIS_DEBUG = True 
PATTERN_TRACKING_DEBUG = True
ENHANCED_LOGGING = True
SIMILARITY_RANGE_DEBUG = True
RECOGNITION_CONFIDENCE_LOGGING = True

# ==== RUNTIME MODE SETTINGS ====
RUNTIME_MODE = os.getenv('BUDDY_RUNTIME_MODE', 'normal')  # normal, development, production
BLANK_SLATE_MODE = os.getenv('BUDDY_BLANK_SLATE', 'false').lower() == 'true'

# ==== TIMEZONE CONFIGURATION ====
DEFAULT_TIMEZONE = 'Australia/Brisbane'
TIMEZONE_OFFSET = '+10:00'

def get_current_time():
    """Get current time in configured timezone"""
    return datetime.now(pytz.timezone(DEFAULT_TIMEZONE))

def startup_summary():
    """Print startup summary for core configuration"""
    print(f"[Config-Core] 🚀 BUDDY CORE CONFIGURATION:")
    print(f"  Debug Mode: {DEBUG}")
    print(f"  Voice Debug: {VOICE_DEBUG_MODE}")  
    print(f"  Runtime Mode: {RUNTIME_MODE}")
    print(f"  Blank Slate Mode: {BLANK_SLATE_MODE}")
    print(f"  Timezone: {DEFAULT_TIMEZONE} ({TIMEZONE_OFFSET})")
    print(f"  Current Time: {get_current_time().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if BLANK_SLATE_MODE:
        print("[Config-Core] 🌱 BLANK SLATE MODE ENABLED - Starting with minimal identity")
    else:
        print("[Config-Core] 🧠 Standard mode - Loading established consciousness")

# Export commonly used values
CURRENT_TIMESTAMP = get_current_time().strftime("%Y-%m-%d %H:%M:%S")