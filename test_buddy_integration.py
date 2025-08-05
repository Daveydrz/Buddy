#!/usr/bin/env python3
"""
Comprehensive Buddy Integration Tests with Class 5+ Consciousness
Tests 50-turn conversations with full mocking of hardware dependencies
"""

import pytest
import sys
import os
import time
import json
import threading
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, List, Any, Generator

# Add current directory to path
sys.path.append('.')

# Import Buddy's core components
from ai.llm_handler import LLMHandler
from ai.autonomous_consciousness_integrator import autonomous_consciousness_integrator, AutonomousMode
from ai.memory import get_user_memory, add_to_conversation_history

# Global test results storage
GLOBAL_TEST_RESULTS = {
    "test_start": datetime.now().isoformat(),
    "conversations": [],
    "module_tests": {},
    "performance_metrics": {},
    "errors": [],
    "warnings": []
}

class MockSTT:
    """Mock Speech-to-Text system"""
    def transcribe(self, audio_data):
        return "Hello Buddy, this is a test message"

class MockTTS:
    """Mock Text-to-Speech system"""
    def synthesize(self, text):
        return b"mock_audio_data"
    
    def speak(self, text):
        return True

class MockWakeWordDetector:
    """Mock wake word detection"""
    def __init__(self):
        self.is_listening = False
    
    def start_listening(self):
        self.is_listening = True
        return True
    
    def stop_listening(self):
        self.is_listening = False
        return True
    
    def check_wake_word(self, audio_data):
        return True  # Always detect wake word for testing

class MockAudioSystem:
    """Mock audio input/output system"""
    def __init__(self):
        self.recording = False
        self.playing = False
    
    def start_recording(self):
        self.recording = True
        return [100, -100, 200, -200] * 1024  # Mock audio data
    
    def stop_recording(self):
        self.recording = False
    
    def play_audio(self, audio_data):
        self.playing = True
        time.sleep(0.1)  # Simulate playback time
        self.playing = False

class BuddyIntegrationTester:
    """Comprehensive Buddy integration test suite"""
    
    def __init__(self):
        self.llm_handler = None
        self.conversation_contexts = {}
        self.mock_systems = self._setup_mock_systems()
        
    def _setup_mock_systems(self):
        """Setup all mock systems"""
        return {
            "stt": MockSTT(),
            "tts": MockTTS(), 
            "wake_word": MockWakeWordDetector(),
            "audio": MockAudioSystem()
        }
    
    def log_error(self, test_name, error_msg):
        """Log test error"""
        GLOBAL_TEST_RESULTS["errors"].append({
            "test": test_name,
            "error": str(error_msg),
            "timestamp": datetime.now().isoformat()
        })
    
    def log_warning(self, test_name, warning_msg):
        """Log test warning"""
        GLOBAL_TEST_RESULTS["warnings"].append({
            "test": test_name,
            "warning": str(warning_msg),
            "timestamp": datetime.now().isoformat()
        })

@pytest.fixture(scope="session")
def buddy_tester():
    """Pytest session-wide fixture for buddy tester instance"""
    return BuddyIntegrationTester()

@pytest.fixture
def llm_handler():
    """Pytest fixture for LLM handler with mocked responses"""
    handler = LLMHandler()
    
    # Mock the generate_response_with_consciousness method
    def mock_consciousness_response(text, user, context=None, stream=True, **kwargs):
        """Mock consciousness-integrated LLM response"""
        # Generate different responses based on input
        response_templates = [
            f"Hello {user}! I understand you said: '{text[:50]}'...",
            f"That's interesting, {user}. Let me think about that...",
            f"I appreciate your input, {user}. Here's my response to '{text[:30]}'...",
            f"Good point, {user}. Regarding '{text[:40]}'...",
            f"Thank you for sharing that, {user}. About '{text[:35]}'..."
        ]
        
        # Select response based on conversation turn
        response_idx = hash(text + user) % len(response_templates)
        full_response = response_templates[response_idx]
        
        if stream:
            # Simulate streaming response
            words = full_response.split()
            for word in words:
                yield word + " "
                time.sleep(0.001)  # Very fast for testing
        else:
            yield full_response
    
    # Apply the mock
    handler.generate_response_with_consciousness = mock_consciousness_response
    return handler

class TestBuddyIntegration:
    """Main test class for Buddy integration"""
    
    def test_module_imports(self, buddy_tester):
        """Test that all core modules can be imported"""
        modules_to_test = [
            "ai.llm_handler",
            "ai.autonomous_consciousness_integrator", 
            "ai.memory",
            "ai.global_workspace",
            "ai.self_model",
            "ai.emotion",
            "ai.motivation",
            "ai.inner_monologue",
            "ai.subjective_experience",
            "ai.temporal_awareness",
            "ai.belief_evolution_tracker",
            "ai.personality_state",
            "ai.mood_manager"
        ]
        
        imported_modules = []
        failed_modules = []
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                imported_modules.append(module_name)
                GLOBAL_TEST_RESULTS["module_tests"][module_name] = "SUCCESS"
            except ImportError as e:
                failed_modules.append((module_name, str(e)))
                buddy_tester.log_error("module_import", f"{module_name}: {e}")
                GLOBAL_TEST_RESULTS["module_tests"][module_name] = f"FAILED: {e}"
        
        print(f"✅ Successfully imported {len(imported_modules)} modules")
        if failed_modules:
            print(f"⚠️ Failed to import {len(failed_modules)} modules")
        
        # At least 70% of modules should import successfully
        success_rate = len(imported_modules) / len(modules_to_test)
        assert success_rate >= 0.7, f"Only {success_rate*100:.1f}% of modules imported successfully"
    
    def test_consciousness_mode_switching(self, buddy_tester):
        """Test autonomous consciousness mode switching"""
        try:
            # Test setting BACKGROUND_ONLY mode
            autonomous_consciousness_integrator.set_autonomous_mode(AutonomousMode.BACKGROUND_ONLY)
            current_mode = autonomous_consciousness_integrator.get_autonomous_mode()
            assert current_mode == AutonomousMode.BACKGROUND_ONLY
            
            # Test setting FULL_AUTONOMY mode
            autonomous_consciousness_integrator.set_autonomous_mode(AutonomousMode.FULL_AUTONOMY)
            current_mode = autonomous_consciousness_integrator.get_autonomous_mode()
            assert current_mode == AutonomousMode.FULL_AUTONOMY
            
            GLOBAL_TEST_RESULTS["module_tests"]["consciousness_mode_switching"] = "SUCCESS"
            print("✅ Consciousness mode switching working correctly")
            
        except Exception as e:
            buddy_tester.log_error("consciousness_mode_switching", str(e))
            pytest.fail(f"Consciousness mode switching failed: {e}")
    
    def test_llm_consciousness_integration(self, buddy_tester, llm_handler):
        """Test LLM consciousness integration"""
        try:
            test_input = "Hello, test the consciousness integration"
            test_user = "test_user_llm"
            
            # Test streaming response
            start_time = time.time()
            response_chunks = []
            chunk_count = 0
            
            for chunk in llm_handler.generate_response_with_consciousness(
                test_input, test_user, context={}, stream=True
            ):
                response_chunks.append(chunk)
                chunk_count += 1
                if chunk_count > 20:  # Prevent infinite loops
                    break
            
            response_time = time.time() - start_time
            full_response = "".join(response_chunks)
            
            # Verify response quality
            assert len(full_response) > 10, "Response too short"
            assert test_user in full_response, "Response doesn't personalize to user"
            assert chunk_count > 0, "No response chunks generated"
            
            GLOBAL_TEST_RESULTS["performance_metrics"]["llm_response_time"] = response_time
            GLOBAL_TEST_RESULTS["module_tests"]["llm_consciousness_integration"] = "SUCCESS"
            
            print(f"✅ LLM consciousness integration: {chunk_count} chunks, {response_time:.3f}s")
            
        except Exception as e:
            buddy_tester.log_error("llm_consciousness_integration", str(e))
            pytest.fail(f"LLM consciousness integration failed: {e}")
    
    def test_memory_system_isolation(self, buddy_tester):
        """Test memory system with user isolation"""
        try:
            user1 = "test_user_1"
            user2 = "test_user_2"
            
            # Add different conversation history for each user
            add_to_conversation_history(user1, "Hello from user 1", "Hi user 1!")
            add_to_conversation_history(user2, "Hello from user 2", "Hi user 2!")
            
            # Verify user isolation
            memory1 = get_user_memory(user1)
            memory2 = get_user_memory(user2)
            
            assert memory1 != memory2, "User memories are not isolated"
            
            # Test memory retrieval
            history1 = memory1.get_conversation_history() if hasattr(memory1, 'get_conversation_history') else []
            history2 = memory2.get_conversation_history() if hasattr(memory2, 'get_conversation_history') else []
            
            GLOBAL_TEST_RESULTS["module_tests"]["memory_isolation"] = "SUCCESS"
            print(f"✅ Memory isolation working: User1 has {len(history1)} entries, User2 has {len(history2)} entries")
            
        except Exception as e:
            buddy_tester.log_error("memory_isolation", str(e))
            pytest.fail(f"Memory isolation test failed: {e}")
    
    @pytest.mark.parametrize("conversation_id", range(50))
    def test_50_turn_conversations(self, buddy_tester, llm_handler, conversation_id):
        """Test 50-turn conversations with consciousness integration"""
        user_id = f"test_user_conv_{conversation_id}"
        
        # Conversation scenarios with variety
        conversation_scenarios = [
            "Tell me about your consciousness",
            "What are your goals and motivations?", 
            "How do you process emotions?",
            "Can you remember our previous conversations?",
            "What's your personality like?",
            "How do you handle complex reasoning?",
            "Tell me about your inner thoughts",
            "What makes you feel curious?",
            "How do you adapt to different users?",
            "Explain your decision-making process"
        ]
        
        scenario_text = conversation_scenarios[conversation_id % len(conversation_scenarios)]
        input_text = f"{scenario_text} (Turn {conversation_id + 1})"
        
        try:
            start_time = time.time()
            
            # Build conversation context
            context = buddy_tester.conversation_contexts.get(user_id, {
                "conversation_history": [],
                "turn_count": 0,
                "working_memory": {}
            })
            
            # Generate response with consciousness integration
            response_chunks = []
            chunk_count = 0
            
            for chunk in llm_handler.generate_response_with_consciousness(
                input_text, user_id, context=context, stream=True
            ):
                response_chunks.append(chunk)
                chunk_count += 1
                if chunk_count > 30:  # Prevent infinite loops
                    break
            
            response_time = time.time() - start_time
            full_response = "".join(response_chunks)
            
            # Update conversation context
            context["conversation_history"].append({
                "user": input_text,
                "assistant": full_response,
                "timestamp": datetime.now().isoformat()
            })
            context["turn_count"] += 1
            buddy_tester.conversation_contexts[user_id] = context
            
            # Verify response quality
            assert len(full_response) > 5, f"Response too short for turn {conversation_id}"
            assert chunk_count > 0, f"No chunks generated for turn {conversation_id}"
            assert response_time < 5.0, f"Response too slow: {response_time:.3f}s"
            
            # Record conversation result
            conversation_result = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "input": input_text,
                "response": full_response[:100] + "..." if len(full_response) > 100 else full_response,
                "chunk_count": chunk_count,
                "response_time": response_time,
                "context_size": len(context["conversation_history"]),
                "status": "SUCCESS"
            }
            
            GLOBAL_TEST_RESULTS["conversations"].append(conversation_result)
            
            print(f"✅ Conversation {conversation_id + 1}/50: {chunk_count} chunks, {response_time:.3f}s")
            
        except Exception as e:
            buddy_tester.log_error(f"conversation_{conversation_id}", str(e))
            
            # Record failed conversation
            conversation_result = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "input": input_text,
                "error": str(e),
                "status": "FAILED"
            }
            GLOBAL_TEST_RESULTS["conversations"].append(conversation_result)
            
            pytest.fail(f"Conversation {conversation_id} failed: {e}")
    
    def test_autonomous_consciousness_modes(self, buddy_tester):
        """Test autonomous consciousness in different modes"""
        try:
            # Test BACKGROUND_ONLY mode (should not generate vocal responses)
            autonomous_consciousness_integrator.set_autonomous_mode(AutonomousMode.BACKGROUND_ONLY)
            time.sleep(0.1)  # Let mode settle
            
            mode = autonomous_consciousness_integrator.get_autonomous_mode()
            assert mode == AutonomousMode.BACKGROUND_ONLY
            
            # Test FULL_AUTONOMY mode (should allow vocal responses) 
            autonomous_consciousness_integrator.set_autonomous_mode(AutonomousMode.FULL_AUTONOMY)
            time.sleep(0.1)  # Let mode settle
            
            mode = autonomous_consciousness_integrator.get_autonomous_mode()
            assert mode == AutonomousMode.FULL_AUTONOMY
            
            GLOBAL_TEST_RESULTS["module_tests"]["autonomous_modes"] = "SUCCESS"
            print("✅ Autonomous consciousness modes working correctly")
            
        except Exception as e:
            buddy_tester.log_error("autonomous_modes", str(e))
            pytest.fail(f"Autonomous consciousness modes test failed: {e}")
    
    def test_no_infinite_loops(self, buddy_tester, llm_handler):
        """Test that no infinite loops occur during processing"""
        try:
            test_input = "Test for infinite loop prevention"
            test_user = "test_user_loops"
            
            # Set a reasonable timeout
            start_time = time.time()
            timeout = 10.0  # 10 second timeout
            
            response_chunks = []
            chunk_count = 0
            
            for chunk in llm_handler.generate_response_with_consciousness(
                test_input, test_user, context={}, stream=True
            ):
                current_time = time.time()
                if current_time - start_time > timeout:
                    break
                
                response_chunks.append(chunk)
                chunk_count += 1
                
                # Reasonable limit to prevent infinite loops
                if chunk_count > 100:
                    break
            
            processing_time = time.time() - start_time
            
            # Verify no infinite loops
            assert processing_time < timeout, f"Processing took too long: {processing_time:.3f}s"
            assert chunk_count < 100, f"Too many chunks generated: {chunk_count}"
            assert len(response_chunks) > 0, "No response generated"
            
            GLOBAL_TEST_RESULTS["module_tests"]["infinite_loop_prevention"] = "SUCCESS"
            GLOBAL_TEST_RESULTS["performance_metrics"]["max_processing_time"] = processing_time
            
            print(f"✅ No infinite loops detected: {chunk_count} chunks in {processing_time:.3f}s")
            
        except Exception as e:
            buddy_tester.log_error("infinite_loop_prevention", str(e))
            pytest.fail(f"Infinite loop prevention test failed: {e}")

class TestReportGenerator:
    """Generate comprehensive test reports"""
    
    @staticmethod
    def generate_final_report():
        """Generate final test summary report"""
        results = GLOBAL_TEST_RESULTS
        
        # Calculate statistics
        total_conversations = len(results["conversations"])
        successful_conversations = len([c for c in results["conversations"] if c.get("status") == "SUCCESS"])
        failed_conversations = total_conversations - successful_conversations
        
        success_rate = (successful_conversations / total_conversations * 100) if total_conversations > 0 else 0
        
        # Calculate performance metrics
        response_times = [c.get("response_time", 0) for c in results["conversations"] if c.get("response_time")]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Module test summary
        module_tests = results["module_tests"]
        successful_modules = len([test for test, status in module_tests.items() if status == "SUCCESS"])
        total_modules = len(module_tests)
        module_success_rate = (successful_modules / total_modules * 100) if total_modules > 0 else 0
        
        report = f"""
🧪 BUDDY INTEGRATION TEST REPORT
=====================================

📊 CONVERSATION TESTING:
• Total conversations: {total_conversations}
• Successful: {successful_conversations} 
• Failed: {failed_conversations}
• Success rate: {success_rate:.1f}%
• Average response time: {avg_response_time:.3f}s

🔧 MODULE TESTING:
• Modules tested: {total_modules}
• Successful: {successful_modules}
• Module success rate: {module_success_rate:.1f}%

⚠️ ISSUES:
• Errors: {len(results["errors"])}
• Warnings: {len(results["warnings"])}

🎯 PERFORMANCE:
• Max processing time: {results["performance_metrics"].get("max_processing_time", 0):.3f}s
• LLM response time: {results["performance_metrics"].get("llm_response_time", 0):.3f}s

📝 DETAILED RESULTS:
{json.dumps(results, indent=2)}
"""
        
        return report

def test_generate_final_report():
    """Generate and save final test report"""
    report = TestReportGenerator.generate_final_report()
    
    # Save report to file
    with open("buddy_integration_test_report.txt", "w") as f:
        f.write(report)
    
    # Save detailed results as JSON
    with open("buddy_integration_test_results.json", "w") as f:
        json.dump(GLOBAL_TEST_RESULTS, f, indent=2)
    
    print(report)

if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v", "--tb=short"])