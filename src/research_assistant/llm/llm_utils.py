from typing import Dict, Any, List, Optional, Union
import json
import re
from datetime import datetime

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

def format_prompt(
    template: str,
    **kwargs: Any
) -> str:
    """
    Format a prompt template with variables.

    Args:
        template: Prompt template string
        **kwargs: Variables to format in the template

    Returns:
        Formatted prompt string
    """
    try:
        return template.format(**kwargs)
    except Exception as e:
        logger.error(f"Error formatting prompt: {str(e)}")
        raise

def parse_json_response(
    response: str,
    default: Optional[Any] = None
) -> Optional[Dict[str, Any]]:
    """
    Parse a JSON response from an LLM.

    Args:
        response: LLM response string
        default: Default value if parsing fails

    Returns:
        Parsed JSON dictionary or default value
    """
    try:
        # Try to find JSON in the response
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))

        # Try to parse the entire response as JSON
        return json.loads(response)
    except Exception as e:
        logger.warning(f"Error parsing JSON response: {str(e)}")
        return default

def extract_entities(
    text: str,
    entity_types: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Extract entities from text using regex patterns.

    Args:
        text: Input text
        entity_types: List of entity types to extract

    Returns:
        List of extracted entities with type and value
    """
    entities = []
    
    # Common entity patterns
    patterns = {
        "url": r'https?://\S+',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "date": r'\b\d{4}-\d{2}-\d{2}\b',
        "number": r'\b\d+(?:\.\d+)?\b',
        "percentage": r'\b\d+(?:\.\d+)?%\b'
    }

    # Filter patterns based on requested entity types
    if entity_types:
        patterns = {k: v for k, v in patterns.items() if k in entity_types}

    # Extract entities
    for entity_type, pattern in patterns.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            entities.append({
                "type": entity_type,
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            })

    return entities

def calculate_token_estimate(
    text: str,
    model_name: str
) -> int:
    """
    Estimate the number of tokens in text.

    Args:
        text: Input text
        model_name: Name of the model

    Returns:
        Estimated number of tokens
    """
    # Simple estimation: 1 token ≈ 4 characters for English text
    # This is a rough estimate and may vary by model
    return len(text) // 4

def format_chat_history(
    messages: List[Dict[str, str]]
) -> str:
    """
    Format chat history for display or storage.

    Args:
        messages: List of message dictionaries with 'role' and 'content'

    Returns:
        Formatted chat history string
    """
    formatted = []
    for msg in messages:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        timestamp = msg.get("timestamp", datetime.utcnow().isoformat())
        formatted.append(f"[{timestamp}] {role}: {content}")
    return "\n".join(formatted)

def validate_model_response(
    response: str,
    required_fields: Optional[List[str]] = None,
    max_length: Optional[int] = None
) -> bool:
    """
    Validate a model response.

    Args:
        response: Model response string
        required_fields: List of required fields in JSON response
        max_length: Maximum allowed response length

    Returns:
        True if response is valid, False otherwise
    """
    try:
        # Check length
        if max_length and len(response) > max_length:
            return False

        # Check required fields if response is JSON
        if required_fields:
            data = parse_json_response(response)
            if not data:
                return False
            return all(field in data for field in required_fields)

        return True

    except Exception as e:
        logger.error(f"Error validating model response: {str(e)}")
        return False

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200
) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text
        chunk_size: Size of each chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks 