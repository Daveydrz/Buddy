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

class LLMConnectionPool:
    """Connection pool for LLM services with retry and failover capabilities"""
    
    def __init__(self, max_connections: int = 5, retry_attempts: int = 3):
        self.max_connections = max_connections
        self.retry_attempts = retry_attempts
        self.connections = []
        self.failed_connections = []
        self.connection_lock = threading.Lock()
        self.primary_endpoints = [
            "http://localhost:5001/v1/chat/completions",  # KoboldCpp
            "http://localhost:8080/v1/chat/completions",  # Text Generation WebUI
            "http://localhost:11434/api/chat",            # Ollama
        ]
        self.backup_endpoints = [
            "http://127.0.0.1:5001/v1/chat/completions",
            "http://127.0.0.1:8080/v1/chat/completions",
        ]
        
    def get_healthy_endpoint(self) -> Optional[str]:
        """Get a healthy endpoint for LLM requests"""
        import requests
        
        # Try primary endpoints first
        for endpoint in self.primary_endpoints:
            try:
                response = requests.get(endpoint.replace("/chat/completions", "/models").replace("/api/chat", "/api/tags"), timeout=5)
                if response.status_code == 200:
                    return endpoint
            except Exception:
                continue
                
        # Try backup endpoints
        for endpoint in self.backup_endpoints:
            try:
                response = requests.get(endpoint.replace("/chat/completions", "/models"), timeout=5)
                if response.status_code == 200:
                    return endpoint
            except Exception:
                continue
                
        return None
    
    def execute_with_retry(self, func: Callable, *args, **kwargs):
        """Execute function with retry logic and endpoint failover"""
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                # Get healthy endpoint
                endpoint = self.get_healthy_endpoint()
                if not endpoint:
                    raise ConnectionError("No healthy LLM endpoints available")
                
                # Update kwargs with current endpoint if needed
                if 'endpoint' in kwargs:
                    kwargs['endpoint'] = endpoint
                
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                last_exception = e
                wait_time = (2 ** attempt) * 0.5  # Exponential backoff: 0.5s, 1s, 2s
                if attempt < self.retry_attempts - 1:
                    print(f"[ConnectionPool] Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"[ConnectionPool] All {self.retry_attempts} attempts failed")
        
        raise last_exception

class EnhancedCircuitBreaker(CircuitBreaker):
    """Enhanced circuit breaker with connection pooling and advanced recovery"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        super().__init__(name, config)
        self.connection_pool = LLMConnectionPool()
        self.recovery_strategies = []
        self.health_check_interval = 30  # seconds
        self.last_health_check = 0
        
    def add_recovery_strategy(self, strategy: Callable):
        """Add a recovery strategy function"""
        self.recovery_strategies.append(strategy)
        
    def call_with_connection_pool(self, func: Callable, *args, **kwargs):
        """Execute function through circuit breaker with connection pooling"""
        with self.lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    # Try recovery strategies first
                    self._attempt_recovery()
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    print(f"[EnhancedCircuitBreaker] {self.name} entering HALF_OPEN state with recovery")
                else:
                    raise CircuitBreakerOpenError(f"Circuit breaker {self.name} is OPEN")
        
        try:
            # Use connection pool for retry logic
            result = self.connection_pool.execute_with_retry(func, *args, **kwargs)
            self._on_success(0)  # execution_time handled by pool
            return result
            
        except Exception as e:
            self._on_failure(e)
            raise
    
    def _attempt_recovery(self):
        """Attempt to recover using registered strategies"""
        for strategy in self.recovery_strategies:
            try:
                strategy()
                print(f"[EnhancedCircuitBreaker] Recovery strategy succeeded for {self.name}")
                break
            except Exception as e:
                print(f"[EnhancedCircuitBreaker] Recovery strategy failed: {e}")
    
    def health_check(self) -> bool:
        """Perform health check on the service"""
        current_time = time.time()
        if current_time - self.last_health_check < self.health_check_interval:
            return True  # Skip frequent health checks
            
        self.last_health_check = current_time
        
        try:
            endpoint = self.connection_pool.get_healthy_endpoint()
            return endpoint is not None
        except Exception:
            return False

# Global enhanced fallback manager instance
fallback_manager = FallbackManager()

# Enhanced LLM circuit breaker with connection pooling
llm_circuit_breaker = EnhancedCircuitBreaker(
    "llm_service", 
    CircuitBreakerConfig(
        failure_threshold=3,    # Lower threshold for faster detection
        recovery_timeout=30,    # Faster recovery attempts
        success_threshold=2,    # Require fewer successes to close
        timeout=45             # Longer timeout for LLM operations
    )
)

# Register LLM recovery strategies
def restart_llm_connection():
    """Strategy to restart LLM connection"""
    print("[Recovery] Attempting to restart LLM connection...")
    # This would contain actual restart logic in production
    pass

def switch_to_backup_model():
    """Strategy to switch to backup model"""
    print("[Recovery] Switching to backup model...")
    # This would contain backup model logic in production
    pass

llm_circuit_breaker.add_recovery_strategy(restart_llm_connection)
llm_circuit_breaker.add_recovery_strategy(switch_to_backup_model)

# Register enhanced circuit breaker with fallback manager
fallback_manager.circuit_breakers['llm_service'] = llm_circuit_breaker

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

print("[CircuitBreaker] ✅ Enhanced circuit breaker with connection pooling initialized")