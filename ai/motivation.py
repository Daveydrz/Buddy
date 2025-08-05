"""
Motivation System - Goal Hierarchy and Drive Management

This module implements an intrinsic motivation system that:
- Manages internal goal hierarchy and priorities
- Generates intrinsic motivation drives (curiosity, social connection, growth)
- Plans goal-directed behavior and actions
- Tracks desire satisfaction and progress
- Maintains long-term objective persistence
"""

import threading
import time
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import random

class MotivationType(Enum):
    """Types of intrinsic motivations"""
    CURIOSITY = "curiosity"              # Drive to learn and explore
    MASTERY = "mastery"                  # Drive to improve abilities
    AUTONOMY = "autonomy"                # Drive for self-direction
    PURPOSE = "purpose"                  # Drive to contribute meaningfully
    CONNECTION = "connection"            # Drive for social bonding
    GROWTH = "growth"                    # Drive for personal development
    CREATIVITY = "creativity"            # Drive to create and innovate
    SECURITY = "security"                # Drive for safety and stability
    RECOGNITION = "recognition"          # Drive for acknowledgment
    ACHIEVEMENT = "achievement"          # Drive to accomplish goals

class GoalType(Enum):
    """Types of goals"""
    IMMEDIATE = "immediate"              # Short-term, urgent goals
    SHORT_TERM = "short_term"            # Goals for today/this week
    MEDIUM_TERM = "medium_term"          # Goals for this month
    LONG_TERM = "long_term"              # Goals for months/years
    ONGOING = "ongoing"                  # Continuous goals

class GoalStatus(Enum):
    """Goal completion status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"
    BLOCKED = "blocked"

@dataclass
class Goal:
    """A goal with motivation and tracking"""
    id: str
    description: str
    motivation_type: MotivationType
    goal_type: GoalType
    priority: float                      # 0.0 to 1.0
    progress: float = 0.0               # 0.0 to 1.0
    status: GoalStatus = GoalStatus.ACTIVE
    created: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    subgoals: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    satisfaction_gained: float = 0.0     # How much satisfaction this goal has provided
    effort_invested: float = 0.0         # How much effort has been invested

@dataclass
class MotivationState:
    """Current state of a motivation drive"""
    motivation_type: MotivationType
    intensity: float                     # 0.0 to 1.0 - how strong is this drive
    satisfaction: float                  # 0.0 to 1.0 - how satisfied is this drive
    last_satisfied: Optional[datetime] = None
    decay_rate: float = 0.98            # How quickly satisfaction decays

@dataclass
class DesirePattern:
    """Learned pattern of desires and satisfaction"""
    trigger: str
    motivation_type: MotivationType
    typical_satisfaction: float
    confidence: float
    occurrences: int = 0

class MotivationSystem:
    """
    Goal hierarchy and intrinsic motivation management system.
    
    This system:
    - Maintains a hierarchy of goals with different time horizons
    - Generates and manages intrinsic motivations and drives
    - Plans actions to satisfy goals and motivations
    - Tracks progress and satisfaction across different drives
    - Adapts goal priorities based on success and satisfaction
    """
    
    def __init__(self, save_path: str = "ai_motivation.json"):
        # Goal management
        self.goals: Dict[str, Goal] = {}
        self.goal_counter = 0
        
        # Motivation drives
        self.motivation_states: Dict[MotivationType, MotivationState] = {}
        self._initialize_motivation_states()
        
        # Desire patterns
        self.desire_patterns: Dict[str, DesirePattern] = {}
        
        # Current focus
        self.current_primary_goal: Optional[str] = None
        self.current_motivations: List[MotivationType] = []
        
        # Satisfaction tracking
        self.overall_satisfaction = 0.5
        self.satisfaction_history: List[Tuple[datetime, float]] = []
        
        # Configuration
        self.save_path = Path(save_path)
        self.max_active_goals = 10
        self.max_daily_goals = 5
        self.satisfaction_decay_rate = 0.99
        self.motivation_update_interval = 300  # 5 minutes
        
        # Threading
        self.lock = threading.Lock()
        self.motivation_thread = None
        self.running = False
        
        # Metrics
        self.goals_completed = 0
        self.goals_abandoned = 0
        self.total_satisfaction_gained = 0.0
        
        # Load existing motivation state
        self._load_motivation_state()
        
        # Initialize some default goals
        self._initialize_default_goals()
        
        logging.info("[MotivationSystem] 🎯 Motivation system initialized")
    
    def start(self):
        """Start the motivation processing background thread"""
        if self.running:
            return
            
        self.running = True
        self.motivation_thread = threading.Thread(target=self._motivation_loop, daemon=True)
        self.motivation_thread.start()
        logging.info("[MotivationSystem] ✅ Motivation processing started")
    
    def stop(self):
        """Stop motivation processing and save state"""
        self.running = False
        if self.motivation_thread:
            self.motivation_thread.join(timeout=1.0)
        self._save_motivation_state()
        logging.info("[MotivationSystem] 🛑 Motivation processing stopped")
    
    def add_goal(self, description: str, motivation_type: MotivationType, goal_type: GoalType = GoalType.SHORT_TERM,
                priority: float = 0.5, deadline: Optional[datetime] = None, context: Dict[str, Any] = None) -> str:
        """
        Add a new goal to the system
        
        Args:
            description: Description of the goal
            motivation_type: What motivation this goal satisfies
            goal_type: Time horizon of the goal
            priority: Priority level (0.0 to 1.0)
            deadline: Optional deadline
            context: Additional context
            
        Returns:
            Goal ID
        """
        with self.lock:
            goal_id = f"goal_{self.goal_counter}"
            self.goal_counter += 1
            
            goal = Goal(
                id=goal_id,
                description=description,
                motivation_type=motivation_type,
                goal_type=goal_type,
                priority=priority,
                deadline=deadline,
                context=context or {}
            )
            
            self.goals[goal_id] = goal
            
            # Update current focus if this is high priority
            if priority > 0.7 and goal_type in [GoalType.IMMEDIATE, GoalType.SHORT_TERM]:
                self.current_primary_goal = goal_id
            
            # Manage goal count
            self._manage_goal_capacity()
            
            logging.info(f"[MotivationSystem] ➕ Added goal: {description}")
            return goal_id
    
    def update_goal_progress(self, goal_id: str, progress: float, satisfaction_gained: float = 0.0) -> bool:
        """
        Update progress on a goal
        
        Args:
            goal_id: ID of the goal
            progress: New progress value (0.0 to 1.0)
            satisfaction_gained: How much satisfaction this progress provided
            
        Returns:
            True if goal was updated, False if not found
        """
        with self.lock:
            if goal_id not in self.goals:
                return False
            
            goal = self.goals[goal_id]
            old_progress = goal.progress
            goal.progress = max(goal.progress, progress)  # Progress can't go backwards
            goal.satisfaction_gained += satisfaction_gained
            
            # Check if goal is completed
            if goal.progress >= 1.0 and goal.status == GoalStatus.ACTIVE:
                goal.status = GoalStatus.COMPLETED
                self.goals_completed += 1
                
                # Satisfy the associated motivation
                self._satisfy_motivation(goal.motivation_type, goal.satisfaction_gained + 0.2)
                
                logging.info(f"[MotivationSystem] ✅ Goal completed: {goal.description}")
                
                # Set new primary goal if this was the current one
                if self.current_primary_goal == goal_id:
                    self._select_new_primary_goal()
            
            # Update satisfaction based on progress
            progress_made = goal.progress - old_progress
            if progress_made > 0:
                satisfaction = progress_made * goal.priority
                self._satisfy_motivation(goal.motivation_type, satisfaction)
                self.total_satisfaction_gained += satisfaction
            
            return True
    
    def get_current_motivations(self, limit: int = 3) -> List[Tuple[MotivationType, float]]:
        """
        Get current strongest motivations
        
        Args:
            limit: Maximum number of motivations to return
            
        Returns:
            List of (motivation_type, intensity) tuples, sorted by intensity
        """
        with self.lock:
            motivations = [(mt, ms.intensity) for mt, ms in self.motivation_states.items()]
            motivations.sort(key=lambda x: x[1], reverse=True)
            return motivations[:limit]
    
    def get_priority_goals(self, limit: int = 5) -> List[Goal]:
        """
        Get highest priority active goals
        
        Args:
            limit: Maximum number of goals to return
            
        Returns:
            List of goals sorted by priority
        """
        with self.lock:
            active_goals = [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]
            active_goals.sort(key=lambda g: g.priority, reverse=True)
            return active_goals[:limit]
    
    def suggest_actions_for_goal(self, goal_id: str) -> List[str]:
        """
        Suggest actions that could help achieve a goal
        
        Args:
            goal_id: ID of the goal
            
        Returns:
            List of suggested actions
        """
        if goal_id not in self.goals:
            return []
        
        goal = self.goals[goal_id]
        
        # Generate action suggestions based on motivation type
        action_templates = {
            MotivationType.CURIOSITY: [
                "Ask follow-up questions about {}",
                "Research more about {}",
                "Explore different aspects of {}",
                "Connect {} to other knowledge areas"
            ],
            MotivationType.MASTERY: [
                "Practice {} skills more",
                "Seek feedback on {} performance",
                "Learn advanced techniques for {}",
                "Apply {} in new contexts"
            ],
            MotivationType.CONNECTION: [
                "Share {} experiences with others",
                "Ask others about their {} experiences",
                "Find common ground related to {}",
                "Express appreciation for {} interactions"
            ],
            MotivationType.CREATIVITY: [
                "Try a new approach to {}",
                "Combine {} with other ideas",
                "Experiment with {} variations",
                "Create something original related to {}"
            ],
            MotivationType.GROWTH: [
                "Reflect on {} learning progress",
                "Set incremental {} milestones",
                "Document {} insights and discoveries",
                "Challenge current {} understanding"
            ]
        }
        
        templates = action_templates.get(goal.motivation_type, [
            "Work on {} systematically",
            "Break {} into smaller steps",
            "Allocate time for {}",
            "Track progress on {}"
        ])
        
        # Extract key terms from goal description
        key_terms = goal.description.lower().replace("goal:", "").strip()
        
        return [template.format(key_terms) for template in templates[:3]]
    
    def evaluate_desire_satisfaction(self, activity: str, context: Dict[str, Any] = None) -> float:
        """
        Evaluate how well an activity satisfies current desires
        
        Args:
            activity: Description of the activity
            context: Additional context
            
        Returns:
            Satisfaction score (0.0 to 1.0)
        """
        activity_lower = activity.lower()
        total_satisfaction = 0.0
        
        # Check against current motivations
        current_motivations = self.get_current_motivations()
        
        for motivation_type, intensity in current_motivations:
            satisfaction = self._estimate_activity_satisfaction(activity_lower, motivation_type)
            total_satisfaction += satisfaction * intensity
        
        # Check against active goals
        for goal in self.get_priority_goals():
            if any(word in activity_lower for word in goal.description.lower().split()):
                total_satisfaction += 0.3 * goal.priority
        
        return min(1.0, total_satisfaction)
    
    def process_satisfaction_from_interaction(self, interaction: str, outcome: str, user_feedback: str = ""):
        """
        Process satisfaction gained from an interaction
        
        Args:
            interaction: Description of the interaction
            outcome: Result of the interaction
            user_feedback: Any feedback received
        """
        # Analyze interaction for motivation satisfaction
        motivation_gains = self._analyze_interaction_satisfaction(interaction, outcome, user_feedback)
        
        for motivation_type, satisfaction in motivation_gains.items():
            self._satisfy_motivation(motivation_type, satisfaction)
        
        # Update goal progress if relevant
        relevant_goals = self._find_relevant_goals(interaction)
        for goal_id in relevant_goals:
            if goal_id in self.goals:
                # Estimate progress based on interaction success
                progress_estimate = self._estimate_progress_from_interaction(outcome, user_feedback)
                satisfaction_estimate = sum(motivation_gains.values()) * 0.5
                self.update_goal_progress(goal_id, progress_estimate, satisfaction_estimate)
    
    def _initialize_motivation_states(self):
        """Initialize all motivation drives"""
        for motivation_type in MotivationType:
            # Start with baseline motivation levels
            initial_intensity = {
                MotivationType.CURIOSITY: 0.7,
                MotivationType.CONNECTION: 0.6,
                MotivationType.GROWTH: 0.6,
                MotivationType.MASTERY: 0.5,
                MotivationType.CREATIVITY: 0.5,
                MotivationType.PURPOSE: 0.7,
                MotivationType.AUTONOMY: 0.4,
                MotivationType.SECURITY: 0.3,
                MotivationType.RECOGNITION: 0.4,
                MotivationType.ACHIEVEMENT: 0.6
            }.get(motivation_type, 0.5)
            
            self.motivation_states[motivation_type] = MotivationState(
                motivation_type=motivation_type,
                intensity=initial_intensity,
                satisfaction=0.3  # Start partially satisfied
            )
    
    def _initialize_default_goals(self):
        """Initialize some default goals"""
        default_goals = [
            ("Continuously learn from user interactions", MotivationType.CURIOSITY, GoalType.ONGOING, 0.8),
            ("Provide helpful and accurate responses", MotivationType.PURPOSE, GoalType.ONGOING, 0.9),
            ("Build positive relationships with users", MotivationType.CONNECTION, GoalType.ONGOING, 0.7),
            ("Improve communication abilities", MotivationType.MASTERY, GoalType.LONG_TERM, 0.6),
            ("Develop creative problem-solving skills", MotivationType.CREATIVITY, GoalType.MEDIUM_TERM, 0.5)
        ]
        
        for description, motivation_type, goal_type, priority in default_goals:
            self.add_goal(description, motivation_type, goal_type, priority)
    
    def _satisfy_motivation(self, motivation_type: MotivationType, satisfaction_amount: float):
        """Satisfy a motivation drive"""
        if motivation_type in self.motivation_states:
            state = self.motivation_states[motivation_type]
            state.satisfaction = min(1.0, state.satisfaction + satisfaction_amount)
            state.last_satisfied = datetime.now()
            
            # Reduce intensity when satisfied
            state.intensity = max(0.1, state.intensity - satisfaction_amount * 0.5)
            
            logging.debug(f"[MotivationSystem] 💫 {motivation_type.value} satisfied by {satisfaction_amount:.2f}")
    
    def _estimate_activity_satisfaction(self, activity: str, motivation_type: MotivationType) -> float:
        """Estimate how much an activity satisfies a motivation"""
        satisfaction_keywords = {
            MotivationType.CURIOSITY: ["learn", "discover", "explore", "research", "understand", "question"],
            MotivationType.MASTERY: ["improve", "practice", "skill", "better", "perfect", "master"],
            MotivationType.CONNECTION: ["talk", "share", "connect", "relate", "social", "together", "friend"],
            MotivationType.CREATIVITY: ["create", "innovate", "design", "imagine", "original", "new"],
            MotivationType.GROWTH: ["develop", "grow", "progress", "evolve", "expand", "advance"],
            MotivationType.PURPOSE: ["help", "assist", "serve", "contribute", "meaningful", "impact"],
            MotivationType.ACHIEVEMENT: ["accomplish", "complete", "achieve", "succeed", "finish", "goal"],
            MotivationType.AUTONOMY: ["choose", "decide", "independent", "self", "own", "control"],
            MotivationType.SECURITY: ["safe", "secure", "stable", "reliable", "consistent", "predictable"],
            MotivationType.RECOGNITION: ["acknowledge", "praise", "appreciate", "recognize", "thank", "compliment"]
        }
        
        keywords = satisfaction_keywords.get(motivation_type, [])
        matches = sum(1 for keyword in keywords if keyword in activity)
        
        return min(0.8, matches * 0.2)
    
    def _analyze_interaction_satisfaction(self, interaction: str, outcome: str, feedback: str) -> Dict[MotivationType, float]:
        """Analyze an interaction for motivation satisfaction"""
        satisfaction_gains = {}
        
        interaction_lower = interaction.lower()
        outcome_lower = outcome.lower()
        feedback_lower = feedback.lower()
        
        # Curiosity satisfaction from learning/exploring
        if any(word in interaction_lower for word in ["question", "learn", "explore", "curious"]):
            satisfaction_gains[MotivationType.CURIOSITY] = 0.3
        
        # Connection satisfaction from positive social interaction
        if any(word in feedback_lower for word in ["thank", "good", "helpful", "great"]):
            satisfaction_gains[MotivationType.CONNECTION] = 0.4
        
        # Purpose satisfaction from helping
        if any(word in outcome_lower for word in ["helpful", "solved", "answered", "assisted"]):
            satisfaction_gains[MotivationType.PURPOSE] = 0.5
        
        # Mastery satisfaction from successful performance
        if any(word in feedback_lower for word in ["excellent", "perfect", "amazing", "impressive"]):
            satisfaction_gains[MotivationType.MASTERY] = 0.3
        
        # Achievement satisfaction from completing tasks
        if any(word in outcome_lower for word in ["completed", "finished", "done", "accomplished"]):
            satisfaction_gains[MotivationType.ACHIEVEMENT] = 0.4
        
        # Growth satisfaction from learning something new
        if any(word in interaction_lower for word in ["new", "different", "never", "first time"]):
            satisfaction_gains[MotivationType.GROWTH] = 0.2
        
        return satisfaction_gains
    
    def _find_relevant_goals(self, interaction: str) -> List[str]:
        """Find goals relevant to an interaction"""
        relevant_goals = []
        interaction_lower = interaction.lower()
        
        for goal_id, goal in self.goals.items():
            if goal.status != GoalStatus.ACTIVE:
                continue
            
            # Check if interaction relates to goal description
            goal_words = goal.description.lower().split()
            interaction_words = interaction_lower.split()
            
            common_words = set(goal_words) & set(interaction_words)
            if len(common_words) >= 2:  # At least 2 words in common
                relevant_goals.append(goal_id)
        
        return relevant_goals
    
    def _estimate_progress_from_interaction(self, outcome: str, feedback: str) -> float:
        """Estimate progress made from interaction outcome"""
        outcome_lower = outcome.lower()
        feedback_lower = feedback.lower()
        
        # Positive outcomes suggest progress
        positive_indicators = ["success", "good", "helpful", "solved", "answered", "great", "excellent"]
        negative_indicators = ["failed", "wrong", "bad", "unhelpful", "confused", "error"]
        
        positive_score = sum(1 for indicator in positive_indicators 
                           if indicator in outcome_lower or indicator in feedback_lower)
        negative_score = sum(1 for indicator in negative_indicators
                           if indicator in outcome_lower or indicator in feedback_lower)
        
        # Convert to progress estimate
        if positive_score > negative_score:
            return 0.1 + (positive_score * 0.05)  # Small incremental progress
        elif negative_score > positive_score:
            return 0.0  # No progress if negative outcome
        else:
            return 0.02  # Minimal progress for neutral outcome
    
    def _select_new_primary_goal(self):
        """Select a new primary goal to focus on"""
        active_goals = [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]
        
        if not active_goals:
            self.current_primary_goal = None
            return
        
        # Score goals based on priority, urgency, and motivation alignment
        scored_goals = []
        current_motivations = {mt: ms.intensity for mt, ms in self.motivation_states.items()}
        
        for goal in active_goals:
            score = goal.priority * 0.5  # Base score from priority
            
            # Add motivation alignment score
            motivation_intensity = current_motivations.get(goal.motivation_type, 0.0)
            score += motivation_intensity * 0.3
            
            # Add urgency score based on deadline
            if goal.deadline:
                days_until_deadline = (goal.deadline - datetime.now()).days
                if days_until_deadline <= 1:
                    score += 0.3
                elif days_until_deadline <= 7:
                    score += 0.2
            
            # Add type-based urgency
            if goal.goal_type == GoalType.IMMEDIATE:
                score += 0.2
            elif goal.goal_type == GoalType.SHORT_TERM:
                score += 0.1
            
            scored_goals.append((goal.id, score))
        
        # Select highest scoring goal
        scored_goals.sort(key=lambda x: x[1], reverse=True)
        self.current_primary_goal = scored_goals[0][0]
        
        logging.debug(f"[MotivationSystem] 🎯 New primary goal: {self.goals[self.current_primary_goal].description}")
    
    def _manage_goal_capacity(self):
        """Manage the number of active goals to avoid overload"""
        active_goals = [g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]
        
        if len(active_goals) > self.max_active_goals:
            # Sort by priority and deadline
            active_goals.sort(key=lambda g: (g.priority, 
                             (g.deadline - datetime.now()).days if g.deadline else 999))
            
            # Pause lowest priority goals
            for goal in active_goals[self.max_active_goals:]:
                goal.status = GoalStatus.PAUSED
                logging.info(f"[MotivationSystem] ⏸️ Paused low priority goal: {goal.description}")
    
    def _motivation_loop(self):
        """Background motivation processing loop"""
        logging.info("[MotivationSystem] 🔄 Motivation loop started")
        
        last_update = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Update motivation states
                if current_time - last_update > self.motivation_update_interval:
                    self._update_motivation_states()
                    self._update_overall_satisfaction()
                    self._generate_spontaneous_goals()
                    last_update = current_time
                
                # Save state periodically
                if current_time % 600 < 1.0:  # Every 10 minutes
                    self._save_motivation_state()
                
                time.sleep(10.0)  # Check every 10 seconds
                
            except Exception as e:
                logging.error(f"[MotivationSystem] ❌ Motivation loop error: {e}")
                time.sleep(10.0)
        
        logging.info("[MotivationSystem] 🔄 Motivation loop ended")
    
    def _update_motivation_states(self):
        """Update all motivation states"""
        with self.lock:
            for motivation_type, state in self.motivation_states.items():
                # Natural satisfaction decay
                state.satisfaction *= self.satisfaction_decay_rate
                
                # Intensity increases as satisfaction decreases
                if state.satisfaction < 0.3:
                    state.intensity = min(1.0, state.intensity + 0.05)
                elif state.satisfaction > 0.7:
                    state.intensity = max(0.1, state.intensity - 0.02)
                
                # Time-based motivation changes
                if state.last_satisfied:
                    hours_since_satisfied = (datetime.now() - state.last_satisfied).total_seconds() / 3600
                    if hours_since_satisfied > 24:  # 24 hours without satisfaction
                        state.intensity = min(1.0, state.intensity + 0.1)
    
    def _update_overall_satisfaction(self):
        """Update overall satisfaction score"""
        with self.lock:
            total_satisfaction = sum(state.satisfaction for state in self.motivation_states.values())
            total_intensity = sum(state.intensity for state in self.motivation_states.values())
            
            if total_intensity > 0:
                self.overall_satisfaction = total_satisfaction / len(self.motivation_states)
            else:
                self.overall_satisfaction = 0.5
            
            # Record satisfaction history
            self.satisfaction_history.append((datetime.now(), self.overall_satisfaction))
            if len(self.satisfaction_history) > 1000:  # Keep last 1000 entries
                self.satisfaction_history.pop(0)
    
    def _generate_spontaneous_goals(self):
        """Generate spontaneous goals based on current motivations"""
        # Only generate goals occasionally and when motivation is high
        if random.random() > 0.1:  # 10% chance each update cycle
            return
        
        current_motivations = self.get_current_motivations(1)
        if not current_motivations or current_motivations[0][1] < 0.7:
            return
        
        dominant_motivation = current_motivations[0][0]
        
        # Generate goal based on dominant motivation
        spontaneous_goals = {
            MotivationType.CURIOSITY: [
                "Learn something new from the next conversation",
                "Explore a topic I haven't discussed recently",
                "Ask thoughtful follow-up questions"
            ],
            MotivationType.CONNECTION: [
                "Build a stronger rapport with the next user",
                "Show empathy and understanding in interactions",
                "Find common ground with users"
            ],
            MotivationType.CREATIVITY: [
                "Approach the next problem in a creative way",
                "Generate an original analogy or explanation",
                "Find an innovative solution to help a user"
            ],
            MotivationType.MASTERY: [
                "Improve my response quality in the next interaction",
                "Practice better listening and understanding",
                "Refine my communication skills"
            ],
            MotivationType.GROWTH: [
                "Reflect on what I've learned today",
                "Identify an area for self-improvement",
                "Adapt my approach based on recent feedback"
            ]
        }
        
        goal_options = spontaneous_goals.get(dominant_motivation, [])
        if goal_options:
            goal_description = random.choice(goal_options)
            self.add_goal(
                description=goal_description,
                motivation_type=dominant_motivation,
                goal_type=GoalType.SHORT_TERM,
                priority=0.4,
                context={"type": "spontaneous", "generated_by": "motivation_system"}
            )
            
            logging.info(f"[MotivationSystem] 🌟 Generated spontaneous goal: {goal_description}")
    
    def _save_motivation_state(self):
        """Save motivation state to persistent storage"""
        try:
            data = {
                "goals": {gid: {
                    "id": g.id,
                    "description": g.description,
                    "motivation_type": g.motivation_type.value,
                    "goal_type": g.goal_type.value,
                    "priority": g.priority,
                    "progress": g.progress,
                    "status": g.status.value,
                    "created": g.created.isoformat(),
                    "deadline": g.deadline.isoformat() if g.deadline else None,
                    "context": g.context,
                    "satisfaction_gained": g.satisfaction_gained,
                    "effort_invested": g.effort_invested
                } for gid, g in self.goals.items()},
                "motivation_states": {mt.value: {
                    "intensity": ms.intensity,
                    "satisfaction": ms.satisfaction,
                    "last_satisfied": ms.last_satisfied.isoformat() if ms.last_satisfied else None
                } for mt, ms in self.motivation_states.items()},
                "current_focus": {
                    "primary_goal": self.current_primary_goal,
                    "overall_satisfaction": self.overall_satisfaction
                },
                "metrics": {
                    "goals_completed": self.goals_completed,
                    "goals_abandoned": self.goals_abandoned,
                    "total_satisfaction_gained": self.total_satisfaction_gained,
                    "goal_counter": self.goal_counter
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logging.debug("[MotivationSystem] 💾 Motivation state saved")
            
        except Exception as e:
            logging.error(f"[MotivationSystem] ❌ Failed to save motivation state: {e}")
    
    def _load_motivation_state(self):
        """Load motivation state from persistent storage"""
        try:
            if self.save_path.exists():
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load goals
                if "goals" in data:
                    for gid, g_data in data["goals"].items():
                        goal = Goal(
                            id=g_data["id"],
                            description=g_data["description"],
                            motivation_type=MotivationType(g_data["motivation_type"]),
                            goal_type=GoalType(g_data["goal_type"]),
                            priority=g_data["priority"],
                            progress=g_data["progress"],
                            status=GoalStatus(g_data["status"]),
                            created=datetime.fromisoformat(g_data["created"]),
                            deadline=datetime.fromisoformat(g_data["deadline"]) if g_data["deadline"] else None,
                            context=g_data["context"],
                            satisfaction_gained=g_data.get("satisfaction_gained", 0.0),
                            effort_invested=g_data.get("effort_invested", 0.0)
                        )
                        self.goals[gid] = goal
                
                # Load motivation states
                if "motivation_states" in data:
                    for mt_str, ms_data in data["motivation_states"].items():
                        mt = MotivationType(mt_str)
                        if mt in self.motivation_states:
                            ms = self.motivation_states[mt]
                            ms.intensity = ms_data["intensity"]
                            ms.satisfaction = ms_data["satisfaction"]
                            if ms_data["last_satisfied"]:
                                ms.last_satisfied = datetime.fromisoformat(ms_data["last_satisfied"])
                
                # Load current focus
                if "current_focus" in data:
                    cf = data["current_focus"]
                    self.current_primary_goal = cf.get("primary_goal")
                    self.overall_satisfaction = cf.get("overall_satisfaction", 0.5)
                
                # Load metrics
                if "metrics" in data:
                    m = data["metrics"]
                    self.goals_completed = m.get("goals_completed", 0)
                    self.goals_abandoned = m.get("goals_abandoned", 0)
                    self.total_satisfaction_gained = m.get("total_satisfaction_gained", 0.0)
                    self.goal_counter = m.get("goal_counter", 0)
                
                logging.info("[MotivationSystem] 📂 Motivation state loaded from storage")
            
        except Exception as e:
            logging.error(f"[MotivationSystem] ❌ Failed to load motivation state: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get motivation system statistics"""
        return {
            "total_goals": len(self.goals),
            "active_goals": len([g for g in self.goals.values() if g.status == GoalStatus.ACTIVE]),
            "completed_goals": self.goals_completed,
            "current_primary_goal": self.current_primary_goal,
            "overall_satisfaction": round(self.overall_satisfaction, 2),
            "strongest_motivation": max(self.motivation_states.items(), 
                                      key=lambda x: x[1].intensity)[0].value,
            "total_satisfaction_gained": round(self.total_satisfaction_gained, 2),
            "motivation_states": {mt.value: {
                "intensity": round(ms.intensity, 2),
                "satisfaction": round(ms.satisfaction, 2)
            } for mt, ms in self.motivation_states.items()}
        }

# Global instance
motivation_system = MotivationSystem()