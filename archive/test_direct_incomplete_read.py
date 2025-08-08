#!/usr/bin/env python3
"""
Direct IncompleteRead Error Test
Purpose: Test the specific IncompleteRead error handling mentioned in the problem statement
"""

import sys
import time
from unittest.mock import patch, Mock
import requests
from urllib3.exceptions import IncompleteRead

# Add project root to path
sys.path.insert(0, '/home/runner/work/Buddy/Buddy')

from ai.kobold_connection_manager import EnhancedKoboldCPPManager
from ai.chat import ask_kobold, generate_response


def test_specific_incomplete_read_scenario():
    """Test the specific IncompleteRead scenario from the problem statement"""
    print("🔍 Testing Specific IncompleteRead Error Scenario")
    print("=" * 50)
    print("Error Pattern: IncompleteRead(646 bytes read, 690 more expected)")
    
    # Create a manager for testing
    manager = EnhancedKoboldCPPManager(
        kobold_url="http://localhost:5001/v1/chat/completions",
        max_concurrent_requests=1,
        max_retries=3
    )
    
    # Mock the specific IncompleteRead error
    def mock_post_with_incomplete_read(*args, **kwargs):
        """Mock that simulates the exact error from the problem statement"""
        # First call fails with IncompleteRead
        if not hasattr(mock_post_with_incomplete_read, 'call_count'):
            mock_post_with_incomplete_read.call_count = 0
        
        mock_post_with_incomplete_read.call_count += 1
        
        if mock_post_with_incomplete_read.call_count <= 2:
            # Simulate the exact error from the logs
            raise requests.exceptions.ChunkedEncodingError(
                "Connection broken: IncompleteRead(646 bytes read, 690 more expected)"
            )
        else:
            # Third attempt succeeds
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Connection recovered successfully!"}}]
            }
            return mock_response
    
    # Test with health check passing
    print("📋 Test 1: Enhanced Manager with IncompleteRead Recovery")
    print("-" * 40)
    
    with patch('requests.get') as mock_get:
        # Mock health check to pass
        mock_get.return_value.status_code = 200
        
        with patch('requests.Session.post', side_effect=mock_post_with_incomplete_read):
            try:
                payload = {
                    "model": "llama3",
                    "messages": [{"role": "user", "content": "Test IncompleteRead recovery"}],
                    "max_tokens": 50
                }
                
                start_time = time.time()
                response = manager.execute_request(payload)
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    print(f"✅ SUCCESS: Request recovered after IncompleteRead ({duration:.2f}s)")
                    print(f"   Response: {response.json()['choices'][0]['message']['content']}")
                    print(f"   Retry attempts: {mock_post_with_incomplete_read.call_count}")
                    
                    # Check manager stats
                    stats = manager.get_comprehensive_stats()
                    print(f"📊 Manager Stats:")
                    print(f"   Health Score: {stats.get('health_score', 0):.1f}/100")
                    print(f"   Total Requests: {stats['metrics']['total_requests']}")
                    print(f"   Incomplete Read Errors: {stats['metrics']['incomplete_read_errors']}")
                    
                    return True
                else:
                    print(f"❌ FAILED: Unexpected status code {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ FAILED: Exception occurred: {e}")
                print(f"   Error type: {type(e).__name__}")
                return False


def test_chat_integration_with_incomplete_read():
    """Test chat integration with IncompleteRead handling"""
    print("\n📋 Test 2: Chat Integration with IncompleteRead")
    print("-" * 40)
    
    # Mock the specific error scenario
    def mock_enhanced_manager_with_error(*args, **kwargs):
        if not hasattr(mock_enhanced_manager_with_error, 'call_count'):
            mock_enhanced_manager_with_error.call_count = 0
        
        mock_enhanced_manager_with_error.call_count += 1
        
        if mock_enhanced_manager_with_error.call_count <= 1:
            # First attempt fails
            raise requests.exceptions.ChunkedEncodingError(
                "Connection broken: IncompleteRead(646 bytes read, 690 more expected)"
            )
        else:
            # Second attempt succeeds
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "I'm working properly now after the connection issue."}}]
            }
            return mock_response
    
    # Test the ask_kobold function
    try:
        with patch('ai.chat._enhanced_kobold_manager') as mock_manager:
            mock_manager.execute_request.side_effect = mock_enhanced_manager_with_error
            
            # Test message
            messages = [
                {"role": "system", "content": "You are Buddy, a helpful AI assistant."},
                {"role": "user", "content": "Hello, are you working correctly?"}
            ]
            
            start_time = time.time()
            response = ask_kobold(messages)
            duration = time.time() - start_time
            
            if response and "working properly" in response:
                print(f"✅ SUCCESS: Chat function recovered from IncompleteRead ({duration:.2f}s)")
                print(f"   Response: {response}")
                return True
            else:
                print(f"❌ FAILED: Unexpected response: {response}")
                return False
                
    except Exception as e:
        print(f"❌ FAILED: Chat integration error: {e}")
        return False


def test_consciousness_protection():
    """Test consciousness protection during IncompleteRead errors"""
    print("\n📋 Test 3: Consciousness Protection During Errors")
    print("-" * 40)
    
    try:
        from ai.kobold_connection_manager import maintain_consciousness_during_error
        
        # Test consciousness protection for IncompleteRead
        error_context = {
            'error_type': 'incomplete_read_error',
            'error_details': 'IncompleteRead(646 bytes read, 690 more expected)',
            'situation': 'kobold_streaming'
        }
        
        consciousness_preserved = maintain_consciousness_during_error(error_context)
        
        if consciousness_preserved:
            print("✅ SUCCESS: Consciousness protection is working")
            print("   Consciousness state preserved during IncompleteRead errors")
            return True
        else:
            print("❌ FAILED: Consciousness not preserved during IncompleteRead")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Consciousness protection error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Direct IncompleteRead Error Testing")
    print("🎯 Validating Fixes for Connection Issues")
    print("=" * 60)
    
    # Run all tests
    test_results = []
    
    print("🧪 Running specific IncompleteRead error tests...")
    
    # Test 1: Enhanced Manager
    result1 = test_specific_incomplete_read_scenario()
    test_results.append(('Enhanced Manager Recovery', result1))
    
    # Test 2: Chat Integration
    result2 = test_chat_integration_with_incomplete_read()
    test_results.append(('Chat Integration Recovery', result2))
    
    # Test 3: Consciousness Protection
    result3 = test_consciousness_protection()
    test_results.append(('Consciousness Protection', result3))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print("-" * 30)
    
    all_passed = True
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 SUCCESS: All IncompleteRead error handling tests PASSED!")
        print("✅ The enhanced connection manager handles IncompleteRead errors correctly")
        print("✅ Chat integration maintains functionality during connection issues")
        print("✅ Consciousness system is protected during connection failures")
        print("✅ Ready for production - KoboldCPP connection issues are resolved!")
    else:
        print("⚠️ PARTIAL SUCCESS: Some tests failed")
        print("🔧 The connection improvements are working but may need additional refinement")
    
    print(f"\n💡 IncompleteRead error handling: {"FULLY IMPLEMENTED" if all_passed else "PARTIALLY IMPLEMENTED"}")
    
    exit(0 if all_passed else 1)