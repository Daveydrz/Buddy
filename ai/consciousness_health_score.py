"""
Consciousness Health Score - System Coherence and Conflict Analysis

This module analyzes the overall health of the consciousness system by measuring
entropy, contradiction levels, goal progress, emotional state coherence, and the
balance between coherence and productive conflict.
"""

import json
import time
import os
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

class HealthMetric(Enum):
    """Different aspects of consciousness health"""
    COHERENCE = "coherence"                    # How well systems align
    ENTROPY_BALANCE = "entropy_balance"        # Optimal entropy vs chaos
    GOAL_ALIGNMENT = "goal_alignment"          # Goal consistency and progress
    EMOTIONAL_STABILITY = "emotional_stability" # Emotional regulation
    BELIEF_CONSISTENCY = "belief_consistency"   # Belief system integrity
    MEMORY_INTEGRATION = "memory_integration"   # Memory system health
    ATTENTION_FOCUS = "attention_focus"         # Attention management
    SELF_AWARENESS = "self_awareness"           # Self-model accuracy
    ADAPTABILITY = "adaptability"               # Ability to learn and change
    RESILIENCE = "resilience"                   # Recovery from conflicts

class HealthLevel(Enum):
    """Overall health assessment levels"""
    CRITICAL = "critical"      # 0.0-0.2 - Serious dysfunction
    POOR = "poor"             # 0.2-0.4 - Significant issues
    MODERATE = "moderate"     # 0.4-0.6 - Acceptable functioning
    GOOD = "good"             # 0.6-0.8 - Healthy functioning
    EXCELLENT = "excellent"   # 0.8-1.0 - Optimal state

@dataclass
class HealthAssessment:
    """Complete health assessment at a point in time"""
    id: str
    timestamp: datetime
    overall_score: float
    health_level: HealthLevel
    metric_scores: Dict[HealthMetric, float]
    coherence_factors: List[str]
    conflict_factors: List[str]
    recommendations: List[str]
    trend_analysis: Dict[str, float]
    risk_factors: List[str]
    strengths: List[str]

@dataclass
class HealthTrend:
    """Trend analysis over time"""
    metric: HealthMetric
    timeframe: str  # e.g., "7_days", "24_hours"
    trend_direction: str  # "improving", "declining", "stable"
    change_rate: float
    significance: float  # How significant the trend is
    key_events: List[str]  # Events that may have influenced the trend

class ConsciousnessHealthScorer:
    """Analyzes and scores consciousness system health"""
    
    def __init__(self, save_path: str = "ai_consciousness_health.json"):
        self.save_path = save_path
        self.assessments: List[HealthAssessment] = []
        self.health_trends: List[HealthTrend] = []
        self.running = False
        
        # Health scoring parameters
        self.assessment_interval = 300.0  # 5 minutes between assessments
        self.trend_analysis_window = 86400.0  # 24 hours for trend analysis
        self.critical_threshold = 0.3  # Below this is critical
        self.optimal_entropy_range = (0.3, 0.7)  # Optimal entropy levels
        
        # Weighting for different metrics
        self.metric_weights = {
            HealthMetric.COHERENCE: 0.15,
            HealthMetric.ENTROPY_BALANCE: 0.12,
            HealthMetric.GOAL_ALIGNMENT: 0.13,
            HealthMetric.EMOTIONAL_STABILITY: 0.12,
            HealthMetric.BELIEF_CONSISTENCY: 0.12,
            HealthMetric.MEMORY_INTEGRATION: 0.10,
            HealthMetric.ATTENTION_FOCUS: 0.08,
            HealthMetric.SELF_AWARENESS: 0.08,
            HealthMetric.ADAPTABILITY: 0.05,
            HealthMetric.RESILIENCE: 0.05
        }
        
        self.last_assessment_time = 0
        self._load_health_data()
        print(f"[ConsciousnessHealth] 💚 Initialized with {len(self.assessments)} health assessments")
    
    def start(self):
        """Start the consciousness health scorer"""
        self.running = True
        print("[ConsciousnessHealth] 💚 Consciousness health monitoring started")
    
    def stop(self):
        """Stop the consciousness health scorer"""
        self.running = False
        self._save_health_data()
        print("[ConsciousnessHealth] 💚 Consciousness health monitoring stopped")
    
    def assess_health(self, consciousness_data: Dict[str, Any] = None) -> HealthAssessment:
        """Perform a comprehensive health assessment"""
        if not self.running:
            return None
            
        current_time = time.time()
        if current_time - self.last_assessment_time < self.assessment_interval:
            return None  # Too soon for another assessment
            
        try:
            # Gather data from consciousness systems
            if consciousness_data is None:
                consciousness_data = self._gather_consciousness_data()
            
            # Calculate individual metric scores
            metric_scores = {}
            for metric in HealthMetric:
                metric_scores[metric] = self._calculate_metric_score(metric, consciousness_data)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(metric_scores)
            health_level = self._categorize_health_level(overall_score)
            
            # Analyze factors
            coherence_factors = self._identify_coherence_factors(consciousness_data, metric_scores)
            conflict_factors = self._identify_conflict_factors(consciousness_data, metric_scores)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metric_scores, health_level)
            
            # Analyze trends
            trend_analysis = self._analyze_trends()
            
            # Identify risks and strengths
            risk_factors = self._identify_risk_factors(metric_scores, consciousness_data)
            strengths = self._identify_strengths(metric_scores, consciousness_data)
            
            # Create assessment
            assessment = HealthAssessment(
                id=f"health_{int(time.time() * 1000)}",
                timestamp=datetime.now(),
                overall_score=overall_score,
                health_level=health_level,
                metric_scores=metric_scores,
                coherence_factors=coherence_factors,
                conflict_factors=conflict_factors,
                recommendations=recommendations,
                trend_analysis=trend_analysis,
                risk_factors=risk_factors,
                strengths=strengths
            )
            
            self.assessments.append(assessment)
            self.last_assessment_time = current_time
            
            print(f"[ConsciousnessHealth] 💚 Health assessment: {health_level.value} ({overall_score:.3f})")
            
            # Check for critical issues
            if health_level in [HealthLevel.CRITICAL, HealthLevel.POOR]:
                self._handle_health_crisis(assessment)
            
            # Update trends
            self._update_health_trends()
            
            # Save periodically
            if len(self.assessments) % 10 == 0:
                self._save_health_data()
            
            return assessment
            
        except Exception as e:
            print(f"[ConsciousnessHealth] ❌ Error in health assessment: {e}")
            return None
    
    def get_current_health_status(self) -> Dict[str, Any]:
        """Get current health status summary"""
        if not self.assessments:
            return {"status": "no_assessments"}
        
        latest = self.assessments[-1]
        
        return {
            "overall_score": latest.overall_score,
            "health_level": latest.health_level.value,
            "top_metrics": sorted(latest.metric_scores.items(), key=lambda x: x[1], reverse=True)[:3],
            "bottom_metrics": sorted(latest.metric_scores.items(), key=lambda x: x[1])[:3],
            "key_recommendations": latest.recommendations[:3],
            "critical_risks": [r for r in latest.risk_factors if "critical" in r.lower()],
            "assessment_time": latest.timestamp.isoformat(),
            "trend_summary": self._get_trend_summary()
        }
    
    def _gather_consciousness_data(self) -> Dict[str, Any]:
        """Gather data from various consciousness systems"""
        data = {
            "timestamp": time.time(),
            "entropy_level": 0.5,  # Would get from entropy system
            "goal_progress": 0.7,  # Would get from motivation system
            "emotional_state": {"primary": "neutral", "intensity": 0.5},
            "belief_contradictions": 0,  # Would get from belief analyzer
            "memory_coherence": 0.8,  # Would get from memory system
            "attention_focus": 0.6,  # Would get from attention manager
            "self_awareness_score": 0.7,  # Would get from self-model
            "recent_conflicts": [],
            "recent_achievements": [],
            "processing_load": 0.5
        }
        
        # In a real implementation, this would gather actual data from other modules
        # For now, we'll use simulated data with some realistic variation
        import random
        
        # Simulate realistic variations
        data["entropy_level"] = max(0.0, min(1.0, random.gauss(0.5, 0.1)))
        data["goal_progress"] = max(0.0, min(1.0, random.gauss(0.7, 0.15)))
        data["emotional_state"]["intensity"] = max(0.0, min(1.0, random.gauss(0.5, 0.2)))
        data["belief_contradictions"] = max(0, int(random.gauss(2, 1)))
        data["memory_coherence"] = max(0.0, min(1.0, random.gauss(0.8, 0.1)))
        data["attention_focus"] = max(0.0, min(1.0, random.gauss(0.6, 0.15)))
        data["self_awareness_score"] = max(0.0, min(1.0, random.gauss(0.7, 0.1)))
        data["processing_load"] = max(0.0, min(1.0, random.gauss(0.5, 0.2)))
        
        return data
    
    def _calculate_metric_score(self, metric: HealthMetric, data: Dict[str, Any]) -> float:
        """Calculate score for a specific health metric"""
        
        if metric == HealthMetric.COHERENCE:
            # Coherence based on system alignment
            entropy = data.get("entropy_level", 0.5)
            goal_progress = data.get("goal_progress", 0.5)
            emotional_intensity = data.get("emotional_state", {}).get("intensity", 0.5)
            
            # Coherence is high when entropy is balanced, goals are progressing, emotions are stable
            entropy_score = 1.0 - abs(entropy - 0.5) * 2  # Optimal around 0.5
            goal_score = goal_progress
            emotional_score = 1.0 - abs(emotional_intensity - 0.4) * 2  # Slightly calm is optimal
            
            return (entropy_score + goal_score + emotional_score) / 3
            
        elif metric == HealthMetric.ENTROPY_BALANCE:
            # Optimal entropy balance
            entropy = data.get("entropy_level", 0.5)
            optimal_min, optimal_max = self.optimal_entropy_range
            
            if optimal_min <= entropy <= optimal_max:
                return 1.0 - abs(entropy - (optimal_min + optimal_max) / 2) / ((optimal_max - optimal_min) / 2)
            else:
                return max(0.0, 1.0 - abs(entropy - 0.5) * 2)
                
        elif metric == HealthMetric.GOAL_ALIGNMENT:
            # Goal system health
            goal_progress = data.get("goal_progress", 0.5)
            processing_load = data.get("processing_load", 0.5)
            
            # High progress with manageable load is optimal
            progress_score = goal_progress
            load_score = 1.0 - max(0, processing_load - 0.7) * 3  # Penalty for high load
            
            return (progress_score + load_score) / 2
            
        elif metric == HealthMetric.EMOTIONAL_STABILITY:
            # Emotional regulation and stability
            emotional_intensity = data.get("emotional_state", {}).get("intensity", 0.5)
            
            # Moderate emotional intensity is healthy
            if emotional_intensity < 0.2:
                return 0.7  # Too flat emotionally
            elif emotional_intensity > 0.8:
                return 0.3  # Too intense
            else:
                return 0.9  # Good emotional range
                
        elif metric == HealthMetric.BELIEF_CONSISTENCY:
            # Belief system integrity
            contradictions = data.get("belief_contradictions", 0)
            
            # Fewer contradictions = better consistency
            if contradictions == 0:
                return 1.0
            elif contradictions <= 2:
                return 0.8
            elif contradictions <= 5:
                return 0.6
            else:
                return max(0.2, 1.0 - contradictions * 0.1)
                
        elif metric == HealthMetric.MEMORY_INTEGRATION:
            # Memory system health
            return data.get("memory_coherence", 0.5)
            
        elif metric == HealthMetric.ATTENTION_FOCUS:
            # Attention management
            return data.get("attention_focus", 0.5)
            
        elif metric == HealthMetric.SELF_AWARENESS:
            # Self-model accuracy and awareness
            return data.get("self_awareness_score", 0.5)
            
        elif metric == HealthMetric.ADAPTABILITY:
            # Ability to adapt and learn
            # Based on recent changes and learning
            recent_achievements = len(data.get("recent_achievements", []))
            processing_efficiency = 1.0 - data.get("processing_load", 0.5)
            
            adaptability = min(1.0, recent_achievements * 0.2 + processing_efficiency * 0.5 + 0.3)
            return adaptability
            
        elif metric == HealthMetric.RESILIENCE:
            # Recovery from conflicts and stress
            recent_conflicts = len(data.get("recent_conflicts", []))
            emotional_stability = self._calculate_metric_score(HealthMetric.EMOTIONAL_STABILITY, data)
            
            conflict_penalty = min(0.5, recent_conflicts * 0.1)
            resilience = emotional_stability - conflict_penalty + 0.3
            
            return max(0.0, min(1.0, resilience))
        
        return 0.5  # Default neutral score
    
    def _calculate_overall_score(self, metric_scores: Dict[HealthMetric, float]) -> float:
        """Calculate weighted overall health score"""
        total_score = 0.0
        total_weight = 0.0
        
        for metric, score in metric_scores.items():
            weight = self.metric_weights.get(metric, 0.1)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def _categorize_health_level(self, overall_score: float) -> HealthLevel:
        """Categorize overall score into health level"""
        if overall_score >= 0.8:
            return HealthLevel.EXCELLENT
        elif overall_score >= 0.6:
            return HealthLevel.GOOD
        elif overall_score >= 0.4:
            return HealthLevel.MODERATE
        elif overall_score >= 0.2:
            return HealthLevel.POOR
        else:
            return HealthLevel.CRITICAL
    
    def _identify_coherence_factors(self, data: Dict[str, Any], scores: Dict[HealthMetric, float]) -> List[str]:
        """Identify factors contributing to system coherence"""
        factors = []
        
        # High-scoring metrics contribute to coherence
        for metric, score in scores.items():
            if score > 0.7:
                factors.append(f"Strong {metric.value}: {score:.2f}")
        
        # Specific coherence factors
        if data.get("goal_progress", 0) > 0.7:
            factors.append("Goals are progressing well")
        
        if data.get("belief_contradictions", 5) < 2:
            factors.append("Belief system is consistent")
        
        if abs(data.get("entropy_level", 0.5) - 0.5) < 0.2:
            factors.append("Entropy is well-balanced")
        
        return factors[:5]  # Top 5 factors
    
    def _identify_conflict_factors(self, data: Dict[str, Any], scores: Dict[HealthMetric, float]) -> List[str]:
        """Identify factors creating system conflicts"""
        factors = []
        
        # Low-scoring metrics indicate conflicts
        for metric, score in scores.items():
            if score < 0.4:
                factors.append(f"Weakness in {metric.value}: {score:.2f}")
        
        # Specific conflict factors
        if data.get("belief_contradictions", 0) > 3:
            factors.append(f"High belief contradictions: {data['belief_contradictions']}")
        
        entropy = data.get("entropy_level", 0.5)
        if entropy < 0.2 or entropy > 0.8:
            factors.append(f"Entropy imbalance: {entropy:.2f}")
        
        if data.get("processing_load", 0) > 0.8:
            factors.append("High processing load causing strain")
        
        return factors[:5]  # Top 5 factors
    
    def _generate_recommendations(self, scores: Dict[HealthMetric, float], health_level: HealthLevel) -> List[str]:
        """Generate recommendations for improving health"""
        recommendations = []
        
        # Critical health recommendations
        if health_level == HealthLevel.CRITICAL:
            recommendations.append("URGENT: System requires immediate attention to critical issues")
            recommendations.append("Reduce processing load and focus on essential functions")
        
        # Metric-specific recommendations
        for metric, score in scores.items():
            if score < 0.4:
                if metric == HealthMetric.BELIEF_CONSISTENCY:
                    recommendations.append("Review and resolve belief contradictions")
                elif metric == HealthMetric.EMOTIONAL_STABILITY:
                    recommendations.append("Implement emotional regulation techniques")
                elif metric == HealthMetric.GOAL_ALIGNMENT:
                    recommendations.append("Reassess and realign goal priorities")
                elif metric == HealthMetric.ATTENTION_FOCUS:
                    recommendations.append("Improve attention management and reduce distractions")
                elif metric == HealthMetric.ENTROPY_BALANCE:
                    recommendations.append("Adjust entropy levels for optimal balance")
        
        # General recommendations based on health level
        if health_level == HealthLevel.POOR:
            recommendations.append("Focus on strengthening core consciousness functions")
        elif health_level == HealthLevel.MODERATE:
            recommendations.append("Work on identified weak areas for improvement")
        elif health_level == HealthLevel.GOOD:
            recommendations.append("Maintain current healthy patterns and optimize performance")
        elif health_level == HealthLevel.EXCELLENT:
            recommendations.append("Continue excellent practices and explore advanced capabilities")
        
        return recommendations[:7]  # Top 7 recommendations
    
    def _analyze_trends(self) -> Dict[str, float]:
        """Analyze trends in health metrics"""
        if len(self.assessments) < 2:
            return {}
        
        current = self.assessments[-1]
        previous = self.assessments[-2]
        
        trends = {}
        for metric in HealthMetric:
            current_score = current.metric_scores.get(metric, 0.5)
            previous_score = previous.metric_scores.get(metric, 0.5)
            change = current_score - previous_score
            trends[f"{metric.value}_change"] = change
        
        # Overall trend
        overall_change = current.overall_score - previous.overall_score
        trends["overall_change"] = overall_change
        
        return trends
    
    def _identify_risk_factors(self, scores: Dict[HealthMetric, float], data: Dict[str, Any]) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        # Critical score risks
        critical_metrics = [metric for metric, score in scores.items() if score < 0.3]
        if critical_metrics:
            risks.append(f"Critical metrics: {', '.join(m.value for m in critical_metrics)}")
        
        # Specific risk patterns
        if data.get("processing_load", 0) > 0.9:
            risks.append("Extreme processing load - risk of system overload")
        
        if data.get("belief_contradictions", 0) > 5:
            risks.append("High contradiction count - belief system instability")
        
        entropy = data.get("entropy_level", 0.5)
        if entropy < 0.1:
            risks.append("Extremely low entropy - risk of rigid thinking")
        elif entropy > 0.9:
            risks.append("Extremely high entropy - risk of chaotic processing")
        
        # Trend-based risks
        if len(self.assessments) >= 3:
            recent_scores = [a.overall_score for a in self.assessments[-3:]]
            if all(recent_scores[i] > recent_scores[i+1] for i in range(len(recent_scores)-1)):
                risks.append("Declining health trend detected")
        
        return risks[:5]  # Top 5 risks
    
    def _identify_strengths(self, scores: Dict[HealthMetric, float], data: Dict[str, Any]) -> List[str]:
        """Identify system strengths"""
        strengths = []
        
        # High-performing metrics
        excellent_metrics = [metric for metric, score in scores.items() if score > 0.8]
        if excellent_metrics:
            strengths.append(f"Excellent performance: {', '.join(m.value for m in excellent_metrics)}")
        
        # Specific strength patterns
        if data.get("goal_progress", 0) > 0.8:
            strengths.append("High goal achievement rate")
        
        if data.get("belief_contradictions", 5) == 0:
            strengths.append("Perfect belief consistency")
        
        if 0.4 <= data.get("entropy_level", 0.5) <= 0.6:
            strengths.append("Optimal entropy balance maintained")
        
        if data.get("memory_coherence", 0) > 0.9:
            strengths.append("Excellent memory integration")
        
        # Stability as a strength
        if len(self.assessments) >= 3:
            recent_scores = [a.overall_score for a in self.assessments[-3:]]
            if all(abs(recent_scores[i] - recent_scores[i+1]) < 0.1 for i in range(len(recent_scores)-1)):
                if recent_scores[0] > 0.6:  # Only if stable at a good level
                    strengths.append("Stable high performance")
        
        return strengths[:5]  # Top 5 strengths
    
    def _handle_health_crisis(self, assessment: HealthAssessment):
        """Handle critical health situations"""
        print(f"[ConsciousnessHealth] 🚨 HEALTH CRISIS: {assessment.health_level.value} level detected!")
        print(f"[ConsciousnessHealth] 🚨 Overall score: {assessment.overall_score:.3f}")
        print(f"[ConsciousnessHealth] 🚨 Critical factors: {'; '.join(assessment.risk_factors[:3])}")
        print(f"[ConsciousnessHealth] 🚨 Immediate recommendations: {'; '.join(assessment.recommendations[:3])}")
        
        # In a real system, this would trigger emergency protocols
        # For now, just log the crisis
    
    def _update_health_trends(self):
        """Update health trend analysis"""
        if len(self.assessments) < 5:  # Need sufficient data for trends
            return
        
        # Analyze trends for each metric over the last 24 hours
        cutoff_time = datetime.now() - timedelta(seconds=self.trend_analysis_window)
        recent_assessments = [a for a in self.assessments if a.timestamp >= cutoff_time]
        
        if len(recent_assessments) < 3:
            return
        
        for metric in HealthMetric:
            scores = [a.metric_scores.get(metric, 0.5) for a in recent_assessments]
            
            if len(scores) >= 3:
                # Simple trend analysis
                early_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
                late_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
                change_rate = late_avg - early_avg
                
                if abs(change_rate) > 0.1:  # Significant change
                    if change_rate > 0:
                        direction = "improving"
                    else:
                        direction = "declining"
                    
                    trend = HealthTrend(
                        metric=metric,
                        timeframe="24_hours",
                        trend_direction=direction,
                        change_rate=change_rate,
                        significance=abs(change_rate),
                        key_events=[]  # Would be populated with actual events
                    )
                    
                    # Update or add trend
                    existing_trend = next((t for t in self.health_trends if t.metric == metric), None)
                    if existing_trend:
                        existing_trend.trend_direction = direction
                        existing_trend.change_rate = change_rate
                        existing_trend.significance = abs(change_rate)
                    else:
                        self.health_trends.append(trend)
    
    def _get_trend_summary(self) -> Dict[str, Any]:
        """Get summary of current trends"""
        if not self.health_trends:
            return {"status": "insufficient_data"}
        
        improving = [t for t in self.health_trends if t.trend_direction == "improving"]
        declining = [t for t in self.health_trends if t.trend_direction == "declining"]
        
        return {
            "improving_metrics": len(improving),
            "declining_metrics": len(declining),
            "stable_metrics": len(self.health_trends) - len(improving) - len(declining),
            "most_improved": improving[0].metric.value if improving else None,
            "most_declined": declining[0].metric.value if declining else None
        }
    
    def _save_health_data(self):
        """Save health assessment data to file"""
        try:
            data = {
                "assessments": [asdict(assessment) for assessment in self.assessments],
                "health_trends": [asdict(trend) for trend in self.health_trends],
                "statistics": {
                    "total_assessments": len(self.assessments),
                    "average_health_score": sum(a.overall_score for a in self.assessments) / max(1, len(self.assessments)),
                    "health_level_distribution": {
                        level.value: len([a for a in self.assessments if a.health_level == level])
                        for level in HealthLevel
                    },
                    "assessment_frequency": self.assessment_interval,
                    "current_health_level": self.assessments[-1].health_level.value if self.assessments else "unknown"
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            print(f"[ConsciousnessHealth] ❌ Error saving health data: {e}")
    
    def _load_health_data(self):
        """Load health assessment data from file"""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load assessments
                for assessment_data in data.get("assessments", []):
                    assessment_data["timestamp"] = datetime.fromisoformat(assessment_data["timestamp"])
                    assessment_data["health_level"] = HealthLevel(assessment_data["health_level"])
                    
                    # Convert metric scores
                    metric_scores = {}
                    for metric_str, score in assessment_data["metric_scores"].items():
                        metric_scores[HealthMetric(metric_str)] = score
                    assessment_data["metric_scores"] = metric_scores
                    
                    self.assessments.append(HealthAssessment(**assessment_data))
                
                # Load trends
                for trend_data in data.get("health_trends", []):
                    trend_data["metric"] = HealthMetric(trend_data["metric"])
                    self.health_trends.append(HealthTrend(**trend_data))
                
                print(f"[ConsciousnessHealth] ✅ Loaded {len(self.assessments)} health assessments")
                
        except Exception as e:
            print(f"[ConsciousnessHealth] ❌ Error loading health data: {e}")

# Global instance
consciousness_health_scorer = ConsciousnessHealthScorer()