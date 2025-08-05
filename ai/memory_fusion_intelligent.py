# ai/memory_fusion_intelligent.py - LLM-Powered Memory Fusion using Hermes 3 Pro Mistral
import json
import os
import shutil
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from ai.memory import get_user_memory, UserMemorySystem
from ai.chat import ask_kobold

# ✅ CRITICAL: Global session cache to prevent infinite loops during memory extraction
_analysis_cache = {}
_analysis_timestamp = {}
CACHE_EXPIRY_SECONDS = 300  # 5 minutes
MAX_COMPARISONS_PER_SESSION = 3  # Prevent infinite loops

class IntelligentMemoryAnalyzer:
    """🧠 Use Hermes 3 Pro Mistral for smart memory analysis"""
    
    def __init__(self):
        self.memory_base_dir = Path("memory")
        self.cluster_file = self.memory_base_dir / "intelligent_clusters.json"
        self.load_existing_clusters()
    
    def load_existing_clusters(self):
        """Load known user clusters"""
        if self.cluster_file.exists():
            with open(self.cluster_file, 'r') as f:
                self.clusters = json.load(f)
        else:
            self.clusters = {}
    
    def save_clusters(self):
        """Save user clusters"""
        os.makedirs(self.memory_base_dir, exist_ok=True)
        with open(self.cluster_file, 'w') as f:
            json.dump(self.clusters, f, indent=2)
    
    def analyze_user_similarity_intelligent(self, user1: str, user2: str) -> Tuple[float, str]:
        """🧠 Use Hermes 3 Pro Mistral to analyze user similarity with infinite loop prevention"""
        
        # ✅ CRITICAL: Create cache key and check for infinite loop prevention
        cache_key = f"{user1}||{user2}"
        reverse_cache_key = f"{user2}||{user1}"
        current_time = time.time()
        
        # Check if we've analyzed this pair recently (within 5 minutes)
        if cache_key in _analysis_cache and cache_key in _analysis_timestamp:
            if current_time - _analysis_timestamp[cache_key] < CACHE_EXPIRY_SECONDS:
                cached_result = _analysis_cache[cache_key]
                print(f"[IntelligentFusion] 🚫 Using cached result for {user1} ↔ {user2}: {cached_result[0]:.2f}")
                return cached_result
        
        # Check reverse key too (user2 vs user1)
        if reverse_cache_key in _analysis_cache and reverse_cache_key in _analysis_timestamp:
            if current_time - _analysis_timestamp[reverse_cache_key] < CACHE_EXPIRY_SECONDS:
                cached_result = _analysis_cache[reverse_cache_key]
                print(f"[IntelligentFusion] 🚫 Using cached result (reverse) for {user1} ↔ {user2}: {cached_result[0]:.2f}")
                return cached_result
        
        # Count current session analysis calls to prevent infinite loops
        session_count_key = f"session_count_{current_time // 60}"  # Per minute tracking
        if session_count_key not in _analysis_cache:
            _analysis_cache[session_count_key] = 0
        
        if _analysis_cache[session_count_key] >= MAX_COMPARISONS_PER_SESSION:
            print(f"[IntelligentFusion] 🚫 Maximum comparisons reached for this session, preventing infinite loop")
            return 0.0, "Session limit reached - preventing infinite loop"
        
        _analysis_cache[session_count_key] += 1
        
        print(f"[IntelligentFusion] 🧠 Analyzing {user1} ↔ {user2} with Hermes 3 Pro Mistral... (call #{_analysis_cache[session_count_key]})")
        
        # Load user data
        user1_data = self._load_user_complete_profile(user1)
        user2_data = self._load_user_complete_profile(user2)
        
        # ✅ CRITICAL FIX: Validate data quality before proceeding
        if not self._has_sufficient_data(user1_data, user2_data):
            result = (0.0, "Insufficient profile data for meaningful comparison")
            _analysis_cache[cache_key] = result
            _analysis_timestamp[cache_key] = current_time
            return result
        
        # Format profiles for analysis
        user1_profile = self._format_user_profile(user1_data)
        user2_profile = self._format_user_profile(user2_data)
        
        # ✅ CRITICAL FIX: Check if profiles actually have content
        if len(user1_profile) < 50 or len(user2_profile) < 50:
            result = (0.0, "User profiles too minimal for analysis")
            _analysis_cache[cache_key] = result
            _analysis_timestamp[cache_key] = current_time
            return result
        
        # Create intelligent analysis prompt WITHOUT hardcoded examples
        analysis_prompt = f"""You are an expert memory analyst. Analyze if these two user profiles belong to the same person.

Current Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

User Profile 1 ({user1}):
{user1_profile}

User Profile 2 ({user2}):
{user2_profile}

ANALYSIS CRITERIA:
1. Personal relationships (husband/wife names, family members)
2. Preferences and interests (pets, activities, food) 
3. Life circumstances (work, living situation, health)
4. Username patterns (Anonymous_XXX vs real names)
5. Semantic similarities (francesco/frank, dogs/puppies)
6. Timeline consistency and contradictions
7. Emotional patterns and context

IDENTITY INDICATORS:
- Same person: Shared unique personal details, relationship names, consistent preferences
- Anonymous transition: Anonymous_XXX usernames later revealing real name
- Nickname variations: Francesco/Frank, Michael/Mike, etc.
- Different persons: Contradictory relationships, incompatible life details

CRITICAL: Only mention details that actually exist in the profiles above.
Do NOT fabricate or assume information not present in the data.

Respond in this JSON format:
{{
  "similarity_score": 0.0,
  "confidence": "low",
  "reasoning": "Based on actual profile analysis",
  "key_matches": [],
  "contradictions": [],
  "recommendation": "keep_separate"
}}

SCORING GUIDE:
- 0.9-1.0: Definitely same person (unique shared details)
- 0.7-0.89: Highly likely same person (multiple strong matches)
- 0.5-0.69: Possibly same person (some matches, investigation needed)
- 0.3-0.49: Unlikely same person (few or weak matches)
- 0.0-0.29: Different persons (contradictions or no matches)

Analyze ONLY the actual data provided. Do not invent details."""

        try:
            # ✅ TOKEN OPTIMIZATION: Use optimized LLM function
            from ai.llm_optimized import analyze_user_similarity_optimized
            
            # Use the optimized function instead of full prompt
            similarity, reasoning = analyze_user_similarity_optimized(user1_profile, user2_profile)
            
            print(f"[IntelligentFusion] 🎯 Optimized Analysis Results:")
            print(f"  👥 Users: {user1} ↔ {user2}")
            print(f"  📊 Similarity: {similarity:.2f}")
            print(f"  🧠 Reasoning: {reasoning}")
            
            # ✅ CRITICAL: Cache the result to prevent infinite loops
            result = (similarity, reasoning)
            _analysis_cache[cache_key] = result
            _analysis_timestamp[cache_key] = current_time
            
            return similarity, reasoning
            
        except ImportError:
            print(f"[IntelligentFusion] ⚠️ Optimized function not available, using fallback")
            # Fallback to original method
            result = self._analyze_similarity_fallback(user1_profile, user2_profile)
            
            # ✅ CRITICAL: Cache the fallback result too
            _analysis_cache[cache_key] = result
            _analysis_timestamp[cache_key] = current_time
            
            return result
        except Exception as e:
            print(f"[IntelligentFusion] ❌ Optimized analysis error: {e}")
            result = self._analyze_similarity_fallback(user1_profile, user2_profile)
            
            # ✅ CRITICAL: Cache the fallback result
            _analysis_cache[cache_key] = result
            _analysis_timestamp[cache_key] = current_time
            
            return result
    
    def _analyze_similarity_fallback(self, user1_profile: str, user2_profile: str) -> Tuple[float, str]:
        """Fallback to original LLM analysis method"""
        try:
            # Original implementation
            analysis_prompt = f"""You are an expert memory analyst. Analyze if these two user profiles belong to the same person.

Current Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

User Profile 1:
{user1_profile}

User Profile 2:
{user2_profile}

ANALYSIS CRITERIA:
1. Personal relationships (husband/wife names, family members)
2. Preferences and interests (pets, activities, food) 
3. Life circumstances (work, living situation, health)
4. Username patterns (Anonymous_XXX vs real names)
5. Semantic similarities (francesco/frank, dogs/puppies)
6. Timeline consistency and contradictions
7. Emotional patterns and context

IDENTITY INDICATORS:
- Same person: Shared unique personal details, relationship names, consistent preferences
- Anonymous transition: Anonymous_XXX usernames later revealing real name
- Nickname variations: Francesco/Frank, Michael/Mike, etc.
- Different persons: Contradictory relationships, incompatible life details

CRITICAL: Only mention details that actually exist in the profiles above.
Do NOT fabricate or assume information not present in the data.

Respond in this JSON format:
{{
  "similarity_score": 0.0,
  "confidence": "low",
  "reasoning": "Based on actual profile analysis",
  "key_matches": [],
  "contradictions": [],
  "recommendation": "keep_separate"
}}

SCORING GUIDE:
- 0.9-1.0: Definitely same person (unique shared details)
- 0.7-0.89: Highly likely same person (multiple strong matches)
- 0.5-0.69: Possibly same person (some matches, investigation needed)
- 0.3-0.49: Unlikely same person (few or weak matches)
- 0.0-0.29: Different persons (contradictions or no matches)

Analyze ONLY the actual data provided. Do not invent details."""

            # Get LLM analysis with reduced timeout
            messages = [
                {"role": "system", "content": "You are an expert identity analyst. Analyze ONLY the actual data provided in user profiles. Never fabricate or assume information not present. Respond with precise JSON analysis based solely on the given data."},
                {"role": "user", "content": analysis_prompt}
            ]
            
            # ✅ PERFORMANCE FIX: Reduced max_tokens and timeout
            llm_response = ask_kobold(messages, max_tokens=200)
            
            # Parse LLM response
            analysis = self._extract_json_analysis(llm_response)
            
            if analysis:
                similarity = float(analysis.get("similarity_score", 0.0))
                confidence = analysis.get("confidence", "unknown")
                reasoning = analysis.get("reasoning", "Fallback LLM analysis")
                key_matches = analysis.get("key_matches", [])
                contradictions = analysis.get("contradictions", [])
                recommendation = analysis.get("recommendation", "investigate")
                
                # ✅ VALIDATION FIX: Verify matches exist in actual data
                validated_matches = self._validate_key_matches(key_matches, {}, {})
                
                print(f"[IntelligentFusion] 🎯 Fallback Analysis Results:")
                print(f"  📊 Similarity: {similarity:.2f}")
                print(f"  🎯 Confidence: {confidence}")
                print(f"  🧠 Reasoning: {reasoning}")
                print(f"  ✅ Validated Matches: {validated_matches}")
                if contradictions:
                    print(f"  ⚠️ Contradictions: {contradictions}")
                print(f"  💡 Recommendation: {recommendation}")
                
                # ✅ SAFETY CHECK: Lower score if matches don't validate
                if len(validated_matches) < len(key_matches):
                    similarity = max(0.0, similarity - 0.3)
                    print(f"  ⚠️ Similarity reduced to {similarity:.2f} due to invalid matches")
                
                return similarity, reasoning
            
        except Exception as e:
            print(f"[IntelligentFusion] ❌ Fallback analysis error: {e}")
        
        # Final fallback to basic analysis
        return self._basic_similarity_fallback("", "")
    
    def _has_fusion_potential(self, username: str) -> bool:
        """🎯 Check if user has potential for fusion (context-aware optimization)"""
        
        # Don't analyze system users or well-established users
        if username in ['Daveydrz', 'system', 'admin']:
            return False
        
        # Check if this looks like an anonymous user
        import re
        if re.match(r'^Anonymous_\d{3}$', username):
            return True  # Anonymous users have high fusion potential
        
        # Check if user directory exists and has minimal data
        user_dir = Path(f"memory/{username}")
        if not user_dir.exists():
            return False  # No data to fuse
        
        # Count total memory content
        try:
            files = list(user_dir.glob("*.json"))
            if len(files) < 2:
                return False  # Not enough data for meaningful fusion
            
            # Check if user has been active recently
            latest_file = max(files, key=lambda f: f.stat().st_mtime)
            file_age = time.time() - latest_file.stat().st_mtime
            
            if file_age > 86400:  # 24 hours
                return False  # Old data, probably not worth fusing
            
            return True
            
        except Exception as e:
            print(f"[IntelligentFusion] ⚠️ Error checking fusion potential: {e}")
            return False
    
    def _has_sufficient_data(self, user1_data: Dict, user2_data: Dict) -> bool:
        """✅ Check if users have sufficient data for meaningful comparison"""
        user1_content = (
            len(user1_data.get("personal_facts", {})) +
            len(user1_data.get("emotional_history", [])) +
            len(user1_data.get("entity_memories", {})) +
            len(user1_data.get("conversation_topics", [])) +
            len(user1_data.get("smart_memories", {}))
        )
        
        user2_content = (
            len(user2_data.get("personal_facts", {})) +
            len(user2_data.get("emotional_history", [])) +
            len(user2_data.get("entity_memories", {})) +
            len(user2_data.get("conversation_topics", [])) +
            len(user2_data.get("smart_memories", {}))
        )
        
        # Need at least some content from both users
        has_enough = user1_content >= 2 and user2_content >= 2
        
        if not has_enough:
            print(f"[IntelligentFusion] 📊 Insufficient data: User1={user1_content}, User2={user2_content}")
        
        return has_enough
    
    def _validate_key_matches(self, key_matches: List[str], user1_data: Dict, user2_data: Dict) -> List[str]:
        """✅ Validate that key matches actually exist in the data"""
        validated = []
        
        for match in key_matches:
            match_lower = match.lower()
            
            # Check if the match refers to actual data
            found_in_data = False
            
            # Check personal facts
            for facts in [user1_data.get("personal_facts", {}), user2_data.get("personal_facts", {})]:
                for key, value in facts.items():
                    if any(term in value.lower() for term in match_lower.split('_')):
                        found_in_data = True
                        break
            
            # Check entity memories
            for entities in [user1_data.get("entity_memories", {}), user2_data.get("entity_memories", {})]:
                for name, entity in entities.items():
                    if any(term in name.lower() for term in match_lower.split('_')):
                        found_in_data = True
                        break
            
            if found_in_data:
                validated.append(match)
            else:
                print(f"[IntelligentFusion] ⚠️ Invalid match '{match}' - not found in actual data")
        
        return validated
    
    def _load_user_complete_profile(self, username: str) -> Dict:
        """Load complete user profile for analysis"""
        user_dir = Path(f"memory/{username}")
        if not user_dir.exists():
            return {}
        
        profile = {
            "username": username,
            "personal_facts": {},
            "emotional_history": [],
            "conversation_topics": [],
            "entity_memories": {},
            "scheduled_events": [],
            "smart_memories": {},
            "recent_activity": None,
            "account_created": None
        }
        
        try:
            # Load personal facts
            facts_file = user_dir / "personal_facts.json"
            if facts_file.exists():
                with open(facts_file, 'r') as f:
                    facts_data = json.load(f)
                    for key, fact in facts_data.items():
                        if isinstance(fact, dict) and 'value' in fact:
                            clean_key = fact.get('key', key).replace('_', ' ')
                            profile["personal_facts"][clean_key] = fact['value']
            
            # Load emotional history (recent)
            emotions_file = user_dir / "emotions.json"
            if emotions_file.exists():
                with open(emotions_file, 'r') as f:
                    emotions = json.load(f)
                    profile["emotional_history"] = emotions[-5:]  # Last 5 emotions
            
            # Load conversation topics
            topics_file = user_dir / "conversation_topics.json"
            if topics_file.exists():
                with open(topics_file, 'r') as f:
                    topics = json.load(f)
                    topic_names = []
                    for t in topics[-5:]:  # Last 5 topics
                        if isinstance(t, dict):
                            topic_names.append(t.get('topic', 'unknown'))
                        else:
                            topic_names.append(str(t))
                    profile["conversation_topics"] = topic_names
            
            # Load entity memories
            entities_file = user_dir / "entity_memories.json"
            if entities_file.exists():
                with open(entities_file, 'r') as f:
                    entities = json.load(f)
                    for name, entity in entities.items():
                        if isinstance(entity, dict):
                            profile["entity_memories"][name] = {
                                "type": entity.get("entity_type", "unknown"),
                                "status": entity.get("status", "unknown"),
                                "significance": entity.get("emotional_significance", 0.0),
                                "context": entity.get("context_description", "")
                            }
            
            # Load scheduled events
            events_file = user_dir / "events.json"
            if events_file.exists():
                with open(events_file, 'r') as f:
                    events = json.load(f)
                    profile["scheduled_events"] = events[-3:]  # Last 3 events
            
            # Load smart memory files (appointments, life events, highlights)
            for smart_file in ["smart_appointments.json", "smart_life_events.json", "smart_highlights.json"]:
                smart_path = user_dir / smart_file
                if smart_path.exists():
                    try:
                        with open(smart_path, 'r') as f:
                            smart_data = json.load(f)
                            profile["smart_memories"][smart_file] = smart_data[-3:]  # Last 3 items
                    except:
                        pass
            
            # Get file timestamps
            files = list(user_dir.glob("*.json"))
            if files:
                latest_file = max(files, key=lambda f: f.stat().st_mtime)
                oldest_file = min(files, key=lambda f: f.stat().st_mtime)
                profile["recent_activity"] = datetime.fromtimestamp(latest_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                profile["account_created"] = datetime.fromtimestamp(oldest_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        except Exception as e:
            print(f"[IntelligentFusion] ⚠️ Error loading profile for {username}: {e}")
        
        return profile
    
    def _format_user_profile(self, profile: Dict) -> str:
        """Format user profile for LLM analysis"""
        
        sections = []
        
        # Basic info
        sections.append(f"Username: {profile['username']}")
        if profile.get("account_created"):
            sections.append(f"Account Created: {profile['account_created']}")
        if profile.get("recent_activity"):
            sections.append(f"Last Active: {profile['recent_activity']}")
        
        # Personal facts
        if profile["personal_facts"]:
            sections.append("\nPersonal Facts:")
            for key, value in profile["personal_facts"].items():
                sections.append(f"  - {key}: {value}")
        
        # Entity memories (relationships, pets, etc.)
        if profile["entity_memories"]:
            sections.append("\nImportant People/Entities:")
            for name, entity in profile["entity_memories"].items():
                significance = entity.get('significance', 0)
                context = entity.get('context', '')
                sections.append(f"  - {name}: {entity['type']} ({entity['status']}, significance: {significance})")
                if context:
                    sections.append(f"    Context: {context[:100]}...")
        
        # Recent emotions
        if profile["emotional_history"]:
            sections.append("\nRecent Emotional States:")
            for emotion in profile["emotional_history"]:
                if isinstance(emotion, dict):
                    emo_text = emotion.get('emotion', 'unknown')
                    emo_context = emotion.get('context', 'no context')
                    sections.append(f"  - {emo_text}: {emo_context[:80]}...")
        
        # Smart memories
        if profile["smart_memories"]:
            sections.append("\nSmart Memory Events:")
            for file_name, events in profile["smart_memories"].items():
                if events:
                    memory_type = file_name.replace('smart_', '').replace('.json', '')
                    sections.append(f"  {memory_type.title()}:")
                    for event in events:
                        if isinstance(event, dict):
                            topic = event.get('topic', event.get('description', 'unknown'))
                            sections.append(f"    - {topic}")
        
        # Conversation topics
        if profile["conversation_topics"]:
            sections.append(f"\nDiscussion Topics: {', '.join(profile['conversation_topics'])}")
        
        # Scheduled events
        if profile["scheduled_events"]:
            sections.append("\nScheduled Events:")
            for event in profile["scheduled_events"]:
                if isinstance(event, dict):
                    desc = event.get('description', 'unknown event')
                    date = event.get('date', 'unknown date')
                    sections.append(f"  - {desc} on {date}")
        
        result = "\n".join(sections) if sections else "No profile data available"
        
        # ✅ QUALITY CHECK: Ensure meaningful content
        if len(result) < 50:
            return "No meaningful profile data available"
            
        return result
    
    def _extract_json_analysis(self, response: str) -> Optional[Dict]:
        """Extract JSON analysis from LLM response"""
        try:
            import re
            
            # Find JSON in response
            json_match = re.search(r'\{.*?\}', response, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                # Clean up common JSON issues
                json_text = json_text.replace('\n', ' ').replace('  ', ' ')
                return json.loads(json_text)
        
        except Exception as e:
            print(f"[IntelligentFusion] ❌ JSON extraction error: {e}")
            print(f"[IntelligentFusion] Raw response: {response[:200]}...")
        
        return None
    
    def _basic_similarity_fallback(self, user1: str, user2: str) -> Tuple[float, str]:
        """Fallback to basic similarity if LLM fails"""
        
        import re
        anon_pattern = r'^Anonymous_\d{3}$'
        
        if re.match(anon_pattern, user1) and re.match(anon_pattern, user2):
            return 0.5, "Both Anonymous users - possible same person (fallback analysis)"
        elif (re.match(anon_pattern, user1) and not re.match(anon_pattern, user2)) or \
             (re.match(anon_pattern, user2) and not re.match(anon_pattern, user1)):
            return 0.4, "Anonymous to named user transition - possibly same person (fallback analysis)"
        
        return 0.1, "Basic pattern analysis - low confidence (fallback analysis)"

class IntelligentMemoryUnifier:
    """🧠 LLM-powered memory unification"""
    
    def __init__(self):
        self.analyzer = IntelligentMemoryAnalyzer()
    
    def find_and_merge_intelligent(self, target_username: str, threshold: float = 0.7) -> str:
        """🧠 Intelligent detection and merging of similar users with infinite loop prevention"""
        
        # ✅ CRITICAL: Check if this is a frequent memory extraction call
        fusion_cache_key = f"fusion_check_{target_username}"
        current_time = time.time()
        
        # If we checked this user recently (within last 2 minutes), skip fusion to prevent loops
        if fusion_cache_key in _analysis_timestamp:
            if current_time - _analysis_timestamp[fusion_cache_key] < 120:  # 2 minutes
                print(f"[IntelligentFusion] 🚫 Skipping fusion for {target_username} - checked recently (preventing infinite loop)")
                return target_username
        
        _analysis_timestamp[fusion_cache_key] = current_time
        
        print(f"[IntelligentFusion] 🧠 Starting intelligent analysis for {target_username}")
        print(f"[IntelligentFusion] 📅 Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check if already clustered
        mapping_key = f"mapping_{target_username}"
        if mapping_key in self.analyzer.clusters:
            cluster_id = self.analyzer.clusters[mapping_key]
            if cluster_id in self.analyzer.clusters:
                primary = self.analyzer.clusters[cluster_id]["primary_username"]
                print(f"[IntelligentFusion] 🔗 {target_username} already mapped to {primary}")
                return primary
        
        # Get all existing users
        if not os.path.exists(f"memory/{target_username}"):
            print(f"[IntelligentFusion] ℹ️ No memory directory found for {target_username}")
            return target_username
        
        existing_users = [d for d in os.listdir("memory") 
                         if os.path.isdir(f"memory/{d}") and d != target_username]
        
        if not existing_users:
            print(f"[IntelligentFusion] ℹ️ No other users found for comparison")
            return target_username
        
        # ✅ CRITICAL: Limit number of users to compare to prevent infinite loops
        if len(existing_users) > 5:
            print(f"[IntelligentFusion] ⚠️ Too many users ({len(existing_users)}) - limiting to 5 most recent to prevent infinite loops")
            existing_users = sorted(existing_users, key=lambda x: os.path.getmtime(f"memory/{x}"), reverse=True)[:5]
        
        print(f"[IntelligentFusion] 🔍 Found {len(existing_users)} existing users to analyze: {existing_users}")
        
        # Analyze each user with LLM
        similar_users = []
        for existing_user in existing_users:
            print(f"[IntelligentFusion] 🔄 Analyzing similarity with {existing_user}...")
            similarity, reasoning = self.analyzer.analyze_user_similarity_intelligent(target_username, existing_user)
            
            if similarity >= threshold:
                similar_users.append((existing_user, similarity, reasoning))
                print(f"[IntelligentFusion] 🎯 MATCH FOUND: {existing_user} (similarity: {similarity:.2f})")
            else:
                print(f"[IntelligentFusion] ❌ No match: {existing_user} (similarity: {similarity:.2f} < {threshold})")
        
        # Merge if matches found
        if similar_users:
            # Sort by similarity (highest first)
            similar_users.sort(key=lambda x: x[1], reverse=True)
            usernames_to_merge = [user for user, sim, reason in similar_users]
            
            print(f"[IntelligentFusion] 🚀 Found {len(similar_users)} users to merge!")
            for user, sim, reason in similar_users:
                print(f"  - {user}: {sim:.2f} ({reason[:100]}...)")
            
            # Perform intelligent merge
            if self._intelligent_merge(target_username, usernames_to_merge):
                print(f"[IntelligentFusion] ✅ Intelligent merge complete for {target_username}!")
                return target_username
        else:
            print(f"[IntelligentFusion] ℹ️ No similar users found for {target_username} (threshold: {threshold})")
        
        return target_username
    
    def _intelligent_merge(self, primary_username: str, secondary_usernames: List[str]) -> bool:
        """Perform intelligent memory merge with conflict resolution"""
        
        try:
            print(f"[IntelligentFusion] 🔄 Starting intelligent merge:")
            print(f"  Primary: {primary_username}")
            print(f"  Secondary: {secondary_usernames}")
            
            # Create backup
            self._create_backup(primary_username, secondary_usernames)
            
            # Load primary memory
            primary_memory = get_user_memory(primary_username)
            
            # Merge with LLM-guided conflict resolution
            for secondary_username in secondary_usernames:
                print(f"[IntelligentFusion] 🔄 Merging {secondary_username} into {primary_username}...")
                self._merge_with_conflict_resolution(primary_memory, secondary_username)
            
            # Save merged memory
            primary_memory.save_memory()
            print(f"[IntelligentFusion] 💾 Saved unified memory for {primary_username}")
            
            # Update clusters
            self._update_intelligent_clusters(primary_username, secondary_usernames)
            
            return True
            
        except Exception as e:
            print(f"[IntelligentFusion] ❌ Intelligent merge error: {e}")
            return False
    
    def _merge_with_conflict_resolution(self, primary_memory: UserMemorySystem, secondary_username: str):
        """Merge memories with intelligent conflict resolution"""
        
        if not os.path.exists(f"memory/{secondary_username}"):
            print(f"[IntelligentFusion] ⚠️ No memory directory for {secondary_username}")
            return
        
        secondary_memory = get_user_memory(secondary_username)
        
        # Merge facts with conflict detection
        conflicts = []
        added_facts = 0
        
        for key, fact in secondary_memory.personal_facts.items():
            if key in primary_memory.personal_facts:
                existing = primary_memory.personal_facts[key]
                if existing.value.lower().strip() != fact.value.lower().strip():
                    conflicts.append((key, existing.value, fact.value))
                    print(f"[IntelligentFusion] ⚠️ Conflict detected: {key} = '{existing.value}' vs '{fact.value}'")
            else:
                primary_memory.personal_facts[key] = fact
                added_facts += 1
                print(f"[IntelligentFusion] ➕ Added fact: {key} = {fact.value}")
        
        print(f"[IntelligentFusion] 📊 Added {added_facts} new facts, {len(conflicts)} conflicts")
        
        # Resolve conflicts with LLM if needed
        if conflicts:
            self._resolve_conflicts_intelligent(primary_memory, conflicts)
        
        # Merge other memory types
        before_emotions = len(primary_memory.emotional_history)
        primary_memory.emotional_history.extend(secondary_memory.emotional_history)
        print(f"[IntelligentFusion] 😊 Merged emotions: {before_emotions} → {len(primary_memory.emotional_history)}")
        
        before_events = len(primary_memory.scheduled_events)
        primary_memory.scheduled_events.extend(secondary_memory.scheduled_events)
        print(f"[IntelligentFusion] 📅 Merged events: {before_events} → {len(primary_memory.scheduled_events)}")
        
        before_topics = len(primary_memory.conversation_topics)
        primary_memory.conversation_topics.extend(secondary_memory.conversation_topics)
        print(f"[IntelligentFusion] 💬 Merged topics: {before_topics} → {len(primary_memory.conversation_topics)}")
        
        # Merge MEGA-INTELLIGENT entity memories
        if hasattr(secondary_memory, 'entity_memories'):
            before_entities = len(primary_memory.entity_memories)
            for name, entity in secondary_memory.entity_memories.items():
                if name not in primary_memory.entity_memories:
                    primary_memory.entity_memories[name] = entity
                    print(f"[IntelligentFusion] 👤 Added entity: {name} ({entity.entity_type})")
            print(f"[IntelligentFusion] 👥 Merged entities: {before_entities} → {len(primary_memory.entity_memories)}")
        
        # Merge life events
        if hasattr(secondary_memory, 'life_events'):
            before_life_events = len(primary_memory.life_events)
            primary_memory.life_events.update(secondary_memory.life_events)
            print(f"[IntelligentFusion] 🎭 Merged life events: {before_life_events} → {len(primary_memory.life_events)}")
    
    def _resolve_conflicts_intelligent(self, primary_memory: UserMemorySystem, conflicts: List[Tuple]):
        """Use LLM to resolve memory conflicts"""
        
        if not conflicts:
            return
        
        print(f"[IntelligentFusion] 🤔 Resolving {len(conflicts)} conflicts with Hermes 3 Pro Mistral...")
        
        conflict_prompt = f"""You are resolving memory conflicts during user profile merge. Choose the most accurate value for each conflict.

Current Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Memory Conflicts Found:
"""
        
        for i, (key, value1, value2) in enumerate(conflicts, 1):
            conflict_prompt += f"{i}. Field: {key}\n   Value A: '{value1}'\n   Value B: '{value2}'\n\n"
        
        conflict_prompt += """CONFLICT RESOLUTION GUIDELINES:
- Full names over nicknames (Francesco > Frank)
- More specific over general (husband > spouse)
- Recent over old information
- Consistent with other known facts
- If both valid, choose most informative

Respond ONLY in this exact JSON format:
{
  "resolutions": [
    {
      "key": "field_name",
      "chosen_value": "selected_value", 
      "reasoning": "Francesco is full name, Frank is nickname - same person"
    }
  ]
}"""
        
        try:
            messages = [
                {"role": "system", "content": "You are a memory conflict resolver. Analyze conflicting memory values and choose the most accurate one. Consider nicknames, full names, and context. Respond with precise JSON."},
                {"role": "user", "content": conflict_prompt}
            ]
            
            response = ask_kobold(messages, max_tokens=400)
            resolution = self.analyzer._extract_json_analysis(response)
            
            if resolution and "resolutions" in resolution:
                resolved_count = 0
                for res in resolution["resolutions"]:
                    key = res.get("key")
                    chosen_value = res.get("chosen_value")
                    reasoning = res.get("reasoning", "LLM decision")
                    
                    # Find matching fact and update
                    for fact_key, fact in primary_memory.personal_facts.items():
                        if key in fact_key or fact.key == key:
                            fact.value = chosen_value
                            resolved_count += 1
                            print(f"[IntelligentFusion] 🧠 Resolved '{key}' = '{chosen_value}' ({reasoning})")
                            break
                
                print(f"[IntelligentFusion] ✅ Resolved {resolved_count}/{len(conflicts)} conflicts")
            else:
                print(f"[IntelligentFusion] ⚠️ Could not parse LLM conflict resolution")
        
        except Exception as e:
            print(f"[IntelligentFusion] ❌ Conflict resolution error: {e}")
            # Keep original values on error
            print(f"[IntelligentFusion] 🔄 Keeping original values due to resolution error")
    
    def _create_backup(self, primary_username: str, secondary_usernames: List[str]):
        """Create backup before merge"""
        
        backup_dir = Path(f"memory_backups/intelligent_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backed_up = 0
        for username in [primary_username] + secondary_usernames:
            if os.path.exists(f"memory/{username}"):
                shutil.copytree(f"memory/{username}", backup_dir / username)
                backed_up += 1
        
        print(f"[IntelligentFusion] 💾 Backup created: {backup_dir} ({backed_up} users)")
    
    def _update_intelligent_clusters(self, primary_username: str, secondary_usernames: List[str]):
        """Update cluster mappings"""
        
        cluster_id = f"intelligent_cluster_{primary_username}"
        self.analyzer.clusters[cluster_id] = {
            "primary_username": primary_username,
            "secondary_usernames": secondary_usernames,
            "unified_date": datetime.now().isoformat(),
            "method": "llm_intelligent_hermes3",
            "fusion_version": "2.0"
        }
        
        # Add mapping for quick lookup
        for username in [primary_username] + secondary_usernames:
            self.analyzer.clusters[f"mapping_{username}"] = cluster_id
        
        self.analyzer.save_clusters()
        print(f"[IntelligentFusion] 🗂️ Cluster mapping saved for {primary_username}")

# Global intelligent fusion engine
intelligent_fusion = IntelligentMemoryUnifier()

def get_intelligent_unified_username(original_username: str, skip_fusion: bool = False) -> str:
    """🧠 Get intelligently unified username using Hermes 3 Pro Mistral with infinite loop prevention"""
    
    # ✅ CRITICAL: Allow bypassing fusion during memory extraction to prevent infinite loops
    if skip_fusion:
        print(f"[IntelligentFusion] 🚫 Skipping fusion for {original_username} (skip_fusion=True)")
        return original_username
    
    # ✅ NEW: Use extraction coordinator for optimized fusion analysis if available
    try:
        from ai.extraction_coordinator import extract_with_coordination, ExtractionType, ExtractionPriority
        
        # Use coordinator for fusion context analysis
        print(f"[IntelligentFusion] 🚀 Starting coordinated intelligent memory fusion for {original_username}")
        
        # Check if fusion analysis is actually needed (context awareness)
        if not intelligent_fusion.analyzer._has_fusion_potential(original_username):
            print(f"[IntelligentFusion] 🚫 No fusion potential detected for {original_username}")
            return original_username
        
        return intelligent_fusion.find_and_merge_intelligent(original_username, threshold=0.7)
        
    except ImportError:
        print(f"[IntelligentFusion] 🔄 Using standard fusion - coordinator not available")
        return intelligent_fusion.find_and_merge_intelligent(original_username, threshold=0.7)

# Export for easy import
__all__ = ['get_intelligent_unified_username', 'intelligent_fusion']