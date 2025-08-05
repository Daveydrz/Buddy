#!/usr/bin/env python3
"""
Reactive Neural Architecture for Newbudd - Advanced Event-Driven Consciousness System

This module implements a reactive neural architecture that combines:
1. Event-Driven Nervous System (pub/sub messaging)
2. Async Neural Pathways (async/await for I/O operations)
3. Parallel Processing Cortex (thread-based parallelism)
4. Integration Layer (hybrid coordination)
5. Optimized Memory Management (shared memory, pooling)

Created: 2025-01-09
Purpose: Enhance consciousness processing with reactive patterns
"""

import asyncio
import threading
import time
import logging
import uuid
import weakref
import mmap
import pickle
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Dict, Any, List, Callable, Optional, Tuple, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from threading import RLock, Lock, Condition, Event, BoundedSemaphore
import multiprocessing as mp
from functools import wraps
import traceback
try:
    import psutil
except ImportError:
    psutil = None
import gc

# Setup logging
logger = logging.getLogger(__name__)

class EventPriority(Enum):
    """Priority levels for events in the nervous system"""
    CRITICAL = 1    # System critical (errors, shutdown)
    HIGH = 2        # User interactions, consciousness changes
    MEDIUM = 3      # Background consciousness processing
    LOW = 4         # Analytics, logging, maintenance

class EventType(Enum):
    """Types of events in the neural architecture"""
    # User interaction events
    USER_INPUT = auto()
    USER_RESPONSE = auto()
    
    # Consciousness events
    CONSCIOUSNESS_UPDATE = auto()
    EMOTION_CHANGE = auto()
    MEMORY_FORMATION = auto()
    GOAL_UPDATE = auto()
    
    # System events
    MODULE_START = auto()
    MODULE_COMPLETE = auto()
    MODULE_ERROR = auto()
    SYSTEM_HEALTH = auto()
    
    # Neural pathway events
    ASYNC_OPERATION = auto()
    THREAD_OPERATION = auto()
    INTEGRATION_REQUEST = auto()

@dataclass
class NeuralEvent:
    """Event in the reactive neural architecture"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType = EventType.CONSCIOUSNESS_UPDATE
    priority: EventPriority = EventPriority.MEDIUM
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    target: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: float = 30.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            'id': self.id,
            'type': self.type.name,
            'priority': self.priority.value,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'target': self.target,
            'data': self.data,
            'correlation_id': self.correlation_id,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'timeout': self.timeout
        }

class EventSubscriber(ABC):
    """Abstract base class for event subscribers"""
    
    @abstractmethod
    async def handle_event(self, event: NeuralEvent) -> bool:
        """Handle an event. Return True if handled successfully."""
        pass
    
    @abstractmethod
    def get_subscription_patterns(self) -> List[str]:
        """Return patterns this subscriber is interested in"""
        pass

class EventBus:
    """Central Event Bus for module communication with pub/sub pattern"""
    
    def __init__(self, max_queue_size: int = 10000):
        self.max_queue_size = max_queue_size
        self.subscribers: Dict[str, Set[EventSubscriber]] = defaultdict(set)
        self.event_queue: asyncio.Queue = None
        self.priority_queues: Dict[EventPriority, asyncio.Queue] = {}
        self.dead_letter_queue: deque = deque(maxlen=1000)
        
        # Threading support
        self.thread_subscribers: Dict[str, Set[Callable]] = defaultdict(set)
        self.thread_event_queue = deque(maxlen=max_queue_size)
        self.thread_queue_lock = Lock()
        
        # Statistics and monitoring
        self.stats = {
            'events_published': 0,
            'events_processed': 0,
            'events_failed': 0,
            'dead_letters': 0,
            'avg_processing_time': 0.0,
            'subscribers_count': 0
        }
        self.stats_lock = Lock()
        
        # Event processing control
        self.processing_event = Event()
        self.processing_event.set()
        self.shutdown_flag = threading.Event()
        
        logger.info("[EventBus] 🚌 Reactive Event Bus initialized")
    
    async def initialize_async(self):
        """Initialize async components"""
        if self.event_queue is None:
            self.event_queue = asyncio.Queue(maxsize=self.max_queue_size)
            
            # Initialize priority queues
            for priority in EventPriority:
                self.priority_queues[priority] = asyncio.Queue(maxsize=self.max_queue_size // 4)
            
            # Start event processing loop
            asyncio.create_task(self._event_processing_loop())
            logger.info("[EventBus] 🔄 Async event processing initialized")
    
    def subscribe(self, pattern: str, subscriber: Union[EventSubscriber, Callable]):
        """Subscribe to events matching a pattern"""
        if isinstance(subscriber, EventSubscriber):
            self.subscribers[pattern].add(subscriber)
            logger.debug(f"[EventBus] 📝 Async subscriber registered for pattern: {pattern}")
        else:
            # Thread-based subscriber
            self.thread_subscribers[pattern].add(subscriber)
            logger.debug(f"[EventBus] 📝 Thread subscriber registered for pattern: {pattern}")
        
        with self.stats_lock:
            self.stats['subscribers_count'] = sum(len(subs) for subs in self.subscribers.values()) + \
                                            sum(len(subs) for subs in self.thread_subscribers.values())
    
    def unsubscribe(self, pattern: str, subscriber: Union[EventSubscriber, Callable]):
        """Unsubscribe from events"""
        if isinstance(subscriber, EventSubscriber):
            self.subscribers[pattern].discard(subscriber)
        else:
            self.thread_subscribers[pattern].discard(subscriber)
        
        with self.stats_lock:
            self.stats['subscribers_count'] = sum(len(subs) for subs in self.subscribers.values()) + \
                                            sum(len(subs) for subs in self.thread_subscribers.values())
    
    async def publish_async(self, event: NeuralEvent):
        """Publish event asynchronously"""
        if self.event_queue is None:
            await self.initialize_async()
        
        try:
            # Add to priority queue
            priority_queue = self.priority_queues[event.priority]
            await priority_queue.put(event)
            
            with self.stats_lock:
                self.stats['events_published'] += 1
            
            logger.debug(f"[EventBus] 📤 Event published: {event.type.name} (Priority: {event.priority.name})")
            
        except asyncio.QueueFull:
            # Add to dead letter queue
            self.dead_letter_queue.append(event)
            with self.stats_lock:
                self.stats['dead_letters'] += 1
            logger.warning(f"[EventBus] 💀 Event queue full, added to dead letter queue: {event.id}")
    
    def publish_sync(self, event: NeuralEvent):
        """Publish event synchronously for thread-based subscribers"""
        with self.thread_queue_lock:
            if len(self.thread_event_queue) >= self.max_queue_size:
                # Remove oldest event
                old_event = self.thread_event_queue.popleft()
                logger.warning(f"[EventBus] 🗑️ Dropped old event: {old_event.id}")
            
            self.thread_event_queue.append(event)
        
        # Process immediately for thread subscribers
        self._process_thread_event(event)
        
        with self.stats_lock:
            self.stats['events_published'] += 1
    
    def _process_thread_event(self, event: NeuralEvent):
        """Process event for thread-based subscribers"""
        for pattern, subscribers in self.thread_subscribers.items():
            if self._matches_pattern(event, pattern):
                for subscriber in subscribers:
                    try:
                        start_time = time.time()
                        subscriber(event)
                        processing_time = time.time() - start_time
                        
                        with self.stats_lock:
                            self.stats['events_processed'] += 1
                            self._update_avg_processing_time(processing_time)
                            
                    except Exception as e:
                        logger.error(f"[EventBus] ❌ Thread subscriber error: {e}")
                        with self.stats_lock:
                            self.stats['events_failed'] += 1
    
    async def _event_processing_loop(self):
        """Main event processing loop for async subscribers"""
        while not self.shutdown_flag.is_set():
            try:
                # Process events by priority
                for priority in [EventPriority.CRITICAL, EventPriority.HIGH, EventPriority.MEDIUM, EventPriority.LOW]:
                    priority_queue = self.priority_queues[priority]
                    
                    try:
                        # Get event with timeout
                        event = await asyncio.wait_for(priority_queue.get(), timeout=0.1)
                        await self._process_async_event(event)
                        priority_queue.task_done()
                        
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"[EventBus] ❌ Event processing error: {e}")
                        with self.stats_lock:
                            self.stats['events_failed'] += 1
                
            except Exception as e:
                logger.error(f"[EventBus] ❌ Event loop error: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_async_event(self, event: NeuralEvent):
        """Process event for async subscribers"""
        start_time = time.time()
        
        for pattern, subscribers in self.subscribers.items():
            if self._matches_pattern(event, pattern):
                for subscriber in subscribers:
                    try:
                        success = await subscriber.handle_event(event)
                        if success:
                            with self.stats_lock:
                                self.stats['events_processed'] += 1
                        else:
                            # Retry logic
                            if event.retry_count < event.max_retries:
                                event.retry_count += 1
                                await self.publish_async(event)
                                
                    except Exception as e:
                        logger.error(f"[EventBus] ❌ Async subscriber error: {e}")
                        with self.stats_lock:
                            self.stats['events_failed'] += 1
        
        processing_time = time.time() - start_time
        with self.stats_lock:
            self._update_avg_processing_time(processing_time)
    
    def _matches_pattern(self, event: NeuralEvent, pattern: str) -> bool:
        """Check if event matches subscription pattern"""
        if pattern == "*":
            return True
        elif pattern == event.type.name:
            return True
        elif pattern.startswith(event.source + "."):
            return True
        elif pattern in event.data.get('tags', []):
            return True
        return False
    
    def _update_avg_processing_time(self, processing_time: float):
        """Update average processing time (thread-safe)"""
        current_avg = self.stats['avg_processing_time']
        processed_count = self.stats['events_processed']
        if processed_count > 0:
            self.stats['avg_processing_time'] = ((current_avg * (processed_count - 1)) + processing_time) / processed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        with self.stats_lock:
            return {
                **self.stats,
                'queue_sizes': {
                    priority.name: queue.qsize() if queue else 0
                    for priority, queue in self.priority_queues.items()
                },
                'thread_queue_size': len(self.thread_event_queue),
                'dead_letter_count': len(self.dead_letter_queue)
            }
    
    async def shutdown(self):
        """Shutdown event bus gracefully"""
        self.shutdown_flag.set()
        
        # Wait for queues to empty
        for queue in self.priority_queues.values():
            if queue:
                await queue.join()
        
        logger.info("[EventBus] 🛑 Event bus shutdown complete")

class AsyncNeuralPathways:
    """Async Neural Pathways for high-throughput I/O operations"""
    
    def __init__(self, max_concurrent: int = 100, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.max_concurrent = max_concurrent
        self.loop = loop or asyncio.get_event_loop()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_operations: Dict[str, asyncio.Task] = {}
        self.operation_stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'avg_duration': 0.0,
            'concurrent_peak': 0
        }
        self.stats_lock = asyncio.Lock()
        
        # Coroutine pools for different operation types
        self.llm_pool = asyncio.Queue(maxsize=10)
        self.io_pool = asyncio.Queue(maxsize=20)
        self.compute_pool = asyncio.Queue(maxsize=5)
        
        logger.info(f"[AsyncNeuralPathways] 🧠 Initialized with {max_concurrent} max concurrent operations")
    
    async def execute_llm_operation(self, operation_id: str, llm_func: Callable, *args, **kwargs) -> Any:
        """Execute LLM operation asynchronously"""
        return await self._execute_with_pool(operation_id, self.llm_pool, llm_func, *args, **kwargs)
    
    async def execute_io_operation(self, operation_id: str, io_func: Callable, *args, **kwargs) -> Any:
        """Execute I/O operation asynchronously"""
        return await self._execute_with_pool(operation_id, self.io_pool, io_func, *args, **kwargs)
    
    async def execute_compute_operation(self, operation_id: str, compute_func: Callable, *args, **kwargs) -> Any:
        """Execute computation asynchronously"""
        return await self._execute_with_pool(operation_id, self.compute_pool, compute_func, *args, **kwargs)
    
    async def _execute_with_pool(self, operation_id: str, pool: asyncio.Queue, func: Callable, *args, **kwargs) -> Any:
        """Execute operation with resource pooling"""
        async with self.semaphore:
            start_time = time.time()
            
            try:
                # Update statistics
                async with self.stats_lock:
                    self.operation_stats['total_operations'] += 1
                    current_concurrent = len(self.active_operations)
                    if current_concurrent > self.operation_stats['concurrent_peak']:
                        self.operation_stats['concurrent_peak'] = current_concurrent
                
                # Create and track task
                task = asyncio.create_task(self._run_async_operation(func, *args, **kwargs))
                self.active_operations[operation_id] = task
                
                try:
                    result = await task
                    
                    async with self.stats_lock:
                        self.operation_stats['successful_operations'] += 1
                    
                    return result
                    
                finally:
                    # Clean up task
                    if operation_id in self.active_operations:
                        del self.active_operations[operation_id]
            
            except Exception as e:
                async with self.stats_lock:
                    self.operation_stats['failed_operations'] += 1
                logger.error(f"[AsyncNeuralPathways] ❌ Operation {operation_id} failed: {e}")
                raise
            
            finally:
                # Update average duration
                duration = time.time() - start_time
                async with self.stats_lock:
                    total_ops = self.operation_stats['total_operations']
                    current_avg = self.operation_stats['avg_duration']
                    self.operation_stats['avg_duration'] = ((current_avg * (total_ops - 1)) + duration) / total_ops
    
    async def _run_async_operation(self, func: Callable, *args, **kwargs) -> Any:
        """Run operation, converting sync functions to async if needed"""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # Run in thread pool for sync functions
            return await self.loop.run_in_executor(None, func, *args, **kwargs)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get async pathway statistics"""
        async with self.stats_lock:
            return {
                **self.operation_stats,
                'active_operations': len(self.active_operations),
                'max_concurrent': self.max_concurrent,
                'pool_sizes': {
                    'llm_pool': self.llm_pool.qsize(),
                    'io_pool': self.io_pool.qsize(),
                    'compute_pool': self.compute_pool.qsize()
                }
            }
    
    async def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a specific operation"""
        if operation_id in self.active_operations:
            task = self.active_operations[operation_id]
            task.cancel()
            del self.active_operations[operation_id]
            return True
        return False
    
    async def cancel_all_operations(self):
        """Cancel all active operations"""
        for operation_id, task in list(self.active_operations.items()):
            task.cancel()
        self.active_operations.clear()
        logger.info("[AsyncNeuralPathways] 🛑 All operations cancelled")

class WorkStealingThreadPool:
    """Work-stealing thread pool for CPU-bound operations with thread affinity"""
    
    def __init__(self, num_workers: int = None, thread_affinity: bool = True):
        self.num_workers = num_workers or min(32, (mp.cpu_count() or 1) + 4)
        self.thread_affinity = thread_affinity
        self.work_queues: List[deque] = [deque() for _ in range(self.num_workers)]
        self.workers: List[threading.Thread] = []
        self.locks: List[Lock] = [Lock() for _ in range(self.num_workers)]
        self.shutdown_event = threading.Event()
        self.stats = {
            'tasks_submitted': 0,
            'tasks_completed': 0,
            'tasks_stolen': 0,
            'worker_utilization': [0.0] * self.num_workers
        }
        self.stats_lock = Lock()
        
        self._start_workers()
        logger.info(f"[WorkStealingThreadPool] ⚡ Started {self.num_workers} workers with affinity: {thread_affinity}")
    
    def _start_workers(self):
        """Start worker threads"""
        for i in range(self.num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                args=(i,),
                name=f"WorkStealer-{i}",
                daemon=True
            )
            self.workers.append(worker)
            worker.start()
            
            # Set thread affinity if enabled
            if self.thread_affinity and psutil:
                try:
                    process = psutil.Process()
                    cpu_affinity = list(range(mp.cpu_count()))
                    if len(cpu_affinity) > self.num_workers:
                        # Assign specific CPU cores to workers
                        assigned_cpu = cpu_affinity[i % len(cpu_affinity)]
                        process.cpu_affinity([assigned_cpu])
                except (ImportError, AttributeError):
                    pass  # psutil not available or method not supported
    
    def submit(self, func: Callable, *args, **kwargs) -> threading.Event:
        """Submit task to work-stealing pool"""
        completion_event = threading.Event()
        task = {
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'completion_event': completion_event,
            'result': None,
            'error': None
        }
        
        # Add to least loaded queue
        min_queue_idx = min(range(self.num_workers), key=lambda i: len(self.work_queues[i]))
        with self.locks[min_queue_idx]:
            self.work_queues[min_queue_idx].append(task)
        
        with self.stats_lock:
            self.stats['tasks_submitted'] += 1
        
        return completion_event
    
    def _worker_loop(self, worker_id: int):
        """Main worker loop with work stealing"""
        while not self.shutdown_event.is_set():
            task = None
            
            # Try to get task from own queue
            with self.locks[worker_id]:
                if self.work_queues[worker_id]:
                    task = self.work_queues[worker_id].popleft()
            
            # If no task, try to steal from other queues
            if not task:
                for steal_from in range(self.num_workers):
                    if steal_from == worker_id:
                        continue
                    
                    with self.locks[steal_from]:
                        if self.work_queues[steal_from]:
                            task = self.work_queues[steal_from].popleft()
                            with self.stats_lock:
                                self.stats['tasks_stolen'] += 1
                            break
            
            if task:
                # Execute task
                start_time = time.time()
                try:
                    result = task['func'](*task['args'], **task['kwargs'])
                    task['result'] = result
                except Exception as e:
                    task['error'] = e
                    logger.error(f"[WorkStealingThreadPool] Worker {worker_id} task error: {e}")
                finally:
                    task['completion_event'].set()
                    
                    # Update statistics
                    with self.stats_lock:
                        self.stats['tasks_completed'] += 1
                        execution_time = time.time() - start_time
                        self.stats['worker_utilization'][worker_id] += execution_time
            else:
                # No work available, short sleep
                time.sleep(0.001)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get work-stealing pool statistics"""
        with self.stats_lock:
            return {
                **self.stats,
                'num_workers': self.num_workers,
                'queue_sizes': [len(q) for q in self.work_queues],
                'active_workers': sum(1 for worker in self.workers if worker.is_alive())
            }
    
    def shutdown(self, wait: bool = True):
        """Shutdown the thread pool"""
        self.shutdown_event.set()
        
        if wait:
            for worker in self.workers:
                worker.join(timeout=5.0)
        
        logger.info("[WorkStealingThreadPool] 🛑 Work-stealing pool shutdown")

class OptimizedMemoryManager:
    """Optimized memory management with shared memory and pooling"""
    
    def __init__(self, shared_memory_size: int = 100 * 1024 * 1024):  # 100MB default
        self.shared_memory_size = shared_memory_size
        self.memory_pools: Dict[str, List[Any]] = defaultdict(list)
        self.shared_memory_segments: Dict[str, Any] = {}
        self.pool_locks: Dict[str, Lock] = defaultdict(Lock)
        self.memory_stats = {
            'pools_created': 0,
            'objects_pooled': 0,
            'objects_reused': 0,
            'memory_allocated': 0,
            'memory_freed': 0
        }
        self.stats_lock = Lock()
        
        # Copy-on-write tracking
        self.cow_objects: Dict[str, Any] = {}
        self.cow_reference_counts: Dict[str, int] = defaultdict(int)
        self.cow_lock = Lock()
        
        logger.info(f"[OptimizedMemoryManager] 🧠 Initialized with {shared_memory_size // (1024*1024)}MB shared memory")
    
    def get_pooled_object(self, pool_name: str, factory_func: Callable = None) -> Any:
        """Get object from pool or create new one"""
        with self.pool_locks[pool_name]:
            if self.memory_pools[pool_name]:
                obj = self.memory_pools[pool_name].pop()
                with self.stats_lock:
                    self.memory_stats['objects_reused'] += 1
                return obj
            elif factory_func:
                obj = factory_func()
                with self.stats_lock:
                    self.memory_stats['objects_pooled'] += 1
                return obj
            else:
                return None
    
    def return_to_pool(self, pool_name: str, obj: Any, reset_func: Callable = None):
        """Return object to pool for reuse"""
        if reset_func:
            reset_func(obj)
        
        with self.pool_locks[pool_name]:
            self.memory_pools[pool_name].append(obj)
    
    def create_shared_memory_segment(self, name: str, size: int) -> Any:
        """Create shared memory segment"""
        try:
            import mmap
            import tempfile
            
            # Create temporary file for shared memory
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(b'\x00' * size)
            temp_file.flush()
            
            # Create memory map
            with open(temp_file.name, 'r+b') as f:
                memory_map = mmap.mmap(f.fileno(), size)
                self.shared_memory_segments[name] = {
                    'mmap': memory_map,
                    'file': temp_file.name,
                    'size': size
                }
                
                with self.stats_lock:
                    self.memory_stats['memory_allocated'] += size
                
                logger.debug(f"[OptimizedMemoryManager] 📝 Created shared memory segment: {name} ({size} bytes)")
                return memory_map
                
        except Exception as e:
            logger.error(f"[OptimizedMemoryManager] ❌ Failed to create shared memory: {e}")
            return None
    
    def create_cow_object(self, name: str, obj: Any) -> str:
        """Create copy-on-write object"""
        with self.cow_lock:
            object_id = f"{name}_{uuid.uuid4().hex[:8]}"
            self.cow_objects[object_id] = obj
            self.cow_reference_counts[object_id] = 1
            
            logger.debug(f"[OptimizedMemoryManager] 🐄 Created COW object: {object_id}")
            return object_id
    
    def get_cow_object(self, object_id: str, copy_on_write: bool = False) -> Any:
        """Get copy-on-write object"""
        with self.cow_lock:
            if object_id in self.cow_objects:
                if copy_on_write:
                    # Create copy for modification
                    import copy
                    obj_copy = copy.deepcopy(self.cow_objects[object_id])
                    new_id = f"{object_id}_copy_{uuid.uuid4().hex[:8]}"
                    self.cow_objects[new_id] = obj_copy
                    self.cow_reference_counts[new_id] = 1
                    return obj_copy, new_id
                else:
                    # Just increment reference count
                    self.cow_reference_counts[object_id] += 1
                    return self.cow_objects[object_id], object_id
            return None, None
    
    def release_cow_object(self, object_id: str):
        """Release copy-on-write object"""
        with self.cow_lock:
            if object_id in self.cow_reference_counts:
                self.cow_reference_counts[object_id] -= 1
                if self.cow_reference_counts[object_id] <= 0:
                    del self.cow_objects[object_id]
                    del self.cow_reference_counts[object_id]
                    logger.debug(f"[OptimizedMemoryManager] 🗑️ Released COW object: {object_id}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory management statistics"""
        with self.stats_lock:
            return {
                **self.memory_stats,
                'pool_counts': {name: len(pool) for name, pool in self.memory_pools.items()},
                'shared_segments': len(self.shared_memory_segments),
                'cow_objects': len(self.cow_objects),
                'total_cow_references': sum(self.cow_reference_counts.values())
            }
    
    def cleanup(self):
        """Cleanup memory resources"""
        # Clear pools
        for pool in self.memory_pools.values():
            pool.clear()
        
        # Close shared memory segments
        for segment_info in self.shared_memory_segments.values():
            try:
                segment_info['mmap'].close()
                os.unlink(segment_info['file'])
            except Exception as e:
                logger.warning(f"[OptimizedMemoryManager] ⚠️ Cleanup error: {e}")
        
        # Clear COW objects
        with self.cow_lock:
            self.cow_objects.clear()
            self.cow_reference_counts.clear()
        
        logger.info("[OptimizedMemoryManager] 🧹 Memory cleanup complete")

# Global instances
event_bus = EventBus()
async_pathways = AsyncNeuralPathways()
work_stealing_pool = WorkStealingThreadPool()
memory_manager = OptimizedMemoryManager()

def get_reactive_neural_architecture():
    """Get the global reactive neural architecture components"""
    return {
        'event_bus': event_bus,
        'async_pathways': async_pathways,
        'work_stealing_pool': work_stealing_pool,
        'memory_manager': memory_manager
    }

async def initialize_reactive_architecture():
    """Initialize the complete reactive neural architecture"""
    await event_bus.initialize_async()
    logger.info("[ReactiveNeuralArchitecture] 🚀 Reactive Neural Architecture initialized")
    return get_reactive_neural_architecture()

def shutdown_reactive_architecture():
    """Shutdown the reactive neural architecture"""
    work_stealing_pool.shutdown()
    memory_manager.cleanup()
    logger.info("[ReactiveNeuralArchitecture] 🛑 Reactive Neural Architecture shutdown")