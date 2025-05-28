import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import mimetypes
from pathlib import Path
import aiofiles
import aiohttp
from bs4 import BeautifulSoup
import magic
import chardet

class ExtractionUtils:
    """Utility functions for content extraction."""

    @staticmethod
    async def detect_file_type(file_path: str) -> Tuple[str, str]:
        """
        Detect file type and mime type.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (file_type, mime_type)
        """
        try:
            # Get mime type
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                # Use python-magic to detect mime type
                async with aiofiles.open(file_path, 'rb') as f:
                    content = await f.read(2048)
                    mime_type = magic.from_buffer(content, mime=True)

            # Get file type from extension
            file_type = Path(file_path).suffix.lower()[1:]

            return file_type, mime_type
        except Exception as e:
            return None, None

    @staticmethod
    async def detect_encoding(file_path: str) -> str:
        """
        Detect file encoding.

        Args:
            file_path: Path to the file

        Returns:
            Detected encoding
        """
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read(4096)
                result = chardet.detect(content)
                return result['encoding'] or 'utf-8'
        except Exception:
            return 'utf-8'

    @staticmethod
    def extract_dates(text: str) -> List[str]:
        """
        Extract dates from text.

        Args:
            text: Text to extract dates from

        Returns:
            List of extracted dates
        """
        # Common date patterns
        patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY
            r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY
            r'\d{4}-\d{2}-\d{2}',        # YYYY-MM-DD
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}',  # DD Month YYYY
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}'  # Month DD, YYYY
        ]

        dates = []
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            dates.extend(match.group() for match in matches)

        return list(set(dates))

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        Extract email addresses from text.

        Args:
            text: Text to extract emails from

        Returns:
            List of extracted email addresses
        """
        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        return list(set(re.findall(pattern, text)))

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        Extract URLs from text.

        Args:
            text: Text to extract URLs from

        Returns:
            List of extracted URLs
        """
        pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return list(set(re.findall(pattern, text)))

    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """
        Extract phone numbers from text.

        Args:
            text: Text to extract phone numbers from

        Returns:
            List of extracted phone numbers
        """
        patterns = [
            r'\+\d{1,3}[-.\s]?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{4}',  # International
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',                # US/Canada
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'                       # Simple
        ]

        numbers = []
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            numbers.extend(match.group() for match in matches)

        return list(set(numbers))

    @staticmethod
    def extract_entities(text: str, entity_types: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """
        Extract named entities from text.

        Args:
            text: Text to extract entities from
            entity_types: Optional list of entity types to extract

        Returns:
            Dictionary of entity types and their values
        """
        entities = {
            'dates': ExtractionUtils.extract_dates(text),
            'emails': ExtractionUtils.extract_emails(text),
            'urls': ExtractionUtils.extract_urls(text),
            'phone_numbers': ExtractionUtils.extract_phone_numbers(text)
        }

        if entity_types:
            return {k: v for k, v in entities.items() if k in entity_types}
        return entities

    @staticmethod
    async def download_file(url: str, output_path: str, timeout: int = 30) -> bool:
        """
        Download a file from a URL.

        Args:
            url: URL to download from
            output_path: Path to save the file
            timeout: Request timeout in seconds

        Returns:
            True if download successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        async with aiofiles.open(output_path, 'wb') as f:
                            await f.write(await response.read())
                        return True
            return False
        except Exception:
            return False

    @staticmethod
    def parse_html_table(table_html: str) -> List[List[str]]:
        """
        Parse HTML table into 2D list.

        Args:
            table_html: HTML table content

        Returns:
            2D list of table data
        """
        try:
            soup = BeautifulSoup(table_html, 'html.parser')
            table = soup.find('table')
            if not table:
                return []

            rows = []
            for tr in table.find_all('tr'):
                row = []
                for cell in tr.find_all(['td', 'th']):
                    row.append(cell.get_text(strip=True))
                if row:
                    rows.append(row)

            return rows
        except Exception:
            return []

    @staticmethod
    def extract_table_metadata(table_html: str) -> Dict[str, Any]:
        """
        Extract metadata from HTML table.

        Args:
            table_html: HTML table content

        Returns:
            Dictionary of table metadata
        """
        try:
            soup = BeautifulSoup(table_html, 'html.parser')
            table = soup.find('table')
            if not table:
                return {}

            metadata = {
                'caption': '',
                'headers': [],
                'num_rows': 0,
                'num_cols': 0,
                'has_header_row': False
            }

            # Extract caption
            caption = table.find('caption')
            if caption:
                metadata['caption'] = caption.get_text(strip=True)

            # Extract headers
            headers = []
            header_row = table.find('tr')
            if header_row:
                for th in header_row.find_all('th'):
                    headers.append(th.get_text(strip=True))
                metadata['headers'] = headers
                metadata['has_header_row'] = bool(headers)

            # Count rows and columns
            rows = table.find_all('tr')
            metadata['num_rows'] = len(rows)
            if rows:
                metadata['num_cols'] = max(len(row.find_all(['td', 'th'])) for row in rows)

            return metadata
        except Exception:
            return {}

    @staticmethod
    def extract_list_items(html: str) -> List[str]:
        """
        Extract items from HTML lists.

        Args:
            html: HTML content containing lists

        Returns:
            List of extracted items
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            items = []

            # Extract from ordered and unordered lists
            for ul in soup.find_all(['ul', 'ol']):
                for li in ul.find_all('li'):
                    items.append(li.get_text(strip=True))

            return items
        except Exception:
            return []

    @staticmethod
    def extract_links(html: str, base_url: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Extract links from HTML content.

        Args:
            html: HTML content
            base_url: Optional base URL for resolving relative links

        Returns:
            List of dictionaries containing link information
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []

            for a in soup.find_all('a', href=True):
                link = {
                    'text': a.get_text(strip=True),
                    'href': a['href'],
                    'title': a.get('title', '')
                }

                # Resolve relative URLs
                if base_url and not link['href'].startswith(('http://', 'https://')):
                    link['href'] = f"{base_url.rstrip('/')}/{link['href'].lstrip('/')}"

                links.append(link)

            return links
        except Exception:
            return []

    @staticmethod
    def extract_images(html: str, base_url: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Extract images from HTML content.

        Args:
            html: HTML content
            base_url: Optional base URL for resolving relative image URLs

        Returns:
            List of dictionaries containing image information
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            images = []

            for img in soup.find_all('img'):
                image = {
                    'src': img.get('src', ''),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                }

                # Resolve relative URLs
                if base_url and not image['src'].startswith(('http://', 'https://')):
                    image['src'] = f"{base_url.rstrip('/')}/{image['src'].lstrip('/')}"

                images.append(image)

            return images
        except Exception:
            return [] 