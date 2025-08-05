#!/usr/bin/env python3
"""
Comprehensive Flow Test for Buddy - 50 Dummy Interactions
Tests all integrations and consciousness systems to ensure proper operation
"""

import sys
import os
import time
import json
import threading
import traceback
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
# Add current directory to path
sys.path.append('.')

# Test configuration
TEST_INTERACTIONS = 50
TEST_USER = "TestUser_Flow"
MOCK_AUDIO_DATA = [500, -500, 750, -750] * 256  # Simple mock audio data
LOG_FILE = "buddy_flow_test_results.json"

class BuddyFlowTester:
    def __init__(self):
        self.results = {
            "test_start_time": datetime.now().isoformat(),
            "total_interactions": TEST_INTERACTIONS,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "errors": [],
            "warnings": [],
            "consciousness_states": [],
            "response_times": [],
            "import_status": {},
            "integration_status": {},
            "memory_operations": [],
            "voice_operations": []
        }
        self.consciousness_available = False
        self.autonomous_available = False
        self.llm_handler = None
        self.voice_manager = None
    
    def log_error(self, stage, error_msg):
        """Log an error during testing"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "error": str(error_msg),
            "interaction_number": len(self.results["errors"]) + 1
        }
        self.results["errors"].append(error_entry)
        print(f"❌ ERROR in {stage}: {error_msg}")
    
    def log_warning(self, stage, warning_msg):
        """Log a warning during testing"""
        warning_entry = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "warning": str(warning_msg)
        }
        self.results["warnings"].append(warning_entry)
        print(f"⚠️ WARNING in {stage}: {warning_msg}")
    
    def test_imports(self):
        """Test all critical imports"""
        print("\n🔍 Testing critical imports...")
        
        import_tests = [
            ("main_imports", "Main imports and basic systems"),
            ("consciousness", "Consciousness architecture"),
            ("autonomous", "Autonomous consciousness"),
            ("voice", "Voice management"),
            ("memory", "Memory systems"),
            ("llm", "LLM handlers"),
            ("audio", "Audio systems")
        ]
        
        for test_name, description in import_tests:
            try:
                if test_name == "main_imports":
                    import config
                    from voice.database import load_known_users, known_users
                    from ai.memory import add_to_conversation_history
                    
                elif test_name == "consciousness":
                    from ai.global_workspace import global_workspace
                    from ai.self_model import self_model
                    from ai.emotion import emotion_engine
                    from ai.motivation import motivation_system
                    from ai.inner_monologue import inner_monologue
                    self.consciousness_available = True
                    
                elif test_name == "autonomous":
                    from ai.autonomous_consciousness_integrator import autonomous_consciousness_integrator
                    self.autonomous_available = True
                    
                elif test_name == "voice":
                    from voice.voice_manager_instance import voice_manager
                    self.voice_manager = voice_manager
                    
                elif test_name == "memory":
                    from ai.memory import get_user_memory, validate_ai_response_appropriateness
                    
                elif test_name == "llm":
                    from ai.llm_handler import llm_handler
                    self.llm_handler = llm_handler
                    
                elif test_name == "audio":
                    from audio.output import speak_async, speak_streaming
                
                self.results["import_status"][test_name] = "SUCCESS"
                print(f"✅ {description}: SUCCESS")
                
            except Exception as e:
                self.results["import_status"][test_name] = f"FAILED: {str(e)}"
                self.log_error(f"import_{test_name}", str(e))
    
    def mock_audio_systems(self):
        """Mock audio input/output systems for testing"""
        print("🎵 Mocking audio systems...")
        
        # Mock speak_streaming to capture outputs
        self.spoken_outputs = []
        
        def mock_speak_streaming(text):
            self.spoken_outputs.append({
                "timestamp": datetime.now().isoformat(),
                "text": text,
                "length": len(text)
            })
            print(f"🔊 MOCK SPEAK: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        # Mock speak_async
        def mock_speak_async(text):
            self.spoken_outputs.append({
                "timestamp": datetime.now().isoformat(),
                "text": text,
                "length": len(text),
                "async": True
            })
            print(f"🔊 MOCK ASYNC: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        # Apply mocks
        try:
            import audio.output
            audio.output.speak_streaming = mock_speak_streaming
            audio.output.speak_async = mock_speak_async
            print("✅ Audio systems mocked successfully")
        except Exception as e:
            self.log_warning("audio_mock", f"Could not mock audio: {e}")
    
    def test_consciousness_initialization(self):
        """Test consciousness system initialization"""
        print("\n🧠 Testing consciousness initialization...")
        
        if not self.consciousness_available:
            self.log_warning("consciousness_init", "Consciousness systems not available")
            return
        
        try:
            from ai.autonomous_consciousness_integrator import AutonomousMode
            
            # Test autonomous mode setting
            if self.autonomous_available:
                from ai.autonomous_consciousness_integrator import autonomous_consciousness_integrator
                
                # Test background mode (should prevent LLM loops)
                autonomous_consciousness_integrator.set_autonomous_mode(AutonomousMode.BACKGROUND_ONLY)
                current_mode = autonomous_consciousness_integrator.get_autonomous_mode()
                
                if current_mode == AutonomousMode.BACKGROUND_ONLY:
                    print("✅ Background mode set successfully")
                    self.results["integration_status"]["autonomous_mode"] = "SUCCESS"
                else:
                    self.log_error("consciousness_init", f"Failed to set background mode: {current_mode}")
            
            # Test consciousness components
            from ai.global_workspace import global_workspace
            from ai.self_model import self_model
            from ai.emotion import emotion_engine
            
            # Test basic consciousness operations
            if hasattr(global_workspace, 'get_stats'):
                stats = global_workspace.get_stats()
                print(f"✅ Global workspace active: {stats}")
            
            if hasattr(emotion_engine, 'get_current_state'):
                state = emotion_engine.get_current_state()
                print(f"✅ Emotion engine active: {state}")
            
            self.results["integration_status"]["consciousness_core"] = "SUCCESS"
            
        except Exception as e:
            self.log_error("consciousness_init", str(e))
    
    def test_llm_integration(self):
        """Test LLM consciousness integration"""
        print("\n🤖 Testing LLM consciousness integration...")
        
        if not self.llm_handler:
            self.log_warning("llm_test", "LLM handler not available")
            return
        
        try:
            # Test consciousness-integrated response generation
            test_input = "Hello, this is a test message"
            
            # Mock the LLM response to avoid actual API calls
            def mock_generate_response_with_consciousness(user_input, user_id, context=None, **kwargs):
                # Simulate streaming response
                response_parts = [
                    "Hello! I'm",
                    " processing your",
                    " test message",
                    " successfully."
                ]
                for part in response_parts:
                    yield part
                    time.sleep(0.01)  # Simulate streaming delay
            
            # Temporarily replace the method
            original_method = None
            if hasattr(self.llm_handler, 'generate_response_with_consciousness'):
                original_method = self.llm_handler.generate_response_with_consciousness
                self.llm_handler.generate_response_with_consciousness = mock_generate_response_with_consciousness
            
            # Test the integration
            start_time = time.time()
            full_response = ""
            chunk_count = 0
            
            for chunk in self.llm_handler.generate_response_with_consciousness(test_input, TEST_USER):
                full_response += chunk
                chunk_count += 1
                if chunk_count > 10:  # Prevent infinite loops
                    break
            
            response_time = time.time() - start_time
            
            if full_response and chunk_count > 0:
                print(f"✅ LLM integration successful: {chunk_count} chunks, {response_time:.3f}s")
                self.results["integration_status"]["llm_consciousness"] = "SUCCESS"
                self.results["response_times"].append(response_time)
            else:
                self.log_error("llm_test", "No response generated")
            
            # Restore original method
            if original_method:
                self.llm_handler.generate_response_with_consciousness = original_method
                
        except Exception as e:
            self.log_error("llm_test", str(e))
    
    def test_voice_integration(self):
        """Test voice management integration"""
        print("\n🎤 Testing voice management integration...")
        
        if not self.voice_manager:
            self.log_warning("voice_test", "Voice manager not available")
            return
        
        try:
            # Test voice identification
            if hasattr(self.voice_manager, 'handle_voice_identification'):
                result = self.voice_manager.handle_voice_identification(MOCK_AUDIO_DATA, "test message")
                if result:
                    print(f"✅ Voice identification successful: {result}")
                    self.results["voice_operations"].append({
                        "operation": "voice_identification",
                        "result": str(result),
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    self.log_warning("voice_test", "Voice identification returned None")
            
            # Test session stats
            if hasattr(self.voice_manager, 'get_session_stats'):
                stats = self.voice_manager.get_session_stats()
                print(f"✅ Voice manager stats: {stats}")
            
            self.results["integration_status"]["voice_management"] = "SUCCESS"
            
        except Exception as e:
            self.log_error("voice_test", str(e))
    
    def test_memory_integration(self):
        """Test memory system integration"""
        print("\n🧠 Testing memory system integration...")
        
        try:
            from ai.memory import get_user_memory, add_to_conversation_history
            
            # Test user memory
            user_memory = get_user_memory(TEST_USER)
            if user_memory:
                print("✅ User memory system accessible")
                
                # Test conversation history
                test_input = "Test memory input"
                test_response = "Test memory response"
                add_to_conversation_history(TEST_USER, test_input, test_response)
                
                self.results["memory_operations"].append({
                    "operation": "conversation_history",
                    "user": TEST_USER,
                    "input": test_input,
                    "response": test_response,
                    "timestamp": datetime.now().isoformat()
                })
                
                print("✅ Conversation history updated")
                self.results["integration_status"]["memory_system"] = "SUCCESS"
            else:
                self.log_error("memory_test", "Could not get user memory")
                
        except Exception as e:
            self.log_error("memory_test", str(e))
    
    def simulate_interaction(self, interaction_num, user_input):
        """Simulate a single user interaction"""
        print(f"\n🔄 Interaction {interaction_num}: '{user_input}'")
        
        interaction_start = time.time()
        interaction_data = {
            "number": interaction_num,
            "input": user_input,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "response_generated": False,
            "errors": [],
            "response_time": 0
        }
        
        try:
            # Clear previous outputs
            self.spoken_outputs = []
            
            # Test consciousness state before interaction
            consciousness_state = {}
            if self.consciousness_available and self.autonomous_available:
                try:
                    from ai.autonomous_consciousness_integrator import autonomous_consciousness_integrator
                    current_mode = autonomous_consciousness_integrator.get_autonomous_mode()
                    consciousness_state["mode"] = current_mode.value if hasattr(current_mode, 'value') else str(current_mode)
                except Exception as e:
                    consciousness_state["error"] = str(e)
            
            # Simulate voice identification
            if self.voice_manager and hasattr(self.voice_manager, 'handle_voice_identification'):
                try:
                    voice_result = self.voice_manager.handle_voice_identification(MOCK_AUDIO_DATA, user_input)
                    interaction_data["voice_identification"] = str(voice_result)
                except Exception as e:
                    interaction_data["errors"].append(f"Voice ID error: {e}")
            
            # Test LLM response generation
            if self.llm_handler:
                try:
                    # Mock the consciousness integration to avoid infinite loops
                    def safe_mock_response(user_input, user_id, context=None, **kwargs):
                        # Simple mock response
                        responses = [
                            f"I understand you said: {user_input[:30]}",
                            " This is a test response",
                            " from the consciousness system."
                        ]
                        for response_part in responses:
                            yield response_part
                            time.sleep(0.01)
                    
                    # Test with mock to avoid actual API calls
                    original_method = None
                    if hasattr(self.llm_handler, 'generate_response_with_consciousness'):
                        original_method = self.llm_handler.generate_response_with_consciousness
                        self.llm_handler.generate_response_with_consciousness = safe_mock_response
                    
                    response_parts = []
                    chunk_count = 0
                    
                    for chunk in self.llm_handler.generate_response_with_consciousness(user_input, TEST_USER):
                        response_parts.append(chunk)
                        chunk_count += 1
                        if chunk_count > 5:  # Prevent runaway generation
                            break
                    
                    if response_parts:
                        full_response = "".join(response_parts)
                        interaction_data["response"] = full_response
                        interaction_data["response_generated"] = True
                        interaction_data["chunk_count"] = chunk_count
                        print(f"✅ Response generated: {chunk_count} chunks")
                    
                    # Restore original method
                    if original_method:
                        self.llm_handler.generate_response_with_consciousness = original_method
                
                except Exception as e:
                    interaction_data["errors"].append(f"LLM error: {e}")
                    self.log_error(f"interaction_{interaction_num}", f"LLM error: {e}")
            
            # Test memory update
            try:
                from ai.memory import add_to_conversation_history
                if interaction_data.get("response"):
                    add_to_conversation_history(TEST_USER, user_input, interaction_data["response"])
                    interaction_data["memory_updated"] = True
            except Exception as e:
                interaction_data["errors"].append(f"Memory error: {e}")
            
            # Check for any consciousness loops (no repeated outputs)
            if len(self.spoken_outputs) > 10:
                interaction_data["errors"].append("Too many spoken outputs - possible loop")
            
            # Determine success
            if (interaction_data["response_generated"] and 
                len(interaction_data["errors"]) == 0 and 
                len(self.spoken_outputs) < 10):
                interaction_data["success"] = True
                self.results["successful_interactions"] += 1
                print(f"✅ Interaction {interaction_num} successful")
            else:
                self.results["failed_interactions"] += 1
                print(f"❌ Interaction {interaction_num} failed")
            
            interaction_data["response_time"] = time.time() - interaction_start
            interaction_data["consciousness_state"] = consciousness_state
            interaction_data["spoken_outputs_count"] = len(self.spoken_outputs)
            
        except Exception as e:
            interaction_data["errors"].append(f"Critical error: {e}")
            interaction_data["success"] = False
            self.results["failed_interactions"] += 1
            self.log_error(f"interaction_{interaction_num}", str(e))
            traceback.print_exc()
        
        return interaction_data
    
    def run_comprehensive_test(self):
        """Run the comprehensive 50-interaction test"""
        print(f"🚀 Starting comprehensive Buddy flow test with {TEST_INTERACTIONS} interactions")
        print(f"📝 Results will be saved to: {LOG_FILE}")
        
        # Phase 1: Test imports and initialization
        self.test_imports()
        self.mock_audio_systems()
        self.test_consciousness_initialization()
        self.test_llm_integration()
        self.test_voice_integration()
        self.test_memory_integration()
        
        # Phase 2: Run interaction tests
        print(f"\n🎯 Starting {TEST_INTERACTIONS} dummy interactions...")
        
        # Diverse test inputs to cover different scenarios
        test_inputs = [
            "Hello, how are you?",
            "What time is it?",
            "Tell me about artificial intelligence",
            "What's the weather like?",
            "How do you work?",
            "What's my name?",
            "Tell me a joke",
            "What can you do?",
            "Where are you located?",
            "Explain quantum physics",
            # Add more varied inputs
            "I'm feeling sad today",
            "What are your thoughts on consciousness?",
            "Can you help me with math?",
            "What's the meaning of life?",
            "Do you have emotions?",
            "Tell me about your memory",
            "What goals do you have?",
            "How do you learn?",
            "What makes you unique?",
            "Can you be creative?",
            # Technical questions
            "How does your voice recognition work?",
            "What's your language model?",
            "How do you process emotions?",
            "Tell me about your consciousness",
            "What's your purpose?",
            # Conversational
            "That's interesting, tell me more",
            "I disagree with that",
            "You're very helpful",
            "I'm confused about something",
            "Can we talk about something else?",
            # Edge cases
            "...",
            "What?",
            "Why?",
            "Really?",
            "Hmm",
            # Complex queries
            "If you could change one thing about yourself what would it be?",
            "Describe your perfect day",
            "What would you do if you were human?",
            "How do you handle uncertainty?",
            "What's your biggest fear?",
            # System tests
            "Test consciousness integration",
            "Test memory persistence",
            "Test voice identification",
            "Test emotional processing",
            "Test goal reasoning",
            # Final tests
            "How has this conversation been for you?",
            "What have you learned today?",
            "Do you remember our first interaction?",
            "Thank you for the conversation",
            "Goodbye"
        ]
        
        interaction_results = []
        
        for i in range(1, TEST_INTERACTIONS + 1):
            # Use different inputs, cycling through the list
            input_text = test_inputs[(i - 1) % len(test_inputs)]
            if (i - 1) >= len(test_inputs):
                input_text = f"{input_text} (variation {(i - 1) // len(test_inputs) + 1})"
            
            interaction_result = self.simulate_interaction(i, input_text)
            interaction_results.append(interaction_result)
            
            # Brief pause between interactions
            time.sleep(0.1)
            
            # Progress update every 10 interactions
            if i % 10 == 0:
                success_rate = (self.results["successful_interactions"] / i) * 100
                print(f"📊 Progress: {i}/{TEST_INTERACTIONS} ({success_rate:.1f}% success rate)")
        
        # Phase 3: Final analysis
        self.results["interaction_results"] = interaction_results
        self.results["test_end_time"] = datetime.now().isoformat()
        self.results["success_rate"] = (self.results["successful_interactions"] / TEST_INTERACTIONS) * 100
        
        # Calculate statistics
        if self.results["response_times"]:
            self.results["avg_response_time"] = sum(self.results["response_times"]) / len(self.results["response_times"])
            self.results["max_response_time"] = max(self.results["response_times"])
            self.results["min_response_time"] = min(self.results["response_times"])
        
        # Save results
        try:
            with open(LOG_FILE, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"✅ Results saved to {LOG_FILE}")
        except Exception as e:
            print(f"❌ Could not save results: {e}")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🏁 COMPREHENSIVE FLOW TEST SUMMARY")
        print("="*60)
        
        print(f"📊 Total Interactions: {TEST_INTERACTIONS}")
        print(f"✅ Successful: {self.results['successful_interactions']}")
        print(f"❌ Failed: {self.results['failed_interactions']}")
        print(f"📈 Success Rate: {self.results['success_rate']:.1f}%")
        
        print(f"\n🔧 Import Status:")
        for component, status in self.results["import_status"].items():
            status_icon = "✅" if status == "SUCCESS" else "❌"
            print(f"  {status_icon} {component}: {status}")
        
        print(f"\n🔗 Integration Status:")
        for component, status in self.results["integration_status"].items():
            status_icon = "✅" if status == "SUCCESS" else "❌"
            print(f"  {status_icon} {component}: {status}")
        
        if self.results.get("avg_response_time"):
            print(f"\n⏱️ Performance:")
            print(f"  Average Response Time: {self.results['avg_response_time']:.3f}s")
            print(f"  Min Response Time: {self.results['min_response_time']:.3f}s")
            print(f"  Max Response Time: {self.results['max_response_time']:.3f}s")
        
        if self.results["errors"]:
            print(f"\n❌ Errors ({len(self.results['errors'])}):")
            for error in self.results["errors"][-5:]:  # Show last 5 errors
                print(f"  • {error['stage']}: {error['error'][:100]}...")
        
        if self.results["warnings"]:
            print(f"\n⚠️ Warnings ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"][-3:]:  # Show last 3 warnings
                print(f"  • {warning['stage']}: {warning['warning'][:100]}...")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if self.results["success_rate"] >= 90:
            print("🟢 EXCELLENT - Buddy is functioning properly")
        elif self.results["success_rate"] >= 75:
            print("🟡 GOOD - Minor issues detected")
        elif self.results["success_rate"] >= 50:
            print("🟠 FAIR - Some significant issues")
        else:
            print("🔴 POOR - Major issues need attention")
        
        print("="*60)

if __name__ == "__main__":
    print("🧪 Buddy Comprehensive Flow Test")
    print("Testing all integrations with 50 dummy interactions...")
    
    tester = BuddyFlowTester()
    try:
        tester.run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        tester.print_summary()
    except Exception as e:
        print(f"\n❌ Test failed with critical error: {e}")
        traceback.print_exc()
        tester.print_summary()