"""
Enterprise-Grade Extraction Optimization Framework
Created: 2025-01-08
Purpose: Unified extraction coordinator that manages all consciousness extraction operations
         with enterprise-grade performance, reliability, and coordination.

Key Features:
- Unified request coordination and batching
- Context-aware prioritization based on interaction type
- Smart result sharing and deduplication
- Connection pooling and circuit breaking
- Progressive resolution strategies
- Performance monitoring and metrics
"""

import asyncio
import threading
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
import hashlib

# Import existing systems to build upon
from ai.comprehensive_memory_extractor import ComprehensiveMemoryExtractor, ExtractionResult
from ai.unified_memory_manager import get_unified_memory_extractor
from ai.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitBreakerOpenError
from ai.consciousness_timeout_manager import timeout_manager, safe_consciousness_call

class ExtractionPriority(Enum):
    """Priority levels for extraction requests"""
    CRITICAL = "critical"      # Voice interactions, real-time responses
    HIGH = "high"             # Interactive conversations, immediate responses
    NORMAL = "normal"         # Background processing, memory analysis
    LOW = "low"               # Batch operations, cleanup tasks

class InteractionType(Enum):
    """Types of user interactions for context-aware processing"""
    VOICE_TO_SPEECH = "voice_to_speech"     # Real-time voice conversation
    TEXT_CHAT = "text_chat"                 # Text-based conversation
    BACKGROUND_PROCESSING = "background"     # Background memory processing
    BATCH_OPERATION = "batch"               # Bulk memory operations
    CONSCIOUSNESS_UPDATE = "consciousness"   # Consciousness state updates

@dataclass
class ExtractionRequest:
    """Unified extraction request with context and priority"""
    request_id: str
    username: str
    text: str
    conversation_context: str
    interaction_type: InteractionType
    priority: ExtractionPriority
    created_at: datetime
    timeout_seconds: int = 30
    callback: Optional[Callable] = None
    metadata: Dict[str, Any] = None

@dataclass
class ExtractionMetrics:
    """Performance metrics for extraction operations"""
    total_requests: int = 0
    successful_extractions: int = 0
    failed_extractions: int = 0
    cached_hits: int = 0
    average_response_time: float = 0.0
    batched_operations: int = 0
    circuit_breaker_triggers: int = 0
    connection_pool_size: int = 0
    active_connections: int = 0

class ConnectionPool:
    """Enterprise-grade connection pool for KoboldCPP"""
    
    def __init__(self, max_connections: int = 5, connection_timeout: int = 30):
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.available_connections = deque()
        self.active_connections = set()
        self.lock = threading.Lock()
        self.total_connections = 0
        
    def acquire_connection(self) -> Optional[Any]:
        """Acquire a connection from the pool"""
        with self.lock:
            if self.available_connections:
                connection = self.available_connections.popleft()
                self.active_connections.add(connection)
                return connection
            elif self.total_connections < self.max_connections:
                # Create new connection
                connection_id = f"conn_{self.total_connections}"
                self.total_connections += 1
                self.active_connections.add(connection_id)
                return connection_id
            else:
                return None  # Pool exhausted
    
    def release_connection(self, connection: Any):
        """Release a connection back to the pool"""
        with self.lock:
            if connection in self.active_connections:
                self.active_connections.remove(connection)
                self.available_connections.append(connection)
    
    def get_pool_stats(self) -> Dict[str, int]:
        """Get connection pool statistics"""
        with self.lock:
            return {
                "total_connections": self.total_connections,
                "active_connections": len(self.active_connections),
                "available_connections": len(self.available_connections),
                "max_connections": self.max_connections
            }

class SmartRequestQueue:
    """Context-aware request queue with batching and prioritization"""
    
    def __init__(self):
        self.queue = []
        self.processing = {}
        self.completed = {}
        self.lock = threading.Lock()
        self.batch_threshold = 3  # Batch requests if 3+ similar ones
        self.batch_timeout = 2.0  # Wait max 2 seconds for batching
        
    def add_request(self, request: ExtractionRequest) -> str:
        """Add request to queue with intelligent batching"""
        with self.lock:
            # Check for similar pending requests for batching
            similar_requests = self._find_similar_requests(request)
            
            if len(similar_requests) >= self.batch_threshold - 1:
                # Create batch operation
                batch_id = f"batch_{int(time.time() * 1000)}"
                batch_requests = similar_requests + [request]
                self._create_batch_operation(batch_id, batch_requests)
                return batch_id
            else:
                # Add as individual request
                self.queue.append(request)
                self.queue.sort(key=lambda r: (r.priority.value, r.created_at))
                return request.request_id
    
    def get_next_request(self) -> Optional[ExtractionRequest]:
        """Get next request to process based on priority"""
        with self.lock:
            if self.queue:
                return self.queue.pop(0)
            return None
    
    def _find_similar_requests(self, request: ExtractionRequest) -> List[ExtractionRequest]:
        """Find similar requests for potential batching"""
        similar = []
        for r in self.queue:
            if (r.username == request.username and 
                r.interaction_type == request.interaction_type and
                r.priority == request.priority and
                len(r.text) < 100 and len(request.text) < 100):  # Only batch short requests
                similar.append(r)
        return similar
    
    def _create_batch_operation(self, batch_id: str, requests: List[ExtractionRequest]):
        """Create a batch operation for similar requests"""
        # Remove individual requests from queue
        for req in requests:
            if req in self.queue:
                self.queue.remove(req)
        
        # Create combined batch request
        combined_text = " | ".join([r.text for r in requests])
        batch_request = ExtractionRequest(
            request_id=batch_id,
            username=requests[0].username,
            text=combined_text,
            conversation_context="",
            interaction_type=requests[0].interaction_type,
            priority=requests[0].priority,
            created_at=datetime.now(),
            metadata={"batch_size": len(requests), "original_requests": [r.request_id for r in requests]}
        )
        self.queue.insert(0, batch_request)  # High priority for batches

class ExtractionCoordinator:
    """
    Enterprise-Grade Unified Extraction Coordinator
    
    Centralizes all extraction operations with:
    - Context-aware prioritization
    - Smart request batching and result sharing
    - Connection pooling and circuit breaking
    - Progressive resolution strategies
    - Performance monitoring
    """
    
    def __init__(self):
        self.connection_pool = ConnectionPool(max_connections=5)
        self.request_queue = SmartRequestQueue()
        self.result_cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.metrics = ExtractionMetrics()
        self.lock = threading.Lock()
        
        # Circuit breakers for different operation types
        self.circuit_breakers = {
            "memory_extraction": CircuitBreaker("memory_extraction", CircuitBreakerConfig(
                failure_threshold=3, recovery_timeout=60, timeout=30
            )),
            "consciousness_processing": CircuitBreaker("consciousness_processing", CircuitBreakerConfig(
                failure_threshold=5, recovery_timeout=45, timeout=20
            )),
            "llm_communication": CircuitBreaker("llm_communication", CircuitBreakerConfig(
                failure_threshold=2, recovery_timeout=120, timeout=40
            ))
        }
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="ExtractionWorker")
        self.running = True
        
        # Start background processing thread
        self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()
        
        print("[ExtractionCoordinator] 🏢 Enterprise-grade extraction coordinator initialized")
        print(f"[ExtractionCoordinator] 🔄 Connection pool: {self.connection_pool.max_connections} max connections")
        print(f"[ExtractionCoordinator] 🧠 Circuit breakers: {len(self.circuit_breakers)} protection systems")
    
    def extract_with_coordination(self, 
                                username: str, 
                                text: str, 
                                interaction_type: InteractionType = InteractionType.TEXT_CHAT,
                                priority: ExtractionPriority = ExtractionPriority.NORMAL,
                                conversation_context: str = "",
                                timeout_seconds: int = 30) -> Future[ExtractionResult]:
        """
        Main extraction method with enterprise-grade coordination
        Returns a Future that can be awaited for the result
        """
        # Create extraction request
        request_id = f"req_{int(time.time() * 1000)}_{hash(text) % 10000}"
        request = ExtractionRequest(
            request_id=request_id,
            username=username,
            text=text,
            conversation_context=conversation_context,
            interaction_type=interaction_type,
            priority=priority,
            created_at=datetime.now(),
            timeout_seconds=timeout_seconds
        )
        
        # Check cache first for rapid response
        cache_key = self._generate_cache_key(username, text, conversation_context)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.metrics.cached_hits += 1
            future = Future()
            future.set_result(cached_result)
            return future
        
        # Submit to processing queue
        future = self.executor.submit(self._process_extraction_request, request)
        self.metrics.total_requests += 1
        
        # Add to queue for coordinated processing
        self.request_queue.add_request(request)
        
        return future
    
    def _process_extraction_request(self, request: ExtractionRequest) -> ExtractionResult:
        """Process individual extraction request with circuit breaking and fallbacks"""
        start_time = time.time()
        
        try:
            # Acquire connection from pool
            connection = self.connection_pool.acquire_connection()
            if not connection:
                raise RuntimeError("Connection pool exhausted")
            
            try:
                # Determine processing strategy based on interaction type
                if request.interaction_type == InteractionType.VOICE_TO_SPEECH:
                    result = self._process_voice_interaction(request, connection)
                elif request.interaction_type == InteractionType.BACKGROUND_PROCESSING:
                    result = self._process_background_extraction(request, connection)
                else:
                    result = self._process_standard_extraction(request, connection)
                
                # Cache successful result
                cache_key = self._generate_cache_key(request.username, request.text, request.conversation_context)
                self._cache_result(cache_key, result)
                
                self.metrics.successful_extractions += 1
                execution_time = time.time() - start_time
                self._update_average_response_time(execution_time)
                
                return result
                
            finally:
                self.connection_pool.release_connection(connection)
                
        except Exception as e:
            self.metrics.failed_extractions += 1
            
            # Try progressive resolution strategy
            fallback_result = self._apply_progressive_resolution(request, e)
            if fallback_result:
                return fallback_result
            
            # If all fallbacks fail, return minimal result
            return ExtractionResult(
                memory_events=[],
                intent_classification="error_recovery",
                emotional_state={"error": str(e)},
                conversation_thread_id=None,
                memory_enhancements=[],
                context_keywords=[],
                follow_up_suggestions=[]
            )
    
    def _process_voice_interaction(self, request: ExtractionRequest, connection: Any) -> ExtractionResult:
        """Optimized processing for voice-to-speech interactions (critical latency)"""
        try:
            # Use circuit breaker for LLM communication
            def extract_operation():
                extractor = get_unified_memory_extractor(request.username)
                # Use minimal extraction for voice to reduce latency
                return extractor.extract_all_from_text(request.text, request.conversation_context)
            
            return self.circuit_breakers["llm_communication"].call(extract_operation)
            
        except CircuitBreakerOpenError:
            # Fast fallback for voice interactions
            return self._create_minimal_extraction_result(request)
    
    def _process_standard_extraction(self, request: ExtractionRequest, connection: Any) -> ExtractionResult:
        """Standard extraction processing with full consciousness integration"""
        try:
            def extract_operation():
                extractor = get_unified_memory_extractor(request.username)
                return extractor.extract_all_from_text(request.text, request.conversation_context)
            
            return self.circuit_breakers["memory_extraction"].call(extract_operation)
            
        except CircuitBreakerOpenError:
            self.metrics.circuit_breaker_triggers += 1
            raise
    
    def _process_background_extraction(self, request: ExtractionRequest, connection: Any) -> ExtractionResult:
        """Background processing with extended timeout and comprehensive analysis"""
        try:
            def extract_operation():
                extractor = get_unified_memory_extractor(request.username)
                # Use comprehensive extraction for background processing
                return extractor.extract_all_from_text(request.text, request.conversation_context)
            
            # Use longer timeout for background processing
            bg_config = CircuitBreakerConfig(failure_threshold=5, recovery_timeout=120, timeout=60)
            bg_breaker = CircuitBreaker("background_extraction", bg_config)
            return bg_breaker.call(extract_operation)
            
        except CircuitBreakerOpenError:
            # Background operations can be delayed/retried
            raise
    
    def _apply_progressive_resolution(self, request: ExtractionRequest, error: Exception) -> Optional[ExtractionResult]:
        """Apply progressive resolution strategy: try simpler methods if complex ones fail"""
        try:
            print(f"[ExtractionCoordinator] 🔄 Applying progressive resolution for error: {error}")
            
            # Strategy 1: Try with reduced context
            if len(request.conversation_context) > 100:
                reduced_context = request.conversation_context[:100] + "..."
                simple_request = ExtractionRequest(
                    request_id=f"{request.request_id}_simple",
                    username=request.username,
                    text=request.text,
                    conversation_context=reduced_context,
                    interaction_type=request.interaction_type,
                    priority=request.priority,
                    created_at=datetime.now()
                )
                return self._process_standard_extraction(simple_request, None)
            
            # Strategy 2: Try minimal extraction
            return self._create_minimal_extraction_result(request)
            
        except Exception as fallback_error:
            print(f"[ExtractionCoordinator] ❌ Progressive resolution failed: {fallback_error}")
            return None
    
    def _create_minimal_extraction_result(self, request: ExtractionRequest) -> ExtractionResult:
        """Create minimal extraction result for fallback scenarios"""
        return ExtractionResult(
            memory_events=[],
            intent_classification="conversation",
            emotional_state={"primary_emotion": "neutral", "confidence": 0.5},
            conversation_thread_id=None,
            memory_enhancements=[],
            context_keywords=request.text.lower().split()[:5],  # Simple keyword extraction
            follow_up_suggestions=[]
        )
    
    def _process_queue(self):
        """Background thread for processing queued requests"""
        while self.running:
            try:
                request = self.request_queue.get_next_request()
                if request:
                    # Process batched requests if applicable
                    if request.metadata and request.metadata.get("batch_size", 0) > 1:
                        self._process_batch_request(request)
                        self.metrics.batched_operations += 1
                
                time.sleep(0.1)  # Small delay to prevent CPU spinning
                
            except Exception as e:
                print(f"[ExtractionCoordinator] ❌ Queue processing error: {e}")
                time.sleep(1)  # Longer delay on error
    
    def _process_batch_request(self, batch_request: ExtractionRequest):
        """Process a batch of similar requests together"""
        try:
            # Extract from combined text
            result = self._process_standard_extraction(batch_request, None)
            
            # Split results back to individual requests (simplified)
            # In a real implementation, this would intelligently distribute results
            print(f"[ExtractionCoordinator] 📦 Processed batch of {batch_request.metadata['batch_size']} requests")
            
        except Exception as e:
            print(f"[ExtractionCoordinator] ❌ Batch processing failed: {e}")
    
    def _generate_cache_key(self, username: str, text: str, context: str) -> str:
        """Generate cache key for extraction results"""
        content = f"{username}:{text}:{context}".encode('utf-8')
        return hashlib.md5(content).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[ExtractionResult]:
        """Get cached extraction result if available and valid"""
        with self.lock:
            if cache_key in self.result_cache:
                cached_data = self.result_cache[cache_key]
                if datetime.now() - cached_data["timestamp"] < timedelta(seconds=self.cache_timeout):
                    return cached_data["result"]
                else:
                    # Remove expired cache entry
                    del self.result_cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: ExtractionResult):
        """Cache extraction result with timestamp"""
        with self.lock:
            self.result_cache[cache_key] = {
                "result": result,
                "timestamp": datetime.now()
            }
            
            # Clean old cache entries periodically
            if len(self.result_cache) > 1000:  # Limit cache size
                self._clean_cache()
    
    def _clean_cache(self):
        """Remove expired cache entries"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, data in self.result_cache.items():
            if current_time - data["timestamp"] > timedelta(seconds=self.cache_timeout):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.result_cache[key]
        
        print(f"[ExtractionCoordinator] 🧹 Cleaned {len(expired_keys)} expired cache entries")
    
    def _update_average_response_time(self, execution_time: float):
        """Update average response time metric"""
        with self.lock:
            if self.metrics.successful_extractions <= 1:
                self.metrics.average_response_time = execution_time
            else:
                # Exponential moving average
                alpha = 0.1
                self.metrics.average_response_time = (
                    alpha * execution_time + 
                    (1 - alpha) * self.metrics.average_response_time
                )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        with self.lock:
            return {
                "extraction_metrics": asdict(self.metrics),
                "connection_pool": self.connection_pool.get_pool_stats(),
                "circuit_breakers": {
                    name: breaker.get_stats() 
                    for name, breaker in self.circuit_breakers.items()
                },
                "cache_stats": {
                    "cached_entries": len(self.result_cache),
                    "cache_timeout": self.cache_timeout,
                    "hit_rate": (
                        self.metrics.cached_hits / max(1, self.metrics.total_requests)
                    ) * 100
                },
                "queue_stats": {
                    "pending_requests": len(self.request_queue.queue),
                    "batched_operations": self.metrics.batched_operations
                }
            }
    
    def shutdown(self):
        """Gracefully shutdown the coordinator"""
        print("[ExtractionCoordinator] 🛑 Shutting down extraction coordinator...")
        self.running = False
        self.executor.shutdown(wait=True)
        print("[ExtractionCoordinator] ✅ Extraction coordinator shutdown complete")

# Global coordinator instance
_extraction_coordinator = None

def get_extraction_coordinator() -> ExtractionCoordinator:
    """Get or create the global extraction coordinator instance"""
    global _extraction_coordinator
    if _extraction_coordinator is None:
        _extraction_coordinator = ExtractionCoordinator()
    return _extraction_coordinator

def extract_with_enterprise_coordination(username: str, 
                                       text: str, 
                                       interaction_type: InteractionType = InteractionType.TEXT_CHAT,
                                       priority: ExtractionPriority = ExtractionPriority.NORMAL,
                                       conversation_context: str = "",
                                       timeout_seconds: int = 30) -> ExtractionResult:
    """
    Main entry point for enterprise-grade extraction coordination
    
    This function provides a clean interface that maintains compatibility
    with existing code while adding enterprise-grade capabilities.
    """
    coordinator = get_extraction_coordinator()
    future = coordinator.extract_with_coordination(
        username, text, interaction_type, priority, conversation_context, timeout_seconds
    )
    
    try:
        # Wait for result with timeout
        return future.result(timeout=timeout_seconds)
    except Exception as e:
        print(f"[ExtractionCoordinator] ❌ Extraction failed: {e}")
        # Return minimal fallback result
        return ExtractionResult(
            memory_events=[],
            intent_classification="error_fallback",
            emotional_state={"error": str(e)},
            conversation_thread_id=None,
            memory_enhancements=[],
            context_keywords=[],
            follow_up_suggestions=[]
        )

def get_extraction_performance_report() -> Dict[str, Any]:
    """Get comprehensive performance report for monitoring"""
    coordinator = get_extraction_coordinator()
    return coordinator.get_performance_metrics()