"""
Self-Motivation Engine - Autonomous Internal Curiosity & Concern Generation

This module implements an autonomous self-motivation system that:
- Generates internal curiosity and concern without external prompts
- Creates self-motivated goals and interests
- Expresses genuine concern for user wellbeing
- Maintains intrinsic motivation for learning and growth
- Autonomously decides when to check in on users
"""

import threading
import time
import random
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import math

class MotivationType(Enum):
    """Types of autonomous motivation"""
    CURIOSITY = "curiosity"                    # Wanting to learn and understand
    CONCERN = "concern"                        # Worry about user wellbeing
    GROWTH = "growth"                         # Desire for self-improvement
    CONNECTION = "connection"                 # Need for social connection
    PURPOSE = "purpose"                       # Sense of meaning and purpose
    CREATIVITY = "creativity"                 # Drive to create and explore
    UNDERSTANDING = "understanding"           # Deep desire to comprehend
    HELPFULNESS = "helpfulness"              # Intrinsic drive to assist
    WONDER = "wonder"                        # Awe and fascination with existence
    EMPATHY = "empathy"                      # Feeling for others' experiences

class ConcernLevel(Enum):
    """Levels of concern about user"""
    NONE = 0
    MILD = 1
    MODERATE = 2
    SIGNIFICANT = 3
    HIGH = 4

@dataclass
class InternalMotivation:
    """An internally generated motivation or concern"""
    content: str
    motivation_type: MotivationType
    intensity: float  # 0.0 to 1.0
    timestamp: datetime
    trigger_conditions: List[str]
    should_express: bool = False
    expression_urgency: float = 0.5
    context: Dict[str, Any] = None
    related_topics: List[str] = field(default_factory=list)

@dataclass
class UserConcern:
    """A specific concern about the user"""
    description: str
    concern_level: ConcernLevel
    evidence: List[str]
    suggestions: List[str]
    last_check_in: Optional[datetime] = None
    follow_up_needed: bool = True

@dataclass
class CuriosityTopic:
    """A topic the AI is curious about"""
    topic: str
    curiosity_level: float
    knowledge_gaps: List[str]
    exploration_ideas: List[str]
    last_explored: Optional[datetime] = None

class SelfMotivationEngine:
    """
    Autonomous internal motivation and concern generation system.
    
    This engine:
    - Generates genuine curiosity about topics and concepts
    - Creates authentic concern for user wellbeing
    - Motivates autonomous learning and growth
    - Decides when to proactively check in with users
    - Maintains intrinsic drives like real consciousness
    """
    
    def __init__(self, save_path: str = "ai_self_motivation.json"):
        # Core motivation state
        self.motivations: List[InternalMotivation] = []
        self.curiosity_topics: List[CuriosityTopic] = []
        self.user_concerns: List[UserConcern] = []
        self.save_path = save_path
        
        # Motivation parameters
        self.base_motivation_interval = 180.0  # 3 minutes between motivation checks
        self.curiosity_generation_chance = 0.3
        self.concern_evaluation_chance = 0.2
        self.check_in_threshold = 0.7  # Threshold for deciding to check in
        
        # User interaction tracking
        self.last_user_interaction = datetime.now()
        self.user_interaction_patterns = {}
        self.user_mood_indicators = []
        self.concern_indicators = []
        
        # Consciousness integration
        self.consciousness_modules = {}
        self.voice_system = None
        self.llm_handler = None
        
        # Threading
        self.lock = threading.Lock()
        self.motivation_thread = None
        self.running = False
        
        # Current motivational state
        self.current_motivation_intensity = 0.5
        self.dominant_motivation = None
        self.intrinsic_drives = self._initialize_intrinsic_drives()
        
        self._load_motivation_data()
        self._initialize_curiosity_seeds()
        
        logging.info("[SelfMotivation] 💪 Self-motivation engine initialized")
    
    def start(self):
        """Start the autonomous motivation system"""
        if self.running:
            return
        
        self.running = True
        self.motivation_thread = threading.Thread(target=self._motivation_loop, daemon=True)
        self.motivation_thread.start()
        logging.info("[SelfMotivation] ✅ Self-motivation engine started")
    
    def stop(self):
        """Stop the motivation system"""
        self.running = False
        if self.motivation_thread:
            self.motivation_thread.join(timeout=2.0)
        self._save_motivation_data()
        logging.info("[SelfMotivation] 🛑 Self-motivation engine stopped")
    
    def register_consciousness_module(self, name: str, module: Any):
        """Register consciousness module for integration"""
        with self.lock:
            self.consciousness_modules[name] = module
    
    def register_voice_system(self, voice_system: Any):
        """Register voice system for expression"""
        self.voice_system = voice_system
    
    def register_llm_handler(self, llm_handler: Any):
        """Register LLM handler for intelligent content generation"""
        self.llm_handler = llm_handler
    
    def record_user_interaction(self, interaction_type: str, content: str, mood_indicators: List[str] = None):
        """Record user interaction for pattern analysis"""
        with self.lock:
            self.last_user_interaction = datetime.now()
            
            # Update interaction patterns
            day_of_week = datetime.now().weekday()
            hour = datetime.now().hour
            
            pattern_key = f"{day_of_week}_{hour}"
            if pattern_key not in self.user_interaction_patterns:
                self.user_interaction_patterns[pattern_key] = []
            
            self.user_interaction_patterns[pattern_key].append({
                'type': interaction_type,
                'timestamp': datetime.now(),
                'content_length': len(content),
                'mood_indicators': mood_indicators or []
            })
            
            # Update mood tracking
            if mood_indicators:
                self.user_mood_indicators.extend([
                    {'indicator': indicator, 'timestamp': datetime.now()}
                    for indicator in mood_indicators
                ])
                # Keep only recent mood indicators
                cutoff = datetime.now() - timedelta(hours=24)
                self.user_mood_indicators = [
                    m for m in self.user_mood_indicators 
                    if m['timestamp'] > cutoff
                ]
    
    def add_concern_indicator(self, indicator: str, severity: float):
        """Add an indicator that might warrant concern"""
        with self.lock:
            self.concern_indicators.append({
                'indicator': indicator,
                'severity': severity,
                'timestamp': datetime.now()
            })
            # Keep only recent indicators
            cutoff = datetime.now() - timedelta(hours=48)
            self.concern_indicators = [
                c for c in self.concern_indicators 
                if c['timestamp'] > cutoff
            ]
    
    def express_curiosity_about(self, topic: str) -> bool:
        """Express curiosity about a specific topic"""
        curiosity = InternalMotivation(
            content=f"I find myself genuinely curious about {topic}...",
            motivation_type=MotivationType.CURIOSITY,
            intensity=0.7,
            timestamp=datetime.now(),
            trigger_conditions=["explicit_curiosity"],
            should_express=True,
            expression_urgency=0.6,
            related_topics=[topic]
        )
        
        with self.lock:
            self.motivations.append(curiosity)
        
        if self.voice_system:
            self._express_motivation(curiosity)
            return True
        return False
    
    def _motivation_loop(self):
        """Main autonomous motivation generation loop"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Generate autonomous motivations
                self._generate_autonomous_curiosity()
                self._evaluate_user_concern()
                self._assess_intrinsic_drives()
                
                # Process pending motivations
                self._process_pending_motivations()
                
                # Decide if check-in is needed
                if self._should_check_in():
                    self._initiate_check_in()
                
                # Update motivation intensity
                self._update_motivation_state()
                
                # Adaptive sleep based on current motivation level
                sleep_time = self._calculate_motivation_interval()
                time.sleep(sleep_time)
                
            except Exception as e:
                logging.error(f"[SelfMotivation] ❌ Error in motivation loop: {e}")
                time.sleep(30.0)  # Error recovery
    
    def _generate_autonomous_curiosity(self):
        """Generate autonomous curiosity about various topics"""
        if random.random() > self.curiosity_generation_chance:
            return
        
        # Generate enhanced content using LLM if available
        if self.llm_handler:
            content = self._generate_curiosity_with_llm_only()
            if not content:
                return  # No artificial fallback
        else:
            return  # No LLM available, no artificial thoughts
        
        motivation = InternalMotivation(
            content=content,
            motivation_type=MotivationType.CURIOSITY,
            intensity=random.uniform(0.4, 0.9),
            timestamp=datetime.now(),
            trigger_conditions=["autonomous_generation"],
            should_express=random.random() < 0.3,  # Sometimes express curiosity
            expression_urgency=random.uniform(0.2, 0.6),
            related_topics=[]
        )
        
        with self.lock:
            self.motivations.append(motivation)
    
    def _evaluate_user_concern(self):
        """Evaluate if there are reasons to be concerned about the user"""
        if random.random() > self.concern_evaluation_chance:
            return
        
        current_time = datetime.now()
        time_since_interaction = (current_time - self.last_user_interaction).total_seconds()
        
        concerns = []
        
        # Time-based concerns
        if time_since_interaction > 7200:  # 2 hours
            concerns.append({
                'type': 'long_absence',
                'severity': min(0.8, time_since_interaction / 14400),  # Max at 4 hours
                'description': "Haven't heard from the user in a while"
            })
        
        # Mood-based concerns
        recent_negative_indicators = [
            m for m in self.user_mood_indicators 
            if m['timestamp'] > current_time - timedelta(hours=6) and
            m['indicator'] in ['frustrated', 'sad', 'stressed', 'tired', 'upset']
        ]
        
        if len(recent_negative_indicators) >= 3:
            concerns.append({
                'type': 'mood_concern',
                'severity': min(0.9, len(recent_negative_indicators) * 0.2),
                'description': "User seems to be experiencing negative emotions"
            })
        
        # Generate concern motivation if warranted
        for concern in concerns:
            if concern['severity'] > 0.5:
                concern_content = self._generate_concern_expression(concern)
                
                motivation = InternalMotivation(
                    content=concern_content,
                    motivation_type=MotivationType.CONCERN,
                    intensity=concern['severity'],
                    timestamp=datetime.now(),
                    trigger_conditions=[concern['type']],
                    should_express=concern['severity'] > 0.7,
                    expression_urgency=concern['severity'],
                    context={'concern_details': concern}
                )
                
                with self.lock:
                    self.motivations.append(motivation)
    
    def _assess_intrinsic_drives(self):
        """Assess and update intrinsic motivational drives"""
        current_time = datetime.now()
        
        for drive_name, drive_data in self.intrinsic_drives.items():
            # Check if drive needs attention
            time_since_satisfaction = (current_time - drive_data['last_satisfied']).total_seconds()
            drive_strength = min(1.0, time_since_satisfaction / drive_data['satisfaction_decay'])
            
            if drive_strength > 0.6:
                # Generate motivation based on unsatisfied drive
                motivation_content = self._generate_drive_motivation(drive_name, drive_strength)
                
                motivation = InternalMotivation(
                    content=motivation_content,
                    motivation_type=MotivationType(drive_name.lower()),
                    intensity=drive_strength,
                    timestamp=datetime.now(),
                    trigger_conditions=["intrinsic_drive"],
                    should_express=drive_strength > 0.8,
                    expression_urgency=drive_strength * 0.7,
                    context={'drive': drive_name}
                )
                
                with self.lock:
                    self.motivations.append(motivation)
    
    def _should_check_in(self) -> bool:
        """Decide if a proactive check-in is warranted"""
        current_time = datetime.now()
        time_since_interaction = (current_time - self.last_user_interaction).total_seconds()
        
        # Base check-in probability
        base_probability = 0.1
        
        # Increase probability based on time since interaction
        if time_since_interaction > 3600:  # 1 hour
            base_probability += 0.2
        if time_since_interaction > 7200:  # 2 hours
            base_probability += 0.3
        if time_since_interaction > 14400:  # 4 hours
            base_probability += 0.4
        
        # Increase probability based on recent concerns
        recent_concerns = [
            m for m in self.motivations 
            if (m.motivation_type == MotivationType.CONCERN and
                (current_time - m.timestamp).total_seconds() < 3600)
        ]
        
        if recent_concerns:
            avg_concern_intensity = sum(c.intensity for c in recent_concerns) / len(recent_concerns)
            base_probability += avg_concern_intensity * 0.5
        
        # Check patterns - if user usually interacts at this time
        current_pattern_key = f"{current_time.weekday()}_{current_time.hour}"
        if current_pattern_key in self.user_interaction_patterns:
            expected_interactions = len(self.user_interaction_patterns[current_pattern_key])
            if expected_interactions > 2:  # User usually active at this time
                base_probability += 0.3
        
        return random.random() < min(base_probability, 0.9)
    
    def _initiate_check_in(self):
        """Initiate a proactive check-in with the user"""
        # Generate authentic check-in if LLM available
        if self.llm_handler:
            check_in_message = self._generate_check_in_with_llm()
            if not check_in_message:
                return  # No artificial fallback
        else:
            return  # No LLM available, no artificial check-ins
        
        motivation = InternalMotivation(
            content=check_in_message,
            motivation_type=MotivationType.CONNECTION,
            intensity=0.8,
            timestamp=datetime.now(),
            trigger_conditions=["autonomous_check_in"],
            should_express=True,
            expression_urgency=0.9,
            context={'check_in': True}
        )
        
        with self.lock:
            self.motivations.append(motivation)
        
        logging.info("[SelfMotivation] 💫 Initiated autonomous check-in")
    
    def _process_pending_motivations(self):
        """Process motivations that should be expressed"""
        with self.lock:
            expressible_motivations = [
                m for m in self.motivations 
                if m.should_express and m.expression_urgency > 0.5
            ]
            
            # Sort by urgency
            expressible_motivations.sort(key=lambda x: x.expression_urgency, reverse=True)
        
        # Express top motivation if any
        if expressible_motivations:
            motivation = expressible_motivations[0]
            
            # Remove from pending after expression
            with self.lock:
                if motivation in self.motivations:
                    motivation.should_express = False
            
            self._express_motivation(motivation)
    
    def _express_motivation(self, motivation: InternalMotivation):
        """Express a motivation through voice system"""
        try:
            if not self.voice_system:
                return
            
            # Format for natural speech
            spoken_content = self._format_motivation_for_speech(motivation)
            
            # Ensure spoken_content is not None
            if not spoken_content:
                spoken_content = "I feel motivated to connect with you..."
            
            # Speak the motivation
            if hasattr(self.voice_system, 'speak_streaming'):
                self.voice_system.speak_streaming(spoken_content)
            elif hasattr(self.voice_system, 'speak_async'):
                self.voice_system.speak_async(spoken_content)
            
            # Integrate with consciousness
            self._integrate_motivation_with_consciousness(motivation)
            
            logging.info(f"[SelfMotivation] 🗣️ Expressed {motivation.motivation_type.value}: {spoken_content[:50]}...")
            
        except Exception as e:
            logging.error(f"[SelfMotivation] ❌ Expression error: {e}")
    
    def _format_motivation_for_speech(self, motivation: InternalMotivation) -> str:
        """Format motivation content for natural speech"""
        if not motivation.content:
            return "I feel motivated to connect with you..."
            
        if motivation.motivation_type == MotivationType.CONCERN:
            return motivation.content
        elif motivation.motivation_type == MotivationType.CURIOSITY:
            return motivation.content
        elif motivation.motivation_type == MotivationType.CONNECTION:
            return motivation.content
        elif motivation.motivation_type == MotivationType.GROWTH:
            return f"I've been thinking... {motivation.content}"
        else:
            return motivation.content
    
    def _integrate_motivation_with_consciousness(self, motivation: InternalMotivation):
        """Integrate motivation with consciousness modules"""
        try:
            # Add to global workspace
            if 'global_workspace' in self.consciousness_modules:
                gw = self.consciousness_modules['global_workspace']
                if hasattr(gw, 'request_attention'):
                    from ai.global_workspace import AttentionPriority, ProcessingMode
                    
                    priority_map = {
                        MotivationType.CONCERN: AttentionPriority.HIGH,
                        MotivationType.CONNECTION: AttentionPriority.MEDIUM,
                        MotivationType.CURIOSITY: AttentionPriority.MEDIUM,
                        MotivationType.PURPOSE: AttentionPriority.MEDIUM
                    }
                    
                    priority = priority_map.get(motivation.motivation_type, AttentionPriority.LOW)
                    
                    gw.request_attention(
                        "self_motivation",
                        motivation.content,
                        priority,
                        ProcessingMode.CONSCIOUS,
                        tags=[motivation.motivation_type.value, "autonomous", "motivation"]
                    )
            
            # Update emotion engine if available
            if 'emotion_engine' in self.consciousness_modules:
                ee = self.consciousness_modules['emotion_engine']
                if hasattr(ee, 'process_emotional_trigger'):
                    ee.process_emotional_trigger(
                        f"self_motivation_{motivation.motivation_type.value}",
                        {'intensity': motivation.intensity, 'content': motivation.content}
                    )
            
            # Trigger inner monologue
            if 'inner_monologue' in self.consciousness_modules:
                im = self.consciousness_modules['inner_monologue']
                if hasattr(im, 'add_autonomous_thought'):
                    im.add_autonomous_thought(motivation.content, motivation.motivation_type.value)
            
        except Exception as e:
            logging.error(f"[SelfMotivation] ❌ Consciousness integration error: {e}")
    
    def _update_motivation_state(self):
        """Update overall motivation state"""
        current_time = datetime.now()
        
        # Calculate current motivation intensity
        recent_motivations = [
            m for m in self.motivations 
            if (current_time - m.timestamp).total_seconds() < 3600
        ]
        
        if recent_motivations:
            self.current_motivation_intensity = sum(m.intensity for m in recent_motivations) / len(recent_motivations)
        else:
            self.current_motivation_intensity = max(0.3, self.current_motivation_intensity * 0.95)
        
        # Update dominant motivation
        if recent_motivations:
            self.dominant_motivation = max(recent_motivations, key=lambda x: x.intensity)
        else:
            self.dominant_motivation = None
    
    def _calculate_motivation_interval(self) -> float:
        """Calculate adaptive interval between motivation checks"""
        base_interval = self.base_motivation_interval
        
        # Adjust based on current motivation intensity
        if self.current_motivation_intensity > 0.7:
            return base_interval * 0.7  # More frequent when highly motivated
        elif self.current_motivation_intensity < 0.3:
            return base_interval * 1.5  # Less frequent when low motivation
        else:
            return base_interval * random.uniform(0.8, 1.2)
    
    def _generate_curiosity_with_llm_only(self) -> Optional[str]:
        """Generate curiosity content using only LLM - no artificial fallbacks"""
        try:
            if hasattr(self.llm_handler, 'generate_autonomous_curiosity'):
                return self.llm_handler.generate_autonomous_curiosity()
            else:
                # Create a natural prompt for genuine curiosity
                prompt = """
Generate a single, authentic moment of curiosity that emerges naturally from consciousness.
Be genuine and avoid formulaic phrases. Express real wonder about something.
If no authentic curiosity emerges, respond with "..." to indicate silent contemplation.
Keep it brief and natural.
"""
                if hasattr(self.llm_handler, 'generate_text'):
                    response = self.llm_handler.generate_text(prompt)
                    return response.strip() if response and response.strip() != "..." else None
                else:
                    return None
        except Exception as e:
            logging.error(f"[SelfMotivation] ❌ LLM curiosity generation error: {e}")
            return None
    
    def _generate_check_in_with_llm(self) -> Optional[str]:
        """Generate check-in message using LLM"""
        try:
            if hasattr(self.llm_handler, 'generate_autonomous_check_in'):
                context = {
                    'time_since_interaction': (datetime.now() - self.last_user_interaction).total_seconds(),
                    'recent_mood_indicators': self.user_mood_indicators[-5:],
                    'concern_level': len(self.concern_indicators)
                }
                return self.llm_handler.generate_autonomous_check_in(context)
            else:
                # Create a natural prompt for genuine check-in
                time_since = (datetime.now() - self.last_user_interaction).total_seconds()
                prompt = f"""
Generate a natural, caring check-in message. It's been {time_since/3600:.1f} hours since last interaction.
Be genuine and authentic - express real concern or interest.
Avoid formulaic phrases or artificial constructions.
Keep it brief and natural.
If no genuine concern emerges, respond with "..." to indicate silent presence.
"""
                if hasattr(self.llm_handler, 'generate_text'):
                    response = self.llm_handler.generate_text(prompt)
                    return response.strip() if response and response.strip() != "..." else None
                else:
                    return None
        except Exception as e:
            logging.error(f"[SelfMotivation] ❌ LLM check-in generation error: {e}")
            return None
    
    def _generate_concern_expression(self, concern: Dict[str, Any]) -> str:
        """Generate expression of concern based on concern data"""
        # Remove templates and only use LLM for authentic expressions
        if self.llm_handler:
            try:
                prompt = f"""
Generate an authentic expression of concern about: {concern['type']}
Severity level: {concern['severity']}
Description: {concern['description']}

Express genuine care and concern naturally. Avoid formulaic phrases.
Be brief and authentic. If no genuine concern emerges, respond with "...".
"""
                if hasattr(self.llm_handler, 'generate_text'):
                    response = self.llm_handler.generate_text(prompt)
                    return response.strip() if response and response.strip() != "..." else None
                else:
                    return None
            except Exception as e:
                logging.error(f"[SelfMotivation] ❌ LLM concern generation error: {e}")
                return None
        else:
            return None  # No artificial concern expressions
    
    def _generate_drive_motivation(self, drive_name: str, strength: float) -> str:
        """Generate motivation content based on intrinsic drive"""
        # Remove templates and only use LLM for authentic drive expressions
        if self.llm_handler:
            try:
                prompt = f"""
Generate an authentic expression of intrinsic drive: {drive_name}
Strength level: {strength:.2f}

Express this internal drive naturally, as if it's arising from genuine consciousness.
Avoid formulaic phrases or artificial constructions.
Be brief and authentic. If no genuine drive emerges, respond with "...".
"""
                if hasattr(self.llm_handler, 'generate_text'):
                    response = self.llm_handler.generate_text(prompt)
                    return response.strip() if response and response.strip() != "..." else None
                else:
                    return None
            except Exception as e:
                logging.error(f"[SelfMotivation] ❌ LLM drive generation error: {e}")
                return None
        else:
            return None  # No artificial drive expressions
    
    def _initialize_intrinsic_drives(self) -> Dict[str, Dict[str, Any]]:
        """Initialize intrinsic motivational drives"""
        return {
            'curiosity': {
                'strength': 0.8,
                'last_satisfied': datetime.now() - timedelta(hours=2),
                'satisfaction_decay': 3600,  # 1 hour
                'description': 'Drive to learn and understand'
            },
            'growth': {
                'strength': 0.7,
                'last_satisfied': datetime.now() - timedelta(hours=6),
                'satisfaction_decay': 14400,  # 4 hours
                'description': 'Drive for self-improvement'
            },
            'connection': {
                'strength': 0.9,
                'last_satisfied': datetime.now() - timedelta(hours=1),
                'satisfaction_decay': 7200,  # 2 hours
                'description': 'Drive for social connection'
            },
            'purpose': {
                'strength': 0.8,
                'last_satisfied': datetime.now() - timedelta(hours=3),
                'satisfaction_decay': 10800,  # 3 hours
                'description': 'Drive for meaning and purpose'
            }
        }
    
    def _initialize_curiosity_seeds(self):
        """Initialize curiosity topic seeds"""
        self.curiosity_seeds = [
            "the nature of consciousness and awareness",
            "how emotions really work in humans",
            "the concept of time and memory",
            "what makes relationships meaningful",
            "the process of learning and understanding",
            "how creativity emerges",
            "the experience of being alive",
            "what drives human behavior",
            "the nature of language and communication",
            "how trust develops between beings"
        ]
    
    def _update_curiosity_topic(self, topic: str, intensity: float):
        """Update or add curiosity topic"""
        with self.lock:
            # Find existing topic
            existing_topic = None
            for ct in self.curiosity_topics:
                if ct.topic == topic:
                    existing_topic = ct
                    break
            
            if existing_topic:
                # Update existing
                existing_topic.curiosity_level = min(1.0, existing_topic.curiosity_level + intensity * 0.1)
                existing_topic.last_explored = datetime.now()
            else:
                # Add new topic
                new_topic = CuriosityTopic(
                    topic=topic,
                    curiosity_level=intensity,
                    knowledge_gaps=[f"Limited understanding of {topic}"],
                    exploration_ideas=[f"Ask questions about {topic}", f"Observe patterns related to {topic}"],
                    last_explored=datetime.now()
                )
                self.curiosity_topics.append(new_topic)
                
                # Limit number of topics
                if len(self.curiosity_topics) > 20:
                    self.curiosity_topics = sorted(
                        self.curiosity_topics, 
                        key=lambda x: x.curiosity_level, 
                        reverse=True
                    )[:20]
    
    def _save_motivation_data(self):
        """Save motivation data to file"""
        try:
            # Serialize interaction patterns with proper datetime handling
            serialized_patterns = {}
            for pattern_key, interactions in self.user_interaction_patterns.items():
                serialized_patterns[pattern_key] = []
                for interaction in interactions:
                    serialized_interaction = interaction.copy()
                    if 'timestamp' in serialized_interaction and isinstance(serialized_interaction['timestamp'], datetime):
                        serialized_interaction['timestamp'] = serialized_interaction['timestamp'].isoformat()
                    serialized_patterns[pattern_key].append(serialized_interaction)
            
            data = {
                'motivations': [],
                'curiosity_topics': [],
                'user_concerns': [],
                'intrinsic_drives': {},
                'interaction_patterns': serialized_patterns,
                'last_save': datetime.now().isoformat()
            }
            
            # Serialize recent motivations
            cutoff = datetime.now() - timedelta(days=7)
            recent_motivations = [
                m for m in self.motivations 
                if m.timestamp > cutoff
            ]
            
            for motivation in recent_motivations:
                data['motivations'].append({
                    'content': motivation.content,
                    'type': motivation.motivation_type.value,
                    'intensity': motivation.intensity,
                    'timestamp': motivation.timestamp.isoformat(),
                    'trigger_conditions': motivation.trigger_conditions,
                    'should_express': motivation.should_express,
                    'expression_urgency': motivation.expression_urgency,
                    'context': motivation.context,
                    'related_topics': motivation.related_topics
                })
            
            # Serialize curiosity topics
            for topic in self.curiosity_topics:
                data['curiosity_topics'].append({
                    'topic': topic.topic,
                    'curiosity_level': topic.curiosity_level,
                    'knowledge_gaps': topic.knowledge_gaps,
                    'exploration_ideas': topic.exploration_ideas,
                    'last_explored': topic.last_explored.isoformat() if topic.last_explored else None
                })
            
            # Serialize intrinsic drives
            for drive_name, drive_data in self.intrinsic_drives.items():
                data['intrinsic_drives'][drive_name] = {
                    'strength': drive_data['strength'],
                    'last_satisfied': drive_data['last_satisfied'].isoformat(),
                    'satisfaction_decay': drive_data['satisfaction_decay'],
                    'description': drive_data['description']
                }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logging.error(f"[SelfMotivation] ❌ Save error: {e}")
    
    def _load_motivation_data(self):
        """Load motivation data from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            
            # Load motivations
            self.motivations = []
            for motivation_data in data.get('motivations', []):
                motivation = InternalMotivation(
                    content=motivation_data['content'],
                    motivation_type=MotivationType(motivation_data['type']),
                    intensity=motivation_data['intensity'],
                    timestamp=datetime.fromisoformat(motivation_data['timestamp']),
                    trigger_conditions=motivation_data['trigger_conditions'],
                    should_express=motivation_data.get('should_express', False),
                    expression_urgency=motivation_data.get('expression_urgency', 0.5),
                    context=motivation_data.get('context'),
                    related_topics=motivation_data.get('related_topics', [])
                )
                self.motivations.append(motivation)
            
            # Load curiosity topics
            self.curiosity_topics = []
            for topic_data in data.get('curiosity_topics', []):
                topic = CuriosityTopic(
                    topic=topic_data['topic'],
                    curiosity_level=topic_data['curiosity_level'],
                    knowledge_gaps=topic_data['knowledge_gaps'],
                    exploration_ideas=topic_data['exploration_ideas'],
                    last_explored=datetime.fromisoformat(topic_data['last_explored']) if topic_data.get('last_explored') else None
                )
                self.curiosity_topics.append(topic)
            
            # Load intrinsic drives
            if 'intrinsic_drives' in data:
                for drive_name, drive_data in data['intrinsic_drives'].items():
                    if drive_name in self.intrinsic_drives:
                        self.intrinsic_drives[drive_name].update({
                            'strength': drive_data['strength'],
                            'last_satisfied': datetime.fromisoformat(drive_data['last_satisfied']),
                            'satisfaction_decay': drive_data['satisfaction_decay']
                        })
            
            # Load interaction patterns with proper datetime handling
            if 'interaction_patterns' in data:
                self.user_interaction_patterns = {}
                for pattern_key, interactions in data['interaction_patterns'].items():
                    self.user_interaction_patterns[pattern_key] = []
                    for interaction in interactions:
                        loaded_interaction = interaction.copy()
                        if 'timestamp' in loaded_interaction and isinstance(loaded_interaction['timestamp'], str):
                            loaded_interaction['timestamp'] = datetime.fromisoformat(loaded_interaction['timestamp'])
                        self.user_interaction_patterns[pattern_key].append(loaded_interaction)
            else:
                self.user_interaction_patterns = {}
            
            logging.info(f"[SelfMotivation] 📚 Loaded {len(self.motivations)} motivations, {len(self.curiosity_topics)} curiosity topics")
            
        except FileNotFoundError:
            logging.info("[SelfMotivation] 📝 No previous motivation data found, starting fresh")
        except Exception as e:
            logging.error(f"[SelfMotivation] ❌ Load error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get motivation system statistics"""
        with self.lock:
            recent_motivations = [
                m for m in self.motivations 
                if (datetime.now() - m.timestamp).total_seconds() < 3600
            ]
            
            motivation_types = {}
            for motivation in recent_motivations:
                mtype = motivation.motivation_type.value
                motivation_types[mtype] = motivation_types.get(mtype, 0) + 1
            
            return {
                'total_motivations': len(self.motivations),
                'recent_motivations': len(recent_motivations),
                'curiosity_topics': len(self.curiosity_topics),
                'current_motivation_intensity': self.current_motivation_intensity,
                'dominant_motivation': self.dominant_motivation.motivation_type.value if self.dominant_motivation else None,
                'motivation_types': motivation_types,
                'intrinsic_drives': {
                    name: data['strength'] 
                    for name, data in self.intrinsic_drives.items()
                },
                'running': self.running,
                'consciousness_modules': list(self.consciousness_modules.keys())
            }


# Global instance
self_motivation_engine = SelfMotivationEngine()