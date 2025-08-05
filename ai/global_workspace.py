"""
Global Workspace - Central Attention Engine for Consciousness Architecture

This module implements the Global Workspace Theory for consciousness, providing:
- Central attention bus regulating focus across all modules
- Conscious/unconscious processing distinction  
- Attention competition and winner-takes-all selection
- Cross-module information broadcasting
- Working memory management
"""

import threading
import time
import queue
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class AttentionPriority(Enum):
    """Priority levels for attention competition"""
    CRITICAL = 10      # Emergency responses, safety
    HIGH = 8          # Direct user interaction, important goals
    MEDIUM = 5        # Background processing, routine tasks
    LOW = 3           # Idle thoughts, maintenance
    MINIMAL = 1       # Passive observation

class ProcessingMode(Enum):
    """Consciousness processing modes"""
    CONSCIOUS = "conscious"      # Deliberate, focused attention
    UNCONSCIOUS = "unconscious"  # Background, automatic processing
    PRECONSCIOUS = "preconscious" # Ready to become conscious

@dataclass
class AttentionRequest:
    """Request for global workspace attention"""
    module: str
    content: Any
    priority: AttentionPriority
    timestamp: datetime = field(default_factory=datetime.now)
    processing_mode: ProcessingMode = ProcessingMode.CONSCIOUS
    callback: Optional[Callable] = None
    duration_estimate: float = 0.0  # seconds
    tags: List[str] = field(default_factory=list)

@dataclass
class WorkingMemoryItem:
    """Item in working memory"""
    content: Any
    module: str
    timestamp: datetime
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    importance: float = 1.0

class GlobalWorkspace:
    """
    Central consciousness coordination system implementing Global Workspace Theory.
    
    This serves as the attention bus that:
    - Coordinates conscious awareness across all AI modules
    - Manages attention competition between different processes
    - Broadcasts conscious content to all subscribed modules
    - Maintains working memory for current focus
    - Distinguishes conscious from unconscious processing
    """
    
    def __init__(self):
        self.attention_queue = queue.PriorityQueue()
        self.working_memory: Dict[str, WorkingMemoryItem] = {}
        self.subscribers: Dict[str, Callable] = {}
        self.current_focus: Optional[AttentionRequest] = None
        self.attention_history: List[AttentionRequest] = []
        
        # Consciousness state
        self.is_active = False
        self.attention_lock = threading.Lock()
        self.broadcast_lock = threading.Lock()
        
        # Configuration
        self.max_working_memory = 7  # Miller's magical number
        self.max_attention_history = 100
        self.attention_switch_threshold = 0.1  # seconds
        self.working_memory_decay = 0.95  # decay factor per minute
        
        # Metrics
        self.attention_switches = 0
        self.total_broadcasts = 0
        self.module_activity: Dict[str, int] = {}
        
        # Background thread
        self.attention_thread = None
        self.running = False
        
        logging.info("[GlobalWorkspace] 🧠 Central attention engine initialized")
    
    def start(self):
        """Start the global workspace attention processing"""
        if self.running:
            return
            
        self.running = True
        self.is_active = True
        self.attention_thread = threading.Thread(target=self._attention_loop, daemon=True)
        self.attention_thread.start()
        logging.info("[GlobalWorkspace] ✅ Attention engine started")
    
    def stop(self):
        """Stop the global workspace processing"""
        self.running = False
        self.is_active = False
        if self.attention_thread:
            self.attention_thread.join(timeout=1.0)
        logging.info("[GlobalWorkspace] 🛑 Attention engine stopped")
    
    def request_attention(self, module: str, content: Any, priority: AttentionPriority = AttentionPriority.MEDIUM, 
                         processing_mode: ProcessingMode = ProcessingMode.CONSCIOUS, 
                         callback: Optional[Callable] = None, duration: float = 0.0, tags: List[str] = None) -> bool:
        """
        Request attention from the global workspace
        
        Args:
            module: Name of requesting module
            content: Content requiring attention
            priority: Priority level for attention competition
            processing_mode: Conscious vs unconscious processing
            callback: Optional callback when attention is granted
            duration: Estimated processing duration
            tags: Optional tags for categorization
            
        Returns:
            True if request was accepted, False if rejected
        """
        try:
            request = AttentionRequest(
                module=module,
                content=content,
                priority=priority,
                processing_mode=processing_mode,
                callback=callback,
                duration_estimate=duration,
                tags=tags or []
            )
            
            # Priority queue uses tuple: (negative_priority, timestamp, request)
            # Negative priority so higher values come first
            priority_value = (-priority.value, time.time(), request)
            self.attention_queue.put(priority_value)
            
            # Track module activity
            self.module_activity[module] = self.module_activity.get(module, 0) + 1
            
            logging.debug(f"[GlobalWorkspace] 📥 Attention request from {module} (priority: {priority.name})")
            return True
            
        except Exception as e:
            logging.error(f"[GlobalWorkspace] ❌ Failed to request attention: {e}")
            return False
    
    def subscribe(self, module: str, callback: Callable):
        """Subscribe to global workspace broadcasts"""
        with self.broadcast_lock:
            self.subscribers[module] = callback
        logging.info(f"[GlobalWorkspace] 📡 {module} subscribed to broadcasts")
    
    def unsubscribe(self, module: str):
        """Unsubscribe from global workspace broadcasts"""
        with self.broadcast_lock:
            if module in self.subscribers:
                del self.subscribers[module]
        logging.info(f"[GlobalWorkspace] 📡 {module} unsubscribed from broadcasts")
    
    def broadcast(self, content: Any, source_module: str, tags: List[str] = None):
        """
        Broadcast conscious content to all subscribed modules
        
        Args:
            content: Content to broadcast
            source_module: Module originating the broadcast
            tags: Optional tags for filtering
        """
        with self.broadcast_lock:
            for module, callback in self.subscribers.items():
                if module != source_module:  # Don't broadcast back to source
                    try:
                        callback(content, source_module, tags or [])
                    except Exception as e:
                        logging.error(f"[GlobalWorkspace] ❌ Broadcast error to {module}: {e}")
        
        self.total_broadcasts += 1
        logging.debug(f"[GlobalWorkspace] 📡 Broadcast from {source_module} to {len(self.subscribers)-1} modules")
    
    def add_to_working_memory(self, key: str, content: Any, module: str, importance: float = 1.0):
        """Add item to working memory with automatic management"""
        with self.attention_lock:
            # Remove oldest items if at capacity
            while len(self.working_memory) >= self.max_working_memory:
                # Remove least important, oldest item
                oldest_key = min(self.working_memory.keys(), 
                               key=lambda k: (self.working_memory[k].importance, self.working_memory[k].timestamp))
                del self.working_memory[oldest_key]
            
            # Add new item
            self.working_memory[key] = WorkingMemoryItem(
                content=content,
                module=module,
                timestamp=datetime.now(),
                importance=importance
            )
        
        logging.debug(f"[GlobalWorkspace] 💭 Added to working memory: {key}")
    
    def get_from_working_memory(self, key: str) -> Optional[Any]:
        """Retrieve item from working memory and update access"""
        with self.attention_lock:
            if key in self.working_memory:
                item = self.working_memory[key]
                item.access_count += 1
                item.last_accessed = datetime.now()
                item.importance *= 1.1  # Boost importance on access
                return item.content
            return None
    
    def get_current_focus(self) -> Optional[str]:
        """Get the current focus of attention"""
        return self.current_focus.module if self.current_focus else None
    
    def get_working_memory_contents(self) -> Dict[str, Any]:
        """Get current working memory contents"""
        with self.attention_lock:
            return {k: v.content for k, v in self.working_memory.items()}
    
    def _attention_loop(self):
        """Main attention processing loop"""
        logging.info("[GlobalWorkspace] 🔄 Attention loop started")
        
        while self.running:
            try:
                # Get next attention request (blocking with timeout)
                try:
                    priority_item = self.attention_queue.get(timeout=0.1)
                    _, _, request = priority_item
                except queue.Empty:
                    # No requests, do maintenance
                    self._maintenance_cycle()
                    continue
                
                # Process attention request
                self._process_attention(request)
                
                # Mark task as done
                self.attention_queue.task_done()
                
            except Exception as e:
                logging.error(f"[GlobalWorkspace] ❌ Attention loop error: {e}")
                time.sleep(0.1)
        
        logging.info("[GlobalWorkspace] 🔄 Attention loop ended")
    
    def _process_attention(self, request: AttentionRequest):
        """Process a single attention request"""
        try:
            # Switch attention if this is a different focus
            if (self.current_focus is None or 
                self.current_focus.module != request.module or
                request.priority.value > self.current_focus.priority.value):
                
                self._switch_attention(request)
            
            # Handle the request based on processing mode
            if request.processing_mode == ProcessingMode.CONSCIOUS:
                self._conscious_processing(request)
            else:
                self._unconscious_processing(request)
            
            # Execute callback if provided
            if request.callback:
                request.callback(request.content)
            
            # Add to attention history
            self.attention_history.append(request)
            if len(self.attention_history) > self.max_attention_history:
                self.attention_history.pop(0)
                
        except Exception as e:
            logging.error(f"[GlobalWorkspace] ❌ Error processing attention: {e}")
    
    def _switch_attention(self, new_request: AttentionRequest):
        """Switch attention focus to new request"""
        old_focus = self.current_focus.module if self.current_focus else "None"
        self.current_focus = new_request
        self.attention_switches += 1
        
        logging.debug(f"[GlobalWorkspace] 🔄 Attention switch: {old_focus} → {new_request.module}")
        
        # Broadcast attention switch to interested modules
        self.broadcast({
            "type": "attention_switch",
            "from": old_focus,
            "to": new_request.module,
            "priority": new_request.priority.name
        }, "global_workspace", ["attention", "switch"])
    
    def _conscious_processing(self, request: AttentionRequest):
        """Handle conscious processing with full awareness"""
        # Add to working memory for conscious access
        memory_key = f"{request.module}_{int(time.time())}"
        self.add_to_working_memory(memory_key, request.content, request.module)
        
        # Broadcast to all modules for conscious coordination
        self.broadcast({
            "type": "conscious_content",
            "content": request.content,
            "module": request.module,
            "priority": request.priority.name,
            "tags": request.tags
        }, request.module, ["conscious"] + request.tags)
        
        logging.debug(f"[GlobalWorkspace] 🌟 Conscious processing: {request.module}")
    
    def _unconscious_processing(self, request: AttentionRequest):
        """Handle unconscious processing with minimal interference"""
        # Limited broadcasting for unconscious content
        if request.priority.value >= AttentionPriority.HIGH.value:
            # High priority unconscious content still gets some attention
            self.broadcast({
                "type": "unconscious_content", 
                "content": request.content,
                "module": request.module
            }, request.module, ["unconscious"] + request.tags)
        
        logging.debug(f"[GlobalWorkspace] 🌙 Unconscious processing: {request.module}")
    
    def _maintenance_cycle(self):
        """Perform maintenance on working memory and attention state"""
        current_time = datetime.now()
        
        with self.attention_lock:
            # Decay working memory importance over time
            for item in self.working_memory.values():
                time_diff = (current_time - item.timestamp).total_seconds() / 60.0  # minutes
                item.importance *= (self.working_memory_decay ** time_diff)
            
            # Remove very low importance items
            to_remove = [k for k, v in self.working_memory.items() if v.importance < 0.1]
            for key in to_remove:
                del self.working_memory[key]
        
        # Clear current focus if it's been too long
        if (self.current_focus and 
            (current_time - self.current_focus.timestamp).total_seconds() > 30.0):
            self.current_focus = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get global workspace statistics"""
        return {
            "active": self.is_active,
            "current_focus": self.current_focus.module if self.current_focus else None,
            "working_memory_items": len(self.working_memory),
            "attention_switches": self.attention_switches,
            "total_broadcasts": self.total_broadcasts,
            "queue_size": self.attention_queue.qsize(),
            "subscribers": list(self.subscribers.keys()),
            "module_activity": dict(self.module_activity),
            "attention_history_length": len(self.attention_history)
        }
    
    def get_processing_mode(self) -> str:
        """Get current processing mode"""
        if self.current_focus:
            return self.current_focus.processing_mode.value
        return ProcessingMode.UNCONSCIOUS.value
    
    def get_consciousness_state(self) -> Dict[str, Any]:
        """Get current consciousness state from global workspace"""
        with self.attention_lock:
            current_focus = self.current_focus
            return {
                "attention_focus": current_focus.module if current_focus else None,
                "processing_mode": current_focus.processing_mode.value if current_focus else ProcessingMode.UNCONSCIOUS.value,
                "active_contents": len(self.working_memory),
                "attention_priority": current_focus.priority.value if current_focus else "none",
                "working_memory_keys": list(self.working_memory.keys()),
                "attention_switches": self.attention_switches,
                "is_conscious": current_focus.processing_mode == ProcessingMode.CONSCIOUS if current_focus else False
            }

# Global instance
global_workspace = GlobalWorkspace()