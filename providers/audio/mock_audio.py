"""
Mock Audio Provider — for testing without any network access.

Returns a minimal valid MP3 header so Anki can store and
reference the file without crashing. The audio will be silent.
"""

import time
from typing import Optional

from .base import BaseAudioProvider
from ...utils.logger import get_logger

logger = get_logger(__name__)

# Minimal valid MP3 frame (MPEG-1, Layer 3, 128 kbps, 44100 Hz, stereo)
# followed by 200 bytes of silence padding — enough for Anki to accept it.
_SILENT_MP3 = (
    b"\xff\xfb\x90\x00"   # MP3 frame sync + header
    + b"\x00" * 200        # silent frame data
)


class MockAudioProvider(BaseAudioProvider):
    """Returns a silent mock MP3 for offline/testing use."""

    def fetch_audio(self, word: str, lang_code: str) -> Optional[bytes]:
        logger.info(
            f"MockAudioProvider: returning silent audio for '{word}' ({lang_code})"
        )
        time.sleep(0.3)   # simulate slight network latency
        return _SILENT_MP3
