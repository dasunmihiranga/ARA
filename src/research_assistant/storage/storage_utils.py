from typing import Dict, Any, List, Optional, Union, Callable
import json
import pickle
import hashlib
from datetime import datetime
import os
from pathlib import Path
import shutil
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor
import aiofiles
import aiofiles.os

from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class StorageUtils:
    """Utility functions for storage operations."""

    @staticmethod
    def generate_hash(data: Union[str, bytes, Dict[str, Any]]) -> str:
        """
        Generate a hash for data.

        Args:
            data: Data to hash

        Returns:
            Hash string
        """
        try:
            if isinstance(data, dict):
                data = json.dumps(data, sort_keys=True)
            if isinstance(data, str):
                data = data.encode()
            return hashlib.md5(data).hexdigest()
        except Exception as e:
            logger.error(f"Error generating hash: {str(e)}")
            raise

    @staticmethod
    def ensure_dir(directory: Union[str, Path]) -> None:
        """
        Ensure directory exists.

        Args:
            directory: Directory path
        """
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Error ensuring directory {directory}: {str(e)}")
            raise

    @staticmethod
    def safe_remove(path: Union[str, Path]) -> bool:
        """
        Safely remove a file or directory.

        Args:
            path: Path to remove

        Returns:
            True if removed, False if not found
        """
        try:
            path = Path(path)
            if path.exists():
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing {path}: {str(e)}")
            return False

    @staticmethod
    def get_file_size(path: Union[str, Path]) -> int:
        """
        Get file size in bytes.

        Args:
            path: File path

        Returns:
            File size in bytes
        """
        try:
            return Path(path).stat().st_size
        except Exception as e:
            logger.error(f"Error getting file size {path}: {str(e)}")
            return 0

    @staticmethod
    def get_dir_size(path: Union[str, Path]) -> int:
        """
        Get directory size in bytes.

        Args:
            path: Directory path

        Returns:
            Directory size in bytes
        """
        try:
            total_size = 0
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    total_size += os.path.getsize(fp)
            return total_size
        except Exception as e:
            logger.error(f"Error getting directory size {path}: {str(e)}")
            return 0

    @staticmethod
    async def async_write_json(
        data: Dict[str, Any],
        path: Union[str, Path],
        ensure_dir: bool = True
    ) -> None:
        """
        Asynchronously write JSON data to file.

        Args:
            data: Data to write
            path: Output path
            ensure_dir: Whether to ensure directory exists
        """
        try:
            path = Path(path)
            if ensure_dir:
                StorageUtils.ensure_dir(path.parent)

            async with aiofiles.open(path, "w") as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Error writing JSON to {path}: {str(e)}")
            raise

    @staticmethod
    async def async_read_json(
        path: Union[str, Path]
    ) -> Optional[Dict[str, Any]]:
        """
        Asynchronously read JSON data from file.

        Args:
            path: Input path

        Returns:
            JSON data or None if not found
        """
        try:
            path = Path(path)
            if not path.exists():
                return None

            async with aiofiles.open(path, "r") as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logger.error(f"Error reading JSON from {path}: {str(e)}")
            return None

    @staticmethod
    async def async_write_pickle(
        data: Any,
        path: Union[str, Path],
        ensure_dir: bool = True
    ) -> None:
        """
        Asynchronously write pickle data to file.

        Args:
            data: Data to write
            path: Output path
            ensure_dir: Whether to ensure directory exists
        """
        try:
            path = Path(path)
            if ensure_dir:
                StorageUtils.ensure_dir(path.parent)

            # Use temporary file for atomic write
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                pickle.dump(data, tmp)
                tmp_path = tmp.name

            try:
                await aiofiles.os.replace(tmp_path, path)
            except Exception as e:
                StorageUtils.safe_remove(tmp_path)
                raise e

        except Exception as e:
            logger.error(f"Error writing pickle to {path}: {str(e)}")
            raise

    @staticmethod
    async def async_read_pickle(
        path: Union[str, Path]
    ) -> Optional[Any]:
        """
        Asynchronously read pickle data from file.

        Args:
            path: Input path

        Returns:
            Pickle data or None if not found
        """
        try:
            path = Path(path)
            if not path.exists():
                return None

            async with aiofiles.open(path, "rb") as f:
                content = await f.read()
                return pickle.loads(content)
        except Exception as e:
            logger.error(f"Error reading pickle from {path}: {str(e)}")
            return None

    @staticmethod
    def batch_process(
        items: List[Any],
        process_func: Callable,
        batch_size: int = 100,
        max_workers: Optional[int] = None
    ) -> List[Any]:
        """
        Process items in batches using thread pool.

        Args:
            items: Items to process
            process_func: Processing function
            batch_size: Batch size
            max_workers: Maximum number of workers

        Returns:
            List of processed items
        """
        try:
            results = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for i in range(0, len(items), batch_size):
                    batch = items[i:i + batch_size]
                    batch_results = list(executor.map(process_func, batch))
                    results.extend(batch_results)
            return results
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            return []

    @staticmethod
    async def async_batch_process(
        items: List[Any],
        process_func: Callable,
        batch_size: int = 100,
        max_concurrent: Optional[int] = None
    ) -> List[Any]:
        """
        Process items in batches asynchronously.

        Args:
            items: Items to process
            process_func: Processing function
            batch_size: Batch size
            max_concurrent: Maximum concurrent tasks

        Returns:
            List of processed items
        """
        try:
            results = []
            semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None

            async def process_with_semaphore(item):
                if semaphore:
                    async with semaphore:
                        return await process_func(item)
                return await process_func(item)

            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                batch_results = await asyncio.gather(
                    *[process_with_semaphore(item) for item in batch]
                )
                results.extend(batch_results)

            return results
        except Exception as e:
            logger.error(f"Error in async batch processing: {str(e)}")
            return []

    @staticmethod
    def get_file_info(path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get file information.

        Args:
            path: File path

        Returns:
            Dictionary with file information
        """
        try:
            path = Path(path)
            if not path.exists():
                return {}

            stat = path.stat()
            return {
                "name": path.name,
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "is_file": path.is_file(),
                "is_dir": path.is_dir()
            }
        except Exception as e:
            logger.error(f"Error getting file info {path}: {str(e)}")
            return {}

    @staticmethod
    def get_dir_contents(
        path: Union[str, Path],
        recursive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get directory contents.

        Args:
            path: Directory path
            recursive: Whether to include subdirectories

        Returns:
            List of file information dictionaries
        """
        try:
            path = Path(path)
            if not path.exists() or not path.is_dir():
                return []

            contents = []
            for item in path.iterdir():
                if recursive and item.is_dir():
                    contents.extend(StorageUtils.get_dir_contents(item, recursive=True))
                else:
                    contents.append(StorageUtils.get_file_info(item))

            return contents
        except Exception as e:
            logger.error(f"Error getting directory contents {path}: {str(e)}")
            return [] 