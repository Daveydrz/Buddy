"""
Personality Token Generation System
Created: 2025-01-17
Purpose: Core tokenization system that transforms memory data into consumable LLM tokens
         with symbolic personality tokens like <pers_name>, <mem_emotion>, etc.
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

class PersonalityTokenGenerator:
    """
    Core tokenization system that converts stored memory data into symbolic tokens
    Integrates with IntelligentMemoryAnalyzer profiles
    """
    
    def __init__(self):
        self.token_formats = {
            'personality': '<pers{index}:{trait}:{strength:.2f}:{adaptation}>',
            'memory_emotion': '<mem_emotion:{emotion}:{intensity:.2f}>',
            'entity_relationship': '<ent_{type}:{status}:{name}>',
            'factual_data': '<fact_{category}:{value}>',
            'temporal_context': '<time_{type}:{timeframe}:{significance:.2f}>',
            'behavioral_pattern': '<behav_{pattern}:{frequency:.2f}:{confidence:.2f}>',
            'conversation_style': '<style_{aspect}:{level}:{adaptation}>'
        }
        
        # Priority mapping for trait importance
        self.trait_priorities = {
            'friendliness': 1,
            'empathy': 2,
            'humor': 3,
            'curiosity': 4,
            'patience': 5,
            'formality': 6,
            'enthusiasm': 7,
            'assertiveness': 8,
            'supportiveness': 9,
            'playfulness': 10
        }
        
        # Adaptation level mappings
        self.adaptation_levels = {
            'increasing': 'inc',
            'decreasing': 'dec', 
            'stable': 'stable',
            'fluctuating': 'flux',
            'uncertain': 'unc'
        }
        
        print("[PersonalityTokens] 🎭 Personality token generator initialized")
    
    def generate_personality_tokens(self, user: str, personality_data: Dict[str, Any], 
                                   max_tokens: int = 5) -> str:
        """
        Convert stored memory data into symbolic tokens
        Consumes data from IntelligentMemoryAnalyzer profiles
        
        Args:
            user: User identifier
            personality_data: Personality trait data from memory analysis
            max_tokens: Maximum number of personality tokens to generate
            
        Returns:
            String with symbolic tokens like <pers1:friendliness:0.90:stable>
        """
        try:
            if not personality_data:
                return "<pers_none>"
            
            tokens = []
            
            # Sort traits by priority and strength
            sorted_traits = self._prioritize_traits(personality_data)
            
            # Generate symbolic personality tokens
            for i, (trait, data) in enumerate(sorted_traits[:max_tokens]):
                if isinstance(data, dict):
                    strength = data.get('strength', 0.5)
                    adaptation = data.get('adaptation', 'stable')
                else:
                    strength = float(data) if isinstance(data, (int, float)) else 0.5
                    adaptation = 'stable'
                
                # Map adaptation to shorter form
                adaptation_short = self.adaptation_levels.get(adaptation, adaptation[:6])
                
                # Generate symbolic token as specified in requirements
                token = f"<pers{i+1}:{trait}:{strength:.2f}:{adaptation_short}>"
                tokens.append(token)
            
            result = " ".join(tokens)
            print(f"[PersonalityTokens] 🎭 Generated {len(tokens)} personality tokens for {user}")
            return result
            
        except Exception as e:
            print(f"[PersonalityTokens] ❌ Error generating personality tokens: {e}")
            return "<pers_error>"
    
    def generate_entity_tokens(self, entity_memories: Dict[str, Any]) -> List[str]:
        """
        Generate entity relationship tokens like <ent_pet:deceased:Fluffy>
        
        Args:
            entity_memories: Entity memory data
            
        Returns:
            List of entity tokens
        """
        try:
            tokens = []
            
            for entity_id, entity_data in entity_memories.items():
                entity_type = entity_data.get('type', 'unknown')
                status = entity_data.get('status', 'unknown') 
                name = entity_data.get('name', entity_id)
                
                # Clean name for token format
                clean_name = re.sub(r'[^a-zA-Z0-9]', '', name)[:15]
                
                token = f"<ent_{entity_type}:{status}:{clean_name}>"
                tokens.append(token)
            
            print(f"[PersonalityTokens] 🎯 Generated {len(tokens)} entity tokens")
            return tokens
            
        except Exception as e:
            print(f"[PersonalityTokens] ❌ Error generating entity tokens: {e}")
            return ["<ent_error>"]
    
    def generate_factual_tokens(self, personal_facts: Dict[str, Any]) -> List[str]:
        """
        Generate factual data tokens like <fact_job:engineer>
        
        Args:
            personal_facts: Personal factual data
            
        Returns:
            List of factual tokens
        """
        try:
            tokens = []
            
            # Common fact categories
            fact_categories = {
                'occupation': 'job',
                'job': 'job',
                'career': 'job',
                'location': 'loc',
                'city': 'loc',
                'country': 'loc',
                'education': 'edu',
                'school': 'edu',
                'university': 'edu',
                'hobby': 'hobby',
                'interest': 'hobby',
                'family': 'family',
                'age': 'age',
                'skills': 'skill'
            }
            
            for fact_key, fact_value in personal_facts.items():
                category = fact_categories.get(fact_key.lower(), fact_key[:8])
                
                # Clean value for token format
                if isinstance(fact_value, str):
                    clean_value = re.sub(r'[^a-zA-Z0-9]', '', fact_value)[:20]
                else:
                    clean_value = str(fact_value)[:20]
                
                token = f"<fact_{category}:{clean_value}>"
                tokens.append(token)
            
            print(f"[PersonalityTokens] 📋 Generated {len(tokens)} factual tokens")
            return tokens
            
        except Exception as e:
            print(f"[PersonalityTokens] ❌ Error generating factual tokens: {e}")
            return ["<fact_error>"]
    
    def generate_emotional_context_tokens(self, emotion_data: Dict[str, Any]) -> List[str]:
        """
        Generate emotional context tokens like <mem_emotion:happy>
        
        Args:
            emotion_data: Emotional context data
            
        Returns:
            List of emotional tokens
        """
        try:
            tokens = []
            
            if 'dominant_emotion' in emotion_data:
                emotion = emotion_data['dominant_emotion']
                intensity = emotion_data.get('intensity', 0.5)
                token = f"<mem_emotion:{emotion}:{intensity:.2f}>"
                tokens.append(token)
            
            # Add secondary emotions if significant
            if 'secondary_emotions' in emotion_data:
                for emotion, intensity in emotion_data['secondary_emotions'].items():
                    if intensity > 0.3:  # Only include significant emotions
                        token = f"<mem_emotion:{emotion}:{intensity:.2f}>"
                        tokens.append(token)
                        if len(tokens) >= 3:  # Limit to avoid token budget issues
                            break
            
            print(f"[PersonalityTokens] 😊 Generated {len(tokens)} emotional tokens")
            return tokens
            
        except Exception as e:
            print(f"[PersonalityTokens] ❌ Error generating emotional tokens: {e}")
            return ["<emotion_error>"]
    
    def generate_behavioral_tokens(self, behavioral_data: Dict[str, Any]) -> List[str]:
        """
        Generate behavioral pattern tokens
        
        Args:
            behavioral_data: Behavioral pattern data
            
        Returns:
            List of behavioral tokens
        """
        try:
            tokens = []
            
            patterns = behavioral_data.get('patterns', {})
            for pattern_name, pattern_data in patterns.items():
                frequency = pattern_data.get('frequency', 0.5)
                confidence = pattern_data.get('confidence', 0.5)
                
                if confidence > 0.3:  # Only include confident patterns
                    clean_pattern = re.sub(r'[^a-zA-Z0-9]', '', pattern_name)[:15]
                    token = f"<behav_{clean_pattern}:{frequency:.2f}:{confidence:.2f}>"
                    tokens.append(token)
            
            print(f"[PersonalityTokens] 🎯 Generated {len(tokens)} behavioral tokens")
            return tokens
            
        except Exception as e:
            print(f"[PersonalityTokens] ❌ Error generating behavioral tokens: {e}")
            return ["<behav_error>"]
    
    def generate_comprehensive_token_set(self, user_profile: Dict[str, Any], 
                                        max_total_tokens: int = 15) -> str:
        """
        Generate comprehensive set of personality tokens from complete user profile
        Integrates with existing IntelligentMemoryAnalyzer system
        
        Args:
            user_profile: Complete user profile from memory analyzer
            max_total_tokens: Maximum total tokens to generate
            
        Returns:
            Complete token string for LLM integration
        """
        try:
            all_tokens = []
            
            # Generate personality tokens (highest priority)
            if 'personality' in user_profile:
                personality_tokens = self.generate_personality_tokens(
                    user_profile.get('user', 'unknown'),
                    user_profile['personality'],
                    max_tokens=5
                )
                all_tokens.extend(personality_tokens.split())
            
            # Generate entity tokens
            if 'entities' in user_profile:
                entity_tokens = self.generate_entity_tokens(user_profile['entities'])
                all_tokens.extend(entity_tokens[:3])  # Limit entity tokens
            
            # Generate factual tokens
            if 'personal_facts' in user_profile:
                fact_tokens = self.generate_factual_tokens(user_profile['personal_facts'])
                all_tokens.extend(fact_tokens[:3])  # Limit fact tokens
            
            # Generate emotional context tokens
            if 'emotional_context' in user_profile:
                emotion_tokens = self.generate_emotional_context_tokens(user_profile['emotional_context'])
                all_tokens.extend(emotion_tokens[:2])  # Limit emotion tokens
            
            # Generate behavioral tokens
            if 'behavioral_patterns' in user_profile:
                behavior_tokens = self.generate_behavioral_tokens(user_profile['behavioral_patterns'])
                all_tokens.extend(behavior_tokens[:2])  # Limit behavior tokens
            
            # Trim to max tokens while preserving priorities
            if len(all_tokens) > max_total_tokens:
                all_tokens = all_tokens[:max_total_tokens]
            
            result = " ".join(all_tokens)
            print(f"[PersonalityTokens] ✅ Generated comprehensive token set: {len(all_tokens)} tokens")
            return result
            
        except Exception as e:
            print(f"[PersonalityTokens] ❌ Error generating comprehensive tokens: {e}")
            return "<tokens_error>"
    
    def _prioritize_traits(self, personality_data: Dict[str, Any]) -> List[Tuple[str, Any]]:
        """
        Prioritize personality traits by importance and strength
        
        Args:
            personality_data: Raw personality data
            
        Returns:
            Sorted list of (trait, data) tuples
        """
        try:
            trait_scores = []
            
            for trait, data in personality_data.items():
                # Get base priority (lower number = higher priority)
                base_priority = self.trait_priorities.get(trait, 100)
                
                # Get strength value
                if isinstance(data, dict):
                    strength = data.get('strength', 0.5)
                else:
                    strength = float(data) if isinstance(data, (int, float)) else 0.5
                
                # Calculate combined score (lower is better)
                # High strength and high priority (low number) = low score
                score = base_priority - (strength * 50)
                
                trait_scores.append((score, trait, data))
            
            # Sort by score (ascending - lower scores first)
            trait_scores.sort(key=lambda x: x[0])
            
            # Return trait, data pairs
            return [(trait, data) for score, trait, data in trait_scores]
            
        except Exception as e:
            print(f"[PersonalityTokens] ❌ Error prioritizing traits: {e}")
            return list(personality_data.items())
    
    def validate_token_format(self, token: str) -> bool:
        """
        Validate that a token follows the expected format
        
        Args:
            token: Token string to validate
            
        Returns:
            True if token format is valid
        """
        try:
            # Check for basic symbolic token structure
            if not (token.startswith('<') and token.endswith('>')):
                return False
            
            # Check for expected patterns
            patterns = [
                r'<pers\d+:[a-zA-Z]+:\d\.\d{2}:[a-zA-Z]+>',
                r'<mem_emotion:[a-zA-Z]+:\d\.\d{2}>',
                r'<ent_[a-zA-Z]+:[a-zA-Z]+:[a-zA-Z0-9]+>',
                r'<fact_[a-zA-Z]+:[a-zA-Z0-9]+>',
                r'<behav_[a-zA-Z0-9]+:\d\.\d{2}:\d\.\d{2}>'
            ]
            
            for pattern in patterns:
                if re.match(pattern, token):
                    return True
            
            return False
            
        except Exception as e:
            print(f"[PersonalityTokens] ❌ Error validating token: {e}")
            return False

# Global instance
personality_token_generator = PersonalityTokenGenerator()

def generate_personality_tokens(user: str, personality_data: Dict[str, Any], 
                              max_tokens: int = 5) -> str:
    """
    Main function to generate personality tokens
    Compatible with existing consciousness_tokenizer interface
    """
    return personality_token_generator.generate_personality_tokens(user, personality_data, max_tokens)

def generate_user_token_profile(user_profile: Dict[str, Any], max_tokens: int = 15) -> str:
    """
    Generate comprehensive user token profile from memory analyzer data
    """
    return personality_token_generator.generate_comprehensive_token_set(user_profile, max_tokens)

def validate_personality_token(token: str) -> bool:
    """
    Validate personality token format
    """
    return personality_token_generator.validate_token_format(token)

if __name__ == "__main__":
    # Test the personality token generator
    print("🧪 Testing Personality Token Generator")
    
    # Test basic personality tokens
    test_personality = {
        'friendliness': {'strength': 0.9, 'adaptation': 'stable'},
        'humor': {'strength': 0.7, 'adaptation': 'increasing'},
        'empathy': {'strength': 0.8, 'adaptation': 'stable'}
    }
    
    tokens = generate_personality_tokens("test_user", test_personality)
    print(f"✅ Personality tokens: {tokens}")
    
    # Test comprehensive profile
    test_profile = {
        'user': 'test_user',
        'personality': test_personality,
        'entities': {
            'pet_dog': {'type': 'pet', 'status': 'alive', 'name': 'Buddy'},
            'old_car': {'type': 'vehicle', 'status': 'sold', 'name': 'Toyota'}
        },
        'personal_facts': {
            'job': 'engineer',
            'location': 'Brisbane',
            'hobby': 'programming'
        },
        'emotional_context': {
            'dominant_emotion': 'happy',
            'intensity': 0.8
        }
    }
    
    comprehensive = generate_user_token_profile(test_profile)
    print(f"✅ Comprehensive tokens: {comprehensive}")