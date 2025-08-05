# voice/smart_voice_recognition.py - Smart Voice Recognition Layer
# Works with your existing voice_models.py without modifying it

import numpy as np
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from collections import defaultdict

# Import your existing voice models
try:
    from voice.voice_models import dual_voice_model_manager
    VOICE_MODELS_AVAILABLE = True
    print("[SmartVoice] ✅ Using your existing voice_models.py")
except ImportError:
    VOICE_MODELS_AVAILABLE = False
    print("[SmartVoice] ❌ voice_models.py not available")

# Import voice database
try:
    from voice.database import known_users, anonymous_clusters, save_known_users, link_anonymous_to_named
    DATABASE_AVAILABLE = True
    print("[SmartVoice] ✅ Voice database available")
except ImportError:
    DATABASE_AVAILABLE = False
    known_users = {}
    anonymous_clusters = {}
    def save_known_users(): pass
    def link_anonymous_to_named(cluster_id, name): return True
    print("[SmartVoice] ⚠️ Voice database not available - using fallback")

class SmartVoiceCluster:
    """🎯 Enhanced cluster that works with your existing system"""
    
    def __init__(self, username: str, cluster_id: str):
        self.username = username
        self.cluster_id = cluster_id
        self.embeddings = []  # List of your existing embeddings
        self.voice_states = set(['normal'])
        self.recognition_count = 0
        self.last_seen = datetime.utcnow().isoformat()
        self.similarities_history = []
        
    def add_embedding(self, embedding_data: Dict, voice_state: str = "normal"):
        """Add embedding (your format) to this cluster"""
        enhanced_embedding = {
            'embedding_data': embedding_data,
            'voice_state': voice_state,
            'timestamp': datetime.utcnow().isoformat(),
            'quality_score': self._assess_embedding_quality(embedding_data)
        }
        
        self.embeddings.append(enhanced_embedding)
        self.voice_states.add(voice_state)
        self.recognition_count += 1
        self.last_seen = datetime.utcnow().isoformat()
        
        # Keep only last 50 embeddings
        if len(self.embeddings) > 50:
            self.embeddings = self.embeddings[-50:]
    
    def _assess_embedding_quality(self, embedding_data: Dict) -> float:
        """Assess quality of your embedding format"""
        try:
            # Check if it's dual embedding or single
            if 'embeddings' in embedding_data:
                # Your dual embedding format
                embeddings = embedding_data['embeddings']
                if 'resemblyzer' in embeddings and 'speechbrain_ecapa' in embeddings:
                    return 1.0  # High quality - dual model
                elif 'resemblyzer' in embeddings or 'speechbrain_ecapa' in embeddings:
                    return 0.8  # Good quality - single model
            else:
                # Single embedding
                return 0.6
            
            return 0.5
        except:
            return 0.3
    
    def get_best_embeddings(self, max_count: int = 10) -> List[Dict]:
        """Get best quality embeddings for comparison"""
        if not self.embeddings:
            return []
        
        # Sort by quality score and recency
        sorted_embeddings = sorted(
            self.embeddings, 
            key=lambda x: (x.get('quality_score', 0), x.get('timestamp', '')), 
            reverse=True
        )
        
        return [emb['embedding_data'] for emb in sorted_embeddings[:max_count]]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for saving"""
        return {
            'username': self.username,
            'cluster_id': self.cluster_id,
            'embeddings': self.embeddings,
            'voice_states': list(self.voice_states),
            'recognition_count': self.recognition_count,
            'last_seen': self.last_seen,
            'similarities_history': self.similarities_history[-100:]  # Keep last 100
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        cluster = cls(data['username'], data['cluster_id'])
        cluster.embeddings = data.get('embeddings', [])
        cluster.voice_states = set(data.get('voice_states', ['normal']))
        cluster.recognition_count = data.get('recognition_count', 0)
        cluster.last_seen = data.get('last_seen', datetime.utcnow().isoformat())
        cluster.similarities_history = data.get('similarities_history', [])
        return cluster

class SmartVoiceRecognition:
    """🎯 Smart voice recognition that enhances your existing system"""
    
    def __init__(self, data_dir: str = "voice_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Smart clusters (enhanced version of your data)
        self.smart_clusters: Dict[str, SmartVoiceCluster] = {}
        
        # Session management
        self.active_cluster_id: Optional[str] = None
        self.last_similarity = 0.0
        self.session_start_time = datetime.utcnow()
        
        # Smart thresholds (you can adjust these)
        self.thresholds = {
            'direct_match': 0.85,      # High confidence - direct recognition
            'fallback_confirm': 0.70,  # Medium confidence - ask for confirmation
            'reject_threshold': 0.50   # Low confidence - reject
        }
        
        # Performance tracking
        self.stats = {
            'total_recognitions': 0,
            'direct_matches': 0,
            'fallback_confirms': 0,
            'rejections': 0,
            'avg_processing_time': 0.0
        }
        
        # Load existing data
        self._load_smart_clusters()
        self._sync_with_existing_database()
        
        print(f"[SmartVoice] 🎯 Initialized with {len(self.smart_clusters)} smart clusters")
    
    def _sync_with_existing_database(self):
        """Sync with your existing known_users and anonymous_clusters"""
        try:
            # Import from known_users
            for username, user_data in known_users.items():
                if isinstance(user_data, dict) and user_data.get('status') == 'trained':
                    cluster_id = f"smart_{username}_{int(time.time())}"
                    
                    if cluster_id not in self.smart_clusters:
                        smart_cluster = SmartVoiceCluster(username, cluster_id)
                        
                        # Add existing embeddings if available
                        if 'voice_embeddings' in user_data:
                            for embedding in user_data['voice_embeddings'][-10:]:  # Last 10
                                smart_cluster.add_embedding({'embeddings': {'imported': embedding}})
                        
                        self.smart_clusters[cluster_id] = smart_cluster
                        print(f"[SmartVoice] 📥 Imported {username} from known_users")
            
            print(f"[SmartVoice] ✅ Synced with existing database")
            
        except Exception as e:
            print(f"[SmartVoice] ❌ Sync error: {e}")
    
    def recognize_speaker(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Dict:
        """🎯 Main recognition method using your existing voice_models.py"""
        
        start_time = time.time()
        print(f"[SmartVoice] 🎯 Recognizing speaker...")
        
        if not VOICE_MODELS_AVAILABLE:
            return {'status': 'error', 'message': 'Voice models not available'}
        
        try:
            # Use YOUR existing dual_voice_model_manager
            current_embedding = dual_voice_model_manager.generate_dual_embedding(audio_data)
            
            if not current_embedding:
                return {'status': 'error', 'message': 'Failed to generate embedding'}
            
            # Check active session first (session continuity)
            if self.active_cluster_id and self.active_cluster_id in self.smart_clusters:
                active_cluster = self.smart_clusters[self.active_cluster_id]
                session_similarity = self._compare_with_cluster(current_embedding, active_cluster)
                
                if session_similarity > self.thresholds['direct_match']:
                    # Continue active session
                    active_cluster.add_embedding(current_embedding)
                    self.last_similarity = session_similarity
                    
                    processing_time = time.time() - start_time
                    self._update_stats('direct_match', processing_time)
                    
                    print(f"[SmartVoice] ✅ Session continued: {active_cluster.username} (sim: {session_similarity:.3f})")
                    
                    return {
                        'status': 'recognized',
                        'username': active_cluster.username,
                        'cluster_id': active_cluster.cluster_id,
                        'similarity': session_similarity,
                        'method': 'session_continuity',
                        'processing_time': processing_time
                    }
            
            # Find best match across all clusters
            best_match = self._find_best_match(current_embedding)
            
            processing_time = time.time() - start_time
            self.last_similarity = best_match['similarity']
            
            # Decision logic based on similarity
            if best_match['similarity'] > self.thresholds['direct_match']:
                # High confidence - direct match
                best_cluster = best_match['cluster']
                best_cluster.add_embedding(current_embedding)
                self.active_cluster_id = best_cluster.cluster_id
                
                self._update_stats('direct_match', processing_time)
                
                print(f"[SmartVoice] ✅ Direct match: {best_cluster.username} (sim: {best_match['similarity']:.3f})")
                
                return {
                    'status': 'recognized',
                    'username': best_cluster.username,
                    'cluster_id': best_cluster.cluster_id,
                    'similarity': best_match['similarity'],
                    'method': 'direct_match',
                    'processing_time': processing_time
                }
            
            elif best_match['similarity'] > self.thresholds['fallback_confirm']:
                # Medium confidence - need confirmation
                self._update_stats('fallback_confirm', processing_time)
                
                print(f"[SmartVoice] ❓ Needs confirmation: {best_match['cluster'].username if best_match['cluster'] else 'Unknown'} (sim: {best_match['similarity']:.3f})")
                
                return {
                    'status': 'needs_confirmation',
                    'suspected_username': best_match['cluster'].username if best_match['cluster'] else None,
                    'suspected_cluster_id': best_match['cluster'].cluster_id if best_match['cluster'] else None,
                    'similarity': best_match['similarity'],
                    'method': 'fallback_confirm',
                    'processing_time': processing_time,
                    'pending_embedding': current_embedding
                }
            
            else:
                # Low confidence - unknown speaker
                self._update_stats('rejection', processing_time)
                
                print(f"[SmartVoice] ❓ Unknown speaker (best sim: {best_match['similarity']:.3f})")
                
                return {
                    'status': 'unknown',
                    'similarity': best_match['similarity'],
                    'method': 'unknown',
                    'processing_time': processing_time,
                    'pending_embedding': current_embedding
                }
        
        except Exception as e:
            print(f"[SmartVoice] ❌ Recognition error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _compare_with_cluster(self, current_embedding: Dict, cluster: SmartVoiceCluster) -> float:
        """Compare current embedding with cluster using YOUR comparison method"""
        
        if not cluster.embeddings:
            return 0.0
        
        # Get best embeddings from cluster
        cluster_embeddings = cluster.get_best_embeddings(5)  # Compare with 5 best
        
        similarities = []
        
        for stored_embedding in cluster_embeddings:
            try:
                # Use YOUR existing comparison method
                similarity = dual_voice_model_manager.compare_dual_embeddings(
                    current_embedding, stored_embedding
                )
                similarities.append(similarity)
                
            except Exception as e:
                print(f"[SmartVoice] ❌ Comparison error: {e}")
                continue
        
        if not similarities:
            return 0.0
        
        # Use maximum similarity (best match)
        max_similarity = max(similarities)
        
        # Store similarity history
        cluster.similarities_history.append({
            'similarity': max_similarity,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return max_similarity
    
    def _find_best_match(self, current_embedding: Dict) -> Dict:
        """Find best matching cluster"""
        
        best_similarity = 0.0
        best_cluster = None
        
        for cluster in self.smart_clusters.values():
            similarity = self._compare_with_cluster(current_embedding, cluster)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_cluster = cluster
        
        return {
            'similarity': best_similarity,
            'cluster': best_cluster
        }
    
    def confirm_recognition(self, confirmed: bool, pending_data: Dict, voice_state: str = "normal"):
        """Handle confirmation response"""
        
        if not confirmed:
            print("[SmartVoice] ❌ Recognition rejected by user")
            return
        
        pending_embedding = pending_data.get('pending_embedding')
        if not pending_embedding:
            return
        
        if 'suspected_cluster_id' in pending_data:
            # Add to existing cluster
            cluster = self.smart_clusters[pending_data['suspected_cluster_id']]
            cluster.add_embedding(pending_embedding, voice_state)
            self.active_cluster_id = cluster.cluster_id
            
            print(f"[SmartVoice] ✅ Confirmed and added to {cluster.username}")
        
        self._save_smart_clusters()
    
    def create_new_cluster(self, username: str, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """Create new smart cluster"""
        
        if not VOICE_MODELS_AVAILABLE:
            return None
        
        try:
            # Generate unique cluster ID
            cluster_id = f"smart_{username.lower()}_{int(time.time())}"
            
            # Create cluster
            cluster = SmartVoiceCluster(username, cluster_id)
            
            # Generate initial embedding using YOUR system
            initial_embedding = dual_voice_model_manager.generate_dual_embedding(audio_data)
            
            if initial_embedding:
                cluster.add_embedding(initial_embedding, "normal")
                
                # Store cluster
                self.smart_clusters[cluster_id] = cluster
                self.active_cluster_id = cluster_id
                
                print(f"[SmartVoice] ✅ Created smart cluster: {cluster_id} for {username}")
                
                # Also update your existing database
                if DATABASE_AVAILABLE:
                    if username not in known_users:
                        known_users[username] = {
                            'status': 'trained',
                            'username': username,
                            'voice_embeddings': [initial_embedding],
                            'created_at': datetime.utcnow().isoformat(),
                            'last_updated': datetime.utcnow().isoformat(),
                            'smart_cluster_id': cluster_id
                        }
                        save_known_users()
                
                self._save_smart_clusters()
                return cluster_id
            
            return None
            
        except Exception as e:
            print(f"[SmartVoice] ❌ Cluster creation error: {e}")
            return None
    
    def force_recognition_check(self, claimed_username: str, audio_data: np.ndarray, sample_rate: int = 16000) -> Dict:
        """Handle when someone claims to be a specific user"""
        
        if not VOICE_MODELS_AVAILABLE:
            return {'status': 'error', 'message': 'Voice models not available'}
        
        try:
            # Find clusters for this username
            target_clusters = [
                cluster for cluster in self.smart_clusters.values()
                if cluster.username.lower() == claimed_username.lower()
            ]
            
            if not target_clusters:
                return {
                    'status': 'user_not_found',
                    'message': f"I don't know anyone named {claimed_username}"
                }
            
            # Generate embedding for current audio
            current_embedding = dual_voice_model_manager.generate_dual_embedding(audio_data)
            
            if not current_embedding:
                return {'status': 'error', 'message': 'Failed to generate embedding'}
            
            # Check against all user's clusters
            best_similarity = 0.0
            best_cluster = None
            
            for cluster in target_clusters:
                similarity = self._compare_with_cluster(current_embedding, cluster)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_cluster = cluster
            
            # Decision logic
            if best_similarity > self.thresholds['direct_match']:
                # High confidence - accept
                best_cluster.add_embedding(current_embedding)
                self.active_cluster_id = best_cluster.cluster_id
                
                return {
                    'status': 'verified',
                    'username': claimed_username,
                    'similarity': best_similarity,
                    'message': f"Welcome back, {claimed_username}!"
                }
            
            elif best_similarity > self.thresholds['fallback_confirm']:
                # Medium confidence - ask for confirmation
                return {
                    'status': 'verify_confirm',
                    'similarity': best_similarity,
                    'message': f"I'm not completely sure you're {claimed_username}. Can you say another phrase?",
                    'pending_data': {
                        'suspected_username': claimed_username,
                        'suspected_cluster_id': best_cluster.cluster_id,
                        'similarity': best_similarity,
                        'pending_embedding': current_embedding
                    }
                }
            
            else:
                # Low confidence - reject
                return {
                    'status': 'verify_rejected',
                    'similarity': best_similarity,
                    'message': f"Sorry, I don't think you're {claimed_username}. Your voice is quite different."
                }
        
        except Exception as e:
            print(f"[SmartVoice] ❌ Force recognition error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _update_stats(self, result_type: str, processing_time: float):
        """Update performance statistics"""
        self.stats['total_recognitions'] += 1
        
        if result_type == 'direct_match':
            self.stats['direct_matches'] += 1
        elif result_type == 'fallback_confirm':
            self.stats['fallback_confirms'] += 1
        elif result_type == 'rejection':
            self.stats['rejections'] += 1
        
        # Update average processing time
        total = self.stats['total_recognitions']
        current_avg = self.stats['avg_processing_time']
        self.stats['avg_processing_time'] = ((current_avg * (total - 1)) + processing_time) / total
    
    def get_stats(self) -> Dict:
        """Get performance statistics"""
        total = self.stats['total_recognitions']
        
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            'direct_match_rate': self.stats['direct_matches'] / total,
            'fallback_confirm_rate': self.stats['fallback_confirms'] / total,
            'rejection_rate': self.stats['rejections'] / total,
            'total_clusters': len(self.smart_clusters),
            'active_cluster': self.active_cluster_id
        }
    
    def debug_status(self):
        """Debug current status"""
        print("\n" + "="*60)
        print("🎯 SMART VOICE RECOGNITION DEBUG")
        print("="*60)
        
        print(f"📊 Statistics:")
        stats = self.get_stats()
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  • {key}: {value:.3f}")
            else:
                print(f"  • {key}: {value}")
        
        print(f"\n🎯 Smart Clusters ({len(self.smart_clusters)}):")
        for cluster_id, cluster in self.smart_clusters.items():
            print(f"  • {cluster.username}: {len(cluster.embeddings)} embeddings, states: {cluster.voice_states}")
        
        print(f"\n🔊 Voice Models Status:")
        print(f"  • Available: {VOICE_MODELS_AVAILABLE}")
        print(f"  • Database: {DATABASE_AVAILABLE}")
        
        if VOICE_MODELS_AVAILABLE:
            try:
                model_info = dual_voice_model_manager.get_model_info()
                print(f"  • Models: {model_info.get('available_models', 'unknown')}")
                print(f"  • Dual Available: {model_info.get('dual_available', 'unknown')}")
            except:
                print(f"  • Model info not available")
        
        print("="*60 + "\n")
    
    def _save_smart_clusters(self):
        """Save smart clusters to disk"""
        try:
            clusters_data = {
                cluster_id: cluster.to_dict() 
                for cluster_id, cluster in self.smart_clusters.items()
            }
            
            save_path = self.data_dir / "smart_voice_clusters.json"
            with open(save_path, 'w') as f:
                json.dump(clusters_data, f, indent=2)
            
            print(f"[SmartVoice] 💾 Saved {len(self.smart_clusters)} smart clusters")
            
        except Exception as e:
            print(f"[SmartVoice] ❌ Save failed: {e}")
    
    def _load_smart_clusters(self):
        """Load smart clusters from disk"""
        try:
            save_path = self.data_dir / "smart_voice_clusters.json"
            if save_path.exists():
                with open(save_path, 'r') as f:
                    clusters_data = json.load(f)
                
                self.smart_clusters = {
                    cluster_id: SmartVoiceCluster.from_dict(data)
                    for cluster_id, data in clusters_data.items()
                }
                
                print(f"[SmartVoice] 📁 Loaded {len(self.smart_clusters)} smart clusters")
            
        except Exception as e:
            print(f"[SmartVoice] ❌ Load failed: {e}")

# Global instance
smart_voice_recognition = SmartVoiceRecognition()