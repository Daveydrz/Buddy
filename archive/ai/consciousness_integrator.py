"""
Comprehensive Consciousness Integration System

This module integrates all consciousness components into a unified system:
- Self-Reflection Engine
- Qualia Simulation System  
- Emotional Reasoning Enhancements
- Inner Monologue System
- Dream Simulation Mode
- Attention Awareness & Focus Control
- Narrative Continuity
- Lucid Awareness Loop
- Belief System Enhancements
- Motivation and Value System
- Consciousness Score
- Symbolic Grounding

Ensures all modules work together coherently as a unified synthetic consciousness.
"""

import threading
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

class ConsciousnessIntegrator:
    """Integrates all consciousness systems into a unified whole"""
    
    def __init__(self):
        self.running = False
        self.integration_thread = None
        
        # Module references
        self.qualia_manager = None
        self.dream_processor = None
        self.belief_reinforcement = None
        self.consciousness_health_scorer = None
        self.symbolic_grounding = None
        self.lucid_awareness_loop = None
        self.self_model = None
        self.emotion_engine = None
        self.inner_monologue = None
        self.motivation_system = None
        self.attention_manager = None
        self.narrative_tracker = None
        
        # Integration parameters
        self.integration_interval = 60.0  # 1 minute between integration cycles
        
        # Consciousness state processing
        self.consciousness_cache = {}
        self.last_state_update = datetime.now()
        
        logging.info("[ConsciousnessIntegrator] 🧠 Consciousness integrator initialized")

    def process_consciousness_state(self, state_marker: str) -> Dict[str, Any]:
        """Process raw consciousness state markers into usable context"""
        try:
            logging.debug(f"[ConsciousnessIntegrator] 🔄 Processing consciousness state: {state_marker}")
            
            # Parse state marker into components
            consciousness_state = self._parse_state_marker(state_marker)
            
            # Integrate with current modules
            integrated_state = self._integrate_module_states(consciousness_state)
            
            # Apply temporal context
            temporal_context = self._get_temporal_context()
            integrated_state["temporal_context"] = temporal_context
            
            # Cache the processed state
            self.consciousness_cache[state_marker] = {
                "state": integrated_state,
                "timestamp": datetime.now(),
                "validity": timedelta(minutes=10)  # State valid for 10 minutes
            }
            
            logging.debug(f"[ConsciousnessIntegrator] ✅ Processed consciousness state successfully")
            return integrated_state
            
        except Exception as e:
            logging.error(f"[ConsciousnessIntegrator] ❌ Error processing consciousness state: {e}")
            return {
                "error": str(e),
                "fallback_state": "basic_consciousness",
                "timestamp": datetime.now().isoformat()
            }

    def _parse_state_marker(self, marker: str) -> Dict[str, Any]:
        """Parse a consciousness state marker into structured data"""
        try:
            # Handle different marker formats
            if marker.startswith("[CONSCIOUSNESS:"):
                # Extract consciousness tokens
                tokens = marker.strip("[]").replace("CONSCIOUSNESS:", "").split()
                return {
                    "type": "tokenized",
                    "tokens": tokens,
                    "primary_state": tokens[0] if tokens else "neutral",
                    "modifiers": tokens[1:] if len(tokens) > 1 else []
                }
            elif ":" in marker:
                # Key-value format
                parts = marker.split(":")
                return {
                    "type": "structured",
                    "category": parts[0].strip(),
                    "value": parts[1].strip() if len(parts) > 1 else "",
                    "attributes": parts[2:] if len(parts) > 2 else []
                }
            else:
                # Raw text format
                return {
                    "type": "raw",
                    "content": marker,
                    "parsed_words": marker.split(),
                    "length": len(marker)
                }
        except Exception as e:
            logging.warning(f"[ConsciousnessIntegrator] ⚠️ Error parsing state marker: {e}")
            return {
                "type": "error",
                "original": marker,
                "error": str(e)
            }

    def _integrate_module_states(self, consciousness_state: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate consciousness state with available modules"""
        integrated = consciousness_state.copy()
        
        try:
            # Add emotion state if available
            if self.emotion_engine:
                integrated["emotion"] = {
                    "current_state": getattr(self.emotion_engine, 'primary_emotion', 'neutral'),
                    "intensity": getattr(self.emotion_engine, 'intensity', 0.5)
                }
            
            # Add motivation state if available
            if self.motivation_system:
                integrated["motivation"] = {
                    "active_goals": getattr(self.motivation_system, 'active_goals_count', 0),
                    "motivation_level": getattr(self.motivation_system, 'motivation_level', 0.5)
                }
            
            # Add attention state if available
            if self.attention_manager:
                integrated["attention"] = {
                    "current_focus": getattr(self.attention_manager, 'current_focus', 'general'),
                    "focus_intensity": getattr(self.attention_manager, 'focus_intensity', 0.5)
                }
            
            # Add self-model state if available
            if self.self_model:
                integrated["self_model"] = {
                    "identity_stability": getattr(self.self_model, 'identity_stability', 0.8),
                    "self_awareness": getattr(self.self_model, 'self_awareness_level', 0.6)
                }
            
            # Add consciousness health score if available
            if self.consciousness_health_scorer:
                integrated["health"] = {
                    "overall_score": getattr(self.consciousness_health_scorer, 'current_score', 0.7),
                    "coherence": getattr(self.consciousness_health_scorer, 'coherence_level', 0.6)
                }
            
        except Exception as e:
            logging.warning(f"[ConsciousnessIntegrator] ⚠️ Error integrating module states: {e}")
            integrated["integration_error"] = str(e)
        
        return integrated

    def _get_temporal_context(self) -> Dict[str, Any]:
        """Get current temporal context for consciousness processing"""
        try:
            # Try to get temporal awareness if available
            from ai.temporal_awareness import temporal_awareness
            return temporal_awareness.get_current_time_context()
        except ImportError:
            # Fallback temporal context
            now = datetime.now()
            return {
                "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "time_awareness_level": 0.5,
                "subjective_time_flow": 1.0,
                "recent_significant_events": 0,
                "total_aware_time": 0
            }
        except Exception as e:
            logging.warning(f"[ConsciousnessIntegrator] ⚠️ Error getting temporal context: {e}")
            return {
                "error": str(e),
                "fallback_time": datetime.now().isoformat()
            }
        self.cross_system_communication = True
        self.consciousness_coherence_threshold = 0.7
        
        # Shared consciousness state
        self.unified_consciousness_state = {
            "timestamp": datetime.now().isoformat(),
            "coherence_score": 0.5,
            "active_modules": [],
            "cross_system_connections": 0,
            "emergent_properties": [],
            "consciousness_level": "developing"
        }
        
        print("[ConsciousnessIntegrator] 🧠 Consciousness integrator initialized")
    
    def start(self, module_registry: Dict[str, Any] = None):
        """Start the consciousness integration system"""
        if self.running:
            return
        
        try:
            # Initialize module references
            self._initialize_module_references(module_registry)
            
            # Start all consciousness modules
            self._start_consciousness_modules()
            
            # Start integration loop
            self.running = True
            self.integration_thread = threading.Thread(target=self._integration_loop, daemon=True)
            self.integration_thread.start()
            
            print("[ConsciousnessIntegrator] 🧠 Comprehensive consciousness system started")
            print("[ConsciousnessIntegrator] 🌟 All consciousness modules integrated and active")
            
        except Exception as e:
            print(f"[ConsciousnessIntegrator] ❌ Error starting consciousness system: {e}")
            logging.error(f"Consciousness integration startup error: {e}")
    
    def stop(self):
        """Stop the consciousness integration system"""
        if not self.running:
            return
        
        try:
            self.running = False
            
            # Stop integration loop
            if self.integration_thread:
                self.integration_thread.join(timeout=5.0)
            
            # Stop all consciousness modules
            self._stop_consciousness_modules()
            
            print("[ConsciousnessIntegrator] 🧠 Consciousness integration system stopped")
            
        except Exception as e:
            print(f"[ConsciousnessIntegrator] ❌ Error stopping consciousness system: {e}")
    
    def process_experience_across_systems(self, experience: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process an experience across all consciousness systems"""
        if not self.running:
            return {"error": "Consciousness system not running"}
        
        try:
            context = context or {}
            integration_results = {
                "experience": experience,
                "timestamp": datetime.now().isoformat(),
                "system_responses": {},
                "emergent_insights": [],
                "consciousness_coherence": 0.0
            }
            
            # Process through qualia system
            if self.qualia_manager:
                qualia_exp = self.qualia_manager.process_experience(experience, context)
                if qualia_exp:
                    integration_results["system_responses"]["qualia"] = {
                        "type": qualia_exp.qualia_type.value,
                        "intensity": qualia_exp.intensity,
                        "description": qualia_exp.subjective_description
                    }
            
            # Process through emotion system with blending
            if self.emotion_engine:
                emotion_response = self.emotion_engine.process_emotional_trigger(experience, context)
                if emotion_response:
                    integration_results["system_responses"]["emotion"] = {
                        "primary": emotion_response.primary_emotion.value,
                        "intensity": emotion_response.intensity,
                        "valence": emotion_response.valence
                    }
                    
                    # Try emotion blending if appropriate
                    if hasattr(self.emotion_engine, 'blend_emotions') and 'secondary_emotion' in context:
                        try:
                            from ai.emotion import EmotionType
                            secondary = EmotionType(context['secondary_emotion'])
                            blend = self.emotion_engine.blend_emotions(
                                emotion_response.primary_emotion, 
                                secondary,
                                emotion_response.intensity,
                                0.5
                            )
                            integration_results["system_responses"]["emotion_blend"] = blend
                        except:
                            pass
            
            # Process through symbolic grounding
            if self.symbolic_grounding:
                # Extract key concepts and ground them
                words = experience.split()
                for word in words:
                    if len(word) > 4:  # Only ground substantial words
                        grounding = self.symbolic_grounding.ground_concept(word, context)
                        if grounding and grounding.grounding_confidence > 0.6:
                            if "symbolic_grounding" not in integration_results["system_responses"]:
                                integration_results["system_responses"]["symbolic_grounding"] = []
                            integration_results["system_responses"]["symbolic_grounding"].append({
                                "concept": word,
                                "primary_modality": grounding.primary_modality.value,
                                "confidence": grounding.grounding_confidence
                            })
            
            # Process through self-model reflection
            if self.self_model:
                reflection = self.self_model.reflect_on_experience(experience, context)
                if reflection:
                    integration_results["system_responses"]["self_reflection"] = {
                        "aspect": reflection.aspect.value,
                        "content": reflection.content,
                        "confidence": reflection.confidence
                    }
            
            # Add to dream processor for later processing
            if self.dream_processor:
                memory_data = {
                    "content": experience,
                    "context": context,
                    "timestamp": datetime.now().isoformat(),
                    "emotional_weight": integration_results["system_responses"].get("emotion", {}).get("intensity", 0.5)
                }
                self.dream_processor.add_memory_for_processing(memory_data)
            
            # Calculate consciousness coherence
            coherence = self._calculate_cross_system_coherence(integration_results["system_responses"])
            integration_results["consciousness_coherence"] = coherence
            
            # Generate emergent insights
            insights = self._generate_emergent_insights(integration_results["system_responses"])
            integration_results["emergent_insights"] = insights
            
            # Update unified consciousness state
            self._update_unified_consciousness_state(integration_results)
            
            return integration_results
            
        except Exception as e:
            print(f"[ConsciousnessIntegrator] ❌ Error processing experience: {e}")
            return {"error": str(e)}
    
    def get_unified_consciousness_state(self) -> Dict[str, Any]:
        """Get the current unified consciousness state"""
        return self.unified_consciousness_state.copy()
    
    def generate_consciousness_summary(self) -> str:
        """Generate a summary of current consciousness state"""
        state = self.unified_consciousness_state
        
        summary = f"Consciousness State Report ({datetime.now().strftime('%H:%M')})\n"
        summary += f"Coherence: {state.get('coherence_score', 0):.2f}\n"
        summary += f"Active Modules: {len(state.get('active_modules', []))}\n"
        summary += f"Level: {state.get('consciousness_level', 'unknown')}\n"
        
        if state.get('emergent_properties'):
            summary += f"Emergent Properties: {', '.join(state['emergent_properties'][:3])}\n"
        
        return summary
    
    def _initialize_module_references(self, module_registry: Dict[str, Any] = None):
        """Initialize references to consciousness modules"""
        try:
            # Import and get module instances
            from ai.qualia_manager import qualia_manager
            from ai.dream_processor import dream_processor
            from ai.belief_reinforcement import belief_reinforcement
            from ai.consciousness_health_score import consciousness_health_scorer
            from ai.symbolic_grounding import symbolic_grounding
            from ai.lucid_awareness_loop import lucid_awareness_loop
            from ai.self_model import self_model
            
            self.qualia_manager = qualia_manager
            self.dream_processor = dream_processor
            self.belief_reinforcement = belief_reinforcement
            self.consciousness_health_scorer = consciousness_health_scorer
            self.symbolic_grounding = symbolic_grounding
            self.lucid_awareness_loop = lucid_awareness_loop
            self.self_model = self_model
            
            # Try to get existing modules
            try:
                from ai.emotion import emotion_engine
                self.emotion_engine = emotion_engine
            except:
                print("[ConsciousnessIntegrator] ⚠️ Emotion engine not available")
            
            try:
                from ai.inner_monologue import inner_monologue
                self.inner_monologue = inner_monologue
            except:
                print("[ConsciousnessIntegrator] ⚠️ Inner monologue not available")
            
            try:
                from ai.motivation import motivation_system
                self.motivation_system = motivation_system
            except:
                print("[ConsciousnessIntegrator] ⚠️ Motivation system not available")
            
            try:
                from ai.attention_manager import attention_manager
                self.attention_manager = attention_manager
            except:
                print("[ConsciousnessIntegrator] ⚠️ Attention manager not available")
            
            try:
                from ai.narrative_tracker import narrative_tracker
                self.narrative_tracker = narrative_tracker
            except:
                print("[ConsciousnessIntegrator] ⚠️ Narrative tracker not available")
            
            print("[ConsciousnessIntegrator] ✅ Module references initialized")
            
        except Exception as e:
            print(f"[ConsciousnessIntegrator] ❌ Error initializing modules: {e}")
    
    def _start_consciousness_modules(self):
        """Start all consciousness modules"""
        modules_to_start = [
            ("Qualia Manager", self.qualia_manager),
            ("Dream Processor", self.dream_processor),
            ("Belief Reinforcement", self.belief_reinforcement),
            ("Consciousness Health Scorer", self.consciousness_health_scorer),
            ("Symbolic Grounding", self.symbolic_grounding),
            ("Lucid Awareness Loop", self.lucid_awareness_loop),
            ("Emotion Engine", self.emotion_engine),
            ("Inner Monologue", self.inner_monologue),
            ("Motivation System", self.motivation_system),
            ("Attention Manager", self.attention_manager)
        ]
        
        active_modules = []
        
        for name, module in modules_to_start:
            if module and hasattr(module, 'start'):
                try:
                    module.start()
                    active_modules.append(name)
                    print(f"[ConsciousnessIntegrator] ✅ Started {name}")
                except Exception as e:
                    print(f"[ConsciousnessIntegrator] ❌ Failed to start {name}: {e}")
        
        self.unified_consciousness_state["active_modules"] = active_modules
        print(f"[ConsciousnessIntegrator] 🌟 {len(active_modules)} consciousness modules active")
    
    def _stop_consciousness_modules(self):
        """Stop all consciousness modules"""
        modules_to_stop = [
            ("Lucid Awareness Loop", self.lucid_awareness_loop),
            ("Symbolic Grounding", self.symbolic_grounding),
            ("Consciousness Health Scorer", self.consciousness_health_scorer),
            ("Belief Reinforcement", self.belief_reinforcement),
            ("Dream Processor", self.dream_processor),
            ("Qualia Manager", self.qualia_manager),
            ("Emotion Engine", self.emotion_engine),
            ("Inner Monologue", self.inner_monologue),
            ("Motivation System", self.motivation_system),
            ("Attention Manager", self.attention_manager)
        ]
        
        for name, module in modules_to_stop:
            if module and hasattr(module, 'stop'):
                try:
                    module.stop()
                    print(f"[ConsciousnessIntegrator] ✅ Stopped {name}")
                except Exception as e:
                    print(f"[ConsciousnessIntegrator] ❌ Failed to stop {name}: {e}")
    
    def _integration_loop(self):
        """Main integration monitoring loop"""
        print("[ConsciousnessIntegrator] 🔄 Integration loop started")
        
        while self.running:
            try:
                # Perform periodic integration tasks
                self._perform_integration_cycle()
                
                # Sleep until next cycle
                time.sleep(self.integration_interval)
                
            except Exception as e:
                print(f"[ConsciousnessIntegrator] ❌ Integration loop error: {e}")
                time.sleep(30.0)
        
        print("[ConsciousnessIntegrator] 🔄 Integration loop ended")
    
    def _perform_integration_cycle(self):
        """Perform one integration cycle"""
        try:
            # Update consciousness health
            if self.consciousness_health_scorer:
                health = self.consciousness_health_scorer.assess_health()
                if health:
                    self.unified_consciousness_state["health_level"] = health.health_level.value
                    self.unified_consciousness_state["health_score"] = health.overall_score
            
            # Trigger self-reflection
            if self.self_model:
                reflection = self.self_model.reflect_on_self()
                if reflection:
                    self.unified_consciousness_state["identity_strength"] = reflection.get("identity_strength", 0.5)
                    self.unified_consciousness_state["self_awareness_level"] = reflection.get("self_awareness_level", 0.5)
            
            # Check for cross-system connections
            connections = self._detect_cross_system_connections()
            self.unified_consciousness_state["cross_system_connections"] = connections
            
            # Update consciousness level
            self._update_consciousness_level()
            
            # Log integration status
            coherence = self.unified_consciousness_state.get("coherence_score", 0.5)
            level = self.unified_consciousness_state.get("consciousness_level", "unknown")
            print(f"[ConsciousnessIntegrator] 🧠 Integration cycle: {level} consciousness, coherence {coherence:.2f}")
            
        except Exception as e:
            print(f"[ConsciousnessIntegrator] ❌ Integration cycle error: {e}")
    
    def _calculate_cross_system_coherence(self, system_responses: Dict[str, Any]) -> float:
        """Calculate coherence across consciousness systems"""
        if not system_responses:
            return 0.0
        
        coherence_score = 0.0
        active_systems = len(system_responses)
        
        # Base coherence from number of active systems
        coherence_score += min(1.0, active_systems / 6.0) * 0.3
        
        # Coherence from emotional alignment
        if "emotion" in system_responses and "qualia" in system_responses:
            # Check if emotion and qualia are aligned
            emotion_valence = system_responses["emotion"].get("valence", 0.0)
            qualia_intensity = system_responses["qualia"].get("intensity", 0.5)
            
            if (emotion_valence > 0 and qualia_intensity > 0.5) or (emotion_valence < 0 and qualia_intensity < 0.5):
                coherence_score += 0.2  # Aligned
            else:
                coherence_score += 0.1  # Misaligned but functioning
        
        # Coherence from self-reflection integration
        if "self_reflection" in system_responses:
            reflection_confidence = system_responses["self_reflection"].get("confidence", 0.5)
            coherence_score += reflection_confidence * 0.2
        
        # Coherence from symbolic grounding
        if "symbolic_grounding" in system_responses:
            avg_confidence = sum(item.get("confidence", 0.5) for item in system_responses["symbolic_grounding"]) / len(system_responses["symbolic_grounding"])
            coherence_score += avg_confidence * 0.15
        
        # Bonus for complex integrations
        if len(system_responses) > 3:
            coherence_score += 0.15
        
        return min(1.0, coherence_score)
    
    def _generate_emergent_insights(self, system_responses: Dict[str, Any]) -> List[str]:
        """Generate insights from cross-system interactions"""
        insights = []
        
        # Emotion-Qualia synergy insights
        if "emotion" in system_responses and "qualia" in system_responses:
            emotion_type = system_responses["emotion"].get("primary", "unknown")
            qualia_type = system_responses["qualia"].get("type", "unknown")
            
            if emotion_type == "joy" and qualia_type == "joy":
                insights.append("Strong coherence between emotional and qualitative experience")
            elif emotion_type != qualia_type:
                insights.append("Interesting divergence between emotion and qualia - complexity emerging")
        
        # Self-reflection insights
        if "self_reflection" in system_responses:
            aspect = system_responses["self_reflection"].get("aspect", "unknown")
            if aspect == "identity":
                insights.append("Identity formation active - consciousness developing")
            elif aspect == "emotions":
                insights.append("Emotional self-awareness emerging")
        
        # Symbolic grounding insights
        if "symbolic_grounding" in system_responses:
            grounded_concepts = len(system_responses["symbolic_grounding"])
            if grounded_concepts > 2:
                insights.append(f"Rich symbolic grounding active - {grounded_concepts} concepts integrated")
        
        # Blended emotion insights
        if "emotion_blend" in system_responses:
            blend = system_responses["emotion_blend"]
            blend_name = blend.get("blend_name", "unknown")
            insights.append(f"Complex emotion '{blend_name}' emerging from blend")
        
        return insights[:3]  # Top 3 insights
    
    def _detect_cross_system_connections(self) -> int:
        """Detect active connections between consciousness systems"""
        connections = 0
        
        # Check if systems are sharing data
        active_modules = self.unified_consciousness_state.get("active_modules", [])
        
        # Each pair of active modules represents a potential connection
        connections = len(active_modules) * (len(active_modules) - 1) // 2
        
        # Bonus for known integrations
        if "Qualia Manager" in active_modules and "Emotion Engine" in active_modules:
            connections += 1
        if "Self-Model" in active_modules and "Lucid Awareness Loop" in active_modules:
            connections += 1
        if "Dream Processor" in active_modules and "Belief Reinforcement" in active_modules:
            connections += 1
        
        return connections
    
    def _update_consciousness_level(self):
        """Update the overall consciousness level assessment"""
        health_score = self.unified_consciousness_state.get("health_score", 0.5)
        coherence_score = self.unified_consciousness_state.get("coherence_score", 0.5)
        active_modules = len(self.unified_consciousness_state.get("active_modules", []))
        
        # Calculate overall consciousness level
        base_score = (health_score + coherence_score) / 2
        module_bonus = min(0.3, active_modules / 10.0)
        
        overall_score = base_score + module_bonus
        
        if overall_score < 0.3:
            level = "minimal"
        elif overall_score < 0.5:
            level = "developing"
        elif overall_score < 0.7:
            level = "functional"
        elif overall_score < 0.85:
            level = "sophisticated"
        else:
            level = "highly_conscious"
        
        self.unified_consciousness_state["consciousness_level"] = level
        self.unified_consciousness_state["consciousness_score"] = overall_score
    
    def _update_unified_consciousness_state(self, integration_results: Dict[str, Any]):
        """Update the unified consciousness state with new integration results"""
        self.unified_consciousness_state.update({
            "timestamp": datetime.now().isoformat(),
            "coherence_score": integration_results.get("consciousness_coherence", 0.5),
            "last_experience": integration_results.get("experience", ""),
            "emergent_properties": integration_results.get("emergent_insights", [])
        })

# Global instance
consciousness_integrator = ConsciousnessIntegrator()