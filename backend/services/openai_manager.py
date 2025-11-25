import os
from typing import Optional, Dict
from openai import OpenAI, AsyncOpenAI
import logging

logger = logging.getLogger(__name__)


class OpenAIManager:
    """
    Manages OpenAI API keys and client instances.
    Supports both system-level keys and user-provided keys.
    """
    
    def __init__(self):
        self.system_api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        # Session storage for user API keys (in-memory, not persisted)
        self._session_keys: Dict[str, str] = {}
        
    def set_session_key(self, session_id: str, api_key: str) -> None:
        """Store API key for a session"""
        self._session_keys[session_id] = api_key
        logger.info(f"API key set for session: {session_id}")
        
    def get_session_key(self, session_id: str) -> Optional[str]:
        """Retrieve API key for a session"""
        return self._session_keys.get(session_id)
        
    def remove_session_key(self, session_id: str) -> None:
        """Remove API key for a session"""
        if session_id in self._session_keys:
            del self._session_keys[session_id]
            logger.info(f"API key removed for session: {session_id}")
            
    def get_client(self, session_id: Optional[str] = None, api_key: Optional[str] = None) -> OpenAI:
        """
        Get OpenAI client with priority:
        1. Explicitly provided api_key
        2. Session-specific key
        3. System key
        """
        key_to_use = None
        
        if api_key:
            key_to_use = api_key
            logger.debug("Using explicitly provided API key")
        elif session_id and session_id in self._session_keys:
            key_to_use = self._session_keys[session_id]
            logger.debug(f"Using session API key for: {session_id}")
        elif self.system_api_key:
            key_to_use = self.system_api_key
            logger.debug("Using system API key")
        else:
            raise ValueError("No OpenAI API key available. Please provide one.")
            
        return OpenAI(api_key=key_to_use)
        
    def get_async_client(self, session_id: Optional[str] = None, api_key: Optional[str] = None) -> AsyncOpenAI:
        """
        Get async OpenAI client with same priority as get_client
        """
        key_to_use = None
        
        if api_key:
            key_to_use = api_key
        elif session_id and session_id in self._session_keys:
            key_to_use = self._session_keys[session_id]
        elif self.system_api_key:
            key_to_use = self.system_api_key
        else:
            raise ValueError("No OpenAI API key available. Please provide one.")
            
        return AsyncOpenAI(api_key=key_to_use)
        
    async def validate_api_key(self, api_key: str) -> tuple[bool, str, Optional[str]]:
        """
        Validate an API key by making a test request.
        Returns: (is_valid, message, model_name)
        """
        try:
            client = OpenAI(api_key=api_key)
            # Make a minimal test request
            response = client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            model_used = response.model
            logger.info(f"API key validated successfully. Model: {model_used}")
            return True, "API key is valid", model_used
        except Exception as e:
            error_msg = str(e)
            logger.error(f"API key validation failed: {error_msg}")
            if "invalid" in error_msg.lower() or "incorrect" in error_msg.lower():
                return False, "Invalid API key", None
            elif "quota" in error_msg.lower():
                return False, "API key valid but quota exceeded", None
            else:
                return False, f"Validation error: {error_msg}", None
                

# Global instance
openai_manager = OpenAIManager()
