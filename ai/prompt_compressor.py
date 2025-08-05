# ai/prompt_compressor.py - Prompt Token Compression and Expansion System
"""
Handles compression of large prompts into ~100 token references and expansion
back to full content just before LLM API calls. Reduces token usage dramatically.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from ai.prompt_templates import (
    PROMPT_TEMPLATES, TOKEN_MAPPING, REVERSE_TOKEN_MAPPING,
    get_template, get_template_token, get_template_variables
)

class PromptCompressor:
    """Handles compression and expansion of prompts for token optimization."""
    
    def __init__(self):
        self.memory_context_cache = {}
        self.consciousness_state_cache = {}
        self.compressed_context_counter = 1
        
    def compress_system_prompt(self, full_prompt: str, context_data: Dict[str, Any] = None) -> str:
        """
        Compress a full system prompt into token references.
        
        Args:
            full_prompt: The full system prompt text
            context_data: Dynamic data for template variables
            
        Returns:
            Compressed prompt with tokens
        """
        if context_data is None:
            context_data = {}
            
        compressed_parts = []
        
        # Always include core character (essential)
        compressed_parts.append("[CHARACTER:BuddyV1]")
        
        # Add name handling if user info available (essential)
        if context_data.get('name_instruction'):
            compressed_parts.append("[NAME:HANDLING_V1]")
        
        # Add memory context only if significant
        if context_data.get('context') and len(context_data['context'].strip()) > 10:
            ctx_id = self._store_memory_context(context_data['context'])
            compressed_parts.append(f"[MEMORY:CTX_{ctx_id}]")
        
        # 🧠 NEW: Add working memory context if available
        if context_data.get('natural_context') and len(context_data['natural_context'].strip()) > 5:
            compressed_parts.append("[WORKING_MEMORY:V1]")
            
        # 🧠 NEW: Add retrospective memory context if available
        if context_data.get('retrospective_context') and len(context_data['retrospective_context'].strip()) > 5:
            compressed_parts.append("[RETROSPECTIVE:V1]")
            
        # Skip location and consciousness for ultra-compression unless specifically needed
        location_context = context_data.get('current_location', '')
        if location_context and any(keyword in full_prompt.lower() for keyword in ['location', 'where', 'time', 'date']):
            compressed_parts.append("[LOCATION:CONTEXT]")
        
        result = " ".join(compressed_parts)
        print(f"[PromptCompressor] 🗜️ Ultra-compressed {len(full_prompt)} chars to {len(result)} chars")
        return result
    
    def expand_compressed_prompt(self, compressed_prompt: str, context_data: Dict[str, Any] = None) -> str:
        """
        Expand compressed tokens back to full prompt content.
        
        Args:
            compressed_prompt: Prompt with token references
            context_data: Dynamic data for template variables
            
        Returns:
            Full expanded prompt
        """
        if context_data is None:
            context_data = {}
            
        expanded_parts = []
        tokens = compressed_prompt.split()
        
        for token in tokens:
            if token.startswith('[') and token.endswith(']'):
                expanded_content = self._expand_single_token(token, context_data)
                if expanded_content:
                    expanded_parts.append(expanded_content)
            else:
                # Regular text, keep as-is
                expanded_parts.append(token)
        
        result = "\n\n".join(expanded_parts)
        print(f"[PromptCompressor] 📤 Expanded {len(compressed_prompt)} chars to {len(result)} chars")
        return result
    
    def _expand_single_token(self, token: str, context_data: Dict[str, Any]) -> str:
        """Expand a single token to its full content."""
        
        # Handle memory context tokens
        if token.startswith('[MEMORY:CTX_'):
            ctx_id = token.replace('[MEMORY:CTX_', '').replace(']', '')
            context_content = self.memory_context_cache.get(ctx_id, '')
            return get_template('MEMORY_CONTEXT').format(context=context_content)
        
        # Handle consciousness state tokens
        if token.startswith('[CONSCIOUSNESS:'):
            cons_id = token.replace('[CONSCIOUSNESS:', '').replace(']', '')
            consciousness_data = self.consciousness_state_cache.get(cons_id, {})
            return get_template('CONSCIOUSNESS_STATE').format(**consciousness_data)
        
        # Handle emotional context tokens
        if token.startswith('[EMOTIONAL:CTX_'):
            emo_id = token.replace('[EMOTIONAL:CTX_', '').replace(']', '')
            emotional_data = self.consciousness_state_cache.get(f"emo_{emo_id}", {})
            return get_template('EMOTIONAL_CONTEXT').format(**emotional_data)
        
        # Handle static template tokens (including new optimized templates)
        template_id = TOKEN_MAPPING.get(token)
        if template_id:
            template = get_template(template_id)
            variables = get_template_variables(template_id)
            
            # Fill in variables if available
            if variables:
                try:
                    return template.format(**{var: context_data.get(var, '') for var in variables})
                except KeyError as e:
                    print(f"[PromptCompressor] ⚠️ Missing variable {e} for template {template_id}")
                    return template  # Return template without variable substitution
            else:
                return template
        
        print(f"[PromptCompressor] ⚠️ Unknown token: {token}")
        return token  # Return token as-is if not recognized
    
    def _store_memory_context(self, context: str) -> str:
        """Store memory context and return reference ID."""
        ctx_id = str(self.compressed_context_counter)
        self.memory_context_cache[ctx_id] = context
        self.compressed_context_counter += 1
        return ctx_id
    
    def _store_consciousness_state(self, context_data: Dict[str, Any]) -> str:
        """Store consciousness state and return reference ID."""
        cons_id = str(self.compressed_context_counter)
        consciousness_data = {
            'emotion': context_data.get('emotion', 'neutral'),
            'goal': context_data.get('goal', 'assist_user')
        }
        self.consciousness_state_cache[cons_id] = consciousness_data
        self.compressed_context_counter += 1
        return cons_id
    
    def _store_emotional_context(self, context_data: Dict[str, Any]) -> str:
        """Store emotional context and return reference ID."""
        emo_id = str(self.compressed_context_counter)
        emotional_data = {
            'emotional_state': context_data.get('emotional_state', ''),
            'reminder_text': context_data.get('reminder_text', ''),
            'follow_up_text': context_data.get('follow_up_text', '')
        }
        self.consciousness_state_cache[f"emo_{emo_id}"] = emotional_data
        self.compressed_context_counter += 1
        return emo_id
    
    def estimate_token_count(self, text: str) -> int:
        """Estimate token count using approximation (1 token ≈ 4 characters)."""
        return len(text) // 4
    
    def optimize_context_for_budget(self, context: str, max_tokens: int = 50) -> str:
        """Optimize context to fit within token budget."""
        current_tokens = self.estimate_token_count(context)
        
        if current_tokens <= max_tokens:
            return context
        
        # Prioritize recent conversation over older context
        lines = context.split('\n')
        
        # Keep important memory facts
        important_lines = []
        conversation_lines = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['personal', 'important', 'remember', 'emotional']):
                important_lines.append(line)
            elif 'human:' in line.lower() or 'assistant:' in line.lower():
                conversation_lines.append(line)
        
        # Build optimized context within budget
        optimized_lines = important_lines[:3]  # Top 3 important facts
        
        # Add recent conversation if space allows
        remaining_budget = max_tokens - self.estimate_token_count('\n'.join(optimized_lines))
        
        for line in conversation_lines[-5:]:  # Last 5 conversation exchanges
            line_tokens = self.estimate_token_count(line)
            if line_tokens <= remaining_budget:
                optimized_lines.append(line)
                remaining_budget -= line_tokens
            else:
                break
        
        result = '\n'.join(optimized_lines)
        print(f"[PromptCompressor] 🎯 Optimized context: {current_tokens} → {self.estimate_token_count(result)} tokens")
        return result
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        return {
            'memory_contexts_stored': len(self.memory_context_cache),
            'consciousness_states_stored': len(self.consciousness_state_cache),
            'total_templates': len(PROMPT_TEMPLATES),
            'available_tokens': len(TOKEN_MAPPING)
        }

# Global instance
prompt_compressor = PromptCompressor()

def compress_prompt(full_prompt: str, context_data: Dict[str, Any] = None) -> str:
    """Convenience function to compress a prompt."""
    return prompt_compressor.compress_system_prompt(full_prompt, context_data)

def expand_prompt(compressed_prompt: str, context_data: Dict[str, Any] = None) -> str:
    """Convenience function to expand a compressed prompt."""
    return prompt_compressor.expand_compressed_prompt(compressed_prompt, context_data)

def estimate_tokens(text: str) -> int:
    """Convenience function to estimate token count."""
    return prompt_compressor.estimate_token_count(text)