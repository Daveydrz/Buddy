#!/usr/bin/env python3
"""
Cognitive Integration Module - Connects all cognitive modules to LLM pipeline
Created: 2025-01-18
Purpose: Integrate and activate all existing cognitive modules (memory, beliefs, emotions, 
         qualia, personality, introspection, timeline) so they directly affect Buddy's 
         behavior and language model reasoning in real time.
"""

import threading
import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

# Import all cognitive modules
try:
    from .emotion import emotion_engine, EmotionType, MoodType
    from .global_workspace import global_workspace, AttentionPriority, ProcessingMode
    from .self_model import self_model, SelfAspect
    from .motivation import motivation_system, MotivationType, GoalType  
    from .inner_monologue import inner_monologue, ThoughtType
    from .temporal_awareness import temporal_awareness, TemporalScale
    from .subjective_experience import subjective_experience, ExperienceType
    from .entropy import entropy_system, EntropyType
    from .memory_context_corrector import MemoryContextCorrector
    from .belief_qualia_linking import BeliefQualiaLinker
    from .value_system import ValueSystem
    from .conscious_prompt_builder import ConsciousPromptBuilder
    from .introspection_loop import IntrospectionLoop
    from .emotion_response_modulator import EmotionResponseModulator
    from .dialogue_confidence_filter import DialogueConfidenceFilter
    from .qualia_analytics import QualiaAnalytics
    from .belief_memory_refiner import BeliefMemoryRefiner
    from .self_model_updater import SelfModelUpdater
    from .goal_reasoning import GoalReasoner
    from .motivation_reasoner import MotivationReasoner
    from .internal_state_verbalizer import InternalStateVerbalizer
    from .memory import get_user_memory
    from .belief_analyzer import belief_analyzer
    from .personality_state import personality_state
    COGNITIVE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"[CognitiveIntegration] ⚠️ Some cognitive modules not available: {e}")
    COGNITIVE_MODULES_AVAILABLE = False

@dataclass
class CognitiveState:
    """Current cognitive state snapshot"""
    emotional_state: Dict[str, Any] = field(default_factory=dict)
    consciousness_state: Dict[str, Any] = field(default_factory=dict)
    memory_context: str = ""
    beliefs_summary: str = ""
    personality_modulation: Dict[str, float] = field(default_factory=dict)
    qualia_state: Dict[str, Any] = field(default_factory=dict)
    internal_thoughts: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

class CognitiveIntegrator:
    """
    Orchestrates all cognitive modules to provide real-time consciousness integration
    """
    
    def __init__(self):
        self.running = False
        self.integration_thread = None
        self.current_state = CognitiveState()
        self.state_lock = threading.Lock()
        
        # Initialize individual modules
        self.memory_corrector = None
        self.belief_qualia_linker = None
        self.value_system = None
        self.prompt_builder = None
        self.introspection_loop = None
        self.emotion_modulator = None
        self.confidence_filter = None
        self.qualia_analytics = None
        self.belief_refiner = None
        self.self_updater = None
        self.goal_reasoner = None
        self.motivation_reasoner = None
        self.state_verbalizer = None
        
        # Integration statistics
        self.total_updates = 0
        self.last_introspection = None
        self.consciousness_events = []
        
        if COGNITIVE_MODULES_AVAILABLE:
            self._initialize_modules()
        
        logging.info("[CognitiveIntegrator] 🧠 Cognitive integration system initialized")
    
    def _initialize_modules(self):
        """Initialize all cognitive module instances"""
        try:
            self.memory_corrector = MemoryContextCorrector()
            self.belief_qualia_linker = BeliefQualiaLinker()
            self.value_system = ValueSystem()
            self.prompt_builder = ConsciousPromptBuilder()
            self.introspection_loop = IntrospectionLoop()
            self.emotion_modulator = EmotionResponseModulator()
            self.confidence_filter = DialogueConfidenceFilter()
            self.qualia_analytics = QualiaAnalytics()
            self.belief_refiner = BeliefMemoryRefiner()
            self.self_updater = SelfModelUpdater()
            self.goal_reasoner = GoalReasoner()
            self.motivation_reasoner = MotivationReasoner()
            self.state_verbalizer = InternalStateVerbalizer()
            
            logging.info("[CognitiveIntegrator] ✅ All cognitive modules initialized")
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Module initialization error: {e}")
    
    def start(self):
        """Start the cognitive integration system"""
        if not COGNITIVE_MODULES_AVAILABLE:
            logging.warning("[CognitiveIntegrator] ⚠️ Cognitive modules not available")
            return
            
        if self.running:
            return
        
        self.running = True
        
        # Start core consciousness modules
        try:
            global_workspace.start()
            emotion_engine.start()
            motivation_system.start()
            inner_monologue.start()
            temporal_awareness.start()
            subjective_experience.start()
            entropy_system.start()
            
            logging.info("[CognitiveIntegrator] 🚀 Core consciousness modules started")
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Error starting core modules: {e}")
        
        # Start integration loop
        self.integration_thread = threading.Thread(target=self._integration_loop, daemon=True)
        self.integration_thread.start()
        
        logging.info("[CognitiveIntegrator] ✅ Cognitive integration system started")
    
    def stop(self):
        """Stop the cognitive integration system"""
        self.running = False
        
        if self.integration_thread:
            self.integration_thread.join(timeout=2.0)
        
        # Stop core consciousness modules
        try:
            entropy_system.stop()
            subjective_experience.stop()
            temporal_awareness.stop()
            inner_monologue.stop()
            motivation_system.stop()
            emotion_engine.stop()
            global_workspace.stop()
            
            logging.info("[CognitiveIntegrator] 🛑 Core consciousness modules stopped")
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Error stopping core modules: {e}")
        
        logging.info("[CognitiveIntegrator] ✅ Cognitive integration system stopped")
    
    def process_user_input(self, text: str, user_id: str) -> Dict[str, Any]:
        """
        Process user input through all cognitive modules and return integrated state
        
        Args:
            text: User input text
            user_id: User identifier
            
        Returns:
            Integrated cognitive state for LLM prompt injection
        """
        if not COGNITIVE_MODULES_AVAILABLE:
            return {"error": "cognitive_modules_unavailable"}
        
        try:
            # 1. Correct input using memory context
            corrected_text = self._correct_input_with_context(text, user_id)
            
            # 2. Process emotional response
            emotional_state = self._process_emotional_input(corrected_text, user_id)
            
            # 3. Update consciousness and attention
            consciousness_state = self._update_consciousness_attention(corrected_text, user_id)
            
            # 4. Extract and refine beliefs
            beliefs_state = self._process_beliefs_and_qualia(corrected_text, user_id)
            
            # 5. Update personality and motivation
            personality_state = self._update_personality_motivation(corrected_text, user_id)
            
            # 6. Generate internal state verbalization
            internal_state = self._generate_internal_state(corrected_text, user_id)
            
            # 7. Create integrated cognitive state
            with self.state_lock:
                self.current_state = CognitiveState(
                    emotional_state=emotional_state,
                    consciousness_state=consciousness_state,
                    memory_context=self._get_memory_context(user_id),
                    beliefs_summary=beliefs_state.get("summary", ""),
                    personality_modulation=personality_state.get("modulation", {}),
                    qualia_state=beliefs_state.get("qualia", {}),
                    internal_thoughts=internal_state.get("thoughts", []),
                    timestamp=datetime.now()
                )
                self.total_updates += 1
            
            # 8. Create prompt injection data
            prompt_data = self._create_prompt_injection_data()
            
            logging.debug(f"[CognitiveIntegrator] 🧠 Processed input: {len(corrected_text)} chars → {len(prompt_data)} injection keys")
            
            return prompt_data
            
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Error processing input: {e}")
            return {"error": str(e)}
    
    def _correct_input_with_context(self, text: str, user_id: str) -> str:
        """Use memory context to correct potential STT errors"""
        if not self.memory_corrector:
            return text
        
        try:
            # Apply corrections using memory context and beliefs
            corrected, corrections = self.memory_corrector.correct_with_belief_context(text, user_id)
            
            if corrected != text:
                logging.debug(f"[CognitiveIntegrator] 🔧 Input corrected: '{text}' → '{corrected}'")
            
            return corrected
            
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Context correction error: {e}")
            return text
    
    def _process_emotional_input(self, text: str, user_id: str) -> Dict[str, Any]:
        """Process emotional response to input"""
        try:
            # Trigger emotional processing
            emotion_response = emotion_engine.process_external_stimulus(
                f"User {user_id} said: {text}",
                {"user_id": user_id, "input": text}
            )
            
            # Get current emotional state
            current_state = emotion_engine.get_current_state()
            
            # Get emotional modulation
            modulation = emotion_engine.get_emotional_modulation("response")
            
            return {
                "current_emotion": current_state.get("primary_emotion", "neutral"),
                "intensity": current_state.get("intensity", 0.5),
                "arousal": current_state.get("arousal", 0.5),
                "valence": current_state.get("valence", 0.0),
                "mood": current_state.get("mood", "neutral"),
                "modulation": modulation
            }
            
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Emotional processing error: {e}")
            return {"current_emotion": "neutral", "intensity": 0.5}
    
    def _update_consciousness_attention(self, text: str, user_id: str) -> Dict[str, Any]:
        """Update consciousness and attention systems"""
        try:
            # Request attention for user input
            global_workspace.request_attention(
                "user_interaction",
                f"Processing input from {user_id}: {text[:50]}...",
                AttentionPriority.HIGH,
                ProcessingMode.CONSCIOUS,
                duration=30.0,
                tags=["user_input", "real_time_processing"]
            )
            
            # Get consciousness state
            consciousness_state = global_workspace.get_consciousness_state()
            
            # Mark temporal event
            temporal_awareness.mark_temporal_event(
                f"User interaction: {text[:30]}...",
                significance=0.7,
                context={"user_id": user_id, "input_length": len(text)}
            )
            
            return consciousness_state
            
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Consciousness update error: {e}")
            return {"attention_focus": "user_interaction", "processing_mode": "conscious"}
    
    def _process_beliefs_and_qualia(self, text: str, user_id: str) -> Dict[str, Any]:
        """Process beliefs and link to qualia"""
        try:
            # Extract beliefs from text
            belief_analysis = belief_analyzer.analyze_text_for_beliefs(text, user_id)
            beliefs = belief_analysis.get("extracted_beliefs", [])
            
            # Create qualia linkings for emotional content
            if self.belief_qualia_linker:
                for belief in beliefs:
                    # Link beliefs to qualia based on emotional content
                    if any(emotion_word in text.lower() for emotion_word in 
                          ["happy", "sad", "excited", "worried", "love", "hate", "feel"]):
                        belief_id = belief.get("id", "unknown") if isinstance(belief, dict) else "unknown"
                        self.belief_qualia_linker.create_belief_qualia_link(
                            belief_id,
                            "emotional_response",
                            {"trigger_text": text, "user_id": user_id}
                        )
            
            # Get qualia state
            qualia_state = {}
            if self.qualia_analytics:
                qualia_state = self.qualia_analytics.get_current_qualia_snapshot()
            
            return {
                "beliefs_extracted": len(beliefs),
                "summary": f"Extracted {len(beliefs)} beliefs from user input",
                "qualia": qualia_state
            }
            
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Beliefs/qualia processing error: {e}")
            return {"beliefs_extracted": 0, "summary": "No beliefs extracted"}
    
    def _update_personality_motivation(self, text: str, user_id: str) -> Dict[str, Any]:
        """Update personality and motivation systems"""
        try:
            # Update personality based on interaction
            personality_triggers = []
            try:
                personality_triggers = personality_state.analyze_user_text_for_triggers(text, user_id)
                if not isinstance(personality_triggers, list):
                    personality_triggers = []
            except Exception as e:
                logging.debug(f"[CognitiveIntegrator] Personality triggers error: {e}")
                personality_triggers = []
            
            # Process motivation and goals
            goals = []
            if self.goal_reasoner:
                try:
                    goals = self.goal_reasoner.generate_goals_from_context(
                        f"User {user_id} conversation about: {text[:50]}..."
                    )
                    if not isinstance(goals, list):
                        goals = []
                except Exception as e:
                    logging.debug(f"[CognitiveIntegrator] Goal generation error: {e}")
                    goals = []
            
            # Get personality modulation
            modulation = {}
            try:
                modulation = personality_state.get_personality_modifiers_for_llm(user_id)
                if not isinstance(modulation, dict):
                    modulation = {}
            except Exception as e:
                logging.debug(f"[CognitiveIntegrator] Personality modulation error: {e}")
                modulation = {}
            
            return {
                "personality_triggers": len(personality_triggers),
                "modulation": modulation,
                "goals_generated": len(goals) if goals else 0
            }
            
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Personality/motivation error: {e}")
            return {"personality_triggers": 0, "modulation": {}}
    
    def _generate_internal_state(self, text: str, user_id: str) -> Dict[str, Any]:
        """Generate internal state verbalizations"""
        try:
            thoughts = []
            
            # Trigger inner monologue thoughts
            inner_monologue.trigger_thought(
                f"User {user_id} said: {text}",
                {"user_id": user_id, "interaction_type": "conversation"},
                ThoughtType.OBSERVATION
            )
            
            # Get internal state verbalization
            if self.state_verbalizer:
                internal_state = self.state_verbalizer.verbalize_internal_state(
                    {"current_state": "processing_user_input", "context": text[:50]},
                    {"user_id": user_id, "emotional_state": "engaged"},
                    f"User {user_id} interaction: {text[:30]}..."
                )
                if internal_state and internal_state != "None":
                    thoughts.append(internal_state)
            
            # Create subjective experience
            experience = subjective_experience.process_experience(
                f"Conversing with {user_id} about: {text[:30]}...",
                ExperienceType.SOCIAL,
                {"user_id": user_id, "input": text}
            )
            
            return {
                "thoughts": thoughts,
                "experience_valence": experience.valence if hasattr(experience, 'valence') else 0.0,
                "experience_intensity": experience.intensity if hasattr(experience, 'intensity') else 0.5
            }
            
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Internal state generation error: {e}")
            return {"thoughts": [], "experience_valence": 0.0}
    
    def _get_memory_context(self, user_id: str) -> str:
        """Get memory context for the user"""
        try:
            memory = get_user_memory(user_id)
            return memory.get_contextual_memory_for_response()
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Memory context error: {e}")
            return ""
    
    def _create_prompt_injection_data(self) -> Dict[str, Any]:
        """Create data structure for LLM prompt injection"""
        with self.state_lock:
            state = self.current_state
            
            # 🎯 Get plan context for current user if available
            plan_context = ""
            try:
                from .memory import get_user_memory
                # Try to get current user from last interaction
                # This is a simplified approach - in full implementation would track current user
                for user_id in ["user_1", "default", "User"]:  # Common user IDs
                    try:
                        memory = get_user_memory(user_id)
                        user_plan = memory.get_user_today_plan()
                        if user_plan:
                            should_ask, reason = memory.should_ask_about_plans()
                            plan_context = f"User plan status: {reason}"
                            break
                    except:
                        continue
            except Exception as e:
                logging.debug(f"[CognitiveIntegrator] Plan context retrieval error: {e}")
            
            return {
                "cognitive_state": {
                    "emotion": state.emotional_state.get("current_emotion", "neutral"),
                    "mood": state.emotional_state.get("mood", "neutral"),
                    "arousal": state.emotional_state.get("arousal", 0.5),
                    "consciousness_focus": state.consciousness_state.get("attention_focus", "conversation"),
                    "processing_mode": state.consciousness_state.get("processing_mode", "conscious"),
                    "memory_context": state.memory_context[:200] if state.memory_context else "",
                    "beliefs_summary": state.beliefs_summary,
                    "internal_thoughts": state.internal_thoughts[:2],  # Limit to 2 most recent thoughts
                    "plan_context": plan_context  # 🎯 Add plan context
                },
                "response_modulation": {
                    **state.emotional_state.get("modulation", {}),
                    **state.personality_modulation
                },
                "timestamp": state.timestamp.isoformat(),
                "integration_stats": {
                    "total_updates": self.total_updates,
                    "modules_active": COGNITIVE_MODULES_AVAILABLE
                }
            }
    
    def _integration_loop(self):
        """Background integration and introspection loop"""
        logging.info("[CognitiveIntegrator] 🔄 Integration loop started")
        
        introspection_interval = 600  # 10 minutes
        last_introspection = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Run introspection every 10 minutes
                if current_time - last_introspection > introspection_interval:
                    self._run_introspection_cycle()
                    last_introspection = current_time
                
                # Update consciousness systems
                self._maintenance_cycle()
                
                # Sleep for a short interval
                time.sleep(30)  # Run maintenance every 30 seconds
                
            except Exception as e:
                logging.error(f"[CognitiveIntegrator] ❌ Integration loop error: {e}")
                time.sleep(5)
        
        logging.info("[CognitiveIntegrator] 🔄 Integration loop ended")
    
    def _run_introspection_cycle(self):
        """Run introspection and self-reflection cycle"""
        try:
            # Trigger introspection
            if self.introspection_loop:
                self.introspection_loop.trigger_introspection(
                    "regular_integration_cycle",
                    {"trigger": "scheduled", "timestamp": datetime.now().isoformat()}
                )
            
            # Update self-model based on recent interactions
            if self.self_updater:
                self.self_updater.update_personality_evolution()
            
            # Refine beliefs based on recent evidence
            if self.belief_refiner:
                self.belief_refiner.refine_belief_confidence()
            
            # Self-reflection
            self_model.reflect_on_experience(
                "Regular introspection cycle - reflecting on recent interactions and growth",
                {"type": "scheduled_introspection", "cycle_number": self.total_updates}
            )
            
            self.last_introspection = datetime.now()
            
            logging.info(f"[CognitiveIntegrator] 🔄 Introspection cycle completed (cycle #{self.total_updates})")
            
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Introspection cycle error: {e}")
    
    def _maintenance_cycle(self):
        """Perform maintenance on cognitive systems"""
        try:
            # Update qualia analytics
            if self.qualia_analytics:
                self.qualia_analytics.update_qualia_trends()
            
            # Process pending motivations
            if self.motivation_reasoner:
                self.motivation_reasoner.process_pending_decisions()
            
            # Track consciousness events
            self.consciousness_events.append({
                "timestamp": datetime.now().isoformat(),
                "state": self.current_state.consciousness_state,
                "emotion": self.current_state.emotional_state.get("current_emotion", "neutral")
            })
            
            # Limit event history
            if len(self.consciousness_events) > 100:
                self.consciousness_events = self.consciousness_events[-50:]
                
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Maintenance cycle error: {e}")
    
    def get_current_cognitive_state(self) -> Dict[str, Any]:
        """Get current integrated cognitive state"""
        with self.state_lock:
            return {
                "cognitive_state": self.current_state,
                "integration_stats": {
                    "total_updates": self.total_updates,
                    "last_introspection": self.last_introspection.isoformat() if self.last_introspection else None,
                    "modules_available": COGNITIVE_MODULES_AVAILABLE,
                    "running": self.running
                },
                "consciousness_events": len(self.consciousness_events)
            }
    
    def should_express_internal_state(self) -> Tuple[bool, Optional[str]]:
        """
        Determine if Buddy should express internal feelings/thoughts
        
        Returns:
            Tuple of (should_express, expression_text)
        """
        try:
            with self.state_lock:
                state = self.current_state
                
                # Express internal state occasionally based on conditions
                current_time = datetime.now()
                
                # Check if there are interesting internal thoughts
                if state.internal_thoughts:
                    # Express if emotion is intense or consciousness is highly active
                    emotion_intensity = state.emotional_state.get("intensity", 0.5)
                    arousal = state.emotional_state.get("arousal", 0.5)
                    
                    if emotion_intensity > 0.7 or arousal > 0.8:
                        thought = state.internal_thoughts[0] if state.internal_thoughts else None
                        if thought and thought != "None":
                            return True, f"I'm feeling quite {state.emotional_state.get('current_emotion', 'engaged')} right now... {thought}"
                
                # Express if consciousness state is interesting
                consciousness_focus = state.consciousness_state.get("attention_focus", "")
                if consciousness_focus and "high_priority" in consciousness_focus:
                    return True, f"I find myself really focused on this conversation right now."
                
                # Occasionally express based on qualia state
                if state.qualia_state and len(state.qualia_state) > 0:
                    if "emotional" in str(state.qualia_state).lower():
                        return True, f"This conversation is bringing up some interesting feelings for me."
                
                return False, None
                
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] ❌ Internal state expression error: {e}")
            return False, None

# Global instance
cognitive_integrator = CognitiveIntegrator()