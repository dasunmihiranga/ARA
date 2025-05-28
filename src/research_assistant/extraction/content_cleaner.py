import re
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup
import html2text
import unicodedata

class ContentCleaner:
    """Utility class for cleaning and normalizing extracted content."""

    def __init__(self):
        """Initialize the content cleaner."""
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.ignore_tables = False
        self.html_converter.ignore_emphasis = False

    def clean_text(
        self,
        text: str,
        remove_urls: bool = False,
        remove_emails: bool = False,
        remove_numbers: bool = False,
        remove_special_chars: bool = False,
        normalize_whitespace: bool = True,
        normalize_unicode: bool = True
    ) -> str:
        """
        Clean and normalize text content.

        Args:
            text: Text to clean
            remove_urls: Whether to remove URLs
            remove_emails: Whether to remove email addresses
            remove_numbers: Whether to remove numbers
            remove_special_chars: Whether to remove special characters
            normalize_whitespace: Whether to normalize whitespace
            normalize_unicode: Whether to normalize unicode characters

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Convert to string if not already
        text = str(text)

        # Normalize unicode
        if normalize_unicode:
            text = unicodedata.normalize('NFKC', text)

        # Remove URLs
        if remove_urls:
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        # Remove email addresses
        if remove_emails:
            text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', text)

        # Remove numbers
        if remove_numbers:
            text = re.sub(r'\d+', '', text)

        # Remove special characters
        if remove_special_chars:
            text = re.sub(r'[^\w\s]', '', text)

        # Normalize whitespace
        if normalize_whitespace:
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n\s*\n', '\n', text)
            text = text.strip()

        return text

    def clean_html(
        self,
        html: str,
        remove_scripts: bool = True,
        remove_styles: bool = True,
        remove_comments: bool = True,
        remove_meta: bool = True,
        convert_to_markdown: bool = False
    ) -> str:
        """
        Clean HTML content.

        Args:
            html: HTML content to clean
            remove_scripts: Whether to remove script tags
            remove_styles: Whether to remove style tags
            remove_comments: Whether to remove HTML comments
            remove_meta: Whether to remove meta tags
            convert_to_markdown: Whether to convert HTML to markdown

        Returns:
            Cleaned HTML or markdown
        """
        if not html:
            return ""

        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Remove unwanted elements
        if remove_scripts:
            for script in soup.find_all('script'):
                script.decompose()

        if remove_styles:
            for style in soup.find_all('style'):
                style.decompose()

        if remove_comments:
            for comment in soup.find_all(text=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
                comment.extract()

        if remove_meta:
            for meta in soup.find_all('meta'):
                meta.decompose()

        # Convert to markdown if requested
        if convert_to_markdown:
            return self.html_converter.handle(str(soup))

        return str(soup)

    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace in text.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        if not text:
            return ""

        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with single newline
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def remove_duplicates(self, items: List[str]) -> List[str]:
        """
        Remove duplicate items while preserving order.

        Args:
            items: List of items to deduplicate

        Returns:
            Deduplicated list
        """
        seen = set()
        return [x for x in items if not (x in seen or seen.add(x))]

    def extract_metadata(
        self,
        html: str,
        extract_title: bool = True,
        extract_description: bool = True,
        extract_keywords: bool = True,
        extract_author: bool = True,
        extract_date: bool = True
    ) -> Dict[str, Any]:
        """
        Extract metadata from HTML content.

        Args:
            html: HTML content to extract metadata from
            extract_title: Whether to extract title
            extract_description: Whether to extract description
            extract_keywords: Whether to extract keywords
            extract_author: Whether to extract author
            extract_date: Whether to extract date

        Returns:
            Dictionary of extracted metadata
        """
        metadata = {}
        soup = BeautifulSoup(html, 'html.parser')

        if extract_title:
            title = soup.find('title')
            if title:
                metadata['title'] = title.text.strip()

        if extract_description:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                metadata['description'] = meta_desc.get('content', '').strip()

        if extract_keywords:
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                keywords = meta_keywords.get('content', '').strip()
                metadata['keywords'] = [k.strip() for k in keywords.split(',')]

        if extract_author:
            meta_author = soup.find('meta', attrs={'name': 'author'})
            if meta_author:
                metadata['author'] = meta_author.get('content', '').strip()

        if extract_date:
            meta_date = soup.find('meta', attrs={'name': 'date'})
            if meta_date:
                metadata['date'] = meta_date.get('content', '').strip()

        return metadata

    def clean_table(
        self,
        table_data: List[List[str]],
        remove_empty_rows: bool = True,
        remove_empty_cols: bool = True,
        normalize_cells: bool = True
    ) -> List[List[str]]:
        """
        Clean table data.

        Args:
            table_data: 2D list of table data
            remove_empty_rows: Whether to remove empty rows
            remove_empty_cols: Whether to remove empty columns
            normalize_cells: Whether to normalize cell content

        Returns:
            Cleaned table data
        """
        if not table_data:
            return []

        # Normalize cells
        if normalize_cells:
            table_data = [
                [self.normalize_whitespace(str(cell)) for cell in row]
                for row in table_data
            ]

        # Remove empty rows
        if remove_empty_rows:
            table_data = [
                row for row in table_data
                if any(cell.strip() for cell in row)
            ]

        # Remove empty columns
        if remove_empty_cols and table_data:
            empty_cols = set()
            for col in range(len(table_data[0])):
                if all(not row[col].strip() for row in table_data):
                    empty_cols.add(col)
            
            table_data = [
                [cell for i, cell in enumerate(row) if i not in empty_cols]
                for row in table_data
            ]

        return table_data 