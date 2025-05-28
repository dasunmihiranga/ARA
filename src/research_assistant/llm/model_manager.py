from typing import Dict, Any, Optional, List
import yaml
from pathlib import Path
import asyncio
import aiohttp
import json

from research_assistant.llm.ollama_client import OllamaClient
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ModelManager:
    """Manager for handling model loading and management."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        base_url: str = "http://localhost:11434"
    ):
        """
        Initialize the model manager.

        Args:
            config_path: Path to the model configuration file
            base_url: Base URL for the Ollama API
        """
        self.config_path = config_path or str(Path(__file__).parent.parent.parent.parent / "config" / "models.yaml")
        self.base_url = base_url
        self.config = self._load_config()
        self.models: Dict[str, OllamaClient] = {}
        self.logger = get_logger("model_manager")

    def _load_config(self) -> dict:
        """
        Load model configuration from YAML file.

        Returns:
            Dictionary containing model configurations
        """
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading model config: {str(e)}")
            return {}

    async def load_model(self, model_name: str) -> Optional[OllamaClient]:
        """
        Load a model by name.

        Args:
            model_name: Name of the model to load

        Returns:
            OllamaClient instance or None if loading fails
        """
        try:
            if model_name in self.models:
                return self.models[model_name]

            # Get model config
            model_config = self.config.get(model_name, {})
            if not model_config:
                self.logger.warning(f"Model config not found: {model_name}")
                return None

            # Create client
            client = OllamaClient(
                model_name=model_name,
                base_url=self.base_url,
                timeout=model_config.get("timeout", 30)
            )

            # Verify model availability
            models = await client.list_models()
            if not any(m["name"] == model_name for m in models):
                self.logger.warning(f"Model not available: {model_name}")
                return None

            self.models[model_name] = client
            return client

        except Exception as e:
            self.logger.error(f"Error loading model {model_name}: {str(e)}")
            return None

    async def unload_model(self, model_name: str) -> None:
        """
        Unload a model.

        Args:
            model_name: Name of the model to unload
        """
        if model_name in self.models:
            try:
                await self.models[model_name].close()
                del self.models[model_name]
            except Exception as e:
                self.logger.error(f"Error unloading model {model_name}: {str(e)}")

    async def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List all available models.

        Returns:
            List of model information dictionaries
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {error_text}")

                    result = await response.json()
                    return result.get("models", [])

        except Exception as e:
            self.logger.error(f"Error listing models: {str(e)}")
            return []

    async def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama.

        Args:
            model_name: Name of the model to pull

        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error: {error_text}")

                    return True

        except Exception as e:
            self.logger.error(f"Error pulling model {model_name}: {str(e)}")
            return False

    async def close(self):
        """Close all model instances."""
        for model_name in list(self.models.keys()):
            await self.unload_model(model_name) 