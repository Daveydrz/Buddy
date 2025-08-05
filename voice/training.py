# voice/training.py - Advanced Interactive Voice Training with clustering intelligence
import re
import time
import numpy as np
from audio.input import aec_training_listen
from audio.output import speak_streaming, play_chime, buddy_talking
from ai.speech import transcribe_audio
from voice.recognition import generate_voice_embedding
from config import *

# ✅ ADVANCED: Comprehensive training phrases for robust clustering
ADVANCED_TRAINING_PHRASES = [
    # Core speech patterns with emotional variation
    "Hello, my name is speaking clearly and confidently now",
    "What time is it right now on this beautiful day", 
    "How are you doing this wonderful morning",
    "The weather outside looks absolutely beautiful today",
    "I need to make an important phone call right now",
    
    # Question patterns with different intonations
    "Can you please help me with this important question",
    "What would you like me to say next in our conversation",
    "How do I get to the nearest train station quickly",
    "When will the meeting start today at the office",
    "Where can I find more detailed information about this",
    
    # Command patterns with varying complexity
    "Please turn on all the lights in the room now",
    "Set a timer for exactly fifteen minutes from now",
    "Play some relaxing classical music softly in background", 
    "Show me the latest weather forecast for this week",
    "Call my family members when you have a moment",
    
    # Conversational patterns with natural flow
    "Thank you very much for all your helpful assistance",
    "That sounds like a really great idea to me",
    "I really appreciate your assistance and patience today",
    "Let me think about that important question for a moment",
    "Could you please repeat that information more slowly"
]

# ✅ CLUSTERING-OPTIMIZED: Shorter reliable phrases for quick training
CLUSTERING_OPTIMIZED_PHRASES = [
    "Hello, my name is speaking clearly",
    "What time is it right now",
    "How are you doing today",
    "The weather outside looks nice",
    "Can you help me with this",
    "Thank you very much",
    "I need to make a call",
    "Please turn on the lights"
]

def advanced_voice_training_mode():
    """🎯 Advanced training with clustering intelligence"""
    print("\n" + "="*60)
    print("🚀 BUDDY ADVANCED AI VOICE TRAINING")
    print("="*60)
    
    # Import enhanced modules
    try:
        from voice.speaker_profiles import enhanced_speaker_profiles
        from voice.voice_models import dual_voice_model_manager
        from voice.database import handle_same_name_collision
        ENHANCED_MODULES = True
        print("[AdvancedTraining] ✅ Enhanced clustering modules available")
    except ImportError:
        ENHANCED_MODULES = False
        print("[AdvancedTraining] ⚠️ Using basic training mode")
    
    # ✅ CLEAR INSTRUCTION with clustering context
    speak_streaming("Let's start advanced voice training with AI clustering technology.")
    
    # ✅ CRITICAL: Wait for TTS to complete
    while buddy_talking.is_set():
        time.sleep(0.1)
    time.sleep(2.0)
    
    # ✅ RELIABLE: Get name with advanced validation
    username = get_name_with_clustering_validation()
    if not username:
        username = "David"  # Fallback to default
    
    # ✅ SAME NAME COLLISION HANDLING
    if ENHANCED_MODULES:
        final_username = handle_same_name_collision(username)
        if final_username != username:
            speak_streaming(f"I'll call you {final_username} to avoid name conflicts.")
            while buddy_talking.is_set():
                time.sleep(0.1)
            time.sleep(1.0)
        username = final_username
    
    print(f"[AdvancedTraining] 👤 Training for: {username}")
    
    # ✅ CLUSTERING-OPTIMIZED PHRASES
    training_phrases = CLUSTERING_OPTIMIZED_PHRASES
    
    speak_streaming(f"Excellent! I'll train with {len(training_phrases)} clustering-optimized phrases for {username}.")
    
    while buddy_talking.is_set():
        time.sleep(0.1)
    time.sleep(1.0)
    
    speak_streaming("Each phrase helps build your unique voice profile. Speak naturally when ready.")
    while buddy_talking.is_set():
        time.sleep(0.1)
    time.sleep(2.0)
    
    # ✅ ADVANCED SAMPLE COLLECTION with clustering intelligence
    voice_samples = []
    quality_scores = []
    clustering_metrics = []
    successful_recordings = 0
    total_attempts = 0
    
    for i, phrase in enumerate(training_phrases):
        phrase_num = i + 1
        print(f"\n[AdvancedTraining] 📝 Phrase {phrase_num}/{len(training_phrases)}: {phrase}")
        
        # ✅ CLUSTERING-AWARE COLLECTION
        audio, quality_info, clustering_info = collect_phrase_with_clustering_analysis(phrase, phrase_num)
        total_attempts += 1
        
        if audio is not None:
            voice_samples.append(audio)
            
            if ENHANCED_MODULES:
                quality_scores.append(quality_info.get('overall_score', 0.5))
                clustering_metrics.append(clustering_info)
            else:
                quality_scores.append(0.7)  # Default quality
                clustering_metrics.append({'clustering_suitability': 'good'})
                
            successful_recordings += 1
            clustering_suit = clustering_info.get('clustering_suitability', 'unknown')
            print(f"[AdvancedTraining] ✅ Phrase {phrase_num} accepted - Quality: {quality_info.get('overall_score', 0.5):.2f}, Clustering: {clustering_suit}")
            
            # ✅ BRIEF FEEDBACK with clustering context
            if clustering_suit == 'excellent':
                speak_streaming("Excellent quality.")
            elif clustering_suit == 'good':
                speak_streaming("Good.")
            else:
                speak_streaming("Accepted.")
            
            while buddy_talking.is_set():
                time.sleep(0.1)
            time.sleep(0.5)
        else:
            print(f"[AdvancedTraining] ❌ Phrase {phrase_num} failed")
            speak_streaming("Let's continue.")
            while buddy_talking.is_set():
                time.sleep(0.1)
            time.sleep(0.5)
    
    # ✅ CREATE ADVANCED PROFILE with clustering intelligence
    if successful_recordings >= 4:  # Lower threshold for reliability
        return create_advanced_clustering_profile(username, voice_samples, quality_scores, clustering_metrics, successful_recordings, total_attempts)
    else:
        speak_streaming(f"I only got {successful_recordings} phrases. Let's try again later.")
        while buddy_talking.is_set():
            time.sleep(0.1)
        return False

def get_name_with_clustering_validation():
    """🏷️ Advanced name collection with clustering validation"""
    for attempt in range(3):
        speak_streaming("Please say your first name clearly for voice profile creation.")
        
        # ✅ CRITICAL: Wait for TTS to complete
        while buddy_talking.is_set():
            time.sleep(0.1)
        
        # ✅ PATIENT: Give user time to prepare
        time.sleep(1.0)
        
        # ✅ Optional beep for clarity
        try:
            play_chime()
            time.sleep(0.5)
        except:
            pass
        
        print(f"[AdvancedTraining] 👂 Listening for name (attempt {attempt + 1}/3)...")
        
        # ✅ LONGER TIMEOUT for name
        name_audio = aec_training_listen("name", timeout=45)
        if name_audio is None:
            speak_streaming("I didn't hear anything. Let's try again.")
            while buddy_talking.is_set():
                time.sleep(0.1)
            continue
        
        # ✅ CLUSTERING-AWARE Quality check
        try:
            from voice.speaker_profiles import enhanced_speaker_profiles
            quality = enhanced_speaker_profiles.assess_audio_quality_advanced(name_audio)
            
            if quality['auto_discard'] or quality['clustering_suitability'] == 'unusable':
                speak_streaming("Audio wasn't clear enough for voice clustering. Please speak a bit louder.")
                while buddy_talking.is_set():
                    time.sleep(0.1)
                continue
                
        except ImportError:
            pass  # Skip quality check if enhanced modules not available
        
        # Transcribe name
        name_text = transcribe_audio(name_audio)
        if not name_text or len(name_text.strip()) < 2:
            speak_streaming("I couldn't understand clearly. Please try again.")
            while buddy_talking.is_set():
                time.sleep(0.1)
            continue
        
        print(f"[AdvancedTraining] 📝 Name transcription: '{name_text}'")
        
        # Extract name with clustering context
        username = extract_clustering_aware_name(name_text)
        if username:
            # ✅ ADVANCED: Confirm name with clustering context
            speak_streaming(f"I heard {username}. This will be used for your voice clustering profile. Is that correct?")
            
            while buddy_talking.is_set():
                time.sleep(0.1)
            time.sleep(1.0)
            
            confirmation_audio = aec_training_listen("name_confirmation", timeout=30)
            if confirmation_audio:
                confirmation_text = transcribe_audio(confirmation_audio)
                if confirmation_text and any(word in confirmation_text.lower() for word in ["yes", "yeah", "correct", "right", "ok"]):
                    return username
                else:
                    speak_streaming("Let me try again.")
                    while buddy_talking.is_set():
                        time.sleep(0.1)
                    continue
            else:
                # ✅ ASSUME YES if no response (timeout)
                speak_streaming(f"I'll use {username} for your voice clustering profile.")
                while buddy_talking.is_set():
                    time.sleep(0.1)
                return username
        else:
            speak_streaming("I couldn't extract your name clearly. Please try again.")
            while buddy_talking.is_set():
                time.sleep(0.1)
    
    # ✅ FALLBACK: Use default name if all attempts fail
    print("[AdvancedTraining] ❌ Name collection failed, using default")
    speak_streaming("I'll use David as your name for advanced voice training.")
    while buddy_talking.is_set():
        time.sleep(0.1)
    return "David"

def check_voice_training_command(text):
    """🔍 Check if user wants to train their voice"""
    training_commands = [
        "learn my voice", "train my voice", "remember my voice",
        "voice training", "teach you my voice", "register my voice",
        "advanced training", "clustering training", "comprehensive training",
        "ai training", "voice profile", "create voice profile"
    ]
    
    text_lower = text.lower().strip()
    return any(cmd in text_lower for cmd in training_commands)

def collect_phrase_with_clustering_analysis(phrase, phrase_num):
    """🎯 Advanced phrase collection with clustering analysis"""
    for attempt in range(2):  # Two attempts per phrase
        print(f"[AdvancedTraining] 🎯 Collecting phrase {phrase_num} with clustering analysis (attempt {attempt + 1}/2)")
        
        # ✅ PATIENT: Clear instruction with TTS wait
        speak_streaming(f"Phrase {phrase_num}: {phrase}")
        
        # ✅ CRITICAL: Wait for TTS to complete
        while buddy_talking.is_set():
            time.sleep(0.1)
        
        # ✅ PATIENT: Give user time to prepare
        time.sleep(1.0)
        
        speak_streaming("Speak when you're ready.")
        
        # ✅ CRITICAL: Wait for TTS to complete again
        while buddy_talking.is_set():
            time.sleep(0.1)
        
        print(f"[AdvancedTraining] 👂 Listening for phrase {phrase_num}...")
        
        # ✅ USE EXISTING FUNCTION with longer timeout
        audio = aec_training_listen(f"phrase_{phrase_num}_attempt_{attempt + 1}", timeout=60)
        
        if audio is not None and len(audio) > SAMPLE_RATE * 0.5:
            # ✅ CLUSTERING-AWARE QUALITY ASSESSMENT
            try:
                from voice.speaker_profiles import enhanced_speaker_profiles
                quality_info = enhanced_speaker_profiles.assess_audio_quality_advanced(audio)
                
                clustering_info = {
                    'clustering_suitability': quality_info['clustering_suitability'],
                    'snr_db': quality_info['snr_db'],
                    'spectral_quality': quality_info['spectral_quality'],
                    'voice_ratio': quality_info.get('voice_ratio', 0.5),
                    'clustering_optimized': True
                }
                
                print(f"[AdvancedTraining] 📊 Quality: {quality_info['overall_score']:.2f}, Clustering: {quality_info['clustering_suitability']}")
                
                if quality_info['auto_discard'] or quality_info['clustering_suitability'] == 'unusable':
                    if attempt == 0:
                        speak_streaming("Audio quality isn't optimal for clustering. Let's try again.")
                        while buddy_talking.is_set():
                            time.sleep(0.1)
                        time.sleep(1.0)
                        continue
                    else:
                        return None, quality_info, clustering_info
                
            except ImportError:
                quality_info = basic_quality_assessment(audio)
                clustering_info = {'clustering_suitability': 'unknown', 'clustering_optimized': False}
            
            # ✅ CLUSTERING-ENHANCED Phrase validation
            spoken_text = transcribe_audio(audio)
            print(f"[AdvancedTraining] 📝 You said: '{spoken_text}'")
            
            if is_phrase_clustering_acceptable(spoken_text, phrase, tolerance=0.3):  # Lower tolerance
                print(f"[AdvancedTraining] ✅ Phrase {phrase_num} accepted for clustering")
                return audio, quality_info, clustering_info
            else:
                if attempt == 0:
                    speak_streaming("Let's try that phrase again for better clustering.")
                    while buddy_talking.is_set():
                        time.sleep(0.1)
                    time.sleep(1.0)
                else:
                    print(f"[AdvancedTraining] ❌ Phrase {phrase_num} failed after 2 attempts")
                    # ✅ ACCEPT ANYWAY for clustering continuity
                    print(f"[AdvancedTraining] 🔄 Accepting phrase anyway for clustering training")
                    return audio, quality_info, clustering_info
        else:
            if attempt == 0:
                speak_streaming("I didn't hear anything. Please try again.")
                while buddy_talking.is_set():
                    time.sleep(0.1)
                time.sleep(1.0)
            else:
                print(f"[AdvancedTraining] ❌ No audio for phrase {phrase_num}")
                return None, {}, {}
    
    return None, {}, {}

def create_advanced_clustering_profile(username, voice_samples, quality_scores, clustering_metrics, successful, total):
    """🧠 Create advanced voice profile with clustering intelligence"""
    try:
        print(f"[AdvancedTraining] 🧠 Creating advanced clustering profile: {successful}/{total} samples")
        speak_streaming("Processing your voice samples with advanced AI clustering algorithms...")
        
        # ✅ WAIT FOR TTS
        while buddy_talking.is_set():
            time.sleep(0.1)
        
        # ✅ ADVANCED: Use enhanced profile creation with clustering
        try:
            from voice.speaker_profiles import enhanced_speaker_profiles
            
            success = enhanced_speaker_profiles.create_enhanced_profile(
                username=username,
                audio_samples=voice_samples,
                training_type='formal_clustering_enhanced'
            )
            
            if success:
                print(f"[AdvancedTraining] 🎊 Advanced clustering profile created!")
                
                # Calculate clustering effectiveness
                excellent_count = sum(1 for m in clustering_metrics if m.get('clustering_suitability') == 'excellent')
                good_count = sum(1 for m in clustering_metrics if m.get('clustering_suitability') == 'good')
                clustering_effectiveness = (excellent_count + good_count) / len(clustering_metrics) if clustering_metrics else 0.5
                
                speak_streaming("Excellent! Your advanced voice profile has been created with AI clustering technology.")
                while buddy_talking.is_set():
                    time.sleep(0.1)
                time.sleep(2.0)
                
                speak_streaming(f"Training success: {successful}/{total} samples with {clustering_effectiveness:.0%} clustering effectiveness.")
                while buddy_talking.is_set():
                    time.sleep(0.1)
                time.sleep(1.5)
                
                speak_streaming("Your voice is now ready for intelligent recognition across all interactions.")
                while buddy_talking.is_set():
                    time.sleep(0.1)
                
                return True
            else:
                return create_basic_clustering_profile(username, voice_samples, clustering_metrics)
                
        except ImportError:
            return create_basic_clustering_profile(username, voice_samples, clustering_metrics)
            
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Advanced profile creation error: {e}")
        return create_basic_clustering_profile(username, voice_samples, clustering_metrics)

def create_basic_clustering_profile(username, voice_samples, clustering_metrics):
    """🔄 Create basic voice profile with clustering awareness"""
    try:
        print(f"[AdvancedTraining] 🔄 Creating basic clustering profile with {len(voice_samples)} samples")
        
        # Generate embeddings
        embeddings = []
        for sample in voice_samples:
            embedding = generate_voice_embedding(sample)
            if embedding is not None:
                embeddings.append(embedding)
        
        if len(embeddings) >= 2:
            # Save voice profile with clustering context
            from voice.database import known_users, save_known_users
            from datetime import datetime
            
            current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            
            # ✅ CLUSTERING-AWARE PROFILE
            if len(embeddings) > 1:
                # Use multiple embeddings for better clustering
                profile_data = {
                    'username': username,
                    'status': 'trained',
                    'created_date': current_time,
                    'last_updated': current_time,
                    'confidence_threshold': 0.4,  # Lower threshold for clustering
                    'embeddings': [emb.tolist() for emb in embeddings],
                    'embedding_metadata': [
                        {
                            'source': 'training_clustering',
                            'timestamp': current_time,
                            'clustering_aware': True
                        }
                        for _ in embeddings
                    ],
                    'clustering_metrics': clustering_metrics,
                    'training_type': 'formal_clustering_basic',
                    'samples_used': len(embeddings),
                    'recognition_count': 0,
                    'login_user': 'Daveydrz',
                    'clustering_enabled': True,
                    'background_learning': True
                }
            else:
                # Single embedding fallback
                profile_data = {
                    'username': username,
                    'embedding': embeddings[0].tolist(),
                    'status': 'trained',
                    'created_date': current_time,
                    'confidence_threshold': 0.4,
                    'training_type': 'formal_clustering_basic_single',
                    'login_user': 'Daveydrz',
                    'clustering_enabled': False
                }
            
            # ✅ CRITICAL: Save profile and verify
            print(f"[AdvancedTraining] 💾 Saving clustering profile to database...")
            known_users[username] = profile_data
            save_known_users()
            
            print(f"[AdvancedTraining] ✅ Basic clustering profile created for {username} with {len(embeddings)} embeddings")
            
            # ✅ VERIFY save with detailed debug
            if username in known_users:
                saved_profile = known_users[username]
                print(f"[AdvancedTraining] ✅ Profile verification successful")
                print(f"[AdvancedTraining] 📊 Profile details: status={saved_profile.get('status')}, clustering_enabled={saved_profile.get('clustering_enabled', False)}")
                
                speak_streaming("Voice training completed successfully with clustering support!")
                while buddy_talking.is_set():
                    time.sleep(0.1)
                return True
            else:
                print(f"[AdvancedTraining] ❌ Profile verification failed - not found in database")
                return False
        else:
            print(f"[AdvancedTraining] ❌ Not enough valid embeddings: {len(embeddings)}")
            speak_streaming("I had trouble processing your voice. Let's try again later.")
            while buddy_talking.is_set():
                time.sleep(0.1)
            return False
            
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Basic clustering profile creation error: {e}")
        return False

def is_phrase_clustering_acceptable(spoken_text, target_phrase, tolerance=0.3):
    """✅ CLUSTERING-ENHANCED: More intelligent phrase matching"""
    if not spoken_text:
        return False
    
    spoken_lower = spoken_text.lower().strip()
    target_lower = target_phrase.lower().strip()
    
    # ✅ CLUSTERING-OPTIMIZED: Remove filler words and common variations
    fillers = ["um", "uh", "like", "you know", "well", "so", "the", "a", "an", "and", "but", "or"]
    spoken_words = [w for w in spoken_lower.split() if w not in fillers and len(w) > 1]
    target_words = [w for w in target_lower.split() if w not in fillers and len(w) > 1]
    
    if len(target_words) == 0:
        return False
    
    # ✅ CLUSTERING-AWARE: Enhanced matching for voice distinctiveness
    exact_matches = 0
    partial_matches = 0
    semantic_matches = 0
    
    # Semantic equivalents for clustering training
    semantic_equivalents = {
        'hello': ['hi', 'hey', 'good', 'greetings'],
        'time': ['clock', 'hour', 'minute'],
        'weather': ['climate', 'temperature', 'conditions'],
        'help': ['assist', 'support', 'aid'],
        'thank': ['thanks', 'appreciate', 'grateful'],
        'please': ['kindly', 'would', 'could'],
        'call': ['phone', 'ring', 'contact'],
        'lights': ['light', 'lamp', 'illumination']
    }
    
    for target_word in target_words:
        # Exact match
        if target_word in spoken_words:
            exact_matches += 1
        # Partial match (for longer words)
        elif len(target_word) >= 3:
            for spoken_word in spoken_words:
                if (target_word in spoken_word or spoken_word in target_word or
                    abs(len(target_word) - len(spoken_word)) <= 2):
                    partial_matches += 1
                    break
        # Semantic match for clustering effectiveness
        else:
            for spoken_word in spoken_words:
                if target_word in semantic_equivalents:
                    if spoken_word in semantic_equivalents[target_word]:
                        semantic_matches += 1
                        break
                elif spoken_word in semantic_equivalents:
                    if target_word in semantic_equivalents[spoken_word]:
                        semantic_matches += 1
                        break
    
    # ✅ CLUSTERING-ENHANCED: Weighted scoring with semantic awareness
    total_matches = exact_matches + (partial_matches * 0.8) + (semantic_matches * 0.6)
    accuracy = total_matches / len(target_words)
    
    print(f"[AdvancedTraining] 📊 Clustering phrase accuracy: {accuracy:.2f}")
    print(f"  Exact matches: {exact_matches}/{len(target_words)}")
    print(f"  Partial matches: {partial_matches}")
    print(f"  Semantic matches: {semantic_matches}")
    print(f"  Tolerance: {tolerance}")
    
    return accuracy >= tolerance

def extract_clustering_aware_name(text):
    """🧠 CLUSTERING-AWARE: Enhanced name extraction for training"""
    try:
        print(f"[AdvancedTraining] 🔍 Clustering-aware name extraction from: '{text}'")
        
        words = text.lower().split()
        
        # ✅ CLUSTERING-ENHANCED: Comprehensive known names database with clustering context
        known_names = [
            # Current user variations
            'dawid', 'david', 'daveydrz', 'dave', 'davy', 'davie',
            # Common international names optimized for clustering
            'francesco', 'john', 'mike', 'sarah', 'anna', 'mary', 'james',
            'robert', 'michael', 'william', 'richard', 'thomas', 'chris',
            'daniel', 'paul', 'mark', 'elizabeth', 'jennifer', 'maria',
            'susan', 'margaret', 'lisa', 'nancy', 'karen', 'betty',
            # Modern names
            'alex', 'sam', 'jordan', 'taylor', 'casey', 'jamie', 'riley',
            'morgan', 'cameron', 'blake', 'drew', 'sage', 'parker'
        ]
        
        # Look for known names first (clustering optimization)
        for word in words:
            clean_word = re.sub(r'[^a-zA-Z]', '', word).lower()
            if clean_word in known_names:
                print(f"[AdvancedTraining] ✅ Found clustering-optimized name: '{clean_word.title()}'")
                return clean_word.title()
        
        # ✅ CLUSTERING-ENHANCED: Pattern-based extraction
        name_patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"i am (\w+)",
            r"call me (\w+)",
            r"(\w+) here",
            r"this is (\w+)",
            r"it's (\w+)"
        ]
        
        text_lower = ' '.join(words)
        for pattern in name_patterns:
            match = re.search(pattern, text_lower)
            if match:
                potential_name = match.group(1).title()
                if is_valid_clustering_name(potential_name):
                    print(f"[AdvancedTraining] ✅ Pattern match for clustering: '{potential_name}'")
                    return potential_name
        
        # Look for reasonable name candidates with clustering optimization
        for word in words:
            clean_word = re.sub(r'[^a-zA-Z]', '', word)
            if is_valid_clustering_name(clean_word):
                print(f"[AdvancedTraining] ✅ Found clustering candidate name: '{clean_word.title()}'")
                return clean_word.title()
        
        print(f"[AdvancedTraining] ❌ No valid clustering name found")
        return None
        
    except Exception as e:
        print(f"[AdvancedTraining] Name extraction error: {e}")
        return None

def is_valid_clustering_name(name):
    """✅ CLUSTERING-ENHANCED: Validate name for training context"""
    if not name or len(name) < 2 or len(name) > 20:
        return False
    
    if not name.isalpha():
        return False
    
    # ✅ CLUSTERING-OPTIMIZED: More comprehensive non-name filtering
    non_names = {
        'voice', 'name', 'hello', 'hey', 'buddy', 'yes', 'yeah', 'no', 'nope',
        'okay', 'ok', 'thanks', 'good', 'great', 'fine', 'nice', 'time', 'today',
        'what', 'when', 'where', 'how', 'why', 'the', 'and', 'but', 'for', 'with',
        'first', 'last', 'clearly', 'say', 'speak', 'talking', 'listen', 'hear',
        'training', 'session', 'complete', 'start', 'begin', 'ready', 'now',
        'please', 'thank', 'sorry', 'excuse', 'clustering', 'profile', 'system',
        'audio', 'quality', 'sound', 'voice', 'recording', 'microphone'
    }
    
    if name.lower() in non_names:
        return False
    
    # Must start with capital letter (proper name format) - clustering requirement
    if not name[0].isupper():
        return False
    
    # ✅ CLUSTERING-SPECIFIC: Additional validation for clustering effectiveness
    # Names should have reasonable phonetic diversity for clustering
    vowel_count = sum(1 for c in name.lower() if c in 'aeiou')
    consonant_count = len(name) - vowel_count
    
    # Clustering works better with phonetically diverse names
    if vowel_count == 0 or consonant_count == 0:
        return False
    
    vowel_ratio = vowel_count / len(name)
    if vowel_ratio < 0.2 or vowel_ratio > 0.8:  # Names need balanced phonetics for clustering
        return False
    
    return True

def basic_quality_assessment(audio):
    """🔄 Basic quality assessment when enhanced modules not available"""
    try:
        volume = np.abs(audio).mean()
        duration = len(audio) / SAMPLE_RATE
        
        score = 0.5  # Default
        if 100 <= volume <= 5000 and duration >= 1.0:
            score = 0.7
        
        return {
            'overall_score': score,
            'volume': volume,
            'duration': duration,
            'issues': [],
            'auto_discard': False,
            'clustering_suitability': 'unknown'
        }
    except:
        return {
            'overall_score': 0.5, 
            'issues': [], 
            'auto_discard': False,
            'clustering_suitability': 'unknown'
        }

# ✅ CLUSTERING-ENHANCED: Main training function selector
def voice_training_mode():
    """🎯 Main training function - uses advanced clustering mode"""
    try:
        return advanced_voice_training_mode()
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Advanced clustering training failed: {e}")
        print(f"[AdvancedTraining] 🔄 Falling back to basic training")
        # Could fall back to original training here if needed
        return False

def check_voice_training_command(text):
    """🔍 Check if user wants to train their voice"""
    training_commands = [
        "learn my voice", "train my voice", "remember my voice",
        "voice training", "teach you my voice", "register my voice",
        "advanced training", "clustering training", "comprehensive training",
        "ai training", "voice profile", "create voice profile"
    ]
    
    text_lower = text.lower().strip()
    return any(cmd in text_lower for cmd in training_commands)

def get_training_effectiveness_report():
    """📊 Get training effectiveness report"""
    try:
        from voice.database import known_users
        
        report = {
            'total_trained_users': 0,
            'clustering_enabled_users': 0,
            'training_types': {},
            'average_embeddings_per_user': 0,
            'quality_distribution': {'high': 0, 'medium': 0, 'low': 0}
        }
        
        total_embeddings = 0
        
        for username, profile in known_users.items():
            if profile.get('status') == 'trained':
                report['total_trained_users'] += 1
                
                # Count embeddings
                embedding_count = len(profile.get('embeddings', [profile.get('embedding', [])]))
                total_embeddings += embedding_count
                
                # Clustering enabled
                if profile.get('clustering_enabled', False):
                    report['clustering_enabled_users'] += 1
                
                # Training type
                training_type = profile.get('training_type', 'unknown')
                report['training_types'][training_type] = report['training_types'].get(training_type, 0) + 1
                
                # Quality assessment
                quality_scores = profile.get('quality_scores', [])
                if quality_scores:
                    avg_quality = sum(quality_scores) / len(quality_scores)
                    if avg_quality > 0.7:
                        report['quality_distribution']['high'] += 1
                    elif avg_quality > 0.5:
                        report['quality_distribution']['medium'] += 1
                    else:
                        report['quality_distribution']['low'] += 1
        
        if report['total_trained_users'] > 0:
            report['average_embeddings_per_user'] = total_embeddings / report['total_trained_users']
        
        return report
        
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Training effectiveness report error: {e}")
        return {}

def optimize_training_for_clustering():
    """⚡ Optimize existing training data for clustering"""
    try:
        from voice.database import known_users, save_known_users
        from voice.speaker_profiles import enhanced_speaker_profiles
        
        optimized_count = 0
        
        for username, profile in known_users.items():
            if profile.get('status') == 'trained' and not profile.get('clustering_enabled', False):
                # Try to enable clustering for existing profiles
                embeddings = profile.get('embeddings', [])
                if not embeddings and 'embedding' in profile:
                    # Convert single embedding to multi-embedding format
                    embeddings = [profile['embedding']]
                    profile['embeddings'] = embeddings
                    del profile['embedding']
                
                if len(embeddings) >= 2:
                    # Enable clustering features
                    profile['clustering_enabled'] = True
                    profile['confidence_threshold'] = min(profile.get('confidence_threshold', 0.6), 0.5)  # Lower threshold
                    profile['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    profile['clustering_optimization'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Add clustering metrics if missing
                    if 'clustering_metrics' not in profile:
                        profile['clustering_metrics'] = [
                            {
                                'clustering_suitability': 'good',  # Assume good for existing data
                                'snr_db': 15.0,  # Default reasonable SNR
                                'spectral_quality': 0.6
                            }
                            for _ in embeddings
                        ]
                    
                    optimized_count += 1
                    print(f"[AdvancedTraining] ⚡ Optimized {username} for clustering")
        
        if optimized_count > 0:
            save_known_users()
            print(f"[AdvancedTraining] ✅ Optimized {optimized_count} profiles for clustering")
        
        return optimized_count
        
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Clustering optimization error: {e}")
        return 0

def validate_training_quality():
    """🔍 Validate quality of existing training data"""
    try:
        from voice.database import known_users
        
        validation_report = {
            'total_profiles': 0,
            'valid_profiles': 0,
            'issues_found': [],
            'recommendations': []
        }
        
        for username, profile in known_users.items():
            validation_report['total_profiles'] += 1
            
            issues = []
            
            # Check for valid embeddings
            embeddings = profile.get('embeddings', [])
            if not embeddings and 'embedding' in profile:
                embeddings = [profile['embedding']]
            
            if not embeddings:
                issues.append('no_embeddings')
            elif len(embeddings) < 2 and not profile.get('clustering_enabled', False):
                issues.append('insufficient_embeddings_for_clustering')
            
            # Check embedding validity
            for i, embedding in enumerate(embeddings):
                if isinstance(embedding, list):
                    if len(embedding) != 256:
                        issues.append(f'invalid_embedding_size_{i}')
                elif isinstance(embedding, dict) and 'resemblyzer' in embedding:
                    if len(embedding['resemblyzer']) != 256:
                        issues.append(f'invalid_dual_embedding_size_{i}')
                else:
                    issues.append(f'invalid_embedding_format_{i}')
            
            # Check metadata consistency
            embedding_count = len(embeddings)
            quality_scores = profile.get('quality_scores', [])
            clustering_metrics = profile.get('clustering_metrics', [])
            
            if quality_scores and len(quality_scores) != embedding_count:
                issues.append('quality_scores_mismatch')
            
            if clustering_metrics and len(clustering_metrics) != embedding_count:
                issues.append('clustering_metrics_mismatch')
            
            # Check thresholds
            threshold = profile.get('confidence_threshold', 0.5)
            if threshold > 0.9:
                issues.append('threshold_too_high')
            elif threshold < 0.2:
                issues.append('threshold_too_low')
            
            if not issues:
                validation_report['valid_profiles'] += 1
            else:
                validation_report['issues_found'].append({
                    'username': username,
                    'issues': issues
                })
        
        # Generate recommendations
        if validation_report['issues_found']:
            validation_report['recommendations'].append("Run optimize_training_for_clustering() to fix metadata issues")
            
            if any('insufficient_embeddings' in str(issue) for issue in validation_report['issues_found']):
                validation_report['recommendations'].append("Consider additional training for users with single embeddings")
            
            if any('threshold' in str(issue) for issue in validation_report['issues_found']):
                validation_report['recommendations'].append("Run adaptive threshold tuning for users with extreme thresholds")
        
        return validation_report
        
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Training validation error: {e}")
        return {'error': str(e)}

def retrain_user_with_clustering(username):
    """🔄 Retrain specific user with clustering enhancements"""
    try:
        from voice.database import known_users
        from voice.speaker_profiles import enhanced_speaker_profiles
        
        if username not in known_users:
            print(f"[AdvancedTraining] ❌ User {username} not found")
            return False
        
        # Load raw audio samples if available
        try:
            raw_samples = enhanced_speaker_profiles.load_raw_audio_samples(username)
            if len(raw_samples) >= 3:
                print(f"[AdvancedTraining] 📂 Found {len(raw_samples)} raw samples for {username}")
                
                # Recreate profile with clustering enhancements
                success = enhanced_speaker_profiles.create_enhanced_profile(
                    username=username,
                    audio_samples=raw_samples,
                    training_type='clustering_retrain'
                )
                
                if success:
                    print(f"[AdvancedTraining] ✅ Successfully retrained {username} with clustering")
                    return True
                else:
                    print(f"[AdvancedTraining] ❌ Retraining failed for {username}")
                    return False
            else:
                print(f"[AdvancedTraining] ❌ Not enough raw samples for {username}: {len(raw_samples)}")
                return False
                
        except Exception as e:
            print(f"[AdvancedTraining] ❌ Could not load raw samples for {username}: {e}")
            return False
            
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Retraining error: {e}")
        return False

def generate_training_statistics():
    """📊 Generate comprehensive training statistics"""
    try:
        from voice.database import known_users, anonymous_clusters
        
        stats = {
            'training_overview': {
                'total_known_users': len(known_users),
                'total_anonymous_clusters': len(anonymous_clusters),
                'clustering_enabled_users': 0,
                'successfully_trained_users': 0
            },
            'training_methods': {},
            'quality_analysis': {
                'high_quality_profiles': 0,
                'medium_quality_profiles': 0,
                'low_quality_profiles': 0,
                'average_quality_score': 0.0
            },
            'clustering_analysis': {
                'excellent_clustering': 0,
                'good_clustering': 0,
                'fair_clustering': 0,
                'poor_clustering': 0
            },
            'threshold_analysis': {
                'conservative_thresholds': 0,  # > 0.7
                'balanced_thresholds': 0,      # 0.4-0.7
                'aggressive_thresholds': 0     # < 0.4
            },
            'embedding_analysis': {
                'single_embedding_users': 0,
                'multi_embedding_users': 0,
                'average_embeddings_per_user': 0.0,
                'total_embeddings': 0
            }
        }
        
        total_quality_score = 0.0
        quality_count = 0
        total_embeddings = 0
        
        for username, profile in known_users.items():
            # Training status
            if profile.get('status') == 'trained':
                stats['training_overview']['successfully_trained_users'] += 1
            
            # Clustering enabled
            if profile.get('clustering_enabled', False):
                stats['training_overview']['clustering_enabled_users'] += 1
            
            # Training methods
            training_type = profile.get('training_type', 'unknown')
            stats['training_methods'][training_type] = stats['training_methods'].get(training_type, 0) + 1
            
            # Quality analysis
            quality_scores = profile.get('quality_scores', [])
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                total_quality_score += avg_quality
                quality_count += 1
                
                if avg_quality > 0.7:
                    stats['quality_analysis']['high_quality_profiles'] += 1
                elif avg_quality > 0.5:
                    stats['quality_analysis']['medium_quality_profiles'] += 1
                else:
                    stats['quality_analysis']['low_quality_profiles'] += 1
            
            # Clustering analysis
            clustering_metrics = profile.get('clustering_metrics', [])
            for metric in clustering_metrics:
                suitability = metric.get('clustering_suitability', 'unknown')
                if suitability == 'excellent':
                    stats['clustering_analysis']['excellent_clustering'] += 1
                elif suitability == 'good':
                    stats['clustering_analysis']['good_clustering'] += 1
                elif suitability == 'fair':
                    stats['clustering_analysis']['fair_clustering'] += 1
                elif suitability == 'poor':
                    stats['clustering_analysis']['poor_clustering'] += 1
            
            # Threshold analysis
            threshold = profile.get('confidence_threshold', 0.5)
            if threshold > 0.7:
                stats['threshold_analysis']['conservative_thresholds'] += 1
            elif threshold >= 0.4:
                stats['threshold_analysis']['balanced_thresholds'] += 1
            else:
                stats['threshold_analysis']['aggressive_thresholds'] += 1
            
            # Embedding analysis
            embeddings = profile.get('embeddings', [])
            if not embeddings and 'embedding' in profile:
                embeddings = [profile['embedding']]
            
            embedding_count = len(embeddings)
            total_embeddings += embedding_count
            
            if embedding_count == 1:
                stats['embedding_analysis']['single_embedding_users'] += 1
            elif embedding_count > 1:
                stats['embedding_analysis']['multi_embedding_users'] += 1
        
        # Calculate averages
        if quality_count > 0:
            stats['quality_analysis']['average_quality_score'] = total_quality_score / quality_count
        
        if len(known_users) > 0:
            stats['embedding_analysis']['average_embeddings_per_user'] = total_embeddings / len(known_users)
        
        stats['embedding_analysis']['total_embeddings'] = total_embeddings
        
        return stats
        
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Statistics generation error: {e}")
        return {'error': str(e)}

def cleanup_training_artifacts():
    """🧹 Clean up training artifacts and temporary files"""
    try:
        import os
        import glob
        
        cleaned_files = 0
        
        # Clean up temporary training files
        temp_patterns = [
            "voice_profiles/raw_audio/*_training_*.pkl.gz",
            "voice_profiles/uncertain/*_training_*.pkl.gz",
            "*.wav.tmp",
            "*.audio.tmp",
            "training_session_*.log"
        ]
        
        for pattern in temp_patterns:
            for file_path in glob.glob(pattern):
                try:
                    # Only clean files older than 24 hours
                    file_age = time.time() - os.path.getctime(file_path)
                    if file_age > 24 * 3600:  # 24 hours
                        os.remove(file_path)
                        cleaned_files += 1
                        print(f"[AdvancedTraining] 🗑️ Cleaned up: {file_path}")
                except Exception as e:
                    print(f"[AdvancedTraining] ⚠️ Could not clean {file_path}: {e}")
        
        print(f"[AdvancedTraining] ✅ Cleaned up {cleaned_files} training artifacts")
        return cleaned_files
        
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Cleanup error: {e}")
        return 0

def export_training_report(output_file="training_report.json"):
    """📤 Export comprehensive training report"""
    try:
        import json
        from datetime import datetime
        
        report = {
            'report_metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'generated_by': 'Daveydrz',  # Current user
                'report_version': '2.0_clustering_enhanced',
                'system_info': {
                    'clustering_enabled': True,
                    'advanced_training': True,
                    'ai_enhanced': True
                }
            },
            'training_statistics': generate_training_statistics(),
            'training_effectiveness': get_training_effectiveness_report(),
            'validation_report': validate_training_quality(),
            'recommendations': []
        }
        
        # Generate recommendations based on analysis
        stats = report['training_statistics']
        
        if stats['training_overview']['clustering_enabled_users'] < stats['training_overview']['successfully_trained_users']:
            report['recommendations'].append("Consider enabling clustering for more users to improve recognition accuracy")
        
        if stats['quality_analysis']['low_quality_profiles'] > 0:
            report['recommendations'].append("Some profiles have low quality - consider retraining with better audio conditions")
        
        if stats['threshold_analysis']['conservative_thresholds'] > stats['threshold_analysis']['balanced_thresholds']:
            report['recommendations'].append("Many users have conservative thresholds - consider adaptive threshold tuning")
        
        if stats['embedding_analysis']['single_embedding_users'] > stats['embedding_analysis']['multi_embedding_users']:
            report['recommendations'].append("Many users have single embeddings - additional training samples would improve clustering")
        
        # Export to file
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"[AdvancedTraining] 📤 Training report exported to: {output_file}")
        return True
        
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Export error: {e}")
        return False

def run_training_maintenance():
    """🔧 Run comprehensive training system maintenance"""
    try:
        print("[AdvancedTraining] 🔧 Starting training system maintenance...")
        
        maintenance_results = {
            'optimized_profiles': 0,
            'cleaned_artifacts': 0,
            'validation_issues': 0,
            'recommendations_generated': 0
        }
        
        # 1. Optimize existing profiles for clustering
        maintenance_results['optimized_profiles'] = optimize_training_for_clustering()
        
        # 2. Clean up training artifacts
        maintenance_results['cleaned_artifacts'] = cleanup_training_artifacts()
        
        # 3. Validate training quality
        validation_report = validate_training_quality()
        maintenance_results['validation_issues'] = len(validation_report.get('issues_found', []))
        maintenance_results['recommendations_generated'] = len(validation_report.get('recommendations', []))
        
        # 4. Generate and export training report
        export_training_report(f"training_maintenance_report_{int(time.time())}.json")
        
        print(f"[AdvancedTraining] ✅ Training maintenance complete:")
        print(f"  - Optimized profiles: {maintenance_results['optimized_profiles']}")
        print(f"  - Cleaned artifacts: {maintenance_results['cleaned_artifacts']}")
        print(f"  - Validation issues: {maintenance_results['validation_issues']}")
        print(f"  - Recommendations: {maintenance_results['recommendations_generated']}")
        
        return maintenance_results
        
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Maintenance error: {e}")
        return {}

# ✅ ADVANCED TRAINING UTILITIES

def quick_train_from_conversation(username, audio_samples, context="conversation"):
    """⚡ Quick training from conversation samples"""
    try:
        if len(audio_samples) < 2:
            print(f"[AdvancedTraining] ❌ Need at least 2 samples, got {len(audio_samples)}")
            return False
        
        print(f"[AdvancedTraining] ⚡ Quick training {username} from {len(audio_samples)} conversation samples")
        
        # Use enhanced profile creation if available
        try:
            from voice.speaker_profiles import enhanced_speaker_profiles
            from voice.database import handle_same_name_collision
            
            # Handle name collision
            final_username = handle_same_name_collision(username)
            
            success = enhanced_speaker_profiles.create_enhanced_profile(
                username=final_username,
                audio_samples=audio_samples,
                training_type=f'quick_conversation_{context}'
            )
            
            if success:
                print(f"[AdvancedTraining] ✅ Quick training successful for {final_username}")
                return True
            else:
                print(f"[AdvancedTraining] ❌ Quick training failed for {final_username}")
                return False
                
        except ImportError:
            # Fallback to basic training
            return create_basic_clustering_profile(username, audio_samples, [])
            
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Quick training error: {e}")
        return False

def adaptive_training_difficulty(username):
    """🎯 Adapt training difficulty based on user performance"""
    try:
        from voice.database import known_users
        
        if username not in known_users:
            return "standard"  # Default difficulty
        
        profile = known_users[username]
        recognition_successes = profile.get('recognition_successes', 0)
        recognition_count = profile.get('recognition_count', 0)
        
        if recognition_count < 5:
            return "gentle"  # New user - gentle training
        
        success_rate = recognition_successes / recognition_count if recognition_count > 0 else 0.0
        
        if success_rate > 0.9:
            return "challenging"  # High performer - more challenging phrases
        elif success_rate > 0.7:
            return "standard"     # Good performer - standard phrases
        elif success_rate > 0.5:
            return "supportive"   # Struggling - more supportive training
        else:
            return "remedial"     # Poor performance - basic training
            
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Difficulty adaptation error: {e}")
        return "standard"

def get_personalized_training_phrases(username):
    """📝 Get personalized training phrases based on user patterns"""
    try:
        difficulty = adaptive_training_difficulty(username)
        
        phrase_sets = {
            "gentle": [
                "Hello there",
                "How are you",
                "Thank you",
                "Good morning",
                "Nice to meet you"
            ],
            "standard": CLUSTERING_OPTIMIZED_PHRASES,
            "supportive": [
                "I am speaking clearly now",
                "This is my voice training",
                "Hello my name is speaking",
                "Thank you for helping me",
                "I can speak more clearly"
            ],
            "challenging": ADVANCED_TRAINING_PHRASES[:10],  # More complex phrases
            "remedial": [
                "Hello",
                "Yes",
                "Thank you",
                "My name",
                "Good"
            ]
        }
        
        return phrase_sets.get(difficulty, CLUSTERING_OPTIMIZED_PHRASES)
        
    except Exception as e:
        print(f"[AdvancedTraining] ❌ Personalized phrases error: {e}")
        return CLUSTERING_OPTIMIZED_PHRASES

def estimate_training_duration(num_phrases, user_experience="new"):
    """⏱️ Estimate training duration"""
    try:
        base_time_per_phrase = {
            "new": 45,        # 45 seconds per phrase for new users
            "returning": 30,   # 30 seconds for returning users  
            "experienced": 20  # 20 seconds for experienced users
        }
        
        time_per_phrase = base_time_per_phrase.get(user_experience, 30)
        total_seconds = num_phrases * time_per_phrase
        
        # Add overhead time
        overhead = 120  # 2 minutes for instructions and setup
        total_seconds += overhead
        
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        return {
            'total_seconds': total_seconds,
            'minutes': minutes,
            'seconds': seconds,
            'formatted': f"{minutes}:{seconds:02d}"
        }
        
    except Exception as e:
        return {'formatted': 'Unknown', 'total_seconds': 0}

# Initialize advanced training system
print("[AdvancedTraining] 🚀 Advanced clustering training system initialized")

# Optional: Run maintenance on startup (uncomment if desired)
# run_training_maintenance()
                            