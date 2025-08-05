"""
Qualia Analytics - Track emotion/qualia trends over time
Provides comprehensive analysis of subjective experiences and emotional patterns
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics
from enum import Enum

class AnalyticsTimeframe(Enum):
    """Time frames for analytics"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    ALL_TIME = "all_time"

@dataclass
class QualiaSnapshot:
    """Snapshot of qualia state at a point in time"""
    timestamp: str
    dominant_qualia: str
    emotional_valence: float
    cognitive_clarity: float
    intensity: float
    active_qualia_count: int
    qualia_types: List[str]
    context: str
    user_id: str

@dataclass
class EmotionalTrend:
    """Represents an emotional trend over time"""
    trend_id: str
    timeframe: AnalyticsTimeframe
    start_time: str
    end_time: str
    dominant_emotion: str
    average_valence: float
    average_intensity: float
    peak_emotion: str
    peak_intensity: float
    emotional_stability: float
    transition_count: int
    most_common_triggers: List[str]

@dataclass
class QualiaPattern:
    """Represents a pattern in qualia experiences"""
    pattern_id: str
    pattern_type: str
    frequency: int
    avg_duration: float
    trigger_contexts: List[str]
    emotional_signature: Dict[str, float]
    temporal_distribution: Dict[str, int]  # hour -> count
    confidence: float

class QualiaAnalytics:
    """Analytics system for tracking qualia and emotional patterns"""
    
    def __init__(self, save_path: str = "qualia_analytics.json"):
        self.save_path = save_path
        self.qualia_snapshots: List[QualiaSnapshot] = []
        self.emotional_trends: List[EmotionalTrend] = []
        self.qualia_patterns: List[QualiaPattern] = []
        self.load_analytics_data()
        
        # Configuration
        self.max_snapshots = 10000  # Maximum snapshots to keep
        self.snapshot_interval = 300  # 5 minutes between snapshots
        self.last_snapshot_time = 0
        self.pattern_detection_threshold = 3  # Minimum occurrences for pattern
        
    def capture_qualia_snapshot(self, user_id: str, context: str = "general") -> QualiaSnapshot:
        """Capture current qualia state"""
        try:
            # Get current qualia state
            qualia_state = self._get_current_qualia_state()
            
            # Create snapshot
            snapshot = QualiaSnapshot(
                timestamp=datetime.now().isoformat(),
                dominant_qualia=qualia_state.get('dominant_qualia', {}).get('type', 'neutral'),
                emotional_valence=qualia_state.get('average_valence', 0.0),
                cognitive_clarity=qualia_state.get('average_clarity', 0.5),
                intensity=qualia_state.get('dominant_qualia', {}).get('intensity', 0.5),
                active_qualia_count=qualia_state.get('active_qualia_count', 0),
                qualia_types=qualia_state.get('active_types', []),
                context=context,
                user_id=user_id
            )
            
            self.qualia_snapshots.append(snapshot)
            self.last_snapshot_time = time.time()
            
            # Limit snapshot count
            if len(self.qualia_snapshots) > self.max_snapshots:
                self.qualia_snapshots = self.qualia_snapshots[-self.max_snapshots:]
            
            self.save_analytics_data()
            return snapshot
            
        except Exception as e:
            print(f"[QualiaAnalytics] ❌ Error capturing snapshot: {e}")
            return self._create_default_snapshot(user_id, context)
    
    def _get_current_qualia_state(self) -> Dict[str, Any]:
        """Get current qualia state from the system"""
        try:
            from ai.belief_qualia_linking import get_current_qualia_state
            return get_current_qualia_state()
        except Exception as e:
            print(f"[QualiaAnalytics] ⚠️ Could not get qualia state: {e}")
            return {
                'dominant_qualia': {'type': 'neutral', 'intensity': 0.5},
                'average_valence': 0.0,
                'average_clarity': 0.5,
                'active_qualia_count': 0,
                'active_types': []
            }
    
    def _create_default_snapshot(self, user_id: str, context: str) -> QualiaSnapshot:
        """Create default snapshot for error cases"""
        return QualiaSnapshot(
            timestamp=datetime.now().isoformat(),
            dominant_qualia='neutral',
            emotional_valence=0.0,
            cognitive_clarity=0.5,
            intensity=0.5,
            active_qualia_count=0,
            qualia_types=[],
            context=context,
            user_id=user_id
        )
    
    def analyze_emotional_trends(self, timeframe: AnalyticsTimeframe, user_id: Optional[str] = None) -> List[EmotionalTrend]:
        """Analyze emotional trends over specified timeframe"""
        try:
            # Filter snapshots by timeframe and user
            filtered_snapshots = self._filter_snapshots_by_timeframe(timeframe, user_id)
            
            if not filtered_snapshots:
                return []
            
            # Group snapshots by time periods
            time_groups = self._group_snapshots_by_time(filtered_snapshots, timeframe)
            
            trends = []
            for group_key, snapshots in time_groups.items():
                if len(snapshots) < 2:
                    continue
                
                trend = self._analyze_trend_for_group(snapshots, timeframe, group_key)
                trends.append(trend)
            
            self.emotional_trends.extend(trends)
            return trends
            
        except Exception as e:
            print(f"[QualiaAnalytics] ❌ Error analyzing trends: {e}")
            return []
    
    def _filter_snapshots_by_timeframe(self, timeframe: AnalyticsTimeframe, user_id: Optional[str] = None) -> List[QualiaSnapshot]:
        """Filter snapshots by timeframe and user"""
        now = datetime.now()
        
        # Calculate time cutoff
        if timeframe == AnalyticsTimeframe.HOUR:
            cutoff = now - timedelta(hours=1)
        elif timeframe == AnalyticsTimeframe.DAY:
            cutoff = now - timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.WEEK:
            cutoff = now - timedelta(weeks=1)
        elif timeframe == AnalyticsTimeframe.MONTH:
            cutoff = now - timedelta(days=30)
        else:  # ALL_TIME
            cutoff = datetime.min
        
        filtered = []
        for snapshot in self.qualia_snapshots:
            try:
                snapshot_time = datetime.fromisoformat(snapshot.timestamp)
                if snapshot_time >= cutoff:
                    if user_id is None or snapshot.user_id == user_id:
                        filtered.append(snapshot)
            except ValueError:
                continue
        
        return filtered
    
    def _group_snapshots_by_time(self, snapshots: List[QualiaSnapshot], timeframe: AnalyticsTimeframe) -> Dict[str, List[QualiaSnapshot]]:
        """Group snapshots by time periods"""
        groups = defaultdict(list)
        
        for snapshot in snapshots:
            try:
                timestamp = datetime.fromisoformat(snapshot.timestamp)
                
                if timeframe == AnalyticsTimeframe.HOUR:
                    group_key = timestamp.strftime("%Y-%m-%d %H:00")
                elif timeframe == AnalyticsTimeframe.DAY:
                    group_key = timestamp.strftime("%Y-%m-%d")
                elif timeframe == AnalyticsTimeframe.WEEK:
                    # Group by week
                    week_start = timestamp - timedelta(days=timestamp.weekday())
                    group_key = week_start.strftime("%Y-%m-%d")
                elif timeframe == AnalyticsTimeframe.MONTH:
                    group_key = timestamp.strftime("%Y-%m")
                else:  # ALL_TIME
                    group_key = "all_time"
                
                groups[group_key].append(snapshot)
                
            except ValueError:
                continue
        
        return dict(groups)
    
    def _analyze_trend_for_group(self, snapshots: List[QualiaSnapshot], timeframe: AnalyticsTimeframe, group_key: str) -> EmotionalTrend:
        """Analyze emotional trend for a group of snapshots"""
        # Calculate statistics
        valences = [s.emotional_valence for s in snapshots]
        intensities = [s.intensity for s in snapshots]
        
        avg_valence = statistics.mean(valences)
        avg_intensity = statistics.mean(intensities)
        
        # Find peak emotion
        peak_snapshot = max(snapshots, key=lambda s: s.intensity)
        
        # Calculate emotional stability (inverse of variance)
        valence_variance = statistics.variance(valences) if len(valences) > 1 else 0
        emotional_stability = 1 / (1 + valence_variance)
        
        # Count emotional transitions
        transition_count = self._count_emotional_transitions(snapshots)
        
        # Find most common triggers
        triggers = [s.context for s in snapshots]
        trigger_counts = defaultdict(int)
        for trigger in triggers:
            trigger_counts[trigger] += 1
        
        most_common_triggers = sorted(trigger_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        most_common_triggers = [trigger for trigger, count in most_common_triggers]
        
        # Find dominant emotion
        qualia_types = [s.dominant_qualia for s in snapshots]
        dominant_emotion = max(set(qualia_types), key=qualia_types.count)
        
        return EmotionalTrend(
            trend_id=f"trend_{len(self.emotional_trends)}",
            timeframe=timeframe,
            start_time=snapshots[0].timestamp,
            end_time=snapshots[-1].timestamp,
            dominant_emotion=dominant_emotion,
            average_valence=avg_valence,
            average_intensity=avg_intensity,
            peak_emotion=peak_snapshot.dominant_qualia,
            peak_intensity=peak_snapshot.intensity,
            emotional_stability=emotional_stability,
            transition_count=transition_count,
            most_common_triggers=most_common_triggers
        )
    
    def _count_emotional_transitions(self, snapshots: List[QualiaSnapshot]) -> int:
        """Count emotional transitions in snapshots"""
        if len(snapshots) < 2:
            return 0
        
        transitions = 0
        prev_emotion = snapshots[0].dominant_qualia
        
        for snapshot in snapshots[1:]:
            if snapshot.dominant_qualia != prev_emotion:
                transitions += 1
                prev_emotion = snapshot.dominant_qualia
        
        return transitions
    
    def detect_qualia_patterns(self, user_id: Optional[str] = None) -> List[QualiaPattern]:
        """Detect patterns in qualia experiences"""
        try:
            # Filter snapshots by user
            snapshots = self.qualia_snapshots if user_id is None else [
                s for s in self.qualia_snapshots if s.user_id == user_id
            ]
            
            if len(snapshots) < self.pattern_detection_threshold:
                return []
            
            patterns = []
            
            # Detect recurring emotional states
            patterns.extend(self._detect_emotional_patterns(snapshots))
            
            # Detect temporal patterns
            patterns.extend(self._detect_temporal_patterns(snapshots))
            
            # Detect context-based patterns
            patterns.extend(self._detect_context_patterns(snapshots))
            
            self.qualia_patterns.extend(patterns)
            return patterns
            
        except Exception as e:
            print(f"[QualiaAnalytics] ❌ Error detecting patterns: {e}")
            return []
    
    def _detect_emotional_patterns(self, snapshots: List[QualiaSnapshot]) -> List[QualiaPattern]:
        """Detect recurring emotional state patterns"""
        patterns = []
        
        # Group by emotion type
        emotion_groups = defaultdict(list)
        for snapshot in snapshots:
            emotion_groups[snapshot.dominant_qualia].append(snapshot)
        
        for emotion, emotion_snapshots in emotion_groups.items():
            if len(emotion_snapshots) >= self.pattern_detection_threshold:
                # Calculate pattern statistics
                durations = []
                triggers = []
                
                for snapshot in emotion_snapshots:
                    triggers.append(snapshot.context)
                
                # Calculate average duration (simplified)
                avg_duration = 300.0  # 5 minutes default
                
                # Create emotional signature
                valences = [s.emotional_valence for s in emotion_snapshots]
                intensities = [s.intensity for s in emotion_snapshots]
                
                emotional_signature = {
                    'valence': statistics.mean(valences),
                    'intensity': statistics.mean(intensities),
                    'stability': 1 / (1 + statistics.variance(valences)) if len(valences) > 1 else 1.0
                }
                
                # Calculate temporal distribution
                temporal_distribution = defaultdict(int)
                for snapshot in emotion_snapshots:
                    try:
                        timestamp = datetime.fromisoformat(snapshot.timestamp)
                        hour = timestamp.hour
                        temporal_distribution[str(hour)] += 1
                    except ValueError:
                        continue
                
                pattern = QualiaPattern(
                    pattern_id=f"emotion_pattern_{emotion}",
                    pattern_type=f"recurring_{emotion}",
                    frequency=len(emotion_snapshots),
                    avg_duration=avg_duration,
                    trigger_contexts=list(set(triggers)),
                    emotional_signature=emotional_signature,
                    temporal_distribution=dict(temporal_distribution),
                    confidence=min(1.0, len(emotion_snapshots) / 10.0)
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _detect_temporal_patterns(self, snapshots: List[QualiaSnapshot]) -> List[QualiaPattern]:
        """Detect time-based patterns"""
        patterns = []
        
        # Group by hour of day
        hour_groups = defaultdict(list)
        for snapshot in snapshots:
            try:
                timestamp = datetime.fromisoformat(snapshot.timestamp)
                hour = timestamp.hour
                hour_groups[hour].append(snapshot)
            except ValueError:
                continue
        
        # Find hours with consistent emotional patterns
        for hour, hour_snapshots in hour_groups.items():
            if len(hour_snapshots) >= self.pattern_detection_threshold:
                # Check if there's a dominant emotion for this hour
                emotions = [s.dominant_qualia for s in hour_snapshots]
                emotion_counts = defaultdict(int)
                for emotion in emotions:
                    emotion_counts[emotion] += 1
                
                if emotion_counts:
                    dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])
                    
                    # If one emotion dominates this hour
                    if dominant_emotion[1] >= len(hour_snapshots) * 0.6:
                        pattern = QualiaPattern(
                            pattern_id=f"temporal_pattern_{hour}",
                            pattern_type=f"hourly_{dominant_emotion[0]}",
                            frequency=dominant_emotion[1],
                            avg_duration=3600.0,  # 1 hour
                            trigger_contexts=list(set(s.context for s in hour_snapshots)),
                            emotional_signature={
                                'valence': statistics.mean([s.emotional_valence for s in hour_snapshots]),
                                'intensity': statistics.mean([s.intensity for s in hour_snapshots])
                            },
                            temporal_distribution={str(hour): len(hour_snapshots)},
                            confidence=dominant_emotion[1] / len(hour_snapshots)
                        )
                        patterns.append(pattern)
        
        return patterns
    
    def _detect_context_patterns(self, snapshots: List[QualiaSnapshot]) -> List[QualiaPattern]:
        """Detect context-based patterns"""
        patterns = []
        
        # Group by context
        context_groups = defaultdict(list)
        for snapshot in snapshots:
            context_groups[snapshot.context].append(snapshot)
        
        for context, context_snapshots in context_groups.items():
            if len(context_snapshots) >= self.pattern_detection_threshold:
                # Analyze emotional response to this context
                valences = [s.emotional_valence for s in context_snapshots]
                intensities = [s.intensity for s in context_snapshots]
                emotions = [s.dominant_qualia for s in context_snapshots]
                
                # Check for consistent emotional response
                avg_valence = statistics.mean(valences)
                avg_intensity = statistics.mean(intensities)
                
                # Find most common emotion for this context
                emotion_counts = defaultdict(int)
                for emotion in emotions:
                    emotion_counts[emotion] += 1
                
                dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])
                
                pattern = QualiaPattern(
                    pattern_id=f"context_pattern_{context}",
                    pattern_type=f"context_{context}",
                    frequency=len(context_snapshots),
                    avg_duration=600.0,  # 10 minutes default
                    trigger_contexts=[context],
                    emotional_signature={
                        'valence': avg_valence,
                        'intensity': avg_intensity,
                        'dominant_emotion': dominant_emotion[0]
                    },
                    temporal_distribution={},
                    confidence=min(1.0, len(context_snapshots) / 5.0)
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def get_emotional_summary(self, timeframe: AnalyticsTimeframe, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get emotional summary for timeframe"""
        try:
            snapshots = self._filter_snapshots_by_timeframe(timeframe, user_id)
            
            if not snapshots:
                return {'error': 'No data available for timeframe'}
            
            # Calculate statistics
            valences = [s.emotional_valence for s in snapshots]
            intensities = [s.intensity for s in snapshots]
            emotions = [s.dominant_qualia for s in snapshots]
            
            # Count emotions
            emotion_counts = defaultdict(int)
            for emotion in emotions:
                emotion_counts[emotion] += 1
            
            # Calculate stability
            valence_variance = statistics.variance(valences) if len(valences) > 1 else 0
            emotional_stability = 1 / (1 + valence_variance)
            
            return {
                'timeframe': timeframe.value,
                'total_snapshots': len(snapshots),
                'average_valence': statistics.mean(valences),
                'average_intensity': statistics.mean(intensities),
                'emotional_stability': emotional_stability,
                'dominant_emotion': max(emotion_counts.items(), key=lambda x: x[1])[0],
                'emotion_distribution': dict(emotion_counts),
                'peak_intensity': max(intensities),
                'peak_valence': max(valences),
                'lowest_valence': min(valences),
                'emotional_range': max(valences) - min(valences),
                'start_time': snapshots[0].timestamp,
                'end_time': snapshots[-1].timestamp
            }
            
        except Exception as e:
            print(f"[QualiaAnalytics] ❌ Error generating summary: {e}")
            return {'error': str(e)}
    
    def get_pattern_insights(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get insights from detected patterns"""
        try:
            patterns = self.qualia_patterns if user_id is None else [
                p for p in self.qualia_patterns if user_id in p.trigger_contexts
            ]
            
            if not patterns:
                return {'message': 'No patterns detected yet'}
            
            # Analyze patterns
            pattern_types = defaultdict(int)
            high_confidence_patterns = []
            
            for pattern in patterns:
                pattern_types[pattern.pattern_type] += 1
                if pattern.confidence > 0.7:
                    high_confidence_patterns.append(pattern)
            
            # Find most frequent patterns
            most_frequent = sorted(pattern_types.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'total_patterns': len(patterns),
                'high_confidence_patterns': len(high_confidence_patterns),
                'most_frequent_patterns': most_frequent,
                'pattern_types': dict(pattern_types),
                'average_confidence': statistics.mean([p.confidence for p in patterns]),
                'insights': self._generate_pattern_insights(patterns)
            }
            
        except Exception as e:
            print(f"[QualiaAnalytics] ❌ Error generating pattern insights: {e}")
            return {'error': str(e)}
    
    def _generate_pattern_insights(self, patterns: List[QualiaPattern]) -> List[str]:
        """Generate insights from patterns"""
        insights = []
        
        # Analyze temporal patterns
        temporal_patterns = [p for p in patterns if p.pattern_type.startswith('hourly_')]
        if temporal_patterns:
            insights.append(f"Detected {len(temporal_patterns)} time-based emotional patterns")
        
        # Analyze context patterns
        context_patterns = [p for p in patterns if p.pattern_type.startswith('context_')]
        if context_patterns:
            insights.append(f"Found {len(context_patterns)} context-specific emotional responses")
        
        # Analyze emotional patterns
        emotional_patterns = [p for p in patterns if p.pattern_type.startswith('recurring_')]
        if emotional_patterns:
            most_frequent_emotion = max(emotional_patterns, key=lambda p: p.frequency)
            insights.append(f"Most frequent emotional state: {most_frequent_emotion.pattern_type}")
        
        return insights
    
    def should_capture_snapshot(self) -> bool:
        """Check if it's time to capture a new snapshot"""
        return time.time() - self.last_snapshot_time >= self.snapshot_interval
    
    def load_analytics_data(self):
        """Load analytics data from file"""
        try:
            with open(self.save_path, 'r') as f:
                data = json.load(f)
            
            # Load snapshots
            for snapshot_data in data.get('snapshots', []):
                snapshot = QualiaSnapshot(
                    timestamp=snapshot_data['timestamp'],
                    dominant_qualia=snapshot_data['dominant_qualia'],
                    emotional_valence=snapshot_data['emotional_valence'],
                    cognitive_clarity=snapshot_data['cognitive_clarity'],
                    intensity=snapshot_data['intensity'],
                    active_qualia_count=snapshot_data['active_qualia_count'],
                    qualia_types=snapshot_data['qualia_types'],
                    context=snapshot_data['context'],
                    user_id=snapshot_data['user_id']
                )
                self.qualia_snapshots.append(snapshot)
            
            # Load trends
            for trend_data in data.get('trends', []):
                trend = EmotionalTrend(
                    trend_id=trend_data['trend_id'],
                    timeframe=AnalyticsTimeframe(trend_data['timeframe']),
                    start_time=trend_data['start_time'],
                    end_time=trend_data['end_time'],
                    dominant_emotion=trend_data['dominant_emotion'],
                    average_valence=trend_data['average_valence'],
                    average_intensity=trend_data['average_intensity'],
                    peak_emotion=trend_data['peak_emotion'],
                    peak_intensity=trend_data['peak_intensity'],
                    emotional_stability=trend_data['emotional_stability'],
                    transition_count=trend_data['transition_count'],
                    most_common_triggers=trend_data['most_common_triggers']
                )
                self.emotional_trends.append(trend)
            
            # Load patterns
            for pattern_data in data.get('patterns', []):
                pattern = QualiaPattern(
                    pattern_id=pattern_data['pattern_id'],
                    pattern_type=pattern_data['pattern_type'],
                    frequency=pattern_data['frequency'],
                    avg_duration=pattern_data['avg_duration'],
                    trigger_contexts=pattern_data['trigger_contexts'],
                    emotional_signature=pattern_data['emotional_signature'],
                    temporal_distribution=pattern_data['temporal_distribution'],
                    confidence=pattern_data['confidence']
                )
                self.qualia_patterns.append(pattern)
            
            print(f"[QualiaAnalytics] 📄 Loaded {len(self.qualia_snapshots)} snapshots, {len(self.emotional_trends)} trends, {len(self.qualia_patterns)} patterns")
            
        except FileNotFoundError:
            print(f"[QualiaAnalytics] 📄 No analytics data found, starting fresh")
        except Exception as e:
            print(f"[QualiaAnalytics] ❌ Error loading analytics data: {e}")
    
    def save_analytics_data(self):
        """Save analytics data to file"""
        try:
            data = {
                'snapshots': [asdict(snapshot) for snapshot in self.qualia_snapshots],
                'trends': [asdict(trend) for trend in self.emotional_trends],
                'patterns': [asdict(pattern) for pattern in self.qualia_patterns],
                'last_updated': datetime.now().isoformat(),
                'total_snapshots': len(self.qualia_snapshots),
                'total_trends': len(self.emotional_trends),
                'total_patterns': len(self.qualia_patterns)
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"[QualiaAnalytics] ❌ Error saving analytics data: {e}")
    
    def get_analytics_stats(self) -> Dict[str, Any]:
        """Get overall analytics statistics"""
        return {
            'total_snapshots': len(self.qualia_snapshots),
            'total_trends': len(self.emotional_trends),
            'total_patterns': len(self.qualia_patterns),
            'snapshot_interval': self.snapshot_interval,
            'last_snapshot_time': self.last_snapshot_time,
            'pattern_detection_threshold': self.pattern_detection_threshold,
            'data_timespan': self._calculate_data_timespan()
        }
    
    def _calculate_data_timespan(self) -> str:
        """Calculate timespan of collected data"""
        if not self.qualia_snapshots:
            return "No data"
        
        try:
            earliest = datetime.fromisoformat(self.qualia_snapshots[0].timestamp)
            latest = datetime.fromisoformat(self.qualia_snapshots[-1].timestamp)
            timespan = latest - earliest
            
            days = timespan.days
            hours = timespan.seconds // 3600
            
            return f"{days} days, {hours} hours"
        except Exception:
            return "Unknown"
    
    def update_qualia_trends(self):
        """Update qualia trends and analytics (maintenance method)"""
        try:
            # Analyze recent trends
            recent_trends = self.analyze_emotional_trends(AnalyticsTimeframe.DAY)
            
            # Update pattern detection
            new_patterns = self.detect_qualia_patterns()
            
            # Cleanup old data if needed
            if len(self.qualia_snapshots) > self.max_snapshots:
                # Keep most recent snapshots
                self.qualia_snapshots = self.qualia_snapshots[-self.max_snapshots:]
                
            # Save updated data
            self.save_analytics_data()
            
            logging.debug(f"[QualiaAnalytics] Updated trends: {len(recent_trends)} trends, {len(new_patterns)} patterns")
            
        except Exception as e:
            logging.error(f"[QualiaAnalytics] Error updating trends: {e}")
    
    def get_current_qualia_snapshot(self) -> Dict[str, Any]:
        """Get current qualia state snapshot"""
        try:
            if self.qualia_snapshots:
                # Return most recent snapshot
                latest = self.qualia_snapshots[-1]
                return asdict(latest)
            else:
                # Return default empty state
                return {
                    "timestamp": datetime.now().isoformat(),
                    "dominant_qualia": "neutral",
                    "emotional_valence": 0.0,
                    "cognitive_clarity": 0.5,
                    "intensity": 0.5,
                    "active_qualia_count": 0,
                    "qualia_types": [],
                    "context": "no_data",
                    "user_id": "unknown"
                }
        except Exception as e:
            logging.error(f"[QualiaAnalytics] Error getting current snapshot: {e}")
            return {}

# Global instance
qualia_analytics = QualiaAnalytics()

def capture_current_qualia_state(user_id: str, context: str = "general") -> Dict[str, Any]:
    """Capture current qualia state - main API function"""
    snapshot = qualia_analytics.capture_qualia_snapshot(user_id, context)
    return asdict(snapshot)

def get_emotional_trends(timeframe: AnalyticsTimeframe, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get emotional trends for timeframe"""
    trends = qualia_analytics.analyze_emotional_trends(timeframe, user_id)
    return [asdict(trend) for trend in trends]

def get_qualia_patterns(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get detected qualia patterns"""
    patterns = qualia_analytics.detect_qualia_patterns(user_id)
    return [asdict(pattern) for pattern in patterns]

def get_emotional_summary(timeframe: AnalyticsTimeframe, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get emotional summary for timeframe"""
    return qualia_analytics.get_emotional_summary(timeframe, user_id)

def get_pattern_insights(user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get insights from detected patterns"""
    return qualia_analytics.get_pattern_insights(user_id)

def should_capture_qualia_snapshot() -> bool:
    """Check if it's time to capture a new snapshot"""
    return qualia_analytics.should_capture_snapshot()

def get_qualia_analytics_stats() -> Dict[str, Any]:
    """Get analytics system statistics"""
    return qualia_analytics.get_analytics_stats()