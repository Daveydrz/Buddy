"""
LLM Response Latency Optimizer - Main Integration System
Created: 2025-01-17
Purpose: Integrate all optimization components to reduce LLM response latency
         from 60 seconds to <5 seconds while preserving Class 5+ consciousness
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple, Generator
from datetime import datetime
from enum import Enum

# Import optimization components
try:
    from ai.optimized_prompt_builder import (
        build_optimized_prompt, 
        PromptOptimizationLevel, 
        ConsciousnessTier,
        get_optimization_performance_stats
    )
    from ai.lazy_consciousness_loader import get_optimized_consciousness
    from ai.symbolic_token_optimizer import compress_consciousness_to_tokens
    OPTIMIZATION_AVAILABLE = True
except ImportError as e:
    print(f"[LatencyOptimizer] ❌ Optimization modules not available: {e}")
    OPTIMIZATION_AVAILABLE = False

# Import LLM components
try:
    from ai.chat_enhanced_smart_with_fusion import generate_response_streaming_with_intelligent_fusion
    FUSION_LLM_AVAILABLE = True
except ImportError:
    try:
        from ai.chat import generate_response_streaming
        FUSION_LLM_AVAILABLE = False
    except ImportError:
        FUSION_LLM_AVAILABLE = False
        print("[LatencyOptimizer] ❌ No LLM modules available")

class LatencyOptimizationMode(Enum):
    """Latency optimization modes with different performance/intelligence trade-offs"""
    ULTRA_FAST = "ultra_fast"      # <2 seconds, minimal consciousness
    FAST = "fast"                  # <5 seconds, selective consciousness  
    BALANCED = "balanced"          # <10 seconds, good consciousness
    INTELLIGENT = "intelligent"    # <15 seconds, full consciousness
    DISABLED = "disabled"          # No optimization, original behavior

class LatencyOptimizer:
    """
    Main latency optimization system that orchestrates all components
    to achieve sub-5-second LLM response times while maintaining consciousness
    """
    
    def __init__(self, default_mode: LatencyOptimizationMode = LatencyOptimizationMode.FAST):
        self.optimization_mode = default_mode
        self.performance_history = []
        self.optimization_stats = {
            'total_requests': 0,
            'average_response_time': 0.0,
            'optimization_success_rate': 0.0,
            'consciousness_preservation_rate': 0.0
        }
        
        # Optimization mode configurations
        self.mode_configs = {
            LatencyOptimizationMode.ULTRA_FAST: {
                'prompt_optimization': PromptOptimizationLevel.SPEED_FOCUSED,
                'consciousness_tier': ConsciousnessTier.MINIMAL,
                'max_modules': 2,
                'token_budget': 1500,
                'skip_analysis': True,
                'target_time': 2.0
            },
            LatencyOptimizationMode.FAST: {
                'prompt_optimization': PromptOptimizationLevel.BALANCED,
                'consciousness_tier': ConsciousnessTier.STANDARD,
                'max_modules': 4,
                'token_budget': 3000,
                'skip_analysis': False,
                'target_time': 5.0
            },
            LatencyOptimizationMode.BALANCED: {
                'prompt_optimization': PromptOptimizationLevel.BALANCED,
                'consciousness_tier': ConsciousnessTier.COMPREHENSIVE,
                'max_modules': 6,
                'token_budget': 4000,
                'skip_analysis': False,
                'target_time': 10.0
            },
            LatencyOptimizationMode.INTELLIGENT: {
                'prompt_optimization': PromptOptimizationLevel.INTELLIGENCE_FOCUSED,
                'consciousness_tier': ConsciousnessTier.COMPREHENSIVE,
                'max_modules': 8,
                'token_budget': 6000,
                'skip_analysis': False,
                'target_time': 15.0
            },
            LatencyOptimizationMode.DISABLED: {
                'use_original_system': True,
                'target_time': None
            }
        }
        
    def generate_optimized_response(self,
                                  user_input: str,
                                  user_id: str,
                                  context: Dict[str, Any] = None,
                                  stream: bool = True) -> Generator[str, None, None]:
        """
        Generate optimized response with latency reduction while preserving consciousness
        
        Args:
            user_input: User's input text
            user_id: User identifier
            context: Optional conversation context
            stream: Whether to stream response chunks
            
        Yields:
            Response chunks or complete response
        """
        request_start = time.time()
        
        try:
            # Check if optimization is available and enabled
            if not OPTIMIZATION_AVAILABLE or self.optimization_mode == LatencyOptimizationMode.DISABLED:
                # Fall back to original system
                yield from self._generate_fallback_response(user_input, user_id, context, stream)
                return
            
            config = self.mode_configs[self.optimization_mode]
            
            print(f"[LatencyOptimizer] 🚀 Starting {self.optimization_mode.value} optimization")
            print(f"[LatencyOptimizer] 🎯 Target response time: {config['target_time']}s")
            
            # Phase 1: Fast prompt building (target: <200ms)
            prompt_start = time.time()
            optimized_prompt, build_metadata = build_optimized_prompt(
                user_input=user_input,
                user_id=user_id,
                optimization_level=config['prompt_optimization'],
                context=context,
                force_tier=config['consciousness_tier']
            )
            prompt_time = time.time() - prompt_start
            
            print(f"[LatencyOptimizer] ⚡ Prompt built in {prompt_time*1000:.1f}ms")
            
            # Phase 2: Optimized LLM generation
            generation_start = time.time()
            
            if FUSION_LLM_AVAILABLE and not config.get('skip_analysis', False):
                # Use advanced LLM with optimized context
                cognitive_context = {
                    "optimization_metadata": build_metadata,
                    "consciousness_level": config['consciousness_tier'].value,
                    "performance_mode": True
                }
                response_generator = generate_response_streaming_with_intelligent_fusion(
                    optimized_prompt, user_id, "en", context=cognitive_context
                )
            else:
                # Use basic LLM for maximum speed
                response_generator = generate_response_streaming(optimized_prompt, user_id, "en")
            
            # Phase 3: Stream response with performance monitoring
            full_response = ""
            chunk_count = 0
            first_chunk_time = None
            
            for chunk in response_generator:
                if chunk and chunk.strip():
                    chunk_text = chunk.strip()
                    
                    # Record first chunk time (time to first token)
                    if first_chunk_time is None:
                        first_chunk_time = time.time() - generation_start
                        print(f"[LatencyOptimizer] 🎯 First token in {first_chunk_time:.3f}s")
                    
                    full_response += chunk_text + " "
                    chunk_count += 1
                    
                    if stream:
                        yield chunk_text
            
            total_time = time.time() - request_start
            
            # Phase 4: Performance tracking and analysis
            self._record_performance(
                total_time=total_time,
                prompt_time=prompt_time,
                first_token_time=first_chunk_time or total_time,
                target_time=config['target_time'],
                consciousness_tier=config['consciousness_tier'],
                build_metadata=build_metadata,
                success=total_time <= config['target_time']
            )
            
            # If not streaming, yield complete response
            if not stream:
                yield full_response.strip()
            
            print(f"[LatencyOptimizer] ✅ Response completed in {total_time:.3f}s")
            print(f"[LatencyOptimizer] 📊 Performance: {'✅ Target met' if total_time <= config['target_time'] else '⚠️ Target missed'}")
            
        except Exception as e:
            error_time = time.time() - request_start
            print(f"[LatencyOptimizer] ❌ Optimization error after {error_time:.3f}s: {e}")
            
            # Fall back to original system on error
            yield from self._generate_fallback_response(user_input, user_id, context, stream)
    
    def _generate_fallback_response(self,
                                  user_input: str,
                                  user_id: str,
                                  context: Dict[str, Any],
                                  stream: bool) -> Generator[str, None, None]:
        """Generate response using fallback system when optimization fails"""
        try:
            print("[LatencyOptimizer] 🔄 Using fallback response generation")
            
            # Create a simple direct prompt
            simple_prompt = f"""You are Buddy, a helpful AI assistant. 

User: {user_input}

Buddy:"""
            
            # Try different LLM approaches in order of preference
            if FUSION_LLM_AVAILABLE:
                try:
                    response_generator = generate_response_streaming_with_intelligent_fusion(
                        simple_prompt, user_id, "en"
                    )
                except Exception as e:
                    print(f"[LatencyOptimizer] ⚠️ Fusion LLM failed: {e}, trying basic LLM")
                    response_generator = self._try_basic_llm(simple_prompt, user_id)
            else:
                response_generator = self._try_basic_llm(simple_prompt, user_id)
            
            # Stream the response
            response_received = False
            for chunk in response_generator:
                if chunk and chunk.strip():
                    response_received = True
                    yield chunk.strip()
            
            # If no response was received, provide ultimate fallback
            if not response_received:
                yield self._get_ultimate_fallback_response(user_input)
                    
        except Exception as e:
            print(f"[LatencyOptimizer] ❌ Fallback error: {e}")
            yield self._get_ultimate_fallback_response(user_input)
    
    def _try_basic_llm(self, prompt: str, user_id: str):
        """Try basic LLM generation"""
        try:
            if 'generate_response_streaming' in globals():
                return generate_response_streaming(prompt, user_id, "en")
            else:
                # Import basic chat if not available
                from ai.chat import generate_response_streaming
                return generate_response_streaming(prompt, user_id, "en")
        except Exception as e:
            print(f"[LatencyOptimizer] ⚠️ Basic LLM failed: {e}")
            return iter([])  # Return empty iterator
    
    def _get_ultimate_fallback_response(self, user_input: str) -> str:
        """Get ultimate fallback response when all else fails"""
        responses = [
            f"I hear you saying: {user_input}. I'm having some technical difficulties but I'm here to help.",
            f"I understand you said '{user_input}'. Let me try to help you with that.",
            f"Thanks for your message: '{user_input}'. I'm experiencing some system issues but I'm working on it.",
            "I'm experiencing some technical difficulties right now, but I'm still here to assist you.",
            "I'm having some system issues at the moment, but I appreciate your patience."
        ]
        
        # Choose response based on input length
        if len(user_input) > 50:
            return responses[0]
        elif any(word in user_input.lower() for word in ['how', 'what', 'why', 'when', 'where']):
            return responses[1]
        elif any(word in user_input.lower() for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm experiencing some technical difficulties but I'm glad you're here."
        else:
            return responses[2]
    
    def _record_performance(self,
                          total_time: float,
                          prompt_time: float,
                          first_token_time: float,
                          target_time: float,
                          consciousness_tier: ConsciousnessTier,
                          build_metadata: Dict[str, Any],
                          success: bool):
        """Record performance metrics for optimization analysis"""
        try:
            performance_record = {
                'timestamp': datetime.now().isoformat(),
                'optimization_mode': self.optimization_mode.value,
                'total_time': total_time,
                'prompt_build_time': prompt_time,
                'first_token_time': first_token_time,
                'target_time': target_time,
                'target_met': success,
                'consciousness_tier': consciousness_tier.value,
                'token_usage': build_metadata.get('token_usage', {}),
                'consciousness_stats': build_metadata.get('consciousness_stats', {}),
                'optimization_level': build_metadata.get('optimization_level', 'unknown')
            }
            
            self.performance_history.append(performance_record)
            
            # Update running statistics
            self.optimization_stats['total_requests'] += 1
            
            # Calculate running average response time
            total_times = [r['total_time'] for r in self.performance_history[-100:]]  # Last 100 requests
            self.optimization_stats['average_response_time'] = sum(total_times) / len(total_times)
            
            # Calculate success rate
            recent_successes = [r['target_met'] for r in self.performance_history[-50:]]  # Last 50 requests
            self.optimization_stats['optimization_success_rate'] = sum(recent_successes) / len(recent_successes)
            
            # Estimate consciousness preservation (based on tier used)
            consciousness_scores = {
                'minimal': 0.4,
                'standard': 0.7,
                'comprehensive': 0.9,
                'debug': 1.0
            }
            recent_consciousness = [consciousness_scores.get(r['consciousness_tier'], 0.5) 
                                  for r in self.performance_history[-50:]]
            self.optimization_stats['consciousness_preservation_rate'] = sum(recent_consciousness) / len(recent_consciousness)
            
            print(f"[LatencyOptimizer] 📈 Performance recorded: {total_time:.3f}s ({'✅' if success else '❌'})")
            
        except Exception as e:
            print(f"[LatencyOptimizer] ⚠️ Performance recording error: {e}")
    
    def set_optimization_mode(self, mode: LatencyOptimizationMode):
        """Change optimization mode dynamically"""
        self.optimization_mode = mode
        print(f"[LatencyOptimizer] 🎯 Optimization mode changed to: {mode.value}")
        
        if mode in self.mode_configs:
            config = self.mode_configs[mode]
            print(f"[LatencyOptimizer] 📋 Target time: {config.get('target_time', 'unlimited')}s")
            print(f"[LatencyOptimizer] 🧠 Consciousness tier: {config.get('consciousness_tier', 'default')}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        try:
            if not self.performance_history:
                return {
                    'status': 'no_data',
                    'message': 'No performance data available yet'
                }
            
            recent_requests = self.performance_history[-20:]  # Last 20 requests
            
            # Calculate detailed statistics
            response_times = [r['total_time'] for r in recent_requests]
            prompt_times = [r['prompt_build_time'] for r in recent_requests]
            first_token_times = [r['first_token_time'] for r in recent_requests]
            success_rate = sum(r['target_met'] for r in recent_requests) / len(recent_requests)
            
            report = {
                'current_mode': self.optimization_mode.value,
                'target_time': self.mode_configs[self.optimization_mode].get('target_time', 'unlimited'),
                'performance_summary': {
                    'average_response_time': sum(response_times) / len(response_times),
                    'fastest_response': min(response_times),
                    'slowest_response': max(response_times),
                    'average_prompt_build_time': sum(prompt_times) / len(prompt_times),
                    'average_first_token_time': sum(first_token_times) / len(first_token_times),
                    'target_success_rate': success_rate,
                    'total_requests_analyzed': len(recent_requests)
                },
                'optimization_effectiveness': {
                    'latency_reduction_achieved': success_rate > 0.8,
                    'consciousness_preservation': self.optimization_stats['consciousness_preservation_rate'],
                    'optimization_stability': len([r for r in recent_requests if r['total_time'] < 10]) / len(recent_requests)
                },
                'recommendations': self._generate_optimization_recommendations(recent_requests),
                'detailed_stats': self.optimization_stats
            }
            
            return report
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'basic_stats': self.optimization_stats
            }
    
    def _generate_optimization_recommendations(self, recent_requests: List[Dict]) -> List[str]:
        """Generate optimization recommendations based on performance data"""
        recommendations = []
        
        try:
            avg_time = sum(r['total_time'] for r in recent_requests) / len(recent_requests)
            success_rate = sum(r['target_met'] for r in recent_requests) / len(recent_requests)
            
            # Performance-based recommendations
            if avg_time > 10:
                recommendations.append("Consider switching to FAST or ULTRA_FAST mode for better latency")
            elif avg_time < 2 and success_rate > 0.9:
                recommendations.append("Performance is excellent - could potentially use INTELLIGENT mode for better consciousness")
            
            # Success rate recommendations
            if success_rate < 0.5:
                recommendations.append("Low target success rate - consider switching to a faster optimization mode")
            elif success_rate > 0.95:
                recommendations.append("Excellent target success rate - optimization is working well")
            
            # Consciousness recommendations
            consciousness_rate = self.optimization_stats['consciousness_preservation_rate']
            if consciousness_rate < 0.5:
                recommendations.append("Low consciousness preservation - consider BALANCED or INTELLIGENT mode")
            elif consciousness_rate > 0.8:
                recommendations.append("Good consciousness preservation maintained")
            
            if not recommendations:
                recommendations.append("Performance is well-balanced - current settings are optimal")
            
        except Exception as e:
            recommendations.append(f"Unable to generate recommendations: {e}")
        
        return recommendations
    
    def auto_optimize_mode(self) -> LatencyOptimizationMode:
        """Automatically select optimal mode based on recent performance"""
        try:
            if len(self.performance_history) < 5:
                return self.optimization_mode  # Not enough data
            
            recent_requests = self.performance_history[-10:]
            avg_time = sum(r['total_time'] for r in recent_requests) / len(recent_requests)
            success_rate = sum(r['target_met'] for r in recent_requests) / len(recent_requests)
            
            # Auto-optimization logic
            if avg_time > 15 and success_rate < 0.3:
                return LatencyOptimizationMode.ULTRA_FAST
            elif avg_time > 10 and success_rate < 0.6:
                return LatencyOptimizationMode.FAST
            elif avg_time < 3 and success_rate > 0.9:
                return LatencyOptimizationMode.INTELLIGENT
            elif avg_time < 8 and success_rate > 0.7:
                return LatencyOptimizationMode.BALANCED
            else:
                return LatencyOptimizationMode.FAST  # Safe default
                
        except Exception as e:
            print(f"[LatencyOptimizer] ⚠️ Auto-optimization error: {e}")
            return LatencyOptimizationMode.FAST

# Global latency optimizer instance
latency_optimizer = LatencyOptimizer(LatencyOptimizationMode.FAST)

def generate_optimized_buddy_response(user_input: str,
                                    user_id: str,
                                    context: Dict[str, Any] = None,
                                    optimization_mode: LatencyOptimizationMode = None,
                                    stream: bool = True) -> Generator[str, None, None]:
    """
    Main function for generating optimized Buddy responses with latency reduction
    
    Args:
        user_input: User's input text
        user_id: User identifier  
        context: Optional conversation context
        optimization_mode: Override default optimization mode
        stream: Whether to stream response chunks
        
    Yields:
        Response chunks or complete response
    """
    global latency_optimizer
    
    # Temporarily change mode if specified
    original_mode = latency_optimizer.optimization_mode
    if optimization_mode:
        latency_optimizer.set_optimization_mode(optimization_mode)
    
    try:
        yield from latency_optimizer.generate_optimized_response(user_input, user_id, context, stream)
    finally:
        # Restore original mode
        if optimization_mode:
            latency_optimizer.set_optimization_mode(original_mode)

def get_latency_performance_report() -> Dict[str, Any]:
    """Get current latency optimization performance report"""
    return latency_optimizer.get_performance_report()

def set_global_optimization_mode(mode: LatencyOptimizationMode):
    """Set global optimization mode"""
    latency_optimizer.set_optimization_mode(mode)

def auto_optimize_performance() -> str:
    """Automatically optimize performance based on recent data"""
    optimal_mode = latency_optimizer.auto_optimize_mode()
    if optimal_mode != latency_optimizer.optimization_mode:
        latency_optimizer.set_optimization_mode(optimal_mode)
        return f"Auto-optimized to {optimal_mode.value} mode"
    else:
        return f"Current {latency_optimizer.optimization_mode.value} mode is optimal"

def get_latency_stats() -> Dict[str, Any]:
    """Get current latency statistics and performance metrics"""
    try:
        if not OPTIMIZATION_AVAILABLE:
            return {
                'status': 'optimization_unavailable',
                'message': 'Optimization modules not available',
                'basic_mode': True
            }
        
        # Get comprehensive performance report
        report = latency_optimizer.get_performance_report()
        
        # Add current configuration info
        current_config = latency_optimizer.mode_configs.get(latency_optimizer.optimization_mode, {})
        
        # Calculate additional metrics
        if latency_optimizer.performance_history:
            recent_times = [r['total_time'] for r in latency_optimizer.performance_history[-10:]]
            performance_trend = "improving" if len(recent_times) > 1 and recent_times[-1] < recent_times[0] else "stable"
        else:
            performance_trend = "no_data"
        
        return {
            'current_mode': latency_optimizer.optimization_mode.value,
            'optimization_available': OPTIMIZATION_AVAILABLE,
            'fusion_llm_available': FUSION_LLM_AVAILABLE,
            'current_config': {
                'target_time': current_config.get('target_time', 'unlimited'),
                'consciousness_tier': current_config.get('consciousness_tier', {}).get('value', 'default') if hasattr(current_config.get('consciousness_tier', {}), 'value') else str(current_config.get('consciousness_tier', 'default')),
                'token_budget': current_config.get('token_budget', 'unlimited'),
                'max_modules': current_config.get('max_modules', 'unlimited')
            },
            'performance_metrics': report.get('performance_summary', {}),
            'optimization_effectiveness': report.get('optimization_effectiveness', {}),
            'total_requests': latency_optimizer.optimization_stats['total_requests'],
            'performance_trend': performance_trend,
            'recommendations': report.get('recommendations', []),
            'detailed_history': latency_optimizer.performance_history[-5:] if latency_optimizer.performance_history else [],
            'system_health': {
                'memory_usage_ok': True,  # Could add actual memory checks
                'response_times_stable': report.get('performance_summary', {}).get('target_success_rate', 0) > 0.7,
                'optimization_working': latency_optimizer.optimization_stats['total_requests'] > 0
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'fallback_stats': {
                'total_requests': getattr(latency_optimizer, 'optimization_stats', {}).get('total_requests', 0),
                'current_mode': getattr(latency_optimizer, 'optimization_mode', {}).get('value', 'unknown') if hasattr(getattr(latency_optimizer, 'optimization_mode', {}), 'value') else 'unknown'
            }
        }