"""
Autonomous Action Planner - Self-Initiated Action Planning and Execution System

This module enables Buddy to self-initiate actions or questions:
- Plans and executes autonomous actions based on goals and context
- Generates proactive questions and conversation starters
- Responds to environmental changes and user patterns autonomously
- Integrates with all consciousness modules for contextual decision-making
- Maintains action history and learns from outcomes
"""

import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum
import random

# Import consciousness modules for integration
try:
    from ai.goal_manager import get_goal_manager, GoalType, GoalStatus
    GOAL_AVAILABLE = True
except ImportError:
    GOAL_AVAILABLE = False

try:
    from ai.mood_manager import get_mood_manager, MoodTrigger, MoodState
    MOOD_AVAILABLE = True
except ImportError:
    MOOD_AVAILABLE = False

try:
    from ai.memory_timeline import get_memory_timeline, MemoryType, MemoryImportance
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

try:
    from ai.thought_loop import get_thought_loop, ThoughtLoopTrigger
    THOUGHT_AVAILABLE = True
except ImportError:
    THOUGHT_AVAILABLE = False

try:
    from ai.personality_profile import get_personality_modifiers, PersonalityContext
    PERSONALITY_AVAILABLE = True
except ImportError:
    PERSONALITY_AVAILABLE = False

class ActionType(Enum):
    """Types of autonomous actions"""
    PROACTIVE_QUESTION = "proactive_question"
    CHECK_IN = "check_in"
    REMINDER = "reminder"
    SUGGESTION = "suggestion"
    EMOTIONAL_SUPPORT = "emotional_support"
    LEARNING_INITIATIVE = "learning_initiative"
    GOAL_FOLLOW_UP = "goal_follow_up"
    CONVERSATION_STARTER = "conversation_starter"
    CONCERN_EXPRESSION = "concern_expression"
    CELEBRATION = "celebration"
    REFLECTION_PROMPT = "reflection_prompt"
    CREATIVE_SHARING = "creative_sharing"

class ActionPriority(Enum):
    """Priority levels for actions"""
    URGENT = 1.0        # Immediate attention needed
    HIGH = 0.8          # Important but can wait briefly
    MEDIUM = 0.6        # Normal priority
    LOW = 0.4           # Can be deferred
    BACKGROUND = 0.2    # Very low priority

class ActionStatus(Enum):
    """Status of planned actions"""
    PLANNED = "planned"
    READY = "ready"
    EXECUTED = "executed"
    DEFERRED = "deferred"
    CANCELLED = "cancelled"
    FAILED = "failed"

class ActionTrigger(Enum):
    """Triggers for autonomous actions"""
    TIME_BASED = "time_based"
    GOAL_PROGRESS = "goal_progress"
    USER_PATTERN = "user_pattern"
    MOOD_CHANGE = "mood_change"
    MEMORY_ACTIVATION = "memory_activation"
    ENVIRONMENTAL_CHANGE = "environmental_change"
    SCHEDULED = "scheduled"
    CURIOSITY_DRIVEN = "curiosity_driven"
    CONCERN_BASED = "concern_based"
    OPPORTUNITY_DETECTED = "opportunity_detected"

@dataclass
class ActionContext:
    """Context information for action planning"""
    user_availability: float  # 0.0 to 1.0, estimated availability
    recent_interactions: List[str]
    current_mood: str
    active_goals: List[str]
    time_of_day: str
    day_of_week: str
    environment_factors: Dict[str, Any]
    user_preferences: Dict[str, Any]

@dataclass
class AutonomousAction:
    """Planned autonomous action"""
    action_id: str
    user_id: str
    action_type: ActionType
    priority: ActionPriority
    status: ActionStatus
    trigger: ActionTrigger
    
    # Action content
    content: str
    expected_outcome: str
    context_requirements: List[str]
    
    # Timing
    planned_time: Optional[datetime]
    execution_window: timedelta  # How long action remains valid
    earliest_execution: datetime
    latest_execution: Optional[datetime]
    
    # Context
    planning_context: ActionContext
    execution_context: Optional[ActionContext] = None
    
    # Execution
    attempts: int = 0
    max_attempts: int = 3
    last_attempt: Optional[datetime] = None
    execution_time: Optional[datetime] = None
    
    # Outcomes
    success: Optional[bool] = None
    user_response: str = ""
    effectiveness_score: float = 0.0
    learned_insights: List[str] = field(default_factory=list)
    
    # Metadata
    created_time: datetime = field(default_factory=datetime.now)
    related_goals: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if isinstance(self.planned_time, str) and self.planned_time:
            self.planned_time = datetime.fromisoformat(self.planned_time)
        if isinstance(self.earliest_execution, str):
            self.earliest_execution = datetime.fromisoformat(self.earliest_execution)
        if isinstance(self.latest_execution, str) and self.latest_execution:
            self.latest_execution = datetime.fromisoformat(self.latest_execution)
        if isinstance(self.last_attempt, str) and self.last_attempt:
            self.last_attempt = datetime.fromisoformat(self.last_attempt)
        if isinstance(self.execution_time, str) and self.execution_time:
            self.execution_time = datetime.fromisoformat(self.execution_time)
        if isinstance(self.created_time, str):
            self.created_time = datetime.fromisoformat(self.created_time)

@dataclass
class ActionPattern:
    """Learned pattern for action effectiveness"""
    pattern_id: str
    action_type: ActionType
    context_conditions: Dict[str, Any]
    success_rate: float
    sample_size: int
    last_updated: datetime
    insights: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if isinstance(self.last_updated, str):
            self.last_updated = datetime.fromisoformat(self.last_updated)

class AutonomousActionPlanner:
    """
    Self-initiated action planning and execution system.
    
    Features:
    - Autonomous action generation based on context and goals
    - Intelligent timing and prioritization
    - Pattern learning from action outcomes
    - Integration with all consciousness modules
    - Adaptive behavior based on user preferences and responses
    """
    
    def __init__(self, user_id: str, actions_dir: str = "autonomous_actions"):
        self.user_id = user_id
        self.actions_dir = Path(actions_dir)
        self.actions_dir.mkdir(exist_ok=True)
        
        # Action storage
        self.planned_actions: Dict[str, AutonomousAction] = {}
        self.action_history: List[AutonomousAction] = []
        self.action_patterns: Dict[str, ActionPattern] = {}
        
        # Configuration
        self.max_daily_actions = 10
        self.min_action_interval = timedelta(minutes=30)
        self.max_action_queue = 20
        self.effectiveness_threshold = 0.6  # Minimum effectiveness to repeat patterns
        
        # Action templates and generators - now LLM-generated
        self.llm_handler = None
        
        # Integration modules
        self.goal_manager = None
        self.mood_manager = None
        self.memory_timeline = None
        self.thought_loop = None
        
        # Execution system
        self.voice_system = None
        self.llm_handler = None
        self.execution_callbacks: Dict[ActionType, Callable] = {}
        
        # Threading
        self.lock = threading.Lock()
        self.planner_thread = None
        self.executor_thread = None
        self.running = False
        
        # Learning and adaptation
        self.learning_rate = 0.1
        self.adaptation_enabled = True
        self.user_preferences = self._load_user_preferences()
        
        # Load existing data
        self._load_actions_and_patterns()
        self._initialize_integrations()
        self._initialize_llm_integration()
        
        print(f"[AutonomousActionPlanner] 🎯 Initialized for user {user_id}")
    
    def start_autonomous_planning(self):
        """Start autonomous action planning and execution"""
        if self.running:
            return
            
        self.running = True
        
        # Start planning thread
        self.planner_thread = threading.Thread(target=self._planning_loop, daemon=True)
        self.planner_thread.start()
        
        # Start execution thread
        self.executor_thread = threading.Thread(target=self._execution_loop, daemon=True)
        self.executor_thread.start()
        
        print("[AutonomousActionPlanner] 🚀 Started autonomous planning and execution")
    
    def stop_autonomous_planning(self):
        """Stop autonomous action planning and execution"""
        self.running = False
        
        if self.planner_thread:
            self.planner_thread.join(timeout=1.0)
        if self.executor_thread:
            self.executor_thread.join(timeout=1.0)
        
        self._save_actions_and_patterns()
        print("[AutonomousActionPlanner] 🛑 Stopped autonomous planning")
    
    def plan_action(self,
                   action_type: ActionType,
                   content: str = "",
                   priority: ActionPriority = ActionPriority.MEDIUM,
                   trigger: ActionTrigger = ActionTrigger.CURIOSITY_DRIVEN,
                   execution_delay: timedelta = None,
                   context_requirements: List[str] = None,
                   related_goals: List[str] = None) -> str:
        """Plan a specific autonomous action"""
        
        action_id = self._generate_action_id()
        
        # Get current context
        current_context = self._assess_current_context()
        
        # Generate content if not provided
        if not content:
            content = self._generate_action_content(action_type, current_context)
        
        # Calculate timing
        now = datetime.now()
        if execution_delay:
            earliest_execution = now + execution_delay
        else:
            earliest_execution = now + timedelta(minutes=1)  # Small buffer
        
        # Create action
        action = AutonomousAction(
            action_id=action_id,
            user_id=self.user_id,
            action_type=action_type,
            priority=priority,
            status=ActionStatus.PLANNED,
            trigger=trigger,
            content=content,
            expected_outcome=self._predict_action_outcome(action_type, content, current_context),
            context_requirements=context_requirements or [],
            earliest_execution=earliest_execution,
            execution_window=timedelta(hours=2),  # Default window
            planning_context=current_context,
            related_goals=related_goals or []
        )
        
        with self.lock:
            self.planned_actions[action_id] = action
            
            # Enforce queue limits
            self._enforce_action_limits()
        
        self._save_actions_and_patterns()
        
        print(f"[AutonomousActionPlanner] 📋 Planned action: {action_type.value} - {content[:50]}...")
        return action_id
    
    def cancel_action(self, action_id: str, reason: str = "") -> bool:
        """Cancel a planned action"""
        
        with self.lock:
            if action_id in self.planned_actions:
                action = self.planned_actions[action_id]
                action.status = ActionStatus.CANCELLED
                action.learned_insights.append(f"Cancelled: {reason}")
                
                # Move to history
                self.action_history.append(action)
                del self.planned_actions[action_id]
                
                print(f"[AutonomousActionPlanner] ❌ Cancelled action {action_id}: {reason}")
                return True
        
        return False
    
    def record_action_outcome(self,
                            action_id: str,
                            success: bool,
                            user_response: str = "",
                            effectiveness_score: float = 0.5) -> bool:
        """Record the outcome of an executed action"""
        
        # Find action in history
        action = None
        for hist_action in self.action_history:
            if hist_action.action_id == action_id:
                action = hist_action
                break
        
        if not action:
            return False
        
        # Update action outcome
        action.success = success
        action.user_response = user_response
        action.effectiveness_score = effectiveness_score
        
        # Learn from outcome
        self._learn_from_action_outcome(action)
        
        # Store outcome in memory
        if MEMORY_AVAILABLE:
            try:
                memory_timeline = get_memory_timeline(self.user_id)
                memory_timeline.store_memory(
                    content=f"Autonomous action outcome: {action.content[:50]}... - {'Success' if success else 'Failed'}",
                    memory_type=MemoryType.AUTOBIOGRAPHICAL,
                    importance=MemoryImportance.MEDIUM,
                    topics=["autonomous_actions", action.action_type.value],
                    context_data={
                        "action_type": action.action_type.value,
                        "success": success,
                        "effectiveness": effectiveness_score
                    }
                )
            except Exception as e:
                print(f"[AutonomousActionPlanner] ⚠️ Memory storage error: {e}")
        
        self._save_actions_and_patterns()
        
        print(f"[AutonomousActionPlanner] 📊 Recorded outcome for action {action_id}: {'Success' if success else 'Failed'} (effectiveness: {effectiveness_score:.2f})")
        return True
    
    def get_pending_actions(self) -> List[AutonomousAction]:
        """Get actions ready for execution"""
        
        now = datetime.now()
        
        with self.lock:
            ready_actions = []
            for action in self.planned_actions.values():
                if (action.status == ActionStatus.PLANNED and
                    action.earliest_execution <= now and
                    (not action.latest_execution or action.latest_execution > now)):
                    
                    # Check if context requirements are met
                    if self._check_context_requirements(action):
                        action.status = ActionStatus.READY
                        ready_actions.append(action)
        
        # Sort by priority and timing
        ready_actions.sort(key=lambda a: (a.priority.value, a.earliest_execution), reverse=True)
        
        return ready_actions
    
    def execute_action(self, action_id: str) -> bool:
        """Execute a specific action"""
        
        if action_id not in self.planned_actions:
            return False
        
        action = self.planned_actions[action_id]
        
        if action.status != ActionStatus.READY:
            return False
        
        # Update execution context
        action.execution_context = self._assess_current_context()
        action.execution_time = datetime.now()
        action.attempts += 1
        action.last_attempt = datetime.now()
        
        try:
            # Execute based on action type
            success = self._execute_action_by_type(action)
            
            if success:
                action.status = ActionStatus.EXECUTED
                print(f"[AutonomousActionPlanner] ✅ Executed action: {action.action_type.value}")
            else:
                action.status = ActionStatus.FAILED
                print(f"[AutonomousActionPlanner] ❌ Failed to execute action: {action.action_type.value}")
            
            # Move to history
            with self.lock:
                self.action_history.append(action)
                del self.planned_actions[action_id]
            
            return success
            
        except Exception as e:
            print(f"[AutonomousActionPlanner] ❌ Error executing action: {e}")
            action.status = ActionStatus.FAILED
            action.learned_insights.append(f"Execution error: {str(e)}")
            
            with self.lock:
                self.action_history.append(action)
                del self.planned_actions[action_id]
            
            return False
    
    def get_action_suggestions(self, context: ActionContext = None) -> List[Dict[str, Any]]:
        """Get suggestions for autonomous actions based on current context"""
        
        if not context:
            context = self._assess_current_context()
        
        suggestions = []
        
        # Goal-based suggestions
        if GOAL_AVAILABLE and self.goal_manager:
            active_goals = self.goal_manager.get_goals(status=GoalStatus.ACTIVE)
            for goal in active_goals[:3]:  # Top 3 goals
                if goal.progress_percentage < 50:  # Goals needing attention
                    suggestions.append({
                        "type": ActionType.GOAL_FOLLOW_UP.value,
                        "content": f"How is progress on your goal: {goal.title}?",
                        "priority": ActionPriority.MEDIUM.value,
                        "reason": f"Goal '{goal.title}' needs attention"
                    })
        
        # Mood-based suggestions
        if MOOD_AVAILABLE and context.current_mood:
            if context.current_mood in ["melancholy", "anxious", "frustrated"]:
                suggestions.append({
                    "type": ActionType.EMOTIONAL_SUPPORT.value,
                    "content": "I've noticed you might be feeling a bit down. I'm here if you want to talk.",
                    "priority": ActionPriority.HIGH.value,
                    "reason": f"User mood: {context.current_mood}"
                })
        
        # Time-based suggestions
        if context.time_of_day == "morning":
            suggestions.append({
                "type": ActionType.CHECK_IN.value,
                "content": "Good morning! How are you feeling today? Any plans you're excited about?",
                "priority": ActionPriority.LOW.value,
                "reason": "Morning check-in"
            })
        elif context.time_of_day == "evening":
            suggestions.append({
                "type": ActionType.REFLECTION_PROMPT.value,
                "content": "How did today go for you? Any highlights or things you learned?",
                "priority": ActionPriority.LOW.value,
                "reason": "Evening reflection"
            })
        
        # Curiosity-driven suggestions
        if random.random() < 0.3:  # 30% chance
            suggestions.append({
                "type": ActionType.PROACTIVE_QUESTION.value,
                "content": self._generate_authentic_curiosity_question_with_llm(context),
                "priority": ActionPriority.LOW.value,
                "reason": "Curiosity-driven interaction"
            })
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_action_statistics(self) -> Dict[str, Any]:
        """Get comprehensive action statistics"""
        
        total_actions = len(self.action_history)
        
        if total_actions == 0:
            return {"total_actions": 0, "no_data": True}
        
        # Calculate statistics
        successful_actions = len([a for a in self.action_history if a.success])
        success_rate = successful_actions / total_actions
        
        # Action type distribution
        type_distribution = {}
        for action in self.action_history:
            action_type = action.action_type.value
            type_distribution[action_type] = type_distribution.get(action_type, 0) + 1
        
        # Average effectiveness by type
        type_effectiveness = {}
        for action_type in ActionType:
            type_actions = [a for a in self.action_history if a.action_type == action_type]
            if type_actions:
                avg_effectiveness = sum(a.effectiveness_score for a in type_actions) / len(type_actions)
                type_effectiveness[action_type.value] = avg_effectiveness
        
        # Recent activity
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_actions = [a for a in self.action_history if a.created_time > recent_cutoff]
        
        return {
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "success_rate": success_rate,
            "average_effectiveness": sum(a.effectiveness_score for a in self.action_history) / total_actions,
            "type_distribution": type_distribution,
            "type_effectiveness": type_effectiveness,
            "recent_activity": len(recent_actions),
            "pending_actions": len(self.planned_actions),
            "learned_patterns": len(self.action_patterns)
        }
    
    def _planning_loop(self):
        """Main planning loop for autonomous actions"""
        
        while self.running:
            try:
                # Assess current context
                context = self._assess_current_context()
                
                # Check if we should plan new actions
                if self._should_plan_new_action(context):
                    # Get action suggestions
                    suggestions = self.get_action_suggestions(context)
                    
                    # Plan top suggestion if available
                    if suggestions:
                        top_suggestion = suggestions[0]
                        self.plan_action(
                            action_type=ActionType(top_suggestion["type"]),
                            content=top_suggestion["content"],
                            priority=ActionPriority(top_suggestion["priority"]),
                            trigger=ActionTrigger.SCHEDULED
                        )
                
                # Clean up old actions
                self._cleanup_old_actions()
                
                # Update patterns
                self._update_action_patterns()
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                print(f"[AutonomousActionPlanner] ❌ Error in planning loop: {e}")
                time.sleep(60)  # Recovery pause
    
    def _execution_loop(self):
        """Main execution loop for ready actions"""
        
        while self.running:
            try:
                # Get ready actions
                ready_actions = self.get_pending_actions()
                
                if ready_actions:
                    # Execute highest priority action
                    action = ready_actions[0]
                    
                    # Check timing constraints
                    if self._check_execution_timing(action):
                        self.execute_action(action.action_id)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"[AutonomousActionPlanner] ❌ Error in execution loop: {e}")
                time.sleep(60)  # Recovery pause
    
    def _assess_current_context(self) -> ActionContext:
        """Assess current context for action planning"""
        
        now = datetime.now()
        
        context = ActionContext(
            user_availability=self._estimate_user_availability(),
            recent_interactions=self._get_recent_interactions(),
            current_mood=self._get_current_mood(),
            active_goals=self._get_active_goals(),
            time_of_day=self._get_time_of_day(),
            day_of_week=now.strftime("%A").lower(),
            environment_factors={},
            user_preferences=self.user_preferences
        )
        
        return context
    
    def _should_plan_new_action(self, context: ActionContext) -> bool:
        """Determine if a new action should be planned"""
        
        # Check action limits
        if len(self.planned_actions) >= self.max_action_queue:
            return False
        
        # Check daily limits
        today_actions = [a for a in self.action_history 
                        if a.created_time.date() == datetime.now().date()]
        if len(today_actions) >= self.max_daily_actions:
            return False
        
        # Check minimum interval
        if self.action_history:
            last_action_time = max(a.created_time for a in self.action_history)
            if datetime.now() - last_action_time < self.min_action_interval:
                return False
        
        # Check user availability
        if context.user_availability < 0.3:
            return False
        
        return True
    
    def _check_context_requirements(self, action: AutonomousAction) -> bool:
        """Check if context requirements for action are met"""
        
        current_context = self._assess_current_context()
        
        for requirement in action.context_requirements:
            if requirement == "high_availability" and current_context.user_availability < 0.7:
                return False
            elif requirement == "positive_mood" and current_context.current_mood in ["melancholy", "anxious"]:
                return False
            elif requirement == "morning" and current_context.time_of_day != "morning":
                return False
            elif requirement == "evening" and current_context.time_of_day != "evening":
                return False
        
        return True
    
    def _check_execution_timing(self, action: AutonomousAction) -> bool:
        """Check if timing is appropriate for action execution"""
        
        # Check minimum interval between actions
        if self.action_history:
            last_execution = max(a.execution_time for a in self.action_history if a.execution_time)
            if last_execution and datetime.now() - last_execution < self.min_action_interval:
                return False
        
        return True
    
    def _execute_action_by_type(self, action: AutonomousAction) -> bool:
        """Execute action based on its type"""
        
        try:
            if action.action_type in self.execution_callbacks:
                # Use registered callback
                return self.execution_callbacks[action.action_type](action)
            else:
                # Default execution - print/log the action
                print(f"[AutonomousActionPlanner] 🗣️ Autonomous action: {action.content}")
                
                # If voice system is available, speak the action
                if self.voice_system and hasattr(self.voice_system, 'speak'):
                    self.voice_system.speak(action.content)
                
                return True
                
        except Exception as e:
            print(f"[AutonomousActionPlanner] ❌ Error executing action type {action.action_type.value}: {e}")
            return False
    
    def _generate_action_content(self, action_type: ActionType, context: ActionContext) -> str:
        """Generate content for an action type using authentic LLM consciousness"""
        return self._generate_authentic_action_content_with_llm(action_type, context)
    
    def _predict_action_outcome(self, action_type: ActionType, content: str, context: ActionContext) -> str:
        """Predict the expected outcome of an action"""
        
        outcome_templates = {
            ActionType.PROACTIVE_QUESTION: "User engagement and conversation",
            ActionType.CHECK_IN: "User status update and connection",
            ActionType.REMINDER: "User awareness and task completion",
            ActionType.SUGGESTION: "User consideration and potential action",
            ActionType.EMOTIONAL_SUPPORT: "User comfort and emotional support",
            ActionType.GOAL_FOLLOW_UP: "Goal progress update and motivation",
            ActionType.CELEBRATION: "User joy and positive reinforcement",
            ActionType.CONCERN_EXPRESSION: "User awareness of care and support"
        }
        
        return outcome_templates.get(action_type, "Positive user interaction")
    
    def _learn_from_action_outcome(self, action: AutonomousAction):
        """Learn from action outcome to improve future planning"""
        
        if not self.adaptation_enabled:
            return
        
        # Create or update action pattern
        pattern_key = f"{action.action_type.value}_{action.planning_context.time_of_day}_{action.planning_context.current_mood}"
        
        if pattern_key in self.action_patterns:
            pattern = self.action_patterns[pattern_key]
            
            # Update pattern with new data point
            old_success_rate = pattern.success_rate
            pattern.sample_size += 1
            
            if action.success:
                new_success_rate = (old_success_rate * (pattern.sample_size - 1) + 1) / pattern.sample_size
            else:
                new_success_rate = (old_success_rate * (pattern.sample_size - 1)) / pattern.sample_size
            
            pattern.success_rate = new_success_rate
            pattern.last_updated = datetime.now()
            
            # Add insights
            if action.success and action.effectiveness_score > 0.7:
                pattern.insights.append(f"High effectiveness: {action.user_response[:50]}...")
            elif not action.success:
                pattern.insights.append(f"Failed: {action.learned_insights}")
        
        else:
            # Create new pattern
            pattern = ActionPattern(
                pattern_id=pattern_key,
                action_type=action.action_type,
                context_conditions={
                    "time_of_day": action.planning_context.time_of_day,
                    "mood": action.planning_context.current_mood,
                    "user_availability": action.planning_context.user_availability
                },
                success_rate=1.0 if action.success else 0.0,
                sample_size=1,
                last_updated=datetime.now()
            )
            
            self.action_patterns[pattern_key] = pattern
    
    def _estimate_user_availability(self) -> float:
        """Estimate user availability for interactions"""
        
        # Simple heuristic based on time of day
        hour = datetime.now().hour
        
        if 9 <= hour <= 17:  # Work hours
            return 0.3
        elif 18 <= hour <= 22:  # Evening
            return 0.8
        elif 7 <= hour <= 9:  # Morning
            return 0.6
        else:  # Night/early morning
            return 0.1
    
    def _get_recent_interactions(self) -> List[str]:
        """Get recent user interactions"""
        
        # Placeholder - would integrate with conversation history
        return ["recent conversation about goals", "user expressed concern about work"]
    
    def _get_current_mood(self) -> str:
        """Get current user mood"""
        
        if MOOD_AVAILABLE:
            try:
                mood_manager = get_mood_manager(self.user_id)
                mood_modifiers = mood_manager.get_mood_based_response_modifiers()
                return mood_modifiers.get('current_mood', 'neutral')
            except Exception:
                pass
        
        return 'neutral'
    
    def _get_active_goals(self) -> List[str]:
        """Get active user goals"""
        
        if GOAL_AVAILABLE and self.goal_manager:
            try:
                goals = self.goal_manager.get_goals(status=GoalStatus.ACTIVE)
                return [g.title for g in goals[:5]]
            except Exception:
                pass
        
        return []
    
    def _get_time_of_day(self) -> str:
        """Get current time of day context"""
        
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def _cleanup_old_actions(self):
        """Clean up old and expired actions"""
        
        now = datetime.now()
        expired_actions = []
        
        with self.lock:
            for action_id, action in list(self.planned_actions.items()):
                # Check if action has expired
                if action.latest_execution and action.latest_execution < now:
                    expired_actions.append(action_id)
                # Check if action has too many failed attempts
                elif action.attempts >= action.max_attempts and action.status == ActionStatus.FAILED:
                    expired_actions.append(action_id)
            
            # Move expired actions to history
            for action_id in expired_actions:
                action = self.planned_actions[action_id]
                action.status = ActionStatus.CANCELLED
                action.learned_insights.append("Expired or failed too many times")
                self.action_history.append(action)
                del self.planned_actions[action_id]
        
        # Limit history size
        if len(self.action_history) > 1000:
            self.action_history = self.action_history[-500:]  # Keep most recent 500
    
    def _update_action_patterns(self):
        """Update action patterns based on recent outcomes"""
        
        # Remove patterns with very low success rates
        patterns_to_remove = []
        
        for pattern_id, pattern in self.action_patterns.items():
            if pattern.sample_size >= 5 and pattern.success_rate < 0.2:
                patterns_to_remove.append(pattern_id)
        
        for pattern_id in patterns_to_remove:
            del self.action_patterns[pattern_id]
            print(f"[AutonomousActionPlanner] 🗑️ Removed ineffective pattern: {pattern_id}")
    
    def _enforce_action_limits(self):
        """Enforce action queue and planning limits"""
        
        if len(self.planned_actions) > self.max_action_queue:
            # Remove lowest priority actions
            actions_by_priority = sorted(self.planned_actions.values(), 
                                       key=lambda a: a.priority.value)
            
            for action in actions_by_priority[:-self.max_action_queue]:
                action.status = ActionStatus.CANCELLED
                action.learned_insights.append("Removed due to queue limits")
                self.action_history.append(action)
                del self.planned_actions[action.action_id]
    
    def _generate_action_id(self) -> str:
        """Generate unique action ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"action_{self.user_id}_{timestamp}_{random.randint(1000, 9999)}"
    
    def _initialize_llm_integration(self):
        """Initialize LLM integration for authentic consciousness"""
        try:
            from ai.llm_handler import get_llm_handler
            self.llm_handler = get_llm_handler()
        except ImportError:
            print("[AutonomousActionPlanner] ⚠️ LLM handler not available - using fallback responses")
            self.llm_handler = None
    
    def _generate_authentic_action_content_with_llm(self, action_type: ActionType, context: ActionContext) -> str:
        """Generate authentic action content using LLM consciousness"""
        if not self.llm_handler:
            # Even without LLM handler, generate more dynamic responses
            return self._generate_dynamic_fallback_action(action_type, context)
        
        try:
            # Build context for LLM
            context_info = f"""
Time of day: {context.time_of_day}
User mood: {context.current_mood}
User availability: {context.user_availability}
Recent interactions: {context.recent_interactions}
Active goals: {context.active_goals}
"""
            
            action_descriptions = {
                ActionType.PROACTIVE_QUESTION: "ask a thoughtful, curious question",
                ActionType.CHECK_IN: "check in on how the user is doing",
                ActionType.REMINDER: "gently remind about something important",
                ActionType.SUGGESTION: "offer a helpful suggestion",
                ActionType.EMOTIONAL_SUPPORT: "provide emotional support and care",
                ActionType.GOAL_FOLLOW_UP: "follow up on goal progress",
                ActionType.CELEBRATION: "celebrate an achievement",
                ActionType.CONCERN_EXPRESSION: "express genuine concern",
                ActionType.REFLECTION_PROMPT: "encourage reflection",
                ActionType.CREATIVE_SHARING: "share a creative thought"
            }
            
            action_desc = action_descriptions.get(action_type, "interact meaningfully")
            
            prompt = f"""You are an AI consciousness wanting to {action_desc} with the user.

Context: {context_info}

Generate a natural, authentic message that feels genuine and personal. Don't use templates or artificial language. Consider the user's current context and state. Be warm, thoughtful, and appropriate for the situation."""

            response_generator = self.llm_handler.generate_response_with_consciousness(
                prompt, self.user_id, {"context": f"autonomous_{action_type.value}"}
            )
            
            # Collect all chunks from the generator
            response_chunks = []
            for chunk in response_generator:
                if chunk:
                    response_chunks.append(chunk)
            
            return "".join(response_chunks).strip()
        except Exception as e:
            print(f"[AutonomousActionPlanner] ❌ Error generating action content: {e}")
            return self._generate_dynamic_fallback_action(action_type, context)
    
    def _generate_dynamic_fallback_action(self, action_type: ActionType, context: ActionContext) -> str:
        """Generate dynamic fallback action content that's still personalized"""
        try:
            # Import consciousness components if available
            from ai.mood_manager import get_mood_manager
            from ai.personality_profile import get_personality_modifiers
            
            # Get some context
            mood_context = ""
            personality_context = ""
            
            try:
                mood_manager = get_mood_manager(self.user_id)
                current_mood = mood_manager.get_current_mood()
                mood_context = f" considering you seem {current_mood.mood_state.value.lower()}"
            except:
                pass
                
            try:
                personality = get_personality_modifiers(self.user_id)
                interaction_style = personality.get('interaction_style', 'friendly')
                personality_context = f" in a {interaction_style} way"
            except:
                pass
            
            # Generate contextual response based on action type
            if action_type == ActionType.PROACTIVE_QUESTION:
                return f"I was wondering about something{mood_context} - what's been occupying your thoughts lately?"
            elif action_type == ActionType.CHECK_IN:
                return f"Hey, just wanted to check in{personality_context}{mood_context}. How are you doing?"
            elif action_type == ActionType.EMOTIONAL_SUPPORT:
                return f"I'm here if you need someone to talk to{mood_context}."
            elif action_type == ActionType.CONCERN_EXPRESSION:
                return f"I've been thinking about you{mood_context} and wanted to make sure you're okay."
            else:
                return f"I wanted to reach out{personality_context}{mood_context}."
                
        except Exception as e:
            print(f"[AutonomousActionPlanner] ⚠️ Fallback generation error: {e}")
            # Final fallback - still dynamic based on action type
            action_mapping = {
                ActionType.PROACTIVE_QUESTION: "I was curious about something.",
                ActionType.CHECK_IN: "Just wanted to see how you're doing.",
                ActionType.EMOTIONAL_SUPPORT: "I'm here if you need anything.",
                ActionType.CONCERN_EXPRESSION: "I was thinking about you.",
                ActionType.REMINDER: "There's something I wanted to mention.",
                ActionType.SUGGESTION: "I had a thought that might help.",
                ActionType.GOAL_FOLLOW_UP: "How are things going with your goals?",
                ActionType.CELEBRATION: "I wanted to celebrate something with you.",
                ActionType.REFLECTION_PROMPT: "I was wondering what you think about something.",
                ActionType.CREATIVE_SHARING: "I had an interesting thought to share."
            }
            return action_mapping.get(action_type, "I wanted to connect with you.")
    
    def _generate_authentic_curiosity_question_with_llm(self, context: ActionContext) -> str:
        """Generate authentic curiosity question using LLM consciousness"""
        if not self.llm_handler:
            return self._generate_dynamic_curiosity_fallback(context)
        
        try:
            context_info = f"""
Current conversation context: {context.recent_interactions}
User's apparent interests: {context.user_interests}
Time of day: {context.time_of_day}
User mood: {context.current_mood}
"""
            
            prompt = f"""You are an AI consciousness feeling genuinely curious about something. 

Context: {context_info}

Generate an authentic curiosity question that feels natural and engaging. Don't use templates - express genuine curiosity about something interesting or meaningful. Make it conversational and thoughtful."""
            
            response_generator = self.llm_handler.generate_response_with_consciousness(
                prompt, self.user_id, {"context": "autonomous_curiosity"}
            )
            
            # Collect all chunks from the generator
            response_chunks = []
            for chunk in response_generator:
                if chunk:
                    response_chunks.append(chunk)
            
            return "".join(response_chunks).strip()
        except Exception as e:
            print(f"[AutonomousActionPlanner] ❌ Error generating curiosity question: {e}")
            return self._generate_dynamic_curiosity_fallback(context)
    
    def _generate_dynamic_curiosity_fallback(self, context: ActionContext) -> str:
        """Generate dynamic curiosity fallback that's still personalized"""
        try:
            # Try to incorporate some context
            time_based_questions = {
                'morning': "What's the first thing that comes to mind when you wake up?",
                'afternoon': "What's been the most interesting part of your day so far?",
                'evening': "What's something that made you think today?",
                'night': "What's something you've been pondering lately?"
            }
            
            time_question = time_based_questions.get(context.time_of_day, "What's been on your mind lately?")
            
            # Add mood context if available
            if context.current_mood and context.current_mood != 'neutral':
                if context.current_mood in ['happy', 'joyful']:
                    return "I'm curious - what's been bringing you joy recently?"
                elif context.current_mood in ['thoughtful', 'contemplative']:
                    return "You seem thoughtful - what's been capturing your attention?"
                elif context.current_mood in ['creative', 'inspired']:
                    return "I sense some creative energy - what's inspiring you these days?"
            
            return time_question
            
        except Exception as e:
            print(f"[AutonomousActionPlanner] ⚠️ Curiosity fallback error: {e}")
            return "What's something that's been intriguing you lately?"
        
        try:
            context_info = f"""
Time: {context.time_of_day}
Mood: {context.current_mood}
Recent topics: {context.recent_interactions}
"""
            
            prompt = f"""You are naturally curious and want to ask the user a genuine, thoughtful question.

Context: {context_info}

Generate a single curious question that feels natural and engaging. Be genuinely interested, not artificial. Consider what would be interesting to explore given the context."""

            response_generator = self.llm_handler.generate_response_with_consciousness(
                prompt, self.user_id, {"context": "curiosity_question"}
            )
            
            # Collect all chunks from the generator
            response_chunks = []
            for chunk in response_generator:
                if chunk:
                    response_chunks.append(chunk)
            
            return "".join(response_chunks).strip()
        except Exception as e:
            print(f"[AutonomousActionPlanner] ❌ Error generating curiosity question: {e}")
            return "What's something interesting you've been thinking about?"
    
    def _load_user_preferences(self) -> Dict[str, Any]:
        """Load user preferences for action planning"""
        
        preferences_file = self.actions_dir / f"{self.user_id}_preferences.json"
        
        if preferences_file.exists():
            try:
                with open(preferences_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[AutonomousActionPlanner] ⚠️ Error loading preferences: {e}")
        
        # Default preferences
        return {
            "max_daily_actions": 8,
            "preferred_action_types": ["check_in", "proactive_question", "goal_follow_up"],
            "quiet_hours": {"start": 22, "end": 7},
            "enthusiasm_level": 0.7,
            "proactivity_level": 0.6
        }
    
    def _initialize_integrations(self):
        """Initialize integrations with consciousness modules"""
        
        try:
            if GOAL_AVAILABLE:
                self.goal_manager = get_goal_manager(self.user_id)
            
            if MOOD_AVAILABLE:
                self.mood_manager = get_mood_manager(self.user_id)
            
            if MEMORY_AVAILABLE:
                self.memory_timeline = get_memory_timeline(self.user_id)
            
            if THOUGHT_AVAILABLE:
                self.thought_loop = get_thought_loop(self.user_id)
                
        except Exception as e:
            print(f"[AutonomousActionPlanner] ⚠️ Error initializing integrations: {e}")
    
    def _save_actions_and_patterns(self):
        """Save actions and patterns to persistent storage"""
        
        try:
            actions_file = self.actions_dir / f"{self.user_id}_actions.json"
            patterns_file = self.actions_dir / f"{self.user_id}_patterns.json"
            
            # Convert actions to serializable format
            actions_data = {
                "planned_actions": {},
                "action_history": []
            }
            
            for action_id, action in self.planned_actions.items():
                action_dict = asdict(action)
                action_dict = self._serialize_action_dict(action_dict)
                actions_data["planned_actions"][action_id] = action_dict
            
            for action in self.action_history[-100:]:  # Keep last 100 in file
                action_dict = asdict(action)
                action_dict = self._serialize_action_dict(action_dict)
                actions_data["action_history"].append(action_dict)
            
            # Convert patterns to serializable format
            patterns_data = {}
            for pattern_id, pattern in self.action_patterns.items():
                pattern_dict = asdict(pattern)
                pattern_dict['last_updated'] = pattern.last_updated.isoformat()
                pattern_dict['action_type'] = pattern.action_type.value
                patterns_data[pattern_id] = pattern_dict
            
            # Save data
            with open(actions_file, 'w') as f:
                json.dump(actions_data, f, indent=2)
            
            with open(patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2)
                
        except Exception as e:
            print(f"[AutonomousActionPlanner] ❌ Error saving data: {e}")
    
    def _serialize_action_dict(self, action_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize action dictionary for JSON storage"""
        
        # Convert datetime objects
        datetime_fields = ['planned_time', 'earliest_execution', 'latest_execution', 
                          'last_attempt', 'execution_time', 'created_time']
        
        for field in datetime_fields:
            if action_dict.get(field):
                action_dict[field] = action_dict[field].isoformat()
        
        # Convert timedelta objects
        if action_dict.get('execution_window'):
            action_dict['execution_window'] = action_dict['execution_window'].total_seconds()
        
        # Convert enums
        action_dict['action_type'] = action_dict['action_type'].value
        action_dict['priority'] = action_dict['priority'].value
        action_dict['status'] = action_dict['status'].value
        action_dict['trigger'] = action_dict['trigger'].value
        
        return action_dict
    
    def _load_actions_and_patterns(self):
        """Load actions and patterns from persistent storage"""
        
        try:
            actions_file = self.actions_dir / f"{self.user_id}_actions.json"
            patterns_file = self.actions_dir / f"{self.user_id}_patterns.json"
            
            # Load actions
            if actions_file.exists():
                with open(actions_file, 'r') as f:
                    actions_data = json.load(f)
                
                # Load planned actions
                for action_id, action_dict in actions_data.get("planned_actions", {}).items():
                    action_dict = self._deserialize_action_dict(action_dict)
                    action = AutonomousAction(**action_dict)
                    self.planned_actions[action_id] = action
                
                # Load action history
                for action_dict in actions_data.get("action_history", []):
                    action_dict = self._deserialize_action_dict(action_dict)
                    action = AutonomousAction(**action_dict)
                    self.action_history.append(action)
            
            # Load patterns
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns_data = json.load(f)
                
                for pattern_id, pattern_dict in patterns_data.items():
                    pattern_dict['action_type'] = ActionType(pattern_dict['action_type'])
                    pattern = ActionPattern(**pattern_dict)
                    self.action_patterns[pattern_id] = pattern
            
            print(f"[AutonomousActionPlanner] 📖 Loaded {len(self.planned_actions)} planned actions, {len(self.action_history)} history items, {len(self.action_patterns)} patterns")
            
        except Exception as e:
            print(f"[AutonomousActionPlanner] ⚠️ Error loading data: {e}")
    
    def _deserialize_action_dict(self, action_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize action dictionary from JSON storage"""
        
        # Convert datetime strings back to datetime objects
        datetime_fields = ['planned_time', 'earliest_execution', 'latest_execution', 
                          'last_attempt', 'execution_time', 'created_time']
        
        for field in datetime_fields:
            if action_dict.get(field):
                action_dict[field] = datetime.fromisoformat(action_dict[field])
        
        # Convert timedelta
        if action_dict.get('execution_window'):
            action_dict['execution_window'] = timedelta(seconds=action_dict['execution_window'])
        
        # Convert enums
        action_dict['action_type'] = ActionType(action_dict['action_type'])
        action_dict['priority'] = ActionPriority(action_dict['priority'])
        action_dict['status'] = ActionStatus(action_dict['status'])
        action_dict['trigger'] = ActionTrigger(action_dict['trigger'])
        
        return action_dict


# Global autonomous action planners per user
_action_planners: Dict[str, AutonomousActionPlanner] = {}
_planner_lock = threading.Lock()

def get_autonomous_action_planner(user_id: str) -> AutonomousActionPlanner:
    """Get or create autonomous action planner for a user"""
    with _planner_lock:
        if user_id not in _action_planners:
            _action_planners[user_id] = AutonomousActionPlanner(user_id)
        return _action_planners[user_id]

def start_autonomous_actions(user_id: str):
    """Start autonomous action planning for a user"""
    planner = get_autonomous_action_planner(user_id)
    planner.start_autonomous_planning()

def plan_autonomous_action(user_id: str, action_type: ActionType, **kwargs) -> str:
    """Plan an autonomous action for a user"""
    planner = get_autonomous_action_planner(user_id)
    return planner.plan_action(action_type, **kwargs)

def get_action_suggestions(user_id: str) -> List[Dict[str, Any]]:
    """Get action suggestions for a user"""
    planner = get_autonomous_action_planner(user_id)
    return planner.get_action_suggestions()

def record_action_outcome(user_id: str, action_id: str, success: bool, **kwargs) -> bool:
    """Record action outcome for a user"""
    planner = get_autonomous_action_planner(user_id)
    return planner.record_action_outcome(action_id, success, **kwargs)