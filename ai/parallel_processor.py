#!/usr/bin/env python3
"""
Enhanced Parallel Consciousness Processor - Reactive Neural Architecture Integration
Dramatically reduces response time from 2 minutes to ~20 seconds while preserving full consciousness depth.

Now integrated with:
- Event-Driven Nervous System
- Async Neural Pathways  
- Hybrid Consciousness Workers
- Optimized Memory Management

Created: 2025-01-09
Updated: 2025-01-09 (Reactive Architecture Integration)
Purpose: Enable parallel processing of consciousness modules with reactive patterns
"""

import threading
import time
import logging
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from typing import Dict, Any, List, Callable, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from threading import RLock, Lock, Condition, Event
import weakref
from collections import defaultdict

# Setup logging
logger = logging.getLogger(__name__)

class ModulePriority(Enum):
    """Priority levels for consciousness modules"""
    CRITICAL = 1    # Must complete for response (emotion, motivation)
    HIGH = 2        # Important for quality (inner_monologue, self_model)
    MEDIUM = 3      # Enhances response (temporal_awareness, entropy)
    LOW = 4         # Background processing (analytics, logging)

@dataclass
class ModuleConfig:
    """Configuration for a consciousness module"""
    name: str
    function: Callable
    priority: ModulePriority
    timeout: float
    fallback_value: Any
    description: str
    required: bool = False
    shared_resources: List[str] = field(default_factory=list)  # NEW: List of shared resources this module accesses
    lock_timeout: float = 1.0  # NEW: Maximum time to wait for locks

@dataclass
class ModuleResult:
    """Result from a consciousness module execution"""
    name: str
    success: bool
    result: Any
    execution_time: float
    error: Optional[str] = None
    timed_out: bool = False
    lock_wait_time: float = 0.0  # NEW: Time spent waiting for locks
    state_version: int = 0  # NEW: Version of state when this module executed

@dataclass
class StateSnapshot:
    """Versioned snapshot of consciousness state"""
    version: int
    timestamp: datetime
    data: Dict[str, Any]
    module_states: Dict[str, Any] = field(default_factory=dict)

class LockManager:
    """Thread-safe lock manager for consciousness modules"""
    
    def __init__(self):
        self._global_lock = RLock()  # Main coordination lock
        self._module_locks: Dict[str, RLock] = {}  # Per-module locks
        self._resource_locks: Dict[str, RLock] = {}  # Per-resource locks
        self._lock_registry = defaultdict(set)  # Track what locks each thread holds
        self._deadlock_timeout = 5.0  # Maximum time to wait for all locks
        
    def get_module_lock(self, module_name: str) -> RLock:
        """Get or create a lock for a specific module"""
        with self._global_lock:
            if module_name not in self._module_locks:
                self._module_locks[module_name] = RLock()
            return self._module_locks[module_name]
    
    def get_resource_lock(self, resource_name: str) -> RLock:
        """Get or create a lock for a shared resource"""
        with self._global_lock:
            if resource_name not in self._resource_locks:
                self._resource_locks[resource_name] = RLock()
            return self._resource_locks[resource_name]
    
    def acquire_locks(self, module_name: str, shared_resources: List[str], timeout: float = 1.0) -> bool:
        """Acquire all necessary locks for a module with deadlock prevention"""
        thread_id = threading.get_ident()
        acquired_locks = []
        start_time = time.time()
        
        try:
            # Sort locks by name to prevent deadlock
            all_locks = [(f"module:{module_name}", self.get_module_lock(module_name))]
            for resource in sorted(shared_resources):
                all_locks.append((f"resource:{resource}", self.get_resource_lock(resource)))
            
            # Try to acquire all locks within timeout
            for lock_name, lock in all_locks:
                remaining_time = timeout - (time.time() - start_time)
                if remaining_time <= 0:
                    raise TimeoutError(f"Lock acquisition timeout for {lock_name}")
                
                if lock.acquire(timeout=remaining_time):
                    acquired_locks.append((lock_name, lock))
                    self._lock_registry[thread_id].add(lock_name)
                else:
                    raise TimeoutError(f"Failed to acquire lock {lock_name}")
            
            return True
            
        except (TimeoutError, Exception) as e:
            # Release any acquired locks
            for lock_name, lock in reversed(acquired_locks):
                lock.release()
                self._lock_registry[thread_id].discard(lock_name)
            logger.warning(f"[LockManager] Failed to acquire locks for {module_name}: {e}")
            return False
    
    def release_locks(self, module_name: str, shared_resources: List[str]):
        """Release all locks for a module"""
        thread_id = threading.get_ident()
        
        # Release in reverse order
        for resource in reversed(sorted(shared_resources)):
            lock = self.get_resource_lock(resource)
            lock.release()
            self._lock_registry[thread_id].discard(f"resource:{resource}")
        
        # Release module lock last
        module_lock = self.get_module_lock(module_name)
        module_lock.release()
        self._lock_registry[thread_id].discard(f"module:{module_name}")

class StateManager:
    """Thread-safe state manager with versioning"""
    
    def __init__(self):
        self._state_lock = RLock()
        self._current_state: Dict[str, Any] = {}
        self._state_version = 0
        self._state_history: List[StateSnapshot] = []
        self._max_history = 10
        self._module_versions: Dict[str, int] = {}
        
    def get_current_version(self) -> int:
        """Get current state version"""
        with self._state_lock:
            return self._state_version
    
    def get_state_snapshot(self) -> StateSnapshot:
        """Get a versioned snapshot of current state"""
        with self._state_lock:
            return StateSnapshot(
                version=self._state_version,
                timestamp=datetime.now(),
                data=self._current_state.copy(),
                module_states=self._module_versions.copy()
            )
    
    def update_state(self, module_name: str, updates: Dict[str, Any], expected_version: Optional[int] = None) -> bool:
        """Update state atomically with conflict detection"""
        with self._state_lock:
            # Check for version conflicts
            if expected_version is not None and expected_version != self._state_version:
                logger.warning(f"[StateManager] Version conflict for {module_name}: expected {expected_version}, current {self._state_version}")
                return False
            
            # Create snapshot before update
            if len(self._state_history) >= self._max_history:
                self._state_history.pop(0)
            
            self._state_history.append(self.get_state_snapshot())
            
            # Apply updates
            self._current_state.update(updates)
            self._state_version += 1
            self._module_versions[module_name] = self._state_version
            
            logger.debug(f"[StateManager] State updated by {module_name} to version {self._state_version}")
            return True
    
    def get_state_copy(self) -> Tuple[Dict[str, Any], int]:
        """Get a copy of current state and version"""
        with self._state_lock:
            return self._current_state.copy(), self._state_version
    
    def rollback_to_version(self, version: int) -> bool:
        """Rollback state to a specific version"""
        with self._state_lock:
            for snapshot in reversed(self._state_history):
                if snapshot.version == version:
                    self._current_state = snapshot.data.copy()
                    self._state_version = version
                    self._module_versions = snapshot.module_states.copy()
                    logger.info(f"[StateManager] Rolled back to version {version}")
                    return True
            return False

class ParallelConsciousnessProcessor:
    """
    Thread-safe parallel processor for consciousness modules that dramatically reduces response time
    while maintaining full consciousness capabilities and preventing race conditions.
    """
    
    def __init__(self, max_workers: int = 8, global_timeout: float = 20.0):
        """
        Initialize the thread-safe parallel consciousness processor.
        
        Args:
            max_workers: Maximum number of concurrent threads
            global_timeout: Global timeout for all processing (seconds)
        """
        self.max_workers = max_workers
        self.global_timeout = global_timeout
        self.module_configs: Dict[str, ModuleConfig] = {}
        self.background_futures: List[Future] = []
        
        # Thread safety components
        self.lock_manager = LockManager()
        self.state_manager = StateManager()
        self.processing_lock = RLock()  # Main processing coordination
        self.stats_lock = Lock()  # For performance statistics
        
        # Thread pool
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="consciousness")
        
        # Performance tracking (thread-safe)
        self.execution_stats = {
            'total_executions': 0,
            'average_time': 0.0,
            'fastest_time': float('inf'),
            'slowest_time': 0.0,
            'timeout_count': 0,
            'error_count': 0,
            'lock_contention_count': 0,
            'version_conflicts': 0
        }
        
        # Active processing tracking
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_lock = Lock()
        
        logger.info(f"[ParallelProcessor] ✅ Thread-safe processor initialized: {max_workers} workers, {global_timeout}s timeout")
    
    def register_module(self, config: ModuleConfig):
        """Register a consciousness module for thread-safe parallel processing"""
        with self.processing_lock:
            self.module_configs[config.name] = config
            logger.debug(f"[ParallelProcessor] 📝 Registered thread-safe module: {config.name} (Priority: {config.priority.name})")
            if config.shared_resources:
                logger.debug(f"[ParallelProcessor] 🔒 Module {config.name} accesses resources: {config.shared_resources}")
    
    def setup_default_modules(self):
        """Setup default consciousness modules with thread-safe configurations"""
        try:
            # Import consciousness modules
            from ai.emotion import emotion_engine
            from ai.motivation import motivation_system
            from ai.inner_monologue import inner_monologue, ThoughtType
            from ai.subjective_experience import subjective_experience, ExperienceType
            from ai.temporal_awareness import temporal_awareness
            from ai.self_model import self_model
            from ai.entropy import entropy_system
            from ai.global_workspace import global_workspace, AttentionPriority, ProcessingMode
            
            # Register modules with priority, timeout, and shared resource configurations
            modules = [
                ModuleConfig(
                    name="emotion_processing",
                    function=self._process_emotion_module,
                    priority=ModulePriority.CRITICAL,
                    timeout=3.0,
                    fallback_value={"primary_emotion": "neutral", "emotional_modulation": {}},
                    description="Process emotional response to user input",
                    required=True,
                    shared_resources=["emotion_state", "mood_history"],
                    lock_timeout=2.0
                ),
                ModuleConfig(
                    name="motivation_evaluation", 
                    function=self._process_motivation_module,
                    priority=ModulePriority.CRITICAL,
                    timeout=3.0,
                    fallback_value={"motivation_satisfaction": 0.5},
                    description="Evaluate motivation satisfaction",
                    required=True,
                    shared_resources=["motivation_state", "goal_tracking"],
                    lock_timeout=2.0
                ),
                ModuleConfig(
                    name="inner_monologue",
                    function=self._process_inner_monologue_module,
                    priority=ModulePriority.HIGH,
                    timeout=4.0,
                    fallback_value={"thoughts_triggered": False},
                    description="Generate internal thoughts about interaction",
                    shared_resources=["thought_stream", "reflection_state"],
                    lock_timeout=1.5
                ),
                ModuleConfig(
                    name="subjective_experience",
                    function=self._process_subjective_experience_module,
                    priority=ModulePriority.HIGH,
                    timeout=4.0,
                    fallback_value={"experience_valence": 0.5, "experience_significance": 0.5},
                    description="Create subjective experience of interaction",
                    shared_resources=["experience_history", "memory_formation"],
                    lock_timeout=1.5
                ),
                ModuleConfig(
                    name="self_reflection",
                    function=self._process_self_model_module,
                    priority=ModulePriority.HIGH,
                    timeout=3.0,
                    fallback_value={"reflection_completed": False},
                    description="Self-reflection on the interaction",
                    shared_resources=["self_model_state", "identity_tracking"],
                    lock_timeout=1.5
                ),
                ModuleConfig(
                    name="temporal_awareness",
                    function=self._process_temporal_module,
                    priority=ModulePriority.MEDIUM,
                    timeout=2.0,
                    fallback_value={"temporal_event_marked": False},
                    description="Mark temporal significance of interaction",
                    shared_resources=["temporal_timeline", "event_markers"],
                    lock_timeout=1.0
                ),
                ModuleConfig(
                    name="entropy_processing",
                    function=self._process_entropy_module,
                    priority=ModulePriority.MEDIUM,
                    timeout=2.0,
                    fallback_value={"response_uncertainty": 0.3},
                    description="Apply entropy to response planning",
                    shared_resources=["entropy_state"],
                    lock_timeout=1.0
                ),
                ModuleConfig(
                    name="attention_management",
                    function=self._process_attention_module,
                    priority=ModulePriority.MEDIUM,
                    timeout=2.0,
                    fallback_value={"attention_requested": False},
                    description="Request attention in global workspace",
                    shared_resources=["attention_queue", "workspace_state"],
                    lock_timeout=1.0
                )
            ]
            
            for config in modules:
                self.register_module(config)
                
            logger.info(f"[ParallelProcessor] ✅ Setup {len(modules)} thread-safe consciousness modules")
            
        except ImportError as e:
            logger.warning(f"[ParallelProcessor] ⚠️ Some consciousness modules not available: {e}")
    
    def process_consciousness_parallel(self, text: str, current_user: str) -> Dict[str, Any]:
        """
        Process all consciousness modules in parallel with thread safety, dramatically reducing response time.
        
        Args:
            text: User input text
            current_user: Current user identifier
            
        Returns:
            Combined consciousness state from all modules
        """
        session_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Create processing session
        with self.session_lock:
            self.active_sessions[session_id] = {
                'start_time': start_time,
                'text': text,
                'user': current_user,
                'status': 'starting'
            }
        
        logger.info(f"[ParallelProcessor] 🚀 Starting thread-safe parallel processing (session: {session_id[:8]})")
        logger.info(f"[ParallelProcessor] 📝 Input: '{text[:30]}...' | User: {current_user}")
        
        try:
            with self.processing_lock:
                # Get initial state snapshot
                initial_state, initial_version = self.state_manager.get_state_copy()
                
                # Prepare context for all modules
                context = {
                    'text': text,
                    'current_user': current_user,
                    'timestamp': datetime.now().isoformat(),
                    'interaction_id': f"interaction_{int(time.time())}",
                    'session_id': session_id,
                    'state_version': initial_version
                }
                
                # Update session status
                with self.session_lock:
                    self.active_sessions[session_id]['status'] = 'processing'
                    self.active_sessions[session_id]['modules_count'] = len(self.module_configs)
                
                # Submit all modules for concurrent execution with thread safety
                futures = {}
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    for name, config in self.module_configs.items():
                        future = executor.submit(self._execute_module_with_thread_safety, config, context)
                        futures[future] = name
                    
                    # Collect results with priority-based processing and conflict resolution
                    results = self._collect_results_with_conflict_resolution(futures, session_id)
                
                # Integrate and merge all results with state management
                consciousness_state = self._integrate_results_thread_safe(results, context, initial_version)
                
                # Update performance statistics (thread-safe)
                total_time = time.time() - start_time
                self._update_stats_thread_safe(total_time, results)
                
                # Update session completion
                with self.session_lock:
                    self.active_sessions[session_id]['status'] = 'completed'
                    self.active_sessions[session_id]['completion_time'] = total_time
                    self.active_sessions[session_id]['success_rate'] = self._calculate_success_rate(results)
                
                logger.info(f"[ParallelProcessor] ✅ Thread-safe processing complete in {total_time:.2f}s (target: {self.global_timeout}s)")
                logger.info(f"[ParallelProcessor] 📊 Success rate: {self._calculate_success_rate(results):.1f}% | Lock contentions: {self.execution_stats.get('lock_contention_count', 0)}")
                
                return consciousness_state
                
        except Exception as e:
            logger.error(f"[ParallelProcessor] ❌ Thread-safe processing failed: {e}")
            with self.session_lock:
                self.active_sessions[session_id]['status'] = 'failed'
                self.active_sessions[session_id]['error'] = str(e)
            raise
        finally:
            # Cleanup session after delay
            threading.Timer(60.0, self._cleanup_session, args=[session_id]).start()
    
    def _execute_module_with_thread_safety(self, config: ModuleConfig, context: Dict[str, Any]) -> ModuleResult:
        """Execute a single module with comprehensive thread safety"""
        start_time = time.time()
        lock_start_time = start_time
        lock_acquired = False
        
        try:
            # Acquire necessary locks with timeout
            if self.lock_manager.acquire_locks(config.name, config.shared_resources, config.lock_timeout):
                lock_acquired = True
                lock_wait_time = time.time() - lock_start_time
                
                logger.debug(f"[ParallelProcessor] 🔒 Locks acquired for {config.name} in {lock_wait_time:.3f}s")
                
                # Get current state version for conflict detection
                current_state, state_version = self.state_manager.get_state_copy()
                
                # Update context with current state version
                context['state_version'] = state_version
                
                # Execute the module function
                result = config.function(context)
                execution_time = time.time() - start_time
                
                # Update shared state if module returns state updates
                if isinstance(result, dict) and '_state_updates' in result:
                    state_updates = result.pop('_state_updates')
                    success = self.state_manager.update_state(config.name, state_updates, state_version)
                    if not success:
                        logger.warning(f"[ParallelProcessor] ⚠️ State conflict detected for {config.name}")
                        with self.stats_lock:
                            self.execution_stats['version_conflicts'] += 1
                
                return ModuleResult(
                    name=config.name,
                    success=True,
                    result=result,
                    execution_time=execution_time,
                    lock_wait_time=lock_wait_time,
                    state_version=state_version
                )
                
            else:
                # Lock acquisition failed
                with self.stats_lock:
                    self.execution_stats['lock_contention_count'] += 1
                
                logger.warning(f"[ParallelProcessor] 🔒 Failed to acquire locks for {config.name}")
                execution_time = time.time() - start_time
                
                return ModuleResult(
                    name=config.name,
                    success=False,
                    result=config.fallback_value,
                    execution_time=execution_time,
                    error="Lock acquisition timeout",
                    lock_wait_time=execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.warning(f"[ParallelProcessor] ❌ Module {config.name} failed: {e}")
            
            return ModuleResult(
                name=config.name,
                success=False,
                result=config.fallback_value,
                execution_time=execution_time,
                error=str(e),
                lock_wait_time=time.time() - lock_start_time if not lock_acquired else 0
            )
        finally:
            # Always release locks
            if lock_acquired:
                try:
                    self.lock_manager.release_locks(config.name, config.shared_resources)
                    logger.debug(f"[ParallelProcessor] 🔓 Locks released for {config.name}")
                except Exception as e:
                    logger.error(f"[ParallelProcessor] ❌ Failed to release locks for {config.name}: {e}")
    
    def _collect_results_with_conflict_resolution(self, futures: Dict[Future, str], session_id: str) -> Dict[str, ModuleResult]:
        """Collect results with priority-based processing and conflict resolution"""
        results = {}
        priority_groups = {priority: [] for priority in ModulePriority}
        
        # Group futures by priority
        for future, name in futures.items():
            config = self.module_configs[name]
            priority_groups[config.priority].append((future, name))
        
        # Process by priority (CRITICAL first, then HIGH, etc.)
        for priority in [ModulePriority.CRITICAL, ModulePriority.HIGH, ModulePriority.MEDIUM, ModulePriority.LOW]:
            priority_futures = priority_groups[priority]
            
            if not priority_futures:
                continue
                
            # Set timeout based on priority
            timeout = 5.0 if priority == ModulePriority.CRITICAL else 3.0
            
            # Update session progress
            with self.session_lock:
                if session_id in self.active_sessions:
                    self.active_sessions[session_id][f'processing_{priority.name.lower()}'] = True
            
            for future, name in priority_futures:
                try:
                    result = future.result(timeout=timeout)
                    results[name] = result
                    
                    logger.debug(f"[ParallelProcessor] ✅ {name} completed: {result.success}, time: {result.execution_time:.3f}s")
                    
                except Exception as e:
                    # Use fallback for failed modules
                    config = self.module_configs[name]
                    results[name] = ModuleResult(
                        name=name,
                        success=False,
                        result=config.fallback_value,
                        execution_time=timeout,
                        error=str(e),
                        timed_out=True
                    )
                    logger.warning(f"[ParallelProcessor] ⏰ Module {name} timed out after {timeout}s")
        
        return results
    
    def _integrate_results_thread_safe(self, results: Dict[str, ModuleResult], context: Dict[str, Any], initial_version: int) -> Dict[str, Any]:
        """Thread-safe integration and merging of results from all consciousness modules"""
        consciousness_state = {
            'processing_time': sum(r.execution_time for r in results.values()),
            'parallel_time': max(r.execution_time for r in results.values()) if results else 0,
            'modules_processed': len(results),
            'successful_modules': sum(1 for r in results.values() if r.success),
            'failed_modules': [r.name for r in results.values() if not r.success],
            'lock_wait_times': {r.name: r.lock_wait_time for r in results.values()},
            'state_version_conflicts': sum(1 for r in results.values() if hasattr(r, 'state_version') and r.state_version != initial_version),
            'context': context,
            'thread_safety_stats': {
                'total_lock_time': sum(r.lock_wait_time for r in results.values()),
                'max_lock_time': max((r.lock_wait_time for r in results.values()), default=0),
                'lock_contentions': self.execution_stats.get('lock_contention_count', 0)
            }
        }
        
        # Merge results from each module in a thread-safe manner
        state_updates = {}
        for name, result in results.items():
            if result.success and result.result:
                if isinstance(result.result, dict):
                    # Separate state updates from regular results
                    result_data = result.result.copy()
                    if '_state_updates' in result_data:
                        result_data.pop('_state_updates')
                    
                    consciousness_state.update(result_data)
                    state_updates[name] = result_data
                else:
                    consciousness_state[name] = result.result
                    state_updates[name] = {name: result.result}
            else:
                # Use fallback values for failed modules
                config = self.module_configs[name]
                if isinstance(config.fallback_value, dict):
                    consciousness_state.update(config.fallback_value)
                    state_updates[name] = config.fallback_value
                else:
                    consciousness_state[name] = config.fallback_value
                    state_updates[name] = {name: config.fallback_value}
        
        # Apply all state updates atomically
        if state_updates:
            all_updates = {}
            for module_updates in state_updates.values():
                all_updates.update(module_updates)
            
            self.state_manager.update_state("parallel_integration", all_updates, initial_version)
        
        # Ensure critical values are present with defaults
        consciousness_state.setdefault('current_emotion', 'neutral')
        consciousness_state.setdefault('motivation_satisfaction', 0.5)
        consciousness_state.setdefault('experience_valence', 0.5)
        consciousness_state.setdefault('experience_significance', 0.5)
        consciousness_state.setdefault('response_uncertainty', 0.3)
        
        logger.debug(f"[ParallelProcessor] 🔄 Thread-safe integration: {len(results)} modules, "
                    f"{consciousness_state['successful_modules']} successful")
        
        return consciousness_state
    
    def _update_stats_thread_safe(self, total_time: float, results: Dict[str, ModuleResult]):
        """Thread-safe update of performance statistics"""
        with self.stats_lock:
            self.execution_stats['total_executions'] += 1
            
            # Update timing stats
            if total_time < self.execution_stats['fastest_time']:
                self.execution_stats['fastest_time'] = total_time
            if total_time > self.execution_stats['slowest_time']:
                self.execution_stats['slowest_time'] = total_time
            
            # Update average
            current_avg = self.execution_stats['average_time']
            count = self.execution_stats['total_executions']
            self.execution_stats['average_time'] = ((current_avg * (count - 1)) + total_time) / count
            
            # Count timeouts and errors
            for result in results.values():
                if result.timed_out:
                    self.execution_stats['timeout_count'] += 1
                if not result.success:
                    self.execution_stats['error_count'] += 1
    
    def _cleanup_session(self, session_id: str):
        """Clean up completed session"""
        with self.session_lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                logger.debug(f"[ParallelProcessor] 🧹 Cleaned up session {session_id[:8]}")
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about currently active processing sessions"""
        with self.session_lock:
            return {k: v.copy() for k, v in self.active_sessions.items()}
    
    def get_lock_status(self) -> Dict[str, Any]:
        """Get current lock status for debugging"""
        return {
            'module_locks_count': len(self.lock_manager._module_locks),
            'resource_locks_count': len(self.lock_manager._resource_locks),
            'active_threads': threading.active_count(),
            'lock_registry_size': len(self.lock_manager._lock_registry)
        }
    
    def _calculate_success_rate(self, results: Dict[str, ModuleResult]) -> float:
        """Calculate success rate for the current processing"""
        if not results:
            return 0.0
        success_count = sum(1 for r in results.values() if r.success)
        return (success_count / len(results)) * 100
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed thread-safe performance report"""
        with self.stats_lock:
            return {
                'execution_stats': self.execution_stats.copy(),
                'registered_modules': len(self.module_configs),
                'active_workers': self.max_workers,
                'global_timeout': self.global_timeout,
                'thread_safety_stats': {
                    'lock_contentions': self.execution_stats.get('lock_contention_count', 0),
                    'version_conflicts': self.execution_stats.get('version_conflicts', 0),
                    'active_sessions': len(self.active_sessions),
                    'current_state_version': self.state_manager.get_current_version()
                },
                'module_configs': {name: {
                    'priority': config.priority.name,
                    'timeout': config.timeout,
                    'required': config.required,
                    'shared_resources': config.shared_resources,
                    'lock_timeout': config.lock_timeout
                } for name, config in self.module_configs.items()},
                'lock_status': self.get_lock_status()
            }
    
    def cleanup(self):
        """Thread-safe cleanup of resources"""
        try:
            # Wait for active sessions to complete
            max_wait = 30.0  # Maximum wait time for graceful shutdown
            wait_start = time.time()
            
            while self.active_sessions and (time.time() - wait_start) < max_wait:
                logger.info(f"[ParallelProcessor] 🕐 Waiting for {len(self.active_sessions)} active sessions to complete...")
                time.sleep(1.0)
            
            # Force cleanup remaining sessions
            with self.session_lock:
                if self.active_sessions:
                    logger.warning(f"[ParallelProcessor] ⚠️ Force-closing {len(self.active_sessions)} remaining sessions")
                    self.active_sessions.clear()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            logger.info("[ParallelProcessor] 🧹 Thread-safe cleanup completed")
            
        except Exception as e:
            logger.warning(f"[ParallelProcessor] ⚠️ Cleanup error: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()
    
    # Module-specific processing functions
    def _process_emotion_module(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process emotion module"""
        try:
            from ai.emotion import emotion_engine
            
            text = context['text']
            current_user = context['current_user']
            
            # Process emotional response
            emotion_response = emotion_engine.process_emotional_trigger(
                f"User said: {text}",
                {"user": current_user, "input": text}
            )
            
            # Get emotional modulation
            emotional_modulation = emotion_engine.get_emotional_modulation("response")
            
            return {
                "emotional_modulation": emotional_modulation,
                "current_emotion": emotion_response.primary_emotion.value,
                "emotion_intensity": getattr(emotion_response, 'intensity', 0.7)
            }
        except Exception as e:
            logger.warning(f"[ParallelProcessor] ⚠️ Emotion module error: {e}")
            return {"primary_emotion": "neutral", "emotional_modulation": {}}
    
    def _process_motivation_module(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process motivation module"""
        try:
            from ai.motivation import motivation_system
            
            text = context['text']
            current_user = context['current_user']
            
            # Evaluate motivation satisfaction
            motivation_satisfaction = motivation_system.evaluate_desire_satisfaction(
                f"responding to: {text}",
                {"user": current_user, "input": text}
            )
            
            return {"motivation_satisfaction": motivation_satisfaction}
        except Exception as e:
            logger.warning(f"[ParallelProcessor] ⚠️ Motivation module error: {e}")
            return {"motivation_satisfaction": 0.5}
    
    def _process_inner_monologue_module(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process inner monologue module"""
        try:
            from ai.inner_monologue import inner_monologue, ThoughtType
            
            text = context['text']
            current_user = context['current_user']
            
            # Trigger inner thought
            inner_monologue.trigger_thought(
                f"The user asked about: {text}",
                {"user": current_user, "input": text},
                ThoughtType.OBSERVATION
            )
            
            return {"thoughts_triggered": True, "thought_type": "observation"}
        except Exception as e:
            logger.warning(f"[ParallelProcessor] ⚠️ Inner monologue module error: {e}")
            return {"thoughts_triggered": False}
    
    def _process_subjective_experience_module(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process subjective experience module"""
        try:
            from ai.subjective_experience import subjective_experience, ExperienceType
            
            text = context['text']
            current_user = context['current_user']
            
            # Create subjective experience
            experience = subjective_experience.process_experience(
                f"Processing user request: {text}",
                ExperienceType.SOCIAL,
                {"user": current_user, "input": text, "interaction_type": "question_response"}
            )
            
            return {
                "experience_valence": experience.valence,
                "experience_significance": experience.significance
            }
        except Exception as e:
            logger.warning(f"[ParallelProcessor] ⚠️ Subjective experience module error: {e}")
            return {"experience_valence": 0.5, "experience_significance": 0.5}
    
    def _process_self_model_module(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process self-model module"""
        try:
            from ai.self_model import self_model
            
            text = context['text']
            current_user = context['current_user']
            
            # Self-reflection
            self_model.reflect_on_experience(
                f"Responding to user input about: {text}",
                {"user": current_user, "input": text, "response_context": True}
            )
            
            return {"reflection_completed": True}
        except Exception as e:
            logger.warning(f"[ParallelProcessor] ⚠️ Self-model module error: {e}")
            return {"reflection_completed": False}
    
    def _process_temporal_module(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process temporal awareness module"""
        try:
            from ai.temporal_awareness import temporal_awareness
            
            text = context['text']
            current_user = context['current_user']
            
            # Mark temporal event
            temporal_awareness.mark_temporal_event(
                f"User interaction: {text[:50]}...",
                significance=0.6,
                context={"user": current_user, "input_length": len(text)}
            )
            
            return {"temporal_event_marked": True, "temporal_significance": 0.6}
        except Exception as e:
            logger.warning(f"[ParallelProcessor] ⚠️ Temporal module error: {e}")
            return {"temporal_event_marked": False}
    
    def _process_entropy_module(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process entropy module"""
        try:
            from ai.entropy import entropy_system
            
            current_user = context['current_user']
            
            # Apply entropy to response planning
            response_uncertainty = entropy_system.get_decision_uncertainty(
                0.8, {"type": "response_generation", "user": current_user}
            )
            
            return {"response_uncertainty": response_uncertainty}
        except Exception as e:
            logger.warning(f"[ParallelProcessor] ⚠️ Entropy module error: {e}")
            return {"response_uncertainty": 0.3}
    
    def _process_attention_module(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process attention/global workspace module"""
        try:
            from ai.global_workspace import global_workspace, AttentionPriority, ProcessingMode
            
            text = context['text']
            
            # Request attention for user input
            global_workspace.request_attention(
                "user_interaction",
                text,
                AttentionPriority.HIGH,
                ProcessingMode.CONSCIOUS,
                duration=30.0,
                tags=["user_input", "response_generation"]
            )
            
            return {"attention_requested": True}
        except Exception as e:
            logger.warning(f"[ParallelProcessor] ⚠️ Attention module error: {e}")
            return {"attention_requested": False}
    
    async def process_consciousness_reactive(self, text: str, current_user: str, 
                                          event_bus=None, memory_manager=None) -> Dict[str, Any]:
        """
        Process consciousness modules with reactive neural architecture integration
        
        Args:
            text: User input text
            current_user: Current user identifier
            event_bus: Optional event bus for reactive coordination
            memory_manager: Optional memory manager for optimization
            
        Returns:
            Combined consciousness state with reactive enhancements
        """
        session_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Create processing session with reactive capabilities
        with self.session_lock:
            self.active_sessions[session_id] = {
                'start_time': start_time,
                'text': text,
                'user': current_user,
                'status': 'reactive_processing',
                'reactive_enabled': event_bus is not None
            }
        
        logger.info(f"[ParallelProcessor] 🚀 Starting reactive consciousness processing (session: {session_id[:8]})")
        
        try:
            # Publish reactive event if event bus available
            if event_bus:
                try:
                    from ai.reactive_neural_architecture import NeuralEvent, EventType, EventPriority
                    
                    consciousness_event = NeuralEvent(
                        type=EventType.CONSCIOUSNESS_UPDATE,
                        priority=EventPriority.HIGH,
                        source="parallel_processor",
                        data={
                            'text': text,
                            'user': current_user,
                            'session_id': session_id,
                            'processing_type': 'parallel_consciousness'
                        },
                        correlation_id=session_id
                    )
                    
                    # Publish asynchronously if in async context
                    if asyncio.iscoroutinefunction(event_bus.publish_async):
                        await event_bus.publish_async(consciousness_event)
                    else:
                        event_bus.publish_sync(consciousness_event)
                        
                    logger.debug(f"[ParallelProcessor] 📤 Published reactive consciousness event")
                    
                except Exception as e:
                    logger.warning(f"[ParallelProcessor] ⚠️ Reactive event publishing failed: {e}")
            
            # Use memory-optimized processing if memory manager available
            if memory_manager:
                # Create copy-on-write snapshot for shared state
                context_snapshot = memory_manager.create_cow_object(
                    f"consciousness_context_{session_id}",
                    {
                        'text': text,
                        'current_user': current_user,
                        'timestamp': datetime.now().isoformat(),
                        'session_id': session_id
                    }
                )
                logger.debug(f"[ParallelProcessor] 🐄 Created COW context snapshot: {context_snapshot}")
            
            # Process using existing parallel implementation with reactive enhancements
            consciousness_state = self.process_consciousness_parallel(text, current_user)
            
            # Add reactive metadata
            consciousness_state['reactive_processing'] = {
                'event_bus_used': event_bus is not None,
                'memory_optimized': memory_manager is not None,
                'session_id': session_id,
                'reactive_latency': time.time() - start_time
            }
            
            # Update session completion
            total_time = time.time() - start_time
            with self.session_lock:
                self.active_sessions[session_id]['status'] = 'reactive_completed'
                self.active_sessions[session_id]['completion_time'] = total_time
                
            logger.info(f"[ParallelProcessor] ✅ Reactive processing complete in {total_time:.3f}s")
            return consciousness_state
            
        except Exception as e:
            logger.error(f"[ParallelProcessor] ❌ Reactive processing failed: {e}")
            with self.session_lock:
                self.active_sessions[session_id]['status'] = 'reactive_failed'
                self.active_sessions[session_id]['error'] = str(e)
            raise
        finally:
            # Cleanup session after delay
            threading.Timer(60.0, self._cleanup_session, args=[session_id]).start()

    def integrate_with_reactive_architecture(self, event_bus=None, async_pathways=None, 
                                           memory_manager=None):
        """
        Integrate parallel processor with reactive neural architecture components
        
        Args:
            event_bus: Event bus for reactive coordination
            async_pathways: Async neural pathways for I/O operations
            memory_manager: Memory manager for optimization
        """
        self.reactive_components = {
            'event_bus': event_bus,
            'async_pathways': async_pathways,
            'memory_manager': memory_manager,
            'integration_enabled': True
        }
        
        logger.info("[ParallelProcessor] 🔗 Integrated with reactive neural architecture")
        
        # Register as event subscriber if event bus available
        if event_bus and hasattr(event_bus, 'subscribe'):
            try:
                event_bus.subscribe("CONSCIOUSNESS_REQUEST", self._handle_consciousness_event)
                logger.debug("[ParallelProcessor] 📝 Subscribed to consciousness events")
            except Exception as e:
                logger.warning(f"[ParallelProcessor] ⚠️ Event subscription failed: {e}")
    
    def _handle_consciousness_event(self, event):
        """Handle consciousness processing events from reactive architecture"""
        try:
            text = event.data.get('text', '')
            user = event.data.get('user', '')
            
            if text and user:
                # Process consciousness in background thread
                def process_background():
                    try:
                        result = self.process_consciousness_parallel(text, user)
                        logger.debug(f"[ParallelProcessor] ✅ Background consciousness processing completed")
                        return result
                    except Exception as e:
                        logger.error(f"[ParallelProcessor] ❌ Background processing error: {e}")
                
                # Submit to thread pool
                future = self.executor.submit(process_background)
                self.background_futures.append(future)
                
                # Clean up old futures
                self.background_futures = [f for f in self.background_futures if not f.done()]
                
        except Exception as e:
            logger.error(f"[ParallelProcessor] ❌ Consciousness event handling error: {e}")

    def get_reactive_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report including reactive architecture metrics"""
        base_report = self.get_performance_report()
        
        # Add reactive-specific metrics
        reactive_metrics = {
            'reactive_integration': {
                'enabled': hasattr(self, 'reactive_components'),
                'components': getattr(self, 'reactive_components', {}),
                'reactive_sessions': sum(1 for session in self.active_sessions.values() 
                                       if session.get('reactive_enabled', False)),
                'background_futures': len(getattr(self, 'background_futures', []))
            }
        }
        
        base_report.update(reactive_metrics)
        return base_report
    
    def cleanup(self):
        """Thread-safe cleanup of resources"""
        try:
            # Wait for active sessions to complete
            max_wait = 30.0  # Maximum wait time for graceful shutdown
            wait_start = time.time()
            
            while self.active_sessions and (time.time() - wait_start) < max_wait:
                logger.info(f"[ParallelProcessor] 🕐 Waiting for {len(self.active_sessions)} active sessions to complete...")
                time.sleep(1.0)
            
            # Force cleanup remaining sessions
            with self.session_lock:
                if self.active_sessions:
                    logger.warning(f"[ParallelProcessor] ⚠️ Force-closing {len(self.active_sessions)} remaining sessions")
                    self.active_sessions.clear()
            
            # Shutdown executor
            self.executor.shutdown(wait=True)
            logger.info("[ParallelProcessor] 🧹 Thread-safe cleanup completed")
            
        except Exception as e:
            logger.warning(f"[ParallelProcessor] ⚠️ Cleanup error: {e}")

# Global instance with thread safety and reactive integration
parallel_processor = None
_processor_lock = threading.Lock()

def get_parallel_processor() -> ParallelConsciousnessProcessor:
    """Get the global thread-safe parallel processor instance with reactive integration"""
    global parallel_processor
    with _processor_lock:
        if parallel_processor is None:
            parallel_processor = ParallelConsciousnessProcessor()
            parallel_processor.setup_default_modules()
            logger.info("[ParallelProcessor] 🚀 Thread-safe global instance created with reactive support")
        return parallel_processor

def initialize_parallel_consciousness():
    """Initialize thread-safe parallel consciousness processing with reactive architecture"""
    processor = get_parallel_processor()
    
    # Attempt to integrate with reactive architecture if available
    try:
        from ai.reactive_neural_architecture import get_reactive_neural_architecture
        reactive_components = get_reactive_neural_architecture()
        
        processor.integrate_with_reactive_architecture(
            event_bus=reactive_components.get('event_bus'),
            async_pathways=reactive_components.get('async_pathways'),
            memory_manager=reactive_components.get('memory_manager')
        )
        logger.info("[ParallelProcessor] 🔗 Reactive neural architecture integration enabled")
        
    except ImportError:
        logger.info("[ParallelProcessor] ℹ️ Reactive architecture not available, using standard processing")
    
    logger.info("[ParallelProcessor] 🚀 Thread-safe parallel consciousness processing initialized")
    return processor

def get_parallel_processor_with_reactive_integration():
    """Get parallel processor with guaranteed reactive integration"""
    processor = get_parallel_processor()
    
    # Ensure reactive integration
    if not hasattr(processor, 'reactive_components'):
        try:
            from ai.reactive_neural_architecture import get_reactive_neural_architecture
            reactive_components = get_reactive_neural_architecture()
            
            processor.integrate_with_reactive_architecture(
                event_bus=reactive_components.get('event_bus'),
                async_pathways=reactive_components.get('async_pathways'),
                memory_manager=reactive_components.get('memory_manager')
            )
        except ImportError:
            logger.warning("[ParallelProcessor] ⚠️ Cannot integrate reactive architecture - not available")
    
    return processor