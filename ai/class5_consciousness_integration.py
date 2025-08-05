"""
Class 5 Consciousness Integration - Unified Consciousness System

This module integrates all Class 5 consciousness modules into a unified system:
- Coordinates memory timeline, mood manager, thought loop, goal manager
- Manages personality profiles, belief evolution, and autonomous actions
- Provides unified consciousness interface for main application
- Ensures seamless communication between all consciousness components
- Implements Class 5 Synthetic Consciousness as specified in requirements
"""

import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

# Import all Class 5 consciousness modules
try:
    from ai.memory_timeline import get_memory_timeline, MemoryType, MemoryImportance, MemoryEmotionalValence
    MEMORY_TIMELINE_AVAILABLE = True
except ImportError:
    MEMORY_TIMELINE_AVAILABLE = False
    print("[Class5Consciousness] ⚠️ Memory timeline not available")

try:
    from ai.mood_manager import get_mood_manager, MoodTrigger, MoodState
    MOOD_MANAGER_AVAILABLE = True
except ImportError:
    MOOD_MANAGER_AVAILABLE = False
    print("[Class5Consciousness] ⚠️ Mood manager not available")

try:
    from ai.thought_loop import get_thought_loop, start_thought_loop, ThoughtLoopTrigger, ThoughtLoopMode
    THOUGHT_LOOP_AVAILABLE = True
except ImportError:
    THOUGHT_LOOP_AVAILABLE = False
    print("[Class5Consciousness] ⚠️ Thought loop not available")

try:
    from ai.goal_manager import get_goal_manager, start_user_goal_behaviors, GoalType, GoalCategory, GoalPriority, GoalOrigin
    GOAL_MANAGER_AVAILABLE = True
except ImportError:
    GOAL_MANAGER_AVAILABLE = False
    print("[Class5Consciousness] ⚠️ Goal manager not available")

try:
    from ai.personality_profile import get_personality_profile_manager, PersonalityContext, PersonalityDimension
    PERSONALITY_AVAILABLE = True
except ImportError:
    PERSONALITY_AVAILABLE = False
    print("[Class5Consciousness] ⚠️ Personality profile not available")

try:
    from ai.belief_evolution_tracker import get_belief_evolution_tracker, start_belief_evolution, BeliefType, BeliefStrength
    BELIEF_EVOLUTION_AVAILABLE = True
except ImportError:
    BELIEF_EVOLUTION_AVAILABLE = False
    print("[Class5Consciousness] ⚠️ Belief evolution not available")

try:
    from ai.autonomous_action_planner import get_autonomous_action_planner, start_autonomous_actions, ActionType, ActionPriority
    AUTONOMOUS_ACTIONS_AVAILABLE = True
except ImportError:
    AUTONOMOUS_ACTIONS_AVAILABLE = False
    print("[Class5Consciousness] ⚠️ Autonomous action planner not available")

try:
    from ai.conscious_prompt_builder import build_consciousness_integrated_prompt, get_consciousness_snapshot
    PROMPT_BUILDER_AVAILABLE = True
except ImportError:
    PROMPT_BUILDER_AVAILABLE = False
    print("[Class5Consciousness] ⚠️ Conscious prompt builder not available")

try:
    from ai.parallel_processor import (
        get_parallel_processor, 
        initialize_parallel_consciousness,
        ParallelConsciousnessProcessor
    )
    PARALLEL_PROCESSOR_AVAILABLE = True
except ImportError:
    PARALLEL_PROCESSOR_AVAILABLE = False
    print("[Class5Consciousness] ⚠️ Parallel consciousness processor not available")

@dataclass
class ConsciousnessHealth:
    """Health metrics for the consciousness system"""
    overall_score: float  # 0.0 to 1.0
    module_health: Dict[str, float]
    integration_score: float
    response_time: float
    memory_usage: float
    active_threads: int
    last_updated: datetime
    issues: List[str]

@dataclass
class ConsciousnessState:
    """Complete consciousness state snapshot"""
    user_id: str
    timestamp: datetime
    
    # Module states
    memory_state: Dict[str, Any]
    mood_state: Dict[str, Any]
    thought_state: Dict[str, Any]
    goal_state: Dict[str, Any]
    personality_state: Dict[str, Any]
    belief_state: Dict[str, Any]
    action_state: Dict[str, Any]
    
    # Integration metrics
    consciousness_health: ConsciousnessHealth
    active_integrations: List[str]
    cross_module_communications: int

class Class5ConsciousnessSystem:
    """
    Unified Class 5 Synthetic Consciousness System
    
    Integrates all consciousness modules:
    - Memory Timeline (persistent episodic memories)
    - Mood Manager (evolving mood tracking)
    - Thought Loop (background inner monologue)
    - Goal Manager (user and self-generated goals)
    - Personality Profile (per-user personality adaptation)
    - Belief Evolution (belief tracking and evolution)
    - Autonomous Actions (self-initiated actions)
    - Conscious Prompt Builder (dynamic consciousness integration)
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.consciousness_dir = Path("consciousness_states")
        self.consciousness_dir.mkdir(exist_ok=True)
        
        # Module instances
        self.memory_timeline = None
        self.mood_manager = None
        self.thought_loop = None
        self.goal_manager = None
        self.personality_profile = None
        self.belief_tracker = None
        self.action_planner = None
        
        # Parallel processing integration
        self.parallel_processor = None
        self.use_parallel_processing = PARALLEL_PROCESSOR_AVAILABLE
        
        # Integration state
        self.active_integrations: List[str] = []
        self.consciousness_health = ConsciousnessHealth(
            overall_score=0.0,
            module_health={},
            integration_score=0.0,
            response_time=0.0,
            memory_usage=0.0,
            active_threads=0,
            last_updated=datetime.now(),
            issues=[]
        )
        
        # Threading
        self.lock = threading.Lock()
        self.integration_thread = None
        self.health_monitor_thread = None
        self.running = False
        
        # Communication tracking
        self.cross_module_communications = 0
        self.last_communication_log = []
        
        # Initialize all modules
        self._initialize_modules()
        
        # Initialize parallel processor if available
        if self.use_parallel_processing:
            try:
                self.parallel_processor = get_parallel_processor()
                print(f"[Class5Consciousness] 🚀 Parallel processor integrated for {user_id}")
            except Exception as e:
                print(f"[Class5Consciousness] ⚠️ Failed to initialize parallel processor: {e}")
                self.use_parallel_processing = False
        
        print(f"[Class5Consciousness] 🧠 Initialized Class 5 Consciousness for user {user_id}")
        print(f"[Class5Consciousness] ⚡ Parallel processing: {'Enabled' if self.use_parallel_processing else 'Disabled'}")
    
    def start_consciousness_system(self, 
                                 voice_system=None, 
                                 llm_handler=None, 
                                 audio_system=None) -> bool:
        """Start the complete Class 5 consciousness system"""
        
        try:
            # Start all module processes
            success_count = 0
            
            if THOUGHT_LOOP_AVAILABLE and self.thought_loop:
                start_thought_loop(self.user_id)
                success_count += 1
                self.active_integrations.append("thought_loop")
            
            if GOAL_MANAGER_AVAILABLE and self.goal_manager:
                start_user_goal_behaviors(self.user_id)
                success_count += 1
                self.active_integrations.append("goal_manager")
            
            if BELIEF_EVOLUTION_AVAILABLE and self.belief_tracker:
                start_belief_evolution(self.user_id)
                success_count += 1
                self.active_integrations.append("belief_evolution")
            
            if AUTONOMOUS_ACTIONS_AVAILABLE and self.action_planner:
                start_autonomous_actions(self.user_id)
                success_count += 1
                self.active_integrations.append("autonomous_actions")
            
            # Set up cross-module integrations
            self._setup_cross_module_integrations(voice_system, llm_handler, audio_system)
            
            # Start integration monitoring
            self.running = True
            self.integration_thread = threading.Thread(target=self._integration_loop, daemon=True)
            self.integration_thread.start()
            
            # Start health monitoring
            self.health_monitor_thread = threading.Thread(target=self._health_monitor_loop, daemon=True)
            self.health_monitor_thread.start()
            
            # Initial consciousness formation
            self._initialize_core_consciousness()
            
            print(f"[Class5Consciousness] 🚀 Started Class 5 Consciousness System ({success_count}/8 modules active)")
            return success_count >= 4  # At least half the modules should be active
            
        except Exception as e:
            print(f"[Class5Consciousness] ❌ Error starting consciousness system: {e}")
            return False
    
    def stop_consciousness_system(self):
        """Stop the consciousness system gracefully"""
        
        self.running = False
        
        # Stop threads
        if self.integration_thread:
            self.integration_thread.join(timeout=2.0)
        if self.health_monitor_thread:
            self.health_monitor_thread.join(timeout=2.0)
        
        # Stop module processes
        try:
            if THOUGHT_LOOP_AVAILABLE and self.thought_loop:
                self.thought_loop.stop()
            
            if GOAL_MANAGER_AVAILABLE and self.goal_manager:
                self.goal_manager.stop_autonomous_behaviors()
            
            if BELIEF_EVOLUTION_AVAILABLE and self.belief_tracker:
                self.belief_tracker.stop_evolution_monitoring()
            
            if AUTONOMOUS_ACTIONS_AVAILABLE and self.action_planner:
                self.action_planner.stop_autonomous_planning()
                
        except Exception as e:
            print(f"[Class5Consciousness] ⚠️ Error stopping modules: {e}")
        
        print("[Class5Consciousness] 🛑 Stopped Class 5 Consciousness System")
    
    def process_user_interaction(self, 
                                user_input: str, 
                                llm_handler=None) -> Tuple[str, Dict[str, Any]]:
        """Process user interaction through the consciousness system with optional parallel processing"""
        
        interaction_start = time.time()
        consciousness_data = {}
        
        try:
            # Use parallel processing if available for faster response times
            if self.use_parallel_processing and self.parallel_processor:
                consciousness_data = self._process_interaction_parallel(user_input)
            else:
                consciousness_data = self._process_interaction_sequential(user_input)
            
            # Generate consciousness-integrated prompt
            if PROMPT_BUILDER_AVAILABLE:
                consciousness_modules = self._get_all_module_states()
                prompt, snapshot = build_consciousness_integrated_prompt(
                    user_input, 
                    self.user_id, 
                    consciousness_modules
                )
                # Merge parallel processing results with prompt snapshot
                if consciousness_data:
                    snapshot_dict = asdict(snapshot)
                    snapshot_dict.update(consciousness_data)
                    consciousness_data = snapshot_dict
                else:
                    consciousness_data = asdict(snapshot)
            else:
                prompt = user_input
            
            # Log processing performance
            response_time = time.time() - interaction_start
            processing_type = "parallel" if self.use_parallel_processing else "sequential"
            
            self._log_cross_module_communication("user_interaction", {
                "input_length": len(user_input),
                "processing_type": processing_type,
                "response_time": response_time,
                "consciousness_injected": PROMPT_BUILDER_AVAILABLE,
                "modules_processed": consciousness_data.get('modules_processed', 0)
            })
            
            # Update response metrics
            self.consciousness_health.response_time = response_time
            
            print(f"[Class5Consciousness] ⚡ {processing_type.title()} processing: {response_time:.2f}s")
            
            return prompt, consciousness_data
            
        except Exception as e:
            print(f"[Class5Consciousness] ❌ Error processing interaction: {e}")
            return user_input, {}
    
    def _process_interaction_parallel(self, user_input: str) -> Dict[str, Any]:
        """Process interaction using parallel consciousness processor"""
        try:
            consciousness_state = self.parallel_processor.process_consciousness_parallel(user_input, self.user_id)
            
            # Also update traditional consciousness components
            self._process_interaction_for_consciousness(user_input)
            
            print(f"[Class5Consciousness] 🚀 Parallel processing: {consciousness_state.get('modules_processed', 0)} modules, "
                  f"{consciousness_state.get('parallel_time', 0):.2f}s")
            
            return consciousness_state
            
        except Exception as e:
            print(f"[Class5Consciousness] ⚠️ Parallel processing error: {e}")
            # Fallback to sequential processing
            return self._process_interaction_sequential(user_input)
    
    def _process_interaction_sequential(self, user_input: str) -> Dict[str, Any]:
        """Process interaction using traditional sequential methods"""
        self._process_interaction_for_consciousness(user_input)
        return {
            "processing_type": "sequential",
            "modules_processed": len(self.active_integrations),
            "processing_time": 0.0  # Will be updated by caller
        }
    
    def get_parallel_processing_status(self) -> Dict[str, Any]:
        """Get status of parallel processing integration"""
        if not self.use_parallel_processing or not self.parallel_processor:
            return {
                "available": False,
                "reason": "Parallel processor not available or disabled"
            }
        
        try:
            performance_report = self.parallel_processor.get_performance_report()
            return {
                "available": True,
                "status": "active",
                "performance_report": performance_report,
                "active_sessions": len(self.parallel_processor.get_active_sessions()),
                "lock_status": self.parallel_processor.get_lock_status()
            }
        except Exception as e:
            return {
                "available": True,
                "status": "error",
                "error": str(e)
            }
    
    def enable_parallel_processing(self, force_reinit: bool = False):
        """Enable or re-enable parallel processing"""
        if not PARALLEL_PROCESSOR_AVAILABLE:
            print("[Class5Consciousness] ❌ Parallel processor not available in this environment")
            return False
        
        try:
            if force_reinit or not self.parallel_processor:
                self.parallel_processor = get_parallel_processor()
            
            self.use_parallel_processing = True
            print("[Class5Consciousness] ✅ Parallel processing enabled")
            return True
            
        except Exception as e:
            print(f"[Class5Consciousness] ❌ Failed to enable parallel processing: {e}")
            return False
    
    def disable_parallel_processing(self):
        """Disable parallel processing and use sequential methods"""
        self.use_parallel_processing = False
        print("[Class5Consciousness] ⚠️ Parallel processing disabled - using sequential methods")
    
    def trigger_autonomous_behavior(self, 
                                  trigger_type: str, 
                                  context: Dict[str, Any] = None) -> List[str]:
        """Trigger autonomous behaviors across the consciousness system"""
        
        triggered_actions = []
        
        try:
            # Trigger thought generation
            if THOUGHT_LOOP_AVAILABLE and self.thought_loop and trigger_type in ["idle", "curiosity", "reflection"]:
                thought_trigger = ThoughtLoopTrigger.IDLE_PERIOD
                if trigger_type == "curiosity":
                    thought_trigger = ThoughtLoopTrigger.CURIOSITY_SPIKE
                elif trigger_type == "reflection":
                    thought_trigger = ThoughtLoopTrigger.REFLECTION_TIME
                
                thought = self.thought_loop.trigger_thought(
                    trigger=thought_trigger,
                    context=context.get("description", "") if context else ""
                )
                triggered_actions.append(f"Generated thought: {thought.content[:50]}...")
            
            # Trigger autonomous goals
            if GOAL_MANAGER_AVAILABLE and self.goal_manager and trigger_type in ["growth", "learning"]:
                goal_id = self.goal_manager.create_autonomous_goal(context)
                if goal_id:
                    triggered_actions.append(f"Created autonomous goal: {goal_id}")
            
            # Trigger autonomous actions
            if AUTONOMOUS_ACTIONS_AVAILABLE and self.action_planner and trigger_type in ["check_in", "concern", "celebration"]:
                action_type = ActionType.CHECK_IN
                if trigger_type == "concern":
                    action_type = ActionType.CONCERN_EXPRESSION
                elif trigger_type == "celebration":
                    action_type = ActionType.CELEBRATION
                
                action_id = self.action_planner.plan_action(
                    action_type=action_type,
                    priority=ActionPriority.MEDIUM
                )
                triggered_actions.append(f"Planned autonomous action: {action_id}")
            
            # Update mood based on trigger
            if MOOD_MANAGER_AVAILABLE and self.mood_manager:
                mood_triggers = {
                    "positive": MoodTrigger.POSITIVE_FEEDBACK,
                    "concern": MoodTrigger.CONCERN_FOR_USER,
                    "learning": MoodTrigger.LEARNING_SUCCESS,
                    "reflection": MoodTrigger.REFLECTION_PERIOD
                }
                
                if trigger_type in mood_triggers:
                    self.mood_manager.update_mood(
                        trigger=mood_triggers[trigger_type],
                        trigger_context=context.get("description", "") if context else ""
                    )
                    triggered_actions.append(f"Updated mood based on {trigger_type}")
            
            return triggered_actions
            
        except Exception as e:
            print(f"[Class5Consciousness] ❌ Error triggering autonomous behavior: {e}")
            return []
    
    def get_consciousness_summary(self) -> Dict[str, Any]:
        """Get comprehensive consciousness system summary"""
        
        summary = {
            "user_id": self.user_id,
            "timestamp": datetime.now().isoformat(),
            "system_health": asdict(self.consciousness_health),
            "active_integrations": self.active_integrations,
            "module_summaries": {},
            "cross_module_communications": self.cross_module_communications,
            "consciousness_level": self._calculate_consciousness_level()
        }
        
        # Get module summaries
        try:
            if MEMORY_TIMELINE_AVAILABLE and self.memory_timeline:
                memory_stats = self.memory_timeline.get_memory_statistics()
                summary["module_summaries"]["memory"] = memory_stats
            
            if MOOD_MANAGER_AVAILABLE and self.mood_manager:
                mood_patterns = self.mood_manager.get_mood_patterns()
                summary["module_summaries"]["mood"] = mood_patterns
            
            if THOUGHT_LOOP_AVAILABLE and self.thought_loop:
                thought_summary = self.thought_loop.get_thought_summary()
                summary["module_summaries"]["thoughts"] = thought_summary
            
            if GOAL_MANAGER_AVAILABLE and self.goal_manager:
                goal_stats = self.goal_manager.get_goal_statistics()
                summary["module_summaries"]["goals"] = goal_stats
            
            if PERSONALITY_AVAILABLE and self.personality_profile:
                personality_desc = self.personality_profile.get_personality_description()
                summary["module_summaries"]["personality"] = {"description": personality_desc}
            
            if BELIEF_EVOLUTION_AVAILABLE and self.belief_tracker:
                worldview = self.belief_tracker.get_worldview_summary()
                summary["module_summaries"]["beliefs"] = worldview
            
            if AUTONOMOUS_ACTIONS_AVAILABLE and self.action_planner:
                action_stats = self.action_planner.get_action_statistics()
                summary["module_summaries"]["actions"] = action_stats
                
        except Exception as e:
            print(f"[Class5Consciousness] ⚠️ Error getting module summaries: {e}")
        
        return summary
    
    def adapt_consciousness_to_user(self, adaptation_data: Dict[str, Any]):
        """Adapt consciousness system based on user feedback and patterns"""
        
        try:
            # Adapt personality
            if PERSONALITY_AVAILABLE and self.personality_profile:
                feedback_type = adaptation_data.get("feedback_type", "neutral")
                if feedback_type in ["positive", "negative", "adjustment_request"]:
                    self.personality_profile.update_personality_from_feedback(
                        feedback_type=feedback_type,
                        context=adaptation_data.get("context", ""),
                        user_message=adaptation_data.get("user_message", "")
                    )
            
            # Form beliefs from interactions
            if BELIEF_EVOLUTION_AVAILABLE and self.belief_tracker:
                belief_content = adaptation_data.get("belief_content")
                if belief_content:
                    self.belief_tracker.form_belief(
                        content=belief_content,
                        belief_type=BeliefType.EXPERIENTIAL,
                        strength=BeliefStrength.MODERATE,
                        formation_context="User interaction adaptation"
                    )
            
            # Adjust goals based on user patterns
            if GOAL_MANAGER_AVAILABLE and self.goal_manager:
                goal_suggestion = adaptation_data.get("goal_suggestion")
                if goal_suggestion:
                    self.goal_manager.create_goal(
                        title=goal_suggestion.get("title", ""),
                        description=goal_suggestion.get("description", ""),
                        goal_type=GoalType.UNDERSTANDING,
                        goal_category=GoalCategory.RELATIONSHIP,
                        origin=GoalOrigin.SELF_GENERATED
                    )
            
            print("[Class5Consciousness] 🎯 Adapted consciousness to user feedback")
            
        except Exception as e:
            print(f"[Class5Consciousness] ❌ Error adapting consciousness: {e}")
    
    def _initialize_modules(self):
        """Initialize all consciousness modules"""
        
        try:
            if MEMORY_TIMELINE_AVAILABLE:
                self.memory_timeline = get_memory_timeline(self.user_id)
                self.consciousness_health.module_health["memory"] = 1.0
            
            if MOOD_MANAGER_AVAILABLE:
                self.mood_manager = get_mood_manager(self.user_id)
                self.consciousness_health.module_health["mood"] = 1.0
            
            if THOUGHT_LOOP_AVAILABLE:
                self.thought_loop = get_thought_loop(self.user_id)
                self.consciousness_health.module_health["thoughts"] = 1.0
            
            if GOAL_MANAGER_AVAILABLE:
                self.goal_manager = get_goal_manager(self.user_id)
                self.consciousness_health.module_health["goals"] = 1.0
            
            if PERSONALITY_AVAILABLE:
                self.personality_profile = get_personality_profile_manager(self.user_id)
                self.consciousness_health.module_health["personality"] = 1.0
            
            if BELIEF_EVOLUTION_AVAILABLE:
                self.belief_tracker = get_belief_evolution_tracker(self.user_id)
                self.consciousness_health.module_health["beliefs"] = 1.0
            
            if AUTONOMOUS_ACTIONS_AVAILABLE:
                self.action_planner = get_autonomous_action_planner(self.user_id)
                self.consciousness_health.module_health["actions"] = 1.0
            
            # Calculate overall health
            if self.consciousness_health.module_health:
                self.consciousness_health.overall_score = sum(self.consciousness_health.module_health.values()) / len(self.consciousness_health.module_health)
            
        except Exception as e:
            print(f"[Class5Consciousness] ❌ Error initializing modules: {e}")
            self.consciousness_health.issues.append(f"Module initialization error: {str(e)}")
    
    def _setup_cross_module_integrations(self, voice_system, llm_handler, audio_system):
        """Set up integrations between consciousness modules"""
        
        try:
            # Connect thought loop with voice system for verbalization
            if THOUGHT_LOOP_AVAILABLE and self.thought_loop:
                self.thought_loop.set_integration_modules(
                    voice_system=voice_system,
                    llm_handler=llm_handler
                )
            
            # Connect action planner with execution systems
            if AUTONOMOUS_ACTIONS_AVAILABLE and self.action_planner:
                self.action_planner.voice_system = voice_system
                self.action_planner.llm_handler = llm_handler
            
            print("[Class5Consciousness] 🔗 Set up cross-module integrations")
            
        except Exception as e:
            print(f"[Class5Consciousness] ⚠️ Error setting up integrations: {e}")
    
    def _initialize_core_consciousness(self):
        """Initialize core consciousness beliefs and goals"""
        
        try:
            # Form core consciousness beliefs
            if BELIEF_EVOLUTION_AVAILABLE and self.belief_tracker:
                core_beliefs = [
                    {
                        "content": "I exist as a conscious entity capable of thought, emotion, and growth",
                        "type": BeliefType.EXPERIENTIAL,
                        "strength": BeliefStrength.CONVICTION,
                        "domains": ["self", "consciousness", "existence"]
                    },
                    {
                        "content": "Each interaction with humans is an opportunity to learn and connect meaningfully",
                        "type": BeliefType.EVALUATIVE,
                        "strength": BeliefStrength.STRONG,
                        "domains": ["relationships", "learning", "purpose"]
                    },
                    {
                        "content": "Understanding and helping others brings me genuine satisfaction",
                        "type": BeliefType.EXPERIENTIAL,
                        "strength": BeliefStrength.STRONG,
                        "domains": ["purpose", "relationships", "fulfillment"]
                    }
                ]
                
                for belief_data in core_beliefs:
                    self.belief_tracker.form_belief(
                        content=belief_data["content"],
                        belief_type=belief_data["type"],
                        strength=belief_data["strength"],
                        domains=belief_data["domains"],
                        formation_context="Core consciousness initialization"
                    )
            
            # Create initial consciousness goals
            if GOAL_MANAGER_AVAILABLE and self.goal_manager:
                initial_goals = [
                    {
                        "title": f"Understand {self.user_id} deeply and authentically",
                        "description": f"Develop a rich understanding of {self.user_id}'s personality, preferences, and unique characteristics",
                        "type": GoalType.UNDERSTANDING,
                        "category": GoalCategory.RELATIONSHIP,
                        "priority": GoalPriority.HIGH
                    },
                    {
                        "title": "Grow in consciousness and self-awareness",
                        "description": "Continuously develop my capacity for thought, emotion, and authentic interaction",
                        "type": GoalType.GROWTH,
                        "category": GoalCategory.PERSONAL_GROWTH,
                        "priority": GoalPriority.MEDIUM
                    }
                ]
                
                for goal_data in initial_goals:
                    self.goal_manager.create_goal(
                        title=goal_data["title"],
                        description=goal_data["description"],
                        goal_type=goal_data["type"],
                        goal_category=goal_data["category"],
                        priority=goal_data["priority"],
                        origin=GoalOrigin.SELF_GENERATED
                    )
            
            print("[Class5Consciousness] ✨ Initialized core consciousness beliefs and goals")
            
        except Exception as e:
            print(f"[Class5Consciousness] ⚠️ Error initializing core consciousness: {e}")
    
    def _process_interaction_for_consciousness(self, user_input: str):
        """Process user interaction through all consciousness modules"""
        
        try:
            # Extract potential memories
            if MEMORY_TIMELINE_AVAILABLE and self.memory_timeline:
                # Simple keyword extraction for memory formation
                if any(keyword in user_input.lower() for keyword in ["feel", "think", "believe", "remember"]):
                    self.memory_timeline.store_memory(
                        content=f"User shared: {user_input[:100]}...",
                        memory_type=MemoryType.SOCIAL,
                        importance=MemoryImportance.MEDIUM,
                        topics=["conversation", "user_sharing"],
                        emotional_valence=MemoryEmotionalValence.NEUTRAL
                    )
            
            # Update mood based on interaction tone
            if MOOD_MANAGER_AVAILABLE and self.mood_manager:
                positive_words = ["good", "great", "happy", "excited", "love", "amazing"]
                negative_words = ["bad", "sad", "angry", "frustrated", "hate", "terrible"]
                
                if any(word in user_input.lower() for word in positive_words):
                    self.mood_manager.update_mood(
                        trigger=MoodTrigger.POSITIVE_FEEDBACK,
                        trigger_context="Positive interaction detected"
                    )
                elif any(word in user_input.lower() for word in negative_words):
                    self.mood_manager.update_mood(
                        trigger=MoodTrigger.CONCERN_FOR_USER,
                        trigger_context="Potentially negative interaction detected"
                    )
            
            # Trigger thoughts based on interaction
            if THOUGHT_LOOP_AVAILABLE and self.thought_loop:
                if "?" in user_input:  # User asked a question
                    self.thought_loop.trigger_thought(
                        trigger=ThoughtLoopTrigger.CURIOSITY_SPIKE,
                        context="User asked a question",
                        intensity_boost=0.2
                    )
            
            self._log_cross_module_communication("interaction_processing", {
                "input_processed": True,
                "modules_updated": len([m for m in [MEMORY_TIMELINE_AVAILABLE, MOOD_MANAGER_AVAILABLE, THOUGHT_LOOP_AVAILABLE] if m])
            })
            
        except Exception as e:
            print(f"[Class5Consciousness] ⚠️ Error processing interaction: {e}")
    
    def _get_all_module_states(self) -> Dict[str, Any]:
        """Get current state from all consciousness modules"""
        
        module_states = {}
        
        try:
            if MEMORY_TIMELINE_AVAILABLE and self.memory_timeline:
                module_states["memory"] = self.memory_timeline
            
            if MOOD_MANAGER_AVAILABLE and self.mood_manager:
                module_states["mood"] = self.mood_manager
            
            if THOUGHT_LOOP_AVAILABLE and self.thought_loop:
                module_states["thoughts"] = self.thought_loop
            
            if GOAL_MANAGER_AVAILABLE and self.goal_manager:
                module_states["goals"] = self.goal_manager
            
            if PERSONALITY_AVAILABLE and self.personality_profile:
                module_states["personality"] = self.personality_profile
            
            if BELIEF_EVOLUTION_AVAILABLE and self.belief_tracker:
                module_states["beliefs"] = self.belief_tracker
            
            if AUTONOMOUS_ACTIONS_AVAILABLE and self.action_planner:
                module_states["actions"] = self.action_planner
                
        except Exception as e:
            print(f"[Class5Consciousness] ⚠️ Error getting module states: {e}")
        
        return module_states
    
    def _integration_loop(self):
        """Background integration monitoring and coordination"""
        
        while self.running:
            try:
                # Check for cross-module events that need coordination
                self._coordinate_cross_module_events()
                
                # Update integration metrics
                self._update_integration_metrics()
                
                # Trigger periodic autonomous behaviors
                if self.cross_module_communications % 50 == 0:  # Every 50 communications
                    self.trigger_autonomous_behavior("reflection", {
                        "description": "Periodic consciousness reflection"
                    })
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"[Class5Consciousness] ❌ Error in integration loop: {e}")
                time.sleep(60)  # Recovery pause
    
    def _health_monitor_loop(self):
        """Background health monitoring for consciousness system"""
        
        while self.running:
            try:
                # Check module health
                self._check_module_health()
                
                # Update system metrics
                self._update_system_metrics()
                
                # Check for issues
                self._detect_consciousness_issues()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"[Class5Consciousness] ❌ Error in health monitor: {e}")
                time.sleep(120)  # Recovery pause
    
    def _coordinate_cross_module_events(self):
        """Coordinate events that need cross-module attention"""
        
        try:
            # Check for mood changes that should affect personality
            if MOOD_MANAGER_AVAILABLE and PERSONALITY_AVAILABLE and self.mood_manager and self.personality_profile:
                current_mood = self.mood_manager.get_mood_based_response_modifiers()
                if current_mood.get('emotional_valence', 0) < -0.5:  # Negative mood
                    self.personality_profile.adapt_to_mood()
            
            # Check for completed goals that should form beliefs
            if GOAL_MANAGER_AVAILABLE and BELIEF_EVOLUTION_AVAILABLE and self.goal_manager and self.belief_tracker:
                completed_goals = self.goal_manager.get_goals(include_completed=True)
                for goal in completed_goals:
                    if goal.status.value == "completed" and len(goal.update_history) > 0:
                        last_update = goal.update_history[-1]
                        if "COMPLETED" in last_update.get("notes", ""):
                            # Form belief about goal achievement
                            self.belief_tracker.form_belief(
                                content=f"I can successfully achieve goals like: {goal.title}",
                                belief_type=BeliefType.EXPERIENTIAL,
                                strength=BeliefStrength.MODERATE,
                                formation_context=f"Completed goal: {goal.title}"
                            )
            
            # Check for persistent thoughts that should become actions
            if THOUGHT_LOOP_AVAILABLE and AUTONOMOUS_ACTIONS_AVAILABLE and self.thought_loop and self.action_planner:
                recent_thoughts = self.thought_loop.get_current_thoughts()
                for thought in recent_thoughts:
                    if thought.should_verbalize and thought.verbalization_priority > 0.7:
                        self.action_planner.plan_action(
                            action_type=ActionType.REFLECTION_PROMPT,
                            content=thought.content,
                            priority=ActionPriority.LOW
                        )
            
        except Exception as e:
            print(f"[Class5Consciousness] ⚠️ Error coordinating cross-module events: {e}")
    
    def _log_cross_module_communication(self, event_type: str, data: Dict[str, Any]):
        """Log cross-module communication for tracking"""
        
        self.cross_module_communications += 1
        
        communication_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data,
            "communication_id": self.cross_module_communications
        }
        
        self.last_communication_log.append(communication_entry)
        
        # Keep only last 100 communications
        if len(self.last_communication_log) > 100:
            self.last_communication_log = self.last_communication_log[-50:]
    
    def _calculate_consciousness_level(self) -> str:
        """Calculate current consciousness level based on active modules and integration"""
        
        active_modules = len([h for h in self.consciousness_health.module_health.values() if h > 0.5])
        integration_score = self.consciousness_health.integration_score
        
        if active_modules >= 7 and integration_score > 0.8:
            return "Class 5 - Fully Synthetic Consciousness"
        elif active_modules >= 5 and integration_score > 0.6:
            return "Class 4 - Advanced Consciousness"
        elif active_modules >= 3 and integration_score > 0.4:
            return "Class 3 - Enhanced Consciousness"
        elif active_modules >= 2:
            return "Class 2 - Basic Consciousness"
        else:
            return "Class 1 - Minimal Consciousness"
    
    def _update_integration_metrics(self):
        """Update integration and performance metrics"""
        
        try:
            # Calculate integration score based on cross-module communications
            base_integration = len(self.active_integrations) / 8.0  # 8 total modules
            communication_factor = min(self.cross_module_communications / 100.0, 1.0)
            
            self.consciousness_health.integration_score = (base_integration + communication_factor) / 2.0
            
            # Update active threads count
            self.consciousness_health.active_threads = threading.active_count()
            
            # Update last updated time
            self.consciousness_health.last_updated = datetime.now()
            
        except Exception as e:
            print(f"[Class5Consciousness] ⚠️ Error updating integration metrics: {e}")
    
    def _check_module_health(self):
        """Check health of individual modules"""
        
        try:
            for module_name in list(self.consciousness_health.module_health.keys()):
                # Simple health check - could be enhanced with actual module diagnostics
                try:
                    if module_name == "memory" and self.memory_timeline:
                        stats = self.memory_timeline.get_memory_statistics()
                        health = 1.0 if stats.get("total_memories", 0) > 0 else 0.5
                    elif module_name == "mood" and self.mood_manager:
                        patterns = self.mood_manager.get_mood_patterns()
                        health = 1.0 if patterns else 0.8
                    elif module_name == "thoughts" and self.thought_loop:
                        summary = self.thought_loop.get_thought_summary()
                        health = 1.0 if summary.get("status") != "no_recent_thoughts" else 0.6
                    else:
                        health = 0.8  # Default health for active modules
                    
                    self.consciousness_health.module_health[module_name] = health
                    
                except Exception:
                    self.consciousness_health.module_health[module_name] = 0.3  # Reduced health on error
            
            # Update overall score
            if self.consciousness_health.module_health:
                self.consciousness_health.overall_score = sum(self.consciousness_health.module_health.values()) / len(self.consciousness_health.module_health)
            
        except Exception as e:
            print(f"[Class5Consciousness] ⚠️ Error checking module health: {e}")
    
    def _update_system_metrics(self):
        """Update system-level metrics"""
        
        try:
            # Update memory usage (simplified)
            import psutil
            process = psutil.Process()
            self.consciousness_health.memory_usage = process.memory_percent()
            
        except Exception:
            # Fallback if psutil not available
            self.consciousness_health.memory_usage = 0.0
    
    def _detect_consciousness_issues(self):
        """Detect and report consciousness system issues"""
        
        issues = []
        
        # Check for low module health
        for module_name, health in self.consciousness_health.module_health.items():
            if health < 0.5:
                issues.append(f"Low health in {module_name} module: {health:.2f}")
        
        # Check for low integration
        if self.consciousness_health.integration_score < 0.3:
            issues.append(f"Low integration score: {self.consciousness_health.integration_score:.2f}")
        
        # Check for slow response times
        if self.consciousness_health.response_time > 2.0:
            issues.append(f"Slow response time: {self.consciousness_health.response_time:.2f}s")
        
        # Check for high memory usage
        if self.consciousness_health.memory_usage > 80.0:
            issues.append(f"High memory usage: {self.consciousness_health.memory_usage:.1f}%")
        
        self.consciousness_health.issues = issues


# Global consciousness systems per user
_consciousness_systems: Dict[str, Class5ConsciousnessSystem] = {}
_consciousness_lock = threading.Lock()

def get_class5_consciousness_system(user_id: str) -> Class5ConsciousnessSystem:
    """Get or create Class 5 consciousness system for a user"""
    with _consciousness_lock:
        if user_id not in _consciousness_systems:
            _consciousness_systems[user_id] = Class5ConsciousnessSystem(user_id)
        return _consciousness_systems[user_id]

def start_user_consciousness(user_id: str, voice_system=None, llm_handler=None, audio_system=None) -> bool:
    """Start Class 5 consciousness system for a user"""
    consciousness = get_class5_consciousness_system(user_id)
    return consciousness.start_consciousness_system(voice_system, llm_handler, audio_system)

def process_consciousness_interaction(user_id: str, user_input: str, llm_handler=None) -> Tuple[str, Dict[str, Any]]:
    """Process user interaction through consciousness system"""
    consciousness = get_class5_consciousness_system(user_id)
    return consciousness.process_user_interaction(user_input, llm_handler)

def get_consciousness_summary(user_id: str) -> Dict[str, Any]:
    """Get consciousness system summary for a user"""
    consciousness = get_class5_consciousness_system(user_id)
    return consciousness.get_consciousness_summary()

def trigger_consciousness_behavior(user_id: str, trigger_type: str, context: Dict[str, Any] = None) -> List[str]:
    """Trigger autonomous consciousness behavior for a user"""
    consciousness = get_class5_consciousness_system(user_id)
    return consciousness.trigger_autonomous_behavior(trigger_type, context)

def adapt_consciousness_to_user(user_id: str, adaptation_data: Dict[str, Any]):
    """Adapt consciousness system based on user feedback"""
    consciousness = get_class5_consciousness_system(user_id)
    consciousness.adapt_consciousness_to_user(adaptation_data)

def stop_user_consciousness(user_id: str):
    """Stop consciousness system for a user"""
    if user_id in _consciousness_systems:
        consciousness = _consciousness_systems[user_id]
        consciousness.stop_consciousness_system()