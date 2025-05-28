from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import yaml
import csv
import re
import hashlib
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from research_assistant.tools.tool_schemas import ToolResponse
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class UtilityTools:
    """Utility tools for the MCP server."""

    def __init__(self):
        """Initialize utility tools."""
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def validate_data(
        self,
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> ToolResponse:
        """
        Validate data against a schema.

        Args:
            data: Data to validate
            schema: Validation schema

        Returns:
            Validation results
        """
        try:
            errors = []
            warnings = []

            # Validate required fields
            for field, rules in schema.get("required", {}).items():
                if field not in data:
                    errors.append(f"Missing required field: {field}")
                elif not self._validate_field(data[field], rules):
                    errors.append(f"Invalid value for field: {field}")

            # Validate optional fields
            for field, rules in schema.get("optional", {}).items():
                if field in data and not self._validate_field(data[field], rules):
                    warnings.append(f"Invalid value for optional field: {field}")

            # Validate field types
            for field, field_type in schema.get("types", {}).items():
                if field in data and not isinstance(data[field], field_type):
                    errors.append(f"Invalid type for field: {field}")

            return ToolResponse(
                success=len(errors) == 0,
                data={
                    "valid": len(errors) == 0,
                    "errors": errors,
                    "warnings": warnings
                }
            )

        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    def _validate_field(
        self,
        value: Any,
        rules: Dict[str, Any]
    ) -> bool:
        """
        Validate a field against rules.

        Args:
            value: Field value
            rules: Validation rules

        Returns:
            Whether field is valid
        """
        try:
            # Check type
            if "type" in rules and not isinstance(value, rules["type"]):
                return False

            # Check min/max for numbers
            if isinstance(value, (int, float)):
                if "min" in rules and value < rules["min"]:
                    return False
                if "max" in rules and value > rules["max"]:
                    return False

            # Check min/max length for strings
            if isinstance(value, str):
                if "min_length" in rules and len(value) < rules["min_length"]:
                    return False
                if "max_length" in rules and len(value) > rules["max_length"]:
                    return False
                if "pattern" in rules and not re.match(rules["pattern"], value):
                    return False

            # Check enum values
            if "enum" in rules and value not in rules["enum"]:
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating field: {str(e)}")
            return False

    async def format_data(
        self,
        data: Any,
        format: str,
        options: Optional[Dict[str, Any]] = None
    ) -> ToolResponse:
        """
        Format data in specified format.

        Args:
            data: Data to format
            format: Output format
            options: Formatting options

        Returns:
            Formatted data
        """
        try:
            options = options or {}

            if format == "json":
                formatted = self._format_json(data, options)
            elif format == "yaml":
                formatted = self._format_yaml(data, options)
            elif format == "csv":
                formatted = self._format_csv(data, options)
            else:
                raise ValueError(f"Unsupported format: {format}")

            return ToolResponse(
                success=True,
                data=formatted
            )

        except Exception as e:
            logger.error(f"Error formatting data: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    def _format_json(
        self,
        data: Any,
        options: Dict[str, Any]
    ) -> str:
        """
        Format data as JSON.

        Args:
            data: Data to format
            options: JSON formatting options

        Returns:
            JSON string
        """
        try:
            indent = options.get("indent", 2)
            sort_keys = options.get("sort_keys", False)
            return json.dumps(data, indent=indent, sort_keys=sort_keys)

        except Exception as e:
            logger.error(f"Error formatting JSON: {str(e)}")
            raise

    def _format_yaml(
        self,
        data: Any,
        options: Dict[str, Any]
    ) -> str:
        """
        Format data as YAML.

        Args:
            data: Data to format
            options: YAML formatting options

        Returns:
            YAML string
        """
        try:
            default_flow_style = options.get("default_flow_style", False)
            sort_keys = options.get("sort_keys", False)
            return yaml.dump(
                data,
                default_flow_style=default_flow_style,
                sort_keys=sort_keys
            )

        except Exception as e:
            logger.error(f"Error formatting YAML: {str(e)}")
            raise

    def _format_csv(
        self,
        data: List[Dict[str, Any]],
        options: Dict[str, Any]
    ) -> str:
        """
        Format data as CSV.

        Args:
            data: List of dictionaries to format
            options: CSV formatting options

        Returns:
            CSV string
        """
        try:
            if not data:
                return ""

            # Get fieldnames
            fieldnames = options.get("fieldnames")
            if not fieldnames:
                fieldnames = list(data[0].keys())

            # Create CSV string
            output = []
            writer = csv.DictWriter(
                output,
                fieldnames=fieldnames,
                extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(data)

            return "".join(output)

        except Exception as e:
            logger.error(f"Error formatting CSV: {str(e)}")
            raise

    async def generate_hash(
        self,
        data: Union[str, bytes],
        algorithm: str = "sha256"
    ) -> ToolResponse:
        """
        Generate hash of data.

        Args:
            data: Data to hash
            algorithm: Hash algorithm to use

        Returns:
            Hash value
        """
        try:
            if isinstance(data, str):
                data = data.encode("utf-8")

            if algorithm == "md5":
                hash_obj = hashlib.md5()
            elif algorithm == "sha1":
                hash_obj = hashlib.sha1()
            elif algorithm == "sha256":
                hash_obj = hashlib.sha256()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")

            hash_obj.update(data)
            hash_value = hash_obj.hexdigest()

            return ToolResponse(
                success=True,
                data={
                    "algorithm": algorithm,
                    "hash": hash_value
                }
            )

        except Exception as e:
            logger.error(f"Error generating hash: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    async def run_in_thread(
        self,
        func: callable,
        *args: Any,
        **kwargs: Any
    ) -> ToolResponse:
        """
        Run function in a thread pool.

        Args:
            func: Function to run
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor,
                func,
                *args,
                **kwargs
            )

            return ToolResponse(
                success=True,
                data=result
            )

        except Exception as e:
            logger.error(f"Error running in thread: {str(e)}")
            return ToolResponse(
                success=False,
                error=str(e)
            )

    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.executor.shutdown(wait=True)
        except Exception as e:
            logger.error(f"Error cleaning up: {str(e)}") 