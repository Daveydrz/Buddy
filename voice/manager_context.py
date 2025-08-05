# voice/manager_context.py - Advanced context analysis with clustering intelligence
import time
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import os

from config import *

class AdvancedContextAnalyzer:
    """🧠 Advanced context analysis with clustering and behavioral intelligence"""
    
    def __init__(self):
        self.session_start = datetime.utcnow()
        self.login_user = 'Daveydrz'  # Current user from system
        self.session_interactions = []
        self.user_preferences = self.load_user_preferences()
        self.audio_quality_history = []
        self.recognition_confidence_history = []
        
        # ✅ ADVANCED CLUSTERING CONTEXT
        self.cluster_interaction_patterns = {}
        self.voice_transition_history = []
        self.environmental_adaptation_data = {}
        
        # ✅ BEHAVIORAL INTELLIGENCE
        self.conversation_flow_patterns = []
        self.user_adaptation_metrics = {}
        self.predictive_context_cache = {}
        
        # Smart patterns learning
        self.smart_patterns = {
            'common_phrases': [],
            'speaking_style': 'unknown',
            'audio_environment': 'unknown',
            'preferred_responses': [],
            'context_clues': [],
            'time_patterns': [],
            'interaction_rhythms': []
        }
        
        print(f"[AdvancedContext] 🧠 Advanced AI context initialized for: {self.login_user}")
    
    def load_user_preferences(self):
        """Load comprehensive user preferences with clustering support"""
        try:
            pref_file = f"user_preferences_{self.login_user.lower()}.json"
            if os.path.exists(pref_file):
                with open(pref_file, 'r') as f:
                    prefs = json.load(f)
                print(f"[AdvancedContext] 📋 Loaded preferences for {self.login_user}")
                return prefs
            else:
                # ✅ ENHANCED default preferences for Daveydrz
                default_prefs = {
                    'preferred_names': ['Daveydrz', 'Dave', 'David', 'Dawid'],
                    'typical_session_length': 30,
                    'audio_quality_preference': 'high',
                    'training_preference': 'background_learning',
                    'response_style': 'friendly_professional',
                    'voice_confidence_threshold': 0.75,
                    'context_awareness_level': 'high',
                    'anonymous_clustering': True,  # ✅ NEW
                    'passive_learning': True,      # ✅ NEW
                    'behavioral_adaptation': True, # ✅ NEW
                    'predictive_context': True,    # ✅ NEW
                    'personality_preferences': {
                        'tone': 'friendly_professional',
                        'humor': 'light_jokes',
                        'formality': 'casual',
                        'conversation_style': 'interactive',
                        'proactive_suggestions': True,
                        'context_memory': 'long_term'
                    },
                    'clustering_preferences': {
                        'auto_cluster_threshold': 0.6,
                        'max_anonymous_clusters': 10,
                        'cluster_merge_sensitivity': 0.8,
                        'spontaneous_introduction_detection': True
                    }
                }
                return default_prefs
        except Exception as e:
            print(f"[AdvancedContext] ⚠️ Could not load preferences: {e}")
            return {}
    
    def analyze_comprehensive_context(self, audio, text):
        """🎯 COMPREHENSIVE CONTEXT ANALYSIS with clustering intelligence"""
        context_analysis = {
            'audio_quality': self.assess_audio_quality_detailed(audio),
            'speaking_confidence': self.assess_speaking_confidence(text),
            'environmental_noise': self.assess_environment_advanced(audio),
            'text_clarity': self.assess_text_clarity(text),
            'likely_user': self.predict_likely_user_enhanced(text, audio),
            'session_context': self.analyze_session_context(),
            'clustering_context': self.analyze_clustering_context(audio, text),  # ✅ NEW
            'behavioral_context': self.analyze_behavioral_context(text),         # ✅ NEW
            'predictive_context': self.generate_predictive_context(audio, text), # ✅ NEW
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # ✅ ENHANCED: Store interaction for advanced learning
        self.session_interactions.append({
            'timestamp': datetime.utcnow().isoformat(),
            'text': text,
            'context_analysis': context_analysis,
            'interaction_id': len(self.session_interactions) + 1
        })
        
        # ✅ ADVANCED: Update behavioral patterns
        self._update_behavioral_patterns(context_analysis)
        
        # Keep only last 100 interactions
        if len(self.session_interactions) > 100:
            self.session_interactions = self.session_interactions[-100:]
        
        return context_analysis
    
    def analyze_clustering_context(self, audio, text):
        """🔍 CLUSTERING CONTEXT ANALYSIS"""
        try:
            # Import clustering functions
            from voice.database import anonymous_clusters, find_similar_clusters
            
            clustering_context = {
                'active_anonymous_clusters': len(anonymous_clusters),
                'cluster_interaction_count': sum(
                    cluster.get('sample_count', 0) for cluster in anonymous_clusters.values()
                ),
                'cluster_quality_distribution': self._analyze_cluster_quality(),
                'potential_cluster_merges': [],
                'cluster_aging_analysis': self._analyze_cluster_aging(),
                'voice_transition_probability': self._calculate_voice_transition_probability(),
                'clustering_confidence': 0.0
            }
            
            # ✅ ADVANCED: Analyze potential cluster relationships
            if audio is not None:
                try:
                    from voice.voice_models import dual_voice_model_manager
                    embedding = dual_voice_model_manager.generate_dual_embedding(audio)
                    
                    if embedding:
                        similar_clusters = find_similar_clusters(embedding, threshold=0.5)
                        clustering_context['potential_cluster_merges'] = similar_clusters
                        
                        if similar_clusters:
                            clustering_context['clustering_confidence'] = similar_clusters[0]['similarity']
                except:
                    pass
            
            return clustering_context
            
        except Exception as e:
            print(f"[AdvancedContext] ❌ Clustering context error: {e}")
            return {
                'active_anonymous_clusters': 0,
                'clustering_confidence': 0.0,
                'error': str(e)
            }
    
    def analyze_behavioral_context(self, text):
        """🎭 BEHAVIORAL CONTEXT ANALYSIS"""
        try:
            behavioral_context = {
                'conversation_style': self._detect_conversation_style(text),
                'formality_level': self._assess_formality_level(text),
                'emotional_tone': self._detect_emotional_tone(text),
                'interaction_intent': self._classify_interaction_intent(text),
                'user_state': self._assess_user_state(text),
                'communication_patterns': self._analyze_communication_patterns(text),
                'response_preferences': self._predict_response_preferences(text)
            }
            
            return behavioral_context
            
        except Exception as e:
            print(f"[AdvancedContext] ❌ Behavioral context error: {e}")
            return {'error': str(e)}
    
    def generate_predictive_context(self, audio, text):
        """🔮 PREDICTIVE CONTEXT GENERATION"""
        try:
            predictive_context = {
                'next_interaction_prediction': self._predict_next_interaction(),
                'session_duration_prediction': self._predict_session_duration(),
                'likely_follow_up_questions': self._predict_follow_up_questions(text),
                'context_continuity_score': self._calculate_context_continuity(),
                'proactive_suggestions': self._generate_proactive_suggestions(text),
                'adaptation_recommendations': self._generate_adaptation_recommendations()
            }
            
            return predictive_context
            
        except Exception as e:
            print(f"[AdvancedContext] ❌ Predictive context error: {e}")
            return {'error': str(e)}
    
    def _analyze_cluster_quality(self):
        """📊 ANALYZE CLUSTER QUALITY DISTRIBUTION"""
        try:
            from voice.database import anonymous_clusters
            
            if not anonymous_clusters:
                return {'distribution': 'no_clusters'}
            
            quality_scores = []
            for cluster in anonymous_clusters.values():
                cluster_quality = cluster.get('quality_scores', [0.5])
                avg_quality = sum(cluster_quality) / len(cluster_quality)
                quality_scores.append(avg_quality)
            
            if quality_scores:
                return {
                    'average_quality': sum(quality_scores) / len(quality_scores),
                    'quality_range': [min(quality_scores), max(quality_scores)],
                    'high_quality_clusters': len([q for q in quality_scores if q > 0.7]),
                    'low_quality_clusters': len([q for q in quality_scores if q < 0.4])
                }
            
            return {'distribution': 'no_quality_data'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_cluster_aging(self):
        """⏰ ANALYZE CLUSTER AGING PATTERNS"""
        try:
            from voice.database import anonymous_clusters
            
            if not anonymous_clusters:
                return {'aging_pattern': 'no_clusters'}
            
            current_time = datetime.utcnow()
            aging_data = []
            
            for cluster in anonymous_clusters.values():
                created_at = datetime.fromisoformat(cluster.get('created_at', current_time.isoformat()))
                age_minutes = (current_time - created_at).total_seconds() / 60
                aging_data.append({
                    'age_minutes': age_minutes,
                    'sample_count': cluster.get('sample_count', 0),
                    'activity_rate': cluster.get('sample_count', 0) / max(age_minutes, 1)
                })
            
            if aging_data:
                return {
                    'average_age_minutes': sum(d['age_minutes'] for d in aging_data) / len(aging_data),
                    'most_active_cluster_age': min(aging_data, key=lambda x: x['age_minutes'])['age_minutes'],
                    'stale_clusters': len([d for d in aging_data if d['age_minutes'] > 60]),
                    'active_clusters': len([d for d in aging_data if d['activity_rate'] > 0.1])
                }
            
            return {'aging_pattern': 'no_aging_data'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_voice_transition_probability(self):
        """🔄 CALCULATE VOICE TRANSITION PROBABILITY"""
        try:
            if len(self.voice_transition_history) < 2:
                return 0.0
            
            recent_transitions = self.voice_transition_history[-10:]
            transition_rate = len(set(t['from_user'] for t in recent_transitions)) / len(recent_transitions)
            
            return min(1.0, transition_rate)
            
        except Exception as e:
            return 0.0
    
    def _detect_conversation_style(self, text):
        """💬 DETECT CONVERSATION STYLE"""
        if not text:
            return 'unknown'
        
        text_lower = text.lower()
        
        # Formal indicators
        formal_indicators = ['please', 'thank you', 'could you', 'would you', 'may i']
        formal_score = sum(1 for indicator in formal_indicators if indicator in text_lower)
        
        # Casual indicators
        casual_indicators = ['hey', 'hi', 'yeah', 'cool', 'awesome', 'sure']
        casual_score = sum(1 for indicator in casual_indicators if indicator in text_lower)
        
        # Question vs statement
        is_question = text.strip().endswith('?') or any(word in text_lower for word in ['what', 'how', 'when', 'where', 'why', 'who'])
        
        if formal_score > casual_score:
            return 'formal'
        elif casual_score > formal_score:
            return 'casual'
        elif is_question:
            return 'inquisitive'
        else:
            return 'neutral'
    
    def _assess_formality_level(self, text):
        """🎩 ASSESS FORMALITY LEVEL"""
        if not text:
            return 'unknown'
        
        text_lower = text.lower()
        
        # Formal language markers
        formal_markers = ['please', 'thank you', 'could you', 'would you', 'may i', 'excuse me', 'pardon']
        informal_markers = ['hey', 'hi', 'yeah', 'yep', 'cool', 'awesome', 'sure thing']
        
        formal_count = sum(1 for marker in formal_markers if marker in text_lower)
        informal_count = sum(1 for marker in informal_markers if marker in text_lower)
        
        if formal_count > informal_count:
            return 'formal'
        elif informal_count > formal_count:
            return 'informal'
        else:
            return 'neutral'
    
    def _detect_emotional_tone(self, text):
        """😊 DETECT EMOTIONAL TONE"""
        if not text:
            return 'neutral'
        
        text_lower = text.lower()
        
        # Positive indicators
        positive_words = ['great', 'awesome', 'excellent', 'wonderful', 'amazing', 'fantastic', 'good', 'nice', 'love', 'like']
        positive_score = sum(1 for word in positive_words if word in text_lower)
        
        # Negative indicators
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'wrong', 'error', 'problem', 'issue']
        negative_score = sum(1 for word in negative_words if word in text_lower)
        
        # Neutral/informational
        neutral_words = ['what', 'how', 'when', 'where', 'information', 'help', 'please', 'thank']
        neutral_score = sum(1 for word in neutral_words if word in text_lower)
        
        if positive_score > negative_score and positive_score > neutral_score:
            return 'positive'
        elif negative_score > positive_score and negative_score > neutral_score:
            return 'negative'
        else:
            return 'neutral'
    
    def _classify_interaction_intent(self, text):
        """🎯 CLASSIFY INTERACTION INTENT"""
        if not text:
            return 'unknown'
        
        text_lower = text.lower()
        
        # Question intent
        if any(word in text_lower for word in ['what', 'how', 'when', 'where', 'why', 'who']) or text.strip().endswith('?'):
            return 'question'
        
        # Command intent
        if any(word in text_lower for word in ['please', 'can you', 'could you', 'would you', 'help me', 'show me']):
            return 'request'
        
        # Greeting intent
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            return 'greeting'
        
        # Information sharing
        if any(word in text_lower for word in ['my name is', 'i am', 'i\'m', 'this is', 'here is']):
            return 'information_sharing'
        
        # Conversational
        return 'conversational'
    
    def _assess_user_state(self, text):
        """🧘 ASSESS USER STATE"""
        if not text:
            return 'unknown'
        
        text_lower = text.lower()
        
        # Frustrated indicators
        frustrated_indicators = ['not working', 'wrong', 'error', 'problem', 'issue', 'frustrated', 'annoyed']
        if any(indicator in text_lower for indicator in frustrated_indicators):
            return 'frustrated'
        
        # Curious indicators
        curious_indicators = ['what', 'how', 'why', 'interesting', 'tell me', 'explain']
        if any(indicator in text_lower for indicator in curious_indicators):
            return 'curious'
        
        # Satisfied indicators
        satisfied_indicators = ['great', 'perfect', 'excellent', 'exactly', 'that\'s right']
        if any(indicator in text_lower for indicator in satisfied_indicators):
            return 'satisfied'
        
        return 'neutral'
    
    def _analyze_communication_patterns(self, text):
        """📈 ANALYZE COMMUNICATION PATTERNS"""
        if not text:
            return {'pattern': 'unknown'}
        
        patterns = {
            'word_count': len(text.split()),
            'sentence_count': len([s for s in text.split('.') if s.strip()]),
            'question_count': text.count('?'),
            'avg_word_length': sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0,
            'complexity_score': self._calculate_text_complexity(text)
        }
        
        return patterns
    
    def _calculate_text_complexity(self, text):
        """📊 CALCULATE TEXT COMPLEXITY"""
        if not text:
            return 0.0
        
        words = text.split()
        if not words:
            return 0.0
        
        # Simple complexity metrics
        avg_word_length = sum(len(word) for word in words) / len(words)
        long_words = len([word for word in words if len(word) > 6])
        long_word_ratio = long_words / len(words)
        
        complexity = (avg_word_length / 10) + long_word_ratio
        return min(1.0, complexity)
    
    def _predict_response_preferences(self, text):
        """🎯 PREDICT RESPONSE PREFERENCES"""
        preferences = {
            'response_length': 'medium',
            'formality_level': 'neutral',
            'detail_level': 'standard',
            'interaction_style': 'helpful'
        }
        
        if not text:
            return preferences
        
        text_lower = text.lower()
        
        # Predict response length preference
        if any(word in text_lower for word in ['quickly', 'brief', 'short', 'summary']):
            preferences['response_length'] = 'short'
        elif any(word in text_lower for word in ['detail', 'explain', 'elaborate', 'comprehensive']):
            preferences['response_length'] = 'long'
        
        # Predict formality preference
        if any(word in text_lower for word in ['please', 'thank you', 'could you', 'would you']):
            preferences['formality_level'] = 'formal'
        elif any(word in text_lower for word in ['hey', 'hi', 'yeah', 'cool']):
            preferences['formality_level'] = 'casual'
        
        return preferences
    
    def _predict_next_interaction(self):
        """🔮 PREDICT NEXT INTERACTION"""
        if len(self.session_interactions) < 2:
            return {'prediction': 'unknown', 'confidence': 0.0}
        
        # Analyze recent patterns
        recent_interactions = self.session_interactions[-5:]
        interaction_types = [self._classify_interaction_intent(interaction['text']) for interaction in recent_interactions]
        
        # Simple pattern prediction
        if len(set(interaction_types)) == 1:
            return {'prediction': interaction_types[0], 'confidence': 0.8}
        
        return {'prediction': 'conversational', 'confidence': 0.5}
    
    def _predict_session_duration(self):
        """⏱️ PREDICT SESSION DURATION"""
        current_duration = (datetime.utcnow() - self.session_start).total_seconds() / 60
        
        if current_duration < 5:
            return {'predicted_duration': 15, 'confidence': 0.6}
        elif current_duration < 15:
            return {'predicted_duration': 30, 'confidence': 0.7}
        else:
            return {'predicted_duration': current_duration + 10, 'confidence': 0.8}
    
    def _predict_follow_up_questions(self, text):
        """❓ PREDICT FOLLOW-UP QUESTIONS"""
        if not text:
            return []
        
        text_lower = text.lower()
        
        # Common follow-up patterns
        if 'weather' in text_lower:
            return ['What about tomorrow?', 'Any chance of rain?']
        elif 'time' in text_lower:
            return ['What about the date?', 'Is it morning or afternoon?']
        elif 'how are you' in text_lower:
            return ['How has your day been?', 'What have you been up to?']
        
        return []
    
    def _calculate_context_continuity(self):
        """🔗 CALCULATE CONTEXT CONTINUITY"""
        if len(self.session_interactions) < 2:
            return 0.0
        
        # Simple continuity based on interaction consistency
        recent_interactions = self.session_interactions[-5:]
        topics = [self._extract_topic(interaction['text']) for interaction in recent_interactions]
        
        unique_topics = len(set(topics))
        continuity_score = 1.0 - (unique_topics / len(topics))
        
        return continuity_score
    
    def _extract_topic(self, text):
        """📝 EXTRACT TOPIC FROM TEXT"""
        if not text:
            return 'unknown'
        
        text_lower = text.lower()
        
        # Simple topic extraction
        if any(word in text_lower for word in ['weather', 'temperature', 'rain', 'sunny']):
            return 'weather'
        elif any(word in text_lower for word in ['time', 'clock', 'hour', 'minute']):
            return 'time'
        elif any(word in text_lower for word in ['name', 'call', 'my name']):
            return 'identity'
        
        return 'general'
    
    def _generate_proactive_suggestions(self, text):
        """💡 GENERATE PROACTIVE SUGGESTIONS"""
        suggestions = []
        
        if not text:
            return suggestions
        
        text_lower = text.lower()
        
        # Context-based suggestions
        if 'weather' in text_lower:
            suggestions.append('Would you like a weather forecast for tomorrow?')
        elif 'time' in text_lower:
            suggestions.append('Should I set a reminder for you?')
        elif 'music' in text_lower:
            suggestions.append('Would you like me to play some music?')
        
        return suggestions
    
    def _generate_adaptation_recommendations(self):
        """🔧 GENERATE ADAPTATION RECOMMENDATIONS"""
        recommendations = []
        
        # Analyze recent audio quality
        if len(self.audio_quality_history) > 5:
            recent_quality = self.audio_quality_history[-5:]
            avg_quality = sum(q['quality_score'] for q in recent_quality) / len(recent_quality)
            
            if avg_quality < 0.5:
                recommendations.append('Consider improving audio quality')
        
        # Analyze interaction patterns
        if len(self.session_interactions) > 10:
            recent_interactions = self.session_interactions[-10:]
            avg_confidence = sum(
                interaction.get('context_analysis', {}).get('speaking_confidence', {}).get('score', 0.5)
                for interaction in recent_interactions
            ) / len(recent_interactions)
            
            if avg_confidence < 0.6:
                recommendations.append('Speaking more clearly might help')
        
        return recommendations
    
    def _update_behavioral_patterns(self, context_analysis):
        """📊 UPDATE BEHAVIORAL PATTERNS"""
        try:
            # Update conversation flow patterns
            flow_pattern = {
                'timestamp': datetime.utcnow().isoformat(),
                'conversation_style': context_analysis.get('behavioral_context', {}).get('conversation_style', 'unknown'),
                'emotional_tone': context_analysis.get('behavioral_context', {}).get('emotional_tone', 'neutral'),
                'interaction_intent': context_analysis.get('behavioral_context', {}).get('interaction_intent', 'unknown')
            }
            
            self.conversation_flow_patterns.append(flow_pattern)
            
            # Keep only recent patterns
            if len(self.conversation_flow_patterns) > 50:
                self.conversation_flow_patterns = self.conversation_flow_patterns[-50:]
            
        except Exception as e:
            print(f"[AdvancedContext] ❌ Pattern update error: {e}")
    
    def handle_low_confidence_context(self, audio, text, identified_user, confidence):
        """🔍 ENHANCED: Handle low confidence with clustering context"""
        context_user = self.predict_likely_user_enhanced(text, audio)
        
        # ✅ ENHANCED: Consider clustering context
        clustering_context = self.analyze_clustering_context(audio, text)
        
        # If context strongly suggests a user and it matches low-confidence recognition
        if (context_user['confidence'] > 0.8 and 
            context_user['predicted_user'] == identified_user):
            
            print(f"[AdvancedContext] ✅ CONTEXT RESCUE: {identified_user}")
            return identified_user, "CONTEXT_CONFIRMED"
        
        # If clustering suggests a strong match
        if clustering_context.get('clustering_confidence', 0.0) > 0.7:
            print(f"[AdvancedContext] 🔗 CLUSTERING CONTEXT: High confidence cluster match")
            return "CLUSTER_MATCH", "CLUSTERING_CONFIRMED"
        
        # If context suggests login user strongly
        elif (context_user['confidence'] > 0.85 and 
              context_user['predicted_user'] == self.login_user):
            
            print(f"[AdvancedContext] 🎯 CONTEXT OVERRIDE: {self.login_user}")
            return self.login_user, "CONTEXT_RECOGNIZED"
        
        return "UNKNOWN", confidence
    
    def predict_likely_user_enhanced(self, text, audio):
        """🎯 ENHANCED: Predict likely user with clustering intelligence"""
        
        predictions = []
        
        # Factor 1: System login context (strong weight)
        predictions.append({
            'name': self.login_user,
            'confidence': 0.85,
            'reason': 'system_login',
            'weight': 0.3  # Reduced weight for clustering
        })
        
        # Factor 2: Preferred names from text
        preferred_names = self.user_preferences.get('preferred_names', [])
        text_lower = text.lower()
        
        for name in preferred_names:
            if name.lower() in text_lower:
                predictions.append({
                    'name': name,
                    'confidence': 0.95,
                    'reason': 'self_identification',
                    'weight': 0.4  # High weight for self-identification
                })
        
        # Factor 3: Session consistency with clustering
        if len(self.session_interactions) > 0:
            # Check for consistent cluster usage
            cluster_consistency = self._analyze_cluster_consistency()
            predictions.append({
                'name': self.login_user,
                'confidence': 0.7 + cluster_consistency * 0.2,
                'reason': 'session_consistency',
                'weight': 0.2
            })
        
        # Factor 4: Behavioral patterns
        behavioral_prediction = self._predict_user_from_behavior(text)
        if behavioral_prediction:
            predictions.append(behavioral_prediction)
        
        # Factor 5: Time-based patterns
        current_hour = datetime.utcnow().hour
        typical_hours = self.user_preferences.get('typical_hours', [])
        if not typical_hours or current_hour in typical_hours:
            predictions.append({
                'name': self.login_user,
                'confidence': 0.6,
                'reason': 'time_pattern',
                'weight': 0.1
            })
        
        # Calculate weighted prediction
        if predictions:
            # Find best prediction by weighted score
            best_prediction = max(predictions, key=lambda p: p['confidence'] * p['weight'])
            total_confidence = sum(p['confidence'] * p['weight'] for p in predictions)
            
            return {
                'predicted_user': best_prediction['name'],
                'confidence': total_confidence,
                'reasoning': [p['reason'] for p in predictions],
                'all_predictions': predictions,
                'method': 'enhanced_clustering_context'
            }
        
        return {
            'predicted_user': self.login_user,
            'confidence': 0.5,
            'reasoning': ['fallback_to_login'],
            'all_predictions': [],
            'method': 'fallback'
        }
    
    def _analyze_cluster_consistency(self):
        """📊 ANALYZE CLUSTER CONSISTENCY"""
        try:
            if len(self.session_interactions) < 3:
                return 0.0
            
            # Analyze recent cluster usage patterns
            recent_interactions = self.session_interactions[-10:]
            cluster_mentions = 0
            
            for interaction in recent_interactions:
                clustering_context = interaction.get('context_analysis', {}).get('clustering_context', {})
                if clustering_context.get('clustering_confidence', 0.0) > 0.6:
                    cluster_mentions += 1
            
            return cluster_mentions / len(recent_interactions)
            
        except Exception as e:
            return 0.0
    
    def _predict_user_from_behavior(self, text):
        """🎭 PREDICT USER FROM BEHAVIORAL PATTERNS"""
        try:
            if not text or len(self.conversation_flow_patterns) < 5:
                return None
            
            # Analyze current text style
            current_style = self._detect_conversation_style(text)
            current_tone = self._detect_emotional_tone(text)
            
            # Match against recent patterns
            recent_patterns = self.conversation_flow_patterns[-20:]
            
            style_matches = sum(1 for p in recent_patterns if p['conversation_style'] == current_style)
            tone_matches = sum(1 for p in recent_patterns if p['emotional_tone'] == current_tone)
            
            if style_matches > len(recent_patterns) * 0.6:
                return {
                    'name': self.login_user,
                    'confidence': 0.7,
                    'reason': 'behavioral_pattern',
                    'weight': 0.15
                }
            
            return None
            
        except Exception as e:
            return None
    
    def assess_audio_quality_detailed(self, audio):
        """🔊 DETAILED AUDIO QUALITY ASSESSMENT"""
        try:
            if audio is None or len(audio) == 0:
                return {
                    'quality': 'poor', 'score': 0.0, 'issues': ['no_audio'],
                    'volume': 0, 'peak': 0, 'dynamic_range': 0, 'snr_estimate': 0,
                    'clustering_suitability': 'poor'
                }
            
            # Calculate comprehensive audio metrics
            volume = np.abs(audio).mean()
            peak = np.max(np.abs(audio))
            rms = np.sqrt(np.mean(audio**2))
            noise_floor = np.percentile(np.abs(audio), 10)
            signal_level = np.percentile(np.abs(audio), 90)
            dynamic_range = signal_level - noise_floor if signal_level > noise_floor else 0
            
            # Estimate SNR
            snr_estimate = 20 * np.log10((signal_level + 1e-6) / (noise_floor + 1e-6))
            
            # Assess quality with enhanced criteria
            quality_score = 0.0
            issues = []
            
            # Volume assessment
            if 150 <= volume <= 4000:
                quality_score += 0.25
            elif volume < 100:
                issues.append('low_volume')
            elif volume > 6000:
                issues.append('high_volume')
            else:
                quality_score += 0.15
            
            # Dynamic range assessment
            if dynamic_range > 800:
                quality_score += 0.25
            elif dynamic_range < 300:
                issues.append('poor_dynamic_range')
            else:
                quality_score += 0.15
            
            # Peak level assessment (clipping detection)
            if peak < 25000:
                quality_score += 0.2
            elif peak >= 30000:
                issues.append('clipping')
            
            # Duration assessment
            duration = len(audio) / SAMPLE_RATE
            if duration >= 1.0:
                quality_score += 0.2
            elif duration < 0.5:
                issues.append('too_short')
            else:
                quality_score += 0.1
            
            # SNR assessment
            if snr_estimate > 20:
                quality_score += 0.1
            elif snr_estimate < 10:
                issues.append('high_noise')
            
            # Determine quality level
            if quality_score >= 0.8:
                quality = 'excellent'
                clustering_suitability = 'excellent'
            elif quality_score >= 0.6:
                quality = 'good'
                clustering_suitability = 'good'
            elif quality_score >= 0.4:
                quality = 'fair'
                clustering_suitability = 'fair'
            else:
                quality = 'poor'
                clustering_suitability = 'poor'
            
            result = {
                'quality': quality,
                'score': quality_score,
                'volume': volume,
                'peak': peak,
                'rms': rms,
                'dynamic_range': dynamic_range,
                'snr_estimate': snr_estimate,
                'duration': duration,
                'issues': issues,
                'clustering_suitability': clustering_suitability  # ✅ NEW
            }
            
            # Store in history for trend analysis
            self.audio_quality_history.append({
                'timestamp': time.time(),
                'quality_score': quality_score,
                'snr': snr_estimate,
                'volume': volume,
                'clustering_suitability': clustering_suitability
            })
            
            # Keep only last 50 samples
            if len(self.audio_quality_history) > 50:
                self.audio_quality_history = self.audio_quality_history[-50:]
            
            return result
            
        except Exception as e:
            print(f"[AdvancedContext] ⚠️ Audio assessment error: {e}")
            return {
                'quality': 'unknown', 'score': 0.0, 'issues': ['assessment_error'],
                'clustering_suitability': 'unknown'
            }
    
    def assess_speaking_confidence(self, text):
        """🎤 ASSESS SPEAKING CONFIDENCE"""
        if not text:
            return {'confidence': 'unknown', 'score': 0.0, 'word_count': 0, 'clustering_impact': 'negative'}
        
        confidence_score = 0.0
        indicators = []
        
        words = text.split()
        word_count = len(words)
        
        # Length indicators
        if word_count >= 3:
            confidence_score += 0.2
            indicators.append('adequate_length')
        elif word_count >= 1:
            confidence_score += 0.1
            indicators.append('minimal_length')
        
        # Clarity indicators - no filler words
        fillers = ['um', 'uh', 'er', 'like', 'you know']
        if not any(filler in text.lower() for filler in fillers):
            confidence_score += 0.3
            indicators.append('no_fillers')
        
        # Completeness indicators
        if text.strip().endswith(('.', '!', '?')) or word_count <= 4:
            confidence_score += 0.2
            indicators.append('complete_thought')
        
        # Repetition check
        unique_words = set(word.lower() for word in words)
        if len(unique_words) == len(words):
            confidence_score += 0.2
            indicators.append('no_repetition')
        
        # Coherence check
        if word_count > 1 and all(word.isalpha() or word in ["I", "I'm", "don't", "can't"] for word in words):
            confidence_score += 0.1
            indicators.append('coherent')
        
        # Determine confidence level
        if confidence_score >= 0.7:
            confidence = 'high'
            clustering_impact = 'positive'
        elif confidence_score >= 0.4:
            confidence = 'medium'
            clustering_impact = 'neutral'
        else:
            confidence = 'low'
            clustering_impact = 'negative'
        
        return {
            'confidence': confidence,
            'score': confidence_score,
            'indicators': indicators,
            'word_count': word_count,
            'filler_count': sum(1 for filler in fillers if filler in text.lower()),
            'clustering_impact': clustering_impact  # ✅ NEW
        }
    
    def assess_environment_advanced(self, audio):
        """🌍 ADVANCED ENVIRONMENTAL ASSESSMENT"""
        try:
            if audio is None or len(audio) == 0:
                return {
                    'environment': 'unknown', 'noise_level': 'unknown', 'analysis': {},
                    'clustering_impact': 'unknown'
                }
            
            # Advanced noise analysis
            noise_floor = np.percentile(np.abs(audio), 5)
            signal_level = np.percentile(np.abs(audio), 95)
            noise_variability = np.std(np.abs(audio[:len(audio)//4]))
            
            # Frequency analysis for noise characterization
            try:
                from scipy import signal as sp_signal
                f, psd = sp_signal.welch(audio, SAMPLE_RATE, nperseg=min(512, len(audio)//4))
                
                # Analyze frequency distribution
                low_freq_energy = np.sum(psd[f < 300])
                mid_freq_energy = np.sum(psd[(f >= 300) & (f <= 3400)])
                high_freq_energy = np.sum(psd[f > 3400])
                
                total_energy = low_freq_energy + mid_freq_energy + high_freq_energy
                
                if total_energy > 0:
                    low_ratio = low_freq_energy / total_energy
                    mid_ratio = mid_freq_energy / total_energy
                    high_ratio = high_freq_energy / total_energy
                else:
                    low_ratio = mid_ratio = high_ratio = 0.33
                
            except ImportError:
                low_ratio = mid_ratio = high_ratio = 0.33
            
            # Environment classification
            if noise_floor < 30:
                environment = 'very_quiet'
                noise_level = 'minimal'
                clustering_impact = 'excellent'
            elif noise_floor < 80:
                environment = 'quiet'
                noise_level = 'low'
                clustering_impact = 'good'
            elif noise_floor < 150:
                environment = 'normal'
                noise_level = 'moderate'
                clustering_impact = 'fair'
            elif noise_floor < 300:
                environment = 'noisy'
                noise_level = 'high'
                clustering_impact = 'poor'
            else:
                environment = 'very_noisy'
                noise_level = 'extreme'
                clustering_impact = 'very_poor'
            
            # Noise characterization
            noise_characteristics = []
            if low_ratio > 0.5:
                noise_characteristics.append('low_frequency_dominant')
            if high_ratio > 0.4:
                noise_characteristics.append('high_frequency_noise')
            if noise_variability > noise_floor * 0.5:
                noise_characteristics.append('variable_noise')
            
            result = {
                'environment': environment,
                'noise_level': noise_level,
                'noise_floor': noise_floor,
                'signal_level': signal_level,
                'snr_estimate': signal_level / (noise_floor + 1),
                'noise_variability': noise_variability,
                'frequency_analysis': {
                    'low_freq_ratio': low_ratio,
                    'mid_freq_ratio': mid_ratio,
                    'high_freq_ratio': high_ratio
                },
                'noise_characteristics': noise_characteristics,
                'clustering_impact': clustering_impact  # ✅ NEW
            }
            
            return result
            
        except Exception as e:
            print(f"[AdvancedContext] ⚠️ Environment assessment error: {e}")
            return {
                'environment': 'unknown', 'noise_level': 'unknown', 'analysis': {},
                'clustering_impact': 'unknown'
            }
    
    def assess_text_clarity(self, text):
        """📝 ASSESS TEXT CLARITY"""
        if not text:
            return {
                'clarity': 'poor', 'score': 0.0, 'issues': [], 'analysis': {},
                'clustering_impact': 'negative'
            }
        
        clarity_score = 0.0
        issues = []
        
        # Check for transcription artifacts
        artifacts = ['[', ']', '(', ')', '<', '>', '{', '}']
        if not any(artifact in text for artifact in artifacts):
            clarity_score += 0.25
        else:
            issues.append('transcription_artifacts')
        
        # Check word boundary quality
        words = text.split()
        valid_words = 0
        for word in words:
            clean_word = ''.join(c for c in word if c.isalpha() or c in ["'", "-"])
            if clean_word and (clean_word.isalpha() or clean_word in ["I'm", "don't", "can't", "won't", "it's"]):
                valid_words += 1
        
        if len(words) > 0:
            word_validity = valid_words / len(words)
            clarity_score += 0.25 * word_validity
            if word_validity < 0.8:
                issues.append('unusual_characters')
        
        # Check length reasonableness
        if 1 <= len(words) <= 25:
            clarity_score += 0.2
        else:
            issues.append('unusual_length')
        
        # Check capitalization
        if any(c.isupper() for c in text) and any(c.islower() for c in text):
            clarity_score += 0.15
        
        # Check for complete sentences
        if text.strip().endswith(('.', '!', '?')) or len(words) <= 3:
            clarity_score += 0.15
        
        # Determine clarity level
        if clarity_score >= 0.8:
            clarity = 'excellent'
            clustering_impact = 'positive'
        elif clarity_score >= 0.6:
            clarity = 'high'
            clustering_impact = 'positive'
        elif clarity_score >= 0.4:
            clarity = 'medium'
            clustering_impact = 'neutral'
        else:
            clarity = 'low'
            clustering_impact = 'negative'
        
        return {
            'clarity': clarity,
            'score': clarity_score,
            'issues': issues,
            'analysis': {
                'word_count': len(words),
                'valid_words': valid_words,
                'word_validity_ratio': valid_words / len(words) if words else 0,
                'has_proper_case': any(c.isupper() for c in text) and any(c.islower() for c in text)
            },
            'clustering_impact': clustering_impact  # ✅ NEW
        }
    
    def analyze_session_context(self):
        """📊 ANALYZE SESSION CONTEXT"""
        session_duration = (datetime.utcnow() - self.session_start).total_seconds() / 60
        interactions = len(self.session_interactions)
        
        # Calculate interaction rate
        interaction_rate = interactions / max(session_duration, 1)
        
        # Classify session type
        if session_duration < 2:
            session_type = 'brief'
        elif session_duration < 15:
            session_type = 'short'
        elif session_duration < 45:
            session_type = 'normal'
        else:
            session_type = 'extended'
        
        # Analyze interaction patterns
        if interactions > 0:
            recent_interactions = self.session_interactions[-10:]
            avg_confidence = np.mean([
                interaction.get('context_analysis', {}).get('speaking_confidence', {}).get('score', 0.5)
                for interaction in recent_interactions
            ])
            avg_audio_quality = np.mean([
                interaction.get('context_analysis', {}).get('audio_quality', {}).get('score', 0.5)
                for interaction in recent_interactions
            ])
        else:
            avg_confidence = 0.5
            avg_audio_quality = 0.5
        
        # ✅ ENHANCED: Add clustering context
        clustering_stats = self._analyze_session_clustering()
        
        return {
            'session_duration_minutes': session_duration,
            'total_interactions': interactions,
            'interaction_rate_per_minute': interaction_rate,
            'session_type': session_type,
            'avg_speaking_confidence': avg_confidence,
            'avg_audio_quality': avg_audio_quality,
            'session_start': self.session_start.isoformat(),
            'clustering_stats': clustering_stats  # ✅ NEW
        }
    
    def _analyze_session_clustering(self):
        """🔍 ANALYZE SESSION CLUSTERING PATTERNS"""
        try:
            from voice.database import anonymous_clusters
            
            # Analyze clusters created during this session
            session_clusters = 0
            for cluster in anonymous_clusters.values():
                created_at = datetime.fromisoformat(cluster.get('created_at', '2025-01-01T00:00:00'))
                if created_at >= self.session_start:
                    session_clusters += 1
            
            return {
                'clusters_created_this_session': session_clusters,
                'total_active_clusters': len(anonymous_clusters),
                'clustering_activity': 'high' if session_clusters > 2 else 'normal' if session_clusters > 0 else 'low'
            }
            
        except Exception as e:
            return {
                'clusters_created_this_session': 0,
                'total_active_clusters': 0,
                'clustering_activity': 'unknown'
            }

# Export for compatibility
ContextAnalyzer = AdvancedContextAnalyzer

# Global advanced context analyzer  
advanced_context_analyzer = AdvancedContextAnalyzer()