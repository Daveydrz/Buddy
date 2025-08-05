"""
Belief-Qualia Linking System - Attach qualia IDs to beliefs for emotional-cognitive integration
Provides deep emotional context to beliefs and experiences
"""

import json
import uuid
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

class QualiaType(Enum):
    """Types of qualia experiences"""
    EMOTIONAL = "emotional"
    COGNITIVE = "cognitive"
    SENSORY = "sensory"
    MOTIVATIONAL = "motivational"
    SOCIAL = "social"
    TEMPORAL = "temporal"
    AESTHETIC = "aesthetic"
    MORAL = "moral"

class QualiaIntensity(Enum):
    """Intensity levels of qualia experiences"""
    SUBTLE = "subtle"
    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"
    INTENSE = "intense"

@dataclass
class QualiaMarker:
    """Represents a qualia experience marker"""
    qualia_id: str
    qualia_type: QualiaType
    intensity: QualiaIntensity
    emotional_valence: float  # -1.0 to 1.0
    cognitive_clarity: float  # 0.0 to 1.0
    temporal_duration: float  # seconds
    description: str
    triggers: List[str]
    timestamp: str
    frequency_count: int = 1

@dataclass
class BeliefQualiaLink:
    """Links beliefs to qualia experiences"""
    belief_id: str
    belief_content: str
    qualia_id: str
    link_strength: float  # 0.0 to 1.0
    link_type: str  # "causal", "associative", "contextual", "experiential"
    formation_context: str
    timestamp: str
    activation_count: int = 1

class BeliefQualiaLinker:
    """System to link beliefs with qualia experiences"""
    
    def __init__(self, save_path: str = "belief_qualia_links.json"):
        self.save_path = save_path
        self.qualia_markers: Dict[str, QualiaMarker] = {}
        self.belief_qualia_links: Dict[str, BeliefQualiaLink] = {}
        self.active_qualia: Dict[str, float] = {}  # qualia_id -> activation_time
        self.load_links()
    
    def load_links(self):
        """Load existing links from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                
                # Load qualia markers
                for marker_data in data.get('qualia_markers', []):
                    try:
                        qualia_type = QualiaType(marker_data['qualia_type'])
                    except (ValueError, KeyError):
                        # Handle legacy format or invalid enum
                        qualia_type = QualiaType.EMOTIONAL
                    
                    try:
                        intensity = QualiaIntensity(marker_data['intensity'])
                    except (ValueError, KeyError):
                        # Handle legacy format or invalid enum
                        intensity = QualiaIntensity.MODERATE
                    
                    marker = QualiaMarker(
                        qualia_id=marker_data['qualia_id'],
                        qualia_type=qualia_type,
                        intensity=intensity,
                        emotional_valence=marker_data['emotional_valence'],
                        cognitive_clarity=marker_data['cognitive_clarity'],
                        temporal_duration=marker_data['temporal_duration'],
                        description=marker_data['description'],
                        triggers=marker_data['triggers'],
                        timestamp=marker_data['timestamp'],
                        frequency_count=marker_data.get('frequency_count', 1)
                    )
                    self.qualia_markers[marker.qualia_id] = marker
                
                # Load belief-qualia links
                for link_data in data.get('belief_qualia_links', []):
                    link = BeliefQualiaLink(
                        belief_id=link_data['belief_id'],
                        belief_content=link_data['belief_content'],
                        qualia_id=link_data['qualia_id'],
                        link_strength=link_data['link_strength'],
                        link_type=link_data['link_type'],
                        formation_context=link_data['formation_context'],
                        timestamp=link_data['timestamp'],
                        activation_count=link_data.get('activation_count', 1)
                    )
                    self.belief_qualia_links[link.belief_id] = link
                
                print(f"[BeliefQualiaLinker] 📄 Loaded {len(self.qualia_markers)} qualia markers and {len(self.belief_qualia_links)} links")
        except FileNotFoundError:
            print(f"[BeliefQualiaLinker] 📄 No existing links found, starting fresh")
        except Exception as e:
            print(f"[BeliefQualiaLinker] ❌ Error loading links: {e}")
    
    def save_links(self):
        """Save links to file"""
        try:
            data = {
                'qualia_markers': [asdict(marker) for marker in self.qualia_markers.values()],
                'belief_qualia_links': [asdict(link) for link in self.belief_qualia_links.values()],
                'last_updated': datetime.now().isoformat(),
                'total_markers': len(self.qualia_markers),
                'total_links': len(self.belief_qualia_links)
            }
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"[BeliefQualiaLinker] ❌ Error saving links: {e}")
    
    def create_qualia_marker(self, 
                           qualia_type: QualiaType, 
                           intensity: QualiaIntensity,
                           emotional_valence: float,
                           cognitive_clarity: float,
                           description: str,
                           triggers: List[str],
                           temporal_duration: float = 5.0) -> str:
        """Create a new qualia marker"""
        qualia_id = f"qualia_{uuid.uuid4().hex[:8]}"
        
        marker = QualiaMarker(
            qualia_id=qualia_id,
            qualia_type=qualia_type,
            intensity=intensity,
            emotional_valence=emotional_valence,
            cognitive_clarity=cognitive_clarity,
            temporal_duration=temporal_duration,
            description=description,
            triggers=triggers,
            timestamp=datetime.now().isoformat()
        )
        
        self.qualia_markers[qualia_id] = marker
        self.active_qualia[qualia_id] = time.time()
        
        print(f"[BeliefQualiaLinker] 🌟 Created qualia marker: {qualia_id} ({description})")
        return qualia_id
    
    def link_belief_to_qualia(self, 
                             belief_id: str, 
                             belief_content: str,
                             qualia_id: str,
                             link_strength: float,
                             link_type: str,
                             formation_context: str):
        """Link a belief to a qualia experience"""
        if qualia_id not in self.qualia_markers:
            print(f"[BeliefQualiaLinker] ⚠️ Qualia ID {qualia_id} not found")
            return
        
        link = BeliefQualiaLink(
            belief_id=belief_id,
            belief_content=belief_content,
            qualia_id=qualia_id,
            link_strength=link_strength,
            link_type=link_type,
            formation_context=formation_context,
            timestamp=datetime.now().isoformat()
        )
        
        self.belief_qualia_links[belief_id] = link
        print(f"[BeliefQualiaLinker] 🔗 Linked belief {belief_id} to qualia {qualia_id}")
    
    def process_belief_with_qualia(self, belief_content: str, user_id: str) -> Tuple[str, List[str]]:
        """Process a belief and attach appropriate qualia"""
        qualia_ids = []
        
        # Analyze belief content for emotional triggers
        emotional_triggers = self._detect_emotional_triggers(belief_content)
        cognitive_triggers = self._detect_cognitive_triggers(belief_content)
        
        # Create qualia markers for emotional content
        for trigger in emotional_triggers:
            qualia_id = self.create_qualia_marker(
                qualia_type=QualiaType.EMOTIONAL,
                intensity=self._determine_intensity(trigger),
                emotional_valence=self._determine_valence(trigger),
                cognitive_clarity=0.8,
                description=f"Emotional response to: {trigger}",
                triggers=[trigger],
                temporal_duration=10.0
            )
            qualia_ids.append(qualia_id)
        
        # Create qualia markers for cognitive content
        for trigger in cognitive_triggers:
            qualia_id = self.create_qualia_marker(
                qualia_type=QualiaType.COGNITIVE,
                intensity=QualiaIntensity.MODERATE,
                emotional_valence=0.1,
                cognitive_clarity=0.9,
                description=f"Cognitive processing of: {trigger}",
                triggers=[trigger],
                temporal_duration=15.0
            )
            qualia_ids.append(qualia_id)
        
        # Generate belief ID
        belief_id = f"belief_{uuid.uuid4().hex[:8]}"
        
        # Link belief to qualia
        for qualia_id in qualia_ids:
            self.link_belief_to_qualia(
                belief_id=belief_id,
                belief_content=belief_content,
                qualia_id=qualia_id,
                link_strength=0.8,
                link_type="experiential",
                formation_context=f"Processing user input from {user_id}"
            )
        
        self.save_links()
        return belief_id, qualia_ids
    
    def _detect_emotional_triggers(self, text: str) -> List[str]:
        """Detect emotional triggers in text"""
        emotional_keywords = {
            'joy': ['happy', 'joy', 'excited', 'thrilled', 'delighted', 'cheerful'],
            'sadness': ['sad', 'depressed', 'disappointed', 'grief', 'melancholy'],
            'anger': ['angry', 'frustrated', 'annoyed', 'irritated', 'furious'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'nervous'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished'],
            'disgust': ['disgusted', 'revolted', 'repulsed', 'sick'],
            'love': ['love', 'adore', 'cherish', 'affection', 'care'],
            'curiosity': ['curious', 'wonder', 'interested', 'fascinated'],
            'confusion': ['confused', 'puzzled', 'uncertain', 'unclear']
        }
        
        triggers = []
        text_lower = text.lower()
        
        for emotion, keywords in emotional_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    triggers.append(emotion)
                    break
        
        return triggers
    
    def _detect_cognitive_triggers(self, text: str) -> List[str]:
        """Detect cognitive triggers in text"""
        cognitive_keywords = {
            'learning': ['learn', 'study', 'understand', 'comprehend', 'grasp'],
            'memory': ['remember', 'recall', 'forget', 'memorize', 'reminisce'],
            'reasoning': ['think', 'reason', 'analyze', 'consider', 'conclude'],
            'problem_solving': ['solve', 'figure', 'work out', 'resolve', 'fix'],
            'decision_making': ['decide', 'choose', 'select', 'pick', 'determine'],
            'creativity': ['create', 'imagine', 'invent', 'design', 'innovate'],
            'attention': ['focus', 'concentrate', 'pay attention', 'notice', 'observe'],
            'planning': ['plan', 'organize', 'schedule', 'arrange', 'prepare']
        }
        
        triggers = []
        text_lower = text.lower()
        
        for process, keywords in cognitive_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    triggers.append(process)
                    break
        
        return triggers
    
    def _determine_intensity(self, trigger: str) -> QualiaIntensity:
        """Determine intensity based on trigger"""
        high_intensity = ['thrilled', 'furious', 'terrified', 'ecstatic', 'devastated']
        medium_intensity = ['happy', 'angry', 'scared', 'excited', 'sad']
        low_intensity = ['content', 'annoyed', 'worried', 'pleased', 'disappointed']
        
        if trigger in high_intensity:
            return QualiaIntensity.INTENSE
        elif trigger in medium_intensity:
            return QualiaIntensity.STRONG
        elif trigger in low_intensity:
            return QualiaIntensity.MILD
        else:
            return QualiaIntensity.MODERATE
    
    def _determine_valence(self, trigger: str) -> float:
        """Determine emotional valence (-1.0 to 1.0)"""
        positive_emotions = ['happy', 'joy', 'excited', 'thrilled', 'delighted', 'love', 'curious']
        negative_emotions = ['sad', 'angry', 'scared', 'disgusted', 'disappointed', 'frustrated']
        
        if trigger in positive_emotions:
            return 0.8
        elif trigger in negative_emotions:
            return -0.8
        else:
            return 0.0
    
    def get_belief_qualia(self, belief_id: str) -> Optional[Tuple[BeliefQualiaLink, QualiaMarker]]:
        """Get qualia information for a belief"""
        if belief_id not in self.belief_qualia_links:
            return None
        
        link = self.belief_qualia_links[belief_id]
        marker = self.qualia_markers.get(link.qualia_id)
        
        if marker:
            return link, marker
        return None
    
    def get_active_qualia(self, max_age_seconds: float = 300.0) -> List[QualiaMarker]:
        """Get currently active qualia markers"""
        current_time = time.time()
        active_markers = []
        
        for qualia_id, activation_time in self.active_qualia.items():
            if current_time - activation_time <= max_age_seconds:
                if qualia_id in self.qualia_markers:
                    active_markers.append(self.qualia_markers[qualia_id])
        
        return active_markers
    
    def get_dominant_qualia(self) -> Optional[QualiaMarker]:
        """Get the most dominant currently active qualia"""
        active_qualia = self.get_active_qualia()
        if not active_qualia:
            return None
        
        # Sort by intensity and activation count
        sorted_qualia = sorted(active_qualia, 
                             key=lambda q: (q.intensity.value, q.frequency_count), 
                             reverse=True)
        
        return sorted_qualia[0]
    
    def update_qualia_activation(self, qualia_id: str):
        """Update activation time for a qualia marker"""
        if qualia_id in self.qualia_markers:
            self.active_qualia[qualia_id] = time.time()
            self.qualia_markers[qualia_id].frequency_count += 1
    
    def get_qualia_summary(self) -> Dict[str, Any]:
        """Get summary of current qualia state"""
        active_qualia = self.get_active_qualia()
        dominant_qualia = self.get_dominant_qualia()
        
        return {
            'total_qualia_markers': len(self.qualia_markers),
            'total_belief_links': len(self.belief_qualia_links),
            'active_qualia_count': len(active_qualia),
            'dominant_qualia': {
                'id': dominant_qualia.qualia_id if dominant_qualia else None,
                'type': dominant_qualia.qualia_type.value if dominant_qualia else None,
                'intensity': dominant_qualia.intensity.value if dominant_qualia else None,
                'description': dominant_qualia.description if dominant_qualia else None
            },
            'active_types': [q.qualia_type.value for q in active_qualia],
            'average_valence': sum(q.emotional_valence for q in active_qualia) / len(active_qualia) if active_qualia else 0.0,
            'average_clarity': sum(q.cognitive_clarity for q in active_qualia) / len(active_qualia) if active_qualia else 0.0
        }
    
    def generate_qualia_tokens(self, max_tokens: int = 5) -> List[str]:
        """Generate qualia tokens for LLM prompts"""
        active_qualia = self.get_active_qualia()
        tokens = []
        
        for i, qualia in enumerate(active_qualia[:max_tokens]):
            token = f"<qualia{i+1}:{qualia.qualia_type.value}:{qualia.intensity.value}:{qualia.emotional_valence:.2f}>"
            tokens.append(token)
        
        return tokens
    
    def prune_inactive_qualia(self, max_age_hours: float = 24.0):
        """Remove old, inactive qualia markers"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        inactive_qualia = []
        for qualia_id, activation_time in self.active_qualia.items():
            if current_time - activation_time > max_age_seconds:
                inactive_qualia.append(qualia_id)
        
        for qualia_id in inactive_qualia:
            del self.active_qualia[qualia_id]
        
        print(f"[BeliefQualiaLinker] 🧹 Pruned {len(inactive_qualia)} inactive qualia")
        self.save_links()

# Global instance
belief_qualia_linker = BeliefQualiaLinker()

def link_belief_to_qualia_experience(belief_content: str, user_id: str) -> Tuple[str, List[str]]:
    """Link a belief to qualia experiences - main API function"""
    return belief_qualia_linker.process_belief_with_qualia(belief_content, user_id)

def get_current_qualia_state() -> Dict[str, Any]:
    """Get current qualia state summary"""
    return belief_qualia_linker.get_qualia_summary()

def get_qualia_tokens_for_prompt(max_tokens: int = 5) -> List[str]:
    """Get qualia tokens for LLM prompts"""
    return belief_qualia_linker.generate_qualia_tokens(max_tokens)

def activate_qualia_by_id(qualia_id: str):
    """Activate a specific qualia marker"""
    belief_qualia_linker.update_qualia_activation(qualia_id)

def get_belief_emotional_context(belief_id: str) -> Optional[Dict[str, Any]]:
    """Get emotional context for a belief"""
    result = belief_qualia_linker.get_belief_qualia(belief_id)
    if result:
        link, marker = result
        return {
            'qualia_id': marker.qualia_id,
            'emotional_valence': marker.emotional_valence,
            'cognitive_clarity': marker.cognitive_clarity,
            'intensity': marker.intensity.value,
            'description': marker.description,
            'link_strength': link.link_strength
        }
    return None