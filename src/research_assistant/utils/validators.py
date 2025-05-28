from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import re
from urllib.parse import urlparse
from pathlib import Path
import json
import yaml

class Validator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            bool: True if URL is valid
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_file_path(path: str) -> bool:
        """Validate file path.
        
        Args:
            path: File path to validate
            
        Returns:
            bool: True if path is valid
        """
        try:
            Path(path).resolve()
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_json(data: str) -> bool:
        """Validate JSON string.
        
        Args:
            data: JSON string to validate
            
        Returns:
            bool: True if JSON is valid
        """
        try:
            json.loads(data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_yaml(data: str) -> bool:
        """Validate YAML string.
        
        Args:
            data: YAML string to validate
            
        Returns:
            bool: True if YAML is valid
        """
        try:
            yaml.safe_load(data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            bool: True if email is valid
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_date(date_str: str, format: str = "%Y-%m-%d") -> bool:
        """Validate date format.
        
        Args:
            date_str: Date string to validate
            format: Expected date format
            
        Returns:
            bool: True if date is valid
        """
        try:
            datetime.strptime(date_str, format)
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate required fields in dictionary.
        
        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            
        Returns:
            bool: True if all required fields are present
        """
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_field_type(value: Any, expected_type: type) -> bool:
        """Validate field type.
        
        Args:
            value: Value to validate
            expected_type: Expected type
            
        Returns:
            bool: True if value is of expected type
        """
        return isinstance(value, expected_type)
    
    @staticmethod
    def validate_string_length(value: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
        """Validate string length.
        
        Args:
            value: String to validate
            min_length: Minimum length
            max_length: Maximum length (optional)
            
        Returns:
            bool: True if string length is valid
        """
        if not isinstance(value, str):
            return False
        if len(value) < min_length:
            return False
        if max_length is not None and len(value) > max_length:
            return False
        return True
    
    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                             max_value: Optional[Union[int, float]] = None) -> bool:
        """Validate numeric range.
        
        Args:
            value: Number to validate
            min_value: Minimum value (optional)
            max_value: Maximum value (optional)
            
        Returns:
            bool: True if number is within range
        """
        if not isinstance(value, (int, float)):
            return False
        if min_value is not None and value < min_value:
            return False
        if max_value is not None and value > max_value:
            return False
        return True
    
    @staticmethod
    def validate_list_items(items: List[Any], validator: callable) -> bool:
        """Validate list items using a validator function.
        
        Args:
            items: List to validate
            validator: Function to validate each item
            
        Returns:
            bool: True if all items are valid
        """
        if not isinstance(items, list):
            return False
        return all(validator(item) for item in items)
    
    @staticmethod
    def validate_dict_values(data: Dict[str, Any], validator: callable) -> bool:
        """Validate dictionary values using a validator function.
        
        Args:
            data: Dictionary to validate
            validator: Function to validate each value
            
        Returns:
            bool: True if all values are valid
        """
        if not isinstance(data, dict):
            return False
        return all(validator(value) for value in data.values())
    
    @staticmethod
    def validate_regex(value: str, pattern: str) -> bool:
        """Validate string against regex pattern.
        
        Args:
            value: String to validate
            pattern: Regex pattern
            
        Returns:
            bool: True if string matches pattern
        """
        if not isinstance(value, str):
            return False
        try:
            return bool(re.match(pattern, value))
        except Exception:
            return False 