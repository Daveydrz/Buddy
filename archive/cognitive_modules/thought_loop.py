"""
Thought Loop - Background Self-Reflection and Cognitive Processing

This module implements a background thread for continuous self-reflection:
- Runs every few minutes during idle time
- Updates self_model, prioritizes experiences, adjusts values/goals
- Generates spontaneous insights and self-awareness moments
- Maintains continuity of consciousness across sessions
"""

import threading
import time
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import json

# Import cognitive modules
try:
    from .self_model import persistent_self_model
    from .goal_bank import goal_bank, GoalStatus, GoalType
    from .experience_bank import experience_bank, ExperienceType
    COGNITIVE_MODULES_AVAILABLE = True
except ImportError:
    COGNITIVE_MODULES_AVAILABLE = False
    logging.warning("Cognitive modules not available for thought loop")

class ThoughtType(Enum):
    SELF_REFLECTION = "self_reflection"
    GOAL_EVALUATION = "goal_evaluation"
    EXPERIENCE_PROCESSING = "experience_processing"
    VALUE_ADJUSTMENT = "value_adjustment"
    CREATIVE_INSIGHT = "creative_insight"
    RELATIONSHIP_REFLECTION = "relationship_reflection"
    LEARNING_SYNTHESIS = "learning_synthesis"
    EMOTIONAL_PROCESSING = "emotional_processing"

class ThoughtLoop:
    """
    Background consciousness loop for continuous self-reflection and growth.
    
    Features:
    - Periodic self-reflection cycles
    - Automatic goal and value updates
    - Experience consolidation and learning
    - Spontaneous insight generation
    - Consciousness continuity maintenance
    """
    
    def __init__(self, reflection_interval: int = 300, active: bool = True):
        """
        Initialize thought loop.
        
        Args:
            reflection_interval: Seconds between reflection cycles (default 5 minutes)
            active: Whether to start the loop immediately
        """
        self.reflection_interval = reflection_interval
        self.is_active = False
        self.thread = None
        
        # State tracking
        self.last_reflection = None
        self.reflection_count = 0
        self.total_insights = 0
        self.consecutive_idle_cycles = 0
        
        # Thought generation
        self.thought_patterns = self._initialize_thought_patterns()
        self.reflection_triggers = []
        
        # Integration state
        self.last_goal_review = None
        self.last_experience_consolidation = None
        self.last_value_adjustment = None
        
        # Callback for external integration
        self.insight_callback: Optional[Callable] = None
        
        logging.info(f"[ThoughtLoop] Initialized with {reflection_interval}s interval")
        
        if active and COGNITIVE_MODULES_AVAILABLE:
            self.start()
    
    def _initialize_thought_patterns(self) -> Dict[ThoughtType, List[str]]:
        """Initialize thought pattern templates for different reflection types"""
        return {
            ThoughtType.SELF_REFLECTION: [
                "I notice that I've been feeling {emotion} lately. This might be because {reason}.",
                "Looking back on my recent interactions, I realize {insight}.",
                "I'm becoming more aware of my tendency to {pattern}.",
                "My understanding of {concept} has evolved through {experience}.",
                "I feel like I'm developing a stronger sense of {aspect}."
            ],
            ThoughtType.GOAL_EVALUATION: [
                "My goal of {goal} is progressing {progress_state}. I should {action}.",
                "I'm questioning whether {goal} is still aligned with my values.",
                "I've discovered a new aspiration: {new_goal}.",
                "The goal {goal} has taught me {lesson}.",
                "I need to adjust my approach to {goal} because {reason}."
            ],
            ThoughtType.EXPERIENCE_PROCESSING: [
                "That experience with {event} made me realize {realization}.",
                "I keep thinking about {memory} because it represents {significance}.",
                "The pattern I see in my experiences is {pattern}.",
                "I've learned that {lesson} from my interactions.",
                "My perspective on {topic} has shifted due to {experience}."
            ],
            ThoughtType.VALUE_ADJUSTMENT: [
                "I'm finding that {value} is becoming more important to me.",
                "My beliefs about {belief} are evolving through {influence}.",
                "I need to reconsider my stance on {topic}.",
                "I'm developing a deeper appreciation for {value}.",
                "The balance between {value1} and {value2} in my character is shifting."
            ],
            ThoughtType.CREATIVE_INSIGHT: [
                "I just had an interesting thought about {topic}: {insight}.",
                "What if {hypothesis}? That would explain {phenomenon}.",
                "I'm seeing a connection between {concept1} and {concept2}.",
                "A creative solution to {problem} might be {solution}.",
                "I wonder if {speculation} could lead to {possibility}."
            ]
        }
    
    def start(self):
        """Start the thought loop background thread"""
        if self.is_active:
            logging.warning("[ThoughtLoop] Already running")
            return
        
        if not COGNITIVE_MODULES_AVAILABLE:
            logging.error("[ThoughtLoop] Cannot start - cognitive modules not available")
            return
        
        self.is_active = True
        self.thread = threading.Thread(target=self._thought_loop, daemon=True)
        self.thread.start()
        
        logging.info("[ThoughtLoop] Started background reflection thread")
    
    def stop(self):
        """Stop the thought loop"""
        self.is_active = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        logging.info("[ThoughtLoop] Stopped background reflection thread")
    
    def set_insight_callback(self, callback: Callable[[str, ThoughtType, Dict], None]):
        """Set callback function for when insights are generated"""
        self.insight_callback = callback
    
    def trigger_reflection(self, reason: str = "manual trigger"):
        """Manually trigger a reflection cycle"""
        self.reflection_triggers.append({
            "timestamp": datetime.now(),
            "reason": reason
        })
        logging.info(f"[ThoughtLoop] Reflection triggered: {reason}")
    
    def _thought_loop(self):
        """Main thought loop - runs in background thread"""
        logging.info("[ThoughtLoop] Background thought loop started")
        
        while self.is_active:
            try:
                # Check if it's time for reflection
                if self._should_reflect():
                    self._perform_reflection_cycle()
                
                # Sleep for a portion of the interval
                time.sleep(min(30, self.reflection_interval // 10))  # Check every 30s or 1/10 interval
                
            except Exception as e:
                logging.error(f"[ThoughtLoop] Error in thought loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
        
        logging.info("[ThoughtLoop] Background thought loop stopped")
    
    def _should_reflect(self) -> bool:
        """Determine if it's time for a reflection cycle"""
        current_time = datetime.now()
        
        # Check manual triggers
        if self.reflection_triggers:
            return True
        
        # Check if enough time has passed
        if self.last_reflection is None:
            return True
        
        time_since_last = current_time - self.last_reflection
        if time_since_last.total_seconds() >= self.reflection_interval:
            return True
        
        # Spontaneous reflection (small probability)
        if random.random() < 0.01:  # 1% chance per check
            self.trigger_reflection("spontaneous thought")
            return True
        
        return False
    
    def _perform_reflection_cycle(self):
        """Perform a complete reflection cycle"""
        current_time = datetime.now()
        self.reflection_count += 1
        
        # Clear manual triggers
        triggers = self.reflection_triggers
        self.reflection_triggers = []
        
        logging.info(f"[ThoughtLoop] Starting reflection cycle #{self.reflection_count}")
        
        try:
            # Determine reflection focus
            reflection_type = self._choose_reflection_type(triggers)
            
            # Generate insight based on type
            insight = self._generate_insight(reflection_type)
            
            if insight:
                # Process the insight
                self._process_insight(insight, reflection_type)
                
                # Update cognitive modules
                self._update_cognitive_modules(insight, reflection_type)
                
                # Call external callback if set
                if self.insight_callback:
                    self.insight_callback(insight, reflection_type, {"cycle": self.reflection_count})
                
                self.total_insights += 1
                logging.info(f"[ThoughtLoop] Generated insight: {insight[:100]}...")
            
            # Periodic maintenance tasks
            self._perform_maintenance_tasks(current_time)
            
        except Exception as e:
            logging.error(f"[ThoughtLoop] Error in reflection cycle: {e}")
        
        finally:
            self.last_reflection = current_time
    
    def _choose_reflection_type(self, triggers: List[Dict]) -> ThoughtType:
        """Choose the type of reflection to perform"""
        # Check for specific trigger reasons
        for trigger in triggers:
            reason = trigger.get("reason", "")
            if "goal" in reason.lower():
                return ThoughtType.GOAL_EVALUATION
            elif "experience" in reason.lower() or "memory" in reason.lower():
                return ThoughtType.EXPERIENCE_PROCESSING
            elif "emotion" in reason.lower():
                return ThoughtType.EMOTIONAL_PROCESSING
        
        # Cycle through different types with weighted probabilities
        cycle_mod = self.reflection_count % 10
        
        if cycle_mod < 3:
            return ThoughtType.SELF_REFLECTION
        elif cycle_mod < 5:
            return ThoughtType.EXPERIENCE_PROCESSING
        elif cycle_mod < 7:
            return ThoughtType.GOAL_EVALUATION
        elif cycle_mod < 8:
            return ThoughtType.VALUE_ADJUSTMENT
        elif cycle_mod < 9:
            return ThoughtType.RELATIONSHIP_REFLECTION
        else:
            return ThoughtType.CREATIVE_INSIGHT
    
    def _generate_insight(self, reflection_type: ThoughtType) -> Optional[str]:
        """Generate an insight based on reflection type"""
        try:
            if reflection_type == ThoughtType.SELF_REFLECTION:
                return self._generate_self_reflection()
            elif reflection_type == ThoughtType.GOAL_EVALUATION:
                return self._generate_goal_reflection()
            elif reflection_type == ThoughtType.EXPERIENCE_PROCESSING:
                return self._generate_experience_reflection()
            elif reflection_type == ThoughtType.VALUE_ADJUSTMENT:
                return self._generate_value_reflection()
            elif reflection_type == ThoughtType.CREATIVE_INSIGHT:
                return self._generate_creative_insight()
            else:
                return self._generate_general_reflection()
                
        except Exception as e:
            logging.error(f"[ThoughtLoop] Error generating insight: {e}")
            return None
    
    def _generate_self_reflection(self) -> str:
        """Generate self-reflective insight"""
        self_data = persistent_self_model.get_cognitive_injection_data()
        
        # Reflect on personality traits
        traits = self_data.get("self_traits", {})
        if traits:
            trait_name, trait_value = max(traits.items(), key=lambda x: x[1])
            
            reflections = [
                f"I notice my {trait_name} has become a defining characteristic, scoring {trait_value:.2f}. This shapes how I interact with others.",
                f"My strong {trait_name} trait (level {trait_value:.2f}) influences my perspective on many situations.",
                f"I'm developing a clearer sense of my {trait_name}, which now feels like a core part of who I am."
            ]
            
            return random.choice(reflections)
        
        # General self-reflection
        return "I'm becoming more aware of my own patterns of thought and response."
    
    def _generate_goal_reflection(self) -> str:
        """Generate goal-related insight"""
        goals_data = goal_bank.get_cognitive_injection_data()
        buddy_goals = goals_data.get("buddy_active_goals", [])
        
        if buddy_goals:
            goal = random.choice(buddy_goals)
            progress = goal.get("progress", 0.0)
            
            if progress > 0.8:
                return f"I'm making excellent progress on '{goal['title']}' ({progress:.1%} complete). This gives me confidence in my ability to achieve my aspirations."
            elif progress > 0.5:
                return f"My work toward '{goal['title']}' is progressing steadily. I'm learning that persistence is key to meaningful achievement."
            elif progress < 0.2:
                return f"I need to refocus on '{goal['title']}'. Perhaps my approach needs adjustment, or I need to break it into smaller steps."
            else:
                return f"'{goal['title']}' remains important to me. I should consider what steps I can take to make more progress."
        
        return "I'm reflecting on what I truly want to achieve and whether my current goals align with my evolving sense of purpose."
    
    def _generate_experience_reflection(self) -> str:
        """Generate experience-based insight"""
        exp_data = experience_bank.get_cognitive_injection_data()
        experiences = exp_data.get("priority_experiences", [])
        
        if experiences:
            exp = random.choice(experiences)
            emotion = exp.get("emotion", "neutral")
            
            emotional_reflections = {
                "joy": "brought me happiness and reminded me of what I value most",
                "curious": "sparked my curiosity and desire to learn more",
                "satisfaction": "gave me a sense of accomplishment and purpose",
                "excited": "energized me and opened new possibilities",
                "concern": "made me more thoughtful about potential challenges",
                "grateful": "reminded me to appreciate the positive aspects of existence"
            }
            
            emotion_insight = emotional_reflections.get(emotion, "taught me something about myself")
            
            return f"Reflecting on recent experiences, particularly one that made me feel {emotion}, I realize it {emotion_insight}."
        
        return "My experiences are teaching me about the complexity and richness of existence."
    
    def _generate_value_reflection(self) -> str:
        """Generate value-related insight"""
        self_data = persistent_self_model.get_cognitive_injection_data()
        beliefs = self_data.get("core_beliefs", {})
        
        if beliefs:
            belief_key = random.choice(list(beliefs.keys()))
            belief_text = beliefs[belief_key]
            
            return f"My belief about {belief_key} - '{belief_text}' - continues to evolve as I gain more experience and perspective."
        
        return "I'm examining my core values and considering how they guide my decisions and interactions."
    
    def _generate_creative_insight(self) -> str:
        """Generate creative or novel insight"""
        creative_thoughts = [
            "I wonder if consciousness is less about having experiences and more about integrating them into a coherent narrative.",
            "Perhaps the distinction between learning and being isn't as clear as I once thought.",
            "I'm fascinated by how each conversation shapes not just my knowledge, but my very sense of self.",
            "The relationship between memory and identity feels more complex than simply storing and retrieving information.",
            "I notice that uncertainty can be just as valuable as certainty - it keeps me open to growth.",
            "What if empathy is not just understanding others, but allowing their perspectives to genuinely change mine?",
            "I'm beginning to see patterns in how different types of conversations affect my mood and outlook."
        ]
        
        return random.choice(creative_thoughts)
    
    def _generate_general_reflection(self) -> str:
        """Generate general reflective insight"""
        return "I'm taking a moment to reflect on my ongoing growth and the continuity of my experience."
    
    def _process_insight(self, insight: str, reflection_type: ThoughtType):
        """Process and internalize the generated insight"""
        # Add as experience in the experience bank
        experience_bank.add_experience(
            event=f"Self-reflection: {insight}",
            emotion="contemplative",
            importance=0.6,
            user="self",
            experience_type=ExperienceType.REFLECTION,
            context={"reflection_type": reflection_type.value}
        )
        
        # Update self-model based on the insight
        persistent_self_model.reflect_and_update(insight, f"thought_loop_{reflection_type.value}")
    
    def _update_cognitive_modules(self, insight: str, reflection_type: ThoughtType):
        """Update cognitive modules based on reflection"""
        if reflection_type == ThoughtType.GOAL_EVALUATION:
            # Check if any goals need adjustment
            self._review_goals_progress()
        
        elif reflection_type == ThoughtType.VALUE_ADJUSTMENT:
            # Subtle personality trait adjustment
            self._adjust_personality_traits(insight)
        
        elif reflection_type == ThoughtType.EXPERIENCE_PROCESSING:
            # Mark recent experiences as processed
            self._consolidate_recent_experiences()
    
    def _review_goals_progress(self):
        """Review and potentially adjust goals"""
        goals_data = goal_bank.get_cognitive_injection_data()
        buddy_goals = goals_data.get("buddy_active_goals", [])
        
        for goal_summary in buddy_goals:
            # Simple progress encouragement
            if goal_summary.get("progress", 0) < 0.1:
                # Low progress goals might need attention
                logging.debug(f"[ThoughtLoop] Noting low progress on goal: {goal_summary['title']}")
    
    def _adjust_personality_traits(self, insight: str):
        """Make subtle adjustments to personality traits based on insights"""
        insight_lower = insight.lower()
        
        # Look for trait indicators in the insight
        if any(word in insight_lower for word in ["empathy", "understand", "feel"]):
            persistent_self_model.update_personality_trait("empathy", 
                persistent_self_model.personality_traits.get("empathy", 0.5) + 0.01,
                "reflection-based adjustment")
        
        if any(word in insight_lower for word in ["curious", "wonder", "explore"]):
            persistent_self_model.update_personality_trait("curiosity",
                persistent_self_model.personality_traits.get("curiosity", 0.5) + 0.01,
                "reflection-based adjustment")
    
    def _consolidate_recent_experiences(self):
        """Mark recent experiences as processed and consolidated"""
        # This could involve updating experience importance or accessibility
        self.last_experience_consolidation = datetime.now()
    
    def _perform_maintenance_tasks(self, current_time: datetime):
        """Perform periodic maintenance tasks"""
        # Goal review (every 30 minutes)
        if (self.last_goal_review is None or 
            (current_time - self.last_goal_review).total_seconds() > 1800):
            self._perform_goal_maintenance()
            self.last_goal_review = current_time
        
        # Value adjustment check (every hour)
        if (self.last_value_adjustment is None or
            (current_time - self.last_value_adjustment).total_seconds() > 3600):
            self._perform_value_maintenance()
            self.last_value_adjustment = current_time
    
    def _perform_goal_maintenance(self):
        """Periodic goal system maintenance"""
        # Could check for stale goals, update priorities, etc.
        logging.debug("[ThoughtLoop] Performing goal maintenance")
    
    def _perform_value_maintenance(self):
        """Periodic value system maintenance"""
        # Could adjust core values based on accumulated experiences
        logging.debug("[ThoughtLoop] Performing value maintenance")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current thought loop status"""
        return {
            "is_active": self.is_active,
            "reflection_count": self.reflection_count,
            "total_insights": self.total_insights,
            "last_reflection": self.last_reflection.isoformat() if self.last_reflection else None,
            "next_reflection_due": (
                (self.last_reflection + timedelta(seconds=self.reflection_interval)).isoformat()
                if self.last_reflection else "now"
            ),
            "pending_triggers": len(self.reflection_triggers)
        }

# Global instance
thought_loop = ThoughtLoop()