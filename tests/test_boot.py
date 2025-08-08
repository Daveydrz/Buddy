"""
Test module imports to ensure all new modules can be loaded
"""

import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class TestBootstrap:
    """Test that all modules can be imported"""
    
    def test_config_modules(self):
        """Test config module imports"""
        # Test core config
        from config.core import DEBUG, get_current_time, startup_summary
        assert DEBUG is not None
        assert callable(get_current_time)
        assert callable(startup_summary)
        
        # Test audio config
        from config.audio import SAMPLE_RATE, WATCHDOG_INTERVAL_S
        assert isinstance(SAMPLE_RATE, int)
        assert isinstance(WATCHDOG_INTERVAL_S, (int, float))
        
        # Test models config
        from config.models import KOBOLD_URL, KOKORO_API_BASE_URL, FASTER_WHISPER_WS
        assert KOBOLD_URL.startswith('http')
        assert KOKORO_API_BASE_URL.startswith('http')
        assert FASTER_WHISPER_WS.startswith('ws')
    
    def test_service_adapters(self):
        """Test service adapter imports"""
        # Note: These may fail if numpy is not available, which is OK
        try:
            from stt import WhisperClient
            from llm import KoboldClient
            from tts import KokoroClient
            
            assert WhisperClient is not None
            assert KoboldClient is not None  
            assert KokoroClient is not None
            
        except ImportError as e:
            # Expected if numpy or other dependencies missing
            pytest.skip(f"Service adapters require external dependencies: {e}")
    
    def test_services_facade(self):
        """Test services facade imports"""
        from services import consciousness, idle_tick, pre_reply, post_user_turn
        assert consciousness is not None
        assert callable(idle_tick)
        assert callable(pre_reply)
        assert callable(post_user_turn)
    
    def test_backward_compatibility(self):
        """Test that old config imports still work"""
        import config
        
        # Test that key variables are available
        assert hasattr(config, 'KOBOLD_URL')
        assert hasattr(config, 'KOKORO_API_BASE_URL')
        assert hasattr(config, 'FASTER_WHISPER_WS')
        assert hasattr(config, 'DEBUG')
        assert hasattr(config, 'SAMPLE_RATE')
        
        # Test values match expected defaults
        assert config.KOBOLD_URL == "http://localhost:5001/v1/chat/completions"
        assert config.KOKORO_API_BASE_URL == "http://127.0.0.1:8880"
        assert config.FASTER_WHISPER_WS == "ws://localhost:9090"
        
    def test_tools_import(self):
        """Test tools module import"""
        import tools
        assert hasattr(tools, '__version__')

if __name__ == "__main__":
    pytest.main([__file__, "-v"])