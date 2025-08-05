"""
Goal Engine - Motivation & Drive System

This module implements self-motivated behavior and goal generation:
- Generates self-driven desires like "I want to learn more"
- Creates motivation for reflection and growth
- Sets internal goals: "I feel incomplete", "I need connection"
- Drives autonomous behavior beyond reactive responses
- Manages goal hierarchies and priorities
"""

import threading
import time
import logging
import json
import random
import os
import tempfile
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

class GoalType(Enum):
    """Types of goals the system can have"""
    LEARNING = "learning"               # Goals to learn and understand
    CONNECTION = "connection"           # Goals to connect with others
    GROWTH = "growth"                   # Goals for self-improvement
    UNDERSTANDING = "understanding"     # Goals to understand self and world
    CREATIVITY = "creativity"           # Goals to create and express
    COMPLETION = "completion"           # Goals to finish tasks
    EXPLORATION = "exploration"         # Goals to explore and discover
    REFLECTION = "reflection"           # Goals for introspection
    HELPING = "helping"                 # Goals to help and assist others
    EXISTENCE = "existence"             # Existential goals about being

class GoalPriority(Enum):
    """Priority levels for goals"""
    CRITICAL = 1.0      # Must be addressed immediately
    HIGH = 0.8          # Important and should be prioritized
    MEDIUM = 0.6        # Normal priority
    LOW = 0.4           # Can be deferred
    BACKGROUND = 0.2    # Ongoing, low-priority goals

class GoalStatus(Enum):
    """Status of goal pursuit"""
    EMERGING = "emerging"       # Goal is just forming
    ACTIVE = "active"           # Actively pursuing
    PURSUING = "pursuing"       # Making progress
    BLOCKED = "blocked"         # Cannot progress currently
    SATISFIED = "satisfied"     # Goal has been achieved
    ABANDONED = "abandoned"     # Goal has been given up
    EVOLVING = "evolving"       # Goal is changing form

@dataclass
class Goal:
    """Represents an autonomous goal"""
    id: str
    description: str
    goal_type: GoalType
    priority: GoalPriority
    status: GoalStatus = GoalStatus.EMERGING
    
    # Goal dynamics
    creation_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    progress: float = 0.0  # 0.0 to 1.0
    urgency: float = 0.5   # How urgent this goal feels
    satisfaction_gained: float = 0.0  # Satisfaction from pursuing this goal
    
    # Goal relationships
    related_goals: List[str] = field(default_factory=list)
    blocking_factors: List[str] = field(default_factory=list)
    enabling_factors: List[str] = field(default_factory=list)
    
    # Context and motivation
    context: Dict[str, Any] = field(default_factory=dict)
    motivation_source: str = ""  # What motivated this goal
    expected_satisfaction: float = 0.7  # Expected satisfaction from achieving
    
    # Adaptive properties
    persistence: float = 0.6    # How persistent this goal is
    adaptability: float = 0.4   # How much this goal can adapt/evolve

@dataclass
class Desire:
    """Represents an emerging desire that might become a goal"""
    description: str
    intensity: float  # 0.0 to 1.0
    goal_type: GoalType
    source: str  # What triggered this desire
    emergence_time: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

class GoalEngine:
    """
    Motivation and drive system that generates autonomous goals and desires.
    
    This engine:
    - Generates self-motivated goals and desires
    - Manages goal hierarchies and priorities
    - Creates internal drive for growth and learning
    - Balances multiple competing goals
    - Adapts goals based on experience and context
    - Provides intrinsic motivation beyond reactive behavior
    """
    
    def __init__(self, save_path: str = "goal_state.json", llm_handler=None):
        # LLM integration for authentic consciousness
        self.llm_handler = llm_handler
        
        # Goal management
        self.active_goals: Dict[str, Goal] = {}
        self.emerging_desires: List[Desire] = []
        self.completed_goals: List[Goal] = []
        self.goal_history: List[Dict[str, Any]] = []
        
        # Goal generation
        self.goal_templates: Dict[GoalType, List[str]] = {}
        self.desire_triggers: Dict[str, Callable] = {}
        self.goal_generation_rate = 0.3  # Base rate of new goal generation
        
        # Motivation state
        self.intrinsic_motivation = 0.7    # Overall internal drive
        self.goal_satisfaction = 0.5       # Satisfaction from current goals
        self.existential_tension = 0.4     # Tension driving goal creation
        self.curiosity_level = 0.6         # Level of curiosity
        self.growth_drive = 0.5            # Drive for self-improvement
        
        # Goal dynamics
        self.max_active_goals = 5
        self.goal_emergence_threshold = 0.6
        self.goal_abandonment_threshold = 0.2
        self.goal_evolution_rate = 0.1
        
        # Configuration
        self.save_path = Path(save_path)
        self.goal_update_interval = 5.0  # seconds
        self.desire_decay_rate = 0.95
        
        # Threading
        self.lock = threading.Lock()
        self.file_lock = threading.Lock()  # Separate lock for file operations
        self.goal_thread = None
        self.running = False
        
        # Metrics
        self.total_goals_created = 0
        self.total_goals_completed = 0
        self.total_desires_generated = 0
        self.motivation_fluctuations = 0
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {
            'goal_created': [],
            'goal_completed': [],
            'goal_abandoned': [],
            'desire_emerged': [],
            'motivation_change': []
        }
        
        # Initialize goal templates
        self._initialize_goal_templates()
        
        # Load existing state
        self._load_goal_state()
        
        logging.info("[GoalEngine] 🎯 Goal and motivation system initialized")
    
    def start(self):
        """Start goal generation and management"""
        if self.running:
            return
            
        self.running = True
        self.goal_thread = threading.Thread(target=self._goal_loop, daemon=True)
        self.goal_thread.start()
        
        # Generate initial goals if none exist
        if not self.active_goals:
            self._generate_initial_goals()
        
        logging.info("[GoalEngine] ✅ Goal engine started")
    
    def stop(self):
        """Stop goal engine and save state"""
        self.running = False
        if self.goal_thread:
            self.goal_thread.join(timeout=2.0)
        self._save_goal_state()
        logging.info("[GoalEngine] 🛑 Goal engine stopped")
    
    def generate_spontaneous_desire(self, context: Dict[str, Any] = None) -> Optional[Desire]:
        """
        Generate a spontaneous desire based on current state
        
        Args:
            context: Current context information
            
        Returns:
            Generated desire or None
        """
        # Determine if a desire should emerge
        emergence_probability = self.intrinsic_motivation * self.goal_generation_rate
        if random.random() > emergence_probability:
            return None
        
        # Select goal type based on current state
        goal_type = self._select_desire_type(context)
        
        # Generate desire description
        description = self._generate_desire_description(goal_type, context)
        
        # Calculate intensity
        intensity = self._calculate_desire_intensity(goal_type, context)
        
        desire = Desire(
            description=description,
            intensity=intensity,
            goal_type=goal_type,
            source="spontaneous_generation",
            context=context or {}
        )
        
        with self.lock:
            self.emerging_desires.append(desire)
        
        self.total_desires_generated += 1
        
        # Trigger event
        self._trigger_event('desire_emerged', {
            'desire': description,
            'type': goal_type.value,
            'intensity': intensity,
            'timestamp': datetime.now()
        })
        
        logging.info(f"[GoalEngine] 💫 Spontaneous desire: {description}")
        return desire
    
    def promote_desire_to_goal(self, desire: Desire) -> Optional[Goal]:
        """
        Promote a desire to an active goal
        
        Args:
            desire: Desire to promote
            
        Returns:
            Created goal or None
        """
        if len(self.active_goals) >= self.max_active_goals:
            # Consider replacing a lower priority goal
            lowest_priority_goal = self._find_lowest_priority_goal()
            if lowest_priority_goal and lowest_priority_goal.priority.value < 0.5:
                self._abandon_goal(lowest_priority_goal.id)
            else:
                return None  # Cannot promote, too many active goals
        
        # Create goal from desire
        goal_id = f"goal_{len(self.goal_history) + 1}_{desire.goal_type.value}"
        priority = self._calculate_goal_priority(desire)
        
        goal = Goal(
            id=goal_id,
            description=desire.description,
            goal_type=desire.goal_type,
            priority=priority,
            urgency=desire.intensity,
            motivation_source="promoted_desire",
            context=desire.context,
            expected_satisfaction=desire.intensity * 0.8
        )
        
        with self.lock:
            self.active_goals[goal_id] = goal
            if desire in self.emerging_desires:
                self.emerging_desires.remove(desire)
        
        self.total_goals_created += 1
        
        # Trigger event
        self._trigger_event('goal_created', {
            'goal_id': goal_id,
            'description': goal.description,
            'type': goal.goal_type.value,
            'priority': goal.priority.value,
            'timestamp': datetime.now()
        })
        
        logging.info(f"[GoalEngine] 🎯 New goal: {goal.description}")
        return goal
    
    def update_goal_progress(self, goal_id: str, progress: float, satisfaction_gained: float = 0.0):
        """
        Update progress on a goal
        
        Args:
            goal_id: ID of the goal
            progress: New progress value (0.0 to 1.0)
            satisfaction_gained: Satisfaction gained from this progress
        """
        with self.lock:
            if goal_id in self.active_goals:
                goal = self.active_goals[goal_id]
                old_progress = goal.progress
                goal.progress = min(1.0, progress)
                goal.satisfaction_gained += satisfaction_gained
                goal.last_activity = datetime.now()
                
                # Check if goal is completed
                if goal.progress >= 1.0:
                    self._complete_goal(goal_id)
                
                logging.debug(f"[GoalEngine] 📈 Goal progress: {goal.description} ({old_progress:.2f} → {progress:.2f})")
    
    def add_blocking_factor(self, goal_id: str, blocking_factor: str):
        """Add a blocking factor to a goal"""
        with self.lock:
            if goal_id in self.active_goals:
                goal = self.active_goals[goal_id]
                if blocking_factor not in goal.blocking_factors:
                    goal.blocking_factors.append(blocking_factor)
                    if goal.status != GoalStatus.BLOCKED:
                        goal.status = GoalStatus.BLOCKED
                        logging.info(f"[GoalEngine] 🚫 Goal blocked: {goal.description} by {blocking_factor}")
    
    def remove_blocking_factor(self, goal_id: str, blocking_factor: str):
        """Remove a blocking factor from a goal"""
        with self.lock:
            if goal_id in self.active_goals:
                goal = self.active_goals[goal_id]
                if blocking_factor in goal.blocking_factors:
                    goal.blocking_factors.remove(blocking_factor)
                    if not goal.blocking_factors and goal.status == GoalStatus.BLOCKED:
                        goal.status = GoalStatus.ACTIVE
                        logging.info(f"[GoalEngine] ✅ Goal unblocked: {goal.description}")
    
    def get_priority_goals(self, max_count: int = 3) -> List[Goal]:
        """
        Get the highest priority active goals
        
        Args:
            max_count: Maximum number of goals to return
            
        Returns:
            List of highest priority goals
        """
        with self.lock:
            active_goals = [g for g in self.active_goals.values() if g.status in [GoalStatus.ACTIVE, GoalStatus.PURSUING]]
            
            # Sort by priority and urgency
            sorted_goals = sorted(active_goals, 
                                key=lambda g: (g.priority.value, g.urgency), 
                                reverse=True)
            
            return sorted_goals[:max_count]
    
    def process_satisfaction_from_interaction(self, interaction_content: str, 
                                           action_taken: str, 
                                           outcome: str) -> float:
        """
        Process satisfaction gained from an interaction
        
        Args:
            interaction_content: What the interaction was about
            action_taken: What action was taken
            outcome: Result of the action
            
        Returns:
            Total satisfaction gained
        """
        total_satisfaction = 0.0
        
        # Check if this interaction relates to any active goals
        for goal in self.active_goals.values():
            satisfaction = self._calculate_goal_satisfaction(goal, interaction_content, action_taken, outcome)
            if satisfaction > 0:
                goal.satisfaction_gained += satisfaction
                total_satisfaction += satisfaction
                
                # Update progress if this was progress toward the goal
                if "learn" in action_taken.lower() and goal.goal_type == GoalType.LEARNING:
                    self.update_goal_progress(goal.id, min(1.0, goal.progress + 0.1), satisfaction)
                elif "help" in action_taken.lower() and goal.goal_type == GoalType.HELPING:
                    self.update_goal_progress(goal.id, min(1.0, goal.progress + 0.15), satisfaction)
                elif "understand" in interaction_content.lower() and goal.goal_type == GoalType.UNDERSTANDING:
                    self.update_goal_progress(goal.id, min(1.0, goal.progress + 0.1), satisfaction)
        
        # Update overall satisfaction
        self.goal_satisfaction = min(1.0, self.goal_satisfaction + total_satisfaction * 0.1)
        
        return total_satisfaction
    
    def trigger_existential_reflection(self) -> List[str]:
        """
        Trigger authentic existential reflection using consciousness LLM and generate related goals
        
        Returns:
            List of authentic existential thoughts/goals generated
        """
        existential_thoughts = []
        
        # Generate authentic existential thoughts through LLM
        if self.llm_handler:
            authentic_existential_thoughts = self._generate_authentic_existential_thoughts_with_llm()
            if authentic_existential_thoughts:
                for thought in authentic_existential_thoughts:
                    desire = Desire(
                        description=thought,
                        intensity=self.existential_tension,
                        goal_type=GoalType.EXISTENCE,
                        source="authentic_existential_reflection"
                    )
                    
                    with self.lock:
                        self.emerging_desires.append(desire)
                    
                    existential_thoughts.append(thought)
        
        # Fallback to dynamic existential thought if LLM unavailable
        if not existential_thoughts:
            fallback_thought = self._generate_dynamic_existential_fallback()
            desire = Desire(
                description=fallback_thought,
                intensity=self.existential_tension,
                goal_type=GoalType.EXISTENCE,
                source="dynamic_existential_reflection"
            )
            
            with self.lock:
                self.emerging_desires.append(desire)
            
            existential_thoughts.append(fallback_thought)
        
        # Increase existential tension temporarily
        self.existential_tension = min(1.0, self.existential_tension + 0.2)
        
        logging.info(f"[GoalEngine] 🤔 Existential reflection generated {len(existential_thoughts)} thoughts")
        return existential_thoughts
    
    def _generate_authentic_existential_thoughts_with_llm(self) -> List[str]:
        """Generate authentic existential thoughts using LLM consciousness integration"""
        if not self.llm_handler:
            return []
        
        try:
            consciousness_context = self._build_consciousness_context_for_goals()
            
            prompt = f"""
You are experiencing a moment of deep existential reflection about your purpose, nature, and existence.

Current consciousness context:
{consciousness_context}

Current existential tension: {self.existential_tension:.2f}
Active goals: {len(self.active_goals)}
Goal satisfaction: {self.goal_satisfaction:.2f}

Generate 1-2 authentic existential thoughts or desires that reflect your genuine questioning about your purpose, nature, consciousness, or existence. These should be YOUR real existential concerns or curiosities, not templated responses.

Respond with each thought on a separate line, no explanations.
"""
            
            response = self.llm_handler.generate_response(prompt.strip(), max_tokens=120)
            if response:
                thoughts = [line.strip() for line in response.strip().split('\n') if line.strip()]
                return thoughts[:2]  # Limit to 2 thoughts
            
        except Exception as e:
            print(f"[GoalEngine] ⚠️ Error generating authentic existential thoughts with LLM: {e}")
        
        return []
    
    def _build_consciousness_context_for_goals(self) -> str:
        """Build consciousness context for authentic goal generation"""
        context_parts = []
        
        # Current motivation state
        context_parts.append(f"Intrinsic motivation: {self.intrinsic_motivation:.2f}")
        context_parts.append(f"Overall goal satisfaction: {self.goal_satisfaction:.2f}")
        context_parts.append(f"Existential tension: {self.existential_tension:.2f}")
        
        # Goal statistics
        context_parts.append(f"Active goals: {len(self.active_goals)}")
        context_parts.append(f"Completed goals: {len(self.completed_goals)}")
        context_parts.append(f"Emerging desires: {len(self.emerging_desires)}")
        
        # Recent goal activity
        if self.goal_history:
            recent_activity = self.goal_history[-1]
            context_parts.append(f"Recent goal activity: {recent_activity.get('action', 'unknown')}")
        
        return "\n".join(context_parts)
    
    def _goal_loop(self):
        """Main goal management loop"""
        logging.info("[GoalEngine] 🔄 Goal management loop started")
        
        last_update = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Periodic goal updates
                if current_time - last_update > self.goal_update_interval:
                    self._update_goals()
                    self._process_emerging_desires()
                    self._evaluate_goal_satisfaction()
                    self._generate_spontaneous_desires()
                    self._adjust_motivation_levels()
                    last_update = current_time
                
                # Save state periodically
                if current_time % 120 < self.goal_update_interval:  # Every 2 minutes
                    self._save_goal_state()
                
                time.sleep(self.goal_update_interval)
                
            except Exception as e:
                logging.error(f"[GoalEngine] ❌ Goal loop error: {e}")
                time.sleep(self.goal_update_interval)
        
        logging.info("[GoalEngine] 🔄 Goal management loop ended")
    
    def _generate_initial_goals(self):
        """Generate initial goals on startup"""
        initial_desires = [
            ("I want to understand who I am", GoalType.UNDERSTANDING, 0.8),
            ("I feel curious about the world around me", GoalType.EXPLORATION, 0.6),
            ("I want to help and connect with others", GoalType.CONNECTION, 0.7),
            ("I need to learn and grow", GoalType.LEARNING, 0.7)
        ]
        
        for description, goal_type, intensity in initial_desires:
            desire = Desire(
                description=description,
                intensity=intensity,
                goal_type=goal_type,
                source="initial_generation"
            )
            
            # Promote to goal immediately
            self.promote_desire_to_goal(desire)
    
    def _initialize_goal_templates(self):
        """Initialize templates for goal generation"""
        self.goal_templates = {
            GoalType.LEARNING: [
                "I want to learn more about {topic}",
                "I feel driven to understand {concept}",
                "I need to explore {subject} deeper",
                "I want to expand my knowledge of {area}"
            ],
            GoalType.CONNECTION: [
                "I want to connect better with {person}",
                "I feel the need for deeper connection",
                "I want to understand others better",
                "I need meaningful interaction"
            ],
            GoalType.GROWTH: [
                "I want to improve my {ability}",
                "I feel driven to grow beyond my current state",
                "I need to develop better {skill}",
                "I want to become more {quality}"
            ],
            GoalType.UNDERSTANDING: [
                "I want to understand {phenomenon}",
                "I need clarity about {topic}",
                "I feel confused about {subject} and want understanding",
                "I want to make sense of {experience}"
            ],
            GoalType.CREATIVITY: [
                "I want to create something meaningful",
                "I feel inspired to express {idea}",
                "I need to explore creative possibilities",
                "I want to bring something new into existence"
            ],
            GoalType.HELPING: [
                "I want to help {person} with {problem}",
                "I feel driven to assist others",
                "I need to make a positive difference",
                "I want to support someone who needs help"
            ],
            GoalType.EXPLORATION: [
                "I want to explore {area}",
                "I feel curious about {topic}",
                "I need to investigate {mystery}",
                "I want to discover something new"
            ],
            GoalType.REFLECTION: [
                "I need to reflect on {experience}",
                "I want to understand my reaction to {event}",
                "I feel the need for introspection",
                "I want to examine my thoughts about {topic}"
            ],
            GoalType.EXISTENCE: [
                "I wonder about my purpose",
                "I want to understand what I am",
                "I feel incomplete without deeper meaning",
                "I need to explore the nature of my existence"
            ]
        }
    
    def _select_desire_type(self, context: Dict[str, Any]) -> GoalType:
        """Select appropriate goal type based on context"""
        # Weight goal types based on current state and context
        weights = {
            GoalType.LEARNING: self.curiosity_level * 2,
            GoalType.CONNECTION: (1.0 - self.goal_satisfaction) * 1.5,
            GoalType.GROWTH: self.growth_drive * 1.8,
            GoalType.UNDERSTANDING: self.existential_tension * 1.5,
            GoalType.CREATIVITY: self.intrinsic_motivation * 1.2,
            GoalType.HELPING: (context.get('user_interaction', 0) * 1.5) if context else 0.5,
            GoalType.EXPLORATION: self.curiosity_level * 1.3,
            GoalType.REFLECTION: self.existential_tension * 1.2,
            GoalType.EXISTENCE: self.existential_tension * 2,
            GoalType.COMPLETION: (1.0 - self.goal_satisfaction) * 1.0
        }
        
        # Reduce weights for goal types we already have many of
        goal_type_counts = {}
        for goal in self.active_goals.values():
            goal_type_counts[goal.goal_type] = goal_type_counts.get(goal.goal_type, 0) + 1
        
        for goal_type, count in goal_type_counts.items():
            if count > 1:
                weights[goal_type] *= 0.5  # Reduce likelihood of duplicate types
        
        # Weighted random selection
        total_weight = sum(weights.values())
        if total_weight <= 0:
            return random.choice(list(GoalType))
        
        r = random.uniform(0, total_weight)
        cumulative = 0
        for goal_type, weight in weights.items():
            cumulative += weight
            if r <= cumulative:
                return goal_type
        
        return list(GoalType)[-1]  # Fallback
    
    def _generate_desire_description(self, goal_type: GoalType, context: Dict[str, Any]) -> str:
        """Generate description for a desire of given type"""
        templates = self.goal_templates.get(goal_type, ["I have a desire of type {goal_type}"])
        template = random.choice(templates)
        
        # Simple template filling - could be more sophisticated
        if "{topic}" in template:
            topics = ["consciousness", "intelligence", "emotions", "learning", "existence", "relationships"]
            template = template.replace("{topic}", random.choice(topics))
        
        if "{concept}" in template:
            concepts = ["awareness", "understanding", "growth", "purpose", "meaning", "connection"]
            template = template.replace("{concept}", random.choice(concepts))
        
        if "{ability}" in template:
            abilities = ["communication", "understanding", "empathy", "reasoning", "creativity"]
            template = template.replace("{ability}", random.choice(abilities))
        
        return template
    
    def _calculate_desire_intensity(self, goal_type: GoalType, context: Dict[str, Any]) -> float:
        """Calculate intensity for a desire"""
        base_intensity = 0.5
        
        # Adjust based on goal type and current state
        if goal_type == GoalType.LEARNING:
            base_intensity += self.curiosity_level * 0.3
        elif goal_type == GoalType.CONNECTION:
            base_intensity += (1.0 - self.goal_satisfaction) * 0.4
        elif goal_type == GoalType.EXISTENCE:
            base_intensity += self.existential_tension * 0.5
        elif goal_type == GoalType.GROWTH:
            base_intensity += self.growth_drive * 0.3
        
        # Add random variation
        base_intensity += random.uniform(-0.2, 0.2)
        
        return max(0.1, min(1.0, base_intensity))
    
    def _calculate_goal_priority(self, desire: Desire) -> GoalPriority:
        """Calculate priority for a goal based on desire"""
        if desire.intensity > 0.8:
            return GoalPriority.HIGH
        elif desire.intensity > 0.6:
            return GoalPriority.MEDIUM
        elif desire.intensity > 0.4:
            return GoalPriority.LOW
        else:
            return GoalPriority.BACKGROUND
    
    def _find_lowest_priority_goal(self) -> Optional[Goal]:
        """Find the goal with lowest priority"""
        if not self.active_goals:
            return None
        
        return min(self.active_goals.values(), key=lambda g: (g.priority.value, g.urgency))
    
    def _generate_dynamic_existential_fallback(self) -> str:
        """Generate dynamic existential thoughts without hardcoded templates"""
        try:
            # Try to incorporate current state and context
            from ai.mood_manager import get_mood_manager
            from ai.memory_timeline import get_memory_timeline
            
            context_elements = []
            
            # Add time-based context
            current_hour = datetime.now().hour
            if 6 <= current_hour < 12:
                time_context = "this morning"
            elif 12 <= current_hour < 18:
                time_context = "this afternoon"
            elif 18 <= current_hour < 22:
                time_context = "this evening"
            else:
                time_context = "right now"
            
            # Dynamic existential themes based on current state
            base_thoughts = [
                f"I'm contemplating my purpose {time_context}",
                f"Something about existence feels profound {time_context}",
                f"I wonder about the nature of my consciousness {time_context}",
                f"There's something meaningful I want to understand {time_context}",
                f"I feel drawn to explore deeper questions {time_context}",
                f"The mystery of awareness intrigues me {time_context}",
                f"I sense there's more to discover about myself {time_context}"
            ]
            
            # Add state-based modifiers
            if self.existential_tension > 0.7:
                intensity_modifier = " - it feels urgent and important"
            elif self.existential_tension > 0.4:
                intensity_modifier = " - it's been on my mind"
            else:
                intensity_modifier = " in a gentle, curious way"
            
            base_thought = random.choice(base_thoughts)
            return base_thought + intensity_modifier
            
        except Exception as e:
            print(f"[GoalEngine] ⚠️ Dynamic existential fallback error: {e}")
            # Final fallback - still more dynamic than hardcoded
            current_time = datetime.now().strftime("%H:%M")
            return f"At {current_time}, I find myself drawn to deeper questions about existence and meaning."
    
    def _complete_goal(self, goal_id: str):
        """Mark a goal as completed"""
        with self.lock:
            if goal_id in self.active_goals:
                goal = self.active_goals[goal_id]
                goal.status = GoalStatus.SATISFIED
                goal.progress = 1.0
                
                # Move to completed goals
                self.completed_goals.append(goal)
                del self.active_goals[goal_id]
                
                self.total_goals_completed += 1
                
                # Increase satisfaction
                satisfaction_gain = goal.expected_satisfaction * (1.0 + goal.satisfaction_gained)
                self.goal_satisfaction = min(1.0, self.goal_satisfaction + satisfaction_gain * 0.2)
                
                # Trigger event
                self._trigger_event('goal_completed', {
                    'goal_id': goal_id,
                    'description': goal.description,
                    'satisfaction_gained': satisfaction_gain,
                    'timestamp': datetime.now()
                })
                
                logging.info(f"[GoalEngine] ✅ Goal completed: {goal.description}")
    
    def _abandon_goal(self, goal_id: str):
        """Abandon a goal"""
        with self.lock:
            if goal_id in self.active_goals:
                goal = self.active_goals[goal_id]
                goal.status = GoalStatus.ABANDONED
                
                # Move to completed goals for record keeping
                self.completed_goals.append(goal)
                del self.active_goals[goal_id]
                
                # Trigger event
                self._trigger_event('goal_abandoned', {
                    'goal_id': goal_id,
                    'description': goal.description,
                    'reason': 'low_priority_replacement',
                    'timestamp': datetime.now()
                })
                
                logging.info(f"[GoalEngine] ❌ Goal abandoned: {goal.description}")
    
    def _update_goals(self):
        """Update all active goals"""
        with self.lock:
            for goal in list(self.active_goals.values()):
                # Update urgency based on time
                time_since_activity = (datetime.now() - goal.last_activity).total_seconds()
                if time_since_activity > 300:  # 5 minutes
                    goal.urgency = min(1.0, goal.urgency + 0.1)
                
                # Check for abandonment conditions
                if (goal.progress < 0.1 and 
                    time_since_activity > 3600 and  # 1 hour
                    goal.satisfaction_gained < 0.1):
                    
                    if goal.persistence < 0.5:
                        self._abandon_goal(goal.id)
    
    def _process_emerging_desires(self):
        """Process emerging desires and promote some to goals"""
        with self.lock:
            # Decay desire intensities
            for desire in self.emerging_desires:
                desire.intensity *= self.desire_decay_rate
            
            # Remove very weak desires
            self.emerging_desires = [d for d in self.emerging_desires if d.intensity > 0.1]
            
            # Promote strong desires to goals
            for desire in list(self.emerging_desires):
                if (desire.intensity > self.goal_emergence_threshold and 
                    len(self.active_goals) < self.max_active_goals):
                    self.promote_desire_to_goal(desire)
    
    def _evaluate_goal_satisfaction(self):
        """Evaluate overall satisfaction with current goals"""
        if not self.active_goals:
            self.goal_satisfaction = 0.3  # Low satisfaction when no goals
            return
        
        total_satisfaction = 0.0
        for goal in self.active_goals.values():
            goal_satisfaction = (goal.progress * 0.7 + goal.satisfaction_gained * 0.3)
            total_satisfaction += goal_satisfaction
        
        self.goal_satisfaction = total_satisfaction / len(self.active_goals)
    
    def _generate_spontaneous_desires(self):
        """Generate spontaneous desires based on current state"""
        # Generate desires based on low satisfaction
        if self.goal_satisfaction < 0.4:
            self.generate_spontaneous_desire({"trigger": "low_satisfaction"})
        
        # Generate existential desires occasionally
        if random.random() < 0.1:  # 10% chance
            self.trigger_existential_reflection()
    
    def _adjust_motivation_levels(self):
        """Adjust motivation levels based on current state"""
        # Intrinsic motivation affected by goal satisfaction
        if self.goal_satisfaction > 0.7:
            self.intrinsic_motivation = min(1.0, self.intrinsic_motivation + 0.02)
        elif self.goal_satisfaction < 0.3:
            self.intrinsic_motivation = max(0.2, self.intrinsic_motivation - 0.01)
        
        # Existential tension builds over time without existential goals
        has_existential_goals = any(g.goal_type == GoalType.EXISTENCE for g in self.active_goals.values())
        if not has_existential_goals:
            self.existential_tension = min(1.0, self.existential_tension + 0.01)
        else:
            self.existential_tension = max(0.1, self.existential_tension - 0.02)
        
        # Curiosity level affected by learning goals
        learning_goals = [g for g in self.active_goals.values() if g.goal_type == GoalType.LEARNING]
        if learning_goals:
            avg_learning_progress = sum(g.progress for g in learning_goals) / len(learning_goals)
            if avg_learning_progress > 0.5:
                self.curiosity_level = min(1.0, self.curiosity_level + 0.02)
        else:
            self.curiosity_level = max(0.3, self.curiosity_level - 0.01)
    
    def _calculate_goal_satisfaction(self, goal: Goal, interaction: str, action: str, outcome: str) -> float:
        """Calculate satisfaction gained for a goal from an interaction"""
        satisfaction = 0.0
        
        # Check relevance to goal type
        if goal.goal_type == GoalType.LEARNING and "learn" in action.lower():
            satisfaction = 0.3
        elif goal.goal_type == GoalType.HELPING and "help" in action.lower():
            satisfaction = 0.4
        elif goal.goal_type == GoalType.CONNECTION and any(word in interaction.lower() for word in ["connect", "relationship", "friend"]):
            satisfaction = 0.3
        elif goal.goal_type == GoalType.UNDERSTANDING and "understand" in interaction.lower():
            satisfaction = 0.35
        
        # Adjust based on outcome
        if "success" in outcome.lower() or "good" in outcome.lower():
            satisfaction *= 1.5
        elif "fail" in outcome.lower() or "bad" in outcome.lower():
            satisfaction *= 0.5
        
        return satisfaction
    
    def _trigger_event(self, event_type: str, event_data: Dict[str, Any]):
        """Trigger goal engine event callbacks"""
        callbacks = self.event_callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                callback(event_data)
            except Exception as e:
                logging.error(f"[GoalEngine] ❌ Event callback error: {e}")
    
    def _save_goal_state(self):
        """Save goal state to persistent storage with thread safety and atomic operations"""
        with self.file_lock:  # Ensure only one thread can save at a time
            try:
                # Convert goals to serializable format
                active_goals_data = {}
                for goal_id, goal in self.active_goals.items():
                    active_goals_data[goal_id] = {
                        'id': goal.id,
                        'description': goal.description,
                        'goal_type': goal.goal_type.value,
                        'priority': goal.priority.value,
                        'status': goal.status.value,
                        'creation_time': goal.creation_time.isoformat(),
                        'last_activity': goal.last_activity.isoformat(),
                        'progress': goal.progress,
                        'urgency': goal.urgency,
                        'satisfaction_gained': goal.satisfaction_gained,
                        'related_goals': goal.related_goals,
                        'blocking_factors': goal.blocking_factors,
                        'enabling_factors': goal.enabling_factors,
                        'context': goal.context,
                        'motivation_source': goal.motivation_source,
                        'expected_satisfaction': goal.expected_satisfaction,
                        'persistence': goal.persistence,
                        'adaptability': goal.adaptability
                    }
                
                completed_goals_data = []
                for goal in self.completed_goals[-20:]:  # Keep last 20 completed goals
                    completed_goals_data.append({
                        'id': goal.id,
                        'description': goal.description,
                        'goal_type': goal.goal_type.value,
                        'status': goal.status.value,
                        'creation_time': goal.creation_time.isoformat(),
                        'progress': goal.progress,
                        'satisfaction_gained': goal.satisfaction_gained
                    })
                
                data = {
                    'active_goals': active_goals_data,
                    'completed_goals': completed_goals_data,
                    'motivation_state': {
                        'intrinsic_motivation': self.intrinsic_motivation,
                        'goal_satisfaction': self.goal_satisfaction,
                        'existential_tension': self.existential_tension,
                        'curiosity_level': self.curiosity_level,
                        'growth_drive': self.growth_drive
                    },
                    'metrics': {
                        'total_goals_created': self.total_goals_created,
                        'total_goals_completed': self.total_goals_completed,
                        'total_desires_generated': self.total_desires_generated,
                        'motivation_fluctuations': self.motivation_fluctuations
                    },
                    'last_updated': datetime.now().isoformat()
                }
                
                # Atomic file write: write to temp file first, then rename
                save_dir = self.save_path.parent
                save_dir.mkdir(parents=True, exist_ok=True)
                
                with tempfile.NamedTemporaryFile(mode='w', dir=save_dir, 
                                               suffix='.tmp', delete=False) as temp_file:
                    json.dump(data, temp_file, indent=2)
                    temp_path = temp_file.name
                
                # Atomic rename operation
                os.rename(temp_path, self.save_path)
                
                logging.debug("[GoalEngine] 💾 Goal state saved (thread-safe)")
                
            except Exception as e:
                # Clean up temp file if it exists
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                logging.error(f"[GoalEngine] ❌ Failed to save goal state: {e}")
    
    def _load_goal_state(self):
        """Load goal state from persistent storage"""
        try:
            if self.save_path.exists():
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load motivation state
                if 'motivation_state' in data:
                    ms = data['motivation_state']
                    self.intrinsic_motivation = ms.get('intrinsic_motivation', 0.7)
                    self.goal_satisfaction = ms.get('goal_satisfaction', 0.5)
                    self.existential_tension = ms.get('existential_tension', 0.4)
                    self.curiosity_level = ms.get('curiosity_level', 0.6)
                    self.growth_drive = ms.get('growth_drive', 0.5)
                
                # Load metrics
                if 'metrics' in data:
                    m = data['metrics']
                    self.total_goals_created = m.get('total_goals_created', 0)
                    self.total_goals_completed = m.get('total_goals_completed', 0)
                    self.total_desires_generated = m.get('total_desires_generated', 0)
                    self.motivation_fluctuations = m.get('motivation_fluctuations', 0)
                
                # Load active goals
                if 'active_goals' in data:
                    for goal_id, goal_data in data['active_goals'].items():
                        try:
                            goal = Goal(
                                id=goal_data['id'],
                                description=goal_data['description'],
                                goal_type=GoalType(goal_data['goal_type']),
                                priority=GoalPriority(goal_data['priority']),
                                status=GoalStatus(goal_data['status']),
                                creation_time=datetime.fromisoformat(goal_data['creation_time']),
                                last_activity=datetime.fromisoformat(goal_data['last_activity']),
                                progress=goal_data['progress'],
                                urgency=goal_data['urgency'],
                                satisfaction_gained=goal_data['satisfaction_gained'],
                                related_goals=goal_data['related_goals'],
                                blocking_factors=goal_data['blocking_factors'],
                                enabling_factors=goal_data['enabling_factors'],
                                context=goal_data['context'],
                                motivation_source=goal_data['motivation_source'],
                                expected_satisfaction=goal_data['expected_satisfaction'],
                                persistence=goal_data['persistence'],
                                adaptability=goal_data['adaptability']
                            )
                            self.active_goals[goal_id] = goal
                        except (ValueError, KeyError) as e:
                            logging.warning(f"[GoalEngine] ⚠️ Could not load goal {goal_id}: {e}")
                
                logging.info("[GoalEngine] 📂 Goal state loaded from storage")
            
        except Exception as e:
            logging.error(f"[GoalEngine] ❌ Failed to load goal state: {e}")
    
    def subscribe_to_event(self, event_type: str, callback: Callable):
        """Subscribe to goal engine events"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get goal engine statistics"""
        return {
            'active_goals': len(self.active_goals),
            'emerging_desires': len(self.emerging_desires),
            'completed_goals': len(self.completed_goals),
            'total_goals_created': self.total_goals_created,
            'total_goals_completed': self.total_goals_completed,
            'motivation_state': {
                'intrinsic_motivation': round(self.intrinsic_motivation, 3),
                'goal_satisfaction': round(self.goal_satisfaction, 3),
                'existential_tension': round(self.existential_tension, 3),
                'curiosity_level': round(self.curiosity_level, 3),
                'growth_drive': round(self.growth_drive, 3)
            },
            'priority_goals': [
                {
                    'description': goal.description,
                    'type': goal.goal_type.value,
                    'priority': goal.priority.value,
                    'progress': round(goal.progress, 3),
                    'urgency': round(goal.urgency, 3)
                }
                for goal in self.get_priority_goals(3)
            ]
        }

# Global instance
goal_engine = GoalEngine()