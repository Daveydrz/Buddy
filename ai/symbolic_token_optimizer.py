"""
Symbolic Token Compression System for LLM Latency Optimization
Created: 2025-01-17
Purpose: Replace verbose consciousness descriptions with compact symbolic tokens
         to reduce prompt size by 80-90% while preserving consciousness integration
"""

import json
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class SymbolicToken:
    """Compact representation of consciousness state components"""
    token: str
    category: str
    value: Any
    importance: float  # 0.0-1.0 priority for inclusion
    
class SymbolicTokenOptimizer:
    """
    Converts verbose consciousness data into compact symbolic tokens
    Example: "Currently feeling calm and slightly curious with moderate confidence" 
    → "<<mood_calm_6>><<curiosity_4>><<confidence_5>>"
    """
    
    def __init__(self):
        self.token_patterns = {
            # Emotional state tokens (0-10 scale)
            'mood': '<<mood_{state}_{intensity}>>',
            'emotion': '<<em_{emotion}_{level}>>',
            'valence': '<<val_{direction}_{strength}>>',
            'energy': '<<nrg_{level}>>',
            
            # Cognitive state tokens
            'attention': '<<att_{focus}_{intensity}>>',
            'clarity': '<<clr_{level}>>',
            'processing': '<<proc_{mode}>>',
            'confidence': '<<conf_{level}>>',
            
            # Memory tokens (contextual)
            'memory': '<<mem_{type}_{relevance}>>',
            'context': '<<ctx_{topic}_{importance}>>',
            'recall': '<<rec_{accuracy}_{depth}>>',
            
            # Goal and motivation tokens
            'goal': '<<goal_{status}_{priority}>>',
            'motivation': '<<mot_{level}_{direction}>>',
            'progress': '<<prog_{percentage}>>',
            
            # Personality trait tokens
            'trait': '<<trait_{name}_{strength}>>',
            'style': '<<style_{type}>>',
            'adaptation': '<<adapt_{change}>>',
            
            # Temporal context tokens
            'time': '<<time_{period}>>',
            'session': '<<sess_{duration}_{activity}>>',
            'pattern': '<<ptrn_{type}_{frequency}>>',
            
            # Interaction tokens
            'user_state': '<<usr_{detected_mood}_{confidence}>>',
            'relationship': '<<rel_{closeness}_{interaction_count}>>',
            'communication': '<<comm_{style}_{effectiveness}>>',
        }
        
        # Token priorities for budget constraints
        self.token_priorities = {
            'mood': 0.9,
            'emotion': 0.8,
            'attention': 0.7,
            'goal': 0.6,
            'memory': 0.8,
            'trait': 0.5,
            'time': 0.4,
            'user_state': 0.9,
            'communication': 0.6
        }
        
        # Value mappings for different scales
        self.value_mappings = {
            # 0.0-1.0 → 0-10 scale
            'intensity_10': lambda x: min(10, max(0, int(x * 10))),
            # 0.0-1.0 → 0-5 scale  
            'level_5': lambda x: min(5, max(0, int(x * 5))),
            # Text → numeric
            'mood_numeric': {
                'joyful': 9, 'happy': 8, 'content': 7, 'calm': 6, 'neutral': 5,
                'melancholy': 4, 'sad': 3, 'anxious': 2, 'distressed': 1, 'angry': 0
            },
            'emotion_numeric': {
                'love': 9, 'joy': 8, 'excitement': 7, 'curiosity': 6, 'calm': 5,
                'concern': 4, 'worry': 3, 'frustration': 2, 'fear': 1, 'anger': 0
            }
        }
        
    def compress_consciousness_state(self, 
                                   consciousness_data: Dict[str, Any],
                                   max_tokens: int = 15,
                                   importance_threshold: float = 0.3) -> str:
        """
        Convert full consciousness state to symbolic tokens
        
        Args:
            consciousness_data: Full consciousness state from modules
            max_tokens: Maximum number of tokens to include
            importance_threshold: Minimum importance to include token
            
        Returns:
            Compressed symbolic token string
        """
        try:
            tokens = []
            
            # Extract mood/emotion tokens
            if 'emotional_state' in consciousness_data:
                emotion_tokens = self._extract_emotion_tokens(consciousness_data['emotional_state'])
                tokens.extend(emotion_tokens)
            
            # Extract cognitive tokens
            if 'cognitive_state' in consciousness_data:
                cognitive_tokens = self._extract_cognitive_tokens(consciousness_data['cognitive_state'])
                tokens.extend(cognitive_tokens)
            
            # Extract memory tokens
            if 'memory_context' in consciousness_data:
                memory_tokens = self._extract_memory_tokens(consciousness_data['memory_context'])
                tokens.extend(memory_tokens)
            
            # Extract goal tokens
            if 'goals' in consciousness_data:
                goal_tokens = self._extract_goal_tokens(consciousness_data['goals'])
                tokens.extend(goal_tokens)
            
            # Extract personality tokens
            if 'personality' in consciousness_data:
                personality_tokens = self._extract_personality_tokens(consciousness_data['personality'])
                tokens.extend(personality_tokens)
            
            # Extract temporal tokens
            if 'temporal_context' in consciousness_data:
                temporal_tokens = self._extract_temporal_tokens(consciousness_data['temporal_context'])
                tokens.extend(temporal_tokens)
            
            # Extract user state tokens
            if 'user_context' in consciousness_data:
                user_tokens = self._extract_user_tokens(consciousness_data['user_context'])
                tokens.extend(user_tokens)
            
            # Filter by importance and limit count
            important_tokens = [t for t in tokens if t.importance >= importance_threshold]
            important_tokens.sort(key=lambda x: x.importance, reverse=True)
            selected_tokens = important_tokens[:max_tokens]
            
            # Build symbolic token string
            token_string = ''.join([t.token for t in selected_tokens])
            
            print(f"[SymbolicTokenOptimizer] 🎯 Compressed {len(consciousness_data)} components → {len(selected_tokens)} tokens")
            return token_string
            
        except Exception as e:
            print(f"[SymbolicTokenOptimizer] ❌ Compression error: {e}")
            return "<<consciousness_error>>"
    
    def _extract_emotion_tokens(self, emotional_state: Dict[str, Any]) -> List[SymbolicToken]:
        """Extract emotion-related symbolic tokens"""
        tokens = []
        
        try:
            # Mood token
            if 'mood' in emotional_state:
                mood = emotional_state['mood']
                intensity = emotional_state.get('intensity', 0.5)
                mood_num = self.value_mappings['mood_numeric'].get(mood, 5)
                intensity_num = self.value_mappings['intensity_10'](intensity)
                
                token = SymbolicToken(
                    token=f"<<mood_{mood}_{intensity_num}>>",
                    category='emotion',
                    value={'mood': mood, 'intensity': intensity},
                    importance=self.token_priorities['mood']
                )
                tokens.append(token)
            
            # Valence token
            if 'valence' in emotional_state:
                valence = emotional_state['valence']
                direction = 'pos' if valence > 0 else 'neg' if valence < 0 else 'neu'
                strength = self.value_mappings['level_5'](abs(valence))
                
                token = SymbolicToken(
                    token=f"<<val_{direction}_{strength}>>",
                    category='emotion',
                    value={'valence': valence},
                    importance=0.7
                )
                tokens.append(token)
            
            # Energy level token
            if 'energy' in emotional_state:
                energy = emotional_state['energy']
                energy_level = self.value_mappings['intensity_10'](energy)
                
                token = SymbolicToken(
                    token=f"<<nrg_{energy_level}>>",
                    category='emotion',
                    value={'energy': energy},
                    importance=0.6
                )
                tokens.append(token)
                
        except Exception as e:
            print(f"[SymbolicTokenOptimizer] ⚠️ Emotion token extraction error: {e}")
        
        return tokens
    
    def _extract_cognitive_tokens(self, cognitive_state: Dict[str, Any]) -> List[SymbolicToken]:
        """Extract cognitive-related symbolic tokens"""
        tokens = []
        
        try:
            # Attention focus token
            if 'focus' in cognitive_state:
                focus = cognitive_state['focus']
                intensity = cognitive_state.get('intensity', 0.5)
                intensity_num = self.value_mappings['level_5'](intensity)
                
                token = SymbolicToken(
                    token=f"<<att_{focus}_{intensity_num}>>",
                    category='cognitive',
                    value={'focus': focus, 'intensity': intensity},
                    importance=self.token_priorities['attention']
                )
                tokens.append(token)
            
            # Clarity token
            if 'clarity' in cognitive_state:
                clarity = cognitive_state['clarity']
                clarity_level = self.value_mappings['intensity_10'](clarity)
                
                token = SymbolicToken(
                    token=f"<<clr_{clarity_level}>>",
                    category='cognitive',
                    value={'clarity': clarity},
                    importance=0.6
                )
                tokens.append(token)
            
            # Processing mode token
            if 'mode' in cognitive_state:
                mode = cognitive_state['mode']
                
                token = SymbolicToken(
                    token=f"<<proc_{mode}>>",
                    category='cognitive',
                    value={'mode': mode},
                    importance=0.5
                )
                tokens.append(token)
                
        except Exception as e:
            print(f"[SymbolicTokenOptimizer] ⚠️ Cognitive token extraction error: {e}")
        
        return tokens
    
    def _extract_memory_tokens(self, memory_context: Dict[str, Any]) -> List[SymbolicToken]:
        """Extract memory-related symbolic tokens"""
        tokens = []
        
        try:
            # Recent memory relevance
            if 'recent_memories' in memory_context:
                memories = memory_context['recent_memories']
                relevance = len(memories) / 10.0  # Normalize by typical max
                relevance_level = self.value_mappings['level_5'](relevance)
                
                token = SymbolicToken(
                    token=f"<<mem_recent_{relevance_level}>>",
                    category='memory',
                    value={'memory_count': len(memories)},
                    importance=self.token_priorities['memory']
                )
                tokens.append(token)
            
            # Context topic (most relevant topic from memories)
            if 'context_topic' in memory_context:
                topic = memory_context['context_topic']
                importance = memory_context.get('topic_importance', 0.5)
                importance_level = self.value_mappings['level_5'](importance)
                
                token = SymbolicToken(
                    token=f"<<ctx_{topic}_{importance_level}>>",
                    category='memory',
                    value={'topic': topic, 'importance': importance},
                    importance=0.7
                )
                tokens.append(token)
                
        except Exception as e:
            print(f"[SymbolicTokenOptimizer] ⚠️ Memory token extraction error: {e}")
        
        return tokens
    
    def _extract_goal_tokens(self, goals_data: Dict[str, Any]) -> List[SymbolicToken]:
        """Extract goal-related symbolic tokens"""
        tokens = []
        
        try:
            # Active goals status
            if 'active_goals' in goals_data:
                goals = goals_data['active_goals']
                if goals:
                    # Get highest priority goal
                    priority_goal = goals[0] if isinstance(goals, list) else goals
                    if isinstance(priority_goal, dict):
                        status = priority_goal.get('status', 'active')
                        progress = priority_goal.get('progress', 0.0)
                        priority = priority_goal.get('priority', 0.5)
                        
                        progress_level = self.value_mappings['intensity_10'](progress)
                        priority_level = self.value_mappings['level_5'](priority)
                        
                        token = SymbolicToken(
                            token=f"<<goal_{status}_{priority_level}>>",
                            category='goal',
                            value={'status': status, 'progress': progress},
                            importance=self.token_priorities['goal']
                        )
                        tokens.append(token)
                        
                        # Progress token
                        if progress > 0:
                            progress_token = SymbolicToken(
                                token=f"<<prog_{progress_level}>>",
                                category='goal',
                                value={'progress': progress},
                                importance=0.5
                            )
                            tokens.append(progress_token)
                            
        except Exception as e:
            print(f"[SymbolicTokenOptimizer] ⚠️ Goal token extraction error: {e}")
        
        return tokens
    
    def _extract_personality_tokens(self, personality_data: Dict[str, Any]) -> List[SymbolicToken]:
        """Extract personality-related symbolic tokens"""
        tokens = []
        
        try:
            # Interaction style
            if 'style' in personality_data:
                style = personality_data['style']
                
                token = SymbolicToken(
                    token=f"<<style_{style}>>",
                    category='personality',
                    value={'style': style},
                    importance=self.token_priorities['trait']
                )
                tokens.append(token)
            
            # Most prominent personality trait
            if 'modifiers' in personality_data:
                modifiers = personality_data['modifiers']
                if modifiers:
                    # Get strongest trait
                    strongest_trait = max(modifiers.items(), key=lambda x: abs(x[1]))
                    trait_name, trait_value = strongest_trait
                    trait_level = self.value_mappings['level_5'](abs(trait_value))
                    
                    token = SymbolicToken(
                        token=f"<<trait_{trait_name}_{trait_level}>>",
                        category='personality',
                        value={'trait': trait_name, 'value': trait_value},
                        importance=0.6
                    )
                    tokens.append(token)
                    
        except Exception as e:
            print(f"[SymbolicTokenOptimizer] ⚠️ Personality token extraction error: {e}")
        
        return tokens
    
    def _extract_temporal_tokens(self, temporal_context: Dict[str, Any]) -> List[SymbolicToken]:
        """Extract time-related symbolic tokens"""
        tokens = []
        
        try:
            # Time of day
            if 'time_of_day' in temporal_context:
                time_period = temporal_context['time_of_day']
                
                token = SymbolicToken(
                    token=f"<<time_{time_period}>>",
                    category='temporal',
                    value={'time': time_period},
                    importance=self.token_priorities['time']
                )
                tokens.append(token)
            
            # Session duration/activity
            if 'session_info' in temporal_context:
                session = temporal_context['session_info']
                duration = session.get('duration', 'short')
                activity = session.get('activity', 'chat')
                
                token = SymbolicToken(
                    token=f"<<sess_{duration}_{activity}>>",
                    category='temporal',
                    value={'duration': duration, 'activity': activity},
                    importance=0.4
                )
                tokens.append(token)
                
        except Exception as e:
            print(f"[SymbolicTokenOptimizer] ⚠️ Temporal token extraction error: {e}")
        
        return tokens
    
    def _extract_user_tokens(self, user_context: Dict[str, Any]) -> List[SymbolicToken]:
        """Extract user state-related symbolic tokens"""
        tokens = []
        
        try:
            # Detected user mood
            if 'detected_mood' in user_context:
                mood = user_context['detected_mood']
                confidence = user_context.get('mood_confidence', 0.5)
                confidence_level = self.value_mappings['level_5'](confidence)
                
                token = SymbolicToken(
                    token=f"<<usr_{mood}_{confidence_level}>>",
                    category='user',
                    value={'mood': mood, 'confidence': confidence},
                    importance=self.token_priorities['user_state']
                )
                tokens.append(token)
            
            # Relationship closeness
            if 'relationship' in user_context:
                relationship = user_context['relationship']
                closeness = relationship.get('closeness', 0.5)
                interaction_count = relationship.get('interaction_count', 1)
                
                closeness_level = self.value_mappings['level_5'](closeness)
                count_level = min(9, max(1, int(interaction_count / 10)))
                
                token = SymbolicToken(
                    token=f"<<rel_{closeness_level}_{count_level}>>",
                    category='user',
                    value={'closeness': closeness, 'interactions': interaction_count},
                    importance=0.6
                )
                tokens.append(token)
                
        except Exception as e:
            print(f"[SymbolicTokenOptimizer] ⚠️ User token extraction error: {e}")
        
        return tokens
    
    def expand_symbolic_tokens(self, symbolic_string: str) -> Dict[str, Any]:
        """
        Convert symbolic tokens back to readable consciousness summary
        Used for debugging and verification
        """
        try:
            # Extract all tokens from string
            token_pattern = r'<<([^>]+)>>'
            tokens = re.findall(token_pattern, symbolic_string)
            
            expanded = {
                'emotional_state': {},
                'cognitive_state': {},
                'memory_context': {},
                'goals': {},
                'personality': {},
                'temporal_context': {},
                'user_context': {}
            }
            
            for token in tokens:
                parts = token.split('_')
                if len(parts) >= 2:
                    category = parts[0]
                    
                    # Expand based on category
                    if category in ['mood', 'em', 'val', 'nrg']:
                        self._expand_emotion_token(token, expanded['emotional_state'])
                    elif category in ['att', 'clr', 'proc', 'conf']:
                        self._expand_cognitive_token(token, expanded['cognitive_state'])
                    elif category in ['mem', 'ctx', 'rec']:
                        self._expand_memory_token(token, expanded['memory_context'])
                    elif category in ['goal', 'mot', 'prog']:
                        self._expand_goal_token(token, expanded['goals'])
                    elif category in ['trait', 'style', 'adapt']:
                        self._expand_personality_token(token, expanded['personality'])
                    elif category in ['time', 'sess', 'ptrn']:
                        self._expand_temporal_token(token, expanded['temporal_context'])
                    elif category in ['usr', 'rel', 'comm']:
                        self._expand_user_token(token, expanded['user_context'])
            
            return expanded
            
        except Exception as e:
            print(f"[SymbolicTokenOptimizer] ❌ Token expansion error: {e}")
            return {}
    
    def _expand_emotion_token(self, token: str, emotional_state: Dict[str, Any]):
        """Expand emotion token back to readable form"""
        parts = token.split('_')
        if parts[0] == 'mood' and len(parts) >= 3:
            emotional_state['mood'] = parts[1]
            emotional_state['intensity'] = int(parts[2]) / 10.0
        elif parts[0] == 'val' and len(parts) >= 3:
            direction = parts[1]
            strength = int(parts[2]) / 5.0
            emotional_state['valence'] = strength if direction == 'pos' else -strength if direction == 'neg' else 0
        elif parts[0] == 'nrg' and len(parts) >= 2:
            emotional_state['energy'] = int(parts[1]) / 10.0
    
    def _expand_cognitive_token(self, token: str, cognitive_state: Dict[str, Any]):
        """Expand cognitive token back to readable form"""
        parts = token.split('_')
        if parts[0] == 'att' and len(parts) >= 3:
            cognitive_state['focus'] = parts[1]
            cognitive_state['intensity'] = int(parts[2]) / 5.0
        elif parts[0] == 'clr' and len(parts) >= 2:
            cognitive_state['clarity'] = int(parts[1]) / 10.0
        elif parts[0] == 'proc' and len(parts) >= 2:
            cognitive_state['mode'] = parts[1]
    
    def _expand_memory_token(self, token: str, memory_context: Dict[str, Any]):
        """Expand memory token back to readable form"""
        parts = token.split('_')
        if parts[0] == 'mem' and len(parts) >= 3:
            memory_context['type'] = parts[1]
            memory_context['relevance'] = int(parts[2]) / 5.0
        elif parts[0] == 'ctx' and len(parts) >= 3:
            memory_context['topic'] = parts[1]
            memory_context['importance'] = int(parts[2]) / 5.0
    
    def _expand_goal_token(self, token: str, goals: Dict[str, Any]):
        """Expand goal token back to readable form"""
        parts = token.split('_')
        if parts[0] == 'goal' and len(parts) >= 3:
            goals['status'] = parts[1]
            goals['priority'] = int(parts[2]) / 5.0
        elif parts[0] == 'prog' and len(parts) >= 2:
            goals['progress'] = int(parts[1]) / 10.0
    
    def _expand_personality_token(self, token: str, personality: Dict[str, Any]):
        """Expand personality token back to readable form"""
        parts = token.split('_')
        if parts[0] == 'style' and len(parts) >= 2:
            personality['style'] = parts[1]
        elif parts[0] == 'trait' and len(parts) >= 3:
            if 'traits' not in personality:
                personality['traits'] = {}
            personality['traits'][parts[1]] = int(parts[2]) / 5.0
    
    def _expand_temporal_token(self, token: str, temporal_context: Dict[str, Any]):
        """Expand temporal token back to readable form"""
        parts = token.split('_')
        if parts[0] == 'time' and len(parts) >= 2:
            temporal_context['time_of_day'] = parts[1]
        elif parts[0] == 'sess' and len(parts) >= 3:
            temporal_context['session_duration'] = parts[1]
            temporal_context['session_activity'] = parts[2]
    
    def _expand_user_token(self, token: str, user_context: Dict[str, Any]):
        """Expand user token back to readable form"""
        parts = token.split('_')
        if parts[0] == 'usr' and len(parts) >= 3:
            user_context['detected_mood'] = parts[1]
            user_context['confidence'] = int(parts[2]) / 5.0
        elif parts[0] == 'rel' and len(parts) >= 3:
            user_context['relationship_closeness'] = int(parts[1]) / 5.0
            user_context['interaction_count'] = int(parts[2]) * 10

# Global instance
symbolic_token_optimizer = SymbolicTokenOptimizer()

def compress_consciousness_to_tokens(consciousness_data: Dict[str, Any], 
                                   max_tokens: int = 15,
                                   importance_threshold: float = 0.3) -> str:
    """Convenience function for consciousness compression"""
    return symbolic_token_optimizer.compress_consciousness_state(
        consciousness_data, max_tokens, importance_threshold
    )

def expand_tokens_to_consciousness(token_string: str) -> Dict[str, Any]:
    """Convenience function for token expansion"""
    return symbolic_token_optimizer.expand_symbolic_tokens(token_string)