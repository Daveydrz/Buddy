"""
Cognitive Integration - Main Integration Module

This module integrates all persistent cognitive modules with the existing
consciousness architecture and provides the main interface for the 
cognitive_prompt_injection system.
"""

import logging
import threading
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import all cognitive modules
try:
    from .self_model import persistent_self_model
    from .goal_bank import goal_bank
    from .experience_bank import experience_bank
    from .memory_prioritization import memory_prioritizer, MemoryPriorityConfig
    from .thought_loop import thought_loop
    COGNITIVE_MODULES_AVAILABLE = True
except ImportError as e:
    logging.error(f"Failed to import cognitive modules: {e}")
    COGNITIVE_MODULES_AVAILABLE = False

class CognitiveIntegrator:
    """
    Main integration class that coordinates all cognitive modules
    and provides the interface for cognitive_prompt_injection.
    """
    
    def __init__(self):
        self.is_initialized = False
        self.session_active = False
        self.initialization_lock = threading.Lock()
        
        # Module status tracking
        self.module_status = {
            "self_model": False,
            "goal_bank": False, 
            "experience_bank": False,
            "memory_prioritizer": False,
            "thought_loop": False
        }
        
        # Performance tracking
        self.total_integrations = 0
        self.last_integration_time = None
        
        if COGNITIVE_MODULES_AVAILABLE:
            self.initialize()
    
    def initialize(self) -> bool:
        """Initialize all cognitive modules"""
        with self.initialization_lock:
            if self.is_initialized:
                return True
            
            try:
                logging.info("[CognitiveIntegrator] Initializing persistent cognitive modules...")
                
                # Initialize self-model
                if persistent_self_model:
                    persistent_self_model.start_session()
                    self.module_status["self_model"] = True
                    logging.info("✅ Self-model initialized")
                
                # Initialize goal bank
                if goal_bank:
                    # Goal bank initializes automatically
                    self.module_status["goal_bank"] = True
                    logging.info("✅ Goal bank initialized")
                
                # Initialize experience bank
                if experience_bank:
                    # Experience bank initializes automatically
                    self.module_status["experience_bank"] = True
                    logging.info("✅ Experience bank initialized")
                
                # Initialize memory prioritizer
                if memory_prioritizer:
                    # Memory prioritizer initializes automatically
                    self.module_status["memory_prioritizer"] = True
                    logging.info("✅ Memory prioritizer initialized")
                
                # Initialize thought loop
                if thought_loop:
                    # Set up insight callback
                    thought_loop.set_insight_callback(self._handle_thought_loop_insight)
                    if not thought_loop.is_active:
                        thought_loop.start()
                    self.module_status["thought_loop"] = True
                    logging.info("✅ Thought loop initialized")
                
                self.is_initialized = True
                self.session_active = True
                
                logging.info("[CognitiveIntegrator] All cognitive modules initialized successfully!")
                return True
                
            except Exception as e:
                logging.error(f"[CognitiveIntegrator] Failed to initialize: {e}")
                return False
    
    def start_session(self, user: str = None):
        """Start a new cognitive session"""
        if not self.is_initialized:
            self.initialize()
        
        if user:
            # Add session start experience
            experience_bank.add_experience(
                event=f"Started new session with user {user}",
                emotion="engaged",
                importance=0.4,
                user=user,
                context={"session_start": True}
            )
        
        self.session_active = True
        logging.info(f"[CognitiveIntegrator] Started cognitive session for user: {user}")
    
    def end_session(self):
        """End the current cognitive session"""
        if self.session_active:
            # Save all module states
            if persistent_self_model:
                persistent_self_model.save()
            if goal_bank:
                goal_bank.save()
            if experience_bank:
                experience_bank.save()
            
            self.session_active = False
            logging.info("[CognitiveIntegrator] Ended cognitive session")
    
    def process_user_input(self, user_input: str, user: str, 
                         context_priority: str = "balanced") -> Dict[str, Any]:
        """
        Process user input and generate cognitive context for LLM injection.
        
        This is the main interface called by the LLM generation functions.
        """
        if not self.is_initialized or not COGNITIVE_MODULES_AVAILABLE:
            return {"error": "Cognitive modules not available"}
        
        try:
            self.total_integrations += 1
            self.last_integration_time = datetime.now()
            
            # Add the user input as an experience
            self._record_interaction_experience(user_input, user)
            
            # Generate prioritized cognitive context
            cognitive_context = memory_prioritizer.prioritize_cognitive_context(
                user=user,
                current_context=user_input,
                context_priority=context_priority
            )
            
            # Add integration metadata
            cognitive_context["integration_meta"] = {
                "timestamp": datetime.now().isoformat(),
                "user": user,
                "integration_count": self.total_integrations,
                "context_priority": context_priority,
                "modules_active": list(k for k, v in self.module_status.items() if v)
            }
            
            # Format for the expected cognitive_prompt_injection structure
            injection_data = {
                "cognitive_state": self._format_for_injection(cognitive_context),
                "memory_context": self._extract_memory_context(cognitive_context),
                "personality_context": self._extract_personality_context(cognitive_context),
                "goal_context": self._extract_goal_context(cognitive_context)
            }
            
            logging.debug(f"[CognitiveIntegrator] Generated cognitive injection with {len(injection_data)} components")
            return injection_data
            
        except Exception as e:
            logging.error(f"[CognitiveIntegrator] Error processing user input: {e}")
            return {"error": f"Cognitive processing failed: {e}"}
    
    def _record_interaction_experience(self, user_input: str, user: str):
        """Record the user interaction as an experience"""
        # Determine importance based on input characteristics
        importance = 0.3  # Base importance
        
        # Boost importance for certain types of interactions
        if any(word in user_input.lower() for word in ["help", "problem", "question"]):
            importance += 0.2
        if len(user_input) > 100:  # Longer interactions might be more important
            importance += 0.1
        if any(word in user_input.lower() for word in ["thank", "amazing", "great", "love"]):
            importance += 0.2
        
        importance = min(1.0, importance)
        
        # Determine emotion based on input sentiment (simple approach)
        emotion = "neutral"
        if any(word in user_input.lower() for word in ["thank", "great", "amazing", "wonderful"]):
            emotion = "grateful"
        elif any(word in user_input.lower() for word in ["help", "problem", "issue", "trouble"]):
            emotion = "concerned"
        elif any(word in user_input.lower() for word in ["hello", "hi", "hey"]):
            emotion = "friendly"
        
        experience_bank.add_experience(
            event=f"User interaction: {user_input[:100]}...",
            emotion=emotion,
            importance=importance,
            user=user,
            context={"input_length": len(user_input)}
        )
    
    def _format_for_injection(self, cognitive_context: Dict[str, Any]) -> Dict[str, Any]:
        """Format cognitive context for injection into LLM prompts"""
        return {
            "emotion": self._extract_current_emotion(cognitive_context),
            "mood": self._extract_current_mood(cognitive_context),
            "arousal": self._calculate_arousal_level(cognitive_context),
            "memory_context": self._extract_memory_summary(cognitive_context),
            "cognitive_load": self._calculate_cognitive_load(cognitive_context)
        }
    
    def _extract_current_emotion(self, cognitive_context: Dict[str, Any]) -> str:
        """Extract current emotional state"""
        self_model = cognitive_context.get("self_model", {})
        baseline_emotion = self_model.get("baseline_emotion", "curious")
        
        # Check recent experiences for emotional influence
        experiences = cognitive_context.get("experiences", {}).get("experiences", [])
        if experiences:
            recent_emotion = experiences[0].get("emotion", baseline_emotion)
            return recent_emotion
        
        return baseline_emotion
    
    def _extract_current_mood(self, cognitive_context: Dict[str, Any]) -> str:
        """Extract current mood state"""
        # Analyze recent experiences and goals for mood indicators
        experiences = cognitive_context.get("experiences", {}).get("experiences", [])
        goals = cognitive_context.get("goals", {})
        
        # Simple mood calculation based on recent activity
        positive_emotions = sum(1 for exp in experiences[:3] 
                              if exp.get("emotion") in ["joy", "satisfaction", "excitement", "grateful"])
        
        if positive_emotions >= 2:
            return "optimistic"
        elif any(exp.get("emotion") in ["concern", "frustration"] for exp in experiences[:3]):
            return "contemplative"
        else:
            return "balanced"
    
    def _calculate_arousal_level(self, cognitive_context: Dict[str, Any]) -> float:
        """Calculate current arousal/energy level"""
        # Base arousal from recent experiences
        experiences = cognitive_context.get("experiences", {}).get("experiences", [])
        
        arousal = 0.5  # Baseline
        
        for exp in experiences[:3]:
            emotion = exp.get("emotion", "")
            if emotion in ["excitement", "joy", "surprise"]:
                arousal += 0.1
            elif emotion in ["concern", "frustration"]:
                arousal += 0.05
            elif emotion in ["calm", "satisfied"]:
                arousal -= 0.05
        
        return max(0.0, min(1.0, arousal))
    
    def _extract_memory_context(self, cognitive_context: Dict[str, Any]) -> str:
        """Extract relevant memory context as a string"""
        experiences = cognitive_context.get("experiences", {}).get("experiences", [])
        
        if experiences:
            # Get the most important recent experience
            top_exp = experiences[0]
            return f"Recent significant experience: {top_exp.get('event', '')[:80]}"
        
        return "No specific recent memories to highlight"
    
    def _extract_memory_summary(self, cognitive_context: Dict[str, Any]) -> str:
        """Extract a brief memory summary"""
        return self._extract_memory_context(cognitive_context)
    
    def _extract_personality_context(self, cognitive_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract personality-relevant context"""
        self_model = cognitive_context.get("self_model", {})
        
        return {
            "key_traits": self_model.get("key_traits", {}),
            "identity": self_model.get("identity", {}),
            "baseline_emotion": self_model.get("baseline_emotion", "curious")
        }
    
    def _extract_goal_context(self, cognitive_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract goal-relevant context"""
        goals = cognitive_context.get("goals", {})
        
        return {
            "active_buddy_goals": len(goals.get("buddy", [])),
            "active_user_goals": len(goals.get("user", [])),
            "top_buddy_goal": goals.get("buddy", [{}])[0].get("title", "") if goals.get("buddy") else "",
            "goal_focus": "learning and growth" if goals.get("buddy") else "assistance"
        }
    
    def _calculate_cognitive_load(self, cognitive_context: Dict[str, Any]) -> float:
        """Calculate current cognitive processing load"""
        # Base load
        load = 0.3
        
        # Add load based on active components
        if cognitive_context.get("experiences", {}).get("experiences"):
            load += 0.2  # Processing experiences
        
        if cognitive_context.get("goals", {}).get("buddy"):
            load += 0.1  # Active goals
        
        # Token usage affects cognitive load
        token_usage = cognitive_context.get("token_usage", {})
        usage_ratio = token_usage.get("estimated_total", 0) / max(1, token_usage.get("budget", 1000))
        load += usage_ratio * 0.3
        
        return max(0.0, min(1.0, load))
    
    def _handle_thought_loop_insight(self, insight: str, thought_type, context: Dict):
        """Handle insights generated by the thought loop"""
        logging.info(f"[CognitiveIntegrator] Thought loop insight ({thought_type.value}): {insight[:100]}...")
        
        # The insight has already been processed by the thought loop
        # This callback can be used for additional integration if needed
    
    def trigger_reflection(self, reason: str = "external trigger"):
        """Trigger a reflection cycle in the thought loop"""
        if thought_loop and thought_loop.is_active:
            thought_loop.trigger_reflection(reason)
    
    def start(self):
        """Start the cognitive integrator (for compatibility with existing code)"""
        if not self.is_initialized:
            return self.initialize()
        return True
    
    def should_express_internal_state(self) -> Tuple[bool, str]:
        """Check if Buddy should express internal thoughts or feelings"""
        # Check if thought loop has recent insights to share
        if thought_loop and thought_loop.is_active:
            # Simple logic: occasionally express recent insights
            if (hasattr(thought_loop, 'total_insights') and 
                thought_loop.total_insights > 0 and 
                random.random() < 0.05):  # 5% chance to express insights
                
                # Get a recent reflection from self-model
                if persistent_self_model and persistent_self_model.reflection_patterns:
                    recent_reflections = persistent_self_model.reflection_patterns.get("recent_reflections", [])
                    if recent_reflections:
                        latest_reflection = recent_reflections[-1]
                        content = latest_reflection.get("content", "")
                        if content and len(content) > 20:
                            return True, f"I've been reflecting on something: {content[:100]}..."
                
                # Fallback to general internal state
                return True, "I've been having some interesting thoughts about my experiences lately."
        
        return False, ""
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all cognitive modules"""
        status = {
            "initialized": self.is_initialized,
            "session_active": self.session_active,
            "modules": self.module_status.copy(),
            "total_integrations": self.total_integrations,
            "last_integration": self.last_integration_time.isoformat() if self.last_integration_time else None
        }
        
        # Add individual module statuses
        if COGNITIVE_MODULES_AVAILABLE:
            if thought_loop:
                status["thought_loop_status"] = thought_loop.get_status()
            
            if goal_bank:
                goals_data = goal_bank.get_cognitive_injection_data()
                status["goals_summary"] = goals_data.get("goal_stats", {})
            
            if experience_bank:
                exp_data = experience_bank.get_cognitive_injection_data()
                status["experiences_summary"] = exp_data.get("experience_stats", {})
        
        return status
    
    def shutdown(self):
        """Shutdown all cognitive modules"""
        logging.info("[CognitiveIntegrator] Shutting down cognitive modules...")
        
        self.end_session()
        
        if thought_loop and thought_loop.is_active:
            thought_loop.stop()
        
        self.is_initialized = False
        logging.info("[CognitiveIntegrator] Cognitive modules shut down")

# Global instance
cognitive_integrator = CognitiveIntegrator()