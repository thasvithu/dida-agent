from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from openai import OpenAI
import json
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all AI agents in the DIDA system.
    Provides common functionality for OpenAI API interactions.
    """
    
    def __init__(
        self,
        name: str,
        client: OpenAI,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7
    ):
        self.name = name
        self.client = client
        self.model = model
        self.temperature = temperature
        logger.info(f"Initialized agent: {name}")
        
    def _create_system_prompt(self) -> str:
        """Create system prompt for the agent. Override in subclasses."""
        return f"You are {self.name}, an AI assistant specialized in data science tasks."
        
    def _format_user_prompt(self, **kwargs) -> str:
        """Format user prompt with provided data. Override in subclasses."""
        return str(kwargs)
        
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Make a chat completion request to OpenAI.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Maximum tokens in response
            response_format: Optional format specification (e.g., {"type": "json_object"})
            
        Returns:
            Response content as string
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
                
            if response_format:
                kwargs["response_format"] = response_format
                
            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            
            logger.debug(f"{self.name} - Tokens used: {response.usage.total_tokens}")
            return content
            
        except Exception as e:
            logger.error(f"{self.name} - API error: {str(e)}")
            raise
            
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from the model.
        Handles markdown code blocks if present.
        """
        try:
            # Remove markdown code blocks if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
                
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"{self.name} - JSON parse error: {str(e)}\nResponse: {response}")
            raise ValueError(f"Failed to parse JSON response: {str(e)}")
            
    def execute(self, **kwargs) -> Any:
        """
        Main execution method for the agent.
        Must be implemented by subclasses.
        """
        system_prompt = self._create_system_prompt()
        user_prompt = self._format_user_prompt(**kwargs)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._process_request(messages, **kwargs)
        
    @abstractmethod
    def _process_request(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        """
        Process the request and return results.
        Must be implemented by subclasses.
        """
        pass
