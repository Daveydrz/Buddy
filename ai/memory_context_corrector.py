"""
Memory Context Corrector - System to fix Whisper errors using belief history
Enhanced with contextual repair capabilities and belief integration
"""

import json
import re
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class CorrectionEntry:
    """Represents a correction made to speech recognition"""
    original_text: str
    corrected_text: str
    correction_type: str
    confidence: float
    timestamp: str
    belief_context: Optional[str] = None
    frequency_count: int = 1

class MemoryContextCorrector:
    """Fix Whisper errors using belief history and contextual understanding"""
    
    def __init__(self, save_path: str = "memory_corrections.json"):
        self.save_path = save_path
        self.corrections: Dict[str, CorrectionEntry] = {}
        self.belief_contexts: Dict[str, List[str]] = {}
        self.common_errors: Dict[str, str] = {}
        self.load_corrections()
        self._initialize_common_errors()
    
    def _initialize_common_errors(self):
        """Initialize common Whisper transcription errors"""
        self.common_errors = {
            # Names/People
            "niece": "knees",
            "david": "davey",
            "dave": "davey",
            "davies": "davey",
            "davis": "davey",
            
            # Technical terms
            "phyton": "python",
            "pyton": "python",
            "pie-thon": "python",
            "java script": "javascript",
            "node js": "nodejs",
            "react js": "reactjs",
            "gpt": "GPT",
            "ai": "AI",
            "ml": "machine learning",
            
            # Brisbane/Australian terms
            "brisbane": "Brisbane",
            "queensland": "Queensland",
            "birtinya": "Birtinya",
            "sunshine coast": "Sunshine Coast",
            "aussie": "Australian",
            
            # Common homophones
            "there": "their",
            "your": "you're",
            "its": "it's",
            "to": "too",
            "for": "four",
            "two": "too",
            "here": "hear",
            "right": "write",
            "new": "knew",
            "no": "know",
            "buy": "by",
            "sea": "see",
            "meet": "meat",
            "week": "weak",
            "break": "brake",
            "peace": "piece",
            "plane": "plain",
            "rain": "reign",
            "sale": "sail",
            "tail": "tale",
            "wait": "weight",
            "wood": "would",
            "wore": "war",
            "hole": "whole",
            "hour": "our",
            "made": "maid",
            "male": "mail",
            "night": "knight",
            "pair": "pear",
            "read": "red",
            "road": "rode",
            "scene": "seen",
            "some": "sum",
            "son": "sun",
            "steal": "steel",
            "threw": "through",
            "tire": "tier",
            "way": "weigh",
            "where": "wear",
            "which": "witch",
            "wind": "wined",
            "write": "right",
            "wrote": "rote",
        }
    
    def load_corrections(self):
        """Load existing corrections from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
                self.corrections = {
                    k: CorrectionEntry(**v) for k, v in data.get('corrections', {}).items()
                }
                self.belief_contexts = data.get('belief_contexts', {})
                self.common_errors.update(data.get('common_errors', {}))
        except FileNotFoundError:
            print(f"[MemoryContextCorrector] 📄 No existing corrections found")
        except Exception as e:
            print(f"[MemoryContextCorrector] ❌ Error loading corrections: {e}")
    
    def save_corrections(self):
        """Save corrections to file"""
        try:
            data = {
                'corrections': {k: asdict(v) for k, v in self.corrections.items()},
                'belief_contexts': self.belief_contexts,
                'common_errors': self.common_errors,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[MemoryContextCorrector] ❌ Error saving corrections: {e}")
    
    def extract_belief_context(self, user_id: str) -> List[str]:
        """Extract relevant belief context for correction"""
        try:
            from ai.belief_analyzer import get_active_belief_contradictions
            
            # Get user's beliefs for context
            beliefs = get_active_belief_contradictions(user_id)
            context_terms = []
            
            for belief in beliefs:
                if isinstance(belief, dict):
                    content = belief.get('content', '')
                    # Extract key terms from beliefs
                    terms = re.findall(r'\b[A-Za-z]{3,}\b', content.lower())
                    context_terms.extend(terms)
            
            return list(set(context_terms))
        except Exception as e:
            print(f"[MemoryContextCorrector] ⚠️ Error extracting belief context: {e}")
            return []
    
    def correct_with_belief_context(self, text: str, user_id: str) -> Tuple[str, List[str]]:
        """Correct text using belief context and learned patterns"""
        if not text or not text.strip():
            return text, []
        
        corrections_made = []
        corrected_text = text
        
        # Get belief context for user
        belief_context = self.extract_belief_context(user_id)
        
        # Apply learned corrections first
        for original, correction_entry in self.corrections.items():
            if original.lower() in corrected_text.lower():
                # Check if correction is contextually appropriate
                if self._is_contextually_appropriate(original, correction_entry.corrected_text, belief_context):
                    corrected_text = re.sub(
                        r'\b' + re.escape(original) + r'\b',
                        correction_entry.corrected_text,
                        corrected_text,
                        flags=re.IGNORECASE
                    )
                    corrections_made.append(f"{original} → {correction_entry.corrected_text}")
                    
                    # Update frequency count
                    correction_entry.frequency_count += 1
        
        # Apply common error corrections
        for error, correction in self.common_errors.items():
            if error.lower() in corrected_text.lower():
                # Check belief context compatibility
                if self._is_contextually_appropriate(error, correction, belief_context):
                    pattern = r'\b' + re.escape(error) + r'\b'
                    if re.search(pattern, corrected_text, re.IGNORECASE):
                        corrected_text = re.sub(pattern, correction, corrected_text, flags=re.IGNORECASE)
                        corrections_made.append(f"{error} → {correction}")
        
        # Apply belief-based corrections
        corrected_text, belief_corrections = self._apply_belief_corrections(
            corrected_text, belief_context
        )
        corrections_made.extend(belief_corrections)
        
        return corrected_text, corrections_made
    
    def _is_contextually_appropriate(self, original: str, correction: str, belief_context: List[str]) -> bool:
        """Check if correction is appropriate given belief context"""
        # If no belief context, apply correction
        if not belief_context:
            return True
        
        # Check if correction terms appear in belief context
        correction_terms = correction.lower().split()
        context_terms = [term.lower() for term in belief_context]
        
        # If any correction term is in belief context, it's appropriate
        for term in correction_terms:
            if term in context_terms:
                return True
        
        # For common corrections, default to appropriate
        if original.lower() in self.common_errors:
            return True
        
        return False
    
    def _apply_belief_corrections(self, text: str, belief_context: List[str]) -> Tuple[str, List[str]]:
        """Apply corrections based on belief context"""
        corrections_made = []
        corrected_text = text
        
        # Look for terms that are similar to belief context terms
        words = text.split()
        
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if len(clean_word) < 3:
                continue
            
            # Find closest match in belief context
            best_match = None
            best_score = 0
            
            for context_term in belief_context:
                if len(context_term) < 3:
                    continue
                
                # Simple similarity check
                similarity = self._calculate_similarity(clean_word, context_term.lower())
                if similarity > 0.7 and similarity > best_score:
                    best_match = context_term
                    best_score = similarity
            
            if best_match and best_score > 0.8:
                # Preserve original case and punctuation
                original_case = self._preserve_case(word, best_match)
                words[i] = original_case
                corrections_made.append(f"{word} → {original_case}")
        
        return ' '.join(words), corrections_made
    
    def _calculate_similarity(self, word1: str, word2: str) -> float:
        """Calculate simple similarity between two words"""
        if not word1 or not word2:
            return 0.0
        
        # Simple character-based similarity
        common_chars = set(word1) & set(word2)
        total_chars = set(word1) | set(word2)
        
        if not total_chars:
            return 0.0
        
        return len(common_chars) / len(total_chars)
    
    def _preserve_case(self, original: str, replacement: str) -> str:
        """Preserve original case pattern in replacement"""
        if not original or not replacement:
            return replacement
        
        # If original is all uppercase
        if original.isupper():
            return replacement.upper()
        
        # If original is title case
        if original.istitle():
            return replacement.capitalize()
        
        # If original starts with uppercase
        if original[0].isupper():
            return replacement.capitalize()
        
        # Default to lowercase
        return replacement.lower()
    
    def learn_correction(self, original: str, corrected: str, user_id: str, confidence: float = 0.8):
        """Learn a new correction pattern"""
        if not original or not corrected or original == corrected:
            return
        
        key = original.lower()
        
        if key in self.corrections:
            # Update existing correction
            self.corrections[key].frequency_count += 1
            self.corrections[key].confidence = max(self.corrections[key].confidence, confidence)
        else:
            # Add new correction
            self.corrections[key] = CorrectionEntry(
                original_text=original,
                corrected_text=corrected,
                correction_type="learned",
                confidence=confidence,
                timestamp=datetime.now().isoformat(),
                belief_context=user_id
            )
        
        # Update belief contexts
        if user_id not in self.belief_contexts:
            self.belief_contexts[user_id] = []
        
        context_terms = re.findall(r'\b[A-Za-z]{3,}\b', corrected.lower())
        self.belief_contexts[user_id].extend(context_terms)
        self.belief_contexts[user_id] = list(set(self.belief_contexts[user_id]))
        
        self.save_corrections()
        print(f"[MemoryContextCorrector] 🧠 Learned correction: {original} → {corrected}")
    
    def get_correction_stats(self) -> Dict[str, Any]:
        """Get statistics about corrections"""
        total_corrections = len(self.corrections)
        learned_corrections = sum(1 for c in self.corrections.values() if c.correction_type == "learned")
        total_uses = sum(c.frequency_count for c in self.corrections.values())
        
        return {
            'total_corrections': total_corrections,
            'learned_corrections': learned_corrections,
            'common_errors': len(self.common_errors),
            'total_uses': total_uses,
            'belief_contexts': len(self.belief_contexts),
            'most_used': max(self.corrections.items(), key=lambda x: x[1].frequency_count) if self.corrections else None
        }
    
    def suggest_corrections(self, text: str, user_id: str, threshold: float = 0.6) -> List[Dict[str, Any]]:
        """Suggest potential corrections without applying them"""
        suggestions = []
        
        # Get belief context
        belief_context = self.extract_belief_context(user_id)
        
        words = text.split()
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if len(clean_word) < 3:
                continue
            
            # Check against learned corrections
            for original, correction_entry in self.corrections.items():
                if self._calculate_similarity(clean_word, original) > threshold:
                    suggestions.append({
                        'original': word,
                        'suggested': correction_entry.corrected_text,
                        'confidence': correction_entry.confidence,
                        'type': 'learned',
                        'frequency': correction_entry.frequency_count
                    })
            
            # Check against common errors
            for error, correction in self.common_errors.items():
                if self._calculate_similarity(clean_word, error) > threshold:
                    suggestions.append({
                        'original': word,
                        'suggested': correction,
                        'confidence': 0.7,
                        'type': 'common_error',
                        'frequency': 1
                    })
        
        # Sort by confidence and frequency
        suggestions.sort(key=lambda x: (x['confidence'], x['frequency']), reverse=True)
        return suggestions

# Global instance
memory_context_corrector = MemoryContextCorrector()

def correct_speech_with_context(text: str, user_id: str) -> Tuple[str, List[str]]:
    """Correct speech using memory context - main API function"""
    return memory_context_corrector.correct_with_belief_context(text, user_id)

def learn_speech_correction(original: str, corrected: str, user_id: str, confidence: float = 0.8):
    """Learn a new speech correction"""
    memory_context_corrector.learn_correction(original, corrected, user_id, confidence)

def get_correction_suggestions(text: str, user_id: str, threshold: float = 0.6) -> List[Dict[str, Any]]:
    """Get correction suggestions without applying them"""
    return memory_context_corrector.suggest_corrections(text, user_id, threshold)

def get_correction_statistics() -> Dict[str, Any]:
    """Get correction system statistics"""
    return memory_context_corrector.get_correction_stats()