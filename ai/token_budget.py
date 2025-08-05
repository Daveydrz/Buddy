"""
Token Budget Management System
Created: 2025-01-17
Purpose: Prevent context overflow and manage LLM token limits with intelligent trimming
         Respects MAX_CONTEXT_TOKENS configuration and preserves important content
"""

import json
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import math

# Import configuration
try:
    from config import MAX_CONTEXT_TOKENS
except ImportError:
    MAX_CONTEXT_TOKENS = 1500

class TokenBudgetManager:
    """
    Budget management system to prevent context overflow
    Intelligent trimming that preserves symbolic tokens and important content
    """
    
    def __init__(self, max_tokens: int = MAX_CONTEXT_TOKENS):
        self.max_tokens = max_tokens
        self.reserved_tokens = {
            'system_prompt': 200,
            'response_buffer': 300,
            'safety_margin': 100
        }
        
        # Token priorities (higher number = higher priority)
        self.token_priorities = {
            'symbolic_tokens': 10,
            'personality_tokens': 9,
            'memory_tokens': 8,
            'entity_tokens': 7,
            'factual_tokens': 6,
            'behavioral_tokens': 5,
            'recent_context': 4,
            'user_input': 9,
            'system_instructions': 10,
            'safety_tokens': 10
        }
        
        # Token type patterns for classification
        self.token_patterns = {
            'symbolic_tokens': r'<[^>]+>',
            'personality_tokens': r'<pers\d+:[^>]+>',
            'memory_tokens': r'<mem\d+:[^>]+>',
            'entity_tokens': r'<ent_[^>]+>',
            'factual_tokens': r'<fact_[^>]+>',
            'behavioral_tokens': r'<behav_[^>]+>'
        }
        
        # Budget allocation strategy
        self.budget_allocation = {
            'symbolic_tokens': 0.20,  # 20% for symbolic tokens
            'conversation_context': 0.35,  # 35% for conversation
            'user_input': 0.15,  # 15% for current input
            'memory_context': 0.20,  # 20% for memory
            'buffer': 0.10  # 10% buffer
        }
        
        # Token counting cache
        self.token_cache = {}
        self.cache_timeout = 300  # 5 minutes
        
        print(f"[TokenBudget] 💰 Token budget manager initialized with {max_tokens} max tokens")
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from text
        Uses simple word-based estimation with adjustments for actual tokenization
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        try:
            if not text:
                return 0
            
            # Check cache first
            text_hash = hash(text)
            if text_hash in self.token_cache:
                cached_entry = self.token_cache[text_hash]
                if time.time() - cached_entry['timestamp'] < self.cache_timeout:
                    return cached_entry['count']
            
            # Basic estimation: words * 1.3 (accounting for subword tokenization)
            words = len(text.split())
            
            # Adjust for different content types
            adjustments = 0
            
            # Symbolic tokens are typically 1-2 tokens each
            symbolic_matches = re.findall(r'<[^>]+>', text)
            adjustments += len(symbolic_matches) * 1.5
            
            # Numbers and special characters
            numbers = re.findall(r'\d+', text)
            adjustments += len(numbers) * 0.5
            
            # Punctuation (usually separate tokens)
            punctuation = re.findall(r'[^\w\s]', text)
            adjustments += len(punctuation) * 0.3
            
            # Base estimation
            estimated_tokens = max(1, int(words * 1.3 + adjustments))
            
            # Cache the result
            self.token_cache[text_hash] = {
                'count': estimated_tokens,
                'timestamp': time.time()
            }
            
            return estimated_tokens
            
        except Exception as e:
            print(f"[TokenBudget] ❌ Error estimating tokens: {e}")
            # Fallback: rough character-based estimation
            return max(1, len(text) // 4)
    
    def check_budget_constraint(self, content: str, additional_tokens: int = 0) -> Dict[str, Any]:
        """
        Check if content fits within token budget
        
        Args:
            content: Content to check
            additional_tokens: Additional tokens to account for
            
        Returns:
            Budget analysis results
        """
        try:
            content_tokens = self.estimate_tokens(content)
            total_tokens = content_tokens + additional_tokens
            
            # Calculate available budget (excluding reserved tokens)
            reserved_total = sum(self.reserved_tokens.values())
            available_budget = self.max_tokens - reserved_total
            
            budget_check = {
                'content_tokens': content_tokens,
                'additional_tokens': additional_tokens,
                'total_tokens': total_tokens,
                'available_budget': available_budget,
                'max_tokens': self.max_tokens,
                'reserved_tokens': reserved_total,
                'fits_budget': total_tokens <= available_budget,
                'utilization_percentage': (total_tokens / available_budget) * 100 if available_budget > 0 else 100,
                'tokens_over_budget': max(0, total_tokens - available_budget),
                'recommended_action': 'allow' if total_tokens <= available_budget else 'trim'
            }
            
            # Add severity assessment
            if budget_check['utilization_percentage'] < 70:
                budget_check['severity'] = 'low'
            elif budget_check['utilization_percentage'] < 90:
                budget_check['severity'] = 'medium'
            else:
                budget_check['severity'] = 'high'
            
            return budget_check
            
        except Exception as e:
            print(f"[TokenBudget] ❌ Error checking budget: {e}")
            return {
                'fits_budget': False,
                'error': str(e),
                'recommended_action': 'block'
            }
    
    def trim_content_to_budget(self, content: str, target_budget: int = None) -> str:
        """
        Trim content to fit within token budget while preserving important content
        
        Args:
            content: Content to trim
            target_budget: Target token budget (uses available budget if None)
            
        Returns:
            Trimmed content
        """
        try:
            if not content:
                return ""
            
            # Calculate target budget
            if target_budget is None:
                reserved_total = sum(self.reserved_tokens.values())
                target_budget = self.max_tokens - reserved_total
            
            current_tokens = self.estimate_tokens(content)
            
            # If already within budget, return as-is
            if current_tokens <= target_budget:
                return content
            
            print(f"[TokenBudget] ✂️ Trimming content from {current_tokens} to {target_budget} tokens")
            
            # Parse content into components
            content_components = self._parse_content_components(content)
            
            # Allocate budget to components by priority
            trimmed_components = self._allocate_budget_to_components(
                content_components, target_budget
            )
            
            # Reconstruct trimmed content
            trimmed_content = self._reconstruct_content(trimmed_components)
            
            # Verify final token count
            final_tokens = self.estimate_tokens(trimmed_content)
            print(f"[TokenBudget] ✅ Trimmed to {final_tokens} tokens")
            
            return trimmed_content
            
        except Exception as e:
            print(f"[TokenBudget] ❌ Error trimming content: {e}")
            # Fallback: simple truncation
            words = content.split()
            estimated_words = target_budget // 2 if target_budget else len(words) // 2
            return " ".join(words[:estimated_words]) + "... [TRIMMED]"
    
    def optimize_token_distribution(self, content_parts: Dict[str, str], 
                                   total_budget: int) -> Dict[str, str]:
        """
        Optimize token distribution across different content parts
        
        Args:
            content_parts: Dictionary of content parts to optimize
            total_budget: Total token budget to distribute
            
        Returns:
            Optimized content parts
        """
        try:
            optimized_parts = {}
            
            # Calculate current token usage
            current_usage = {}
            total_current = 0
            
            for part_name, part_content in content_parts.items():
                tokens = self.estimate_tokens(part_content)
                current_usage[part_name] = tokens
                total_current += tokens
            
            # If within budget, return as-is
            if total_current <= total_budget:
                return content_parts
            
            # Allocate budget based on priorities and allocation strategy
            for part_name, part_content in content_parts.items():
                # Get allocation percentage for this part type
                allocation_key = self._get_allocation_key(part_name)
                allocation_percentage = self.budget_allocation.get(allocation_key, 0.1)
                
                # Calculate allocated budget
                allocated_budget = int(total_budget * allocation_percentage)
                
                # Trim part to allocated budget
                optimized_parts[part_name] = self.trim_content_to_budget(
                    part_content, allocated_budget
                )
            
            return optimized_parts
            
        except Exception as e:
            print(f"[TokenBudget] ❌ Error optimizing distribution: {e}")
            return content_parts
    
    def preserve_symbolic_tokens(self, content: str, max_symbolic_tokens: int = None) -> Tuple[str, List[str]]:
        """
        Extract and preserve symbolic tokens when trimming content
        
        Args:
            content: Content containing symbolic tokens
            max_symbolic_tokens: Maximum symbolic tokens to preserve
            
        Returns:
            Tuple of (content_without_tokens, preserved_tokens)
        """
        try:
            # Extract all symbolic tokens
            symbolic_tokens = re.findall(r'<[^>]+>', content)
            
            # Remove tokens from content
            content_without_tokens = re.sub(r'<[^>]+>', '', content)
            content_without_tokens = re.sub(r'\s+', ' ', content_without_tokens).strip()
            
            # Prioritize tokens by type
            prioritized_tokens = self._prioritize_symbolic_tokens(symbolic_tokens)
            
            # Limit tokens if specified
            if max_symbolic_tokens and len(prioritized_tokens) > max_symbolic_tokens:
                prioritized_tokens = prioritized_tokens[:max_symbolic_tokens]
            
            print(f"[TokenBudget] 🎯 Preserved {len(prioritized_tokens)} symbolic tokens")
            return content_without_tokens, prioritized_tokens
            
        except Exception as e:
            print(f"[TokenBudget] ❌ Error preserving tokens: {e}")
            return content, []
    
    def calculate_optimal_context_size(self, components: Dict[str, str]) -> Dict[str, int]:
        """
        Calculate optimal context size for different components
        
        Args:
            components: Dictionary of context components
            
        Returns:
            Dictionary of optimal token allocations
        """
        try:
            total_available = self.max_tokens - sum(self.reserved_tokens.values())
            optimal_allocations = {}
            
            # Calculate priorities and current usage
            component_priorities = {}
            component_tokens = {}
            
            for comp_name, comp_content in components.items():
                tokens = self.estimate_tokens(comp_content)
                component_tokens[comp_name] = tokens
                
                # Get priority based on component type
                priority = self._get_component_priority(comp_name)
                component_priorities[comp_name] = priority
            
            # Allocate budget proportionally to priorities
            total_priority = sum(component_priorities.values())
            
            for comp_name in components.keys():
                priority_ratio = component_priorities[comp_name] / total_priority
                allocated_tokens = int(total_available * priority_ratio)
                
                # Ensure minimum allocation
                min_allocation = 50 if comp_name in ['user_input', 'symbolic_tokens'] else 20
                allocated_tokens = max(min_allocation, allocated_tokens)
                
                optimal_allocations[comp_name] = allocated_tokens
            
            # Adjust if total exceeds budget
            total_allocated = sum(optimal_allocations.values())
            if total_allocated > total_available:
                # Scale down proportionally
                scale_factor = total_available / total_allocated
                for comp_name in optimal_allocations:
                    optimal_allocations[comp_name] = int(optimal_allocations[comp_name] * scale_factor)
            
            return optimal_allocations
            
        except Exception as e:
            print(f"[TokenBudget] ❌ Error calculating optimal context: {e}")
            # Return equal distribution as fallback
            equal_allocation = total_available // max(1, len(components))
            return {comp: equal_allocation for comp in components.keys()}
    
    def _parse_content_components(self, content: str) -> Dict[str, Any]:
        """Parse content into different components for budget allocation"""
        try:
            components = {
                'symbolic_tokens': [],
                'regular_text': [],
                'user_input': [],
                'system_content': []
            }
            
            # Extract symbolic tokens
            symbolic_tokens = re.findall(r'<[^>]+>', content)
            components['symbolic_tokens'] = symbolic_tokens
            
            # Remove symbolic tokens to get regular text
            regular_text = re.sub(r'<[^>]+>', '', content)
            
            # Split by common delimiters
            text_parts = re.split(r'\n\n+|\. (?=[A-Z])', regular_text)
            text_parts = [part.strip() for part in text_parts if part.strip()]
            
            components['regular_text'] = text_parts
            
            return components
            
        except Exception as e:
            print(f"[TokenBudget] ❌ Error parsing components: {e}")
            return {'regular_text': [content]}
    
    def _allocate_budget_to_components(self, components: Dict[str, Any], 
                                     budget: int) -> Dict[str, Any]:
        """Allocate budget to components based on priorities"""
        try:
            allocated_components = {}
            remaining_budget = budget
            
            # First, allocate to symbolic tokens (highest priority)
            if 'symbolic_tokens' in components:
                symbolic_budget = min(
                    int(budget * self.budget_allocation['symbolic_tokens']),
                    len(components['symbolic_tokens']) * 5  # ~5 tokens per symbolic token
                )
                allocated_components['symbolic_tokens'] = components['symbolic_tokens']
                remaining_budget -= symbolic_budget
            
            # Allocate remaining budget to text components
            if 'regular_text' in components and remaining_budget > 0:
                text_parts = components['regular_text']
                
                # Prioritize recent/important parts
                important_parts = []
                regular_parts = []
                
                for part in text_parts:
                    if any(keyword in part.lower() for keyword in ['user:', 'important', 'remember', 'urgent']):
                        important_parts.append(part)
                    else:
                        regular_parts.append(part)
                
                # Allocate budget
                allocated_text = []
                tokens_used = 0
                
                # Important parts first
                for part in important_parts:
                    part_tokens = self.estimate_tokens(part)
                    if tokens_used + part_tokens <= remaining_budget:
                        allocated_text.append(part)
                        tokens_used += part_tokens
                
                # Regular parts if budget remains
                for part in regular_parts:
                    part_tokens = self.estimate_tokens(part)
                    if tokens_used + part_tokens <= remaining_budget:
                        allocated_text.append(part)
                        tokens_used += part_tokens
                    elif remaining_budget - tokens_used > 10:
                        # Try to include partial content
                        words = part.split()
                        partial_words = []
                        partial_tokens = 0
                        
                        for word in words:
                            word_tokens = self.estimate_tokens(word)
                            if partial_tokens + word_tokens <= remaining_budget - tokens_used:
                                partial_words.append(word)
                                partial_tokens += word_tokens
                            else:
                                break
                        
                        if partial_words:
                            allocated_text.append(" ".join(partial_words) + "...")
                            tokens_used += partial_tokens
                        break
                
                allocated_components['regular_text'] = allocated_text
            
            return allocated_components
            
        except Exception as e:
            print(f"[TokenBudget] ❌ Error allocating budget: {e}")
            return components
    
    def _reconstruct_content(self, components: Dict[str, Any]) -> str:
        """Reconstruct content from components"""
        try:
            content_parts = []
            
            # Add symbolic tokens first
            if 'symbolic_tokens' in components:
                content_parts.extend(components['symbolic_tokens'])
            
            # Add regular text
            if 'regular_text' in components:
                content_parts.extend(components['regular_text'])
            
            return " ".join(content_parts)
            
        except Exception as e:
            print(f"[TokenBudget] ❌ Error reconstructing content: {e}")
            return ""
    
    def _prioritize_symbolic_tokens(self, tokens: List[str]) -> List[str]:
        """Prioritize symbolic tokens by importance"""
        try:
            token_priorities = []
            
            for token in tokens:
                priority = 0
                
                # Personality tokens (highest priority)
                if re.match(r'<pers\d+:', token):
                    priority = 10
                # Memory tokens
                elif re.match(r'<mem\d+:', token):
                    priority = 8
                # Entity tokens
                elif re.match(r'<ent_:', token):
                    priority = 7
                # Factual tokens
                elif re.match(r'<fact_:', token):
                    priority = 6
                # Other tokens
                else:
                    priority = 5
                
                token_priorities.append((priority, token))
            
            # Sort by priority (descending)
            token_priorities.sort(key=lambda x: x[0], reverse=True)
            
            return [token for priority, token in token_priorities]
            
        except Exception as e:
            print(f"[TokenBudget] ❌ Error prioritizing tokens: {e}")
            return tokens
    
    def _get_allocation_key(self, part_name: str) -> str:
        """Get allocation key for content part"""
        if 'symbolic' in part_name.lower() or 'token' in part_name.lower():
            return 'symbolic_tokens'
        elif 'memory' in part_name.lower():
            return 'memory_context'
        elif 'user' in part_name.lower() or 'input' in part_name.lower():
            return 'user_input'
        elif 'conversation' in part_name.lower() or 'context' in part_name.lower():
            return 'conversation_context'
        else:
            return 'buffer'
    
    def _get_component_priority(self, component_name: str) -> int:
        """Get priority score for component"""
        component_name_lower = component_name.lower()
        
        if 'symbolic' in component_name_lower or 'personality' in component_name_lower:
            return 10
        elif 'user' in component_name_lower or 'input' in component_name_lower:
            return 9
        elif 'memory' in component_name_lower:
            return 8
        elif 'context' in component_name_lower:
            return 7
        else:
            return 5
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status and statistics"""
        try:
            reserved_total = sum(self.reserved_tokens.values())
            available_budget = self.max_tokens - reserved_total
            
            status = {
                'max_tokens': self.max_tokens,
                'reserved_tokens': self.reserved_tokens,
                'reserved_total': reserved_total,
                'available_budget': available_budget,
                'utilization_percentage': 0,
                'budget_allocation': self.budget_allocation,
                'token_priorities': self.token_priorities,
                'cache_size': len(self.token_cache),
                'recommendations': []
            }
            
            # Add recommendations
            if available_budget < 500:
                status['recommendations'].append("Consider increasing max_tokens or reducing reserved tokens")
            
            if len(self.token_cache) > 1000:
                status['recommendations'].append("Token cache is large, consider clearing old entries")
            
            return status
            
        except Exception as e:
            return {'error': str(e)}
    
    def clear_token_cache(self):
        """Clear the token estimation cache"""
        try:
            old_size = len(self.token_cache)
            self.token_cache.clear()
            print(f"[TokenBudget] 🧹 Cleared token cache ({old_size} entries)")
        except Exception as e:
            print(f"[TokenBudget] ❌ Error clearing cache: {e}")

# Global instance
token_budget_manager = TokenBudgetManager()

def estimate_tokens_from_text(text: str) -> int:
    """
    Main function to estimate tokens from text
    Compatible with existing LLM budget monitor interface
    """
    return token_budget_manager.estimate_tokens(text)

def trim_tokens_to_budget(tokens: str, max_tokens: int) -> str:
    """
    Main function to trim tokens to budget
    Compatible with existing consciousness_tokenizer interface
    """
    return token_budget_manager.trim_content_to_budget(tokens, max_tokens)

def check_token_budget(content: str, additional_tokens: int = 0) -> Dict[str, Any]:
    """
    Check if content fits within token budget
    """
    return token_budget_manager.check_budget_constraint(content, additional_tokens)

def optimize_content_distribution(content_parts: Dict[str, str], total_budget: int) -> Dict[str, str]:
    """
    Optimize token distribution across content parts
    """
    return token_budget_manager.optimize_token_distribution(content_parts, total_budget)

def preserve_important_tokens(content: str, max_tokens: int = None) -> Tuple[str, List[str]]:
    """
    Preserve important symbolic tokens
    """
    return token_budget_manager.preserve_symbolic_tokens(content, max_tokens)

def get_token_budget_status() -> Dict[str, Any]:
    """
    Get current token budget status
    """
    return token_budget_manager.get_budget_status()

if __name__ == "__main__":
    # Test the token budget manager
    print("🧪 Testing Token Budget Manager")
    
    # Test token estimation
    test_text = "Hello! I'm a Python developer from Brisbane. <pers1:friendliness:0.90:stable> Can you help me?"
    estimated = estimate_tokens_from_text(test_text)
    print(f"✅ Estimated tokens: {estimated}")
    
    # Test budget checking
    budget_check = check_token_budget(test_text, 100)
    print(f"✅ Budget check: {budget_check['fits_budget']}, {budget_check['utilization_percentage']:.1f}% used")
    
    # Test trimming
    long_text = "This is a very long text that should be trimmed to fit within the token budget. " * 50
    trimmed = trim_tokens_to_budget(long_text, 50)
    print(f"✅ Trimmed text: {trimmed[:100]}...")
    
    # Test symbolic token preservation
    token_text = "<pers1:friendly:0.9:stable> <mem1:personal:0.8> This is regular text that can be trimmed."
    preserved_content, preserved_tokens = preserve_important_tokens(token_text, 2)
    print(f"✅ Preserved tokens: {preserved_tokens}")
    print(f"✅ Remaining content: {preserved_content}")
    
    # Test budget status
    status = get_token_budget_status()
    print(f"✅ Budget status: {status['available_budget']} tokens available")