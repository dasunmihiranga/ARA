from typing import Dict, Any, Optional, Type
import traceback
from enum import Enum

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class ErrorType(Enum):
    """Types of errors that can occur."""
    VALIDATION = "validation_error"
    TOOL = "tool_error"
    NETWORK = "network_error"
    AUTHENTICATION = "authentication_error"
    PERMISSION = "permission_error"
    RESOURCE = "resource_error"
    INTERNAL = "internal_error"
    UNKNOWN = "unknown_error"

class ErrorHandler:
    """Handler for managing and formatting errors."""

    def __init__(self):
        """Initialize the error handler."""
        self.logger = get_logger("error_handler")
        self._error_mappings: Dict[Type[Exception], ErrorType] = {
            ValueError: ErrorType.VALIDATION,
            TypeError: ErrorType.VALIDATION,
            KeyError: ErrorType.VALIDATION,
            AttributeError: ErrorType.VALIDATION,
            ConnectionError: ErrorType.NETWORK,
            TimeoutError: ErrorType.NETWORK,
            PermissionError: ErrorType.PERMISSION,
            FileNotFoundError: ErrorType.RESOURCE,
            ImportError: ErrorType.RESOURCE,
            NotImplementedError: ErrorType.INTERNAL,
        }

    def handle_error(self, error: Exception) -> str:
        """
        Handle an error and return a formatted error message.

        Args:
            error: Exception to handle

        Returns:
            Formatted error message
        """
        # Get error type
        error_type = self._get_error_type(error)

        # Log error
        self._log_error(error, error_type)

        # Format error message
        return self._format_error_message(error, error_type)

    def _get_error_type(self, error: Exception) -> ErrorType:
        """
        Get the type of error.

        Args:
            error: Exception to classify

        Returns:
            ErrorType enum value
        """
        # Check mapped error types
        for error_class, error_type in self._error_mappings.items():
            if isinstance(error, error_class):
                return error_type

        # Check for custom error types
        if hasattr(error, "error_type"):
            try:
                return ErrorType(error.error_type)
            except ValueError:
                pass

        return ErrorType.UNKNOWN

    def _log_error(self, error: Exception, error_type: ErrorType) -> None:
        """
        Log an error.

        Args:
            error: Exception to log
            error_type: Type of error
        """
        error_info = {
            "type": error_type.value,
            "message": str(error),
            "traceback": traceback.format_exc()
        }

        if error_type in [ErrorType.INTERNAL, ErrorType.UNKNOWN]:
            self.logger.error("Internal error occurred", extra=error_info)
        else:
            self.logger.warning("Error occurred", extra=error_info)

    def _format_error_message(self, error: Exception, error_type: ErrorType) -> str:
        """
        Format an error message.

        Args:
            error: Exception to format
            error_type: Type of error

        Returns:
            Formatted error message
        """
        # Get base message
        if error_type == ErrorType.VALIDATION:
            message = "Invalid input"
        elif error_type == ErrorType.TOOL:
            message = "Tool execution failed"
        elif error_type == ErrorType.NETWORK:
            message = "Network error occurred"
        elif error_type == ErrorType.AUTHENTICATION:
            message = "Authentication failed"
        elif error_type == ErrorType.PERMISSION:
            message = "Permission denied"
        elif error_type == ErrorType.RESOURCE:
            message = "Resource not available"
        elif error_type == ErrorType.INTERNAL:
            message = "Internal server error"
        else:
            message = "An error occurred"

        # Add error details if available
        if str(error):
            message += f": {str(error)}"

        return message

    def register_error_mapping(self, error_class: Type[Exception], error_type: ErrorType) -> None:
        """
        Register a new error mapping.

        Args:
            error_class: Exception class to map
            error_type: ErrorType to map to
        """
        self._error_mappings[error_class] = error_type
        self.logger.info(f"Registered error mapping: {error_class.__name__} -> {error_type.value}")

    def get_error_mappings(self) -> Dict[str, str]:
        """
        Get all registered error mappings.

        Returns:
            Dictionary of error mappings
        """
        return {
            error_class.__name__: error_type.value
            for error_class, error_type in self._error_mappings.items()
        } 