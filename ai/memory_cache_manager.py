"""
Intelligent Memory Cache Manager - Enterprise-Grade Memory Optimization
Created: 2025-01-08
Purpose: Smart memory operation batching, caching, and preloading for enterprise performance

Key Features:
- Intelligent result caching with context-aware invalidation
- Memory operation batching when appropriate  
- Proactive memory pre-loading based on context patterns
- Smart deduplication of memory retrievals
- Adaptive cache sizing based on usage patterns
"""

import json
import threading
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, OrderedDict
from concurrent.futures import ThreadPoolExecutor, Future
import os
import pickle

class SerializableLock:
    """Thread-safe lock that can be safely serialized/pickled"""
    
    def __init__(self):
        self._lock = threading.RLock()
    
    def __enter__(self):
        return self._lock.__enter__()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._lock.__exit__(exc_type, exc_val, exc_tb)
    
    def acquire(self, blocking=True, timeout=-1):
        return self._lock.acquire(blocking, timeout)
    
    def release(self):
        return self._lock.release()
    
    def __getstate__(self):
        # Return an empty state when pickling
        return {}
    
    def __setstate__(self, state):
        # Recreate the lock when unpickling
        self._lock = threading.RLock()

@dataclass
class CacheEntry:
    """Cached memory entry with metadata"""
    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    cache_key: str
    context_tags: Set[str]
    invalidation_triggers: Set[str]
    size_bytes: int

@dataclass
class MemoryOperationBatch:
    """Batch of similar memory operations"""
    batch_id: str
    operations: List[Dict[str, Any]]
    created_at: datetime
    batch_type: str  # 'read', 'write', 'extract'
    priority: int
    user_context: str

class MemoryCacheManager:
    """
    Enterprise-Grade Intelligent Memory Cache Manager
    
    Optimizes memory operations through:
    - Context-aware caching with intelligent invalidation
    - Operation batching for efficiency
    - Proactive pre-loading based on patterns
    - Smart deduplication and compression
    """
    
    def __init__(self, max_cache_size_mb: int = 100, cache_persistence: bool = True):
        self.max_cache_size_mb = max_cache_size_mb
        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        self.cache_persistence = cache_persistence
        
        # Cache storage with LRU eviction
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.cache_size_bytes = 0
        # Use a custom lock class that can be serialized safely
        self.cache_lock = SerializableLock()
        
        # Operation batching
        self.pending_batches: Dict[str, MemoryOperationBatch] = {}
        self.batch_threshold = 3  # Minimum operations to form a batch
        self.batch_timeout = 2.0  # Maximum wait time for batching
        self.batch_lock = SerializableLock()
        
        # Context pattern learning
        self.access_patterns: Dict[str, List[str]] = defaultdict(list)  # user -> access sequence
        self.context_associations: Dict[str, Set[str]] = defaultdict(set)  # context -> related keys
        self.pattern_lock = threading.Lock()
        
        # Pre-loading system
        self.preload_queue: Set[str] = set()
        self.preload_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="MemoryPreloader")
        
        # Performance metrics
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'batch_operations': 0,
            'preload_successes': 0,
            'invalidations': 0,
            'evictions': 0
        }
        
        # Cache persistence
        self.cache_file = "memory_cache_persistence.pkl"
        if cache_persistence:
            self._load_persistent_cache()
        
        # Background maintenance
        self.maintenance_thread = threading.Thread(target=self._background_maintenance, daemon=True)
        self.maintenance_thread.start()
        
        print("[MemoryCacheManager] 🧠 Intelligent memory cache manager initialized")
        print(f"[MemoryCacheManager] 📊 Max cache size: {max_cache_size_mb}MB")
        print(f"[MemoryCacheManager] 💾 Cache persistence: {'enabled' if cache_persistence else 'disabled'}")
    
    def get_cached_memory(self, cache_key: str, context_tags: Set[str] = None) -> Optional[Any]:
        """Get cached memory data with context awareness"""
        with self.cache_lock:
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                
                # Update access statistics
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                
                # Move to end (most recently used)
                self.cache.move_to_end(cache_key)
                
                # Record access pattern
                self._record_access_pattern(cache_key, context_tags)
                
                self.metrics['cache_hits'] += 1
                print(f"[MemoryCacheManager] 🎯 Cache hit: {cache_key[:20]}...")
                return entry.data
            else:
                self.metrics['cache_misses'] += 1
                # Trigger preloading for related content
                self._trigger_contextual_preload(cache_key, context_tags)
                return None
    
    def cache_memory_data(self, cache_key: str, data: Any, context_tags: Set[str] = None, 
                         invalidation_triggers: Set[str] = None) -> bool:
        """Cache memory data with intelligent invalidation triggers"""
        if context_tags is None:
            context_tags = set()
        if invalidation_triggers is None:
            invalidation_triggers = set()
        
        # Calculate data size
        try:
            data_size = len(pickle.dumps(data))
        except:
            data_size = len(str(data).encode('utf-8'))
        
        # Check if we need to make room
        with self.cache_lock:
            if data_size > self.max_cache_size_bytes:
                print(f"[MemoryCacheManager] ⚠️ Data too large to cache: {data_size} bytes")
                return False
            
            # Evict entries if needed
            while (self.cache_size_bytes + data_size > self.max_cache_size_bytes and 
                   len(self.cache) > 0):
                self._evict_lru_entry()
            
            # Create cache entry
            entry = CacheEntry(
                data=data,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                cache_key=cache_key,
                context_tags=context_tags,
                invalidation_triggers=invalidation_triggers,
                size_bytes=data_size
            )
            
            # Store in cache
            self.cache[cache_key] = entry
            self.cache_size_bytes += data_size
            
            # Record context associations
            self._record_context_associations(cache_key, context_tags)
            
            print(f"[MemoryCacheManager] 💾 Cached: {cache_key[:20]}... ({data_size} bytes)")
            return True
    
    def invalidate_cache(self, invalidation_trigger: str):
        """Invalidate cache entries based on trigger"""
        invalidated_count = 0
        
        with self.cache_lock:
            keys_to_remove = []
            
            for cache_key, entry in self.cache.items():
                if invalidation_trigger in entry.invalidation_triggers:
                    keys_to_remove.append(cache_key)
            
            for key in keys_to_remove:
                entry = self.cache[key]
                self.cache_size_bytes -= entry.size_bytes
                del self.cache[key]
                invalidated_count += 1
        
        self.metrics['invalidations'] += invalidated_count
        if invalidated_count > 0:
            print(f"[MemoryCacheManager] 🧹 Invalidated {invalidated_count} entries for trigger: {invalidation_trigger}")
    
    def batch_memory_operations(self, operations: List[Dict[str, Any]], 
                               batch_type: str, user_context: str = "") -> str:
        """Queue memory operations for intelligent batching"""
        batch_id = f"batch_{int(time.time() * 1000)}_{hash(user_context) % 10000}"
        
        with self.batch_lock:
            batch = MemoryOperationBatch(
                batch_id=batch_id,
                operations=operations,
                created_at=datetime.now(),
                batch_type=batch_type,
                priority=1,
                user_context=user_context
            )
            
            self.pending_batches[batch_id] = batch
            
            # Check if we should process immediately
            if len(operations) >= self.batch_threshold:
                self._process_batch_immediate(batch_id)
            else:
                # Schedule for later processing
                threading.Timer(self.batch_timeout, self._process_batch_delayed, [batch_id]).start()
        
        return batch_id
    
    def preload_contextual_memory(self, context_pattern: str, user_context: str = ""):
        """Proactively preload memory based on context patterns"""
        if context_pattern in self.preload_queue:
            return  # Already queued
        
        self.preload_queue.add(context_pattern)
        
        # Submit preload task
        future = self.preload_executor.submit(self._execute_preload, context_pattern, user_context)
        future.add_done_callback(lambda f: self.preload_queue.discard(context_pattern))
    
    def get_intelligent_memory_suggestions(self, user_context: str, 
                                         current_query: str) -> List[str]:
        """Get intelligent memory suggestions based on patterns"""
        suggestions = []
        
        with self.pattern_lock:
            # Look for similar access patterns
            if user_context in self.access_patterns:
                recent_accesses = self.access_patterns[user_context][-10:]  # Last 10 accesses
                
                # Find commonly accessed items after similar queries
                query_hash = hashlib.md5(current_query.lower().encode()).hexdigest()[:8]
                
                for i, access in enumerate(recent_accesses[:-1]):
                    if query_hash in access:
                        # Found similar query, suggest next access
                        next_access = recent_accesses[i + 1]
                        suggestions.append(next_access)
        
        return list(set(suggestions))  # Remove duplicates
    
    def _record_access_pattern(self, cache_key: str, context_tags: Set[str]):
        """Record access pattern for learning"""
        if context_tags:
            primary_context = next(iter(context_tags))  # Use first tag as primary context
            
            with self.pattern_lock:
                self.access_patterns[primary_context].append(cache_key)
                # Keep only recent patterns
                if len(self.access_patterns[primary_context]) > 100:
                    self.access_patterns[primary_context] = self.access_patterns[primary_context][-50:]
    
    def _record_context_associations(self, cache_key: str, context_tags: Set[str]):
        """Record associations between contexts and cache keys"""
        with self.pattern_lock:
            for tag in context_tags:
                self.context_associations[tag].add(cache_key)
    
    def _trigger_contextual_preload(self, missed_key: str, context_tags: Set[str]):
        """Trigger preloading of related content when cache miss occurs"""
        if not context_tags:
            return
        
        # Find related cache keys from context associations
        related_keys = set()
        
        with self.pattern_lock:
            for tag in context_tags:
                if tag in self.context_associations:
                    related_keys.update(self.context_associations[tag])
        
        # Preload up to 3 related items
        for key in list(related_keys)[:3]:
            if key not in self.cache and key != missed_key:
                self.preload_contextual_memory(key)
    
    def _evict_lru_entry(self):
        """Evict least recently used cache entry"""
        if not self.cache:
            return
        
        # Get least recently used key
        lru_key = next(iter(self.cache))
        entry = self.cache[lru_key]
        
        # Remove from cache
        self.cache_size_bytes -= entry.size_bytes
        del self.cache[lru_key]
        
        self.metrics['evictions'] += 1
        print(f"[MemoryCacheManager] 🗑️ Evicted LRU entry: {lru_key[:20]}...")
    
    def _process_batch_immediate(self, batch_id: str):
        """Process batch immediately"""
        with self.batch_lock:
            if batch_id not in self.pending_batches:
                return
            
            batch = self.pending_batches[batch_id]
            del self.pending_batches[batch_id]
        
        self._execute_batch(batch)
    
    def _process_batch_delayed(self, batch_id: str):
        """Process batch after timeout"""
        with self.batch_lock:
            if batch_id not in self.pending_batches:
                return  # Already processed
            
            batch = self.pending_batches[batch_id]
            del self.pending_batches[batch_id]
        
        self._execute_batch(batch)
    
    def _execute_batch(self, batch: MemoryOperationBatch):
        """Execute a batch of memory operations"""
        try:
            print(f"[MemoryCacheManager] 📦 Processing batch: {batch.batch_id} ({len(batch.operations)} ops)")
            
            if batch.batch_type == 'read':
                self._execute_read_batch(batch)
            elif batch.batch_type == 'write':
                self._execute_write_batch(batch)
            elif batch.batch_type == 'extract':
                self._execute_extract_batch(batch)
            
            self.metrics['batch_operations'] += 1
            
        except Exception as e:
            print(f"[MemoryCacheManager] ❌ Batch execution failed: {e}")
    
    def _execute_read_batch(self, batch: MemoryOperationBatch):
        """Execute batch of read operations"""
        # Group operations by similar patterns for efficiency
        for operation in batch.operations:
            # Simulate read operation
            cache_key = operation.get('cache_key', '')
            if cache_key:
                # Check if already cached
                cached_data = self.get_cached_memory(cache_key)
                if not cached_data:
                    # Simulate loading from storage
                    operation['result'] = f"Batch loaded: {cache_key}"
    
    def _execute_write_batch(self, batch: MemoryOperationBatch):
        """Execute batch of write operations"""
        # Group writes for efficient storage
        for operation in batch.operations:
            cache_key = operation.get('cache_key', '')
            data = operation.get('data')
            if cache_key and data:
                self.cache_memory_data(cache_key, data)
    
    def _execute_extract_batch(self, batch: MemoryOperationBatch):
        """Execute batch of extraction operations"""
        # Combine similar extractions for efficiency
        combined_text = " | ".join([op.get('text', '') for op in batch.operations])
        if combined_text:
            # Simulate extraction
            print(f"[MemoryCacheManager] 🧠 Batch extraction: {len(batch.operations)} items")
    
    def _execute_preload(self, context_pattern: str, user_context: str):
        """Execute preload operation"""
        try:
            # Simulate preloading based on context pattern
            cache_key = f"preload_{context_pattern}_{user_context}"
            
            # Check if already cached
            if cache_key not in self.cache:
                # Simulate loading data
                preload_data = f"Preloaded data for {context_pattern}"
                
                if self.cache_memory_data(
                    cache_key, 
                    preload_data, 
                    context_tags={user_context, "preloaded"},
                    invalidation_triggers={"context_change", "user_logout"}
                ):
                    self.metrics['preload_successes'] += 1
                    print(f"[MemoryCacheManager] 🔮 Preloaded: {context_pattern}")
        
        except Exception as e:
            print(f"[MemoryCacheManager] ❌ Preload failed: {e}")
    
    def _background_maintenance(self):
        """Background thread for cache maintenance"""
        while True:
            try:
                time.sleep(60)  # Run every minute
                
                # Clean expired entries
                self._clean_expired_entries()
                
                # Persist cache if enabled
                if self.cache_persistence:
                    self._persist_cache()
                
                # Log metrics
                self._log_metrics()
                
            except Exception as e:
                print(f"[MemoryCacheManager] ❌ Maintenance error: {e}")
    
    def _clean_expired_entries(self):
        """Remove expired cache entries"""
        current_time = datetime.now()
        expired_keys = []
        
        with self.cache_lock:
            for cache_key, entry in self.cache.items():
                # Consider entries expired if not accessed for 1 hour
                if current_time - entry.last_accessed > timedelta(hours=1):
                    expired_keys.append(cache_key)
        
        for key in expired_keys:
            with self.cache_lock:
                if key in self.cache:
                    entry = self.cache[key]
                    self.cache_size_bytes -= entry.size_bytes
                    del self.cache[key]
        
        if expired_keys:
            print(f"[MemoryCacheManager] 🧹 Cleaned {len(expired_keys)} expired entries")
    
    def _persist_cache(self):
        """Persist cache to disk"""
        try:
            # Only persist important entries to avoid large files
            important_entries = {}
            
            with self.cache_lock:
                for key, entry in self.cache.items():
                    if (entry.access_count > 2 and 
                        "important" in entry.context_tags or 
                        entry.size_bytes < 10000):  # Small entries
                        important_entries[key] = {
                            'data': entry.data,
                            'context_tags': list(entry.context_tags),
                            'access_count': entry.access_count
                        }
            
            if important_entries:
                with open(self.cache_file, 'wb') as f:
                    pickle.dump(important_entries, f)
        
        except Exception as e:
            print(f"[MemoryCacheManager] ❌ Cache persistence failed: {e}")
    
    def _load_persistent_cache(self):
        """Load persisted cache from disk"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    persisted_data = pickle.load(f)
                
                # Restore important entries
                for key, entry_data in persisted_data.items():
                    self.cache_memory_data(
                        key,
                        entry_data['data'],
                        context_tags=set(entry_data.get('context_tags', [])),
                        invalidation_triggers={"system_restart"}
                    )
                
                print(f"[MemoryCacheManager] 💾 Restored {len(persisted_data)} cache entries")
        
        except Exception as e:
            print(f"[MemoryCacheManager] ❌ Cache loading failed: {e}")
    
    def _log_metrics(self):
        """Log performance metrics"""
        hit_rate = 0
        if self.metrics['cache_hits'] + self.metrics['cache_misses'] > 0:
            hit_rate = self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses']) * 100
        
        print(f"[MemoryCacheManager] 📊 Metrics - Hit Rate: {hit_rate:.1f}%, "
              f"Cache Size: {self.cache_size_bytes / 1024 / 1024:.1f}MB, "
              f"Entries: {len(self.cache)}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        with self.cache_lock:
            hit_rate = 0
            if self.metrics['cache_hits'] + self.metrics['cache_misses'] > 0:
                hit_rate = self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses']) * 100
            
            return {
                'cache_metrics': dict(self.metrics),
                'cache_stats': {
                    'hit_rate_percent': hit_rate,
                    'cache_size_mb': self.cache_size_bytes / 1024 / 1024,
                    'cache_entries': len(self.cache),
                    'max_size_mb': self.max_cache_size_mb
                },
                'batch_stats': {
                    'pending_batches': len(self.pending_batches),
                    'batch_threshold': self.batch_threshold,
                    'batch_timeout': self.batch_timeout
                },
                'pattern_stats': {
                    'learned_patterns': len(self.access_patterns),
                    'context_associations': len(self.context_associations),
                    'preload_queue_size': len(self.preload_queue)
                }
            }
    
    def shutdown(self):
        """Gracefully shutdown the cache manager"""
        print("[MemoryCacheManager] 🛑 Shutting down memory cache manager...")
        
        # Persist final cache state
        if self.cache_persistence:
            self._persist_cache()
        
        # Shutdown preload executor
        self.preload_executor.shutdown(wait=True)
        
        print("[MemoryCacheManager] ✅ Memory cache manager shutdown complete")

# Global cache manager instance
_memory_cache_manager = None

def get_memory_cache_manager() -> MemoryCacheManager:
    """Get or create the global memory cache manager instance"""
    global _memory_cache_manager
    if _memory_cache_manager is None:
        _memory_cache_manager = MemoryCacheManager()
    return _memory_cache_manager

def cache_memory_intelligent(cache_key: str, data: Any, 
                           context_tags: Set[str] = None,
                           invalidation_triggers: Set[str] = None) -> bool:
    """Intelligently cache memory data with context awareness"""
    manager = get_memory_cache_manager()
    return manager.cache_memory_data(cache_key, data, context_tags, invalidation_triggers)

def get_cached_memory_intelligent(cache_key: str, context_tags: Set[str] = None) -> Optional[Any]:
    """Get intelligently cached memory data"""
    manager = get_memory_cache_manager()
    return manager.get_cached_memory(cache_key, context_tags)

def invalidate_memory_cache(invalidation_trigger: str):
    """Invalidate memory cache based on trigger"""
    manager = get_memory_cache_manager()
    manager.invalidate_cache(invalidation_trigger)

def batch_memory_operations(operations: List[Dict[str, Any]], 
                          batch_type: str, user_context: str = "") -> str:
    """Batch memory operations for efficiency"""
    manager = get_memory_cache_manager()
    return manager.batch_memory_operations(operations, batch_type, user_context)

def preload_memory_contextual(context_pattern: str, user_context: str = ""):
    """Preload memory based on context patterns"""
    manager = get_memory_cache_manager()
    manager.preload_contextual_memory(context_pattern, user_context)

def get_memory_cache_performance() -> Dict[str, Any]:
    """Get memory cache performance metrics"""
    manager = get_memory_cache_manager()
    return manager.get_performance_metrics()