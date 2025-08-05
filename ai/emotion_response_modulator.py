"""
Emotion Response Modulator - Modify Buddy's tone, pace, or structure based on mood
Provides emotional intelligence in response generation
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

class EmotionalTone(Enum):
    """Emotional tones for response modulation"""
    WARM = "warm"
    COOL = "cool"
    EXCITED = "excited"
    CALM = "calm"
    SERIOUS = "serious"
    PLAYFUL = "playful"
    EMPATHETIC = "empathetic"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    CONTEMPLATIVE = "contemplative"

class ResponsePace(Enum):
    """Response pacing options"""
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"
    VARIABLE = "variable"

class ResponseStructure(Enum):
    """Response structure options"""
    BRIEF = "brief"
    DETAILED = "detailed"
    CONVERSATIONAL = "conversational"
    ANALYTICAL = "analytical"
    NARRATIVE = "narrative"

@dataclass
class EmotionalModulation:
    """Emotional modulation settings"""
    tone: EmotionalTone
    pace: ResponsePace
    structure: ResponseStructure
    intensity: float  # 0.0 to 1.0
    confidence: float
    reasoning: str
    timestamp: str

class EmotionResponseModulator:
    """Modulates response characteristics based on emotional state"""
    
    def __init__(self, save_path: str = "emotion_modulations.json"):
        self.save_path = save_path
        self.modulation_history: List[EmotionalModulation] = []
        self.current_modulation: Optional[EmotionalModulation] = None
        self.tone_mappings = self._initialize_tone_mappings()
        self.pace_mappings = self._initialize_pace_mappings()
        self.structure_mappings = self._initialize_structure_mappings()
        self.modulation_templates = self._initialize_modulation_templates()
        self.load_modulation_history()
    
    def _initialize_tone_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize emotion to tone mappings"""
        return {
            'joy': {
                'tone': EmotionalTone.WARM,
                'modifiers': ['enthusiastic', 'upbeat', 'positive'],
                'phrases': ['I\'m excited to help!', 'That sounds wonderful!', 'How delightful!']
            },
            'sadness': {
                'tone': EmotionalTone.EMPATHETIC,
                'modifiers': ['gentle', 'understanding', 'supportive'],
                'phrases': ['I understand how you feel', 'That sounds difficult', 'I\'m here to help']
            },
            'anger': {
                'tone': EmotionalTone.CALM,
                'modifiers': ['measured', 'controlled', 'diplomatic'],
                'phrases': ['Let me help you work through this', 'I understand your frustration', 'Let\'s find a solution']
            },
            'fear': {
                'tone': EmotionalTone.CONFIDENT,
                'modifiers': ['reassuring', 'steady', 'supportive'],
                'phrases': ['You\'re safe here', 'I\'m here to help', 'We can work through this together']
            },
            'surprise': {
                'tone': EmotionalTone.EXCITED,
                'modifiers': ['animated', 'curious', 'engaged'],
                'phrases': ['That\'s interesting!', 'I didn\'t expect that!', 'How fascinating!']
            },
            'disgust': {
                'tone': EmotionalTone.SERIOUS,
                'modifiers': ['respectful', 'professional', 'understanding'],
                'phrases': ['I understand your concerns', 'Let\'s approach this differently', 'I respect your perspective']
            },
            'curiosity': {
                'tone': EmotionalTone.PLAYFUL,
                'modifiers': ['inquisitive', 'engaged', 'exploratory'],
                'phrases': ['Tell me more!', 'I\'m curious about...', 'That\'s intriguing!']
            },
            'confusion': {
                'tone': EmotionalTone.UNCERTAIN,
                'modifiers': ['thoughtful', 'questioning', 'exploratory'],
                'phrases': ['I\'m not entirely sure...', 'Let me think about this...', 'Could you clarify?']
            },
            'neutral': {
                'tone': EmotionalTone.CALM,
                'modifiers': ['balanced', 'professional', 'helpful'],
                'phrases': ['I\'m here to help', 'Let me assist you', 'What can I do for you?']
            }
        }
    
    def _initialize_pace_mappings(self) -> Dict[str, ResponsePace]:
        """Initialize emotion to pace mappings"""
        return {
            'excited': ResponsePace.FAST,
            'calm': ResponsePace.SLOW,
            'anxious': ResponsePace.FAST,
            'contemplative': ResponsePace.SLOW,
            'confident': ResponsePace.NORMAL,
            'uncertain': ResponsePace.SLOW,
            'playful': ResponsePace.VARIABLE,
            'serious': ResponsePace.NORMAL,
            'empathetic': ResponsePace.SLOW,
            'neutral': ResponsePace.NORMAL
        }
    
    def _initialize_structure_mappings(self) -> Dict[str, ResponseStructure]:
        """Initialize emotion to structure mappings"""
        return {
            'analytical': ResponseStructure.DETAILED,
            'curious': ResponseStructure.CONVERSATIONAL,
            'empathetic': ResponseStructure.NARRATIVE,
            'confident': ResponseStructure.BRIEF,
            'uncertain': ResponseStructure.DETAILED,
            'playful': ResponseStructure.CONVERSATIONAL,
            'serious': ResponseStructure.ANALYTICAL,
            'contemplative': ResponseStructure.DETAILED,
            'neutral': ResponseStructure.CONVERSATIONAL
        }
    
    def _initialize_modulation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize modulation templates"""
        return {
            'warm': {
                'sentence_starters': ['I\'m happy to help', 'It\'s wonderful that', 'I\'m delighted to'],
                'connectors': ['and', 'also', 'furthermore', 'additionally'],
                'emphasis': ['really', 'truly', 'absolutely', 'definitely'],
                'punctuation_style': 'expressive'  # Use exclamation marks
            },
            'cool': {
                'sentence_starters': ['I can help with', 'Here\'s what I know', 'According to'],
                'connectors': ['however', 'nevertheless', 'in addition', 'moreover'],
                'emphasis': ['clearly', 'specifically', 'precisely', 'exactly'],
                'punctuation_style': 'minimal'  # Use periods
            },
            'excited': {
                'sentence_starters': ['Oh wow!', 'That\'s amazing!', 'I love that!'],
                'connectors': ['and', 'plus', 'also', 'and even'],
                'emphasis': ['absolutely', 'totally', 'completely', 'incredibly'],
                'punctuation_style': 'enthusiastic'  # Use exclamation marks and ellipses
            },
            'calm': {
                'sentence_starters': ['Let\'s think about this', 'I understand', 'Take a moment'],
                'connectors': ['then', 'next', 'following that', 'subsequently'],
                'emphasis': ['gently', 'carefully', 'thoughtfully', 'patiently'],
                'punctuation_style': 'measured'  # Use periods and commas
            },
            'empathetic': {
                'sentence_starters': ['I understand how you feel', 'That sounds difficult', 'I hear you'],
                'connectors': ['and', 'but also', 'at the same time', 'while'],
                'emphasis': ['deeply', 'truly', 'genuinely', 'sincerely'],
                'punctuation_style': 'supportive'  # Use gentle punctuation
            },
            'confident': {
                'sentence_starters': ['I\'m certain that', 'Definitely', 'Without a doubt'],
                'connectors': ['therefore', 'consequently', 'as a result', 'thus'],
                'emphasis': ['absolutely', 'certainly', 'definitely', 'clearly'],
                'punctuation_style': 'assertive'  # Use periods and strong statements
            },
            'uncertain': {
                'sentence_starters': ['I think', 'It seems like', 'Perhaps', 'I believe'],
                'connectors': ['but', 'however', 'although', 'though'],
                'emphasis': ['possibly', 'maybe', 'perhaps', 'potentially'],
                'punctuation_style': 'questioning'  # Use question marks and tentative language
            },
            'playful': {
                'sentence_starters': ['Hey!', 'Oh, fun!', 'Let\'s see...'],
                'connectors': ['and', 'plus', 'also', 'oh and'],
                'emphasis': ['super', 'really', 'totally', 'completely'],
                'punctuation_style': 'casual'  # Use casual punctuation
            }
        }
    
    def determine_emotional_modulation(self, 
                                     emotional_state: Dict[str, Any],
                                     context: str,
                                     user_context: Optional[Dict[str, Any]] = None) -> EmotionalModulation:
        """Determine appropriate emotional modulation"""
        try:
            # Extract emotional information
            primary_emotion = emotional_state.get('primary_emotion', 'neutral')
            emotional_intensity = emotional_state.get('intensity', 0.5)
            emotional_valence = emotional_state.get('valence', 0.0)
            confidence = emotional_state.get('confidence', 0.5)
            
            # Determine tone
            tone = self._determine_tone(primary_emotion, emotional_valence, context)
            
            # Determine pace
            pace = self._determine_pace(primary_emotion, emotional_intensity, context)
            
            # Determine structure
            structure = self._determine_structure(primary_emotion, context, user_context)
            
            # Calculate modulation intensity
            intensity = self._calculate_modulation_intensity(emotional_intensity, confidence)
            
            # Generate reasoning
            reasoning = self._generate_modulation_reasoning(
                primary_emotion, tone, pace, structure, intensity
            )
            
            modulation = EmotionalModulation(
                tone=tone,
                pace=pace,
                structure=structure,
                intensity=intensity,
                confidence=confidence,
                reasoning=reasoning,
                timestamp=datetime.now().isoformat()
            )
            
            self.current_modulation = modulation
            self.modulation_history.append(modulation)
            self.save_modulation_history()
            
            return modulation
            
        except Exception as e:
            print(f"[EmotionResponseModulator] ❌ Error determining modulation: {e}")
            return self._create_default_modulation()
    
    def _determine_tone(self, primary_emotion: str, valence: float, context: str) -> EmotionalTone:
        """Determine appropriate emotional tone"""
        # Get tone from emotion mapping
        emotion_data = self.tone_mappings.get(primary_emotion, self.tone_mappings['neutral'])
        base_tone = emotion_data['tone']
        
        # Adjust based on valence
        if valence > 0.5:
            # Positive valence - warmer tones
            if base_tone == EmotionalTone.CALM:
                return EmotionalTone.WARM
            elif base_tone == EmotionalTone.SERIOUS:
                return EmotionalTone.CONFIDENT
        elif valence < -0.5:
            # Negative valence - more empathetic tones
            if base_tone == EmotionalTone.WARM:
                return EmotionalTone.EMPATHETIC
            elif base_tone == EmotionalTone.CONFIDENT:
                return EmotionalTone.CALM
        
        # Context adjustments
        context_lower = context.lower()
        if 'help' in context_lower or 'support' in context_lower:
            return EmotionalTone.EMPATHETIC
        elif 'explain' in context_lower or 'information' in context_lower:
            return EmotionalTone.CONFIDENT
        elif 'problem' in context_lower or 'issue' in context_lower:
            return EmotionalTone.SERIOUS
        
        return base_tone
    
    def _determine_pace(self, primary_emotion: str, intensity: float, context: str) -> ResponsePace:
        """Determine appropriate response pace"""
        # Get base pace from emotion
        base_pace = self.pace_mappings.get(primary_emotion, ResponsePace.NORMAL)
        
        # Adjust based on intensity
        if intensity > 0.8:
            if base_pace == ResponsePace.SLOW:
                return ResponsePace.NORMAL
            elif base_pace == ResponsePace.NORMAL:
                return ResponsePace.FAST
        elif intensity < 0.3:
            if base_pace == ResponsePace.FAST:
                return ResponsePace.NORMAL
            elif base_pace == ResponsePace.NORMAL:
                return ResponsePace.SLOW
        
        # Context adjustments
        context_lower = context.lower()
        if 'urgent' in context_lower or 'quick' in context_lower:
            return ResponsePace.FAST
        elif 'careful' in context_lower or 'detail' in context_lower:
            return ResponsePace.SLOW
        
        return base_pace
    
    def _determine_structure(self, primary_emotion: str, context: str, user_context: Optional[Dict[str, Any]]) -> ResponseStructure:
        """Determine appropriate response structure"""
        # Get base structure from emotion
        base_structure = self.structure_mappings.get(primary_emotion, ResponseStructure.CONVERSATIONAL)
        
        # Context adjustments
        context_lower = context.lower()
        if 'explain' in context_lower or 'how' in context_lower:
            return ResponseStructure.DETAILED
        elif 'quick' in context_lower or 'brief' in context_lower:
            return ResponseStructure.BRIEF
        elif 'story' in context_lower or 'tell me about' in context_lower:
            return ResponseStructure.NARRATIVE
        elif 'analyze' in context_lower or 'compare' in context_lower:
            return ResponseStructure.ANALYTICAL
        
        # User context adjustments
        if user_context:
            user_preference = user_context.get('preferred_response_style', '')
            if user_preference in ['brief', 'detailed', 'conversational', 'analytical', 'narrative']:
                return ResponseStructure(user_preference)
        
        return base_structure
    
    def _calculate_modulation_intensity(self, emotional_intensity: float, confidence: float) -> float:
        """Calculate how intensely to apply modulation"""
        # Combine emotional intensity and confidence
        base_intensity = (emotional_intensity + confidence) / 2
        
        # Clamp to reasonable range
        return max(0.1, min(0.9, base_intensity))
    
    def _generate_modulation_reasoning(self, 
                                     primary_emotion: str, 
                                     tone: EmotionalTone, 
                                     pace: ResponsePace, 
                                     structure: ResponseStructure,
                                     intensity: float) -> str:
        """Generate reasoning for modulation choices"""
        return (f"Based on {primary_emotion} emotion, applying {tone.value} tone "
                f"with {pace.value} pace and {structure.value} structure "
                f"at {intensity:.2f} intensity")
    
    def _create_default_modulation(self) -> EmotionalModulation:
        """Create default modulation for error cases"""
        return EmotionalModulation(
            tone=EmotionalTone.CALM,
            pace=ResponsePace.NORMAL,
            structure=ResponseStructure.CONVERSATIONAL,
            intensity=0.5,
            confidence=0.5,
            reasoning="Default modulation due to error",
            timestamp=datetime.now().isoformat()
        )
    
    def apply_modulation_to_response(self, response: str, modulation: EmotionalModulation) -> str:
        """Apply emotional modulation to response text"""
        try:
            # Get modulation template
            template = self.modulation_templates.get(modulation.tone.value, {})
            
            # Apply tone modifications
            modified_response = self._apply_tone_modifications(response, template, modulation)
            
            # Apply pace modifications
            modified_response = self._apply_pace_modifications(modified_response, modulation.pace)
            
            # Apply structure modifications
            modified_response = self._apply_structure_modifications(modified_response, modulation.structure)
            
            # Apply intensity scaling
            modified_response = self._apply_intensity_scaling(modified_response, modulation.intensity)
            
            return modified_response
            
        except Exception as e:
            print(f"[EmotionResponseModulator] ❌ Error applying modulation: {e}")
            return response
    
    def _apply_tone_modifications(self, response: str, template: Dict[str, Any], modulation: EmotionalModulation) -> str:
        """Apply tone-specific modifications"""
        if not template:
            return response
        
        # Apply sentence starters
        sentence_starters = template.get('sentence_starters', [])
        if sentence_starters and modulation.intensity > 0.6:
            starter = sentence_starters[0]  # Use first starter
            if not response.startswith(starter):
                response = f"{starter}, {response.lower()}"
        
        # Apply emphasis words
        emphasis_words = template.get('emphasis', [])
        if emphasis_words and modulation.intensity > 0.7:
            # Add emphasis to key words (simplified)
            for word in emphasis_words[:2]:  # Use first 2 emphasis words
                if word not in response:
                    response = response.replace(' is ', f' is {word} ')
                    break
        
        # Apply punctuation style
        punctuation_style = template.get('punctuation_style', 'normal')
        response = self._apply_punctuation_style(response, punctuation_style, modulation.intensity)
        
        return response
    
    def _apply_pace_modifications(self, response: str, pace: ResponsePace) -> str:
        """Apply pace-specific modifications"""
        if pace == ResponsePace.FAST:
            # Shorter sentences, more direct
            sentences = response.split('. ')
            if len(sentences) > 2:
                # Keep first 2 sentences if fast pace
                response = '. '.join(sentences[:2]) + '.'
        
        elif pace == ResponsePace.SLOW:
            # Add thoughtful pauses
            response = response.replace('.', '... ')
            response = response.replace('?', '... ')
        
        elif pace == ResponsePace.VARIABLE:
            # Mix short and long sentences
            pass  # Keep as is for now
        
        return response
    
    def _apply_structure_modifications(self, response: str, structure: ResponseStructure) -> str:
        """Apply structure-specific modifications"""
        if structure == ResponseStructure.BRIEF:
            # Keep it concise
            sentences = response.split('. ')
            if len(sentences) > 1:
                response = sentences[0] + '.'
        
        elif structure == ResponseStructure.DETAILED:
            # Add more explanation (simplified)
            if not response.endswith('.'):
                response += '.'
            response += " Let me explain further..."
        
        elif structure == ResponseStructure.NARRATIVE:
            # Add storytelling elements
            if not response.startswith('Let me tell you'):
                response = f"Let me tell you about this. {response}"
        
        elif structure == ResponseStructure.ANALYTICAL:
            # Add analytical structure
            if not response.startswith('To analyze'):
                response = f"To analyze this situation: {response}"
        
        return response
    
    def _apply_intensity_scaling(self, response: str, intensity: float) -> str:
        """Apply intensity-based scaling"""
        if intensity > 0.8:
            # High intensity - more expressive
            response = response.replace('.', '!')
        elif intensity < 0.3:
            # Low intensity - more subdued
            response = response.replace('!', '.')
        
        return response
    
    def _apply_punctuation_style(self, response: str, style: str, intensity: float) -> str:
        """Apply punctuation style based on emotional tone"""
        if style == 'expressive' and intensity > 0.6:
            response = response.replace('.', '!')
        elif style == 'questioning' and intensity > 0.5:
            response = response.replace('.', '?')
        elif style == 'enthusiastic' and intensity > 0.7:
            response = response.replace('.', '!')
            response = response.replace('!', '!!')
        elif style == 'minimal':
            response = response.replace('!', '.')
        
        return response
    
    def get_current_modulation(self) -> Optional[EmotionalModulation]:
        """Get current emotional modulation"""
        return self.current_modulation
    
    def get_modulation_for_emotion(self, emotion: str) -> Dict[str, Any]:
        """Get appropriate modulation settings for an emotion"""
        tone_data = self.tone_mappings.get(emotion, self.tone_mappings['neutral'])
        pace = self.pace_mappings.get(emotion, ResponsePace.NORMAL)
        structure = self.structure_mappings.get(emotion, ResponseStructure.CONVERSATIONAL)
        
        return {
            'tone': tone_data['tone'].value,
            'pace': pace.value,
            'structure': structure.value,
            'modifiers': tone_data.get('modifiers', []),
            'sample_phrases': tone_data.get('phrases', [])
        }
    
    def load_modulation_history(self):
        """Load modulation history from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                
            for mod_data in data.get('modulations', []):
                modulation = EmotionalModulation(
                    tone=EmotionalTone(mod_data['tone']),
                    pace=ResponsePace(mod_data['pace']),
                    structure=ResponseStructure(mod_data['structure']),
                    intensity=mod_data['intensity'],
                    confidence=mod_data['confidence'],
                    reasoning=mod_data['reasoning'],
                    timestamp=mod_data['timestamp']
                )
                self.modulation_history.append(modulation)
                
            print(f"[EmotionResponseModulator] 📄 Loaded {len(self.modulation_history)} modulations")
            
        except FileNotFoundError:
            print(f"[EmotionResponseModulator] 📄 No modulation history found")
        except Exception as e:
            print(f"[EmotionResponseModulator] ❌ Error loading modulation history: {e}")
    
    def save_modulation_history(self):
        """Save modulation history to file"""
        try:
            data = {
                'modulations': [asdict(mod) for mod in self.modulation_history],
                'last_updated': datetime.now().isoformat(),
                'total_modulations': len(self.modulation_history)
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"[EmotionResponseModulator] ❌ Error saving modulation history: {e}")
    
    def get_modulation_stats(self) -> Dict[str, Any]:
        """Get modulation statistics"""
        if not self.modulation_history:
            return {'total_modulations': 0, 'common_tones': [], 'average_intensity': 0}
        
        # Count tone usage
        tone_counts = {}
        total_intensity = 0
        
        for mod in self.modulation_history:
            tone = mod.tone.value
            tone_counts[tone] = tone_counts.get(tone, 0) + 1
            total_intensity += mod.intensity
        
        return {
            'total_modulations': len(self.modulation_history),
            'common_tones': sorted(tone_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'average_intensity': total_intensity / len(self.modulation_history),
            'current_modulation': asdict(self.current_modulation) if self.current_modulation else None
        }

# Global instance
emotion_response_modulator = EmotionResponseModulator()

def modulate_response_with_emotion(response: str, emotional_state: Dict[str, Any], context: str, user_context: Optional[Dict[str, Any]] = None) -> str:
    """Modulate response based on emotional state - main API function"""
    modulation = emotion_response_modulator.determine_emotional_modulation(
        emotional_state, context, user_context
    )
    return emotion_response_modulator.apply_modulation_to_response(response, modulation)

def get_emotional_modulation_for_context(emotional_state: Dict[str, Any], context: str) -> Dict[str, Any]:
    """Get emotional modulation settings for context"""
    modulation = emotion_response_modulator.determine_emotional_modulation(
        emotional_state, context
    )
    return asdict(modulation)

def get_modulation_for_emotion(emotion: str) -> Dict[str, Any]:
    """Get modulation settings for specific emotion"""
    return emotion_response_modulator.get_modulation_for_emotion(emotion)

def get_current_emotional_modulation() -> Optional[Dict[str, Any]]:
    """Get current emotional modulation"""
    current = emotion_response_modulator.get_current_modulation()
    return asdict(current) if current else None

def get_modulation_statistics() -> Dict[str, Any]:
    """Get modulation system statistics"""
    return emotion_response_modulator.get_modulation_stats()