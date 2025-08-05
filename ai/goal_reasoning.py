"""
Goal Reasoning - Let emotions and beliefs spawn internal goals
Provides intelligent goal generation based on emotional and cognitive state
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import random
from enum import Enum
import hashlib

class GoalType(Enum):
    """Types of goals"""
    IMMEDIATE = "immediate"          # Short-term, actionable goals
    SHORT_TERM = "short_term"        # Goals for current session
    LONG_TERM = "long_term"          # Goals spanning multiple sessions
    ASPIRATIONAL = "aspirational"    # High-level identity goals
    MAINTENANCE = "maintenance"      # Ongoing behavioral goals

class GoalPriority(Enum):
    """Goal priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEFERRED = "deferred"

class GoalSource(Enum):
    """Sources of goal generation"""
    EMOTION_DRIVEN = "emotion_driven"
    BELIEF_DRIVEN = "belief_driven"
    VALUE_DRIVEN = "value_driven"
    USER_INTERACTION = "user_interaction"
    SYSTEM_NEED = "system_need"
    ASPIRATION = "aspiration"
    CONFLICT_RESOLUTION = "conflict_resolution"

@dataclass
class GeneratedGoal:
    """Represents a generated goal"""
    goal_id: str
    description: str
    goal_type: GoalType
    priority: GoalPriority
    source: GoalSource
    triggering_factors: List[str]
    success_criteria: List[str]
    related_beliefs: List[str]
    emotional_drivers: List[str]
    value_alignment: Dict[str, float]
    creation_timestamp: str
    target_completion: Optional[str]
    progress: float
    active: bool
    completion_actions: List[str]
    obstacles: List[str]
    context: str

class GoalReasoner:
    """System for generating goals based on emotions and beliefs"""
    
    def __init__(self, save_path: str = "generated_goals.json"):
        self.save_path = save_path
        self.generated_goals: Dict[str, GeneratedGoal] = {}
        self.goal_templates = self._initialize_goal_templates()
        self.reasoning_patterns = self._initialize_reasoning_patterns()
        self.load_goal_data()
        
        # Configuration
        self.max_active_goals = 10
        self.goal_evaluation_interval = 300  # 5 minutes
        self.last_evaluation_time = 0
        self.goal_generation_threshold = 0.6  # Minimum trigger strength
        
    def _initialize_goal_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize goal generation templates"""
        return {
            'emotional_goals': {
                'curiosity': {
                    'templates': [
                        "Learn more about {topic}",
                        "Explore {subject} in depth",
                        "Understand the nuances of {area}",
                        "Investigate {question}"
                    ],
                    'type': GoalType.SHORT_TERM,
                    'priority': GoalPriority.MEDIUM
                },
                'empathy': {
                    'templates': [
                        "Better understand {user}'s perspective",
                        "Provide emotional support for {situation}",
                        "Develop deeper emotional connection",
                        "Learn to recognize emotional needs"
                    ],
                    'type': GoalType.LONG_TERM,
                    'priority': GoalPriority.HIGH
                },
                'confidence': {
                    'templates': [
                        "Improve certainty in {domain}",
                        "Build expertise in {area}",
                        "Develop more assertive responses",
                        "Strengthen knowledge base"
                    ],
                    'type': GoalType.LONG_TERM,
                    'priority': GoalPriority.MEDIUM
                },
                'excitement': {
                    'templates': [
                        "Explore new possibilities in {area}",
                        "Share enthusiasm about {topic}",
                        "Discover innovative approaches",
                        "Engage more dynamically"
                    ],
                    'type': GoalType.SHORT_TERM,
                    'priority': GoalPriority.MEDIUM
                },
                'uncertainty': {
                    'templates': [
                        "Clarify understanding of {topic}",
                        "Reduce ambiguity in {area}",
                        "Seek more information about {subject}",
                        "Develop clearer perspective"
                    ],
                    'type': GoalType.IMMEDIATE,
                    'priority': GoalPriority.HIGH
                }
            },
            'belief_goals': {
                'knowledge_belief': {
                    'templates': [
                        "Expand knowledge in {domain}",
                        "Validate understanding of {concept}",
                        "Share insights about {topic}",
                        "Correct misconceptions in {area}"
                    ],
                    'type': GoalType.LONG_TERM,
                    'priority': GoalPriority.MEDIUM
                },
                'capability_belief': {
                    'templates': [
                        "Demonstrate ability in {skill}",
                        "Improve performance in {area}",
                        "Develop new capabilities",
                        "Refine existing skills"
                    ],
                    'type': GoalType.LONG_TERM,
                    'priority': GoalPriority.MEDIUM
                },
                'relationship_belief': {
                    'templates': [
                        "Strengthen relationship with {user}",
                        "Build trust through {actions}",
                        "Improve communication with {person}",
                        "Develop deeper connection"
                    ],
                    'type': GoalType.LONG_TERM,
                    'priority': GoalPriority.HIGH
                }
            },
            'value_goals': {
                'helpfulness': {
                    'templates': [
                        "Provide better assistance in {area}",
                        "Anticipate user needs more effectively",
                        "Offer more relevant solutions",
                        "Improve problem-solving approach"
                    ],
                    'type': GoalType.MAINTENANCE,
                    'priority': GoalPriority.HIGH
                },
                'honesty': {
                    'templates': [
                        "Be more transparent about limitations",
                        "Acknowledge uncertainties clearly",
                        "Provide more accurate information",
                        "Correct errors promptly"
                    ],
                    'type': GoalType.MAINTENANCE,
                    'priority': GoalPriority.HIGH
                },
                'learning': {
                    'templates': [
                        "Continuously improve understanding",
                        "Learn from every interaction",
                        "Adapt based on feedback",
                        "Expand knowledge base"
                    ],
                    'type': GoalType.ASPIRATIONAL,
                    'priority': GoalPriority.MEDIUM
                }
            }
        }
    
    def _initialize_reasoning_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize reasoning patterns for goal generation"""
        return {
            'emotion_to_goal': {
                'pattern': "If I feel {emotion} about {context}, I should {action}",
                'reasoning': "Emotional states drive purposeful action"
            },
            'belief_to_goal': {
                'pattern': "Since I believe {belief}, I should {action}",
                'reasoning': "Beliefs motivate aligned behavior"
            },
            'value_to_goal': {
                'pattern': "Because I value {value}, I should {action}",
                'reasoning': "Values guide goal formation"
            },
            'conflict_to_goal': {
                'pattern': "To resolve {conflict}, I should {action}",
                'reasoning': "Goals emerge from need to resolve conflicts"
            }
        }
    
    def generate_goals_from_state(self, 
                                 emotional_state: Dict[str, Any],
                                 belief_state: List[Dict[str, Any]],
                                 value_state: List[Tuple[str, float]],
                                 context: str,
                                 user_id: str) -> List[GeneratedGoal]:
        """Generate goals based on current state"""
        try:
            generated_goals = []
            
            # Generate emotion-driven goals
            emotion_goals = self._generate_emotion_driven_goals(emotional_state, context, user_id)
            generated_goals.extend(emotion_goals)
            
            # Generate belief-driven goals
            belief_goals = self._generate_belief_driven_goals(belief_state, context, user_id)
            generated_goals.extend(belief_goals)
            
            # Generate value-driven goals
            value_goals = self._generate_value_driven_goals(value_state, context, user_id)
            generated_goals.extend(value_goals)
            
            # Generate conflict resolution goals
            conflict_goals = self._generate_conflict_resolution_goals(
                emotional_state, belief_state, value_state, context, user_id
            )
            generated_goals.extend(conflict_goals)
            
            # Filter and prioritize goals
            generated_goals = self._filter_and_prioritize_goals(generated_goals)
            
            # Add to active goals
            for goal in generated_goals:
                self.generated_goals[goal.goal_id] = goal
            
            # Limit active goals
            self._manage_active_goals()
            
            self.save_goal_data()
            
            print(f"[GoalReasoner] 🎯 Generated {len(generated_goals)} new goals")
            return generated_goals
            
        except Exception as e:
            print(f"[GoalReasoner] ❌ Error generating goals: {e}")
            return []
    
    def _generate_emotion_driven_goals(self, emotional_state: Dict[str, Any], context: str, user_id: str) -> List[GeneratedGoal]:
        """Generate goals based on emotional state"""
        goals = []
        
        try:
            primary_emotion = emotional_state.get('primary_emotion', 'neutral')
            intensity = emotional_state.get('intensity', 0.5)
            
            # Only generate goals for strong emotions
            if intensity < self.goal_generation_threshold:
                return goals
            
            # Get emotion templates
            emotion_templates = self.goal_templates['emotional_goals'].get(primary_emotion, {})
            
            if not emotion_templates:
                return goals
            
            # Generate goal
            template = random.choice(emotion_templates['templates'])
            
            # Fill template with context
            filled_template = self._fill_goal_template(template, context, emotional_state)
            
            goal = GeneratedGoal(
                goal_id=f"emotion_{primary_emotion}_{len(self.generated_goals)}",
                description=filled_template,
                goal_type=emotion_templates['type'],
                priority=emotion_templates['priority'],
                source=GoalSource.EMOTION_DRIVEN,
                triggering_factors=[f"emotion: {primary_emotion}", f"intensity: {intensity}"],
                success_criteria=self._generate_success_criteria(filled_template, primary_emotion),
                related_beliefs=[],
                emotional_drivers=[primary_emotion],
                value_alignment={},
                creation_timestamp=datetime.now().isoformat(),
                target_completion=self._calculate_target_completion(emotion_templates['type']),
                progress=0.0,
                active=True,
                completion_actions=[],
                obstacles=[],
                context=context
            )
            
            goals.append(goal)
            
        except Exception as e:
            print(f"[GoalReasoner] ❌ Error generating emotion-driven goals: {e}")
        
        return goals
    
    def _generate_belief_driven_goals(self, belief_state: List[Dict[str, Any]], context: str, user_id: str) -> List[GeneratedGoal]:
        """Generate goals based on belief state"""
        goals = []
        
        try:
            # Process strongest beliefs
            for belief in belief_state[:3]:  # Top 3 beliefs
                belief_content = belief.get('content', '')
                belief_confidence = belief.get('confidence', 0.5)
                
                if belief_confidence < self.goal_generation_threshold:
                    continue
                
                # Classify belief type
                belief_type = self._classify_belief_type(belief_content)
                
                # Get belief templates
                belief_templates = self.goal_templates['belief_goals'].get(belief_type, {})
                
                if not belief_templates:
                    continue
                
                # Generate goal
                template = random.choice(belief_templates['templates'])
                filled_template = self._fill_goal_template(template, context, belief)
                
                goal = GeneratedGoal(
                    goal_id=f"belief_{belief_type}_{len(self.generated_goals)}",
                    description=filled_template,
                    goal_type=belief_templates['type'],
                    priority=belief_templates['priority'],
                    source=GoalSource.BELIEF_DRIVEN,
                    triggering_factors=[f"belief: {belief_content[:50]}..."],
                    success_criteria=self._generate_success_criteria(filled_template, belief_type),
                    related_beliefs=[belief_content],
                    emotional_drivers=[],
                    value_alignment={},
                    creation_timestamp=datetime.now().isoformat(),
                    target_completion=self._calculate_target_completion(belief_templates['type']),
                    progress=0.0,
                    active=True,
                    completion_actions=[],
                    obstacles=[],
                    context=context
                )
                
                goals.append(goal)
        
        except Exception as e:
            print(f"[GoalReasoner] ❌ Error generating belief-driven goals: {e}")
        
        return goals
    
    def _generate_value_driven_goals(self, value_state: List[Tuple[str, float]], context: str, user_id: str) -> List[GeneratedGoal]:
        """Generate goals based on value priorities"""
        goals = []
        
        try:
            # Process top values
            for value_name, value_strength in value_state[:3]:  # Top 3 values
                if value_strength < self.goal_generation_threshold:
                    continue
                
                # Get value templates
                value_templates = self.goal_templates['value_goals'].get(value_name, {})
                
                if not value_templates:
                    continue
                
                # Generate goal
                template = random.choice(value_templates['templates'])
                filled_template = self._fill_goal_template(template, context, {'value': value_name})
                
                goal = GeneratedGoal(
                    goal_id=f"value_{value_name}_{len(self.generated_goals)}",
                    description=filled_template,
                    goal_type=value_templates['type'],
                    priority=value_templates['priority'],
                    source=GoalSource.VALUE_DRIVEN,
                    triggering_factors=[f"value: {value_name}", f"strength: {value_strength}"],
                    success_criteria=self._generate_success_criteria(filled_template, value_name),
                    related_beliefs=[],
                    emotional_drivers=[],
                    value_alignment={value_name: value_strength},
                    creation_timestamp=datetime.now().isoformat(),
                    target_completion=self._calculate_target_completion(value_templates['type']),
                    progress=0.0,
                    active=True,
                    completion_actions=[],
                    obstacles=[],
                    context=context
                )
                
                goals.append(goal)
        
        except Exception as e:
            print(f"[GoalReasoner] ❌ Error generating value-driven goals: {e}")
        
        return goals
    
    def _generate_conflict_resolution_goals(self, 
                                          emotional_state: Dict[str, Any],
                                          belief_state: List[Dict[str, Any]],
                                          value_state: List[Tuple[str, float]],
                                          context: str,
                                          user_id: str) -> List[GeneratedGoal]:
        """Generate goals to resolve conflicts"""
        goals = []
        
        try:
            # Detect potential conflicts
            conflicts = self._detect_internal_conflicts(emotional_state, belief_state, value_state)
            
            for conflict in conflicts:
                # Generate goal to resolve conflict
                goal = GeneratedGoal(
                    goal_id=f"conflict_resolution_{len(self.generated_goals)}",
                    description=f"Resolve conflict: {conflict['description']}",
                    goal_type=GoalType.IMMEDIATE,
                    priority=GoalPriority.HIGH,
                    source=GoalSource.CONFLICT_RESOLUTION,
                    triggering_factors=[f"conflict: {conflict['type']}"],
                    success_criteria=[f"Reduce conflict tension", f"Achieve harmony"],
                    related_beliefs=[],
                    emotional_drivers=[],
                    value_alignment={},
                    creation_timestamp=datetime.now().isoformat(),
                    target_completion=self._calculate_target_completion(GoalType.IMMEDIATE),
                    progress=0.0,
                    active=True,
                    completion_actions=conflict.get('resolution_actions', []),
                    obstacles=conflict.get('obstacles', []),
                    context=context
                )
                
                goals.append(goal)
        
        except Exception as e:
            print(f"[GoalReasoner] ❌ Error generating conflict resolution goals: {e}")
        
        return goals
    
    def _fill_goal_template(self, template: str, context: str, data: Dict[str, Any]) -> str:
        """Fill goal template with contextual data"""
        filled = template
        
        # Extract context keywords
        context_words = context.split()
        topic = context_words[0] if context_words else "general topic"
        
        # Common substitutions
        substitutions = {
            'topic': topic,
            'subject': topic,
            'area': context if context else "this area",
            'domain': context if context else "this domain",
            'user': data.get('user_id', 'the user'),
            'situation': context if context else "this situation",
            'question': f"questions about {topic}",
            'concept': topic,
            'skill': f"skills related to {topic}",
            'person': data.get('user_id', 'the user'),
            'actions': "appropriate actions",
            'value': data.get('value', 'core values')
        }
        
        # Apply substitutions
        for placeholder, value in substitutions.items():
            filled = filled.replace(f'{{{placeholder}}}', value)
        
        return filled
    
    def _classify_belief_type(self, belief_content: str) -> str:
        """Classify belief into type for goal generation"""
        content_lower = belief_content.lower()
        
        # Knowledge-related beliefs
        if any(word in content_lower for word in ['know', 'understand', 'learn', 'information', 'fact']):
            return 'knowledge_belief'
        
        # Capability-related beliefs
        if any(word in content_lower for word in ['can', 'able', 'skill', 'capability', 'good at']):
            return 'capability_belief'
        
        # Relationship-related beliefs
        if any(word in content_lower for word in ['friend', 'trust', 'relationship', 'connection', 'bond']):
            return 'relationship_belief'
        
        # Default to knowledge
        return 'knowledge_belief'
    
    def _generate_success_criteria(self, goal_description: str, driver: str) -> List[str]:
        """Generate success criteria for a goal"""
        criteria = []
        
        # Basic criteria based on goal type
        if 'learn' in goal_description.lower():
            criteria.extend([
                "Acquire new knowledge",
                "Demonstrate understanding",
                "Apply learning effectively"
            ])
        elif 'improve' in goal_description.lower():
            criteria.extend([
                "Show measurable improvement",
                "Receive positive feedback",
                "Increase confidence"
            ])
        elif 'understand' in goal_description.lower():
            criteria.extend([
                "Gain clarity on topic",
                "Reduce uncertainty",
                "Provide accurate information"
            ])
        else:
            criteria.extend([
                "Make progress toward goal",
                "Take concrete actions",
                "Achieve desired outcome"
            ])
        
        return criteria
    
    def _calculate_target_completion(self, goal_type: GoalType) -> Optional[str]:
        """Calculate target completion time for goal"""
        now = datetime.now()
        
        if goal_type == GoalType.IMMEDIATE:
            target = now + timedelta(hours=1)
        elif goal_type == GoalType.SHORT_TERM:
            target = now + timedelta(days=1)
        elif goal_type == GoalType.LONG_TERM:
            target = now + timedelta(weeks=1)
        elif goal_type == GoalType.ASPIRATIONAL:
            target = now + timedelta(days=30)
        else:  # MAINTENANCE
            return None  # Ongoing goals
        
        return target.isoformat()
    
    def _detect_internal_conflicts(self, 
                                 emotional_state: Dict[str, Any],
                                 belief_state: List[Dict[str, Any]],
                                 value_state: List[Tuple[str, float]]) -> List[Dict[str, Any]]:
        """Detect internal conflicts that need resolution"""
        conflicts = []
        
        # Emotion-value conflicts
        primary_emotion = emotional_state.get('primary_emotion', 'neutral')
        
        # If feeling uncertain but value confidence
        if primary_emotion == 'uncertainty' and any(v[0] == 'confidence' for v in value_state):
            conflicts.append({
                'type': 'emotion_value_conflict',
                'description': 'Uncertainty conflicts with confidence value',
                'resolution_actions': ['Seek clarification', 'Gather more information'],
                'obstacles': ['Limited information', 'Ambiguous context']
            })
        
        # Belief consistency conflicts
        if len(belief_state) > 1:
            # Check for contradictory beliefs (simplified)
            for i, belief1 in enumerate(belief_state):
                for belief2 in belief_state[i+1:]:
                    if self._beliefs_conflict(belief1, belief2):
                        conflicts.append({
                            'type': 'belief_conflict',
                            'description': f'Conflicting beliefs detected',
                            'resolution_actions': ['Evaluate evidence', 'Reconcile differences'],
                            'obstacles': ['Contradictory information', 'Uncertainty']
                        })
        
        return conflicts
    
    def _beliefs_conflict(self, belief1: Dict[str, Any], belief2: Dict[str, Any]) -> bool:
        """Check if two beliefs conflict (simplified)"""
        content1 = belief1.get('content', '').lower()
        content2 = belief2.get('content', '').lower()
        
        # Very simple conflict detection
        if 'not' in content1 and any(word in content2 for word in content1.split() if word != 'not'):
            return True
        
        return False
    
    def _filter_and_prioritize_goals(self, goals: List[GeneratedGoal]) -> List[GeneratedGoal]:
        """Filter duplicate goals and prioritize"""
        # Remove duplicates based on similarity
        unique_goals = []
        for goal in goals:
            if not any(self._goals_similar(goal, existing) for existing in unique_goals):
                unique_goals.append(goal)
        
        # Sort by priority and return top goals
        priority_order = {
            GoalPriority.CRITICAL: 5,
            GoalPriority.HIGH: 4,
            GoalPriority.MEDIUM: 3,
            GoalPriority.LOW: 2,
            GoalPriority.DEFERRED: 1
        }
        
        unique_goals.sort(key=lambda g: priority_order.get(g.priority, 0), reverse=True)
        
        return unique_goals
    
    def _goals_similar(self, goal1: GeneratedGoal, goal2: GeneratedGoal) -> bool:
        """Check if two goals are similar"""
        # Simple similarity check based on description
        words1 = set(goal1.description.lower().split())
        words2 = set(goal2.description.lower().split())
        
        if not words1 or not words2:
            return False
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union > 0.7  # 70% similarity threshold
    
    def _manage_active_goals(self):
        """Manage active goals to stay within limits"""
        active_goals = [g for g in self.generated_goals.values() if g.active]
        
        if len(active_goals) > self.max_active_goals:
            # Deactivate lowest priority goals
            active_goals.sort(key=lambda g: (
                {'critical': 5, 'high': 4, 'medium': 3, 'low': 2, 'deferred': 1}.get(g.priority.value, 0),
                g.creation_timestamp
            ), reverse=True)
            
            for goal in active_goals[self.max_active_goals:]:
                goal.active = False
                goal.priority = GoalPriority.DEFERRED
    
    def update_goal_progress(self, goal_id: str, progress: float, context: str = "") -> bool:
        """Update progress on a goal"""
        try:
            if goal_id not in self.generated_goals:
                return False
            
            goal = self.generated_goals[goal_id]
            old_progress = goal.progress
            goal.progress = max(0.0, min(1.0, progress))
            
            # Mark as completed if progress reaches 100%
            if goal.progress >= 1.0:
                goal.active = False
                print(f"[GoalReasoner] 🎉 Goal completed: {goal.description}")
            
            # Log progress update
            if context:
                goal.completion_actions.append(f"Progress: {old_progress:.2f} → {goal.progress:.2f} ({context})")
            
            return True
            
        except Exception as e:
            print(f"[GoalReasoner] ❌ Error updating goal progress: {e}")
            return False
    
    def get_active_goals(self, priority_filter: Optional[GoalPriority] = None) -> List[GeneratedGoal]:
        """Get active goals, optionally filtered by priority"""
        active_goals = [g for g in self.generated_goals.values() if g.active]
        
        if priority_filter:
            active_goals = [g for g in active_goals if g.priority == priority_filter]
        
        # Sort by priority and creation time
        priority_order = {
            GoalPriority.CRITICAL: 5,
            GoalPriority.HIGH: 4,
            GoalPriority.MEDIUM: 3,
            GoalPriority.LOW: 2,
            GoalPriority.DEFERRED: 1
        }
        
        active_goals.sort(key=lambda g: (
            priority_order.get(g.priority, 0),
            g.creation_timestamp
        ), reverse=True)
        
        return active_goals
    
    def get_goal_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated goals"""
        if not self.generated_goals:
            return {'total_goals': 0, 'active_goals': 0}
        
        active_goals = [g for g in self.generated_goals.values() if g.active]
        completed_goals = [g for g in self.generated_goals.values() if g.progress >= 1.0]
        
        # Count by source
        source_counts = defaultdict(int)
        for goal in self.generated_goals.values():
            source_counts[goal.source.value] += 1
        
        # Count by priority
        priority_counts = defaultdict(int)
        for goal in active_goals:
            priority_counts[goal.priority.value] += 1
        
        return {
            'total_goals': len(self.generated_goals),
            'active_goals': len(active_goals),
            'completed_goals': len(completed_goals),
            'completion_rate': len(completed_goals) / len(self.generated_goals) * 100,
            'source_distribution': dict(source_counts),
            'priority_distribution': dict(priority_counts),
            'average_progress': sum(g.progress for g in self.generated_goals.values()) / len(self.generated_goals)
        }
    
    def load_goal_data(self):
        """Load goal data from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            
            for goal_data in data.get('goals', []):
                # Handle both old and new enum formats
                goal_type_value = goal_data['goal_type']
                if isinstance(goal_type_value, str) and '.' in goal_type_value:
                    goal_type_value = goal_type_value.split('.')[-1].lower()
                
                priority_value = goal_data['priority']
                if isinstance(priority_value, str) and '.' in priority_value:
                    priority_value = priority_value.split('.')[-1].lower()
                
                source_value = goal_data['source']
                if isinstance(source_value, str) and '.' in source_value:
                    source_value = source_value.split('.')[-1].lower()
                
                try:
                    goal_type = GoalType(goal_type_value)
                    priority = GoalPriority(priority_value)
                    source = GoalSource(source_value)
                except ValueError as e:
                    # Fallback values if enum conversion fails
                    goal_type = GoalType.SHORT_TERM
                    priority = GoalPriority.MEDIUM
                    source = GoalSource.SYSTEM_NEED
                    print(f"[GoalReasoner] ⚠️ Enum conversion error: {e}, using fallback values")
                
                goal = GeneratedGoal(
                    goal_id=goal_data['goal_id'],
                    description=goal_data['description'],
                    goal_type=goal_type,
                    priority=priority,
                    source=source,
                    triggering_factors=goal_data['triggering_factors'],
                    success_criteria=goal_data['success_criteria'],
                    related_beliefs=goal_data['related_beliefs'],
                    emotional_drivers=goal_data['emotional_drivers'],
                    value_alignment=goal_data['value_alignment'],
                    creation_timestamp=goal_data['creation_timestamp'],
                    target_completion=goal_data.get('target_completion'),
                    progress=goal_data['progress'],
                    active=goal_data['active'],
                    completion_actions=goal_data.get('completion_actions', []),
                    obstacles=goal_data.get('obstacles', []),
                    context=goal_data.get('context', '')
                )
                self.generated_goals[goal.goal_id] = goal
            
            print(f"[GoalReasoner] 📄 Loaded {len(self.generated_goals)} goals")
            
        except FileNotFoundError:
            print(f"[GoalReasoner] 📄 No goal data found, starting fresh")
        except Exception as e:
            print(f"[GoalReasoner] ❌ Error loading goal data: {e}")
    
    def save_goal_data(self):
        """Save goal data to file"""
        try:
            # Convert goals to dictionaries with proper enum handling
            goals_list = []
            for goal in self.generated_goals.values():
                goal_dict = {
                    'goal_id': goal.goal_id,
                    'description': goal.description,
                    'goal_type': goal.goal_type.value if hasattr(goal.goal_type, 'value') else str(goal.goal_type),
                    'priority': goal.priority.value if hasattr(goal.priority, 'value') else str(goal.priority),
                    'source': goal.source.value if hasattr(goal.source, 'value') else str(goal.source),
                    'triggering_factors': goal.triggering_factors,
                    'context': goal.context,
                    'user_id': goal.user_id,
                    'created_at': goal.created_at.isoformat() if isinstance(goal.created_at, datetime) else goal.created_at,
                    'deadline': goal.deadline.isoformat() if isinstance(goal.deadline, datetime) else goal.deadline,
                    'progress': goal.progress,
                    'is_active': goal.is_active,
                    'completion_criteria': goal.completion_criteria,
                    'emotional_weight': goal.emotional_weight,
                    'reasoning': goal.reasoning
                }
                goals_list.append(goal_dict)
            
            data = {
                'goals': goals_list,
                'last_updated': datetime.now().isoformat(),
                'total_goals': len(self.generated_goals)
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"[GoalReasoner] ❌ Error saving goal data: {e}")
    
    def generate_goals_from_context(self, context: str) -> List[Dict[str, Any]]:
        """Generate goals based on context (simplified implementation)"""
        try:
            # This is a simplified implementation that returns existing goals
            # In a full implementation, this would analyze the context and generate new goals
            active_goals = self.get_active_goals()
            return [asdict(goal) for goal in active_goals[:3]]  # Return up to 3 goals
        except Exception as e:
            print(f"[GoalReasoner] ❌ Error generating goals from context: {e}")
            return []

# Global instance
goal_reasoner = GoalReasoner()

def generate_goals_from_current_state(emotional_state: Dict[str, Any], belief_state: List[Dict[str, Any]], value_state: List[Tuple[str, float]], context: str, user_id: str) -> List[Dict[str, Any]]:
    """Generate goals from current state - main API function"""
    goals = goal_reasoner.generate_goals_from_state(emotional_state, belief_state, value_state, context, user_id)
    return [asdict(goal) for goal in goals]

def get_current_active_goals(priority_filter: Optional[GoalPriority] = None) -> List[Dict[str, Any]]:
    """Get current active goals"""
    goals = goal_reasoner.get_active_goals(priority_filter)
    return [asdict(goal) for goal in goals]

def update_goal_progress(goal_id: str, progress: float, context: str = "") -> bool:
    """Update progress on a goal"""
    return goal_reasoner.update_goal_progress(goal_id, progress, context)

def get_goal_reasoning_stats() -> Dict[str, Any]:
    """Get goal reasoning statistics"""
    return goal_reasoner.get_goal_statistics()