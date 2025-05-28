from typing import Dict, Any, Optional
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ErrorHandler:
    """Handles errors consistently across the MCP server."""

    def __init__(self):
        """Initialize the error handler."""
        self._error_mappings: Dict[type, str] = {
            ValueError: "Invalid input parameters",
            KeyError: "Missing required parameter",
            TypeError: "Invalid parameter type",
            NotImplementedError: "Feature not implemented",
            ConnectionError: "Failed to connect to external service",
            TimeoutError: "Operation timed out",
            Exception: "An unexpected error occurred"
        }

    def handle_error(self, error: Exception) -> Exception:
        """
        Handle an error and return an appropriate exception.

        Args:
            error: The original error

        Returns:
            Processed error with appropriate message
        """
        error_type = type(error)
        error_message = self._error_mappings.get(error_type, str(error))
        
        # Log the error
        logger.error(f"Error occurred: {error_message}", exc_info=True)
        
        # Create a new exception with the processed message
        return type(error)(error_message)

    def register_error_mapping(self, error_type: type, message: str) -> None:
        """
        Register a custom error mapping.

        Args:
            error_type: The type of error to map
            message: The message to use for this error type
        """
        self._error_mappings[error_type] = message

    def get_error_message(self, error: Exception) -> str:
        """
        Get the appropriate error message for an exception.

        Args:
            error: The error to get a message for

        Returns:
            The error message
        """
        return self._error_mappings.get(type(error), str(error))

    def format_error_response(self, error: Exception) -> Dict[str, Any]:
        """
        Format an error for API response.

        Args:
            error: The error to format

        Returns:
            Formatted error response
        """
        return {
            "error": self.get_error_message(error),
            "type": type(error).__name__,
            "details": str(error)
        } 