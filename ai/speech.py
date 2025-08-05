# ai/speech.py - Speech-to-text processing
import asyncio
import json
import numpy as np
import websockets
from config import FASTER_WHISPER_WS, DEBUG
import re
import os
from datetime import datetime

async def whisper_stt_async(audio):
    """Transcribe audio using Whisper WebSocket"""
    try:
        if audio.dtype != np.int16:
            if np.issubdtype(audio.dtype, np.floating):
                audio = (audio * 32767).clip(-32768, 32767).astype(np.int16)
            else:
                audio = audio.astype(np.int16)
        
        async with websockets.connect(FASTER_WHISPER_WS, ping_interval=None) as ws:
            await ws.send(audio.tobytes())
            await ws.send("end")
            
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=15)
            except asyncio.TimeoutError:
                print("[Buddy V2] Whisper timeout")
                return ""
            
            try:
                data = json.loads(message)
                text = data.get("text", "").strip()
                if DEBUG:
                    print(f"[Buddy V2] 📝 Whisper: '{text}'")
                return text
            except:
                text = message.decode("utf-8") if isinstance(message, bytes) else message
                if DEBUG:
                    print(f"[Buddy V2] 📝 Whisper: '{text}'")
                return text.strip()
                
    except Exception as e:
        print(f"[Buddy V2] Whisper error: {e}")
        return ""

def extract_spoken_name(text: str, system_username: str) -> str:
    """Extract the user's actual spoken name using KoboldCPP intelligence"""
    
    try:
        # Try to import the ultra-intelligent name manager
        from voice.manager_names import UltraIntelligentNameManager
        
        # Create instance
        name_manager = UltraIntelligentNameManager()
        
        # Use the smart extraction
        if name_manager.is_ultra_intelligent_spontaneous_introduction(text):
            extracted_name = name_manager.extract_name_mega_intelligent(text)
            
            if extracted_name:
                # Don't use system usernames as spoken names
                if extracted_name.lower() != system_username.lower():
                    print(f"[Speech] ✅ KoboldCPP extracted: {extracted_name}")
                    return extracted_name
                else:
                    print(f"[Speech] ⚠️ Extracted name matches system username: {extracted_name}")
                    return None
            else:
                print(f"[Speech] 🛡️ KoboldCPP blocked: '{text}'")
                return None
        else:
            print(f"[Speech] 🛡️ Not an introduction: '{text}'")
            return None
            
    except ImportError:
        print(f"[Speech] ⚠️ KoboldCPP name manager not available, using fallback")
        return extract_spoken_name_fallback(text, system_username)
    except Exception as e:
        print(f"[Speech] ❌ KoboldCPP error: {e}, using fallback")
        return extract_spoken_name_fallback(text, system_username)

def extract_spoken_name_fallback(text: str, system_username: str) -> str:
    """Fallback name extraction with better validation"""
    
    # More restrictive patterns that require explicit introduction
    name_patterns = [
        r"my\s+name\s+is\s+([a-zA-Z]+)",      # "My name is David"
        r"call\s+me\s+([a-zA-Z]+)",           # "Call me David"
        r"you\s+can\s+call\s+me\s+([a-zA-Z]+)", # "You can call me David"
        r"people\s+call\s+me\s+([a-zA-Z]+)",  # "People call me David"
        # Removed the problematic "i'm\s+([a-zA-Z]+)" pattern
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text.lower())
        if match:
            spoken_name = match.group(1).capitalize()
            
            # Additional validation
            if is_valid_name_candidate(spoken_name, system_username):
                return spoken_name
    
    return None

def is_valid_name_candidate(name: str, system_username: str) -> bool:
    """Validate if extracted name is actually a name"""
    
    if not name or len(name) < 2:
        return False
    
    # Don't use system usernames as spoken names
    if name.lower() == system_username.lower():
        return False
    
    # Block common false positives
    false_positives = {
        'great', 'good', 'fine', 'okay', 'well', 'bad', 'tired', 'busy',
        'ready', 'sorry', 'happy', 'sad', 'angry', 'excited', 'confused',
        'here', 'there', 'home', 'work', 'back', 'away', 'done', 'going',
        'doing', 'working', 'thinking', 'checking', 'testing', 'trying'
    }
    
    if name.lower() in false_positives:
        print(f"[Speech] 🛡️ Blocked false positive: {name}")
        return False
    
    return True

def set_primary_identity(system_username: str, spoken_name: str):
    """Map system username to spoken name"""
    
    identity_file = f"memory/{system_username}/primary_identity.json"
    os.makedirs(f"memory/{system_username}", exist_ok=True)
    
    identity_data = {
        "system_username": system_username,
        "spoken_name": spoken_name,
        "display_name": spoken_name,
        "created_date": datetime.now().isoformat()
    }
    
    with open(identity_file, 'w') as f:
        json.dump(identity_data, f, indent=2)
    
    print(f"[Identity] Set primary identity: {system_username} → {spoken_name}")

def get_display_name(system_username: str) -> str:
    """Get the user's preferred display name"""
    
    identity_file = f"memory/{system_username}/primary_identity.json"
    
    if os.path.exists(identity_file):
        with open(identity_file, 'r') as f:
            identity = json.load(f)
            return identity.get("spoken_name", system_username)
    
    return system_username

def identify_user(spoken_input: str, system_username: str) -> str:
    """Identify user and prevent duplicates with enhanced intelligence"""
    
    # Check if user introduced themselves using KoboldCPP
    spoken_name = extract_spoken_name(spoken_input, system_username)
    
    if spoken_name:
        # Set or update their primary identity
        set_primary_identity(system_username, spoken_name)
        print(f"[Identity] User identified as: {spoken_name} (system: {system_username})")
    else:
        # Debug: Show what was blocked
        print(f"[Identity] No name introduction detected in: '{spoken_input}'")
    
    # Always return the system username for memory storage
    # But display the spoken name in responses
    return system_username

def transcribe_audio(audio):
    """Synchronous wrapper for Whisper STT"""
    return asyncio.run(whisper_stt_async(audio))