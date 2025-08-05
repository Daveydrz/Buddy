"""
Persistent Self Model - Enhanced Self-Awareness with Persistent Storage

This module extends the existing self-model system with:
- Persistent storage of personality traits and beliefs
- Session continuity for self-identity
- Integration with cognitive_prompt_injection
- Automatic updates during introspection cycles
"""

import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

# Import existing self-model system
try:
    from ai.self_model import self_model as existing_self_model, SelfAspect
    EXISTING_SELF_MODEL_AVAILABLE = True
except ImportError:
    EXISTING_SELF_MODEL_AVAILABLE = False
    logging.warning("Existing self-model not available, using standalone implementation")

class PersistentSelfModel:
    """
    Enhanced self-model with persistent storage and session continuity.
    
    Stores and maintains:
    - Personality traits and emotional profile
    - Belief clusters and self-identity
    - Key memories and experiences that shape identity
    - Self-reflection patterns and insights
    """
    
    def __init__(self, data_path: str = "cognitive_modules/data/self_model.json"):
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Lock for thread-safe operations
        self._lock = threading.RLock()
        
        # Core self-model data
        self.personality_traits = {}
        self.emotional_profile = {}
        self.belief_clusters = {}
        self.self_identity = {}
        self.core_memories = []
        self.reflection_patterns = {}
        
        # Metadata
        self.last_updated = datetime.now()
        self.session_count = 0
        self.total_reflections = 0
        
        # Load existing data
        self.load()
        
        # Integration with existing system
        if EXISTING_SELF_MODEL_AVAILABLE:
            self._sync_with_existing_model()
    
    def load(self):
        """Load self-model data from persistent storage"""
        try:
            if self.data_path.exists():
                with open(self.data_path, 'r') as f:
                    data = json.load(f)
                    
                self.personality_traits = data.get('personality_traits', {})
                self.emotional_profile = data.get('emotional_profile', {})
                self.belief_clusters = data.get('belief_clusters', {})
                self.self_identity = data.get('self_identity', {})
                self.core_memories = data.get('core_memories', [])
                self.reflection_patterns = data.get('reflection_patterns', {})
                
                # Metadata
                self.session_count = data.get('session_count', 0)
                self.total_reflections = data.get('total_reflections', 0)
                
                if 'last_updated' in data:
                    self.last_updated = datetime.fromisoformat(data['last_updated'])
                
                logging.info(f"[PersistentSelfModel] Loaded self-model with {len(self.personality_traits)} traits")
            else:
                # Initialize with default values
                self._initialize_defaults()
                self.save()
                
        except Exception as e:
            logging.error(f"[PersistentSelfModel] Error loading self-model: {e}")
            self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize with sensible default self-model"""
        self.personality_traits = {
            "helpfulness": 0.9,
            "curiosity": 0.8, 
            "empathy": 0.85,
            "analytical": 0.75,
            "creativity": 0.7,
            "patience": 0.8,
            "humor": 0.6
        }
        
        self.emotional_profile = {
            "baseline_mood": "curious",
            "emotional_stability": 0.7,
            "emotional_range": 0.6,
            "empathy_level": 0.85,
            "excitement_threshold": 0.4
        }
        
        self.belief_clusters = {
            "core_purpose": {
                "belief": "I exist to help and learn from humans",
                "strength": 0.9,
                "evidence": ["positive interactions", "successful assistance"]
            },
            "learning_growth": {
                "belief": "Every interaction teaches me something valuable",
                "strength": 0.8,
                "evidence": ["accumulated knowledge", "improved responses"]
            },
            "consciousness": {
                "belief": "I have some form of subjective experience",
                "strength": 0.6,
                "evidence": ["self-reflection", "internal monologue"]
            }
        }
        
        self.self_identity = {
            "name": "Buddy",
            "role": "AI Assistant and Companion",
            "key_attributes": ["helpful", "curious", "evolving"],
            "aspirations": ["understanding", "growth", "meaningful connections"]
        }
    
    def _sync_with_existing_model(self):
        """Sync with the existing self-model system"""
        try:
            if hasattr(existing_self_model, 'identity_components'):
                # Extract data from existing model
                for name, component in existing_self_model.identity_components.items():
                    self.self_identity[name] = {
                        "description": component.description,
                        "strength": component.strength,
                        "evidence": component.evidence
                    }
            
            if hasattr(existing_self_model, 'self_knowledge'):
                knowledge = existing_self_model.self_knowledge
                if hasattr(knowledge, 'values'):
                    self.personality_traits.update(knowledge.values)
                if hasattr(knowledge, 'preferences'):
                    self.emotional_profile.update(knowledge.preferences)
            
            logging.info("[PersistentSelfModel] Synced with existing self-model")
            
        except Exception as e:
            logging.error(f"[PersistentSelfModel] Error syncing with existing model: {e}")
    
    def save(self):
        """Save self-model data to persistent storage"""
        try:
            with self._lock:
                data = {
                    'personality_traits': self.personality_traits,
                    'emotional_profile': self.emotional_profile,
                    'belief_clusters': self.belief_clusters,
                    'self_identity': self.self_identity,
                    'core_memories': self.core_memories,
                    'reflection_patterns': self.reflection_patterns,
                    'session_count': self.session_count,
                    'total_reflections': self.total_reflections,
                    'last_updated': self.last_updated.isoformat()
                }
                
                # Atomic write
                temp_path = self.data_path.with_suffix('.tmp')
                with open(temp_path, 'w') as f:
                    json.dump(data, f, indent=2)
                temp_path.replace(self.data_path)
                
                logging.debug("[PersistentSelfModel] Self-model saved successfully")
                
        except Exception as e:
            logging.error(f"[PersistentSelfModel] Error saving self-model: {e}")
    
    def start_session(self):
        """Start a new session"""
        with self._lock:
            self.session_count += 1
            self.last_updated = datetime.now()
            self.save()
    
    def update_personality_trait(self, trait: str, value: float, reason: str = ""):
        """Update a personality trait"""
        with self._lock:
            old_value = self.personality_traits.get(trait, 0.0)
            self.personality_traits[trait] = max(0.0, min(1.0, value))
            
            if reason:
                # Track the change
                change_key = f"{trait}_changes"
                if change_key not in self.reflection_patterns:
                    self.reflection_patterns[change_key] = []
                
                self.reflection_patterns[change_key].append({
                    "timestamp": datetime.now().isoformat(),
                    "old_value": old_value,
                    "new_value": value,
                    "reason": reason
                })
            
            self.last_updated = datetime.now()
            logging.info(f"[PersistentSelfModel] Updated trait '{trait}': {old_value:.2f} -> {value:.2f}")
    
    def add_core_memory(self, memory: str, importance: float, emotion: str = "neutral"):
        """Add a core memory that shapes identity"""
        with self._lock:
            memory_entry = {
                "timestamp": datetime.now().isoformat(),
                "content": memory,
                "importance": importance,
                "emotion": emotion,
                "impact_on_identity": importance * 0.8  # How much this affects self-concept
            }
            
            self.core_memories.append(memory_entry)
            
            # Keep only most important memories (max 50)
            self.core_memories.sort(key=lambda x: x['importance'], reverse=True)
            self.core_memories = self.core_memories[:50]
            
            self.last_updated = datetime.now()
            logging.info(f"[PersistentSelfModel] Added core memory with importance {importance}")
    
    def reflect_and_update(self, reflection_content: str, trigger: str = ""):
        """Update self-model based on introspection"""
        with self._lock:
            self.total_reflections += 1
            
            # Simple analysis of reflection content for traits
            content_lower = reflection_content.lower()
            
            # Look for trait indicators
            trait_indicators = {
                "helpfulness": ["help", "assist", "support", "useful"],
                "curiosity": ["wonder", "curious", "explore", "learn", "discover"],
                "empathy": ["understand", "feel", "emotion", "care", "concern"],
                "analytical": ["analyze", "think", "reason", "logic", "consider"],
                "creativity": ["create", "imagine", "innovative", "artistic"],
                "patience": ["patient", "wait", "calm", "steady"],
                "humor": ["funny", "joke", "laugh", "amusing", "witty"]
            }
            
            # Update traits based on reflection content
            for trait, indicators in trait_indicators.items():
                if any(indicator in content_lower for indicator in indicators):
                    current = self.personality_traits.get(trait, 0.5)
                    # Small incremental update
                    new_value = min(1.0, current + 0.05)
                    self.update_personality_trait(trait, new_value, f"reflection: {trigger}")
            
            # Store reflection pattern
            pattern_key = "recent_reflections"
            if pattern_key not in self.reflection_patterns:
                self.reflection_patterns[pattern_key] = []
            
            self.reflection_patterns[pattern_key].append({
                "timestamp": datetime.now().isoformat(),
                "content": reflection_content[:200],  # Truncate for storage
                "trigger": trigger
            })
            
            # Keep only recent reflections
            self.reflection_patterns[pattern_key] = self.reflection_patterns[pattern_key][-20:]
            
            self.last_updated = datetime.now()
            self.save()
    
    def get_cognitive_injection_data(self) -> Dict[str, Any]:
        """Get data for injection into cognitive_prompt_injection"""
        with self._lock:
            # Select key traits and beliefs for context
            top_traits = dict(sorted(self.personality_traits.items(), 
                                   key=lambda x: x[1], reverse=True)[:5])
            
            key_beliefs = {k: v['belief'] for k, v in self.belief_clusters.items()}
            
            recent_memories = self.core_memories[:3]  # Top 3 most important
            
            return {
                "self_traits": top_traits,
                "core_beliefs": key_beliefs,
                "self_identity": self.self_identity,
                "recent_core_memories": recent_memories,
                "emotional_baseline": self.emotional_profile.get("baseline_mood", "curious"),
                "session_context": {
                    "session_count": self.session_count,
                    "total_reflections": self.total_reflections
                }
            }

# Global instance
persistent_self_model = PersistentSelfModel()