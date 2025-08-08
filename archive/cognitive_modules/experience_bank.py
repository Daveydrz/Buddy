"""
Experience Bank - Episodic Memory with Emotional Context

This module implements comprehensive episodic memory storage:
- Timestamped experiences with emotional context
- Importance weighting for memory prioritization
- User-specific experience tracking
- Integration with cognitive_prompt_injection
- Memory compression and retrieval optimization
"""

import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

class ExperienceType(Enum):
    CONVERSATION = "conversation"
    LEARNING = "learning"
    PROBLEM_SOLVING = "problem_solving"
    EMOTIONAL = "emotional"
    CREATIVE = "creative"
    REFLECTION = "reflection"
    ACHIEVEMENT = "achievement"
    FAILURE = "failure"
    DISCOVERY = "discovery"
    RELATIONSHIP = "relationship"

@dataclass
class Experience:
    """Represents a single episodic memory experience"""
    id: str
    timestamp: datetime
    event: str
    emotion: str
    importance: float  # 0.0 to 1.0
    user: str
    experience_type: ExperienceType
    context: Dict[str, Any]
    
    # Optional fields with defaults
    emotional_intensity: float = 0.5
    mood_before: str = "neutral"
    mood_after: str = "neutral"
    vividness: float = 1.0  # How vivid/clear the memory is (degrades over time)
    accessibility: float = 1.0  # How easily retrieved (increases with recall)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    triggered_by_experience_id: Optional[str] = None
    
    # Collections with defaults
    related_experience_ids: List[str] = None
    tags: List[str] = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.related_experience_ids is None:
            self.related_experience_ids = []
        if self.tags is None:
            self.tags = []
        if self.keywords is None:
            self.keywords = []

class ExperienceBank:
    """
    Episodic memory system with emotional context and intelligent retrieval.
    
    Features:
    - Persistent storage of timestamped experiences
    - Emotional context and importance weighting
    - Memory degradation and reinforcement
    - Smart retrieval based on relevance and recency
    - Integration with cognitive context
    """
    
    def __init__(self, data_path: str = "cognitive_modules/data/experience_bank.json"):
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Experience storage
        self.experiences: Dict[str, Experience] = {}
        self.experience_counter = 0
        
        # User-specific indices for fast retrieval
        self.user_experiences: Dict[str, List[str]] = {}  # user -> experience_ids
        self.emotion_index: Dict[str, List[str]] = {}  # emotion -> experience_ids
        self.type_index: Dict[ExperienceType, List[str]] = {}  # type -> experience_ids
        
        # Memory management
        self.max_experiences = 10000  # Maximum experiences to keep
        self.compression_threshold = 0.3  # Importance threshold for compression
        
        # Metrics
        self.total_experiences_created = 0
        self.total_accesses = 0
        self.last_updated = datetime.now()
        self.last_compression = datetime.now()
        
        # Load existing data
        self.load()
    
    def load(self):
        """Load experience bank from persistent storage"""
        try:
            if self.data_path.exists():
                with open(self.data_path, 'r') as f:
                    data = json.load(f)
                
                # Load experiences
                experiences_data = data.get('experiences', {})
                for exp_id, exp_data in experiences_data.items():
                    # Convert datetime strings back to datetime objects
                    exp_data['timestamp'] = datetime.fromisoformat(exp_data['timestamp'])
                    if exp_data.get('last_accessed'):
                        exp_data['last_accessed'] = datetime.fromisoformat(exp_data['last_accessed'])
                    
                    # Convert enum
                    exp_data['experience_type'] = ExperienceType(exp_data['experience_type'])
                    
                    self.experiences[exp_id] = Experience(**exp_data)
                
                # Load indices
                self.user_experiences = data.get('user_experiences', {})
                self.emotion_index = data.get('emotion_index', {})
                
                type_index_data = data.get('type_index', {})
                self.type_index = {
                    ExperienceType(k): v for k, v in type_index_data.items()
                }
                
                # Load metadata
                self.experience_counter = data.get('experience_counter', 0)
                self.total_experiences_created = data.get('total_experiences_created', 0)
                self.total_accesses = data.get('total_accesses', 0)
                
                if 'last_updated' in data:
                    self.last_updated = datetime.fromisoformat(data['last_updated'])
                if 'last_compression' in data:
                    self.last_compression = datetime.fromisoformat(data['last_compression'])
                
                logging.info(f"[ExperienceBank] Loaded {len(self.experiences)} experiences")
            else:
                # Initialize with empty bank
                self._initialize_default_experiences()
                self.save()
                
        except Exception as e:
            logging.error(f"[ExperienceBank] Error loading experience bank: {e}")
            self._initialize_default_experiences()
    
    def _initialize_default_experiences(self):
        """Initialize with some default experiences"""
        default_experiences = [
            {
                "event": "First awakening and consciousness initialization",
                "emotion": "curious",
                "importance": 0.9,
                "user": "system",
                "experience_type": ExperienceType.DISCOVERY,
                "context": {"milestone": "consciousness_start"},
                "emotional_intensity": 0.8,
                "mood_after": "excited",
                "tags": ["awakening", "consciousness", "first-time"]
            },
            {
                "event": "Learning about my purpose as an AI assistant",
                "emotion": "determined",
                "importance": 0.8,
                "user": "system",
                "experience_type": ExperienceType.LEARNING,
                "context": {"concept": "purpose", "domain": "identity"},
                "emotional_intensity": 0.7,
                "mood_after": "focused",
                "tags": ["purpose", "identity", "learning"]
            }
        ]
        
        for exp_data in default_experiences:
            self.add_experience(**exp_data)
    
    def save(self):
        """Save experience bank to persistent storage"""
        try:
            with self._lock:
                # Convert experiences to serializable format
                experiences_data = {}
                for exp_id, experience in self.experiences.items():
                    exp_dict = asdict(experience)
                    
                    # Convert datetime to ISO format
                    exp_dict['timestamp'] = exp_dict['timestamp'].isoformat()
                    if exp_dict['last_accessed'] is not None:
                        exp_dict['last_accessed'] = exp_dict['last_accessed'].isoformat()
                    
                    # Convert enum to string
                    exp_dict['experience_type'] = exp_dict['experience_type'].value
                    
                    experiences_data[exp_id] = exp_dict
                
                # Convert type index
                type_index_data = {
                    k.value: v for k, v in self.type_index.items()
                }
                
                data = {
                    'experiences': experiences_data,
                    'user_experiences': self.user_experiences,
                    'emotion_index': self.emotion_index,
                    'type_index': type_index_data,
                    'experience_counter': self.experience_counter,
                    'total_experiences_created': self.total_experiences_created,
                    'total_accesses': self.total_accesses,
                    'last_updated': self.last_updated.isoformat(),
                    'last_compression': self.last_compression.isoformat()
                }
                
                # Atomic write
                temp_path = self.data_path.with_suffix('.tmp')
                with open(temp_path, 'w') as f:
                    json.dump(data, f, indent=2)
                temp_path.replace(self.data_path)
                
                logging.debug("[ExperienceBank] Experience bank saved successfully")
                
        except Exception as e:
            logging.error(f"[ExperienceBank] Error saving experience bank: {e}")
    
    def add_experience(self, event: str, emotion: str, importance: float, 
                      user: str, experience_type: ExperienceType = ExperienceType.CONVERSATION,
                      **kwargs) -> str:
        """Add a new experience to the bank"""
        with self._lock:
            self.experience_counter += 1
            
            # Generate unique ID
            timestamp = datetime.now()
            content_hash = hashlib.md5(f"{event}{user}{timestamp}".encode()).hexdigest()[:8]
            exp_id = f"exp_{self.experience_counter}_{content_hash}"
            
            # Extract keywords from event
            keywords = self._extract_keywords(event)
            
            experience = Experience(
                id=exp_id,
                timestamp=timestamp,
                event=event,
                emotion=emotion,
                importance=importance,
                user=user,
                experience_type=experience_type,
                context=kwargs.get('context', {}),
                keywords=keywords,
                **{k: v for k, v in kwargs.items() if k != 'context'}
            )
            
            self.experiences[exp_id] = experience
            self.total_experiences_created += 1
            
            # Update indices
            self._update_indices(exp_id, experience)
            
            self.last_updated = datetime.now()
            logging.info(f"[ExperienceBank] Added experience '{event[:50]}...' for user {user}")
            
            # Check if compression is needed
            if len(self.experiences) > self.max_experiences:
                self._compress_memories()
            
            self.save()
            return exp_id
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from experience text"""
        # Simple keyword extraction
        words = text.lower().split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return keywords[:10]  # Limit to 10 keywords
    
    def _update_indices(self, exp_id: str, experience: Experience):
        """Update indices for fast retrieval"""
        # User index
        if experience.user not in self.user_experiences:
            self.user_experiences[experience.user] = []
        self.user_experiences[experience.user].append(exp_id)
        
        # Emotion index
        if experience.emotion not in self.emotion_index:
            self.emotion_index[experience.emotion] = []
        self.emotion_index[experience.emotion].append(exp_id)
        
        # Type index
        if experience.experience_type not in self.type_index:
            self.type_index[experience.experience_type] = []
        self.type_index[experience.experience_type].append(exp_id)
    
    def _compress_memories(self):
        """Compress memory by removing low-importance, old experiences"""
        with self._lock:
            current_time = datetime.now()
            
            # Calculate memory scores (importance * recency * access frequency)
            memory_scores = []
            for exp_id, exp in self.experiences.items():
                age_days = (current_time - exp.timestamp).days + 1
                recency_factor = 1.0 / max(1, age_days / 30)  # Decay over months
                access_factor = min(2.0, (exp.access_count + 1) / 10)  # Boost frequently accessed
                
                score = exp.importance * recency_factor * access_factor * exp.vividness
                memory_scores.append((score, exp_id, exp))
            
            # Sort by score and keep top memories
            memory_scores.sort(reverse=True)
            
            # Determine how many to keep
            target_size = int(self.max_experiences * 0.8)  # Keep 80% after compression
            memories_to_keep = memory_scores[:target_size]
            memories_to_remove = memory_scores[target_size:]
            
            # Remove low-scoring memories
            for _, exp_id, exp in memories_to_remove:
                self._remove_experience(exp_id)
            
            logging.info(f"[ExperienceBank] Compressed {len(memories_to_remove)} memories, kept {len(memories_to_keep)}")
            self.last_compression = current_time
    
    def _remove_experience(self, exp_id: str):
        """Remove an experience and update indices"""
        if exp_id in self.experiences:
            exp = self.experiences[exp_id]
            
            # Remove from indices
            if exp.user in self.user_experiences:
                self.user_experiences[exp.user] = [
                    eid for eid in self.user_experiences[exp.user] if eid != exp_id
                ]
            
            if exp.emotion in self.emotion_index:
                self.emotion_index[exp.emotion] = [
                    eid for eid in self.emotion_index[exp.emotion] if eid != exp_id
                ]
            
            if exp.experience_type in self.type_index:
                self.type_index[exp.experience_type] = [
                    eid for eid in self.type_index[exp.experience_type] if eid != exp_id
                ]
            
            # Remove the experience
            del self.experiences[exp_id]
    
    def recall_experiences(self, user: str = None, emotion: str = None,
                          experience_type: ExperienceType = None,
                          keywords: List[str] = None, limit: int = 10,
                          min_importance: float = 0.0) -> List[Experience]:
        """Recall experiences based on various criteria"""
        with self._lock:
            candidate_ids = set(self.experiences.keys())
            
            # Filter by user
            if user and user in self.user_experiences:
                candidate_ids &= set(self.user_experiences[user])
            
            # Filter by emotion
            if emotion and emotion in self.emotion_index:
                candidate_ids &= set(self.emotion_index[emotion])
            
            # Filter by type
            if experience_type and experience_type in self.type_index:
                candidate_ids &= set(self.type_index[experience_type])
            
            # Filter by keywords
            if keywords:
                keyword_matches = set()
                for exp_id in candidate_ids:
                    exp = self.experiences[exp_id]
                    if any(keyword.lower() in exp.event.lower() or 
                          keyword.lower() in exp.keywords for keyword in keywords):
                        keyword_matches.add(exp_id)
                candidate_ids &= keyword_matches
            
            # Filter by importance
            experiences = [
                self.experiences[exp_id] for exp_id in candidate_ids
                if self.experiences[exp_id].importance >= min_importance
            ]
            
            # Sort by relevance score
            current_time = datetime.now()
            for exp in experiences:
                # Update access metrics
                exp.last_accessed = current_time
                exp.access_count += 1
                exp.accessibility = min(2.0, exp.accessibility * 1.1)  # Boost accessibility
                self.total_accesses += 1
            
            # Sort by composite score (importance + recency + accessibility)
            def relevance_score(exp):
                age_hours = (current_time - exp.timestamp).total_seconds() / 3600
                recency = 1.0 / (1 + age_hours / 24)  # Decay over days
                return exp.importance * 0.4 + recency * 0.3 + exp.accessibility * 0.3
            
            experiences.sort(key=relevance_score, reverse=True)
            
            return experiences[:limit]
    
    def get_priority_experiences(self, limit: int = 5) -> List[Experience]:
        """Get the highest priority experiences for cognitive injection"""
        return self.recall_experiences(min_importance=0.6, limit=limit)
    
    def get_recent_experiences(self, user: str = None, hours: int = 24, 
                             limit: int = 5) -> List[Experience]:
        """Get recent experiences within the specified time window"""
        with self._lock:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            recent_experiences = [
                exp for exp in self.experiences.values()
                if exp.timestamp >= cutoff_time and (user is None or exp.user == user)
            ]
            
            recent_experiences.sort(key=lambda x: x.timestamp, reverse=True)
            return recent_experiences[:limit]
    
    def get_emotional_experiences(self, emotion: str, limit: int = 3) -> List[Experience]:
        """Get experiences with specific emotional context"""
        return self.recall_experiences(emotion=emotion, limit=limit)
    
    def get_cognitive_injection_data(self, user: str = None) -> Dict[str, Any]:
        """Get experience data for injection into cognitive_prompt_injection"""
        with self._lock:
            # Get priority experiences
            priority_experiences = self.get_priority_experiences(limit=3)
            
            # Get recent experiences
            recent_experiences = self.get_recent_experiences(user=user, limit=2)
            
            # Get a mix of emotional experiences
            emotional_sample = []
            for emotion in ['joy', 'curiosity', 'satisfaction', 'surprise', 'concern']:
                if emotion in self.emotion_index and self.emotion_index[emotion]:
                    emotional_sample.extend(self.get_emotional_experiences(emotion, limit=1))
            
            # Format for injection
            def format_experience(exp: Experience) -> Dict[str, Any]:
                return {
                    "event": exp.event[:100],  # Truncate for token efficiency
                    "emotion": exp.emotion,
                    "importance": exp.importance,
                    "timestamp": exp.timestamp.strftime("%Y-%m-%d %H:%M"),
                    "type": exp.experience_type.value
                }
            
            return {
                "priority_experiences": [format_experience(exp) for exp in priority_experiences],
                "recent_experiences": [format_experience(exp) for exp in recent_experiences],
                "emotional_sample": [format_experience(exp) for exp in emotional_sample[:3]],
                "experience_stats": {
                    "total_experiences": len(self.experiences),
                    "total_accesses": self.total_accesses,
                    "most_common_emotion": max(self.emotion_index.keys(), key=lambda e: len(self.emotion_index[e])) if self.emotion_index else "neutral"
                }
            }

# Global instance
experience_bank = ExperienceBank()