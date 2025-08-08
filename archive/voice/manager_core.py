# voice/manager_core.py - Advanced AI Assistant Core with Alexa/Siri-level intelligence
import time
import sys
from datetime import datetime
import json
import os
import numpy as np
import traceback
import re

from voice.database import known_users, anonymous_clusters, save_known_users, create_anonymous_cluster, link_anonymous_to_named

def safe_import(module_name, fallback=None):
    """Safely import modules with fallback"""
    try:
        return __import__(module_name)
    except ImportError as e:
        print(f"⚠️ Could not import {module_name}: {e}")
        return fallback

# ✅ FALLBACK: Mock voice models if not available
try:
    from voice.voice_models import dual_voice_model_manager
    VOICE_MODELS_AVAILABLE = True
except ImportError:
    print("[ManagerCore] ⚠️ Voice models not available - using fallback")
    VOICE_MODELS_AVAILABLE = False
    
    # Mock dual_voice_model_manager
    class MockVoiceModelManager:
        def generate_dual_embedding(self, audio):
            # Fallback to basic embedding
            try:
                from voice.recognition import generate_voice_embedding
                embedding = generate_voice_embedding(audio)
                if embedding is not None:
                    return {'resemblyzer': embedding.tolist()}
            except:
                pass
            return None
        
        def compare_dual_embeddings(self, emb1, emb2):
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                import numpy as np
                
                if isinstance(emb1, dict) and 'resemblyzer' in emb1:
                    emb1 = emb1['resemblyzer']
                if isinstance(emb2, dict) and 'resemblyzer' in emb2:
                    emb2 = emb2['resemblyzer']
                
                return cosine_similarity([emb1], [emb2])[0][0]
            except:
                return 0.0
        
        def get_model_info(self):
            return {'models': ['resemblyzer_fallback'], 'version': 'fallback'}
    
    dual_voice_model_manager = MockVoiceModelManager()

# Enhanced module imports
try:
    from voice.speaker_profiles import enhanced_speaker_profiles
    from voice.manager_context import ContextAnalyzer
    from voice.manager_names import NameManager
    ENHANCED_MODULES_AVAILABLE = True
    print("[ManagerCore] ✅ Enhanced modules loaded")
except ImportError as e:
    print(f"[ManagerCore] ⚠️ Enhanced modules not available: {e}")
    ENHANCED_MODULES_AVAILABLE = False

# Standard imports
try:
    from voice.database import find_similar_clusters, handle_same_name_collision
    from voice.training import voice_training_mode
    from audio.output import speak_streaming
    from config import *
except ImportError as e:
    print(f"[ManagerCore] ⚠️ Some imports failed: {e}")
    # Set fallback values
    SAMPLE_RATE = 16000
    TRAINING_MODE_NONE_STR = "none"

# ✅ SINGLE CLASS DEFINITION ONLY
class AdvancedAIAssistantCore:
    """🚀 Advanced AI Assistant Core - Alexa/Siri level intelligence"""
    
    def __init__(self):
        # ✅ PASSIVE AUDIO BUFFER - Always collecting
        self.recent_audio_buffer = []
        self.recent_text_buffer = []
        self.buffer_contexts = []
        
        # ✅ ADVANCED STATE MANAGEMENT
        self.session_context = {
            'start_time': datetime.utcnow(),
            'computer_login': 'Daveydrz',
            'actual_person_name': None, 
            'interactions': 0,
            'last_recognized_user': None,
            'current_cluster': None,
            'session_type': 'voice_interactive',
            'llm_locked': False,
            'conversation_quality': 'unknown',
            'user_adaptation_level': 'learning',
            'last_interaction_time': None
        }

        # ✅ DISABLE NAME REQUEST FLAGS
        self.pending_name_confirmation = False
        self.waiting_for_name = False
        self.suggested_name = None

        # ✅ INTELLIGENT USER MANAGEMENT
        self.user_switching_history = []
        self.voice_adaptation_cache = {}
        self.behavioral_patterns = {}
        
      
        # ✅ ADD: Voice confirmation system
        self.pending_voice_confirmation = None
        self.confirmation_timeout = 30  # 30 seconds timeout 

        # ✅ ADVANCED CLUSTERING STATE
        self.active_anonymous_clusters = {}
        self.cluster_merge_candidates = []
        self.voice_similarity_cache = {}
        
        # Legacy state (for compatibility)
        self.pending_training_offer = False
        self.current_training_user = None
        self.training_mode = TRAINING_MODE_NONE_STR
        
        # Initialize enhanced modules
        if ENHANCED_MODULES_AVAILABLE:
            try:
                self.context_analyzer = ContextAnalyzer()
                self.name_manager = NameManager()
                print(f"[AdvancedCore] 🧠 AI modules initialized")
            except Exception as e:
                print(f"[AdvancedCore] ⚠️ AI module init error: {e}")
                self.context_analyzer = None
                self.name_manager = None
        else:
            self.context_analyzer = None
            self.name_manager = None
            print(f"[AdvancedCore] 🔄 Using basic mode")
        
        print(f"[AdvancedCore] 🚀 Advanced AI Assistant initialized for computer: {self.session_context['computer_login']}")

    def _handle_voice_confirmation_response(self, audio, text):
        """✅ Handle confirmation responses"""
        try:
            if not self.pending_voice_confirmation:
                return "Guest", "NO_PENDING_CONFIRMATION"

            # Check timeout
            if time.time() > self.pending_voice_confirmation.get('timeout_at', 0):
                print(f"[AdvancedCore] ⏰ Confirmation timeout")
                self._delete_temp_confirmation_embedding()
                self.pending_voice_confirmation = None
                return self._handle_unknown_speaker_advanced(audio, text, self._basic_context_analysis(audio, text))

            text_lower = text.lower().strip()
            response_type, response_value = self._parse_confirmation_response(text_lower)

            if response_type == "positive":
                return self._process_positive_confirmation(audio, text)
            elif response_type == "negative":
                return self._process_negative_confirmation(audio, text)
            elif response_type == "name":
                return self._process_name_confirmation(response_value, audio, text)
            else:
                self._speak_confirmation_question("Please say yes or no.")
                return "Guest", "UNCLEAR_CONFIRMATION"

        except Exception as e:
            print(f"[AdvancedCore] ❌ Confirmation response error: {e}")
            return "Guest", "CONFIRMATION_ERROR"

    def _parse_confirmation_response(self, text_lower):
        """🧠 Smart parser for confirmation replies"""
        if any(word in text_lower for word in ['yes', 'yeah', 'yep', 'correct', "that's me"]):
            return "positive", None
        if any(word in text_lower for word in ['no', 'nope', 'wrong', 'not me']):
            return "negative", None

        import difflib
        candidates = list(self.known_users.keys())
        for word in text_lower.split():
            matches = difflib.get_close_matches(word, candidates, n=1, cutoff=0.8)
            if matches:
                return "name", matches[0]
        return "unclear", None

    def _start_voice_confirmation(self, candidate_user):
        """⏳ Initialize pending confirmation with timeout"""
        self.pending_voice_confirmation = {
            'candidate_user': candidate_user,
            'timeout_at': time.time() + 30  # 30 seconds to confirm
        }
        self._speak_confirmation_question(f"Is that you {candidate_user}?")

    def _delete_temp_confirmation_embedding(self):
        """🗑️ Delete temporary voice embedding if confirmation expired"""
        try:
            if ENHANCED_MODULES_AVAILABLE and 'candidate_user' in self.pending_voice_confirmation:
                temp_user = self.pending_voice_confirmation['candidate_user']
                if temp_user.startswith("anonymous_"):
                    enhanced_speaker_profiles.delete_user(temp_user)
                    print(f"[AdvancedCore] 🗑️ Deleted expired anonymous embedding: {temp_user}")
        except Exception as e:
            print(f"[AdvancedCore] ⚠️ Failed to delete temp embedding: {e}")

    def _process_negative_confirmation(self, audio, text):
        """❌ Process negative confirmation"""
        try:
            # Check if they provided their name in the rejection
            name = self._extract_name_smart(text, {})
            if name:
                print(f"[AdvancedCore] 👤 Name provided in rejection: {name}")
                return self._process_spontaneous_introduction(name, audio, text, {})

            # Otherwise, create new anonymous cluster
            self.pending_voice_confirmation = None

            # Create new cluster since they're not the suspected user
            if ENHANCED_MODULES_AVAILABLE:
                embedding = dual_voice_model_manager.generate_dual_embedding(audio)
                if embedding:
                    cluster_id = create_anonymous_cluster(embedding, {})
                    self.session_context['current_cluster'] = cluster_id
                    self.session_context['llm_locked'] = False

                    print(f"[AdvancedCore] 🆕 Created new cluster after rejection: {cluster_id}")
                    return cluster_id, "NEW_ANONYMOUS_AFTER_REJECTION"

            self.session_context['llm_locked'] = False
            return "Guest", "REJECTED_UNKNOWN"

        except Exception as e:
            print(f"[AdvancedCore] ❌ Negative confirmation error: {e}")
            return "Guest", "CONFIRMATION_ERROR"

    def _handle_uncertain_voice_match(self, candidate_users, similarity_scores, audio, text):
        """❓ Handle uncertain voice matches with confirmation"""
        try:
            if len(candidate_users) == 1:
                user = candidate_users[0]
                score = similarity_scores[0]
            
                # ✅ UNCERTAINTY RANGE: Ask for confirmation
                if 0.70 <= score <= 0.85:
                    print(f"[AdvancedCore] ❓ Uncertain match for {user} (score: {score:.3f})")
                
                    # Store confirmation data
                    self.pending_voice_confirmation = {
                        'candidate_user': user,
                        'similarity_score': score,
                        'audio_sample': audio.copy(),
                        'timestamp': time.time(),
                        'timeout_at': time.time() + self.confirmation_timeout
                    }
                
                    # ✅ ASK FOR CONFIRMATION
                    self._speak_confirmation_question(f"Is that you, {user}?")
                
                    return user, "CONFIRMATION_PENDING"
        
            elif len(candidate_users) > 1:
                # Multiple possible matches
                print(f"[AdvancedCore] ❓ Multiple possible matches: {candidate_users}")
            
                self.pending_voice_confirmation = {
                    'candidate_users': candidate_users,
                    'similarity_scores': similarity_scores,
                    'audio_sample': audio.copy(),
                    'timestamp': time.time(),
                    'timeout_at': time.time() + self.confirmation_timeout
                }
            
                # Ask which user it is
                user_list = " or ".join(candidate_users)
                self._speak_confirmation_question(f"Are you {user_list}?")
            
                return candidate_users[0], "MULTI_USER_CONFIRMATION_PENDING"
        
            return "Guest", "NO_MATCH"
        
        except Exception as e:
            print(f"[AdvancedCore] ❌ Uncertain voice match error: {e}")
            return "Guest", "ERROR"

    def _speak_confirmation_question(self, question):
        """🗣️ Speak confirmation question"""
        try:
            # Integration with your audio output system
            try:
                from audio.output import speak_streaming
                speak_streaming(question)
            except ImportError:
                print(f"[AdvancedCore] 🗣️ SPEAK: {question}")
        
            print(f"[AdvancedCore] 🗣️ Asked confirmation: {question}")
        except Exception as e:
            print(f"[AdvancedCore] ❌ Speech error: {e}")


    def _analyze_with_clustering(self, audio, identified_user, confidence, context_analysis):
        """🔍 ANALYZE WITH CLUSTERING - ADAPTIVE for voice variation (sick, emotion, volume)"""
        try:
            if not ENHANCED_MODULES_AVAILABLE:
                print("[AdvancedCore] ⚠️ Enhanced modules not available for clustering")
                return None
            
            # ✅ ENHANCED: Validate input audio first
            if audio is None or len(audio) == 0:
                print("[AdvancedCore] ❌ Invalid audio input for clustering")
                return None
            
            # ✅ ENHANCED: Generate embedding with retry logic
            embedding = None
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    print(f"[AdvancedCore] 🎯 Generating embedding (attempt {attempt + 1}/{max_retries})")
                    embedding = dual_voice_model_manager.generate_dual_embedding(audio)
                    
                    if embedding is not None:
                        if self._validate_embedding_structure(embedding):
                            print(f"[AdvancedCore] ✅ Valid embedding generated on attempt {attempt + 1}")
                            break
                        else:
                            print(f"[AdvancedCore] ⚠️ Invalid embedding structure on attempt {attempt + 1}")
                            embedding = None
                    else:
                        print(f"[AdvancedCore] ⚠️ Embedding generation returned None on attempt {attempt + 1}")
                    
                except Exception as embedding_error:
                    print(f"[AdvancedCore] ❌ Embedding generation error (attempt {attempt + 1}): {embedding_error}")
                    embedding = None
                    
                    if "import" in str(embedding_error).lower() or "module" in str(embedding_error).lower():
                        print(f"[AdvancedCore] ❌ Critical import error, stopping retries")
                        break
            
            if embedding is None:
                print(f"[AdvancedCore] ❌ Failed to generate valid embedding after {max_retries} attempts")
                return {
                    'similar_clusters': [],
                    'should_create_cluster': False,
                    'should_merge_cluster': False,
                    'recommended_cluster': None,
                    'cluster_confidence': 0.0,
                    'error': 'embedding_generation_failed'
                }
            
            # 🔧 NEW: ADAPTIVE SIMILARITY THRESHOLD based on voice conditions
            voice_conditions = self._analyze_voice_conditions(audio, context_analysis)
            adaptive_threshold = self._calculate_adaptive_threshold(voice_conditions)
            
            print(f"[AdvancedCore] 🎤 Voice conditions: {voice_conditions}")
            print(f"[AdvancedCore] 🎯 Adaptive threshold: {adaptive_threshold:.3f}")
            
            # ✅ Find similar clusters with ADAPTIVE threshold
            similar_clusters = []
            try:
                print(f"[AdvancedCore] 🔍 Searching with adaptive threshold {adaptive_threshold:.3f}...")
                similar_clusters = find_similar_clusters(embedding, threshold=adaptive_threshold)
                print(f"[AdvancedCore] 📊 Found {len(similar_clusters)} similar clusters")
                
                # Debug: Show cluster similarities
                for i, cluster in enumerate(similar_clusters):
                    print(f"[AdvancedCore]   📊 Cluster {i+1}: {cluster['cluster_id']} (similarity: {cluster['similarity']:.3f})")
                
            except Exception as cluster_search_error:
                print(f"[AdvancedCore] ❌ Cluster search error: {cluster_search_error}")
            
            # ✅ Get audio quality
            quality_info = context_analysis.get('audio_quality', {})
            quality_score = quality_info.get('overall_score', 0.5)
            clustering_suitability = quality_info.get('clustering_suitability', 'unknown')
            
            print(f"[AdvancedCore] 📊 Audio quality: {quality_score:.2f}, Clustering suitability: {clustering_suitability}")
            
            # ✅ Initialize clustering result
            clustering_result = {
                'similar_clusters': similar_clusters,
                'should_create_cluster': False,
                'should_merge_cluster': False,
                'recommended_cluster': None,
                'cluster_confidence': 0.0,
                'audio_quality_score': quality_score,
                'clustering_suitability': clustering_suitability,
                'embedding_valid': True,
                'analysis_method': 'adaptive_voice_variation',
                'voice_conditions': voice_conditions,
                'adaptive_threshold_used': adaptive_threshold
            }
            
            # ✅ ADAPTIVE DECISION LOGIC
            print(f"[AdvancedCore] 🤔 Decision factors: user={identified_user}, confidence={confidence:.3f}")
            
            if identified_user == "UNKNOWN" or confidence < 0.4:
                # ✅ Quality check
                if clustering_suitability in ['unusable', 'error']:
                    print(f"[AdvancedCore] ❌ Audio quality too poor for clustering: {clustering_suitability}")
                    clustering_result['should_create_cluster'] = False
                    clustering_result['should_merge_cluster'] = False
                    clustering_result['error'] = 'poor_audio_quality'
                    return clustering_result
                
                if similar_clusters:
                    # 🔧 NEW: ADAPTIVE MERGE THRESHOLDS based on voice conditions
                    best_cluster = similar_clusters[0]
                    cluster_confidence = best_cluster['similarity']
                    
                    merge_threshold = self._calculate_adaptive_merge_threshold(voice_conditions, clustering_suitability)
                    
                    print(f"[AdvancedCore] 🎯 ADAPTIVE MERGE ANALYSIS:")
                    print(f"[AdvancedCore]   📊 Cluster similarity: {cluster_confidence:.3f}")
                    print(f"[AdvancedCore]   📊 Adaptive merge threshold: {merge_threshold:.3f}")
                    print(f"[AdvancedCore]   🎤 Voice conditions: {voice_conditions}")
                    
                    if cluster_confidence >= merge_threshold:
                        clustering_result['should_merge_cluster'] = True
                        clustering_result['recommended_cluster'] = best_cluster['cluster_id']
                        clustering_result['cluster_confidence'] = cluster_confidence
                        
                        print(f"[AdvancedCore] 🔗 ADAPTIVE MERGE: {best_cluster['cluster_id']} "
                              f"(similarity: {cluster_confidence:.3f} >= {merge_threshold:.3f})")
                        print(f"[AdvancedCore] 🎤 SAME SPEAKER with voice variation: {voice_conditions}")
                    else:
                        clustering_result['should_create_cluster'] = True
                        print(f"[AdvancedCore] 🆕 CREATE DECISION: Different speaker "
                              f"(similarity: {cluster_confidence:.3f} < {merge_threshold:.3f})")
                        
                else:
                    # No similar clusters found
                    if quality_score >= 0.3 and clustering_suitability not in ['unusable']:
                        clustering_result['should_create_cluster'] = True
                        print(f"[AdvancedCore] 🆕 CREATE DECISION: No similar clusters - NEW SPEAKER")
                    else:
                        print(f"[AdvancedCore] ❌ SKIP clustering: Quality too low")
            else:
                print(f"[AdvancedCore] ✅ KNOWN user: {identified_user} - no clustering needed")
            
            return clustering_result
            
        except Exception as e:
            print(f"[AdvancedCore] ❌ Clustering analysis critical error: {e}")
            traceback.print_exc()
            
            return {
                'similar_clusters': [],
                'should_create_cluster': False,
                'should_merge_cluster': False,
                'recommended_cluster': None,
                'cluster_confidence': 0.0,
                'error': f'critical_error: {str(e)}',
                'embedding_valid': False,
                'analysis_method': 'error_fallback'
            }

    def _analyze_voice_conditions(self, audio, context_analysis):
        """🎤 Analyze current voice conditions (emotion, health, volume, etc.)"""
        try:
            conditions = {
                'volume_level': 'normal',
                'emotional_state': 'neutral',
                'health_condition': 'normal',
                'environmental_stress': 'low',
                'voice_variation_detected': False
            }
            
            # Analyze volume (whisper, normal, loud)
            volume = np.abs(audio).mean()
            peak = np.max(np.abs(audio))
            
            if volume < 500:
                conditions['volume_level'] = 'whisper'
                conditions['voice_variation_detected'] = True
            elif volume > 3000:
                conditions['volume_level'] = 'loud'
                conditions['voice_variation_detected'] = True
            else:
                conditions['volume_level'] = 'normal'
            
            # Analyze potential health issues (congestion, etc.)
            audio_quality = context_analysis.get('audio_quality', {})
            snr_db = audio_quality.get('snr_db', 20)
            spectral_quality = audio_quality.get('spectral_quality', 0.5)
            
            if snr_db < 10 or spectral_quality < 0.3:
                conditions['health_condition'] = 'potentially_sick'
                conditions['voice_variation_detected'] = True
            elif snr_db < 15 or spectral_quality < 0.4:
                conditions['health_condition'] = 'mild_variation'
                conditions['voice_variation_detected'] = True
            
            # Analyze emotional/energy state (simplified)
            dynamic_range = peak - np.min(np.abs(audio))
            if dynamic_range > 4000:
                conditions['emotional_state'] = 'energetic'
                conditions['voice_variation_detected'] = True
            elif dynamic_range < 1000:
                conditions['emotional_state'] = 'subdued'
                conditions['voice_variation_detected'] = True
            
            # Environmental stress
            noise_level = audio_quality.get('noise_score', 1.0)
            if noise_level < 0.5:
                conditions['environmental_stress'] = 'high'
                conditions['voice_variation_detected'] = True
            elif noise_level < 0.7:
                conditions['environmental_stress'] = 'medium'
            
            return conditions
            
        except Exception as e:
            print(f"[AdvancedCore] ❌ Voice condition analysis error: {e}")
            return {'voice_variation_detected': False}

    def _calculate_adaptive_threshold(self, voice_conditions):
        """🎯 Calculate adaptive threshold based on voice conditions"""
        try:
            base_threshold = 0.80  # More lenient base than 0.85
            
            # Adjust based on voice conditions
            if voice_conditions.get('voice_variation_detected', False):
                # Lower threshold for voice variations
                adjustment = 0.0
                
                # Volume adjustments
                if voice_conditions.get('volume_level') == 'whisper':
                    adjustment -= 0.10  # Much more lenient for whispers
                elif voice_conditions.get('volume_level') == 'loud':
                    adjustment -= 0.08  # More lenient for loud speech
                
                # Health adjustments
                if voice_conditions.get('health_condition') == 'potentially_sick':
                    adjustment -= 0.12  # Very lenient for sick voice
                elif voice_conditions.get('health_condition') == 'mild_variation':
                    adjustment -= 0.06
                
                # Emotional adjustments
                if voice_conditions.get('emotional_state') in ['energetic', 'subdued']:
                    adjustment -= 0.05
                
                # Environmental adjustments
                if voice_conditions.get('environmental_stress') == 'high':
                    adjustment -= 0.07
                elif voice_conditions.get('environmental_stress') == 'medium':
                    adjustment -= 0.03
                
                final_threshold = base_threshold + adjustment
            else:
                # Normal conditions - use stricter threshold
                final_threshold = 0.85
            
            # Ensure reasonable bounds
            final_threshold = max(0.65, min(0.90, final_threshold))
            
            return final_threshold
            
        except Exception as e:
            print(f"[AdvancedCore] ❌ Adaptive threshold calculation error: {e}")
            return 0.80

    def _calculate_adaptive_merge_threshold(self, voice_conditions, clustering_suitability):
        """🎯 Calculate adaptive merge threshold"""
        try:
            base_merge_threshold = 0.82  # More lenient base
            
            # Adjust for voice variations
            if voice_conditions.get('voice_variation_detected', False):
                adjustment = 0.0
                
                # More lenient for known voice variations
                if voice_conditions.get('volume_level') == 'whisper':
                    adjustment -= 0.15  # Very lenient for whispers
                elif voice_conditions.get('volume_level') == 'loud':
                    adjustment -= 0.10
                
                if voice_conditions.get('health_condition') == 'potentially_sick':
                    adjustment -= 0.18  # Extra lenient for sick voice
                elif voice_conditions.get('health_condition') == 'mild_variation':
                    adjustment -= 0.08
                
                if voice_conditions.get('emotional_state') in ['energetic', 'subdued']:
                    adjustment -= 0.06
                
                if voice_conditions.get('environmental_stress') == 'high':
                    adjustment -= 0.08
                
                final_threshold = base_merge_threshold + adjustment
            else:
                # Normal conditions
                if clustering_suitability == 'excellent':
                    final_threshold = 0.85
                elif clustering_suitability == 'good':
                    final_threshold = 0.88
                else:
                    final_threshold = 0.90
            
            # Ensure reasonable bounds (prevent false positives but allow voice variation)
            final_threshold = max(0.70, min(0.92, final_threshold))
            
            return final_threshold
            
        except Exception as e:
            print(f"[AdvancedCore] ❌ Adaptive merge threshold calculation error: {e}")
            return 0.82

    def _check_session_continuity(self, current_cluster_id, new_similarity):
        """Check if this is likely the same speaker continuing"""
        try:
            last_interaction_time = self.session_context.get('last_interaction_time')
            current_time = time.time()
            
            # If less than 30 seconds since last speech, be more lenient
            if last_interaction_time and (current_time - last_interaction_time) < 30:
                return True  # Likely same speaker continuing
            
            # If longer gap, be more strict
            return False
        except Exception as e:
            print(f"[AdvancedCore] ❌ Session continuity check error: {e}")
            return False

    def _detect_voice_drift(self, cluster_id, current_embedding):
        """Detect if voice is gradually changing (illness, etc.)"""
        try:
            if cluster_id not in anonymous_clusters:
                return "no_cluster"
            
            recent_embeddings = anonymous_clusters[cluster_id]['embeddings'][-5:]
            similarities = []
            
            for emb in recent_embeddings:
                sim = dual_voice_model_manager.compare_dual_embeddings(current_embedding, emb)
                similarities.append(sim)
            
            # Check for gradual drift vs sudden change
            if similarities:
                trend = np.polyfit(range(len(similarities)), similarities, 1)[0]
                if trend < -0.02:  # Gradual decline
                    return "gradual_change"  # Illness, fatigue, etc.
                elif similarities[-1] < 0.7:  # Sudden change
                    return "sudden_change"   # Different speaker
            
            return "stable"
        except Exception as e:
            print(f"[AdvancedCore] ❌ Voice drift detection error: {e}")
            return "error"

    def _multi_factor_validation(self, cluster_id, audio, text):
        """Use multiple factors beyond just voice similarity"""
        try:
            factors = {
                'voice_similarity': 0.0,
                'speaking_pattern': 0.0,
                'vocabulary_match': 0.0,
                'time_pattern': 0.0
            }
            
            # Voice similarity (primary)
            factors['voice_similarity'] = self._calculate_voice_similarity(cluster_id, audio)
            
            # Speaking patterns (secondary)
            factors['speaking_pattern'] = self._analyze_speaking_patterns(cluster_id, audio)
            
            # Vocabulary/phrases (tertiary)
            factors['vocabulary_match'] = self._analyze_vocabulary_patterns(cluster_id, text)
            
            # Time patterns (quaternary)
            factors['time_pattern'] = self._analyze_time_patterns(cluster_id)
            
            # Weighted decision
            weighted_score = (
                factors['voice_similarity'] * 0.70 +
                factors['speaking_pattern'] * 0.15 +
                factors['vocabulary_match'] * 0.10 +
                factors['time_pattern'] * 0.05
            )
            
            return weighted_score > 0.75, factors
        except Exception as e:
            print(f"[AdvancedCore] ❌ Multi-factor validation error: {e}")
            return False, {}

    def _calculate_voice_similarity(self, cluster_id, audio):
        """Calculate voice similarity for multi-factor validation"""
        try:
            if cluster_id not in anonymous_clusters:
                return 0.0
            
            current_embedding = dual_voice_model_manager.generate_dual_embedding(audio)
            if not current_embedding:
                return 0.0
            
            cluster_embeddings = anonymous_clusters[cluster_id]['embeddings']
            if not cluster_embeddings:
                return 0.0
            
            similarities = []
            for emb in cluster_embeddings[-3:]:  # Check last 3 embeddings
                sim = dual_voice_model_manager.compare_dual_embeddings(current_embedding, emb)
                similarities.append(sim)
            
            return np.mean(similarities) if similarities else 0.0
        except Exception as e:
            print(f"[AdvancedCore] ❌ Voice similarity calculation error: {e}")
            return 0.0

    def _analyze_speaking_patterns(self, cluster_id, audio):
        """Analyze speaking patterns (pace, rhythm, etc.)"""
        try:
            # Simplified speaking pattern analysis
            # In a real implementation, this would analyze:
            # - Speaking pace
            # - Pause patterns
            # - Intonation patterns
            # - Volume dynamics
            
            # For now, return a basic pattern score
            volume_variance = np.var(np.abs(audio))
            normalized_variance = min(volume_variance / 10000, 1.0)
            
            return normalized_variance
        except Exception as e:
            print(f"[AdvancedCore] ❌ Speaking pattern analysis error: {e}")
            return 0.5

    def _analyze_vocabulary_patterns(self, cluster_id, text):
        """Analyze vocabulary and phrase patterns"""
        try:
            # Simple vocabulary pattern matching
            # In a real implementation, this would check:
            # - Common phrases used by this cluster
            # - Vocabulary sophistication level
            # - Speaking style patterns
            
            if not text or len(text.strip()) < 3:
                return 0.5
            
            # Basic pattern: longer text suggests more confidence
            text_length_score = min(len(text) / 100, 1.0)
            
            return text_length_score
        except Exception as e:
            print(f"[AdvancedCore] ❌ Vocabulary pattern analysis error: {e}")
            return 0.5

    def _analyze_time_patterns(self, cluster_id):
        """Analyze time-based interaction patterns"""
        try:
            current_hour = datetime.utcnow().hour
            
            # Check if this cluster has consistent time patterns
            if cluster_id in self.behavioral_patterns:
                patterns = self.behavioral_patterns[cluster_id]
                interaction_times = patterns.get('interaction_times', [])
                
                if interaction_times:
                    # Check if current time matches typical interaction times
                    time_matches = [abs(t - current_hour) <= 2 for t in interaction_times[-10:]]
                    return sum(time_matches) / len(time_matches)
            
            return 0.5  # Neutral if no pattern data
        except Exception as e:
            print(f"[AdvancedCore] ❌ Time pattern analysis error: {e}")
            return 0.5

    def _handle_uncertain_recognition(self, similarity_score, cluster_id):
        """Handle cases where confidence is borderline"""
        try:
            if 0.75 <= similarity_score <= 0.85:  # Uncertain range
                print(f"[AdvancedCore] ❓ UNCERTAIN recognition: {similarity_score:.3f}")
                print(f"[AdvancedCore] 🤔 This could be voice variation or different speaker")
                
                # Use multi-factor validation for uncertain cases
                is_valid, factors = self._multi_factor_validation(cluster_id, None, "")
                
                if is_valid:
                    print(f"[AdvancedCore] ✅ Multi-factor validation confirms match")
                    return "merge_with_validation"
                else:
                    print(f"[AdvancedCore] ❌ Multi-factor validation suggests different speaker")
                    return "create_new_cluster"
            
            return "proceed_normal"
        except Exception as e:
            print(f"[AdvancedCore] ❌ Uncertain recognition handling error: {e}")
            return "create_new_cluster"

    def get_last_audio_sample(self):
        """Get the most recent audio sample from passive buffer"""
        try:
            if self.recent_audio_buffer:
                return self.recent_audio_buffer[-1]  # Most recent
            return None
        except Exception as e:
            print(f"[AdvancedCore] ❌ Error getting last audio: {e}")
            return None

    def get_current_speaker_identity(self):
        """Get current speaker identity from advanced processing"""
        try:
            return self.session_context.get('last_recognized_user', None)
        except Exception as e:
            print(f"[AdvancedCore] ❌ Error getting speaker identity: {e}")
            return None

    def _add_to_passive_buffer(self, audio, text, context):
        """✅ PASSIVE AUDIO BUFFER - Always collecting like Alexa"""
        try:
            # Add to circular buffer (keep last 10 interactions)
            self.recent_audio_buffer.append(audio.copy() if audio is not None else None)
            self.recent_text_buffer.append(text)
            self.buffer_contexts.append({
                'context': context,
                'timestamp': datetime.utcnow().isoformat(),
                'interaction_id': self.session_context['interactions']
            })
            
            # Keep buffer size manageable
            if len(self.recent_audio_buffer) > 10:
                self.recent_audio_buffer = self.recent_audio_buffer[-10:]
                self.recent_text_buffer = self.recent_text_buffer[-10:]
                self.buffer_contexts = self.buffer_contexts[-10:]
            
            print(f"[AdvancedCore] 🎤 Buffered audio sample (total: {len(self.recent_audio_buffer)})")
            
        except Exception as e:
            print(f"[AdvancedCore] ❌ Buffer error: {e}")

    def _analyze_comprehensive_context(self, audio, text):
        """🧠 ADVANCED CONTEXT ANALYSIS"""
        if ENHANCED_MODULES_AVAILABLE and self.context_analyzer:
            try:
                context_analysis = self.context_analyzer.analyze_comprehensive_context(audio, text)
                
                # ✅ ENHANCE with clustering context
                context_analysis['clustering_context'] = {
                    'active_clusters': len(self.active_anonymous_clusters),
                    'session_interactions': self.session_context['interactions'],
                    'last_recognized': self.session_context['last_recognized_user'],
                    'current_cluster': self.session_context['current_cluster']
                }
                
                return context_analysis
            except Exception as e:
                print(f"[AdvancedCore] ⚠️ Context analysis error: {e}")
                return self._basic_context_analysis(audio, text)
        else:
            return self._basic_context_analysis(audio, text)

    def _advanced_voice_recognition(self, audio, context_analysis):
        """🎯 Enhanced recognition with multi-candidate detection"""
        try:
            if ENHANCED_MODULES_AVAILABLE:
                # ✅ GET ALL USER SIMILARITIES
                all_user_similarities = self._get_all_user_similarities(audio)

                # Find candidates above threshold
                candidates = []
                scores = []

                threshold = 0.70  # Lower threshold to catch uncertain matches

                for user, score in all_user_similarities.items():
                    if score >= threshold:
                        candidates.append(user)
                        scores.append(score)

                # Sort by confidence (highest first)
                if candidates:
                    sorted_pairs = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
                    candidates = [pair[0] for pair in sorted_pairs]
                    scores = [pair[1] for pair in sorted_pairs]

                    print(f"[AdvancedCore] 🎯 Voice candidates: {list(zip(candidates, scores))}")

                    # ✅ CHECK FOR UNCERTAINTY OR MULTIPLE MATCHES
                    if len(candidates) > 1 or (len(candidates) == 1 and scores[0] < 0.85):
                        return self._handle_uncertain_voice_match(candidates, scores, audio, "")
                    else:
                        # High confidence single match
                        user = candidates[0]
                        confidence = scores[0]
                        return {
                            'primary_user': user,
                            'primary_confidence': confidence,
                            'clustering_result': None,
                            'debug_info': {'method': 'high_confidence_direct'},
                            'method': 'enhanced_direct'
                        }

                # No matches in known users - proceed with clustering
                clustering_result = self._analyze_with_clustering(audio, "UNKNOWN", 0.0, context_analysis)
                return {
                    'primary_user': "UNKNOWN",
                    'primary_confidence': 0.0,
                    'clustering_result': clustering_result,
                    'debug_info': {'method': 'clustering_fallback'},
                    'method': 'enhanced_clustering'
                }
            else:
                # Basic fallback
                try:
                    from voice.recognition import identify_speaker_with_confidence
                    identified_user, confidence = identify_speaker_with_confidence(audio)
                except ImportError:
                    identified_user, confidence = "UNKNOWN", 0.0

                return {
                    'primary_user': identified_user,
                    'primary_confidence': confidence,
                    'clustering_result': None,
                    'debug_info': {'method': 'basic'},
                    'method': 'basic'
                }

        except Exception as e:
            print(f"[AdvancedCore] ❌ Recognition error: {e}")
            return {
                'primary_user': "UNKNOWN",
                'primary_confidence': 0.0,
                'clustering_result': None,
                'debug_info': {'error': str(e)},
                'method': 'error'
            }

    def _validate_embedding_structure(self, embedding):
        """✅ Validate embedding structure"""
        try:
            if embedding is None:
                return False
            
            # Check if it's a dictionary with expected structure
            if isinstance(embedding, dict):
                # Should contain some embedding data
                if not embedding:
                    return False
                
                # Check for common embedding keys
                expected_keys = ['resemblyzer', 'wav2vec2', 'ecapa', 'data', 'features']
                has_valid_key = any(key in embedding for key in expected_keys)
                
                if not has_valid_key:
                    print(f"[AdvancedCore] ⚠️ Embedding dict missing expected keys. Keys found: {list(embedding.keys())}")
                    return False
                
                # Try to convert to JSON to ensure it's serializable
                import json
                json.dumps(embedding)
                return True
            
            # Check if it's a numpy array
            if isinstance(embedding, np.ndarray):
                if embedding.size == 0:
                    return False
                
                # Check for reasonable embedding dimensions
                if embedding.ndim > 2 or embedding.size > 10000:  # Reasonable limits
                    print(f"[AdvancedCore] ⚠️ Embedding dimensions seem unreasonable: shape={embedding.shape}")
                    return False
                
                return True
            
            # Check if it's already a list
            if isinstance(embedding, list):
                if not embedding:
                    return False
                
                # Check for reasonable size
                if len(embedding) > 10000:
                    print(f"[AdvancedCore] ⚠️ Embedding list too large: {len(embedding)} elements")
                    return False
                
                # Try to convert to JSON
                import json
                json.dumps(embedding)
                return True
            
            print(f"[AdvancedCore] ⚠️ Unexpected embedding type: {type(embedding)}")
            return False
            
        except Exception as e:
            print(f"[AdvancedCore] ⚠️ Embedding validation error: {e}")
            return False

    def _make_intelligent_decision(self, recognition_result, context_analysis, audio, text):
        """🧠 INTELLIGENT DECISION MAKING - Alexa/Siri level"""
        
        primary_user = recognition_result['primary_user']
        primary_confidence = recognition_result['primary_confidence']
        clustering_result = recognition_result['clustering_result']
        
        # ✅ PRIORITY 1: Handle name confirmations
        if self.pending_name_confirmation:
            return self._handle_name_confirmation(text, audio, context_analysis)
        
        # ✅ PRIORITY 2: Handle waiting for name
        if self.waiting_for_name:
            return self._handle_name_waiting(text, audio, context_analysis)
        
        # ✅ PRIORITY 3: HIGH CONFIDENCE RECOGNITION
        if primary_user != "UNKNOWN" and primary_confidence >= 0.8:
            return self._handle_high_confidence_recognition(primary_user, primary_confidence, audio, context_analysis)
        
        # ✅ PRIORITY 4: MEDIUM CONFIDENCE with context enhancement
        if primary_user != "UNKNOWN" and primary_confidence >= 0.5:
            return self._handle_medium_confidence_recognition(primary_user, primary_confidence, audio, context_analysis)
        
        # ✅ PRIORITY 5: CLUSTERING-BASED RECOGNITION
        if clustering_result:
            return self._handle_clustering_recognition(clustering_result, audio, text, context_analysis)
        
        # ✅ PRIORITY 6: UNKNOWN SPEAKER - Advanced handling
        return self._handle_unknown_speaker_advanced(audio, text, context_analysis)

    def _handle_high_confidence_recognition(self, user, confidence, audio, context_analysis):
        """✅ HIGH CONFIDENCE - Add passive learning"""
        print(f"[AdvancedCore] ✅ HIGH CONFIDENCE: {user} ({confidence:.3f})")
        
        # ✅ UNLOCK LLM
        self.session_context['llm_locked'] = False
        
        # ✅ PASSIVE LEARNING
        if ENHANCED_MODULES_AVAILABLE:
            try:
                enhanced_speaker_profiles.add_passive_sample(user, audio, confidence)
                enhanced_speaker_profiles.tune_threshold_for_user(user)
            except Exception as e:
                print(f"[AdvancedCore] ⚠️ Passive learning error: {e}")
        
        # ✅ UPDATE SESSION
        self.session_context['last_recognized_user'] = user
        self.session_context['current_cluster'] = user
        
        # ✅ BEHAVIORAL ADAPTATION
        self._update_behavioral_patterns(user, context_analysis)
        
        return user, "RECOGNIZED"

    def _handle_medium_confidence_recognition(self, user, confidence, audio, context_analysis):
        """✅ MEDIUM CONFIDENCE - Context enhancement"""
        print(f"[AdvancedCore] 🤔 MEDIUM CONFIDENCE: {user} ({confidence:.3f})")
        
        # ✅ CONTEXT ENHANCEMENT
        if ENHANCED_MODULES_AVAILABLE and self.context_analyzer:
            try:
                context_user = context_analysis.get('likely_user', {}).get('predicted_user')
                context_confidence = context_analysis.get('likely_user', {}).get('confidence', 0.0)
                
                if context_user == user and context_confidence > 0.8:
                    print(f"[AdvancedCore] 🎯 CONTEXT CONFIRMS: {user}")
                    self.session_context['llm_locked'] = False
                    self.session_context['last_recognized_user'] = user
                    return user, "LIKELY"
            except Exception as e:
                print(f"[AdvancedCore] ⚠️ Context enhancement error: {e}")
        
        # ✅ BEHAVIORAL CONFIRMATION
        if self._check_behavioral_patterns(user, context_analysis):
            print(f"[AdvancedCore] 🎯 BEHAVIORAL CONFIRMS: {user}")
            self.session_context['llm_locked'] = False
            self.session_context['last_recognized_user'] = user
            return user, "LIKELY"
        
        # ✅ STILL UNCERTAIN - Keep learning
        if ENHANCED_MODULES_AVAILABLE:
            try:
                enhanced_speaker_profiles._store_uncertain_sample(audio, f"medium_confidence_{user}")
            except Exception as e:
                print(f"[AdvancedCore] ⚠️ Uncertain sample storage error: {e}")
        
        return user, "UNCERTAIN"

    def _handle_clustering_recognition(self, clustering_result, audio, text, context_analysis):
        """🔍 CLUSTERING-BASED RECOGNITION - FIXED VERSION"""
        try:
            if clustering_result['should_merge_cluster']:
                # ✅ MERGE WITH EXISTING CLUSTER
                cluster_id = clustering_result['recommended_cluster']
                cluster_confidence = clustering_result['cluster_confidence']
                
                print(f"[AdvancedCore] 🔗 MERGING with cluster: {cluster_id}")
                
                # Add to existing cluster
                self._add_to_anonymous_cluster(cluster_id, audio, text, context_analysis)
                
                # ✅ CRITICAL: SET CURRENT CLUSTER
                self.session_context['current_cluster'] = cluster_id
                self.session_context['llm_locked'] = False  # ✅ UNLOCK LLM
                
                return cluster_id, "ANONYMOUS_RECOGNIZED"
                
            elif clustering_result['should_create_cluster']:
                # ✅ CREATE NEW ANONYMOUS CLUSTER
                quality_info = context_analysis.get('audio_quality', {})
                embedding = dual_voice_model_manager.generate_dual_embedding(audio)
                
                if embedding:
                    cluster_id = create_anonymous_cluster(embedding, quality_info)
                    
                    print(f"[AdvancedCore] 🆕 CREATED cluster: {cluster_id}")
                    
                    # ✅ CRITICAL: SET CURRENT CLUSTER
                    self.session_context['current_cluster'] = cluster_id
                    self.session_context['llm_locked'] = False  # ✅ UNLOCK LLM
                    
                    return cluster_id, "ANONYMOUS_RECOGNIZED"
            
            return "Guest", "CLUSTERING_FAILED"
            
        except Exception as e:
            print(f"[AdvancedCore] ❌ Clustering recognition error: {e}")
            return "Guest", "CLUSTERING_ERROR"

    def _handle_unknown_speaker_advanced(self, audio, text, context_analysis):
        """❓ UNKNOWN SPEAKER - Advanced handling"""
        
        # ✅ CHECK FOR SPONTANEOUS NAME INTRODUCTION
        if self._is_spontaneous_introduction(text):
            name = self._extract_name_smart(text, context_analysis)
            if name:
                print(f"[AdvancedCore] 👤 SPONTANEOUS introduction: {name}")
                return self._process_spontaneous_introduction(name, audio, text, context_analysis)
        
        # ✅ CREATE ANONYMOUS CLUSTER and ANSWER NATURALLY
        try:
            if ENHANCED_MODULES_AVAILABLE:
                embedding = dual_voice_model_manager.generate_dual_embedding(audio)
                if embedding:
                    quality_info = context_analysis.get('audio_quality', {})
                    cluster_id = create_anonymous_cluster(embedding, quality_info)
                    
                    print(f"[AdvancedCore] 🆕 UNKNOWN → Created {cluster_id}")
                    
                    # ✅ ANSWER NATURALLY - Don't ask for name
                    self.session_context['current_cluster'] = cluster_id
                    self.session_context['llm_locked'] = False  # ✅ UNLOCK LLM
                    
                    return cluster_id, "ANONYMOUS_RECOGNIZED"
        except Exception as e:
            print(f"[AdvancedCore] ❌ Anonymous cluster creation error: {e}")
        
        # ✅ FALLBACK - Still answer naturally
        self.session_context['llm_locked'] = False
        return "Guest", "ANONYMOUS_FALLBACK"

    def _process_spontaneous_introduction(self, name, audio, text, context_analysis):
        """👤 PROCESS SPONTANEOUS NAME INTRODUCTION with ALL buffered audio"""
        try:
            # ✅ SAME NAME COLLISION HANDLING
            final_name = handle_same_name_collision(name)
        
            combined_audio_chunks = []
        
            # 1. Add all valid audio from the passive buffer.
            for buffered_audio in self.recent_audio_buffer:
                if buffered_audio is not None and len(buffered_audio) > SAMPLE_RATE * 0.5:
                    combined_audio_chunks.append(buffered_audio)
        
            # 2. CRITICAL: Add the current audio chunk that triggered the introduction.
            if audio is not None and len(audio) > SAMPLE_RATE * 0.5:
                # Ensure we don't add the same chunk twice if it's already in the buffer
                if not any(np.array_equal(audio, chunk) for chunk in combined_audio_chunks):
                    combined_audio_chunks.append(audio)
            
            print(f"[AdvancedCore] 🎯 Registering {final_name} with {len(combined_audio_chunks)} audio chunks.")
        
            # ✅ CRITICAL FIX: Only proceed if we have enough audio chunks.
            if len(combined_audio_chunks) >= 1:
                success = self._register_voice_with_multiple_chunks(final_name, combined_audio_chunks)
            
                if success:
                    # Link the most recent anonymous cluster to this new user
                    if self.session_context.get('current_cluster', '').startswith('Anonymous_'):
                        cluster_id = self.session_context['current_cluster']
                        if link_anonymous_to_named(cluster_id, final_name):
                            print(f"[AdvancedCore] 🔗 Linked anonymous cluster {cluster_id} to {final_name}")
                        else:
                            print(f"[AdvancedCore] ❌ Failed to link {cluster_id} to {final_name}")
                    
                            from voice.database import save_known_users
                            save_result = save_known_users()
                            if save_result:
                                print(f"[AdvancedCore] 💾 Database saved after linking cluster to name")

                    # Update session state
                    self.session_context['last_recognized_user'] = final_name
                    self.session_context['current_cluster'] = final_name
                    self.session_context['llm_locked'] = False
                
                    return final_name, "INTRODUCED_AND_SAVED"
                else:
                    print(f"[AdvancedCore] ❌ Registration failed for {final_name} despite having audio chunks.")
                    return final_name, "INTRODUCED_BUT_SAVE_FAILED"
            else:
                print(f"[AdvancedCore] ❌ Not enough valid audio in buffer to create profile for {final_name}.")
                return final_name, "INTRODUCED_NO_PROFILE"
        
        except Exception as e:
            print(f"[AdvancedCore] ❌ Spontaneous introduction error: {e}")
            traceback.print_exc()
            return name, "INTRODUCED_ERROR"

    def _register_voice_with_multiple_chunks(self, username, audio_chunks):
        """🎯 Register voice with multiple audio chunks"""
        try:
            print(f"[AdvancedCore] 🎯 Registering {len(audio_chunks)} chunks for {username}")
        
            if ENHANCED_MODULES_AVAILABLE:
                # Use the enhanced profile creation which handles saving internally.
                success = enhanced_speaker_profiles.create_enhanced_profile(
                    username=username,
                    audio_samples=audio_chunks,
                    training_type='spontaneous_multi_chunk'
                )
            
                if success:
                    # ✅ VERIFY the profile was actually saved
                    if username in known_users:
                        profile = known_users[username]
                        if 'embeddings' in profile and len(profile['embeddings']) > 0:
                            print(f"[AdvancedCore] ✅ Enhanced profile for {username} created and verified in memory.")
                            
                            # ✅ VERIFY file was saved
                            try:
                                from voice.database import KNOWN_USERS_PATH
                                if os.path.exists(KNOWN_USERS_PATH):
                                    print(f"[AdvancedCore] ✅ Database file exists, profile should be persisted.")
                                    return True
                                else:
                                    print(f"[AdvancedCore] ❌ Database file missing after profile creation!")
                                    return False
                            except Exception as e:
                                print(f"[AdvancedCore] ⚠️ Could not verify database file: {e}")
                                return True  # Assume success if we can't verify
                        else:
                            print(f"[AdvancedCore] ❌ Profile in memory but no embeddings found!")
                            return False
                    else:
                        print(f"[AdvancedCore] ❌ Profile not found in memory after creation!")
                        return False
                else:
                    # If enhanced creation fails, attempt the fallback.
                    print(f"[AdvancedCore] ❌ Enhanced profile creation failed for {username}. Attempting fallback.")
                    return self._fallback_register_chunks(username, audio_chunks)
            else:
                # If enhanced modules aren't available, go directly to the fallback.
                print("[AdvancedCore] 🔄 Enhanced modules not available. Using basic registration fallback.")
                return self._fallback_register_chunks(username, audio_chunks)
            
        except Exception as e:
            print(f"[AdvancedCore] ❌ An error occurred during multi-chunk registration: {e}")
            traceback.print_exc()
            return False

    def _add_to_anonymous_cluster(self, cluster_id, audio, text, context_analysis):
        """➕ ADD TO ANONYMOUS CLUSTER"""
        try:
            if cluster_id not in anonymous_clusters:
                print(f"[AdvancedCore] ❌ Cluster {cluster_id} not found")
                return False
            
            if ENHANCED_MODULES_AVAILABLE:
                embedding = dual_voice_model_manager.generate_dual_embedding(audio)
                if embedding:
                    cluster_data = anonymous_clusters[cluster_id]
                    cluster_data['embeddings'].append(embedding)
                    cluster_data['sample_count'] += 1
                    cluster_data['last_updated'] = datetime.utcnow().isoformat()
                    cluster_data.setdefault('audio_contexts', []).append(f"interaction_{self.session_context['interactions']}")
                    
                    # Keep cluster size manageable
                    if len(cluster_data['embeddings']) > 10:
                        cluster_data['embeddings'] = cluster_data['embeddings'][-10:]
                    
                    # ✅ VERIFY SAVE OPERATION
                    save_result = save_known_users()
                    if save_result:
                        print(f"[AdvancedCore] ✅ Added to {cluster_id} and saved successfully")
                        return True
                    else:
                        print(f"[AdvancedCore] ❌ Failed to save after adding to {cluster_id}")
                        return False
                else:
                    print(f"[AdvancedCore] ❌ Failed to generate embedding for {cluster_id}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"[AdvancedCore] ❌ Cluster addition error: {e}")
            traceback.print_exc()
            return False

    def _fallback_register_chunks(self, username, audio_chunks):
        """🔄 Fallback: Register each chunk individually"""
        try:
            try:
                from voice.recognition import register_voice
            except ImportError:
                print("[AdvancedCore] ❌ Cannot import register_voice for fallback")
                return False
            
            success_count = 0
            for i, chunk in enumerate(audio_chunks):
                if register_voice(chunk, username):
                    success_count += 1
                    print(f"[AdvancedCore] ✅ Registered chunk {i+1}/{len(audio_chunks)}")
                else:
                    print(f"[AdvancedCore] ❌ Failed chunk {i+1}/{len(audio_chunks)}")
            
            # Consider success if at least half the chunks worked
            success = success_count >= len(audio_chunks) // 2
            print(f"[AdvancedCore] 📊 Chunk registration: {success_count}/{len(audio_chunks)} = {'SUCCESS' if success else 'FAILED'}")
            
            return success
            
        except Exception as e:
            print(f"[AdvancedCore] ❌ Fallback registration error: {e}")
            return False

    def _update_behavioral_patterns(self, user, context_analysis):
        """📊 UPDATE BEHAVIORAL PATTERNS"""
        try:
            if user not in self.behavioral_patterns:
                self.behavioral_patterns[user] = {
                    'common_phrases': [],
                    'audio_quality_preference': [],
                    'interaction_times': [],
                    'context_patterns': []
                }
            
            # Update patterns
            patterns = self.behavioral_patterns[user]
            patterns['interaction_times'].append(datetime.utcnow().hour)
            patterns['audio_quality_preference'].append(context_analysis.get('audio_quality', {}).get('score', 0.5))
            
            # Keep recent patterns only
            if len(patterns['interaction_times']) > 50:
                patterns['interaction_times'] = patterns['interaction_times'][-50:]
                patterns['audio_quality_preference'] = patterns['audio_quality_preference'][-50:]
            
        except Exception as e:
            print(f"[AdvancedCore] ❌ Behavioral pattern error: {e}")

    def _check_behavioral_patterns(self, user, context_analysis):
        """🔍 CHECK BEHAVIORAL PATTERNS"""
        try:
            if user not in self.behavioral_patterns:
                return False
            
            patterns = self.behavioral_patterns[user]
            current_hour = datetime.utcnow().hour
            
            # Check time patterns
            if patterns['interaction_times']:
                common_hours = [h for h in patterns['interaction_times'] if abs(h - current_hour) <= 2]
                if len(common_hours) >= 3:
                    print(f"[AdvancedCore] 🕐 Time pattern match for {user}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"[AdvancedCore] ❌ Behavioral check error: {e}")
            return False

    def _is_spontaneous_introduction(self, text):
        """🔍 CHECK FOR SPONTANEOUS INTRODUCTION"""
        intro_patterns = [
            "my name is", "i'm ", "i am ", "call me ", "this is ",
            "it's ", "name's ", "i go by "
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in intro_patterns)

    def _extract_name_smart(self, text, context_analysis):
        """🧠 SMART NAME EXTRACTION"""
        if ENHANCED_MODULES_AVAILABLE and self.name_manager:
            try:
                return self.name_manager.extract_name_mega_intelligent(text)
            except Exception as e:
                print(f"[AdvancedCore] ⚠️ Smart name extraction error: {e}")
                return self._extract_basic_name(text)
        else:
            return self._extract_basic_name(text)

    def _extract_basic_name(self, text):
        """Basic name extraction with better validation"""
        import re
        
        patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)(?:\s*,|\s*$|\s+by\s+the\s+way)",
            r"i am (\w+)",
            r"call me (\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                name = match.group(1).title()
                if self._is_valid_name(name):
                    return name
        
        return None

    def _is_valid_name(self, name):
        """Enhanced name validation - NO COMPUTER LOGIN NAMES"""
        if not name or len(name) < 2 or len(name) > 20:
            return False
    
        if not name.isalpha():
            return False
    
        name_lower = name.lower()
    
        # ❌ BLOCK computer login names
        computer_logins = {'daveydrz', 'admin', 'user', 'guest', 'root', 'system'}
        if name_lower in computer_logins:
            print(f"[AdvancedCore] 🛡️ BLOCKED computer login: {name}")
            return False
    
        # ❌ BLOCK obvious non-names
        non_names = {
            'hello', 'hey', 'buddy', 'yes', 'no', 'okay', 'thanks', 'good',
            'doing', 'going', 'working', 'feeling', 'thinking', 'fine', 'tired', 'busy'
        }
        if name_lower in non_names:
            print(f"[AdvancedCore] 🛡️ BLOCKED non-name: {name}")
            return False
    
        # ✅ ALLOW legitimate person names
        legitimate_names = {'david', 'francesco', 'frank', 'dave', 'davey'}
        if name_lower in legitimate_names:
            print(f"[AdvancedCore] ✅ LEGITIMATE person name: {name}")
            return True
    
        # ✅ For unknown names, allow if they pass basic checks
        return True

    def _distinguish_computer_vs_person_name(self, detected_name):
        """🔍 Distinguish between computer login and actual person name"""
        if not detected_name:
            return None, "no_name"
        
        name_lower = detected_name.lower()
        
        # Computer login names (never use as person names)
        if name_lower == 'daveydrz':
            print(f"[AdvancedCore] 🖥️ COMPUTER LOGIN detected: {detected_name} - NOT a person name")
            return None, "computer_login"
        
        # Legitimate person names
        person_names = {'david', 'francesco', 'frank', 'dave', 'davey'}
        if name_lower in person_names:
            print(f"[AdvancedCore] 👤 PERSON NAME detected: {detected_name}")
            return detected_name, "person_name"
        
        # Unknown but potentially valid person name
        if self._is_valid_name(detected_name):
            print(f"[AdvancedCore] ❓ UNKNOWN but potentially valid person name: {detected_name}")
            return detected_name, "unknown_person_name"
        
        print(f"[AdvancedCore] ❌ INVALID name: {detected_name}")
        return None, "invalid_name"

    def _handle_name_confirmation(self, text, audio, context_analysis):
        """Handle name confirmation - DISABLED for natural flow"""
        print("[AdvancedCore] ⚠️ Name confirmation bypassed for natural conversation")
        self.pending_name_confirmation = False
        self.suggested_name = None
        # Create anonymous cluster instead
        return self._handle_unknown_speaker_advanced(audio, text, context_analysis)

    def _handle_name_waiting(self, text, audio, context_analysis):
        """Handle waiting for name - DISABLED for natural flow"""
        print("[AdvancedCore] ⚠️ Name waiting bypassed for natural conversation")
        self.waiting_for_name = False
        # Create anonymous cluster instead
        return self._handle_unknown_speaker_advanced(audio, text, context_analysis)

    def _process_name_interaction(self, name_result, audio, text):
        """Process name-related interactions"""
        # Implementation for name management
        return name_result

    def _basic_context_analysis(self, audio, text):
        """Basic context analysis fallback"""
        return {
            'audio_quality': {'overall_score': 0.5, 'clustering_suitability': 'unknown', 'snr_db': 20, 'spectral_quality': 0.5, 'noise_score': 1.0},
            'environmental_noise': {'environment': 'unknown'},
            'likely_user': {'predicted_user': None},
            'clustering_context': {'active_clusters': 0}
        }

    def handle_training_response(self, text):
        """Handle training response (legacy compatibility)"""
        # Implementation for training offers
        return "NO_TRAINING_PENDING"

    def get_session_stats(self):
        """Get advanced session statistics"""
        duration = (datetime.utcnow() - self.session_context['start_time']).total_seconds() / 60
        
        return {
            'session_duration_minutes': duration,
            'total_interactions': self.session_context['interactions'],
            'last_recognized_user': self.session_context['last_recognized_user'],
            'current_cluster': self.session_context['current_cluster'],
            'session_type': self.session_context['session_type'],
            'enhanced_modules': ENHANCED_MODULES_AVAILABLE,
            'active_anonymous_clusters': len(self.active_anonymous_clusters),
            'llm_locked': self.session_context['llm_locked'],
            'behavioral_patterns_learned': len(self.behavioral_patterns)
        }

    def is_llm_locked(self):
        """✅ Check if LLM is locked"""
        return self.session_context.get('llm_locked', False)

    def unlock_llm(self):
        """✅ Unlock LLM for responses"""
        self.session_context['llm_locked'] = False
        print("[AdvancedCore] 🔓 LLM unlocked")

    def lock_llm(self):
        """✅ Lock LLM until user identity confirmed"""
        self.session_context['llm_locked'] = True
        print("[AdvancedCore] 🔒 LLM locked")

    def _run_periodic_maintenance(self):
        """🔧 Run periodic maintenance"""
        try:
            print(f"[AdvancedCore] 🔧 Running periodic maintenance...")
            
            # ✅ MERGE PASSIVE SAMPLES for all users
            if ENHANCED_MODULES_AVAILABLE:
                for username in known_users.keys():
                    if not username.startswith('Anonymous_'):
                        try:
                            merge_count = enhanced_speaker_profiles.merge_passive_samples(username)
                            if merge_count > 0:
                                print(f"[AdvancedCore] 🔗 Merged {merge_count} samples for {username}")
                        except Exception as e:
                            print(f"[AdvancedCore] ⚠️ Merge error for {username}: {e}")
            
            # ✅ CLEANUP OLD ANONYMOUS CLUSTERS
            try:
                from voice.database import cleanup_old_anonymous_clusters
                cleanup_old_anonymous_clusters(max_age_days=7)
            except Exception as e:
                print(f"[AdvancedCore] ⚠️ Cleanup error: {e}")
            
            print(f"[AdvancedCore] ✅ Periodic maintenance complete")
            
        except Exception as e:
            print(f"[AdvancedCore] ❌ Maintenance error: {e}")

# ✅ SINGLE INITIALIZATION ONLY
if ENHANCED_MODULES_AVAILABLE:
    voice_manager = AdvancedAIAssistantCore()
    print("[ManagerCore] 🚀 Advanced AI Assistant initialized")
else:
    print("[ManagerCore] ⚠️ Using basic mode")
    
    # Create a basic fallback
    class BasicCoreManager:
        def handle_voice_identification(self, audio, text):
            return "Guest", "BASIC_FALLBACK"
        def is_llm_locked(self):
            return False
    
    voice_manager = BasicCoreManager()