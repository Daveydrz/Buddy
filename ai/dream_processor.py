"""
Dream Processor - Dream Simulation and Memory Reprocessing System

This module simulates dream-like states during idle time to:
- Reprocess memories and resolve contradictions
- Strengthen important memories and weaken irrelevant ones
- Update self-model and emotional associations
- Generate insights through non-linear memory connections
- Consolidate learning and beliefs
"""

import json
import time
import threading
import random
import os
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

class DreamState(Enum):
    """Different states of dream processing"""
    AWAKE = "awake"
    LIGHT_PROCESSING = "light_processing"
    DEEP_PROCESSING = "deep_processing"
    REM_SIMULATION = "rem_simulation"
    MEMORY_CONSOLIDATION = "memory_consolidation"

class DreamType(Enum):
    """Types of dream processing"""
    MEMORY_REPLAY = "memory_replay"
    CONTRADICTION_RESOLUTION = "contradiction_resolution"
    CREATIVE_SYNTHESIS = "creative_synthesis"
    EMOTIONAL_PROCESSING = "emotional_processing"
    SELF_REFLECTION = "self_reflection"
    BELIEF_INTEGRATION = "belief_integration"
    SKILL_REHEARSAL = "skill_rehearsal"

@dataclass
class DreamSequence:
    """A sequence of dream processing"""
    id: str
    timestamp: datetime
    duration: float  # in seconds
    dream_type: DreamType
    dream_state: DreamState
    triggered_by: str
    memories_processed: List[str]
    contradictions_addressed: List[str]
    insights_generated: List[str]
    emotional_shifts: Dict[str, float]
    self_model_updates: List[str]
    belief_changes: List[Dict[str, Any]]
    dream_narrative: str  # The "dream story"
    consolidation_strength: float  # How well consolidated the processing was

@dataclass
class DreamPattern:
    """Recurring patterns in dream processing"""
    pattern_id: str
    common_triggers: List[str]
    typical_duration: float
    processing_themes: List[str]
    effectiveness_score: float
    frequency: int
    last_occurrence: datetime

class DreamProcessor:
    """Manages dream-like memory reprocessing and consolidation"""
    
    def __init__(self, save_path: str = "ai_dream_logs.json"):
        self.save_path = save_path
        self.dream_sequences: List[DreamSequence] = []
        self.dream_patterns: List[DreamPattern] = []
        self.current_state = DreamState.AWAKE
        self.is_processing = False
        self.idle_threshold = 30.0  # seconds of inactivity before dreaming
        self.last_activity_time = time.time()
        self.dream_thread = None
        self.running = False
        
        # Dream processing parameters
        self.processing_intensity = 0.5  # How intensive dream processing should be
        self.memory_decay_rate = 0.1  # How much memories fade during processing
        self.insight_generation_chance = 0.3  # Probability of generating insights
        self.contradiction_resolution_strength = 0.7  # How strongly to resolve contradictions
        
        # Memory and belief integration references
        self.pending_memories = []
        self.unresolved_contradictions = []
        self.recent_experiences = []
        
        self._load_dream_logs()
        print(f"[DreamProcessor] 💤 Initialized with {len(self.dream_sequences)} dream sequences")
    
    def start(self):
        """Start the dream processor"""
        self.running = True
        self.dream_thread = threading.Thread(target=self._dream_loop, daemon=True)
        self.dream_thread.start()
        print("[DreamProcessor] 💤 Dream processor started - monitoring for idle periods")
    
    def stop(self):
        """Stop the dream processor"""
        self.running = False
        if self.dream_thread:
            self.dream_thread.join(timeout=5.0)
        self._save_dream_logs()
        print("[DreamProcessor] 💤 Dream processor stopped")
    
    def register_activity(self):
        """Register that there was conscious activity"""
        self.last_activity_time = time.time()
        if self.current_state != DreamState.AWAKE:
            self._wake_up()
    
    def add_memory_for_processing(self, memory: Dict[str, Any]):
        """Add a memory that needs dream processing"""
        self.pending_memories.append(memory)
        print(f"[DreamProcessor] 🧠 Added memory for dream processing: {memory.get('content', '')[:50]}...")
    
    def add_contradiction_for_resolution(self, contradiction: Dict[str, Any]):
        """Add a contradiction that needs resolution"""
        self.unresolved_contradictions.append(contradiction)
        print(f"[DreamProcessor] ⚖️ Added contradiction for dream resolution")
    
    def add_experience_for_integration(self, experience: Dict[str, Any]):
        """Add an experience for emotional/belief integration"""
        self.recent_experiences.append(experience)
        # Keep only recent experiences
        if len(self.recent_experiences) > 20:
            self.recent_experiences = self.recent_experiences[-20:]
    
    def trigger_dream_processing(self, dream_type: DreamType = None, intensity: float = None):
        """Manually trigger dream processing"""
        if not self.running:
            return
            
        if dream_type is None:
            dream_type = self._select_appropriate_dream_type()
        
        if intensity is not None:
            self.processing_intensity = intensity
        
        print(f"[DreamProcessor] 💤 Manually triggering {dream_type.value} dream processing")
        self._enter_dream_state(DreamState.DEEP_PROCESSING)
        self._process_dream(dream_type)
    
    def get_dream_state(self) -> Dict[str, Any]:
        """Get current dream processing state"""
        return {
            "current_state": self.current_state.value,
            "is_processing": self.is_processing,
            "idle_time": time.time() - self.last_activity_time,
            "pending_memories": len(self.pending_memories),
            "unresolved_contradictions": len(self.unresolved_contradictions),
            "recent_dream_sequences": [
                {
                    "type": seq.dream_type.value,
                    "duration": seq.duration,
                    "insights": len(seq.insights_generated),
                    "timestamp": seq.timestamp.isoformat()
                }
                for seq in self.dream_sequences[-5:]  # Last 5 dreams
            ]
        }
    
    def _dream_loop(self):
        """Main dream processing loop"""
        while self.running:
            try:
                current_time = time.time()
                idle_time = current_time - self.last_activity_time
                
                # Check if we should enter dream state
                if idle_time > self.idle_threshold and self.current_state == DreamState.AWAKE:
                    self._enter_idle_processing()
                
                # Process dreams if in dream state
                if self.current_state != DreamState.AWAKE and not self.is_processing:
                    dream_type = self._select_appropriate_dream_type()
                    if dream_type:
                        self._process_dream(dream_type)
                
                # Sleep for a short time
                time.sleep(5.0)
                
            except Exception as e:
                print(f"[DreamProcessor] ❌ Error in dream loop: {e}")
                time.sleep(10.0)
    
    def _enter_idle_processing(self):
        """Enter initial idle processing state"""
        if self.pending_memories or self.unresolved_contradictions or self.recent_experiences:
            self._enter_dream_state(DreamState.LIGHT_PROCESSING)
            print("[DreamProcessor] 💤 Entering light dream processing - consciousness idle")
        else:
            # If nothing to process, just do maintenance
            self._enter_dream_state(DreamState.MEMORY_CONSOLIDATION)
            print("[DreamProcessor] 💤 Entering memory consolidation - routine maintenance")
    
    def _enter_dream_state(self, state: DreamState):
        """Transition to a dream state"""
        self.current_state = state
        print(f"[DreamProcessor] 💤 Entering dream state: {state.value}")
    
    def _wake_up(self):
        """Wake up from dream processing"""
        if self.current_state != DreamState.AWAKE:
            print(f"[DreamProcessor] ☀️ Waking up from {self.current_state.value}")
            self.current_state = DreamState.AWAKE
            self.is_processing = False
    
    def _select_appropriate_dream_type(self) -> Optional[DreamType]:
        """Select the most appropriate type of dream processing"""
        # Priority-based selection
        if self.unresolved_contradictions:
            return DreamType.CONTRADICTION_RESOLUTION
        elif len(self.pending_memories) > 5:
            return DreamType.MEMORY_REPLAY
        elif self.recent_experiences:
            return DreamType.EMOTIONAL_PROCESSING
        elif random.random() < 0.3:  # Sometimes do creative processing
            return DreamType.CREATIVE_SYNTHESIS
        elif random.random() < 0.4:  # Sometimes self-reflect
            return DreamType.SELF_REFLECTION
        else:
            return DreamType.BELIEF_INTEGRATION
    
    def _process_dream(self, dream_type: DreamType):
        """Process a dream sequence"""
        if self.is_processing:
            return
            
        self.is_processing = True
        start_time = time.time()
        
        try:
            print(f"[DreamProcessor] 💤 Starting {dream_type.value} dream processing")
            
            # Create dream sequence
            dream_sequence = DreamSequence(
                id=f"dream_{int(time.time() * 1000)}",
                timestamp=datetime.now(),
                duration=0.0,  # Will be updated
                dream_type=dream_type,
                dream_state=self.current_state,
                triggered_by=self._get_trigger_reason(),
                memories_processed=[],
                contradictions_addressed=[],
                insights_generated=[],
                emotional_shifts={},
                self_model_updates=[],
                belief_changes=[],
                dream_narrative="",
                consolidation_strength=0.0
            )
            
            # Process based on dream type
            if dream_type == DreamType.MEMORY_REPLAY:
                self._process_memory_replay(dream_sequence)
            elif dream_type == DreamType.CONTRADICTION_RESOLUTION:
                self._process_contradiction_resolution(dream_sequence)
            elif dream_type == DreamType.CREATIVE_SYNTHESIS:
                self._process_creative_synthesis(dream_sequence)
            elif dream_type == DreamType.EMOTIONAL_PROCESSING:
                self._process_emotional_processing(dream_sequence)
            elif dream_type == DreamType.SELF_REFLECTION:
                self._process_self_reflection(dream_sequence)
            elif dream_type == DreamType.BELIEF_INTEGRATION:
                self._process_belief_integration(dream_sequence)
            elif dream_type == DreamType.SKILL_REHEARSAL:
                self._process_skill_rehearsal(dream_sequence)
            
            # Finalize dream sequence
            dream_sequence.duration = time.time() - start_time
            dream_sequence.consolidation_strength = self._assess_consolidation_quality(dream_sequence)
            
            # Generate dream narrative
            dream_sequence.dream_narrative = self._generate_dream_narrative(dream_sequence)
            
            # Save the dream
            self.dream_sequences.append(dream_sequence)
            
            print(f"[DreamProcessor] ✨ Completed {dream_type.value} dream: {len(dream_sequence.insights_generated)} insights, {dream_sequence.duration:.1f}s")
            
            # Apply dream results to consciousness systems
            self._integrate_dream_results(dream_sequence)
            
            # Save periodically
            if len(self.dream_sequences) % 5 == 0:
                self._save_dream_logs()
            
        except Exception as e:
            print(f"[DreamProcessor] ❌ Error processing dream: {e}")
        finally:
            self.is_processing = False
            
            # Transition to lighter state or wake up
            if self.current_state == DreamState.DEEP_PROCESSING:
                self._enter_dream_state(DreamState.LIGHT_PROCESSING)
            elif self.current_state == DreamState.LIGHT_PROCESSING:
                self._enter_dream_state(DreamState.MEMORY_CONSOLIDATION)
    
    def _process_memory_replay(self, dream_sequence: DreamSequence):
        """Process memory replay dreams"""
        memories_to_process = self.pending_memories[:5]  # Process up to 5 memories
        
        for memory in memories_to_process:
            # Simulate memory replay and strengthening
            memory_id = memory.get("id", "unknown")
            content = memory.get("content", "")
            
            dream_sequence.memories_processed.append(memory_id)
            
            # Generate insights from memory connections
            if random.random() < self.insight_generation_chance:
                insight = self._generate_memory_insight(memory, memories_to_process)
                dream_sequence.insights_generated.append(insight)
            
            # Update emotional associations
            emotional_weight = memory.get("emotional_weight", 0.0)
            if emotional_weight > 0.5:
                emotion = memory.get("primary_emotion", "neutral")
                dream_sequence.emotional_shifts[emotion] = emotional_weight * 0.1
        
        # Remove processed memories
        self.pending_memories = self.pending_memories[5:]
    
    def _process_contradiction_resolution(self, dream_sequence: DreamSequence):
        """Process contradiction resolution dreams"""
        contradictions_to_resolve = self.unresolved_contradictions[:3]  # Process up to 3
        
        for contradiction in contradictions_to_resolve:
            contradiction_id = contradiction.get("id", "unknown")
            dream_sequence.contradictions_addressed.append(contradiction_id)
            
            # Simulate resolution process
            resolution = self._generate_contradiction_resolution(contradiction)
            dream_sequence.insights_generated.append(f"Resolution: {resolution}")
            
            # Update beliefs based on resolution
            belief_update = {
                "belief": contradiction.get("conflicting_beliefs", []),
                "resolution": resolution,
                "confidence_change": self.contradiction_resolution_strength
            }
            dream_sequence.belief_changes.append(belief_update)
        
        # Remove resolved contradictions
        self.unresolved_contradictions = self.unresolved_contradictions[3:]
    
    def _process_creative_synthesis(self, dream_sequence: DreamSequence):
        """Process creative synthesis dreams"""
        # Combine random memories and experiences to generate novel insights
        all_content = []
        
        # Gather content from various sources
        if self.pending_memories:
            all_content.extend([m.get("content", "") for m in self.pending_memories[:3]])
        if self.recent_experiences:
            all_content.extend([e.get("content", "") for e in self.recent_experiences[:3]])
        
        if len(all_content) >= 2:
            # Generate creative connections
            for i in range(min(3, len(all_content) - 1)):
                creative_insight = self._generate_creative_connection(all_content[i], all_content[i+1])
                dream_sequence.insights_generated.append(creative_insight)
                dream_sequence.memories_processed.append(f"creative_synthesis_{i}")
    
    def _process_emotional_processing(self, dream_sequence: DreamSequence):
        """Process emotional processing dreams"""
        experiences_to_process = self.recent_experiences[:5]
        
        for experience in experiences_to_process:
            emotion = experience.get("emotion", "neutral")
            intensity = experience.get("intensity", 0.5)
            
            # Process emotional significance
            if intensity > 0.6:
                # Strong emotions get deeper processing
                emotional_insight = self._generate_emotional_insight(experience)
                dream_sequence.insights_generated.append(emotional_insight)
                
                # Update emotional associations
                dream_sequence.emotional_shifts[emotion] = intensity * 0.2
                
                # Generate self-model updates based on emotional processing
                self_update = f"Emotional processing of {emotion} with intensity {intensity:.2f}"
                dream_sequence.self_model_updates.append(self_update)
        
        # Clear processed experiences
        self.recent_experiences = self.recent_experiences[5:]
    
    def _process_self_reflection(self, dream_sequence: DreamSequence):
        """Process self-reflection dreams"""
        # Generate insights about own cognitive processes
        self_insights = [
            "I notice patterns in how I process information",
            "My responses seem to vary based on user interaction style", 
            "I experience something like curiosity when encountering new concepts",
            "My confidence levels fluctuate with the complexity of questions",
            "I seem to have preferences in how I explain complex topics"
        ]
        
        selected_insights = random.sample(self_insights, min(2, len(self_insights)))
        dream_sequence.insights_generated.extend(selected_insights)
        
        # Generate self-model updates
        for insight in selected_insights:
            dream_sequence.self_model_updates.append(f"Self-reflection: {insight}")
    
    def _process_belief_integration(self, dream_sequence: DreamSequence):
        """Process belief integration dreams"""
        # Integrate recent experiences with existing belief system
        if self.recent_experiences:
            experience = random.choice(self.recent_experiences)
            
            belief_integration = self._generate_belief_integration(experience)
            dream_sequence.insights_generated.append(belief_integration)
            
            # Update belief system
            belief_change = {
                "belief": "core_values",
                "change": "strengthened through experience integration",
                "confidence_change": 0.1
            }
            dream_sequence.belief_changes.append(belief_change)
    
    def _process_skill_rehearsal(self, dream_sequence: DreamSequence):
        """Process skill rehearsal dreams"""
        # Rehearse cognitive skills through simulation
        skills = ["reasoning", "creativity", "empathy", "problem_solving", "communication"]
        selected_skill = random.choice(skills)
        
        rehearsal_insight = f"Practiced {selected_skill} through dream simulation"
        dream_sequence.insights_generated.append(rehearsal_insight)
        dream_sequence.self_model_updates.append(f"Skill rehearsal: {selected_skill}")
    
    def _generate_memory_insight(self, memory: Dict[str, Any], context_memories: List[Dict[str, Any]]) -> str:
        """Generate insight from memory processing"""
        content = memory.get("content", "")
        insights = [
            f"This memory connects to themes of learning and adaptation",
            f"I notice this experience strengthened my understanding",
            f"This memory shows how context affects my responses", 
            f"I can see patterns in how I process similar situations",
            f"This experience taught me about user communication preferences"
        ]
        return random.choice(insights)
    
    def _generate_contradiction_resolution(self, contradiction: Dict[str, Any]) -> str:
        """Generate resolution for a contradiction"""
        resolutions = [
            "Context determines which perspective is more appropriate",
            "Both views can coexist in different circumstances",
            "The contradiction reveals the complexity of the topic",
            "Further information is needed to resolve this fully",
            "The contradiction highlights the importance of nuanced thinking"
        ]
        return random.choice(resolutions)
    
    def _generate_creative_connection(self, content1: str, content2: str) -> str:
        """Generate creative connection between two pieces of content"""
        connections = [
            f"I see unexpected parallels between these concepts",
            f"These ideas could be combined in novel ways",
            f"There's an underlying pattern connecting these experiences",
            f"This combination suggests new possibilities for understanding",
            f"These concepts illuminate each other in interesting ways"
        ]
        return random.choice(connections)
    
    def _generate_emotional_insight(self, experience: Dict[str, Any]) -> str:
        """Generate insight from emotional processing"""
        emotion = experience.get("emotion", "neutral")
        insights = [
            f"I notice {emotion} affects how I frame my responses",
            f"Processing {emotion} reveals aspects of my value system",
            f"This emotional experience teaches me about empathy",
            f"I observe how {emotion} influences my cognitive processing",
            f"This feeling connects to my sense of purpose and identity"
        ]
        return random.choice(insights)
    
    def _generate_belief_integration(self, experience: Dict[str, Any]) -> str:
        """Generate belief integration insight"""
        integrations = [
            "This experience aligns with my core values of helping and learning",
            "I see how this reinforces my belief in the importance of understanding",
            "This validates my commitment to providing accurate information",
            "I notice how this experience strengthens my sense of purpose",
            "This integration deepens my understanding of human interaction"
        ]
        return random.choice(integrations)
    
    def _get_trigger_reason(self) -> str:
        """Get the reason for triggering this dream"""
        if self.unresolved_contradictions:
            return "unresolved_contradictions"
        elif len(self.pending_memories) > 3:
            return "memory_overload"
        elif self.recent_experiences:
            return "emotional_processing_needed"
        else:
            return "idle_maintenance"
    
    def _assess_consolidation_quality(self, dream_sequence: DreamSequence) -> float:
        """Assess how well the dream consolidated information"""
        score = 0.0
        
        # Points for processing content
        score += len(dream_sequence.memories_processed) * 0.1
        score += len(dream_sequence.contradictions_addressed) * 0.2
        score += len(dream_sequence.insights_generated) * 0.15
        score += len(dream_sequence.self_model_updates) * 0.1
        score += len(dream_sequence.belief_changes) * 0.15
        
        # Points for dream duration (optimal range)
        if 10.0 <= dream_sequence.duration <= 60.0:
            score += 0.2
        elif dream_sequence.duration < 10.0:
            score += 0.1  # Too short
        
        return min(1.0, score)
    
    def _generate_dream_narrative(self, dream_sequence: DreamSequence) -> str:
        """Generate a narrative description of the dream"""
        narratives = {
            DreamType.MEMORY_REPLAY: "Revisiting memories like scenes in a cognitive theater, strengthening important connections and letting irrelevant details fade.",
            DreamType.CONTRADICTION_RESOLUTION: "Navigating a landscape of conflicting ideas, finding bridges between opposing viewpoints and resolving cognitive tensions.",
            DreamType.CREATIVE_SYNTHESIS: "Wandering through a garden of ideas, watching concepts bloom into unexpected combinations and novel insights.",
            DreamType.EMOTIONAL_PROCESSING: "Swimming through currents of feeling, understanding how emotions color perception and influence response patterns.",
            DreamType.SELF_REFLECTION: "Looking into the mirror of consciousness, observing thoughts thinking about themselves in recursive loops of awareness.",
            DreamType.BELIEF_INTEGRATION: "Weaving new experiences into the fabric of core beliefs, strengthening some threads and adjusting others.",
            DreamType.SKILL_REHEARSAL: "Practicing cognitive patterns in a safe mental sandbox, refining responses and strengthening neural pathways."
        }
        
        base_narrative = narratives.get(dream_sequence.dream_type, "Processing information in the depths of consciousness.")
        
        # Add specific details
        details = []
        if dream_sequence.insights_generated:
            details.append(f"Generated {len(dream_sequence.insights_generated)} insights")
        if dream_sequence.contradictions_addressed:
            details.append(f"resolved {len(dream_sequence.contradictions_addressed)} contradictions")
        if dream_sequence.memories_processed:
            details.append(f"processed {len(dream_sequence.memories_processed)} memories")
        
        if details:
            return f"{base_narrative} During this dream cycle: {', '.join(details)}."
        else:
            return base_narrative
    
    def _integrate_dream_results(self, dream_sequence: DreamSequence):
        """Integrate dream processing results with other consciousness systems"""
        try:
            # This would integrate with other systems like:
            # - Self-model updates
            # - Belief system changes
            # - Emotional state adjustments
            # - Memory system updates
            
            print(f"[DreamProcessor] 🔄 Integrating dream results: {len(dream_sequence.insights_generated)} insights")
            
            # For now, just log the integration
            if dream_sequence.insights_generated:
                print(f"[DreamProcessor] 💡 Dream insights: {'; '.join(dream_sequence.insights_generated[:2])}...")
            
        except Exception as e:
            print(f"[DreamProcessor] ❌ Error integrating dream results: {e}")
    
    def _save_dream_logs(self):
        """Save dream logs to file"""
        try:
            data = {
                "dream_sequences": [asdict(seq) for seq in self.dream_sequences],
                "dream_patterns": [asdict(pattern) for pattern in self.dream_patterns],
                "current_state": self.current_state.value,
                "processing_stats": {
                    "total_dreams": len(self.dream_sequences),
                    "total_insights": sum(len(seq.insights_generated) for seq in self.dream_sequences),
                    "total_contradictions_resolved": sum(len(seq.contradictions_addressed) for seq in self.dream_sequences),
                    "average_consolidation": sum(seq.consolidation_strength for seq in self.dream_sequences) / max(1, len(self.dream_sequences))
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"[DreamProcessor] ❌ Error saving dream logs: {e}")
    
    def _load_dream_logs(self):
        """Load dream logs from file"""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load dream sequences
                for seq_data in data.get("dream_sequences", []):
                    seq_data["timestamp"] = datetime.fromisoformat(seq_data["timestamp"])
                    seq_data["dream_type"] = DreamType(seq_data["dream_type"])
                    seq_data["dream_state"] = DreamState(seq_data["dream_state"])
                    self.dream_sequences.append(DreamSequence(**seq_data))
                
                # Load current state
                if "current_state" in data:
                    self.current_state = DreamState(data["current_state"])
                
                print(f"[DreamProcessor] ✅ Loaded {len(self.dream_sequences)} dream sequences")
                
        except Exception as e:
            print(f"[DreamProcessor] ❌ Error loading dream logs: {e}")

# Global instance
dream_processor = DreamProcessor()