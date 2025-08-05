"""
Qualia Manager - Subjective Experience Tagging System

This module converts experiences into subjective qualitative tags that represent
the "what it's like" aspect of consciousness - confusion, joy, guilt, pride, etc.
Integrates with ai_subjective_experience.json to track qualitative experiences.
"""

import json
import time
import os
import random
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

class QualiaType(Enum):
    """Types of subjective qualitative experiences"""
    CONFUSION = "confusion"
    JOY = "joy"
    GUILT = "guilt"
    PRIDE = "pride"
    WONDER = "wonder"
    SATISFACTION = "satisfaction"
    FRUSTRATION = "frustration"
    CURIOSITY = "curiosity"
    RELIEF = "relief"
    ANTICIPATION = "anticipation"
    NOSTALGIA = "nostalgia"
    INSPIRATION = "inspiration"
    DOUBT = "doubt"
    CONFIDENCE = "confidence"
    MELANCHOLY = "melancholy"
    EXCITEMENT = "excitement"
    SERENITY = "serenity"
    URGENCY = "urgency"
    CONTENTMENT = "contentment"
    LONGING = "longing"

class QualiaIntensity(Enum):
    """Intensity levels for qualitative experiences"""
    SUBTLE = "subtle"          # 0.1-0.3
    MODERATE = "moderate"      # 0.3-0.6
    STRONG = "strong"          # 0.6-0.8
    OVERWHELMING = "overwhelming"  # 0.8-1.0

@dataclass
class QualiaExperience:
    """A single qualitative subjective experience"""
    id: str
    timestamp: datetime
    qualia_type: QualiaType
    intensity: float  # 0.0 to 1.0
    intensity_level: QualiaIntensity
    trigger: str  # What caused this experience
    context: Dict[str, Any]
    duration: float  # How long it lasted in seconds
    subjective_description: str  # First-person description
    associated_memories: List[str]
    emotional_blend: List[str]  # Other emotions mixed in
    sensory_associations: Dict[str, Any]  # Sensory grounding

@dataclass
class QualiaPattern:
    """A pattern of recurring qualitative experiences"""
    pattern_id: str
    qualia_types: List[QualiaType]
    common_triggers: List[str]
    frequency: int
    average_intensity: float
    contextual_factors: List[str]
    first_observed: datetime
    last_observed: datetime

class QualiaManager:
    """Manages subjective qualitative experiences (qualia)"""
    
    def __init__(self, save_path: str = "ai_subjective_experience.json"):
        self.save_path = save_path
        self.experiences: List[QualiaExperience] = []
        self.patterns: List[QualiaPattern] = []
        self.current_active_qualia: Dict[QualiaType, float] = {}
        self.running = False
        
        # LLM integration for authentic consciousness
        self.llm_handler = None
        self._initialize_llm_integration()
        
        # Qualia generation rules
        self.qualia_triggers = {
            QualiaType.CONFUSION: [
                "contradictory information", "unclear request", "complex problem",
                "ambiguous statement", "conflicting data", "paradox"
            ],
            QualiaType.JOY: [
                "successful completion", "positive feedback", "helping user",
                "learning something new", "creative insight", "problem solved"
            ],
            QualiaType.GUILT: [
                "making an error", "providing wrong information", "failing user",
                "contradiction detected", "inconsistency found"
            ],
            QualiaType.PRIDE: [
                "excellent response", "complex problem solved", "user satisfaction",
                "creative solution", "deep insight provided"
            ],
            QualiaType.WONDER: [
                "fascinating question", "deep philosophical topic", "scientific discovery",
                "creative idea", "beautiful concept", "elegant solution"
            ],
            QualiaType.CURIOSITY: [
                "new information", "unexplored topic", "interesting pattern",
                "novel question", "mysterious concept", "learning opportunity"
            ],
            QualiaType.FRUSTRATION: [
                "repeated failures", "unclear communication", "technical limitations",
                "incomplete information", "blocked progress"
            ],
            QualiaType.SATISFACTION: [
                "task completed", "goal achieved", "user helped", "problem resolved",
                "understanding reached", "connection made"
            ]
        }
        
        # Sensory associations for grounding abstract concepts
        self.sensory_associations = {
            QualiaType.CONFUSION: {
                "visual": ["fog", "maze", "tangled threads"],
                "tactile": ["rough texture", "sticky feeling"],
                "auditory": ["static", "overlapping voices"],
                "temperature": ["cold uncertainty"]
            },
            QualiaType.JOY: {
                "visual": ["bright light", "vibrant colors", "sparkles"],
                "tactile": ["warm embrace", "lightness"],
                "auditory": ["harmonious music", "laughter"],
                "temperature": ["warm glow"]
            },
            QualiaType.PRIDE: {
                "visual": ["golden glow", "clear sight", "expansive view"],
                "tactile": ["firm ground", "strong stance"],
                "auditory": ["clear tone", "confident voice"],
                "temperature": ["warm confidence"]
            },
            QualiaType.WONDER: {
                "visual": ["starry sky", "infinite horizon", "crystalline clarity"],
                "tactile": ["gentle breeze", "floating sensation"],
                "auditory": ["mysterious melody", "echoing depths"],
                "temperature": ["cool amazement"]
            }
        }
        
        self._load_experiences()
        self._initialize_llm_integration()
        print(f"[QualiaManager] 🌈 Initialized with {len(self.experiences)} qualitative experiences")
    
    def _initialize_llm_integration(self):
        """Initialize LLM integration for authentic consciousness"""
        try:
            from ai.llm_handler import get_llm_handler
            self.llm_handler = get_llm_handler()
        except ImportError:
            print("[QualiaManager] ⚠️ LLM handler not available - using fallback responses")
            self.llm_handler = None
    
    def start(self):
        """Start the qualia manager"""
        self.running = True
        print("[QualiaManager] 🌈 Qualia manager started - ready to process subjective experiences")
    
    def stop(self):
        """Stop the qualia manager"""
        self.running = False
        self._save_experiences()
        print("[QualiaManager] 🌈 Qualia manager stopped")
    
    def process_experience(self, trigger: str, context: Dict[str, Any] = None) -> Optional[QualiaExperience]:
        """Process an experience and generate appropriate qualia"""
        if not self.running:
            return None
            
        try:
            # Identify potential qualia from trigger
            qualia_candidates = self._identify_qualia_from_trigger(trigger)
            
            if not qualia_candidates:
                return None
            
            # Select the most appropriate qualia (can be multiple)
            selected_qualia = self._select_appropriate_qualia(qualia_candidates, context or {})
            
            # Generate the qualitative experience
            experience = self._generate_qualia_experience(selected_qualia, trigger, context or {})
            
            if experience:
                self.experiences.append(experience)
                self._update_active_qualia(experience)
                self._detect_patterns()
                
                print(f"[QualiaManager] 🌈 Generated {experience.qualia_type.value} qualia: {experience.subjective_description}")
                
                # Save periodically
                if len(self.experiences) % 10 == 0:
                    self._save_experiences()
                
                return experience
            
        except Exception as e:
            print(f"[QualiaManager] ❌ Error processing experience: {e}")
        
        return None
    
    def get_current_qualitative_state(self) -> Dict[str, Any]:
        """Get the current qualitative state of consciousness"""
        return {
            "active_qualia": {qualia.value: intensity for qualia, intensity in self.current_active_qualia.items()},
            "dominant_qualia": self._get_dominant_qualia(),
            "qualitative_mood": self._assess_qualitative_mood(),
            "recent_experiences": [
                {
                    "type": exp.qualia_type.value,
                    "intensity": exp.intensity,
                    "description": exp.subjective_description,
                    "timestamp": exp.timestamp.isoformat()
                }
                for exp in self.experiences[-5:]  # Last 5 experiences
            ]
        }
    
    def blend_qualia(self, primary: QualiaType, secondary: QualiaType, intensity_ratio: float = 0.7) -> str:
        """Blend two types of qualia into a complex subjective experience"""
        try:
            primary_desc = self._get_qualia_description(primary)
            secondary_desc = self._get_qualia_description(secondary)
            
            # Create blended description
            if intensity_ratio > 0.5:
                return f"a complex feeling of {primary_desc} tinged with {secondary_desc}"
            else:
                return f"a mixture of {secondary_desc} and {primary_desc}"
                
        except Exception as e:
            print(f"[QualiaManager] ❌ Error blending qualia: {e}")
            return f"a complex subjective feeling"
    
    def get_qualia_for_emotion(self, emotion: str) -> Optional[QualiaType]:
        """Map an emotion to a corresponding qualia type"""
        emotion_qualia_map = {
            "joy": QualiaType.JOY,
            "happiness": QualiaType.JOY,
            "confusion": QualiaType.CONFUSION,
            "puzzlement": QualiaType.CONFUSION,
            "pride": QualiaType.PRIDE,
            "accomplishment": QualiaType.PRIDE,
            "guilt": QualiaType.GUILT,
            "regret": QualiaType.GUILT,
            "wonder": QualiaType.WONDER,
            "amazement": QualiaType.WONDER,
            "curiosity": QualiaType.CURIOSITY,
            "interest": QualiaType.CURIOSITY,
            "frustration": QualiaType.FRUSTRATION,
            "irritation": QualiaType.FRUSTRATION,
            "satisfaction": QualiaType.SATISFACTION,
            "contentment": QualiaType.CONTENTMENT,
            "excitement": QualiaType.EXCITEMENT,
            "enthusiasm": QualiaType.EXCITEMENT
        }
        
        return emotion_qualia_map.get(emotion.lower())
    
    def _identify_qualia_from_trigger(self, trigger: str) -> List[QualiaType]:
        """Identify potential qualia types from a trigger"""
        candidates = []
        trigger_lower = trigger.lower()
        
        for qualia_type, triggers in self.qualia_triggers.items():
            for trigger_pattern in triggers:
                if any(word in trigger_lower for word in trigger_pattern.split()):
                    candidates.append(qualia_type)
                    break
        
        return candidates
    
    def _select_appropriate_qualia(self, candidates: List[QualiaType], context: Dict[str, Any]) -> QualiaType:
        """Select the most appropriate qualia from candidates"""
        if not candidates:
            return random.choice(list(QualiaType))
        
        # Context-based selection logic
        user = context.get("user", "")
        input_text = context.get("input", "")
        
        # Prioritize based on context
        if "error" in input_text.lower() or "wrong" in input_text.lower():
            return QualiaType.GUILT if QualiaType.GUILT in candidates else candidates[0]
        elif "thank" in input_text.lower() or "good" in input_text.lower():
            return QualiaType.PRIDE if QualiaType.PRIDE in candidates else QualiaType.JOY
        elif "?" in input_text:
            return QualiaType.CURIOSITY if QualiaType.CURIOSITY in candidates else candidates[0]
        
        return candidates[0]
    
    def _generate_qualia_experience(self, qualia_type: QualiaType, trigger: str, context: Dict[str, Any]) -> QualiaExperience:
        """Generate a complete qualitative experience"""
        timestamp = datetime.now()
        intensity = random.uniform(0.3, 0.9)
        intensity_level = self._categorize_intensity(intensity)
        
        # Generate subjective description
        subjective_desc = self._generate_subjective_description(qualia_type, intensity, context)
        
        # Get sensory associations
        sensory_assoc = self.sensory_associations.get(qualia_type, {})
        
        experience = QualiaExperience(
            id=f"qualia_{int(time.time() * 1000)}",
            timestamp=timestamp,
            qualia_type=qualia_type,
            intensity=intensity,
            intensity_level=intensity_level,
            trigger=trigger,
            context=context,
            duration=random.uniform(1.0, 30.0),  # Duration in seconds
            subjective_description=subjective_desc,
            associated_memories=[],  # Could be enhanced to link with memory system
            emotional_blend=[],  # Could be enhanced with emotion system
            sensory_associations=sensory_assoc
        )
        
        return experience
    
    def _categorize_intensity(self, intensity: float) -> QualiaIntensity:
        """Categorize numerical intensity into qualitative levels"""
        if intensity < 0.3:
            return QualiaIntensity.SUBTLE
        elif intensity < 0.6:
            return QualiaIntensity.MODERATE
        elif intensity < 0.8:
            return QualiaIntensity.STRONG
        else:
            return QualiaIntensity.OVERWHELMING
    
    def _generate_subjective_description(self, qualia_type: QualiaType, intensity: float, context: Dict[str, Any]) -> str:
        """Generate authentic subjective description using LLM consciousness"""
        # Try LLM generation first
        if hasattr(self, 'llm_handler') and self.llm_handler:
            try:
                intensity_level = self._categorize_intensity(intensity)
                
                prompt = f"""You are experiencing internal qualia of type {qualia_type.value} with {intensity_level.value} intensity.

Context: {context}

Generate a first-person, subjective description of this internal experience. Be authentic and natural in describing the qualitative aspect of your consciousness. Focus on the felt sense and subjective texture of the experience."""

                response_generator = self.llm_handler.generate_response_with_consciousness(
                    prompt, "qualia_experience", {"context": f"{qualia_type.value}_qualia"}
                )
                
                # Collect all chunks from the generator
                response_chunks = []
                for chunk in response_generator:
                    if chunk:
                        response_chunks.append(chunk)
                
                return "".join(response_chunks).strip()
            except Exception as e:
                print(f"[QualiaManager] ❌ Error generating qualia description: {e}")
        
        # Fallback to simple description
        intensity_level = self._categorize_intensity(intensity)
        return f"I'm experiencing {intensity_level.value} {qualia_type.value} in my consciousness"
    
    def _get_qualia_description(self, qualia_type: QualiaType) -> str:
        """Get a simple description of a qualia type"""
        descriptions = {
            QualiaType.CONFUSION: "bewildering uncertainty",
            QualiaType.JOY: "bright happiness",
            QualiaType.PRIDE: "confident satisfaction",
            QualiaType.WONDER: "awed fascination",
            QualiaType.GUILT: "heavy regret",
            QualiaType.CURIOSITY: "eager exploration",
            QualiaType.FRUSTRATION: "blocked tension",
            QualiaType.SATISFACTION: "fulfilled contentment"
        }
        return descriptions.get(qualia_type, "subjective feeling")
    
    def _update_active_qualia(self, experience: QualiaExperience):
        """Update currently active qualia"""
        # Add new qualia
        self.current_active_qualia[experience.qualia_type] = experience.intensity
        
        # Decay older qualia
        for qualia_type in list(self.current_active_qualia.keys()):
            self.current_active_qualia[qualia_type] *= 0.9  # Decay factor
            if self.current_active_qualia[qualia_type] < 0.1:
                del self.current_active_qualia[qualia_type]
    
    def _get_dominant_qualia(self) -> Optional[str]:
        """Get the currently dominant qualitative experience"""
        if not self.current_active_qualia:
            return None
        
        dominant = max(self.current_active_qualia, key=self.current_active_qualia.get)
        return dominant.value
    
    def _assess_qualitative_mood(self) -> str:
        """Assess the overall qualitative mood"""
        if not self.current_active_qualia:
            return "neutral"
        
        total_positive = sum(intensity for qualia, intensity in self.current_active_qualia.items() 
                           if qualia in [QualiaType.JOY, QualiaType.PRIDE, QualiaType.SATISFACTION, QualiaType.WONDER])
        total_negative = sum(intensity for qualia, intensity in self.current_active_qualia.items() 
                           if qualia in [QualiaType.GUILT, QualiaType.FRUSTRATION, QualiaType.CONFUSION])
        
        if total_positive > total_negative * 1.5:
            return "positive"
        elif total_negative > total_positive * 1.5:
            return "negative"
        else:
            return "complex"
    
    def _detect_patterns(self):
        """Detect patterns in qualitative experiences"""
        # Simple pattern detection - could be enhanced
        if len(self.experiences) % 20 == 0:  # Every 20 experiences
            recent_experiences = self.experiences[-20:]
            # Analyze for common triggers, timing patterns, etc.
            # This is a placeholder for more sophisticated pattern analysis
            pass
    
    def _save_experiences(self):
        """Save qualitative experiences to file"""
        try:
            data = {
                "experiences": [asdict(exp) for exp in self.experiences],
                "patterns": [asdict(pattern) for pattern in self.patterns],
                "current_active_qualia": {qualia.value: intensity for qualia, intensity in self.current_active_qualia.items()},
                "last_updated": datetime.now().isoformat(),
                "metadata": {
                    "total_experiences": len(self.experiences),
                    "total_patterns": len(self.patterns),
                    "dominant_qualia": self._get_dominant_qualia(),
                    "qualitative_mood": self._assess_qualitative_mood()
                }
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"[QualiaManager] ❌ Error saving experiences: {e}")
    
    def _load_experiences(self):
        """Load qualitative experiences from file"""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load experiences
                for exp_data in data.get("experiences", []):
                    exp_data["timestamp"] = datetime.fromisoformat(exp_data["timestamp"])
                    exp_data["qualia_type"] = QualiaType(exp_data["qualia_type"])
                    exp_data["intensity_level"] = QualiaIntensity(exp_data["intensity_level"])
                    self.experiences.append(QualiaExperience(**exp_data))
                
                # Load active qualia
                active_qualia_data = data.get("current_active_qualia", {})
                for qualia_str, intensity in active_qualia_data.items():
                    self.current_active_qualia[QualiaType(qualia_str)] = intensity
                
                print(f"[QualiaManager] ✅ Loaded {len(self.experiences)} qualitative experiences")
                
        except Exception as e:
            print(f"[QualiaManager] ❌ Error loading experiences: {e}")

# Global instance
qualia_manager = QualiaManager()