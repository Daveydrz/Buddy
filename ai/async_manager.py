"""
AsyncManager - Thread-safe event loop handling for Buddy System
Created: 2025-08-05
Purpose: Solve "Task got Future attached to a different loop" errors by providing
         centralized async event loop management across threads
"""

import asyncio
import threading
import time
import functools
import weakref
from typing import Any, Callable, Coroutine, Dict, Optional, TypeVar, Union
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError as ConcurrentTimeoutError
import logging

T = TypeVar('T')

class AsyncManager:
    """
    Central manager for async operations across threads.
    Prevents "Task got Future attached to a different loop" errors.
    """
    
    def __init__(self):
        self._main_loop: Optional[asyncio.AbstractEventLoop] = None
        self._main_thread_id: Optional[int] = None
        self._thread_loops: Dict[int, asyncio.AbstractEventLoop] = {}
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="buddy_async")
        self._lock = threading.Lock()
        self._running = True
        
        # Try to get current loop if available
        try:
            self._main_loop = asyncio.get_running_loop()
            self._main_thread_id = threading.get_ident()
        except RuntimeError:
            # No loop running, will create one when needed
            pass
            
    def ensure_loop(self) -> asyncio.AbstractEventLoop:
        """Ensure there's an event loop for the current thread"""
        current_thread = threading.get_ident()
        
        # Check if we're in the main thread with a loop
        if current_thread == self._main_thread_id and self._main_loop:
            return self._main_loop
            
        # Check for existing loop in current thread
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            pass
            
        # Create new loop for this thread if needed
        with self._lock:
            if current_thread not in self._thread_loops:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self._thread_loops[current_thread] = loop
                
                # Start the loop in a separate thread if it's not the main thread
                if current_thread != self._main_thread_id:
                    def run_loop():
                        try:
                            loop.run_forever()
                        except Exception as e:
                            print(f"[AsyncManager] Thread loop error: {e}")
                        finally:
                            loop.close()
                    
                    loop_thread = threading.Thread(target=run_loop, daemon=True)
                    loop_thread.start()
                    
            return self._thread_loops[current_thread]
    
    def run_in_thread_safe(self, coro: Coroutine[Any, Any, T], timeout: float = 30.0) -> T:
        """
        Run a coroutine in a thread-safe manner.
        
        Args:
            coro: The coroutine to run
            timeout: Maximum time to wait for completion
            
        Returns:
            The result of the coroutine
            
        Raises:
            TimeoutError: If the operation times out
            Exception: Any exception raised by the coroutine
        """
        current_thread = threading.get_ident()
        
        # If we're already in an async context, run directly
        try:
            current_loop = asyncio.get_running_loop()
            if current_loop and not current_loop.is_closed():
                # Create a task in the current loop
                task = current_loop.create_task(coro)
                return self._wait_for_task(task, timeout)
        except RuntimeError:
            pass
        
        # Run in executor to avoid loop conflicts
        future = self._executor.submit(self._run_coro_in_new_loop, coro, timeout)
        try:
            return future.result(timeout=timeout + 1.0)  # Extra buffer for executor
        except ConcurrentTimeoutError:
            raise TimeoutError(f"Async operation timed out after {timeout}s")
    
    def _run_coro_in_new_loop(self, coro: Coroutine[Any, Any, T], timeout: float) -> T:
        """Run coroutine in a new event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(asyncio.wait_for(coro, timeout=timeout))
        finally:
            loop.close()
    
    def _wait_for_task(self, task: asyncio.Task, timeout: float) -> T:
        """Wait for a task with timeout"""
        try:
            # Use asyncio.wait_for for timeout handling
            loop = task.get_loop()
            if loop.is_running():
                # If loop is running, we need to handle this differently
                done = threading.Event()
                result = None
                exception = None
                
                def on_done(task):
                    nonlocal result, exception
                    try:
                        result = task.result()
                    except Exception as e:
                        exception = e
                    done.set()
                
                task.add_done_callback(on_done)
                
                if done.wait(timeout):
                    if exception:
                        raise exception
                    return result
                else:
                    task.cancel()
                    raise TimeoutError(f"Task timed out after {timeout}s")
            else:
                # Loop not running, can run directly
                return loop.run_until_complete(asyncio.wait_for(task, timeout=timeout))
        except asyncio.TimeoutError:
            raise TimeoutError(f"Task timed out after {timeout}s")
    
    def submit_async(self, coro: Coroutine[Any, Any, T], timeout: float = 30.0) -> Future[T]:
        """
        Submit a coroutine for async execution and return a Future.
        
        Args:
            coro: The coroutine to run
            timeout: Maximum time to wait for completion
            
        Returns:
            A Future that will contain the result
        """
        return self._executor.submit(self.run_in_thread_safe, coro, timeout)
    
    def safe_async_call(self, func: Callable[..., Coroutine[Any, Any, T]], *args, timeout: float = 30.0, **kwargs) -> T:
        """
        Safely call an async function from any thread context.
        
        Args:
            func: The async function to call
            *args: Positional arguments for the function
            timeout: Maximum time to wait for completion
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the function call
        """
        coro = func(*args, **kwargs)
        return self.run_in_thread_safe(coro, timeout)
    
    def create_task_safe(self, coro: Coroutine[Any, Any, T], name: Optional[str] = None) -> asyncio.Task[T]:
        """
        Create a task in a thread-safe manner.
        
        Args:
            coro: The coroutine to create a task for
            name: Optional name for the task
            
        Returns:
            The created task
        """
        loop = self.ensure_loop()
        
        if name:
            return loop.create_task(coro, name=name)
        else:
            return loop.create_task(coro)
    
    def run_until_complete_safe(self, coro: Coroutine[Any, Any, T], timeout: float = 30.0) -> T:
        """
        Run coroutine until complete in a thread-safe manner.
        
        Args:
            coro: The coroutine to run
            timeout: Maximum time to wait for completion
            
        Returns:
            The result of the coroutine
        """
        return self.run_in_thread_safe(coro, timeout)
    
    def is_async_context(self) -> bool:
        """Check if we're currently in an async context"""
        try:
            asyncio.get_running_loop()
            return True
        except RuntimeError:
            return False
    
    def cleanup(self):
        """Clean up the async manager"""
        self._running = False
        
        # Close all thread loops
        for thread_id, loop in self._thread_loops.items():
            if not loop.is_closed():
                loop.call_soon_threadsafe(loop.stop)
        
        # Shutdown executor
        self._executor.shutdown(wait=True)
        
        print("[AsyncManager] ✅ Cleanup completed")

    def get_stats(self) -> Dict[str, Any]:
        """Get async manager statistics"""
        return {
            "main_loop_active": self._main_loop is not None and not self._main_loop.is_closed(),
            "thread_loops_count": len(self._thread_loops),
            "executor_active": not self._executor._shutdown,
            "current_thread_id": threading.get_ident(),
            "main_thread_id": self._main_thread_id,
            "is_async_context": self.is_async_context()
        }

# Global async manager instance
async_manager = AsyncManager()

def async_safe(timeout: float = 30.0):
    """
    Decorator to make any async function thread-safe.
    
    Usage:
        @async_safe(timeout=10.0)
        async def my_async_function():
            return await some_async_operation()
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            coro = func(*args, **kwargs)
            return async_manager.run_in_thread_safe(coro, timeout)
        return wrapper
    return decorator

def run_async_safe(coro: Coroutine[Any, Any, T], timeout: float = 30.0) -> T:
    """
    Convenience function to run a coroutine safely.
    
    Args:
        coro: The coroutine to run
        timeout: Maximum time to wait for completion
        
    Returns:
        The result of the coroutine
    """
    return async_manager.run_in_thread_safe(coro, timeout)

def submit_async_safe(coro: Coroutine[Any, Any, T], timeout: float = 30.0) -> Future[T]:
    """
    Convenience function to submit a coroutine for async execution.
    
    Args:
        coro: The coroutine to run
        timeout: Maximum time to wait for completion
        
    Returns:
        A Future that will contain the result
    """
    return async_manager.submit_async(coro, timeout)

# Cleanup on module unload
import atexit
atexit.register(async_manager.cleanup)

print("[AsyncManager] ✅ Thread-safe async management system initialized")