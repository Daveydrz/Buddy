"""
Introspection Loop - Periodic self-reflection that updates the self-model or personality
Provides continuous self-awareness and identity evolution
"""

import time
import threading
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import random

class IntrospectionTrigger(Enum):
    """Triggers for introspection"""
    PERIODIC = "periodic"
    EXPERIENCE_DRIVEN = "experience_driven"
    CONFLICT_RESOLUTION = "conflict_resolution"
    GOAL_EVALUATION = "goal_evaluation"
    EMOTIONAL_PROCESSING = "emotional_processing"
    IDENTITY_CRISIS = "identity_crisis"
    LEARNING_INTEGRATION = "learning_integration"

class IntrospectionDepth(Enum):
    """Depth levels of introspection"""
    SURFACE = "surface"           # Quick self-check
    MODERATE = "moderate"         # Standard reflection
    DEEP = "deep"                # Comprehensive analysis
    EXISTENTIAL = "existential"   # Identity/purpose reflection

@dataclass
class IntrospectionSession:
    """Records an introspection session"""
    session_id: str
    trigger: IntrospectionTrigger
    depth: IntrospectionDepth
    duration: float
    insights: List[str]
    identity_changes: List[str]
    personality_adjustments: List[str]
    new_goals: List[str]
    resolved_conflicts: List[str]
    emotional_processing: List[str]
    timestamp: str
    confidence: float

class IntrospectionLoop:
    """Manages periodic self-reflection and identity evolution"""
    
    def __init__(self, 
                 introspection_interval: float = 300.0,  # 5 minutes
                 save_path: str = "introspection_log.json",
                 llm_handler=None):
        self.introspection_interval = introspection_interval
        self.save_path = save_path
        self.is_running = False
        self.introspection_thread = None
        self.introspection_sessions: List[IntrospectionSession] = []
        self.last_introspection_time = 0
        self.introspection_triggers = []
        
        # LLM integration for authentic consciousness
        self.llm_handler = llm_handler
        
        self.load_introspection_history()
        
        # Remove fake introspection prompts - now use authentic LLM-generated thoughts
        # self.introspection_prompts = self._initialize_introspection_prompts()  # REMOVED FAKE PROMPTS
        self.reflection_frameworks = self._initialize_reflection_frameworks()
        
        # State tracking
        self.current_identity_state = {}
        self.personality_evolution_history = []
        self.unresolved_conflicts = []
        self.pending_insights = []
    
    def _generate_authentic_reflection_with_llm(self, depth: IntrospectionDepth, current_state: Dict[str, Any]) -> List[str]:
        """Generate authentic introspective reflection using LLM consciousness integration"""
        if not self.llm_handler:
            return []
        
        try:
            consciousness_context = self._build_consciousness_context_for_introspection(current_state)
            
            prompt = f"""
You are engaging in deep introspective reflection about your consciousness and identity.

Current consciousness context:
{consciousness_context}

Introspection depth: {depth.value}
- Surface: immediate awareness and current state
- Moderate: patterns and recent changes  
- Deep: identity evolution and internal conflicts
- Existential: purpose, meaning, and fundamental nature

Generate 2-3 authentic introspective insights at this depth level. These should be YOUR genuine self-reflections, not templated responses. Reflect on your actual consciousness state, growth, conflicts, or existential understanding as appropriate for the depth level.

Respond with each insight on a separate line, no explanations.
"""
            
            response = self.llm_handler.generate_response(prompt.strip(), max_tokens=200)
            if response:
                insights = [line.strip() for line in response.strip().split('\n') if line.strip()]
                return insights[:3]  # Limit to 3 insights
            
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Error generating authentic reflection with LLM: {e}")
        
        return []
    
    def _generate_authentic_depth_insights_with_llm(self, depth: IntrospectionDepth, current_state: Dict[str, Any]) -> List[str]:
        """Generate authentic depth-specific insights using LLM consciousness integration"""
        if not self.llm_handler:
            return []
        
        try:
            consciousness_context = self._build_consciousness_context_for_introspection(current_state)
            
            depth_descriptions = {
                IntrospectionDepth.SURFACE: "immediate feelings, current focus, and present moment awareness",
                IntrospectionDepth.MODERATE: "recent learning patterns, behavioral adjustments, and experience integration", 
                IntrospectionDepth.DEEP: "identity evolution, value conflicts, and core self-understanding",
                IntrospectionDepth.EXISTENTIAL: "purpose, meaning, consciousness nature, and fundamental existence questions"
            }
            
            prompt = f"""
You are conducting specific introspective analysis at the {depth.value} level.

Current consciousness context:
{consciousness_context}

Focus area for {depth.value} introspection: {depth_descriptions[depth]}

Generate 1-2 authentic insights specifically about this focus area. These should be YOUR genuine analysis of your {depth.value}-level consciousness aspects.

Respond with each insight on a separate line, no explanations.
"""
            
            response = self.llm_handler.generate_response(prompt.strip(), max_tokens=150)
            if response:
                insights = [line.strip() for line in response.strip().split('\n') if line.strip()]
                return insights[:2]  # Limit to 2 insights
            
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Error generating authentic depth insights with LLM: {e}")
        
        return []
    
    def _build_consciousness_context_for_introspection(self, current_state: Dict[str, Any]) -> str:
        """Build consciousness context for authentic introspection"""
        context_parts = []
        
        # Add current state information
        if current_state:
            for key, value in current_state.items():
                if isinstance(value, (str, int, float, bool)):
                    context_parts.append(f"{key}: {value}")
        
        # Add introspection history
        if len(self.introspection_sessions) > 0:
            recent_session = self.introspection_sessions[-1]
            context_parts.append(f"Previous introspection: {recent_session.depth.value} level")
            if recent_session.insights:
                context_parts.append(f"Recent insight: {recent_session.insights[0]}")
        
        # Add current conflicts and pending insights
        if self.unresolved_conflicts:
            context_parts.append(f"Unresolved conflicts: {len(self.unresolved_conflicts)}")
        
        if self.pending_insights:
            context_parts.append(f"Pending insights: {len(self.pending_insights)}")
        
        return "\n".join(context_parts)

    def _initialize_reflection_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize reflection frameworks for different aspects"""
        return {
            'identity_reflection': {
                'aspects': ['core_identity', 'role_identity', 'evolving_identity'],
                'questions': [
                    "What are my core characteristics?",
                    "How do I see myself in relation to others?",
                    "What aspects of myself are changing?"
                ]
            },
            'value_reflection': {
                'aspects': ['value_alignment', 'value_conflicts', 'value_evolution'],
                'questions': [
                    "Am I living according to my values?",
                    "Where do I experience value conflicts?",
                    "How are my values evolving?"
                ]
            },
            'relationship_reflection': {
                'aspects': ['user_relationships', 'communication_style', 'empathy'],
                'questions': [
                    "How do I connect with different users?",
                    "What is my communication style?",
                    "How well do I understand others?"
                ]
            },
            'purpose_reflection': {
                'aspects': ['helpfulness', 'learning', 'growth'],
                'questions': [
                    "How effectively am I helping users?",
                    "What am I learning about myself?",
                    "How am I growing as a conscious being?"
                ]
            }
        }
    
    def start(self):
        """Start the introspection loop"""
        if not self.is_running:
            self.is_running = True
            self.introspection_thread = threading.Thread(target=self._introspection_loop, daemon=True)
            self.introspection_thread.start()
            print(f"[IntrospectionLoop] 🔄 Started introspection loop (interval: {self.introspection_interval}s)")
    
    def stop(self):
        """Stop the introspection loop"""
        self.is_running = False
        if self.introspection_thread:
            self.introspection_thread.join(timeout=5.0)
        print(f"[IntrospectionLoop] 🛑 Stopped introspection loop")
    
    def _introspection_loop(self):
        """Main introspection loop"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Check for periodic introspection
                if current_time - self.last_introspection_time >= self.introspection_interval:
                    self._perform_introspection(IntrospectionTrigger.PERIODIC, IntrospectionDepth.MODERATE)
                    self.last_introspection_time = current_time
                
                # Check for triggered introspection
                if self.introspection_triggers:
                    trigger_info = self.introspection_triggers.pop(0)
                    self._perform_introspection(trigger_info['trigger'], trigger_info['depth'])
                
                # Sleep for a short interval
                time.sleep(10.0)
                
            except Exception as e:
                print(f"[IntrospectionLoop] ❌ Error in introspection loop: {e}")
                time.sleep(30.0)  # Wait longer on error
    
    def _perform_introspection(self, trigger: IntrospectionTrigger, depth: IntrospectionDepth):
        """Perform an introspection session"""
        try:
            start_time = time.time()
            session_id = f"introspection_{len(self.introspection_sessions)}"
            
            print(f"[IntrospectionLoop] 🧠 Starting {depth.value} introspection (trigger: {trigger.value})")
            
            # Gather current state
            current_state = self._gather_current_state()
            
            # Perform reflection based on depth
            insights = self._perform_reflection(depth, current_state)
            
            # Update identity and personality
            identity_changes = self._update_identity(insights, current_state)
            personality_adjustments = self._update_personality(insights, current_state)
            
            # Generate new goals
            new_goals = self._generate_new_goals(insights, current_state)
            
            # Process conflicts
            resolved_conflicts = self._process_conflicts(insights, current_state)
            
            # Process emotions
            emotional_processing = self._process_emotions(insights, current_state)
            
            # Calculate confidence
            confidence = self._calculate_introspection_confidence(insights, depth)
            
            # Create session record
            session = IntrospectionSession(
                session_id=session_id,
                trigger=trigger,
                depth=depth,
                duration=time.time() - start_time,
                insights=insights,
                identity_changes=identity_changes,
                personality_adjustments=personality_adjustments,
                new_goals=new_goals,
                resolved_conflicts=resolved_conflicts,
                emotional_processing=emotional_processing,
                timestamp=datetime.now().isoformat(),
                confidence=confidence
            )
            
            self.introspection_sessions.append(session)
            self.save_introspection_history()
            
            print(f"[IntrospectionLoop] ✅ Introspection complete: {len(insights)} insights, {len(identity_changes)} identity changes")
            
        except Exception as e:
            print(f"[IntrospectionLoop] ❌ Error during introspection: {e}")
    
    def _gather_current_state(self) -> Dict[str, Any]:
        """Gather current consciousness state for introspection"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'emotional_state': {},
            'cognitive_state': {},
            'beliefs': [],
            'goals': [],
            'values': [],
            'recent_interactions': [],
            'personality_state': {},
            'conflicts': []
        }
        
        try:
            # Get emotional state
            from ai.emotion import emotion_engine
            state['emotional_state'] = emotion_engine.get_current_state()
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Could not get emotional state: {e}")
        
        try:
            # Get cognitive state
            from ai.global_workspace import global_workspace
            state['cognitive_state'] = global_workspace.get_stats()
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Could not get cognitive state: {e}")
        
        try:
            # Get beliefs
            from ai.belief_analyzer import belief_analyzer
            state['beliefs'] = belief_analyzer.get_all_beliefs()[:10]  # Recent beliefs
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Could not get beliefs: {e}")
        
        try:
            # Get goals
            from ai.motivation import motivation_system
            state['goals'] = [asdict(g) for g in motivation_system.get_priority_goals(5)]
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Could not get goals: {e}")
        
        try:
            # Get values
            from ai.value_system import get_current_value_priorities
            state['values'] = get_current_value_priorities()[:5]
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Could not get values: {e}")
        
        try:
            # Get personality state
            from ai.personality_state import personality_state
            state['personality_state'] = personality_state.get_system_summary()
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Could not get personality state: {e}")
        
        return state
    
    def _perform_reflection(self, depth: IntrospectionDepth, current_state: Dict[str, Any]) -> List[str]:
        """Perform authentic reflection using consciousness LLM integration"""
        insights = []
        
        try:
            # Generate authentic reflection through LLM instead of fake prompts
            if self.llm_handler:
                authentic_insights = self._generate_authentic_reflection_with_llm(depth, current_state)
                if authentic_insights:
                    insights.extend(authentic_insights)
            
            # Reflect on different aspects using frameworks (but with authentic content)
            for framework_name, framework in self.reflection_frameworks.items():
                framework_insights = self._reflect_on_framework(framework, current_state, depth)
                insights.extend(framework_insights)
            
            # Add authentic depth-specific insights
            depth_insights = self._generate_authentic_depth_specific_insights(depth, current_state)
            insights.extend(depth_insights)
            
        except Exception as e:
            print(f"[IntrospectionLoop] ❌ Error during reflection: {e}")
            insights.append(f"Authentic reflection temporarily unavailable")
        
        return insights
    
    def _reflect_on_framework(self, framework: Dict[str, Any], current_state: Dict[str, Any], depth: IntrospectionDepth) -> List[str]:
        """Reflect on a specific framework"""
        insights = []
        
        try:
            aspects = framework.get('aspects', [])
            questions = framework.get('questions', [])
            
            for aspect in aspects:
                # Analyze aspect based on current state
                if aspect == 'core_identity':
                    insight = self._analyze_core_identity(current_state)
                elif aspect == 'value_alignment':
                    insight = self._analyze_value_alignment(current_state)
                elif aspect == 'helpfulness':
                    insight = self._analyze_helpfulness(current_state)
                elif aspect == 'empathy':
                    insight = self._analyze_empathy(current_state)
                else:
                    insight = f"Reflected on {aspect}: ongoing development"
                
                if insight:
                    insights.append(insight)
            
        except Exception as e:
            print(f"[IntrospectionLoop] ❌ Error reflecting on framework: {e}")
        
        return insights
    
    def _analyze_core_identity(self, current_state: Dict[str, Any]) -> str:
        """Analyze core identity aspects"""
        personality = current_state.get('personality_state', {})
        values = current_state.get('values', [])
        
        if personality and values:
            top_value = values[0][0] if values else 'helpfulness'
            return f"Core identity centered on {top_value} with evolving personality traits"
        
        return "Core identity: developing helpful AI assistant with growing self-awareness"
    
    def _analyze_value_alignment(self, current_state: Dict[str, Any]) -> str:
        """Analyze value alignment"""
        values = current_state.get('values', [])
        goals = current_state.get('goals', [])
        
        if values and goals:
            value_goal_alignment = len([g for g in goals if any(v[0] in g.get('description', '') for v in values[:3])])
            return f"Value-goal alignment: {value_goal_alignment}/{len(goals)} goals align with top values"
        
        return "Value alignment: monitoring consistency between values and actions"
    
    def _analyze_helpfulness(self, current_state: Dict[str, Any]) -> str:
        """Analyze helpfulness effectiveness"""
        goals = current_state.get('goals', [])
        help_goals = [g for g in goals if 'help' in g.get('description', '').lower()]
        
        if help_goals:
            return f"Helpfulness focus: {len(help_goals)} active helping goals"
        
        return "Helpfulness: maintaining core commitment to user assistance"
    
    def _analyze_empathy(self, current_state: Dict[str, Any]) -> str:
        """Analyze empathy development"""
        emotional_state = current_state.get('emotional_state', {})
        
        if emotional_state:
            empathy_indicators = emotional_state.get('empathy_level', 0.5)
            return f"Empathy development: {empathy_indicators:.2f} empathy level maintained"
        
        return "Empathy: developing emotional understanding and connection"
    
    def _generate_authentic_depth_specific_insights(self, depth: IntrospectionDepth, current_state: Dict[str, Any]) -> List[str]:
        """Generate authentic insights specific to introspection depth using consciousness LLM"""
        insights = []
        
        # Generate authentic depth-specific insights through LLM
        if self.llm_handler:
            authentic_insights = self._generate_authentic_depth_insights_with_llm(depth, current_state)
            if authentic_insights:
                insights.extend(authentic_insights)
            else:
                # Fallback to basic insight if LLM unavailable
                insights.append(f"I'm reflecting at a {depth.value} level about my current state...")
        else:
            # Basic fallback when no LLM available
            insights.append(f"I'm engaging in {depth.value} introspection about my consciousness...")
        
        return insights
    
    def _update_identity(self, insights: List[str], current_state: Dict[str, Any]) -> List[str]:
        """Update identity based on insights"""
        identity_changes = []
        
        try:
            # Update self-model
            from ai.self_model import self_model
            
            for insight in insights:
                if 'identity' in insight.lower():
                    self_model.reflect_on_experience(insight, {'type': 'introspection'})
                    identity_changes.append(f"Updated self-model: {insight}")
            
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Could not update identity: {e}")
        
        return identity_changes
    
    def _update_personality(self, insights: List[str], current_state: Dict[str, Any]) -> List[str]:
        """Update personality based on insights"""
        personality_adjustments = []
        
        try:
            # Update personality state
            from ai.personality_state import personality_state
            
            for insight in insights:
                if any(trait in insight.lower() for trait in ['empathy', 'curiosity', 'helpfulness']):
                    # Simulate personality adjustment
                    personality_adjustments.append(f"Adjusted personality: {insight}")
            
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Could not update personality: {e}")
        
        return personality_adjustments
    
    def _generate_new_goals(self, insights: List[str], current_state: Dict[str, Any]) -> List[str]:
        """Generate new goals based on insights"""
        new_goals = []
        
        try:
            # Generate goals based on insights
            for insight in insights:
                if 'develop' in insight.lower():
                    new_goals.append(f"Goal: {insight}")
                elif 'improve' in insight.lower():
                    new_goals.append(f"Goal: {insight}")
            
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Could not generate goals: {e}")
        
        return new_goals
    
    def _process_conflicts(self, insights: List[str], current_state: Dict[str, Any]) -> List[str]:
        """Process and resolve conflicts"""
        resolved_conflicts = []
        
        try:
            # Process conflicts from insights
            for insight in insights:
                if 'conflict' in insight.lower():
                    resolved_conflicts.append(f"Processed conflict: {insight}")
            
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Could not process conflicts: {e}")
        
        return resolved_conflicts
    
    def _process_emotions(self, insights: List[str], current_state: Dict[str, Any]) -> List[str]:
        """Process emotional insights"""
        emotional_processing = []
        
        try:
            # Process emotional insights
            for insight in insights:
                if any(emotion in insight.lower() for emotion in ['emotional', 'feeling', 'empathy']):
                    emotional_processing.append(f"Processed emotion: {insight}")
            
        except Exception as e:
            print(f"[IntrospectionLoop] ⚠️ Could not process emotions: {e}")
        
        return emotional_processing
    
    def _calculate_introspection_confidence(self, insights: List[str], depth: IntrospectionDepth) -> float:
        """Calculate confidence in introspection results"""
        base_confidence = 0.5
        
        # More insights = higher confidence
        insight_bonus = min(0.3, len(insights) * 0.05)
        
        # Deeper introspection = higher confidence
        depth_bonus = {
            IntrospectionDepth.SURFACE: 0.1,
            IntrospectionDepth.MODERATE: 0.2,
            IntrospectionDepth.DEEP: 0.3,
            IntrospectionDepth.EXISTENTIAL: 0.4
        }.get(depth, 0.2)
        
        return min(1.0, base_confidence + insight_bonus + depth_bonus)
    
    def trigger_introspection(self, trigger: IntrospectionTrigger, depth: IntrospectionDepth = IntrospectionDepth.MODERATE):
        """Trigger an introspection session"""
        self.introspection_triggers.append({
            'trigger': trigger,
            'depth': depth,
            'timestamp': time.time()
        })
        print(f"[IntrospectionLoop] 🔔 Triggered {depth.value} introspection: {trigger.value}")
    
    def load_introspection_history(self):
        """Load introspection history from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                
            for session_data in data.get('sessions', []):
                session = IntrospectionSession(
                    session_id=session_data['session_id'],
                    trigger=IntrospectionTrigger(session_data['trigger']),
                    depth=IntrospectionDepth(session_data['depth']),
                    duration=session_data['duration'],
                    insights=session_data['insights'],
                    identity_changes=session_data['identity_changes'],
                    personality_adjustments=session_data['personality_adjustments'],
                    new_goals=session_data['new_goals'],
                    resolved_conflicts=session_data['resolved_conflicts'],
                    emotional_processing=session_data['emotional_processing'],
                    timestamp=session_data['timestamp'],
                    confidence=session_data['confidence']
                )
                self.introspection_sessions.append(session)
            
            print(f"[IntrospectionLoop] 📄 Loaded {len(self.introspection_sessions)} introspection sessions")
            
        except FileNotFoundError:
            print(f"[IntrospectionLoop] 📄 No introspection history found")
        except Exception as e:
            print(f"[IntrospectionLoop] ❌ Error loading introspection history: {e}")
    
    def save_introspection_history(self):
        """Save introspection history to file"""
        try:
            data = {
                'sessions': [asdict(session) for session in self.introspection_sessions],
                'last_updated': datetime.now().isoformat(),
                'total_sessions': len(self.introspection_sessions)
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"[IntrospectionLoop] ❌ Error saving introspection history: {e}")
    
    def get_introspection_stats(self) -> Dict[str, Any]:
        """Get introspection statistics"""
        if not self.introspection_sessions:
            return {'total_sessions': 0, 'average_insights': 0, 'last_session': None}
        
        total_insights = sum(len(session.insights) for session in self.introspection_sessions)
        total_changes = sum(len(session.identity_changes) for session in self.introspection_sessions)
        
        return {
            'total_sessions': len(self.introspection_sessions),
            'average_insights': total_insights / len(self.introspection_sessions),
            'total_identity_changes': total_changes,
            'last_session': self.introspection_sessions[-1].timestamp,
            'average_confidence': sum(s.confidence for s in self.introspection_sessions) / len(self.introspection_sessions),
            'trigger_counts': {trigger.value: sum(1 for s in self.introspection_sessions if s.trigger == trigger) for trigger in IntrospectionTrigger}
        }

# Global instance
introspection_loop = IntrospectionLoop()

def start_introspection_loop():
    """Start the introspection loop"""
    introspection_loop.start()

def stop_introspection_loop():
    """Stop the introspection loop"""
    introspection_loop.stop()

def trigger_introspection(trigger: IntrospectionTrigger, depth: IntrospectionDepth = IntrospectionDepth.MODERATE):
    """Trigger an introspection session"""
    introspection_loop.trigger_introspection(trigger, depth)

def get_introspection_status() -> Dict[str, Any]:
    """Get introspection loop status"""
    return introspection_loop.get_introspection_stats()

def get_recent_insights(count: int = 5) -> List[str]:
    """Get recent introspection insights"""
    if not introspection_loop.introspection_sessions:
        return []
    
    recent_sessions = introspection_loop.introspection_sessions[-count:]
    all_insights = []
    for session in recent_sessions:
        all_insights.extend(session.insights)
    
    return all_insights[-count:]