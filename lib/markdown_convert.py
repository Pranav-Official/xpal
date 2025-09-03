from markitdown import MarkItDown
from pydantic import BaseModel, Field
from typing import Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)


class MarkdownConversionResult(BaseModel):
    """Pydantic model for markdown conversion result"""

    text_content: Optional[str] = Field(
        None, description="The text content of the converted markdown"
    )
    title: Optional[str] = Field(
        None, description="The title of the converted document"
    )
    source_url: Optional[str] = Field(
        None, description="The source URL of the converted document"
    )


class MarkdownConverter:
    """A class to handle markdown conversion with proper error handling and typesafety"""

    def __init__(self):
        self.converter = MarkItDown()

    def convert_url_to_markdown(self, url: str) -> MarkdownConversionResult:
        """
        Convert a URL to markdown text with proper error handling

        Args:
            url (str): The URL to convert

        Returns:
            MarkdownConversionResult: The conversion result with text content and metadata

        Raises:
            ValueError: If the URL is invalid
            Exception: If conversion fails
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")

        try:
            logger.info(f"Converting URL to markdown: {url}")
            result = self.converter.convert(url)

            # Create the Pydantic model with the result
            conversion_result = MarkdownConversionResult(
                text_content=(
                    result.text_content if hasattr(result, "text_content") else None
                ),
                title=result.title if hasattr(result, "title") else None,
                source_url=url,
            )

            return conversion_result

        except Exception as e:
            logger.error(f"Error converting URL to markdown: {str(e)}")
            raise Exception(f"Failed to convert URL to markdown: {str(e)}")
