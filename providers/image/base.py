from abc import ABC, abstractmethod
from typing import Optional


class BaseImageProvider(ABC):
    """Abstract base class for all image search/download providers."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    @abstractmethod
    def search_image(self, query: str) -> Optional[bytes]:
        """
        Searches for and downloads an image matching an English query.

        Args:
            query: Descriptive English search term (e.g. "dog", "person eating").

        Returns:
            Raw image bytes (JPEG or PNG), or None if no image found.

        Raises:
            ConnectionError: On network failure.
            ValueError:      On missing API key or bad response.
        """
        pass
