from abc import ABC, abstractmethod
from typing import Optional


class BaseAudioProvider(ABC):
    """Abstract base class for all audio/TTS providers."""

    @abstractmethod
    def fetch_audio(self, word: str, lang_code: str) -> Optional[bytes]:
        """
        Fetches pronunciation audio for a given word or phrase.

        Args:
            word:      The word or phrase to pronounce.
            lang_code: BCP-47 language code (e.g. 'es', 'fr', 'de').

        Returns:
            Raw audio data as bytes (MP3 format), or None if unavailable.

        Raises:
            ConnectionError: On network failure.
            ValueError:      On bad response / unsupported parameters.
        """
        pass
