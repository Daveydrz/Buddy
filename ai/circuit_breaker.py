"""
Circuit Breaker and Fallback Mechanisms for Buddy System
Created: 2025-08-05
Purpose: Implement circuit breaker pattern and fallback mechanisms for improved stability
"""

import time
import threading
import logging
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
from collections import deque

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit open, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5           # Number of failures to open circuit
    recovery_timeout: int = 60           # Seconds before attempting recovery
    success_threshold: int = 3           # Successful calls needed to close circuit
    timeout: int = 30                    # Request timeout in seconds

class CircuitBreaker:
    """Circuit breaker implementation for service calls"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.lock = threading.Lock()
        self.failure_history = deque(maxlen=100)  # Keep last 100 failures for analysis
        
    def call(self, func: Callable, *args, **kwargs):
        """Execute function through circuit breaker"""
        with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    print(f"[CircuitBreaker] {self.name} entering HALF_OPEN state")
                else:
                    raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is OPEN")
        
        try:
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            self._on_success(execution_time)
            return result
            
        except Exception as e:
            self._on_failure(e)
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.config.recovery_timeout
    
    def _on_success(self, execution_time: float):
        """Handle successful execution"""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    print(f"[CircuitBreaker] {self.name} circuit CLOSED - service recovered")
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on successful call
                self.failure_count = max(0, self.failure_count - 1)
    
    def _on_failure(self, error: Exception):
        """Handle failed execution"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            self.failure_history.append({
                'timestamp': self.last_failure_time,
                'error': str(error),
                'error_type': type(error).__name__
            })
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                print(f"[CircuitBreaker] {self.name} circuit OPEN - recovery failed")
            elif self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"[CircuitBreaker] {self.name} circuit OPEN - threshold reached ({self.failure_count} failures)")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        with self.lock:
            return {
                'name': self.name,
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'last_failure_time': self.last_failure_time,
                'failure_history_count': len(self.failure_history),
                'config': {
                    'failure_threshold': self.config.failure_threshold,
                    'recovery_timeout': self.config.recovery_timeout,
                    'success_threshold': self.config.success_threshold,
                    'timeout': self.config.timeout
                }
            }

class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open"""
    pass

class FallbackManager:
    """Manages fallback mechanisms for failed services"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.fallback_responses: Dict[str, Callable] = {}
        self.lock = threading.Lock()
    
    def register_service(self, service_name: str, config: CircuitBreakerConfig = None):
        """Register a service with circuit breaker"""
        with self.lock:
            self.circuit_breakers[service_name] = CircuitBreaker(service_name, config)
            print(f"[FallbackManager] Registered service: {service_name}")
    
    def register_fallback(self, service_name: str, fallback_func: Callable):
        """Register fallback function for a service"""
        with self.lock:
            self.fallback_responses[service_name] = fallback_func
            print(f"[FallbackManager] Registered fallback for: {service_name}")
    
    def call_with_fallback(self, service_name: str, primary_func: Callable, *args, **kwargs):
        """Call service with automatic fallback on failure"""
        if service_name not in self.circuit_breakers:
            self.register_service(service_name)
        
        circuit_breaker = self.circuit_breakers[service_name]
        
        try:
            return circuit_breaker.call(primary_func, *args, **kwargs)
        except (CircuitBreakerOpenError, Exception) as e:
            print(f"[FallbackManager] Primary service {service_name} failed: {e}")
            
            # Try fallback
            if service_name in self.fallback_responses:
                try:
                    print(f"[FallbackManager] Using fallback for {service_name}")
                    return self.fallback_responses[service_name](*args, **kwargs)
                except Exception as fallback_error:
                    print(f"[FallbackManager] Fallback for {service_name} also failed: {fallback_error}")
            
            # No fallback available or fallback failed
            raise e
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all circuit breakers"""
        with self.lock:
            return {
                'circuit_breakers': {name: cb.get_stats() for name, cb in self.circuit_breakers.items()},
                'registered_fallbacks': list(self.fallback_responses.keys()),
                'timestamp': time.time()
            }

# Global fallback manager instance
fallback_manager = FallbackManager()

# Convenience functions for common fallbacks
def llm_fallback_response(*args, **kwargs) -> str:
    """Fallback response when LLM service is unavailable"""
    return "I'm experiencing some technical difficulties right now, but I'm still here to help as best I can."

def consciousness_fallback_response(*args, **kwargs) -> str:
    """Fallback when consciousness modules are unavailable"""
    return "I'm operating in a simplified mode right now, but I can still assist you."

def memory_fallback_response(*args, **kwargs) -> Dict[str, Any]:
    """Fallback when memory systems are unavailable"""
    return {
        'context': 'Memory system temporarily unavailable',
        'conversation_history': [],
        'user_memory': {}
    }

# Register common fallbacks
fallback_manager.register_fallback('llm_service', llm_fallback_response)
fallback_manager.register_fallback('consciousness_modules', consciousness_fallback_response)
fallback_manager.register_fallback('memory_system', memory_fallback_response)

print("[CircuitBreaker] ✅ Circuit breaker and fallback system initialized")