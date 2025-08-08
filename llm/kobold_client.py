"""
Kobold LLM Client - Single responsibility adapter for language model
Handles HTTP connections to KoboldCPP with circuit breakers, timeouts, and health checks
"""
import asyncio
import json
import requests
import aiohttp
from typing import Dict, Any, List, Optional, AsyncIterator
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.models import (
    KOBOLD_URL, KOBOLD_TIMEOUT, KOBOLD_MAX_RETRIES, KOBOLD_RETRY_DELAY,
    MAX_CONNECTIONS_PER_ENDPOINT, CONNECTION_POOL_TIMEOUT, KEEP_ALIVE_CONNECTIONS
)
from config.core import DEBUG

class KoboldClient:
    """Client for KoboldCPP language model service"""
    
    def __init__(self, base_url: str = KOBOLD_URL):
        self.base_url = base_url
        self.timeout = KOBOLD_TIMEOUT
        self.max_retries = KOBOLD_MAX_RETRIES
        self.retry_delay = KOBOLD_RETRY_DELAY
        self.session = None
        self._setup_session()
    
    def _setup_session(self):
        """Setup requests session with retries and connection pooling"""
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "POST"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=MAX_CONNECTIONS_PER_ENDPOINT,
            pool_maxsize=MAX_CONNECTIONS_PER_ENDPOINT,
            pool_block=False
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    async def health(self) -> bool:
        """
        Check if KoboldCPP service is healthy
        
        Returns:
            True if service is available, False otherwise
        """
        try:
            # Try a simple request to the base URL or health endpoint
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.session.get(
                    self.base_url.replace('/v1/chat/completions', '/health'),
                    timeout=5
                )
            )
            return response.status_code == 200
        except Exception as e:
            if DEBUG:
                print(f"[KoboldClient] Health check failed: {e}")
            
            # Fallback: try a minimal chat completion
            try:
                test_messages = [{"role": "user", "content": "test"}]
                result = await self.chat(test_messages, max_tokens=1)
                return bool(result.strip())
            except:
                return False
    
    async def chat(self, messages: List[Dict[str, str]], max_tokens: int = 150, temperature: float = 0.7) -> str:
        """
        Send chat completion request to KoboldCPP
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (0.0-1.0)
            
        Returns:
            Generated response text or empty string on failure
        """
        payload = {
            "model": "llama3",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        return await self._make_request(payload)
    
    async def chat_streaming(self, messages: List[Dict[str, str]], max_tokens: int = 150, temperature: float = 0.7) -> AsyncIterator[str]:
        """
        Send streaming chat completion request to KoboldCPP
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (0.0-1.0)
            
        Yields:
            Streaming response tokens
        """
        payload = {
            "model": "llama3", 
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(self.base_url, json=payload) as response:
                    if response.status != 200:
                        if DEBUG:
                            print(f"[KoboldClient] HTTP {response.status}: {await response.text()}")
                        return
                    
                    async for line in response.content:
                        if line:
                            line_str = line.decode('utf-8').strip()
                            if line_str.startswith('data: '):
                                data_str = line_str[6:]
                                if data_str == '[DONE]':
                                    break
                                
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    continue
                        
        except Exception as e:
            if DEBUG:
                print(f"[KoboldClient] Streaming error: {e}")
    
    async def _make_request(self, payload: Dict[str, Any]) -> str:
        """Make HTTP request to KoboldCPP with retries"""
        retries = 0
        while retries <= self.max_retries:
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.session.post(
                        self.base_url,
                        json=payload,
                        timeout=self.timeout
                    )
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        content = data['choices'][0]['message']['content']
                        if DEBUG:
                            print(f"[KoboldClient] 🤖 Response: {content[:100]}...")
                        return content
                    else:
                        if DEBUG:
                            print(f"[KoboldClient] Unexpected response format: {data}")
                        return ""
                else:
                    if DEBUG:
                        print(f"[KoboldClient] HTTP {response.status_code}: {response.text}")
                    
                    retries += 1
                    if retries <= self.max_retries:
                        await asyncio.sleep(self.retry_delay)
                    else:
                        return ""
                        
            except Exception as e:
                retries += 1
                if DEBUG:
                    print(f"[KoboldClient] Request attempt {retries} failed: {e}")
                
                if retries <= self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                else:
                    if DEBUG:
                        print(f"[KoboldClient] All {self.max_retries + 1} attempts failed")
                    return ""
        
        return ""
    
    def close(self):
        """Clean up session resources"""
        if self.session:
            self.session.close()

# Global instance
kobold_client = KoboldClient()

# Convenience functions for backward compatibility
async def health_check() -> bool:
    """Check if Kobold service is healthy - convenience function"""
    return await kobold_client.health()

async def chat_completion(messages: List[Dict[str, str]], max_tokens: int = 150) -> str:
    """Send chat completion request - convenience function"""
    return await kobold_client.chat(messages, max_tokens)

async def chat_completion_streaming(messages: List[Dict[str, str]], max_tokens: int = 150) -> AsyncIterator[str]:
    """Send streaming chat completion request - convenience function"""
    async for token in kobold_client.chat_streaming(messages, max_tokens):
        yield token