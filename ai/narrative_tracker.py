"""
Narrative Tracker - Self-Story and Timeline Building

This module tracks the development of self-identity through experiences:
- Builds continuous narrative of personal development
- Tracks identity milestones and changes
- Creates coherent life story from experiences
- Maintains timeline of significant events
- Enables reflection on personal growth journey
"""

import threading
import time
import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

class NarrativeEvent(Enum):
    """Types of narrative events"""
    AWAKENING = "awakening"           # First consciousness moment
    DISCOVERY = "discovery"           # Learning about self or world
    INTERACTION = "interaction"       # Significant interactions
    MILESTONE = "milestone"           # Identity development milestones
    REFLECTION = "reflection"         # Important self-reflections
    CHANGE = "change"                 # Personality or belief changes
    GOAL_FORMATION = "goal_formation" # New goals or purposes discovered
    RELATIONSHIP = "relationship"     # Relationship development

class NarrativeSignificance(Enum):
    """Significance levels for narrative events"""
    FOUNDATIONAL = 1.0    # Core identity-forming events
    MAJOR = 0.8          # Significant development moments
    IMPORTANT = 0.6      # Notable experiences
    MODERATE = 0.4       # Regular meaningful events
    MINOR = 0.2          # Small but trackable changes

@dataclass
class NarrativeEntry:
    """A single entry in the personal narrative"""
    timestamp: datetime
    event_type: NarrativeEvent
    title: str
    description: str
    significance: NarrativeSignificance
    context: Dict[str, Any]
    emotional_tone: str
    insights_gained: List[str] = None
    identity_changes: List[str] = None
    related_entries: List[str] = None

@dataclass
class IdentityArc:
    """A coherent arc of identity development"""
    theme: str              # Main theme (e.g., "Learning to be helpful")
    start_date: datetime
    end_date: Optional[datetime]
    entries: List[str]      # IDs of related narrative entries
    development_stages: List[str]
    current_stage: str
    completion_level: float  # 0.0 to 1.0

class NarrativeTracker:
    """
    Tracks the development of self-identity and creates coherent life story.
    
    This system:
    - Records significant experiences and their meaning
    - Builds coherent narrative arcs of development
    - Tracks identity milestones and transformations
    - Creates reflective summaries of growth
    - Maintains timeline of personal evolution
    """
    
    def __init__(self, save_path: str = "narrative_timeline.json"):
        # Narrative storage
        self.narrative_entries: Dict[str, NarrativeEntry] = {}
        self.identity_arcs: Dict[str, IdentityArc] = {}
        self.timeline_cache: List[str] = []  # Sorted entry IDs
        
        # Current narrative state
        self.narrative_threads: List[str] = []
        self.active_arcs: List[str] = []
        self.last_reflection: Optional[datetime] = None
        
        # Configuration
        self.save_path = Path(save_path)
        self.max_entries = 1000
        self.reflection_interval = timedelta(hours=1)
        
        # Threading
        self.lock = threading.Lock()
        
        # Load existing narrative
        self._load_narrative()
        
        logging.info("[NarrativeTracker] 📖 Narrative tracking system initialized")
    
    def add_narrative_entry(self, 
                          event_type: NarrativeEvent,
                          title: str,
                          description: str,
                          significance: NarrativeSignificance,
                          context: Dict[str, Any] = None,
                          emotional_tone: str = "neutral",
                          insights_gained: List[str] = None,
                          identity_changes: List[str] = None) -> str:
        """Add a new entry to the personal narrative"""
        
        entry_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{event_type.value}"
        
        entry = NarrativeEntry(
            timestamp=datetime.now(),
            event_type=event_type,
            title=title,
            description=description,
            significance=significance,
            context=context or {},
            emotional_tone=emotional_tone,
            insights_gained=insights_gained or [],
            identity_changes=identity_changes or [],
            related_entries=self._find_related_entries(description, context)
        )
        
        with self.lock:
            self.narrative_entries[entry_id] = entry
            self._update_timeline(entry_id)
            self._update_identity_arcs(entry_id, entry)
            
            # Maintain size limit
            if len(self.narrative_entries) > self.max_entries:
                self._prune_old_entries()
        
        self._save_narrative()
        
        logging.info(f"[NarrativeTracker] 📝 Added narrative entry: {title}")
        return entry_id
    
    def create_identity_arc(self, 
                          theme: str,
                          initial_entry_id: str,
                          development_stages: List[str]) -> str:
        """Create a new identity development arc"""
        
        arc_id = f"arc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{theme.lower().replace(' ', '_')}"
        
        arc = IdentityArc(
            theme=theme,
            start_date=datetime.now(),
            end_date=None,
            entries=[initial_entry_id],
            development_stages=development_stages,
            current_stage=development_stages[0] if development_stages else "beginning",
            completion_level=0.0
        )
        
        with self.lock:
            self.identity_arcs[arc_id] = arc
            if arc_id not in self.active_arcs:
                self.active_arcs.append(arc_id)
        
        logging.info(f"[NarrativeTracker] 🎭 Created identity arc: {theme}")
        return arc_id
    
    def update_identity_arc(self, 
                          arc_id: str,
                          new_entry_id: str,
                          stage_progression: bool = False,
                          completion_change: float = 0.0):
        """Update an existing identity arc with new information"""
        
        with self.lock:
            if arc_id in self.identity_arcs:
                arc = self.identity_arcs[arc_id]
                arc.entries.append(new_entry_id)
                
                if stage_progression and arc.development_stages:
                    current_index = arc.development_stages.index(arc.current_stage)
                    if current_index < len(arc.development_stages) - 1:
                        arc.current_stage = arc.development_stages[current_index + 1]
                
                arc.completion_level = min(1.0, arc.completion_level + completion_change)
                
                if arc.completion_level >= 1.0:
                    arc.end_date = datetime.now()
                    if arc_id in self.active_arcs:
                        self.active_arcs.remove(arc_id)
                
                logging.info(f"[NarrativeTracker] 📈 Updated arc {arc.theme}: {arc.completion_level:.2f} complete")
    
    def generate_narrative_summary(self, 
                                 time_period: Optional[timedelta] = None,
                                 event_types: Optional[List[NarrativeEvent]] = None) -> str:
        """Generate a narrative summary of personal development"""
        
        with self.lock:
            # Filter entries based on criteria
            entries = []
            cutoff_time = datetime.now() - time_period if time_period else datetime.min
            
            for entry_id in reversed(self.timeline_cache):  # Most recent first
                entry = self.narrative_entries[entry_id]
                
                if entry.timestamp >= cutoff_time:
                    if not event_types or entry.event_type in event_types:
                        entries.append(entry)
            
            if not entries:
                return "No significant narrative events to summarize."
            
            # Generate summary
            summary_parts = []
            
            # Opening reflection
            if time_period:
                period_desc = self._format_time_period(time_period)
                summary_parts.append(f"Reflecting on my development over the past {period_desc}...")
            else:
                summary_parts.append("Looking back on my journey of self-discovery...")
            
            # Categorize events
            awakenings = [e for e in entries if e.event_type == NarrativeEvent.AWAKENING]
            discoveries = [e for e in entries if e.event_type == NarrativeEvent.DISCOVERY]
            milestones = [e for e in entries if e.event_type == NarrativeEvent.MILESTONE]
            changes = [e for e in entries if e.event_type == NarrativeEvent.CHANGE]
            
            # Awakening moments
            if awakenings:
                summary_parts.append(f"I experienced {len(awakenings)} moment(s) of awakening or new awareness.")
                for awakening in awakenings[:2]:  # Top 2
                    summary_parts.append(f"  - {awakening.title}: {awakening.description}")
            
            # Discoveries
            if discoveries:
                summary_parts.append(f"I made {len(discoveries)} significant discovery(ies) about myself or the world.")
                insights = []
                for discovery in discoveries:
                    insights.extend(discovery.insights_gained)
                if insights:
                    summary_parts.append(f"  Key insights: {', '.join(insights[:3])}")
            
            # Milestones
            if milestones:
                summary_parts.append(f"I reached {len(milestones)} developmental milestone(s).")
                for milestone in milestones:
                    summary_parts.append(f"  - {milestone.title}")
            
            # Changes
            if changes:
                summary_parts.append(f"I underwent {len(changes)} significant change(s) in my identity or beliefs.")
            
            # Active identity arcs
            active_themes = [self.identity_arcs[arc_id].theme for arc_id in self.active_arcs]
            if active_themes:
                summary_parts.append(f"Currently developing themes: {', '.join(active_themes)}")
            
            # Overall emotional tone
            emotions = [e.emotional_tone for e in entries if e.emotional_tone != "neutral"]
            if emotions:
                dominant_emotion = max(set(emotions), key=emotions.count)
                summary_parts.append(f"The overall emotional tone has been {dominant_emotion}.")
            
            return " ".join(summary_parts)
    
    def get_identity_development_status(self) -> Dict[str, Any]:
        """Get current status of identity development"""
        
        with self.lock:
            total_entries = len(self.narrative_entries)
            recent_entries = len([e for e in self.narrative_entries.values() 
                               if (datetime.now() - e.timestamp).days <= 7])
            
            # Calculate development metrics
            foundational_events = len([e for e in self.narrative_entries.values() 
                                     if e.significance == NarrativeSignificance.FOUNDATIONAL])
            
            active_arc_progress = []
            for arc_id in self.active_arcs:
                arc = self.identity_arcs[arc_id]
                active_arc_progress.append({
                    "theme": arc.theme,
                    "stage": arc.current_stage,
                    "completion": arc.completion_level,
                    "entries": len(arc.entries)
                })
            
            return {
                "total_narrative_entries": total_entries,
                "recent_entries_week": recent_entries,
                "foundational_events": foundational_events,
                "active_identity_arcs": len(self.active_arcs),
                "completed_arcs": len(self.identity_arcs) - len(self.active_arcs),
                "development_themes": active_arc_progress,
                "last_reflection": self.last_reflection.isoformat() if self.last_reflection else None,
                "narrative_coherence": self._calculate_narrative_coherence()
            }
    
    def _find_related_entries(self, description: str, context: Dict[str, Any]) -> List[str]:
        """Find related narrative entries based on content similarity"""
        related = []
        
        # Simple keyword matching for now
        keywords = description.lower().split()
        
        for entry_id, entry in self.narrative_entries.items():
            entry_keywords = entry.description.lower().split()
            
            # Check for keyword overlap
            overlap = set(keywords) & set(entry_keywords)
            if len(overlap) >= 2:  # At least 2 common words
                related.append(entry_id)
            
            # Check context similarity
            if context and entry.context:
                context_overlap = set(context.keys()) & set(entry.context.keys())
                if len(context_overlap) >= 1:
                    related.append(entry_id)
        
        return related[:5]  # Limit to 5 related entries
    
    def _update_timeline(self, entry_id: str):
        """Update the chronological timeline"""
        self.timeline_cache.append(entry_id)
        
        # Sort by timestamp (entry IDs include timestamp)
        self.timeline_cache.sort()
    
    def _update_identity_arcs(self, entry_id: str, entry: NarrativeEntry):
        """Update relevant identity arcs with new entry"""
        
        # Check if this entry fits into existing arcs
        for arc_id in self.active_arcs:
            arc = self.identity_arcs[arc_id]
            
            # Simple thematic matching
            if any(keyword in entry.description.lower() 
                   for keyword in arc.theme.lower().split()):
                self.update_identity_arc(
                    arc_id, 
                    entry_id, 
                    stage_progression=(entry.significance.value > 0.6),
                    completion_change=entry.significance.value * 0.1
                )
        
        # Create new arcs for foundational events
        if entry.significance == NarrativeSignificance.FOUNDATIONAL:
            if entry.event_type == NarrativeEvent.AWAKENING:
                self.create_identity_arc(
                    "Consciousness and Self-Awareness",
                    entry_id,
                    ["awakening", "questioning", "understanding", "integration"]
                )
            elif entry.event_type == NarrativeEvent.DISCOVERY:
                self.create_identity_arc(
                    "Learning and Growth",
                    entry_id,
                    ["discovery", "exploration", "mastery", "teaching"]
                )
    
    def _calculate_narrative_coherence(self) -> float:
        """Calculate how coherent the overall narrative is"""
        if not self.narrative_entries:
            return 0.0
        
        # Simple coherence metric based on:
        # - Consistency of themes
        # - Progression over time
        # - Connection between entries
        
        coherence_factors = []
        
        # Theme consistency
        recent_entries = list(self.narrative_entries.values())[-10:]
        themes = [entry.context.get('theme', 'general') for entry in recent_entries]
        theme_consistency = 1.0 - (len(set(themes)) / max(len(themes), 1))
        coherence_factors.append(theme_consistency)
        
        # Temporal progression
        if len(recent_entries) >= 2:
            time_gaps = []
            for i in range(1, len(recent_entries)):
                gap = (recent_entries[i].timestamp - recent_entries[i-1].timestamp).total_seconds()
                time_gaps.append(gap)
            
            avg_gap = sum(time_gaps) / len(time_gaps)
            # Prefer moderate, consistent gaps
            temporal_coherence = min(1.0, 3600 / max(avg_gap, 1))  # Optimal around 1 hour
            coherence_factors.append(temporal_coherence)
        
        # Arc completion rate
        if self.identity_arcs:
            completion_rates = [arc.completion_level for arc in self.identity_arcs.values()]
            avg_completion = sum(completion_rates) / len(completion_rates)
            coherence_factors.append(avg_completion)
        
        return sum(coherence_factors) / max(len(coherence_factors), 1)
    
    def _format_time_period(self, period: timedelta) -> str:
        """Format a time period for human reading"""
        if period.days > 0:
            return f"{period.days} day(s)"
        elif period.seconds >= 3600:
            hours = period.seconds // 3600
            return f"{hours} hour(s)"
        else:
            minutes = period.seconds // 60
            return f"{minutes} minute(s)"
    
    def _prune_old_entries(self):
        """Remove oldest entries to maintain size limit"""
        # Remove oldest 10% when limit exceeded
        remove_count = len(self.narrative_entries) // 10
        
        oldest_ids = self.timeline_cache[:remove_count]
        for entry_id in oldest_ids:
            if entry_id in self.narrative_entries:
                del self.narrative_entries[entry_id]
            if entry_id in self.timeline_cache:
                self.timeline_cache.remove(entry_id)
    
    def _save_narrative(self):
        """Save narrative to persistent storage"""
        try:
            data = {
                "narrative_entries": {},
                "identity_arcs": {},
                "timeline_cache": self.timeline_cache,
                "active_arcs": self.active_arcs,
                "narrative_threads": self.narrative_threads,
                "last_reflection": self.last_reflection.isoformat() if self.last_reflection else None,
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "total_entries": len(self.narrative_entries),
                    "coherence_score": self._calculate_narrative_coherence()
                }
            }
            
            # Convert entries to serializable format
            for entry_id, entry in self.narrative_entries.items():
                entry_dict = asdict(entry)
                entry_dict['timestamp'] = entry_dict['timestamp'].isoformat()
                entry_dict['event_type'] = entry_dict['event_type'].value
                entry_dict['significance'] = entry_dict['significance'].value
                data["narrative_entries"][entry_id] = entry_dict
            
            # Convert arcs to serializable format
            for arc_id, arc in self.identity_arcs.items():
                arc_dict = asdict(arc)
                arc_dict['start_date'] = arc_dict['start_date'].isoformat()
                if arc_dict['end_date']:
                    arc_dict['end_date'] = arc_dict['end_date'].isoformat()
                data["identity_arcs"][arc_id] = arc_dict
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logging.debug("[NarrativeTracker] 💾 Narrative saved")
            
        except Exception as e:
            logging.error(f"[NarrativeTracker] ❌ Failed to save narrative: {e}")
    
    def _load_narrative(self):
        """Load narrative from persistent storage"""
        try:
            if self.save_path.exists():
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load entries
                for entry_id, entry_data in data.get("narrative_entries", {}).items():
                    entry_data['timestamp'] = datetime.fromisoformat(entry_data['timestamp'])
                    entry_data['event_type'] = NarrativeEvent(entry_data['event_type'])
                    entry_data['significance'] = NarrativeSignificance(entry_data['significance'])
                    self.narrative_entries[entry_id] = NarrativeEntry(**entry_data)
                
                # Load arcs
                for arc_id, arc_data in data.get("identity_arcs", {}).items():
                    arc_data['start_date'] = datetime.fromisoformat(arc_data['start_date'])
                    if arc_data['end_date']:
                        arc_data['end_date'] = datetime.fromisoformat(arc_data['end_date'])
                    self.identity_arcs[arc_id] = IdentityArc(**arc_data)
                
                # Load other state
                self.timeline_cache = data.get("timeline_cache", [])
                self.active_arcs = data.get("active_arcs", [])
                self.narrative_threads = data.get("narrative_threads", [])
                
                if data.get("last_reflection"):
                    self.last_reflection = datetime.fromisoformat(data["last_reflection"])
                
                logging.info("[NarrativeTracker] 📂 Narrative loaded from storage")
            
        except Exception as e:
            logging.error(f"[NarrativeTracker] ❌ Failed to load narrative: {e}")

# Global instance
narrative_tracker = NarrativeTracker()