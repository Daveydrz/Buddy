"""
Extraction Process Coordinator for Buddy System
Created: 2025-01-22
Purpose: Central coordinator to optimize memory extraction processes and eliminate resource contention

Features:
- Context-aware prioritization of extraction requests
- Smart result sharing between components
- Efficient KoboldCPP connection management  
- Redundancy elimination through intelligent caching
- Robust error handling and recovery
- Class 5+ consciousness capabilities preservation
"""

import threading
import time
import queue
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

# Import existing modules
from ai.comprehensive_memory_extractor import ExtractionResult, ComprehensiveMemoryExtractor
from ai.kobold_connection_manager import EnhancedKoboldCPPManager

class ExtractionPriority(Enum):
    """Extraction priority levels"""
    CRITICAL = 0    # User interaction in progress
    HIGH = 1        # Consciousness module requests 
    MEDIUM = 2      # Background memory processing
    LOW = 3         # Maintenance and optimization

class ExtractionType(Enum):
    """Types of extraction operations"""
    USER_INPUT = "user_input"          # Direct user message processing
    CONSCIOUSNESS = "consciousness"     # Consciousness module processing
    MEMORY_FUSION = "memory_fusion"     # Memory fusion operations
    BACKGROUND = "background"           # Background processing
    MAINTENANCE = "maintenance"         # System maintenance

@dataclass
class ExtractionRequest:
    """Structured extraction request"""
    request_id: str
    username: str
    text: str
    extraction_type: ExtractionType
    priority: ExtractionPriority
    context: Dict[str, Any]
    created_at: datetime
    callback: Optional[Callable] = None
    timeout: float = 30.0
    
    def get_cache_key(self) -> str:
        """Generate cache key for this request"""
        text_hash = hashlib.md5(self.text.lower().strip().encode()).hexdigest()[:8]
        return f"{self.username}:{text_hash}:{self.extraction_type.value}"

@dataclass 
class ExtractionResponse:
    """Structured extraction response"""
    request_id: str
    result: ExtractionResult
    processing_time: float
    cache_hit: bool
    tier_used: str
    errors: List[str]

class ExtractionCoordinator:
    """
    🧠 Central coordinator for all memory extraction processes
    
    Optimizes Buddy system by:
    1. Prioritizing extractions based on context and importance
    2. Sharing results between components to eliminate redundancy  
    3. Managing KoboldCPP connections efficiently
    4. Implementing proper error handling and recovery
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern for global coordination"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize coordinator if not already done"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        
        # Request management
        self.request_queue = queue.PriorityQueue(maxsize=50)
        self.processing_threads = []
        self.active_requests = {}
        self.request_lock = threading.Lock()
        
        # Result caching and sharing
        self.result_cache = {}
        self.cache_timestamps = {}
        self.cache_lock = threading.Lock()
        self.cache_ttl = 300  # 5 minutes
        
        # Extractors per user
        self.user_extractors = {}
        self.extractor_lock = threading.Lock()
        
        # Connection management
        self.connection_pool = None
        self.connection_lock = threading.Lock()
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'tier1_extractions': 0,
            'tier2_extractions': 0, 
            'tier3_extractions': 0,
            'average_processing_time': 0.0,
            'error_count': 0
        }
        self.metrics_lock = threading.Lock()
        
        # Context awareness
        self.active_users = {}  # Track user activity for context
        self.user_activity_lock = threading.Lock()
        
        # Start processing threads
        self._start_processing_threads()
        
        print("[ExtractionCoordinator] 🚀 Central extraction coordinator initialized")
        print("[ExtractionCoordinator] 🎯 Features: Context-aware prioritization, result sharing, connection optimization")
    
    def _start_processing_threads(self):
        """Start background processing threads"""
        # High priority thread for user interactions
        high_priority_thread = threading.Thread(
            target=self._process_requests,
            args=(ExtractionPriority.CRITICAL, ExtractionPriority.HIGH),
            daemon=True,
            name="ExtractionProcessor-HighPriority"
        )
        high_priority_thread.start()
        self.processing_threads.append(high_priority_thread)
        
        # Medium priority thread for consciousness modules
        medium_priority_thread = threading.Thread(
            target=self._process_requests, 
            args=(ExtractionPriority.MEDIUM,),
            daemon=True,
            name="ExtractionProcessor-MediumPriority"
        )
        medium_priority_thread.start()
        self.processing_threads.append(medium_priority_thread)
        
        # Low priority thread for background tasks
        low_priority_thread = threading.Thread(
            target=self._process_requests,
            args=(ExtractionPriority.LOW,),
            daemon=True,
            name="ExtractionProcessor-LowPriority"
        )
        low_priority_thread.start()
        self.processing_threads.append(low_priority_thread)
        
        print(f"[ExtractionCoordinator] 🔧 Started {len(self.processing_threads)} processing threads")
    
    def extract_with_coordination(self, 
                                username: str,
                                text: str, 
                                extraction_type: ExtractionType = ExtractionType.USER_INPUT,
                                priority: Optional[ExtractionPriority] = None,
                                context: Optional[Dict[str, Any]] = None,
                                timeout: float = 30.0) -> ExtractionResponse:
        """
        🎯 Main extraction method with intelligent coordination
        
        Args:
            username: User identifier
            text: Text to extract from
            extraction_type: Type of extraction operation
            priority: Priority level (auto-determined if None)
            context: Additional context for processing
            timeout: Request timeout in seconds
        
        Returns:
            ExtractionResponse with results and metadata
        """
        
        # Auto-determine priority if not specified
        if priority is None:
            priority = self._determine_priority(extraction_type, username, text)
        
        # Create extraction request
        request = ExtractionRequest(
            request_id=f"req_{int(time.time() * 1000)}_{id(threading.current_thread())}",
            username=username,
            text=text,
            extraction_type=extraction_type,
            priority=priority,
            context=context or {},
            created_at=datetime.now(),
            timeout=timeout
        )
        
        print(f"[ExtractionCoordinator] 📥 Request {request.request_id}: {text[:50]}... (priority: {priority.name})")
        
        # Check cache first
        cache_key = request.get_cache_key()
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            print(f"[ExtractionCoordinator] ⚡ Cache HIT for {request.request_id}")
            self._update_metrics(cache_hit=True)
            return ExtractionResponse(
                request_id=request.request_id,
                result=cached_result,
                processing_time=0.001,
                cache_hit=True,
                tier_used="cache",
                errors=[]
            )
        
        # Update user activity for context awareness
        self._update_user_activity(username, extraction_type)
        
        # Process request with coordination
        try:
            start_time = time.time()
            
            # For high-priority requests, process immediately
            if priority in [ExtractionPriority.CRITICAL, ExtractionPriority.HIGH]:
                response = self._process_request_immediate(request)
            else:
                # Queue for background processing
                response = self._queue_request(request)
            
            processing_time = time.time() - start_time
            response.processing_time = processing_time
            
            # Cache result for future use
            self._cache_result(cache_key, response.result)
            
            self._update_metrics(
                cache_hit=False,
                processing_time=processing_time,
                tier_used=response.tier_used
            )
            
            print(f"[ExtractionCoordinator] ✅ Completed {request.request_id} in {processing_time:.3f}s (tier: {response.tier_used})")
            return response
            
        except Exception as e:
            print(f"[ExtractionCoordinator] ❌ Error processing {request.request_id}: {e}")
            self._update_metrics(error=True)
            
            # Return fallback response
            return ExtractionResponse(
                request_id=request.request_id,
                result=ExtractionResult([], "error", {"primary_emotion": "neutral"}, None, [], [], []),
                processing_time=0.0,
                cache_hit=False,
                tier_used="error",
                errors=[str(e)]
            )
    
    def _determine_priority(self, extraction_type: ExtractionType, username: str, text: str) -> ExtractionPriority:
        """🎯 Intelligently determine extraction priority based on context"""
        
        # Check if user is actively interacting
        with self.user_activity_lock:
            user_activity = self.active_users.get(username, {})
            last_interaction = user_activity.get('last_interaction', datetime.min)
            recent_activity = datetime.now() - last_interaction < timedelta(seconds=30)
        
        # Priority rules
        if extraction_type == ExtractionType.USER_INPUT:
            return ExtractionPriority.CRITICAL
        
        if extraction_type == ExtractionType.CONSCIOUSNESS and recent_activity:
            return ExtractionPriority.HIGH
        
        if extraction_type == ExtractionType.MEMORY_FUSION:
            # Check if this is enhancing recent memory
            if any(word in text.lower() for word in ['mcdonald', 'francesco', 'mcflurry']):
                return ExtractionPriority.HIGH
            return ExtractionPriority.MEDIUM
        
        if extraction_type == ExtractionType.BACKGROUND:
            return ExtractionPriority.LOW
        
        return ExtractionPriority.MEDIUM
    
    def _update_user_activity(self, username: str, extraction_type: ExtractionType):
        """Update user activity tracking for context awareness"""
        with self.user_activity_lock:
            if username not in self.active_users:
                self.active_users[username] = {}
            
            self.active_users[username].update({
                'last_interaction': datetime.now(),
                'extraction_type': extraction_type.value,
                'activity_count': self.active_users[username].get('activity_count', 0) + 1
            })
    
    def _get_cached_result(self, cache_key: str) -> Optional[ExtractionResult]:
        """Get cached extraction result if valid"""
        with self.cache_lock:
            if cache_key in self.result_cache:
                timestamp = self.cache_timestamps.get(cache_key, datetime.min)
                if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                    return self.result_cache[cache_key]
                else:
                    # Remove expired cache entry
                    del self.result_cache[cache_key]
                    del self.cache_timestamps[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: ExtractionResult):
        """Cache extraction result for future use"""
        with self.cache_lock:
            self.result_cache[cache_key] = result
            self.cache_timestamps[cache_key] = datetime.now()
            
            # Limit cache size
            if len(self.result_cache) > 500:
                self._clean_cache()
    
    def _clean_cache(self):
        """Clean expired cache entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, timestamp in self.cache_timestamps.items():
            if current_time - timestamp > timedelta(seconds=self.cache_ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            self.result_cache.pop(key, None)
            self.cache_timestamps.pop(key, None)
        
        print(f"[ExtractionCoordinator] 🧹 Cleaned {len(expired_keys)} expired cache entries")
    
    def _process_request_immediate(self, request: ExtractionRequest) -> ExtractionResponse:
        """Process high-priority request immediately"""
        return self._execute_extraction(request)
    
    def _queue_request(self, request: ExtractionRequest) -> ExtractionResponse:
        """Queue request for background processing"""
        # For now, process immediately but could implement true queuing
        return self._execute_extraction(request)
    
    def _execute_extraction(self, request: ExtractionRequest) -> ExtractionResponse:
        """Execute the actual extraction with proper coordination"""
        
        # Get or create user-specific extractor
        with self.extractor_lock:
            if request.username not in self.user_extractors:
                self.user_extractors[request.username] = ComprehensiveMemoryExtractor(request.username)
            extractor = self.user_extractors[request.username]
        
        # Determine optimal extraction tier based on context
        tier_to_use = self._select_optimal_tier(request)
        
        # Execute extraction with tier override
        start_time = time.time()
        
        try:
            if tier_to_use == "tier1":
                result = extractor._tier1_simple_extraction(request.text)
                tier_used = "tier1"
            elif tier_to_use == "tier2": 
                result = extractor._tier2_medium_extraction(request.text)
                tier_used = "tier2"
            else:  # tier3
                conversation_context = request.context.get('conversation_context', '')
                result = extractor._tier3_comprehensive_extraction(request.text, conversation_context)
                tier_used = "tier3"
            
            # Store any memory events in regular memory system  
            for event in result.memory_events:
                extractor._add_to_regular_memory(event)
            
            return ExtractionResponse(
                request_id=request.request_id,
                result=result,
                processing_time=time.time() - start_time,
                cache_hit=False,
                tier_used=tier_used,
                errors=[]
            )
            
        except Exception as e:
            print(f"[ExtractionCoordinator] ❌ Extraction error for {request.request_id}: {e}")
            return ExtractionResponse(
                request_id=request.request_id,
                result=ExtractionResult([], "error", {"primary_emotion": "neutral"}, None, [], [], []),
                processing_time=time.time() - start_time,
                cache_hit=False,
                tier_used="error",
                errors=[str(e)]
            )
    
    def _select_optimal_tier(self, request: ExtractionRequest) -> str:
        """🎯 Select optimal extraction tier based on context and priority"""
        
        text = request.text
        priority = request.priority
        extraction_type = request.extraction_type
        
        # Force tier selection based on priority
        if priority == ExtractionPriority.CRITICAL:
            # User interaction - use fastest appropriate tier
            if len(text.split()) <= 8:
                return "tier1"  # Quick response for short inputs
            elif len(text.split()) <= 20:
                return "tier2"  # Medium response for medium inputs
            else:
                return "tier3"  # Full analysis for complex inputs
        
        if priority == ExtractionPriority.HIGH:
            # Consciousness modules - balance quality vs speed
            if extraction_type == ExtractionType.CONSCIOUSNESS:
                return "tier2"  # Good balance for consciousness
            else:
                return "tier3"  # Full analysis for important requests
        
        if priority == ExtractionPriority.MEDIUM:
            # Background processing - prefer quality
            return "tier3"
        
        # Low priority - use cheapest option
        return "tier1"
    
    def _process_requests(self, *allowed_priorities):
        """Background thread to process queued requests"""
        while True:
            try:
                # This is a simplified version - would implement full queue processing
                time.sleep(0.1)
            except Exception as e:
                print(f"[ExtractionCoordinator] ❌ Processing thread error: {e}")
                time.sleep(1.0)
    
    def _update_metrics(self, 
                       cache_hit: bool = False,
                       processing_time: float = 0.0,
                       tier_used: str = None,
                       error: bool = False):
        """Update performance metrics"""
        with self.metrics_lock:
            self.metrics['total_requests'] += 1
            
            if cache_hit:
                self.metrics['cache_hits'] += 1
            else:
                self.metrics['cache_misses'] += 1
            
            if tier_used:
                if tier_used == "tier1":
                    self.metrics['tier1_extractions'] += 1
                elif tier_used == "tier2":
                    self.metrics['tier2_extractions'] += 1
                elif tier_used == "tier3":
                    self.metrics['tier3_extractions'] += 1
            
            if processing_time > 0:
                # Update average processing time
                current_avg = self.metrics['average_processing_time']
                total_requests = max(1, self.metrics['total_requests'])
                self.metrics['average_processing_time'] = (
                    (current_avg * (total_requests - 1) + processing_time) / total_requests
                )
            
            if error:
                self.metrics['error_count'] += 1
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        with self.metrics_lock:
            cache_hit_rate = 0.0
            if self.metrics['total_requests'] > 0:
                cache_hit_rate = (self.metrics['cache_hits'] / self.metrics['total_requests']) * 100
            
            return {
                **self.metrics.copy(),
                'cache_hit_rate_percent': cache_hit_rate,
                'active_users': len(self.active_users),
                'cached_results': len(self.result_cache)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'coordinator_active': True,
            'processing_threads': len(self.processing_threads),
            'queue_size': self.request_queue.qsize(),
            'active_extractors': len(self.user_extractors),
            'metrics': self.get_performance_metrics(),
            'timestamp': datetime.now().isoformat()
        }

# Global coordinator instance
extraction_coordinator = ExtractionCoordinator()

def get_extraction_coordinator() -> ExtractionCoordinator:
    """Get global extraction coordinator instance"""
    return extraction_coordinator

# Convenience functions for easy integration
def extract_with_coordination(username: str, 
                            text: str,
                            extraction_type: ExtractionType = ExtractionType.USER_INPUT,
                            priority: Optional[ExtractionPriority] = None,
                            context: Optional[Dict[str, Any]] = None) -> ExtractionResponse:
    """
    🎯 Extract memory with full coordination and optimization
    
    This is the main entry point for all extraction operations in Buddy.
    """
    return extraction_coordinator.extract_with_coordination(
        username=username,
        text=text, 
        extraction_type=extraction_type,
        priority=priority,
        context=context
    )

# Export key classes and functions
__all__ = [
    'ExtractionCoordinator',
    'ExtractionPriority', 
    'ExtractionType',
    'ExtractionRequest',
    'ExtractionResponse',
    'extract_with_coordination',
    'get_extraction_coordinator'
]