from typing import Dict, Any, Optional, List
import aiohttp
import json
from datetime import datetime

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class OllamaClient:
    """Client for interacting with Ollama models."""

    def __init__(
        self,
        model_name: str = "mistral",
        base_url: str = "http://localhost:11434",
        timeout: int = 30
    ):
        """
        Initialize the Ollama client.

        Args:
            model_name: Name of the Ollama model to use
            base_url: Base URL for the Ollama API
            timeout: Request timeout in seconds
        """
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = get_logger(f"ollama.{model_name}")

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None,
        system: Optional[str] = None,
        context: Optional[List[int]] = None
    ) -> str:
        """
        Generate text using the Ollama model.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            stop: List of stop sequences
            system: System message for chat models
            context: Previous context for continued generation

        Returns:
            Generated text
        """
        try:
            await self._ensure_session()

            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False
            }

            if max_tokens is not None:
                payload["max_tokens"] = max_tokens
            if stop is not None:
                payload["stop"] = stop
            if system is not None:
                payload["system"] = system
            if context is not None:
                payload["context"] = context

            async with self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {error_text}")

                result = await response.json()
                return result.get("response", "")

        except Exception as e:
            self.logger.error(f"Error generating text: {str(e)}")
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None
    ) -> str:
        """
        Generate chat completion using the Ollama model.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum number of tokens to generate
            stop: List of stop sequences

        Returns:
            Generated response
        """
        try:
            await self._ensure_session()

            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "stream": False
            }

            if max_tokens is not None:
                payload["max_tokens"] = max_tokens
            if stop is not None:
                payload["stop"] = stop

            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {error_text}")

                result = await response.json()
                return result.get("message", {}).get("content", "")

        except Exception as e:
            self.logger.error(f"Error in chat completion: {str(e)}")
            raise

    async def embeddings(
        self,
        text: str
    ) -> List[float]:
        """
        Generate embeddings for the given text.

        Args:
            text: Input text

        Returns:
            List of embedding values
        """
        try:
            await self._ensure_session()

            payload = {
                "model": self.model_name,
                "prompt": text
            }

            async with self.session.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {error_text}")

                result = await response.json()
                return result.get("embedding", [])

        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available Ollama models.

        Returns:
            List of model information dictionaries
        """
        try:
            await self._ensure_session()

            async with self.session.get(f"{self.base_url}/api/tags") as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {error_text}")

                result = await response.json()
                return result.get("models", [])

        except Exception as e:
            self.logger.error(f"Error listing models: {str(e)}")
            raise

    async def close(self):
        """Close the Ollama client session."""
        if self.session and not self.session.closed:
            await self.session.close() 