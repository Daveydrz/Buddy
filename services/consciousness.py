"""
Consciousness Facade - Non-blocking interface to AI consciousness modules
Provides lazy-loading and timeout-wrapped access to prevent blocking the speech loop
"""

import asyncio
import importlib
from typing import Any, Dict, Optional, Callable
from functools import wraps
from config.core import DEBUG
from config.audio import WATCHDOG_INTERVAL_S

# Timeout for consciousness operations (never block speech loop)
CONSCIOUSNESS_TIMEOUT = 5.0
CONSCIOUSNESS_IDLE_INTERVAL = 15.0  # Run idle_tick every 15 seconds

class ConsciousnessFacade:
    """Non-blocking facade for AI consciousness modules"""
    
    def __init__(self):
        self.modules = {}
        self.module_cache = {}
        self.last_idle_tick = 0
        self.is_running = False
        
        # Define modules to lazy load
        self.module_definitions = {
            'global_workspace': 'ai.global_workspace',
            'self_model': 'ai.self_model', 
            'emotion': 'ai.emotion',
            'motivation': 'ai.motivation',
            'inner_monologue': 'ai.inner_monologue',
            'temporal_awareness': 'ai.temporal_awareness',
            'subjective_experience': 'ai.subjective_experience',
            'entropy': 'ai.entropy',
            'entropy_engine': 'ai.entropy_engine',
            'free_thought_engine': 'ai.free_thought_engine',
            'narrative_tracker': 'ai.narrative_tracker'
        }
    
    def _lazy_import(self, module_name: str) -> Optional[Any]:
        """Safely import a consciousness module with error handling"""
        if module_name in self.module_cache:
            return self.module_cache[module_name]
        
        try:
            if module_name not in self.module_definitions:
                if DEBUG:
                    print(f"[Consciousness] Unknown module: {module_name}")
                return None
            
            module_path = self.module_definitions[module_name]
            module = importlib.import_module(module_path)
            
            # Cache the module
            self.module_cache[module_name] = module
            
            if DEBUG:
                print(f"[Consciousness] ✅ Lazy loaded: {module_name}")
            
            return module
            
        except ImportError as e:
            if DEBUG:
                print(f"[Consciousness] ⚠️ Could not import {module_name}: {e}")
            self.module_cache[module_name] = None
            return None
        except Exception as e:
            if DEBUG:
                print(f"[Consciousness] ❌ Error loading {module_name}: {e}")
            self.module_cache[module_name] = None
            return None
    
    def _timeout_wrapper(self, timeout: float = CONSCIOUSNESS_TIMEOUT):
        """Decorator to wrap consciousness operations with timeouts"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                except asyncio.TimeoutError:
                    if DEBUG:
                        print(f"[Consciousness] ⏱️ Timeout in {func.__name__} ({timeout}s)")
                    return None
                except Exception as e:
                    if DEBUG:
                        print(f"[Consciousness] ❌ Error in {func.__name__}: {e}")
                    return None
            return wrapper
        return decorator
    
    @_timeout_wrapper(CONSCIOUSNESS_TIMEOUT)
    async def _safe_call(self, module_name: str, function_name: str, *args, **kwargs) -> Optional[Any]:
        """Safely call a function from a consciousness module"""
        module = self._lazy_import(module_name)
        if not module:
            return None
        
        try:
            # Get the function/object from the module
            if hasattr(module, function_name):
                func_or_obj = getattr(module, function_name)
                
                # If it's callable, call it
                if callable(func_or_obj):
                    # Run in executor to avoid blocking
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, func_or_obj, *args, **kwargs)
                    return result
                else:
                    # It's an object/variable, return it
                    return func_or_obj
            else:
                if DEBUG:
                    print(f"[Consciousness] Function {function_name} not found in {module_name}")
                return None
                
        except Exception as e:
            if DEBUG:
                print(f"[Consciousness] Error calling {module_name}.{function_name}: {e}")
            return None
    
    async def idle_tick(self) -> None:
        """
        Periodic consciousness processing - called when system is idle
        Runs consciousness systems that can operate in background
        """
        current_time = asyncio.get_event_loop().time()
        
        # Throttle idle_tick calls
        if current_time - self.last_idle_tick < CONSCIOUSNESS_IDLE_INTERVAL:
            return
            
        self.last_idle_tick = current_time
        
        if DEBUG:
            print(f"[Consciousness] 🧠 Running idle_tick cycle...")
        
        # Run background consciousness processes
        tasks = []
        
        # Global workspace processing
        tasks.append(self._safe_call('global_workspace', 'process_idle'))
        
        # Temporal awareness updates
        tasks.append(self._safe_call('temporal_awareness', 'update_time_context'))
        
        # Inner monologue processing
        tasks.append(self._safe_call('inner_monologue', 'process_thoughts'))
        
        # Entropy system updates
        tasks.append(self._safe_call('entropy', 'update_entropy'))
        
        # Free thought processing
        tasks.append(self._safe_call('free_thought_engine', 'generate_free_thoughts'))
        
        # Motivation system updates
        tasks.append(self._safe_call('motivation', 'update_goals'))
        
        # Execute all background tasks concurrently with timeout
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            if DEBUG:
                print(f"[Consciousness] ❌ Error in idle_tick: {e}")
    
    async def pre_reply(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Pre-processing before generating a reply
        Enhances context with consciousness data
        """
        if DEBUG:
            print(f"[Consciousness] 🎯 Pre-reply processing...")
        
        enhanced_context = context.copy()
        
        # Get emotional context
        emotion_state = await self._safe_call('emotion', 'get_current_state')
        if emotion_state:
            enhanced_context['emotion_state'] = emotion_state
        
        # Get motivation context
        motivation_state = await self._safe_call('motivation', 'get_current_goals')
        if motivation_state:
            enhanced_context['motivation_state'] = motivation_state
        
        # Get self-model insights
        self_model_data = await self._safe_call('self_model', 'get_current_self_perception')
        if self_model_data:
            enhanced_context['self_model'] = self_model_data
        
        # Update global workspace with input
        await self._safe_call('global_workspace', 'process_input', context.get('user_input', ''))
        
        return enhanced_context
    
    async def post_user_turn(self, context: Dict[str, Any]) -> None:
        """
        Post-processing after user interaction
        Updates consciousness systems based on interaction
        """
        if DEBUG:
            print(f"[Consciousness] 📝 Post-turn processing...")
        
        # Update self-model based on interaction
        if 'user_input' in context:
            await self._safe_call('self_model', 'process_interaction', context['user_input'])
        
        # Update emotional state
        if 'user_emotion' in context:
            await self._safe_call('emotion', 'process_user_emotion', context['user_emotion'])
        
        # Update narrative tracker
        if 'interaction_summary' in context:
            await self._safe_call('narrative_tracker', 'record_interaction', context['interaction_summary'])
        
        # Update temporal awareness
        await self._safe_call('temporal_awareness', 'record_interaction_time')
        
        # Update inner monologue with reflection
        await self._safe_call('inner_monologue', 'reflect_on_interaction', context)
    
    async def get_consciousness_state(self) -> Dict[str, Any]:
        """Get current state of all consciousness modules"""
        state = {}
        
        # Collect states from all modules
        for module_name in self.module_definitions.keys():
            module_state = await self._safe_call(module_name, 'get_state')
            if module_state:
                state[module_name] = module_state
        
        return state
    
    def get_loaded_modules(self) -> Dict[str, bool]:
        """Get status of which modules are loaded"""
        status = {}
        for module_name in self.module_definitions.keys():
            status[module_name] = module_name in self.module_cache and self.module_cache[module_name] is not None
        return status
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of consciousness systems"""
        health = {
            'loaded_modules': self.get_loaded_modules(),
            'last_idle_tick': self.last_idle_tick,
            'is_running': self.is_running
        }
        
        # Test a few key modules
        test_results = {}
        for module_name in ['global_workspace', 'emotion', 'self_model']:
            result = await self._safe_call(module_name, 'health_check')
            test_results[module_name] = result is not None
        
        health['module_health'] = test_results
        return health

# Global consciousness facade instance
consciousness = ConsciousnessFacade()

# Convenience functions for easy access
async def idle_tick():
    """Run consciousness idle processing - convenience function"""
    await consciousness.idle_tick()

async def pre_reply(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Pre-process reply with consciousness - convenience function"""
    return await consciousness.pre_reply(context)

async def post_user_turn(context: Dict[str, Any]):
    """Post-process user turn with consciousness - convenience function"""
    await consciousness.post_user_turn(context)

async def get_consciousness_health() -> Dict[str, Any]:
    """Get consciousness system health - convenience function"""
    return await consciousness.health_check()