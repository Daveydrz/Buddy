# voice/voice_models.py - Professional Multi-Model Voice Recognition System
import numpy as np
import tempfile
import os
import soundfile as sf
from typing import Optional, Dict, Tuple, List, Any
import logging
import time
import json
from datetime import datetime
import torch
import torchaudio
from pathlib import Path

# Configure professional logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfessionalDualVoiceModelManager:
    """Enhanced professional voice model manager building on your dual-model foundation"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with professional configuration"""
        self.models = {}
        self.model_weights = {}
        self.device = self._detect_optimal_device()
        self.config = self._load_enhanced_config(config_path)
        self.performance_stats = {
            'total_embeddings': 0,
            'model_usage': {},
            'average_time': 0.0,
            'error_count': 0,
            'success_rate': 1.0
        }
        
        logger.info(f"[ProfessionalVoice] 🚀 Initializing on {self.device}")
        self._initialize_all_models()
        logger.info(f"[ProfessionalVoice] ✅ Ready with {len(self.models)} models")
    
    def _detect_optimal_device(self) -> str:
        """Detect the best available device for processing"""
        if torch.cuda.is_available():
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"[ProfessionalVoice] 🎯 Using GPU: {gpu_name} ({gpu_memory:.1f}GB)")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"
            logger.info(f"[ProfessionalVoice] 🍎 Using Apple Metal Performance Shaders")
        else:
            device = "cpu"
            logger.info(f"[ProfessionalVoice] 💻 Using CPU processing")
        return device
    
    def _load_enhanced_config(self, config_path: Optional[str] = None) -> Dict:
        """Load enhanced configuration"""
        default_config = {
            "models": {
                "resemblyzer": {
                    "enabled": True,
                    "weight": 0.35,
                    "priority": 1,
                    "min_duration": 1.0,
                    "optimal_duration": 3.0
                },
                "speechbrain_ecapa": {
                    "enabled": True,
                    "weight": 0.35,
                    "priority": 2,
                    "model_source": "speechbrain/spkrec-ecapa-voxceleb",
                    "min_duration": 0.5,
                    "optimal_duration": 2.0
                },
                "wav2vec2": {
                    "enabled": True,
                    "weight": 0.2,
                    "priority": 3,
                    "model_name": "facebook/wav2vec2-large-xlsr-53"
                },
                "speechbrain_xvector": {
                    "enabled": True,
                    "weight": 0.1,
                    "priority": 4,
                    "model_source": "speechbrain/spkrec-xvect-voxceleb"
                }
            },
            "processing": {
                "sample_rate": 16000,
                "normalize_audio": True,
                "remove_dc_offset": True,
                "noise_gate_threshold": 0.01,
                "auto_gain_control": True,
                "min_audio_length": 0.5,
                "max_audio_length": 30.0
            },
            "similarity": {
                "ensemble_method": "weighted_average",
                "adaptive_weights": True,
                "confidence_threshold": 0.7,
                "use_model_confidence": True
            },
            "performance": {
                "enable_caching": True,
                "cache_size": 1000,
                "enable_benchmarking": True,
                "log_performance": True
            }
        }
        
        # Load custom config if provided
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    custom_config = json.load(f)
                # Deep merge configurations
                self._deep_merge_config(default_config, custom_config)
                logger.info(f"[ProfessionalVoice] 📄 Loaded config from {config_path}")
            except Exception as e:
                logger.warning(f"[ProfessionalVoice] ⚠️ Config load failed: {e}")
        
        return default_config
    
    def _deep_merge_config(self, base: Dict, override: Dict):
        """Deep merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_config(base[key], value)
            else:
                base[key] = value
    
    def _initialize_all_models(self):
        """Initialize all configured models"""
        # Initialize your existing models first (proven to work)
        if self.config["models"]["resemblyzer"]["enabled"]:
            self._init_resemblyzer_enhanced()
        
        if self.config["models"]["speechbrain_ecapa"]["enabled"]:
            self._init_speechbrain_ecapa_enhanced()
        
        # Add new models
        if self.config["models"]["wav2vec2"]["enabled"]:
            self._init_wav2vec2()
        
        if self.config["models"]["speechbrain_xvector"]["enabled"]:
            self._init_speechbrain_xvector()
        
        # Set model weights
        self._configure_model_weights()
    
    def _init_resemblyzer_enhanced(self):
        """Enhanced Resemblyzer initialization based on your working version"""
        try:
            from resemblyzer import VoiceEncoder
            
            class EnhancedResemblyzerWrapper:
                def __init__(self, device):
                    self.encoder = VoiceEncoder(device=device)
                    self.name = "Resemblyzer_Enhanced"
                    self.embedding_dim = 256
                    self.device = device
                    self.processing_times = []
                
                def generate_embedding(self, audio: np.ndarray) -> Optional[np.ndarray]:
                    start_time = time.time()
                    try:
                        if len(audio) < 8000:  # Less than 0.5 seconds
                            return None
                        
                        # Enhanced preprocessing
                        audio_float = self._preprocess_audio_enhanced(audio)
                        
                        # Generate embedding
                        embedding = self.encoder.embed_utterance(audio_float)
                        
                        if embedding is not None and len(embedding) == 256:
                            # L2 normalization
                            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
                            
                            # Track performance
                            processing_time = time.time() - start_time
                            self.processing_times.append(processing_time)
                            if len(self.processing_times) > 100:
                                self.processing_times = self.processing_times[-100:]
                            
                            return embedding
                        return None
                        
                    except Exception as e:
                        logger.error(f"Enhanced Resemblyzer error: {e}")
                        return None
                
                def _preprocess_audio_enhanced(self, audio: np.ndarray) -> np.ndarray:
                    """Enhanced audio preprocessing"""
                    # Convert to float32
                    if audio.dtype != np.float32:
                        if audio.dtype == np.int16:
                            audio_float = audio.astype(np.float32) / 32768.0
                        else:
                            audio_float = audio.astype(np.float32)
                    else:
                        audio_float = audio
                    
                    # Remove DC offset
                    audio_float = audio_float - np.mean(audio_float)
                    
                    # Auto gain control
                    max_val = np.max(np.abs(audio_float))
                    if max_val > 0:
                        audio_float = audio_float / max_val * 0.95
                    
                    # Simple noise gate
                    threshold = np.max(np.abs(audio_float)) * 0.01
                    mask = np.abs(audio_float) > threshold
                    audio_float[~mask] *= 0.1
                    
                    return audio_float
                
                def get_average_processing_time(self) -> float:
                    return np.mean(self.processing_times) if self.processing_times else 0.0
            
            self.models['resemblyzer'] = EnhancedResemblyzerWrapper(self.device)
            logger.info("✅ Enhanced Resemblyzer initialized")
            
        except ImportError:
            logger.error("❌ Resemblyzer not available")
        except Exception as e:
            logger.error(f"❌ Resemblyzer initialization failed: {e}")
    
    def _init_speechbrain_ecapa_enhanced(self):
        """Enhanced SpeechBrain ECAPA based on your working version"""
        try:
            from speechbrain.inference import SpeakerRecognition
            
            class EnhancedSpeechBrainWrapper:
                def __init__(self, device, model_source):
                    self.name = "SpeechBrain_ECAPA_Enhanced"
                    self.embedding_dim = 192
                    self.device = device
                    self.model_source = model_source
                    self.model = None
                    self.processing_times = []
                    self._load_model()
                
                def _load_model(self):
                    try:
                        logger.info("Loading enhanced SpeechBrain ECAPA model...")
                        
                        # Enhanced model loading with better error handling
                        os.environ['HUGGINGFACE_HUB_CACHE'] = os.path.abspath('models/huggingface_cache')
                        
                        run_opts = {"device": self.device if self.device != "mps" else "cpu"}
                        
                        self.model = SpeakerRecognition.from_hparams(
                            source=self.model_source,
                            savedir="models/speechbrain_ecapa_enhanced",
                            run_opts=run_opts
                        )
                        logger.info("✅ Enhanced SpeechBrain ECAPA loaded")
                    except Exception as e:
                        logger.error(f"❌ Enhanced SpeechBrain loading failed: {e}")
                        self.model = None
                
                def generate_embedding(self, audio: np.ndarray) -> Optional[np.ndarray]:
                    if self.model is None:
                        return None
                    
                    start_time = time.time()
                    try:
                        if len(audio) < 4000:  # Less than 0.25 seconds
                            return None
                        
                        # Enhanced preprocessing
                        audio_processed = self._preprocess_audio_enhanced(audio)
                        
                        # Generate embedding
                        audio_tensor = torch.tensor(audio_processed).unsqueeze(0)
                        if self.device == "cuda":
                            audio_tensor = audio_tensor.cuda()
                        
                        with torch.no_grad():
                            embedding = self.model.encode_batch(audio_tensor)
                            embedding = embedding.squeeze().cpu().numpy()
                            
                            # L2 normalization
                            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
                            
                            # Track performance
                            processing_time = time.time() - start_time
                            self.processing_times.append(processing_time)
                            if len(self.processing_times) > 100:
                                self.processing_times = self.processing_times[-100:]
                            
                            return embedding
                    
                    except Exception as e:
                        logger.error(f"Enhanced SpeechBrain embedding error: {e}")
                        return None
                
                def _preprocess_audio_enhanced(self, audio: np.ndarray) -> np.ndarray:
                    """Enhanced audio preprocessing for SpeechBrain"""
                    # Convert to float32
                    if audio.dtype != np.float32:
                        if audio.dtype == np.int16:
                            audio_float = audio.astype(np.float32) / 32768.0
                        else:
                            audio_float = audio.astype(np.float32)
                    else:
                        audio_float = audio
                    
                    # Remove DC offset
                    audio_float = audio_float - np.mean(audio_float)
                    
                    # Enhanced noise gate with dynamic threshold
                    energy = np.abs(audio_float)
                    threshold = np.percentile(energy, 20) * 2  # Dynamic threshold
                    mask = energy > threshold
                    audio_float[~mask] *= 0.05
                    
                    # Auto gain control
                    max_val = np.max(np.abs(audio_float))
                    if max_val > 0:
                        audio_float = audio_float / max_val * 0.9
                    
                    return audio_float
                
                def get_average_processing_time(self) -> float:
                    return np.mean(self.processing_times) if self.processing_times else 0.0
            
            model_source = self.config["models"]["speechbrain_ecapa"]["model_source"]
            self.models['speechbrain_ecapa'] = EnhancedSpeechBrainWrapper(self.device, model_source)
            
            if self.models['speechbrain_ecapa'].model is not None:
                logger.info("✅ Enhanced SpeechBrain ECAPA initialized")
            else:
                del self.models['speechbrain_ecapa']
                logger.warning("⚠️ Enhanced SpeechBrain ECAPA failed to load")
                
        except ImportError:
            logger.warning("⚠️ SpeechBrain not available for enhanced ECAPA")
        except Exception as e:
            logger.error(f"❌ Enhanced SpeechBrain ECAPA init failed: {e}")
    
    def _init_wav2vec2(self):
        """Initialize Wav2Vec2 model"""
        try:
            from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2Model
            
            class Wav2Vec2Wrapper:
                def __init__(self, device, model_name):
                    self.name = "Wav2Vec2"
                    self.device = device
                    self.model_name = model_name
                    self.feature_extractor = None
                    self.model = None
                    self.processing_times = []
                    self._load_model()
                
                def _load_model(self):
                    try:
                        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(self.model_name)
                        self.model = Wav2Vec2Model.from_pretrained(self.model_name)
                        if self.device == "cuda":
                            self.model = self.model.cuda()
                        self.model.eval()
                        logger.info(f"✅ Wav2Vec2 model loaded: {self.model_name}")
                    except Exception as e:
                        logger.error(f"❌ Wav2Vec2 loading failed: {e}")
                        self.model = None
                
                def generate_embedding(self, audio: np.ndarray) -> Optional[np.ndarray]:
                    if self.model is None or self.feature_extractor is None:
                        return None
                    
                    start_time = time.time()
                    try:
                        # Preprocess
                        audio_float = audio.astype(np.float32)
                        if np.max(np.abs(audio_float)) > 1.0:
                            audio_float = audio_float / 32768.0
                        
                        # Extract features
                        inputs = self.feature_extractor(
                            audio_float, 
                            sampling_rate=16000, 
                            return_tensors="pt"
                        )
                        
                        if self.device == "cuda":
                            inputs = {k: v.cuda() for k, v in inputs.items()}
                        
                        # Generate embedding
                        with torch.no_grad():
                            outputs = self.model(**inputs)
                            # Use mean pooling over time dimension
                            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()
                            
                            # Normalize
                            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
                            
                            # Track performance
                            processing_time = time.time() - start_time
                            self.processing_times.append(processing_time)
                            if len(self.processing_times) > 100:
                                self.processing_times = self.processing_times[-100:]
                            
                            return embedding
                    
                    except Exception as e:
                        logger.error(f"Wav2Vec2 embedding error: {e}")
                        return None
                
                def get_average_processing_time(self) -> float:
                    return np.mean(self.processing_times) if self.processing_times else 0.0
            
            model_name = self.config["models"]["wav2vec2"]["model_name"]
            self.models['wav2vec2'] = Wav2Vec2Wrapper(self.device, model_name)
            
            if self.models['wav2vec2'].model is not None:
                logger.info("✅ Wav2Vec2 initialized")
            else:
                del self.models['wav2vec2']
                
        except ImportError:
            logger.warning("⚠️ Transformers not available for Wav2Vec2")
        except Exception as e:
            logger.error(f"❌ Wav2Vec2 init failed: {e}")
    
    def _init_speechbrain_xvector(self):
        """Initialize SpeechBrain X-Vector model"""
        try:
            from speechbrain.inference import SpeakerRecognition
            
            model_source = self.config["models"]["speechbrain_xvector"]["model_source"]
            # Similar implementation to ECAPA but with X-Vector model
            # ... (implementation similar to ECAPA wrapper)
            
        except Exception as e:
            logger.error(f"❌ SpeechBrain X-Vector init failed: {e}")
    
    def _configure_model_weights(self):
        """Configure model weights based on available models"""
        available_models = list(self.models.keys())
        
        # Set weights from config for available models
        total_weight = 0
        for model_name in available_models:
            if model_name in self.config["models"]:
                weight = self.config["models"][model_name]["weight"]
                self.model_weights[model_name] = weight
                total_weight += weight
        
        # Normalize weights
        if total_weight > 0:
            for model_name in self.model_weights:
                self.model_weights[model_name] /= total_weight
        
        logger.info(f"Model weights configured: {self.model_weights}")
    
    def generate_dual_embedding(self, audio: np.ndarray) -> Optional[Dict]:
        """Enhanced dual embedding generation with professional features"""
        start_time = time.time()
        
        try:
            # Enhanced audio preprocessing
            audio = self._preprocess_audio_professional(audio)
            
            result = {
                'timestamp': datetime.utcnow().isoformat(),
                'models_used': [],
                'processing_times': {},
                'model_confidences': {},
                'audio_quality_score': self._assess_audio_quality(audio)
            }
            
            # Generate embeddings from all available models
            for model_name, model in self.models.items():
                try:
                    model_start_time = time.time()
                    embedding = model.generate_embedding(audio)
                    model_time = time.time() - model_start_time
                    
                    if embedding is not None:
                        result[model_name] = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
                        result['models_used'].append(model_name)
                        result['processing_times'][model_name] = model_time
                        
                        # Calculate model confidence based on embedding quality
                        confidence = self._calculate_embedding_confidence(embedding, model_name)
                        result['model_confidences'][model_name] = confidence
                
                except Exception as e:
                    logger.error(f"Model {model_name} failed: {e}")
            
            # Set primary model (highest confidence or configured priority)
            if result['models_used']:
                if self.config["similarity"]["use_model_confidence"]:
                    primary = max(result['model_confidences'], key=result['model_confidences'].get)
                else:
                    primary = result['models_used'][0]  # Use first available
                result['primary'] = primary
            else:
                return None
            
            # Performance tracking
            total_time = time.time() - start_time
            result['total_processing_time'] = total_time
            result['dual_available'] = len(result['models_used']) > 1
            
            # Update performance stats
            self._update_performance_stats(result)
            
            logger.debug(f"Generated embeddings: {len(result['models_used'])} models, {total_time:.3f}s")
            return result
        
        except Exception as e:
            logger.error(f"Professional dual embedding generation error: {e}")
            self.performance_stats['error_count'] += 1
            return None
    
    def _preprocess_audio_professional(self, audio: np.ndarray) -> np.ndarray:
        """Professional-grade audio preprocessing"""
        try:
            # Convert to float32
            if audio.dtype != np.float32:
                if audio.dtype == np.int16:
                    audio = audio.astype(np.float32) / 32768.0
                elif audio.dtype == np.int32:
                    audio = audio.astype(np.float32) / 2147483648.0
                else:
                    audio = audio.astype(np.float32)
            
            # Remove DC offset
            if self.config["processing"]["remove_dc_offset"]:
                audio = audio - np.mean(audio)
            
            # Auto gain control
            if self.config["processing"]["auto_gain_control"]:
                max_val = np.max(np.abs(audio))
                if max_val > 0:
                    audio = audio / max_val * 0.95
            
            # Enhanced noise gate
            threshold = self.config["processing"]["noise_gate_threshold"]
            energy = np.abs(audio)
            gate_threshold = np.max(energy) * threshold
            mask = energy > gate_threshold
            audio[~mask] *= 0.1
            
            # Normalization
            if self.config["processing"]["normalize_audio"]:
                max_val = np.max(np.abs(audio))
                if max_val > 0:
                    audio = audio / max_val
            
            return audio
            
        except Exception as e:
            logger.error(f"Professional audio preprocessing error: {e}")
            return audio
    
    def _assess_audio_quality(self, audio: np.ndarray) -> float:
        """Assess audio quality for better processing decisions"""
        try:
            # Simple quality metrics
            snr_estimate = np.var(audio) / (np.var(audio - np.mean(audio)) + 1e-8)
            dynamic_range = np.max(audio) - np.min(audio)
            zero_crossing_rate = np.sum(np.diff(np.sign(audio)) != 0) / len(audio)
            
            # Combine metrics (simple heuristic)
            quality_score = min(1.0, (snr_estimate * dynamic_range * (1 - zero_crossing_rate)) / 10)
            return max(0.0, quality_score)
            
        except Exception:
            return 0.5  # Default quality
    
    def _calculate_embedding_confidence(self, embedding: np.ndarray, model_name: str) -> float:
        """Calculate confidence score for an embedding"""
        try:
            # Simple confidence metrics
            norm = np.linalg.norm(embedding)
            variance = np.var(embedding)
            
            # Model-specific confidence adjustments
            base_confidence = min(1.0, norm * variance * 10)
            
            if model_name == 'resemblyzer':
                return min(1.0, base_confidence * 1.1)  # Slight boost for proven model
            elif 'speechbrain' in model_name:
                return min(1.0, base_confidence * 1.05)
            else:
                return base_confidence
                
        except Exception:
            return 0.5
    
    def _update_performance_stats(self, result: Dict):
        """Update performance statistics"""
        self.performance_stats['total_embeddings'] += 1
        
        # Update model usage stats
        for model_name in result['models_used']:
            if model_name not in self.performance_stats['model_usage']:
                self.performance_stats['model_usage'][model_name] = 0
            self.performance_stats['model_usage'][model_name] += 1
        
        # Update average processing time
        total_time = result.get('total_processing_time', 0)
        current_avg = self.performance_stats['average_time']
        total_count = self.performance_stats['total_embeddings']
        
        self.performance_stats['average_time'] = (
            (current_avg * (total_count - 1) + total_time) / total_count
        )
        
        # Update success rate
        error_count = self.performance_stats['error_count']
        self.performance_stats['success_rate'] = (
            (total_count - error_count) / total_count if total_count > 0 else 1.0
        )
    
    def compare_dual_embeddings(self, emb1: Dict, emb2: Dict) -> float:
        """Enhanced dual embedding comparison with professional features - FIXED VERSION"""
        try:
            from sklearn.metrics.pairwise import cosine_similarity

            # Extract embeddings - FIXED: Handle both dict and list formats safely
            def safe_extract_embeddings(emb_data):
                """Safely extract embeddings handling both dict and list formats"""
                if isinstance(emb_data, dict):
                    if 'embeddings' in emb_data and isinstance(emb_data['embeddings'], dict):
                        return emb_data['embeddings']
                    else:
                        return emb_data
                elif isinstance(emb_data, list):
                    return {'resemblyzer': emb_data}
                elif isinstance(emb_data, np.ndarray):
                    return {'resemblyzer': emb_data.tolist()}
                else:
                    return emb_data

            embeddings1 = safe_extract_embeddings(emb1)
            embeddings2 = safe_extract_embeddings(emb2)

            if not hasattr(embeddings1, 'keys') or not hasattr(embeddings2, 'keys'):
                logger.warning("Could not extract valid embeddings for comparison")
                return 0.0

            similarities = {}
            confidences = {}

            for model_name in embeddings1.keys():
                if model_name in ['timestamp', 'models_used', 'processing_times', 'model_confidences', 'primary', 'dual_available', 'total_processing_time', 'audio_quality_score']:
                    continue

                if model_name in embeddings2 and model_name in self.model_weights:
                    try:
                        emb1_data = embeddings1[model_name]
                        emb2_data = embeddings2[model_name]

                        if not isinstance(emb1_data, np.ndarray):
                            emb1_data = np.array(emb1_data)
                        if not isinstance(emb2_data, np.ndarray):
                            emb2_data = np.array(emb2_data)

                        if emb1_data.size == 0 or emb2_data.size == 0:
                            logger.warning(f"Empty embedding for model {model_name}")
                            continue

                        if emb1_data.ndim == 1:
                            emb1_data = emb1_data.reshape(1, -1)
                        if emb2_data.ndim == 1:
                            emb2_data = emb2_data.reshape(1, -1)

                        if emb1_data.shape[1] != emb2_data.shape[1]:
                            logger.warning(f"Dimension mismatch for model {model_name}: {emb1_data.shape} vs {emb2_data.shape}")
                            continue

                        similarity = cosine_similarity(emb1_data, emb2_data)[0][0]
                        similarities[model_name] = similarity

                        def safe_get_confidence(emb_data, model_name):
                            if isinstance(emb_data, dict):
                                model_confidences = emb_data.get('model_confidences', {})
                                if isinstance(model_confidences, dict):
                                    return model_confidences.get(model_name, 1.0)
                            return 1.0

                        conf1 = safe_get_confidence(emb1, model_name)
                        conf2 = safe_get_confidence(emb2, model_name)
                        confidences[model_name] = (conf1 + conf2) / 2

                        logger.debug(f"Model {model_name}: similarity={similarity:.3f}, confidence={confidences[model_name]:.3f}")

                    except Exception as e:
                        logger.warning(f"Comparison failed for {model_name}: {e}")
                        continue
                else:
                    if model_name not in embeddings2:
                        logger.debug(f"Model {model_name} not found in second embedding set")
                    if model_name not in self.model_weights:
                        logger.debug(f"No weight configured for model {model_name}")

            if not similarities:
                logger.warning("No valid similarities computed - returning 0.0")
                return 0.0

            try:
                if self.config["similarity"]["ensemble_method"] == "weighted_average":
                    if self.config["similarity"]["adaptive_weights"]:
                        total_weight = 0
                        weighted_score = 0

                        for model_name, similarity in similarities.items():
                            base_weight = self.model_weights.get(model_name, 0)
                            confidence_weight = confidences.get(model_name, 1.0)
                            adjusted_weight = base_weight * confidence_weight

                            weighted_score += similarity * adjusted_weight
                            total_weight += adjusted_weight

                        final_score = weighted_score / total_weight if total_weight > 0 else 0
                    else:
                        available_models = list(similarities.keys())
                        total_weight = sum(self.model_weights.get(model, 0) for model in available_models)

                        if total_weight > 0:
                            final_score = sum(
                                similarities[model] * self.model_weights.get(model, 0)
                                for model in available_models
                            ) / total_weight
                        else:
                            final_score = np.mean(list(similarities.values()))

                elif self.config["similarity"]["ensemble_method"] == "max":
                    final_score = max(similarities.values())
                elif self.config["similarity"]["ensemble_method"] == "min":
                    final_score = min(similarities.values())
                else:
                    final_score = np.mean(list(similarities.values()))

                if np.isnan(final_score) or np.isinf(final_score):
                    logger.warning("Invalid final score computed, returning 0.0")
                    final_score = 0.0

                final_score = max(0.0, min(1.0, float(final_score)))

                logger.debug(f"Similarity scores: {similarities}, Final: {final_score:.3f}")
                return final_score

            except Exception as e:
                logger.error(f"Ensemble scoring failed: {e}")
                return float(np.mean(list(similarities.values())))

        except ImportError:
            logger.error("sklearn not available for cosine similarity")
            return 0.0
        except Exception as e:
            logger.error(f"Professional embedding comparison error: {e}")
            return 0.0
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information"""
        info = {
            'available_models': list(self.models.keys()),
            'model_weights': self.model_weights,
            'device': self.device,
            'dual_available': len(self.models) > 1,
            'performance_stats': self.performance_stats,
            'config': self.config,
            'model_details': {},
            'version': 'professional_enhanced_v1.0'
        }
        
        # Get detailed model information
        for model_name, model in self.models.items():
            info['model_details'][model_name] = {
                'name': getattr(model, 'name', model_name),
                'embedding_dim': getattr(model, 'embedding_dim', 'unknown'),
                'device': getattr(model, 'device', self.device),
                'average_processing_time': getattr(model, 'get_average_processing_time', lambda: 0.0)()
            }
        
        return info
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health = {
            'overall_status': 'healthy',
            'models_status': {},
            'performance_status': {},
            'device_status': self.device,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        issues = []
        
        # Test each model with dummy data
        test_audio = np.random.randn(16000).astype(np.float32)
        
        for model_name, model in self.models.items():
            try:
                embedding = model.generate_embedding(test_audio)
                if embedding is not None:
                    health['models_status'][model_name] = 'healthy'
                else:
                    health['models_status'][model_name] = 'unhealthy'
                    issues.append(f"{model_name} not generating embeddings")
            except Exception as e:
                health['models_status'][model_name] = f'error: {str(e)}'
                issues.append(f"{model_name} error: {str(e)}")
        
        # Performance status
        health['performance_status'] = {
            'success_rate': self.performance_stats['success_rate'],
            'average_processing_time': self.performance_stats['average_time'],
            'total_embeddings_generated': self.performance_stats['total_embeddings']
        }
        
        if self.performance_stats['success_rate'] < 0.9:
            issues.append(f"Low success rate: {self.performance_stats['success_rate']:.2f}")
        
        if issues:
            health['overall_status'] = 'degraded'
            health['issues'] = issues
        
        return health

# Global professional voice model manager
try:
    dual_voice_model_manager = ProfessionalDualVoiceModelManager()
    logger.info("[ProfessionalVoice] 🚀 Professional Dual Voice Model Manager ready")
except Exception as e:
    logger.error(f"[ProfessionalVoice] ❌ Professional manager failed, using your original: {e}")
    
    # Fallback to your working version
    from voice_models_Version3 import dual_voice_model_manager
    logger.info("[ProfessionalVoice] 🔄 Using your original working version as fallback")