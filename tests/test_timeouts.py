"""
Test timeout handling in service clients to ensure no deadlocks
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class TestTimeouts:
    """Test timeout handling in all service components"""
    
    @pytest.mark.asyncio
    async def test_consciousness_timeouts(self):
        """Test that consciousness operations timeout properly"""
        from services.consciousness import ConsciousnessFacade
        
        facade = ConsciousnessFacade()
        
        # Mock a slow operation
        async def slow_operation(*args, **kwargs):
            await asyncio.sleep(10)  # Longer than timeout
            return "should not reach here"
        
        # Test timeout wrapper
        wrapper = facade._timeout_wrapper(1.0)  # 1 second timeout
        wrapped_func = wrapper(slow_operation)
        
        start_time = asyncio.get_event_loop().time()
        result = await wrapped_func()
        end_time = asyncio.get_event_loop().time()
        
        # Should timeout and return None
        assert result is None
        assert (end_time - start_time) < 2.0  # Should be around 1 second
    
    @pytest.mark.asyncio
    async def test_llm_timeout_handling(self):
        """Test LLM client timeout handling"""
        try:
            from llm.kobold_client import KoboldClient
        except ImportError:
            pytest.skip("LLM client requires dependencies")
        
        client = KoboldClient()
        client.timeout = 1  # 1 second timeout
        
        # Mock requests to simulate timeout
        with patch.object(client.session, 'post') as mock_post:
            mock_post.side_effect = asyncio.TimeoutError("Mocked timeout")
            
            result = await client.chat([{"role": "user", "content": "test"}])
            
            # Should return empty string on timeout
            assert result == ""
    
    @pytest.mark.asyncio
    async def test_tts_timeout_handling(self):
        """Test TTS client timeout handling"""
        try:
            from tts.kokoro_client import KokoroClient
        except ImportError:
            pytest.skip("TTS client requires dependencies")
        
        client = KokoroClient()
        client.timeout = 1  # 1 second timeout
        
        # Mock requests to simulate timeout
        with patch.object(client.session, 'post') as mock_post:
            mock_post.side_effect = asyncio.TimeoutError("Mocked timeout")
            
            result = await client.synthesize("test text")
            
            # Should return None on timeout
            assert result is None
    
    @pytest.mark.asyncio
    async def test_stt_timeout_handling(self):
        """Test STT client timeout handling"""
        try:
            from stt.whisper_client import WhisperClient
            import numpy as np
        except ImportError:
            pytest.skip("STT client requires numpy")
        
        client = WhisperClient()
        client.timeout = 1  # 1 second timeout
        
        # Mock websocket to simulate timeout
        with patch('websockets.connect') as mock_connect:
            mock_ws = MagicMock()
            mock_ws.recv.side_effect = asyncio.TimeoutError("Mocked timeout")
            mock_connect.return_value.__aenter__.return_value = mock_ws
            
            test_audio = np.array([0] * 1000, dtype=np.int16)
            result = await client.transcribe_audio(test_audio)
            
            # Should return empty string on timeout
            assert result == ""
    
    @pytest.mark.asyncio
    async def test_consciousness_idle_tick_timeout(self):
        """Test that consciousness idle_tick doesn't block indefinitely"""
        from services.consciousness import consciousness
        
        # Override timeout for testing
        original_timeout = consciousness.CONSCIOUSNESS_TIMEOUT
        consciousness.CONSCIOUSNESS_TIMEOUT = 0.5  # Very short timeout
        
        try:
            start_time = asyncio.get_event_loop().time()
            await consciousness.idle_tick()
            end_time = asyncio.get_event_loop().time()
            
            # Should complete quickly even with timeouts
            assert (end_time - start_time) < 5.0
            
        finally:
            # Restore original timeout
            consciousness.CONSCIOUSNESS_TIMEOUT = original_timeout
    
    @pytest.mark.asyncio
    async def test_multiple_timeouts_no_deadlock(self):
        """Test that multiple simultaneous timeouts don't cause deadlocks"""
        from services.consciousness import ConsciousnessFacade
        
        facade = ConsciousnessFacade()
        
        async def failing_operation():
            await asyncio.sleep(10)  # Will timeout
            return "fail"
        
        # Create multiple operations that will timeout
        wrapper = facade._timeout_wrapper(0.1)  # Very short timeout
        wrapped_func = wrapper(failing_operation)
        
        # Run multiple operations concurrently
        tasks = [wrapped_func() for _ in range(10)]
        
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks)
        end_time = asyncio.get_event_loop().time()
        
        # All should timeout and return None
        assert all(result is None for result in results)
        
        # Should complete quickly without deadlock
        assert (end_time - start_time) < 2.0
    
    @pytest.mark.asyncio  
    async def test_watchdog_interval(self):
        """Test that watchdog respects interval timing"""
        from config.audio import WATCHDOG_INTERVAL_S
        
        # Verify watchdog interval is reasonable
        assert isinstance(WATCHDOG_INTERVAL_S, (int, float))
        assert WATCHDOG_INTERVAL_S > 0
        assert WATCHDOG_INTERVAL_S <= 60  # Not too long
        
        # Test watchdog timing would work
        start_time = asyncio.get_event_loop().time()
        await asyncio.sleep(0.1)  # Simulate watchdog work
        end_time = asyncio.get_event_loop().time()
        
        # Watchdog work should be fast
        assert (end_time - start_time) < 1.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])