"""
Consciousness Tokenizer - Tokenize consciousness state for LLM context integration
Created: 2025-01-17
Purpose: Convert consciousness architecture state into tokens that can be integrated into LLM prompts
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

class ConsciousnessTokenizer:
    """Tokenizes consciousness state into LLM-compatible context tokens"""
    
    def __init__(self):
        self.token_templates = {
            'emotion': "[EMOTION:{emotion}|intensity:{intensity:.2f}]",
            'motivation': "[GOAL:{goal}|priority:{priority:.2f}|progress:{progress:.2f}]",
            'attention': "[FOCUS:{focus}|priority:{priority}]",
            'memory': "[MEMORY:{type}|significance:{significance:.2f}]",
            'thought': "[THOUGHT:{type}|content:{content}]",
            'temporal': "[TIME:{event}|significance:{significance:.2f}]",
            'self_reflection': "[SELF:{aspect}|value:{value}]",
            'experience': "[EXP:{type}|valence:{valence:.2f}|significance:{significance:.2f}]",
            'belief': "[BELIEF:{belief}|certainty:{certainty:.2f}|contradictions:{contradictions}]",
            'personality': "[PERSONALITY:{trait}|strength:{strength:.2f}|adaptation:{adaptation}]",
            'context': "[CONTEXT:{event}|type:{type}|status:{status}|priority:{priority}]"  # New multi-context token
        }
        
        self.max_tokens_per_category = {
            'emotion': 3,
            'motivation': 5,
            'attention': 3,
            'memory': 4,
            'thought': 2,
            'temporal': 3,
            'self_reflection': 3,
            'experience': 2,
            'belief': 4,
            'personality': 3,
            'context': 6  # Allow more tokens for multi-context information
        }
        
        self.consciousness_cache = {}
        self.last_update = time.time()
        
    def tokenize_consciousness_state(self, consciousness_systems: Dict[str, Any]) -> str:
        """
        Convert consciousness state into tokenized string for LLM context
        
        Args:
            consciousness_systems: Dictionary containing consciousness system states
            
        Returns:
            Tokenized consciousness string for LLM prompt integration
        """
        try:
            tokens = []
            
            # Add timestamp token
            current_time = datetime.now().isoformat()
            tokens.append(f"[CONSCIOUSNESS_STATE:{current_time}]")
            
            # Process each consciousness component
            if 'emotion_engine' in consciousness_systems:
                emotion_tokens = self._tokenize_emotions(consciousness_systems['emotion_engine'])
                tokens.extend(emotion_tokens)
            
            if 'motivation_system' in consciousness_systems:
                motivation_tokens = self._tokenize_motivation(consciousness_systems['motivation_system'])
                tokens.extend(motivation_tokens)
                
            if 'global_workspace' in consciousness_systems:
                attention_tokens = self._tokenize_attention(consciousness_systems['global_workspace'])
                tokens.extend(attention_tokens)
                
            if 'temporal_awareness' in consciousness_systems:
                memory_tokens = self._tokenize_memory(consciousness_systems['temporal_awareness'])
                tokens.extend(memory_tokens)
                
            if 'inner_monologue' in consciousness_systems:
                thought_tokens = self._tokenize_thoughts(consciousness_systems['inner_monologue'])
                tokens.extend(thought_tokens)
                
            if 'self_model' in consciousness_systems:
                self_tokens = self._tokenize_self_model(consciousness_systems['self_model'])
                tokens.extend(self_tokens)
                
            if 'subjective_experience' in consciousness_systems:
                exp_tokens = self._tokenize_experience(consciousness_systems['subjective_experience'])
                tokens.extend(exp_tokens)
                
            if 'belief_analyzer' in consciousness_systems:
                belief_tokens = self._tokenize_beliefs(consciousness_systems['belief_analyzer'])
                tokens.extend(belief_tokens)
                
            if 'personality_state' in consciousness_systems:
                personality_tokens = self._tokenize_personality(consciousness_systems['personality_state'])
                tokens.extend(personality_tokens)
            
            # Join tokens with space separation
            return " ".join(tokens)
            
        except Exception as e:
            print(f"[ConsciousnessTokenizer] ❌ Error tokenizing consciousness: {e}")
            return f"[CONSCIOUSNESS_ERROR:{str(e)}]"
    
    def tokenize_multi_context_memory(self, memory_system) -> str:
        """🧠 MULTI-CONTEXT: Tokenize multi-context memory for LLM efficiency"""
        try:
            tokens = []
            
            # Check if memory system has multi-context capability
            if hasattr(memory_system, 'working_memory') and hasattr(memory_system.working_memory, 'active_contexts'):
                active_contexts = memory_system.working_memory.active_contexts
                
                if active_contexts:
                    # Sort contexts by priority and recency
                    sorted_contexts = sorted(
                        active_contexts.values(), 
                        key=lambda x: (x.priority, x.timestamp), 
                        reverse=True
                    )
                    
                    # Tokenize top priority contexts
                    for context in sorted_contexts[:self.max_tokens_per_category['context']]:
                        # Clean description for token efficiency
                        clean_description = context.description[:20]  # Limit length
                        
                        context_token = self.token_templates['context'].format(
                            event=clean_description,
                            type=context.event_type,
                            status=context.status,
                            priority=context.priority
                        )
                        tokens.append(context_token)
            
            return " ".join(tokens) if tokens else ""
            
        except Exception as e:
            print(f"[ConsciousnessTokenizer] ❌ Error tokenizing multi-context: {e}")
            return f"[MULTICONTEXT_ERROR:{str(e)}]"
    
    def _tokenize_emotions(self, emotion_state: Dict[str, Any]) -> List[str]:
        """Tokenize emotional state"""
        tokens = []
        try:
            if 'primary_emotion' in emotion_state:
                emotion = emotion_state['primary_emotion']
                intensity = emotion_state.get('intensity', 0.5)
                tokens.append(self.token_templates['emotion'].format(
                    emotion=emotion, intensity=intensity
                ))
            
            # Add secondary emotions if present
            if 'secondary_emotions' in emotion_state:
                for emotion, intensity in emotion_state['secondary_emotions'].items():
                    if len(tokens) < self.max_tokens_per_category['emotion']:
                        tokens.append(self.token_templates['emotion'].format(
                            emotion=emotion, intensity=intensity
                        ))
                        
        except Exception as e:
            tokens.append(f"[EMOTION_ERROR:{str(e)}]")
            
        return tokens[:self.max_tokens_per_category['emotion']]
    
    def _tokenize_motivation(self, motivation_state: Dict[str, Any]) -> List[str]:
        """Tokenize motivation and goals"""
        tokens = []
        try:
            if 'active_goals' in motivation_state:
                for goal in motivation_state['active_goals'][:self.max_tokens_per_category['motivation']]:
                    tokens.append(self.token_templates['motivation'].format(
                        goal=goal.get('description', 'unknown')[:30],
                        priority=goal.get('priority', 0.5),
                        progress=goal.get('progress', 0.0)
                    ))
                    
        except Exception as e:
            tokens.append(f"[MOTIVATION_ERROR:{str(e)}]")
            
        return tokens
    
    def _tokenize_attention(self, workspace_state: Dict[str, Any]) -> List[str]:
        """Tokenize attention and focus"""
        tokens = []
        try:
            if 'current_focus' in workspace_state:
                focus = workspace_state['current_focus']
                priority = workspace_state.get('focus_priority', 'medium')
                tokens.append(self.token_templates['attention'].format(
                    focus=focus[:30], priority=priority
                ))
                
            if 'attention_queue' in workspace_state:
                for item in workspace_state['attention_queue'][:2]:
                    tokens.append(self.token_templates['attention'].format(
                        focus=item.get('content', 'unknown')[:30],
                        priority=item.get('priority', 'low')
                    ))
                    
        except Exception as e:
            tokens.append(f"[ATTENTION_ERROR:{str(e)}]")
            
        return tokens[:self.max_tokens_per_category['attention']]
    
    def _tokenize_memory(self, temporal_state: Dict[str, Any]) -> List[str]:
        """Tokenize memory and temporal events"""
        tokens = []
        try:
            if 'recent_events' in temporal_state:
                for event in temporal_state['recent_events'][:self.max_tokens_per_category['memory']]:
                    tokens.append(self.token_templates['memory'].format(
                        type=event.get('type', 'event'),
                        significance=event.get('significance', 0.5)
                    ))
                    
        except Exception as e:
            tokens.append(f"[MEMORY_ERROR:{str(e)}]")
            
        return tokens
    
    def _tokenize_thoughts(self, monologue_state: Dict[str, Any]) -> List[str]:
        """Tokenize inner thoughts"""
        tokens = []
        try:
            if 'recent_thoughts' in monologue_state:
                for thought in monologue_state['recent_thoughts'][:self.max_tokens_per_category['thought']]:
                    tokens.append(self.token_templates['thought'].format(
                        type=thought.get('type', 'reflection'),
                        content=thought.get('content', 'unknown')[:40]
                    ))
                    
        except Exception as e:
            tokens.append(f"[THOUGHT_ERROR:{str(e)}]")
            
        return tokens
    
    def _tokenize_self_model(self, self_state: Dict[str, Any]) -> List[str]:
        """Tokenize self-reflection and identity"""
        tokens = []
        try:
            if 'self_aspects' in self_state:
                for aspect, value in self_state['self_aspects'].items():
                    if len(tokens) < self.max_tokens_per_category['self_reflection']:
                        tokens.append(self.token_templates['self_reflection'].format(
                            aspect=aspect[:20], value=str(value)[:20]
                        ))
                        
        except Exception as e:
            tokens.append(f"[SELF_ERROR:{str(e)}]")
            
        return tokens
    
    def _tokenize_experience(self, experience_state: Dict[str, Any]) -> List[str]:
        """Tokenize subjective experiences"""
        tokens = []
        try:
            if 'current_experience' in experience_state:
                exp = experience_state['current_experience']
                tokens.append(self.token_templates['experience'].format(
                    type=exp.get('type', 'unknown'),
                    valence=exp.get('valence', 0.0),
                    significance=exp.get('significance', 0.5)
                ))
                
        except Exception as e:
            tokens.append(f"[EXPERIENCE_ERROR:{str(e)}]")
            
        return tokens
    
    def _tokenize_beliefs(self, belief_state: Dict[str, Any]) -> List[str]:
        """Tokenize beliefs and contradictions"""
        tokens = []
        try:
            if 'active_beliefs' in belief_state:
                for belief in belief_state['active_beliefs'][:self.max_tokens_per_category['belief']]:
                    tokens.append(self.token_templates['belief'].format(
                        belief=belief.get('content', 'unknown')[:30],
                        certainty=belief.get('certainty', 0.5),
                        contradictions=len(belief.get('contradictions', []))
                    ))
                    
        except Exception as e:
            tokens.append(f"[BELIEF_ERROR:{str(e)}]")
            
        return tokens
    
    def _tokenize_personality(self, personality_state: Dict[str, Any]) -> List[str]:
        """Tokenize personality traits and adaptations"""
        tokens = []
        try:
            if 'active_traits' in personality_state:
                for trait, data in personality_state['active_traits'].items():
                    if len(tokens) < self.max_tokens_per_category['personality']:
                        tokens.append(self.token_templates['personality'].format(
                            trait=trait[:20],
                            strength=data.get('strength', 0.5),
                            adaptation=data.get('adaptation_level', 'stable')
                        ))
                        
        except Exception as e:
            tokens.append(f"[PERSONALITY_ERROR:{str(e)}]")
            
        return tokens
    
    def get_consciousness_summary(self, consciousness_systems: Dict[str, Any]) -> str:
        """Get a brief summary of consciousness state for lightweight integration"""
        try:
            summary_parts = []
            
            # Emotional summary
            if 'emotion_engine' in consciousness_systems:
                emotion = consciousness_systems['emotion_engine'].get('primary_emotion', 'neutral')
                summary_parts.append(f"feeling_{emotion}")
            
            # Motivational summary
            if 'motivation_system' in consciousness_systems:
                goals = consciousness_systems['motivation_system'].get('active_goals', [])
                if goals:
                    primary_goal = goals[0].get('description', 'unknown')[:20]
                    summary_parts.append(f"pursuing_{primary_goal}")
            
            # Attention summary
            if 'global_workspace' in consciousness_systems:
                focus = consciousness_systems['global_workspace'].get('current_focus', 'general')
                summary_parts.append(f"focused_on_{focus[:20]}")
            
            return f"[CONSCIOUSNESS:{' '.join(summary_parts)}]"
            
        except Exception as e:
            return f"[CONSCIOUSNESS_SUMMARY_ERROR:{str(e)}]"
    
    def update_consciousness_cache(self, consciousness_systems: Dict[str, Any]):
        """Update cached consciousness state for performance"""
        try:
            self.consciousness_cache = consciousness_systems.copy()
            self.last_update = time.time()
        except Exception as e:
            print(f"[ConsciousnessTokenizer] ❌ Error updating cache: {e}")
    
    def get_cached_tokens(self) -> str:
        """Get tokens from cached consciousness state"""
        if time.time() - self.last_update < 5.0:  # Use cache if less than 5 seconds old
            return self.tokenize_consciousness_state(self.consciousness_cache)
        return "[CONSCIOUSNESS_CACHE_EXPIRED]"

# Global tokenizer instance
consciousness_tokenizer = ConsciousnessTokenizer()

def tokenize_consciousness_for_llm(consciousness_systems: Dict[str, Any]) -> str:
    """
    Main function to tokenize consciousness state for LLM integration
    
    Args:
        consciousness_systems: Dictionary containing all consciousness system states
        
    Returns:
        Tokenized consciousness string ready for LLM prompt
    """
    return consciousness_tokenizer.tokenize_consciousness_state(consciousness_systems)

def get_consciousness_summary_for_llm(consciousness_systems: Dict[str, Any]) -> str:
    """
    Get a brief consciousness summary for lightweight LLM integration
    
    Args:
        consciousness_systems: Dictionary containing consciousness system states
        
    Returns:
        Brief consciousness summary string
    """
    return consciousness_tokenizer.get_consciousness_summary(consciousness_systems)

def update_consciousness_tokens(consciousness_systems: Dict[str, Any]):
    """Update consciousness tokenizer cache"""
    consciousness_tokenizer.update_consciousness_cache(consciousness_systems)

def generate_personality_tokens(user: str, personality_data: Dict[str, Any], max_tokens: int = 5) -> str:
    """
    Generate personality tokens for LLM integration as mentioned in problem statement
    Delegates to dedicated personality_tokens module for better organization
    
    Args:
        user: User identifier
        personality_data: Personality trait data
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        Personality tokens string with symbolic tokens like <pers1>, <pers2>
    """
    try:
        # Use dedicated personality tokens module
        from ai.personality_tokens import generate_personality_tokens as dedicated_generate
        return dedicated_generate(user, personality_data, max_tokens)
        
    except ImportError:
        # Fallback to original implementation for backward compatibility
        try:
            tokens = []
            
            # Generate symbolic personality tokens
            for i, (trait, data) in enumerate(personality_data.items()):
                if i < max_tokens:  # Use max_tokens parameter
                    strength = data.get('strength', 0.5) if isinstance(data, dict) else data
                    adaptation = data.get('adaptation', 'stable') if isinstance(data, dict) else 'stable'
                    
                    # Use symbolic tokens as mentioned in requirements
                    symbolic_token = f"<pers{i+1}:{trait}:{strength:.2f}:{adaptation}>"
                    tokens.append(symbolic_token)
            
            return " ".join(tokens)
            
        except Exception as e:
            print(f"[ConsciousnessTokenizer] ❌ Error generating personality tokens: {e}")
            return "<pers_error>"
    except Exception as e:
        print(f"[ConsciousnessTokenizer] ❌ Error using dedicated module: {e}")
        return "<pers_error>"

def compress_memory_entry(memory_entry: Dict[str, Any], max_tokens: int = 50) -> str:
    """
    Compress memory entry as mentioned in problem statement
    Delegates to dedicated memory_compression module for better organization
    
    Args:
        memory_entry: Memory data to compress
        max_tokens: Maximum token budget
        
    Returns:
        Compressed memory with symbolic tokens like <mem1>, <mem2>
    """
    try:
        # Use dedicated memory compression module
        from ai.memory_compression import compress_memory_entry as dedicated_compress
        return dedicated_compress(memory_entry, max_tokens)
        
    except ImportError:
        # Fallback to original implementation for backward compatibility
        try:
            # Extract key information
            content = memory_entry.get('content', '')
            significance = memory_entry.get('significance', 0.5)
            memory_type = memory_entry.get('type', 'general')
            
            # Compress based on significance
            if significance > 0.8:
                # High significance - keep more detail
                compressed = f"<mem1:{memory_type}:{significance:.2f}> {content[:30]}..."
            elif significance > 0.5:
                # Medium significance - moderate compression
                compressed = f"<mem2:{memory_type}:{significance:.2f}> {content[:20]}..."
            else:
                # Low significance - high compression
                compressed = f"<mem3:{memory_type}:{significance:.2f}> {content[:10]}..."
            
            # Ensure we don't exceed token budget
            words = compressed.split()
            if len(words) > max_tokens:
                words = words[:max_tokens]
                compressed = " ".join(words) + "..."
                
            return compressed
            
        except Exception as e:
            print(f"[ConsciousnessTokenizer] ❌ Error compressing memory: {e}")
            return "<mem_error>"
    except Exception as e:
        print(f"[ConsciousnessTokenizer] ❌ Error using dedicated module: {e}")
        return "<mem_error>"

def trim_tokens_to_budget(tokens: str, max_tokens: int) -> str:
    """
    Trim tokens to fit within budget as mentioned in problem statement
    Delegates to dedicated token_budget module for better organization
    
    Args:
        tokens: Token string to trim
        max_tokens: Maximum allowed tokens
        
    Returns:
        Trimmed token string
    """
    try:
        # Use dedicated token budget module
        from ai.token_budget import trim_tokens_to_budget as dedicated_trim
        return dedicated_trim(tokens, max_tokens)
        
    except ImportError:
        # Fallback to original implementation for backward compatibility
        try:
            words = tokens.split()
            if len(words) <= max_tokens:
                return tokens
                
            # Prioritize symbolic tokens and important content
            symbolic_tokens = [w for w in words if w.startswith('<') and w.endswith('>')]
            regular_words = [w for w in words if not (w.startswith('<') and w.endswith('>'))]
            
            # Keep all symbolic tokens if possible, trim regular words
            if len(symbolic_tokens) <= max_tokens:
                remaining_budget = max_tokens - len(symbolic_tokens)
                if remaining_budget > 0:
                    trimmed_words = symbolic_tokens + regular_words[:remaining_budget]
                else:
                    trimmed_words = symbolic_tokens[:max_tokens]
            else:
                # Even symbolic tokens need trimming
                trimmed_words = symbolic_tokens[:max_tokens]
                
            return " ".join(trimmed_words)
            
        except Exception as e:
            print(f"[ConsciousnessTokenizer] ❌ Error trimming tokens: {e}")
            return tokens[:max_tokens * 6]  # Rough character fallback
    except Exception as e:
        print(f"[ConsciousnessTokenizer] ❌ Error using dedicated module: {e}")
        return tokens[:max_tokens * 6]

if __name__ == "__main__":
    # Test the tokenizer with sample data
    test_consciousness = {
        'emotion_engine': {
            'primary_emotion': 'curious',
            'intensity': 0.7,
            'secondary_emotions': {'excitement': 0.5, 'focus': 0.6}
        },
        'motivation_system': {
            'active_goals': [
                {'description': 'Understand user intent', 'priority': 0.9, 'progress': 0.3},
                {'description': 'Provide helpful response', 'priority': 0.8, 'progress': 0.1}
            ]
        },
        'global_workspace': {
            'current_focus': 'user_conversation',
            'focus_priority': 'high'
        }
    }
    
    tokenized = tokenize_consciousness_for_llm(test_consciousness)
    print("Tokenized consciousness:")
    print(tokenized)
    
    summary = get_consciousness_summary_for_llm(test_consciousness)
    print("\nConsciousness summary:")
    print(summary)