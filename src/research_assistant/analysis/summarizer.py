from typing import Dict, Any, List, Optional
import json

from research_assistant.analysis.base_analyzer import BaseAnalyzer, AnalysisResult
from research_assistant.llm.ollama_client import OllamaClient
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class Summarizer(BaseAnalyzer):
    """Analyzer for generating content summaries using Ollama."""

    def __init__(
        self,
        model_name: str = "mistral",
        max_length: int = 500,
        temperature: float = 0.7
    ):
        """
        Initialize the summarizer.

        Args:
            model_name: Name of the Ollama model to use
            max_length: Maximum length of the summary
            temperature: Temperature for text generation
        """
        super().__init__(
            name="summarizer",
            description="Generate concise summaries of content using Ollama"
        )
        self.model_name = model_name
        self.max_length = max_length
        self.temperature = temperature
        self.ollama = OllamaClient(model_name=model_name)

    async def analyze(
        self,
        content: str,
        options: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """
        Generate a summary of the given content.

        Args:
            content: Content to summarize
            options: Optional summarization options including:
                - max_length: Maximum length of the summary
                - temperature: Temperature for text generation
                - focus_areas: List of areas to focus on in the summary

        Returns:
            Analysis result containing the summary
        """
        try:
            # Validate content
            if not await self.validate_content(content):
                raise ValueError("Invalid content for summarization")

            # Get options
            options = options or {}
            max_length = options.get("max_length", self.max_length)
            temperature = options.get("temperature", self.temperature)
            focus_areas = options.get("focus_areas", [])

            # Prepare prompt
            prompt = self._prepare_prompt(content, max_length, focus_areas)

            # Generate summary
            response = await self.ollama.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_length
            )

            # Process response
            summary = response.strip()
            metadata = {
                "model": self.model_name,
                "max_length": max_length,
                "temperature": temperature,
                "focus_areas": focus_areas,
                "original_length": len(content),
                "summary_length": len(summary),
                "compression_ratio": len(summary) / len(content) if content else 0
            }

            return AnalysisResult(
                content=summary,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise

    async def batch_analyze(
        self,
        contents: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> List[AnalysisResult]:
        """
        Generate summaries for multiple contents.

        Args:
            contents: List of contents to summarize
            options: Optional summarization options

        Returns:
            List of analysis results containing summaries
        """
        try:
            results = []
            for content in contents:
                result = await self.analyze(content, options)
                results.append(result)
            return results
        except Exception as e:
            logger.error(f"Error in batch summarization: {str(e)}")
            raise

    async def validate_content(self, content: str) -> bool:
        """
        Validate if the content can be summarized.

        Args:
            content: Content to validate

        Returns:
            True if content is valid, False otherwise
        """
        if not content or not isinstance(content, str):
            return False
        if len(content.strip()) < 50:  # Minimum content length
            return False
        return True

    async def close(self):
        """Close the summarizer and release resources."""
        try:
            await self.ollama.close()
        except Exception as e:
            logger.error(f"Error closing summarizer: {str(e)}")

    def _prepare_prompt(
        self,
        content: str,
        max_length: int,
        focus_areas: List[str]
    ) -> str:
        """
        Prepare the prompt for summarization.

        Args:
            content: Content to summarize
            max_length: Maximum length of the summary
            focus_areas: List of areas to focus on

        Returns:
            Formatted prompt
        """
        prompt = f"""Please provide a concise summary of the following content in no more than {max_length} characters.

Content:
{content}

"""
        if focus_areas:
            prompt += f"\nPlease focus on the following areas:\n{', '.join(focus_areas)}\n"

        prompt += "\nSummary:"
        return prompt 