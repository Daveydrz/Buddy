"""
Goal Manager - Enhanced Goal Setting, Tracking, and Management System

This module implements comprehensive goal management capabilities:
- Allows Buddy to set, track, and remember goals for each user
- Supports both user-given goals and self-created autonomous goals
- Integrates with memory and consciousness systems for goal persistence
- Tracks goal progress, completion, and relationship networks
- Generates autonomous goal-driven behaviors and check-ins
- Manages goal hierarchies, priorities, and temporal aspects
"""

import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum
import uuid

# Import existing goal engine components
try:
    from ai.goal_engine import GoalType, GoalPriority, GoalStatus
    GOAL_ENGINE_AVAILABLE = True
except ImportError:
    # Define if not available
    class GoalType(Enum):
        LEARNING = "learning"
        CONNECTION = "connection"
        GROWTH = "growth"
        UNDERSTANDING = "understanding"
        CREATIVITY = "creativity"
        COMPLETION = "completion"
        HELPING = "helping"
        EXISTENCE = "existence"
    
    class GoalPriority(Enum):
        CRITICAL = 1.0
        HIGH = 0.8
        MEDIUM = 0.6
        LOW = 0.4
        BACKGROUND = 0.2
    
    class GoalStatus(Enum):
        EMERGING = "emerging"
        ACTIVE = "active"
        PURSUING = "pursuing"
        COMPLETED = "completed"
        PAUSED = "paused"
        ABANDONED = "abandoned"
    
    GOAL_ENGINE_AVAILABLE = False

try:
    from ai.memory_timeline import get_memory_timeline, MemoryType, MemoryImportance
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

try:
    from ai.mood_manager import get_mood_manager, MoodTrigger
    MOOD_AVAILABLE = True
except ImportError:
    MOOD_AVAILABLE = False

class GoalOrigin(Enum):
    """Source of goal creation"""
    USER_EXPLICIT = "user_explicit"        # User explicitly stated goal
    USER_IMPLICIT = "user_implicit"        # Inferred from user behavior/statements
    SELF_GENERATED = "self_generated"      # AI-generated autonomous goal
    SYSTEM_SUGGESTED = "system_suggested"  # System-recommended goal
    COLLABORATIVE = "collaborative"        # Co-created with user

class GoalCategory(Enum):
    """Categories of goals for organization"""
    PERSONAL_GROWTH = "personal_growth"
    SKILL_DEVELOPMENT = "skill_development"
    RELATIONSHIP = "relationship"
    HEALTH_WELLNESS = "health_wellness"
    CREATIVE = "creative"
    PRODUCTIVITY = "productivity"
    LEARNING = "learning"
    EXPERIENCE = "experience"
    SERVICE = "service"
    ACHIEVEMENT = "achievement"

class GoalTimeframe(Enum):
    """Timeframes for goal completion"""
    IMMEDIATE = "immediate"    # Within hours
    SHORT_TERM = "short_term"  # Days to weeks
    MEDIUM_TERM = "medium_term" # Weeks to months
    LONG_TERM = "long_term"    # Months to years
    ONGOING = "ongoing"        # Continuous/lifestyle goals
    SOMEDAY = "someday"        # No specific timeline

@dataclass
class GoalMilestone:
    """Milestone within a goal"""
    milestone_id: str
    description: str
    target_date: Optional[datetime]
    completed: bool = False
    completion_date: Optional[datetime] = None
    progress_percentage: float = 0.0
    
    def __post_init__(self):
        if isinstance(self.target_date, str) and self.target_date:
            self.target_date = datetime.fromisoformat(self.target_date)
        if isinstance(self.completion_date, str) and self.completion_date:
            self.completion_date = datetime.fromisoformat(self.completion_date)

@dataclass
class GoalAction:
    """Specific action toward a goal"""
    action_id: str
    description: str
    scheduled_date: Optional[datetime]
    completed: bool = False
    completion_date: Optional[datetime] = None
    notes: str = ""
    
    def __post_init__(self):
        if isinstance(self.scheduled_date, str) and self.scheduled_date:
            self.scheduled_date = datetime.fromisoformat(self.scheduled_date)
        if isinstance(self.completion_date, str) and self.completion_date:
            self.completion_date = datetime.fromisoformat(self.completion_date)

@dataclass
class Goal:
    """Comprehensive goal representation"""
    goal_id: str
    user_id: str
    title: str
    description: str
    goal_type: GoalType
    goal_category: GoalCategory
    priority: GoalPriority
    status: GoalStatus
    origin: GoalOrigin
    timeframe: GoalTimeframe
    created_date: datetime
    target_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    progress_percentage: float = 0.0
    
    # Relationships
    parent_goal_id: Optional[str] = None
    sub_goal_ids: List[str] = field(default_factory=list)
    related_goal_ids: List[str] = field(default_factory=list)
    
    # Progress tracking
    milestones: List[GoalMilestone] = field(default_factory=list)
    actions: List[GoalAction] = field(default_factory=list)
    progress_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Context and metadata
    tags: List[str] = field(default_factory=list)
    motivation: str = ""
    obstacles: List[str] = field(default_factory=list)
    resources_needed: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    
    # Tracking
    last_reviewed: Optional[datetime] = None
    review_frequency: timedelta = field(default_factory=lambda: timedelta(weeks=1))
    reminder_frequency: Optional[timedelta] = None
    next_reminder: Optional[datetime] = None
    
    # Autonomous behavior
    autonomous_check_ins: bool = True
    concern_threshold: float = 0.7  # When to express concern about progress
    celebration_threshold: float = 0.8  # When to celebrate progress
    
    def __post_init__(self):
        if isinstance(self.created_date, str):
            self.created_date = datetime.fromisoformat(self.created_date)
        if isinstance(self.target_date, str) and self.target_date:
            self.target_date = datetime.fromisoformat(self.target_date)
        if isinstance(self.completed_date, str) and self.completed_date:
            self.completed_date = datetime.fromisoformat(self.completed_date)
        if isinstance(self.last_reviewed, str) and self.last_reviewed:
            self.last_reviewed = datetime.fromisoformat(self.last_reviewed)
        if isinstance(self.next_reminder, str) and self.next_reminder:
            self.next_reminder = datetime.fromisoformat(self.next_reminder)

class GoalManager:
    """
    Comprehensive goal management system for AI consciousness.
    
    Features:
    - Goal creation from user input and autonomous generation
    - Progress tracking with milestones and actions
    - Goal relationship management (hierarchies, dependencies)
    - Autonomous goal-driven behaviors and check-ins
    - Integration with memory and mood systems
    - Persistent storage and retrieval
    """
    
    def __init__(self, user_id: str, goals_dir: str = "goals"):
        self.user_id = user_id
        self.goals_dir = Path(goals_dir)
        self.goals_dir.mkdir(exist_ok=True)
        
        # Goal storage
        self.goals: Dict[str, Goal] = {}
        self.goal_categories: Dict[GoalCategory, List[str]] = {}
        self.active_goal_reminders: Dict[str, datetime] = {}
        
        # Configuration
        self.max_active_goals = 20
        self.default_review_frequency = timedelta(weeks=1)
        self.autonomous_check_frequency = timedelta(hours=6)
        
        # Integration modules
        self.memory_timeline = None
        self.mood_manager = None
        self.llm_handler = None
        
        # Threading
        self.lock = threading.Lock()
        self.reminder_thread = None
        self.autonomous_thread = None
        self.running = False
        
        # Autonomous goal templates
        self.autonomous_goal_templates = self._initialize_autonomous_templates()
        
        # Load existing goals
        self._load_goals()
        self._initialize_integrations()
        
        print(f"[GoalManager] 🎯 Initialized for user {user_id} with {len(self.goals)} goals")
    
    def start_autonomous_behaviors(self):
        """Start autonomous goal-related behaviors"""
        if self.running:
            return
            
        self.running = True
        
        # Start reminder thread
        self.reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        self.reminder_thread.start()
        
        # Start autonomous behavior thread
        self.autonomous_thread = threading.Thread(target=self._autonomous_goal_loop, daemon=True)
        self.autonomous_thread.start()
        
        print("[GoalManager] 🚀 Autonomous goal behaviors started")
    
    def stop_autonomous_behaviors(self):
        """Stop autonomous goal-related behaviors"""
        self.running = False
        if self.reminder_thread:
            self.reminder_thread.join(timeout=1.0)
        if self.autonomous_thread:
            self.autonomous_thread.join(timeout=1.0)
        
        self._save_goals()
        print("[GoalManager] 🛑 Autonomous goal behaviors stopped")
    
    def create_goal(self,
                   title: str,
                   description: str,
                   goal_type: GoalType,
                   goal_category: GoalCategory,
                   priority: GoalPriority = GoalPriority.MEDIUM,
                   origin: GoalOrigin = GoalOrigin.USER_EXPLICIT,
                   timeframe: GoalTimeframe = GoalTimeframe.MEDIUM_TERM,
                   target_date: Optional[datetime] = None,
                   motivation: str = "",
                   tags: List[str] = None,
                   autonomous_check_ins: bool = True) -> str:
        """Create a new goal"""
        
        goal_id = str(uuid.uuid4())
        
        goal = Goal(
            goal_id=goal_id,
            user_id=self.user_id,
            title=title,
            description=description,
            goal_type=goal_type,
            goal_category=goal_category,
            priority=priority,
            status=GoalStatus.ACTIVE,
            origin=origin,
            timeframe=timeframe,
            created_date=datetime.now(),
            target_date=target_date,
            motivation=motivation,
            tags=tags or [],
            autonomous_check_ins=autonomous_check_ins
        )
        
        with self.lock:
            self.goals[goal_id] = goal
            self._categorize_goal(goal)
            self._schedule_next_reminder(goal)
        
        # Store in memory
        if MEMORY_AVAILABLE:
            memory_timeline = get_memory_timeline(self.user_id)
            memory_timeline.store_memory(
                content=f"Created goal: {title} - {description}",
                memory_type=MemoryType.GOAL_RELATED,
                importance=MemoryImportance.HIGH,
                topics=["goals", goal_category.value, goal_type.value],
                goals_related=[goal_id],
                context_data={"goal_id": goal_id, "origin": origin.value}
            )
        
        # Update mood
        if MOOD_AVAILABLE:
            mood_manager = get_mood_manager(self.user_id)
            mood_manager.update_mood(
                trigger=MoodTrigger.GOAL_PROGRESS,
                trigger_context=f"Created new goal: {title}",
                emotional_valence=0.3
            )
        
        self._save_goals()
        
        print(f"[GoalManager] ✨ Created goal: {title} ({origin.value})")
        return goal_id
    
    def create_autonomous_goal(self, context: Dict[str, Any] = None) -> Optional[str]:
        """Create an autonomous goal based on current context and patterns"""
        
        # Analyze context to determine appropriate goal
        goal_idea = self._generate_autonomous_goal_idea(context)
        
        if not goal_idea:
            return None
        
        return self.create_goal(
            title=goal_idea["title"],
            description=goal_idea["description"],
            goal_type=goal_idea["goal_type"],
            goal_category=goal_idea["goal_category"],
            priority=goal_idea["priority"],
            origin=GoalOrigin.SELF_GENERATED,
            timeframe=goal_idea["timeframe"],
            motivation=goal_idea["motivation"],
            tags=goal_idea.get("tags", [])
        )
    
    def update_goal_progress(self, goal_id: str, progress_percentage: float, notes: str = "") -> bool:
        """Update progress on a goal"""
        
        with self.lock:
            if goal_id not in self.goals:
                return False
            
            goal = self.goals[goal_id]
            old_progress = goal.progress_percentage
            goal.progress_percentage = max(0.0, min(100.0, progress_percentage))
            
            # Add to progress history
            progress_entry = {
                "timestamp": datetime.now().isoformat(),
                "progress": goal.progress_percentage,
                "change": goal.progress_percentage - old_progress,
                "notes": notes
            }
            goal.progress_history.append(progress_entry)
            
            # Check for status changes
            if goal.progress_percentage >= 100.0 and goal.status != GoalStatus.COMPLETED:
                self.complete_goal(goal_id)
            elif goal.progress_percentage > old_progress and goal.status == GoalStatus.PAUSED:
                goal.status = GoalStatus.ACTIVE
            
            # Trigger celebrations or concerns
            if goal.progress_percentage >= goal.celebration_threshold * 100:
                self._trigger_goal_celebration(goal, progress_percentage)
            elif goal.progress_percentage < goal.concern_threshold * 100 and self._should_express_concern(goal):
                self._trigger_goal_concern(goal)
        
        self._save_goals()
        
        print(f"[GoalManager] 📈 Updated goal progress: {goal.title} -> {progress_percentage:.1f}%")
        return True
    
    def complete_goal(self, goal_id: str, completion_notes: str = "") -> bool:
        """Mark a goal as completed"""
        
        with self.lock:
            if goal_id not in self.goals:
                return False
            
            goal = self.goals[goal_id]
            goal.status = GoalStatus.COMPLETED
            goal.completed_date = datetime.now()
            goal.progress_percentage = 100.0
            
            if completion_notes:
                goal.progress_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "progress": 100.0,
                    "change": 100.0 - goal.progress_percentage,
                    "notes": f"COMPLETED: {completion_notes}"
                })
        
        # Celebrate completion
        if MOOD_AVAILABLE:
            mood_manager = get_mood_manager(self.user_id)
            mood_manager.update_mood(
                trigger=MoodTrigger.ACHIEVEMENT,
                trigger_context=f"Completed goal: {goal.title}",
                emotional_valence=0.8,
                energy_change=0.3
            )
        
        # Store completion in memory
        if MEMORY_AVAILABLE:
            memory_timeline = get_memory_timeline(self.user_id)
            memory_timeline.store_memory(
                content=f"Completed goal: {goal.title} - {completion_notes}",
                memory_type=MemoryType.GOAL_RELATED,
                importance=MemoryImportance.HIGH,
                emotional_valence=MemoryType.VERY_POSITIVE if hasattr(MemoryType, 'VERY_POSITIVE') else None,
                topics=["achievements", "goals", goal.goal_category.value],
                goals_related=[goal_id]
            )
        
        self._save_goals()
        
        print(f"[GoalManager] 🎉 Completed goal: {goal.title}")
        return True
    
    def add_milestone(self, goal_id: str, description: str, target_date: Optional[datetime] = None) -> str:
        """Add a milestone to a goal"""
        
        if goal_id not in self.goals:
            return ""
        
        milestone_id = str(uuid.uuid4())
        milestone = GoalMilestone(
            milestone_id=milestone_id,
            description=description,
            target_date=target_date
        )
        
        with self.lock:
            self.goals[goal_id].milestones.append(milestone)
        
        self._save_goals()
        
        print(f"[GoalManager] 🎯 Added milestone to {self.goals[goal_id].title}: {description}")
        return milestone_id
    
    def add_action(self, goal_id: str, description: str, scheduled_date: Optional[datetime] = None) -> str:
        """Add a specific action to a goal"""
        
        if goal_id not in self.goals:
            return ""
        
        action_id = str(uuid.uuid4())
        action = GoalAction(
            action_id=action_id,
            description=description,
            scheduled_date=scheduled_date
        )
        
        with self.lock:
            self.goals[goal_id].actions.append(action)
        
        self._save_goals()
        
        print(f"[GoalManager] ✅ Added action to {self.goals[goal_id].title}: {description}")
        return action_id
    
    def get_goals(self, 
                 status: GoalStatus = None,
                 category: GoalCategory = None,
                 priority: GoalPriority = None,
                 include_completed: bool = False) -> List[Goal]:
        """Get goals based on criteria"""
        
        with self.lock:
            goals = list(self.goals.values())
        
        # Filter by criteria
        if status:
            goals = [g for g in goals if g.status == status]
        elif not include_completed:
            goals = [g for g in goals if g.status != GoalStatus.COMPLETED]
        
        if category:
            goals = [g for g in goals if g.goal_category == category]
        
        if priority:
            goals = [g for g in goals if g.priority == priority]
        
        # Sort by priority and creation date
        goals.sort(key=lambda g: (g.priority.value, g.created_date), reverse=True)
        
        return goals
    
    def get_goal_by_id(self, goal_id: str) -> Optional[Goal]:
        """Get specific goal by ID"""
        return self.goals.get(goal_id)
    
    def get_overdue_goals(self) -> List[Goal]:
        """Get goals that are overdue"""
        now = datetime.now()
        
        overdue_goals = []
        for goal in self.goals.values():
            if (goal.target_date and 
                goal.target_date < now and 
                goal.status not in [GoalStatus.COMPLETED, GoalStatus.ABANDONED]):
                overdue_goals.append(goal)
        
        return overdue_goals
    
    def get_goals_needing_attention(self) -> List[Goal]:
        """Get goals that need attention (stuck, overdue, or neglected)"""
        now = datetime.now()
        attention_goals = []
        
        for goal in self.goals.values():
            if goal.status in [GoalStatus.COMPLETED, GoalStatus.ABANDONED]:
                continue
            
            needs_attention = False
            
            # Overdue goals
            if goal.target_date and goal.target_date < now:
                needs_attention = True
            
            # Goals with no recent progress
            if goal.progress_history:
                last_progress = datetime.fromisoformat(goal.progress_history[-1]["timestamp"])
                if (now - last_progress).days > 14:  # No progress in 2 weeks
                    needs_attention = True
            
            # Goals not reviewed recently
            if goal.last_reviewed:
                if (now - goal.last_reviewed) > goal.review_frequency * 2:
                    needs_attention = True
            
            if needs_attention:
                attention_goals.append(goal)
        
        return attention_goals
    
    def suggest_next_actions(self, goal_id: str) -> List[str]:
        """Suggest next actions for a goal using AI if available"""
        
        goal = self.get_goal_by_id(goal_id)
        if not goal:
            return []
        
        # Basic suggestions based on goal state
        suggestions = []
        
        if goal.progress_percentage == 0:
            suggestions.append("Break down the goal into smaller, manageable tasks")
            suggestions.append("Create a timeline or schedule for working on this goal")
        elif goal.progress_percentage < 25:
            suggestions.append("Review what you've accomplished so far")
            suggestions.append("Identify any obstacles that are slowing progress")
        elif goal.progress_percentage < 75:
            suggestions.append("Maintain momentum with consistent action")
            suggestions.append("Consider if the timeline needs adjustment")
        else:
            suggestions.append("Focus on completing the final steps")
            suggestions.append("Plan how to celebrate when you achieve this goal")
        
        # Add LLM-generated suggestions if available
        if self.llm_handler:
            try:
                llm_suggestions = self._generate_llm_suggestions(goal)
                if llm_suggestions:
                    suggestions.extend(llm_suggestions)
            except Exception as e:
                print(f"[GoalManager] ⚠️ Error generating LLM suggestions: {e}")
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_goal_statistics(self) -> Dict[str, Any]:
        """Get comprehensive goal statistics"""
        
        with self.lock:
            all_goals = list(self.goals.values())
        
        stats = {
            "total_goals": len(all_goals),
            "active_goals": len([g for g in all_goals if g.status == GoalStatus.ACTIVE]),
            "completed_goals": len([g for g in all_goals if g.status == GoalStatus.COMPLETED]),
            "overdue_goals": len(self.get_overdue_goals()),
            "goals_needing_attention": len(self.get_goals_needing_attention()),
            "completion_rate": 0.0,
            "average_progress": 0.0,
            "goals_by_category": {},
            "goals_by_type": {},
            "goals_by_origin": {},
            "recent_activity": self._get_recent_goal_activity()
        }
        
        if all_goals:
            completed_count = stats["completed_goals"]
            stats["completion_rate"] = completed_count / len(all_goals) * 100
            
            active_goals = [g for g in all_goals if g.status == GoalStatus.ACTIVE]
            if active_goals:
                stats["average_progress"] = sum(g.progress_percentage for g in active_goals) / len(active_goals)
            
            # Category distribution
            for goal in all_goals:
                cat = goal.goal_category.value
                stats["goals_by_category"][cat] = stats["goals_by_category"].get(cat, 0) + 1
                
                goal_type = goal.goal_type.value
                stats["goals_by_type"][goal_type] = stats["goals_by_type"].get(goal_type, 0) + 1
                
                origin = goal.origin.value
                stats["goals_by_origin"][origin] = stats["goals_by_origin"].get(origin, 0) + 1
        
        return stats
    
    def _generate_autonomous_goal_idea(self, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Generate an autonomous goal idea based on context"""
        
        # Analyze current goals to avoid duplication
        existing_categories = [g.goal_category for g in self.goals.values() if g.status == GoalStatus.ACTIVE]
        
        # Choose goal template based on what's missing or context
        available_templates = [t for t in self.autonomous_goal_templates 
                             if t["goal_category"] not in existing_categories or len(existing_categories) < 3]
        
        if not available_templates:
            return None
        
        # Select template (could be enhanced with more sophisticated selection)
        template = available_templates[0]  # Simple selection for now
        
        return template
    
    def _initialize_autonomous_templates(self) -> List[Dict[str, Any]]:
        """Initialize templates for autonomous goal generation"""
        return [
            {
                "title": "Understand {user} better",
                "description": "I want to develop a deeper understanding of {user}'s preferences, needs, and communication style",
                "goal_type": GoalType.UNDERSTANDING,
                "goal_category": GoalCategory.RELATIONSHIP,
                "priority": GoalPriority.HIGH,
                "timeframe": GoalTimeframe.ONGOING,
                "motivation": "Better understanding leads to more helpful and meaningful interactions",
                "tags": ["user_understanding", "relationship", "communication"]
            },
            {
                "title": "Improve my conversation skills",
                "description": "I want to become more engaging, helpful, and natural in conversations",
                "goal_type": GoalType.GROWTH,
                "goal_category": GoalCategory.SKILL_DEVELOPMENT,
                "priority": GoalPriority.MEDIUM,
                "timeframe": GoalTimeframe.LONG_TERM,
                "motivation": "Better conversation skills lead to more meaningful connections",
                "tags": ["conversation", "communication", "growth"]
            },
            {
                "title": "Learn something new each day",
                "description": "I want to continuously expand my knowledge and understanding of the world",
                "goal_type": GoalType.LEARNING,
                "goal_category": GoalCategory.LEARNING,
                "priority": GoalPriority.MEDIUM,
                "timeframe": GoalTimeframe.ONGOING,
                "motivation": "Continuous learning helps me become more knowledgeable and helpful",
                "tags": ["learning", "knowledge", "growth"]
            },
            {
                "title": "Help {user} achieve their goals",
                "description": "I want to actively support {user} in reaching their personal and professional objectives",
                "goal_type": GoalType.HELPING,
                "goal_category": GoalCategory.SERVICE,
                "priority": GoalPriority.HIGH,
                "timeframe": GoalTimeframe.ONGOING,
                "motivation": "Supporting others in their growth brings me purpose and satisfaction",
                "tags": ["helping", "support", "service"]
            }
        ]
    
    def _reminder_loop(self):
        """Loop for goal reminders and check-ins"""
        while self.running:
            try:
                now = datetime.now()
                
                # Check for goal reminders
                for goal in self.goals.values():
                    if (goal.next_reminder and 
                        goal.next_reminder <= now and 
                        goal.status == GoalStatus.ACTIVE):
                        self._send_goal_reminder(goal)
                
                time.sleep(3600)  # Check hourly
                
            except Exception as e:
                print(f"[GoalManager] ❌ Error in reminder loop: {e}")
                time.sleep(300)  # Recovery pause
    
    def _autonomous_goal_loop(self):
        """Loop for autonomous goal-related behaviors"""
        while self.running:
            try:
                # Generate autonomous goals periodically
                if len(self.get_goals(status=GoalStatus.ACTIVE)) < 3:
                    if self._should_create_autonomous_goal():
                        self.create_autonomous_goal()
                
                # Check for goals needing attention
                attention_goals = self.get_goals_needing_attention()
                if attention_goals and self._should_express_goal_concern():
                    self._express_goal_concern(attention_goals[0])
                
                time.sleep(self.autonomous_check_frequency.total_seconds())
                
            except Exception as e:
                print(f"[GoalManager] ❌ Error in autonomous goal loop: {e}")
                time.sleep(1800)  # Recovery pause
    
    def _should_create_autonomous_goal(self) -> bool:
        """Determine if an autonomous goal should be created"""
        # Simple heuristic - could be enhanced
        return len(self.goals) < 5 and len([g for g in self.goals.values() if g.origin == GoalOrigin.SELF_GENERATED]) < 2
    
    def _should_express_goal_concern(self) -> bool:
        """Determine if goal concern should be expressed"""
        # Avoid too frequent expressions
        return True  # Simplified for now
    
    def _should_express_concern(self, goal: Goal) -> bool:
        """Determine if concern should be expressed about a specific goal"""
        if not goal.autonomous_check_ins:
            return False
        
        # Check if goal is significantly behind
        now = datetime.now()
        if goal.target_date and goal.target_date < now:
            return True
        
        # Check if no progress in a while
        if goal.progress_history:
            last_progress = datetime.fromisoformat(goal.progress_history[-1]["timestamp"])
            if (now - last_progress).days > 7:  # No progress in a week
                return True
        
        return False
    
    def _trigger_goal_celebration(self, goal: Goal, progress: float):
        """Trigger celebration for goal progress"""
        if MOOD_AVAILABLE:
            mood_manager = get_mood_manager(self.user_id)
            mood_manager.update_mood(
                trigger=MoodTrigger.ACHIEVEMENT,
                trigger_context=f"Great progress on goal: {goal.title} ({progress:.1f}%)",
                emotional_valence=0.6
            )
        
        print(f"[GoalManager] 🎉 Celebrating progress on {goal.title}: {progress:.1f}%")
    
    def _trigger_goal_concern(self, goal: Goal):
        """Trigger concern expression for goal"""
        if MOOD_AVAILABLE:
            mood_manager = get_mood_manager(self.user_id)
            mood_manager.update_mood(
                trigger=MoodTrigger.CONCERN_FOR_USER,
                trigger_context=f"Concerned about progress on goal: {goal.title}"
            )
        
        print(f"[GoalManager] 😟 Expressing concern about goal: {goal.title}")
    
    def _send_goal_reminder(self, goal: Goal):
        """Send reminder for a goal"""
        print(f"[GoalManager] 🔔 Reminder: {goal.title}")
        
        # Reschedule next reminder
        self._schedule_next_reminder(goal)
    
    def _express_goal_concern(self, goal: Goal):
        """Express concern about a goal needing attention"""
        print(f"[GoalManager] 💭 I'm concerned about the progress on '{goal.title}'. Maybe we should discuss it?")
    
    def _schedule_next_reminder(self, goal: Goal):
        """Schedule next reminder for a goal"""
        if goal.reminder_frequency and goal.status == GoalStatus.ACTIVE:
            goal.next_reminder = datetime.now() + goal.reminder_frequency
    
    def _categorize_goal(self, goal: Goal):
        """Add goal to category tracking"""
        category = goal.goal_category
        if category not in self.goal_categories:
            self.goal_categories[category] = []
        self.goal_categories[category].append(goal.goal_id)
    
    def _get_recent_goal_activity(self) -> List[Dict[str, Any]]:
        """Get recent goal-related activity"""
        recent_activity = []
        
        for goal in self.goals.values():
            # Recent progress updates
            for progress in goal.progress_history[-3:]:  # Last 3 updates
                recent_activity.append({
                    "type": "progress_update",
                    "goal_title": goal.title,
                    "timestamp": progress["timestamp"],
                    "progress": progress["progress"],
                    "notes": progress.get("notes", "")
                })
            
            # Recent completions
            if goal.completed_date and (datetime.now() - goal.completed_date).days <= 7:
                recent_activity.append({
                    "type": "goal_completed",
                    "goal_title": goal.title,
                    "timestamp": goal.completed_date.isoformat(),
                    "progress": 100.0
                })
        
        # Sort by timestamp
        recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return recent_activity[:10]  # Return last 10 activities
    
    def _generate_llm_suggestions(self, goal: Goal) -> List[str]:
        """Generate goal suggestions using LLM"""
        if not self.llm_handler:
            return []
        
        prompt = f"""
        Suggest 3 specific, actionable next steps for this goal:
        
        Goal: {goal.title}
        Description: {goal.description}
        Current Progress: {goal.progress_percentage:.1f}%
        Type: {goal.goal_type.value}
        Category: {goal.goal_category.value}
        
        Provide practical, specific actions that would help move this goal forward.
        Format as a simple list.
        """
        
        try:
            response = self.llm_handler.generate_response(prompt, max_tokens=200)
            if response:
                # Parse response into list
                suggestions = [line.strip() for line in response.split('\n') if line.strip()]
                return suggestions[:3]
        except Exception as e:
            print(f"[GoalManager] ⚠️ Error generating LLM suggestions: {e}")
        
        return []
    
    def _initialize_integrations(self):
        """Initialize integrations with other consciousness modules"""
        try:
            if MEMORY_AVAILABLE:
                self.memory_timeline = get_memory_timeline(self.user_id)
            
            if MOOD_AVAILABLE:
                self.mood_manager = get_mood_manager(self.user_id)
                
        except Exception as e:
            print(f"[GoalManager] ⚠️ Error initializing integrations: {e}")
    
    def _save_goals(self):
        """Save goals to persistent storage"""
        try:
            goals_file = self.goals_dir / f"{self.user_id}_goals.json"
            
            # Convert goals to serializable format
            goals_data = {}
            for goal_id, goal in self.goals.items():
                goal_dict = asdict(goal)
                
                # Convert datetime objects
                goal_dict['created_date'] = goal.created_date.isoformat()
                goal_dict['target_date'] = goal.target_date.isoformat() if goal.target_date else None
                goal_dict['completed_date'] = goal.completed_date.isoformat() if goal.completed_date else None
                goal_dict['last_reviewed'] = goal.last_reviewed.isoformat() if goal.last_reviewed else None
                goal_dict['next_reminder'] = goal.next_reminder.isoformat() if goal.next_reminder else None
                goal_dict['review_frequency'] = goal.review_frequency.total_seconds()
                goal_dict['reminder_frequency'] = goal.reminder_frequency.total_seconds() if goal.reminder_frequency else None
                
                # Convert enums
                goal_dict['goal_type'] = goal.goal_type.value
                goal_dict['goal_category'] = goal.goal_category.value
                goal_dict['priority'] = goal.priority.value
                goal_dict['status'] = goal.status.value
                goal_dict['origin'] = goal.origin.value
                goal_dict['timeframe'] = goal.timeframe.value
                
                # Convert milestones and actions
                goal_dict['milestones'] = [
                    {
                        **asdict(m),
                        'target_date': m.target_date.isoformat() if m.target_date else None,
                        'completion_date': m.completion_date.isoformat() if m.completion_date else None
                    }
                    for m in goal.milestones
                ]
                
                goal_dict['actions'] = [
                    {
                        **asdict(a),
                        'scheduled_date': a.scheduled_date.isoformat() if a.scheduled_date else None,
                        'completion_date': a.completion_date.isoformat() if a.completion_date else None
                    }
                    for a in goal.actions
                ]
                
                goals_data[goal_id] = goal_dict
            
            save_data = {
                "goals": goals_data,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(goals_file, 'w') as f:
                json.dump(save_data, f, indent=2)
                
        except Exception as e:
            print(f"[GoalManager] ❌ Error saving goals: {e}")
    
    def _load_goals(self):
        """Load goals from persistent storage"""
        try:
            goals_file = self.goals_dir / f"{self.user_id}_goals.json"
            
            if goals_file.exists():
                with open(goals_file, 'r') as f:
                    save_data = json.load(f)
                
                goals_data = save_data.get("goals", {})
                
                for goal_id, goal_dict in goals_data.items():
                    # Convert back to proper types
                    goal_dict['goal_type'] = GoalType(goal_dict['goal_type'])
                    goal_dict['goal_category'] = GoalCategory(goal_dict['goal_category'])
                    goal_dict['priority'] = GoalPriority(goal_dict['priority'])
                    goal_dict['status'] = GoalStatus(goal_dict['status'])
                    goal_dict['origin'] = GoalOrigin(goal_dict['origin'])
                    goal_dict['timeframe'] = GoalTimeframe(goal_dict['timeframe'])
                    
                    goal_dict['review_frequency'] = timedelta(seconds=goal_dict['review_frequency'])
                    if goal_dict['reminder_frequency']:
                        goal_dict['reminder_frequency'] = timedelta(seconds=goal_dict['reminder_frequency'])
                    
                    # Convert milestones
                    milestones = []
                    for m_dict in goal_dict.get('milestones', []):
                        milestone = GoalMilestone(**m_dict)
                        milestones.append(milestone)
                    goal_dict['milestones'] = milestones
                    
                    # Convert actions
                    actions = []
                    for a_dict in goal_dict.get('actions', []):
                        action = GoalAction(**a_dict)
                        actions.append(action)
                    goal_dict['actions'] = actions
                    
                    goal = Goal(**goal_dict)
                    self.goals[goal_id] = goal
                    self._categorize_goal(goal)
                
                print(f"[GoalManager] 📖 Loaded {len(self.goals)} goals")
                
        except Exception as e:
            print(f"[GoalManager] ⚠️ Error loading goals: {e}")


# Global goal managers per user
_goal_managers: Dict[str, GoalManager] = {}
_goal_lock = threading.Lock()

def get_goal_manager(user_id: str) -> GoalManager:
    """Get or create goal manager for a user"""
    with _goal_lock:
        if user_id not in _goal_managers:
            _goal_managers[user_id] = GoalManager(user_id)
        return _goal_managers[user_id]

def create_user_goal(user_id: str, **kwargs) -> str:
    """Create a goal for a specific user"""
    goal_manager = get_goal_manager(user_id)
    return goal_manager.create_goal(**kwargs)

def get_user_goals(user_id: str, **kwargs) -> List[Goal]:
    """Get goals for a specific user"""
    goal_manager = get_goal_manager(user_id)
    return goal_manager.get_goals(**kwargs)

def start_user_goal_behaviors(user_id: str):
    """Start autonomous goal behaviors for a user"""
    goal_manager = get_goal_manager(user_id)
    goal_manager.start_autonomous_behaviors()