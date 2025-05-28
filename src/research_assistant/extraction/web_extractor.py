from typing import Dict, Any, List, Optional
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin
import trafilatura
from trafilatura.settings import use_config
import langdetect

from research_assistant.extraction.base_extractor import BaseExtractor, ExtractedContent, ExtractionOptions
from research_assistant.utils.logging import get_logger

logger = get_logger(__name__)

class WebExtractor(BaseExtractor):
    """Web content extractor implementation."""

    def __init__(
        self,
        timeout: int = 30,
        user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ):
        """
        Initialize the web extractor.

        Args:
            timeout: Request timeout in seconds
            user_agent: User agent string for requests
        """
        super().__init__(
            name="web",
            description="Extract content from web pages"
        )
        self.timeout = timeout
        self.user_agent = user_agent
        self.session: Optional[aiohttp.ClientSession] = None
        self.trafilatura_config = use_config()
        self.trafilatura_config.set("DEFAULT", "fallback", "true")

    async def _ensure_session(self) -> None:
        """Ensure aiohttp session exists."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={"User-Agent": self.user_agent}
            )

    async def extract(
        self,
        source: str,
        options: Optional[ExtractionOptions] = None
    ) -> ExtractedContent:
        """
        Extract content from a web page.

        Args:
            source: URL of the web page
            options: Optional extraction options

        Returns:
            Extracted content

        Raises:
            ValueError: If URL is invalid
            Exception: For other extraction errors
        """
        if not await self.validate_source(source):
            raise ValueError(f"Invalid URL: {source}")

        options = options or ExtractionOptions()
        await self._ensure_session()

        try:
            # Fetch the page
            async with self.session.get(
                source,
                timeout=min(options.timeout, self.timeout),
                allow_redirects=True
            ) as response:
                if response.status != 200:
                    raise Exception(f"HTTP error: {response.status}")

                html = await response.text()
                if options.max_size and len(html) > options.max_size:
                    raise ValueError(f"Page size exceeds maximum limit: {len(html)} bytes")

                # Extract content using trafilatura
                content = trafilatura.extract(
                    html,
                    include_comments=False,
                    include_tables=options.extract_tables,
                    include_images=options.include_images,
                    include_links=options.include_links,
                    config=self.trafilatura_config
                )

                if not content:
                    # Fallback to BeautifulSoup if trafilatura fails
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove unwanted elements
                    for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                        element.decompose()

                    # Extract title
                    title = soup.title.string if soup.title else ""
                    
                    # Extract main content
                    main_content = soup.find('main') or soup.find('article') or soup.find('body')
                    content = main_content.get_text(separator='\n', strip=True) if main_content else ""

                # Clean the content
                content = self._clean_content(content)

                # Extract metadata
                metadata = self._extract_metadata(html, source)

                # Detect language
                try:
                    language = langdetect.detect(content)
                except:
                    language = None

                # Count words and characters
                word_count = len(content.split())
                char_count = len(content)

                return self.format_content({
                    "title": metadata.get("title", ""),
                    "text": content,
                    "metadata": metadata,
                    "language": language,
                    "word_count": word_count,
                    "char_count": char_count
                })

        except asyncio.TimeoutError:
            self.logger.error(f"Timeout while extracting from {source}")
            raise Exception("Extraction timed out")
        except Exception as e:
            self.logger.error(f"Error extracting from {source}: {str(e)}")
            raise

    async def validate_source(self, source: str) -> bool:
        """
        Validate if the source is a valid URL.

        Args:
            source: URL to validate

        Returns:
            True if URL is valid, False otherwise
        """
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _clean_content(self, content: str) -> str:
        """
        Clean extracted content.

        Args:
            content: Raw content to clean

        Returns:
            Cleaned content
        """
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove empty lines
        content = re.sub(r'\n\s*\n', '\n', content)
        
        # Remove special characters
        content = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', content)
        
        return content.strip()

    def _extract_metadata(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract metadata from HTML.

        Args:
            html: HTML content
            url: Source URL

        Returns:
            Dictionary of metadata
        """
        soup = BeautifulSoup(html, 'html.parser')
        metadata = {
            "url": url,
            "title": "",
            "description": "",
            "keywords": [],
            "author": "",
            "published_date": None,
            "modified_date": None,
            "language": None
        }

        # Extract title
        if soup.title:
            metadata["title"] = soup.title.string

        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                metadata["description"] = content
            elif name == 'keywords':
                metadata["keywords"] = [k.strip() for k in content.split(',')]
            elif name == 'author':
                metadata["author"] = content
            elif name == 'article:published_time':
                metadata["published_date"] = content
            elif name == 'article:modified_time':
                metadata["modified_date"] = content
            elif name == 'language':
                metadata["language"] = content

        # Extract Open Graph tags
        for meta in soup.find_all('meta', property=re.compile(r'^og:')):
            property_name = meta.get('property', '').replace('og:', '')
            metadata[f"og_{property_name}"] = meta.get('content', '')

        return metadata

    async def close(self) -> None:
        """Close the web extractor."""
        if self.session:
            await self.session.close()
            self.session = None 