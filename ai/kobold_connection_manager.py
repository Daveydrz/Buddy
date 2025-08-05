"""
Enhanced KoboldCPP Connection Manager for Buddy System
Created: 2025-08-05
Purpose: Dedicated connection manager for KoboldCPP with robust error handling, monitoring, and consciousness protection
"""

import threading
import time
import queue
import json
import requests
from typing import Dict, Any, Optional, Callable
from urllib3.exceptions import IncompleteRead
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import urllib3


@dataclass
class ConnectionHealthMetrics:
    """Metrics for connection health monitoring"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    incomplete_read_errors: int = 0
    timeout_errors: int = 0
    connection_errors: int = 0
    average_response_time: float = 0.0
    last_successful_request: Optional[datetime] = None
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    
    def get_success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_health_score(self) -> float:
        """Calculate overall health score (0-100)"""
        if self.total_requests == 0:
            return 100.0  # Assume healthy if no requests yet
            
        success_rate = self.get_success_rate()
        recency_factor = 1.0
        
        # Reduce score if no recent successful requests
        if self.last_successful_request:
            time_since_success = datetime.now() - self.last_successful_request
            if time_since_success > timedelta(minutes=5):
                recency_factor = 0.5
        
        # Penalize for consecutive failures
        failure_penalty = min(self.consecutive_failures * 10, 50)
        
        health_score = (success_rate * recency_factor) - failure_penalty
        return max(0.0, min(100.0, health_score))


class KoboldCPPHealthMonitor:
    """Advanced health monitoring for KoboldCPP connection"""
    
    def __init__(self, check_interval=30):
        self.check_interval = check_interval
        self.last_check = 0
        self.is_healthy = True
        self.health_lock = threading.Lock()
        
    def check_health(self, url: str, timeout: int = 5) -> bool:
        """Perform health check on KoboldCPP server"""
        current_time = time.time()
        
        # Skip frequent health checks
        if current_time - self.last_check < self.check_interval:
            return self.is_healthy
            
        self.last_check = current_time
        
        try:
            # Try to get models endpoint
            models_url = url.replace('/chat/completions', '/models')
            response = requests.get(models_url, timeout=timeout)
            
            with self.health_lock:
                self.is_healthy = response.status_code == 200
                
            if self.is_healthy:
                print(f"[HealthMonitor] ✅ KoboldCPP health check passed")
            else:
                print(f"[HealthMonitor] ⚠️ KoboldCPP health check failed: status {response.status_code}")
            
            return self.is_healthy
            
        except Exception as e:
            with self.health_lock:
                self.is_healthy = False
            print(f"[HealthMonitor] ❌ KoboldCPP health check failed: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        with self.health_lock:
            return {
                'is_healthy': self.is_healthy,
                'last_check': self.last_check,
                'check_interval': self.check_interval
            }


class EnhancedKoboldCPPManager:
    """Enhanced KoboldCPP connection manager with comprehensive error handling"""
    
    def __init__(self, 
                 kobold_url: str,
                 max_concurrent_requests: int = 2,
                 max_queue_size: int = 10,
                 request_timeout: int = 45,
                 max_retries: int = 5):
        
        self.kobold_url = kobold_url
        self.max_concurrent = max_concurrent_requests
        self.max_queue_size = max_queue_size
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        
        # Request management
        self.request_queue = queue.Queue(maxsize=max_queue_size)
        self.active_requests = 0
        self.request_lock = threading.Lock()
        
        # Metrics and monitoring
        self.metrics = ConnectionHealthMetrics()
        self.health_monitor = KoboldCPPHealthMonitor()
        self.metrics_lock = threading.Lock()
        
        # Session management
        self._session = None
        self._session_lock = threading.Lock()
        
        print(f"[KoboldManager] ✅ Enhanced KoboldCPP manager initialized for {kobold_url}")
    
    def _get_session(self) -> requests.Session:
        """Get or create optimized session for KoboldCPP"""
        if self._session is None:
            with self._session_lock:
                if self._session is None:
                    self._session = requests.Session()
                    
                    # Optimized for KoboldCPP
                    self._session.headers.update({
                        'Connection': 'close',  # Prevent connection reuse to avoid IncompleteRead
                        'User-Agent': 'Buddy-AI-KoboldCPP/1.0',
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache'
                    })
                    
                    print("[KoboldManager] 🔧 Created optimized session for KoboldCPP")
        
        return self._session
    
    def _reset_session(self):
        """Reset session to clear any corrupted connection state"""
        with self._session_lock:
            if self._session:
                try:
                    self._session.close()
                except:
                    pass
                self._session = None
                print("[KoboldManager] 🔄 Session reset due to connection issues")
    
    def _update_metrics(self, success: bool, response_time: float = 0.0, error: str = None):
        """Update connection metrics"""
        with self.metrics_lock:
            self.metrics.total_requests += 1
            
            if success:
                self.metrics.successful_requests += 1
                self.metrics.consecutive_failures = 0
                self.metrics.last_successful_request = datetime.now()
                
                # Update average response time
                if self.metrics.average_response_time == 0:
                    self.metrics.average_response_time = response_time
                else:
                    self.metrics.average_response_time = (
                        self.metrics.average_response_time * 0.8 + response_time * 0.2
                    )
            else:
                self.metrics.failed_requests += 1
                self.metrics.consecutive_failures += 1
                if error:
                    self.metrics.last_error = error
                    
                    # Categorize errors
                    if 'IncompleteRead' in error or 'ChunkedEncodingError' in error:
                        self.metrics.incomplete_read_errors += 1
                    elif 'timeout' in error.lower():
                        self.metrics.timeout_errors += 1
                    elif 'connection' in error.lower():
                        self.metrics.connection_errors += 1
    
    def execute_request(self, payload: Dict[str, Any], stream: bool = False) -> requests.Response:
        """Execute KoboldCPP request with enhanced error handling and queuing"""
        request_id = f"req_{int(time.time() * 1000)}"
        start_time = time.time()
        
        try:
            # Check health before proceeding
            if not self.health_monitor.check_health(self.kobold_url):
                raise ConnectionError("KoboldCPP server health check failed")
            
            # Wait for available slot with timeout to prevent queue deadlock
            wait_timeout = 30  # 30 seconds max wait
            wait_start = time.time()
            
            with self.request_lock:
                while self.active_requests >= self.max_concurrent:
                    if time.time() - wait_start > wait_timeout:
                        # Clean up any stuck requests before failing
                        self._cleanup_stuck_requests()
                        raise TimeoutError(f"Request {request_id} timed out waiting for queue slot")
                    
                    print(f"[KoboldManager] 🚦 Request {request_id} waiting - {self.active_requests} active")
                    time.sleep(0.1)
                
                self.active_requests += 1
            
            try:
                result = self._execute_with_retry(request_id, payload, stream, start_time)
                
                # Update metrics on success
                response_time = time.time() - start_time
                self._update_metrics(success=True, response_time=response_time)
                
                print(f"[KoboldManager] ✅ Request {request_id} completed in {response_time:.2f}s")
                return result
                
            finally:
                with self.request_lock:
                    self.active_requests -= 1
                    
        except Exception as e:
            # Update metrics on failure
            self._update_metrics(success=False, error=str(e))
            print(f"[KoboldManager] ❌ Request {request_id} failed: {e}")
            raise
    
    def _execute_with_retry(self, request_id: str, payload: Dict[str, Any], 
                          stream: bool, start_time: float) -> requests.Response:
        """Execute request with retry logic for different error types"""
        
        for attempt in range(self.max_retries):
            try:
                session = self._get_session()
                
                print(f"[KoboldManager] 🚀 Attempt {attempt + 1}/{self.max_retries} for {request_id}")
                
                response = session.post(
                    self.kobold_url,
                    json=payload,
                    timeout=self.request_timeout,
                    stream=stream
                )
                
                if response.status_code == 200:
                    return response
                else:
                    raise requests.exceptions.HTTPError(f"HTTP {response.status_code}: {response.text}")
                    
            except (IncompleteRead, 
                   requests.exceptions.ChunkedEncodingError,
                   requests.exceptions.ConnectionError,
                   urllib3.exceptions.ProtocolError) as e:
                retry_delay = min(2 ** attempt, 16)  # Exponential backoff, max 16s
                
                print(f"[KoboldManager] ⚠️ Connection/IncompleteRead error on attempt {attempt + 1}: {e}")
                
                if attempt < self.max_retries - 1:
                    print(f"[KoboldManager] 🔄 Resetting session and retrying in {retry_delay}s...")
                    self._reset_session()
                    time.sleep(retry_delay)
                else:
                    print(f"[KoboldManager] 💔 Max retries exceeded for connection/IncompleteRead error")
                    raise
                    
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                retry_delay = min(2 ** attempt, 8)  # Faster retry for connection issues
                
                print(f"[KoboldManager] ⚠️ Timeout/Connection error on attempt {attempt + 1}: {e}")
                
                if attempt < self.max_retries - 1:
                    print(f"[KoboldManager] 🔄 Retrying connection in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print(f"[KoboldManager] 💔 Max retries exceeded for timeout/connection error")
                    raise
                    
            except Exception as e:
                # For other errors, only retry a few times
                if attempt < min(2, self.max_retries - 1):
                    retry_delay = 1.0
                    print(f"[KoboldManager] ⚠️ General error on attempt {attempt + 1}: {e}")
                    print(f"[KoboldManager] 🔄 Retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                else:
                    print(f"[KoboldManager] 💔 Giving up after {attempt + 1} attempts")
                    raise
        
        raise Exception(f"Request {request_id} failed after {self.max_retries} attempts")
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics and health metrics"""
        with self.metrics_lock:
            health_status = self.health_monitor.get_health_status()
            
            return {
                'metrics': asdict(self.metrics),
                'health': health_status,
                'health_score': self.metrics.get_health_score(),
                'active_requests': self.active_requests,
                'configuration': {
                    'kobold_url': self.kobold_url,
                    'max_concurrent': self.max_concurrent,
                    'max_retries': self.max_retries,
                    'request_timeout': self.request_timeout
                },
                'timestamp': datetime.now().isoformat()
            }
    
    def is_healthy(self) -> bool:
        """Check if the connection manager considers KoboldCPP healthy"""
        return (self.health_monitor.is_healthy and 
                self.metrics.get_health_score() > 50.0 and
                self.metrics.consecutive_failures < 5)
    
    def get_consciousness_protection_status(self) -> Dict[str, Any]:
        """Get status for consciousness system protection"""
        return {
            'connection_healthy': self.is_healthy(),
            'can_maintain_consciousness': self.metrics.get_health_score() > 30.0,
            'fallback_mode_recommended': self.metrics.consecutive_failures > 3,
            'last_successful_connection': self.metrics.last_successful_request.isoformat() if self.metrics.last_successful_request else None,
            'error_summary': {
                'incomplete_reads': self.metrics.incomplete_read_errors,
                'timeouts': self.metrics.timeout_errors,
                'connection_errors': self.metrics.connection_errors
            }
        }
    
    def _cleanup_stuck_requests(self):
        """Clean up any stuck requests to prevent queue deadlock"""
        try:
            # Reset active requests counter if it seems stuck
            if self.active_requests > 0:
                print(f"[KoboldManager] 🧹 Cleaning up {self.active_requests} potentially stuck requests")
                self.active_requests = 0
                
            # Clear any session issues
            with self._session_lock:
                if self._session:
                    self._session.close()
                    self._session = None
                    print("[KoboldManager] 🔄 Session reset for cleanup")
                    
        except Exception as e:
            print(f"[KoboldManager] ⚠️ Cleanup error: {e}")
    
    def force_reset_queue(self):
        """Force reset the request queue and active counters"""
        try:
            with self.request_lock:
                self.active_requests = 0
                
            # Clear any stale session
            with self._session_lock:
                if self._session:
                    self._session.close()
                    self._session = None
                    
            print("[KoboldManager] 🔄 Force reset completed")
            
        except Exception as e:
            print(f"[KoboldManager] ❌ Force reset error: {e}")


def maintain_consciousness_during_error(error_context: Dict[str, Any]) -> bool:
    """Maintain consciousness state during connection errors"""
    try:
        # This would interface with the consciousness system
        # For now, we'll implement basic preservation logic
        
        error_type = error_context.get('error_type', '')
        
        # Preserve consciousness for recoverable errors
        recoverable_errors = ['incomplete_read_error', 'timeout_error', 'connection_error']
        
        if error_type in recoverable_errors:
            print(f"[Consciousness] 🧠 Preserving consciousness state during {error_type}")
            return True
        
        print(f"[Consciousness] ⚠️ Cannot preserve consciousness during {error_type}")
        return False
        
    except Exception as e:
        print(f"[Consciousness] ❌ Error in consciousness preservation: {e}")
        return False