"""
Performance Optimization Module
Created: 2025-01-08
Purpose: Implements circuit breaker patterns, connection pooling, caching, and batching optimizations

Key Features:
- Enhanced circuit breaker pattern for extraction stability
- Advanced connection pooling for KoboldCPP efficiency
- Intelligent caching and batching for related memory operations
- Performance monitoring and adaptive optimization
"""

import time
import threading
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor, Future

class OptimizationStrategy(Enum):
    """Different optimization strategies"""
    SPEED_OPTIMIZED = "speed_optimized"          # Prioritize response time
    RESOURCE_OPTIMIZED = "resource_optimized"    # Conserve resources
    BALANCED = "balanced"                        # Balance speed and resources
    QUALITY_OPTIMIZED = "quality_optimized"     # Prioritize accuracy over speed

@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    circuit_breaker_activations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    average_response_time: float = 0.0
    total_bytes_processed: int = 0
    connection_pool_efficiency: float = 0.0
    batch_operations_count: int = 0
    
class AdaptiveCircuitBreaker:
    """Advanced circuit breaker with adaptive thresholds"""
    
    def __init__(self, name: str, failure_threshold: int = 5, 
                 recovery_timeout: int = 60, success_threshold: int = 3,
                 adaptive_mode: bool = True):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.adaptive_mode = adaptive_mode
        
        # State tracking
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.performance_history = deque(maxlen=100)
        
        # Adaptive parameters
        self.adaptive_threshold_min = 3
        self.adaptive_threshold_max = 15
        self.performance_window_size = 20
        
        self.lock = threading.Lock()
        
        print(f"[AdaptiveCircuitBreaker] 🔧 Initialized circuit breaker: {name}")
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        with self.lock:
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                    print(f"[AdaptiveCircuitBreaker] 🔄 {self.name} entering HALF_OPEN state")
                else:
                    raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is OPEN")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            self._record_success(execution_time)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._record_failure(execution_time)
            raise e
    
    def _record_success(self, execution_time: float):
        """Record successful operation"""
        with self.lock:
            self.success_count += 1
            self.performance_history.append({'success': True, 'time': execution_time, 'timestamp': datetime.now()})
            
            if self.state == "HALF_OPEN" and self.success_count >= self.success_threshold:
                self.state = "CLOSED"
                self.failure_count = 0
                print(f"[AdaptiveCircuitBreaker] ✅ {self.name} circuit breaker CLOSED (recovered)")
            
            # Adaptive threshold adjustment
            if self.adaptive_mode:
                self._adjust_adaptive_threshold()
    
    def _record_failure(self, execution_time: float):
        """Record failed operation"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            self.performance_history.append({'success': False, 'time': execution_time, 'timestamp': datetime.now()})
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                self.success_count = 0
                print(f"[AdaptiveCircuitBreaker] ❌ {self.name} circuit breaker OPEN (too many failures)")
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker"""
        if not self.last_failure_time:
            return True
        
        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.recovery_timeout
    
    def _adjust_adaptive_threshold(self):
        """Adjust failure threshold based on recent performance"""
        if len(self.performance_history) < self.performance_window_size:
            return
        
        recent_operations = list(self.performance_history)[-self.performance_window_size:]
        success_rate = sum(1 for op in recent_operations if op['success']) / len(recent_operations)
        
        # Adjust threshold based on success rate
        if success_rate > 0.95:  # Very high success rate
            self.failure_threshold = min(self.adaptive_threshold_max, self.failure_threshold + 1)
        elif success_rate < 0.80:  # Low success rate
            self.failure_threshold = max(self.adaptive_threshold_min, self.failure_threshold - 1)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        with self.lock:
            recent_performance = list(self.performance_history)[-20:] if self.performance_history else []
            recent_success_rate = (sum(1 for op in recent_performance if op['success']) / 
                                 len(recent_performance)) if recent_performance else 0
            
            return {
                'name': self.name,
                'state': self.state,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'failure_threshold': self.failure_threshold,
                'recent_success_rate': recent_success_rate,
                'total_operations': len(self.performance_history),
                'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None
            }

class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class IntelligentConnectionPool:
    """Enhanced connection pool with intelligent management"""
    
    def __init__(self, name: str, max_connections: int = 10, 
                 min_connections: int = 2, connection_timeout: int = 30,
                 health_check_interval: int = 60):
        self.name = name
        self.max_connections = max_connections
        self.min_connections = min_connections
        self.connection_timeout = connection_timeout
        self.health_check_interval = health_check_interval
        
        # Connection management
        self.available_connections = deque()
        self.active_connections = {}
        self.connection_stats = {}
        self.total_connections_created = 0
        
        # Performance tracking
        self.usage_stats = {
            'total_acquisitions': 0,
            'total_releases': 0,
            'wait_times': deque(maxlen=100),
            'connection_lifetimes': deque(maxlen=100)
        }
        
        self.lock = threading.Lock()
        
        # Initialize minimum connections
        self._initialize_min_connections()
        
        # Start health check thread
        self.health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_check_thread.start()
        
        print(f"[IntelligentConnectionPool] 🏊 Initialized connection pool: {name} ({min_connections}-{max_connections} connections)")
    
    def acquire_connection(self, timeout: Optional[float] = None) -> Optional[Any]:
        """Acquire a connection from the pool"""
        start_time = time.time()
        
        with self.lock:
            self.usage_stats['total_acquisitions'] += 1
            
            # Try to get available connection
            if self.available_connections:
                connection_id = self.available_connections.popleft()
                self.active_connections[connection_id] = {
                    'acquired_at': datetime.now(),
                    'usage_count': self.connection_stats.get(connection_id, {}).get('usage_count', 0) + 1
                }
                
                wait_time = time.time() - start_time
                self.usage_stats['wait_times'].append(wait_time)
                
                print(f"[IntelligentConnectionPool] 📞 Acquired existing connection {connection_id}")
                return connection_id
            
            # Create new connection if under limit
            elif len(self.active_connections) < self.max_connections:
                connection_id = self._create_connection()
                if connection_id:
                    self.active_connections[connection_id] = {
                        'acquired_at': datetime.now(),
                        'usage_count': 1
                    }
                    
                    wait_time = time.time() - start_time
                    self.usage_stats['wait_times'].append(wait_time)
                    
                    return connection_id
            
            # Pool exhausted
            print(f"[IntelligentConnectionPool] ⚠️ Connection pool {self.name} exhausted")
            return None
    
    def release_connection(self, connection_id: Any):
        """Release a connection back to the pool"""
        with self.lock:
            if connection_id in self.active_connections:
                acquired_info = self.active_connections[connection_id]
                lifetime = (datetime.now() - acquired_info['acquired_at']).total_seconds()
                
                # Update connection stats
                if connection_id not in self.connection_stats:
                    self.connection_stats[connection_id] = {
                        'created_at': datetime.now(),
                        'usage_count': 0,
                        'total_lifetime': 0
                    }
                
                self.connection_stats[connection_id]['usage_count'] = acquired_info['usage_count']
                self.connection_stats[connection_id]['total_lifetime'] += lifetime
                
                # Move to available pool
                del self.active_connections[connection_id]
                self.available_connections.append(connection_id)
                
                self.usage_stats['total_releases'] += 1
                self.usage_stats['connection_lifetimes'].append(lifetime)
                
                print(f"[IntelligentConnectionPool] 📤 Released connection {connection_id} (lifetime: {lifetime:.2f}s)")
    
    def _create_connection(self) -> Optional[str]:
        """Create a new connection"""
        self.total_connections_created += 1
        connection_id = f"{self.name}_conn_{self.total_connections_created}"
        
        # Initialize connection stats
        self.connection_stats[connection_id] = {
            'created_at': datetime.now(),
            'usage_count': 0,
            'total_lifetime': 0
        }
        
        print(f"[IntelligentConnectionPool] 🆕 Created new connection {connection_id}")
        return connection_id
    
    def _initialize_min_connections(self):
        """Initialize minimum number of connections"""
        for _ in range(self.min_connections):
            connection_id = self._create_connection()
            if connection_id:
                self.available_connections.append(connection_id)
    
    def _health_check_loop(self):
        """Background health check for connections"""
        while True:
            try:
                time.sleep(self.health_check_interval)
                self._perform_health_check()
            except Exception as e:
                print(f"[IntelligentConnectionPool] ❌ Health check error: {e}")
    
    def _perform_health_check(self):
        """Perform health check on connections"""
        with self.lock:
            current_time = datetime.now()
            
            # Check for connections that have been idle too long
            stale_connections = []
            for connection_id in list(self.available_connections):
                stats = self.connection_stats.get(connection_id, {})
                if stats.get('created_at'):
                    idle_time = (current_time - stats['created_at']).total_seconds()
                    if idle_time > self.connection_timeout * 2:  # Double timeout for staleness
                        stale_connections.append(connection_id)
            
            # Remove stale connections (but keep minimum)
            current_total = len(self.available_connections) + len(self.active_connections)
            for connection_id in stale_connections:
                if current_total > self.min_connections:
                    self.available_connections.remove(connection_id)
                    del self.connection_stats[connection_id]
                    current_total -= 1
                    print(f"[IntelligentConnectionPool] 🗑️ Removed stale connection {connection_id}")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        with self.lock:
            total_connections = len(self.available_connections) + len(self.active_connections)
            
            # Calculate efficiency metrics
            efficiency = 0.0
            if self.usage_stats['total_acquisitions'] > 0:
                efficiency = self.usage_stats['total_releases'] / self.usage_stats['total_acquisitions']
            
            avg_wait_time = (sum(self.usage_stats['wait_times']) / len(self.usage_stats['wait_times']) 
                           if self.usage_stats['wait_times'] else 0)
            
            avg_lifetime = (sum(self.usage_stats['connection_lifetimes']) / len(self.usage_stats['connection_lifetimes'])
                          if self.usage_stats['connection_lifetimes'] else 0)
            
            return {
                'name': self.name,
                'total_connections': total_connections,
                'available_connections': len(self.available_connections),
                'active_connections': len(self.active_connections),
                'max_connections': self.max_connections,
                'min_connections': self.min_connections,
                'efficiency': efficiency,
                'total_acquisitions': self.usage_stats['total_acquisitions'],
                'total_releases': self.usage_stats['total_releases'],
                'average_wait_time': avg_wait_time,
                'average_connection_lifetime': avg_lifetime,
                'total_connections_created': self.total_connections_created
            }

class IntelligentCache:
    """Intelligent caching system with adaptive policies"""
    
    def __init__(self, name: str, max_size: int = 1000, default_ttl: int = 300,
                 eviction_policy: str = "LRU"):
        self.name = name
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.eviction_policy = eviction_policy
        
        # Cache storage
        self.cache = {}
        self.access_times = {}
        self.access_counts = {}
        self.insertion_order = deque()
        
        # Performance metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        self.lock = threading.Lock()
        
        print(f"[IntelligentCache] 📦 Initialized cache: {name} (max_size: {max_size}, ttl: {default_ttl}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        with self.lock:
            if key in self.cache:
                item, expiry_time = self.cache[key]
                
                # Check if expired
                if time.time() > expiry_time:
                    self._remove_key(key)
                    self.misses += 1
                    return None
                
                # Update access info
                self.access_times[key] = time.time()
                self.access_counts[key] = self.access_counts.get(key, 0) + 1
                self.hits += 1
                
                return item
            else:
                self.misses += 1
                return None
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Put item in cache"""
        with self.lock:
            if ttl is None:
                ttl = self.default_ttl
            
            expiry_time = time.time() + ttl
            current_time = time.time()
            
            # Check if we need to evict
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_item()
            
            # Add/update item
            self.cache[key] = (value, expiry_time)
            self.access_times[key] = current_time
            self.access_counts[key] = self.access_counts.get(key, 0) + 1
            
            if key not in self.insertion_order:
                self.insertion_order.append(key)
            
            return True
    
    def _evict_item(self):
        """Evict item based on eviction policy"""
        if not self.cache:
            return
        
        if self.eviction_policy == "LRU":
            # Remove least recently used
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            self._remove_key(oldest_key)
        elif self.eviction_policy == "LFU":
            # Remove least frequently used
            least_used_key = min(self.access_counts.keys(), key=lambda k: self.access_counts[k])
            self._remove_key(least_used_key)
        elif self.eviction_policy == "FIFO":
            # Remove first inserted
            if self.insertion_order:
                oldest_key = self.insertion_order.popleft()
                self._remove_key(oldest_key)
        
        self.evictions += 1
    
    def _remove_key(self, key: str):
        """Remove key from all tracking structures"""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]
        if key in self.access_counts:
            del self.access_counts[key]
        if key in self.insertion_order:
            self.insertion_order.remove(key)
    
    def clear_expired(self):
        """Clear expired items"""
        with self.lock:
            current_time = time.time()
            expired_keys = []
            
            for key, (_, expiry_time) in self.cache.items():
                if current_time > expiry_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_key(key)
            
            if expired_keys:
                print(f"[IntelligentCache] 🧹 Cleared {len(expired_keys)} expired items from {self.name}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            
            return {
                'name': self.name,
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'hit_rate': hit_rate,
                'utilization': len(self.cache) / self.max_size
            }

class BatchProcessor:
    """Intelligent batch processor for related operations"""
    
    def __init__(self, name: str, batch_size: int = 5, batch_timeout: float = 2.0):
        self.name = name
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        
        # Batch management
        self.pending_operations = []
        self.batch_groups = defaultdict(list)
        self.batch_futures = {}
        
        # Performance tracking
        self.total_batches_processed = 0
        self.total_operations_batched = 0
        self.batch_efficiency_scores = deque(maxlen=100)
        
        self.lock = threading.Lock()
        
        # Start batch processing thread
        self.processing_thread = threading.Thread(target=self._process_batches, daemon=True)
        self.processing_thread.start()
        
        print(f"[BatchProcessor] 📦 Initialized batch processor: {name} (size: {batch_size}, timeout: {batch_timeout}s)")
    
    def add_operation(self, operation_id: str, operation_data: Dict[str, Any], 
                     batch_key: str, processor_func: Callable) -> Future:
        """Add operation to batch queue"""
        with self.lock:
            future = Future()
            
            operation = {
                'id': operation_id,
                'data': operation_data,
                'batch_key': batch_key,
                'processor_func': processor_func,
                'future': future,
                'timestamp': time.time()
            }
            
            self.pending_operations.append(operation)
            self.batch_groups[batch_key].append(operation)
            
            # Check if we should process this batch
            if len(self.batch_groups[batch_key]) >= self.batch_size:
                self._process_batch_group(batch_key)
            
            return future
    
    def _process_batches(self):
        """Background thread to process batches"""
        while True:
            try:
                time.sleep(0.5)  # Check every 500ms
                self._check_batch_timeouts()
            except Exception as e:
                print(f"[BatchProcessor] ❌ Batch processing error: {e}")
    
    def _check_batch_timeouts(self):
        """Check for batches that have timed out"""
        with self.lock:
            current_time = time.time()
            timeout_batches = []
            
            for batch_key, operations in self.batch_groups.items():
                if operations:
                    oldest_operation = min(operations, key=lambda op: op['timestamp'])
                    if current_time - oldest_operation['timestamp'] >= self.batch_timeout:
                        timeout_batches.append(batch_key)
            
            for batch_key in timeout_batches:
                self._process_batch_group(batch_key)
    
    def _process_batch_group(self, batch_key: str):
        """Process a specific batch group"""
        if batch_key not in self.batch_groups or not self.batch_groups[batch_key]:
            return
        
        operations = self.batch_groups[batch_key].copy()
        self.batch_groups[batch_key].clear()
        
        # Remove from pending operations
        self.pending_operations = [op for op in self.pending_operations 
                                 if op['batch_key'] != batch_key or op not in operations]
        
        print(f"[BatchProcessor] 📦 Processing batch {batch_key} with {len(operations)} operations")
        
        # Process batch in a separate thread
        threading.Thread(
            target=self._execute_batch,
            args=(batch_key, operations),
            daemon=True
        ).start()
    
    def _execute_batch(self, batch_key: str, operations: List[Dict[str, Any]]):
        """Execute a batch of operations"""
        start_time = time.time()
        
        try:
            # Group operations by processor function
            processor_groups = defaultdict(list)
            for operation in operations:
                processor_func = operation['processor_func']
                processor_groups[processor_func].append(operation)
            
            # Execute each processor group
            for processor_func, ops in processor_groups.items():
                try:
                    # Prepare batch data
                    batch_data = [op['data'] for op in ops]
                    
                    # Execute batch processor
                    results = processor_func(batch_data)
                    
                    # Set results for individual futures
                    for i, operation in enumerate(ops):
                        if i < len(results):
                            operation['future'].set_result(results[i])
                        else:
                            operation['future'].set_exception(Exception("Batch result missing"))
                
                except Exception as e:
                    # Set exception for all operations in this group
                    for operation in ops:
                        operation['future'].set_exception(e)
        
        except Exception as e:
            # Set exception for all operations
            for operation in operations:
                operation['future'].set_exception(e)
        
        finally:
            # Update metrics
            processing_time = time.time() - start_time
            efficiency_score = len(operations) / processing_time if processing_time > 0 else 0
            
            with self.lock:
                self.total_batches_processed += 1
                self.total_operations_batched += len(operations)
                self.batch_efficiency_scores.append(efficiency_score)
    
    def get_batch_stats(self) -> Dict[str, Any]:
        """Get batch processing statistics"""
        with self.lock:
            avg_efficiency = (sum(self.batch_efficiency_scores) / len(self.batch_efficiency_scores)
                            if self.batch_efficiency_scores else 0)
            
            return {
                'name': self.name,
                'total_batches_processed': self.total_batches_processed,
                'total_operations_batched': self.total_operations_batched,
                'pending_operations': len(self.pending_operations),
                'active_batch_groups': len([g for g in self.batch_groups.values() if g]),
                'average_efficiency': avg_efficiency,
                'batch_size': self.batch_size,
                'batch_timeout': self.batch_timeout
            }

class PerformanceOptimizer:
    """Main performance optimization coordinator"""
    
    def __init__(self, strategy: OptimizationStrategy = OptimizationStrategy.BALANCED):
        self.strategy = strategy
        self.metrics = PerformanceMetrics()
        
        # Initialize components
        self.circuit_breakers = {}
        self.connection_pools = {}
        self.caches = {}
        self.batch_processors = {}
        
        # Performance monitoring
        self.performance_history = deque(maxlen=1000)
        self.optimization_adjustments = []
        
        self.lock = threading.Lock()
        
        # Initialize default components
        self._initialize_default_components()
        
        print("[PerformanceOptimizer] 🚀 Performance optimization system initialized")
        print(f"[PerformanceOptimizer] 📊 Strategy: {strategy.value}")
    
    def _initialize_default_components(self):
        """Initialize default performance components"""
        # Default circuit breakers
        self.register_circuit_breaker("memory_extraction", 
                                    failure_threshold=5, recovery_timeout=60)
        self.register_circuit_breaker("llm_communication", 
                                    failure_threshold=3, recovery_timeout=120)
        
        # Default connection pool
        self.register_connection_pool("kobold_cpp", 
                                    max_connections=8, min_connections=2)
        
        # Default caches
        self.register_cache("extraction_results", max_size=500, default_ttl=300)
        self.register_cache("conversation_context", max_size=200, default_ttl=600)
        
        # Default batch processor
        self.register_batch_processor("memory_operations", batch_size=5, batch_timeout=2.0)
    
    def register_circuit_breaker(self, name: str, failure_threshold: int = 5,
                               recovery_timeout: int = 60, success_threshold: int = 3) -> AdaptiveCircuitBreaker:
        """Register a new circuit breaker"""
        circuit_breaker = AdaptiveCircuitBreaker(
            name, failure_threshold, recovery_timeout, success_threshold, True
        )
        self.circuit_breakers[name] = circuit_breaker
        print(f"[PerformanceOptimizer] 🔧 Registered circuit breaker: {name}")
        return circuit_breaker
    
    def register_connection_pool(self, name: str, max_connections: int = 10,
                               min_connections: int = 2, connection_timeout: int = 30) -> IntelligentConnectionPool:
        """Register a new connection pool"""
        connection_pool = IntelligentConnectionPool(
            name, max_connections, min_connections, connection_timeout
        )
        self.connection_pools[name] = connection_pool
        print(f"[PerformanceOptimizer] 🏊 Registered connection pool: {name}")
        return connection_pool
    
    def register_cache(self, name: str, max_size: int = 1000, default_ttl: int = 300,
                      eviction_policy: str = "LRU") -> IntelligentCache:
        """Register a new cache"""
        cache = IntelligentCache(name, max_size, default_ttl, eviction_policy)
        self.caches[name] = cache
        print(f"[PerformanceOptimizer] 📦 Registered cache: {name}")
        return cache
    
    def register_batch_processor(self, name: str, batch_size: int = 5,
                               batch_timeout: float = 2.0) -> BatchProcessor:
        """Register a new batch processor"""
        batch_processor = BatchProcessor(name, batch_size, batch_timeout)
        self.batch_processors[name] = batch_processor
        print(f"[PerformanceOptimizer] 📦 Registered batch processor: {name}")
        return batch_processor
    
    def get_comprehensive_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        with self.lock:
            # Collect stats from all components
            circuit_breaker_stats = {name: cb.get_stats() for name, cb in self.circuit_breakers.items()}
            connection_pool_stats = {name: cp.get_pool_stats() for name, cp in self.connection_pools.items()}
            cache_stats = {name: cache.get_cache_stats() for name, cache in self.caches.items()}
            batch_processor_stats = {name: bp.get_batch_stats() for name, bp in self.batch_processors.items()}
            
            # Calculate overall metrics
            total_cache_hits = sum(cache.hits for cache in self.caches.values())
            total_cache_misses = sum(cache.misses for cache in self.caches.values())
            overall_cache_hit_rate = (total_cache_hits / (total_cache_hits + total_cache_misses) 
                                    if (total_cache_hits + total_cache_misses) > 0 else 0)
            
            return {
                'optimization_strategy': self.strategy.value,
                'overall_metrics': {
                    'cache_hit_rate': overall_cache_hit_rate,
                    'active_circuit_breakers': sum(1 for cb in self.circuit_breakers.values() if cb.state != "CLOSED"),
                    'total_connection_pools': len(self.connection_pools),
                    'total_caches': len(self.caches),
                    'total_batch_processors': len(self.batch_processors)
                },
                'circuit_breakers': circuit_breaker_stats,
                'connection_pools': connection_pool_stats,
                'caches': cache_stats,
                'batch_processors': batch_processor_stats,
                'performance_optimizations_applied': len(self.optimization_adjustments)
            }
    
    def optimize_for_latency(self):
        """Optimize all components for minimum latency"""
        print("[PerformanceOptimizer] ⚡ Optimizing for minimum latency...")
        
        # Adjust cache TTLs for faster access
        for cache in self.caches.values():
            cache.default_ttl = min(cache.default_ttl, 180)  # Reduce TTL
        
        # Reduce batch timeouts for faster processing
        for batch_processor in self.batch_processors.values():
            batch_processor.batch_timeout = min(batch_processor.batch_timeout, 1.0)
        
        # Increase connection pool sizes
        for pool in self.connection_pools.values():
            pool.max_connections = min(pool.max_connections * 2, 20)
        
        self.optimization_adjustments.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'latency_optimization',
            'description': 'Optimized all components for minimum latency'
        })
    
    def optimize_for_resources(self):
        """Optimize all components for resource conservation"""
        print("[PerformanceOptimizer] 💰 Optimizing for resource conservation...")
        
        # Reduce cache sizes
        for cache in self.caches.values():
            cache.max_size = max(cache.max_size // 2, 50)
        
        # Increase batch sizes for efficiency
        for batch_processor in self.batch_processors.values():
            batch_processor.batch_size = min(batch_processor.batch_size + 2, 10)
        
        # Reduce connection pool sizes
        for pool in self.connection_pools.values():
            pool.max_connections = max(pool.max_connections // 2, 3)
        
        self.optimization_adjustments.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'resource_optimization',
            'description': 'Optimized all components for resource conservation'
        })

# Global instance
_performance_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get the global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer

def optimize_for_extraction_performance():
    """Optimize system specifically for extraction performance"""
    optimizer = get_performance_optimizer()
    optimizer.optimize_for_latency()
    return optimizer.get_comprehensive_performance_report()

def get_performance_report():
    """Get comprehensive performance report"""
    optimizer = get_performance_optimizer()
    return optimizer.get_comprehensive_performance_report()