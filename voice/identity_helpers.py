# voice/identity_helpers.py - Voice-based identity helper functions
from voice.database import known_users, get_voice_display_name

def debug_voice_identity_status():
    """Debug voice identity status"""
    try:
        from voice.database import known_users, anonymous_clusters
        print(f"[VoiceIdentity] 📊 Debug Status:")
        print(f"[VoiceIdentity] 👥 Known users: {len(known_users)}")
        print(f"[VoiceIdentity] 🔍 Anonymous clusters: {len(anonymous_clusters)}")
        return True
    except Exception as e:
        print(f"[VoiceIdentity] ❌ Debug error: {e}")
        return False

def run_maintenance():
    """Run voice system maintenance"""
    try:
        print(f"[VoiceIdentity] 🔧 Running maintenance...")
        # Add any maintenance tasks here
        return True
    except Exception as e:
        print(f"[VoiceIdentity] ❌ Maintenance error: {e}")
        return False

def get_voice_based_identity(audio_data=None):
    """Get identity from voice recognition, not system login"""
    try:
        if audio_data is None:
            return "Anonymous_Speaker"
        
        # Try smart voice recognition first
        try:
            from voice.smart_voice_recognition import smart_voice_recognition
            result = smart_voice_recognition.recognize_speaker(audio_data)
            
            if result['status'] == 'recognized':
                return result['username']
        except ImportError:
            pass
        
        # Fallback to enhanced recognition
        try:
            from voice.recognition import identify_speaker_with_confidence
            identified_user, confidence = identify_speaker_with_confidence(audio_data)
            
            if identified_user != "UNKNOWN" and confidence > 0.7:
                return identified_user
        except ImportError:
            pass
        
        return "Anonymous_Speaker"
        
    except Exception as e:
        print(f"[VoiceIdentity] ❌ Error: {e}")
        return "Anonymous_Speaker"

def get_voice_based_display_name(identified_user):
    """Get display name based on voice identity, not system login"""
    try:
        # Check if this is the system user (Daveydrz)
        if identified_user == "Daveydrz" or identified_user == "SYSTEM_USER":
            return "Daveydrz"
        
        # Check known voice profiles
        if identified_user in known_users:
            profile = known_users[identified_user]
            if isinstance(profile, dict) and 'display_name' in profile:
                return profile['display_name']
            elif isinstance(profile, dict) and 'real_name' in profile:
                return profile['real_name']
            else:
                return identified_user
        
        # Handle anonymous or unknown users
        if identified_user in ["Anonymous_Speaker", "Unknown", "Guest"]:
            return "friend"  # Friendly generic term
        
        # Default to the identified name
        return identified_user
        
    except Exception as e:
        print(f"[VoiceIdentity] ⚠️ Display name error: {e}")
        return identified_user or "friend"

def update_voice_identity_context(identified_user):
    """
    📌 Update voice identity context in the system.
    Called when a new user is identified from voice.
    """
    try:
        from voice.manager_context import update_current_user_context
        update_current_user_context(identified_user)
        print(f"[VoiceIdentity] 🔄 Context updated for: {identified_user}")
    except ImportError as e:
        print(f"[VoiceIdentity] ⚠️ Failed to update context: {e}")

def get_voice_based_name_response(identified_user, display_name):
    """Handle 'what's my name' using voice matching, not system login"""
    try:
        # Handle system user
        if identified_user == "Daveydrz" or identified_user == "SYSTEM_USER":
            return f"Based on your voice, you are Daveydrz."
        
        # Handle known voice profiles
        elif identified_user in known_users and identified_user not in ["Anonymous_Speaker", "Unknown", "Guest"]:
            return f"Your name is {display_name}."
        
        # Handle anonymous or unrecognized voices
        elif identified_user in ["Anonymous_Speaker", "Unknown", "Guest"]:
            return "I don't recognize your voice yet. Could you tell me your name so I can learn it?"
        
        # Handle any other identified users
        else:
            return f"Based on your voice, I believe you are {display_name}."
            
    except Exception as e:
        print(f"[VoiceIdentity] ❌ Name response error: {e}")
        return "I'm having trouble with voice recognition right now. Could you tell me your name?"