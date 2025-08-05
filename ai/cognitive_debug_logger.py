#!/usr/bin/env python3
"""
Cognitive Debug Logger - Track cognitive state usage per reply
Created: 2025-01-18
Purpose: Log detailed information about how cognitive modules affect each response
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class CognitiveDebugLogger:
    """
    Logs detailed information about cognitive state usage in each response
    """
    
    def __init__(self, log_file: str = "cognitive_debug.json"):
        self.log_file = Path(log_file)
        self.current_interaction = None
        self.interaction_history = []
        
        # Load existing history
        self._load_history()
        
        logging.info(f"[CognitiveDebugLogger] 📊 Initialized with {len(self.interaction_history)} past interactions")
    
    def _load_history(self):
        """Load existing interaction history"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.interaction_history = data.get("interactions", [])
                    # Keep only last 100 interactions
                    if len(self.interaction_history) > 100:
                        self.interaction_history = self.interaction_history[-100:]
        except Exception as e:
            logging.error(f"[CognitiveDebugLogger] ❌ Error loading history: {e}")
            self.interaction_history = []
    
    def start_interaction(self, user_input: str, user_id: str) -> str:
        """
        Start tracking a new interaction
        
        Args:
            user_input: The user's input text
            user_id: User identifier
            
        Returns:
            Interaction ID for this tracking session
        """
        interaction_id = f"interaction_{int(datetime.now().timestamp())}"
        
        self.current_interaction = {
            "id": interaction_id,
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "user_id": user_id,
            "input_length": len(user_input),
            "processing_stages": [],
            "cognitive_modules_used": {},
            "prompt_modifications": {},
            "response_modulations": {},
            "consciousness_events": [],
            "performance_metrics": {},
            "errors": []
        }
        
        logging.debug(f"[CognitiveDebugLogger] 🆕 Started tracking interaction: {interaction_id}")
        return interaction_id
    
    def log_cognitive_module_usage(self, module_name: str, input_data: Any, output_data: Any, 
                                   processing_time: float = None, error: str = None):
        """
        Log usage of a cognitive module
        
        Args:
            module_name: Name of the cognitive module
            input_data: Input data to the module
            output_data: Output data from the module
            processing_time: Time taken to process (seconds)
            error: Error message if any
        """
        if not self.current_interaction:
            return
        
        module_entry = {
            "timestamp": datetime.now().isoformat(),
            "module": module_name,
            "input_summary": self._summarize_data(input_data),
            "output_summary": self._summarize_data(output_data),
            "processing_time": processing_time,
            "success": error is None,
            "error": error
        }
        
        self.current_interaction["cognitive_modules_used"][module_name] = module_entry
        
        logging.debug(f"[CognitiveDebugLogger] 📊 Logged module usage: {module_name}")
    
    def log_processing_stage(self, stage_name: str, description: str, data: Dict[str, Any] = None):
        """
        Log a processing stage in the response pipeline
        
        Args:
            stage_name: Name of the processing stage
            description: Description of what happened
            data: Additional data about the stage
        """
        if not self.current_interaction:
            return
        
        stage_entry = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage_name,
            "description": description,
            "data": self._summarize_data(data) if data else None
        }
        
        self.current_interaction["processing_stages"].append(stage_entry)
        
        logging.debug(f"[CognitiveDebugLogger] 🔄 Logged processing stage: {stage_name}")
    
    def log_prompt_modification(self, modification_type: str, original_size: int, 
                               modified_size: int, cognitive_tokens: Dict[str, Any]):
        """
        Log how cognitive state modified the prompt
        
        Args:
            modification_type: Type of modification (e.g., "consciousness_injection")
            original_size: Original prompt size
            modified_size: Modified prompt size
            cognitive_tokens: Cognitive tokens that were added
        """
        if not self.current_interaction:
            return
        
        modification_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": modification_type,
            "original_size": original_size,
            "modified_size": modified_size,
            "size_delta": modified_size - original_size,
            "cognitive_tokens": self._summarize_data(cognitive_tokens)
        }
        
        self.current_interaction["prompt_modifications"][modification_type] = modification_entry
        
        logging.debug(f"[CognitiveDebugLogger] 📝 Logged prompt modification: {modification_type}")
    
    def log_response_modulation(self, modulation_type: str, factors: Dict[str, float], 
                               applied_modifications: List[str]):
        """
        Log how cognitive state modulated the response
        
        Args:
            modulation_type: Type of modulation (e.g., "emotional", "personality")
            factors: Modulation factors applied
            applied_modifications: List of modifications that were applied
        """
        if not self.current_interaction:
            return
        
        modulation_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": modulation_type,
            "factors": factors,
            "applied_modifications": applied_modifications,
            "total_modifications": len(applied_modifications)
        }
        
        self.current_interaction["response_modulations"][modulation_type] = modulation_entry
        
        logging.debug(f"[CognitiveDebugLogger] 🎭 Logged response modulation: {modulation_type}")
    
    def log_consciousness_event(self, event_type: str, description: str, data: Dict[str, Any] = None):
        """
        Log a consciousness-related event
        
        Args:
            event_type: Type of consciousness event
            description: Description of the event
            data: Additional event data
        """
        if not self.current_interaction:
            return
        
        event_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description,
            "data": self._summarize_data(data) if data else None
        }
        
        self.current_interaction["consciousness_events"].append(event_entry)
        
        logging.debug(f"[CognitiveDebugLogger] 🧠 Logged consciousness event: {event_type}")
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = None):
        """
        Log a performance metric
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
        """
        if not self.current_interaction:
            return
        
        self.current_interaction["performance_metrics"][metric_name] = {
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        }
        
        logging.debug(f"[CognitiveDebugLogger] ⏱️ Logged performance metric: {metric_name}={value}")
    
    def log_error(self, error_stage: str, error_message: str, error_data: Dict[str, Any] = None):
        """
        Log an error that occurred during processing
        
        Args:
            error_stage: Stage where error occurred
            error_message: Error message
            error_data: Additional error data
        """
        if not self.current_interaction:
            return
        
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "stage": error_stage,
            "message": error_message,
            "data": self._summarize_data(error_data) if error_data else None
        }
        
        self.current_interaction["errors"].append(error_entry)
        
        logging.debug(f"[CognitiveDebugLogger] ❌ Logged error: {error_stage} - {error_message}")
    
    def finish_interaction(self, response_text: str, response_time: float):
        """
        Finish tracking the current interaction
        
        Args:
            response_text: The generated response
            response_time: Total response generation time
        """
        if not self.current_interaction:
            return
        
        # Add final information
        self.current_interaction.update({
            "response_text": response_text[:200] + "..." if len(response_text) > 200 else response_text,
            "response_length": len(response_text),
            "total_response_time": response_time,
            "completed_timestamp": datetime.now().isoformat(),
            "modules_count": len(self.current_interaction["cognitive_modules_used"]),
            "stages_count": len(self.current_interaction["processing_stages"]),
            "consciousness_events_count": len(self.current_interaction["consciousness_events"]),
            "errors_count": len(self.current_interaction["errors"])
        })
        
        # Add to history
        self.interaction_history.append(self.current_interaction)
        
        # Log summary
        summary = self._create_interaction_summary(self.current_interaction)
        logging.info(f"[CognitiveDebugLogger] ✅ Interaction completed: {summary}")
        
        # Save to file
        self._save_history()
        
        # Clear current interaction
        self.current_interaction = None
    
    def _summarize_data(self, data: Any) -> Any:
        """Summarize data for logging (truncate large objects)"""
        if data is None:
            return None
        
        if isinstance(data, dict):
            # Summarize dictionaries
            summary = {}
            for key, value in data.items():
                if isinstance(value, str) and len(value) > 100:
                    summary[key] = value[:100] + "..."
                elif isinstance(value, (list, tuple)) and len(value) > 5:
                    summary[key] = f"[{len(value)} items]"
                elif isinstance(value, dict) and len(value) > 10:
                    summary[key] = f"{{{len(value)} keys}}"
                else:
                    summary[key] = value
            return summary
        
        elif isinstance(data, str) and len(data) > 100:
            return data[:100] + "..."
        
        elif isinstance(data, (list, tuple)) and len(data) > 5:
            return f"[{len(data)} items: {data[:3]}...]"
        
        else:
            return data
    
    def _create_interaction_summary(self, interaction: Dict[str, Any]) -> str:
        """Create a summary of the interaction"""
        modules_used = list(interaction["cognitive_modules_used"].keys())
        response_time = interaction.get("total_response_time", 0)
        errors_count = interaction.get("errors_count", 0)
        
        return (f"ID={interaction['id'][:8]}..., "
                f"modules={len(modules_used)}, "
                f"time={response_time:.3f}s, "
                f"errors={errors_count}, "
                f"input={interaction['input_length']}chars, "
                f"output={interaction['response_length']}chars")
    
    def _save_history(self):
        """Save interaction history to file"""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "total_interactions": len(self.interaction_history),
                "interactions": self.interaction_history[-100:]  # Keep only last 100
            }
            
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            logging.debug(f"[CognitiveDebugLogger] 💾 Saved {len(self.interaction_history)} interactions")
            
        except Exception as e:
            logging.error(f"[CognitiveDebugLogger] ❌ Error saving history: {e}")
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get usage statistics across all interactions"""
        if not self.interaction_history:
            return {"total_interactions": 0}
        
        # Aggregate statistics
        total_interactions = len(self.interaction_history)
        total_modules_usage = {}
        total_response_time = 0
        total_errors = 0
        
        for interaction in self.interaction_history:
            # Count module usage
            for module in interaction.get("cognitive_modules_used", {}):
                total_modules_usage[module] = total_modules_usage.get(module, 0) + 1
            
            # Sum response times
            total_response_time += interaction.get("total_response_time", 0)
            
            # Count errors
            total_errors += interaction.get("errors_count", 0)
        
        avg_response_time = total_response_time / total_interactions if total_interactions > 0 else 0
        
        return {
            "total_interactions": total_interactions,
            "average_response_time": avg_response_time,
            "total_errors": total_errors,
            "error_rate": total_errors / total_interactions if total_interactions > 0 else 0,
            "modules_usage_frequency": total_modules_usage,
            "most_used_module": max(total_modules_usage, key=total_modules_usage.get) if total_modules_usage else None,
            "last_interaction": self.interaction_history[-1]["timestamp"] if self.interaction_history else None
        }

# Global instance
cognitive_debug_logger = CognitiveDebugLogger()