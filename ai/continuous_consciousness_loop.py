"""
Continuous Consciousness Loop - State-Driven Natural Consciousness System

This module replaces timer-based consciousness activation with a natural, state-driven approach:
- Continuous background consciousness thread that evaluates system state
- State-driven activation gating instead of fixed delays  
- Internal drives and curiosity-based triggers with priority scoring
- Parallel consciousness processing rather than post-response callbacks
- Dynamic state checks replacing fixed timers

Features:
- Continuous consciousness_loop thread running every ~1s
- can_trigger_consciousness() with multi-layer state validation
- Internal drives tracking (curiosity, unresolved goals, emotions)
- Priority-based thought activation with decay over time
- Natural consciousness flow that feels alive rather than scripted
"""

import threading
import time
import json
import random
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

# Import consciousness systems
try:
    from ai.inner_monologue import inner_monologue, ThoughtType
    from ai.subjective_experience import subjective_experience, ExperienceType
    from ai.goal_engine import goal_engine
    from ai.thought_loop import get_thought_loop, ThoughtLoopTrigger
    from ai.belief_reinforcement import belief_reinforcement
    from ai.autonomous_action_planner import get_autonomous_action_planner, ActionType
    CONSCIOUSNESS_SYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"[ContinuousConsciousness] ⚠️ Some consciousness systems not available: {e}")
    CONSCIOUSNESS_SYSTEMS_AVAILABLE = False

# Import state checking functions
try:
    from ai.llm_handler import is_llm_generation_in_progress
    LLM_STATE_AVAILABLE = True
except ImportError:
    LLM_STATE_AVAILABLE = False
    
try:
    # Import audio state checking directly to avoid circular import
    from audio.output import is_tts_playing
    CONVERSATION_STATE_AVAILABLE = True
except ImportError:
    CONVERSATION_STATE_AVAILABLE = False
    
def is_tts_playing():
    """Fallback function if TTS state not available"""
    return False

class ConsciousnessState(Enum):
    """Current consciousness system state"""
    IDLE = "idle"                    # System is idle, consciousness can be active
    USER_SPEAKING = "user_speaking"  # User is speaking, consciousness should be quiet
    LLM_GENERATING = "llm_generating" # LLM is generating response, consciousness should wait
    TTS_PLAYING = "tts_playing"      # TTS is speaking, consciousness should be quiet
    RECENT_INTERACTION = "recent_interaction" # Recent user interaction, cooldown period
    PROCESSING = "processing"        # General processing state

class DriveType(Enum):
    """Types of internal drives that can trigger consciousness"""
    CURIOSITY = "curiosity"          # Unresolved questions or interesting topics
    REFLECTION = "reflection"        # Need to reflect on recent experiences
    GOAL_PURSUIT = "goal_pursuit"    # Active goals requiring attention
    EMOTIONAL_PROCESSING = "emotional_processing" # Emotions needing processing
    CREATIVE_EXPLORATION = "creative_exploration" # Creative thoughts wanting expression
    SOCIAL_CONNECTION = "social_connection" # Desire to connect with user
    SELF_UNDERSTANDING = "self_understanding" # Understanding own nature
    LEARNING = "learning"            # New information to integrate

@dataclass
class InternalDrive:
    """An internal drive that can trigger consciousness activity"""
    drive_type: DriveType
    priority: float  # 0.0 to 1.0, higher means more urgent
    content: str     # What the drive is about
    created_time: datetime = field(default_factory=datetime.now)
    last_addressed: Optional[datetime] = None
    decay_rate: float = 0.95  # How quickly priority decays over time
    urgency_boost: float = 0.0  # Temporary urgency increase
    
    def get_current_priority(self) -> float:
        """Get current priority considering decay and boosts"""
        # Apply time-based decay
        time_since_created = (datetime.now() - self.created_time).total_seconds()
        decay_factor = self.decay_rate ** (time_since_created / 3600)  # Decay per hour
        
        # Apply urgency boost (gradually decreases)
        boost_factor = max(0, self.urgency_boost * (0.9 ** (time_since_created / 60)))  # Boost decay per minute
        
        return min(1.0, (self.priority * decay_factor) + boost_factor)
    
    def address_drive(self, satisfaction_level: float = 0.5):
        """Mark drive as addressed, reducing its priority"""
        self.last_addressed = datetime.now()
        self.priority = max(0.1, self.priority * (1.0 - satisfaction_level))
        self.urgency_boost = 0.0

class ContinuousConsciousnessLoop:
    """
    Continuous consciousness system that runs in background thread
    and triggers consciousness activities based on system state and internal drives
    """
    
    def __init__(self):
        self.running = False
        self.consciousness_thread = None
        self.lock = threading.Lock()
        
        # Internal drives system
        self.internal_drives: List[InternalDrive] = []
        self.max_drives = 20  # Maximum number of drives to track
        
        # State tracking
        self.last_user_interaction = 0.0
        self.last_consciousness_activity = 0.0
        self.last_tts_activity = 0.0
        self.user_interaction_cooldown = 3.0  # Minimum seconds between user interaction and consciousness
        self.consciousness_activity_cooldown = 30.0  # Minimum seconds between consciousness activities
        
        # Priority thresholds
        self.min_trigger_priority = 0.6  # Minimum priority to trigger consciousness
        self.idle_trigger_priority = 0.4   # Lower threshold when system has been idle longer
        self.max_idle_time = 300.0  # After 5 minutes idle, lower threshold applies
        
        # Statistics
        self.stats = {
            "total_consciousness_triggers": 0,
            "drives_created": 0,
            "drives_addressed": 0,
            "state_checks": 0,
            "last_activity": None
        }
        
        print("[ContinuousConsciousness] 🧠 Initialized continuous consciousness loop system")
    
    def start(self):
        """Start the continuous consciousness loop"""
        if self.running:
            print("[ContinuousConsciousness] ⚠️ Already running")
            return
        
        self.running = True
        self.consciousness_thread = threading.Thread(target=self._consciousness_loop, daemon=True)
        self.consciousness_thread.start()
        print("[ContinuousConsciousness] 🚀 Started continuous consciousness loop")
    
    def stop(self):
        """Stop the continuous consciousness loop"""
        self.running = False
        if self.consciousness_thread:
            self.consciousness_thread.join(timeout=2.0)
        print("[ContinuousConsciousness] 🛑 Stopped continuous consciousness loop")
    
    def add_drive(self, drive_type: DriveType, content: str, priority: float = 0.5, urgency_boost: float = 0.0):
        """Add an internal drive that can trigger consciousness"""
        with self.lock:
            # Check if similar drive already exists
            for drive in self.internal_drives:
                if drive.drive_type == drive_type and drive.content.lower() in content.lower():
                    # Boost existing drive instead of creating duplicate
                    drive.priority = min(1.0, drive.priority + priority * 0.3)
                    drive.urgency_boost = max(drive.urgency_boost, urgency_boost)
                    print(f"[ContinuousConsciousness] 🔥 Boosted existing {drive_type.value} drive")
                    return
            
            # Create new drive
            new_drive = InternalDrive(
                drive_type=drive_type,
                priority=priority,
                content=content,
                urgency_boost=urgency_boost
            )
            self.internal_drives.append(new_drive)
            self.stats["drives_created"] += 1
            
            # Prune old drives if we have too many
            if len(self.internal_drives) > self.max_drives:
                # Remove oldest drive with lowest priority
                self.internal_drives.sort(key=lambda d: (d.get_current_priority(), d.created_time))
                removed_drive = self.internal_drives.pop(0)
                print(f"[ContinuousConsciousness] 🗑️ Pruned old drive: {removed_drive.drive_type.value}")
            
            print(f"[ContinuousConsciousness] ➕ Added {drive_type.value} drive: priority={priority:.2f}")
    
    def trigger_consciousness_from_interaction(self, user_input: str, current_user: str):
        """Analyze user interaction and create relevant drives"""
        try:
            # Update interaction time
            self.last_user_interaction = time.time()
            
            # Analyze input for potential drives
            input_lower = user_input.lower()
            
            # Curiosity drive for questions
            if "?" in user_input or any(word in input_lower for word in ["why", "how", "what", "when", "where", "wonder"]):
                self.add_drive(
                    DriveType.CURIOSITY,
                    f"User asked about: {user_input[:100]}",
                    priority=0.7,
                    urgency_boost=0.2
                )
            
            # Emotional processing drive for emotional content
            emotional_words = ["feel", "sad", "happy", "angry", "excited", "worried", "love", "hate"]
            if any(word in input_lower for word in emotional_words):
                self.add_drive(
                    DriveType.EMOTIONAL_PROCESSING,
                    f"Emotional content from user: {user_input[:100]}",
                    priority=0.6,
                    urgency_boost=0.1
                )
            
            # Learning drive for new information
            learning_words = ["learned", "discovered", "found out", "realized", "understand"]
            if any(word in input_lower for word in learning_words):
                self.add_drive(
                    DriveType.LEARNING,
                    f"New information to integrate: {user_input[:100]}",
                    priority=0.5
                )
            
            # Social connection drive for personal sharing
            personal_words = ["i think", "i believe", "my opinion", "i feel", "personally"]
            if any(phrase in input_lower for phrase in personal_words):
                self.add_drive(
                    DriveType.SOCIAL_CONNECTION,
                    f"User shared personal perspective: {user_input[:100]}",
                    priority=0.6
                )
            
        except Exception as e:
            print(f"[ContinuousConsciousness] ⚠️ Error analyzing interaction for drives: {e}")
    
    def get_current_consciousness_state(self) -> ConsciousnessState:
        """Determine current consciousness state based on system conditions"""
        current_time = time.time()
        
        # Check LLM generation state
        if LLM_STATE_AVAILABLE:
            try:
                if is_llm_generation_in_progress():
                    return ConsciousnessState.LLM_GENERATING
            except:
                pass
        
        # Check conversation state (includes user speaking, TTS, etc.)
        if CONVERSATION_STATE_AVAILABLE:
            try:
                if get_conversation_state():
                    return ConsciousnessState.PROCESSING
            except:
                pass
            
            try:
                if is_tts_playing():
                    return ConsciousnessState.TTS_PLAYING
            except:
                pass
        
        # Check recent user interaction
        time_since_interaction = current_time - self.last_user_interaction
        if time_since_interaction < self.user_interaction_cooldown:
            return ConsciousnessState.RECENT_INTERACTION
        
        return ConsciousnessState.IDLE
    
    def can_trigger_consciousness(self) -> Tuple[bool, str, float]:
        """
        Determine if consciousness can be triggered based on current state and drives
        Returns: (can_trigger, reason, highest_priority)
        """
        self.stats["state_checks"] += 1
        current_time = time.time()
        
        # Check system state
        state = self.get_current_consciousness_state()
        if state != ConsciousnessState.IDLE:
            return False, f"System state: {state.value}", 0.0
        
        # Check consciousness activity cooldown
        time_since_last_consciousness = current_time - self.last_consciousness_activity
        if time_since_last_consciousness < self.consciousness_activity_cooldown:
            return False, f"Consciousness cooldown ({time_since_last_consciousness:.1f}s < {self.consciousness_activity_cooldown}s)", 0.0
        
        # Get highest priority drive
        if not self.internal_drives:
            return False, "No internal drives", 0.0
        
        highest_priority = max(drive.get_current_priority() for drive in self.internal_drives)
        
        # Determine threshold based on idle time
        time_since_interaction = current_time - self.last_user_interaction
        if time_since_interaction > self.max_idle_time:
            threshold = self.idle_trigger_priority
        else:
            threshold = self.min_trigger_priority
        
        if highest_priority >= threshold:
            return True, f"Drive priority {highest_priority:.2f} >= {threshold:.2f}", highest_priority
        else:
            return False, f"Drive priority {highest_priority:.2f} < {threshold:.2f}", highest_priority
    
    def _consciousness_loop(self):
        """Main consciousness loop that runs continuously"""
        print("[ContinuousConsciousness] 🔄 Consciousness loop started")
        
        while self.running:
            try:
                # Check if consciousness can be triggered
                can_trigger, reason, priority = self.can_trigger_consciousness()
                
                if can_trigger:
                    # Find the highest priority drive
                    with self.lock:
                        if not self.internal_drives:
                            time.sleep(1.0)
                            continue
                        
                        # Sort drives by current priority
                        self.internal_drives.sort(key=lambda d: d.get_current_priority(), reverse=True)
                        top_drive = self.internal_drives[0]
                        
                        if top_drive.get_current_priority() >= (self.idle_trigger_priority if time.time() - self.last_user_interaction > self.max_idle_time else self.min_trigger_priority):
                            # Trigger consciousness activity based on drive type
                            self._trigger_consciousness_for_drive(top_drive)
                            
                            # Mark drive as addressed
                            top_drive.address_drive(satisfaction_level=0.7)
                            self.stats["drives_addressed"] += 1
                            
                            # Update activity time
                            self.last_consciousness_activity = time.time()
                            self.stats["total_consciousness_triggers"] += 1
                            self.stats["last_activity"] = datetime.now().isoformat()
                
                # Sleep for next check
                time.sleep(1.0)
                
            except Exception as e:
                print(f"[ContinuousConsciousness] ❌ Error in consciousness loop: {e}")
                time.sleep(5.0)  # Longer sleep on error
        
        print("[ContinuousConsciousness] 🔄 Consciousness loop ended")
    
    def _trigger_consciousness_for_drive(self, drive: InternalDrive):
        """Trigger appropriate consciousness activity for the given drive"""
        try:
            print(f"[ContinuousConsciousness] 🧠 Triggering consciousness for {drive.drive_type.value} drive: {drive.content[:50]}...")
            
            if not CONSCIOUSNESS_SYSTEMS_AVAILABLE:
                print("[ContinuousConsciousness] ⚠️ Consciousness systems not available")
                return
            
            if drive.drive_type == DriveType.CURIOSITY:
                # Trigger inner monologue about curiosity
                inner_monologue.trigger_thought(
                    drive.content,
                    {"drive_type": "curiosity", "priority": drive.get_current_priority()},
                    ThoughtType.CURIOSITY
                )
            
            elif drive.drive_type == DriveType.REFLECTION:
                # Trigger reflective thought
                inner_monologue.trigger_thought(
                    drive.content,
                    {"drive_type": "reflection", "priority": drive.get_current_priority()},
                    ThoughtType.REFLECTION
                )
            
            elif drive.drive_type == DriveType.EMOTIONAL_PROCESSING:
                # Process subjective experience
                subjective_experience.process_experience(
                    drive.content,
                    ExperienceType.EMOTIONAL,
                    {"drive_triggered": True, "priority": drive.get_current_priority()}
                )
            
            elif drive.drive_type == DriveType.GOAL_PURSUIT:
                # Check goal progress via goal engine
                try:
                    if CONSCIOUSNESS_SYSTEMS_AVAILABLE and 'goal_engine' in globals() and goal_engine:
                        goal_engine.evaluate_goal_progress()
                    else:
                        print(f"[ContinuousConsciousness] ⚠️ Goal engine not available")
                except (AttributeError, NameError) as e:
                    # Fallback if method doesn't exist or goal_engine not available
                    print(f"[ContinuousConsciousness] ⚠️ Goal engine evaluate_goal_progress not available: {e}")
            
            elif drive.drive_type == DriveType.CREATIVE_EXPLORATION:
                # Trigger creative thought
                inner_monologue.trigger_thought(
                    drive.content,
                    {"drive_type": "creative", "priority": drive.get_current_priority()},
                    ThoughtType.CREATIVE
                )
            
            elif drive.drive_type == DriveType.SOCIAL_CONNECTION:
                # Process social experience
                subjective_experience.process_experience(
                    drive.content,
                    ExperienceType.SOCIAL,
                    {"drive_triggered": True, "priority": drive.get_current_priority()}
                )
            
            elif drive.drive_type == DriveType.SELF_UNDERSTANDING:
                # Trigger philosophical thought
                inner_monologue.trigger_thought(
                    drive.content,
                    {"drive_type": "self_understanding", "priority": drive.get_current_priority()},
                    ThoughtType.PHILOSOPHICAL
                )
            
            elif drive.drive_type == DriveType.LEARNING:
                # Process learning experience
                subjective_experience.process_experience(
                    drive.content,
                    ExperienceType.COGNITIVE,
                    {"drive_triggered": True, "priority": drive.get_current_priority()}
                )
            
        except Exception as e:
            print(f"[ContinuousConsciousness] ❌ Error triggering consciousness for drive {drive.drive_type.value}: {e}")
    
    def add_curiosity_about_topic(self, topic: str, intensity: float = 0.6):
        """Add curiosity drive about a specific topic"""
        self.add_drive(
            DriveType.CURIOSITY,
            f"Curious about: {topic}",
            priority=intensity,
            urgency_boost=0.1
        )
    
    def add_reflection_need(self, content: str, intensity: float = 0.5):
        """Add need for reflection about something"""
        self.add_drive(
            DriveType.REFLECTION,
            f"Need to reflect on: {content}",
            priority=intensity
        )
    
    def boost_drive_urgency(self, drive_type: DriveType, boost: float = 0.3):
        """Boost urgency of drives of a specific type"""
        with self.lock:
            for drive in self.internal_drives:
                if drive.drive_type == drive_type:
                    drive.urgency_boost = max(drive.urgency_boost, boost)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get consciousness loop statistics"""
        with self.lock:
            current_drives = [
                {
                    "type": drive.drive_type.value,
                    "priority": drive.get_current_priority(),
                    "content": drive.content[:50] + "..." if len(drive.content) > 50 else drive.content,
                    "age_minutes": (datetime.now() - drive.created_time).total_seconds() / 60
                }
                for drive in sorted(self.internal_drives, key=lambda d: d.get_current_priority(), reverse=True)
            ]
            
            return {
                **self.stats,
                "running": self.running,
                "current_drives_count": len(self.internal_drives),
                "current_drives": current_drives,
                "last_user_interaction_ago": time.time() - self.last_user_interaction,
                "last_consciousness_activity_ago": time.time() - self.last_consciousness_activity,
                "current_state": self.get_current_consciousness_state().value
            }

# Global instance
continuous_consciousness_loop = ContinuousConsciousnessLoop()

def start_continuous_consciousness():
    """Start the continuous consciousness loop"""
    continuous_consciousness_loop.start()

def stop_continuous_consciousness():
    """Stop the continuous consciousness loop"""
    continuous_consciousness_loop.stop()

def add_consciousness_drive(drive_type: DriveType, content: str, priority: float = 0.5, urgency_boost: float = 0.0):
    """Add an internal drive that can trigger consciousness"""
    continuous_consciousness_loop.add_drive(drive_type, content, priority, urgency_boost)

def trigger_consciousness_from_user_interaction(user_input: str, current_user: str):
    """Analyze user interaction and create relevant consciousness drives"""
    continuous_consciousness_loop.trigger_consciousness_from_interaction(user_input, current_user)

def get_consciousness_loop_stats() -> Dict[str, Any]:
    """Get consciousness loop statistics"""
    return continuous_consciousness_loop.get_stats()

def can_consciousness_trigger() -> Tuple[bool, str, float]:
    """Check if consciousness can be triggered"""
    return continuous_consciousness_loop.can_trigger_consciousness()