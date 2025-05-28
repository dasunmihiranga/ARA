import functools
import time
import logging
from typing import Any, Callable, Dict, Optional, Type, Union
from functools import wraps
import traceback
import json
from datetime import datetime

from .logger import Logger

logger = Logger.get_logger(__name__)

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
          exceptions: Union[Type[Exception], tuple[Type[Exception], ...]] = Exception):
    """Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Exception(s) to catch and retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {current_delay} seconds...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"All {max_attempts} attempts failed. Last error: {str(e)}")
                        raise last_exception
            
            raise last_exception
        return wrapper
    return decorator

def timer(func: Callable) -> Callable:
    """Timer decorator to measure function execution time.
    
    Args:
        func: Function to measure
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"{func.__name__} took {execution_time:.2f} seconds to execute")
        return result
    return wrapper

def log_errors(func: Callable) -> Callable:
    """Log errors decorator to catch and log exceptions.
    
    Args:
        func: Function to wrap
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    return wrapper

def validate_input(validator: Callable) -> Callable:
    """Input validation decorator.
    
    Args:
        validator: Validation function to apply
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not validator(*args, **kwargs):
                raise ValueError(f"Invalid input for {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def cache_result(ttl: Optional[int] = None) -> Callable:
    """Cache function results decorator.
    
    Args:
        ttl: Time to live in seconds (None for no expiration)
    """
    cache: Dict[str, tuple[Any, float]] = {}
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            if key in cache:
                result, timestamp = cache[key]
                if ttl is None or time.time() - timestamp < ttl:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator

def require_auth(roles: Optional[list[str]] = None) -> Callable:
    """Authentication decorator.
    
    Args:
        roles: List of required roles (None for any authenticated user)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # TODO: Implement actual authentication logic
            logger.debug(f"Authentication check for {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limit(calls: int, period: float) -> Callable:
    """Rate limiting decorator.
    
    Args:
        calls: Maximum number of calls allowed
        period: Time period in seconds
    """
    calls_made: Dict[str, list[float]] = {}
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.time()
            key = func.__name__
            
            if key not in calls_made:
                calls_made[key] = []
            
            # Remove old timestamps
            calls_made[key] = [t for t in calls_made[key] if now - t < period]
            
            if len(calls_made[key]) >= calls:
                raise Exception(f"Rate limit exceeded for {func.__name__}")
            
            calls_made[key].append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_arguments(func: Callable) -> Callable:
    """Log function arguments decorator.
    
    Args:
        func: Function to wrap
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        return func(*args, **kwargs)
    return wrapper

def singleton(cls: Type) -> Type:
    """Singleton decorator for classes.
    
    Args:
        cls: Class to make singleton
    """
    instances: Dict[Type, Any] = {}
    
    @wraps(cls)
    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

def deprecated(reason: str) -> Callable:
    """Mark function as deprecated.
    
    Args:
        reason: Reason for deprecation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.warning(f"{func.__name__} is deprecated: {reason}")
            return func(*args, **kwargs)
        return wrapper
    return decorator 