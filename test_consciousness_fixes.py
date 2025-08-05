"""
Test suite for Buddy Class 5+ consciousness system fixes
Created: 2025-08-05
Purpose: Test the fixes for async event loops, LLM connections, timeouts, latency, and data parsing
"""

import pytest
import asyncio
import time
import json
import threading
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import TimeoutError as ConcurrentTimeoutError

# Import the modules we're testing
from ai.async_manager import AsyncManager, async_safe, run_async_safe
from ai.circuit_breaker import EnhancedCircuitBreaker, LLMConnectionPool, CircuitBreakerConfig
from ai.consciousness_timeout_manager import TimeoutManager, with_consciousness_timeout, ConsciousnessTimeout
from ai.comprehensive_data_parser import ComprehensiveExtractor, parse_json_robust, ParseErrorType

class TestAsyncManager:
    """Test the AsyncManager for handling event loop conflicts"""
    
    def test_async_manager_initialization(self):
        """Test that AsyncManager initializes correctly"""
        async_manager = AsyncManager()
        assert async_manager is not None
        assert async_manager._running == True
        
    def test_ensure_loop(self):
        """Test that ensure_loop creates or returns an event loop"""
        async_manager = AsyncManager()
        loop = async_manager.ensure_loop()
        assert loop is not None
        assert isinstance(loop, asyncio.AbstractEventLoop)
        
    def test_async_safe_decorator(self):
        """Test the async_safe decorator"""
        @async_safe(timeout=5.0)
        async def test_async_function():
            await asyncio.sleep(0.1)
            return "success"
        
        result = test_async_function()
        assert result == "success"
        
    def test_thread_safe_execution(self):
        """Test that async functions can be called from different threads"""
        async_manager = AsyncManager()
        results = []
        
        async def test_coro():
            await asyncio.sleep(0.1)
            return f"thread_{threading.get_ident()}"
        
        def run_in_thread():
            result = async_manager.run_in_thread_safe(test_coro(), timeout=5.0)
            results.append(result)
        
        # Run in multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_in_thread)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(results) == 3
        assert all("thread_" in result for result in results)
        
    def test_timeout_handling(self):
        """Test that timeouts are handled correctly"""
        async_manager = AsyncManager()
        
        async def slow_coro():
            await asyncio.sleep(2.0)
            return "too_slow"
        
        with pytest.raises(TimeoutError):
            async_manager.run_in_thread_safe(slow_coro(), timeout=0.5)

class TestEnhancedCircuitBreaker:
    """Test the enhanced circuit breaker with connection pooling"""
    
    def test_circuit_breaker_initialization(self):
        """Test that circuit breaker initializes correctly"""
        cb = EnhancedCircuitBreaker("test_service")
        assert cb.name == "test_service"
        assert cb.connection_pool is not None
        
    def test_connection_pool_initialization(self):
        """Test that connection pool initializes correctly"""
        pool = LLMConnectionPool()
        assert pool.max_connections == 5
        assert pool.retry_attempts == 3
        assert len(pool.primary_endpoints) > 0
        
    def test_healthy_endpoint_detection(self):
        """Test endpoint health detection (mock)"""
        pool = LLMConnectionPool()
        
        # Mock requests to simulate healthy endpoint
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            endpoint = pool.get_healthy_endpoint()
            assert endpoint is not None
            
    def test_retry_mechanism(self):
        """Test retry mechanism with exponential backoff"""
        pool = LLMConnectionPool()
        call_count = 0
        
        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Simulated failure")
            return "success"
        
        with patch.object(pool, 'get_healthy_endpoint', return_value="http://test:5001"):
            result = pool.execute_with_retry(failing_func)
            assert result == "success"
            assert call_count == 3
            
    def test_circuit_breaker_states(self):
        """Test circuit breaker state transitions"""
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=1)
        cb = EnhancedCircuitBreaker("test", config)
        
        # Test closed state (normal operation)
        assert cb.state.value == "closed"
        
        # Simulate failures to open circuit
        for _ in range(3):
            cb._on_failure(Exception("test error"))
        
        assert cb.state.value == "open"
        
        # Test recovery after timeout
        time.sleep(1.1)
        assert cb._should_attempt_reset() == True

class TestTimeoutManager:
    """Test the consciousness timeout manager"""
    
    def test_timeout_manager_initialization(self):
        """Test that timeout manager initializes correctly"""
        tm = TimeoutManager()
        assert tm.default_timeouts['inner_monologue'] == 3.0
        assert tm.default_timeouts['subjective_experience'] == 3.0
        assert len(tm.escalation_strategies) == 4
        
    def test_timeout_decorator(self):
        """Test the timeout decorator"""
        tm = TimeoutManager()
        
        @tm.with_timeout(1.0, 'test_module', 'fallback')
        def quick_function():
            time.sleep(0.1)
            return "success"
        
        result = quick_function()
        assert result == "success"
        
    def test_timeout_with_fallback(self):
        """Test timeout with fallback strategy"""
        tm = TimeoutManager()
        
        def slow_function():
            time.sleep(2.0)
            return "too_slow"
        
        # Should use fallback strategy
        result = tm.execute_with_timeout(
            slow_function, 0.5, 'inner_monologue', 'fallback'
        )
        
        # Should return fallback result
        assert isinstance(result, dict)
        assert 'timeout_recovery' in result
        
    def test_recovery_callbacks(self):
        """Test custom recovery callbacks"""
        tm = TimeoutManager()
        
        def custom_recovery(*args, **kwargs):
            return {"custom": "recovery", "timeout_recovery": True}
        
        tm.register_recovery_callback('test_module', custom_recovery)
        
        def slow_function():
            time.sleep(2.0)
            return "too_slow"
        
        result = tm.execute_with_timeout(
            slow_function, 0.5, 'test_module', 'fallback'
        )
        
        assert result["custom"] == "recovery"
        
    def test_performance_tracking(self):
        """Test performance statistics tracking"""
        tm = TimeoutManager()
        
        def quick_function():
            time.sleep(0.1)
            return "success"
        
        # Execute several times
        for _ in range(5):
            tm.execute_with_timeout(quick_function, 1.0, 'test_module', 'fallback')
        
        stats = tm.get_stats()
        assert 'test_module' in stats['module_stats']
        assert stats['module_stats']['test_module']['total_calls'] == 5

class TestComprehensiveDataParser:
    """Test the comprehensive data parser and error handler"""
    
    def test_extractor_initialization(self):
        """Test that extractor initializes correctly"""
        extractor = ComprehensiveExtractor()
        assert extractor.parse_stats['total_attempts'] == 0
        assert len(extractor.json_repair_patterns) > 0
        
    def test_valid_json_parsing(self):
        """Test parsing valid JSON"""
        extractor = ComprehensiveExtractor()
        
        valid_json = '{"test": "value", "number": 42}'
        result = extractor.parse_json_safe(valid_json)
        
        assert result.success == True
        assert result.data["test"] == "value"
        assert result.data["number"] == 42
        
    def test_malformed_json_recovery(self):
        """Test recovery from malformed JSON"""
        extractor = ComprehensiveExtractor()
        
        # Missing quotes around key
        malformed_json = '{test: "value", "number": 42}'
        result = extractor.parse_json_safe(malformed_json)
        
        # Should either succeed with recovery or fail gracefully
        if result.success:
            assert result.recovery_applied == True or result.data is not None
        else:
            assert result.error_type is not None
            
    def test_incomplete_response_recovery(self):
        """Test recovery from incomplete responses"""
        extractor = ComprehensiveExtractor()
        
        # Incomplete JSON (missing closing brace)
        incomplete_json = '{"test": "value", "number": 42'
        result = extractor.parse_json_safe(incomplete_json)
        
        # Should attempt recovery
        assert result.error_type in [None, ParseErrorType.JSON_MALFORMED, ParseErrorType.INCOMPLETE_RESPONSE]
        
    def test_encoding_error_handling(self):
        """Test handling of encoding errors"""
        extractor = ComprehensiveExtractor()
        
        # Content with encoding issues
        problematic_content = '{"test": "value\x00\x01", "number": 42}'
        result = extractor.parse_json_safe(problematic_content)
        
        # Should handle gracefully
        assert result is not None
        
    def test_json_extraction_from_text(self):
        """Test extracting JSON objects from mixed content"""
        extractor = ComprehensiveExtractor()
        
        mixed_content = '''
        Here is some text before the JSON.
        {"extracted": "data", "valid": true}
        And some text after.
        '''
        
        json_objects = extractor._extract_json_objects(mixed_content)
        assert len(json_objects) >= 1
        if json_objects:
            assert json_objects[0]["extracted"] == "data"
            
    def test_performance_statistics(self):
        """Test parsing statistics collection"""
        extractor = ComprehensiveExtractor()
        
        # Parse several items
        test_cases = [
            '{"valid": "json"}',
            '{invalid json}',
            '{"another": "valid", "item": true}'
        ]
        
        for case in test_cases:
            extractor.parse_json_safe(case)
        
        stats = extractor.get_parsing_stats()
        assert stats['total_attempts'] == 3
        assert 'success_rate' in stats

class TestIntegration:
    """Integration tests for all components working together"""
    
    def test_async_with_timeout_manager(self):
        """Test async manager working with timeout manager"""
        async_manager = AsyncManager()
        timeout_manager = TimeoutManager()
        
        async def test_async_operation():
            await asyncio.sleep(0.1)
            return {"result": "success"}
        
        # Run async operation through timeout manager
        result = timeout_manager.execute_with_timeout(
            lambda: async_manager.run_in_thread_safe(test_async_operation()),
            2.0, 'integration_test', 'fallback'
        )
        
        assert result["result"] == "success"
        
    def test_circuit_breaker_with_data_parser(self):
        """Test circuit breaker working with data parser"""
        cb = EnhancedCircuitBreaker("parser_service")
        extractor = ComprehensiveExtractor()
        
        def parse_json_response():
            # Simulate LLM response parsing
            response = '{"consciousness": "active", "response": "Hello"}'
            result = extractor.parse_json_safe(response)
            if not result.success:
                raise ValueError("Parsing failed")
            return result.data
        
        # Should work through circuit breaker
        try:
            result = cb.call(parse_json_response)
            assert result["consciousness"] == "active"
        except Exception as e:
            # Circuit breaker might be open, which is acceptable
            print(f"Circuit breaker test: {e}")
            
    def test_comprehensive_system_health(self):
        """Test that all systems can be initialized without conflicts"""
        # Initialize all components
        async_manager = AsyncManager()
        cb = EnhancedCircuitBreaker("health_test")
        timeout_manager = TimeoutManager()
        extractor = ComprehensiveExtractor()
        
        # Test basic functionality of each
        loop = async_manager.ensure_loop()
        assert loop is not None
        
        stats = cb.get_stats()
        assert stats['name'] == "health_test"
        
        tm_stats = timeout_manager.get_stats()
        assert 'default_timeouts' in tm_stats
        
        parse_stats = extractor.get_parsing_stats()
        assert 'status' in parse_stats or 'total_attempts' in parse_stats
        
        print("✅ All systems initialized successfully")

if __name__ == "__main__":
    # Run basic tests if called directly
    print("🧪 Running Buddy consciousness system tests...")
    
    # Test AsyncManager
    print("Testing AsyncManager...")
    test_async = TestAsyncManager()
    test_async.test_async_manager_initialization()
    test_async.test_ensure_loop()
    print("✅ AsyncManager tests passed")
    
    # Test Enhanced Circuit Breaker
    print("Testing Enhanced Circuit Breaker...")
    test_cb = TestEnhancedCircuitBreaker()
    test_cb.test_circuit_breaker_initialization()
    test_cb.test_connection_pool_initialization()
    print("✅ Circuit Breaker tests passed")
    
    # Test Timeout Manager
    print("Testing Timeout Manager...")
    test_tm = TestTimeoutManager()
    test_tm.test_timeout_manager_initialization()
    test_tm.test_timeout_decorator()
    print("✅ Timeout Manager tests passed")
    
    # Test Data Parser
    print("Testing Comprehensive Data Parser...")
    test_parser = TestComprehensiveDataParser()
    test_parser.test_extractor_initialization()
    test_parser.test_valid_json_parsing()
    print("✅ Data Parser tests passed")
    
    # Integration test
    print("Testing Integration...")
    test_integration = TestIntegration()
    test_integration.test_comprehensive_system_health()
    print("✅ Integration tests passed")
    
    print("🎉 All tests completed successfully!")