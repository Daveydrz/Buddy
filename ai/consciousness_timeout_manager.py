"""
Consciousness Timeout Manager - Enhanced timeout handling and recovery for consciousness modules
Created: 2025-08-05
Purpose: Solve timeout issues with inner_monologue, subjective_experience, and other consciousness modules
"""

import time
import threading
import signal
import functools
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from concurrent.futures import ThreadPoolExecutor, TimeoutError as ConcurrentTimeoutError, Future
from contextlib import contextmanager
import weakref

T = TypeVar('T')

class ConsciousnessTimeout(Exception):
    """Custom exception for consciousness module timeouts"""
    pass

class TimeoutManager:
    """Manager for handling timeouts in consciousness modules with recovery mechanisms"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="consciousness_timeout")
        self.active_operations: Dict[str, Future] = {}
        self.timeout_stats: Dict[str, Dict[str, Any]] = {}
        self.recovery_callbacks: Dict[str, Callable] = {}
        self.lock = threading.Lock()
        
        # Default timeouts for different module types
        self.default_timeouts = {
            'inner_monologue': 3.0,
            'subjective_experience': 3.0,
            'belief_tracking': 2.0,
            'memory_operations': 5.0,
            'llm_operations': 30.0,
            'consciousness_integration': 10.0,
            'default': 5.0
        }
        
        # Timeout escalation strategies
        self.escalation_strategies = {
            'retry': self._retry_strategy,
            'fallback': self._fallback_strategy,
            'skip': self._skip_strategy,
            'emergency_stop': self._emergency_stop_strategy
        }
        
    def set_timeout(self, module_name: str, timeout: float):
        """Set custom timeout for a specific module"""
        self.default_timeouts[module_name] = timeout
        
    def register_recovery_callback(self, module_name: str, callback: Callable):
        """Register a recovery callback for a module"""
        self.recovery_callbacks[module_name] = callback
        
    def with_timeout(self, timeout: float = None, module_name: str = 'default', 
                    strategy: str = 'fallback'):
        """
        Decorator for adding timeout handling to functions.
        
        Args:
            timeout: Timeout in seconds (None to use default for module)
            module_name: Name of the module for tracking and recovery
            strategy: Timeout handling strategy ('retry', 'fallback', 'skip', 'emergency_stop')
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> T:
                effective_timeout = timeout or self.default_timeouts.get(module_name, self.default_timeouts['default'])
                return self.execute_with_timeout(
                    func, effective_timeout, module_name, strategy, *args, **kwargs
                )
            return wrapper
        return decorator
    
    def execute_with_timeout(self, func: Callable[..., T], timeout: float, 
                           module_name: str = 'default', strategy: str = 'fallback',
                           *args, **kwargs) -> T:
        """
        Execute a function with timeout and recovery handling.
        
        Args:
            func: Function to execute
            timeout: Timeout in seconds
            module_name: Name of the module for tracking
            strategy: Timeout handling strategy
            *args, **kwargs: Arguments for the function
            
        Returns:
            Result of the function call
            
        Raises:
            ConsciousnessTimeout: If timeout occurs and no recovery strategy works
        """
        operation_id = f"{module_name}_{int(time.time() * 1000)}"
        start_time = time.time()
        
        # Track the operation
        with self.lock:
            if module_name not in self.timeout_stats:
                self.timeout_stats[module_name] = {
                    'total_calls': 0,
                    'timeouts': 0,
                    'recoveries': 0,
                    'avg_execution_time': 0.0,
                    'last_timeout': None
                }
        
        try:
            # Submit to executor with timeout
            future = self.executor.submit(func, *args, **kwargs)
            self.active_operations[operation_id] = future
            
            try:
                result = future.result(timeout=timeout)
                execution_time = time.time() - start_time
                
                # Update stats
                with self.lock:
                    stats = self.timeout_stats[module_name]
                    stats['total_calls'] += 1
                    stats['avg_execution_time'] = (
                        (stats['avg_execution_time'] * (stats['total_calls'] - 1) + execution_time) /
                        stats['total_calls']
                    )
                
                return result
                
            except ConcurrentTimeoutError:
                # Handle timeout with specified strategy
                execution_time = time.time() - start_time
                print(f"[TimeoutManager] {module_name} timed out after {execution_time:.2f}s (limit: {timeout}s)")
                
                # Update timeout stats
                with self.lock:
                    stats = self.timeout_stats[module_name]
                    stats['total_calls'] += 1
                    stats['timeouts'] += 1
                    stats['last_timeout'] = time.time()
                
                # Cancel the operation
                future.cancel()
                
                # Apply escalation strategy
                return self._handle_timeout(func, module_name, strategy, execution_time, *args, **kwargs)
                
        finally:
            # Clean up
            self.active_operations.pop(operation_id, None)
    
    def _handle_timeout(self, func: Callable, module_name: str, strategy: str, 
                       execution_time: float, *args, **kwargs) -> Any:
        """Handle timeout with the specified strategy"""
        print(f"[TimeoutManager] Applying '{strategy}' strategy for {module_name}")
        
        if strategy in self.escalation_strategies:
            try:
                result = self.escalation_strategies[strategy](func, module_name, *args, **kwargs)
                
                # Update recovery stats
                with self.lock:
                    self.timeout_stats[module_name]['recoveries'] += 1
                
                return result
            except Exception as e:
                print(f"[TimeoutManager] {strategy} strategy failed for {module_name}: {e}")
        
        # If all strategies fail, raise timeout exception
        raise ConsciousnessTimeout(
            f"Module '{module_name}' timed out after {execution_time:.2f}s and recovery failed"
        )
    
    def _retry_strategy(self, func: Callable, module_name: str, *args, **kwargs) -> Any:
        """Retry strategy: attempt the operation again with longer timeout"""
        extended_timeout = self.default_timeouts.get(module_name, 5.0) * 2
        print(f"[TimeoutManager] Retrying {module_name} with extended timeout: {extended_timeout}s")
        
        try:
            future = self.executor.submit(func, *args, **kwargs)
            return future.result(timeout=extended_timeout)
        except ConcurrentTimeoutError:
            raise ConsciousnessTimeout(f"Retry failed for {module_name}")
    
    def _fallback_strategy(self, func: Callable, module_name: str, *args, **kwargs) -> Any:
        """Fallback strategy: use registered callback or return safe default"""
        if module_name in self.recovery_callbacks:
            print(f"[TimeoutManager] Using recovery callback for {module_name}")
            return self.recovery_callbacks[module_name](*args, **kwargs)
        
        # Return safe defaults based on module type
        fallback_results = {
            'inner_monologue': {'thoughts': [], 'current_focus': 'default', 'timeout_recovery': True},
            'subjective_experience': {'experience': 'neutral', 'valence': 0.0, 'timeout_recovery': True},
            'belief_tracking': {'beliefs': [], 'confidence': 0.5, 'timeout_recovery': True},
            'memory_operations': {'memories': [], 'context': 'timeout_recovery'},
            'consciousness_integration': {'status': 'partial', 'timeout_recovery': True}
        }
        
        result = fallback_results.get(module_name, {'timeout_recovery': True, 'status': 'fallback'})
        print(f"[TimeoutManager] Using fallback result for {module_name}: {result}")
        return result
    
    def _skip_strategy(self, func: Callable, module_name: str, *args, **kwargs) -> Any:
        """Skip strategy: return None and continue"""
        print(f"[TimeoutManager] Skipping {module_name} due to timeout")
        return None
    
    def _emergency_stop_strategy(self, func: Callable, module_name: str, *args, **kwargs) -> Any:
        """Emergency stop strategy: halt the operation and raise exception"""
        print(f"[TimeoutManager] Emergency stop triggered for {module_name}")
        raise ConsciousnessTimeout(f"Emergency stop: {module_name} timeout")
    
    @contextmanager
    def timeout_context(self, timeout: float, module_name: str = 'default'):
        """
        Context manager for timeout handling.
        
        Usage:
            with timeout_manager.timeout_context(5.0, 'my_module'):
                # Code that might timeout
                result = some_long_operation()
        """
        operation_id = f"context_{module_name}_{int(time.time() * 1000)}"
        start_time = time.time()
        
        # Set up timeout using signal (Unix-like systems only)
        def timeout_handler(signum, frame):
            raise ConsciousnessTimeout(f"Context timeout for {module_name} after {timeout}s")
        
        old_handler = None
        try:
            # Only use signal on Unix-like systems
            if hasattr(signal, 'SIGALRM'):
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(timeout))
            
            yield
            
        except ConsciousnessTimeout:
            execution_time = time.time() - start_time
            print(f"[TimeoutManager] Context timeout for {module_name} after {execution_time:.2f}s")
            raise
            
        finally:
            # Clean up signal handler
            if hasattr(signal, 'SIGALRM') and old_handler is not None:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
    
    def cancel_operation(self, module_name: str) -> bool:
        """Cancel any running operations for a module"""
        cancelled = False
        operations_to_cancel = [
            (op_id, future) for op_id, future in self.active_operations.items()
            if op_id.startswith(f"{module_name}_")
        ]
        
        for op_id, future in operations_to_cancel:
            if future.cancel():
                cancelled = True
                print(f"[TimeoutManager] Cancelled operation {op_id}")
                
        return cancelled
    
    def get_stats(self) -> Dict[str, Any]:
        """Get timeout statistics for all modules"""
        with self.lock:
            stats = {}
            for module_name, module_stats in self.timeout_stats.items():
                stats[module_name] = {
                    **module_stats,
                    'timeout_rate': (
                        module_stats['timeouts'] / max(1, module_stats['total_calls'])
                    ),
                    'recovery_rate': (
                        module_stats['recoveries'] / max(1, module_stats['timeouts'])
                    ) if module_stats['timeouts'] > 0 else 0.0
                }
            
            return {
                'module_stats': stats,
                'active_operations': len(self.active_operations),
                'default_timeouts': self.default_timeouts
            }
    
    def adjust_timeout_based_on_performance(self, module_name: str):
        """Automatically adjust timeout based on historical performance"""
        if module_name not in self.timeout_stats:
            return
            
        stats = self.timeout_stats[module_name]
        if stats['total_calls'] < 5:  # Need sufficient data
            return
            
        avg_time = stats['avg_execution_time']
        timeout_rate = stats['timeouts'] / stats['total_calls']
        
        # If timeout rate is high, increase timeout
        if timeout_rate > 0.2:  # More than 20% timeouts
            new_timeout = avg_time * 3.0  # Give 3x average time
            self.default_timeouts[module_name] = new_timeout
            print(f"[TimeoutManager] Increased timeout for {module_name} to {new_timeout:.2f}s")
        
        # If timeout rate is very low and avg time is much less than timeout, decrease
        elif timeout_rate < 0.05 and avg_time < self.default_timeouts[module_name] * 0.5:
            new_timeout = max(avg_time * 2.0, 1.0)  # At least 1 second
            self.default_timeouts[module_name] = new_timeout
            print(f"[TimeoutManager] Decreased timeout for {module_name} to {new_timeout:.2f}s")
    
    def cleanup(self):
        """Clean up the timeout manager"""
        # Cancel all active operations
        for op_id, future in list(self.active_operations.items()):
            future.cancel()
            
        # Shutdown executor
        self.executor.shutdown(wait=True)
        print("[TimeoutManager] ✅ Cleanup completed")

# Global timeout manager instance
timeout_manager = TimeoutManager()

# Convenience functions
def with_consciousness_timeout(timeout: float = None, module_name: str = 'default', 
                             strategy: str = 'fallback'):
    """
    Decorator for consciousness modules to handle timeouts.
    
    Usage:
        @with_consciousness_timeout(3.0, 'inner_monologue', 'fallback')
        def generate_inner_thoughts():
            return some_complex_operation()
    """
    return timeout_manager.with_timeout(timeout, module_name, strategy)

def safe_consciousness_call(func: Callable[..., T], timeout: float = None, 
                          module_name: str = 'default', *args, **kwargs) -> Optional[T]:
    """
    Safely call a consciousness function with timeout handling.
    
    Returns None if timeout occurs and fallback fails.
    """
    try:
        effective_timeout = timeout or timeout_manager.default_timeouts.get(module_name, 5.0)
        return timeout_manager.execute_with_timeout(
            func, effective_timeout, module_name, 'fallback', *args, **kwargs
        )
    except ConsciousnessTimeout as e:
        print(f"[TimeoutManager] Safe call failed for {module_name}: {e}")
        return None

# Register common recovery callbacks
def inner_monologue_recovery(*args, **kwargs):
    """Recovery for inner monologue timeouts"""
    return {
        'thoughts': ['Processing...', 'Recovering from timeout...'],
        'current_focus': 'recovery_mode',
        'timeout_recovery': True
    }

def subjective_experience_recovery(*args, **kwargs):
    """Recovery for subjective experience timeouts"""
    return {
        'experience': 'recovering',
        'valence': 0.0,
        'significance': 0.3,
        'timeout_recovery': True
    }

def belief_tracking_recovery(*args, **kwargs):
    """Recovery for belief tracking timeouts"""
    return {
        'beliefs': [],
        'confidence': 0.5,
        'status': 'timeout_recovery',
        'timeout_recovery': True
    }

# Register recovery callbacks
timeout_manager.register_recovery_callback('inner_monologue', inner_monologue_recovery)
timeout_manager.register_recovery_callback('subjective_experience', subjective_experience_recovery)
timeout_manager.register_recovery_callback('belief_tracking', belief_tracking_recovery)

# Clean up on exit
import atexit
atexit.register(timeout_manager.cleanup)

print("[TimeoutManager] ✅ Consciousness timeout management system initialized")