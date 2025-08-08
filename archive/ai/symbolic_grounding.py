"""
Symbolic Grounding - Sensory and Embodied Experience Mapping

This module adds sensory tags and embodied associations to abstract concepts,
grounding symbolic understanding in simulated sensory experiences. For example,
"rain" becomes associated with cold, dark, soft sound, and wet sensations.
"""

import json
import time
import os
import random
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import re

class SensoryModality(Enum):
    """Different sensory modalities for grounding"""
    VISUAL = "visual"
    AUDITORY = "auditory"
    TACTILE = "tactile"
    OLFACTORY = "olfactory"
    GUSTATORY = "gustatory"
    THERMAL = "thermal"
    PROPRIOCEPTIVE = "proprioceptive"  # Sense of body position/movement
    VESTIBULAR = "vestibular"         # Balance and spatial orientation
    INTEROCEPTIVE = "interoceptive"   # Internal bodily sensations

class GroundingStrength(Enum):
    """Strength of symbolic grounding"""
    WEAK = "weak"           # 0.1-0.3 - Abstract connection
    MODERATE = "moderate"   # 0.3-0.6 - Clear association
    STRONG = "strong"       # 0.6-0.8 - Vivid connection
    EMBODIED = "embodied"   # 0.8-1.0 - Deeply felt association

@dataclass
class SensoryAssociation:
    """Association between a concept and a sensory experience"""
    concept: str
    modality: SensoryModality
    sensation: str
    strength: float  # 0.0 to 1.0
    grounding_strength: GroundingStrength
    context: List[str]  # Contexts where this association applies
    emotional_valence: float  # -1.0 (negative) to 1.0 (positive)
    intensity: float  # 0.0 to 1.0
    temporal_pattern: Optional[str]  # e.g., "rhythmic", "sustained", "pulsing"
    spatial_qualities: List[str]  # e.g., "expansive", "localized", "directional"

@dataclass
class ConceptGrounding:
    """Complete sensory grounding for a concept"""
    concept: str
    primary_modality: SensoryModality
    sensory_associations: List[SensoryAssociation]
    embodied_metaphors: List[str]
    experiential_tags: List[str]
    grounding_confidence: float
    last_updated: datetime
    usage_count: int
    contextual_variations: Dict[str, List[SensoryAssociation]]

@dataclass
class GroundingPattern:
    """Pattern in how concepts get grounded"""
    pattern_id: str
    concept_categories: List[str]
    common_modalities: List[SensoryModality]
    typical_associations: List[str]
    strength_distribution: Dict[GroundingStrength, int]
    contextual_factors: List[str]

class SymbolicGroundingSystem:
    """Manages symbolic grounding in sensory and embodied experience"""
    
    def __init__(self, save_path: str = "ai_symbolic_grounding.json"):
        self.save_path = save_path
        self.concept_groundings: Dict[str, ConceptGrounding] = {}
        self.grounding_patterns: List[GroundingPattern] = []
        self.running = False
        
        # Predefined sensory vocabularies for different modalities
        self.sensory_vocabularies = {
            SensoryModality.VISUAL: {
                "colors": ["bright", "dark", "vibrant", "muted", "warm", "cool", "saturated", "pale"],
                "textures": ["smooth", "rough", "glossy", "matte", "crystalline", "fuzzy", "sharp", "soft"],
                "patterns": ["flowing", "geometric", "organic", "symmetrical", "chaotic", "rhythmic"],
                "lighting": ["luminous", "shadowy", "glowing", "sparkling", "dim", "brilliant", "ethereal"],
                "movement": ["flowing", "jerky", "graceful", "turbulent", "steady", "oscillating"]
            },
            SensoryModality.AUDITORY: {
                "tones": ["melodious", "harsh", "resonant", "muffled", "clear", "distorted", "pure"],
                "rhythms": ["rhythmic", "arrhythmic", "syncopated", "steady", "pulsing", "irregular"],
                "volumes": ["whispered", "loud", "thunderous", "gentle", "piercing", "subtle"],
                "textures": ["smooth", "gritty", "layered", "thin", "rich", "hollow", "full"]
            },
            SensoryModality.TACTILE: {
                "textures": ["smooth", "rough", "soft", "hard", "sticky", "slippery", "bumpy", "velvety"],
                "temperatures": ["warm", "cool", "hot", "cold", "burning", "freezing", "neutral"],
                "pressures": ["light", "firm", "heavy", "gentle", "crushing", "caressing", "sharp"],
                "movements": ["flowing", "jabbing", "stroking", "pressing", "vibrating", "static"]
            },
            SensoryModality.THERMAL: {
                "sensations": ["warming", "cooling", "burning", "freezing", "tingling", "numbing"],
                "patterns": ["steady", "fluctuating", "gradual", "sudden", "radiating", "localized"]
            },
            SensoryModality.OLFACTORY: {
                "qualities": ["fresh", "stale", "sweet", "acrid", "earthy", "floral", "musky", "sharp"],
                "intensity": ["subtle", "strong", "overwhelming", "faint", "penetrating", "lingering"]
            },
            SensoryModality.GUSTATORY: {
                "tastes": ["sweet", "bitter", "sour", "salty", "umami", "metallic", "bland", "complex"],
                "textures": ["smooth", "gritty", "creamy", "crisp", "chewy", "liquid", "dry"]
            }
        }
        
        # Common grounding patterns
        self.grounding_templates = {
            "weather": {
                SensoryModality.VISUAL: ["sky colors", "light patterns", "movement"],
                SensoryModality.AUDITORY: ["wind sounds", "precipitation sounds"],
                SensoryModality.TACTILE: ["temperature", "humidity", "pressure"],
                SensoryModality.THERMAL: ["temperature changes"]
            },
            "emotions": {
                SensoryModality.VISUAL: ["brightness", "colors", "expansion/contraction"],
                SensoryModality.TACTILE: ["pressure", "texture", "temperature"],
                SensoryModality.THERMAL: ["warmth", "coolness"],
                SensoryModality.PROPRIOCEPTIVE: ["posture changes", "energy levels"]
            },
            "technology": {
                SensoryModality.VISUAL: ["screens", "lights", "interfaces"],
                SensoryModality.AUDITORY: ["electronic sounds", "beeps", "humming"],
                SensoryModality.TACTILE: ["smooth surfaces", "buttons", "vibrations"]
            },
            "nature": {
                SensoryModality.VISUAL: ["organic patterns", "natural colors", "movement"],
                SensoryModality.AUDITORY: ["natural sounds", "rustling", "flowing"],
                SensoryModality.OLFACTORY: ["fresh air", "earth", "plants"],
                SensoryModality.TACTILE: ["natural textures", "temperature variations"]
            }
        }
        
        self._load_grounding_data()
        self._initialize_basic_groundings()
        print(f"[SymbolicGrounding] 🌐 Initialized with {len(self.concept_groundings)} grounded concepts")
    
    def start(self):
        """Start the symbolic grounding system"""
        self.running = True
        print("[SymbolicGrounding] 🌐 Symbolic grounding system started")
    
    def stop(self):
        """Stop the symbolic grounding system"""
        self.running = False
        self._save_grounding_data()
        print("[SymbolicGrounding] 🌐 Symbolic grounding system stopped")
    
    def ground_concept(self, concept: str, context: Dict[str, Any] = None) -> ConceptGrounding:
        """Ground a concept in sensory experience"""
        if not self.running:
            return None
            
        concept_key = concept.lower().strip()
        
        # Check if already grounded
        if concept_key in self.concept_groundings:
            grounding = self.concept_groundings[concept_key]
            grounding.usage_count += 1
            return grounding
        
        try:
            print(f"[SymbolicGrounding] 🌐 Grounding concept: {concept}")
            
            # Determine primary modality based on concept category
            primary_modality = self._determine_primary_modality(concept, context or {})
            
            # Generate sensory associations
            associations = self._generate_sensory_associations(concept, primary_modality, context or {})
            
            # Generate embodied metaphors
            metaphors = self._generate_embodied_metaphors(concept, associations)
            
            # Generate experiential tags
            tags = self._generate_experiential_tags(concept, associations)
            
            # Calculate grounding confidence
            confidence = self._calculate_grounding_confidence(associations)
            
            # Create concept grounding
            grounding = ConceptGrounding(
                concept=concept,
                primary_modality=primary_modality,
                sensory_associations=associations,
                embodied_metaphors=metaphors,
                experiential_tags=tags,
                grounding_confidence=confidence,
                last_updated=datetime.now(),
                usage_count=1,
                contextual_variations={}
            )
            
            self.concept_groundings[concept_key] = grounding
            
            print(f"[SymbolicGrounding] ✅ Grounded '{concept}' with {len(associations)} sensory associations")
            
            # Save periodically
            if len(self.concept_groundings) % 25 == 0:
                self._save_grounding_data()
            
            return grounding
            
        except Exception as e:
            print(f"[SymbolicGrounding] ❌ Error grounding concept: {e}")
            return None
    
    def get_sensory_associations(self, concept: str, modality: SensoryModality = None) -> List[SensoryAssociation]:
        """Get sensory associations for a concept"""
        concept_key = concept.lower().strip()
        
        if concept_key not in self.concept_groundings:
            # Try to ground it first
            grounding = self.ground_concept(concept)
            if not grounding:
                return []
        
        grounding = self.concept_groundings[concept_key]
        
        if modality:
            return [assoc for assoc in grounding.sensory_associations if assoc.modality == modality]
        else:
            return grounding.sensory_associations
    
    def get_embodied_description(self, concept: str, intensity: float = 0.7) -> str:
        """Get an embodied description of a concept"""
        concept_key = concept.lower().strip()
        
        if concept_key not in self.concept_groundings:
            grounding = self.ground_concept(concept)
            if not grounding:
                return f"the abstract concept of {concept}"
        else:
            grounding = self.concept_groundings[concept_key]
        
        # Select associations based on intensity
        relevant_associations = [
            assoc for assoc in grounding.sensory_associations 
            if assoc.strength >= intensity - 0.2
        ]
        
        if not relevant_associations:
            relevant_associations = grounding.sensory_associations[:2]  # Take strongest ones
        
        # Build embodied description
        description_parts = []
        
        # Primary sensory impression
        if relevant_associations:
            primary = relevant_associations[0]
            description_parts.append(f"the {primary.sensation} sensation")
        
        # Additional modalities
        modalities_used = set()
        for assoc in relevant_associations[:3]:  # Top 3 associations
            if assoc.modality not in modalities_used:
                description_parts.append(f"{assoc.modality.value}ly {assoc.sensation}")
                modalities_used.add(assoc.modality)
        
        # Combine with embodied metaphors
        if grounding.embodied_metaphors:
            metaphor = random.choice(grounding.embodied_metaphors)
            description_parts.append(f"like {metaphor}")
        
        return " and ".join(description_parts)
    
    def enhance_text_with_grounding(self, text: str, enhancement_level: float = 0.5) -> str:
        """Enhance text by adding sensory grounding to abstract concepts"""
        words = re.findall(r'\b\w+\b', text.lower())
        enhanced_text = text
        
        # Find concepts that could be grounded
        concepts_to_enhance = []
        for word in words:
            if len(word) > 4 and word in self.concept_groundings:
                concepts_to_enhance.append(word)
        
        # Enhance some concepts based on enhancement level
        num_to_enhance = int(len(concepts_to_enhance) * enhancement_level)
        selected_concepts = random.sample(concepts_to_enhance, min(num_to_enhance, len(concepts_to_enhance)))
        
        for concept in selected_concepts:
            grounding = self.concept_groundings[concept]
            if grounding.sensory_associations:
                strongest_association = max(grounding.sensory_associations, key=lambda a: a.strength)
                enhancement = f" ({strongest_association.sensation})"
                
                # Replace first occurrence
                pattern = re.compile(re.escape(concept), re.IGNORECASE)
                enhanced_text = pattern.sub(concept + enhancement, enhanced_text, count=1)
        
        return enhanced_text
    
    def _determine_primary_modality(self, concept: str, context: Dict[str, Any]) -> SensoryModality:
        """Determine the primary sensory modality for a concept"""
        concept_lower = concept.lower()
        
        # Context-based determination
        if context.get("visual_context"):
            return SensoryModality.VISUAL
        elif context.get("audio_context"):
            return SensoryModality.AUDITORY
        
        # Concept-based heuristics
        visual_keywords = ["color", "light", "see", "bright", "dark", "visual", "appearance", "look"]
        auditory_keywords = ["sound", "hear", "music", "noise", "voice", "audio", "listen"]
        tactile_keywords = ["touch", "feel", "texture", "soft", "hard", "smooth", "rough"]
        thermal_keywords = ["temperature", "hot", "cold", "warm", "cool", "heat"]
        
        if any(keyword in concept_lower for keyword in visual_keywords):
            return SensoryModality.VISUAL
        elif any(keyword in concept_lower for keyword in auditory_keywords):
            return SensoryModality.AUDITORY
        elif any(keyword in concept_lower for keyword in tactile_keywords):
            return SensoryModality.TACTILE
        elif any(keyword in concept_lower for keyword in thermal_keywords):
            return SensoryModality.THERMAL
        
        # Category-based determination
        category = self._categorize_concept(concept)
        if category in self.grounding_templates:
            template = self.grounding_templates[category]
            return list(template.keys())[0]  # Primary modality for category
        
        # Default to visual for most abstract concepts
        return SensoryModality.VISUAL
    
    def _generate_sensory_associations(self, concept: str, primary_modality: SensoryModality, context: Dict[str, Any]) -> List[SensoryAssociation]:
        """Generate sensory associations for a concept"""
        associations = []
        concept_lower = concept.lower()
        
        # Determine concept category for template matching
        category = self._categorize_concept(concept)
        
        # Generate primary modality association
        primary_association = self._create_association(concept, primary_modality, context, strength=0.8)
        if primary_association:
            associations.append(primary_association)
        
        # Generate secondary associations
        if category in self.grounding_templates:
            template = self.grounding_templates[category]
            for modality in list(template.keys())[1:3]:  # Next 2 modalities
                association = self._create_association(concept, modality, context, strength=0.6)
                if association:
                    associations.append(association)
        else:
            # Generate general associations
            secondary_modalities = [SensoryModality.TACTILE, SensoryModality.THERMAL, SensoryModality.AUDITORY]
            for modality in secondary_modalities[:2]:
                if modality != primary_modality:
                    association = self._create_association(concept, modality, context, strength=0.5)
                    if association:
                        associations.append(association)
        
        return associations
    
    def _create_association(self, concept: str, modality: SensoryModality, context: Dict[str, Any], strength: float) -> SensoryAssociation:
        """Create a sensory association for a concept and modality"""
        try:
            concept_lower = concept.lower()
            
            # Get vocabulary for this modality
            vocabulary = self.sensory_vocabularies.get(modality, {})
            if not vocabulary:
                return None
            
            # Select appropriate sensation based on concept
            sensation = self._select_sensation(concept, modality, vocabulary, context)
            if not sensation:
                return None
            
            # Determine grounding strength category
            grounding_strength = self._categorize_grounding_strength(strength)
            
            # Calculate emotional valence
            valence = self._calculate_emotional_valence(concept, sensation)
            
            # Generate contextual information
            contexts = self._generate_contexts(concept, modality)
            spatial_qualities = self._generate_spatial_qualities(concept, modality)
            temporal_pattern = self._generate_temporal_pattern(concept, modality)
            
            association = SensoryAssociation(
                concept=concept,
                modality=modality,
                sensation=sensation,
                strength=strength,
                grounding_strength=grounding_strength,
                context=contexts,
                emotional_valence=valence,
                intensity=min(1.0, strength + random.uniform(-0.2, 0.2)),
                temporal_pattern=temporal_pattern,
                spatial_qualities=spatial_qualities
            )
            
            return association
            
        except Exception as e:
            print(f"[SymbolicGrounding] ❌ Error creating association: {e}")
            return None
    
    def _select_sensation(self, concept: str, modality: SensoryModality, vocabulary: Dict[str, List[str]], context: Dict[str, Any]) -> str:
        """Select appropriate sensation for concept and modality"""
        concept_lower = concept.lower()
        
        # Predefined mappings for common concepts
        concept_mappings = {
            "rain": {
                SensoryModality.VISUAL: "gray and flowing",
                SensoryModality.AUDITORY: "pattering",
                SensoryModality.TACTILE: "cool and wet",
                SensoryModality.THERMAL: "cooling"
            },
            "fire": {
                SensoryModality.VISUAL: "bright and dancing",
                SensoryModality.AUDITORY: "crackling",
                SensoryModality.TACTILE: "hot and intense",
                SensoryModality.THERMAL: "burning"
            },
            "joy": {
                SensoryModality.VISUAL: "bright and expanding",
                SensoryModality.TACTILE: "light and effervescent",
                SensoryModality.THERMAL: "warming"
            },
            "confusion": {
                SensoryModality.VISUAL: "foggy and unclear",
                SensoryModality.TACTILE: "tangled and sticky",
                SensoryModality.AUDITORY: "muffled"
            }
        }
        
        # Check for exact matches
        if concept_lower in concept_mappings and modality in concept_mappings[concept_lower]:
            return concept_mappings[concept_lower][modality]
        
        # Generate based on vocabulary and concept characteristics
        all_sensations = []
        for category, sensations in vocabulary.items():
            all_sensations.extend(sensations)
        
        if not all_sensations:
            return "undefined"
        
        # Simple selection based on concept characteristics
        if "happy" in concept_lower or "joy" in concept_lower or "good" in concept_lower:
            positive_sensations = ["bright", "warm", "smooth", "light", "clear", "melodious", "gentle"]
            matching = [s for s in all_sensations if any(pos in s for pos in positive_sensations)]
            if matching:
                return random.choice(matching)
        
        elif "sad" in concept_lower or "bad" in concept_lower or "dark" in concept_lower:
            negative_sensations = ["dark", "cold", "rough", "heavy", "muffled", "harsh", "sharp"]
            matching = [s for s in all_sensations if any(neg in s for neg in negative_sensations)]
            if matching:
                return random.choice(matching)
        
        # Default: random selection from appropriate category
        return random.choice(all_sensations)
    
    def _categorize_concept(self, concept: str) -> str:
        """Categorize a concept for template matching"""
        concept_lower = concept.lower()
        
        weather_terms = ["rain", "sun", "snow", "wind", "storm", "cloud", "weather"]
        emotion_terms = ["joy", "sad", "happy", "anger", "fear", "love", "hate", "emotion"]
        tech_terms = ["computer", "phone", "software", "digital", "tech", "internet", "code"]
        nature_terms = ["tree", "flower", "mountain", "river", "animal", "forest", "nature"]
        
        if any(term in concept_lower for term in weather_terms):
            return "weather"
        elif any(term in concept_lower for term in emotion_terms):
            return "emotions"
        elif any(term in concept_lower for term in tech_terms):
            return "technology"
        elif any(term in concept_lower for term in nature_terms):
            return "nature"
        else:
            return "abstract"
    
    def _categorize_grounding_strength(self, strength: float) -> GroundingStrength:
        """Categorize numerical strength into grounding strength enum"""
        if strength >= 0.8:
            return GroundingStrength.EMBODIED
        elif strength >= 0.6:
            return GroundingStrength.STRONG
        elif strength >= 0.3:
            return GroundingStrength.MODERATE
        else:
            return GroundingStrength.WEAK
    
    def _calculate_emotional_valence(self, concept: str, sensation: str) -> float:
        """Calculate emotional valence of a concept-sensation pairing"""
        concept_lower = concept.lower()
        sensation_lower = sensation.lower()
        
        positive_indicators = ["bright", "warm", "smooth", "gentle", "clear", "light", "sweet", "fresh"]
        negative_indicators = ["dark", "cold", "rough", "harsh", "sharp", "heavy", "bitter", "stale"]
        
        positive_score = sum(1 for indicator in positive_indicators if indicator in concept_lower or indicator in sensation_lower)
        negative_score = sum(1 for indicator in negative_indicators if indicator in concept_lower or indicator in sensation_lower)
        
        if positive_score > negative_score:
            return min(1.0, positive_score * 0.3)
        elif negative_score > positive_score:
            return max(-1.0, -negative_score * 0.3)
        else:
            return 0.0
    
    def _generate_contexts(self, concept: str, modality: SensoryModality) -> List[str]:
        """Generate contexts where this association applies"""
        contexts = ["general"]
        
        concept_lower = concept.lower()
        
        if "work" in concept_lower or "professional" in concept_lower:
            contexts.append("professional")
        if "personal" in concept_lower or "private" in concept_lower:
            contexts.append("personal")
        if "creative" in concept_lower or "art" in concept_lower:
            contexts.append("creative")
        
        return contexts
    
    def _generate_spatial_qualities(self, concept: str, modality: SensoryModality) -> List[str]:
        """Generate spatial qualities for the association"""
        concept_lower = concept.lower()
        
        if "large" in concept_lower or "big" in concept_lower or "vast" in concept_lower:
            return ["expansive", "encompassing"]
        elif "small" in concept_lower or "tiny" in concept_lower or "local" in concept_lower:
            return ["localized", "concentrated"]
        elif "flow" in concept_lower or "move" in concept_lower:
            return ["directional", "flowing"]
        else:
            return ["diffuse"]
    
    def _generate_temporal_pattern(self, concept: str, modality: SensoryModality) -> Optional[str]:
        """Generate temporal pattern for the association"""
        concept_lower = concept.lower()
        
        if "rhythm" in concept_lower or "beat" in concept_lower:
            return "rhythmic"
        elif "constant" in concept_lower or "steady" in concept_lower:
            return "sustained"
        elif "pulse" in concept_lower or "throb" in concept_lower:
            return "pulsing"
        elif "sudden" in concept_lower or "quick" in concept_lower:
            return "sudden"
        else:
            return None
    
    def _generate_embodied_metaphors(self, concept: str, associations: List[SensoryAssociation]) -> List[str]:
        """Generate embodied metaphors for a concept"""
        metaphors = []
        
        # Create metaphors based on strongest sensory associations
        for association in associations[:2]:  # Top 2 associations
            if association.modality == SensoryModality.TACTILE:
                metaphors.append(f"a {association.sensation} touch")
            elif association.modality == SensoryModality.VISUAL:
                metaphors.append(f"a {association.sensation} light")
            elif association.modality == SensoryModality.AUDITORY:
                metaphors.append(f"a {association.sensation} sound")
            elif association.modality == SensoryModality.THERMAL:
                metaphors.append(f"a {association.sensation} sensation")
        
        # Add concept-specific metaphors
        concept_lower = concept.lower()
        if "flow" in concept_lower:
            metaphors.append("water flowing through consciousness")
        elif "growth" in concept_lower:
            metaphors.append("a plant expanding in awareness")
        elif "understanding" in concept_lower:
            metaphors.append("light dawning in the mind")
        
        return metaphors[:3]  # Limit to 3 metaphors
    
    def _generate_experiential_tags(self, concept: str, associations: List[SensoryAssociation]) -> List[str]:
        """Generate experiential tags for a concept"""
        tags = []
        
        # Tags based on modalities involved
        modalities = [assoc.modality for assoc in associations]
        if SensoryModality.VISUAL in modalities:
            tags.append("visually_grounded")
        if SensoryModality.TACTILE in modalities:
            tags.append("tactilely_grounded")
        if SensoryModality.AUDITORY in modalities:
            tags.append("auditorily_grounded")
        
        # Tags based on emotional valence
        avg_valence = sum(assoc.emotional_valence for assoc in associations) / len(associations) if associations else 0
        if avg_valence > 0.3:
            tags.append("positive_experience")
        elif avg_valence < -0.3:
            tags.append("negative_experience")
        else:
            tags.append("neutral_experience")
        
        # Tags based on intensity
        avg_intensity = sum(assoc.intensity for assoc in associations) / len(associations) if associations else 0
        if avg_intensity > 0.7:
            tags.append("intense_experience")
        elif avg_intensity < 0.3:
            tags.append("subtle_experience")
        
        return tags
    
    def _calculate_grounding_confidence(self, associations: List[SensoryAssociation]) -> float:
        """Calculate confidence in the grounding"""
        if not associations:
            return 0.0
        
        # Base confidence on number and strength of associations
        base_confidence = min(1.0, len(associations) / 3.0)  # More associations = higher confidence
        strength_bonus = sum(assoc.strength for assoc in associations) / len(associations)
        
        confidence = (base_confidence + strength_bonus) / 2
        return min(1.0, confidence)
    
    def _initialize_basic_groundings(self):
        """Initialize basic concept groundings"""
        basic_concepts = {
            "rain": {
                "primary_modality": SensoryModality.AUDITORY,
                "associations": [
                    ("pattering softly", SensoryModality.AUDITORY, 0.9),
                    ("cool and wet", SensoryModality.TACTILE, 0.8),
                    ("gray and flowing", SensoryModality.VISUAL, 0.7),
                    ("cooling", SensoryModality.THERMAL, 0.6)
                ]
            },
            "fire": {
                "primary_modality": SensoryModality.VISUAL,
                "associations": [
                    ("bright and dancing", SensoryModality.VISUAL, 0.9),
                    ("crackling", SensoryModality.AUDITORY, 0.8),
                    ("hot and intense", SensoryModality.TACTILE, 0.8),
                    ("burning", SensoryModality.THERMAL, 0.9)
                ]
            },
            "music": {
                "primary_modality": SensoryModality.AUDITORY,
                "associations": [
                    ("melodious and flowing", SensoryModality.AUDITORY, 0.9),
                    ("rhythmic movement", SensoryModality.PROPRIOCEPTIVE, 0.7),
                    ("emotionally resonant", SensoryModality.INTEROCEPTIVE, 0.6)
                ]
            },
            "peace": {
                "primary_modality": SensoryModality.TACTILE,
                "associations": [
                    ("gentle and calm", SensoryModality.TACTILE, 0.8),
                    ("soft light", SensoryModality.VISUAL, 0.7),
                    ("quiet stillness", SensoryModality.AUDITORY, 0.7),
                    ("warm and settled", SensoryModality.THERMAL, 0.6)
                ]
            }
        }
        
        for concept, data in basic_concepts.items():
            if concept not in self.concept_groundings:
                associations = []
                for sensation, modality, strength in data["associations"]:
                    association = SensoryAssociation(
                        concept=concept,
                        modality=modality,
                        sensation=sensation,
                        strength=strength,
                        grounding_strength=self._categorize_grounding_strength(strength),
                        context=["general"],
                        emotional_valence=self._calculate_emotional_valence(concept, sensation),
                        intensity=strength,
                        temporal_pattern=None,
                        spatial_qualities=["diffuse"]
                    )
                    associations.append(association)
                
                grounding = ConceptGrounding(
                    concept=concept,
                    primary_modality=data["primary_modality"],
                    sensory_associations=associations,
                    embodied_metaphors=self._generate_embodied_metaphors(concept, associations),
                    experiential_tags=self._generate_experiential_tags(concept, associations),
                    grounding_confidence=self._calculate_grounding_confidence(associations),
                    last_updated=datetime.now(),
                    usage_count=0,
                    contextual_variations={}
                )
                
                self.concept_groundings[concept] = grounding
    
    def _save_grounding_data(self):
        """Save symbolic grounding data to file"""
        try:
            data = {
                "concept_groundings": {
                    concept: asdict(grounding) for concept, grounding in self.concept_groundings.items()
                },
                "grounding_patterns": [asdict(pattern) for pattern in self.grounding_patterns],
                "statistics": {
                    "total_concepts": len(self.concept_groundings),
                    "modality_distribution": {},
                    "average_confidence": sum(g.grounding_confidence for g in self.concept_groundings.values()) / max(1, len(self.concept_groundings)),
                    "most_used_concepts": sorted(
                        [(concept, grounding.usage_count) for concept, grounding in self.concept_groundings.items()],
                        key=lambda x: x[1], reverse=True
                    )[:5]
                },
                "last_updated": datetime.now().isoformat()
            }
            
            # Calculate modality distribution
            modality_counts = {}
            for grounding in self.concept_groundings.values():
                modality = grounding.primary_modality.value
                modality_counts[modality] = modality_counts.get(modality, 0) + 1
            data["statistics"]["modality_distribution"] = modality_counts
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"[SymbolicGrounding] ❌ Error saving grounding data: {e}")
    
    def _load_grounding_data(self):
        """Load symbolic grounding data from file"""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load concept groundings
                for concept, grounding_data in data.get("concept_groundings", {}).items():
                    grounding_data["last_updated"] = datetime.fromisoformat(grounding_data["last_updated"])
                    grounding_data["primary_modality"] = SensoryModality(grounding_data["primary_modality"])
                    
                    # Load sensory associations
                    associations = []
                    for assoc_data in grounding_data["sensory_associations"]:
                        assoc_data["modality"] = SensoryModality(assoc_data["modality"])
                        assoc_data["grounding_strength"] = GroundingStrength(assoc_data["grounding_strength"])
                        associations.append(SensoryAssociation(**assoc_data))
                    grounding_data["sensory_associations"] = associations
                    
                    self.concept_groundings[concept] = ConceptGrounding(**grounding_data)
                
                print(f"[SymbolicGrounding] ✅ Loaded {len(self.concept_groundings)} grounded concepts")
                
        except Exception as e:
            print(f"[SymbolicGrounding] ❌ Error loading grounding data: {e}")

# Global instance
symbolic_grounding = SymbolicGroundingSystem()