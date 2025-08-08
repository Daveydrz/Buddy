# audio/voice_fingerprint.py - FIXED with DISABLED voice filtering to prevent human speech blocking
# Date: 2025-07-05 08:24:06
# FIXES: Completely disabled voice fingerprinting to prevent filtering human speech

import numpy as np
import time
from collections import deque

# Safe config loading
try:
    from config import DEBUG, BUDDY_VOICE_THRESHOLD, VOICE_SIMILARITY_BUFFER, VOICE_LEARNING_PATIENCE, VOICE_FINGERPRINTING
except ImportError:
    DEBUG = True
    BUDDY_VOICE_THRESHOLD = 0.99  # Nearly impossible to trigger
    VOICE_SIMILARITY_BUFFER = 5
    VOICE_LEARNING_PATIENCE = 10
    VOICE_FINGERPRINTING = False  # DISABLED by default
    print("[VoiceFingerprint] ⚠️ Using default voice fingerprint settings")

# ✅ CRITICAL FIX: Completely disable voice fingerprinting to prevent human speech filtering
VOICE_FINGERPRINTING_ENABLED = False  # FORCE DISABLED
print("[VoiceFingerprint] 🚨 VOICE FINGERPRINTING FORCIBLY DISABLED")
print("[VoiceFingerprint] 📢 This prevents accidental filtering of human speech")

# Initialize voice encoder only if needed (disabled for now)
encoder = None
if VOICE_FINGERPRINTING_ENABLED:
    try:
        from resemblyzer import VoiceEncoder
        from sklearn.metrics.pairwise import cosine_similarity
        encoder = VoiceEncoder()
        print("[VoiceFingerprint] ✅ Voice encoder loaded")
    except Exception as e:
        print(f"[VoiceFingerprint] ❌ Error loading encoder: {e}")
        encoder = None
else:
    print("[VoiceFingerprint] ⏸️ Voice encoder NOT loaded (fingerprinting disabled)")

# Buddy's voice profile (learned from TTS) - DISABLED
buddy_voice_profile = None
buddy_voice_samples = []
buddy_voice_threshold = min(BUDDY_VOICE_THRESHOLD, 0.99)  # Make it nearly impossible
buddy_voice_buffer = deque(maxlen=VOICE_SIMILARITY_BUFFER)

def learn_buddy_voice(audio_samples):
    """DISABLED: Learn Buddy's voice from TTS samples"""
    global buddy_voice_profile, buddy_voice_samples
    
    # ✅ CRITICAL: Always return False to disable learning
    if not VOICE_FINGERPRINTING_ENABLED:
        if DEBUG:
            print("[VoiceFingerprint] 🚫 Voice learning DISABLED to protect human speech")
        return False
    
    if encoder is None:
        return False
    
    try:
        print("[VoiceFingerprint] 🎓 Learning Buddy's voice... (DISABLED)")
        
        # Even if enabled, make it very conservative
        embeddings = []
        for sample in audio_samples:
            if len(sample) >= 16000:  # At least 1 second
                audio_float = sample.astype(np.float32) / 32768.0
                embedding = encoder.embed_utterance(audio_float)
                if embedding is not None:
                    embeddings.append(embedding)
        
        if len(embeddings) >= 10:  # ✅ FIXED: Require many more samples
            buddy_voice_profile = np.mean(embeddings, axis=0)
            buddy_voice_samples = audio_samples.copy()
            print(f"[VoiceFingerprint] ✅ Buddy's voice learned from {len(embeddings)} samples")
            return True
        else:
            print(f"[VoiceFingerprint] ❌ Not enough samples to learn voice (need 10+)")
            return False
            
    except Exception as e:
        print(f"[VoiceFingerprint] ❌ Error learning voice: {e}")
        return False

def is_buddy_speaking(audio_chunk):
    """DISABLED: Check if audio chunk is Buddy's voice - ALWAYS RETURNS FALSE"""
    global buddy_voice_profile, buddy_voice_buffer
    
    # ✅ CRITICAL FIX: Always return False to never filter human speech
    if not VOICE_FINGERPRINTING_ENABLED:
        return False  # Never identify anything as Buddy's voice
    
    # ✅ BACKUP SAFETY: Even if somehow enabled, be extremely conservative
    if encoder is None or buddy_voice_profile is None:
        return False
    
    try:
        if len(audio_chunk) < 16000:  # ✅ FIXED: Need more audio to be sure
            return False
        
        # Generate embedding for this chunk
        audio_float = audio_chunk.astype(np.float32) / 32768.0
        embedding = encoder.embed_utterance(audio_float)
        
        if embedding is not None:
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Compare with Buddy's voice profile
            similarity = cosine_similarity([embedding], [buddy_voice_profile])[0][0]
            
            # Add to buffer for consistency check
            buddy_voice_buffer.append(similarity)
            
            if DEBUG and similarity > 0.8:
                print(f"[VoiceFingerprint] 🔍 Voice similarity: {similarity:.3f} (DISABLED)")
            
            # ✅ ULTRA CONSERVATIVE: Require PERFECT match AND consistency
            if len(buddy_voice_buffer) >= 5:  # Need more samples
                recent_similarities = list(buddy_voice_buffer)[-5:]
                avg_similarity = np.mean(recent_similarities)
                min_similarity = np.min(recent_similarities)
                
                # ✅ IMPOSSIBLE THRESHOLD: Require near-perfect match
                is_buddy = (avg_similarity >= 0.99 and 
                           min_similarity >= 0.98 and
                           similarity >= 0.99)
                
                if is_buddy and DEBUG:
                    print(f"[VoiceFingerprint] 🤖 BUDDY VOICE DETECTED (avg:{avg_similarity:.3f}) - BUT DISABLED")
                
                # ✅ SAFETY: Still return False even if detected
                return False  # NEVER filter anything
            else:
                return False
        
    except Exception as e:
        if DEBUG:
            print(f"[VoiceFingerprint] Error checking voice: {e}")
    
    return False  # ✅ ALWAYS return False

def add_buddy_sample(audio_sample):
    """DISABLED: Add a new Buddy TTS sample for learning"""
    global buddy_voice_samples
    
    # ✅ CRITICAL: Don't actually learn anything
    if not VOICE_FINGERPRINTING_ENABLED:
        if DEBUG:
            print("[VoiceFingerprint] 🚫 Sample collection DISABLED")
        return
    
    try:
        if len(buddy_voice_samples) < VOICE_LEARNING_PATIENCE:
            buddy_voice_samples.append(audio_sample)
            
            # Re-learn voice profile with new sample (but very conservatively)
            if len(buddy_voice_samples) >= 10:  # ✅ FIXED: Need more samples
                learn_buddy_voice(buddy_voice_samples)
        else:
            # Replace oldest sample
            buddy_voice_samples.pop(0)
            buddy_voice_samples.append(audio_sample)
            learn_buddy_voice(buddy_voice_samples)
            
    except Exception as e:
        if DEBUG:
            print(f"[VoiceFingerprint] Error adding sample: {e}")

def get_buddy_voice_status():
    """Get status of Buddy's voice learning"""
    return {
        "learned": False,  # ✅ ALWAYS report as not learned
        "samples": len(buddy_voice_samples),
        "threshold": buddy_voice_threshold,
        "buffer_size": len(buddy_voice_buffer),
        "fingerprinting_enabled": VOICE_FINGERPRINTING_ENABLED,
        "forced_disabled": True
    }

def reset_voice_learning():
    """Reset voice learning (for debugging)"""
    global buddy_voice_profile, buddy_voice_samples, buddy_voice_buffer
    buddy_voice_profile = None
    buddy_voice_samples = []
    buddy_voice_buffer.clear()
    print("[VoiceFingerprint] 🔄 Voice learning reset (but still DISABLED)")

def emergency_disable_fingerprinting():
    """Emergency function to disable fingerprinting"""
    global VOICE_FINGERPRINTING_ENABLED
    VOICE_FINGERPRINTING_ENABLED = False
    reset_voice_learning()
    print("[VoiceFingerprint] 🚨 EMERGENCY DISABLE - Voice fingerprinting stopped")

def emergency_enable_fingerprinting():
    """Emergency function to re-enable fingerprinting (NOT RECOMMENDED)"""
    global VOICE_FINGERPRINTING_ENABLED
    VOICE_FINGERPRINTING_ENABLED = True
    print("[VoiceFingerprint] ⚠️ EMERGENCY ENABLE - Voice fingerprinting re-enabled")
    print("[VoiceFingerprint] 📢 WARNING: This may filter human speech!")

def is_fingerprinting_enabled():
    """Check if voice fingerprinting is enabled"""
    return VOICE_FINGERPRINTING_ENABLED

# ✅ FORCE DISABLE ON IMPORT
emergency_disable_fingerprinting()
print("[VoiceFingerprint] ✅ VOICE FINGERPRINTING FORCIBLY DISABLED FOR SAFETY")
print("[VoiceFingerprint] 📢 Human speech protection: MAXIMUM")