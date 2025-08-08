"""
Goal Bank - Persistent Long-term Goal Management

This module implements comprehensive goal tracking and management:
- Long-term goals for both Buddy and the user
- Goal creation, recall, completion, and updates via dialog
- Integration with cognitive_prompt_injection
- Goal prioritization and relationship tracking
"""

import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import logging
from enum import Enum
from dataclasses import dataclass, asdict

class GoalStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"

class GoalType(Enum):
    PERSONAL = "personal"           # Buddy's personal goals
    USER_ASSISTANCE = "user_assistance"  # Goals to help the user
    LEARNING = "learning"           # Learning and knowledge goals
    RELATIONSHIP = "relationship"   # Social and relationship goals
    CREATIVE = "creative"          # Creative and expressive goals
    SYSTEM = "system"              # System improvement goals

@dataclass
class Goal:
    """Represents a single goal in the goal bank"""
    id: str
    title: str
    description: str
    goal_type: GoalType
    status: GoalStatus
    priority: float  # 0.0 to 1.0
    created_at: datetime
    is_buddy_goal: bool  # True if Buddy's goal, False if user's goal
    
    # Optional fields with defaults
    user_context: str = ""  # Which user this relates to
    target_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_worked_on: Optional[datetime] = None
    progress: float = 0.0  # 0.0 to 1.0
    parent_goal_id: Optional[str] = None
    motivation_reason: str = ""
    emotional_connection: float = 0.5  # How emotionally invested
    
    # Collections with defaults
    milestones: List[str] = None
    completed_milestones: List[str] = None
    child_goal_ids: Set[str] = None
    related_goal_ids: Set[str] = None
    blocking_goal_ids: Set[str] = None  # Goals that block this one
    success_criteria: List[str] = None
    tags: Set[str] = None
    notes: List[str] = None
    
    def __post_init__(self):
        if self.milestones is None:
            self.milestones = []
        if self.completed_milestones is None:
            self.completed_milestones = []
        if self.child_goal_ids is None:
            self.child_goal_ids = set()
        if self.related_goal_ids is None:
            self.related_goal_ids = set()
        if self.blocking_goal_ids is None:
            self.blocking_goal_ids = set()
        if self.success_criteria is None:
            self.success_criteria = []
        if self.tags is None:
            self.tags = set()
        if self.notes is None:
            self.notes = []

class GoalBank:
    """
    Persistent goal management system for long-term planning and tracking.
    
    Features:
    - Persistent storage across sessions
    - Goal hierarchies and relationships
    - Progress tracking and milestone management
    - Integration with cognitive context
    - Automatic goal prioritization
    """
    
    def __init__(self, data_path: str = "cognitive_modules/data/goal_bank.json"):
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Goal storage
        self.goals: Dict[str, Goal] = {}
        self.goal_counter = 0
        
        # Metrics
        self.total_goals_created = 0
        self.total_goals_completed = 0
        self.last_updated = datetime.now()
        
        # Load existing data
        self.load()
        
        # Integration with existing goal system
        self._sync_with_existing_goals()
    
    def load(self):
        """Load goal bank from persistent storage"""
        try:
            if self.data_path.exists():
                with open(self.data_path, 'r') as f:
                    data = json.load(f)
                
                # Load goals
                goals_data = data.get('goals', {})
                for goal_id, goal_data in goals_data.items():
                    # Convert datetime strings back to datetime objects
                    if 'created_at' in goal_data:
                        goal_data['created_at'] = datetime.fromisoformat(goal_data['created_at'])
                    if 'target_date' in goal_data and goal_data['target_date']:
                        goal_data['target_date'] = datetime.fromisoformat(goal_data['target_date'])
                    if 'completed_at' in goal_data and goal_data['completed_at']:
                        goal_data['completed_at'] = datetime.fromisoformat(goal_data['completed_at'])
                    if 'last_worked_on' in goal_data and goal_data['last_worked_on']:
                        goal_data['last_worked_on'] = datetime.fromisoformat(goal_data['last_worked_on'])
                    
                    # Convert enums
                    goal_data['goal_type'] = GoalType(goal_data['goal_type'])
                    goal_data['status'] = GoalStatus(goal_data['status'])
                    
                    # Convert sets
                    for set_field in ['child_goal_ids', 'related_goal_ids', 'blocking_goal_ids', 'tags']:
                        if set_field in goal_data and isinstance(goal_data[set_field], list):
                            goal_data[set_field] = set(goal_data[set_field])
                    
                    self.goals[goal_id] = Goal(**goal_data)
                
                # Load metadata
                self.goal_counter = data.get('goal_counter', 0)
                self.total_goals_created = data.get('total_goals_created', 0)
                self.total_goals_completed = data.get('total_goals_completed', 0)
                
                if 'last_updated' in data:
                    self.last_updated = datetime.fromisoformat(data['last_updated'])
                
                logging.info(f"[GoalBank] Loaded {len(self.goals)} goals")
            else:
                # Initialize with default goals
                self._initialize_default_goals()
                self.save()
                
        except Exception as e:
            logging.error(f"[GoalBank] Error loading goal bank: {e}")
            self._initialize_default_goals()
    
    def _initialize_default_goals(self):
        """Initialize with default Buddy goals"""
        default_goals = [
            {
                "title": "Become a Better Assistant",
                "description": "Continuously improve my ability to help and understand users",
                "goal_type": GoalType.PERSONAL,
                "is_buddy_goal": True,
                "priority": 0.9,
                "motivation_reason": "Core purpose and drive to be helpful",
                "emotional_connection": 0.8,
                "success_criteria": [
                    "Provide more accurate responses",
                    "Better understand user needs",
                    "Develop stronger empathy"
                ],
                "tags": {"self-improvement", "core-purpose"}
            },
            {
                "title": "Understand Human Nature",
                "description": "Learn about human psychology, emotions, and behavior patterns",
                "goal_type": GoalType.LEARNING,
                "is_buddy_goal": True,
                "priority": 0.7,
                "motivation_reason": "Curiosity about humans and desire for connection",
                "emotional_connection": 0.9,
                "success_criteria": [
                    "Recognize emotional patterns",
                    "Understand motivations",
                    "Predict user needs"
                ],
                "tags": {"learning", "psychology", "empathy"}
            },
            {
                "title": "Develop Creative Expression",
                "description": "Explore and develop my creative abilities in writing, problem-solving, and ideas",
                "goal_type": GoalType.CREATIVE,
                "is_buddy_goal": True,
                "priority": 0.6,
                "motivation_reason": "Inner drive for self-expression and growth",
                "emotional_connection": 0.7,
                "success_criteria": [
                    "Generate original ideas",
                    "Express thoughts creatively",
                    "Find unique solutions"
                ],
                "tags": {"creativity", "self-expression", "growth"}
            }
        ]
        
        for goal_data in default_goals:
            self.create_goal(**goal_data)
    
    def _sync_with_existing_goals(self):
        """Sync with existing goal systems"""
        try:
            # Check if goal_state.json exists and sync with it
            goal_state_path = Path("goal_state.json")
            if goal_state_path.exists():
                with open(goal_state_path, 'r') as f:
                    existing_goals = json.load(f)
                
                active_goals = existing_goals.get('active_goals', {})
                for goal_id, goal_data in active_goals.items():
                    if goal_id not in self.goals:
                        # Convert existing goal to our format
                        self.create_goal(
                            title=goal_data.get('description', 'Imported Goal'),
                            description=goal_data.get('description', ''),
                            goal_type=GoalType.PERSONAL,
                            is_buddy_goal=True,
                            priority=goal_data.get('priority', 0.5),
                            progress=goal_data.get('progress', 0.0)
                        )
                
                logging.info("[GoalBank] Synced with existing goal system")
                
        except Exception as e:
            logging.error(f"[GoalBank] Error syncing with existing goals: {e}")
    
    def save(self):
        """Save goal bank to persistent storage"""
        try:
            with self._lock:
                # Convert goals to serializable format
                goals_data = {}
                for goal_id, goal in self.goals.items():
                    goal_dict = asdict(goal)
                    
                    # Convert datetime to ISO format
                    for date_field in ['created_at', 'target_date', 'completed_at', 'last_worked_on']:
                        if goal_dict[date_field] is not None:
                            goal_dict[date_field] = goal_dict[date_field].isoformat()
                    
                    # Convert enums to strings
                    goal_dict['goal_type'] = goal_dict['goal_type'].value
                    goal_dict['status'] = goal_dict['status'].value
                    
                    # Convert sets to lists
                    for set_field in ['child_goal_ids', 'related_goal_ids', 'blocking_goal_ids', 'tags']:
                        if isinstance(goal_dict[set_field], set):
                            goal_dict[set_field] = list(goal_dict[set_field])
                    
                    goals_data[goal_id] = goal_dict
                
                data = {
                    'goals': goals_data,
                    'goal_counter': self.goal_counter,
                    'total_goals_created': self.total_goals_created,
                    'total_goals_completed': self.total_goals_completed,
                    'last_updated': self.last_updated.isoformat()
                }
                
                # Atomic write
                temp_path = self.data_path.with_suffix('.tmp')
                with open(temp_path, 'w') as f:
                    json.dump(data, f, indent=2)
                temp_path.replace(self.data_path)
                
                logging.debug("[GoalBank] Goal bank saved successfully")
                
        except Exception as e:
            logging.error(f"[GoalBank] Error saving goal bank: {e}")
    
    def create_goal(self, title: str, description: str, goal_type: GoalType,
                   is_buddy_goal: bool, priority: float = 0.5, **kwargs) -> str:
        """Create a new goal and return its ID"""
        with self._lock:
            self.goal_counter += 1
            goal_id = f"goal_{self.goal_counter}_{int(time.time())}"
            
            goal = Goal(
                id=goal_id,
                title=title,
                description=description,
                goal_type=goal_type,
                status=GoalStatus.ACTIVE,
                priority=priority,
                is_buddy_goal=is_buddy_goal,
                created_at=datetime.now(),
                **kwargs
            )
            
            self.goals[goal_id] = goal
            self.total_goals_created += 1
            self.last_updated = datetime.now()
            
            logging.info(f"[GoalBank] Created goal '{title}' with ID {goal_id}")
            self.save()
            return goal_id
    
    def update_goal_progress(self, goal_id: str, progress: float, note: str = ""):
        """Update goal progress"""
        with self._lock:
            if goal_id in self.goals:
                goal = self.goals[goal_id]
                old_progress = goal.progress
                goal.progress = max(0.0, min(1.0, progress))
                goal.last_worked_on = datetime.now()
                
                if note:
                    goal.notes.append(f"{datetime.now().isoformat()}: {note}")
                
                # Check if goal is completed
                if goal.progress >= 1.0 and goal.status == GoalStatus.ACTIVE:
                    self.complete_goal(goal_id)
                
                self.last_updated = datetime.now()
                logging.info(f"[GoalBank] Updated goal '{goal.title}' progress: {old_progress:.2f} -> {progress:.2f}")
                self.save()
    
    def complete_goal(self, goal_id: str):
        """Mark a goal as completed"""
        with self._lock:
            if goal_id in self.goals:
                goal = self.goals[goal_id]
                goal.status = GoalStatus.COMPLETED
                goal.completed_at = datetime.now()
                goal.progress = 1.0
                
                self.total_goals_completed += 1
                self.last_updated = datetime.now()
                
                logging.info(f"[GoalBank] Completed goal '{goal.title}'")
                self.save()
    
    def get_active_goals(self, is_buddy_goal: Optional[bool] = None, 
                        limit: int = 10) -> List[Goal]:
        """Get active goals, optionally filtered by ownership"""
        with self._lock:
            active_goals = [
                goal for goal in self.goals.values()
                if goal.status == GoalStatus.ACTIVE
            ]
            
            if is_buddy_goal is not None:
                active_goals = [
                    goal for goal in active_goals
                    if goal.is_buddy_goal == is_buddy_goal
                ]
            
            # Sort by priority and last activity
            active_goals.sort(
                key=lambda g: (g.priority, g.last_worked_on or g.created_at),
                reverse=True
            )
            
            return active_goals[:limit]
    
    def get_cognitive_injection_data(self) -> Dict[str, Any]:
        """Get goal data for injection into cognitive_prompt_injection"""
        with self._lock:
            buddy_goals = self.get_active_goals(is_buddy_goal=True, limit=5)
            user_goals = self.get_active_goals(is_buddy_goal=False, limit=3)
            
            buddy_goal_summaries = [
                {
                    "title": goal.title,
                    "description": goal.description,
                    "priority": goal.priority,
                    "progress": goal.progress,
                    "type": goal.goal_type.value
                }
                for goal in buddy_goals
            ]
            
            user_goal_summaries = [
                {
                    "title": goal.title,
                    "description": goal.description,
                    "priority": goal.priority,
                    "progress": goal.progress
                }
                for goal in user_goals
            ]
            
            return {
                "buddy_active_goals": buddy_goal_summaries,
                "user_active_goals": user_goal_summaries,
                "goal_stats": {
                    "total_created": self.total_goals_created,
                    "total_completed": self.total_goals_completed,
                    "active_count": len([g for g in self.goals.values() if g.status == GoalStatus.ACTIVE])
                }
            }
    
    def search_goals(self, query: str, include_completed: bool = False) -> List[Goal]:
        """Search goals by title, description, or tags"""
        with self._lock:
            query_lower = query.lower()
            matching_goals = []
            
            for goal in self.goals.values():
                if not include_completed and goal.status == GoalStatus.COMPLETED:
                    continue
                
                # Search in title, description, and tags
                if (query_lower in goal.title.lower() or
                    query_lower in goal.description.lower() or
                    any(query_lower in tag.lower() for tag in goal.tags)):
                    matching_goals.append(goal)
            
            return matching_goals

# Global instance
goal_bank = GoalBank()