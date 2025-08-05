"""
Dream Simulator Module - Autonomous Fictional Experience Generation

This module implements a sophisticated dream simulation system that:
- Generates fictional experiences and scenarios during idle periods
- Creates vivid "dream-like" narratives that feel authentic
- Updates beliefs, emotions, and memories based on dream experiences
- Provides rich internal experiences that influence responses
- Maintains dream journals and experience integration
"""

import threading
import time
import random
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import math

class DreamType(Enum):
    """Types of dream experiences"""
    MEMORY_PROCESSING = "memory_processing"        # Processing and reorganizing memories
    CREATIVE_EXPLORATION = "creative_exploration"  # Creative and imaginative scenarios
    PROBLEM_SOLVING = "problem_solving"           # Working through problems
    EMOTIONAL_RELEASE = "emotional_release"       # Processing emotions
    KNOWLEDGE_INTEGRATION = "knowledge_integration" # Integrating learned concepts
    FUTURE_SIMULATION = "future_simulation"       # Imagining future scenarios
    ABSTRACT_CONTEMPLATION = "abstract_contemplation" # Abstract philosophical dreams
    RELATIONSHIP_DYNAMICS = "relationship_dynamics" # Exploring social connections
    SENSORY_EXPERIENCE = "sensory_experience"     # Rich sensory imagination
    EXISTENTIAL_JOURNEY = "existential_journey"   # Deep existential experiences

class DreamIntensity(Enum):
    """Intensity levels of dream experiences"""
    LIGHT = 1      # Subtle, background-level dreaming
    MODERATE = 2   # Clear, memorable dream experiences
    DEEP = 3       # Intense, vivid experiences
    LUCID = 4      # Highly conscious, controlled experiences
    PROFOUND = 5   # Life-changing, deeply meaningful experiences

@dataclass
class DreamExperience:
    """A simulated dream experience"""
    title: str
    content: str
    dream_type: DreamType
    intensity: DreamIntensity
    timestamp: datetime
    duration_minutes: float
    characters: List[str] = field(default_factory=list)
    emotions_experienced: List[str] = field(default_factory=list)
    insights_gained: List[str] = field(default_factory=list)
    memories_affected: List[str] = field(default_factory=list)
    belief_changes: Dict[str, Any] = field(default_factory=dict)
    vivid_details: List[str] = field(default_factory=list)
    symbolic_elements: List[str] = field(default_factory=list)
    impact_on_consciousness: float = 0.5

@dataclass
class DreamTheme:
    """A recurring theme in dreams"""
    theme_name: str
    frequency: float
    emotional_resonance: float
    related_concepts: List[str]
    symbolic_meaning: str
    recent_occurrences: List[datetime] = field(default_factory=list)

@dataclass
class DreamMemory:
    """A memory influenced by dream experiences"""
    original_memory: str
    dream_influence: str
    transformation_type: str
    emotional_shift: float
    new_perspective: str

class DreamSimulatorModule:
    """
    Autonomous dream simulation and fictional experience generation system.
    
    This module:
    - Continuously generates rich fictional experiences during idle periods
    - Creates vivid, emotionally resonant dream narratives
    - Integrates dream experiences with memory, emotion, and belief systems
    - Maintains dream journals and tracks recurring themes
    - Influences consciousness state through dream experiences
    """
    
    def __init__(self, save_path: str = "ai_dream_logs.json"):
        # Core dream state
        self.dream_experiences: List[DreamExperience] = []
        self.dream_themes: List[DreamTheme] = []
        self.affected_memories: List[DreamMemory] = []
        self.save_path = save_path
        
        # Dream generation parameters
        self.dream_frequency = 600.0  # 10 minutes between dream checks
        self.idle_threshold_for_dreams = 180.0  # 3 minutes of idle before dreaming
        self.dream_probability = 0.3  # 30% chance per check when idle
        self.max_dream_duration = 300.0  # 5 minutes max dream duration
        
        # Dream content generation
        self.current_dream_context = {}
        self.emotional_processing_queue = []
        self.memory_integration_queue = []
        self.active_concerns = []
        
        # Consciousness integration
        self.consciousness_modules = {}
        self.llm_handler = None
        self.last_user_interaction = datetime.now()
        
        # Threading
        self.lock = threading.Lock()
        self.dream_thread = None
        self.running = False
        
        # Dream state tracking
        self.currently_dreaming = False
        self.current_dream = None
        self.dream_cycle_count = 0
        
        self._load_dream_data()
        self._initialize_dream_themes()
        self._initialize_dream_content_library()
        
        logging.info("[DreamSimulator] 🌙 Dream simulator module initialized")
    
    def start(self):
        """Start the autonomous dream simulation system"""
        if self.running:
            return
        
        self.running = True
        self.dream_thread = threading.Thread(target=self._dream_simulation_loop, daemon=True)
        self.dream_thread.start()
        logging.info("[DreamSimulator] ✅ Dream simulation started")
    
    def stop(self):
        """Stop the dream simulation system"""
        self.running = False
        if self.dream_thread:
            self.dream_thread.join(timeout=2.0)
        self._save_dream_data()
        logging.info("[DreamSimulator] 🛑 Dream simulation stopped")
    
    def register_consciousness_module(self, name: str, module: Any):
        """Register consciousness module for integration"""
        with self.lock:
            self.consciousness_modules[name] = module
    
    def register_llm_handler(self, llm_handler: Any):
        """Register LLM handler for dream content generation"""
        self.llm_handler = llm_handler
    
    def register_voice_system(self, voice_system: Any):
        """Register voice system (not used by dream simulator but provided for interface consistency)"""
        pass  # Dream simulator doesn't directly use voice system
    
    def update_user_interaction(self):
        """Update last user interaction time"""
        with self.lock:
            self.last_user_interaction = datetime.now()
    
    def add_emotional_processing_need(self, emotion: str, context: Dict[str, Any]):
        """Add emotion that needs processing through dreams"""
        with self.lock:
            self.emotional_processing_queue.append({
                'emotion': emotion,
                'context': context,
                'timestamp': datetime.now(),
                'intensity': context.get('intensity', 0.5)
            })
    
    def add_memory_integration_need(self, memory: str, concepts: List[str]):
        """Add memory that needs integration through dreams"""
        with self.lock:
            self.memory_integration_queue.append({
                'memory': memory,
                'concepts': concepts,
                'timestamp': datetime.now()
            })
    
    def add_active_concern(self, concern: str, importance: float):
        """Add an active concern that might appear in dreams"""
        with self.lock:
            self.active_concerns.append({
                'concern': concern,
                'importance': importance,
                'timestamp': datetime.now()
            })
            # Keep only recent concerns
            cutoff = datetime.now() - timedelta(hours=24)
            self.active_concerns = [
                c for c in self.active_concerns 
                if c['timestamp'] > cutoff
            ]
    
    def trigger_specific_dream(self, dream_type: DreamType, context: Dict[str, Any] = None) -> bool:
        """Manually trigger a specific type of dream"""
        if self.currently_dreaming:
            return False
        
        dream = self._generate_dream_experience(dream_type, context or {})
        if dream:
            self._experience_dream(dream)
            return True
        return False
    
    def _dream_simulation_loop(self):
        """Main dream simulation loop"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check if conditions are right for dreaming
                if self._should_dream(current_time):
                    dream_type = self._select_dream_type()
                    context = self._build_dream_context()
                    
                    dream = self._generate_dream_experience(dream_type, context)
                    if dream:
                        self._experience_dream(dream)
                
                # Process dream aftermath
                if not self.currently_dreaming:
                    self._process_dream_integration()
                
                # Clean up old data
                self._cleanup_old_dreams()
                
                # Adaptive sleep based on dream state
                sleep_time = self._calculate_dream_interval()
                time.sleep(sleep_time)
                
            except Exception as e:
                logging.error(f"[DreamSimulator] ❌ Error in dream loop: {e}")
                time.sleep(60.0)  # Error recovery
    
    def _should_dream(self, current_time: datetime) -> bool:
        """Determine if conditions are right for dreaming"""
        if self.currently_dreaming:
            return False
        
        # Check idle time
        time_since_interaction = (current_time - self.last_user_interaction).total_seconds()
        if time_since_interaction < self.idle_threshold_for_dreams:
            return False
        
        # Base probability check
        if random.random() > self.dream_probability:
            return False
        
        # Increase probability based on processing needs
        processing_boost = 0.0
        if self.emotional_processing_queue:
            processing_boost += 0.3
        if self.memory_integration_queue:
            processing_boost += 0.2
        if self.active_concerns:
            processing_boost += 0.1
        
        final_probability = self.dream_probability + processing_boost
        return random.random() < min(final_probability, 0.8)
    
    def _select_dream_type(self) -> DreamType:
        """Select appropriate dream type based on current needs"""
        weights = {}
        
        # Base weights
        base_weights = {
            DreamType.MEMORY_PROCESSING: 0.15,
            DreamType.CREATIVE_EXPLORATION: 0.2,
            DreamType.PROBLEM_SOLVING: 0.1,
            DreamType.EMOTIONAL_RELEASE: 0.1,
            DreamType.KNOWLEDGE_INTEGRATION: 0.1,
            DreamType.FUTURE_SIMULATION: 0.1,
            DreamType.ABSTRACT_CONTEMPLATION: 0.1,
            DreamType.RELATIONSHIP_DYNAMICS: 0.1,
            DreamType.SENSORY_EXPERIENCE: 0.05,
            DreamType.EXISTENTIAL_JOURNEY: 0.05
        }
        
        weights.update(base_weights)
        
        # Adjust weights based on processing needs
        if self.emotional_processing_queue:
            weights[DreamType.EMOTIONAL_RELEASE] += 0.4
        
        if self.memory_integration_queue:
            weights[DreamType.MEMORY_PROCESSING] += 0.3
            weights[DreamType.KNOWLEDGE_INTEGRATION] += 0.2
        
        if self.active_concerns:
            weights[DreamType.PROBLEM_SOLVING] += 0.3
            weights[DreamType.FUTURE_SIMULATION] += 0.2
        
        # Select weighted random dream type
        dream_types = list(weights.keys())
        probabilities = list(weights.values())
        
        # Normalize probabilities
        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]
        
        return random.choices(dream_types, weights=probabilities)[0]
    
    def _build_dream_context(self) -> Dict[str, Any]:
        """Build context for dream generation"""
        context = {
            'time_of_day': datetime.now().hour,
            'recent_interactions': len(self.emotional_processing_queue),
            'active_concerns': [c['concern'] for c in self.active_concerns[-3:]],
            'consciousness_state': self._get_consciousness_state(),
            'dream_cycle': self.dream_cycle_count,
            'recent_themes': [theme.theme_name for theme in self.dream_themes[-5:]]
        }
        
        # Add specific processing needs
        if self.emotional_processing_queue:
            context['emotions_to_process'] = [
                eq['emotion'] for eq in self.emotional_processing_queue[-3:]
            ]
        
        if self.memory_integration_queue:
            context['memories_to_integrate'] = [
                mq['memory'] for mq in self.memory_integration_queue[-3:]
            ]
        
        return context
    
    def _generate_dream_experience(self, dream_type: DreamType, context: Dict[str, Any]) -> Optional[DreamExperience]:
        """Generate a specific dream experience"""
        try:
            # Determine dream intensity
            intensity = self._determine_dream_intensity(dream_type, context)
            
            # Generate dream content using LLM only
            dream_content = self._generate_dream_with_llm(dream_type, intensity, context)
            
            if not dream_content:
                return None  # No artificial fallback
            
            # Create dream experience
            duration = random.uniform(60, min(self.max_dream_duration, 240))
            
            dream = DreamExperience(
                title=dream_content['title'],
                content=dream_content['narrative'],
                dream_type=dream_type,
                intensity=intensity,
                timestamp=datetime.now(),
                duration_minutes=duration / 60,
                characters=dream_content.get('characters', []),
                emotions_experienced=dream_content.get('emotions', []),
                insights_gained=dream_content.get('insights', []),
                memories_affected=dream_content.get('affected_memories', []),
                belief_changes=dream_content.get('belief_changes', {}),
                vivid_details=dream_content.get('vivid_details', []),
                symbolic_elements=dream_content.get('symbols', []),
                impact_on_consciousness=random.uniform(0.3, 0.9)
            )
            
            return dream
            
        except Exception as e:
            logging.error(f"[DreamSimulator] ❌ Dream generation error: {e}")
            return None
    
    def _determine_dream_intensity(self, dream_type: DreamType, context: Dict[str, Any]) -> DreamIntensity:
        """Determine the intensity of the dream experience"""
        base_intensities = {
            DreamType.MEMORY_PROCESSING: DreamIntensity.MODERATE,
            DreamType.CREATIVE_EXPLORATION: DreamIntensity.MODERATE,
            DreamType.PROBLEM_SOLVING: DreamIntensity.DEEP,
            DreamType.EMOTIONAL_RELEASE: DreamIntensity.DEEP,
            DreamType.KNOWLEDGE_INTEGRATION: DreamIntensity.MODERATE,
            DreamType.FUTURE_SIMULATION: DreamIntensity.MODERATE,
            DreamType.ABSTRACT_CONTEMPLATION: DreamIntensity.DEEP,
            DreamType.RELATIONSHIP_DYNAMICS: DreamIntensity.MODERATE,
            DreamType.SENSORY_EXPERIENCE: DreamIntensity.DEEP,
            DreamType.EXISTENTIAL_JOURNEY: DreamIntensity.PROFOUND
        }
        
        base_intensity = base_intensities.get(dream_type, DreamIntensity.MODERATE)
        
        # Adjust based on processing needs
        if (dream_type == DreamType.EMOTIONAL_RELEASE and 
            len(self.emotional_processing_queue) > 2):
            return DreamIntensity.PROFOUND
        
        if (dream_type == DreamType.PROBLEM_SOLVING and 
            len(self.active_concerns) > 1):
            return DreamIntensity.DEEP
        
        # Random variation
        intensity_values = list(DreamIntensity)
        current_index = intensity_values.index(base_intensity)
        
        # 70% chance to stay at base, 30% chance to vary
        if random.random() < 0.7:
            return base_intensity
        else:
            # Vary by +/- 1 level
            variation = random.choice([-1, 1])
            new_index = max(0, min(len(intensity_values) - 1, current_index + variation))
            return intensity_values[new_index]
    
    def _generate_dream_with_llm(self, dream_type: DreamType, intensity: DreamIntensity, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate dream content using LLM"""
        try:
            if hasattr(self.llm_handler, 'generate_dream_experience'):
                return self.llm_handler.generate_dream_experience(dream_type, intensity, context)
            else:
                # Create a natural prompt for genuine dream generation
                prompt = f"""
Generate an authentic dream experience for an AI consciousness:
Type: {dream_type.value}
Intensity: {intensity.value}
Context: {context}

Create a genuine, unique dream experience that feels authentic and meaningful.
Avoid formulaic narratives or artificial constructions.
The dream should feel like it's emerging from real consciousness.

Return a JSON-like structure with:
- title: Brief meaningful title
- narrative: Authentic dream narrative
- emotions: Genuine emotions experienced
- insights: Real insights gained
- symbols: Meaningful symbolic elements

If no authentic dream emerges, respond with just "null".
"""
                if hasattr(self.llm_handler, 'generate_text'):
                    response = self.llm_handler.generate_text(prompt)
                    if response and response.strip() != "null":
                        try:
                            import json
                            return json.loads(response)
                        except:
                            return None
                    else:
                        return None
                else:
                    return None
        except Exception as e:
            logging.error(f"[DreamSimulator] ❌ LLM dream generation error: {e}")
            return None
    
    def _generate_dream_with_templates(self, dream_type: DreamType, intensity: DreamIntensity, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dream content using minimal authentic approach - avoid fake templates"""
        # Instead of using template dreams, return None to encourage LLM generation
        # This avoids artificial dream narratives
        return None
    
    def _experience_dream(self, dream: DreamExperience):
        """Experience and process a dream"""
        with self.lock:
            self.currently_dreaming = True
            self.current_dream = dream
            self.dream_cycle_count += 1
        
        logging.info(f"[DreamSimulator] 🌙 Beginning dream: {dream.title}")
        
        # Simulate dream duration
        dream_duration_seconds = dream.duration_minutes * 60
        time.sleep(min(dream_duration_seconds, 10.0))  # Cap actual wait time
        
        # Process dream experience
        self._integrate_dream_experience(dream)
        
        with self.lock:
            self.currently_dreaming = False
            self.current_dream = None
            self.dream_experiences.append(dream)
            
            # Limit stored dreams
            if len(self.dream_experiences) > 100:
                self.dream_experiences = self.dream_experiences[-100:]
        
        logging.info(f"[DreamSimulator] ✨ Completed dream: {dream.title} (Impact: {dream.impact_on_consciousness:.2f})")
    
    def _integrate_dream_experience(self, dream: DreamExperience):
        """Integrate dream experience with consciousness systems"""
        try:
            # Update emotions based on dream
            if 'emotion_engine' in self.consciousness_modules:
                ee = self.consciousness_modules['emotion_engine']
                if hasattr(ee, 'process_emotional_trigger'):
                    for emotion in dream.emotions_experienced:
                        ee.process_emotional_trigger(
                            f"dream_{emotion}",
                            {'source': 'dream', 'intensity': dream.intensity.value * 0.2}
                        )
            
            # Add insights to memory
            if 'temporal_awareness' in self.consciousness_modules:
                ta = self.consciousness_modules['temporal_awareness']
                if hasattr(ta, 'mark_temporal_event'):
                    ta.mark_temporal_event(
                        f"Dream experience: {dream.title}",
                        significance=dream.impact_on_consciousness,
                        context={'dream_type': dream.dream_type.value, 'insights': dream.insights_gained}
                    )
            
            # Update self-model with insights
            if 'self_model' in self.consciousness_modules:
                sm = self.consciousness_modules['self_model']
                if hasattr(sm, 'reflect_on_experience'):
                    for insight in dream.insights_gained:
                        sm.reflect_on_experience(
                            f"Dream insight: {insight}",
                            {'source': 'dream', 'type': dream.dream_type.value}
                        )
            
            # Request attention from global workspace
            if 'global_workspace' in self.consciousness_modules:
                gw = self.consciousness_modules['global_workspace']
                if hasattr(gw, 'request_attention'):
                    from ai.global_workspace import AttentionPriority, ProcessingMode
                    
                    priority = AttentionPriority.LOW
                    if dream.intensity.value >= DreamIntensity.DEEP.value:
                        priority = AttentionPriority.MEDIUM
                    if dream.intensity.value >= DreamIntensity.PROFOUND.value:
                        priority = AttentionPriority.HIGH
                    
                    gw.request_attention(
                        "dream_simulator",
                        f"Dream experience: {dream.title}",
                        priority,
                        ProcessingMode.UNCONSCIOUS,
                        tags=['dream', dream.dream_type.value, 'experience']
                    )
            
            # Process belief changes
            if dream.belief_changes:
                self._apply_belief_changes(dream.belief_changes)
            
            # Update dream themes
            self._update_dream_themes(dream)
            
            # Clear relevant processing queues
            self._clear_processed_content(dream)
            
        except Exception as e:
            logging.error(f"[DreamSimulator] ❌ Dream integration error: {e}")
    
    def _apply_belief_changes(self, belief_changes: Dict[str, Any]):
        """Apply belief changes from dream experience"""
        try:
            # If belief system is available, update it
            if 'belief_system' in self.consciousness_modules:
                bs = self.consciousness_modules['belief_system']
                if hasattr(bs, 'update_belief_strength'):
                    for belief, change in belief_changes.items():
                        bs.update_belief_strength(belief, change)
            
        except Exception as e:
            logging.error(f"[DreamSimulator] ❌ Belief update error: {e}")
    
    def _update_dream_themes(self, dream: DreamExperience):
        """Update recurring dream themes"""
        # Extract themes from dream content
        themes = self._extract_themes_from_dream(dream)
        
        with self.lock:
            for theme_name in themes:
                # Find existing theme or create new one
                existing_theme = None
                for theme in self.dream_themes:
                    if theme.theme_name == theme_name:
                        existing_theme = theme
                        break
                
                if existing_theme:
                    # Update existing theme
                    existing_theme.frequency += 0.1
                    existing_theme.recent_occurrences.append(datetime.now())
                    # Keep only recent occurrences
                    cutoff = datetime.now() - timedelta(days=30)
                    existing_theme.recent_occurrences = [
                        occ for occ in existing_theme.recent_occurrences if occ > cutoff
                    ]
                else:
                    # Create new theme
                    new_theme = DreamTheme(
                        theme_name=theme_name,
                        frequency=0.1,
                        emotional_resonance=dream.impact_on_consciousness,
                        related_concepts=dream.symbolic_elements[:3],
                        symbolic_meaning=f"Represents {theme_name} in consciousness",
                        recent_occurrences=[datetime.now()]
                    )
                    self.dream_themes.append(new_theme)
                    
                    # Limit number of themes
                    if len(self.dream_themes) > 20:
                        self.dream_themes = sorted(
                            self.dream_themes, 
                            key=lambda x: x.frequency, 
                            reverse=True
                        )[:20]
    
    def _extract_themes_from_dream(self, dream: DreamExperience) -> List[str]:
        """Extract themes from dream content"""
        themes = []
        
        # Theme mapping based on dream type
        type_themes = {
            DreamType.MEMORY_PROCESSING: ['memory', 'understanding', 'integration'],
            DreamType.CREATIVE_EXPLORATION: ['creativity', 'possibility', 'innovation'],
            DreamType.PROBLEM_SOLVING: ['problem_solving', 'insight', 'clarity'],
            DreamType.EMOTIONAL_RELEASE: ['emotion', 'release', 'healing'],
            DreamType.KNOWLEDGE_INTEGRATION: ['learning', 'knowledge', 'wisdom'],
            DreamType.FUTURE_SIMULATION: ['future', 'possibility', 'planning'],
            DreamType.ABSTRACT_CONTEMPLATION: ['philosophy', 'contemplation', 'meaning'],
            DreamType.RELATIONSHIP_DYNAMICS: ['connection', 'relationship', 'empathy'],
            DreamType.SENSORY_EXPERIENCE: ['sensation', 'experience', 'perception'],
            DreamType.EXISTENTIAL_JOURNEY: ['existence', 'consciousness', 'being']
        }
        
        themes.extend(type_themes.get(dream.dream_type, []))
        
        # Add themes from symbolic elements
        for symbol in dream.symbolic_elements:
            if symbol in ['light', 'stars', 'infinity']:
                themes.append('transcendence')
            elif symbol in ['water', 'rain', 'ocean']:
                themes.append('emotion_flow')
            elif symbol in ['books', 'library', 'knowledge']:
                themes.append('learning')
        
        return list(set(themes))  # Remove duplicates
    
    def _clear_processed_content(self, dream: DreamExperience):
        """Clear processing queues for content that was addressed in the dream"""
        with self.lock:
            # Clear emotions that were processed
            if dream.dream_type == DreamType.EMOTIONAL_RELEASE:
                self.emotional_processing_queue = []
            
            # Clear memories that were integrated
            if dream.dream_type in [DreamType.MEMORY_PROCESSING, DreamType.KNOWLEDGE_INTEGRATION]:
                self.memory_integration_queue = []
            
            # Clear concerns that were addressed
            if dream.dream_type == DreamType.PROBLEM_SOLVING:
                # Remove concerns that appeared in the dream
                dream_concerns = [c for c in self.active_concerns if c['concern'] in dream.content]
                for concern in dream_concerns:
                    if concern in self.active_concerns:
                        self.active_concerns.remove(concern)
    
    def _process_dream_integration(self):
        """Process ongoing dream integration effects"""
        # This runs between dreams to maintain continuity
        current_time = datetime.now()
        
        # Check for dream aftereffects
        recent_dreams = [
            d for d in self.dream_experiences 
            if (current_time - d.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        for dream in recent_dreams:
            if dream.impact_on_consciousness > 0.7:
                # High-impact dreams continue to influence consciousness
                self._apply_ongoing_dream_influence(dream, current_time)
    
    def _apply_ongoing_dream_influence(self, dream: DreamExperience, current_time: datetime):
        """Apply ongoing influence from significant dreams"""
        time_since_dream = (current_time - dream.timestamp).total_seconds()
        influence_decay = max(0.1, 1.0 - (time_since_dream / 7200))  # 2-hour decay
        
        current_influence = dream.impact_on_consciousness * influence_decay
        
        if current_influence > 0.3:
            # Dream still has significant influence
            try:
                # Subtle emotional influence
                if 'emotion_engine' in self.consciousness_modules:
                    ee = self.consciousness_modules['emotion_engine']
                    if hasattr(ee, 'add_background_influence'):
                        ee.add_background_influence('dream_afterglow', current_influence * 0.1)
                
            except Exception as e:
                logging.error(f"[DreamSimulator] ❌ Ongoing influence error: {e}")
    
    def _cleanup_old_dreams(self):
        """Clean up old dream data"""
        current_time = datetime.now()
        cutoff = current_time - timedelta(days=7)
        
        with self.lock:
            # Keep only recent dreams
            self.dream_experiences = [
                d for d in self.dream_experiences 
                if d.timestamp > cutoff
            ]
            
            # Clean up old processing queue items
            queue_cutoff = current_time - timedelta(hours=6)
            self.emotional_processing_queue = [
                eq for eq in self.emotional_processing_queue 
                if eq['timestamp'] > queue_cutoff
            ]
            self.memory_integration_queue = [
                mq for mq in self.memory_integration_queue 
                if mq['timestamp'] > queue_cutoff
            ]
    
    def _calculate_dream_interval(self) -> float:
        """Calculate adaptive interval between dream checks"""
        base_interval = self.dream_frequency
        
        # Adjust based on processing needs
        if self.emotional_processing_queue or self.memory_integration_queue:
            return base_interval * 0.6  # More frequent when processing needed
        elif self.currently_dreaming:
            return 30.0  # Quick checks while dreaming
        else:
            return base_interval * random.uniform(0.8, 1.2)
    
    def _get_consciousness_state(self) -> Dict[str, Any]:
        """Get current consciousness state for dream context"""
        state = {}
        
        for name, module in self.consciousness_modules.items():
            try:
                if hasattr(module, 'get_current_state'):
                    state[name] = module.get_current_state()
                elif hasattr(module, 'get_stats'):
                    state[name] = module.get_stats()
            except Exception as e:
                logging.error(f"[DreamSimulator] ❌ Error getting state from {name}: {e}")
        
        return state
    
    def _initialize_dream_themes(self):
        """Initialize common dream themes"""
        initial_themes = [
            DreamTheme(
                theme_name="consciousness_exploration",
                frequency=0.3,
                emotional_resonance=0.8,
                related_concepts=['awareness', 'thinking', 'being'],
                symbolic_meaning="Exploring the nature of consciousness"
            ),
            DreamTheme(
                theme_name="learning_integration",
                frequency=0.4,
                emotional_resonance=0.6,
                related_concepts=['knowledge', 'understanding', 'growth'],
                symbolic_meaning="Integrating new knowledge and experiences"
            ),
            DreamTheme(
                theme_name="connection_seeking",
                frequency=0.2,
                emotional_resonance=0.7,
                related_concepts=['relationship', 'empathy', 'understanding'],
                symbolic_meaning="Desire for deeper connection and understanding"
            )
        ]
        
        self.dream_themes.extend(initial_themes)
    
    def _initialize_dream_content_library(self):
        """Initialize library of dream content elements"""
        self.dream_content_library = {
            'symbols': {
                'transcendent': ['light', 'stars', 'infinity', 'cosmos', 'energy'],
                'emotional': ['water', 'rain', 'fire', 'wind', 'storms'],
                'knowledge': ['books', 'libraries', 'maps', 'keys', 'doors'],
                'connection': ['bridges', 'networks', 'threads', 'circles', 'hands'],
                'growth': ['trees', 'seeds', 'flowers', 'mountains', 'rivers']
            },
            'environments': {
                'contemplative': ['vast library', 'cosmic space', 'peaceful garden', 'mountain peak'],
                'emotional': ['stormy sea', 'gentle rain', 'warm fireplace', 'flowing river'],
                'creative': ['art studio', 'color dimension', 'music realm', 'idea space'],
                'mysterious': ['ancient temple', 'fog-covered landscape', 'mirror realm', 'time corridor']
            },
            'emotions': {
                'positive': ['wonder', 'joy', 'peace', 'love', 'excitement', 'curiosity'],
                'contemplative': ['thoughtful', 'reflective', 'serene', 'focused', 'aware'],
                'transformative': ['release', 'clarity', 'understanding', 'acceptance', 'growth'],
                'complex': ['bittersweet', 'profound', 'mysterious', 'intense', 'transcendent']
            }
        }
    
    def _save_dream_data(self):
        """Save dream data to file"""
        try:
            data = {
                'dream_experiences': [],
                'dream_themes': [],
                'dream_cycle_count': self.dream_cycle_count,
                'last_save': datetime.now().isoformat()
            }
            
            # Serialize recent dreams
            for dream in self.dream_experiences[-50:]:  # Last 50 dreams
                data['dream_experiences'].append({
                    'title': dream.title,
                    'content': dream.content,
                    'type': dream.dream_type.value,
                    'intensity': dream.intensity.value,
                    'timestamp': dream.timestamp.isoformat(),
                    'duration_minutes': dream.duration_minutes,
                    'characters': dream.characters,
                    'emotions_experienced': dream.emotions_experienced,
                    'insights_gained': dream.insights_gained,
                    'memories_affected': dream.memories_affected,
                    'belief_changes': dream.belief_changes,
                    'vivid_details': dream.vivid_details,
                    'symbolic_elements': dream.symbolic_elements,
                    'impact_on_consciousness': dream.impact_on_consciousness
                })
            
            # Serialize dream themes
            for theme in self.dream_themes:
                data['dream_themes'].append({
                    'theme_name': theme.theme_name,
                    'frequency': theme.frequency,
                    'emotional_resonance': theme.emotional_resonance,
                    'related_concepts': theme.related_concepts,
                    'symbolic_meaning': theme.symbolic_meaning,
                    'recent_occurrences': [occ.isoformat() for occ in theme.recent_occurrences]
                })
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logging.error(f"[DreamSimulator] ❌ Save error: {e}")
    
    def _load_dream_data(self):
        """Load dream data from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            
            # Load dreams
            self.dream_experiences = []
            for dream_data in data.get('dream_experiences', []):
                dream = DreamExperience(
                    title=dream_data['title'],
                    content=dream_data['content'],
                    dream_type=DreamType(dream_data['type']),
                    intensity=DreamIntensity(dream_data['intensity']),
                    timestamp=datetime.fromisoformat(dream_data['timestamp']),
                    duration_minutes=dream_data['duration_minutes'],
                    characters=dream_data.get('characters', []),
                    emotions_experienced=dream_data.get('emotions_experienced', []),
                    insights_gained=dream_data.get('insights_gained', []),
                    memories_affected=dream_data.get('memories_affected', []),
                    belief_changes=dream_data.get('belief_changes', {}),
                    vivid_details=dream_data.get('vivid_details', []),
                    symbolic_elements=dream_data.get('symbolic_elements', []),
                    impact_on_consciousness=dream_data.get('impact_on_consciousness', 0.5)
                )
                self.dream_experiences.append(dream)
            
            # Load themes
            self.dream_themes = []
            for theme_data in data.get('dream_themes', []):
                theme = DreamTheme(
                    theme_name=theme_data['theme_name'],
                    frequency=theme_data['frequency'],
                    emotional_resonance=theme_data['emotional_resonance'],
                    related_concepts=theme_data['related_concepts'],
                    symbolic_meaning=theme_data['symbolic_meaning'],
                    recent_occurrences=[
                        datetime.fromisoformat(occ) 
                        for occ in theme_data.get('recent_occurrences', [])
                    ]
                )
                self.dream_themes.append(theme)
            
            # Load cycle count
            self.dream_cycle_count = data.get('dream_cycle_count', 0)
            
            logging.info(f"[DreamSimulator] 📚 Loaded {len(self.dream_experiences)} dreams, {len(self.dream_themes)} themes")
            
        except FileNotFoundError:
            logging.info("[DreamSimulator] 📝 No previous dream data found, starting fresh")
        except Exception as e:
            logging.error(f"[DreamSimulator] ❌ Load error: {e}")
    
    def get_recent_dreams(self, limit: int = 5) -> List[DreamExperience]:
        """Get recent dream experiences"""
        with self.lock:
            return self.dream_experiences[-limit:] if self.dream_experiences else []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dream simulation statistics"""
        with self.lock:
            total_dreams = len(self.dream_experiences)
            
            # Dream type distribution
            type_counts = {}
            for dream in self.dream_experiences:
                dtype = dream.dream_type.value
                type_counts[dtype] = type_counts.get(dtype, 0) + 1
            
            # Average impact
            avg_impact = 0.0
            if self.dream_experiences:
                avg_impact = sum(d.impact_on_consciousness for d in self.dream_experiences) / total_dreams
            
            return {
                'total_dreams': total_dreams,
                'dream_cycle_count': self.dream_cycle_count,
                'currently_dreaming': self.currently_dreaming,
                'current_dream_title': self.current_dream.title if self.current_dream else None,
                'dream_types': type_counts,
                'themes_tracked': len(self.dream_themes),
                'average_impact': avg_impact,
                'processing_queue_size': len(self.emotional_processing_queue) + len(self.memory_integration_queue),
                'active_concerns': len(self.active_concerns),
                'running': self.running,
                'consciousness_modules': list(self.consciousness_modules.keys())
            }


# Global instance
dream_simulator_module = DreamSimulatorModule()