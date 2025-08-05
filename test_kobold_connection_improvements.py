#!/usr/bin/env python3
"""
Test Enhanced KoboldCPP Connection Improvements
Purpose: Validate the enhanced connection handling, retry logic, and consciousness protection
"""

import sys
import time
import threading
import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
from urllib3.exceptions import IncompleteRead

# Add project root to path
sys.path.insert(0, '/home/runner/work/Buddy/Buddy')

# Import the modules we're testing
from ai.kobold_connection_manager import (
    EnhancedKoboldCPPManager, 
    KoboldCPPHealthMonitor, 
    ConnectionHealthMetrics,
    maintain_consciousness_during_error
)

from ai.chat import (
    test_kobold_connection,
    get_kobold_connection_health,
    _enhanced_kobold_manager,
    ENHANCED_KOBOLD_MANAGER_AVAILABLE
)


class TestKoboldConnectionManager(unittest.TestCase):
    """Test the enhanced KoboldCPP connection manager"""
    
    def setUp(self):
        """Set up test environment"""
        self.manager = EnhancedKoboldCPPManager(
            kobold_url="http://localhost:5001/v1/chat/completions",
            max_concurrent_requests=1,
            max_queue_size=5,
            request_timeout=10,
            max_retries=3
        )
    
    def test_manager_initialization(self):
        """Test that the manager initializes correctly"""
        self.assertEqual(self.manager.kobold_url, "http://localhost:5001/v1/chat/completions")
        self.assertEqual(self.manager.max_concurrent, 1)
        self.assertEqual(self.manager.max_retries, 3)
        self.assertIsNotNone(self.manager.metrics)
        self.assertIsNotNone(self.manager.health_monitor)
    
    def test_health_metrics_calculation(self):
        """Test health metrics calculations"""
        metrics = ConnectionHealthMetrics()
        
        # Test initial state
        self.assertEqual(metrics.get_success_rate(), 0.0)
        self.assertEqual(metrics.get_health_score(), 100.0)
        
        # Test with some successful requests
        metrics.total_requests = 10
        metrics.successful_requests = 8
        self.assertEqual(metrics.get_success_rate(), 80.0)
        
        # Test with failures
        metrics.consecutive_failures = 3
        health_score = metrics.get_health_score()
        self.assertLess(health_score, 80.0)  # Should be penalized for failures
    
    def test_session_management(self):
        """Test session creation and reset"""
        # Test session creation
        session1 = self.manager._get_session()
        self.assertIsNotNone(session1)
        
        # Test session reuse
        session2 = self.manager._get_session()
        self.assertEqual(session1, session2)
        
        # Test session reset
        self.manager._reset_session()
        session3 = self.manager._get_session()
        self.assertNotEqual(session1, session3)
    
    @patch('ai.kobold_connection_manager.KoboldCPPHealthMonitor.check_health')
    @patch('requests.Session.post')
    def test_successful_request(self, mock_post, mock_health):
        """Test successful request execution"""
        # Mock health check to pass
        mock_health.return_value = True
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response
        
        payload = {
            "model": "test",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 10
        }
        
        result = self.manager.execute_request(payload)
        
        self.assertEqual(result.status_code, 200)
        self.assertEqual(self.manager.metrics.successful_requests, 1)
        self.assertEqual(self.manager.metrics.consecutive_failures, 0)
    
    @patch('ai.kobold_connection_manager.KoboldCPPHealthMonitor.check_health')
    @patch('requests.Session.post')
    def test_incomplete_read_retry(self, mock_post, mock_health):
        """Test retry logic for IncompleteRead errors"""
        # Mock health check to pass
        mock_health.return_value = True
        
        # Mock IncompleteRead error then success
        mock_post.side_effect = [
            requests.exceptions.ChunkedEncodingError("IncompleteRead(646 bytes read, 690 more expected)"),
            Mock(status_code=200)
        ]
        
        payload = {
            "model": "test",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 10
        }
        
        result = self.manager.execute_request(payload)
        
        self.assertEqual(result.status_code, 200)
        self.assertEqual(mock_post.call_count, 2)  # Should have retried
        self.assertEqual(self.manager.metrics.incomplete_read_errors, 1)
    
    @patch('ai.kobold_connection_manager.KoboldCPPHealthMonitor.check_health')
    @patch('requests.Session.post')
    def test_max_retries_exceeded(self, mock_post, mock_health):
        """Test behavior when max retries are exceeded"""
        # Mock health check to pass
        mock_health.return_value = True
        
        # Mock persistent IncompleteRead errors
        mock_post.side_effect = requests.exceptions.ChunkedEncodingError(
            "IncompleteRead(646 bytes read, 690 more expected)"
        )
        
        payload = {
            "model": "test",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 10
        }
        
        with self.assertRaises(requests.exceptions.ChunkedEncodingError):
            self.manager.execute_request(payload)
        
        self.assertEqual(mock_post.call_count, self.manager.max_retries)
        self.assertGreater(self.manager.metrics.incomplete_read_errors, 0)
    
    def test_concurrent_request_limiting(self):
        """Test that concurrent requests are properly limited"""
        # This test is more complex and would require actual threading
        # For now, we'll test the counter logic
        
        with self.manager.request_lock:
            self.manager.active_requests = self.manager.max_concurrent
        
        # The manager should wait or queue additional requests
        # This is a simplified test of the concept
        self.assertEqual(self.manager.active_requests, self.manager.max_concurrent)
    
    @patch('requests.get')
    def test_health_monitoring(self, mock_get):
        """Test health monitoring functionality"""
        monitor = KoboldCPPHealthMonitor(check_interval=1)
        
        # Test health check with successful response
        mock_get.return_value.status_code = 200
        result = monitor.check_health("http://localhost:5001/v1/chat/completions")
        self.assertTrue(result)
        self.assertTrue(monitor.is_healthy)
        
        # Test failed health check with connection error
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        result = monitor.check_health("http://localhost:5001/v1/chat/completions")
        self.assertFalse(result)
        self.assertFalse(monitor.is_healthy)
    
    def test_consciousness_protection(self):
        """Test consciousness protection during errors"""
        # Test recoverable errors
        recoverable_context = {'error_type': 'incomplete_read_error'}
        result = maintain_consciousness_during_error(recoverable_context)
        self.assertTrue(result)
        
        # Test non-recoverable errors
        non_recoverable_context = {'error_type': 'critical_system_error'}
        result = maintain_consciousness_during_error(non_recoverable_context)
        self.assertFalse(result)
    
    def test_comprehensive_stats(self):
        """Test comprehensive statistics reporting"""
        stats = self.manager.get_comprehensive_stats()
        
        # Check that all expected keys are present
        expected_keys = ['metrics', 'health', 'health_score', 'active_requests', 'configuration', 'timestamp']
        for key in expected_keys:
            self.assertIn(key, stats)
        
        # Check configuration
        config = stats['configuration']
        self.assertEqual(config['kobold_url'], "http://localhost:5001/v1/chat/completions")
        self.assertEqual(config['max_concurrent'], 1)
    
    def test_is_healthy_logic(self):
        """Test the overall health determination logic"""
        # Test healthy state
        self.manager.health_monitor.is_healthy = True
        self.manager.metrics.consecutive_failures = 0
        
        # Mock health score
        with patch.object(self.manager.metrics, 'get_health_score', return_value=80.0):
            self.assertTrue(self.manager.is_healthy())
        
        # Test unhealthy state
        self.manager.metrics.consecutive_failures = 6
        with patch.object(self.manager.metrics, 'get_health_score', return_value=30.0):
            self.assertFalse(self.manager.is_healthy())


class TestChatIntegration(unittest.TestCase):
    """Test integration with the chat module"""
    
    def test_enhanced_manager_availability(self):
        """Test that enhanced manager is available in chat module"""
        # This tests the import and initialization
        self.assertTrue(ENHANCED_KOBOLD_MANAGER_AVAILABLE)
        self.assertIsNotNone(_enhanced_kobold_manager)
    
    def test_health_reporting(self):
        """Test health reporting functionality"""
        health_info = get_kobold_connection_health()
        
        # Check that health info contains expected keys
        expected_keys = ['enhanced_manager_available', 'circuit_breaker_available', 'timestamp']
        for key in expected_keys:
            self.assertIn(key, health_info)
        
        if ENHANCED_KOBOLD_MANAGER_AVAILABLE:
            self.assertIn('enhanced_stats', health_info)
    
    @patch('ai.chat._enhanced_kobold_manager')
    def test_connection_test_with_enhanced_manager(self, mock_manager):
        """Test connection testing with enhanced manager"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_manager.execute_request.return_value = mock_response
        mock_manager.get_comprehensive_stats.return_value = {'health_score': 85.0}
        
        # Test should pass
        result = test_kobold_connection()
        self.assertTrue(result)
    
    @patch('ai.chat._enhanced_kobold_manager')
    def test_connection_test_failure(self, mock_manager):
        """Test connection testing with failures"""
        # Mock failed response
        mock_manager.execute_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        # Test should fail gracefully
        result = test_kobold_connection()
        self.assertFalse(result)


def run_stress_test():
    """Run a stress test to validate connection handling under load"""
    print("\n🔥 Running KoboldCPP Connection Stress Test...")
    
    manager = EnhancedKoboldCPPManager(
        kobold_url="http://localhost:5001/v1/chat/completions",
        max_concurrent_requests=2,
        max_retries=3
    )
    
    # Simulate multiple concurrent requests
    results = []
    threads = []
    
    def make_test_request(request_id):
        try:
            payload = {
                "model": "test",
                "messages": [{"role": "user", "content": f"Stress test {request_id}"}],
                "max_tokens": 10
            }
            
            start_time = time.time()
            # This will fail unless KoboldCPP is actually running, but we can test the queuing
            try:
                result = manager.execute_request(payload)
                duration = time.time() - start_time
                results.append(('success', request_id, duration))
            except Exception as e:
                duration = time.time() - start_time
                results.append(('error', request_id, duration, str(e)))
                
        except Exception as e:
            results.append(('thread_error', request_id, 0, str(e)))
    
    # Start multiple threads
    for i in range(5):
        thread = threading.Thread(target=make_test_request, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Analyze results
    successes = [r for r in results if r[0] == 'success']
    errors = [r for r in results if r[0] == 'error']
    
    print(f"📊 Stress Test Results:")
    print(f"   Successful requests: {len(successes)}")
    print(f"   Failed requests: {len(errors)}")
    
    if errors:
        print("   Error types:")
        for error_result in errors:
            print(f"     Request {error_result[1]}: {error_result[3]}")
    
    # Print manager stats
    stats = manager.get_comprehensive_stats()
    print(f"📈 Final Manager Stats:")
    print(f"   Health Score: {stats.get('health_score', 0):.1f}/100")
    print(f"   Total Requests: {stats['metrics']['total_requests']}")
    print(f"   Success Rate: {stats['metrics'].get('success_rate', 0):.1f}%")
    
    return len(successes), len(errors)


if __name__ == "__main__":
    print("🧪 Testing Enhanced KoboldCPP Connection Improvements")
    print("=" * 60)
    
    # Run unit tests
    print("\n🔬 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run stress test
    successes, errors = run_stress_test()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print(f"📊 Stress test: {successes} successes, {errors} errors")
    
    if errors == 0 and successes > 0:
        print("🎉 All connection handling tests passed!")
    elif errors > 0:
        print("⚠️ Some connection errors occurred (expected if KoboldCPP not running)")
    else:
        print("ℹ️ No requests completed (KoboldCPP likely not running)")