# voice/speaker_profiles.py - Advanced speaker profiles with clustering and AI intelligence  
import json
import os
import time
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging
import pickle
import gzip

from voice.database import known_users, anonymous_clusters, save_known_users
from config import *

logger = logging.getLogger(__name__)

class AdvancedSpeakerProfiles:
    """🎯 Advanced speaker profile management with clustering intelligence"""
    
    def __init__(self):
        self.quality_threshold = 0.4  # Minimum audio quality
        self.max_embeddings_per_user = 15  # Store multiple embeddings (like Alexa)
        self.max_raw_samples = 10  # Store raw audio for re-training
        self.confidence_logs = {}  # Log similarity scores over time
        self.uncertain_samples = {}  # Store uncertain samples for retraining
        
        # ✅ CLUSTERING INTELLIGENCE
        self.cluster_quality_cache = {}
        self.user_adaptation_history = {}
        self.behavioral_voice_patterns = {}
        
        # Ensure directories exist
        os.makedirs("voice_profiles/raw_audio", exist_ok=True)
        os.makedirs("voice_profiles/uncertain", exist_ok=True)
        os.makedirs("voice_profiles/clusters", exist_ok=True)  # ✅ NEW
        
        print("[AdvancedSpeakerProfiles] 🎯 Advanced AI speaker profiling initialized")
    
    def assess_audio_quality_advanced(self, audio: np.ndarray) -> Dict[str, Any]:
        """🔊 Advanced audio quality assessment with clustering optimization"""
        try:
            if audio is None or len(audio) == 0:
                return {
                    'overall_score': 0.0,
                    'volume_score': 0.0,
                    'noise_score': 0.0,
                    'clarity_score': 0.0,
                    'duration_score': 0.0,
                    'snr_db': 0.0,
                    'spectral_quality': 0.0,
                    'clustering_suitability': 'poor',  # ✅ NEW
                    'issues': ['no_audio'],
                    'auto_discard': True
                }
            
            # Basic metrics
            duration = len(audio) / SAMPLE_RATE
            volume = np.abs(audio).mean()
            peak = np.max(np.abs(audio))
            rms = np.sqrt(np.mean(audio**2))
            
            # Advanced noise analysis
            noise_floor = np.percentile(np.abs(audio), 5)
            signal_level = np.percentile(np.abs(audio), 95)
            snr_db = 20 * np.log10((signal_level + 1e-6) / (noise_floor + 1e-6))
            
            # Spectral analysis for voice quality
            try:
                from scipy import signal as sp_signal
                f, psd = sp_signal.welch(audio, SAMPLE_RATE, nperseg=min(1024, len(audio)//4))
                
                # Voice frequency range analysis (85Hz - 8kHz for speech)
                voice_low = (f >= 85) & (f <= 300)   # Fundamental frequency
                voice_mid = (f >= 300) & (f <= 3400) # Main speech band
                voice_high = (f >= 3400) & (f <= 8000) # Consonants/clarity
                
                voice_energy = np.sum(psd[voice_mid])
                total_energy = np.sum(psd)
                voice_ratio = voice_energy / (total_energy + 1e-6)
                
                # Spectral centroid (brightness indicator)
                spectral_centroid = np.sum(f * psd) / (np.sum(psd) + 1e-6)
                
                spectral_quality = min(1.0, voice_ratio * 2.0)  # Favor speech frequencies
                
            except ImportError:
                spectral_quality = 0.5  # Neutral if scipy not available
                voice_ratio = 0.5
            
            # Scoring system (0.0 to 1.0)
            scores = {}
            issues = []
            
            # Volume score (optimized for speech)
            if 200 <= volume <= 3000:
                scores['volume_score'] = 1.0
            elif 100 <= volume < 200 or 3000 < volume <= 5000:
                scores['volume_score'] = 0.8
                if volume < 200:
                    issues.append('low_volume')
                else:
                    issues.append('loud_volume')
            elif 50 <= volume < 100 or 5000 < volume <= 8000:
                scores['volume_score'] = 0.5
                if volume < 100:
                    issues.append('very_low_volume')
                else:
                    issues.append('very_loud_volume')
            else:
                scores['volume_score'] = 0.2
                issues.append('volume_extreme')
            
            # Noise score (based on SNR)
            if snr_db > 25:
                scores['noise_score'] = 1.0
            elif snr_db > 20:
                scores['noise_score'] = 0.9
            elif snr_db > 15:
                scores['noise_score'] = 0.7
            elif snr_db > 10:
                scores['noise_score'] = 0.5
                issues.append('moderate_noise')
            elif snr_db > 5:
                scores['noise_score'] = 0.3
                issues.append('high_noise')
            else:
                scores['noise_score'] = 0.1
                issues.append('very_high_noise')
            
            # Clarity score (spectral quality)
            scores['clarity_score'] = spectral_quality
            if spectral_quality < 0.3:
                issues.append('poor_clarity')
            
            # Duration score
            if 1.0 <= duration <= 6.0:
                scores['duration_score'] = 1.0
            elif 0.7 <= duration < 1.0 or 6.0 < duration <= 10.0:
                scores['duration_score'] = 0.8
            elif 0.5 <= duration < 0.7 or 10.0 < duration <= 15.0:
                scores['duration_score'] = 0.6
                if duration < 0.7:
                    issues.append('short_duration')
                else:
                    issues.append('long_duration')
            else:
                scores['duration_score'] = 0.3
                if duration < 0.5:
                    issues.append('too_short')
                else:
                    issues.append('too_long')
            
            # Clipping detection
            clipping_threshold = 0.98 * np.max(np.abs(audio))
            clipping_ratio = np.sum(np.abs(audio) >= clipping_threshold) / len(audio)
            if clipping_ratio > 0.01:  # More than 1% clipping
                issues.append('clipping')
                scores['volume_score'] *= 0.6  # Significant penalty for clipping
            
            # Silence detection
            silence_threshold = np.max(np.abs(audio)) * 0.02
            silence_ratio = np.sum(np.abs(audio) < silence_threshold) / len(audio)
            if silence_ratio > 0.3:  # More than 30% silence
                issues.append('too_much_silence')
                scores['clarity_score'] *= 0.7
            
            # Overall score (weighted combination)
            overall_score = (
                0.25 * scores['volume_score'] +
                0.30 * scores['noise_score'] +
                0.25 * scores['clarity_score'] +
                0.20 * scores['duration_score']
            )
            
            # ✅ CLUSTERING SUITABILITY ASSESSMENT
            clustering_suitability = self._assess_clustering_suitability(
                overall_score, snr_db, spectral_quality, duration, issues
            )
            
            # Auto-discard decision
            auto_discard = (
                overall_score < self.quality_threshold or
                'clipping' in issues or
                'too_short' in issues or
                'volume_extreme' in issues or
                snr_db < 3 or  # Extremely poor SNR
                clustering_suitability == 'unusable'
            )
            
            return {
                'overall_score': overall_score,
                'volume_score': scores['volume_score'],
                'noise_score': scores['noise_score'],
                'clarity_score': scores['clarity_score'],
                'duration_score': scores['duration_score'],
                'snr_db': snr_db,
                'spectral_quality': spectral_quality,
                'voice_ratio': voice_ratio,
                'volume': volume,
                'duration': duration,
                'clipping_ratio': clipping_ratio,
                'silence_ratio': silence_ratio,
                'clustering_suitability': clustering_suitability,  # ✅ NEW
                'issues': issues,
                'auto_discard': auto_discard
            }
        
        except Exception as e:
            logger.error(f"Advanced audio quality assessment error: {e}")
            return {
                'overall_score': 0.0,
                'clustering_suitability': 'error',
                'issues': ['assessment_error'],
                'auto_discard': True
            }
    
    def _assess_clustering_suitability(self, overall_score, snr_db, spectral_quality, duration, issues):
        """🔍 Assess how suitable audio is for clustering"""
        try:
            # Multiple factors determine clustering suitability
            suitability_score = 0.0
            
            # Overall quality contribution (40%)
            suitability_score += 0.4 * overall_score
            
            # SNR contribution (30%)
            if snr_db > 20:
                suitability_score += 0.3
            elif snr_db > 15:
                suitability_score += 0.25
            elif snr_db > 10:
                suitability_score += 0.15
            elif snr_db > 5:
                suitability_score += 0.05
            
            # Duration contribution (20%)
            if 1.5 <= duration <= 5.0:
                suitability_score += 0.2
            elif 1.0 <= duration < 1.5 or 5.0 < duration <= 8.0:
                suitability_score += 0.15
            elif 0.8 <= duration < 1.0:
                suitability_score += 0.1
            
            # Spectral quality contribution (10%)
            suitability_score += 0.1 * spectral_quality
            
            # Penalty for critical issues
            critical_issues = ['clipping', 'volume_extreme', 'too_short', 'very_high_noise']
            for issue in critical_issues:
                if issue in issues:
                    suitability_score -= 0.2
            
            # Determine suitability level
            if suitability_score >= 0.8:
                return 'excellent'
            elif suitability_score >= 0.65:
                return 'good'
            elif suitability_score >= 0.45:
                return 'fair'
            elif suitability_score >= 0.25:
                return 'poor'
            else:
                return 'unusable'
                
        except Exception as e:
            return 'unknown'
    
    def save_raw_audio_sample(self, username: str, audio: np.ndarray, context: str = "training") -> str:
        """💾 Save raw audio sample for future re-training"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{username}_{context}_{timestamp}.pkl.gz"
            filepath = os.path.join("voice_profiles/raw_audio", filename)
            
            # Compress and save
            audio_data = {
                'audio': audio.tolist(),
                'username': username,
                'context': context,
                'timestamp': timestamp,
                'sample_rate': SAMPLE_RATE,
                'quality_info': self.assess_audio_quality_advanced(audio)
            }
            
            with gzip.open(filepath, 'wb') as f:
                pickle.dump(audio_data, f)
            
            logger.info(f"Saved raw audio sample: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to save raw audio sample: {e}")
            return ""
    
    def load_raw_audio_samples(self, username: str) -> List[np.ndarray]:
        """📂 Load raw audio samples for re-training"""
        try:
            samples = []
            raw_audio_dir = "voice_profiles/raw_audio"
            
            if not os.path.exists(raw_audio_dir):
                return samples
            
            for filename in os.listdir(raw_audio_dir):
                if filename.startswith(f"{username}_") and filename.endswith('.pkl.gz'):
                    filepath = os.path.join(raw_audio_dir, filename)
                    try:
                        with gzip.open(filepath, 'rb') as f:
                            audio_data = pickle.load(f)
                            samples.append(np.array(audio_data['audio']))
                    except Exception as e:
                        logger.warning(f"Failed to load {filename}: {e}")
            
            logger.info(f"Loaded {len(samples)} raw audio samples for {username}")
            return samples
            
        except Exception as e:
            logger.error(f"Failed to load raw audio samples: {e}")
            return []

    def create_enhanced_profile(self, username: str, audio_samples: List[np.ndarray], 
                                training_type: str = 'formal') -> bool:
        """🧠 Create advanced profile with clustering intelligence"""
        try:
            # ✅ IMPROVED: Better import error handling
            try:
                from voice.voice_models import dual_voice_model_manager
            except ImportError as import_error:
                logger.error(f"Failed to import voice models: {import_error}")
                print(f"[AdvancedProfiles] ❌ Voice models import failed: {import_error}")
                return False
            
            # ✅ IMPROVED: Input validation
            if not username or not username.strip():
                logger.error("Username cannot be empty")
                return False
            
            if not audio_samples or len(audio_samples) == 0:
                logger.error("No audio samples provided")
                return False
            
            # Clean username
            username = username.strip()
            
            embeddings = []
            quality_scores = []
            embedding_metadata = []
            stored_samples = 0
            clustering_metrics = []
            
            logger.info(f"Creating advanced profile for {username} with {len(audio_samples)} samples")
            print(f"[AdvancedProfiles] 🎯 Starting profile creation for {username}")
            
            for i, audio in enumerate(audio_samples):
                try:
                    # ✅ IMPROVED: Validate audio sample
                    if audio is None or len(audio) == 0:
                        logger.warning(f"Skipping empty audio sample {i+1}")
                        continue
                    
                    # Advanced quality assessment with clustering focus
                    quality = self.assess_audio_quality_advanced(audio)
                    
                    print(f"[AdvancedProfiles] Sample {i+1}: Quality {quality['overall_score']:.2f}, "
                          f"SNR {quality['snr_db']:.1f}dB, Clustering: {quality['clustering_suitability']}")
                    
                    # Save raw audio (even if discarded, for analysis)
                    if stored_samples < self.max_raw_samples:
                        try:
                            filename = self.save_raw_audio_sample(username, audio, f"training_{i+1}")
                            if filename:
                                stored_samples += 1
                        except Exception as save_error:
                            logger.warning(f"Failed to save raw audio sample {i+1}: {save_error}")
                            # Continue processing even if raw save fails
                    
                    # ✅ CLUSTERING-AWARE QUALITY FILTERING
                    if quality['auto_discard'] or quality['clustering_suitability'] == 'unusable':
                        logger.warning(f"Auto-discarded sample {i+1}: {quality['issues']}")
                        continue
                    
                    # Generate dual embeddings
                    try:
                        embedding_result = dual_voice_model_manager.generate_dual_embedding(audio)
                        if embedding_result is not None:
                            # ✅ IMPROVED: Validate embedding result
                            if not self._validate_embedding(embedding_result):
                                logger.warning(f"Invalid embedding for sample {i+1}")
                                continue
                            
                            embeddings.append(embedding_result)
                            quality_scores.append(quality['overall_score'])
                            
                            # ✅ CLUSTERING METADATA
                            clustering_metrics.append({
                                'clustering_suitability': quality['clustering_suitability'],
                                'snr_db': quality['snr_db'],
                                'spectral_quality': quality['spectral_quality'],
                                'voice_ratio': quality.get('voice_ratio', 0.5)
                            })
                            
                            embedding_metadata.append({
                                'sample_index': i,
                                'snr_db': quality['snr_db'],
                                'spectral_quality': quality['spectral_quality'],
                                'clustering_suitability': quality['clustering_suitability'],
                                'issues': quality['issues'],
                                'timestamp': datetime.utcnow().isoformat()
                            })
                            
                            logger.info(f"Accepted sample {i+1}: Quality {quality['overall_score']:.2f}, "
                                       f"Clustering: {quality['clustering_suitability']}")
                        else:
                            logger.warning(f"Failed to generate embedding for sample {i+1}")
                            
                    except Exception as embedding_error:
                        logger.error(f"Embedding generation error for sample {i+1}: {embedding_error}")
                        continue
                        
                except Exception as sample_error:
                    logger.error(f"Error processing sample {i+1}: {sample_error}")
                    continue
            
            # ✅ IMPROVED: Better minimum embedding check
            min_embeddings = 1  # Reduced from 3 for more flexibility
            if len(embeddings) >= min_embeddings:
                try:
                    # ✅ ADVANCED THRESHOLD CALCULATION with clustering intelligence
                    dynamic_threshold = self._calculate_clustering_aware_threshold(
                        embeddings, quality_scores, clustering_metrics
                    )
                    
                    # ✅ BEHAVIORAL PATTERN INITIALIZATION
                    behavioral_patterns = self._initialize_behavioral_patterns(
                        username, embeddings, quality_scores
                    )
                    
                    profile_data = {
                        'username': username,
                        'embeddings': embeddings,
                        'quality_scores': quality_scores,
                        'embedding_metadata': embedding_metadata,
                        'clustering_metrics': clustering_metrics,
                        'behavioral_patterns': behavioral_patterns,
                        'raw_samples_stored': stored_samples,
                        'created_date': datetime.utcnow().isoformat(),
                        'last_updated': datetime.utcnow().isoformat(),
                        'training_type': training_type,
                        'samples_used': len(embeddings),
                        'samples_total': len(audio_samples),
                        'status': 'trained',
                        'confidence_threshold': dynamic_threshold,
                        'recognition_count': 0,
                        'recognition_history': [],
                        'recognition_successes': 0,
                        'recognition_failures': 0,
                        'previous_names': [],
                        'embedding_version': '2.0_clustering_enhanced',
                        'voice_model_info': self._get_model_info_safely(dual_voice_model_manager),
                        'clustering_enabled': True,
                        'adaptation_enabled': True,
                    }
                    
                    # ✅ IMPROVED: Validate profile data before saving
                    if not self._validate_profile_data(profile_data):
                        logger.error(f"Profile data validation failed for {username}")
                        return False
                    
                    # ✅ CRITICAL FIX: Proper save with verification and error handling
                    try:
                        print(f"[AdvancedProfiles] 💾 Saving profile for {username}...")
                        
                        # Add to global known_users dictionary
                        known_users[username] = profile_data
                        
                        # Attempt to save the entire database to file
                        save_result = save_known_users()
                        if save_result:
                            # If save is successful, the profile is persisted.
                            print(f"[AdvancedProfiles] ✅ Profile successfully saved for {username}")
                            print(f"[AdvancedProfiles] 📊 Profile details: {len(embeddings)} embeddings, threshold {dynamic_threshold:.3f}")
                            
                            # Initialize user tracking systems
                            try:
                                self._initialize_user_tracking(username, profile_data)
                            except Exception as tracking_error:
                                logger.warning(f"User tracking initialization failed: {tracking_error}")
                                # Don't fail the entire operation for tracking errors
                            
                            logger.info(f"Advanced profile created for {username}: {len(embeddings)} embeddings, threshold {dynamic_threshold:.3f}")
                            return True
                        else:
                            # If save_known_users() returns False
                            print(f"[AdvancedProfiles] ❌ Save operation failed for {username}. Reverting.")
                            logger.error(f"save_known_users() returned False for {username}")
                            
                            # CLEANUP: Remove from memory if save failed to maintain consistency
                            if username in known_users:
                                del known_users[username]
                            return False
                            
                    except Exception as save_error:
                        print(f"[AdvancedProfiles] ❌ Exception during save for {username}: {save_error}")
                        logger.error(f"Save exception for {username}: {save_error}")
                        
                        # CLEANUP: Also remove from memory on exception
                        if username in known_users:
                            del known_users[username]
                        return False
                        
                except Exception as profile_creation_error:
                    logger.error(f"Profile creation error for {username}: {profile_creation_error}")
                    return False
            else:
                logger.error(f"Not enough quality samples for {username}: {len(embeddings)}/{min_embeddings}")
                print(f"[AdvancedProfiles] ❌ Insufficient quality samples: {len(embeddings)}/{min_embeddings}")
                return False
            
        except Exception as e:
            logger.error(f"Advanced profile creation error: {e}")
            print(f"[AdvancedProfiles] ❌ Critical error: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ✅ FIXED: Proper indentation as class method
    def _validate_embedding(self, embedding) -> bool:
        """✅ NEW: Validate embedding data"""
        try:
            if embedding is None:
                return False
            
            # Check if it's a dictionary with expected structure
            if isinstance(embedding, dict):
                # Should contain some embedding data
                if not embedding:
                    return False
                
                # Try to convert to JSON to ensure it's serializable
                import json
                json.dumps(embedding)
                return True
            
            # Check if it's a numpy array
            if isinstance(embedding, np.ndarray):
                if embedding.size == 0:
                    return False
                
                # Try to convert to list (JSON serializable)
                embedding.tolist()
                return True
            
            # Check if it's already a list
            if isinstance(embedding, list):
                if not embedding:
                    return False
                
                # Try to convert to JSON
                import json
                json.dumps(embedding)
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Embedding validation error: {e}")
            return False

    # ✅ FIXED: Proper indentation as class method
    def _validate_profile_data(self, profile_data: Dict) -> bool:
        """✅ NEW: Validate profile data before saving"""
        try:
            required_fields = ['username', 'embeddings', 'created_date', 'status']
            
            for field in required_fields:
                if field not in profile_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            # Validate embeddings are not empty
            if not profile_data['embeddings']:
                logger.error("No embeddings in profile")
                return False
            
            # Validate username is not empty
            if not profile_data['username'] or not profile_data['username'].strip():
                logger.error("Username is empty")
                return False
            
            # Validate embeddings are JSON-serializable
            try:
                import json
                json.dumps(profile_data['embeddings'])
            except (TypeError, ValueError) as e:
                logger.error(f"Embeddings not JSON-serializable: {e}")
                return False
            
            # Validate other critical fields
            if not isinstance(profile_data.get('quality_scores', []), list):
                logger.error("Quality scores must be a list")
                return False
            
            if not isinstance(profile_data.get('confidence_threshold', 0.5), (int, float)):
                logger.error("Confidence threshold must be a number")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Profile validation error: {e}")
            return False

    # ✅ FIXED: Proper indentation as class method
    def _get_model_info_safely(self, model_manager) -> Dict:
        """✅ NEW: Safely get model info"""
        try:
            return model_manager.get_model_info()
        except Exception as e:
            logger.warning(f"Failed to get model info: {e}")
            return {
                'model_name': 'unknown',
                'version': 'unknown',
                'error': str(e)
            }

    def _calculate_clustering_aware_threshold(self, embeddings: List[Dict], 
                                           quality_scores: List[float],
                                           clustering_metrics: List[Dict]) -> float:
        """🎯 Calculate clustering-aware confidence threshold"""
        try:
            from voice.voice_models import dual_voice_model_manager
            
            # Calculate inter-embedding similarities
            similarities = []
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    sim = dual_voice_model_manager.compare_dual_embeddings(embeddings[i], embeddings[j])
                    similarities.append(sim)
            
            if similarities:
                # Statistical analysis of similarities
                mean_sim = np.mean(similarities)
                std_sim = np.std(similarities)
                min_sim = np.min(similarities)
                
                # ✅ CLUSTERING-AWARE ADJUSTMENT
                clustering_quality_bonus = 0.0
                for metric in clustering_metrics:
                    if metric['clustering_suitability'] == 'excellent':
                        clustering_quality_bonus += 0.02
                    elif metric['clustering_suitability'] == 'good':
                        clustering_quality_bonus += 0.01
                
                clustering_quality_bonus = min(0.1, clustering_quality_bonus / len(clustering_metrics))
                
                # Conservative threshold: mean - 1.5 * std, but not below minimum similarity
                base_threshold = max(min_sim * 0.9, mean_sim - 1.5 * std_sim)
                
                # Quality-based adjustment
                avg_quality = np.mean(quality_scores)
                quality_bonus = (avg_quality - 0.5) * 0.1  # Up to 0.1 bonus for high quality
                
                # Final threshold with clustering awareness
                final_threshold = np.clip(
                    base_threshold + quality_bonus + clustering_quality_bonus, 
                    0.3, 0.85
                )
                
                logger.info(f"Clustering-aware threshold: mean={mean_sim:.3f}, std={std_sim:.3f}, "
                           f"clustering_bonus={clustering_quality_bonus:.3f}, final={final_threshold:.3f}")
                return final_threshold
            else:
                return VOICE_CONFIDENCE_THRESHOLD
                
        except Exception as e:
            logger.error(f"Clustering-aware threshold calculation error: {e}")
            return VOICE_CONFIDENCE_THRESHOLD
    
    def _initialize_behavioral_patterns(self, username: str, embeddings: List[Dict], 
                                      quality_scores: List[float]) -> Dict:
        """🎭 Initialize behavioral patterns for user"""
        try:
            patterns = {
                'voice_consistency': np.std(quality_scores) if len(quality_scores) > 1 else 0.0,
                'preferred_quality_range': [min(quality_scores), max(quality_scores)],
                'adaptation_rate': 'medium',  # How quickly to adapt to voice changes
                'clustering_affinity': 'high',  # How well voice clusters
                'recognition_difficulty': 'normal',  # Expected recognition difficulty
                'voice_characteristics': {
                    'stability': 'good' if np.std(quality_scores) < 0.2 else 'variable',
                    'distinctiveness': 'high',  # Will be updated based on recognition performance
                    'environmental_sensitivity': 'unknown'  # Will be learned over time
                }
            }
            
            # Initialize in behavioral tracking
            self.behavioral_voice_patterns[username] = {
                'creation_date': datetime.utcnow().isoformat(),
                'patterns': patterns,
                'adaptation_history': [],
                'recognition_patterns': []
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Behavioral pattern initialization error: {e}")
            return {}
    
    def _initialize_user_tracking(self, username: str, profile_data: Dict):
        """📊 Initialize user tracking systems"""
        try:
            # Initialize confidence logging
            self.confidence_logs[username] = []
            
            # Initialize adaptation history
            self.user_adaptation_history[username] = {
                'threshold_changes': [],
                'quality_improvements': [],
                'recognition_improvements': [],
                'last_adaptation': None
            }
            
            # Initialize cluster quality cache
            self.cluster_quality_cache[username] = {
                'last_assessment': datetime.utcnow().isoformat(),
                'quality_trend': 'stable',
                'clustering_effectiveness': 'unknown'
            }
            
        except Exception as e:
            logger.error(f"User tracking initialization error: {e}")
    
    def recognize_with_multiple_embeddings(self, audio: np.ndarray) -> Tuple[str, float, Dict]:
        """🎯 Advanced recognition with clustering intelligence"""
        try:
            from voice.voice_models import dual_voice_model_manager
            
            if not known_users:
                return "UNKNOWN", 0.0, {'reason': 'no_profiles'}
            
            # Generate test embedding
            test_embedding = dual_voice_model_manager.generate_dual_embedding(audio)
            if test_embedding is None:
                return "UNKNOWN", 0.0, {'reason': 'embedding_failed'}
            
            # Assess input quality with clustering awareness
            input_quality = self.assess_audio_quality_advanced(audio)
            
            # ✅ CLUSTERING-AWARE QUALITY FILTERING
            if input_quality['auto_discard'] or input_quality['clustering_suitability'] == 'unusable':
                self._store_uncertain_sample(audio, f"poor_input_quality_{input_quality['clustering_suitability']}")
                return "UNKNOWN", 0.0, {
                    'reason': 'poor_input_quality', 
                    'quality': input_quality,
                    'clustering_suitability': input_quality['clustering_suitability']
                }
            
            best_user = None
            best_confidence = 0.0
            debug_info = {
                'input_quality': input_quality['overall_score'],
                'input_snr': input_quality['snr_db'],
                'clustering_suitability': input_quality['clustering_suitability'],
                'candidates': {},
                'comparison_method': 'clustering_enhanced_multi_embedding'
            }
            
            for username, profile in known_users.items():
                if not isinstance(profile, dict) or 'embeddings' not in profile:
                    continue
                
                # ✅ CLUSTERING-ENHANCED COMPARISON
                user_confidence = self._calculate_clustering_aware_confidence(
                    test_embedding, profile, input_quality
                )
                
                if user_confidence['final_confidence'] > best_confidence:
                    user_threshold = profile.get('confidence_threshold', VOICE_CONFIDENCE_THRESHOLD)
                    
                    if user_confidence['final_confidence'] >= user_threshold:
                        best_confidence = user_confidence['final_confidence']
                        best_user = username
                
                debug_info['candidates'][username] = user_confidence
            
            # Log recognition attempt for adaptive learning
            if best_user:
                self._log_recognition_result(best_user, best_confidence, True, input_quality)
                self._update_recognition_stats(best_user, True)
                
                # ✅ BEHAVIORAL ADAPTATION
                self._update_behavioral_patterns(best_user, input_quality, best_confidence)
            else:
                # Store uncertain sample for potential clustering
                if best_confidence > 0.3:  # Some similarity but below threshold
                    candidate = max(debug_info['candidates'].items(), key=lambda x: x[1]['final_confidence'])[0]
                    self._store_uncertain_sample(audio, f"low_confidence_{candidate}_{best_confidence:.2f}")
            
            return best_user or "UNKNOWN", best_confidence, debug_info
            
        except Exception as e:
            logger.error(f"Clustering-enhanced recognition error: {e}")
            return "UNKNOWN", 0.0, {'reason': 'error', 'error': str(e)}
    
    def _calculate_clustering_aware_confidence(self, test_embedding: Dict, profile: Dict, 
                                             input_quality: Dict) -> Dict:
        """🔍 Calculate clustering-aware confidence score"""
        try:
            from voice.voice_models import dual_voice_model_manager
            
            similarities = []
            quality_weights = profile.get('quality_scores', [1.0] * len(profile['embeddings']))
            clustering_metrics = profile.get('clustering_metrics', [])
            
            for i, stored_embedding in enumerate(profile['embeddings']):
                similarity = dual_voice_model_manager.compare_dual_embeddings(test_embedding, stored_embedding)
                
                # ✅ CLUSTERING-AWARE WEIGHTING
                quality_weight = quality_weights[i] if i < len(quality_weights) else 1.0
                
                # Additional clustering-based weighting
                clustering_weight = 1.0
                if i < len(clustering_metrics):
                    clustering_metric = clustering_metrics[i]
                    if clustering_metric.get('clustering_suitability') == 'excellent':
                        clustering_weight = 1.2
                    elif clustering_metric.get('clustering_suitability') == 'good':
                        clustering_weight = 1.1
                    elif clustering_metric.get('clustering_suitability') == 'poor':
                        clustering_weight = 0.9
                
                # Input quality compatibility bonus
                input_clustering_bonus = 1.0
                if input_quality['clustering_suitability'] == 'excellent':
                    input_clustering_bonus = 1.1
                elif input_quality['clustering_suitability'] == 'good':
                    input_clustering_bonus = 1.05
                
                weighted_similarity = similarity * quality_weight * clustering_weight * input_clustering_bonus
                similarities.append(weighted_similarity)
            
            if similarities:
                # Advanced scoring strategy with clustering intelligence
                similarities_sorted = sorted(similarities, reverse=True)
                
                # Use top 3 similarities for robustness
                top_similarities = similarities_sorted[:min(3, len(similarities_sorted))]
                avg_top = np.mean(top_similarities)
                max_similarity = similarities_sorted[0]
                
                # ✅ CLUSTERING-ENHANCED CONFIDENCE CALCULATION
                base_confidence = 0.6 * avg_top + 0.4 * max_similarity
                
                # Behavioral pattern bonus
                behavioral_bonus = self._calculate_behavioral_bonus(profile, input_quality)
                
                # Final confidence with clustering intelligence
                final_confidence = min(1.0, base_confidence + behavioral_bonus)
                
                return {
                    'similarities': similarities,
                    'top_similarities': top_similarities,
                    'avg_top': avg_top,
                    'max_similarity': max_similarity,
                    'base_confidence': base_confidence,
                    'behavioral_bonus': behavioral_bonus,
                    'final_confidence': final_confidence,
                    'threshold': profile.get('confidence_threshold', VOICE_CONFIDENCE_THRESHOLD),
                    'embedding_count': len(similarities),
                    'clustering_enhanced': True
                }
            
            return {'final_confidence': 0.0, 'clustering_enhanced': False}
            
        except Exception as e:
            logger.error(f"Clustering-aware confidence calculation error: {e}")
            return {'final_confidence': 0.0, 'error': str(e)}
    
    def _calculate_behavioral_bonus(self, profile: Dict, input_quality: Dict) -> float:
        """🎭 Calculate behavioral pattern bonus"""
        try:
            behavioral_patterns = profile.get('behavioral_patterns', {})
            voice_characteristics = behavioral_patterns.get('voice_characteristics', {})
            
            bonus = 0.0
            
            # Quality consistency bonus
            preferred_quality_range = behavioral_patterns.get('preferred_quality_range', [0.0, 1.0])
            input_score = input_quality['overall_score']
            
            if preferred_quality_range[0] <= input_score <= preferred_quality_range[1]:
                bonus += 0.05  # Quality within expected range
            
            # Clustering affinity bonus
            clustering_affinity = behavioral_patterns.get('clustering_affinity', 'medium')
            input_clustering = input_quality['clustering_suitability']
            
            if clustering_affinity == 'high' and input_clustering in ['excellent', 'good']:
                bonus += 0.03
            elif clustering_affinity == 'medium' and input_clustering in ['good', 'fair']:
                bonus += 0.02
            
            # Voice stability bonus
            if voice_characteristics.get('stability') == 'good':
                bonus += 0.02
            
            return min(0.1, bonus)  # Cap bonus at 0.1
            
        except Exception as e:
            return 0.0
    
    def _update_behavioral_patterns(self, username: str, input_quality: Dict, confidence: float):
        """📊 Update behavioral patterns based on recognition"""
        try:
            if username not in known_users:
                return
            
            profile = known_users[username]
            behavioral_patterns = profile.get('behavioral_patterns', {})
            
            # Update quality range
            current_quality = input_quality['overall_score']
            quality_range = behavioral_patterns.get('preferred_quality_range', [current_quality, current_quality])
            
            # Expand range if needed (with smoothing)
            if current_quality < quality_range[0]:
                quality_range[0] = quality_range[0] * 0.9 + current_quality * 0.1
            elif current_quality > quality_range[1]:
                quality_range[1] = quality_range[1] * 0.9 + current_quality * 0.1
            
            behavioral_patterns['preferred_quality_range'] = quality_range
            
            # Update clustering affinity based on recognition success
            if confidence > 0.8:
                clustering_suitability = input_quality['clustering_suitability']
                if clustering_suitability in ['excellent', 'good']:
                    behavioral_patterns['clustering_affinity'] = 'high'
            
            # Update voice characteristics
            voice_characteristics = behavioral_patterns.get('voice_characteristics', {})
            
            # Update distinctiveness based on confidence
            if confidence > 0.9:
                voice_characteristics['distinctiveness'] = 'high'
            elif confidence > 0.7:
                voice_characteristics['distinctiveness'] = 'medium'
            elif confidence < 0.5:
                voice_characteristics['distinctiveness'] = 'low'
            
            # Update environmental sensitivity
            snr = input_quality['snr_db']
            if snr > 20 and confidence > 0.8:
                voice_characteristics['environmental_sensitivity'] = 'low'
            elif snr < 10 and confidence < 0.6:
                voice_characteristics['environmental_sensitivity'] = 'high'
            else:
                voice_characteristics['environmental_sensitivity'] = 'medium'
            
            # Save updated patterns
            behavioral_patterns['voice_characteristics'] = voice_characteristics
            profile['behavioral_patterns'] = behavioral_patterns
            profile['last_updated'] = datetime.utcnow().isoformat()
            
            # Update tracking
            if username in self.behavioral_voice_patterns:
                self.behavioral_voice_patterns[username]['patterns'] = behavioral_patterns
                self.behavioral_voice_patterns[username]['recognition_patterns'].append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'confidence': confidence,
                    'quality': current_quality,
                    'clustering_suitability': input_quality['clustering_suitability']
                })
            
            save_known_users()
            
        except Exception as e:
            logger.error(f"Behavioral pattern update error: {e}")
    
    def _store_uncertain_sample(self, audio: np.ndarray, reason: str):
        """💾 Store uncertain samples for potential clustering"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"uncertain_{reason}_{timestamp}.pkl.gz"
            filepath = os.path.join("voice_profiles/uncertain", filename)
            
            uncertain_data = {
                'audio': audio.tolist(),
                'reason': reason,
                'timestamp': timestamp,
                'quality_info': self.assess_audio_quality_advanced(audio),
                'clustering_candidate': True  # ✅ NEW
            }
            
            with gzip.open(filepath, 'wb') as f:
                pickle.dump(uncertain_data, f)
            
            logger.info(f"Stored uncertain sample for clustering: {reason}")
            
        except Exception as e:
            logger.error(f"Failed to store uncertain sample: {e}")
    
    def _log_recognition_result(self, username: str, confidence: float, success: bool, quality_info: Dict):
        """📊 Log recognition results for adaptive learning"""
        if username not in self.confidence_logs:
            self.confidence_logs[username] = []
        
        log_entry = {
            'timestamp': time.time(),
            'confidence': confidence,
            'success': success,
            'input_quality': quality_info.get('overall_score', 0.0),
            'snr_db': quality_info.get('snr_db', 0.0),
            'clustering_suitability': quality_info.get('clustering_suitability', 'unknown')
        }
        
        self.confidence_logs[username].append(log_entry)
        
        # Keep only last 100 results
        if len(self.confidence_logs[username]) > 100:
            self.confidence_logs[username] = self.confidence_logs[username][-100:]
    
    def _update_recognition_stats(self, username: str, success: bool):
        """📈 Update recognition statistics"""
        if username in known_users:
            profile = known_users[username]
            profile['recognition_count'] = profile.get('recognition_count', 0) + 1
            
            if success:
                profile['recognition_successes'] = profile.get('recognition_successes', 0) + 1
            else:
                profile['recognition_failures'] = profile.get('recognition_failures', 0) + 1
            
            # Update recognition history
            profile.setdefault('recognition_history', []).append({
                'timestamp': datetime.utcnow().isoformat(),
                'success': success,
                'confidence': 0.0  # Will be filled by caller
            })
            
            # Keep only last 50 recognitions
            if len(profile['recognition_history']) > 50:
                profile['recognition_history'] = profile['recognition_history'][-50:]
            
            save_known_users()
    
    def tune_threshold_for_user(self, username: str) -> float:
        """🎯 Advanced threshold tuning with clustering intelligence"""
        if username not in self.confidence_logs or username not in known_users:
            return VOICE_CONFIDENCE_THRESHOLD
        
        try:
            logs = self.confidence_logs[username]
            if len(logs) < 10:  # Need at least 10 samples
                return known_users[username].get('confidence_threshold', VOICE_CONFIDENCE_THRESHOLD)
            
            # Analyze recent performance with clustering awareness
            recent_logs = logs[-30:]  # Last 30 recognitions
            successes = [log for log in recent_logs if log['success']]
            failures = [log for log in recent_logs if not log['success']]
            
            if len(successes) >= 10:  # Need sufficient successful recognitions
                # ✅ CLUSTERING-AWARE THRESHOLD CALCULATION
                success_confidences = [log['confidence'] for log in successes]
                success_qualities = [log['clustering_suitability'] for log in successes]
                
                # Weight confidences by clustering suitability
                weighted_confidences = []
                for conf, quality in zip(success_confidences, success_qualities):
                    weight = 1.0
                    if quality == 'excellent':
                        weight = 1.2
                    elif quality == 'good':
                        weight = 1.1
                    elif quality == 'poor':
                        weight = 0.9
                    weighted_confidences.append(conf * weight)
                
                # Calculate optimal threshold
                min_success = min(weighted_confidences)
                mean_success = np.mean(weighted_confidences)
                
                # Set threshold to capture 95% of successful recognitions
                success_sorted = sorted(weighted_confidences)
                percentile_5 = success_sorted[max(0, len(success_sorted) // 20)]  # 5th percentile
                
                # ✅ BEHAVIORAL PATTERN ADJUSTMENT
                behavioral_patterns = known_users[username].get('behavioral_patterns', {})
                clustering_affinity = behavioral_patterns.get('clustering_affinity', 'medium')
                
                adjustment = 0.0
                if clustering_affinity == 'high':
                    adjustment = -0.02  # Lower threshold for high clustering affinity
                elif clustering_affinity == 'low':
                    adjustment = 0.02   # Higher threshold for low clustering affinity
                
                new_threshold = max(0.3, min(0.8, percentile_5 - 0.02 + adjustment))
                
                # Update profile
                known_users[username]['confidence_threshold'] = new_threshold
                known_users[username]['last_threshold_update'] = datetime.utcnow().isoformat()
                
                # Update adaptation history
                if username in self.user_adaptation_history:
                    self.user_adaptation_history[username]['threshold_changes'].append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'old_threshold': known_users[username].get('confidence_threshold', VOICE_CONFIDENCE_THRESHOLD),
                        'new_threshold': new_threshold,
                        'reason': 'clustering_aware_adaptive_tuning'
                    })
                
                save_known_users()
                
                logger.info(f"Clustering-aware threshold tuned for {username}: {new_threshold:.3f} "
                           f"(clustering affinity: {clustering_affinity})")
                return new_threshold
            
            return known_users[username].get('confidence_threshold', VOICE_CONFIDENCE_THRESHOLD)
            
        except Exception as e:
            logger.error(f"Clustering-aware threshold tuning error for {username}: {e}")
            return VOICE_CONFIDENCE_THRESHOLD
    
    def add_passive_sample(self, username: str, audio: np.ndarray, confidence: float) -> bool:
        """📈 Add passive learning sample with clustering intelligence"""
        try:
            if username not in known_users:
                return False
            
            profile = known_users[username]
            
            # ✅ CLUSTERING-AWARE QUALITY CHECK
            quality = self.assess_audio_quality_advanced(audio)
            if quality['auto_discard'] or quality['clustering_suitability'] == 'unusable':
                return False
            
            # Only add high-confidence recognitions for passive learning
            if confidence < 0.8:
                return False
            
            # ✅ CLUSTERING INTELLIGENCE: Check if sample adds value
            if not self._should_add_passive_sample(profile, audio, quality):
                return False
            
            # Generate embedding
            from voice.voice_models import dual_voice_model_manager
            embedding = dual_voice_model_manager.generate_dual_embedding(audio)
            
            if embedding is not None:
                # Check if we have room for more embeddings
                current_embeddings = len(profile.get('embeddings', []))
                
                if current_embeddings < self.max_embeddings_per_user:
                    # Add new embedding
                    profile['embeddings'].append(embedding)
                    profile['quality_scores'].append(quality['overall_score'])
                    profile.setdefault('embedding_metadata', []).append({
                        'type': 'passive',
                        'confidence': confidence,
                        'snr_db': quality['snr_db'],
                        'clustering_suitability': quality['clustering_suitability'],
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    profile.setdefault('clustering_metrics', []).append({
                        'clustering_suitability': quality['clustering_suitability'],
                        'snr_db': quality['snr_db'],
                        'spectral_quality': quality['spectral_quality'],
                        'voice_ratio': quality.get('voice_ratio', 0.5)
                    })
                else:
                    # Replace lowest quality embedding if this one is better
                    quality_scores = profile.get('quality_scores', [])
                    if quality_scores:
                        min_quality_idx = np.argmin(quality_scores)
                        if quality['overall_score'] > quality_scores[min_quality_idx]:
                            profile['embeddings'][min_quality_idx] = embedding
                            profile['quality_scores'][min_quality_idx] = quality['overall_score']
                            if len(profile['embedding_metadata']) > min_quality_idx:
                                profile['embedding_metadata'][min_quality_idx] = {
                                    'type': 'passive_replacement',
                                    'confidence': confidence,
                                    'snr_db': quality['snr_db'],
                                    'clustering_suitability': quality['clustering_suitability'],
                                    'timestamp': datetime.utcnow().isoformat()
                                }
                            if len(profile.get('clustering_metrics', [])) > min_quality_idx:
                                profile['clustering_metrics'][min_quality_idx] = {
                                    'clustering_suitability': quality['clustering_suitability'],
                                    'snr_db': quality['snr_db'],
                                    'spectral_quality': quality['spectral_quality'],
                                    'voice_ratio': quality.get('voice_ratio', 0.5)
                                }
                
                # Save raw audio sample
                self.save_raw_audio_sample(username, audio, "passive")
                
                profile['last_updated'] = datetime.utcnow().isoformat()
                profile['passive_samples_added'] = profile.get('passive_samples_added', 0) + 1
                save_known_users()
                
                # ✅ UPDATE BEHAVIORAL PATTERNS
                self._update_behavioral_patterns(username, quality, confidence)
                
                logger.info(f"Added passive sample for {username} (quality: {quality['overall_score']:.2f}, "
                           f"clustering: {quality['clustering_suitability']})")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Passive sample addition error: {e}")
            return False
    
    def _should_add_passive_sample(self, profile: Dict, audio: np.ndarray, quality: Dict) -> bool:
        """🤔 Determine if passive sample adds value with clustering intelligence"""
        try:
            from voice.voice_models import dual_voice_model_manager
            
            # Generate embedding for comparison
            test_embedding = dual_voice_model_manager.generate_dual_embedding(audio)
            if test_embedding is None:
                return False
            
            # Check similarity with existing embeddings
            existing_embeddings = profile.get('embeddings', [])
            if not existing_embeddings:
                return True  # First sample is always valuable
            
            max_similarity = 0.0
            for existing_embedding in existing_embeddings:
                similarity = dual_voice_model_manager.compare_dual_embeddings(test_embedding, existing_embedding)
                max_similarity = max(max_similarity, similarity)
            
            # ✅ CLUSTERING INTELLIGENCE: Add sample if it's sufficiently different or high quality
            clustering_suitability = quality['clustering_suitability']
            
            # Lower similarity threshold for excellent clustering samples
            if clustering_suitability == 'excellent' and max_similarity < 0.95:
                return True
            elif clustering_suitability == 'good' and max_similarity < 0.90:
                return True
            elif clustering_suitability in ['fair', 'poor'] and max_similarity < 0.85:
                return True
            
            # Don't add very similar samples
            return False
            
        except Exception as e:
            logger.error(f"Passive sample evaluation error: {e}")
            return False
    
    def merge_passive_samples(self, username: str) -> int:
        """🔗 Merge passive samples to optimize profile"""
        try:
            if username not in known_users:
                return 0
            
            from voice.voice_models import dual_voice_model_manager
            
            profile = known_users[username]
            embeddings = profile.get('embeddings', [])
            quality_scores = profile.get('quality_scores', [])
            
            if len(embeddings) <= 3:  # Keep minimum embeddings
                return 0
            
            # Find similar embeddings to merge
            merged_count = 0
            indices_to_remove = set()
            
            for i in range(len(embeddings)):
                if i in indices_to_remove:
                    continue
                    
                for j in range(i + 1, len(embeddings)):
                    if j in indices_to_remove:
                        continue
                    
                    similarity = dual_voice_model_manager.compare_dual_embeddings(embeddings[i], embeddings[j])
                    
                    # Merge very similar embeddings (keep higher quality one)
                    if similarity > 0.95:
                        quality_i = quality_scores[i] if i < len(quality_scores) else 0.5
                        quality_j = quality_scores[j] if j < len(quality_scores) else 0.5
                        
                        if quality_i >= quality_j:
                            indices_to_remove.add(j)
                        else:
                            indices_to_remove.add(i)
                            break
                        
                        merged_count += 1
            
            # Remove merged embeddings
            if indices_to_remove:
                new_embeddings = [emb for i, emb in enumerate(embeddings) if i not in indices_to_remove]
                new_quality_scores = [score for i, score in enumerate(quality_scores) if i not in indices_to_remove]
                
                profile['embeddings'] = new_embeddings
                profile['quality_scores'] = new_quality_scores
                
                # Update metadata arrays
                for metadata_key in ['embedding_metadata', 'clustering_metrics']:
                    if metadata_key in profile:
                        new_metadata = [meta for i, meta in enumerate(profile[metadata_key]) if i not in indices_to_remove]
                        profile[metadata_key] = new_metadata
                
                profile['last_updated'] = datetime.utcnow().isoformat()
                save_known_users()
                
                logger.info(f"Merged {merged_count} similar embeddings for {username}")
            
            return merged_count
            
        except Exception as e:
            logger.error(f"Passive sample merging error: {e}")
            return 0
    
    def analyze_user_voice_evolution(self, username: str) -> Dict:
        """📊 Analyze how user's voice has evolved over time"""
        try:
            if username not in known_users or username not in self.confidence_logs:
                return {}
            
            profile = known_users[username]
            logs = self.confidence_logs[username]
            
            if len(logs) < 5:
                return {'analysis': 'insufficient_data'}
            
            # Analyze confidence trends
            recent_logs = logs[-30:]  # Last 30 interactions
            older_logs = logs[-60:-30] if len(logs) >= 60 else logs[:-30]
            
            recent_confidence = np.mean([log['confidence'] for log in recent_logs])
            older_confidence = np.mean([log['confidence'] for log in older_logs]) if older_logs else recent_confidence
            
            # Analyze quality trends
            recent_quality = np.mean([log['input_quality'] for log in recent_logs])
            older_quality = np.mean([log['input_quality'] for log in older_logs]) if older_logs else recent_quality
            
            # Analyze clustering suitability trends
            clustering_trend = self._analyze_clustering_trend(recent_logs, older_logs)
            
            evolution = {
                'confidence_trend': {
                    'recent_average': recent_confidence,
                    'older_average': older_confidence,
                    'change': recent_confidence - older_confidence,
                    'trend': 'improving' if recent_confidence > older_confidence + 0.05 else 
                            'declining' if recent_confidence < older_confidence - 0.05 else 'stable'
                },
                'quality_trend': {
                    'recent_average': recent_quality,
                    'older_average': older_quality,
                    'change': recent_quality - older_quality,
                    'trend': 'improving' if recent_quality > older_quality + 0.05 else 
                            'declining' if recent_quality < older_quality - 0.05 else 'stable'
                },
                'clustering_analysis': clustering_trend,
                'behavioral_changes': self._analyze_behavioral_changes(username),
                'adaptation_recommendations': self._generate_adaptation_recommendations(username, recent_logs)
            }
            
            return evolution
            
        except Exception as e:
            logger.error(f"Voice evolution analysis error: {e}")
            return {'error': str(e)}
    
    def _analyze_clustering_trend(self, recent_logs: List, older_logs: List) -> Dict:
        """🔍 Analyze clustering suitability trends"""
        try:
            recent_clustering = [log.get('clustering_suitability', 'unknown') for log in recent_logs]
            older_clustering = [log.get('clustering_suitability', 'unknown') for log in older_logs]
            
            # Convert to numeric scores for comparison
            def clustering_to_score(suitability):
                scores = {'excellent': 4, 'good': 3, 'fair': 2, 'poor': 1, 'unusable': 0, 'unknown': 2}
                return scores.get(suitability, 2)
            
            recent_scores = [clustering_to_score(c) for c in recent_clustering]
            older_scores = [clustering_to_score(c) for c in older_clustering] if older_clustering else recent_scores
            
            recent_avg = np.mean(recent_scores)
            older_avg = np.mean(older_scores)
            
            return {
                'recent_average_score': recent_avg,
                'older_average_score': older_avg,
                'improvement': recent_avg - older_avg,
                'trend': 'improving' if recent_avg > older_avg + 0.5 else 
                        'declining' if recent_avg < older_avg - 0.5 else 'stable',
                'dominant_recent_quality': max(set(recent_clustering), key=recent_clustering.count) if recent_clustering else 'unknown'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_behavioral_changes(self, username: str) -> Dict:
        """🎭 Analyze behavioral pattern changes"""
        try:
            if username not in self.behavioral_voice_patterns:
                return {'analysis': 'no_behavioral_data'}
            
            behavioral_data = self.behavioral_voice_patterns[username]
            recognition_patterns = behavioral_data.get('recognition_patterns', [])
            
            if len(recognition_patterns) < 10:
                return {'analysis': 'insufficient_behavioral_data'}
            
            # Analyze recent vs older patterns
            recent_patterns = recognition_patterns[-20:]
            older_patterns = recognition_patterns[-40:-20] if len(recognition_patterns) >= 40 else recognition_patterns[:-20]
            
            changes = {}
            
            # Confidence stability
            recent_confidence_std = np.std([p['confidence'] for p in recent_patterns])
            older_confidence_std = np.std([p['confidence'] for p in older_patterns]) if older_patterns else recent_confidence_std
            
            changes['confidence_stability'] = {
                'recent_std': recent_confidence_std,
                'older_std': older_confidence_std,
                'change': 'more_stable' if recent_confidence_std < older_confidence_std - 0.05 else
                         'less_stable' if recent_confidence_std > older_confidence_std + 0.05 else 'stable'
            }
            
            # Quality consistency
            recent_quality_std = np.std([p['quality'] for p in recent_patterns])
            older_quality_std = np.std([p['quality'] for p in older_patterns]) if older_patterns else recent_quality_std
            
            changes['quality_consistency'] = {
                'recent_std': recent_quality_std,
                'older_std': older_quality_std,
                'change': 'more_consistent' if recent_quality_std < older_quality_std - 0.05 else
                         'less_consistent' if recent_quality_std > older_quality_std + 0.05 else 'stable'
            }
            
            return changes
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_adaptation_recommendations(self, username: str, recent_logs: List) -> List[str]:
        """💡 Generate personalized adaptation recommendations"""
        try:
            recommendations = []
            
            if not recent_logs:
                return recommendations
            
            # Analyze recent performance
            avg_confidence = np.mean([log['confidence'] for log in recent_logs])
            avg_quality = np.mean([log['input_quality'] for log in recent_logs])
            
            # Low confidence recommendations
            if avg_confidence < 0.6:
                clustering_qualities = [log.get('clustering_suitability', 'unknown') for log in recent_logs]
                poor_clustering_count = sum(1 for q in clustering_qualities if q in ['poor', 'unusable'])
                
                if poor_clustering_count > len(recent_logs) * 0.3:
                    recommendations.append("Consider improving audio environment to enhance voice clustering")
                
                recommendations.append("Additional voice training samples may improve recognition accuracy")
            
            # Quality recommendations
            if avg_quality < 0.5:
                recommendations.append("Audio quality appears inconsistent - check microphone and environment")
            
            # Clustering-specific recommendations
            profile = known_users.get(username, {})
            behavioral_patterns = profile.get('behavioral_patterns', {})
            clustering_affinity = behavioral_patterns.get('clustering_affinity', 'medium')
            
            if clustering_affinity == 'low':
                recommendations.append("Voice clustering effectiveness is low - consider retraining with varied audio conditions")
            
            # Threshold recommendations
            threshold = profile.get('confidence_threshold', VOICE_CONFIDENCE_THRESHOLD)
            if threshold > 0.8:
                recommendations.append("Recognition threshold is very high - consider lowering if experiencing false rejections")
            elif threshold < 0.4:
                recommendations.append("Recognition threshold is very low - consider raising if experiencing false positives")
            
            return recommendations
            
        except Exception as e:
            return [f"Error generating recommendations: {str(e)}"]
    
    def cleanup_user_data(self, username: str) -> Dict:
        """🧹 Cleanup and optimize user data"""
        try:
            if username not in known_users:
                return {'error': 'user_not_found'}
            
            results = {
                'merged_samples': 0,
                'cleaned_logs': 0,
                'optimized_metadata': False,
                'updated_patterns': False
            }
            
            # Merge similar passive samples
            results['merged_samples'] = self.merge_passive_samples(username)
            
            # Clean old confidence logs
            if username in self.confidence_logs:
                old_count = len(self.confidence_logs[username])
                # Keep only last 100 logs
                self.confidence_logs[username] = self.confidence_logs[username][-100:]
                results['cleaned_logs'] = old_count - len(self.confidence_logs[username])
            
            # Optimize metadata
            profile = known_users[username]
            if self._optimize_profile_metadata(profile):
                results['optimized_metadata'] = True
            
            # Update behavioral patterns
            if self._update_user_behavioral_patterns(username):
                results['updated_patterns'] = True
            
            # Save changes
            profile['last_cleanup'] = datetime.utcnow().isoformat()
            save_known_users()
            
            logger.info(f"Cleaned up user data for {username}: {results}")
            return results
            
        except Exception as e:
            logger.error(f"User data cleanup error: {e}")
            return {'error': str(e)}
    
    def _optimize_profile_metadata(self, profile: Dict) -> bool:
        """⚡ Optimize profile metadata"""
        try:
            optimized = False
            
            # Ensure metadata arrays match embeddings
            embeddings_count = len(profile.get('embeddings', []))
            
            for metadata_key in ['embedding_metadata', 'clustering_metrics', 'quality_scores']:
                if metadata_key in profile:
                    metadata = profile[metadata_key]
                    if len(metadata) != embeddings_count:
                        # Trim or extend to match
                        if len(metadata) > embeddings_count:
                            profile[metadata_key] = metadata[:embeddings_count]
                        else:
                            # Extend with default values
                            while len(profile[metadata_key]) < embeddings_count:
                                if metadata_key == 'quality_scores':
                                    profile[metadata_key].append(0.5)
                                elif metadata_key == 'embedding_metadata':
                                    profile[metadata_key].append({
                                        'type': 'unknown',
                                        'timestamp': datetime.utcnow().isoformat()
                                    })
                                elif metadata_key == 'clustering_metrics':
                                    profile[metadata_key].append({
                                        'clustering_suitability': 'unknown',
                                        'snr_db': 0.0,
                                        'spectral_quality': 0.5
                                    })
                        optimized = True
            
            return optimized
            
        except Exception as e:
            logger.error(f"Metadata optimization error: {e}")
            return False
    
    def _update_user_behavioral_patterns(self, username: str) -> bool:
        """📊 Update user behavioral patterns"""
        try:
            if username not in known_users or username not in self.confidence_logs:
                return False
            
            profile = known_users[username]
            logs = self.confidence_logs[username]
            
            if len(logs) < 5:
                return False
            
            behavioral_patterns = profile.get('behavioral_patterns', {})
            
            # Update voice consistency
            recent_qualities = [log['input_quality'] for log in logs[-20:]]
            if recent_qualities:
                consistency = 1.0 - np.std(recent_qualities)
                behavioral_patterns['voice_consistency'] = max(0.0, min(1.0, consistency))
            
            # Update recognition difficulty
            recent_confidences = [log['confidence'] for log in logs[-20:]]
            if recent_confidences:
                avg_confidence = np.mean(recent_confidences)
                if avg_confidence > 0.8:
                    behavioral_patterns['recognition_difficulty'] = 'easy'
                elif avg_confidence > 0.6:
                    behavioral_patterns['recognition_difficulty'] = 'normal'
                else:
                    behavioral_patterns['recognition_difficulty'] = 'difficult'
            
            # Update clustering affinity based on recent performance
            recent_clustering = [log.get('clustering_suitability', 'unknown') for log in logs[-20:]]
            excellent_count = sum(1 for c in recent_clustering if c == 'excellent')
            good_count = sum(1 for c in recent_clustering if c == 'good')
            
            if excellent_count > len(recent_clustering) * 0.5:
                behavioral_patterns['clustering_affinity'] = 'high'
            elif (excellent_count + good_count) > len(recent_clustering) * 0.6:
                behavioral_patterns['clustering_affinity'] = 'medium'
            else:
                behavioral_patterns['clustering_affinity'] = 'low'
            
            profile['behavioral_patterns'] = behavioral_patterns
            profile['last_updated'] = datetime.utcnow().isoformat()
            
            return True
            
        except Exception as e:
            logger.error(f"Behavioral pattern update error: {e}")
            return False
    
    def get_user_analytics(self, username: str) -> Dict:
        """📈 Get comprehensive user analytics"""
        try:
            if username not in known_users:
                return {'error': 'user_not_found'}
            
            profile = known_users[username]
            
            analytics = {
                'profile_info': {
                    'username': username,
                    'status': profile.get('status', 'unknown'),
                    'created_date': profile.get('created_date', 'unknown'),
                    'last_updated': profile.get('last_updated', 'unknown'),
                    'training_type': profile.get('training_type', 'unknown'),
                    'embedding_count': len(profile.get('embeddings', [])),
                    'confidence_threshold': profile.get('confidence_threshold', VOICE_CONFIDENCE_THRESHOLD)
                },
                'recognition_stats': {
                    'total_recognitions': profile.get('recognition_count', 0),
                    'successful_recognitions': profile.get('recognition_successes', 0),
                    'failed_recognitions': profile.get('recognition_failures', 0),
                    'success_rate': 0.0,
                    'passive_samples_added': profile.get('passive_samples_added', 0)
                },
                'quality_analysis': self._analyze_user_quality(username),
                'behavioral_patterns': profile.get('behavioral_patterns', {}),
                'clustering_analysis': self._analyze_user_clustering(username),
                'voice_evolution': self.analyze_user_voice_evolution(username),
                'recommendations': self._generate_adaptation_recommendations(username, 
                    self.confidence_logs.get(username, [])[-20:])
            }
            
            # Calculate success rate
            total = analytics['recognition_stats']['total_recognitions']
            successful = analytics['recognition_stats']['successful_recognitions']
            if total > 0:
                analytics['recognition_stats']['success_rate'] = successful / total
            
            return analytics
            
        except Exception as e:
            logger.error(f"User analytics error: {e}")
            return {'error': str(e)}
    
    def _analyze_user_quality(self, username: str) -> Dict:
        """🔊 Analyze user audio quality patterns"""
        try:
            if username not in self.confidence_logs:
                return {'analysis': 'no_quality_data'}
            
            logs = self.confidence_logs[username]
            if not logs:
                return {'analysis': 'no_quality_data'}
            
            qualities = [log['input_quality'] for log in logs]
            snrs = [log['snr_db'] for log in logs]
            clustering_qualities = [log.get('clustering_suitability', 'unknown') for log in logs]
            
            return {
                'average_quality': np.mean(qualities),
                'quality_std': np.std(qualities),
                'quality_range': [min(qualities), max(qualities)],
                'average_snr': np.mean(snrs),
                'snr_std': np.std(snrs),
                'clustering_distribution': {
                    quality: clustering_qualities.count(quality) 
                    for quality in set(clustering_qualities)
                },
                'trend': 'improving' if len(qualities) > 10 and 
                        np.mean(qualities[-5:]) > np.mean(qualities[:5]) + 0.1 else 'stable'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_user_clustering(self, username: str) -> Dict:
        """🔍 Analyze user clustering effectiveness"""
        try:
            profile = known_users.get(username, {})
            clustering_metrics = profile.get('clustering_metrics', [])
            
            if not clustering_metrics:
                return {'analysis': 'no_clustering_data'}
            
            suitabilities = [m.get('clustering_suitability', 'unknown') for m in clustering_metrics]
            snrs = [m.get('snr_db', 0.0) for m in clustering_metrics]
            spectral_qualities = [m.get('spectral_quality', 0.5) for m in clustering_metrics]
            
            return {
                'suitability_distribution': {
                    suitability: suitabilities.count(suitability) 
                    for suitability in set(suitabilities)
                },
                'average_snr': np.mean(snrs),
                'average_spectral_quality': np.mean(spectral_qualities),
                'clustering_effectiveness': self._calculate_clustering_effectiveness(suitabilities),
                'dominant_suitability': max(set(suitabilities), key=suitabilities.count) if suitabilities else 'unknown'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_clustering_effectiveness(self, suitabilities: List[str]) -> str:
        """📊 Calculate overall clustering effectiveness"""
        try:
            if not suitabilities:
                return 'unknown'
            
            scores = {'excellent': 4, 'good': 3, 'fair': 2, 'poor': 1, 'unusable': 0, 'unknown': 2}
            total_score = sum(scores.get(s, 2) for s in suitabilities)
            avg_score = total_score / len(suitabilities)
            
            if avg_score >= 3.5:
                return 'excellent'
            elif avg_score >= 2.5:
                return 'good'
            elif avg_score >= 1.5:
                return 'fair'
            else:
                return 'poor'
                
        except Exception as e:
            return 'unknown'

# Global advanced speaker profiles manager
enhanced_speaker_profiles = AdvancedSpeakerProfiles()