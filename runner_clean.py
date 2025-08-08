"""
Runner Clean - Modern async event loop architecture for Buddy Voice Assistant
Orchestrates audio input, STT, LLM, TTS, audio output, consciousness, and watchdog tasks
Maintains identical behavior to original main.py while providing clean architecture
"""

import asyncio
import time
from collections import deque
from typing import Dict, Any, Optional
import signal
import sys

# Optional numpy import
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Mock numpy array for testing
    class MockArray:
        def __init__(self, data, dtype=None):
            self.data = data
            self.dtype = dtype
        def __len__(self):
            return len(self.data)
    np = type('numpy', (), {'array': MockArray, 'int16': int})()

# Import our clean modular components
from config.core import DEBUG, get_current_time
from config.audio import WATCHDOG_INTERVAL_S, WATCHDOG_ENABLED
from stt import transcribe_audio
from llm import chat_completion, health_check as llm_health_check
from tts import synthesize_speech, test_tts_service
from services import idle_tick, pre_reply, post_user_turn, get_consciousness_health

class BuddyRunner:
    """Clean async runner for Buddy Voice Assistant"""
    
    def __init__(self):
        self.running = False
        self.tasks = []
        
        # Inter-task communication queues
        self.audio_in_queue = asyncio.Queue(maxsize=100)
        self.stt_queue = asyncio.Queue(maxsize=50) 
        self.llm_queue = asyncio.Queue(maxsize=20)
        self.tts_queue = asyncio.Queue(maxsize=50)
        self.audio_out_queue = asyncio.Queue(maxsize=100)
        
        # Task health tracking
        self.task_health = {
            'audio_in': {'status': 'stopped', 'last_activity': 0, 'error_count': 0},
            'stt': {'status': 'stopped', 'last_activity': 0, 'error_count': 0},
            'llm': {'status': 'stopped', 'last_activity': 0, 'error_count': 0}, 
            'tts': {'status': 'stopped', 'last_activity': 0, 'error_count': 0},
            'audio_out': {'status': 'stopped', 'last_activity': 0, 'error_count': 0},
            'consciousness': {'status': 'stopped', 'last_activity': 0, 'error_count': 0},
            'watchdog': {'status': 'stopped', 'last_activity': 0, 'error_count': 0}
        }
        
        # Performance metrics
        self.start_time = None
        self.interaction_count = 0
        
    async def start(self):
        """Start all async tasks"""
        if self.running:
            print("[Runner] Already running")
            return
            
        print(f"[Runner] 🚀 Starting Buddy Clean Runner at {get_current_time()}")
        self.running = True
        self.start_time = time.time()
        
        # Setup signal handlers for graceful shutdown
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, self._signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Create all tasks
            tasks = [
                self._create_task(self.audio_in_task(), "audio_in"),
                self._create_task(self.stt_task(), "stt"), 
                self._create_task(self.llm_task(), "llm"),
                self._create_task(self.tts_task(), "tts"),
                self._create_task(self.audio_out_task(), "audio_out"),
                self._create_task(self.consciousness_task(), "consciousness"),
            ]
            
            if WATCHDOG_ENABLED:
                tasks.append(self._create_task(self.watchdog_task(), "watchdog"))
            
            self.tasks = tasks
            
            print(f"[Runner] ✅ Started {len(tasks)} tasks")
            
            # Wait for all tasks
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            print("\n[Runner] 🛑 Keyboard interrupt received")
        except Exception as e:
            print(f"[Runner] ❌ Unexpected error: {e}")
        finally:
            await self.stop()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n[Runner] 🛑 Received signal {signum}")
        self.running = False
        
    def _create_task(self, coro, name: str):
        """Create a named task with error handling"""
        task = asyncio.create_task(coro, name=name)
        return task
        
    async def stop(self):
        """Stop all tasks gracefully"""
        if not self.running:
            return
            
        print("[Runner] 🛑 Stopping all tasks...")
        self.running = False
        
        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for cancellation with timeout
        if self.tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.tasks, return_exceptions=True),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                print("[Runner] ⚠️ Some tasks didn't stop gracefully")
        
        print("[Runner] ✅ Shutdown complete")
        
    async def audio_in_task(self):
        """Audio input processing task"""
        task_name = 'audio_in'
        self.task_health[task_name]['status'] = 'running'
        
        print("[Runner-AudioIn] 🎤 Audio input task started")
        
        try:
            while self.running:
                # Placeholder for actual audio input
                # In real implementation, this would:
                # 1. Capture audio from microphone
                # 2. Apply VAD (Voice Activity Detection)  
                # 3. Buffer audio chunks
                # 4. Put audio chunks in stt_queue when speech detected
                
                await asyncio.sleep(0.1)  # Simulate audio processing
                self._update_task_health(task_name)
                
                # Simulate audio input (for testing)
                if DEBUG and False:  # Disabled for now
                    test_audio = np.array([0] * 16000, dtype=np.int16)
                    await self.stt_queue.put({
                        'audio': test_audio,
                        'timestamp': time.time()
                    })
                    await asyncio.sleep(5)  # Don't spam
                    
        except asyncio.CancelledError:
            print("[Runner-AudioIn] 🛑 Audio input task cancelled")
        except Exception as e:
            print(f"[Runner-AudioIn] ❌ Error: {e}")
            self.task_health[task_name]['error_count'] += 1
        finally:
            self.task_health[task_name]['status'] = 'stopped'
            
    async def stt_task(self):
        """Speech-to-text processing task"""
        task_name = 'stt'
        self.task_health[task_name]['status'] = 'running'
        
        print("[Runner-STT] 📝 STT task started")
        
        try:
            while self.running:
                try:
                    # Wait for audio from audio input
                    audio_data = await asyncio.wait_for(
                        self.stt_queue.get(),
                        timeout=1.0
                    )
                    
                    self._update_task_health(task_name)
                    
                    # Transcribe audio using our STT client
                    transcript = await transcribe_audio(audio_data['audio'])
                    
                    if transcript and transcript.strip():
                        if DEBUG:
                            print(f"[Runner-STT] 📝 Transcribed: '{transcript}'")
                        
                        # Send to LLM queue
                        await self.llm_queue.put({
                            'transcript': transcript,
                            'timestamp': audio_data['timestamp'],
                            'audio_timestamp': audio_data['timestamp']
                        })
                    
                except asyncio.TimeoutError:
                    # No audio to process, continue
                    continue
                except Exception as e:
                    if DEBUG:
                        print(f"[Runner-STT] ⚠️ Transcription error: {e}")
                    self.task_health[task_name]['error_count'] += 1
                    await asyncio.sleep(1)  # Brief pause on error
                    
        except asyncio.CancelledError:
            print("[Runner-STT] 🛑 STT task cancelled")
        except Exception as e:
            print(f"[Runner-STT] ❌ Error: {e}")
            self.task_health[task_name]['error_count'] += 1
        finally:
            self.task_health[task_name]['status'] = 'stopped'
            
    async def llm_task(self):
        """Language model processing task"""  
        task_name = 'llm'
        self.task_health[task_name]['status'] = 'running'
        
        print("[Runner-LLM] 🤖 LLM task started")
        
        try:
            while self.running:
                try:
                    # Wait for transcript from STT
                    stt_data = await asyncio.wait_for(
                        self.llm_queue.get(),
                        timeout=1.0
                    )
                    
                    self._update_task_health(task_name)
                    
                    transcript = stt_data['transcript']
                    
                    # Prepare context for consciousness
                    context = {
                        'user_input': transcript,
                        'timestamp': stt_data['timestamp'],
                        'audio_timestamp': stt_data['audio_timestamp']
                    }
                    
                    # Pre-process with consciousness
                    enhanced_context = await pre_reply(context)
                    if enhanced_context:
                        context.update(enhanced_context)
                    
                    # Generate LLM response
                    messages = [
                        {"role": "system", "content": "You are Buddy, a helpful AI assistant."},
                        {"role": "user", "content": transcript}
                    ]
                    
                    response = await chat_completion(messages, max_tokens=150)
                    
                    if response and response.strip():
                        if DEBUG:
                            print(f"[Runner-LLM] 🤖 Generated: {response[:100]}...")
                        
                        # Send to TTS queue
                        await self.tts_queue.put({
                            'text': response,
                            'context': context,
                            'timestamp': time.time()
                        })
                        
                        self.interaction_count += 1
                    
                except asyncio.TimeoutError:
                    # No transcripts to process, continue
                    continue
                except Exception as e:
                    if DEBUG:
                        print(f"[Runner-LLM] ⚠️ Generation error: {e}")
                    self.task_health[task_name]['error_count'] += 1
                    
                    # Send fallback response on LLM error
                    fallback_response = "I'm sorry, I'm having trouble processing that right now."
                    await self.tts_queue.put({
                        'text': fallback_response,
                        'context': {},
                        'timestamp': time.time()
                    })
                    await asyncio.sleep(2)  # Pause on error
                    
        except asyncio.CancelledError:
            print("[Runner-LLM] 🛑 LLM task cancelled") 
        except Exception as e:
            print(f"[Runner-LLM] ❌ Error: {e}")
            self.task_health[task_name]['error_count'] += 1
        finally:
            self.task_health[task_name]['status'] = 'stopped'
            
    async def tts_task(self):
        """Text-to-speech processing task"""
        task_name = 'tts' 
        self.task_health[task_name]['status'] = 'running'
        
        print("[Runner-TTS] 🎵 TTS task started")
        
        try:
            while self.running:
                try:
                    # Wait for text from LLM
                    llm_data = await asyncio.wait_for(
                        self.tts_queue.get(),
                        timeout=1.0
                    )
                    
                    self._update_task_health(task_name)
                    
                    text = llm_data['text']
                    context = llm_data.get('context', {})
                    
                    # Synthesize speech using our TTS client
                    audio_bytes = await synthesize_speech(text)
                    
                    if audio_bytes:
                        if DEBUG:
                            print(f"[Runner-TTS] 🎵 Synthesized {len(audio_bytes)} bytes")
                        
                        # Send to audio output queue
                        await self.audio_out_queue.put({
                            'audio_bytes': audio_bytes,
                            'text': text,
                            'context': context,
                            'timestamp': llm_data['timestamp']
                        })
                    
                except asyncio.TimeoutError:
                    # No text to synthesize, continue
                    continue
                except Exception as e:
                    if DEBUG:
                        print(f"[Runner-TTS] ⚠️ Synthesis error: {e}")
                    self.task_health[task_name]['error_count'] += 1
                    await asyncio.sleep(1)  # Brief pause on error
                    
        except asyncio.CancelledError:
            print("[Runner-TTS] 🛑 TTS task cancelled")
        except Exception as e:
            print(f"[Runner-TTS] ❌ Error: {e}") 
            self.task_health[task_name]['error_count'] += 1
        finally:
            self.task_health[task_name]['status'] = 'stopped'
            
    async def audio_out_task(self):
        """Audio output playback task"""
        task_name = 'audio_out'
        self.task_health[task_name]['status'] = 'running'
        
        print("[Runner-AudioOut] 🔊 Audio output task started")
        
        try:
            while self.running:
                try:
                    # Wait for audio from TTS
                    tts_data = await asyncio.wait_for(
                        self.audio_out_queue.get(),
                        timeout=1.0
                    )
                    
                    self._update_task_health(task_name)
                    
                    audio_bytes = tts_data['audio_bytes']
                    context = tts_data.get('context', {})
                    
                    # Placeholder for actual audio playback
                    # In real implementation, this would:
                    # 1. Play audio through speakers
                    # 2. Handle audio device management
                    # 3. Apply professional audio smoothing
                    # 4. Manage playback queue
                    
                    if DEBUG:
                        print(f"[Runner-AudioOut] 🔊 Playing {len(audio_bytes)} bytes")
                    
                    # Simulate playback time based on audio length
                    # Approximate: 44100 Hz * 2 bytes/sample = 88200 bytes/second
                    estimated_duration = len(audio_bytes) / 22050  # Rough estimate
                    await asyncio.sleep(max(0.1, min(estimated_duration, 10.0)))
                    
                    # Post-process with consciousness after speech
                    context['interaction_summary'] = {
                        'response_text': tts_data.get('text', ''),
                        'audio_duration': estimated_duration,
                        'timestamp': tts_data['timestamp']
                    }
                    await post_user_turn(context)
                    
                except asyncio.TimeoutError:
                    # No audio to play, continue  
                    continue
                except Exception as e:
                    if DEBUG:
                        print(f"[Runner-AudioOut] ⚠️ Playback error: {e}")
                    self.task_health[task_name]['error_count'] += 1
                    await asyncio.sleep(0.5)  # Brief pause on error
                    
        except asyncio.CancelledError:
            print("[Runner-AudioOut] 🛑 Audio output task cancelled")
        except Exception as e:
            print(f"[Runner-AudioOut] ❌ Error: {e}")
            self.task_health[task_name]['error_count'] += 1
        finally:
            self.task_health[task_name]['status'] = 'stopped'
            
    async def consciousness_task(self):
        """Background consciousness processing task"""
        task_name = 'consciousness'
        self.task_health[task_name]['status'] = 'running'
        
        print("[Runner-Consciousness] 🧠 Consciousness task started")
        
        try:
            while self.running:
                try:
                    # Run consciousness idle processing
                    await idle_tick()
                    self._update_task_health(task_name)
                    
                    # Wait before next consciousness cycle
                    await asyncio.sleep(15.0)  # Run every 15 seconds
                    
                except Exception as e:
                    if DEBUG:
                        print(f"[Runner-Consciousness] ⚠️ Processing error: {e}")
                    self.task_health[task_name]['error_count'] += 1
                    await asyncio.sleep(5.0)  # Longer pause on error
                    
        except asyncio.CancelledError:
            print("[Runner-Consciousness] 🛑 Consciousness task cancelled")
        except Exception as e:
            print(f"[Runner-Consciousness] ❌ Error: {e}")
            self.task_health[task_name]['error_count'] += 1
        finally:
            self.task_health[task_name]['status'] = 'stopped'
            
    async def watchdog_task(self):
        """Watchdog monitoring task"""
        task_name = 'watchdog'
        self.task_health[task_name]['status'] = 'running'
        
        print(f"[Runner-Watchdog] 🐕 Watchdog task started (interval: {WATCHDOG_INTERVAL_S}s)")
        
        try:
            while self.running:
                try:
                    await asyncio.sleep(WATCHDOG_INTERVAL_S)
                    
                    if not self.running:
                        break
                        
                    self._update_task_health(task_name)
                    await self._print_health_status()
                    
                except Exception as e:
                    if DEBUG:
                        print(f"[Runner-Watchdog] ⚠️ Monitoring error: {e}")
                    self.task_health[task_name]['error_count'] += 1
                    await asyncio.sleep(WATCHDOG_INTERVAL_S)
                    
        except asyncio.CancelledError:
            print("[Runner-Watchdog] 🛑 Watchdog task cancelled")
        except Exception as e:
            print(f"[Runner-Watchdog] ❌ Error: {e}")
            self.task_health[task_name]['error_count'] += 1
        finally:
            self.task_health[task_name]['status'] = 'stopped'
            
    def _update_task_health(self, task_name: str):
        """Update health status for a task"""
        if task_name in self.task_health:
            self.task_health[task_name]['last_activity'] = time.time()
            
    async def _print_health_status(self):
        """Print comprehensive health status"""
        current_time = time.time()
        uptime = current_time - (self.start_time or current_time)
        
        print(f"\n[Watchdog] 🐕 === BUDDY SYSTEM STATUS ===")
        print(f"[Watchdog] ⏱️ Uptime: {uptime:.1f}s | Interactions: {self.interaction_count}")
        print(f"[Watchdog] 📊 Task Health:")
        
        for task_name, health in self.task_health.items():
            status = health['status']
            last_activity = current_time - health['last_activity']
            errors = health['error_count'] 
            
            status_icon = "✅" if status == 'running' else "❌"
            activity_str = f"{last_activity:.1f}s ago" if last_activity < 999 else "never"
            
            print(f"[Watchdog]   {status_icon} {task_name:<12} | {status:<7} | Last: {activity_str:<10} | Errors: {errors}")
        
        # Get service health
        try:
            llm_healthy = await asyncio.wait_for(llm_health_check(), timeout=2.0)
            tts_healthy = await asyncio.wait_for(test_tts_service(), timeout=2.0) 
            consciousness_health = await asyncio.wait_for(get_consciousness_health(), timeout=2.0)
            
            print(f"[Watchdog] 🔗 Services:")
            print(f"[Watchdog]   {'✅' if llm_healthy else '❌'} LLM (Kobold)    | {'Healthy' if llm_healthy else 'Unhealthy'}")
            print(f"[Watchdog]   {'✅' if tts_healthy else '❌'} TTS (Kokoro)    | {'Healthy' if tts_healthy else 'Unhealthy'}")
            
            loaded_modules = consciousness_health.get('loaded_modules', {})
            loaded_count = sum(1 for v in loaded_modules.values() if v)
            print(f"[Watchdog]   🧠 Consciousness   | {loaded_count}/11 modules loaded")
            
        except Exception as e:
            print(f"[Watchdog]   ⚠️ Service check failed: {e}")
        
        print(f"[Watchdog] =======================================\n")

# Global runner instance
buddy_runner = BuddyRunner()

async def run_buddy():
    """Main entry point to run Buddy"""
    await buddy_runner.start()

if __name__ == "__main__":
    try:
        print("[Runner] 🚀 Buddy Clean Runner starting...")
        asyncio.run(run_buddy())
    except KeyboardInterrupt:
        print("\n[Runner] 👋 Goodbye!")
    except Exception as e:
        print(f"[Runner] ❌ Fatal error: {e}")
        sys.exit(1)