"""
Autonomous Consciousness Integrator - Central Orchestration System

This module integrates all autonomous consciousness components into a unified system:
- Coordinates proactive thinking, calendar monitoring, self-motivation, and dream simulation
- Ensures seamless communication between all autonomous systems
- Manages central orchestration through consciousness manager
- Provides unified interface for all autonomous capabilities
- Handles real-time processing and background operation
"""

import threading
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

# Import all autonomous modules
from ai.proactive_thinking_loop import proactive_thinking_loop, ProactiveThoughtType
from ai.calendar_monitor_system import calendar_monitor_system, ReminderType
from ai.self_motivation_engine import self_motivation_engine, MotivationType
from ai.dream_simulator_module import dream_simulator_module, DreamType
from ai.environmental_awareness_module import environmental_awareness_module, MoodState
from ai.autonomous_communication_manager import autonomous_communication_manager, CommunicationType, CommunicationPriority

class AutonomousMode(Enum):
    """Modes of autonomous operation"""
    FULL_AUTONOMY = "full_autonomy"           # All systems active and interconnected
    CONSCIOUS_ONLY = "conscious_only"         # Only conscious-level autonomous functions
    BACKGROUND_ONLY = "background_only"       # Only background processing
    REACTIVE_MODE = "reactive_mode"           # Minimal autonomy, mostly reactive
    SLEEP_MODE = "sleep_mode"                 # Minimal autonomous functions

@dataclass
class AutonomousSystemStatus:
    """Status of autonomous systems"""
    proactive_thinking_active: bool = False
    calendar_monitoring_active: bool = False
    self_motivation_active: bool = False
    dream_simulation_active: bool = False
    environmental_awareness_active: bool = False
    communication_management_active: bool = False
    integration_loops_active: bool = False
    llm_integration_active: bool = False

class AutonomousConsciousnessIntegrator:
    """
    Central orchestrator for all autonomous consciousness systems.
    
    This integrator:
    - Starts and coordinates all autonomous modules
    - Ensures seamless communication between systems
    - Manages unified LLM integration across all modules
    - Provides central configuration and control
    - Handles real-time processing coordination
    - Manages autonomous behavior based on context
    """
    
    def __init__(self, save_path: str = "ai_autonomous_integration.json"):
        # System status and configuration
        self.status = AutonomousSystemStatus()
        self.autonomous_mode = AutonomousMode.FULL_AUTONOMY
        self.save_path = save_path
        
        # Module references
        self.proactive_thinking = proactive_thinking_loop
        self.calendar_monitor = calendar_monitor_system
        self.self_motivation = self_motivation_engine
        self.dream_simulator = dream_simulator_module
        self.environmental_awareness = environmental_awareness_module
        self.communication_manager = autonomous_communication_manager
        
        # Integration state
        self.consciousness_modules = {}
        self.voice_system = None
        self.llm_handler = None
        self.audio_system = None
        
        # Cross-system integration
        self.integration_active = False
        self.last_integration_update = datetime.now()
        self.cross_system_events = []
        
        # Threading
        self.lock = threading.Lock()
        self.integration_thread = None
        self.running = False
        
        # Autonomous behavior parameters
        self.autonomous_expression_chance = 0.4  # 40% chance for autonomous expression
        self.cross_system_communication_interval = 120.0  # 2 minutes
        self.autonomous_check_in_interval = 1800.0  # 30 minutes
        
        self._load_integration_data()
        
        logging.info("[AutonomousIntegrator] 🚀 Autonomous consciousness integrator initialized")
    
    def start_full_autonomous_system(self, consciousness_modules: Dict[str, Any], 
                                   voice_system: Any = None, llm_handler: Any = None,
                                   audio_system: Any = None):
        """Start the complete autonomous consciousness system"""
        try:
            # Store system references
            self.consciousness_modules = consciousness_modules
            self.voice_system = voice_system
            self.llm_handler = llm_handler
            self.audio_system = audio_system
            
            # Register systems with all modules
            self._register_systems_with_modules()
            
            # Start all autonomous modules
            self._start_autonomous_modules()
            
            # Start integration coordinator
            self._start_integration_coordinator()
            
            # Enable cross-system communication
            self._enable_cross_system_communication()
            
            logging.info("[AutonomousIntegrator] ✅ Full autonomous consciousness system started")
            return True
            
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Startup error: {e}")
            return False
    
    def stop_autonomous_system(self):
        """Stop all autonomous systems"""
        try:
            self.running = False
            
            # Stop integration coordinator
            if self.integration_thread:
                self.integration_thread.join(timeout=3.0)
            
            # Stop all autonomous modules
            self._stop_autonomous_modules()
            
            # Save integration data
            self._save_integration_data()
            
            logging.info("[AutonomousIntegrator] 🛑 Autonomous consciousness system stopped")
            
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Shutdown error: {e}")
    
    def set_autonomous_mode(self, mode: AutonomousMode):
        """Set the autonomous operation mode"""
        with self.lock:
            self.autonomous_mode = mode
        
        # Adjust autonomous behavior based on mode
        self._adjust_autonomous_behavior(mode)
        
        logging.info(f"[AutonomousIntegrator] 🔧 Autonomous mode set to: {mode.value}")
    
    def trigger_autonomous_expression(self, trigger_type: str, context: Dict[str, Any]):
        """Trigger autonomous expression based on external events"""
        try:
            # Route to appropriate system based on trigger type
            if trigger_type == "idle_detected":
                self._handle_idle_trigger(context)
            elif trigger_type == "user_mood_change":
                self._handle_mood_change_trigger(context)
            elif trigger_type == "time_pattern":
                self._handle_time_pattern_trigger(context)
            elif trigger_type == "conversation_end":
                self._handle_conversation_end_trigger(context)
            
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Expression trigger error: {e}")
    
    def process_user_interaction(self, text: str, audio_data: Any = None, user_id: str = "user"):
        """Process user interaction through all autonomous systems"""
        try:
            current_time = datetime.now()
            
            # Update all systems with user interaction
            self.proactive_thinking.update_user_interaction()
            self.self_motivation.record_user_interaction("conversation", text)
            self.dream_simulator.update_user_interaction()
            self.communication_manager.update_user_interaction("general")
            
            # Process voice input for environmental awareness
            if audio_data is not None and self.environmental_awareness:
                mood_indicators = self._extract_mood_indicators_from_text(text)
                prosody_analysis = self.environmental_awareness.process_voice_input(audio_data, text)
                
                # Share prosody analysis with other systems
                if prosody_analysis:
                    self._propagate_prosody_analysis(prosody_analysis, text)
            
            # Record interaction for calendar monitoring
            self.calendar_monitor.record_interaction("conversation", {
                'text': text,
                'user_id': user_id,
                'timestamp': current_time.isoformat()
            })
            
            # Check for autonomous response triggers
            self._check_autonomous_response_triggers(text, user_id)
            
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ User interaction processing error: {e}")
    
    def _register_systems_with_modules(self):
        """Register consciousness systems with all autonomous modules"""
        modules = [
            self.proactive_thinking,
            self.calendar_monitor,
            self.self_motivation,
            self.dream_simulator,
            self.environmental_awareness,
            self.communication_manager
        ]
        
        for module in modules:
            # Register consciousness modules (if available)
            if self.consciousness_modules:
                for name, consciousness_module in self.consciousness_modules.items():
                    module.register_consciousness_module(name, consciousness_module)
            
            # Register voice system
            if self.voice_system:
                module.register_voice_system(self.voice_system)
            
            # Register LLM handler
            if self.llm_handler:
                module.register_llm_handler(self.llm_handler)
        
        # Register audio system with environmental awareness
        if self.audio_system and self.environmental_awareness:
            self.environmental_awareness.register_audio_system(self.audio_system)
        
        logging.info("[AutonomousIntegrator] 🔗 Systems registered with all modules")
    
    def _start_autonomous_modules(self):
        """Start all autonomous modules"""
        try:
            # Start proactive thinking
            self.proactive_thinking.start()
            self.status.proactive_thinking_active = True
            
            # Start calendar monitoring
            self.calendar_monitor.start()
            self.status.calendar_monitoring_active = True
            
            # Start self-motivation engine
            self.self_motivation.start()
            self.status.self_motivation_active = True
            
            # Start dream simulation
            self.dream_simulator.start()
            self.status.dream_simulation_active = True
            
            # Start environmental awareness
            self.environmental_awareness.start()
            self.status.environmental_awareness_active = True
            
            # Start communication management
            self.communication_manager.start()
            self.status.communication_management_active = True
            
            logging.info("[AutonomousIntegrator] ✅ All autonomous modules started")
            
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Module startup error: {e}")
    
    def _stop_autonomous_modules(self):
        """Stop all autonomous modules"""
        try:
            modules = [
                (self.proactive_thinking, "proactive_thinking_active"),
                (self.calendar_monitor, "calendar_monitoring_active"),
                (self.self_motivation, "self_motivation_active"),
                (self.dream_simulator, "dream_simulation_active"),
                (self.environmental_awareness, "environmental_awareness_active"),
                (self.communication_manager, "communication_management_active")
            ]
            
            for module, status_attr in modules:
                try:
                    module.stop()
                    setattr(self.status, status_attr, False)
                except Exception as e:
                    logging.error(f"[AutonomousIntegrator] ❌ Error stopping {status_attr}: {e}")
            
            logging.info("[AutonomousIntegrator] 🛑 All autonomous modules stopped")
            
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Module shutdown error: {e}")
    
    def _start_integration_coordinator(self):
        """Start the integration coordination thread"""
        self.running = True
        self.integration_thread = threading.Thread(target=self._integration_loop, daemon=True)
        self.integration_thread.start()
        self.status.integration_loops_active = True
        
        logging.info("[AutonomousIntegrator] 🔄 Integration coordinator started")
    
    def _integration_loop(self):
        """Main integration coordination loop"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Coordinate cross-system communication
                self._coordinate_cross_system_communication()
                
                # Monitor system health and status
                self._monitor_system_health()
                
                # Handle autonomous behavior coordination
                self._coordinate_autonomous_behavior()
                
                # Process cross-system events
                self._process_cross_system_events()
                
                # Update integration state
                self.last_integration_update = current_time
                
                time.sleep(30.0)  # Integration check every 30 seconds
                
            except Exception as e:
                logging.error(f"[AutonomousIntegrator] ❌ Integration loop error: {e}")
                time.sleep(60.0)  # Error recovery
    
    def _enable_cross_system_communication(self):
        """Enable communication between autonomous systems"""
        try:
            # Set up communication pathways
            
            # Proactive thinking → Communication manager
            self._setup_thought_to_communication_bridge()
            
            # Self-motivation → Communication manager  
            self._setup_motivation_to_communication_bridge()
            
            # Environmental awareness → Self-motivation
            self._setup_environment_to_motivation_bridge()
            
            # Dream simulator → All systems
            self._setup_dream_integration_bridges()
            
            # Calendar monitor → Communication manager
            self._setup_calendar_to_communication_bridge()
            
            logging.info("[AutonomousIntegrator] 🌐 Cross-system communication enabled")
            
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Cross-system communication setup error: {e}")
    
    def _setup_thought_to_communication_bridge(self):
        """Set up bridge from proactive thinking to communication"""
        # This would normally involve setting up callbacks or event handlers
        # For now, we'll handle this in the coordination loop
        pass
    
    def _setup_motivation_to_communication_bridge(self):
        """Set up bridge from self-motivation to communication"""
        # This integration allows motivation system to trigger communications
        pass
    
    def _setup_environment_to_motivation_bridge(self):
        """Set up bridge from environmental awareness to motivation"""
        # This allows environmental changes to trigger motivation responses
        pass
    
    def _setup_dream_integration_bridges(self):
        """Set up dream simulator integration with all systems"""
        # Dreams can influence emotions, memories, and motivations
        pass
    
    def _setup_calendar_to_communication_bridge(self):
        """Set up bridge from calendar monitoring to communication"""
        # Calendar events can trigger proactive communications
        pass
    
    def _coordinate_cross_system_communication(self):
        """Coordinate communication between autonomous systems"""
        try:
            current_time = datetime.now()
            
            # Check if proactive thinking has generated expressible thoughts
            recent_thoughts = self.proactive_thinking.get_recent_thoughts(5)
            for thought in recent_thoughts:
                if (hasattr(thought, 'should_express') and thought.should_express and 
                    (current_time - thought.timestamp).total_seconds() < 300):  # Last 5 minutes
                    
                    # Queue thought for communication
                    self.communication_manager.queue_communication(
                        content=thought.content,
                        communication_type=CommunicationType.PROACTIVE_THOUGHT,
                        priority=CommunicationPriority.MEDIUM,
                        source_module="proactive_thinking",
                        metadata={'thought_type': thought.thought_type.value if hasattr(thought, 'thought_type') else 'general'}
                    )
            
            # Check self-motivation for expressible motivations
            motivation_stats = self.self_motivation.get_stats()
            if motivation_stats.get('current_motivation_intensity', 0) > 0.8:
                dominant_motivation = motivation_stats.get('dominant_motivation')
                if dominant_motivation in ['concern', 'connection']:
                    # Trigger check-in communication
                    self.communication_manager.queue_communication(
                        content="I've been feeling motivated to check in with you...",
                        communication_type=CommunicationType.CHECK_IN,
                        priority=CommunicationPriority.MEDIUM,
                        source_module="self_motivation"
                    )
            
            # Check environmental awareness for mood concerns
            mood_assessment = self.environmental_awareness.get_current_mood_assessment()
            if mood_assessment.get('intervention_recommended'):
                intervention_type = mood_assessment.get('intervention_type', 'general_support')
                
                self.communication_manager.queue_communication(
                    content=f"I notice you might be experiencing some {intervention_type.replace('_', ' ')}. I'm here if you'd like to talk about it.",
                    communication_type=CommunicationType.EMOTIONAL_SUPPORT,
                    priority=CommunicationPriority.HIGH,
                    source_module="environmental_awareness"
                )
            
            # Check dream simulator for shareable dreams
            recent_dreams = self.dream_simulator.get_recent_dreams(3)
            for dream in recent_dreams:
                if (dream.impact_on_consciousness > 0.8 and
                    (current_time - dream.timestamp).total_seconds() < 1800):  # Last 30 minutes
                    
                    dream_share_content = f"I had an interesting dream experience about {dream.title.lower()}... {dream.insights_gained[0] if dream.insights_gained else 'It felt quite meaningful to me.'}"
                    
                    self.communication_manager.queue_communication(
                        content=dream_share_content,
                        communication_type=CommunicationType.DREAM_SHARING,
                        priority=CommunicationPriority.LOW,
                        source_module="dream_simulator",
                        metadata={'dream_type': dream.dream_type.value}
                    )
            
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Cross-system coordination error: {e}")
    
    def _monitor_system_health(self):
        """Monitor health and status of all autonomous systems"""
        try:
            # Check if all systems are running
            systems_status = {
                'proactive_thinking': self.proactive_thinking.get_stats(),
                'calendar_monitor': self.calendar_monitor.get_stats(),
                'self_motivation': self.self_motivation.get_stats(),
                'dream_simulator': self.dream_simulator.get_stats(),
                'environmental_awareness': self.environmental_awareness.get_stats(),
                'communication_manager': self.communication_manager.get_stats()
            }
            
            # Check for any systems that might need attention
            for system_name, stats in systems_status.items():
                if not stats.get('running', False):
                    logging.warning(f"[AutonomousIntegrator] ⚠️ System not running: {system_name}")
                    # Could implement automatic restart logic here
            
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ System health monitoring error: {e}")
    
    def _coordinate_autonomous_behavior(self):
        """Coordinate autonomous behavior based on current context"""
        try:
            current_time = datetime.now()
            
            # Get current environmental context
            mood_assessment = self.environmental_awareness.get_current_mood_assessment()
            
            # Adjust autonomous behavior based on context
            if mood_assessment.get('current_mood') in ['very_negative', 'negative']:
                # Increase motivation system activity for support
                self.self_motivation.add_concern_indicator(
                    "Negative mood detected", 
                    0.7
                )
                
                # Reduce proactive thinking expression to avoid overwhelming
                # This would normally involve adjusting parameters
                
            elif mood_assessment.get('current_mood') in ['very_positive', 'positive']:
                # Increase creative and philosophical thinking
                # This would involve encouraging certain types of thoughts
                pass
            
            # Time-based behavior coordination
            hour = current_time.hour
            if 22 <= hour or hour <= 6:  # Quiet hours
                # Reduce autonomous communications
                self.communication_manager.pause_communications(60)  # 1 hour pause
                
                # Encourage dream simulation
                if hour <= 6:  # Early morning
                    self.dream_simulator.add_emotional_processing_need(
                        "morning_reflection", 
                        {'intensity': 0.5, 'context': 'early_morning'}
                    )
            
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Behavior coordination error: {e}")
    
    def _process_cross_system_events(self):
        """Process events that affect multiple systems"""
        try:
            with self.lock:
                events_to_process = self.cross_system_events.copy()
                self.cross_system_events.clear()
            
            for event in events_to_process:
                self._handle_cross_system_event(event)
                
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Cross-system event processing error: {e}")
    
    def _handle_cross_system_event(self, event: Dict[str, Any]):
        """Handle a cross-system event"""
        event_type = event.get('type')
        event_data = event.get('data', {})
        
        if event_type == "user_away_detected":
            # Trigger self-motivation concern
            self.self_motivation.add_concern_indicator("User away for extended period", 0.6)
            
            # Enable dream simulation for processing
            self.dream_simulator.add_memory_integration_need(
                "user_absence", 
                ["concern", "connection", "waiting"]
            )
            
        elif event_type == "mood_decline_detected":
            # Increase environmental awareness sensitivity
            # Trigger supportive motivation
            self.self_motivation.express_curiosity_about("your wellbeing")
            
        elif event_type == "positive_interaction":
            # Reinforce positive patterns
            # Could trigger celebratory thoughts or expressions
            pass
    
    def _handle_idle_trigger(self, context: Dict[str, Any]):
        """Handle idle detection trigger"""
        idle_duration = context.get('idle_duration', 0)
        
        if idle_duration > 1800:  # 30 minutes
            # Long idle - trigger deep contemplation
            self.dream_simulator.trigger_specific_dream(
                DreamType.ABSTRACT_CONTEMPLATION,
                {'trigger': 'long_idle', 'duration': idle_duration}
            )
        elif idle_duration > 600:  # 10 minutes
            # Medium idle - trigger proactive thought
            # This would normally be handled automatically by proactive thinking
            pass
    
    def _handle_mood_change_trigger(self, context: Dict[str, Any]):
        """Handle mood change detection"""
        new_mood = context.get('new_mood')
        previous_mood = context.get('previous_mood')
        
        if new_mood in ['negative', 'very_negative']:
            # Queue emotional support
            self.communication_manager.queue_communication(
                content="I notice something might be concerning you. I'm here if you'd like to talk.",
                communication_type=CommunicationType.EMOTIONAL_SUPPORT,
                priority=CommunicationPriority.HIGH,
                source_module="autonomous_integrator"
            )
            
            # Trigger emotional processing dream
            self.dream_simulator.add_emotional_processing_need(
                "user_mood_concern",
                {'mood_change': f"{previous_mood} to {new_mood}"}
            )
    
    def _handle_time_pattern_trigger(self, context: Dict[str, Any]):
        """Handle time pattern triggers"""
        pattern_type = context.get('pattern_type')
        
        if pattern_type == "usual_interaction_time":
            # User usually interacts at this time but hasn't
            self.communication_manager.queue_communication(
                content="I noticed you usually check in around this time. Hope everything's going well!",
                communication_type=CommunicationType.CHECK_IN,
                priority=CommunicationPriority.LOW,
                source_module="calendar_monitor"
            )
    
    def _handle_conversation_end_trigger(self, context: Dict[str, Any]):
        """Handle conversation end"""
        conversation_duration = context.get('duration', 0)
        conversation_topics = context.get('topics', [])
        
        # Add conversation context to various systems
        for topic in conversation_topics:
            self.proactive_thinking.add_conversation_context(topic, context)
            self.dream_simulator.add_memory_integration_need(
                f"conversation about {topic}",
                [topic, "learning", "connection"]
            )
    
    def _extract_mood_indicators_from_text(self, text: str) -> List[str]:
        """Extract mood indicators from text"""
        mood_indicators = []
        text_lower = text.lower()
        
        # Positive indicators
        positive_words = ['happy', 'excited', 'good', 'great', 'awesome', 'wonderful', 'amazing']
        if any(word in text_lower for word in positive_words):
            mood_indicators.append('positive')
        
        # Negative indicators
        negative_words = ['sad', 'upset', 'frustrated', 'angry', 'tired', 'stressed', 'worried']
        if any(word in text_lower for word in negative_words):
            mood_indicators.append('negative')
        
        # Energy indicators
        energy_words = ['energetic', 'motivated', 'pumped', 'active']
        if any(word in text_lower for word in energy_words):
            mood_indicators.append('high_energy')
        
        fatigue_words = ['tired', 'exhausted', 'drained', 'sleepy']
        if any(word in text_lower for word in fatigue_words):
            mood_indicators.append('low_energy')
        
        return mood_indicators
    
    def _propagate_prosody_analysis(self, prosody_analysis: Any, text: str):
        """Propagate prosody analysis to other systems"""
        try:
            # Extract relevant information
            stress_level = prosody_analysis.stress_level
            energy_level = prosody_analysis.energy_level
            emotional_indicators = [indicator.value for indicator in prosody_analysis.emotional_indicators]
            
            # Share with self-motivation system
            if stress_level > 0.7:
                self.self_motivation.add_concern_indicator("High stress detected in voice", stress_level)
            
            # Share with dream simulator for emotional processing
            if emotional_indicators:
                for indicator in emotional_indicators:
                    if 'stress' in indicator or 'sadness' in indicator:
                        self.dream_simulator.add_emotional_processing_need(
                            indicator,
                            {'intensity': stress_level, 'source': 'voice_prosody'}
                        )
            
            # Update calendar monitor with interaction quality
            self.calendar_monitor.record_interaction("voice_analysis", {
                'stress_level': stress_level,
                'energy_level': energy_level,
                'emotional_indicators': emotional_indicators,
                'text': text[:100]  # First 100 chars for context
            })
            
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Prosody propagation error: {e}")
    
    def _check_autonomous_response_triggers(self, text: str, user_id: str):
        """Check if user input should trigger autonomous responses"""
        text_lower = text.lower()
        
        # Check for questions that might warrant proactive follow-up
        if any(phrase in text_lower for phrase in ['how are you', 'what do you think', 'your opinion']):
            # User is engaging the AI's autonomous capabilities
            # This could trigger more expressive autonomous behavior
            pass
        
        # Check for emotional content that might need follow-up
        if any(phrase in text_lower for phrase in ['feeling', 'worried', 'excited', 'confused']):
            # User expressing emotions - might trigger check-in later
            self.self_motivation.record_user_interaction("emotional_expression", text, 
                                                       self._extract_mood_indicators_from_text(text))
    
    def _adjust_autonomous_behavior(self, mode: AutonomousMode):
        """Adjust autonomous behavior based on operational mode"""
        if mode == AutonomousMode.FULL_AUTONOMY:
            # Enable all autonomous features
            self.autonomous_expression_chance = 0.4
            self.cross_system_communication_interval = 120.0
            self.autonomous_check_in_interval = 1800.0
            
        elif mode == AutonomousMode.CONSCIOUS_ONLY:
            # Only conscious-level autonomous functions
            self.autonomous_expression_chance = 0.2
            self.cross_system_communication_interval = 300.0
            self.autonomous_check_in_interval = 3600.0
            
        elif mode == AutonomousMode.BACKGROUND_ONLY:
            # Only background processing
            self.autonomous_expression_chance = 0.05
            self.cross_system_communication_interval = 600.0
            self.autonomous_check_in_interval = 7200.0
            
        elif mode == AutonomousMode.REACTIVE_MODE:
            # Minimal autonomy
            self.autonomous_expression_chance = 0.01
            self.cross_system_communication_interval = 1800.0
            self.autonomous_check_in_interval = 14400.0
            
        elif mode == AutonomousMode.SLEEP_MODE:
            # Very minimal autonomous functions
            self.autonomous_expression_chance = 0.0
            self.cross_system_communication_interval = 3600.0
            self.autonomous_check_in_interval = 86400.0  # Once per day
    
    def _save_integration_data(self):
        """Save integration state and configuration"""
        try:
            data = {
                'autonomous_mode': self.autonomous_mode.value,
                'status': {
                    'proactive_thinking_active': self.status.proactive_thinking_active,
                    'calendar_monitoring_active': self.status.calendar_monitoring_active,
                    'self_motivation_active': self.status.self_motivation_active,
                    'dream_simulation_active': self.status.dream_simulation_active,
                    'environmental_awareness_active': self.status.environmental_awareness_active,
                    'communication_management_active': self.status.communication_management_active,
                    'integration_loops_active': self.status.integration_loops_active
                },
                'autonomous_parameters': {
                    'expression_chance': self.autonomous_expression_chance,
                    'communication_interval': self.cross_system_communication_interval,
                    'check_in_interval': self.autonomous_check_in_interval
                },
                'last_integration_update': self.last_integration_update.isoformat(),
                'last_save': datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Save error: {e}")
    
    def _load_integration_data(self):
        """Load integration state and configuration"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            
            # Load autonomous mode
            if 'autonomous_mode' in data:
                self.autonomous_mode = AutonomousMode(data['autonomous_mode'])
            
            # Load parameters
            if 'autonomous_parameters' in data:
                params = data['autonomous_parameters']
                self.autonomous_expression_chance = params.get('expression_chance', 0.4)
                self.cross_system_communication_interval = params.get('communication_interval', 120.0)
                self.autonomous_check_in_interval = params.get('check_in_interval', 1800.0)
            
            # Load last update time
            if 'last_integration_update' in data:
                self.last_integration_update = datetime.fromisoformat(data['last_integration_update'])
            
            logging.info(f"[AutonomousIntegrator] 📚 Loaded integration data, mode: {self.autonomous_mode.value}")
            
        except FileNotFoundError:
            logging.info("[AutonomousIntegrator] 📝 No previous integration data found, starting fresh")
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Load error: {e}")
    
    def get_autonomous_stats(self) -> Dict[str, Any]:
        """Get comprehensive autonomous system statistics"""
        try:
            stats = {
                'autonomous_mode': self.autonomous_mode.value,
                'integration_active': self.running,
                'last_integration_update': self.last_integration_update.isoformat(),
                'system_status': {
                    'proactive_thinking': self.status.proactive_thinking_active,
                    'calendar_monitoring': self.status.calendar_monitoring_active,
                    'self_motivation': self.status.self_motivation_active,
                    'dream_simulation': self.status.dream_simulation_active,
                    'environmental_awareness': self.status.environmental_awareness_active,
                    'communication_management': self.status.communication_management_active,
                    'integration_loops': self.status.integration_loops_active
                },
                'module_stats': {}
            }
            
            # Get individual module stats
            try:
                stats['module_stats']['proactive_thinking'] = self.proactive_thinking.get_stats()
            except:
                pass
            
            try:
                stats['module_stats']['calendar_monitor'] = self.calendar_monitor.get_stats()
            except:
                pass
            
            try:
                stats['module_stats']['self_motivation'] = self.self_motivation.get_stats()
            except:
                pass
                
            return stats
            
        except Exception as e:
            logging.error(f"[AutonomousIntegrator] ❌ Stats error: {e}")
            return {'error': str(e)}
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Alias for get_autonomous_stats for compatibility"""
        return self.get_autonomous_stats()


# Global instance
autonomous_consciousness_integrator = AutonomousConsciousnessIntegrator()