import os
import json
import yaml
import hashlib
import uuid
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging
import traceback
import requests
from urllib.parse import urlparse, urljoin
import mimetypes
import shutil
import tempfile
import zipfile
import tarfile
import gzip
import bz2
import lzma
from concurrent.futures import ThreadPoolExecutor, as_completed

from .logger import Logger
from .constants import (
    SUPPORTED_DOCUMENT_EXTENSIONS,
    SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_VIDEO_EXTENSIONS,
    SUPPORTED_AUDIO_EXTENSIONS,
    MIME_TYPES
)

logger = Logger.get_logger(__name__)

def generate_id() -> str:
    """Generate a unique ID.
    
    Returns:
        str: Unique ID
    """
    return str(uuid.uuid4())

def hash_content(content: Union[str, bytes]) -> str:
    """Generate hash of content.
    
    Args:
        content: Content to hash
        
    Returns:
        str: Hash of content
    """
    if isinstance(content, str):
        content = content.encode()
    return hashlib.sha256(content).hexdigest()

def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Load JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dict[str, Any]: JSON data
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        raise

def save_json(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """Save data to JSON file.
    
    Args:
        data: Data to save
        file_path: Path to save file
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        raise

def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Load YAML file.
    
    Args:
        file_path: Path to YAML file
        
    Returns:
        Dict[str, Any]: YAML data
    """
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading YAML file {file_path}: {e}")
        raise

def save_yaml(data: Dict[str, Any], file_path: Union[str, Path]) -> None:
    """Save data to YAML file.
    
    Args:
        data: Data to save
        file_path: Path to save file
    """
    try:
        with open(file_path, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False)
    except Exception as e:
        logger.error(f"Error saving YAML file {file_path}: {e}")
        raise

def ensure_dir(directory: Union[str, Path]) -> None:
    """Ensure directory exists.
    
    Args:
        directory: Directory path
    """
    Path(directory).mkdir(parents=True, exist_ok=True)

def clean_filename(filename: str) -> str:
    """Clean filename to be safe for all operating systems.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Cleaned filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename

def get_file_extension(filename: str) -> str:
    """Get file extension.
    
    Args:
        filename: Filename
        
    Returns:
        str: File extension
    """
    return os.path.splitext(filename)[1].lower()

def is_supported_file(filename: str) -> bool:
    """Check if file type is supported.
    
    Args:
        filename: Filename
        
    Returns:
        bool: True if file type is supported
    """
    ext = get_file_extension(filename)
    return (ext in SUPPORTED_DOCUMENT_EXTENSIONS or
            ext in SUPPORTED_IMAGE_EXTENSIONS or
            ext in SUPPORTED_VIDEO_EXTENSIONS or
            ext in SUPPORTED_AUDIO_EXTENSIONS)

def get_mime_type(filename: str) -> str:
    """Get MIME type of file.
    
    Args:
        filename: Filename
        
    Returns:
        str: MIME type
    """
    ext = get_file_extension(filename).lstrip('.')
    return MIME_TYPES.get(ext, mimetypes.guess_type(filename)[0] or 'application/octet-stream')

def download_file(url: str, save_path: Optional[Union[str, Path]] = None) -> Union[str, bytes]:
    """Download file from URL.
    
    Args:
        url: URL to download
        save_path: Path to save file (optional)
        
    Returns:
        Union[str, bytes]: Downloaded content or path to saved file
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        if save_path:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return str(save_path)
        else:
            return response.content
    except Exception as e:
        logger.error(f"Error downloading file from {url}: {e}")
        raise

def extract_archive(archive_path: Union[str, Path], extract_path: Optional[Union[str, Path]] = None) -> str:
    """Extract archive file.
    
    Args:
        archive_path: Path to archive file
        extract_path: Path to extract to (optional)
        
    Returns:
        str: Path to extracted files
    """
    if extract_path is None:
        extract_path = tempfile.mkdtemp()
    
    archive_path = Path(archive_path)
    extract_path = Path(extract_path)
    
    try:
        if archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
        elif archive_path.suffix in ['.tar', '.gz', '.bz2']:
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_path)
        else:
            raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
        
        return str(extract_path)
    except Exception as e:
        logger.error(f"Error extracting archive {archive_path}: {e}")
        raise

def compress_file(file_path: Union[str, Path], compression: str = 'gzip') -> str:
    """Compress file.
    
    Args:
        file_path: Path to file
        compression: Compression type (gzip, bzip2, lzma)
        
    Returns:
        str: Path to compressed file
    """
    file_path = Path(file_path)
    
    try:
        if compression == 'gzip':
            output_path = file_path.with_suffix(file_path.suffix + '.gz')
            with open(file_path, 'rb') as f_in:
                with gzip.open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        elif compression == 'bzip2':
            output_path = file_path.with_suffix(file_path.suffix + '.bz2')
            with open(file_path, 'rb') as f_in:
                with bz2.open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        elif compression == 'lzma':
            output_path = file_path.with_suffix(file_path.suffix + '.xz')
            with open(file_path, 'rb') as f_in:
                with lzma.open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            raise ValueError(f"Unsupported compression type: {compression}")
        
        return str(output_path)
    except Exception as e:
        logger.error(f"Error compressing file {file_path}: {e}")
        raise

def parallel_process(items: List[Any], process_func: callable, max_workers: Optional[int] = None) -> List[Any]:
    """Process items in parallel.
    
    Args:
        items: Items to process
        process_func: Function to process items
        max_workers: Maximum number of workers (optional)
        
    Returns:
        List[Any]: Processed items
    """
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(process_func, item): item for item in items}
        for future in as_completed(future_to_item):
            try:
                results.append(future.result())
            except Exception as e:
                logger.error(f"Error processing item: {e}")
                raise
    return results

def retry_on_failure(func: callable, max_attempts: int = 3, delay: float = 1.0) -> Any:
    """Retry function on failure.
    
    Args:
        func: Function to retry
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
        
    Returns:
        Any: Function result
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)

def format_timestamp(timestamp: Union[str, float, datetime], format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp.
    
    Args:
        timestamp: Timestamp to format
        format: Output format
        
    Returns:
        str: Formatted timestamp
    """
    if isinstance(timestamp, str):
        timestamp = float(timestamp)
    if isinstance(timestamp, float):
        timestamp = datetime.fromtimestamp(timestamp)
    return timestamp.strftime(format)

def parse_timestamp(timestamp_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse timestamp string.
    
    Args:
        timestamp_str: Timestamp string
        format: Input format
        
    Returns:
        datetime: Parsed timestamp
    """
    return datetime.strptime(timestamp_str, format)

def sanitize_url(url: str) -> str:
    """Sanitize URL.
    
    Args:
        url: URL to sanitize
        
    Returns:
        str: Sanitized URL
    """
    parsed = urlparse(url)
    if not parsed.scheme:
        url = 'https://' + url
    return url

def is_valid_url(url: str) -> bool:
    """Check if URL is valid.
    
    Args:
        url: URL to check
        
    Returns:
        bool: True if URL is valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def get_base_url(url: str) -> str:
    """Get base URL.
    
    Args:
        url: URL to process
        
    Returns:
        str: Base URL
    """
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def join_urls(base: str, url: str) -> str:
    """Join URLs.
    
    Args:
        base: Base URL
        url: URL to join
        
    Returns:
        str: Joined URL
    """
    return urljoin(base, url)

def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks.
    
    Args:
        items: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List[List[Any]]: List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

def flatten_list(items: List[List[Any]]) -> List[Any]:
    """Flatten nested list.
    
    Args:
        items: Nested list
        
    Returns:
        List[Any]: Flattened list
    """
    return [item for sublist in items for item in sublist]

def remove_duplicates(items: List[Any]) -> List[Any]:
    """Remove duplicates from list while preserving order.
    
    Args:
        items: List to process
        
    Returns:
        List[Any]: List without duplicates
    """
    seen = set()
    return [x for x in items if not (x in seen or seen.add(x))]

def safe_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary value.
    
    Args:
        data: Dictionary to search
        keys: Keys to traverse
        default: Default value if key not found
        
    Returns:
        Any: Value if found, default otherwise
    """
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is None:
            return default
    return current 